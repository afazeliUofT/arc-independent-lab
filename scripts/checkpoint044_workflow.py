#!/usr/bin/env python3
"""Continue the incomplete043 development profile once and publish its saved result.

The ZIP's public tree is an immutable input snapshot, not an experimental worktree.
One source-pinned Python child imports six completed043 rows, preserves their
source identity, and may attempt the remaining21 fabricated workload rows once.
Publication retries reuse its saved output. No native model or target
experiment is invoked; working-directory separation is not OS isolation.
"""
from __future__ import annotations

import argparse
import base64
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
                 '_checkpoint044_safe')
REPOSITORY = safe.REPOSITORY
MANIFEST = 'evidence/P3_CHECKPOINT_044_MANIFEST.json'
WORKFLOW = 'delivery/P3_044_RETURN_WORKFLOW'
VERIFIER = 'scripts/profile044.py'
PROFILE_SOURCES = {'scripts/accounting043.py', 'scripts/reference_n1_043.py',
    'scripts/reference_n3_043.py', 'scripts/profile043.py',
    'configs/P3_PROFILE_FIXTURES_043.json', 'tests/test_reference_n1_043.py',
    'tests/test_reference_n3_043.py', 'tests/test_profile043.py', VERIFIER,
    'configs/P3_PROFILE_CONTINUATION_044.json', 'tests/test_profile044.py'}
BASELINE_FOLDER = 'artifacts/CHECKPOINT_043_RETURN/097ca0e6c91e0f3d5b50f7cf98415faf1e8ed57b6f09544f5e2d6c4bdb406582'
BASELINE_REPORT = BASELINE_FOLDER + '/REPORT.json'
BASELINE_RECEIPT = BASELINE_FOLDER + '/RECEIPT.json'
BASELINE_FILES = {BASELINE_REPORT, BASELINE_RECEIPT}
CAPS = {'parent_wall_seconds': 300, 'driver_wall_seconds': 270,
    'address_space_bytes': 2 * 1024 ** 3, 'cpu_soft_seconds': 290,
    'cpu_hard_seconds': 300, 'available_cpus_used': 1,
    'maximum_child_file_bytes': 8 * 1024 ** 2}
REQUIRED_CODE = {VERIFIER, 'scripts/checkpoint044_workflow.py',
                 'scripts/stage_source_packet038.py', 'scripts/launch044_home.py',
                 'scripts/downloads_bootstrap044.py'} | PROFILE_SOURCES | BASELINE_FILES
RETURN_COMMIT = 'f025d2ffe0745e40b2d6718293bfe5d72b54b7ba'
BASELINE_GIT_COMMIT = RETURN_COMMIT
RETURN043_REPORT_SHA256 = '9de019e2d8649895627e7c25d1e46366f4e08c0c890404c3197da3bed0317f61'
RETURN043_RECEIPT_SHA256 = 'b89ab8c0caa981289afa2ab84b8eda0bb22c4dd78abd5d95ec958437e51d1ae0'
CONTINUATION = {'baseline_report_sha256': RETURN043_REPORT_SHA256,
    'imported_completed_rows': 6, 'eligible_new_rows': 21,
    'imported_rows_remeasured': False, 'original043_reservation_preserved': True}
COMMIT_MESSAGE = 'Checkpoint044: return once-reserved profile continuation with preserved043 measurements'



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
        value['kind'] == 'P3_CHECKPOINT_044_RELEASE_v1' and
        value['repository'] == REPOSITORY and value['manifest_path'] == MANIFEST and
        value['accepted_return_commit'] == RETURN_COMMIT,
        'wrong044_release_metadata')
    safe.require(type(value['content_commit']) is str and
        re.fullmatch('[0-9a-f]{40}', value['content_commit']) and
        type(value['manifest_sha256']) is str and
        re.fullmatch('[0-9a-f]{64}', value['manifest_sha256']), 'invalid044_release_pin')
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
                         'changed_expected044_receipt_preserved')
            if '--cached' in args:
                safe.require(git.call('show', ':' + name) == expected[name],
                             'changed_staged044_receipt_preserved')


