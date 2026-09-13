#!/usr/bin/env python3
"""Run the source-pinned046 development resource profile once and publish evidence.

Accepted043–045 measurements, diagnostic results and reservations remain immutable.
This invocation measures fabricated full-work fixtures; it starts no target
experiment, reviewer or model API. Publication retries reuse the first reserved
execution evidence, including incomplete or rejected output.
"""
from __future__ import annotations

import argparse
import base64
import ctypes
import fcntl
import hashlib
import importlib.util
import json
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
import zlib

sys.dont_write_bytecode = True


def module_at(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


safe = module_at(Path(__file__).absolute().with_name('stage_source_packet038.py'),
                 '_checkpoint046_safe')
REPOSITORY = safe.REPOSITORY
MANIFEST = 'evidence/P3_CHECKPOINT_046_MANIFEST.json'
WORKFLOW = 'delivery/P3_046_RETURN_WORKFLOW'
VERIFIER = 'scripts/profile046.py'
PROFILE_SOURCES = {'scripts/accounting043.py', 'scripts/reference_n1_043.py',
    'scripts/reference_n3_043.py', 'scripts/diagnostics045.py', 'scripts/fullwork046.py', VERIFIER,
    'configs/P3_FULL_WORK_FIXTURES_046.json', 'tests/test_fullwork046.py'}
BASELINE_FOLDER = 'artifacts/CHECKPOINT_045_RETURN/9685b38ec4c503e4944a1c3ae5d63c2ed6247541ef97bf85bcc78d9d9bf72e25'
BASELINE_REPORT = BASELINE_FOLDER + '/REPORT.json'
BASELINE_RECEIPT = BASELINE_FOLDER + '/RECEIPT.json'
BASELINE_FILES = {BASELINE_REPORT, BASELINE_RECEIPT}
WORKER_NAMES = {'CONFORMANCE.json'} | {'row_%02d.json' % i for i in range(48)}
CAPS = {'parent_wall_seconds': 14400, 'driver_wall_seconds': 14100,
    'profile_row_wall_seconds': 1200, 'conformance_wall_seconds': 270,
    'address_space_bytes': 2 * 1024 ** 3, 'cpu_soft_seconds': 14390,
    'cpu_hard_seconds': 14400, 'available_cpus_used': 1,
    'maximum_child_file_bytes': 32 * 1024 ** 2,
    'maximum_child_report_bytes': 16 * 1024 ** 2}
REQUIRED_CODE = {VERIFIER, 'scripts/checkpoint046_workflow.py',
                 'scripts/stage_source_packet038.py', 'scripts/launch046_home.py',
                 'scripts/downloads_bootstrap046.py'} | PROFILE_SOURCES | BASELINE_FILES
RETURN_COMMIT = '72f0792d242bfe19e59a0ed765d09748879926d6'
RETURN045_REPORT_SHA256 = 'b66c9e0bb8b324b5d1be1a9eb48c44c5dc502716590a6744400bacaa156623dc'
RETURN045_RECEIPT_SHA256 = 'a17a9902d5374ad3c46e5764fdd5cb544e730b89c4b29215993304d72be09361'
SCOPE = {'accepted045_report_sha256': RETURN045_REPORT_SHA256,
    'accepted045_passed_tests': 23, 'accepted045_passed_case_families': 13,
    'original043044045_remeasured': False, 'fabricated_resource_profile_only': True,
    'complete_work_budget_admitted': False}
COMMIT_MESSAGE = 'Checkpoint046: return once-reserved full-work resource profile and execution receipt'


def compact_json(value):
    """The exact sorted ASCII JSON encoding used by the frozen046 driver."""
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                       allow_nan=False) + '\n').encode('ascii')


def execution_bytes(value):
    raw = compact_json(value)
    safe.require(len(raw) <= safe.MAX_FILE, '046_outer_report_size_limit')
    return raw



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
        value['kind'] == 'P3_CHECKPOINT_046_RELEASE_v1' and
        value['repository'] == REPOSITORY and value['manifest_path'] == MANIFEST and
        value['accepted_return_commit'] == RETURN_COMMIT,
        'wrong046_release_metadata')
    safe.require(type(value['content_commit']) is str and
        re.fullmatch('[0-9a-f]{40}', value['content_commit']) and
        type(value['manifest_sha256']) is str and
        re.fullmatch('[0-9a-f]{64}', value['manifest_sha256']), 'invalid046_release_pin')
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
                         'changed_expected046_receipt_preserved')
            if '--cached' in args:
                safe.require(git.call('show', ':' + name) == expected[name],
                             'changed_staged046_receipt_preserved')


def ignored(git, paths):
    safe.require(not git.call('ls-files', '-z', '--', WORKFLOW),
                 '046_private_workflow_is_tracked')
    names = [WORKFLOW + '/WORKFLOW.lock', *paths]
    actual = safe.git_names(git.call('check-ignore', '--no-index', '-z', '--stdin',
        input=b''.join(name.encode() + b'\0' for name in names), allowed=(0, 1)))
    safe.require(actual == set(names), '046_private_bundle_or_workflow_not_ignored')


