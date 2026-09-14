"""Finite048 publication boundary cases; scientific tests use tiny synthetic fixtures."""
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


w = load('test_checkpoint048_workflow_module', ROOT / 'scripts/checkpoint048_workflow.py')
l = load('test_checkpoint048_launcher_module', ROOT / 'scripts/launch048_home.py')
b = load('test_checkpoint048_builder_module', ROOT / 'scripts/build_checkpoint048.py')


class ConformanceHandoff048(unittest.TestCase):
    def setUp(self):
        (ROOT / 'delivery').mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix='fixture048_', dir=ROOT / 'delivery')
        self.base = Path(self.temporary.name)
        self.home = self.base / 'home'
        self.home.mkdir()
        self.lab, self.source, self.remote = self.home / 'ARC_Independent_Lab', self.base / 'source', self.base / 'remote.git'
        self.git(self.base, 'init', '--bare', '--initial-branch=main', str(self.remote))
        self.git(self.base, 'init', '--initial-branch=main', str(self.source))
        self.configure(self.source)
        self.write(self.source / '.gitignore', b'delivery/\n__pycache__/\n*.pyc\n')
        self.write(self.source / 'PRIOR.txt', b'Accepted history stays unchanged.\n')
        self.git(self.source, 'add', '--', '.gitignore', 'PRIOR.txt')
        self.git(self.source, 'commit', '-m', 'Synthetic accepted047')
        self.parent = self.git(self.source, 'rev-parse', 'HEAD').decode().strip()
        self.git(self.source, 'remote', 'add', 'origin', str(self.remote))
        self.git(self.source, 'push', 'origin', 'main')
        self.git(self.home, 'clone', str(self.remote), str(self.lab))
        self.configure(self.lab)
        for name in l.SOURCE_PATHS:
            if name in ('scripts/launch048_home.py', 'scripts/checkpoint048_workflow.py'):
                raw = (ROOT / name).read_bytes()
            elif name in l.SUITES:
                raw = (b'import unittest\nclass Synthetic048(unittest.TestCase):\n'
                       b'    def test_arithmetic(self):\n        self.assertEqual(2 + 3, 5)\n')
            else:
                raw = b'# Public synthetic fixture; no learner/profile/model.\n'
            self.write(self.source / name, raw)
        self.git(self.source, 'add', '--', *l.SOURCE_PATHS)
        self.git(self.source, 'commit', '-m', 'Synthetic048 release')
        self.commit = self.git(self.source, 'rev-parse', 'HEAD').decode().strip()
        self.git(self.source, 'push', 'origin', 'main')
        self.patches = []
        for module in (l, w.safe, b.safe):
            for key, value in (('REMOTE', str(self.remote)), ('PARENT_COMMIT', self.parent)):
                item = patch.object(module, key, value)
                item.start()
                self.patches.append(item)
        self.addCleanup(lambda: [item.stop() for item in reversed(self.patches)])
        self.addCleanup(self.temporary.cleanup)
        with patch('sys.stdout', new=io.StringIO()):
            built = b.build(self.source, self.base / l.ZIP_NAME)
        self.raw = (self.base / l.ZIP_NAME).read_bytes()
        self.sha = built['archive_sha256']
        self.files, self.release = l.archive_payloads(self.raw, self.sha)
        self.calls = 0
        self.failure = None
        self.real_git = w.safe.git

    def git(self, root, *args):
        return subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', '-C', str(root), *args],
                              capture_output=True, check=True).stdout

    def configure(self, root):
        self.git(root, 'config', 'user.name', 'Synthetic048 Test')
        self.git(root, 'config', 'user.email', 'fixture048@example.invalid')

    def write(self, path, raw):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)

    def child(self, source, release, state, lock_fd):
        self.calls += 1
        return w.run_conformance(source, release, state, lock_fd)

    def controlled_git(self, root, *args, **kwargs):
        if Path(root) == self.lab and args[0] == self.failure:
            self.failure = None
            raise w.safe.Stop('synthetic_publication_failure')
        return self.real_git(root, *args, **kwargs)

    def execute(self):
        result = []
        def runner(command, **kwargs):
            self.assertEqual(command[1:5], ['-I', '-S', '-B', '-u'])
            package = Path(command[command.index('--package') + 1])
            with patch.object(w.safe, 'git', side_effect=self.controlled_git):
                result.append(w.workflow(self.lab, package, self.sha, runner=self.child))
            return subprocess.CompletedProcess(command, 0)
        l.launch(self.raw, self.sha, home=self.home, runner=runner)
        return result[0]

    def state(self):
        return self.lab / '.git/checkpoint048' / self.sha

    def test_exact_result_only_publication_and_completed_reuse(self):
        result = self.execute()
        self.assertEqual(result['status'], 'KERNEL_CONFORMANCE_PASSED')
        self.assertEqual(result, self.execute())
        self.assertEqual(self.calls, 1)
        changed = self.git(self.lab, 'diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD').decode().splitlines()
        self.assertEqual(set(changed), {result['report_path'], result['receipt_path']})
        self.assertEqual(self.git(self.remote, 'rev-parse', 'main').decode().strip(), result['commit'])
        report = json.loads((self.lab / result['report_path']).read_text())
        child = report['conformance_run']['conformance']
        self.assertEqual(child['tests_run'], 2)
        self.assertEqual(child['source_sha256_before'], child['source_sha256_after'])
        self.assertFalse(report['accounting_correction_complete'])
        self.assertFalse(report['target_admitted'])
        for name in ('stdout.raw', 'stderr.raw', 'RESERVED.json', 'RUN.json'):
            self.assertEqual(stat.S_IMODE((self.state() / name).stat().st_mode), 0o600)

    def test_push_and_commit_failures_retry_without_new_conformance(self):
        for failure in ('commit', 'push'):
            with self.subTest(failure=failure):
                self.failure = failure
                if failure == 'push':
                    # A second publication attempt reaches push without creating a new commit.
                    pass
                with self.assertRaisesRegex(w.safe.Stop, 'synthetic_publication_failure'):
                    self.execute()
                self.execute()
                self.assertEqual(self.calls, 1)

    def test_dirty_and_unrelated_committed_work_is_preserved_before_run(self):
        (self.lab / 'PRIOR.txt').write_text('Human local edit\n')
        self.git(self.lab, 'add', '--', 'PRIOR.txt')
        staged = self.git(self.lab, 'diff', '--cached', '--binary')
        with self.assertRaisesRegex(w.safe.Stop, 'dirty_canonical_checkout_preserved'):
            self.execute()
        self.assertEqual(self.calls, 0)
        self.assertEqual(staged, self.git(self.lab, 'diff', '--cached', '--binary'))
        self.git(self.lab, 'commit', '-m', 'Human unpublished change')
        before = self.git(self.lab, 'rev-parse', 'HEAD')
        with self.assertRaisesRegex(w.safe.Stop, 'unrelated_unpublished_local_commit_preserved'):
            self.execute()
        self.assertEqual(before, self.git(self.lab, 'rev-parse', 'HEAD'))
        self.assertEqual(self.calls, 0)

    def test_wrong_origin_and_archive_hash_refuse_before_installation(self):
        with self.assertRaisesRegex(l.Stop, 'outer_archive_sha256_mismatch'):
            l.launch(self.raw, '0' * 64, home=self.home)
        self.git(self.lab, 'remote', 'set-url', 'origin', str(self.base / 'other.git'))
        with self.assertRaisesRegex(l.Stop, 'wrong_authorized_origin'):
            self.execute()
        self.assertFalse((self.lab / 'delivery').exists())
        self.assertEqual(self.calls, 0)

    def test_actual_extracted_workflow_executes_frozen_synthetic_child(self):
        result = []
        def extracted(command, **kwargs):
            module = load('extracted048_workflow', Path(command[5]))
            package = Path(command[command.index('--package') + 1])
            with patch.object(module.safe, 'REMOTE', str(self.remote)), patch.object(module.safe, 'PARENT_COMMIT', self.parent):
                result.append(module.workflow(self.lab, package, self.sha))
            return subprocess.CompletedProcess(command, 0)
        l.launch(self.raw, self.sha, home=self.home, runner=extracted)
        self.assertEqual(result[0]['status'], 'KERNEL_CONFORMANCE_PASSED')
        report = json.loads((self.lab / result[0]['report_path']).read_text())
        self.assertEqual([r['test_id'] for r in report['conformance_run']['conformance']['tests']], self.release['test_ids'])

    def test_interrupted_reservation_is_published_without_automatic_rerun(self):
        def interrupt(source, release, state, lock_fd):
            self.calls += 1
            raise w.safe.Stop('synthetic_interruption')
        self.child = interrupt
        with self.assertRaisesRegex(w.safe.Stop, 'synthetic_interruption'):
            self.execute()
        result = self.execute()
        self.assertEqual(result['status'], 'INTERRUPTED_NO_AUTOMATIC_RERUN')
        self.assertEqual(result, self.execute())
        self.assertEqual(self.calls, 1)

    def test_changed_saved_outcome_and_unknown_public_fields_are_refused(self):
        self.execute()
        path = self.state() / 'RUN.json'
        original = path.read_bytes()
        value = json.loads(original)
        value['private_secret'] = 'must never be published'
        path.write_bytes(l.canonical(value))
        with self.assertRaisesRegex(w.safe.Stop, 'invalid_saved_run_schema'):
            self.execute()
        self.assertEqual(self.calls, 1)
        path.write_bytes(original)
        value = json.loads(original)
        value['conformance']['tests'][0]['status'] = 'FAILED'
        value['conformance']['status'] = 'KERNEL_CONFORMANCE_FAILED'
        value['status'] = 'KERNEL_CONFORMANCE_FAILED'
        value['returncode'] = 1
        path.write_bytes(l.canonical(value))
        with self.assertRaisesRegex(w.safe.Stop, 'saved_conformance_differs_from_private_stdout'):
            self.execute()
        path.write_bytes(original)
        report = value['conformance']
        report['unexpected'] = 'private data'
        with self.assertRaisesRegex(w.safe.Stop, 'child_report_identity_or_scope_differs'):
            w.validate_child_report(report, self.release)

    def test_remote_changed_result_and_ignored_file_are_preserved(self):
        self.write(self.lab / '.git/info/exclude', b'scripts/\n')
        occupied = self.lab / 'scripts/accounting048.py'
        self.write(occupied, b'Human ignored file\n')
        with self.assertRaisesRegex(w.safe.Stop, 'git_merge_failed'):
            self.execute()
        self.assertEqual(occupied.read_bytes(), b'Human ignored file\n')
        self.assertEqual(self.calls, 0)
        occupied.unlink()
        result = self.execute()
        original = (self.lab / result['report_path']).read_bytes()
        self.git(self.source, 'fetch', 'origin', 'main')
        self.git(self.source, 'merge', '--ff-only', 'FETCH_HEAD')
        self.write(self.source / result['report_path'], b'{"human":"changed remote"}\n')
        self.git(self.source, 'add', '--', result['report_path'])
        self.git(self.source, 'commit', '-m', 'Changed remote conformance report')
        self.git(self.source, 'push', 'origin', 'main')
        with self.assertRaisesRegex(w.safe.Stop, 'changed_remote048_result_preserved'):
            self.execute()
        self.assertEqual((self.lab / result['report_path']).read_bytes(), original)
        self.assertEqual(self.calls, 1)

    def test_downloads_resolution_uses_exact_windows_known_folder(self):
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
            self.assertEqual(l.downloads_archive(), folder / 'ARC_Independent_Lab_048_HOME.zip')
        self.assertEqual(len(calls), 2)


if __name__ == '__main__':
    unittest.main()