def ignored(git, paths):
    safe.require(not git.call('ls-files', '-z', '--', WORKFLOW),
                 '044_private_workflow_is_tracked')
    names = [WORKFLOW + '/WORKFLOW.lock', *paths]
    actual = safe.git_names(git.call('check-ignore', '--no-index', '-z', '--stdin',
        input=b''.join(name.encode() + b'\0' for name in names), allowed=(0, 1)))
    safe.require(actual == set(names), '044_private_bundle_or_workflow_not_ignored')


def load_snapshot(git, bundle, release):
    commit = release['content_commit']
    manifest_raw = safe.pinned_file(git, commit, MANIFEST, release['manifest_sha256'])
    safe.require(safe.read_regular(bundle / 'public' / MANIFEST) == manifest_raw,
                 '044_bundled_manifest_differs_from_release')
    manifest = safe.parse(manifest_raw)
    safe.require(type(manifest) is dict and type(manifest.get('inputs')) is list and
        type(manifest.get('private_files')) is list and
        1 <= len(manifest['inputs']) <= 500 and
        1 <= len(manifest['private_files']) <= 500, 'invalid044_manifest')
    public = {MANIFEST: manifest_raw}
    for row in manifest['inputs']:
        safe.require(type(row) is dict and set(row) == {'path', 'sha256'},
                     'invalid044_public_input_row')
        name = safe.safe_name(row['path'])
        safe.require(name not in public and not name.startswith(
            ('delivery/', 'private/', 'private_sources/', 'private_papers/')) and
            not name.lower().endswith(('.pdf', '.png', '.jpg', '.zip')),
            'duplicate_or_private044_public_input')
        public[name] = safe.pinned_file(git, commit, name, row['sha256'])
        safe.require(safe.read_regular(bundle / 'public' / name) == public[name],
                     '044_public_snapshot_differs_from_git_object')
    safe.require(REQUIRED_CODE <= set(public), '044_runtime_dependency_pins_missing')
    for name, expected in ((BASELINE_REPORT, RETURN043_REPORT_SHA256),
                           (BASELINE_RECEIPT, RETURN043_RECEIPT_SHA256)):
        safe.require(safe.pinned_file(git, RETURN_COMMIT, name, expected) == public[name],
                     '044_baseline_differs_from_accepted043_git_return')
    validate_baseline(public)
    for name in ('checkpoint044_workflow.py', 'stage_source_packet038.py'):
        safe.require(safe.read_regular(Path(__file__).absolute().with_name(name)) ==
            public['scripts/' + name], '044_executing_wrapper_differs_from_release')
    safe.require(safe.read_regular(bundle / 'launch044_home.py') ==
        public['scripts/launch044_home.py'], '044_launcher_differs_from_release')
    private = {}
    for row in manifest['private_files']:
        safe.require(type(row) is dict and set(row) == {'path', 'sha256'},
                     'invalid044_private_input_row')
        name = safe.safe_name(row['path'])
        safe.require(name.startswith('private/') and name.removeprefix('private/') not in private and
            type(row['sha256']) is str and re.fullmatch('[0-9a-f]{64}', row['sha256']),
            'invalid044_private_input_path')
        raw = safe.read_regular(bundle / name)
        safe.require(safe.sha(raw) == row['sha256'], '044_private_packet_hash_mismatch')
        private[name.removeprefix('private/')] = raw
    safe.require(sum(map(len, public.values())) + sum(map(len, private.values())) <=
                 safe.MAX_TOTAL, '044_snapshot_byte_limit')
    verify_snapshot(bundle, public, private)
    return public, private


def verify_snapshot(bundle, public, private):
    for prefix, files in (('public', public), ('private', private)):
        folder = bundle / prefix
        safe.verify_existing_tree(folder, files)
        safe.require(all(safe.read_regular(folder / name) == raw for name, raw in files.items()),
                     '044_snapshot_changed_or_incomplete')