def load_snapshot(git, bundle, release):
    commit = release['content_commit']
    manifest_raw = safe.pinned_file(git, commit, MANIFEST, release['manifest_sha256'])
    safe.require(safe.read_regular(bundle / 'public' / MANIFEST) == manifest_raw,
                 '046_bundled_manifest_differs_from_release')
    manifest = safe.parse(manifest_raw)
    safe.require(type(manifest) is dict and type(manifest.get('inputs')) is list and
        type(manifest.get('private_files')) is list and
        1 <= len(manifest['inputs']) <= 500 and
        1 <= len(manifest['private_files']) <= 500, 'invalid046_manifest')
    public = {MANIFEST: manifest_raw}
    for row in manifest['inputs']:
        safe.require(type(row) is dict and set(row) == {'path', 'sha256'},
                     'invalid046_public_input_row')
        name = safe.safe_name(row['path'])
        safe.require(name not in public and not name.startswith(
            ('delivery/', 'private/', 'private_sources/', 'private_papers/')) and
            not name.lower().endswith(('.pdf', '.png', '.jpg', '.zip')),
            'duplicate_or_private046_public_input')
        public[name] = safe.pinned_file(git, commit, name, row['sha256'])
        safe.require(safe.read_regular(bundle / 'public' / name) == public[name],
                     '046_public_snapshot_differs_from_git_object')
    safe.require(REQUIRED_CODE <= set(public), '046_runtime_dependency_pins_missing')
    for name, expected in ((BASELINE_REPORT, RETURN045_REPORT_SHA256),
                           (BASELINE_RECEIPT, RETURN045_RECEIPT_SHA256)):
        safe.require(safe.pinned_file(git, RETURN_COMMIT, name, expected) == public[name],
                     '046_baseline_differs_from_accepted045_git_return')
    validate_baseline(public)
    for name in ('checkpoint046_workflow.py', 'stage_source_packet038.py'):
        safe.require(safe.read_regular(Path(__file__).absolute().with_name(name)) ==
            public['scripts/' + name], '046_executing_wrapper_differs_from_release')
    safe.require(safe.read_regular(bundle / 'launch046_home.py') ==
        public['scripts/launch046_home.py'], '046_launcher_differs_from_release')
    private = {}
    for row in manifest['private_files']:
        safe.require(type(row) is dict and set(row) == {'path', 'sha256'},
                     'invalid046_private_input_row')
        name = safe.safe_name(row['path'])
        safe.require(name.startswith('private/') and name.removeprefix('private/') not in private and
            type(row['sha256']) is str and re.fullmatch('[0-9a-f]{64}', row['sha256']),
            'invalid046_private_input_path')
        raw = safe.read_regular(bundle / name)
        safe.require(safe.sha(raw) == row['sha256'], '046_private_packet_hash_mismatch')
        private[name.removeprefix('private/')] = raw
    safe.require(sum(map(len, public.values())) + sum(map(len, private.values())) <=
                 safe.MAX_TOTAL, '046_snapshot_byte_limit')
    verify_snapshot(bundle, public, private)
    return public, private


def verify_snapshot(bundle, public, private):
    for prefix, files in (('public', public), ('private', private)):
        folder = bundle / prefix
        safe.verify_existing_tree(folder, files)
        safe.require(all(safe.read_regular(folder / name) == raw for name, raw in files.items()),
                     '046_snapshot_changed_or_incomplete')


def atomic_new(path, raw):
    """Publish a complete file without replacing any existing bytes."""
    safe.directory(path.parent, create=True)
    if os.path.lexists(path):
        safe.require(safe.read_regular(path) == raw, '046_saved_state_differs_preserved')
        return
    fd, name = tempfile.mkstemp(prefix='.atomic046_', dir=path.parent)
    temp = Path(name)
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temp, path, follow_symlinks=False)
        except FileExistsError:
            safe.require(safe.read_regular(path) == raw, '046_concurrent_state_differs_preserved')
        temp.unlink()
        parent_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(parent_fd)
        finally:
            os.close(parent_fd)
    finally:
        if os.path.lexists(temp):
            temp.unlink()
    safe.require(safe.read_regular(path) == raw, '046_atomic_state_verification_failed')


def source_pins(public):
    return [{'path': name, 'sha256': safe.sha(public[name])} for name in sorted(PROFILE_SOURCES)]


def baseline_pins(public):
    return [{'path': name, 'sha256': safe.sha(public[name])} for name in sorted(BASELINE_FILES)]


def validate_baseline(public):
    safe.require(safe.sha(public[BASELINE_REPORT]) == RETURN045_REPORT_SHA256 and
        safe.sha(public[BASELINE_RECEIPT]) == RETURN045_RECEIPT_SHA256,
        '046_accepted045_baseline_hash_differs')
    report, receipt = (safe.parse(public[name]) for name in (BASELINE_REPORT, BASELINE_RECEIPT))
    child = report.get('diagnostic_report')
    safe.require(receipt.get('report_sha256') == RETURN045_REPORT_SHA256 and
        receipt.get('report_path') == BASELINE_REPORT and
        receipt.get('diagnostic_source_pins') == report.get('source_pins') and
        report.get('diagnostic_launches_observed') == 1 and
        report.get('reservation_consumed') is True and report.get('status') == 'DIAGNOSTICS_COMPLETED' and
        type(child) is dict and child.get('status') == 'COMPLETED' and
        report.get('diagnostic_report_canonical_sha256') == safe.sha(safe.canonical(child)) and
        len(child.get('test_outcomes', [])) == 23 and
        all(row.get('status') == 'PASSED' for row in child['test_outcomes']) and
        len(child.get('required_case_families', [])) == 13 and
        all(child.get('case_results', {}).get('cases', {}).get(name, {}).get('status') == 'PASSED'
            for name in child['required_case_families']) and child.get('passed') is True and
        child.get('B_comp') is None and child.get('B_mem') is None and
        report.get('target_experiment_started') is False and
        report.get('complete_work_budget_admitted') is False,
        '046_accepted045_provenance_or_scope_differs')
    for pin in report['source_pins']:
        safe.require(pin['path'] in public and safe.sha(public[pin['path']]) == pin['sha256'],
            '046_accepted045_source_identity_not_preserved')

