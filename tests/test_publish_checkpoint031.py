#!/usr/bin/env python3
"""Adversarial publisher fixtures. All Git commits/pushes are mocked."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('publication031_under_test', HERE.parent / 'scripts' / 'publish_checkpoint031.py')
pub = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pub)


def digest(body):
    return hashlib.sha256(body).hexdigest()


class FakeGit:
    """In-memory Git object/index/HEAD fixture; no subprocess Git calls."""
    def __init__(self, root, parent=pub.BASE):
        self.root = root
        self.parent = parent
        self.head = parent
        self.parents = []
        self.trees = {parent: {}}
        self.index = {}
        self.blobs = {}
        self.working_changes = set()
        self.staged_override = None
        self.commit_count = 0
        self.push_count = 0
        self.push_codes = [0]
        self.commit_extra = None
        self.commit_parent = None
        self.commands = []

    def changed(self, left, right):
        return set(k for k in set(left) | set(right) if left.get(k) != right.get(k))

    def nul(self, names):
        return b''.join(n.encode() + b'\0' for n in sorted(names))

    def git(self, root, *args, input=None):
        assert Path(root) == self.root
        self.commands.append(args)
        if args == ('rev-parse', 'HEAD'):
            return (self.head + '\n').encode()
        if args == ('show', '-s', '--format=%P', 'HEAD'):
            return (' '.join(self.parents) + '\n').encode()
        if args[0] == 'show':
            at = args[1]
            if at.startswith(':'):
                if at[1:] not in self.index:
                    raise RuntimeError('Local Git check failed: show')
                return self.index[at[1:]]
            commit, name = at.split(':', 1)
            if commit == 'HEAD':
                commit = self.head
            if name not in self.trees[commit]:
                raise RuntimeError('Local Git check failed: show')
            return self.trees[commit][name]
        if args[0] == 'diff':
            if '--cached' in args:
                names = self.staged_override if self.staged_override is not None else self.changed(self.trees[self.head], self.index)
            elif len(args) >= 5 and args[-2:] == (self.parent, 'HEAD'):
                names = self.changed(self.trees[self.parent], self.trees[self.head])
            else:
                names = self.working_changes
            return self.nul(names) if '-z' in args else ('\n'.join(sorted(names)) + ('\n' if names else '')).encode()
        if args[:3] == ('hash-object', '-w', '--stdin'):
            oid = hashlib.sha1(b'blob ' + str(len(input)).encode() + b'\0' + input).hexdigest()
            self.blobs[oid] = input
            return (oid + '\n').encode()
        if args[:3] == ('update-index', '-z', '--index-info'):
            for line in input.split(b'\0'):
                if line:
                    prefix, name = line.split(b'\t', 1)
                    mode, oid = prefix.split()
                    assert mode == b'100644'
                    self.index[name.decode()] = self.blobs[oid.decode()]
            return b''
        raise AssertionError('Unexpected fixture Git call: ' + repr(args))

    def run(self, args, **kwargs):
        if args[0] != 'git':
            raise AssertionError('No non-Git process is permitted in publisher fixture')
        if 'commit' in args:
            self.commit_count += 1
            old_head = self.head
            self.head = 'c' * 40
            self.parents = [self.commit_parent or old_head]
            self.trees[self.head] = dict(self.index)
            if self.commit_extra:
                name, body = self.commit_extra
                self.trees[self.head][name] = body
                self.index[name] = body
            return mock.Mock(returncode=0)
        if 'push' in args:
            self.push_count += 1
            return mock.Mock(returncode=self.push_codes.pop(0))
        raise AssertionError('Unexpected real-style subprocess: ' + repr(args))


class PublisherTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='publisher031-fixture-', dir=HERE)
        self.area = Path(self.temporary.name)
        self.root = self.area / 'ARC_Independent_Lab'
        self.bundle = self.area / 'bundle'
        self.root.mkdir()
        (self.bundle / 'payload').mkdir(parents=True)
        self.fake = FakeGit(self.root)
        self.patches = [mock.patch.object(pub, 'git', self.fake.git),
                        mock.patch.object(pub.subprocess, 'run', self.fake.run)]
        for patch in self.patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()
        self.temporary.cleanup()

    def put(self, name, body, *, target=None):
        path = (target or self.root) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
        return path

    def manifest(self, name='scripts/fixed031.py', old=None, new=b'new\n'):
        self.put(name, new, target=self.bundle / 'payload')
        row = {'sha256': digest(new), 'old_sha256': digest(old) if old is not None else None}
        if old is not None:
            self.put(name, old)
            self.fake.trees[self.fake.parent][name] = old
            self.fake.index[name] = old
        return {'base_commit': pub.BASE, 'files': {name: row}}

    def pending(self, name='artifacts/P3_REVIEW_030_RETURN/fixed/REPORT.json', body=b'{"status":"no_verdict"}\n'):
        self.put(name, body)
        value = {'kind': 'P3_031_PENDING_PUBLICATION_v1', 'parent': self.fake.parent,
                 'files': {name: {'sha256': digest(body)}},
                 'return_index': 'artifacts/P3_REVIEW_030_RETURN/fixed/INDEX.json',
                 'reviewer_launch_forbidden_during_publication_retry': True}
        self.put(pub.META + '/PENDING.json', pub.encoded(value))
        return value

    def test_safe_name_rejects_escape_git_backslash_and_control(self):
        for name in ('../secret', '/absolute', '.git/config', 'a/../b', 'a//b', 'a\\b', 'a:b', 'a\nsecret'):
            with self.subTest(name=name), self.assertRaises((RuntimeError, TypeError)):
                pub.safe_name(name)

    def test_read_rejects_symlink_without_reading_target(self):
        secret = self.put('secret', b'not public')
        link = self.root / 'link'
        link.symlink_to(secret)
        with self.assertRaises(RuntimeError):
            pub.read(link)

    def test_read_rejects_hardlink_and_size(self):
        original = self.put('original', b'123456')
        import os
        os.link(original, self.root / 'alias')
        with self.assertRaises(RuntimeError):
            pub.read(original)
        bounded = self.put('bounded', b'123456')
        with mock.patch.object(pub, 'MAX_FILE', 5), self.assertRaises(RuntimeError):
            pub.read(bounded)

    def test_install_refuses_unrelated_staged_and_preserves_bytes(self):
        manifest = self.manifest(old=b'old')
        self.fake.staged_override = {'unrelated.txt'}
        with self.assertRaises(RuntimeError):
            pub.install(self.root, self.bundle, manifest)
        self.assertEqual((self.root / 'scripts/fixed031.py').read_bytes(), b'old')

    def test_install_refuses_unrelated_working_change(self):
        manifest = self.manifest(old=b'old')
        self.fake.working_changes = {'other_programme.txt'}
        with self.assertRaises(RuntimeError):
            pub.install(self.root, self.bundle, manifest)

    def test_install_checks_entire_payload_before_mutation(self):
        manifest = self.manifest(old=b'old')
        manifest['files']['docs/second.md'] = {'sha256': digest(b'expected'), 'old_sha256': None}
        self.put('docs/second.md', b'wrong', target=self.bundle / 'payload')
        with self.assertRaises(RuntimeError):
            pub.install(self.root, self.bundle, manifest)
        self.assertEqual((self.root / 'scripts/fixed031.py').read_bytes(), b'old')
        self.assertFalse((self.root / 'docs/second.md').exists())

    def test_install_refuses_unknown_declared_working_version(self):
        manifest = self.manifest(old=b'old')
        self.put('scripts/fixed031.py', b'human edit')
        with self.assertRaises(RuntimeError):
            pub.install(self.root, self.bundle, manifest)
        self.assertEqual((self.root / 'scripts/fixed031.py').read_bytes(), b'human edit')

    def test_install_refuses_unknown_declared_staged_version(self):
        manifest = self.manifest(old=b'old')
        self.fake.index['scripts/fixed031.py'] = b'human staged edit'
        with self.assertRaises(RuntimeError):
            pub.install(self.root, self.bundle, manifest)
        self.assertEqual(self.fake.index['scripts/fixed031.py'], b'human staged edit')
        self.assertEqual((self.root / 'scripts/fixed031.py').read_bytes(), b'old')

    def test_install_accepts_exact_declared_transition_and_repeat(self):
        manifest = self.manifest(old=b'old')
        pub.install(self.root, self.bundle, manifest)
        pub.install(self.root, self.bundle, manifest)
        self.assertEqual((self.root / 'scripts/fixed031.py').read_bytes(), b'new\n')
        self.assertEqual(self.fake.commit_count, 0)

    def test_exact_staging_preserves_crlf_bytes(self):
        raw = b'key,value\r\na,b\r\n'
        path = 'artifacts/P3_REVIEW_030_RETURN/fixed/metrics.csv'
        self.put(path, raw)
        pub.stage_exact(self.root, {path: {'sha256': digest(raw)}})
        self.assertEqual(self.fake.index[path], raw)

    def test_exact_staging_refuses_unknown_staged_version(self):
        pending = self.pending()
        name = next(iter(pending['files']))
        self.fake.index[name] = b'human staged version'
        with self.assertRaises(RuntimeError):
            pub.stage_exact(self.root, pending['files'])
        self.assertEqual(self.fake.index[name], b'human staged version')

    def test_publication_push_failure_retains_pending_and_retry_never_recommits(self):
        pending = self.pending()
        self.fake.push_codes = [128, 0]
        with mock.patch('builtins.print'):
            self.assertEqual(pub.publish_pending(self.root, pending), 128)
            self.assertTrue((self.root / pub.META / 'PENDING.json').is_file())
            self.assertEqual(pub.publish_pending(self.root, pending), 0)
        self.assertEqual(self.fake.commit_count, 1)
        self.assertEqual(self.fake.push_count, 2)
        self.assertFalse((self.root / pub.META / 'PENDING.json').exists())
        self.assertTrue((self.root / pub.META / ('PUBLISHED_' + self.fake.head + '.json')).is_file())

    def test_publication_refuses_existing_child_with_unrelated_change(self):
        pending = self.pending()
        self.fake.head = 'c' * 40
        self.fake.parents = [pending['parent']]
        self.fake.trees[self.fake.head] = {'unrelated.txt': b'other'}
        self.fake.index = dict(self.fake.trees[self.fake.head])
        with self.assertRaises(RuntimeError):
            pub.publish_pending(self.root, pending)
        self.assertEqual(self.fake.push_count, 0)

    def test_publication_refuses_existing_child_wrong_parent(self):
        pending = self.pending()
        self.fake.head = 'c' * 40
        self.fake.parents = ['d' * 40]
        self.fake.trees[self.fake.head] = {}
        with self.assertRaises(RuntimeError):
            pub.publish_pending(self.root, pending)
        self.assertEqual(self.fake.push_count, 0)

    def test_publication_refuses_commit_hook_extra_tracked_path_before_push(self):
        pending = self.pending()
        self.fake.commit_extra = ('unrelated.txt', b'commit hook added this')
        with mock.patch('builtins.print'), self.assertRaises(RuntimeError):
            pub.publish_pending(self.root, pending)
        self.assertEqual(self.fake.push_count, 0)
        self.assertTrue((self.root / pub.META / 'PENDING.json').exists())

    def test_publication_refuses_commit_changed_parent_before_push(self):
        pending = self.pending()
        self.fake.commit_parent = 'd' * 40
        with mock.patch('builtins.print'), self.assertRaises(RuntimeError):
            pub.publish_pending(self.root, pending)
        self.assertEqual(self.fake.push_count, 0)

    def test_failed_collection_without_report_produces_fixed_publishable_index(self):
        result = pub.failed_collection(self.root)
        self.assertEqual(len(result['tracked_paths']), 1)
        index = json.loads((self.root / result['tracked_paths'][0]).read_bytes())
        self.assertEqual(index['status'], 'COLLECTION_FAILED_LOCAL_EVIDENCE_PRESERVED')
        self.assertFalse(index['execution_receipts_published'])
        self.assertFalse(index['native_or_model_retry_authorized'])
        self.assertFalse(index['scientific_admission_claimed'])
        self.assertEqual(self.fake.commit_count, 0)
        self.assertEqual(self.fake.push_count, 0)

    def test_failed_collection_does_not_bypass_redaction_by_copying_raw_report(self):
        raw = b'{"status":"WORKFLOW_STOPPED_EVIDENCE_PRESERVED","access_token":"SYNTHETIC_SECRET_NOT_PUBLIC"}'
        self.put('delivery/P3_030_RETURN_WORKFLOW/WORKFLOW_REPORT.json', raw)
        result = pub.failed_collection(self.root)
        published = b''.join((self.root / name).read_bytes() for name in result['tracked_paths'])
        self.assertNotIn(b'SYNTHETIC_SECRET_NOT_PUBLIC', published)
        self.assertNotIn(digest(raw).encode(), published)
        self.assertFalse(any(name.endswith('/WORKFLOW_REPORT.json') for name in result['tracked_paths']))

    def test_pending_retry_enters_publication_without_install_or_workflow(self):
        pending = self.pending()
        with mock.patch.object(pub.Path, 'home', return_value=self.area), \
             mock.patch.object(pub.sys, 'argv', ['publish_checkpoint031.py', '--run-and-publish']), \
             mock.patch.object(pub, 'repository_check'), \
             mock.patch.object(pub, 'install', side_effect=AssertionError('install forbidden on pending retry')), \
             mock.patch.object(pub.importlib.util, 'spec_from_file_location', side_effect=AssertionError('reviewer import forbidden')), \
             mock.patch.object(pub, 'publish_pending', return_value=0) as publish:
            self.assertEqual(pub.main(), 0)
            publish.assert_called_once_with(self.root, pending)


if __name__ == '__main__':
    unittest.main(verbosity=2)