def atomic_new(path, raw):
    """Publish a complete file without replacing any existing bytes."""
    safe.directory(path.parent, create=True)
    if os.path.lexists(path):
        safe.require(safe.read_regular(path) == raw, '044_saved_state_differs_preserved')
        return
    fd, name = tempfile.mkstemp(prefix='.atomic044_', dir=path.parent)
    temp = Path(name)
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temp, path, follow_symlinks=False)
        except FileExistsError:
            safe.require(safe.read_regular(path) == raw, '044_concurrent_state_differs_preserved')
        temp.unlink()
        parent_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(parent_fd)
        finally:
            os.close(parent_fd)
    finally:
        if os.path.lexists(temp):
            temp.unlink()
    safe.require(safe.read_regular(path) == raw, '044_atomic_state_verification_failed')


def source_pins(public):
    return [{'path': name, 'sha256': safe.sha(public[name])} for name in sorted(PROFILE_SOURCES)]


def baseline_pins(public):
    return [{'path': name, 'sha256': safe.sha(public[name])} for name in sorted(BASELINE_FILES)]


def validate_baseline(public):
    safe.require(safe.sha(public[BASELINE_REPORT]) == RETURN043_REPORT_SHA256 and
        safe.sha(public[BASELINE_RECEIPT]) == RETURN043_RECEIPT_SHA256,
        '044_original043_baseline_hash_differs')
    report, receipt = (safe.parse(public[name]) for name in (BASELINE_REPORT, BASELINE_RECEIPT))
    safe.require(receipt.get('report_sha256') == RETURN043_REPORT_SHA256 and
        receipt.get('report_path') == BASELINE_REPORT and
        receipt.get('profile_source_pins') == report.get('source_pins') and
        report.get('profile_launches_observed') == 1 and
        report.get('reservation_consumed') is True and
        report.get('status') == 'PROFILE_INCOMPLETE', '044_original043_provenance_differs')
    for pin in report['source_pins']:
        safe.require(pin['path'] in PROFILE_SOURCES and
            safe.sha(public[pin['path']]) == pin['sha256'],
            '044_original043_source_identity_not_preserved')


def stage_baseline(folder, public):
    files = {Path(name).name: public[name] for name in BASELINE_FILES}
    safe.verify_existing_tree(folder, files)
    for name, raw in sorted(files.items()):
        safe.write_equal_or_new(folder / name, raw, private=True)
        (folder / name).chmod(0o400)
    safe.verify_existing_tree(folder, files)
    safe.require(all(safe.read_regular(folder / name) == raw for name, raw in files.items()),
                 '044_original043_baseline_copy_changed')


def stage_profile_sources(folder, public):
    files = {name: public[name] for name in PROFILE_SOURCES}
    safe.verify_existing_tree(folder, files)
    for name, raw in sorted(files.items()):
        safe.write_equal_or_new(folder / name, raw, private=True)
        (folder / name).chmod(0o400)
    safe.verify_existing_tree(folder, files)
    safe.require(all(safe.read_regular(folder / name) == raw for name, raw in files.items()),
                 '044_profile_source_copy_changed')


def validate_child_report(value):
    safe.require(type(value) is dict and value.get('kind') == 'P3_DEVELOPMENT_PROFILE_044_v1'
        and value.get('status') in ('COMPLETED', 'INCOMPLETE', 'FAILED_CONFORMANCE')
        and value.get('target_experiment_started') is False
        and value.get('target_execution_admitted') is False
        and value.get('native_started') is False
        and value.get('outcome_blind') is True
        and value.get('complete_work_budget_admitted') is False
        and type(value.get('continuation')) is dict
        and all(value['continuation'].get(key) == expected for key, expected in CONTINUATION.items()),
        '044_child_report_shape_or_boundary_refused')
    safe.canonical(value)
    return value


