"""047 dangerous-boundary tests use synthetic evidence and a local bare Git server."""
from __future__ import annotations

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
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


w = load('checkpoint047_test_workflow', ROOT / 'scripts/checkpoint047_workflow.py')
l = load('checkpoint047_test_launcher', ROOT / 'scripts/launch047_home.py')


class Offline047(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='fixture047_', dir=ROOT.parent)
        self.base = Path(self.temporary.name)
        self.home = self.base / 'home'
        self.home.mkdir()
        self.lab = self.home / 'ARC_Independent_Lab'
        self.source = self.base / 'source'
        self.remote = self.base / 'remote.git'
        self.run_git(self.base, 'init', '--bare', '--initial-branch=main', str(self.remote))
        self.run_git(self.base, 'init', '--initial-branch=main', str(self.source))
        self.configure(self.source)
        self.write(self.source / '.gitignore', b'delivery/\n__pycache__/\n*.pyc\n')
        self.write(self.source / 'PRIOR_RETURN.txt', b'Prior measurements stay byte identical.\n')
        self.run_git(self.source, 'add', '--', '.gitignore', 'PRIOR_RETURN.txt')
        self.run_git(self.source, 'commit', '-m', 'Synthetic accepted prior return')
        self.accepted = self.run_git(self.source, 'rev-parse', 'HEAD').decode().strip()
        self.run_git(self.source, 'remote', 'add', 'origin', str(self.remote))
        self.run_git(self.source, 'push', 'origin', 'main')
        self.run_git(self.home, 'clone', str(self.remote), str(self.lab))
        self.configure(self.lab)
        self.assessment = {'kind': 'SYNTHETIC047_FIXTURE', 'status': 'VERIFIED',
                           'prior_profiles_started': False}
        self.write(self.source / l.ASSESSMENT, l.canonical(self.assessment))
        self.write(self.source / 'scripts/assess_return046.py',
            b'import argparse,json\nfrom pathlib import Path\np=argparse.ArgumentParser()\n'
            b'p.add_argument("--repo",type=Path); p.add_argument("--output",type=Path)\na=p.parse_args()\n'
            b'v=json.loads((a.repo/"evidence/P3_CHECKPOINT_046_RETURN_VERIFICATION_047.json").read_text())\n'
            b'a.output.write_text(json.dumps(v,sort_keys=True,indent=2)+"\\n")\n')
        for name in ('launch047_home.py', 'checkpoint047_workflow.py'):
            self.write(self.source / 'scripts' / name, (ROOT / 'scripts' / name).read_bytes())
        self.run_git(self.source, 'add', '--', 'scripts', 'evidence')
        self.run_git(self.source, 'commit', '-m', 'Synthetic047 release')
        self.release_commit = self.run_git(self.source, 'rev-parse', 'HEAD').decode().strip()
        self.run_git(self.source, 'push', 'origin', 'main')
        self.bundle = self.base / 'repo.bundle'
        self.run_git(self.source, 'bundle', 'create', str(self.bundle), 'main')
        self.release = {'kind': 'P3_CHECKPOINT_047_RELEASE_v1', 'repository': l.REPOSITORY,
                        'release_commit': self.release_commit,
                        'bundle_sha256': l.sha(self.bundle.read_bytes()),
                        'assessment_path': l.ASSESSMENT,
                        'assessment_sha256': l.sha(l.canonical(self.assessment))}
        self.files = {'repo.bundle': self.bundle.read_bytes(),
                      'package_release.json': l.canonical(self.release),
                      'README_047.md': b'Synthetic offline handoff fixture.\n'}
        for name in ('launch047_home.py', 'checkpoint047_workflow.py'):
            self.files[name] = (ROOT / 'scripts' / name).read_bytes()
        self.raw = self.make_zip(self.files)
        self.archive_sha = l.sha(self.raw)
        self.calls = 0
        self.failure = None
        self.real_git = w.safe.git
        self.launch_remote = patch.object(l, 'REMOTE', str(self.remote))
        self.workflow_remote = patch.object(w.safe, 'REMOTE', str(self.remote))
        self.launch_remote.start()
        self.workflow_remote.start()

    def tearDown(self):
        self.workflow_remote.stop()
        self.launch_remote.stop()
        self.temporary.cleanup()

    def run_git(self, root, *args):
        result = subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', '-C', str(root), *args],
                                capture_output=True, check=True)
        return result.stdout

    def configure(self, root):
        self.run_git(root, 'config', 'user.name', 'Synthetic047 Test')
        self.run_git(root, 'config', 'user.email', 'fixture047@example.invalid')

    def write(self, path, raw):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)

    def make_zip(self, files):
        files = dict(files)
        files['SHA256SUMS'] = ''.join(l.sha(body) + '  ' + name + '\n'
                                    for name, body in sorted(files.items())).encode()
        target = io.BytesIO()
        with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
            for name, body in files.items():
                info = zipfile.ZipInfo(name)
                info.external_attr = (stat.S_IFREG | 0o600) << 16
                archive.writestr(info, body)
        return target.getvalue()

    def assessor(self, snapshot, output):
        self.calls += 1
        w.run_assessor(snapshot, output)

    def git_with_failure(self, root, *args, **kwargs):
        if Path(root) == self.lab and args[0] == self.failure:
            self.failure = None
            raise w.safe.Stop('synthetic_publication_failure')
        return self.real_git(root, *args, **kwargs)

    def execute(self):
        received = []
        def runner(command, **kwargs):
            self.assertEqual(command[1:5], ['-I', '-S', '-B', '-u'])
            package = Path(command[command.index('--package') + 1])
            with patch.object(w.safe, 'git', side_effect=self.git_with_failure):
                result = w.workflow(self.lab, package, self.archive_sha, assessor=self.assessor)
            received.append(result)
            return subprocess.CompletedProcess(command, 0)
        l.launch(self.raw, self.archive_sha, home=self.home, runner=runner)
        return received[0]

    def test_complete_bundle_from_old_checkout_and_repeat_without_reexecution(self):
        result = self.execute()
        self.assertEqual(self.calls, 1)
        self.assertEqual(result, self.execute())
        self.assertEqual(self.calls, 1)
        self.assertEqual(self.run_git(self.remote, 'rev-parse', 'main').decode().strip(), result['commit'])
        self.assertEqual((self.lab / 'PRIOR_RETURN.txt').read_bytes(),
                         b'Prior measurements stay byte identical.\n')
        self.assertEqual(set(self.run_git(self.lab, 'diff-tree', '--no-commit-id', '--name-only',
                                         '-r', 'HEAD').decode().splitlines()),
                         {result['report_path'], result['receipt_path']})
        snapshot = self.lab / 'delivery/P3_CHECKPOINT_047' / self.archive_sha / 'snapshot'
        self.assertEqual(self.run_git(snapshot, 'rev-parse', 'HEAD').decode().strip(), self.release_commit)
        self.assertEqual(self.run_git(snapshot, 'show', self.accepted + ':PRIOR_RETURN.txt'),
                         b'Prior measurements stay byte identical.\n')

    def test_wrong_outer_hash_and_wrong_inventory_do_not_write(self):
        with self.assertRaisesRegex(l.Stop, 'outer_archive_sha256_mismatch'):
            l.launch(self.raw, '0' * 64, home=self.home)
        changed = dict(self.files)
        changed['../escape'] = b'bad'
        raw = self.make_zip(changed)
        with self.assertRaisesRegex(l.Stop, 'archive_inventory_differs'):
            l.launch(raw, l.sha(raw), home=self.home)
        self.assertFalse((self.lab / 'delivery').exists())

    def test_wrong_bundle_hash_and_wrong_origin_are_refused(self):
        changed = dict(self.files)
        metadata = dict(self.release, bundle_sha256='0' * 64)
        changed['package_release.json'] = l.canonical(metadata)
        raw = self.make_zip(changed)
        with self.assertRaisesRegex(l.Stop, 'invalid_release_pin'):
            l.launch(raw, l.sha(raw), home=self.home)
        self.run_git(self.lab, 'remote', 'set-url', 'origin', str(self.base / 'wrong.git'))
        with self.assertRaisesRegex(l.Stop, 'wrong_authorized_origin'):
            self.execute()
        self.assertFalse((self.lab / 'delivery').exists())
        self.assertEqual(self.calls, 0)

    def test_dirty_tracked_staged_and_untracked_checkout_is_preserved(self):
        for staged in (False, True):
            with self.subTest(staged=staged):
                (self.lab / 'PRIOR_RETURN.txt').write_text('Human change\n')
                if staged:
                    self.run_git(self.lab, 'add', '--', 'PRIOR_RETURN.txt')
                before = self.run_git(self.lab, 'diff', '--cached', '--binary')
                with self.assertRaisesRegex(w.safe.Stop, 'dirty_canonical_checkout_preserved'):
                    self.execute()
                self.assertEqual(self.calls, 0)
                self.assertEqual(before, self.run_git(self.lab, 'diff', '--cached', '--binary'))
                self.assertEqual((self.lab / 'PRIOR_RETURN.txt').read_text(), 'Human change\n')
                self.run_git(self.lab, 'restore', '--staged', '--worktree', 'PRIOR_RETURN.txt')
        (self.lab / 'human_notes.txt').write_text('Preserve me\n')
        with self.assertRaisesRegex(w.safe.Stop, 'dirty_canonical_checkout_preserved'):
            self.execute()
        self.assertEqual(self.calls, 0)

    def test_push_failure_retries_saved_assessment_and_existing_commit(self):
        self.failure = 'push'
        with self.assertRaisesRegex(w.safe.Stop, 'synthetic_publication_failure'):
            self.execute()
        head = self.run_git(self.lab, 'rev-parse', 'HEAD')
        self.assertEqual(self.calls, 1)
        result = self.execute()
        self.assertEqual(self.calls, 1)
        self.assertEqual(head.decode().strip(), result['commit'])

    def test_remote_descendant_fast_forward_reuses_assessment(self):
        first = self.execute()
        self.run_git(self.source, 'fetch', 'origin', 'main')
        self.run_git(self.source, 'merge', '--ff-only', 'FETCH_HEAD')
        self.write(self.source / 'NEW_PUBLIC_NOTE.md', b'A subsequent public note.\n')
        self.run_git(self.source, 'add', '--', 'NEW_PUBLIC_NOTE.md')
        self.run_git(self.source, 'commit', '-m', 'Synthetic subsequent public note')
        self.run_git(self.source, 'push', 'origin', 'main')
        result = self.execute()
        self.assertEqual(self.calls, 1)
        self.assertNotEqual(first['commit'], result['commit'])
        self.assertEqual((self.lab / 'NEW_PUBLIC_NOTE.md').read_bytes(), b'A subsequent public note.\n')

    def test_remote_changed_result_is_refused_without_overwriting_local(self):
        first = self.execute()
        original = (self.lab / first['report_path']).read_bytes()
        self.run_git(self.source, 'fetch', 'origin', 'main')
        self.run_git(self.source, 'merge', '--ff-only', 'FETCH_HEAD')
        self.write(self.source / first['report_path'], b'{"changed":"remote"}\n')
        self.run_git(self.source, 'add', '--', first['report_path'])
        self.run_git(self.source, 'commit', '-m', 'Synthetic changed remote output')
        self.run_git(self.source, 'push', 'origin', 'main')
        with self.assertRaisesRegex(w.safe.Stop, 'changed_remote047_result_preserved'):
            self.execute()
        self.assertEqual(self.calls, 1)
        self.assertEqual((self.lab / first['report_path']).read_bytes(), original)

    def test_actual_extracted_workflow_uses_complete_package_and_real_synthetic_child(self):
        completed = []
        def run_extracted(command, **kwargs):
            module = load('extracted047_fixture', Path(command[5]))
            package = Path(command[command.index('--package') + 1])
            with patch.object(module.safe, 'REMOTE', str(self.remote)):
                completed.append(module.workflow(self.lab, package, self.archive_sha))
            return subprocess.CompletedProcess(command, 0)
        l.launch(self.raw, self.archive_sha, home=self.home, runner=run_extracted)
        result = completed[0]
        report = json.loads((self.lab / result['report_path']).read_text())
        self.assertEqual(report['assessment'], self.assessment)
        self.assertFalse(report['target_experiment_started'])
        self.assertEqual(self.run_git(self.remote, 'rev-parse', 'main').decode().strip(), result['commit'])

    def test_commit_failure_recovers_exact_staged_outputs_without_reexecution(self):
        self.failure = 'commit'
        with self.assertRaisesRegex(w.safe.Stop, 'synthetic_publication_failure'):
            self.execute()
        self.assertEqual(self.calls, 1)
        self.assertTrue(self.run_git(self.lab, 'diff', '--cached', '--name-only'))
        self.execute()
        self.assertEqual(self.calls, 1)

    def test_changed_saved_and_canonical_results_are_preserved(self):
        result = self.execute()
        path = self.lab / result['report_path']
        path.write_text('{"human":"changed"}\n')
        with self.assertRaisesRegex(w.safe.Stop, 'changed047_output_preserved'):
            self.execute()
        self.assertEqual(self.calls, 1)
        self.assertEqual(path.read_text(), '{"human":"changed"}\n')
        self.run_git(self.lab, 'restore', '--', result['report_path'])
        state = self.lab / 'delivery/P3_CHECKPOINT_047' / self.archive_sha / 'state'
        (state / 'REPORT.json').write_text('{"human":"saved change"}\n')
        with self.assertRaisesRegex(w.safe.Stop, 'changed_saved_result_preserved'):
            self.execute()
        self.assertEqual(self.calls, 1)

    def test_mismatched_assessment_never_publishes_or_reexecutes(self):
        def bad_assessor(snapshot, output):
            self.calls += 1
            output.write_text('{"unexpected":"change"}\n')
        self.assessor = bad_assessor
        for attempt in range(2):
            with self.assertRaisesRegex(w.safe.Stop, 'offline_result_differs'):
                self.execute()
        self.assertEqual(self.calls, 1)
        self.assertEqual(self.run_git(self.lab, 'rev-parse', 'HEAD').decode().strip(), self.accepted)
        self.assertFalse((self.lab / 'artifacts').exists())

    def test_interrupted_read_only_parser_without_output_retries_safely(self):
        original = self.assessor
        def interrupted(snapshot, output):
            self.calls += 1
            raise w.safe.Stop('synthetic_read_only_parser_interruption')
        self.assessor = interrupted
        with self.assertRaisesRegex(w.safe.Stop, 'synthetic_read_only_parser_interruption'):
            self.execute()
        self.assertEqual(self.calls, 1)
        self.assessor = original
        result = self.execute()
        self.assertEqual(self.calls, 2)
        self.assertEqual(result, self.execute())
        self.assertEqual(self.calls, 2)
        report = json.loads((self.lab / result['report_path']).read_text())
        self.assertFalse(report['prior_measurements_reexecuted'])

    def test_fast_forward_does_not_overwrite_ignored_local_file(self):
        self.write(self.lab / '.git/info/exclude', b'scripts/\n')
        occupied = self.lab / 'scripts/assess_return046.py'
        self.write(occupied, b'Human ignored file must survive.\n')
        with self.assertRaisesRegex(w.safe.Stop, 'git_merge_failed'):
            self.execute()
        self.assertEqual(occupied.read_bytes(), b'Human ignored file must survive.\n')
        self.assertEqual(self.run_git(self.lab, 'rev-parse', 'HEAD').decode().strip(), self.accepted)
        self.assertEqual(self.calls, 1)

    def test_unrelated_clean_local_commit_is_not_published(self):
        self.run_git(self.lab, 'fetch', 'origin', 'main')
        self.run_git(self.lab, 'merge', '--ff-only', 'FETCH_HEAD')
        self.write(self.lab / 'UNPUBLISHED_NOTE.md', b'Human unpublished note.\n')
        self.run_git(self.lab, 'add', '--', 'UNPUBLISHED_NOTE.md')
        self.run_git(self.lab, 'commit', '-m', 'Human unrelated unpublished work')
        head = self.run_git(self.lab, 'rev-parse', 'HEAD')
        with self.assertRaisesRegex(w.safe.Stop, 'unrelated_unpublished_local_commit_preserved'):
            self.execute()
        self.assertEqual(self.run_git(self.lab, 'rev-parse', 'HEAD'), head)
        self.assertEqual(self.run_git(self.remote, 'rev-parse', 'main').decode().strip(), self.release_commit)
        self.assertEqual((self.lab / 'UNPUBLISHED_NOTE.md').read_bytes(), b'Human unpublished note.\n')

    def test_snapshot_ignored_additions_are_rejected_without_new_assessment(self):
        self.execute()
        snapshot = self.lab / 'delivery/P3_CHECKPOINT_047' / self.archive_sha / 'snapshot'
        self.write(snapshot / 'delivery/hidden.py', b'Never run this.\n')
        with self.assertRaisesRegex(w.safe.Stop, 'snapshot_extra_or_missing_files'):
            self.execute()
        self.assertEqual(self.calls, 1)

    def test_downloads_uses_registry_exact_filename_and_never_guesses_users(self):
        folder = self.base / 'Downloads with spaces'
        folder.mkdir()
        calls = []
        def resolve(command, **kwargs):
            calls.append(command)
            if command[0] == 'wslpath':
                self.assertEqual(command[1:], ['-u', r'C:\Users\Exact Name\Downloads'])
                return subprocess.CompletedProcess(command, 0, (str(folder) + '\n').encode())
            self.assertIn('User Shell Folders', command[-1])
            return subprocess.CompletedProcess(command, 0, b'\xef\xbb\xbfC:\\Users\\Exact Name\\Downloads\r\n')
        with patch.object(l.subprocess, 'run', side_effect=resolve):
            self.assertEqual(l.downloads_archive(), folder / 'ARC_Independent_Lab_047_HOME.zip')
        self.assertEqual(len(calls), 2)


if __name__ == '__main__':
    unittest.main()