def stage_profile_sources(folder, public):
    files = {name: public[name] for name in PROFILE_SOURCES}
    safe.verify_existing_tree(folder, files)
    for name, raw in sorted(files.items()):
        safe.write_equal_or_new(folder / name, raw, private=True)
        (folder / name).chmod(0o400)
    safe.verify_existing_tree(folder, files)
    safe.require(all(safe.read_regular(folder / name) == raw for name, raw in files.items()),
                 '046_profile_source_copy_changed')


def validate_child_report(value):
    safe.require(type(value) is dict and value.get('kind') == 'P3_CONSOLIDATED_RESOURCE_PROFILE_046_v1'
        and value.get('status') in ('COMPLETED', 'INCOMPLETE', 'FAILED_CONFORMANCE')
        and value.get('target_experiment_started') is False
        and value.get('target_execution_admitted') is False
        and value.get('native_started') is False and value.get('outcome_blind') is True
        and value.get('complete_work_budget_admitted') is False
        and value.get('full_resource_profile_started') is True
        and value.get('original043044045_remeasured') is False
        and value.get('instruction_accounting_complete') is False
        and value.get('maximal_geometry_proved') is False
        and value.get('automatic_rerun_permitted') is False,
        '046_child_report_shape_or_boundary_refused')
    safe.require(value.get('evidence_transport') == 'EXACT_SEPARATE_WORKER_REPORTS_046_v1',
                 '046_worker_transport_shape_differs')
    safe.require(len(compact_json(value)) <= CAPS['maximum_child_report_bytes'],
                 '046_normalized_child_report_oversized')
    return value


def planned_profile_rows(config):
    rows = []
    for size in config['sizes']:
        for arm in config['arms']:
            for repetition in range(config['repetitions']):
                rows.append({'case': 'complete_chain', 'size': size['name'],
                    'arm': arm, 'repetition': repetition, 'row_id': 'row_%02d' % len(rows)})
    for name in config['stress_cases']:
        for repetition in range(config['repetitions']):
            rows.append({'case': name, 'size': 'envelope', 'arm': None,
                'repetition': repetition, 'row_id': 'row_%02d' % len(rows)})
    return rows


def validate_evidence_archive(container):
    """Check all source bytes in fixed chunks, without materializing a decoded graph."""
    archive = container.get('archive')
    safe.require(type(archive) is dict and archive.get('encoding') == 'zlib6+base64' and
        type(archive.get('data')) is str and
        type(archive.get('compressed_bytes')) is int and
        0 < archive['compressed_bytes'] <= CAPS['maximum_child_report_bytes'] and
        type(archive.get('uncompressed_bytes')) is int and
        0 <= archive['uncompressed_bytes'] <= 128 * 1024 ** 2 and
        archive.get('uncompressed_limit_bytes') == 128 * 1024 ** 2 and
        container.get('encoded_bytes') == archive['uncompressed_bytes'] and
        container.get('sha256') == archive.get('uncompressed_sha256'),
        '046_evidence_archive_metadata_differs')
    try:
        raw = base64.b64decode(archive['data'], validate=True)
        safe.require(len(raw) == archive['compressed_bytes'] and
            safe.sha(raw) == archive.get('compressed_sha256'), '046_evidence_compressed_bytes_differ')
        decoder, digest = zlib.decompressobj(), hashlib.sha256()
        pending, total = raw, 0
        while pending:
            block = decoder.decompress(pending, 1024 ** 2)
            total += len(block)
            safe.require(total <= archive['uncompressed_bytes'], '046_evidence_decoded_size_exceeded')
            digest.update(block)
            pending = decoder.unconsumed_tail
        safe.require(decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail and
            total == archive['uncompressed_bytes'] and
            digest.hexdigest() == archive.get('uncompressed_sha256'),
            '046_evidence_decoded_bytes_or_stream_differ')
    except (ValueError, zlib.error) as error:
        raise safe.StageStop('046_evidence_archive_decode_refused') from error


def validate_all_evidence_archives(value):
    pending = [value]
    while pending:
        node = pending.pop()
        if type(node) is dict:
            if 'archive' in node:
                validate_evidence_archive(node)
            pending.extend(node.values())
        elif type(node) is list:
            pending.extend(node)


