#!/usr/bin/env python3
"""Run one bounded outcome-blind development profile and publish its saved result.

The ZIP's public tree is an immutable input snapshot, not an experimental worktree.
One source-pinned Python child runs reference conformance and fabricated workload
profiling. Publication retries reuse its saved output. No native model or target
experiment is invoked; working-directory separation is not OS isolation.
"""
from __future__ import annotations

import argparse
import ctypes
import fcntl
import importlib.util
import os
from pathlib import Path
import re
import resource
import signal
import stat
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True


def module_at(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


safe = module_at(Path(__file__).absolute().with_name('stage_source_packet038.py'),
                 '_checkpoint043_safe')
REPOSITORY = safe.REPOSITORY
MANIFEST = 'evidence/P3_CHECKPOINT_043_MANIFEST.json'
WORKFLOW = 'delivery/P3_043_RETURN_WORKFLOW'
VERIFIER = 'scripts/profile043.py'
PROFILE_SOURCES = {'scripts/accounting043.py', 'scripts/reference_n1_043.py',
    'scripts/reference_n3_043.py', VERIFIER, 'configs/P3_PROFILE_FIXTURES_043.json',
    'tests/test_reference_n1_043.py', 'tests/test_reference_n3_043.py',
    'tests/test_profile043.py'}
CAPS = {'parent_wall_seconds': 300, 'driver_wall_seconds': 270,
    'address_space_bytes': 2 * 1024 ** 3, 'cpu_soft_seconds': 290,
    'cpu_hard_seconds': 300, 'available_cpus_used': 1,
    'maximum_child_file_bytes': 8 * 1024 ** 2}
REQUIRED_CODE = {VERIFIER, 'scripts/checkpoint043_workflow.py',
                 'scripts/stage_source_packet038.py', 'scripts/launch043_home.py',
                 'scripts/downloads_bootstrap043.py'} | PROFILE_SOURCES
RETURN_COMMIT = 'c66f764955c6cfe17d78ae593c290b4ae949e4d3'
RETURN_REPORT_SHA256 = '877c4eeda0b31154d42885f8afbe7e01a56a5a452bdcef56a279b46cb2a7c372'
RETURN_VERDICT_SHA256 = 'a31b9d8ec2103f09d81b963fd7f9ff51c4287490a0f0bf2f74f5dfbc1407d673'
RETURN042_REPORT_SHA256 = '79704515c920415f0ef7c90c70c45a49e44228157e759b26d32f570729ede0ea'
RETURN042_RECEIPT_SHA256 = '0ceb4418024b409638f4f2dfb89d734c29f55261ad7e3e17d674dbd65c71227b'
COMMIT_MESSAGE = 'Checkpoint043: return reserved development profile report and receipt without target execution'


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
        value['kind'] == 'P3_CHECKPOINT_043_RELEASE_v1' and
        value['repository'] == REPOSITORY and value['manifest_path'] == MANIFEST and
        value['accepted_return_commit'] == RETURN_COMMIT,
        'wrong043_release_metadata')
    safe.require(type(value['content_commit']) is str and
        re.fullmatch('[0-9a-f]{40}', value['content_commit']) and
        type(value['manifest_sha256']) is str and
        re.fullmatch('[0-9a-f]{64}', value['manifest_sha256']), 'invalid043_release_pin')
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
                         'changed_expected043_receipt_preserved')
            if '--cached' in args:
                safe.require(git.call('show', ':' + name) == expected[name],
                             'changed_staged043_receipt_preserved')


def ignored(git, paths):
    safe.require(not git.call('ls-files', '-z', '--', WORKFLOW),
                 '043_private_workflow_is_tracked')
    names = [WORKFLOW + '/WORKFLOW.lock', *paths]
    actual = safe.git_names(git.call('check-ignore', '--no-index', '-z', '--stdin',
        input=b''.join(name.encode() + b'\0' for name in names), allowed=(0, 1)))
    safe.require(actual == set(names), '043_private_bundle_or_workflow_not_ignored')


