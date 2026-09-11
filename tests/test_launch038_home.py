"""Offline launcher checks with actual Git/filesystems and a substitute helper.

These tests do not run Windows interop, contact GitHub, or execute a reviewer.
The unchanged source helper has its separate local-Git integration tests.
"""
import importlib.util
import io
from pathlib import Path
import stat
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import warnings
import zipfile


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/launch038_home.py'
SPEC = importlib.util.spec_from_file_location('launch038', SCRIPT)
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
        self.members.update({name: b'%PDF-1.4\nfixture\n' for name in launcher.PAPERS})
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
        self.assertEqual(command[3:], [str(bundle / 'stage_source_packet038.py'),
                                     '--lab', str(self.lab), '--bundle', str(bundle)])
        self.assertEqual(options, {'cwd': self.lab})
        self.assertFalse(self.git('ls-files', '--', launcher.STEM))
        self.assertFalse(self.git('status', '--porcelain'))

    def test_matching_partial_extraction_is_completed(self):
        raw = self.archive()
        destination = self.destination(raw)
        path = destination / 'bundle' / 'README_038.md'
        path.parent.mkdir(parents=True)
        path.write_bytes(self.members['README_038.md'])
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
                     'unexpected.py', 'private_papers/extra.pdf', 'public/private.pdf'):
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
        members = dict(self.members)
        members.pop('stage_source_packet038.py')
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
        with self.assertRaisesRegex(launcher.LaunchStop, 'Source helper stopped'):
            self.run_launch(raw, runner=fail)
        package = self.destination(raw) / 'PACKAGE.zip'
        before = package.stat().st_mtime_ns
        self.run_launch(raw)
        self.assertEqual(package.stat().st_mtime_ns, before)
        self.assertEqual(len(self.calls), 2)

    def test_unrelated_tracked_edits_are_preserved_before_copy(self):
        (self.lab / '.gitignore').write_text('Human changed tracked work\n')
        with self.assertRaisesRegex(launcher.LaunchStop, 'Tracked or staged edits preserved'):
            self.run_launch()
        self.assertEqual((self.lab / '.gitignore').read_text(), 'Human changed tracked work\n')
        self.assert_no_copy()


if __name__ == '__main__':
    unittest.main()