def validate_profile_scope(value, public):
    expected = {pin['path']: pin['sha256'] for pin in source_pins(public)}
    config = safe.parse(public['configs/P3_FULL_WORK_FIXTURES_046.json'])
    metrics = value.get('aggregate_metrics')
    safe.require(value.get('source_hashes') == expected and value.get('B_comp') is None and
        value.get('B_mem') is None and type(value.get('profiles')) is list and
        ((metrics is None and value['status'] != 'COMPLETED') or
            (type(metrics) is dict and metrics.get('scope') == '046_RESOURCE_PROFILE_INVOCATION_ONLY')) and
        value.get('limits') == config['limits'], '046_profile_sources_or_usage_differs')
    expected_limits = {'inclusive_outer_wall_seconds': CAPS['parent_wall_seconds'],
        'driver_wall_seconds': CAPS['driver_wall_seconds'],
        'row_wall_seconds': CAPS['profile_row_wall_seconds'],
        'conformance_wall_seconds': CAPS['conformance_wall_seconds'],
        'address_space_bytes': CAPS['address_space_bytes'],
        'cpu_affinity_count': CAPS['available_cpus_used'],
        'file_size_bytes': CAPS['maximum_child_file_bytes'],
        'report_bytes': CAPS['maximum_child_report_bytes'], 'automatic_remeasurement': False}
    safe.require(config['limits'] == expected_limits, '046_profile_config_and_outer_caps_differ')
    planned = planned_profile_rows(config)
    identities = {row['row_id']: row for row in planned}
    rows = value['profiles']
    safe.require(all(type(row) is dict and type(row.get('row_id')) is str for row in rows),
                 '046_profile_row_shape_differs')
    safe.require(len(rows) <= len(planned) and len({row['row_id'] for row in rows}) == len(rows)
        and all(row['row_id'] in identities and
            safe.canonical({key: row.get(key) for key in identities[row['row_id']]}) ==
                safe.canonical(identities[row['row_id']]) and
            row.get('status') in ('NOT_STARTED', 'RESERVED', 'COMPLETED', 'INCOMPLETE', 'FAILED_CONFORMANCE')
            for row in rows), '046_profile_row_identity_or_status_differs')
    safe.require([row['row_id'] for row in rows] == sorted(row['row_id'] for row in rows),
                 '046_profile_row_order_differs')
    validate_all_evidence_archives(value)
    for row in rows:
        if row['status'] == 'COMPLETED':
            safe.require(type(row.get('full_worker_report')) is dict,
                '046_completed_row_missing_worker_descriptor')
    if 'planned_rows' in value:
        safe.require(value['planned_rows'] == planned, '046_profile_plan_differs')
    worker = value.get('conformance')
    safe.require(worker is None or type(worker) is dict, '046_conformance_shape_differs')
    conformance = worker.get('summary') if type(worker) is dict else None
    if worker is not None:
        safe.require(worker.get('row_id') == 'conformance' and
            worker.get('source_hashes') in (None, expected) and
            worker.get('status') in ('COMPLETED', 'INCOMPLETE', 'FAILED_CONFORMANCE') and
            (conformance is None or type(conformance) is dict), '046_conformance_worker_shape_differs')
    if type(conformance) is dict and 'test_outcomes' in conformance:
        outcomes = conformance['test_outcomes']
        safe.require(type(outcomes) is list and all(type(row) is dict and
            type(row.get('name')) is str and row.get('status') in
            ('PASSED', 'FAILED', 'ERROR', 'SKIPPED', 'EXPECTED_FAILURE', 'UNEXPECTED_SUCCESS', 'INTERRUPTED')
            for row in outcomes) and len({row['name'] for row in outcomes}) == len(outcomes),
            '046_conformance_outcome_shape_differs')
    if value['status'] == 'COMPLETED':
        safe.require(type(worker) is dict and worker.get('status') == 'COMPLETED' and
            worker.get('source_hashes') == expected and
            type(conformance) is dict and conformance.get('passed') is True and
            type(conformance.get('tests_run')) is int and conformance['tests_run'] > 0 and
            type(conformance.get('test_outcomes')) is list and
            len(conformance['test_outcomes']) == conformance['tests_run'] and
            all(row['status'] == 'PASSED' for row in conformance['test_outcomes']) and
            type(conformance.get('case_results')) is dict and
            len(rows) == len(planned) and all(row['status'] == 'COMPLETED' for row in rows) and
            value.get('complete_required_paths_measured') is True and value.get('interruption') is None,
            '046_completed_claim_without_all_required_work')


def worker_pins(files):
    return [{'filename': name, 'sha256': safe.sha(raw), 'bytes': len(raw)}
            for name, raw in sorted(files.items())]


def descriptor_names(value):
    pins = value.get('worker_report_pins')
    safe.require(type(pins) is list and len(pins) <= len(WORKER_NAMES) and
        all(type(pin) is dict and set(pin) == {'filename', 'sha256', 'bytes'} and
            pin.get('filename') in WORKER_NAMES and type(pin.get('bytes')) is int and
            0 <= pin['bytes'] <= safe.MAX_FILE and type(pin.get('sha256')) is str and
            re.fullmatch('[0-9a-f]{64}', pin['sha256']) for pin in pins) and
        len({pin['filename'] for pin in pins}) == len(pins), '046_worker_pin_shape_differs')
    return [pin['filename'] for pin in pins]


def read_worker_files(folder, value=None):
    names = sorted(WORKER_NAMES) if value is None else descriptor_names(value)
    files = {}
    for name in names:
        path = folder / name
        if os.path.lexists(path):
            files[name] = safe.read_regular(path)
    return files


def save_worker_files(folder, files):
    safe.require(set(files) <= WORKER_NAMES, '046_worker_filename_refused')
    for name, raw in sorted(files.items()):
        atomic_new(folder / name, raw)


