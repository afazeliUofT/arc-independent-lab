#!/usr/bin/env python3
"""Stage the two supplied papers privately and publish a source-integrity receipt.

The bundle identifies a published commit and a public input manifest. Git objects
at that commit supply the public input bytes. This program never imports a
reviewer, runs a model, or treats a source packet as a scientific verdict.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys

REPOSITORY = 'afazeliUofT/arc-independent-lab'
REMOTE = 'https://github.com/' + REPOSITORY + '.git'
MANIFEST_PATH = 'evidence/P3_FOCUSED_REVIEW_MANIFEST_038.json'
PACKET = 'delivery/P3_SOURCE_PACKET_038'
PRIVATE_DIGESTS = (
    '70e60317cc1e7815118aac54b00d3aadf5558f7bc219ca2d3b6e3396c2611086',
    '873998cb1f647756e12f061f5c9152c2bae9fa3b37b0efa45432aa4b7e9df570',
)
MAX_FILE = 32 * 1024 * 1024
MAX_TOTAL = 128 * 1024 * 1024
COMMIT_MESSAGE = 'Checkpoint038: record private source packet integrity without reviewer execution'


class StageStop(RuntimeError):
    pass


def require(condition, reason):
    if not condition:
        raise StageStop(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True,
                       allow_nan=False) + '\n').encode('ascii')


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate_json_key')
        result[key] = value
    return result


def parse(raw):
    return json.loads(raw, object_pairs_hook=unique_pairs)


def safe_name(value):
    require(type(value) is str and value and len(value) <= 1024,
            'invalid_relative_path')
    path = PurePosixPath(value)
    require(not path.is_absolute() and path.as_posix() == value and
            all(p not in ('', '.', '..', '.git') for p in value.split('/')) and
            not any(ord(c) < 32 for c in value) and '\\' not in value and ':' not in value,
            'invalid_relative_path')
    return value


def directory(path, *, create=False):
    path = Path(path).absolute()
    require('..' not in path.parts, 'parent_directory_step_refused')
    cursor = Path(path.anchor)
    for part in path.parts[1:]:
        cursor /= part
        try:
            info = cursor.lstat()
        except FileNotFoundError:
            require(create, 'required_directory_missing')
            try:
                cursor.mkdir(mode=0o700)
            except FileExistsError:
                pass
            info = cursor.lstat()
        require(stat.S_ISDIR(info.st_mode), 'linked_or_special_directory_refused')
    return path


def signature(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


def read_regular(path):
    path = Path(path)
    directory(path.parent)
    before = path.lstat()
    require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
            before.st_size <= MAX_FILE, 'linked_special_or_oversized_file_refused')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        opened = os.fstat(fd)
        require(signature(opened) == signature(before), 'source_changed_while_opening')
        chunks = []
        total = 0
        while True:
            block = os.read(fd, min(65536, MAX_FILE + 1 - total))
            if not block:
                break
            chunks.append(block)
            total += len(block)
            require(total <= MAX_FILE, 'file_byte_limit')
        require(signature(os.fstat(fd)) == signature(opened) == signature(path.lstat())
                and total == opened.st_size, 'source_changed_while_reading')
        return b''.join(chunks)
    finally:
        os.close(fd)


def write_equal_or_new(path, raw, *, private=False):
    path = Path(path)
    directory(path.parent, create=True)
    if os.path.lexists(path):
        require(read_regular(path) == raw, 'existing_different_file_preserved')
        return
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                 0o600 if private else 0o644)
    try:
        with os.fdopen(fd, 'wb', closefd=False) as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(fd)
    finally:
        os.close(fd)
    require(read_regular(path) == raw, 'stored_byte_verification_failed')


class Git:
    def __init__(self, root, runner=None):
        self.root = Path(root)
        self.runner = subprocess.run if runner is None else runner

    def call(self, *args, input=None, allowed=(0,)):
        env = os.environ.copy()
        for key in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_COMMON_DIR',
                    'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'):
            env.pop(key, None)
        result = self.runner(['git', '--no-pager', '-C', str(self.root), *args],
                             input=input, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             env=env, timeout=60)
        require(result.returncode in allowed, 'git_' + args[0] + '_failed')
        return result.stdout

    def ancestor(self, first, second):
        # rev-list has an unambiguous empty result when first is an ancestor.
        return not self.call('rev-list', '--max-count=1', first, '^' + second).strip()


def git_names(raw):
    return {safe_name(value.decode('utf-8')) for value in raw.split(b'\0') if value}


def repository_precheck(git):
    directory(git.root)
    require(git.call('rev-parse', '--show-toplevel').decode().strip() == str(git.root),
            'wrong_project_root')
    require(git.call('branch', '--show-current').decode().strip() == 'main',
            'main_branch_required')
    for option in ((), ('--push',)):
        actual = git.call('remote', 'get-url', *option, 'origin').decode().strip()
        require(actual.rstrip('/').removesuffix('.git') == REMOTE.removesuffix('.git'),
                'origin_differs_from_authorized_repository')
    require(not git.call('diff', '--name-only', '-z').strip() and
            not git.call('diff', '--cached', '--name-only', '-z').strip(),
            'tracked_or_staged_edits_preserved_sync_stopped')


def read_release(bundle):
    release = parse(read_regular(bundle / 'RELEASE.json'))
    expected = {'kind', 'repository', 'content_commit', 'manifest_path', 'manifest_sha256'}
    require(type(release) is dict and set(release) == expected and
            release['kind'] == 'P3_SOURCE_PACKET_038_RELEASE_v1' and
            release['repository'] == REPOSITORY and release['manifest_path'] == MANIFEST_PATH,
            'wrong_release_metadata')
    require(re.fullmatch('[0-9a-f]{40}', release['content_commit']) and
            re.fullmatch('[0-9a-f]{64}', release['manifest_sha256']),
            'invalid_release_digest')
    return release


def pinned_file(git, commit, name, digest):
    safe_name(name)
    require(type(digest) is str and re.fullmatch('[0-9a-f]{64}', digest),
            'invalid_input_digest')
    tree = git.call('ls-tree', '-z', commit, '--', name)
    entries = [entry for entry in tree.split(b'\0') if entry]
    require(len(entries) == 1, 'pinned_input_missing')
    metadata, actual_name = entries[0].split(b'\t', 1)
    require(actual_name.decode() == name and metadata.split()[0] in (b'100644', b'100755')
            and metadata.split()[1] == b'blob', 'pinned_input_not_regular_file')
    size = int(git.call('cat-file', '-s', commit + ':' + name))
    require(size <= MAX_FILE, 'pinned_input_byte_limit')
    raw = git.call('show', commit + ':' + name)
    require(len(raw) == size and sha(raw) == digest, 'pinned_input_digest_mismatch')
    return raw


def declared_inputs(git, bundle, release):
    commit = release['content_commit']
    manifest_raw = pinned_file(git, commit, MANIFEST_PATH, release['manifest_sha256'])
    manifest = parse(manifest_raw)
    require(type(manifest) is dict and type(manifest.get('inputs')) is list and
            0 < len(manifest['inputs']) <= 500 and type(manifest.get('private_sources')) is list,
            'invalid_source_manifest')
    private_rows = [{'path': 'private_papers/' + digest + '.pdf', 'sha256': digest}
                    for digest in PRIVATE_DIGESTS]
    require(sorted(manifest['private_sources'], key=lambda row: row['path']) ==
            sorted(private_rows, key=lambda row: row['path']), 'private_source_inventory_differs')
    payloads = {MANIFEST_PATH: manifest_raw}
    for row in manifest['inputs']:
        require(type(row) is dict and set(row) == {'path', 'sha256'}, 'invalid_public_input_row')
        name = safe_name(row['path'])
        require(name not in payloads and not name.startswith(('delivery/', 'private_sources/',
                'private_papers/')) and not name.lower().endswith(('.pdf', '.png', '.jpg', '.zip')),
                'duplicate_or_private_public_input_refused')
        payloads[name] = pinned_file(git, commit, name, row['sha256'])
        payloads[name].decode('utf-8')
    for row in private_rows:
        raw = read_regular(bundle / row['path'])
        require(raw.startswith(b'%PDF-') and sha(raw) == row['sha256'],
                'private_pdf_digest_or_type_mismatch')
        payloads[row['path']] = raw
    require(sum(len(raw) for raw in payloads.values()) <= MAX_TOTAL, 'packet_total_byte_limit')
    return payloads


def receipt_bytes(release, payloads):
    receipt = {'kind': 'P3_SOURCE_PACKET_038_INTEGRITY_RECEIPT_v1',
        'repository': REPOSITORY, 'content_commit': release['content_commit'],
        'public_manifest_path': MANIFEST_PATH, 'public_manifest_sha256': release['manifest_sha256'],
        'packet_relative_path': PACKET,
        'files': [{'path': path, 'sha256': sha(raw), 'bytes': len(raw),
                   'origin': 'private_user_supplied_pdf' if path.startswith('private_papers/')
                             else 'pinned_public_git_object'}
                  for path, raw in sorted(payloads.items())],
        'exact_packet_bytes_verified': True, 'packet_paths_ignored_and_untracked_verified': True,
        'private_content_published': False, 'source_integrity_only': True,
        'reviewer_execution_started': False, 'native_starts': 0, 'model_turns': 0,
        'independent_review_completed': False, 'scientific_verdict_created': False,
        'new_native_allowance': 0, 'historical032_scope_reused': False,
        'timestamp_omitted_for_idempotence': True}
    raw = canonical(receipt)
    stem = 'artifacts/P3_SOURCE_PACKET_038/' + release['manifest_sha256']
    return {stem + '/RECEIPT.json': raw,
            stem + '/SHA256SUMS': (sha(raw) + '  RECEIPT.json\n').encode('ascii')}


def ignored_and_untracked(git, payloads):
    require(not git.call('ls-files', '-z', '--', PACKET).strip(),
            'private_packet_path_is_tracked')
    paths = [PACKET + '/' + name for name in sorted(payloads)]
    actual = git_names(git.call('check-ignore', '--no-index', '-z', '--stdin',
                               input=b''.join(path.encode() + b'\0' for path in paths)))
    require(actual == set(paths), 'private_packet_is_not_fully_ignored')


def verify_existing_tree(packet, payloads):
    if not os.path.lexists(packet):
        return
    directory(packet)
    expected_dirs = {str(parent) for name in payloads for parent in PurePosixPath(name).parents
                     if str(parent) != '.'}
    for parent, dirs, files in os.walk(packet, followlinks=False):
        parent = Path(parent)
        for name in dirs:
            path = parent / name
            require(path.relative_to(packet).as_posix() in expected_dirs,
                    'unexpected_packet_directory_preserved')
            directory(path)
        for name in files:
            path = parent / name
            relative = path.relative_to(packet).as_posix()
            require(relative in payloads and read_regular(path) == payloads[relative],
                    'unexpected_or_changed_packet_file_preserved')


def sync_after_fetch(git, fetched, receipt):
    current = git.call('rev-parse', 'HEAD').decode().strip()
    if git.ancestor(current, fetched):
        git.call('merge', '--ff-only', fetched)
        return
    require(git.ancestor(fetched, current), 'branches_diverged_preserved')
    commits = git.call('rev-list', fetched + '..' + current).decode().split()
    require(len(commits) == 1 and git.call('show', '-s', '--format=%P', current).decode().split()
            == [fetched], 'unpublished_unrelated_commits_preserved')
    changed = git_names(git.call('diff', '--name-only', '-z', fetched, current))
    require(changed == set(receipt) and all(git.call('show', current + ':' + path) == raw
            for path, raw in receipt.items()), 'unpublished_commit_is_not_exact_source_receipt')


def publish_receipt(git, expected, fetched):
    for path, raw in expected.items():
        write_equal_or_new(git.root / path, raw)
    require(not git.call('diff', '--name-only', '-z').strip() and
            not git.call('diff', '--cached', '--name-only', '-z').strip(),
            'tracked_or_staged_edits_preserved_publication_stopped')
    parent = git.call('rev-parse', 'HEAD').decode().strip()
    git.call('add', '--', *sorted(expected))
    staged = git_names(git.call('diff', '--cached', '--name-only', '-z'))
    require(staged <= set(expected), 'unrelated_staged_files_preserved')
    for path, raw in expected.items():
        require(git.call('show', ':' + path) == raw, 'staged_receipt_bytes_differ')
    if staged:
        require(staged == set(expected), 'partial_receipt_commit_refused')
        git.call('commit', '-m', COMMIT_MESSAGE)
        current = git.call('rev-parse', 'HEAD').decode().strip()
        require(git.call('show', '-s', '--format=%P', current).decode().split() == [parent] and
                git_names(git.call('diff', '--name-only', '-z', parent, current)) == set(expected),
                'committed_receipt_scope_differs')
    else:
        current = parent
    require(all(git.call('show', current + ':' + path) == raw for path, raw in expected.items()),
            'committed_receipt_bytes_differ')
    if current != fetched:
        git.call('push', 'origin', current + ':refs/heads/main')
    remote = git.call('ls-remote', '--exit-code', 'origin', 'refs/heads/main').decode().split()
    require(len(remote) == 2 and remote == [current, 'refs/heads/main'],
            'remote_publication_not_verified')
    return current


def stage(lab, bundle, *, runner=None):
    lab, bundle = directory(lab), directory(bundle)
    release = read_release(bundle)
    git = Git(lab, runner=runner)
    repository_precheck(git)
    # Fetch does not change the checkout. The pinned commit must be present in
    # the fetched approved remote history before any source packet is written.
    git.call('fetch', '--no-tags', 'origin', 'main')
    fetched = git.call('rev-parse', 'FETCH_HEAD').decode().strip()
    require(git.ancestor(release['content_commit'], fetched),
            'published_content_commit_not_in_remote_history')
    payloads = declared_inputs(git, bundle, release)
    receipt = receipt_bytes(release, payloads)
    sync_after_fetch(git, fetched, receipt)
    require(git.ancestor(release['content_commit'], 'HEAD'),
            'published_content_commit_not_in_local_history')
    packet = lab / PACKET
    if os.path.lexists(packet):
        directory(packet)
    ignored_and_untracked(git, payloads)
    verify_existing_tree(packet, payloads)
    for name, raw in sorted(payloads.items()):
        write_equal_or_new(packet / name, raw, private=True)
    verify_existing_tree(packet, payloads)
    require(all(read_regular(packet / name) == raw for name, raw in payloads.items()),
            'packet_not_complete')
    ignored_and_untracked(git, payloads)
    commit = publish_receipt(git, receipt, fetched)
    return {'status': 'SOURCE_PACKET_STAGED_AND_RECEIPT_PUBLICATION_VERIFIED',
            'receipt_path': next(path for path in receipt if path.endswith('RECEIPT.json')),
            'receipt_sha256': sha(next(raw for path, raw in receipt.items()
                                       if path.endswith('RECEIPT.json'))),
            'commit': commit, 'packet_path': str(packet),
            'reviewer_execution_started': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lab', type=Path, default=Path.home() / 'ARC_Independent_Lab')
    parser.add_argument('--bundle', type=Path, default=Path(__file__).absolute().parent)
    args = parser.parse_args()
    try:
        result = stage(args.lab, args.bundle)
    except (StageStop, OSError, ValueError, KeyError, TypeError, UnicodeError,
            subprocess.SubprocessError) as error:
        reason = str(error) if type(error) is StageStop else type(error).__name__
        print('STOP: ' + reason + '. Existing files and commits are preserved.', file=sys.stderr)
        print('No reviewer or model was started. A failed push can be retried with the same command.',
              file=sys.stderr)
        return 1
    print('Source packet verified. No reviewer or model was started.')
    print('GitHub receipt: https://github.com/' + REPOSITORY + '/blob/' +
          result['commit'] + '/' + result['receipt_path'])
    print('GitHub is updated; the PI can read the receipt directly.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