def load_snapshot(git, bundle, release):
    commit = release['content_commit']
    manifest_raw = safe.pinned_file(git, commit, MANIFEST, release['manifest_sha256'])
    safe.require(safe.read_regular(bundle / 'public' / MANIFEST) == manifest_raw,
                 '043_bundled_manifest_differs_from_release')
    manifest = safe.parse(manifest_raw)
    safe.require(type(manifest) is dict and type(manifest.get('inputs')) is list and
        type(manifest.get('private_files')) is list and
        1 <= len(manifest['inputs']) <= 500 and
        1 <= len(manifest['private_files']) <= 500, 'invalid043_manifest')
    public = {MANIFEST: manifest_raw}
    for row in manifest['inputs']:
        safe.require(type(row) is dict and set(row) == {'path', 'sha256'},
                     'invalid043_public_input_row')
        name = safe.safe_name(row['path'])
        safe.require(name not in public and not name.startswith(
            ('delivery/', 'private/', 'private_sources/', 'private_papers/')) and
            not name.lower().endswith(('.pdf', '.png', '.jpg', '.zip')),
            'duplicate_or_private043_public_input')
        public[name] = safe.pinned_file(git, commit, name, row['sha256'])
        safe.require(safe.read_regular(bundle / 'public' / name) == public[name],
                     '043_public_snapshot_differs_from_git_object')
    safe.require(REQUIRED_CODE <= set(public), '043_runtime_dependency_pins_missing')
    for name in ('checkpoint043_workflow.py', 'stage_source_packet038.py'):
        safe.require(safe.read_regular(Path(__file__).absolute().with_name(name)) ==
            public['scripts/' + name], '043_executing_wrapper_differs_from_release')
    safe.require(safe.read_regular(bundle / 'launch043_home.py') ==
        public['scripts/launch043_home.py'], '043_launcher_differs_from_release')
    private = {}
    for row in manifest['private_files']:
        safe.require(type(row) is dict and set(row) == {'path', 'sha256'},
                     'invalid043_private_input_row')
        name = safe.safe_name(row['path'])
        safe.require(name.startswith('private/') and name.removeprefix('private/') not in private and
            type(row['sha256']) is str and re.fullmatch('[0-9a-f]{64}', row['sha256']),
            'invalid043_private_input_path')
        raw = safe.read_regular(bundle / name)
        safe.require(safe.sha(raw) == row['sha256'], '043_private_packet_hash_mismatch')
        private[name.removeprefix('private/')] = raw
    safe.require(sum(map(len, public.values())) + sum(map(len, private.values())) <=
                 safe.MAX_TOTAL, '043_snapshot_byte_limit')
    verify_snapshot(bundle, public, private)
    return public, private


def verify_snapshot(bundle, public, private):
    for prefix, files in (('public', public), ('private', private)):
        folder = bundle / prefix
        safe.verify_existing_tree(folder, files)
        safe.require(all(safe.read_regular(folder / name) == raw for name, raw in files.items()),
                     '043_snapshot_changed_or_incomplete')


def atomic_new(path, raw):
    """Publish a complete file without replacing any existing bytes."""
    safe.directory(path.parent, create=True)
    if os.path.lexists(path):
        safe.require(safe.read_regular(path) == raw, '043_saved_state_differs_preserved')
        return
    fd, name = tempfile.mkstemp(prefix='.atomic043_', dir=path.parent)
    temp = Path(name)
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temp, path, follow_symlinks=False)
        except FileExistsError:
            safe.require(safe.read_regular(path) == raw, '043_concurrent_state_differs_preserved')
        temp.unlink()
        parent_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(parent_fd)
        finally:
            os.close(parent_fd)
    finally:
        if os.path.lexists(temp):
            temp.unlink()
    safe.require(safe.read_regular(path) == raw, '043_atomic_state_verification_failed')


def source_pins(public):
    return [{'path': name, 'sha256': safe.sha(public[name])} for name in sorted(PROFILE_SOURCES)]


def stage_profile_sources(folder, public):
    files = {name: public[name] for name in PROFILE_SOURCES}
    safe.verify_existing_tree(folder, files)
    for name, raw in sorted(files.items()):
        safe.write_equal_or_new(folder / name, raw, private=True)
        (folder / name).chmod(0o400)
    safe.verify_existing_tree(folder, files)
    safe.require(all(safe.read_regular(folder / name) == raw for name, raw in files.items()),
                 '043_profile_source_copy_changed')


def validate_child_report(value):
    safe.require(type(value) is dict and value.get('kind') == 'P3_DEVELOPMENT_PROFILE_043_v1'
        and value.get('status') in ('COMPLETED', 'INCOMPLETE', 'FAILED_CONFORMANCE')
        and value.get('target_experiment_started') is False
        and value.get('target_execution_admitted') is False
        and value.get('native_started') is False
        and value.get('outcome_blind') is True
        and value.get('complete_work_budget_admitted') is False,
        '043_child_report_shape_or_boundary_refused')
    safe.canonical(value)
    return value


