"""Actual offline041 workflow and extracted launcher, using explicit local Git fixtures.

Only transport endpoints and the immutable historical commit are substituted.
The verifier fixture is a pinned source file loaded through the production API;
it is plainly synthetic and neither a reviewer nor scientific evidence.
"""
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


w = load('workflow041_test', ROOT / 'scripts/checkpoint041_workflow.py')
l = load('launcher041_test', ROOT / 'scripts/launch041_home.py')
b = load('bootstrap041_test', ROOT / 'scripts/downloads_bootstrap041.py')


class HandoffTests(unittest.TestCase):
    def setUp(self):
        temp_root = ROOT / 'delivery' / 'tests041'
        temp_root.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=temp_root)
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name) / 'home with espace é'
        self.lab = self.home / 'ARC_Independent_Lab'
        self.lab.mkdir(parents=True)
        self.bundle = self.lab / 'delivery' / 'fixture_bundle'
        self.bundle.mkdir(parents=True)
        self.remote = Path(self.temp.name) / 'remote.git'
        self.raw_git('init', '--bare', str(self.remote))
        self.git('init', '-b', 'main')
        self.git('config', 'user.name', 'Offline041 fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        (self.lab / '.gitignore').write_text('delivery/\n')
        self.git('add', '.gitignore')
        self.git('commit', '-m', 'Fixture accepted return ancestor')
        self.accepted = self.git('rev-parse', 'HEAD').decode().strip()
        self.commands = []
        self.fail_action = None
        verifier = ("def verify(root, packet):\n"
            "    assert (packet / 'BROKER_MANIFEST.json').read_bytes() == b'private fixture\\n'\n"
            "    return {'kind':'P3_ORIGINAL_RETURN_VERIFICATION_041_v1',"
            "'integrity_verified':True,'scope':'EXPLICIT_OFFLINE_FIXTURE_ONLY'}\n").encode()
        self.public = {name: (verifier if name == w.VERIFIER else (ROOT / name).read_bytes())
                       for name in w.REQUIRED_CODE}
        self.public['state/PROJECT_STATE.json'] = b'{"fixture":"frozen mutable state snapshot"}\n'
        self.private = {'private/BROKER_MANIFEST.json': b'private fixture\n'}
        self.make_release()
        self.git('remote', 'add', 'origin', w.safe.REMOTE)
        self.git('push', str(self.remote), 'main')

    def raw_git(self, *args):
        return subprocess.run(['git', *args], check=True, capture_output=True).stdout

    def git(self, *args):
        return self.raw_git('-C', str(self.lab), *args)

    def write(self, path, raw):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)

    def make_release(self):
        self.manifest = {'kind': 'P3_CHECKPOINT_041_MANIFEST_v1',
            'inputs': [{'path': name, 'sha256': w.safe.sha(raw)}
                       for name, raw in sorted(self.public.items())],
            'private_files': [{'path': name, 'sha256': w.safe.sha(raw)}
                              for name, raw in sorted(self.private.items())]}
        manifest_raw = w.safe.canonical(self.manifest)
        for name, raw in self.public.items():
            self.write(self.lab / name, raw)
            self.write(self.bundle / 'public' / name, raw)
        for name, raw in self.private.items():
            self.write(self.bundle / name, raw)
        self.write(self.lab / w.MANIFEST, manifest_raw)
        self.write(self.bundle / 'public' / w.MANIFEST, manifest_raw)
        for name in ('checkpoint041_workflow.py', 'stage_source_packet038.py'):
            self.write(self.bundle / 'scripts' / name, self.public['scripts/' + name])
        self.write(self.bundle / 'launch041_home.py', self.public['scripts/launch041_home.py'])
        self.git('add', '.')
        self.git('commit', '-m', 'Fixture041 frozen release')
        self.content = self.git('rev-parse', 'HEAD').decode().strip()
        self.release = {'kind': 'P3_CHECKPOINT_041_RELEASE_v1', 'repository': w.REPOSITORY,
            'content_commit': self.content, 'accepted_return_commit': self.accepted,
            'manifest_path': w.MANIFEST, 'manifest_sha256': w.safe.sha(manifest_raw)}
        self.write(self.bundle / 'package_release.json', w.safe.canonical(self.release))

    def runner(self, command, **kwargs):
        command = list(command)
        self.commands.append(command[:])
        self.assertEqual(command[0], 'git')
        action = command[command.index('-C') + 2]
        if action == self.fail_action:
            self.fail_action = None
            return subprocess.CompletedProcess(command, 1, b'', b'fixture transport failure')
        if action in ('fetch', 'push', 'ls-remote'):
            command[command.index('origin')] = str(self.remote)
        return subprocess.run(command, **kwargs)

    def execute(self, module=w, bundle=None):
        with patch.object(module, 'RETURN_COMMIT', self.accepted):
            return module.workflow(self.lab, bundle or self.bundle,
                git_runner=self.runner, emit=lambda value: None)

    def test_real_workflow_publishes_only_receipt_and_repeat_is_identical(self):
        first = self.execute()
        second = self.execute()
        self.assertEqual(first, second)
        self.assertTrue(first['integrity_verified'])
        self.assertEqual(self.git('diff', '--name-only', self.content, 'HEAD').decode().splitlines(),
                         [first['receipt_path']])
        receipt = json.loads((self.lab / first['receipt_path']).read_text())
        self.assertEqual(receipt['native_starts'], 0)
        self.assertEqual(receipt['model_turns_sent'], 0)
        self.assertFalse(receipt['candidate_or_experiment_started'])
        self.assertFalse(receipt['future_experiment_admission'])
        self.assertNotIn('private fixture', (self.lab / first['receipt_path']).read_text())
        self.assertFalse(self.git('status', '--porcelain'))
        self.assertEqual(self.raw_git('--git-dir', str(self.remote), 'rev-parse', 'refs/heads/main'),
                         self.git('rev-parse', 'HEAD'))

    def test_failed_push_retries_same_commit_and_failed_commit_retries_exact_index(self):
        for action in ('commit', 'push'):
            with self.subTest(action=action):
                self.fail_action = action
                with self.assertRaisesRegex(w.safe.StageStop, 'git_' + action + '_failed'):
                    self.execute()
                old_head = self.git('rev-parse', 'HEAD')
                before = len([c for c in self.commands if c[c.index('-C') + 2] == 'commit'])
                result = self.execute()
                if action == 'push':
                    self.assertEqual(old_head, self.git('rev-parse', 'HEAD'))
                    self.assertEqual(before, len([c for c in self.commands if c[c.index('-C') + 2] == 'commit']))
                self.assertTrue(result['integrity_verified'])
                if action == 'commit':
                    # A second independent fixture release makes a new receipt
                    # without rewriting a previously published result.
                    self.public['docs/fixture_revision.md'] = b'Release revision fixture.\n'
                    self.make_release()
                    self.git('push', str(self.remote), 'main')

    def test_current_state_can_advance_but_frozen_snapshot_is_used(self):
        path = self.lab / 'state/PROJECT_STATE.json'
        path.write_text('{"fixture":"later state"}\n')
        self.git('add', str(path))
        self.git('commit', '-m', 'Later mutable state fixture')
        self.git('push', str(self.remote), 'main')
        self.assertTrue(self.execute()['integrity_verified'])
        self.assertIn('later state', path.read_text())

    def test_wrong_public_or_private_bytes_stop_without_receipt(self):
        for name in ('public/' + w.VERIFIER, 'private/BROKER_MANIFEST.json'):
            path = self.bundle / name
            raw = path.read_bytes()
            path.write_bytes(raw + b'altered')
            with self.subTest(name=name), self.assertRaises(w.safe.StageStop):
                self.execute()
            path.write_bytes(raw)
        self.assertFalse((self.lab / 'artifacts').exists())
        self.assertFalse(any(c[c.index('-C') + 2] == 'push' for c in self.commands))

    def test_verifier_failure_returns_small_failure_receipt_without_exception_content(self):
        def failure(bundle):
            raise ValueError('PRIVATE DEPENDENCY CONTENT MUST NOT PUBLISH')
        with patch.object(w, 'RETURN_COMMIT', self.accepted):
            result = w.workflow(self.lab, self.bundle, git_runner=self.runner,
                                verifier_runner=failure, emit=lambda value: None)
        self.assertFalse(result['integrity_verified'])
        text = (self.lab / result['receipt_path']).read_text()
        self.assertIn('ValueError', text)
        self.assertNotIn('PRIVATE DEPENDENCY CONTENT', text)
        self.assertNotIn('private fixture', text)

    def test_changed_staged_receipt_and_unrelated_work_are_preserved(self):
        self.fail_action = 'commit'
        with self.assertRaises(w.safe.StageStop):
            self.execute()
        receipt = next((self.lab / 'artifacts').rglob('RECEIPT.json'))
        receipt.write_text('{"human":"preserve me"}\n')
        before = self.git('diff', '--cached', '--binary')
        with self.assertRaisesRegex(w.safe.StageStop, 'changed_staged041_receipt_preserved'):
            self.execute()
        self.assertEqual(before, self.git('diff', '--cached', '--binary'))
        self.assertIn('preserve me', receipt.read_text())

    def test_dirty_tracked_file_and_unpublished_unrelated_commit_stop(self):
        path = self.lab / 'state/PROJECT_STATE.json'
        path.write_text('human work\n')
        with self.assertRaisesRegex(w.safe.StageStop, 'unrelated_tracked_or_staged'):
            self.execute()
        self.git('add', str(path))
        self.git('commit', '-m', 'Unpublished human work')
        with self.assertRaisesRegex(w.safe.StageStop, 'unpublished_commit_is_not_exact041'):
            self.execute()
        self.assertEqual(path.read_text(), 'human work\n')
        self.assertFalse(any(c[c.index('-C') + 2] == 'push' for c in self.commands))

    def test_publication_does_not_execute_configured_repository_hook(self):
        marker = self.lab / 'delivery/hook_was_executed.txt'
        hook = self.lab / '.git/hooks/pre-commit'
        hook.write_text('#!/bin/sh\nprintf fixture > "' + str(marker) + '"\nexit 1\n')
        hook.chmod(0o700)
        result = self.execute()
        self.assertTrue(result['integrity_verified'])
        self.assertFalse(marker.exists())

    def package(self, extra=None, override=None):
        files = {path.relative_to(self.bundle).as_posix(): path.read_bytes()
                 for path in self.bundle.rglob('*') if path.is_file()}
        files['README_041.md'] = b'Explicit offline handoff fixture.\n'
        files.update(extra or {})
        files['SHA256SUMS'] = ''.join(l.digest(raw) + '  ' + name + '\n'
            for name, raw in sorted(files.items())).encode()
        files.update(override or {})
        output = io.BytesIO()
        with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
            for name, raw in files.items():
                info = zipfile.ZipInfo(name)
                info.external_attr = (stat.S_IFREG | 0o600) << 16
                archive.writestr(info, raw)
        return output.getvalue()

    def launcher_runner(self, command, **kwargs):
        self.assertEqual(command[1:3], ['-B', '-u'])
        self.assertEqual(Path(command[3]).name, 'checkpoint041_workflow.py')
        module = load('extracted041_workflow_fixture', command[3])
        try:
            self.execute(module, Path(command[-1]))
            return subprocess.CompletedProcess(command, 0)
        except module.safe.StageStop:
            return subprocess.CompletedProcess(command, 1)

    def test_actual_extracted_launcher_workflow_push_retry_and_complete_inventory(self):
        raw = self.package(extra={'public/artifacts/fixture/REPORT.sha256': b'a' * 64 + b'\n'})
        # Extra public files are correctly rejected by workflow's exact snapshot.
        with self.assertRaisesRegex(l.LaunchStop, 'Offline verification workflow stopped'):
            l.launch(raw, home=self.home, runner=self.launcher_runner)
        raw = self.package()
        self.fail_action = 'push'
        with self.assertRaises(l.LaunchStop):
            l.launch(raw, home=self.home, runner=self.launcher_runner)
        current = self.git('rev-parse', 'HEAD')
        bundle = l.launch(raw, home=self.home, runner=self.launcher_runner)
        self.assertEqual((bundle.parent / 'PACKAGE.zip').read_bytes(), raw)
        self.assertEqual(current, self.git('rev-parse', 'HEAD'))
        self.assertFalse(self.git('ls-files', '--', l.STEM))

    def test_archive_tamper_traversal_and_existing_edits_preserved(self):
        for raw in (self.package(override={'package_release.json': b'changed'}),
                    self.package(extra={'../escape.py': b'bad'})):
            with self.assertRaises(l.LaunchStop):
                l.launch(raw, home=self.home, runner=self.launcher_runner)
        self.assertFalse((self.lab / l.STEM).exists())
        raw = self.package()
        target = self.lab / l.STEM / l.digest(raw) / 'bundle/package_release.json'
        self.write(target, b'prior changed bytes')
        with self.assertRaises(l.LaunchStop):
            l.launch(raw, home=self.home, runner=self.launcher_runner)
        self.assertEqual(target.read_bytes(), b'prior changed bytes')

    def test_redirected_downloads_and_checksum_before_embedded_launcher(self):
        folder = self.home / 'One Drive Téléchargements'
        folder.mkdir()
        marker = self.lab / 'delivery/bootstrap_marker.txt'
        source = 'from pathlib import Path\nPath(' + repr(str(marker)) + ').write_text("fixture")\n'
        output = io.BytesIO()
        with zipfile.ZipFile(output, 'w') as archive:
            archive.writestr('launch041_home.py', source)
        raw = output.getvalue()
        (folder / b.ZIP_NAME).write_bytes(raw + b'wrong')
        (folder / (b.ZIP_NAME.removesuffix('.zip') + ' (1).zip')).write_bytes(raw)
        def discover(command, **kwargs):
            text = str(folder) if command[0] == 'wslpath' else 'D:\\One Drive Téléchargements'
            return subprocess.CompletedProcess(command, 0, (text + '\n').encode(), b'')
        with patch.object(b, 'ZIP_SHA256', l.digest(raw)), \
             patch.object(b.subprocess, 'run', discover), \
             patch.object(b.shutil, 'which', return_value='/fixture/powershell.exe'), \
             patch.object(b.Path, 'home', return_value=self.home):
            b.main()
        self.assertEqual(marker.read_text(), 'fixture')

    def test_command_template_shell_parses_and_has_no_native_call(self):
        source = (ROOT / 'scripts/downloads_bootstrap041.py').read_text().replace('__ZIP_SHA256__', 'a' * 64)
        command = "python3 - <<'PY'\n" + source.rstrip() + '\nPY\n'
        result = subprocess.run(['bash', '-n', '-c', command], capture_output=True)
        self.assertEqual(result.returncode, 0)
        self.assertNotIn('__ZIP_SHA256__', command)
        self.assertNotIn('run-attended-review', (ROOT / 'scripts/checkpoint041_workflow.py').read_text())


if __name__ == '__main__':
    unittest.main()
