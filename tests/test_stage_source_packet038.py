"""Exercise source staging and publication against temporary local Git repos.

Only the network transport is substituted: fetch/push/ls-remote use a local bare
repository. All index, commit, history, ignore and source-byte checks use Git.
"""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/stage_source_packet038.py'
SPEC = importlib.util.spec_from_file_location('stage038', SCRIPT)
stage038 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(stage038)


class StagePacketTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.lab, self.remote, self.bundle = (self.base / name for name in ('lab', 'remote.git', 'bundle'))
        self.lab.mkdir()
        self.bundle.mkdir()
        self.commands = []
        self.fail_push = False
        self.raw_git('init', '--bare', str(self.remote), cwd=self.base)
        self.git('init', '-b', 'main')
        self.git('config', 'user.name', 'Source packet fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        (self.lab / '.gitignore').write_text('delivery/\nprivate_sources/\n')
        (self.lab / 'docs').mkdir()
        (self.lab / 'docs/source.md').write_text('Original frozen public source.\n')
        self.pdfs = (b'%PDF-1.4\nprivate fixture one\n', b'%PDF-1.4\nprivate fixture two\n')
        self.digests = tuple(stage038.sha(raw) for raw in self.pdfs)
        self.patch = patch.object(stage038, 'PRIVATE_DIGESTS', self.digests)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        manifest = {'kind': 'TEST_FOCUSED_REVIEW_INPUTS',
            'inputs': [{'path': 'docs/source.md',
                        'sha256': stage038.sha((self.lab / 'docs/source.md').read_bytes())}],
            'private_sources': [{'path': 'private_papers/' + digest + '.pdf', 'sha256': digest}
                                for digest in self.digests]}
        self.manifest_raw = stage038.canonical(manifest)
        self.manifest_sha = stage038.sha(self.manifest_raw)
        path = self.lab / stage038.MANIFEST_PATH
        path.parent.mkdir()
        path.write_bytes(self.manifest_raw)
        self.git('add', '.')
        self.git('commit', '-m', 'Pinned source fixture')
        self.content_commit = self.git('rev-parse', 'HEAD').decode().strip()
        self.git('remote', 'add', 'origin', str(self.remote))
        self.git('push', 'origin', 'main')
        self.git('remote', 'set-url', 'origin', stage038.REMOTE)
        release = {'kind': 'P3_SOURCE_PACKET_038_RELEASE_v1',
            'repository': stage038.REPOSITORY, 'content_commit': self.content_commit,
            'manifest_path': stage038.MANIFEST_PATH, 'manifest_sha256': self.manifest_sha}
        (self.bundle / 'RELEASE.json').write_bytes(stage038.canonical(release))
        (self.bundle / 'private_papers').mkdir()
        for digest, raw in zip(self.digests, self.pdfs):
            (self.bundle / 'private_papers' / (digest + '.pdf')).write_bytes(raw)

    def raw_git(self, *args, cwd=None):
        return subprocess.run(['git', *args], cwd=cwd, check=True, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE).stdout

    def git(self, *args):
        return self.raw_git('-C', str(self.lab), *args)

    def runner(self, command, **kwargs):
        self.commands.append(list(command))
        command = list(command)
        action = command[4]
        if action == 'push' and self.fail_push:
            self.fail_push = False
            return subprocess.CompletedProcess(command, 1, b'', b'simulated private transport error')
        if action in ('fetch', 'push', 'ls-remote'):
            command[command.index('origin', 5)] = str(self.remote)
        return subprocess.run(command, **kwargs)

    def run_stage(self):
        return stage038.stage(self.lab, self.bundle, runner=self.runner)

    def publish_local_change(self, message):
        self.git('add', '.')
        self.git('commit', '-m', message)
        self.git('push', str(self.remote), 'main')

    def receipt_paths(self):
        stem = 'artifacts/P3_SOURCE_PACKET_038/' + self.manifest_sha
        return {stem + '/RECEIPT.json', stem + '/SHA256SUMS'}

    def test_stages_pinned_bytes_publishes_only_receipt_and_is_idempotent(self):
        (self.lab / 'docs/source.md').write_text('Later public source version.\n')
        self.publish_local_change('Later source; retain old release pin')
        before = self.git('rev-parse', 'HEAD').decode().strip()
        result = self.run_stage()
        self.assertFalse(result['reviewer_execution_started'])
        self.assertEqual((self.lab / stage038.PACKET / 'docs/source.md').read_text(),
                         'Original frozen public source.\n')
        self.assertEqual((self.lab / 'docs/source.md').read_text(), 'Later public source version.\n')
        changed = set(self.git('diff', '--name-only', before, 'HEAD').decode().splitlines())
        self.assertEqual(changed, self.receipt_paths())
        self.assertFalse(self.git('ls-files', '--', stage038.PACKET).strip())
        receipt = json.loads((self.lab / result['receipt_path']).read_text())
        self.assertEqual(receipt['content_commit'], self.content_commit)
        self.assertEqual(receipt['native_starts'], 0)
        self.assertFalse(receipt['independent_review_completed'])
        repeated = self.run_stage()
        self.assertEqual(result, repeated)
        self.assertEqual(sum(command[4] == 'commit' for command in self.commands), 1)
        self.assertEqual(sum(command[4] == 'push' for command in self.commands), 1)

    def test_failed_push_preserves_real_receipt_and_retries_without_new_commit(self):
        self.fail_push = True
        with self.assertRaisesRegex(stage038.StageStop, 'git_push_failed'):
            self.run_stage()
        local = self.git('rev-parse', 'HEAD').decode().strip()
        self.assertNotEqual(local, self.content_commit)
        self.assertTrue((self.lab / next(p for p in self.receipt_paths()
                                        if p.endswith('RECEIPT.json'))).exists())
        result = self.run_stage()
        self.assertEqual(result['commit'], local)
        self.assertEqual(sum(command[4] == 'commit' for command in self.commands), 1)

    def test_wrong_private_bytes_stop_before_packet_or_receipt(self):
        pdf = self.bundle / 'private_papers' / (self.digests[0] + '.pdf')
        pdf.write_bytes(b'%PDF-1.4\nwrong source\n')
        with self.assertRaisesRegex(stage038.StageStop, 'private_pdf_digest'):
            self.run_stage()
        self.assertFalse((self.lab / stage038.PACKET).exists())
        self.assertFalse((self.lab / 'artifacts').exists())

    def test_unignored_destination_stops_before_copy(self):
        (self.lab / '.gitignore').write_text('private_sources/\n')
        self.publish_local_change('No delivery ignore')
        with self.assertRaises(stage038.StageStop):
            self.run_stage()
        self.assertFalse((self.lab / stage038.PACKET).exists())
        self.assertFalse((self.lab / 'artifacts').exists())

    def test_tracked_private_destination_stops_before_any_paper_copy(self):
        packet = self.lab / stage038.PACKET
        packet.mkdir(parents=True)
        (packet / 'tracked.txt').write_text('Wrong public location')
        self.git('add', '-f', str(packet / 'tracked.txt'))
        self.git('commit', '-m', 'Invalid tracked packet fixture')
        self.git('push', str(self.remote), 'main')
        with self.assertRaisesRegex(stage038.StageStop, 'private_packet_path_is_tracked'):
            self.run_stage()
        self.assertFalse((packet / 'private_papers').exists())

    def test_unrelated_tracked_edits_stop_before_fetch_and_are_preserved(self):
        target = self.lab / 'docs/source.md'
        target.write_text('Uncommitted human work.\n')
        with self.assertRaisesRegex(stage038.StageStop, 'tracked_or_staged_edits_preserved'):
            self.run_stage()
        self.assertEqual(target.read_text(), 'Uncommitted human work.\n')
        self.assertFalse(any(command[4] == 'fetch' for command in self.commands))

    def test_existing_changed_packet_bytes_are_preserved(self):
        self.run_stage()
        target = self.lab / stage038.PACKET / 'docs/source.md'
        target.write_text('Changed private packet.\n')
        before = self.git('rev-parse', 'HEAD')
        with self.assertRaisesRegex(stage038.StageStop, 'unexpected_or_changed_packet_file'):
            self.run_stage()
        self.assertEqual(target.read_text(), 'Changed private packet.\n')
        self.assertEqual(self.git('rev-parse', 'HEAD'), before)

    def test_symlink_destination_refused_without_writing_target(self):
        target = self.base / 'outside'
        target.mkdir()
        (self.lab / 'delivery').mkdir()
        (self.lab / stage038.PACKET).symlink_to(target, target_is_directory=True)
        with self.assertRaisesRegex(stage038.StageStop, 'linked_or_special_directory'):
            self.run_stage()
        self.assertEqual(list(target.iterdir()), [])

    def test_unrelated_unpublished_commit_is_preserved_without_push(self):
        (self.lab / 'human.txt').write_text('Unpublished human work.\n')
        self.git('add', 'human.txt')
        self.git('commit', '-m', 'Human unpublished work')
        before = self.git('rev-parse', 'HEAD')
        with self.assertRaisesRegex(stage038.StageStop, 'unpublished_commit_is_not_exact_source_receipt'):
            self.run_stage()
        self.assertEqual(self.git('rev-parse', 'HEAD'), before)
        self.assertFalse(any(command[4] == 'push' for command in self.commands))
        self.assertFalse((self.lab / stage038.PACKET).exists())


if __name__ == '__main__':
    unittest.main()