def validate_worker_reports(child, files, public):
    """Preserve every fixed-name file; errors block acceptance, never erase evidence."""
    failures = []
    safe.require(set(files) <= WORKER_NAMES and all(type(raw) is bytes and
        len(raw) <= safe.MAX_FILE for raw in files.values()), '046_worker_file_boundary_refused')
    rows = ([] if child is None else child['profiles'])
    entries = {row['row_id'] + '.json': row for row in rows}
    if child is not None and child.get('conformance') is not None:
        entries['CONFORMANCE.json'] = child['conformance']
    expected_sources = {pin['path']: pin['sha256'] for pin in source_pins(public)}
    observed_pins = {pin['filename']: pin for pin in worker_pins(files)}
    referenced = set()
    for name, entry in entries.items():
        descriptor = entry.get('full_worker_report')
        if descriptor is None:
            if entry.get('status') == 'COMPLETED':
                failures.append({'filename': name, 'reason': 'MISSING_WORKER_DESCRIPTOR'})
            continue
        referenced.add(name)
        if descriptor != observed_pins.get(name):
            failures.append({'filename': name, 'reason': 'WORKER_DESCRIPTOR_OR_BYTES_DIFFER'})
    for name, raw in sorted(files.items()):
        if name not in referenced:
            failures.append({'filename': name, 'reason': 'UNINDEXED_RECOVERED_WORKER_EVIDENCE'})
        try:
            safe.require(len(raw) <= CAPS['maximum_child_report_bytes'], 'worker_report_size_limit')
            value = safe.parse(raw)
            row_id = 'conformance' if name == 'CONFORMANCE.json' else name.removesuffix('.json')
            safe.require(type(value) is dict and value.get('row_id') == row_id and
                value.get('worker_kind') == 'P3_FULL_WORK_ROW_046_v1' and
                value.get('source_hashes') == expected_sources and
                value.get('status') in ('COMPLETED', 'INCOMPLETE', 'FAILED_CONFORMANCE'),
                'worker_source_identity_or_status_differs')
            validate_all_evidence_archives(value)
            entry = entries.get(name)
            if entry is not None and entry.get('status') == 'COMPLETED':
                safe.require(value['status'] == 'COMPLETED', 'completed_index_has_incomplete_worker')
                summary = value.get('summary')
                if name == 'CONFORMANCE.json':
                    safe.require(summary == entry.get('summary'), 'conformance_summary_differs')
                else:
                    required = ('complete_evidence_serialization' if entry['case'] == 'complete_chain'
                                else 'overlap_serialization')
                    safe.require(type(summary) is dict and type(summary.get(required)) is dict and
                        type(summary[required].get('archive')) is dict,
                        'completed_worker_missing_complete_evidence_archive')
        except (safe.StageStop, ValueError, TypeError, KeyError) as error:
            failures.append({'filename': name, 'reason': str(error) if type(error) is safe.StageStop
                else type(error).__name__})
    return failures

def read_child_report(output, public=None):
    path = output / 'REPORT.json'
    if not os.path.lexists(path):
        return None, 'MISSING_CHILD_REPORT'
    try:
        raw = safe.read_regular(path)
        safe.require(len(raw) <= CAPS['maximum_child_report_bytes'], '046_child_report_oversized')
        value = validate_child_report(safe.parse(raw))
        if public is not None:
            validate_profile_scope(value, public)
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
        safe.require(len(raw) <= CAPS['maximum_child_report_bytes'], '046_child_report_oversized')
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
               '--root', str(source), '--output', str(output)]
    available = sorted(os.sched_getaffinity(0))
    safe.require(bool(available), '046_cpu_affinity_unavailable')
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
        'process_group_kill_attempted': False, 'process_group_cleanup_kill_attempted': False,
        'parent_death_signal_requested': True}
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
                while True:
                    remaining = CAPS['parent_wall_seconds'] - (time.monotonic() - started)
                    if remaining <= 0:
                        raise subprocess.TimeoutExpired(command, CAPS['parent_wall_seconds'])
                    try:
                        child.wait(timeout=min(60, remaining))
                        break
                    except subprocess.TimeoutExpired:
                        if time.monotonic() - started >= CAPS['parent_wall_seconds']:
                            raise
                        print('WORKFLOW: resource profile still running; elapsed ' +
                              str(int(time.monotonic() - started)) + ' seconds. ' +
                              'Completed rows are saved incrementally; the invocation will not restart.',
                              flush=True)
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
            outcome['process_group_kill_attempted'] = True
            outcome['process_group_cleanup_kill_attempted'] = True
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


def execution_report(release, public, outcome, child_report, report_failure, rejected_child=None, worker_files=None):
    worker_files = {} if worker_files is None else worker_files
    worker_failures = validate_worker_reports(child_report, worker_files, public)
    complete = (outcome.get('termination') == 'EXITED' and outcome.get('exit_code') == 0
                and child_report is not None and child_report.get('status') == 'COMPLETED' and not worker_failures)
    return {'kind': 'P3_RESOURCE_PROFILE_EXECUTION_046_v1',
        'report_encoding': 'SORTED_COMPACT_ASCII_JSON_046_v1',
        'release_manifest_sha256': release['manifest_sha256'],
        'content_commit': release['content_commit'],
        'status': 'PROFILE_COMPLETED' if complete else 'PROFILE_INCOMPLETE',
        'profile_report': child_report,
        'profile_report_canonical_sha256': safe.sha(compact_json(child_report))
            if child_report is not None else None,
        'child_report_failure_class': report_failure,
        'rejected_child_report': rejected_child,
        'worker_report_pins': worker_pins(worker_files),
        'worker_report_validation_failures': worker_failures,
        'source_pins': source_pins(public), 'caps': CAPS,
        'baseline_pins': baseline_pins(public), 'profile_scope': SCOPE,
        'baseline_return_commit': RETURN_COMMIT,
        'baseline_report_path': BASELINE_REPORT,
        'execution': outcome, 'reservation_consumed': True,
        'maximum_profile_launches_for_release': 1,
        'profile_launches_observed': (1 if outcome.get('child_start_observed') is True
            else 0 if outcome.get('child_start_observed') is False else None),
        'outcome_blind': True, 'development_resource_profile_only': True,
        'B_comp': None, 'B_mem': None,
        'instruction_accounting_complete': False, 'maximal_geometry_proved': False,
        'native_starts': 0, 'model_turns_sent': 0, 'target_experiment_started': False,
        'target_execution_admitted': False, 'complete_work_budget_admitted': False,
        'automatic_rerun_permitted': False, 'profile_source_and_working_directory_separation': True,
        'operating_system_isolation_asserted': False, 'private_content_published': False}


