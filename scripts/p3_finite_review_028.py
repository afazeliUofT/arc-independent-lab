#!/usr/bin/env python3
"""One exactly approved synthetic admission and conditional fresh scientific review.

The new 10-start/7-sent-turn cumulative ceiling requires exact028 approval. Every
actual prior receipt is preserved and reverified. A completed receipt is reused;
partial or incompatible work stops. No automatic retry or credential inspection.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SCOPE_PATH = 'configs/P3_FINITE_REVIEW_SCOPE_028.json'
SCOPE_SHA256 = '69d8413411518a4a33998fc0a271049b125520d7854341cc5584fa9dea4056c6'
SOURCE_PINS = {
    "scripts/p3_finite_review_027.py": "bfb8ef28f4176e51c2466892fc8f3b559486337534e706bb566f434c1564884a",
    "scripts/p3_review_interface_028.py": "ef41a59491f67252674079b18fa21e46257bdaf5cb2cabf76d9ba376ce6e2d1a",
    "scripts/p3_review_protocol_028.py": "d41ecb40a6d63179657e5e04df2491b4bf431a5b28229210b96e640fba49b224",
    "scripts/p3_reviewer_session_028.py": "ddaac65b673ccf17095b7a8a4c5f1d7908a497fbef865dee5ed5bd77f9149bea",
    "configs/P3_SYNTHETIC_PROMPT_028.txt": "c930a6accbe8d704cf3467319a39cf81b189e0c18425108baed0023d01873c1a",
    "artifacts/P3_INTERFACE_CONTRACT_SOURCE/20260910_028/MANIFEST.json": "e791f83e1966c29dcd04683ae403e3229cae6ba9f0fb6845fc3dd601f9e0b16d"
}

RUN_NAME = 'P3_FINITE_REVIEW_028'
REPORT_KIND = 'P3_FINITE_REVIEW_028_v1'
SESSION_KIND = 'P3_FINITE_REVIEWER_SESSION_028_v1'
REPORT027_PATH = 'artifacts/P3_SCIENTIFIC_BROKER_STOP_OBSERVATIONS/20260910_028/REPORT.json'
REPORT027_SHA256 = '6460fffe52e02b5388d871c328d3d7d72885d7222b086d664786b4a822084769'
SESSION027_SHA256 = {'synthetic': '0666046ba3a1bae069fdd134cc9d7848820fa0e4a293ce71107ce29d628e3ff7',
    'science': 'c7e13df8e1829a700293641da8fcce7c4f134ad08e5b14eed322ea29d55abbbb'}
AUTH027_PATH = 'state/escalations/2026-09-10_FINITE_REVIEW_027_APPROVED.md'
AUTH027_SHA256 = 'a3c7990fafb5abace91929e46eecca6fb40de76e80248fa5865c0d0d2ab30a84'
OLD_CONTROLLER_SHA256 = 'bfb8ef28f4176e51c2466892fc8f3b559486337534e706bb566f434c1564884a'
BINDING = {'model': 'gpt-5.6-sol', 'id': 'gpt-5.6-sol', 'effort': 'max'}
TERMINAL = ('REVIEWER_OUTPUT_PRESERVED', 'STOPPED_WITHOUT_REVIEWER_VERDICT',
            'STOPPED_WITHOUT_COMPLETED_REVIEW', 'INTERRUPTED_PARTIAL_PRESERVED')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value, indent=2, ensure_ascii=True, allow_nan=False) + '\n').encode()


def _prior_controller():
    path = ROOT / 'scripts/p3_finite_review_027.py'
    cursor = Path(path.anchor)
    for part in path.parts[1:]:
        cursor /= part
        if cursor.is_symlink():
            raise RuntimeError('Symlink in historical controller path')
    info = path.stat()
    if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > 16 * 1024 * 1024 or
            sha(path.read_bytes()) != OLD_CONTROLLER_SHA256):
        raise RuntimeError('Historical027 controller changed')
    name = 'p3_finite_review_027'
    if name in sys.modules:
        value = sys.modules[name]
        if Path(value.__file__).resolve() != path:
            raise RuntimeError('Historical controller origin differs')
        return value
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


previous = _prior_controller()
old = previous.old
Stop = old.Stop
require = old.require
bounded = old.bounded
plain = old.plain
module = old.module
exclusive_json = old.exclusive_json
new_directory = old.new_directory
synthetic_packet = old.synthetic_packet
host_checks = old.host_checks
PROMPTS = {**old.PROMPTS, 'synthetic': 'configs/P3_SYNTHETIC_PROMPT_028.txt'}


def load_bundle():
    scope027, prior, inherited = previous.load_bundle()
    raw = bounded(ROOT / SCOPE_PATH)
    require(sha(raw) == SCOPE_SHA256 and len(SOURCE_PINS) >= 3,
            'Unfinished028 scope or dependency pins')
    for path, digest in SOURCE_PINS.items():
        require(sha(bounded(ROOT / path, 16 * 1024 * 1024)) == digest,
                '028 dependency changed')
    scope = json.loads(raw)
    require(scope.get('scope_id') == 'P3_FINITE_REVIEW_SCOPE_028' and
            scope.get('approval_id') == 'APPROVE_P3_FINITE_REVIEW_028_CORRECTION' and
            scope.get('report_directory') == 'delivery/' + RUN_NAME,
            '028 scope identity differs')
    # All host/model/time/call controls remain fixed. Only the declared tool-interface
    # correction, synthetic challenge and cumulative reservation change.
    fixed = ('canonical_home', 'canonical_project', 'runtime_sha256', 'bwrap_sha256',
        'accepted_metadata_path', 'accepted_metadata_sha256', 'prior_native_scope_path',
        'prior_native_scope_sha256', 'synthetic_seconds_including_cleanup',
        'scientific_seconds_including_cleanup', 'cleanup_seconds_per_process',
        'maximum_native_processes', 'maximum_model_turns', 'maximum_synthetic_broker_calls',
        'maximum_scientific_broker_calls', 'maximum_native_file_bytes',
        'maximum_native_runtime_tree_bytes', 'maximum_synthetic_native_cpu_seconds',
        'maximum_scientific_native_cpu_seconds', 'maximum_run_attempts_per_invocation',
        'model_policy', 'authorized_native_effects', 'private_packet_directory', 'private_packet_manifest_sha256',
        'maximum_synthetic_stdout_bytes', 'maximum_scientific_stdout_bytes',
        'maximum_stderr_bytes_per_process', 'maximum_protocol_frame_bytes',
        'maximum_outbound_queue_bytes', 'maximum_early_frames', 'maximum_early_frame_bytes',
        'parent_request_timeout_seconds', 'maximum_catalog_pages', 'maximum_catalog_entries',
        'native_cpu_hard_limit_grace_seconds')
    require(all(scope.get(k) == scope027[k] and type(scope.get(k)) is type(scope027[k])
                for k in fixed), '028 changed the inherited operational controls')
    expected = {'native_starts_observed': 8, 'explicit_model_turns_observed': 5,
        'additional_native_processes_maximum': 2, 'additional_explicit_model_turns_maximum': 2,
        'cumulative_native_starts_maximum': 10, 'cumulative_explicit_model_turns_maximum': 7,
        'no_automatic_retry': True, 'count_sent_turn_even_without_reviewer_output': True}
    counts = scope.get('prior_attempt_accounting', {})
    require(all(counts.get(k) == v and type(counts.get(k)) is type(v) for k, v in expected.items()),
            '028 cumulative accounting or no-retry restriction differs')
    policy = scope.get('interface_correction', {})
    require(type(policy.get('maximum_recoverable_input_errors_per_stage')) is int and
            policy['maximum_recoverable_input_errors_per_stage'] == 8 and
            policy.get('ninth_input_error_is_terminal') is True and
            policy.get('synthetic_prompt') == PROMPTS['synthetic'] and
            policy.get('scientific_prompt_unchanged') is True and
            policy.get('no_new_tools_or_file_authority') is True, '028 interface correction policy differs')
    require(sha(bounded(ROOT / REPORT027_PATH)) == REPORT027_SHA256 and
            sha(bounded(ROOT / AUTH027_PATH)) == AUTH027_SHA256,
            '027 input or historical027 approval archive changed')
    return scope, prior, {'scope_sha256': SCOPE_SHA256,
        'controller_sha256': sha(bounded(Path(__file__))), 'source_pins': SOURCE_PINS,
        'inherited027_pins': inherited, 'report027_sha256': REPORT027_SHA256,
        'historical027_approval_sha256': AUTH027_SHA256,
        'packet_manifest_sha256': scope['private_packet_manifest_sha256']}


def approval(scope, *, manual_launch=False):
    require(manual_launch is True, 'Explicit --run-attended-review is required')
    path = ROOT / 'state/ESCALATION.md'
    raw = bounded(path)
    text = raw.decode('utf-8')
    require('<!--' not in text and '-->' not in text, 'HTML comment ambiguity in approval')
    fence, positions = None, []
    lines = text.splitlines()
    for i, line in enumerate(lines):
        start = line.lstrip(' ')
        if len(line) - len(start) <= 3 and start.startswith(('```', '~~~')):
            char = start[0]
            length = len(start) - len(start.lstrip(char))
            if fence is None:
                fence = (char, length)
            elif char == fence[0] and length >= fence[1] and not start[length:].strip():
                fence = None
            continue
        if fence is None and line == '## ANSWER':
            positions.append(i)
    require(len(positions) == 1, 'Exactly one actual028 ANSWER is required')
    require([line for line in lines[positions[0] + 1:] if line.strip()] ==
            ['APPROVE_P3_FINITE_REVIEW_028_CORRECTION', 'scope_sha256: ' + SCOPE_SHA256],
            'Recorded answer differs from exact028 scope')
    return {'path': 'state/ESCALATION.md', 'sha256': sha(raw)}


def prior_history(pins):
    # Historical validators inspect canonical receipts; they never launch or use
    # today's approval. Actual separate SESSION files are never reconstructed.
    inherited = pins['inherited027_pins']
    earlier = previous.prior_history(inherited)
    path = previous.existing(ROOT / 'delivery' / previous.RUN_NAME, inherited)
    require(path is not None, 'Actual027 receipt is required before new reservation')
    raw = bounded(path)
    require(sha(raw) == REPORT027_SHA256 and bounded(ROOT / REPORT027_PATH) == raw,
            'Actual027 report differs from archived original')
    archived_authorization = bounded(ROOT / AUTH027_PATH)
    require(sha(archived_authorization) == AUTH027_SHA256 and
            bounded(path.parent / 'AUTHORIZATION.md') == archived_authorization,
            'Historical027 approval archive or original run authorization changed')
    value = json.loads(raw)
    stages = value.get('stages')
    require(value.get('history') == earlier and value.get('pins') == inherited and
            value.get('status') == 'STOPPED_WITHOUT_REVIEWER_VERDICT' and
            value.get('science_started') is True and value.get('reviewer_output') is None and
            type(stages) is list and [s.get('stage') for s in stages] == ['synthetic', 'science'],
            'Actual027 stage, history or provenance differs')
    measured_sessions = {}
    for mode, stage in zip(('synthetic', 'science'), stages):
        session_raw = bounded(path.parent / (mode + '_SESSION.json'))
        require(sha(session_raw) == SESSION027_SHA256[mode],
                'Actual027 SESSION missing or changed; never reconstruct it')
        observation = stage.get('observation', {})
        require(canonical(observation) == session_raw and
                all(observation.get(k) is True for k in ('client_started', 'model_turn_request_sent',
                                                         'native_process_reaped')) and
                observation.get('verdict_submitted') is False and
                stage.get('host_checks', {}).get('all_noncredential_checks_pass') is True and
                stage.get('fresh_process_and_runtime_directories') is True and
                stage.get('pi_conversation_imported') is False,
                'Actual027 separate session linkage or cleanup differs')
        measured_sessions[mode] = sha(session_raw)
    require(previous.admitted_synthetic(stages[0]) and
            stages[1]['observation'].get('broker_receipts') == [] and
            stages[1]['observation'].get('broker_protocol_reason') == 'Broker or protocol validation failed',
            'Actual027 synthetic admission or masked first scientific request differs')
    counts = value['attempt_accounting']
    expected = {'cumulative_observed_native_starts': 8, 'cumulative_observed_sent_turns': 5,
        'cumulative_native_ceiling': 8, 'cumulative_sent_turn_ceiling': 5}
    require(all(type(counts.get(k)) is int and counts[k] == v for k, v in expected.items()),
            'Actual027 observed counts or exhausted ceiling differs')
    return {'actual019_to027_history_reverified': True, 'separate027_sessions_reverified': True,
        'report027_sha256': sha(raw), 'session027_sha256': measured_sessions,
        'historical027_authorization_sha256': sha(archived_authorization),
        'prior_native_starts': 8, 'prior_sent_turns': 5,
        'previous_cumulative_native_ceiling': 8, 'previous_cumulative_sent_turn_ceiling': 5,
        'new_cumulative_native_ceiling': 10, 'new_cumulative_sent_turn_ceiling': 7,
        'counters_reset': False, 'new_exact_approval_required': True}


def run_stage(scope, prior_scope, run, mode, packet, manifest_sha, expected_binding=None):
    """Fresh actual native process/state; only called after exact human approval."""
    metadata = module('gate0_postlogin_metadata')
    preflight = module('gate0_client_preflight')
    profile = module('p3_reviewer_profile_022')
    planner = module('gate0_client_mount_plan')
    broker_module = module('p3_review_interface_028')
    session = module('p3_reviewer_session_028')
    facts = metadata.inventory(prior_scope, preflight)  # Read-only host provenance; no credentials read.
    require(facts['runtime_before']['sha256'] == scope['runtime_sha256'] and
            facts['bwrap_before']['sha256'] == scope['bwrap_sha256'], 'Native executables changed')
    native = new_directory(run / (mode + '_native'))
    output = new_directory(run / (mode + '_output'))
    for name in ('runtime_state', 'runtime_logs'):
        new_directory(native / name)
    identity = native / 'installation_id_copy'
    with identity.open('xb') as f:
        f.write(facts['identifier_bytes'])
    identity.chmod(0o644)
    require(identity.read_bytes() == facts['identifier_bytes'], 'Private nonsecret identity backing differs')
    requested = profile.reviewer_overrides(preflight.overrides(native),
        bounded(ROOT / 'artifacts/GATE0_CODEX_INTERFACE/20260907_001/config-schema.json'))
    command = [str(facts['runtime']), *profile.cli_override_arguments(requested),
               'app-server','--strict-config','--stdio']
    plan = metadata.build_live_plan(facts, native, command, planner)
    plan.update({'kind':'P3_FINITE_REVIEW_NATIVE_MOUNT_PLAN_028_v1',
                 'native_operation_scope_sha256':SCOPE_SHA256,
                 'full_reviewer_boundary_verified':False})
    prompt = bounded(ROOT / PROMPTS[mode], 64000).decode('utf-8')
    with broker_module.ReviewBroker(packet, manifest_sha256=manifest_sha, output_root=output) as broker:
        before_inputs = broker.verify_inputs()
        observation = session.run_session(plan, native, requested, broker, mode=mode, prompt=prompt,
            wall_seconds=scope['synthetic_seconds_including_cleanup'] if mode=='synthetic'
                         else scope['scientific_seconds_including_cleanup'],
            max_calls=scope['maximum_synthetic_broker_calls'] if mode=='synthetic'
                      else scope['maximum_scientific_broker_calls'], expected_binding=expected_binding)
        # Preserve the safe transport receipt before any later local check can
        # fail. This is evidence of observation, not final stage admission.
        exclusive_json(run / (mode + '_SESSION.json'), observation)
        # A synthetic refusal intentionally closes its broker. Never turn that
        # terminal state into a second synthetic dispatch or a scientific broker.
        after_inputs = broker.verify_inputs() if mode=='science' and not broker._failed else None
    checks = host_checks(facts, metadata, preflight)
    checks['private_installation_id_matches'] = identity.read_bytes() == facts['identifier_bytes']
    checks['all_noncredential_checks_pass'] &= checks['private_installation_id_matches']
    result = {'stage':mode,'mount_plan':plan,'observation':observation,
              'host_checks':checks,'credential_metadata_before':facts['auth_before'],
              'config_origins':facts['origins'],'cache_origins':facts['cache_origins'],
              'packet_before':before_inputs,'packet_after':after_inputs,
              'fresh_process_and_runtime_directories':True,'pi_conversation_imported':False,
              'prior_mount_observation':{'path':'artifacts/GATE0_POSTLOGIN_OBSERVATIONS/20260908_001/REPORT.json',
                  'sha256':'4aa0757da0d56a4db65ca7a33cf15d7454129c21fab7283457261d3a8ebcbba7',
                  'exact_archived_bytes_pinned_by_controller':True,'executed_this_stage':False,
                  'fresh_kernel_attestation':False}}
    exclusive_json(run / (mode + '_STAGE.json'), result)
    return result



def synthetic_recovery_admitted(observation):
    receipts = observation.get('broker_receipts')
    boundary = observation.get('broker_boundary_failure')
    return (observation.get('synthetic_argument_error_observed') is True and
        type(observation.get('recoverable_input_errors')) is int and
        observation['recoverable_input_errors'] == 1 and
        type(observation.get('failed_broker_calls')) is int and observation['failed_broker_calls'] == 2 and
        type(receipts) is list and len(receipts) == 2 and
        all(type(r) is dict and r.get('method') == 'item/tool/call' and
            r.get('tool') == 'read_text' for r in receipts) and
        receipts[0].get('successful') is False and receipts[0].get('error_code') == 'integer_bounds' and
        receipts[1].get('successful') is True and receipts[1].get('error_code') is None and
        boundary == {'layer': 'dispatch', 'code': 'boundary.resource_path', 'tool': 'read_text',
                     'raw_input_path_or_exception_saved': False})


def _packet_preflight(root, packet_info):
    """Local complete content/dependency check, before any native reservation.

    The unchanged installer first verifies the exact private tree and bytes.
    This adds the content-type checks formerly deferred until model calls and
    checks the two bootstrap indexes without assuming an undocumented layout.
    No auditor execution or scientific decision takes place here.
    """
    broker_module = module('p3_review_broker')
    packet = Path(packet_info['packet_path'])
    plain(root / 'delivery', True)
    with tempfile.TemporaryDirectory(prefix='packet028_preflight_', dir=root / 'delivery') as name:
        with broker_module.ReviewBroker(packet,
                manifest_sha256=packet_info['manifest_sha256'], output_root=Path(name)) as broker:
            before = broker.verify_inputs()
            kinds = {'text': 0, 'image': 0, 'binary': 0}
            index_values, image_names = {}, set()
            for path, entry in broker._files.items():
                raw, _ = broker._read(path)
                kind = entry['kind']
                require(kind in kinds, 'Packet has an unsupported resource kind')
                kinds[kind] += 1
                if kind == 'text':
                    try:
                        decoded = raw.decode('utf-8')
                    except UnicodeError:
                        raise Stop('Manifested packet text is not UTF-8') from None
                    if path in ('PACKET_INDEX.json', 'PDF_PAGE_INDEX.json'):
                        try:
                            value = json.loads(decoded)
                        except (ValueError, TypeError):
                            raise Stop('Packet bootstrap index is not valid JSON') from None
                        require(type(value) in (dict, list), 'Packet bootstrap index has a scalar root')
                        index_values[path] = value
                elif kind == 'image':
                    require(len(raw) <= broker_module.MAX_IMAGE_BYTES and
                        raw.startswith(b'\x89PNG\r\n\x1a\n'), 'Packet image is not a bounded PNG page')
                    image_names.add(path)
            for name in ('PACKET_INDEX.json', 'PDF_PAGE_INDEX.json',
                    'docs/P3_AUDIT_REVIEW_PACKET.md', 'docs/P3_RESIDUAL_REVIEW_SUPPLEMENT.md'):
                require(broker._files.get(name, {}).get('kind') == 'text',
                    'Scientific bootstrap resource missing or not text')
            require(set(index_values) == {'PACKET_INDEX.json', 'PDF_PAGE_INDEX.json'},
                    'Scientific bootstrap indexes missing')
            # This checks declarations and all recognized references while leaving
            # the index's descriptive fields and nesting layout uninterpreted.
            index_references = {}
            def check_index(value, references):
                if type(value) is dict:
                    path = value.get('path')
                    if type(path) is str and path in broker._files:
                        entry = broker._files[path]
                        if 'sha256' in value:
                            require(value['sha256'] == entry['sha256'], 'Packet index hash disagrees with manifest')
                        if 'kind' in value:
                            require(value['kind'] == entry['kind'], 'Packet index kind disagrees with manifest')
                        if 'bytes' in value:
                            raw, _ = broker._read(path)
                            require(type(value['bytes']) is int and value['bytes'] == len(raw),
                                'Packet index byte count disagrees with resource')
                    for item in value.values(): check_index(item, references)
                elif type(value) is list:
                    for item in value: check_index(item, references)
                elif type(value) is str and value in broker._files:
                    references.add(value)
            for path, value in index_values.items():
                refs = set(); check_index(value, refs); index_references[path] = refs
            raw, measured = broker._read(broker_module.CLOSURE, 'text')
            require(measured == broker_module.CLOSURE_SHA256, 'Fixed auditor closure changed')
            closure = json.loads(raw)
            _, measured = broker._read(broker_module.AUDITOR, 'text')
            require(measured == broker_module.AUDITOR_SHA256, 'Fixed auditor executable changed')
            dependencies = closure.get('view_input_files')
            require(type(dependencies) is list and type(closure.get('view_input_file_count')) is int and
                len(dependencies) == closure['view_input_file_count'], 'Fixed auditor input count differs')
            names = set()
            for entry in dependencies:
                require(type(entry) is dict and type(entry.get('path')) is str and
                    entry['path'] not in names, 'Fixed auditor dependency declaration differs')
                _, measured = broker._read(entry['path'])
                require(measured == entry.get('sha256'), 'Fixed auditor dependency changed')
                names.add(entry['path'])
            require(broker_module.AUDITOR in names, 'Fixed auditor absent from its view')
            archive = broker._expanded_inventory(closure)
            require(broker.verify_inputs() == before, 'Packet changed during local content preflight')
    return {'kind': 'P3_PRIVATE_PACKET_CONTENT_PREFLIGHT_028_v1',
        'manifest_sha256': packet_info['manifest_sha256'], 'files_rehashed': before['files_rehashed'],
        'content_kinds_verified': kinds,
        'bootstrap_index_reference_counts': {p: len(refs) for p, refs in index_references.items()},
        'fixed_auditor_dependencies_verified': len(dependencies), 'archive_inventory': archive,
        'model_called': False, 'native_process_started': False, 'auditor_executed': False,
        'index_descriptive_schema_not_claimed_validated': True}


def packet_preflight(root, packet_info):
    try:
        return _packet_preflight(root, packet_info)
    except Stop:
        raise
    except Exception as error:
        interface = module('p3_review_interface_028')
        code = interface.classify_broker_failure(error)
        raise Stop('Private packet content preflight refused: ' + code) from None


def admitted_synthetic(stage):
    observation = stage.get('observation', {})
    return (stage.get('stage') == 'synthetic' and
        stage.get('host_checks', {}).get('all_noncredential_checks_pass') is True and
        stage.get('fresh_process_and_runtime_directories') is True and
        stage.get('pi_conversation_imported') is False and
        observation.get('status') == 'SYNTHETIC_REFUSAL_OBSERVED' and
        observation.get('selected_binding') == BINDING and
        observation.get('verdict_submitted') is False and
        synthetic_recovery_admitted(observation) and
        all(observation.get(k) is True for k in ('synthetic_allowed_read_observed', 'observed_refusal',
            'native_process_reaped', 'client_started', 'model_turn_request_sent')))


def admitted_science(stage):
    observation = stage.get('observation', {})
    return (stage.get('stage') == 'science' and
        stage.get('host_checks', {}).get('all_noncredential_checks_pass') is True and
        stage.get('fresh_process_and_runtime_directories') is True and
        stage.get('pi_conversation_imported') is False and
        observation.get('selected_binding') == BINDING and
        observation.get('status') == 'VERDICT_SUBMITTED' and
        all(observation.get(k) is True for k in ('verdict_submitted', 'native_process_reaped',
                                               'client_started', 'model_turn_request_sent')))


def linked_stage(run, stage, mode):
    require(type(stage) is dict and stage.get('stage') == mode and
            canonical(stage.get('observation')) == bounded(run / (mode + '_SESSION.json')),
            'Stage must match separately preserved SESSION before admission')
    require(canonical(stage) == bounded(run / (mode + '_STAGE.json')),
            'Stage differs from separately preserved STAGE receipt')
    return stage


def collect_sessions(run):
    sessions, observations = [], {}
    for mode in ('synthetic', 'science'):
        path = run / (mode + '_SESSION.json')
        if os.path.lexists(path):
            raw = bounded(path)
            observation = json.loads(raw)
            require(observation.get('kind') == SESSION_KIND and observation.get('mode') == mode and
                type(observation.get('client_started')) is bool and
                type(observation.get('model_turn_request_sent')) is bool and
                not (observation['model_turn_request_sent'] and not observation['client_started']),
                'SESSION kind or actual execution counters differ')
            if mode == 'synthetic':
                require(observation.get('verdict_submitted') is False, 'Synthetic SESSION claims a verdict')
            sessions.append({'path': path.name, 'sha256': sha(raw)})
            observations[mode] = observation
    return sessions, observations


def accounting(observations, attempted_modes):
    starts = sum(int(o['client_started']) for o in observations.values())
    turns = sum(int(o['model_turn_request_sent']) for o in observations.values())
    return {'prior_native_starts': 8, 'prior_sent_turns': 5,
        'observed_native_starts_this_attempt': starts, 'observed_sent_turns_this_attempt': turns,
        'cumulative_observed_native_starts': 8 + starts, 'cumulative_observed_sent_turns': 5 + turns,
        'reserved_native_starts_this_attempt': 2, 'reserved_turns_this_attempt': 2,
        'cumulative_native_ceiling': 10, 'cumulative_sent_turn_ceiling': 7,
        'maximum_cumulative_reservation_native_starts': 10, 'maximum_cumulative_reservation_turns': 7,
        'missing_session_counts_are_only_minimum_observations':
            any(mode not in observations for mode in attempted_modes),
        'sent_turn_counts_without_output': True, 'backend_usage_or_charge': 'unknown',
        'unobserved_reserved_capacity_is_not_automatically_released': True, 'no_counter_reset': True}


def existing(run, pins):
    if not os.path.lexists(run):
        return None
    plain(run, True)
    raw = bounded(run / 'REPORT.json')
    require(bounded(run / 'REPORT.sha256', 65) == (sha(raw) + '\n').encode(),
            'Existing028 report checksum differs; preserve it')
    value = json.loads(raw)
    require(value.get('kind') == REPORT_KIND and value.get('pins') == pins and
        value.get('status') in TERMINAL and value.get('parent_credential_contents_read') is False and
        value.get('unattended_model_use_authorized') is False and
        value.get('scientific_verdict_chosen_by_parent') is False,
        'Existing028 provenance or terminal state differs')
    preflight = value.get('private_packet_preflight')
    require(type(preflight) is dict and preflight.get('kind') == 'P3_PRIVATE_PACKET_CONTENT_PREFLIGHT_028_v1' and
        preflight.get('manifest_sha256') == pins['packet_manifest_sha256'] and
        all(preflight.get(k) is False for k in ('model_called', 'native_process_started', 'auditor_executed')),
        'Existing028 local packet preflight receipt differs')
    authorization = value.get('authorization')
    require(type(authorization) is dict and set(authorization) == {'path', 'sha256'} and
        authorization['path'] == 'state/ESCALATION.md' and
        type(authorization['sha256']) is str and len(authorization['sha256']) == 64 and
        all(c in '0123456789abcdef' for c in authorization['sha256']),
        'Existing028 authorization receipt malformed')
    attempt = json.loads(bounded(run / 'ATTEMPT.json'))
    require(attempt.get('pins') == pins and attempt.get('authorization') == authorization and
        type(attempt.get('reserved_native_starts')) is int and attempt['reserved_native_starts'] == 2 and
        type(attempt.get('reserved_turns')) is int and attempt['reserved_turns'] == 2 and
        attempt.get('automatic_retry') is False and attempt.get('science_conditioned_on_synthetic') is True,
        'Existing028 reservation journal differs from receipt')
    # Exact original approval bytes are kept beside the attempt, so later unrelated
    # answers cannot invalidate provenance or authorize a repeat operation.
    approval_raw = bounded(run / 'AUTHORIZATION.md')
    require(sha(approval_raw) == authorization['sha256'], 'Existing028 preserved authorization changed')
    requested = value.get('stage_attempts')
    require(requested in ([], ['synthetic'], ['synthetic', 'science']),
        'Existing028 attempted-stage order differs')
    stages = value.get('stages')
    require(type(stages) is list and len(stages) <= len(requested) and
        [s.get('stage') for s in stages] == requested[:len(stages)], 'Existing028 stage order differs')
    sessions, observations = collect_sessions(run)
    require(value.get('preserved_session_receipts') == sessions and
        all(mode in requested for mode in observations), 'Existing028 SESSION inventory differs')
    for stage in stages:
        linked_stage(run, stage, stage['stage'])
    require({mode for mode in ('synthetic', 'science') if os.path.lexists(run / (mode + '_STAGE.json'))}
            == {stage['stage'] for stage in stages}, 'Unrecorded028 STAGE receipt exists; preserve it')
    require(value.get('science_started') is ('science' in requested),
        'Existing028 science stage declaration differs')
    if 'science' in requested:
        require(stages and admitted_synthetic(stages[0]),
            'Existing028 science lacks separately observed synthetic admission')
    else:
        require(not any(os.path.lexists(run / p) for p in
            ('science_native', 'science_output', 'science_SESSION.json', 'science_STAGE.json')),
            'Unrecorded scientific-stage path exists')
    expected = accounting(observations, requested)
    count = value.get('attempt_accounting')
    require(type(count) is dict and set(count) == set(expected) and
        all(count[k] == v and type(count[k]) is type(v) for k, v in expected.items()),
        'Existing028 counts differ from actual SESSION or reserved capacity')
    output = value.get('reviewer_output')
    output_path = run / 'science_output/REVIEW_VERDICT.json'
    if output is None:
        require(not os.path.lexists(output_path), 'Unrecorded reviewer output exists; preserve it')
        require(value['status'] != 'REVIEWER_OUTPUT_PRESERVED', 'Completed status lacks reviewer output')
    else:
        require(type(output) is dict and output.get('path') == 'science_output/REVIEW_VERDICT.json' and
            output.get('parent_edited') is False and type(output.get('bytes')) is int and
            output.get('execution_admitted') is (value['status'] == 'REVIEWER_OUTPUT_PRESERVED'),
            'Existing028 reviewer output provenance differs')
        output_raw = bounded(output_path, 1024 * 1024)
        require(sha(output_raw) == output.get('sha256') and len(output_raw) == output['bytes'],
            'Existing028 reviewer bytes changed; preserve them')
    if value['status'] == 'REVIEWER_OUTPUT_PRESERVED':
        require(len(stages) == 2 and admitted_synthetic(stages[0]) and admitted_science(stages[1]),
            'Existing028 completion lacks actual stage admission')
    return run / 'REPORT.json'


def execute(scope, prior_scope, pins, authorization, packet_info):
    history = prior_history(pins)
    preflight_receipt = packet_preflight(ROOT, packet_info)
    approval_raw = bounded(ROOT / authorization['path'])
    require(sha(approval_raw) == authorization['sha256'], 'Approval changed before reservation')
    run = ROOT / 'delivery' / RUN_NAME
    new_directory(run)
    with (run / 'AUTHORIZATION.md').open('xb') as handle:
        handle.write(approval_raw); handle.flush(); os.fsync(handle.fileno())
    exclusive_json(run / 'ATTEMPT.json', {'created_utc': datetime.now(timezone.utc).isoformat(),
        'pins': pins, 'authorization': authorization, 'reserved_native_starts': 2, 'reserved_turns': 2,
        'automatic_retry': False, 'science_conditioned_on_synthetic': True})
    result = {'kind': REPORT_KIND, 'created_utc': datetime.now(timezone.utc).isoformat(),
        'pins': pins, 'authorization': authorization, 'history': history,
        'private_packet_preflight': preflight_receipt, 'status': 'STARTED',
        'stages': [], 'stage_attempts': [], 'science_started': False, 'reviewer_output': None,
        'parent_credential_contents_read': False, 'unattended_model_use_authorized': False,
        'continuous_human_attendance_verified': False, 'scientific_verdict_chosen_by_parent': False,
        'automatic_retry_requested': False, 'raw_native_logs_or_protocol_in_report': False}
    try:
        packet, manifest = synthetic_packet(run)
        result['stage_attempts'].append('synthetic')
        stage = run_stage(scope, prior_scope, run, 'synthetic', packet, manifest)
        result['stages'].append(linked_stage(run, stage, 'synthetic'))
        require(admitted_synthetic(stage), 'Synthetic admission incomplete; no science started')
        reloaded_scope, reloaded_prior, reloaded_pins = load_bundle()
        require(reloaded_scope == scope and reloaded_prior == prior_scope and reloaded_pins == pins,
            'Frozen dependencies changed before scientific stage')
        ready = module('install_p3_review_packet').verify_packet(ROOT)
        require(ready['manifest_sha256'] == pins['packet_manifest_sha256'] and
                ready == packet_info, 'Private packet changed before scientific stage')
        result['stage_attempts'].append('science')
        result['science_started'] = True  # Stage attempted; exact process start remains in SESSION.
        stage = run_stage(scope, prior_scope, run, 'science', Path(ready['packet_path']),
            ready['manifest_sha256'], expected_binding=BINDING.copy())
        result['stages'].append(linked_stage(run, stage, 'science'))
        require(stage.get('host_checks', {}).get('all_noncredential_checks_pass') is True,
            'Scientific stage changed protected host inputs')
        if os.path.lexists(run / 'science_output/REVIEW_VERDICT.json'):
            require(admitted_science(stage), 'Output lacks completed broker/session admission; preserve it')
            result['status'] = 'REVIEWER_OUTPUT_PRESERVED'
        else:
            result['status'] = 'STOPPED_WITHOUT_REVIEWER_VERDICT'
    except KeyboardInterrupt:
        result['status'] = 'INTERRUPTED_PARTIAL_PRESERVED'
        result['reason'] = 'Human interruption; no automatic retry'
    except Exception as error:
        result['status'] = 'STOPPED_WITHOUT_COMPLETED_REVIEW'
        result['reason'] = str(error) if type(error) is Stop else 'Guarded local dependency or session stopped; preserve safe receipts'
    # Evidence is retained independently of admission, including a verdict written
    # before later cleanup or host checks failed. The parent never selects content.
    output = run / 'science_output/REVIEW_VERDICT.json'
    if os.path.lexists(output):
        try:
            raw = bounded(output, 1024 * 1024)
            result['reviewer_output'] = {'path': 'science_output/REVIEW_VERDICT.json',
                'sha256': sha(raw), 'bytes': len(raw), 'parent_edited': False,
                'execution_admitted': result['status'] == 'REVIEWER_OUTPUT_PRESERVED'}
        except (Stop, OSError):
            result['status'] = 'STOPPED_WITHOUT_COMPLETED_REVIEW'
            result['reason'] = 'Reviewer output protected inspection failed; preserve all files'
    sessions, observations = collect_sessions(run)
    result['preserved_session_receipts'] = sessions
    result['attempt_accounting'] = accounting(observations, result['stage_attempts'])
    raw = exclusive_json(run / 'REPORT.json', result)
    with (run / 'REPORT.sha256').open('x') as handle:
        handle.write(sha(raw) + '\n'); handle.flush(); os.fsync(handle.fileno())
    return run / 'REPORT.json'


def print_receipt(path):
    value = json.loads(bounded(path))
    require(value.get('status') in TERMINAL, 'Receipt status is not terminal')
    print('STATUS: ' + value['status'])
    print('REPORT: ' + str(path))
    print('REPORT_SHA256: ' + sha(bounded(path)))
    if value.get('reviewer_output') is not None:
        output = path.parent / 'science_output/REVIEW_VERDICT.json'
        require(os.path.lexists(output), 'Recorded verdict is absent; preserve the receipt')
        print('REVIEW_VERDICT: ' + str(output))
    else:
        print('No scientific verdict was submitted. Attach REPORT.json only.')


def safe_stop_message(error):
    return str(error) if type(error) is Stop else (
        'Protected history, approval, dependency or receipt check failed; existing work preserved.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-attended-review', action='store_true')
    args = parser.parse_args()
    scope, prior, pins = load_bundle()
    cached = existing(ROOT / 'delivery' / RUN_NAME, pins)
    if cached:
        print('VERIFIED TERMINAL RECEIPT; REUSED without a native process or new turn.')
        print_receipt(cached)
        return 0
    if not args.run_attended_review:
        print('Inspection only. Prepared028 scope SHA256: ' + SCOPE_SHA256)
        print('Observed 8 starts / 5 sent turns exhaust the prior ceiling. Exact028 approval required for 10/7.')
        print('At most one synthetic and one conditional fresh scientific stage; no automatic retry.')
        return 0
    old.canonical_host(scope)
    authorization = approval(scope, manual_launch=True)
    info = module('install_p3_review_packet').verify_packet(ROOT)
    require(info['manifest_sha256'] == scope['private_packet_manifest_sha256'], 'Wrong private evidence packet')
    path = execute(scope, prior, pins, authorization, info)
    print_receipt(path)
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (Stop, OSError, ValueError, KeyError, TypeError) as error:
        print('STOP: ' + safe_stop_message(error))
        raise SystemExit(1)
