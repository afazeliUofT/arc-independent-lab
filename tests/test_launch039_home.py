"""Offline launcher checks with actual Git/filesystems and a substitute helper.

These tests do not run Windows interop, contact GitHub, or execute a reviewer.
The finite workflow has separate local-Git integration tests; no model is run here.
"""
import importlib.util
import io
import json
from pathlib import Path
import stat
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import warnings
import zipfile


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/launch039_home.py'
SPEC = importlib.util.spec_from_file_location('launch039', SCRIPT)
launcher = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(launcher)


class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name) / 'home with space and \u00e9'
        self.lab = self.home / 'ARC_Independent_Lab'
        self.lab.mkdir(parents=True)
        self.git('init', '-b', 'main')
        self.git('config', 'user.name', 'Launcher fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.git('remote', 'add', 'origin', launcher.REMOTE + '.git')
        (self.lab / '.gitignore').write_text('delivery/\n')
        self.git('add', '.gitignore')
        self.git('commit', '-m', 'Fixture ignore rule')
        self.members = {name: ('Fixture ' + name + '\n').encode()
                        for name in launcher.ROOT_FILES - {'SHA256SUMS'}}
        self.members.update({
            'packet/private_papers/chvatal.pdf': b'%PDF-1.4\nprivate supplied fixture\n',
            'packet/reading/CHV79/full_text.txt': b'Private extracted text fixture.\n',
            'packet/reading/PK97/pages/page_001.png': b'\x89PNG\r\n\x1a\nfixture',
            'packet/FOCUSED_SCOPE.json': b'{\"kind\":\"fixture\"}\n',
            **{'scripts/' + name: b'# Fixture script; never executed.\n' for name in
               ('review039_workflow.py', 'stage_source_packet038.py',
                'review032_workflow.py', 'publish_review039_evidence.py')}
        })
        self.members['public/docs/source.md'] = b'Original public source fixture.\n'
        self.calls = []

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.lab), *args], check=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout

    def archive(self, members=None, *, extra=(), overrides=None):
        files = dict(self.members if members is None else members)
        files['SHA256SUMS'] = ''.join(launcher.digest(raw) + '  ' + name + '\n'
                                     for name, raw in sorted(files.items())).encode()
        files.update(overrides or {})
        buffer = io.BytesIO()
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
                for name, raw in files.items():
                    entry = zipfile.ZipInfo(name)
                    entry.external_attr = (stat.S_IFREG | 0o600) << 16
                    archive.writestr(entry, raw)
                for entry, raw in extra:
                    archive.writestr(entry, raw)
        return buffer.getvalue()

    def run_helper(self, command, **kwargs):
        self.calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0)

    def run_launch(self, raw=None, **kwargs):
        return launcher.launch(self.archive() if raw is None else raw,
                               '/mnt/c/Users/fixture/Downloads/package (1).zip',
                               home=self.home, runner=kwargs.get('runner', self.run_helper))

    def destination(self, raw):
        return self.lab / launcher.STEM / launcher.digest(raw)

    def assert_no_copy(self):
        self.assertFalse((self.lab / 'delivery').exists())
        self.assertEqual(self.calls, [])

    def test_valid_package_copies_exact_bytes_is_private_and_repeatable(self):
        raw = self.archive()
        bundle = self.run_launch(raw)
        self.assertEqual((bundle.parent / 'PACKAGE.zip').read_bytes(), raw)
        members = launcher.archive_payloads(raw)
        for name, body in members.items():
            self.assertEqual((bundle / name).read_bytes(), body)
            self.assertEqual((bundle / name).stat().st_mode & 0o777, 0o600)
        snapshot = {path: path.stat().st_mtime_ns for path in bundle.parent.rglob('*')
                    if path.is_file()}
        self.assertEqual(self.run_launch(raw), bundle)
        self.assertEqual(snapshot, {path: path.stat().st_mtime_ns for path in snapshot})
        self.assertEqual(len(self.calls), 2)
        command, options = self.calls[0]
        self.assertEqual(command[1:3], ['-B', '-u'])
        self.assertEqual(command[3:], [str(bundle / 'scripts/review039_workflow.py'),
                                     '--lab', str(self.lab), '--bundle', str(bundle)])
        self.assertEqual(options, {'cwd': self.lab})
        self.assertFalse(self.git('ls-files', '--', launcher.STEM))
        self.assertFalse(self.git('status', '--porcelain'))

    def test_matching_partial_extraction_is_completed(self):
        raw = self.archive()
        destination = self.destination(raw)
        path = destination / 'bundle' / 'README_039.md'
        path.parent.mkdir(parents=True)
        path.write_bytes(self.members['README_039.md'])
        before = path.stat().st_mtime_ns
        bundle = self.run_launch(raw)
        self.assertEqual(path.stat().st_mtime_ns, before)
        self.assertTrue((bundle / 'RELEASE.json').exists())

    def test_changed_existing_file_is_preserved_without_helper(self):
        raw = self.archive()
        path = self.destination(raw) / 'bundle' / 'RELEASE.json'
        path.parent.mkdir(parents=True)
        path.write_bytes(b'Human work; preserve me.\n')
        with self.assertRaisesRegex(launcher.LaunchStop, 'changed existing file'):
            self.run_launch(raw)
        self.assertEqual(path.read_bytes(), b'Human work; preserve me.\n')
        self.assertFalse((path.parent.parent / 'PACKAGE.zip').exists())
        self.assertEqual(self.calls, [])

    def test_unexpected_existing_file_or_directory_is_preserved(self):
        raw = self.archive()
        destination = self.destination(raw)
        destination.mkdir(parents=True)
        path = destination / 'unrelated.txt'
        path.write_text('Preserve me')
        with self.assertRaisesRegex(launcher.LaunchStop, 'Unexpected or changed'):
            self.run_launch(raw)
        self.assertEqual(path.read_text(), 'Preserve me')
        path.unlink()
        (destination / 'unrelated').mkdir()
        with self.assertRaisesRegex(launcher.LaunchStop, 'Unexpected existing directory'):
            self.run_launch(raw)
        self.assertTrue((destination / 'unrelated').is_dir())
        self.assertEqual(self.calls, [])

    def test_linked_destination_is_refused_without_touching_target(self):
        outside = self.home / 'outside'
        outside.mkdir()
        (self.lab / 'delivery').symlink_to(outside, target_is_directory=True)
        # Git itself can reject a symlinked parent before the file walker runs.
        with self.assertRaises(launcher.LaunchStop):
            self.run_launch()
        self.assertEqual(list(outside.iterdir()), [])
        self.assertEqual(self.calls, [])

    def test_linked_bundle_and_changed_archive_are_preserved(self):
        raw = self.archive()
        destination = self.destination(raw)
        destination.mkdir(parents=True)
        outside = self.home / 'outside'
        outside.mkdir()
        bundle = destination / 'bundle'
        bundle.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(launcher.LaunchStop):
            self.run_launch(raw)
        self.assertEqual(list(outside.iterdir()), [])
        bundle.unlink()
        package = destination / 'PACKAGE.zip'
        package.write_bytes(b'Existing different archive; preserve me')
        with self.assertRaisesRegex(launcher.LaunchStop, 'changed existing file'):
            self.run_launch(raw)
        self.assertEqual(package.read_bytes(), b'Existing different archive; preserve me')
        self.assertFalse(bundle.exists())
        self.assertEqual(self.calls, [])

    def test_existing_hardlinked_file_is_preserved(self):
        raw = self.archive()
        path = self.destination(raw) / 'PACKAGE.zip'
        path.parent.mkdir(parents=True)
        path.write_bytes(raw)
        (self.home / 'alias.zip').hardlink_to(path)
        with self.assertRaisesRegex(launcher.LaunchStop, 'Linked, special'):
            self.run_launch(raw)
        self.assertEqual(path.read_bytes(), raw)
        self.assertEqual(self.calls, [])

    def test_checksum_mismatch_is_refused_before_copy(self):
        raw = self.archive(overrides={'RELEASE.json': b'Corrupted bytes\n'})
        with self.assertRaisesRegex(launcher.LaunchStop, 'digest mismatch'):
            self.run_launch(raw)
        self.assert_no_copy()

    def test_checksum_inventory_requires_every_member_once(self):
        for checksum in (b'', b'bad checksum line\n',
                         b'0' * 64 + b'  SHA256SUMS\n',
                         (b'0' * 64 + b'  RELEASE.json\n') * 2):
            with self.subTest(checksum=checksum):
                with self.assertRaises(launcher.LaunchStop):
                    self.run_launch(self.archive(overrides={'SHA256SUMS': checksum}))
                self.assert_no_copy()

    def test_duplicate_zip_member_is_refused(self):
        raw = self.archive(extra=[('RELEASE.json', b'duplicate\n')])
        with self.assertRaisesRegex(launcher.LaunchStop, 'Duplicate'):
            self.run_launch(raw)
        self.assert_no_copy()

    def test_unsafe_or_unexpected_member_paths_are_refused(self):
        for name in ('../escape.py', '/absolute.py', 'public/../escape.py',
                     'C:/escape.py', 'public\\escape.py', 'public/./escape.py',
                     'public/.git/config.py', 'public/__MACOSX/sidecar.py',
                     'public/._sidecar.py', 'public/double//separator.py',
                     'unexpected.py', 'private_papers/extra.pdf', 'scripts/unsafe.sh'):
            with self.subTest(name=name):
                with self.assertRaises(launcher.LaunchStop):
                    self.run_launch(self.archive({**self.members, name: b'Bad member'}))
                self.assert_no_copy()

    def test_zip_symlink_and_directory_entry_are_refused(self):
        for mode in (stat.S_IFLNK | 0o777, stat.S_IFDIR | 0o700):
            entry = zipfile.ZipInfo('public/link.py')
            entry.external_attr = mode << 16
            with self.subTest(mode=mode):
                with self.assertRaisesRegex(launcher.LaunchStop, 'Nonregular'):
                    self.run_launch(self.archive(extra=[(entry, b'outside')]))
                self.assert_no_copy()

    def test_archive_file_directory_collision_is_refused(self):
        members = {**self.members, 'public/name.py': b'file',
                   'public/name.py/child.py': b'child'}
        with self.assertRaisesRegex(launcher.LaunchStop, 'path collision'):
            self.run_launch(self.archive(members))
        self.assert_no_copy()

    def test_missing_required_file_is_refused(self):
        for missing in launcher.BOOT_SCRIPTS:
            with self.subTest(missing=missing):
                members = dict(self.members)
                members.pop(missing)
                with self.assertRaisesRegex(launcher.LaunchStop, 'Required package files missing'):
                    self.run_launch(self.archive(members))
                self.assert_no_copy()

    def test_archive_limits_are_enforced_before_copy(self):
        raw = self.archive()
        for field, value in (('MAX_ARCHIVE', len(raw) - 1), ('MAX_MEMBERS', 1),
                             ('MAX_FILE', 1), ('MAX_TOTAL', 1)):
            with self.subTest(field=field), patch.object(launcher, field, value):
                with self.assertRaises(launcher.LaunchStop):
                    self.run_launch(raw)
                self.assert_no_copy()

    def test_wrong_origin_stops_before_private_copy(self):
        self.git('remote', 'set-url', 'origin', 'https://github.com/wrong/repository.git')
        with self.assertRaisesRegex(launcher.LaunchStop, 'Origin differs'):
            self.run_launch()
        self.assert_no_copy()

    def test_multiple_push_urls_are_refused(self):
        self.git('remote', 'set-url', '--add', '--push', 'origin', launcher.REMOTE + '.git')
        self.git('remote', 'set-url', '--add', '--push', 'origin', 'https://github.com/wrong/repo.git')
        with self.assertRaisesRegex(launcher.LaunchStop, 'Origin differs'):
            self.run_launch()
        self.assert_no_copy()

    def test_unignored_delivery_is_refused_before_copy(self):
        (self.lab / '.gitignore').write_text('# delivery is not ignored\n')
        self.git('add', '.gitignore')
        self.git('commit', '-m', 'Fixture lacks ignore')
        with self.assertRaises(launcher.LaunchStop):
            self.run_launch()
        self.assert_no_copy()

    def test_tracked_destination_is_refused_before_copy(self):
        raw = self.archive()
        path = self.destination(raw) / 'tracked.txt'
        path.parent.mkdir(parents=True)
        path.write_text('Invalid tracked destination')
        self.git('add', '-f', str(path))
        self.git('commit', '-m', 'Invalid tracked fixture')
        with self.assertRaisesRegex(launcher.LaunchStop, 'destination is tracked'):
            self.run_launch(raw)
        self.assertEqual(path.read_text(), 'Invalid tracked destination')
        self.assertFalse((path.parent / 'PACKAGE.zip').exists())
        self.assertEqual(self.calls, [])

    def test_helper_failure_is_propagated_and_same_command_can_retry(self):
        raw = self.archive()
        def fail(command, **kwargs):
            self.calls.append((command, kwargs))
            return subprocess.CompletedProcess(command, 1)
        with self.assertRaisesRegex(launcher.LaunchStop, 'Review workflow stopped'):
            self.run_launch(raw, runner=fail)
        package = self.destination(raw) / 'PACKAGE.zip'
        before = package.stat().st_mtime_ns
        self.run_launch(raw)
        self.assertEqual(package.stat().st_mtime_ns, before)
        self.assertEqual(len(self.calls), 2)

    def test_staged_evidence_recovery_is_delegated_without_altering_index(self):
        path = self.lab / 'artifacts/P3_REVIEW_039_RETURN/fixture/INDEX.json'
        path.parent.mkdir(parents=True)
        path.write_text('{"fixture":"staged result for workflow verification"}\n')
        self.git('add', str(path))
        before = self.git('diff', '--cached', '--binary')
        bundle = self.run_launch()
        self.assertEqual(self.git('diff', '--cached', '--binary'), before)
        self.assertEqual(self.calls[0][0][3], str(bundle / 'scripts/review039_workflow.py'))

    def test_unrelated_tracked_edits_delegated_and_preserved_on_workflow_refusal(self):
        path = self.lab / '.gitignore'
        path.write_text('delivery/\n# human work preserved for workflow validation\n')
        def fail(command, **kwargs):
            self.calls.append((command, kwargs))
            return subprocess.CompletedProcess(command, 1)
        with self.assertRaisesRegex(launcher.LaunchStop, 'Review workflow stopped'):
            self.run_launch(runner=fail)
        self.assertEqual(path.read_text(), 'delivery/\n# human work preserved for workflow validation\n')
        self.assertEqual(len(self.calls), 1)

    def test_failed_commit_recovery_through_real_launcher_and_workflow(self):
        root = Path(__file__).resolve().parents[1]
        spec = importlib.util.spec_from_file_location('home_workflow039_fixture', root / 'scripts/review039_workflow.py')
        workflow = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(workflow)
        public = {}
        for name in workflow.REQUIRED_CODE:
            raw = (root / name).read_bytes()
            target = self.lab / name
            target.parent.mkdir(exist_ok=True, parents=True)
            target.write_bytes(raw)
            public[name] = raw
        for name in launcher.BOOT_SCRIPTS:
            self.members[name] = public[name]
        packet = {name: raw for name, raw in self.members.items() if name.startswith('packet/')}
        manifest = {'inputs': [{'path': name, 'sha256': workflow.safe.sha(raw)} for name, raw in sorted(public.items())],
                    'bundle_files': [{'path': name, 'sha256': workflow.safe.sha(raw)} for name, raw in sorted(packet.items())]}
        raw = workflow.safe.canonical(manifest)
        path = self.lab / workflow.MANIFEST
        path.parent.mkdir(exist_ok=True, parents=True)
        path.write_bytes(raw)
        self.git('add', '.')
        self.git('commit', '-m', 'Frozen full handoff fixture')
        commit = self.git('rev-parse', 'HEAD').decode().strip()
        self.members['RELEASE.json'] = workflow.safe.canonical({
            'kind': 'P3_FOCUSED_REVIEW_039_RELEASE_v1', 'repository': workflow.REPOSITORY,
            'content_commit': commit, 'manifest_path': workflow.MANIFEST,
            'manifest_sha256': workflow.safe.sha(raw)})
        remote = self.home / 'remote.git'
        subprocess.run(['git', 'init', '--bare', str(remote)], check=True, capture_output=True)
        self.git('push', str(remote), 'main')
        observed = {'controller_calls': 0, 'commit_failure_sent': False}
        def git_runner(command, **kwargs):
            command = list(command)
            action = command[4]
            if action == 'commit' and not observed['commit_failure_sent']:
                observed['commit_failure_sent'] = True
                return subprocess.CompletedProcess(command, 1, b'', b'fixture failed commit')
            if action in ('fetch', 'push', 'ls-remote'):
                command[command.index('origin', 5)] = str(remote)
            return subprocess.run(command, **kwargs)
        def controller(lab, emit):
            observed['controller_calls'] += 1
            path = lab / workflow.MAIN
            path.mkdir()
            (path / 'REPORT.json').write_text('{"fixture":"bounded synthetic report, not a scientific verdict"}\n')
            return {'controller_started': True, 'exit_code': 0}
        def execute(command, **kwargs):
            try:
                workflow.workflow(self.lab, Path(command[-1]), git_runner=git_runner,
                                  controller_runner=controller, emit=lambda value: None)
                return subprocess.CompletedProcess(command, 0)
            except workflow.safe.StageStop:
                return subprocess.CompletedProcess(command, 1)
        raw = self.archive()
        with self.assertRaisesRegex(launcher.LaunchStop, 'Review workflow stopped'):
            self.run_launch(raw, runner=execute)
        self.assertTrue(self.git('diff', '--cached', '--name-only'))
        self.run_launch(raw, runner=execute)
        self.assertEqual(observed['controller_calls'], 1)
        self.assertFalse(self.git('diff', '--cached', '--name-only'))
        remote_head = subprocess.run(['git', '--git-dir', str(remote), 'rev-parse', 'refs/heads/main'],
                                     check=True, capture_output=True).stdout
        self.assertEqual(remote_head, self.git('rev-parse', 'HEAD'))

    def test_minimal_initial_sibling_dependency_closure_imports_offline(self):
        root = Path(__file__).resolve().parents[1]
        minimal = self.home / 'minimal scripts'
        minimal.mkdir()
        names = ('review039_workflow.py', 'stage_source_packet038.py',
                 'review032_workflow.py', 'publish_review039_evidence.py')
        for name in names:
            (minimal / name).write_bytes((root / 'scripts' / name).read_bytes())
        code = ("import importlib.util; s=importlib.util.spec_from_file_location('import_fixture', "
                + repr(str(minimal / 'review039_workflow.py'))
                + "); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(m.PACKET)")
        result = subprocess.run(['python3', '-I', '-B', '-c', code], check=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(result.stdout.decode().strip(), 'delivery/P3_FOCUSED_REVIEW_PACKET_039')




"""Verify filename selection, Windows path translation and checksum-before-code."""
import importlib.util
import io
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import zipfile

SPEC = importlib.util.spec_from_file_location('bootstrap039',
    Path(__file__).resolve().parents[1] / 'scripts/downloads_bootstrap039.py')
BOOT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BOOT)


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.downloads = self.base / 'One Drive' / 'Téléchargements'
        self.downloads.mkdir(parents=True)
        self.marker = self.base / 'executed.json'
        code = ("from pathlib import Path\nimport json\n"
                "Path(" + repr(str(self.marker)) + ").write_text(json.dumps({"
                "'archive': ARCHIVE_PATH, 'bytes': len(ARCHIVE_BYTES)}))\n")
        out = io.BytesIO()
        with zipfile.ZipFile(out, 'w') as archive:
            archive.writestr('launch039_home.py', code)
        self.raw = out.getvalue()
        self.sha = BOOT.hashlib.sha256(self.raw).hexdigest()
        self.commands = []

    def runner(self, command, **kwargs):
        self.commands.append(command)
        self.assertTrue(kwargs['check'])
        self.assertLessEqual(kwargs['timeout'], 20)
        if command[0] == 'wslpath':
            self.assertEqual(command, ['wslpath', '-u', 'D:\\One Drive\\Téléchargements'])
            return subprocess.CompletedProcess(command, 0, (str(self.downloads) + '\n').encode(), b'')
        return subprocess.CompletedProcess(command, 0,
            b'\xef\xbb\xbf' + 'D:\\One Drive\\Téléchargements\r\n'.encode(), b'')

    def invoke(self, runner=None):
        with patch.object(BOOT, 'ZIP_SHA256', self.sha), \
             patch.object(BOOT.subprocess, 'run', runner or self.runner), \
             patch.object(BOOT.shutil, 'which', return_value='/interop/powershell.exe'), \
             patch.object(BOOT.Path, 'home', return_value=self.base):
            BOOT.main()

    def test_redirected_unicode_downloads_and_verified_duplicate_filename(self):
        (self.downloads / BOOT.ZIP_NAME).write_bytes(b'wrong older download')
        name = BOOT.ZIP_NAME.removesuffix('.zip') + ' (1).zip'
        (self.downloads / name).write_bytes(self.raw)
        self.invoke()
        self.assertTrue(self.marker.exists())
        self.assertIn(name, self.marker.read_text())
        self.assertEqual(len(self.commands), 2)

    def test_wrong_archive_never_executes_embedded_code(self):
        (self.downloads / BOOT.ZIP_NAME).write_bytes(self.raw + b'changed')
        with self.assertRaisesRegex(SystemExit, 'failed the release checksum'):
            self.invoke()
        self.assertFalse(self.marker.exists())

    def test_missing_package_gives_actionable_diagnostic_without_writing(self):
        with self.assertRaisesRegex(SystemExit, 'package not found; Downloads discovery: Windows Downloads resolved'):
            self.invoke()
        self.assertFalse(self.marker.exists())

    def test_symlink_and_oversized_downloads_are_not_executed(self):
        target = self.base / 'verified.zip'
        target.write_bytes(self.raw)
        link = self.downloads / BOOT.ZIP_NAME
        link.symlink_to(target)
        with self.assertRaisesRegex(SystemExit, 'package not found'):
            self.invoke()
        self.assertFalse(self.marker.exists())
        link.unlink()
        with link.open('wb') as handle:
            handle.truncate(launcher.MAX_ARCHIVE + 1)
        with self.assertRaisesRegex(SystemExit, 'package not found'):
            self.invoke()
        self.assertFalse(self.marker.exists())

    def test_bootstrap_is_one_literal_python_here_document(self):
        source = (Path(__file__).resolve().parents[1] / 'scripts/downloads_bootstrap039.py').read_text()
        filled = source.replace('__ZIP_SHA256__', self.sha)
        compile(filled, 'download039_fixture.py', 'exec')
        command = "python3 - <<'PY'\n" + filled.rstrip() + "\nPY\n"
        # Parse only: the shell must not execute Windows interop or launcher code.
        result = subprocess.run(['bash', '-n', '-c', command], capture_output=True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(command.count("python3 - <<'PY'"), 1)
        self.assertNotIn('__ZIP_SHA256__', command)

    def test_wsl_downloads_fallback_if_interop_is_unavailable(self):
        folder = self.base / 'Downloads'
        folder.mkdir()
        (folder / BOOT.ZIP_NAME).write_bytes(self.raw)
        def unavailable(*args, **kwargs):
            raise FileNotFoundError('no interop')
        self.invoke(unavailable)
        self.assertTrue(self.marker.exists())


if __name__ == '__main__':
    unittest.main()
