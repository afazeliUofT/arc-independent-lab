"""Offline Git fixtures: one controller call, safe return, and publication recovery."""
import importlib.util
import fcntl
import os
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('workflow039_fixture', ROOT / 'scripts/review039_workflow.py')
w = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(w)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.lab, self.bundle, self.remote = [self.base / name for name in ('lab', 'bundle', 'remote.git')]
        self.lab.mkdir()
        self.bundle.mkdir()
        self.commands = []
        self.native_calls = 0
        self.fail_push = False
        self.fail_commit = False
        self.git_raw('init', '--bare', str(self.remote))
        self.git('init', '-b', 'main')
        self.git('config', 'user.name', 'Review fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        (self.lab / '.gitignore').write_text('delivery/\n')
        self.public = {}
        for name in sorted(w.REQUIRED_CODE):
            src = ROOT / name
            raw = src.read_bytes() if src.is_file() else b'{}\n'
            self.public[name] = raw
            target = self.lab / name
            target.parent.mkdir(exist_ok=True, parents=True)
            target.write_bytes(raw)
        self.packet = b'{"fixture":"private page indexes only"}\n'
        (self.bundle / 'packet').mkdir()
        (self.bundle / 'packet/MANIFEST.json').write_bytes(self.packet)
        manifest = {'inputs': [{'path': name, 'sha256': w.safe.sha(raw)}
                              for name, raw in sorted(self.public.items())],
                    'bundle_files': [{'path': 'packet/MANIFEST.json', 'sha256': w.safe.sha(self.packet)}]}
        manifest_raw = w.safe.canonical(manifest)
        (self.lab / w.MANIFEST).parent.mkdir(exist_ok=True)
        (self.lab / w.MANIFEST).write_bytes(manifest_raw)
        self.git('add', '.')
        self.git('commit', '-m', 'Frozen fixture039')
        self.content = self.git('rev-parse', 'HEAD').decode().strip()
        self.git('remote', 'add', 'origin', str(self.remote))
        self.git('push', 'origin', 'main')
        self.git('remote', 'set-url', 'origin', w.safe.REMOTE)
        release = {'kind': 'P3_FOCUSED_REVIEW_039_RELEASE_v1', 'repository': w.REPOSITORY,
            'content_commit': self.content, 'manifest_path': w.MANIFEST,
            'manifest_sha256': w.safe.sha(manifest_raw)}
        (self.bundle / 'RELEASE.json').write_bytes(w.safe.canonical(release))

    def git_raw(self, *args):
        return subprocess.run(['git', *args], check=True, capture_output=True).stdout

    def git(self, *args):
        return self.git_raw('-C', str(self.lab), *args)

    def git_runner(self, command, **kwargs):
        command = list(command)
        self.commands.append(command[:])
        action = command[4]
        if action == 'commit' and self.fail_commit:
            self.fail_commit = False
            return subprocess.CompletedProcess(command, 1, b'', b'fixture commit failure')
        if action == 'push' and self.fail_push:
            self.fail_push = False
            return subprocess.CompletedProcess(command, 1, b'', b'fixture transport failure')
        if action in ('fetch', 'push', 'ls-remote'):
            command[command.index('origin', 5)] = str(self.remote)
        return subprocess.run(command, **kwargs)

    def fake_controller(self, lab, emit):
        self.native_calls += 1
        directory = lab / w.MAIN
        directory.mkdir()
        (directory / 'science_output').mkdir()
        (directory / 'REPORT.json').write_bytes(b'{"status":"fixture", "actual_turns":1}\n')
        digest = w.safe.sha((directory / 'REPORT.json').read_bytes())
        (directory / 'REPORT.sha256').write_text(digest + '\n')
        (directory / 'science_SESSION.json').write_bytes(b'{"native_starts":1,"model_turns":1}\n')
        (directory / 'science_output/REVIEW_VERDICT.json').write_bytes(b'{"verdict":"fixture, not scientific evidence"}\n')
        (directory / 'raw_native_stream.txt').write_bytes(b'SECRET MUST NEVER PUBLISH\n')
        return {'controller_started': True, 'exit_code': 0}

    def run_workflow(self, controller=None):
        return w.workflow(self.lab, self.bundle, git_runner=self.git_runner,
                          controller_runner=controller or self.fake_controller, emit=lambda value: None)

    def test_one_invocation_and_idempotent_receipt_only_retry(self):
        first = self.run_workflow()
        head = self.git('rev-parse', 'HEAD')
        second = self.run_workflow()
        self.assertEqual(self.native_calls, 1)
        self.assertEqual(first['commit'], second['commit'])
        self.assertEqual(self.git('rev-parse', 'HEAD'), head)
        self.assertTrue(second['collect_only'])
        names = self.git('diff', '--name-only', self.content, 'HEAD').decode().splitlines()
        self.assertTrue(names)
        self.assertTrue(all(name.startswith('artifacts/P3_REVIEW_039_RETURN/') for name in names))
        tree = self.git('ls-tree', '-r', '--name-only', 'HEAD').decode()
        self.assertNotIn('raw_native_stream', tree)
        self.assertFalse(any(name.startswith('delivery/') for name in tree.splitlines()))
        self.assertEqual((self.lab / w.PACKET / 'MANIFEST.json').read_bytes(), self.packet)

    def test_failed_push_is_retried_without_controller_or_new_commit(self):
        self.fail_push = True
        with self.assertRaisesRegex(w.safe.StageStop, 'git_push_failed'):
            self.run_workflow()
        head = self.git('rev-parse', 'HEAD').decode().strip()
        result = self.run_workflow()
        self.assertEqual(result['commit'], head)
        self.assertEqual(self.native_calls, 1)
        self.assertEqual(sum(command[4] == 'commit' for command in self.commands), 1)

    def test_failed_commit_retries_only_exact_staged_archive(self):
        self.fail_commit = True
        with self.assertRaisesRegex(w.safe.StageStop, 'git_commit_failed'):
            self.run_workflow()
        self.assertTrue(self.git('diff', '--cached', '--name-only').strip())
        result = self.run_workflow()
        self.assertEqual(self.native_calls, 1)
        self.assertEqual(result['status'], '039_EVIDENCE_PUBLISHED')
        self.assertFalse(self.git('diff', '--cached', '--name-only').strip())

    def test_active_workflow_lock_stops_concurrent_launch(self):
        folder = self.lab / w.WORKFLOW
        folder.mkdir(parents=True)
        descriptor = os.open(folder / 'WORKFLOW.lock', os.O_RDWR | os.O_CREAT, 0o600)
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with self.assertRaisesRegex(w.safe.StageStop, '039_workflow_already_active_no_second_launch'):
                self.run_workflow()
        finally:
            os.close(descriptor)
        self.assertEqual(self.native_calls, 0)
        self.assertFalse(any(command[4] in ('fetch', 'push') for command in self.commands))

    def test_prior_reservation_without_controller_files_returns_unknown_usage(self):
        folder = self.lab / w.WORKFLOW
        folder.mkdir(parents=True)
        (folder / 'LAUNCH_RESERVED.json').write_text('{"reserved":true}\n')
        result = self.run_workflow()
        self.assertEqual(self.native_calls, 0)
        summary = result['collection_summary']
        self.assertEqual(summary['collection_status'], 'WORKFLOW_EVIDENCE_ONLY_NO_039_RECEIPTS')
        self.assertTrue(summary['missing_files_do_not_establish_no_execution'])
        report = json.loads((folder / 'WORKFLOW_REPORT.json').read_text())
        self.assertIn('UNKNOWN', report['actual_usage'])

    def test_controller_failure_publishes_partial_stop_without_retry(self):
        def fail(lab, emit):
            self.native_calls += 1
            (lab / w.MAIN).mkdir()
            (lab / w.MAIN / 'ATTEMPT.json').write_text('{"started":true}\n')
            raise RuntimeError('PRIVATE ERROR CONTENT MUST NOT PUBLISH')
        first = self.run_workflow(fail)
        self.assertEqual(first['collection_summary']['collection_status'], 'PARTIAL_EVIDENCE_WITHOUT_MAIN_REPORT')
        self.run_workflow(fail)
        self.assertEqual(self.native_calls, 1)
        report = (self.lab / w.WORKFLOW / 'WORKFLOW_REPORT.json').read_text()
        self.assertNotIn('PRIVATE ERROR', report)
        self.assertIn('RuntimeError', report)

    def test_unrelated_commit_stops_and_never_pushes_or_starts(self):
        (self.lab / 'human.txt').write_text('Unpublished human work.\n')
        self.git('add', 'human.txt')
        self.git('commit', '-m', 'Human work')
        head = self.git('rev-parse', 'HEAD')
        with self.assertRaisesRegex(w.safe.StageStop, 'unpublished_commit_is_not_exact039_evidence'):
            self.run_workflow()
        self.assertEqual(self.native_calls, 0)
        self.assertEqual(self.git('rev-parse', 'HEAD'), head)
        self.assertFalse(any(command[4] == 'push' for command in self.commands))

    def test_unignored_private_destination_stops_before_any_packet_copy(self):
        (self.lab / '.gitignore').write_text('')
        self.git('add', '.gitignore')
        self.git('commit', '-m', 'Remove ignore fixture')
        self.git('push', str(self.remote), 'main')
        with self.assertRaisesRegex(w.safe.StageStop, '039_private_runtime_paths_not_ignored'):
            self.run_workflow()
        self.assertEqual(self.native_calls, 0)
        self.assertFalse((self.lab / w.PACKET).exists())

    def test_wrong_private_packet_stops_and_returns_categorical_evidence(self):
        (self.bundle / 'packet/MANIFEST.json').write_text('wrong private bytes')
        result = self.run_workflow()
        self.assertEqual(self.native_calls, 0)
        self.assertEqual(result['collection_summary']['collection_status'], 'WORKFLOW_EVIDENCE_ONLY_NO_039_RECEIPTS')
        self.assertFalse((self.lab / w.PACKET).exists())
        report = (self.lab / w.WORKFLOW / 'WORKFLOW_REPORT.json').read_text()
        self.assertIn('039_private_packet_hash_mismatch', report)
        self.assertNotIn('wrong private bytes', report)
        repeated = self.run_workflow()
        self.assertEqual(result['commit'], repeated['commit'])
        self.assertTrue(repeated['collect_only'])
        self.assertEqual(self.native_calls, 0)

    def test_dirty_human_file_preserved(self):
        path = self.lab / w.SCOPE
        path.write_text('Human modification.\n')
        with self.assertRaisesRegex(w.safe.StageStop, 'unrelated_tracked_or_staged_edits_preserved'):
            self.run_workflow()
        self.assertEqual(self.native_calls, 0)
        self.assertEqual(path.read_text(), 'Human modification.\n')


if __name__ == '__main__':
    unittest.main()