def validate_continuation(value, public):
    """Check row identity/provenance and invocation accounting without importing a learner."""
    baseline = safe.parse(public[BASELINE_REPORT])
    prior = baseline['profile_report']
    current_hashes = {pin['path']: pin['sha256'] for pin in source_pins(public)}
    rows = value.get('profiles')
    safe.require(type(rows) is list and len(rows) == 27 and
        value.get('source_hashes') == current_hashes and
        value.get('B_comp') is None and value.get('B_mem') is None and
        value.get('automatic_remeasurement') is False,
        '044_continuation_row_count_sources_or_budget_differs')
    for index, row in enumerate(rows):
        original = prior['profiles'][index]
        safe.require(type(row) is dict and all(row.get(key) == original[key]
            for key in ('case', 'size', 'repetition')), '044_continuation_row_identity_differs')
        provenance = row.get('measurement_provenance')
        if index < 6:
            expected = {'release': '043', 'imported': True, 'remeasured': False,
                'baseline_report_sha256': RETURN043_REPORT_SHA256,
                'baseline_git_commit': BASELINE_GIT_COMMIT, 'original_row_index': index,
                'original_row_canonical_sha256': safe.sha(safe.canonical(original)),
                'source_hashes': prior['source_hashes']}
            safe.require(provenance == expected and
                {key: item for key, item in row.items() if key != 'measurement_provenance'} == original,
                '044_imported043_measurement_or_provenance_changed')
        else:
            safe.require(type(provenance) is dict and
                type(provenance.get('new_invocation_attempt_reserved')) is bool,
                '044_new_row_reservation_provenance_missing')
            expected = {'release': '044', 'imported': False, 'original_row_index': index,
                'original043_status': original['status'], 'source_hashes': current_hashes,
                'new_invocation_attempt_reserved': provenance['new_invocation_attempt_reserved']}
            safe.require(provenance == expected and row.get('status') in
                ('NOT_STARTED', 'RESERVED', 'COMPLETED', 'INCOMPLETE', 'FAILED_CONFORMANCE') and
                (row['status'] == 'NOT_STARTED' or provenance['new_invocation_attempt_reserved']) and
                (row['status'] != 'COMPLETED' or type(row.get('metrics')) is dict),
                '044_new_row_provenance_or_reservation_differs')
    continuation = value['continuation']
    safe.require(continuation.get('baseline_git_commit') == BASELINE_GIT_COMMIT and
        continuation.get('prior_failed_attempts') == [prior['profiles'][6]] and
        continuation.get('new_rows_attempted') == sum(
            row['measurement_provenance']['new_invocation_attempt_reserved'] for row in rows[6:]) and
        continuation.get('new_rows_completed') == sum(row['status'] == 'COMPLETED' for row in rows[6:]),
        '044_continuation_attempt_counts_or_failed043_evidence_differs')
    metrics = value.get('invocation_metrics')
    aggregate = value.get('aggregate_metrics')
    safe.require(type(metrics) is dict and metrics.get('original043') ==
        {'aggregate_metrics': prior['aggregate_metrics'], 'wrapper_execution': baseline['execution'],
         'host': prior['host']} and
        type(value.get('host')) is dict and value['host'].get('scope') == '044_INVOCATION_ONLY' and
        metrics.get('continuation044') == aggregate and
        (aggregate is None or (type(aggregate) is dict and aggregate.get('scope') ==
            '044_INVOCATION_ONLY_EXCLUDES_IMPORTED_043_MEASUREMENTS')),
        '044_invocation_usage_not_separate_or_baseline_usage_changed')
    if value['status'] == 'COMPLETED':
        safe.require(all(row['status'] == 'COMPLETED' for row in rows) and
            continuation['new_rows_attempted'] == 21 and type(aggregate) is dict and
            type(value.get('conformance')) is dict and value['conformance'].get('status') == 'COMPLETED' and
            type(value['conformance'].get('summary')) is dict and
            value['conformance']['summary'].get('passed') is True,
            '044_completed_claim_without_complete_rows_conformance_and_usage')