def validate_saved_report(raw, release, public, worker_files=None):
    worker_files = {} if worker_files is None else worker_files
    value = safe.parse(raw)
    safe.require(type(value) is dict and value.get('kind') ==
        'P3_RESOURCE_PROFILE_EXECUTION_046_v1'
        and value.get('report_encoding') == 'SORTED_COMPACT_ASCII_JSON_046_v1'
        and value.get('release_manifest_sha256') == release['manifest_sha256']
        and value.get('content_commit') == release['content_commit']
        and type(value.get('execution')) is dict
        and value.get('source_pins') == source_pins(public) and value.get('caps') == CAPS
        and value.get('baseline_pins') == baseline_pins(public)
        and value.get('profile_scope') == SCOPE
        and value.get('baseline_return_commit') == RETURN_COMMIT
        and value.get('status') in ('PROFILE_COMPLETED', 'PROFILE_INCOMPLETE')
        and value.get('native_starts') == 0 and value.get('model_turns_sent') == 0
        and value.get('target_experiment_started') is False
        and value.get('target_execution_admitted') is False
        and value.get('complete_work_budget_admitted') is False
        and value.get('B_comp') is None and value.get('B_mem') is None
        and value.get('instruction_accounting_complete') is False
        and value.get('maximal_geometry_proved') is False
        and value.get('automatic_rerun_permitted') is False
        and value.get('reservation_consumed') is True
        and value.get('maximum_profile_launches_for_release') == 1
        and value.get('outcome_blind') is True and execution_bytes(value) == raw,
        '046_saved_report_shape_or_release_differs')
    child = value.get('profile_report')
    descriptor_names(value)
    safe.require(value['worker_report_pins'] == worker_pins(worker_files), '046_saved_worker_pins_differ')
    worker_failures = validate_worker_reports(child, worker_files, public)
    safe.require(value.get('worker_report_validation_failures') == worker_failures,
                 '046_saved_worker_validation_differs')
    observed_start = value['execution'].get('child_start_observed')
    safe.require(observed_start is None or type(observed_start) is bool,
                 '046_observed_start_type_differs')
    safe.require(value.get('profile_launches_observed') ==
        (None if observed_start is None else int(observed_start)),
        '046_observed_launch_accounting_differs')
    if child is not None:
        validate_child_report(child)
        validate_profile_scope(child, public)
        safe.require(value.get('profile_report_canonical_sha256') == safe.sha(compact_json(child)),
                     '046_saved_child_report_hash_differs')
    complete = (value['execution'].get('termination') == 'EXITED' and
        value['execution'].get('exit_code') == 0 and child is not None and child['status'] == 'COMPLETED'
        and not worker_failures)
    safe.require(value['status'] == ('PROFILE_COMPLETED' if complete else 'PROFILE_INCOMPLETE'),
                 '046_wrapper_status_differs_from_validated_execution')
    rejected = value.get('rejected_child_report')
    if rejected is not None:
        safe.require(type(rejected) is dict and child is None and value.get('child_report_failure_class') and
            rejected.get('encoding') == 'base64' and rejected.get('interpretation') ==
            'REJECTED_CHILD_OUTPUT_NOT_ACCEPTED_MEASUREMENTS', '046_rejected_child_evidence_shape_differs')
        decoded = base64.b64decode(rejected['content'], validate=True)
        safe.require(len(decoded) == rejected['bytes'] and safe.sha(decoded) == rejected['sha256'],
                     '046_rejected_child_evidence_bytes_differ')
    return value


def obtain_saved_report(folder, release, public, *, profile_runner=run_profile_child):
    saved = folder / 'SAVED_REPORT.json'
    if os.path.lexists(saved):
        raw = safe.read_regular(saved)
        return validate_saved_report(raw, release, public,
            read_worker_files(folder / 'SAVED_WORKER_REPORTS', safe.parse(raw)))
    reservation_path = folder / 'EXECUTION_RESERVED.json'
    reservation = {'kind': 'P3_DEVELOPMENT_RESOURCE_PROFILE_RESERVATION_046_v1',
        'release_manifest_sha256': release['manifest_sha256'],
        'content_commit': release['content_commit'], 'source_pins': source_pins(public),
        'baseline_pins': baseline_pins(public), 'profile_scope': SCOPE,
        'caps': CAPS, 'maximum_profile_launches': 1, 'automatic_rerun_permitted': False}
    source, output = folder / 'execution_source', folder / 'profile_output'
    if os.path.lexists(reservation_path):
        safe.require(safe.read_regular(reservation_path) == safe.canonical(reservation),
                     '046_existing_reservation_differs_preserved')
        child, failure = read_child_report(output, public)
        outcome = {'child_start_observed': None, 'exit_code': None, 'wall_seconds': None,
            'termination': 'RESERVATION_FOUND_WITHOUT_SAVED_RESULT',
            'automatic_relaunch_refused': True}
    else:
        validate_baseline(public)
        stage_profile_sources(source, public)
        safe.directory(output, create=True)
        safe.require(not any(output.iterdir()), '046_unreserved_profile_output_preserved')
        atomic_new(reservation_path, safe.canonical(reservation))
        try:
            outcome = profile_runner(source, output)
            safe.require(type(outcome) is dict, '046_child_outcome_shape_refused')
        except Exception as error:
            outcome = {'child_start_observed': None, 'exit_code': None, 'wall_seconds': None,
                'termination': 'WRAPPER_INTERRUPTED_AFTER_RESERVATION',
                'failure_class': type(error).__name__, 'automatic_relaunch_refused': True}
        child, failure = read_child_report(output, public)
        try:
            expected_sources = {name: public[name] for name in PROFILE_SOURCES}
            safe.verify_existing_tree(source, expected_sources)
            safe.require(all(safe.read_regular(source / name) == raw
                for name, raw in expected_sources.items()), '046_profile_sources_changed')
        except (safe.StageStop, OSError) as error:
            outcome = dict(outcome, termination='PROFILE_SOURCE_CHANGED',
                           source_verification_failure_class=type(error).__name__)
    workers = read_worker_files(output)
    save_worker_files(folder / 'SAVED_WORKER_REPORTS', workers)
    value = execution_report(release, public, outcome, child, failure,
                             rejected_child_evidence(output, failure), workers)
    atomic_new(saved, execution_bytes(value))
    return validate_saved_report(safe.read_regular(saved), release, public, workers)