def read_child_report(output):
    path = output / 'REPORT.json'
    if not os.path.lexists(path):
        return None, 'MISSING_CHILD_REPORT'
    try:
        raw = safe.read_regular(path)
        safe.require(len(raw) <= CAPS['maximum_child_file_bytes'], '043_child_report_oversized')
        return validate_child_report(safe.parse(raw)), None
    except (safe.StageStop, OSError, ValueError, TypeError, KeyError) as error:
        return None, type(error).__name__


def run_profile_child(source, output):
    """Observe one capped child; stdout/stderr remain private and are never quoted."""
    safe.directory(source)
    safe.directory(output, create=True)
    command = [sys.executable, '-I', '-B', '-S', str(source / VERIFIER),
               '--root', str(source), '--output', str(output)]
    available = sorted(os.sched_getaffinity(0))
    safe.require(bool(available), '043_cpu_affinity_unavailable')
    selected_cpu = available[0]
    owner_pid = os.getpid()
    libc = ctypes.CDLL(None, use_errno=True)

    def limits():
        resource.setrlimit(resource.RLIMIT_AS, (CAPS['address_space_bytes'],) * 2)
        resource.setrlimit(resource.RLIMIT_CPU,
            (CAPS['cpu_soft_seconds'], CAPS['cpu_hard_seconds']))
        resource.setrlimit(resource.RLIMIT_FSIZE, (CAPS['maximum_child_file_bytes'],) * 2)
        os.sched_setaffinity(0, {selected_cpu})
        # Linux/WSL: kill this child if its parent dies, including the pre-exec race.
        if libc.prctl(1, signal.SIGKILL, 0, 0, 0) != 0:
            os._exit(125)
        if os.getppid() != owner_pid:
            os.kill(os.getpid(), signal.SIGKILL)

    handles = []
    child = None
    outcome = {'child_start_observed': False, 'exit_code': None,
        'wall_seconds': None, 'termination': 'NOT_STARTED',
        'available_cpu_count': len(available), 'selected_cpu_count': 1,
        'process_group_kill_attempted': False, 'parent_death_signal_requested': True}
    started = time.monotonic()
    try:
        for name in ('stdout.bin', 'stderr.bin'):
            fd = os.open(output / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
            handles.append(os.fdopen(fd, 'wb'))
        try:
            child = subprocess.Popen(command, cwd=source,
                stdin=subprocess.DEVNULL, stdout=handles[0], stderr=handles[1],
                env={'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8',
                     'TZ': 'UTC', 'TMPDIR': str(output)},
                start_new_session=True, preexec_fn=limits)
        except (OSError, subprocess.SubprocessError) as error:
            outcome.update(termination='START_FAILED', failure_class=type(error).__name__)
        else:
            outcome['child_start_observed'] = True
            try:
                child.wait(timeout=max(0.001, CAPS['parent_wall_seconds'] - (time.monotonic() - started)))
                outcome.update(exit_code=child.returncode, termination='EXITED')
            except subprocess.TimeoutExpired:
                outcome['process_group_kill_attempted'] = True
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                child.wait(timeout=10)
                outcome.update(exit_code=child.returncode, termination='PARENT_WALL_CAP')
    finally:
        if child is not None:
            # Also reap on unexpected wrapper errors; publication must not race a live child.
            try:
                os.killpg(child.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            if child.poll() is None:
                child.wait(timeout=10)
        for handle in handles:
            handle.close()
        outcome['wall_seconds'] = round(time.monotonic() - started, 9)
    for name in ('stdout.bin', 'stderr.bin'):
        path = output / name
        if os.path.lexists(path):
            raw = safe.read_regular(path)
            outcome[name.removesuffix('.bin')] = {'bytes': len(raw), 'sha256': safe.sha(raw),
                'content_published': False}
    return outcome


def execution_report(release, public, outcome, child_report, report_failure):
    complete = (outcome.get('termination') == 'EXITED' and outcome.get('exit_code') == 0
                and child_report is not None and child_report.get('status') == 'COMPLETED')
    return {'kind': 'P3_DEVELOPMENT_PROFILE_EXECUTION_043_v1',
        'release_manifest_sha256': release['manifest_sha256'],
        'content_commit': release['content_commit'],
        'status': 'PROFILE_COMPLETED' if complete else 'PROFILE_INCOMPLETE',
        'profile_report': child_report,
        'profile_report_canonical_sha256': safe.sha(safe.canonical(child_report))
            if child_report is not None else None,
        'child_report_failure_class': report_failure,
        'source_pins': source_pins(public), 'caps': CAPS,
        'execution': outcome, 'reservation_consumed': True,
        'maximum_profile_launches_for_release': 1,
        'profile_launches_observed': (1 if outcome.get('child_start_observed') is True
            else 0 if outcome.get('child_start_observed') is False else None),
        'outcome_blind': True, 'development_reference_profile_only': True,
        'native_starts': 0, 'model_turns_sent': 0, 'target_experiment_started': False,
        'target_execution_admitted': False, 'complete_work_budget_admitted': False,
        'automatic_rerun_permitted': False, 'profile_source_and_working_directory_separation': True,
        'operating_system_isolation_asserted': False, 'private_content_published': False}


def validate_saved_report(raw, release, public):
    value = safe.parse(raw)
    safe.require(type(value) is dict and value.get('kind') ==
        'P3_DEVELOPMENT_PROFILE_EXECUTION_043_v1'
        and value.get('release_manifest_sha256') == release['manifest_sha256']
        and value.get('content_commit') == release['content_commit']
        and value.get('source_pins') == source_pins(public) and value.get('caps') == CAPS
        and value.get('status') in ('PROFILE_COMPLETED', 'PROFILE_INCOMPLETE')
        and value.get('native_starts') == 0 and value.get('model_turns_sent') == 0
        and value.get('target_experiment_started') is False
        and value.get('target_execution_admitted') is False
        and value.get('complete_work_budget_admitted') is False
        and value.get('automatic_rerun_permitted') is False
        and value.get('reservation_consumed') is True
        and value.get('maximum_profile_launches_for_release') == 1
        and value.get('outcome_blind') is True and safe.canonical(value) == raw,
        '043_saved_report_shape_or_release_differs')
    child = value.get('profile_report')
    if child is not None:
        validate_child_report(child)
        safe.require(value.get('profile_report_canonical_sha256') == safe.sha(safe.canonical(child)),
                     '043_saved_child_report_hash_differs')
    return value


def obtain_saved_report(folder, release, public, *, profile_runner=run_profile_child):
    saved = folder / 'SAVED_REPORT.json'
    if os.path.lexists(saved):
        return validate_saved_report(safe.read_regular(saved), release, public)
    reservation_path = folder / 'EXECUTION_RESERVED.json'
    reservation = {'kind': 'P3_DEVELOPMENT_PROFILE_RESERVATION_043_v1',
        'release_manifest_sha256': release['manifest_sha256'],
        'content_commit': release['content_commit'], 'source_pins': source_pins(public),
        'caps': CAPS, 'maximum_profile_launches': 1, 'automatic_rerun_permitted': False}
    source, output = folder / 'execution_source', folder / 'profile_output'
    if os.path.lexists(reservation_path):
        safe.require(safe.read_regular(reservation_path) == safe.canonical(reservation),
                     '043_existing_reservation_differs_preserved')
        child, failure = read_child_report(output)
        outcome = {'child_start_observed': None, 'exit_code': None, 'wall_seconds': None,
            'termination': 'RESERVATION_FOUND_WITHOUT_SAVED_RESULT',
            'automatic_relaunch_refused': True}
    else:
        stage_profile_sources(source, public)
        safe.directory(output, create=True)
        safe.require(not any(output.iterdir()), '043_unreserved_profile_output_preserved')
        atomic_new(reservation_path, safe.canonical(reservation))
        try:
            outcome = profile_runner(source, output)
            safe.require(type(outcome) is dict, '043_child_outcome_shape_refused')
        except Exception as error:
            outcome = {'child_start_observed': None, 'exit_code': None, 'wall_seconds': None,
                'termination': 'WRAPPER_INTERRUPTED_AFTER_RESERVATION',
                'failure_class': type(error).__name__, 'automatic_relaunch_refused': True}
        child, failure = read_child_report(output)
        try:
            expected_sources = {name: public[name] for name in PROFILE_SOURCES}
            safe.verify_existing_tree(source, expected_sources)
            safe.require(all(safe.read_regular(source / name) == raw
                for name, raw in expected_sources.items()), '043_profile_sources_changed')
        except (safe.StageStop, OSError) as error:
            outcome = dict(outcome, termination='PROFILE_SOURCE_CHANGED',
                           source_verification_failure_class=type(error).__name__)
    value = execution_report(release, public, outcome, child, failure)
    atomic_new(saved, safe.canonical(value))
    return validate_saved_report(safe.read_regular(saved), release, public)


def return_files(release, result, public, private):
    folder = 'artifacts/CHECKPOINT_043_RETURN/' + release['manifest_sha256']
    report_path = folder + '/REPORT.json'
    report_raw = safe.canonical(result)
    receipt = {'kind': 'P3_CHECKPOINT_043_DEVELOPMENT_PROFILE_RECEIPT_v1',
        'repository': REPOSITORY, 'content_commit': release['content_commit'],
        'release_manifest_path': MANIFEST, 'release_manifest_sha256': release['manifest_sha256'],
        'accepted_return_commit': RETURN_COMMIT,
        'accepted042_report_sha256': RETURN042_REPORT_SHA256,
        'accepted042_receipt_sha256': RETURN042_RECEIPT_SHA256,
        'profiler_path': VERIFIER, 'profiler_sha256': safe.sha(public[VERIFIER]),
        'profile_source_pins': source_pins(public), 'report_path': report_path,
        'report_sha256': safe.sha(report_raw), 'full_profile_and_execution_result_published': True,
        'profile_status': result['status'], 'public_snapshot_files_verified': len(public),
        'private_packet_files_verified': len(private), 'private_content_published': False,
        'outcome_blind_development_profile_only': True,
        'new_native_allowance': 0, 'native_starts': 0, 'model_turns_sent': 0,
        'cumulative_native_starts': 18, 'cumulative_model_turns_sent': 14,
        'reviewer_or_review_controller_started': False, 'target_experiment_started': False,
        'target_execution_admitted': False, 'complete_work_budget_admitted': False,
        'automatic_profile_rerun_permitted': False,
        'maximum_profile_launches_for_release': 1,
        'profile_launches_observed': result['profile_launches_observed'],
        'historical040_rerun': False, 'historical039_rerun': False,
        'timestamp_omitted_for_publication_idempotence': True}
    return {report_path: report_raw, folder + '/RECEIPT.json': safe.canonical(receipt)}



def sync_repository(git, fetched, expected):
    current = git.call('rev-parse', 'HEAD').decode().strip()
    if current == fetched:
        return
    if git.ancestor(current, fetched):
        safe.require(not git.call('diff', '--cached', '--name-only', '-z').strip(),
                     'staged043_receipt_preserved_before_remote_fast_forward')
        git.call('merge', '--ff-only', fetched)
        return
    safe.require(git.ancestor(fetched, current), 'branches_diverged_preserved')
    safe.require(git.call('rev-list', fetched + '..' + current).decode().split() == [current]
        and git.call('show', '-s', '--format=%P', current).decode().split() == [fetched],
        'unrelated_unpublished_commits_preserved')
    changed = safe.git_names(git.call('diff', '--name-only', '-z', fetched, current))
    safe.require(changed == set(expected) and all(
        git.call('show', current + ':' + name) == raw for name, raw in expected.items()),
        'unpublished_commit_is_not_exact043_receipt')


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
    safe.require(staged <= set(expected), 'unrelated043_index_change_preserved')
    safe.require(all(git.call('show', ':' + name) == raw for name, raw in expected.items()),
                 '043_staged_receipt_bytes_differ')
    if staged:
        safe.require(staged == set(expected), '043_partial_receipt_commit_refused')
        git.call('commit', '-m', COMMIT_MESSAGE)
    current = git.call('rev-parse', 'HEAD').decode().strip()
    if current != parent:
        safe.require(git.call('show', '-s', '--format=%P', current).decode().split() == [parent]
            and safe.git_names(git.call('diff', '--name-only', '-z', parent, current)) == set(expected),
            '043_commit_scope_differs')
    safe.require(all(git.call('show', current + ':' + name) == raw for name, raw in expected.items()),
                 '043_committed_receipt_bytes_differ')
    if current != fetched:
        git.call('push', 'origin', current + ':refs/heads/main')
    remote = git.call('ls-remote', '--exit-code', 'origin', 'refs/heads/main').decode().split()
    safe.require(remote == [current, 'refs/heads/main'], '043_remote_publication_not_verified')
    return current


def workflow(lab, bundle, *, git_runner=None, profile_runner=run_profile_child, emit=print):
    lab, bundle = safe.directory(lab), safe.directory(bundle)
    safe.require(bundle.is_relative_to(lab / 'delivery'), '043_bundle_must_be_inside_ignored_delivery')
    release = release_metadata(bundle)
    git = Git(lab, runner=git_runner)
    safe.require(not git.call('ls-files', '-z', '--', bundle.relative_to(lab).as_posix()),
                 '043_private_bundle_is_tracked')
    return_folder = 'artifacts/CHECKPOINT_043_RETURN/' + release['manifest_sha256']
    receipt_path, report_path = return_folder + '/RECEIPT.json', return_folder + '/REPORT.json'
    prior = {name: safe.read_regular(lab / name) for name in (report_path, receipt_path)
             if os.path.lexists(lab / name)}
    check_repository(git, prior)
    relative_files = [path.relative_to(lab).as_posix() for path in bundle.rglob('*') if path.is_file()]
    ignored(git, relative_files)
    folder = safe.directory(lab / WORKFLOW / release['manifest_sha256'], create=True)
    ignored(git, [str((folder / 'WORKFLOW.lock').relative_to(lab))])
    lock = os.open(folder / 'WORKFLOW.lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        info = os.fstat(lock)
        safe.require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, '043_lock_shape_refused')
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise safe.StageStop('043_workflow_already_active')
        git.call('fetch', '--no-tags', 'origin', 'main')
        fetched = git.call('rev-parse', 'FETCH_HEAD').decode().strip()
        safe.require(git.ancestor(RETURN_COMMIT, release['content_commit']) and
            git.ancestor(release['content_commit'], fetched), '043_release_not_in_return_and_remote_history')
        public, private = load_snapshot(git, bundle, release)
        # Reject unrelated unpublished work before reserving the sole profile launch.
        sync_repository(git, fetched, prior)
        remote_names = safe.git_names(git.call('ls-tree', '--name-only', '-r', '-z', fetched,
                                             '--', report_path, receipt_path))
        if remote_names:
            safe.require(remote_names == {report_path, receipt_path}, '043_partial_remote_return_preserved')
            remote_report = git.call('show', fetched + ':' + report_path)
            result = validate_saved_report(remote_report, release, public)
            expected = return_files(release, result, public, private)
            safe.require(all(git.call('show', fetched + ':' + name) == raw
                             for name, raw in expected.items()), '043_remote_report_or_receipt_differs')
            atomic_new(folder / 'SAVED_REPORT.json', remote_report)
            emit('WORKFLOW: reusing the exact published043 profile; no profile is restarted.')
        else:
            if set(prior) == {report_path, receipt_path}:
                prior_result = validate_saved_report(prior[report_path], release, public)
                safe.require(return_files(release, prior_result, public, private) == prior,
                             '043_prior_local_return_differs_preserved')
                atomic_new(folder / 'SAVED_REPORT.json', prior[report_path])
            emit('WORKFLOW: using the single043 development-profile reservation; retries reuse saved output.')
            result = obtain_saved_report(folder, release, public, profile_runner=profile_runner)
            expected = return_files(release, result, public, private)
        atomic_new(folder / 'SAVED_RECEIPT.json', expected[receipt_path])
        verify_snapshot(bundle, public, private)
        safe.require(all(expected.get(name) == raw for name, raw in prior.items()),
                     '043_prior_report_or_receipt_differs_preserved')
        check_repository(git, expected)
        safe.require(git.ancestor(release['content_commit'], 'HEAD'), '043_release_not_in_local_history')
        ignored(git, relative_files + [path.relative_to(lab).as_posix()
            for path in folder.rglob('*') if path.is_file()])
        commit = publish(git, expected, fetched)
        return {'status': '043_DEVELOPMENT_PROFILE_REPORT_AND_RECEIPT_PUBLISHED', 'commit': commit,
            'receipt_path': receipt_path, 'report_path': report_path, 'profile_status': result['status'],
            'native_starts': 0, 'model_turns_sent': 0, 'target_experiment_started': False}
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
        print('No target experiment or model is authorized. Repeat the same command to recover the saved execution state and retry publication; a reserved profile is never restarted.', file=sys.stderr)
        return 1
    print('GitHub receipt: https://github.com/' + REPOSITORY + '/blob/' +
          result['commit'] + '/' + result['receipt_path'])
    print('GitHub report: https://github.com/' + REPOSITORY + '/blob/' +
          result['commit'] + '/' + result['report_path'])
    print('Development043 profile: ' + result['profile_status'])
    print('No reviewer, model or target experiment was started. Future experiment admission is not asserted.')
    return 0 if result['profile_status'] == 'PROFILE_COMPLETED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