def read_child_report(output, public=None):
    path = output / 'REPORT.json'
    if not os.path.lexists(path):
        return None, 'MISSING_CHILD_REPORT'
    try:
        raw = safe.read_regular(path)
        safe.require(len(raw) <= CAPS['maximum_child_file_bytes'], '044_child_report_oversized')
        value = validate_child_report(safe.parse(raw))
        if public is not None:
            validate_continuation(value, public)
        return value, None
    except (safe.StageStop, OSError, ValueError, TypeError, KeyError) as error:
        return None, str(error) if type(error) is safe.StageStop else type(error).__name__


def rejected_child_evidence(output, failure):
    """Retain uninterpreted bytes for a rejected report without accepting its claims."""
    path = output / 'REPORT.json'
    if not failure or not os.path.lexists(path):
        return None
    try:
        raw = safe.read_regular(path)
        safe.require(len(raw) <= CAPS['maximum_child_file_bytes'], '044_child_report_oversized')
        return {'interpretation': 'REJECTED_CHILD_OUTPUT_NOT_ACCEPTED_MEASUREMENTS',
            'bytes': len(raw), 'sha256': safe.sha(raw), 'encoding': 'base64',
            'content': base64.b64encode(raw).decode('ascii')}
    except (safe.StageStop, OSError):
        return None


def run_profile_child(source, output):
    """Observe one capped child; stdout/stderr remain private and are never quoted."""
    safe.directory(source)
    safe.directory(output, create=True)
    command = [sys.executable, '-I', '-B', '-S', str(source / VERIFIER),
               '--root', str(source), '--output', str(output),
               '--prior-report', str(source.parent / 'baseline_043' / 'REPORT.json')]
    available = sorted(os.sched_getaffinity(0))
    safe.require(bool(available), '044_cpu_affinity_unavailable')
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


def execution_report(release, public, outcome, child_report, report_failure, rejected_child=None):
    complete = (outcome.get('termination') == 'EXITED' and outcome.get('exit_code') == 0
                and child_report is not None and child_report.get('status') == 'COMPLETED')
    return {'kind': 'P3_DEVELOPMENT_PROFILE_EXECUTION_044_v1',
        'release_manifest_sha256': release['manifest_sha256'],
        'content_commit': release['content_commit'],
        'status': 'PROFILE_COMPLETED' if complete else 'PROFILE_INCOMPLETE',
        'profile_report': child_report,
        'profile_report_canonical_sha256': safe.sha(safe.canonical(child_report))
            if child_report is not None else None,
        'child_report_failure_class': report_failure,
        'rejected_child_report': rejected_child,
        'source_pins': source_pins(public), 'caps': CAPS,
        'baseline_pins': baseline_pins(public), 'continuation': CONTINUATION,
        'baseline_return_commit': RETURN_COMMIT,
        'baseline_report_path': BASELINE_REPORT,
        'original043_failure': {'wrapper_status': 'PROFILE_INCOMPLETE',
            'child_status': 'FAILED_CONFORMANCE', 'failure_class': 'KeyError',
            'failed_row': {'size': 'small', 'case': 'n3_proposal_and_credit', 'repetition': 0},
            'original_wrapper_wall_seconds': 3.172950293,
            'original_measurements_remain_immutable': True},
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
        'P3_DEVELOPMENT_PROFILE_EXECUTION_044_v1'
        and value.get('release_manifest_sha256') == release['manifest_sha256']
        and value.get('content_commit') == release['content_commit']
        and value.get('source_pins') == source_pins(public) and value.get('caps') == CAPS
        and value.get('baseline_pins') == baseline_pins(public)
        and value.get('continuation') == CONTINUATION
        and value.get('baseline_return_commit') == RETURN_COMMIT
        and value.get('status') in ('PROFILE_COMPLETED', 'PROFILE_INCOMPLETE')
        and value.get('native_starts') == 0 and value.get('model_turns_sent') == 0
        and value.get('target_experiment_started') is False
        and value.get('target_execution_admitted') is False
        and value.get('complete_work_budget_admitted') is False
        and value.get('automatic_rerun_permitted') is False
        and value.get('reservation_consumed') is True
        and value.get('maximum_profile_launches_for_release') == 1
        and value.get('outcome_blind') is True and safe.canonical(value) == raw,
        '044_saved_report_shape_or_release_differs')
    child = value.get('profile_report')
    if child is not None:
        validate_child_report(child)
        validate_continuation(child, public)
        safe.require(value.get('profile_report_canonical_sha256') == safe.sha(safe.canonical(child)),
                     '044_saved_child_report_hash_differs')
    complete = (value['execution'].get('termination') == 'EXITED' and
        value['execution'].get('exit_code') == 0 and child is not None and child['status'] == 'COMPLETED')
    safe.require(value['status'] == ('PROFILE_COMPLETED' if complete else 'PROFILE_INCOMPLETE'),
                 '044_wrapper_status_differs_from_validated_execution')
    rejected = value.get('rejected_child_report')
    if rejected is not None:
        safe.require(child is None and value.get('child_report_failure_class') and
            rejected.get('encoding') == 'base64' and rejected.get('interpretation') ==
            'REJECTED_CHILD_OUTPUT_NOT_ACCEPTED_MEASUREMENTS', '044_rejected_child_evidence_shape_differs')
        decoded = base64.b64decode(rejected['content'], validate=True)
        safe.require(len(decoded) == rejected['bytes'] and safe.sha(decoded) == rejected['sha256'],
                     '044_rejected_child_evidence_bytes_differ')
    return value