def return_files(release, result, public, private, worker_files=None):
    worker_files = {} if worker_files is None else worker_files
    folder = 'artifacts/CHECKPOINT_046_RETURN/' + release['manifest_sha256']
    report_path = folder + '/REPORT.json'
    report_raw = execution_bytes(result)
    receipt = {'kind': 'P3_CHECKPOINT_046_RESOURCE_PROFILE_RECEIPT_v1',
        'repository': REPOSITORY, 'content_commit': release['content_commit'],
        'release_manifest_path': MANIFEST, 'release_manifest_sha256': release['manifest_sha256'],
        'accepted_return_commit': RETURN_COMMIT,
        'accepted045_report_sha256': RETURN045_REPORT_SHA256,
        'accepted045_receipt_sha256': RETURN045_RECEIPT_SHA256,
        'accepted045_report_path': BASELINE_REPORT, 'accepted045_receipt_path': BASELINE_RECEIPT,
        'profile_scope': SCOPE, 'original043044045_remeasured': False,
        'runner_path': VERIFIER, 'runner_sha256': safe.sha(public[VERIFIER]),
        'profile_source_pins': source_pins(public), 'report_path': report_path,
        'report_sha256': safe.sha(report_raw), 'full_profile_and_execution_result_published': True,
        'report_encoding': 'SORTED_COMPACT_ASCII_JSON_046_v1',
        'worker_report_pins': [{'path': folder + '/' + pin['filename'], **pin}
            for pin in worker_pins(worker_files)],
        'worker_report_validation_failures': result['worker_report_validation_failures'],
        'maximum_return_files': 51, 'return_file_count': 2 + len(worker_files),
        'profile_status': result['status'], 'public_snapshot_files_verified': len(public),
        'private_packet_files_verified': len(private), 'private_content_published': False,
        'outcome_blind_resource_profile_only': True,
        'full_resource_profile_started': (None if result['profile_launches_observed'] is None
            else result['profile_launches_observed'] == 1),
        'B_comp': None, 'B_mem': None, 'instruction_accounting_complete': False,
        'maximal_geometry_proved': False,
        'new_native_allowance': 0, 'native_starts': 0, 'model_turns_sent': 0,
        'cumulative_native_starts': 18, 'cumulative_model_turns_sent': 14,
        'reviewer_or_review_controller_started': False, 'target_experiment_started': False,
        'target_execution_admitted': False, 'complete_work_budget_admitted': False,
        'automatic_profile_rerun_permitted': False,
        'maximum_profile_launches_for_release': 1,
        'profile_launches_observed': result['profile_launches_observed'],
        'historical040_rerun': False, 'historical039_rerun': False,
        'timestamp_omitted_for_publication_idempotence': True}
    safe.require(result['worker_report_pins'] == worker_pins(worker_files), '046_return_worker_pins_differ')
    return {report_path: report_raw, folder + '/RECEIPT.json': safe.canonical(receipt),
            **{folder + '/' + name: raw for name, raw in worker_files.items()}}

def sync_repository(git, fetched, expected):
    current = git.call('rev-parse', 'HEAD').decode().strip()
    if current == fetched:
        return
    if git.ancestor(current, fetched):
        safe.require(not git.call('diff', '--cached', '--name-only', '-z').strip(),
                     'staged046_receipt_preserved_before_remote_fast_forward')
        git.call('merge', '--ff-only', fetched)
        return
    safe.require(git.ancestor(fetched, current), 'branches_diverged_preserved')
    safe.require(git.call('rev-list', fetched + '..' + current).decode().split() == [current]
        and git.call('show', '-s', '--format=%P', current).decode().split() == [fetched],
        'unrelated_unpublished_commits_preserved')
    changed = safe.git_names(git.call('diff', '--name-only', '-z', fetched, current))
    safe.require(changed == set(expected) and all(
        git.call('show', current + ':' + name) == raw for name, raw in expected.items()),
        'unpublished_commit_is_not_exact046_receipt')


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
    safe.require(staged <= set(expected), 'unrelated046_index_change_preserved')
    safe.require(all(git.call('show', ':' + name) == raw for name, raw in expected.items()),
                 '046_staged_receipt_bytes_differ')
    if staged:
        safe.require(staged == set(expected), '046_partial_receipt_commit_refused')
        git.call('commit', '-m', COMMIT_MESSAGE)
    current = git.call('rev-parse', 'HEAD').decode().strip()
    if current != parent:
        safe.require(git.call('show', '-s', '--format=%P', current).decode().split() == [parent]
            and safe.git_names(git.call('diff', '--name-only', '-z', parent, current)) == set(expected),
            '046_commit_scope_differs')
    safe.require(all(git.call('show', current + ':' + name) == raw for name, raw in expected.items()),
                 '046_committed_receipt_bytes_differ')
    if current != fetched:
        git.call('push', 'origin', current + ':refs/heads/main')
    remote = git.call('ls-remote', '--exit-code', 'origin', 'refs/heads/main').decode().split()
    safe.require(remote == [current, 'refs/heads/main'], '046_remote_publication_not_verified')
    return current


