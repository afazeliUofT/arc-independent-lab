#!/usr/bin/env python3
"""Verify the frozen040 return offline and publish only a deterministic041 receipt.

The ZIP's public tree is an immutable input snapshot, not an experimental worktree.
The only subprocesses used here are bounded Git transport/object operations. No
review controller, native runtime, model, candidate or experiment is invoked.
"""
from __future__ import annotations

import argparse
import fcntl
import importlib.util
import os
from pathlib import Path
import re
import stat
import subprocess
import sys

sys.dont_write_bytecode = True


def module_at(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


safe = module_at(Path(__file__).absolute().with_name('stage_source_packet038.py'),
                 '_checkpoint041_safe')
REPOSITORY = safe.REPOSITORY
MANIFEST = 'evidence/P3_CHECKPOINT_041_MANIFEST.json'
WORKFLOW = 'delivery/P3_041_RETURN_WORKFLOW'
VERIFIER = 'scripts/check_return040_041.py'
REQUIRED_CODE = {VERIFIER, 'scripts/checkpoint041_workflow.py',
                 'scripts/stage_source_packet038.py', 'scripts/launch041_home.py',
                 'scripts/downloads_bootstrap041.py'}
RETURN_COMMIT = '540370fdb73c8f87f6433e14463951673640d033'
RETURN_REPORT_SHA256 = '877c4eeda0b31154d42885f8afbe7e01a56a5a452bdcef56a279b46cb2a7c372'
RETURN_VERDICT_SHA256 = 'a31b9d8ec2103f09d81b963fd7f9ff51c4287490a0f0bf2f74f5dfbc1407d673'
COMMIT_MESSAGE = 'Checkpoint041: return offline verification receipt without model or experiment execution'


class Git(safe.Git):
    """Keep configured repository hooks outside this fixed publication operation."""
    def __init__(self, root, runner=None):
        execute = subprocess.run if runner is None else runner

        def bounded(command, **kwargs):
            return execute(command[:1] + ['-c', 'core.hooksPath=/dev/null'] + command[1:],
                           **kwargs)

        super().__init__(root, runner=bounded)


def release_metadata(bundle):
    value = safe.parse(safe.read_regular(bundle / 'package_release.json'))
    safe.require(type(value) is dict and set(value) == {'kind', 'repository',
        'content_commit', 'accepted_return_commit', 'manifest_path', 'manifest_sha256'} and
        value['kind'] == 'P3_CHECKPOINT_041_RELEASE_v1' and
        value['repository'] == REPOSITORY and value['manifest_path'] == MANIFEST and
        value['accepted_return_commit'] == RETURN_COMMIT,
        'wrong041_release_metadata')
    safe.require(type(value['content_commit']) is str and
        re.fullmatch('[0-9a-f]{40}', value['content_commit']) and
        type(value['manifest_sha256']) is str and
        re.fullmatch('[0-9a-f]{64}', value['manifest_sha256']), 'invalid041_release_pin')
    return value


def check_repository(git, expected):
    safe.directory(git.root)
    safe.directory(git.root / '.git')
    safe.require(git.call('rev-parse', '--show-toplevel').decode().strip() == str(git.root),
                 'wrong_project_root')
    safe.require(git.call('branch', '--show-current').decode().strip() == 'main',
                 'main_branch_required')
    for flags in (('--all',), ('--push', '--all')):
        values = git.call('remote', 'get-url', *flags, 'origin').decode().splitlines()
        safe.require(len(values) == 1 and values[0].rstrip('/').removesuffix('.git') ==
                     safe.REMOTE.removesuffix('.git'), 'origin_differs_from_authorized_repository')
    for args in (('diff', '--name-only', '-z'), ('diff', '--cached', '--name-only', '-z')):
        names = safe.git_names(git.call(*args))
        safe.require(names <= set(expected), 'unrelated_tracked_or_staged_edits_preserved')
        for name in names:
            safe.require(safe.read_regular(git.root / name) == expected[name],
                         'changed_expected041_receipt_preserved')
            if '--cached' in args:
                safe.require(git.call('show', ':' + name) == expected[name],
                             'changed_staged041_receipt_preserved')


def ignored(git, paths):
    safe.require(not git.call('ls-files', '-z', '--', WORKFLOW),
                 '041_private_workflow_is_tracked')
    names = [WORKFLOW + '/WORKFLOW.lock', *paths]
    actual = safe.git_names(git.call('check-ignore', '--no-index', '-z', '--stdin',
        input=b''.join(name.encode() + b'\0' for name in names), allowed=(0, 1)))
    safe.require(actual == set(names), '041_private_bundle_or_workflow_not_ignored')


def load_snapshot(git, bundle, release):
    commit = release['content_commit']
    manifest_raw = safe.pinned_file(git, commit, MANIFEST, release['manifest_sha256'])
    safe.require(safe.read_regular(bundle / 'public' / MANIFEST) == manifest_raw,
                 '041_bundled_manifest_differs_from_release')
    manifest = safe.parse(manifest_raw)
    safe.require(type(manifest) is dict and type(manifest.get('inputs')) is list and
        type(manifest.get('private_files')) is list and
        1 <= len(manifest['inputs']) <= 500 and
        1 <= len(manifest['private_files']) <= 500, 'invalid041_manifest')
    public = {MANIFEST: manifest_raw}
    for row in manifest['inputs']:
        safe.require(type(row) is dict and set(row) == {'path', 'sha256'},
                     'invalid041_public_input_row')
        name = safe.safe_name(row['path'])
        safe.require(name not in public and not name.startswith(
            ('delivery/', 'private/', 'private_sources/', 'private_papers/')) and
            not name.lower().endswith(('.pdf', '.png', '.jpg', '.zip')),
            'duplicate_or_private041_public_input')
        public[name] = safe.pinned_file(git, commit, name, row['sha256'])
        safe.require(safe.read_regular(bundle / 'public' / name) == public[name],
                     '041_public_snapshot_differs_from_git_object')
    safe.require(REQUIRED_CODE <= set(public), '041_runtime_dependency_pins_missing')
    for name in ('checkpoint041_workflow.py', 'stage_source_packet038.py'):
        safe.require(safe.read_regular(Path(__file__).absolute().with_name(name)) ==
            public['scripts/' + name], '041_executing_wrapper_differs_from_release')
    safe.require(safe.read_regular(bundle / 'launch041_home.py') ==
        public['scripts/launch041_home.py'], '041_launcher_differs_from_release')
    private = {}
    for row in manifest['private_files']:
        safe.require(type(row) is dict and set(row) == {'path', 'sha256'},
                     'invalid041_private_input_row')
        name = safe.safe_name(row['path'])
        safe.require(name.startswith('private/') and name.removeprefix('private/') not in private and
            type(row['sha256']) is str and re.fullmatch('[0-9a-f]{64}', row['sha256']),
            'invalid041_private_input_path')
        raw = safe.read_regular(bundle / name)
        safe.require(safe.sha(raw) == row['sha256'], '041_private_packet_hash_mismatch')
        private[name.removeprefix('private/')] = raw
    safe.require(sum(map(len, public.values())) + sum(map(len, private.values())) <=
                 safe.MAX_TOTAL, '041_snapshot_byte_limit')
    verify_snapshot(bundle, public, private)
    return public, private


def verify_snapshot(bundle, public, private):
    for prefix, files in (('public', public), ('private', private)):
        folder = bundle / prefix
        safe.verify_existing_tree(folder, files)
        safe.require(all(safe.read_regular(folder / name) == raw for name, raw in files.items()),
                     '041_snapshot_changed_or_incomplete')


def verify_return(bundle):
    verifier = module_at(bundle / 'public' / VERIFIER, '_checkpoint041_original_return_verifier')
    value = verifier.verify(bundle / 'public', bundle / 'private')
    safe.require(type(value) is dict and value.get('kind') ==
        'P3_ORIGINAL_RETURN_VERIFICATION_041_v1' and
        value.get('integrity_verified') is True, '041_return_verifier_did_not_admit_integrity')
    # Canonical serialization disallows NaN and prevents platform formatting drift.
    safe.canonical(value)
    return value


def receipt_bytes(release, result, public, private):
    receipt = {'kind': 'P3_CHECKPOINT_041_OFFLINE_VERIFICATION_RECEIPT_v1',
        'repository': REPOSITORY, 'content_commit': release['content_commit'],
        'release_manifest_path': MANIFEST,
        'release_manifest_sha256': release['manifest_sha256'],
        'accepted_return_commit': RETURN_COMMIT,
        'original040_report_sha256': RETURN_REPORT_SHA256,
        'original040_verdict_sha256': RETURN_VERDICT_SHA256,
        'verifier_path': VERIFIER, 'verifier_sha256': safe.sha(public[VERIFIER]),
        'verifier_result_sha256': safe.sha(safe.canonical(result)),
        'integrity_verified': result.get('integrity_verified') is True,
        'verification_status': 'VERIFIED' if result.get('integrity_verified') is True
                               else 'OFFLINE_VERIFICATION_STOPPED',
        'failure_class': result.get('failure_class'),
        'public_snapshot_files_verified': len(public),
        'private_packet_files_verified': len(private),
        'private_content_published': False,
        'scientific_verdict_created': False,
        'offline_verification_and_specification_only': True,
        'new_native_allowance': 0, 'native_starts': 0, 'model_turns_sent': 0,
        'reviewer_or_review_controller_started': False,
        'candidate_or_experiment_started': False,
        'future_experiment_admission': False,
        'historical040_rerun': False, 'historical039_rerun': False,
        'timestamp_omitted_for_idempotence': True}
    raw = safe.canonical(receipt)
    return {'artifacts/CHECKPOINT_041_RETURN/' + release['manifest_sha256'] + '/RECEIPT.json': raw}


def sync_repository(git, fetched, expected):
    current = git.call('rev-parse', 'HEAD').decode().strip()
    if current == fetched:
        return
    if git.ancestor(current, fetched):
        safe.require(not git.call('diff', '--cached', '--name-only', '-z').strip(),
                     'staged041_receipt_preserved_before_remote_fast_forward')
        git.call('merge', '--ff-only', fetched)
        return
    safe.require(git.ancestor(fetched, current), 'branches_diverged_preserved')
    safe.require(git.call('rev-list', fetched + '..' + current).decode().split() == [current]
        and git.call('show', '-s', '--format=%P', current).decode().split() == [fetched],
        'unrelated_unpublished_commits_preserved')
    changed = safe.git_names(git.call('diff', '--name-only', '-z', fetched, current))
    safe.require(changed == set(expected) and all(
        git.call('show', current + ':' + name) == raw for name, raw in expected.items()),
        'unpublished_commit_is_not_exact041_receipt')


def publish(git, expected, fetched):
    check_repository(git, expected)
    for name, raw in expected.items():
        safe.write_equal_or_new(git.root / name, raw)
    parent = git.call('rev-parse', 'HEAD').decode().strip()
    entries = []
    for name, raw in sorted(expected.items()):
        oid = git.call('hash-object', '-w', '--stdin', '--no-filters', input=raw).decode().strip()
        entries.append(('100644 ' + oid + '\t' + name + '\0').encode())
    git.call('update-index', '-z', '--index-info', input=b''.join(entries))
    staged = safe.git_names(git.call('diff', '--cached', '--name-only', '-z'))
    safe.require(staged <= set(expected), 'unrelated041_index_change_preserved')
    safe.require(all(git.call('show', ':' + name) == raw for name, raw in expected.items()),
                 '041_staged_receipt_bytes_differ')
    if staged:
        safe.require(staged == set(expected), '041_partial_receipt_commit_refused')
        git.call('commit', '-m', COMMIT_MESSAGE)
    current = git.call('rev-parse', 'HEAD').decode().strip()
    if current != parent:
        safe.require(git.call('show', '-s', '--format=%P', current).decode().split() == [parent]
            and safe.git_names(git.call('diff', '--name-only', '-z', parent, current)) == set(expected),
            '041_commit_scope_differs')
    safe.require(all(git.call('show', current + ':' + name) == raw for name, raw in expected.items()),
                 '041_committed_receipt_bytes_differ')
    if current != fetched:
        git.call('push', 'origin', current + ':refs/heads/main')
    remote = git.call('ls-remote', '--exit-code', 'origin', 'refs/heads/main').decode().split()
    safe.require(remote == [current, 'refs/heads/main'], '041_remote_publication_not_verified')
    return current


def workflow(lab, bundle, *, git_runner=None, verifier_runner=verify_return, emit=print):
    lab, bundle = safe.directory(lab), safe.directory(bundle)
    safe.require(bundle.is_relative_to(lab / 'delivery'), '041_bundle_must_be_inside_ignored_delivery')
    release = release_metadata(bundle)
    git = Git(lab, runner=git_runner)
    safe.require(not git.call('ls-files', '-z', '--', bundle.relative_to(lab).as_posix()),
                 '041_private_bundle_is_tracked')
    # A partial prior commit can only contain the one expected receipt path.
    receipt_path = ('artifacts/CHECKPOINT_041_RETURN/' + release['manifest_sha256'] + '/RECEIPT.json')
    prior = ({receipt_path: safe.read_regular(lab / receipt_path)}
             if os.path.lexists(lab / receipt_path) else {})
    check_repository(git, prior)
    relative_files = [path.relative_to(lab).as_posix() for path in bundle.rglob('*') if path.is_file()]
    ignored(git, relative_files)
    folder = safe.directory(lab / WORKFLOW, create=True)
    lock = os.open(folder / 'WORKFLOW.lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        info = os.fstat(lock)
        safe.require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, '041_lock_shape_refused')
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise safe.StageStop('041_workflow_already_active')
        git.call('fetch', '--no-tags', 'origin', 'main')
        fetched = git.call('rev-parse', 'FETCH_HEAD').decode().strip()
        safe.require(git.ancestor(RETURN_COMMIT, release['content_commit']) and
            git.ancestor(release['content_commit'], fetched), '041_release_not_in_return_and_remote_history')
        public, private = load_snapshot(git, bundle, release)
        emit('WORKFLOW: checking original040 return hashes, source delivery and frozen receipts offline.')
        try:
            result = verifier_runner(bundle)
            safe.require(type(result) is dict and result.get('kind') ==
                'P3_ORIGINAL_RETURN_VERIFICATION_041_v1' and
                result.get('integrity_verified') is True, '041_return_verifier_did_not_admit_integrity')
        except Exception as error:
            # Never copy arbitrary exception text or private material into GitHub.
            result = {'kind': 'P3_ORIGINAL_RETURN_VERIFICATION_041_v1',
                      'integrity_verified': False, 'failure_class': type(error).__name__}
        verify_snapshot(bundle, public, private)
        expected = receipt_bytes(release, result, public, private)
        safe.require(not prior or prior == expected, '041_prior_receipt_differs_preserved')
        check_repository(git, expected)
        sync_repository(git, fetched, expected)
        safe.require(git.ancestor(release['content_commit'], 'HEAD'), '041_release_not_in_local_history')
        ignored(git, relative_files)
        commit = publish(git, expected, fetched)
        return {'status': '041_OFFLINE_RECEIPT_PUBLISHED', 'commit': commit,
            'receipt_path': receipt_path, 'integrity_verified': result['integrity_verified'],
            'native_starts': 0, 'model_turns_sent': 0, 'candidate_or_experiment_started': False}
    finally:
        os.close(lock)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lab', type=Path, default=Path.home() / 'ARC_Independent_Lab')
    parser.add_argument('--bundle', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = workflow(args.lab, args.bundle)
    except (safe.StageStop, OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        reason = str(error) if type(error) is safe.StageStop else type(error).__name__
        print('STOP: ' + reason + '. Existing files and commits are preserved.', file=sys.stderr)
        print('No reviewer, model or experiment was started. Repeat the same command for an exact receipt publication retry.', file=sys.stderr)
        return 1
    print('GitHub receipt: https://github.com/' + REPOSITORY + '/blob/' +
          result['commit'] + '/' + result['receipt_path'])
    print('Original040 offline integrity verification: ' +
          ('VERIFIED' if result['integrity_verified'] else 'STOPPED; categorical failure receipt returned'))
    print('No reviewer, model or experiment was started. Future experiment admission is not asserted.')
    return 0 if result['integrity_verified'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
