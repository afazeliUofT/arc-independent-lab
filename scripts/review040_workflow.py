#!/usr/bin/env python3
"""Synchronize checkpoint040, execute its finite controller once, return evidence.

The human calls this from the delivered ZIP. A durable reservation precedes the
controller. Every later call only collects and retries exact evidence publication.
Old032 is imported only for its bounded subprocess transport and safe file writes;
old038 contributes filesystem/Git utilities, never its source-stage operation.
"""
from __future__ import annotations

import argparse
import fcntl
import importlib.util
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys


def sibling(name):
    path = Path(__file__).absolute().with_name(name + '.py')
    spec = importlib.util.spec_from_file_location('_checkpoint040_' + name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


safe = sibling('stage_source_packet038')
transport = sibling('review032_workflow')
publisher = sibling('publish_review040_evidence')
REPOSITORY = safe.REPOSITORY
MANIFEST = 'evidence/P3_FOCUSED_REVIEW_MANIFEST_040.json'
PACKET = 'delivery/P3_FOCUSED_REVIEW_PACKET_040'
WORKFLOW = 'delivery/P3_040_RETURN_WORKFLOW'
MAIN = 'delivery/P3_FOCUSED_REVIEW_040'
CONTROLLER = 'scripts/p3_focused_review_040.py'
SCOPE = 'configs/P3_FOCUSED_REVIEW_SCOPE_040.json'
REQUIRED_CODE = {CONTROLLER, SCOPE, 'scripts/review040_workflow.py',
    'scripts/publish_review040_evidence.py', 'scripts/stage_source_packet038.py',
    'scripts/review032_workflow.py'}
COMMIT_MESSAGE = 'Checkpoint040: return focused review execution or partial-stop evidence'
OUTER_SECONDS = 4310


def release_metadata(bundle):
    value = safe.parse(safe.read_regular(bundle / 'RELEASE.json'))
    safe.require(type(value) is dict and set(value) == {'kind', 'repository',
        'content_commit', 'manifest_path', 'manifest_sha256'} and
        value['kind'] == 'P3_FOCUSED_REVIEW_040_RELEASE_v1' and
        value['repository'] == REPOSITORY and value['manifest_path'] == MANIFEST,
        'wrong040_release_metadata')
    safe.require(type(value['content_commit']) is str and re.fullmatch('[0-9a-f]{40}', value['content_commit'])
        and type(value['manifest_sha256']) is str and re.fullmatch('[0-9a-f]{64}', value['manifest_sha256']),
        'invalid040_release_pin')
    return value


def receipt_payloads(root, collection):
    return {name: safe.read_regular(root / name) for name in collection['tracked_paths']}


def check_repository(git, expected):
    safe.directory(git.root)
    safe.require(git.call('rev-parse', '--show-toplevel').decode().strip() == str(git.root),
                 'wrong_project_root')
    safe.require(git.call('branch', '--show-current').decode().strip() == 'main',
                 'main_branch_required')
    for options in (('--all',), ('--push', '--all')):
        actual = git.call('remote', 'get-url', *options, 'origin').decode().splitlines()
        safe.require(actual == [safe.REMOTE], 'origin_differs_from_authorized_repository')
    for args in (('diff', '--name-only', '-z'), ('diff', '--cached', '--name-only', '-z')):
        paths = safe.git_names(git.call(*args))
        safe.require(paths <= set(expected), 'unrelated_tracked_or_staged_edits_preserved')
        for name in paths:
            safe.require(safe.read_regular(git.root / name) == expected[name],
                         'changed_expected_evidence_preserved')
            if '--cached' in args:
                safe.require(git.call('show', ':' + name) == expected[name],
                             'changed_staged_evidence_preserved')


def sync_repository(git, fetched, expected):
    current = git.call('rev-parse', 'HEAD').decode().strip()
    if current == fetched:
        return
    if git.ancestor(current, fetched):
        safe.require(not git.call('diff', '--cached', '--name-only', '-z').strip(),
                     'staged_evidence_preserved_before_remote_fast_forward')
        git.call('merge', '--ff-only', fetched)
        return
    safe.require(git.ancestor(fetched, current), 'branches_diverged_preserved')
    safe.require(git.call('rev-list', fetched + '..' + current).decode().split() == [current]
        and git.call('show', '-s', '--format=%P', current).decode().split() == [fetched],
        'unrelated_unpublished_commits_preserved')
    changed = safe.git_names(git.call('diff', '--name-only', '-z', fetched, current))
    safe.require(changed and changed == set(expected) and all(
        git.call('show', current + ':' + name) == raw for name, raw in expected.items()),
        'unpublished_commit_is_not_exact040_evidence')


def load_packet(git, bundle, release):
    commit = release['content_commit']
    raw = safe.pinned_file(git, commit, MANIFEST, release['manifest_sha256'])
    manifest = safe.parse(raw)
    safe.require(type(manifest) is dict and type(manifest.get('inputs')) is list
        and type(manifest.get('bundle_files')) is list and 1 <= len(manifest['inputs']) <= 500
        and 1 <= len(manifest['bundle_files']) <= 1000, 'invalid040_manifest')
    public = {}
    for row in manifest['inputs']:
        safe.require(type(row) is dict and set(row) == {'path', 'sha256'}, 'invalid040_public_row')
        name = safe.safe_name(row['path'])
        safe.require(name not in public and name != MANIFEST and not name.startswith(
            ('delivery/', 'private_sources/', 'private_papers/')) and
            not name.lower().endswith(('.pdf', '.png', '.jpg', '.zip')), 'invalid040_public_input')
        public[name] = safe.pinned_file(git, commit, name, row['sha256'])
        # Executable/config bytes must be exact in the actual checkout, not just
        # present somewhere in remote history. Frozen source docs may be newer.
        if name.startswith(('scripts/', 'configs/')):
            safe.require(safe.read_regular(git.root / name) == public[name],
                         'runtime_checkout_differs_from_release_pin')
    safe.require(REQUIRED_CODE <= set(public), '040_required_runtime_pins_missing')
    for name in REQUIRED_CODE:
        if name.startswith('scripts/') and (bundle / name).exists():
            safe.require(safe.read_regular(bundle / name) == public[name],
                         'bundled_runtime_differs_from_release_pin')
    # The currently running workflow and imports must come from the exact bundle.
    for name in ('review040_workflow.py', 'publish_review040_evidence.py',
                 'stage_source_packet038.py', 'review032_workflow.py'):
        safe.require(safe.read_regular(Path(__file__).absolute().with_name(name)) == public['scripts/' + name],
                     'executing_wrapper_differs_from_release_pin')
    payloads = {}
    for row in manifest['bundle_files']:
        safe.require(type(row) is dict and set(row) == {'path', 'sha256'}, 'invalid040_bundle_row')
        name = safe.safe_name(row['path'])
        safe.require(name.startswith('packet/') and name[len('packet/'):] not in payloads
            and re.fullmatch('[0-9a-f]{64}', row['sha256']), 'invalid040_packet_path')
        body = safe.read_regular(bundle / name)
        safe.require(safe.sha(body) == row['sha256'], '040_private_packet_hash_mismatch')
        payloads[name[len('packet/'):]] = body
    safe.require(sum(len(value) for value in payloads.values()) <= safe.MAX_TOTAL,
                 '040_private_packet_total_limit')
    return payloads


def ignored(git, paths):
    for prefix in (PACKET, WORKFLOW, MAIN):
        safe.require(not git.call('ls-files', '-z', '--', prefix).strip(),
                     '040_private_runtime_path_is_tracked')
    names = [PACKET + '/' + name for name in paths]
    names += [WORKFLOW + '/LAUNCH_RESERVED.json', MAIN + '/REPORT.json']
    actual = safe.git_names(git.call('check-ignore', '--no-index', '-z', '--stdin',
        input=b''.join(name.encode() + b'\0' for name in names), allowed=(0, 1)))
    safe.require(actual == set(names), '040_private_runtime_paths_not_ignored')


def install_packet(git, payloads):
    ignored(git, payloads)
    packet = git.root / PACKET
    safe.verify_existing_tree(packet, payloads)
    for name, raw in sorted(payloads.items()):
        safe.write_equal_or_new(packet / name, raw, private=True)
    safe.verify_existing_tree(packet, payloads)
    safe.require(all(safe.read_regular(packet / name) == raw for name, raw in payloads.items()),
                 '040_packet_incomplete')
    ignored(git, payloads)


def publish(git, collection, fetched):
    expected = receipt_payloads(git.root, collection)
    check_repository(git, expected)
    parent = git.call('rev-parse', 'HEAD').decode().strip()
    # Bypass clean filters to preserve exact evidence bytes; verify staged blobs.
    entries = []
    for name, raw in sorted(expected.items()):
        oid = git.call('hash-object', '-w', '--stdin', '--no-filters', input=raw).decode().strip()
        entries.append(('100644 ' + oid + '\t' + name + '\0').encode())
    git.call('update-index', '-z', '--index-info', input=b''.join(entries))
    staged = safe.git_names(git.call('diff', '--cached', '--name-only', '-z'))
    safe.require(staged <= set(expected), 'unrelated_index_change_preserved')
    safe.require(all(git.call('show', ':' + name) == raw for name, raw in expected.items()),
                 '040_staged_evidence_bytes_differ')
    if staged:
        safe.require(staged == set(expected), '040_partial_archive_commit_refused')
        git.call('commit', '-m', COMMIT_MESSAGE)
    current = git.call('rev-parse', 'HEAD').decode().strip()
    if current != parent:
        safe.require(git.call('show', '-s', '--format=%P', current).decode().split() == [parent]
            and safe.git_names(git.call('diff', '--name-only', '-z', parent, current)) == set(expected),
            '040_commit_scope_differs')
    safe.require(all(git.call('show', current + ':' + name) == raw for name, raw in expected.items()),
                 '040_committed_evidence_bytes_differ')
    if current != fetched:
        git.call('push', 'origin', current + ':refs/heads/main')
    remote = git.call('ls-remote', '--exit-code', 'origin', 'refs/heads/main').decode().split()
    safe.require(remote == [current, 'refs/heads/main'], '040_remote_publication_not_verified')
    return current


def invoke(root, emit=print):
    return transport.run_controller(root, emit, command=[sys.executable, '-I', '-B', '-u',
        str(root / CONTROLLER), '--run-attended-review', '--packet', str(root / PACKET)],
        wall_seconds=OUTER_SECONDS)


def workflow(lab, bundle, *, git_runner=None, controller_runner=invoke, emit=print):
    lab, bundle = safe.directory(lab), safe.directory(bundle)
    release = release_metadata(bundle)
    git = safe.Git(lab, runner=git_runner)
    # Identity and clean tracked state checked before local controlled writes.
    folder = lab / WORKFLOW
    prior = (os.path.lexists(folder / 'LAUNCH_RESERVED.json') or os.path.lexists(lab / MAIN)
             or os.path.lexists(folder / 'WORKFLOW_REPORT.json'))
    collection = publisher.collect(lab) if prior else None
    expected = receipt_payloads(lab, collection) if collection else {}
    check_repository(git, expected)
    # Ensure even the workflow's own reservation/lock are ignored before creation.
    ignored(git, ())
    safe.directory(folder, create=True)
    lock = os.open(folder / 'WORKFLOW.lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        info = os.fstat(lock)
        safe.require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1,
                     '040_workflow_lock_shape_refused')
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise safe.StageStop('040_workflow_already_active_no_second_launch')
        # A second process may have completed while this process reached its lock.
        prior = (os.path.lexists(folder / 'LAUNCH_RESERVED.json') or os.path.lexists(lab / MAIN)
             or os.path.lexists(folder / 'WORKFLOW_REPORT.json'))
        if prior:
            collection = publisher.collect(lab)
            expected = receipt_payloads(lab, collection)
        check_repository(git, expected)
        git.call('fetch', '--no-tags', 'origin', 'main')
        fetched = git.call('rev-parse', 'FETCH_HEAD').decode().strip()
        safe.require(git.ancestor(release['content_commit'], fetched),
                     '040_content_commit_not_in_remote_history')
        sync_repository(git, fetched, expected)
        if prior:
            emit('WORKFLOW: existing040 reservation, attempt or stop report; collect and publish only. No model retry.')
            if not os.path.lexists(folder / 'WORKFLOW_REPORT.json'):
                transport.write_json(folder / 'WORKFLOW_REPORT.json', {
                    'kind': 'P3_040_RETURN_WORKFLOW_v1', 'status': 'COLLECT_ONLY_PRIOR_ATTEMPT_REPORT_ABSENT',
                    'controller_invoked_by_this_call': False, 'actual_usage': 'UNKNOWN_SEE_AVAILABLE_NATIVE_RECEIPTS',
                    'automatic_retry': False, 'missing_files_do_not_establish_no_execution': True}, exclusive=True)
        else:
            report = {'kind': 'P3_040_RETURN_WORKFLOW_v1', 'started_utc': transport.utc(),
                'content_commit': release['content_commit'], 'manifest_sha256': release['manifest_sha256'],
                'controller_invoked': False, 'controller_outcome': None, 'automatic_retry': False,
                'fresh_scope040_start_ceiling': 2, 'fresh_scope040_turn_ceiling': 2,
                'scope032_reused': False, 'scope039_reused': False,
                'scientific_admission_asserted': False,
                'actual_usage': 'UNKNOWN_UNTIL_CONTROLLER_AND_NATIVE_RECEIPTS_ARE_REVIEWED',
                'missing_files_do_not_establish_no_execution': True}
            reserved = False
            try:
                payloads = load_packet(git, bundle, release)
                install_packet(git, payloads)
                check_repository(git, {})
                transport.write_json(folder / 'LAUNCH_RESERVED.json', {
                    'kind': 'P3_040_DURABLE_WRAPPER_RESERVATION_v1', 'reserved_utc': transport.utc(),
                    'content_commit': release['content_commit'], 'manifest_sha256': release['manifest_sha256'],
                    'controller_path': CONTROLLER, 'automatic_retry': False,
                    'reservation_is_not_proof_of_native_start': True}, exclusive=True)
                reserved = True
                safe.require(not os.path.lexists(lab / MAIN), '040_attempt_appeared_before_controller_launch')
                report['controller_invoked'] = True
                emit('WORKFLOW: invoking the fresh finite040 controller once; results will be returned automatically.')
                report['controller_outcome'] = controller_runner(lab, emit)
                report['status'] = 'CONTROLLER_RETURNED_EVIDENCE_COLLECTION_REQUIRED'
            except BaseException as error:
                report['status'] = 'WORKFLOW_STOPPED_EVIDENCE_PRESERVED'
                report['reason_code'] = str(error) if type(error) is safe.StageStop else 'guarded040_workflow_failure'
                report['error_class'] = type(error).__name__
                if not reserved:
                    report['no_controller_invocation_by_this_call'] = True
            finally:
                report['finished_utc'] = transport.utc()
                if reserved:
                    transport.write_json(folder / 'LAUNCH_OUTCOME.json', report, exclusive=True)
                transport.write_json(folder / 'WORKFLOW_REPORT.json', report)
        collection = publisher.collect(lab)
        commit = publish(git, collection, fetched)
        return {'status': '040_EVIDENCE_PUBLISHED', 'commit': commit,
            'archive_relative_path': collection['archive_relative_path'],
            'collection_summary': collection['status_summary'], 'collect_only': prior,
            'scientific_admission': 'NOT_ASSERTED_BY_WORKFLOW'}
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
        print('STOP: ' + reason + '. Preserve all existing files. Repeat this same command to collect/retry publication;', file=sys.stderr)
        print('an existing040 reservation prevents another controller or model launch.', file=sys.stderr)
        return 1
    print('GitHub is updated: https://github.com/' + REPOSITORY + '/tree/' + result['commit'] + '/' + result['archive_relative_path'])
    print('Evidence status: ' + result['collection_summary']['collection_status'])
    print('The PI will evaluate the returned verdict, usage and execution boundaries directly from GitHub.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