def workflow(lab, bundle, *, git_runner=None, profile_runner=run_profile_child, emit=print):
    lab, bundle = safe.directory(lab), safe.directory(bundle)
    safe.require(bundle.is_relative_to(lab / 'delivery'), '046_bundle_must_be_inside_ignored_delivery')
    release = release_metadata(bundle)
    git = Git(lab, runner=git_runner)
    safe.require(not git.call('ls-files', '-z', '--', bundle.relative_to(lab).as_posix()),
                 '046_private_bundle_is_tracked')
    return_folder = 'artifacts/CHECKPOINT_046_RETURN/' + release['manifest_sha256']
    receipt_path, report_path = return_folder + '/RECEIPT.json', return_folder + '/REPORT.json'
    prior = {name: safe.read_regular(lab / name) for name in (report_path, receipt_path)
             if os.path.lexists(lab / name)}
    if report_path in prior:
        local_value = safe.parse(prior[report_path])
        for name in descriptor_names(local_value):
            path = return_folder + '/' + name
            if os.path.lexists(lab / path):
                prior[path] = safe.read_regular(lab / path)
    check_repository(git, prior)
    relative_files = [path.relative_to(lab).as_posix() for path in bundle.rglob('*') if path.is_file()]
    ignored(git, relative_files)
    folder = safe.directory(lab / WORKFLOW / release['manifest_sha256'], create=True)
    ignored(git, [str((folder / 'WORKFLOW.lock').relative_to(lab))])
    lock = os.open(folder / 'WORKFLOW.lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        info = os.fstat(lock)
        safe.require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, '046_lock_shape_refused')
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise safe.StageStop('046_workflow_already_active')
        git.call('fetch', '--no-tags', 'origin', 'main')
        fetched = git.call('rev-parse', 'FETCH_HEAD').decode().strip()
        safe.require(git.ancestor(RETURN_COMMIT, release['content_commit']) and
            git.ancestor(release['content_commit'], fetched), '046_release_not_in_return_and_remote_history')
        public, private = load_snapshot(git, bundle, release)
        # Reject unrelated unpublished work before reserving the sole resource profile launch.
        sync_repository(git, fetched, prior)
        remote_names = safe.git_names(git.call('ls-tree', '--name-only', '-r', '-z', fetched,
                                             '--', return_folder))
        if remote_names:
            safe.require({report_path, receipt_path} <= remote_names, '046_partial_remote_return_preserved')
            remote_report = git.call('show', fetched + ':' + report_path)
            candidate = safe.parse(remote_report)
            descriptor_names(candidate)
            workers = {pin['filename']: safe.pinned_file(git, fetched,
                return_folder + '/' + pin['filename'], pin['sha256'])
                for pin in candidate['worker_report_pins']}
            result = validate_saved_report(remote_report, release, public, workers)
            expected = return_files(release, result, public, private, workers)
            safe.require(remote_names == set(expected), '046_remote_return_path_set_differs')
            safe.require(all(git.call('show', fetched + ':' + name) == raw
                             for name, raw in expected.items()), '046_remote_report_or_receipt_differs')
            save_worker_files(folder / 'SAVED_WORKER_REPORTS', workers)
            atomic_new(folder / 'SAVED_REPORT.json', remote_report)
            emit('WORKFLOW: reusing the exact published046 profile; no profile is restarted.')
        else:
            if {report_path, receipt_path} <= set(prior):
                workers = {name.removeprefix(return_folder + '/'): raw for name, raw in prior.items()
                    if name not in (report_path, receipt_path)}
                prior_result = validate_saved_report(prior[report_path], release, public, workers)
                safe.require(return_files(release, prior_result, public, private, workers) == prior,
                             '046_prior_local_return_differs_preserved')
                save_worker_files(folder / 'SAVED_WORKER_REPORTS', workers)
                atomic_new(folder / 'SAVED_REPORT.json', prior[report_path])
            emit('WORKFLOW: running the single046 resource profile reservation; retries reuse the first saved evidence.')
            result = obtain_saved_report(folder, release, public, profile_runner=profile_runner)
            workers = read_worker_files(folder / 'SAVED_WORKER_REPORTS', result)
            expected = return_files(release, result, public, private, workers)
        atomic_new(folder / 'SAVED_RECEIPT.json', expected[receipt_path])
        verify_snapshot(bundle, public, private)
        safe.require(all(expected.get(name) == raw for name, raw in prior.items()),
                     '046_prior_report_or_receipt_differs_preserved')
        check_repository(git, expected)
        safe.require(git.ancestor(release['content_commit'], 'HEAD'), '046_release_not_in_local_history')
        ignored(git, relative_files + [path.relative_to(lab).as_posix()
            for path in folder.rglob('*') if path.is_file()])
        commit = publish(git, expected, fetched)
        return {'status': '046_DEVELOPMENT_PROFILE_REPORT_AND_RECEIPT_PUBLISHED', 'commit': commit,
            'receipt_path': receipt_path, 'report_path': report_path, 'profile_status': result['status'],
            'worker_report_paths': sorted(return_folder + '/' + name for name in workers),
            'profile_reason': ((result['profile_report'].get('interruption')
                if result['profile_report'] is not None else None) or
                result['child_report_failure_class'] or
                ('WORKER_EVIDENCE_VALIDATION_FAILED' if result['worker_report_validation_failures'] else None) or
                result['execution'].get('termination')),
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
    print('Development046 profile: ' + result['profile_status'])
    if result['profile_status'] != 'PROFILE_COMPLETED':
        print('Resource profiling is incomplete; its full available result was successfully published. '
              'Reason: ' + str(result['profile_reason']) + '. Repeating this command does not remeasure any row.')
    print('All043/044 measurements and045 diagnostics are preserved; new046 invocation usage is reported separately.')
    print('No reviewer, model or target experiment was started. Future experiment admission is not asserted.')
    # Publication success and profile completeness are different outcomes.
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