def obtain_saved_report(folder, release, public, *, profile_runner=run_profile_child):
    saved = folder / 'SAVED_REPORT.json'
    if os.path.lexists(saved):
        return validate_saved_report(safe.read_regular(saved), release, public)
    reservation_path = folder / 'EXECUTION_RESERVED.json'
    reservation = {'kind': 'P3_DEVELOPMENT_PROFILE_RESERVATION_044_v1',
        'release_manifest_sha256': release['manifest_sha256'],
        'content_commit': release['content_commit'], 'source_pins': source_pins(public),
        'baseline_pins': baseline_pins(public), 'continuation': CONTINUATION,
        'caps': CAPS, 'maximum_profile_launches': 1, 'automatic_rerun_permitted': False}
    source, output = folder / 'execution_source', folder / 'profile_output'
    if os.path.lexists(reservation_path):
        safe.require(safe.read_regular(reservation_path) == safe.canonical(reservation),
                     '044_existing_reservation_differs_preserved')
        child, failure = read_child_report(output, public)
        outcome = {'child_start_observed': None, 'exit_code': None, 'wall_seconds': None,
            'termination': 'RESERVATION_FOUND_WITHOUT_SAVED_RESULT',
            'automatic_relaunch_refused': True}
    else:
        validate_baseline(public)
        stage_profile_sources(source, public)
        stage_baseline(folder / 'baseline_043', public)
        safe.directory(output, create=True)
        safe.require(not any(output.iterdir()), '044_unreserved_profile_output_preserved')
        atomic_new(reservation_path, safe.canonical(reservation))
        try:
            outcome = profile_runner(source, output)
            safe.require(type(outcome) is dict, '044_child_outcome_shape_refused')
        except Exception as error:
            outcome = {'child_start_observed': None, 'exit_code': None, 'wall_seconds': None,
                'termination': 'WRAPPER_INTERRUPTED_AFTER_RESERVATION',
                'failure_class': type(error).__name__, 'automatic_relaunch_refused': True}
        child, failure = read_child_report(output, public)
        try:
            expected_sources = {name: public[name] for name in PROFILE_SOURCES}
            safe.verify_existing_tree(source, expected_sources)
            safe.require(all(safe.read_regular(source / name) == raw
                for name, raw in expected_sources.items()), '044_profile_sources_changed')
            baseline = {Path(name).name: public[name] for name in BASELINE_FILES}
            safe.verify_existing_tree(folder / 'baseline_043', baseline)
            safe.require(all(safe.read_regular(folder / 'baseline_043' / name) == raw
                for name, raw in baseline.items()), '044_original043_baseline_changed')
        except (safe.StageStop, OSError) as error:
            outcome = dict(outcome, termination='PROFILE_SOURCE_CHANGED',
                           source_verification_failure_class=type(error).__name__)
    value = execution_report(release, public, outcome, child, failure,
                             rejected_child_evidence(output, failure))
    atomic_new(saved, safe.canonical(value))
    return validate_saved_report(safe.read_regular(saved), release, public)


def return_files(release, result, public, private):
    folder = 'artifacts/CHECKPOINT_044_RETURN/' + release['manifest_sha256']
    report_path = folder + '/REPORT.json'
    report_raw = safe.canonical(result)
    receipt = {'kind': 'P3_CHECKPOINT_044_DEVELOPMENT_PROFILE_RECEIPT_v1',
        'repository': REPOSITORY, 'content_commit': release['content_commit'],
        'release_manifest_path': MANIFEST, 'release_manifest_sha256': release['manifest_sha256'],
        'accepted_return_commit': RETURN_COMMIT,
        'accepted043_report_sha256': RETURN043_REPORT_SHA256,
        'accepted043_receipt_sha256': RETURN043_RECEIPT_SHA256,
        'accepted043_report_path': BASELINE_REPORT,
        'accepted043_receipt_path': BASELINE_RECEIPT,
        'continuation': CONTINUATION,
        'original043_profile_restarted': False,
        'original043_failed_attempt_retained_in_baseline_report': True,
        'original043_completed_rows_keep_original_source_identity': True,
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
                     'staged044_receipt_preserved_before_remote_fast_forward')
        git.call('merge', '--ff-only', fetched)
        return
    safe.require(git.ancestor(fetched, current), 'branches_diverged_preserved')
    safe.require(git.call('rev-list', fetched + '..' + current).decode().split() == [current]
        and git.call('show', '-s', '--format=%P', current).decode().split() == [fetched],
        'unrelated_unpublished_commits_preserved')
    changed = safe.git_names(git.call('diff', '--name-only', '-z', fetched, current))
    safe.require(changed == set(expected) and all(
        git.call('show', current + ':' + name) == raw for name, raw in expected.items()),
        'unpublished_commit_is_not_exact044_receipt')


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
    safe.require(staged <= set(expected), 'unrelated044_index_change_preserved')
    safe.require(all(git.call('show', ':' + name) == raw for name, raw in expected.items()),
                 '044_staged_receipt_bytes_differ')
    if staged:
        safe.require(staged == set(expected), '044_partial_receipt_commit_refused')
        git.call('commit', '-m', COMMIT_MESSAGE)
    current = git.call('rev-parse', 'HEAD').decode().strip()
    if current != parent:
        safe.require(git.call('show', '-s', '--format=%P', current).decode().split() == [parent]
            and safe.git_names(git.call('diff', '--name-only', '-z', parent, current)) == set(expected),
            '044_commit_scope_differs')
    safe.require(all(git.call('show', current + ':' + name) == raw for name, raw in expected.items()),
                 '044_committed_receipt_bytes_differ')
    if current != fetched:
        git.call('push', 'origin', current + ':refs/heads/main')
    remote = git.call('ls-remote', '--exit-code', 'origin', 'refs/heads/main').decode().split()
    safe.require(remote == [current, 'refs/heads/main'], '044_remote_publication_not_verified')
    return current


def workflow(lab, bundle, *, git_runner=None, profile_runner=run_profile_child, emit=print):
    lab, bundle = safe.directory(lab), safe.directory(bundle)
    safe.require(bundle.is_relative_to(lab / 'delivery'), '044_bundle_must_be_inside_ignored_delivery')
    release = release_metadata(bundle)
    git = Git(lab, runner=git_runner)
    safe.require(not git.call('ls-files', '-z', '--', bundle.relative_to(lab).as_posix()),
                 '044_private_bundle_is_tracked')
    return_folder = 'artifacts/CHECKPOINT_044_RETURN/' + release['manifest_sha256']
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
        safe.require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, '044_lock_shape_refused')
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise safe.StageStop('044_workflow_already_active')
        git.call('fetch', '--no-tags', 'origin', 'main')
        fetched = git.call('rev-parse', 'FETCH_HEAD').decode().strip()
        safe.require(git.ancestor(RETURN_COMMIT, release['content_commit']) and
            git.ancestor(release['content_commit'], fetched), '044_release_not_in_return_and_remote_history')
        public, private = load_snapshot(git, bundle, release)
        # Reject unrelated unpublished work before reserving the sole profile launch.
        sync_repository(git, fetched, prior)
        remote_names = safe.git_names(git.call('ls-tree', '--name-only', '-r', '-z', fetched,
                                             '--', report_path, receipt_path))
        if remote_names:
            safe.require(remote_names == {report_path, receipt_path}, '044_partial_remote_return_preserved')
            remote_report = git.call('show', fetched + ':' + report_path)
            result = validate_saved_report(remote_report, release, public)
            expected = return_files(release, result, public, private)
            safe.require(all(git.call('show', fetched + ':' + name) == raw
                             for name, raw in expected.items()), '044_remote_report_or_receipt_differs')
            atomic_new(folder / 'SAVED_REPORT.json', remote_report)
            emit('WORKFLOW: reusing the exact published044 profile; no profile is restarted.')
        else:
            if set(prior) == {report_path, receipt_path}:
                prior_result = validate_saved_report(prior[report_path], release, public)
                safe.require(return_files(release, prior_result, public, private) == prior,
                             '044_prior_local_return_differs_preserved')
                atomic_new(folder / 'SAVED_REPORT.json', prior[report_path])
            emit('WORKFLOW: importing six completed043 rows and using the single044 reservation for the remaining21 rows; retries reuse saved output.')
            result = obtain_saved_report(folder, release, public, profile_runner=profile_runner)
            expected = return_files(release, result, public, private)
        atomic_new(folder / 'SAVED_RECEIPT.json', expected[receipt_path])
        verify_snapshot(bundle, public, private)
        safe.require(all(expected.get(name) == raw for name, raw in prior.items()),
                     '044_prior_report_or_receipt_differs_preserved')
        check_repository(git, expected)
        safe.require(git.ancestor(release['content_commit'], 'HEAD'), '044_release_not_in_local_history')
        ignored(git, relative_files + [path.relative_to(lab).as_posix()
            for path in folder.rglob('*') if path.is_file()])
        commit = publish(git, expected, fetched)
        return {'status': '044_DEVELOPMENT_PROFILE_REPORT_AND_RECEIPT_PUBLISHED', 'commit': commit,
            'receipt_path': receipt_path, 'report_path': report_path, 'profile_status': result['status'],
            'profile_reason': ((result['profile_report'].get('interruption')
                if result['profile_report'] is not None else None) or
                result['child_report_failure_class'] or result['execution'].get('termination')),
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
    print('Development044 profile: ' + result['profile_status'])
    if result['profile_status'] != 'PROFILE_COMPLETED':
        print('The continuation is incomplete; its full available result was successfully published. '
              'Reason: ' + str(result['profile_reason']) + '. Repeating this command does not remeasure any row.')
    print('Six completed043 measurements and the original043 failed attempt are preserved; '
          'new044 invocation usage is reported separately.')
    print('No reviewer, model or target experiment was started. Future experiment admission is not asserted.')
    # Publication success and profile completeness are different outcomes.
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
