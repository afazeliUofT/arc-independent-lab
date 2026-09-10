#!/usr/bin/env python3
"""One exactly approved synthetic admission and conditional fresh scientific review.

The proposed 12-start/9-sent-turn cumulative ceiling requires exact030 approval. Every
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
SCOPE_PATH = 'configs/P3_FINITE_REVIEW_SCOPE_030.json'
SCOPE_SHA256 = '5abc5794f3adadeebc0e3df3e1ffd5bc4416806d2d1212f0a6b73db96d177060'
SOURCE_PINS = {
    "scripts/p3_finite_review_028.py": "be4e03c682e9050bd1d4ab61a0c24dd3ab1e97782e221c4c7813cab315763c19",
    "scripts/p3_review_interface_028.py": "ef41a59491f67252674079b18fa21e46257bdaf5cb2cabf76d9ba376ce6e2d1a",
    "scripts/p3_review_protocol_028.py": "d41ecb40a6d63179657e5e04df2491b4bf431a5b28229210b96e640fba49b224",
    "scripts/p3_reviewer_session_030.py": "3aa2881e5bad8d9b9fa61aa64eeb54cb784f5bd16ca04fee152caf5c0de0145b",
    "configs/P3_SYNTHETIC_PROMPT_028.txt": "c930a6accbe8d704cf3467319a39cf81b189e0c18425108baed0023d01873c1a",
    "artifacts/P3_INTERFACE_CONTRACT_SOURCE/20260910_028/MANIFEST.json": "e791f83e1966c29dcd04683ae403e3229cae6ba9f0fb6845fc3dd601f9e0b16d",
    "scripts/p3_cache_inputs_030.py": "aa29e239efcd23cfdefe4c1488a200924c494fa21d28e5ecb750adb388fdc711",
    "scripts/p3_stage_evidence_030.py": "669c4169df508f9aac143b0bef3702bc478b18659300d8f80404a6db51e04378",
    "scripts/p3_event_policy_030.py": "ad8c1fa0bb3bb1c755f90b5d1c4c68f3368d4fa6af6552ea21f57f215de7dd2c"
}

RUN_NAME = 'P3_FINITE_REVIEW_030'
REPORT_KIND = 'P3_FINITE_REVIEW_030_v1'
SESSION_KIND = 'P3_FINITE_REVIEWER_SESSION_030_v1'
REPORT028_PATH = 'artifacts/P3_REVIEW_SESSION_STOP_OBSERVATIONS/20260910_029/REPORT.json'
REPORT028_SHA256 = 'b96152d5f07f502a41b7e218417d20d6775b9751c7440f94de1015dc39cd336a'
SESSION028_SHA256 = {'synthetic': 'a71633940cbc5b448f28a21f5aa3ef49f3f3ff2be5a7d816d28f28f4b05b3c8b',
    'science': '9fb59ef888e174c8265ba960c1e683703dec90d855d609f8cccfa07d19456af0'}
AUTH028_PATH = 'state/escalations/2026-09-10_FINITE_REVIEW_028_APPROVED.md'
AUTH028_SHA256 = 'fd51efe16cd1a1ea2401935237ac674f18b4c963dfaf0322c13c9de428a16b35'
OLD_CONTROLLER_SHA256 = 'be4e03c682e9050bd1d4ab61a0c24dd3ab1e97782e221c4c7813cab315763c19'
BINDING = {'model': 'gpt-5.6-sol', 'id': 'gpt-5.6-sol', 'effort': 'max'}
TERMINAL = ('REVIEWER_OUTPUT_PRESERVED', 'STOPPED_WITHOUT_REVIEWER_VERDICT',
            'STOPPED_WITHOUT_COMPLETED_REVIEW', 'INTERRUPTED_PARTIAL_PRESERVED')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value, indent=2, ensure_ascii=True, allow_nan=False) + '\n').encode()


def _prior_controller():
    path = ROOT / 'scripts/p3_finite_review_028.py'
    cursor = Path(path.anchor)
    for part in path.parts[1:]:
        cursor /= part
        if cursor.is_symlink():
            raise RuntimeError('Symlink in historical controller path')
    info = path.stat()
    if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > 16 * 1024 * 1024 or
            sha(path.read_bytes()) != OLD_CONTROLLER_SHA256):
        raise RuntimeError('Historical028 controller changed')
    name = 'p3_finite_review_028'
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
PROMPTS = {**old.PROMPTS, 'synthetic': 'configs/P3_SYNTHETIC_PROMPT_028.txt'}


def load_bundle():
    scope028, prior, inherited = previous.load_bundle()
    raw = bounded(ROOT / SCOPE_PATH)
    require(sha(raw) == SCOPE_SHA256 and len(SOURCE_PINS) >= 3,
            'Unfinished030 scope or dependency pins')
    for path, digest in SOURCE_PINS.items():
        require(sha(bounded(ROOT / path, 16 * 1024 * 1024)) == digest,
                '030 dependency changed')
    scope = json.loads(raw)
    require(scope.get('scope_id') == 'P3_FINITE_REVIEW_SCOPE_030' and
            scope.get('approval_id') == 'APPROVE_P3_FINITE_REVIEW_030_CORRECTION' and
            scope.get('report_directory') == 'delivery/' + RUN_NAME,
            '030 scope identity differs')
    # All per-stage, model and account controls remain fixed. The declared cache
    # backing, native lifecycle and failure evidence corrections require new approval.
    fixed = ('canonical_home', 'canonical_project', 'runtime_sha256', 'bwrap_sha256',
        'accepted_metadata_path', 'accepted_metadata_sha256', 'prior_native_scope_path',
        'prior_native_scope_sha256', 'synthetic_seconds_including_cleanup',
        'scientific_seconds_including_cleanup', 'cleanup_seconds_per_process',
        'maximum_native_processes', 'maximum_model_turns', 'maximum_synthetic_broker_calls',
        'maximum_scientific_broker_calls', 'maximum_native_file_bytes',
        'maximum_native_runtime_tree_bytes', 'maximum_synthetic_native_cpu_seconds',
        'maximum_scientific_native_cpu_seconds', 'maximum_run_attempts_per_invocation',
        'model_policy', 'private_packet_directory', 'private_packet_manifest_sha256',
        'maximum_synthetic_stdout_bytes', 'maximum_scientific_stdout_bytes',
        'maximum_stderr_bytes_per_process', 'maximum_protocol_frame_bytes',
        'maximum_outbound_queue_bytes', 'maximum_early_frames', 'maximum_early_frame_bytes',
        'parent_request_timeout_seconds', 'maximum_catalog_pages', 'maximum_catalog_entries',
        'native_cpu_hard_limit_grace_seconds')
    require(all(scope.get(k) == scope028[k] and type(scope.get(k)) is type(scope028[k])
                for k in fixed), '030 changed the inherited operational controls')
    expected = {'native_starts_observed': 10, 'explicit_model_turns_observed': 7,
        'additional_native_processes_maximum': 2, 'additional_explicit_model_turns_maximum': 2,
        'cumulative_native_starts_maximum': 12, 'cumulative_explicit_model_turns_maximum': 9,
        'no_automatic_retry': True, 'count_sent_turn_even_without_reviewer_output': True}
    counts = scope.get('prior_attempt_accounting', {})
    require(all(counts.get(k) == v and type(counts.get(k)) is type(v) for k, v in expected.items()),
            '030 cumulative accounting or no-retry restriction differs')
    policy = scope.get('interface_correction', {})
    require(type(policy.get('maximum_recoverable_input_errors_per_stage')) is int and
            policy['maximum_recoverable_input_errors_per_stage'] == 8 and
            policy.get('ninth_input_error_is_terminal') is True and
            policy.get('synthetic_prompt') == PROMPTS['synthetic'] and
            policy.get('scientific_prompt_unchanged') is True and
            policy.get('no_new_tools_or_file_authority') is True, '030 interface correction policy differs')
    cache_policy = scope.get('cache_input_correction', {})
    lifecycle = scope.get('native_lifecycle_correction', {})
    evidence_policy = scope.get('stage_evidence_correction', {})
    require(cache_policy.get('exact_cache_names') ==
            ['cloud-config-bundle-cache.json', 'models_cache.json'] and
            type(cache_policy.get('maximum_bytes_per_cache')) is int and
            cache_policy['maximum_bytes_per_cache'] == 4 * 1024 * 1024 and
            all(cache_policy.get(k) is True for k in (
                'sealed_memfd_backing_same_native_paths', 'absence_preserved',
                'source_matches_preflight_origins_required', 'all_non_cache_mount_arguments_unchanged',
                'no_credentials_opened_hashed_or_copied', 'no_cache_content_saved_or_rewritten',
                'read_only_data_bind', 'live_descriptors_not_serialized_as_reusable_authority',
                'source_after_metadata_recorded_separately', 'source_writer_not_inferred',
                'sealed_input_integrity_mandatory')), '030 cache input amendment differs')
    require(lifecycle.get('newly_admitted_item_types') == ['contextCompaction', 'plan'] and
            lifecycle.get('newly_admitted_notifications') ==
                ['item/plan/delta', 'model/safetyBuffering/updated'] and
            type(lifecycle.get('maximum_lifecycle_items_per_stage')) is int and
            lifecycle['maximum_lifecycle_items_per_stage'] == 4096 and
            all(lifecycle.get(k) is True for k in ('all_other_native_item_effects_remain_terminal',
                'retained_context_may_change_and_internal_inference_may_occur',
                'extra_explicit_parent_turn_start_forbidden', 'all_existing_limits_continue_without_reset',
                'safety_buffering_metadata_same_bound_model_only',
                'safety_buffering_recommendations_never_select_model',
                'raw_safety_metadata_not_retained',
                'passive_metadata_bounded_by_existing_protocol_frame')),
            '030 native lifecycle amendment differs')
    require(all(evidence_policy.get(k) is True for k in ('session_saved_before_postchecks',
                'independent_checks_do_not_short_circuit', 'all_failure_classes_retained',
                'session_failure_not_replaced_by_later_postcheck',
                'any_integrity_failure_blocks_admission', 'preserved_verdict_never_implies_admission')),
            '030 stage evidence amendment differs')
    kernel = scope.get('kernel_mount_prerequisite', {})
    require(type(kernel.get('maximum_synthetic_sandbox_processes')) is int and
            kernel['maximum_synthetic_sandbox_processes'] == 1 and
            type(kernel.get('maximum_seconds_including_cleanup')) is int and
            kernel['maximum_seconds_including_cleanup'] == 10 and
            all(kernel.get(k) is True for k in ('before_native_reservation',
                'source_bwrap_sha256_verified_first', 'no_real_cache_or_credential_content_access',
                'no_native_client_or_model_request', 'network_unshared',
                'preserve_pass_failure_or_partial_without_automatic_retry',
                'no_separate_human_probe', 'fresh_process_group_and_bounded_reaping_required')),
            '030 kernel prerequisite amendment differs')
    require(sha(bounded(ROOT / REPORT028_PATH)) == REPORT028_SHA256 and
            sha(bounded(ROOT / AUTH028_PATH)) == AUTH028_SHA256,
            '028 input or historical028 approval archive changed')
    return scope, prior, {'scope_sha256': SCOPE_SHA256,
        'controller_sha256': sha(bounded(Path(__file__))), 'source_pins': SOURCE_PINS,
        'inherited028_pins': inherited, 'report028_sha256': REPORT028_SHA256,
        'historical028_approval_sha256': AUTH028_SHA256,
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
    require(len(positions) == 1, 'Exactly one actual030 ANSWER is required')
    require([line for line in lines[positions[0] + 1:] if line.strip()] ==
            ['APPROVE_P3_FINITE_REVIEW_030_CORRECTION', 'scope_sha256: ' + SCOPE_SHA256],
            'Recorded answer differs from exact030 scope')
    return {'path': 'state/ESCALATION.md', 'sha256': sha(raw)}


def prior_history(pins):
    # Historical validators inspect canonical receipts; they never launch or use
    # today's approval. Actual separate SESSION files are never reconstructed.
    inherited = pins['inherited028_pins']
    earlier = previous.prior_history(inherited)
    path = previous.existing(ROOT / 'delivery' / previous.RUN_NAME, inherited)
    require(path is not None, 'Actual028 receipt is required before new reservation')
    raw = bounded(path)
    require(sha(raw) == REPORT028_SHA256 and bounded(ROOT / REPORT028_PATH) == raw,
            'Actual028 report differs from archived original')
    archived_authorization = bounded(ROOT / AUTH028_PATH)
    require(sha(archived_authorization) == AUTH028_SHA256 and
            bounded(path.parent / 'AUTHORIZATION.md') == archived_authorization,
            'Historical028 approval archive or original run authorization changed')
    value = json.loads(raw)
    stages = value.get('stages')
    require(value.get('history') == earlier and value.get('pins') == inherited and
            value.get('status') == 'STOPPED_WITHOUT_COMPLETED_REVIEW' and
            value.get('reason') == 'Scientific stage changed protected host inputs' and
            value.get('science_started') is True and value.get('reviewer_output') is None and
            type(stages) is list and [s.get('stage') for s in stages] == ['synthetic', 'science'],
            'Actual028 failed stage, history or provenance differs')
    measured_sessions = {}
    for mode, stage in zip(('synthetic', 'science'), stages):
        session_raw = bounded(path.parent / (mode + '_SESSION.json'))
        require(sha(session_raw) == SESSION028_SHA256[mode],
                'Actual028 SESSION missing or changed; never reconstruct it')
        observation = stage.get('observation', {})
        require(canonical(observation) == session_raw and
                all(observation.get(k) is True for k in ('client_started', 'model_turn_request_sent',
                                                         'native_process_reaped')) and
                observation.get('verdict_submitted') is False and
                stage.get('fresh_process_and_runtime_directories') is True and
                stage.get('pi_conversation_imported') is False,
                'Actual028 separate session linkage or cleanup differs')
        measured_sessions[mode] = sha(session_raw)
    science = stages[1]
    observation = science['observation']
    checks = science.get('host_checks', {})
    require(previous.admitted_synthetic(stages[0]) and
            observation.get('status') == 'STOPPED_WITHOUT_VERDICT' and
            observation.get('reason') == 'Unadvertised native item effect' and
            observation.get('broker_boundary_failure') is None and
            len(observation.get('broker_receipts', [])) == 88 and
            checks.get('cache_metadata_unchanged') is False and
            checks.get('all_noncredential_checks_pass') is False and
            science.get('packet_before') == science.get('packet_after'),
            'Actual028 expected failed historical state differs; it is not admitted')
    counts = value['attempt_accounting']
    expected = {'cumulative_observed_native_starts': 10, 'cumulative_observed_sent_turns': 7,
        'cumulative_native_ceiling': 10, 'cumulative_sent_turn_ceiling': 7}
    require(all(type(counts.get(k)) is int and counts[k] == v for k, v in expected.items()),
            'Actual028 observed counts or exhausted ceiling differs')
    return {'actual019_to028_history_reverified': True, 'separate028_sessions_reverified': True,
        'report028_sha256': sha(raw), 'session028_sha256': measured_sessions,
        'historical028_authorization_sha256': sha(archived_authorization),
        'historical028_science_admitted': False, 'historical028_failures_preserved': True,
        'prior_native_starts': 10, 'prior_sent_turns': 7,
        'previous_cumulative_native_ceiling': 10, 'previous_cumulative_sent_turn_ceiling': 7,
        'new_cumulative_native_ceiling': 12, 'new_cumulative_sent_turn_ceiling': 9,
        'counters_reset': False, 'new_exact_approval_required': True}



def run_stage(scope, prior_scope, run, mode, packet, manifest_sha, expected_binding=None):
    """Fresh native process only after exact human scope and explicit command.

    Snapshots change only the backing of two known noncredential cache files.
    Credential and configuration grants, science packet and model controls retain
    their inherited origins. Session evidence is saved before independent checks.
    """
    metadata = module('gate0_postlogin_metadata')
    preflight = module('gate0_client_preflight')
    profile = module('p3_reviewer_profile_022')
    planner = module('gate0_client_mount_plan')
    broker_module = module('p3_review_interface_028')
    session = module('p3_reviewer_session_030')
    cache = module('p3_cache_inputs_030')
    evidence = module('p3_stage_evidence_030')
    facts = metadata.inventory(prior_scope, preflight)
    require(facts['runtime_before']['sha256'] == scope['runtime_sha256'] and
            facts['bwrap_before']['sha256'] == scope['bwrap_sha256'], 'Native executables changed')
    native = new_directory(run / (mode + '_native'))
    output = new_directory(run / (mode + '_output'))
    for name in ('runtime_state', 'runtime_logs'):
        new_directory(native / name)
    identity = native / 'installation_id_copy'
    with identity.open('xb') as handle:
        handle.write(facts['identifier_bytes'])
    identity.chmod(0o644)
    require(identity.read_bytes() == facts['identifier_bytes'], 'Private nonsecret identity backing differs')
    requested = profile.reviewer_overrides(preflight.overrides(native),
        bounded(ROOT / 'artifacts/GATE0_CODEX_INTERFACE/20260907_001/config-schema.json'))
    command = [str(facts['runtime']), *profile.cli_override_arguments(requested),
               'app-server', '--strict-config', '--stdio']
    plan = metadata.build_live_plan(facts, native, command, planner)
    plan.update({'kind': 'P3_FINITE_REVIEW_NATIVE_MOUNT_PLAN_030_v1',
                 'native_operation_scope_sha256': SCOPE_SHA256,
                 'full_reviewer_boundary_verified': False})
    prompt = bounded(ROOT / PROMPTS[mode], 64000).decode('utf-8')
    with cache.capture_cache_inputs(facts['codex_home'], auth_metadata=facts['auth_before']) as cache_inputs:
        cache_inputs.verify_origins(facts['cache_origins'])
        plan = cache_inputs.apply_to_plan(plan)
        with broker_module.ReviewBroker(packet, manifest_sha256=manifest_sha, output_root=output) as broker:
            before_inputs = broker.verify_inputs()
            base = {'mount_plan': cache_inputs.report_plan(plan),
                    'credential_metadata_before': facts['auth_before'],
                    'config_origins': facts['origins'], 'cache_origins': facts['cache_origins'],
                    'cache_inputs_before': cache_inputs.receipt(), 'packet_before': before_inputs,
                    'fresh_process_and_runtime_directories': True, 'pi_conversation_imported': False,
                    'prior_mount_observation': {
                        'path': 'artifacts/GATE0_POSTLOGIN_OBSERVATIONS/20260908_001/REPORT.json',
                        'sha256': '4aa0757da0d56a4db65ca7a33cf15d7454129c21fab7283457261d3a8ebcbba7',
                        'exact_archived_bytes_pinned_by_controller': True, 'executed_this_stage': False,
                        'fresh_kernel_attestation': False}}
            observation = session.run_session(plan, native, requested, broker, mode=mode, prompt=prompt,
                wall_seconds=scope['synthetic_seconds_including_cleanup'] if mode == 'synthetic'
                             else scope['scientific_seconds_including_cleanup'],
                max_calls=scope['maximum_synthetic_broker_calls'] if mode == 'synthetic'
                          else scope['maximum_scientific_broker_calls'],
                expected_binding=expected_binding, cache_inputs=cache_inputs)
            def packet_after():
                if mode == 'synthetic':
                    return None  # Expected refusal closes only the synthetic broker.
                require(not broker._failed, 'Scientific broker closed before integrity postcheck')
                return broker.verify_inputs()
            return evidence.finalize_stage(run, mode, observation,
                host_checks_call=lambda: evidence.collect_postchecks(
                    facts, metadata, preflight, identity, cache_inputs),
                packet_check_call=packet_after, base_fields=base, write_json=exclusive_json)



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
    with tempfile.TemporaryDirectory(prefix='packet030_preflight_', dir=root / 'delivery') as name:
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
        stage.get('failures') == [] and
        stage.get('fresh_process_and_runtime_directories') is True and
        stage.get('pi_conversation_imported') is False and
        observation.get('status') == 'SYNTHETIC_REFUSAL_OBSERVED' and
        observation.get('selected_binding') == BINDING and
        observation.get('cache_input_descriptors_verified') is True and
        observation.get('verdict_submitted') is False and
        synthetic_recovery_admitted(observation) and
        all(observation.get(k) is True for k in ('synthetic_allowed_read_observed', 'observed_refusal',
            'native_process_reaped', 'client_started', 'model_turn_request_sent')))


def admitted_science(stage):
    observation = stage.get('observation', {})
    return (stage.get('stage') == 'science' and
        stage.get('host_checks', {}).get('all_noncredential_checks_pass') is True and
        stage.get('failures') == [] and
        stage.get('fresh_process_and_runtime_directories') is True and
        stage.get('pi_conversation_imported') is False and
        observation.get('selected_binding') == BINDING and
        observation.get('cache_input_descriptors_verified') is True and
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
    return {'prior_native_starts': 10, 'prior_sent_turns': 7,
        'observed_native_starts_this_attempt': starts, 'observed_sent_turns_this_attempt': turns,
        'cumulative_observed_native_starts': 10 + starts, 'cumulative_observed_sent_turns': 7 + turns,
        'reserved_native_starts_this_attempt': 2, 'reserved_turns_this_attempt': 2,
        'cumulative_native_ceiling': 12, 'cumulative_sent_turn_ceiling': 9,
        'maximum_cumulative_reservation_native_starts': 12, 'maximum_cumulative_reservation_turns': 9,
        'missing_session_counts_are_only_minimum_observations':
            any(mode not in observations for mode in attempted_modes),
        'sent_turn_counts_without_output': True, 'backend_usage_or_charge': 'unknown',
        'unobserved_reserved_capacity_is_not_automatically_released': True, 'no_counter_reset': True}


def primary_session_stops(observations):
    return [{'stage': mode, 'reason': observation.get('primary_failure', observation.get('reason'))}
        for mode, observation in observations.items()
        if observation.get('status') not in ('SYNTHETIC_REFUSAL_OBSERVED', 'VERDICT_SUBMITTED')]


def stage_failures(stages):
    return [{'stage': stage['stage'], **failure}
        for stage in stages for failure in stage.get('failures', [])]


def existing(run, pins):
    if not os.path.lexists(run):
        return None
    plain(run, True)
    raw = bounded(run / 'REPORT.json')
    require(bounded(run / 'REPORT.sha256', 65) == (sha(raw) + '\n').encode(),
            'Existing030 report checksum differs; preserve it')
    value = json.loads(raw)
    require(value.get('kind') == REPORT_KIND and value.get('pins') == pins and
        value.get('status') in TERMINAL and value.get('parent_credential_contents_read') is False and
        value.get('unattended_model_use_authorized') is False and
        value.get('scientific_verdict_chosen_by_parent') is False,
        'Existing030 provenance or terminal state differs')
    preflight = value.get('private_packet_preflight')
    require(type(preflight) is dict and preflight.get('kind') == 'P3_PRIVATE_PACKET_CONTENT_PREFLIGHT_028_v1' and
        preflight.get('manifest_sha256') == pins['packet_manifest_sha256'] and
        all(preflight.get(k) is False for k in ('model_called', 'native_process_started', 'auditor_executed')),
        'Existing030 local packet preflight receipt differs')
    authorization = value.get('authorization')
    require(type(authorization) is dict and set(authorization) == {'path', 'sha256'} and
        authorization['path'] == 'state/ESCALATION.md' and
        type(authorization['sha256']) is str and len(authorization['sha256']) == 64 and
        all(c in '0123456789abcdef' for c in authorization['sha256']),
        'Existing030 authorization receipt malformed')
    attempt = json.loads(bounded(run / 'ATTEMPT.json'))
    require(attempt.get('pins') == pins and attempt.get('authorization') == authorization and
        type(attempt.get('reserved_native_starts')) is int and attempt['reserved_native_starts'] == 2 and
        type(attempt.get('reserved_turns')) is int and attempt['reserved_turns'] == 2 and
        attempt.get('automatic_retry') is False and attempt.get('science_conditioned_on_synthetic') is True,
        'Existing030 reservation journal differs from receipt')
    kernel = verify_kernel_preflight_receipt(value.get('sealed_cache_kernel_preflight'),
        run=run, pins=pins, authorization=authorization)
    require(attempt.get('sealed_cache_kernel_preflight') == kernel,
            'Existing030 kernel prerequisite differs from original reservation')
    # Exact original approval bytes are kept beside the attempt, so later unrelated
    # answers cannot invalidate provenance or authorize a repeat operation.
    approval_raw = bounded(run / 'AUTHORIZATION.md')
    require(sha(approval_raw) == authorization['sha256'], 'Existing030 preserved authorization changed')
    requested = value.get('stage_attempts')
    require(requested in ([], ['synthetic'], ['synthetic', 'science']),
        'Existing030 attempted-stage order differs')
    stages = value.get('stages')
    require(value.get('unlinked_stage_receipts') == [],
            'Existing030 has an unlinked stage; partial evidence preserved without retry')
    require(type(stages) is list and len(stages) <= len(requested) and
        [s.get('stage') for s in stages] == requested[:len(stages)], 'Existing030 stage order differs')
    sessions, observations = collect_sessions(run)
    require(value.get('preserved_session_receipts') == sessions and
        all(mode in requested for mode in observations), 'Existing030 SESSION inventory differs')
    for stage in stages:
        linked_stage(run, stage, stage['stage'])
    require({mode for mode in ('synthetic', 'science') if os.path.lexists(run / (mode + '_STAGE.json'))}
            == {stage['stage'] for stage in stages}, 'Unrecorded030 STAGE receipt exists; preserve it')
    require(value.get('science_started') is ('science' in requested),
        'Existing030 science stage declaration differs')
    if 'science' in requested:
        require(stages and admitted_synthetic(stages[0]),
            'Existing030 science lacks separately observed synthetic admission')
    else:
        require(not any(os.path.lexists(run / p) for p in
            ('science_native', 'science_output', 'science_SESSION.json', 'science_STAGE.json')),
            'Unrecorded scientific-stage path exists')
    require(value.get('primary_session_stops') == primary_session_stops(observations) and
            value.get('stage_failures') == stage_failures(stages),
            'Existing030 independent failure evidence differs from preserved receipts')
    expected = accounting(observations, requested)
    count = value.get('attempt_accounting')
    require(type(count) is dict and set(count) == set(expected) and
        all(count[k] == v and type(count[k]) is type(v) for k, v in expected.items()),
        'Existing030 counts differ from actual SESSION or reserved capacity')
    output = value.get('reviewer_output')
    output_path = run / 'science_output/REVIEW_VERDICT.json'
    if output is None:
        require(not os.path.lexists(output_path), 'Unrecorded reviewer output exists; preserve it')
        require(value['status'] != 'REVIEWER_OUTPUT_PRESERVED', 'Completed status lacks reviewer output')
    else:
        require(type(output) is dict and output.get('path') == 'science_output/REVIEW_VERDICT.json' and
            output.get('parent_edited') is False and type(output.get('bytes')) is int and
            output.get('execution_admitted') is (value['status'] == 'REVIEWER_OUTPUT_PRESERVED'),
            'Existing030 reviewer output provenance differs')
        output_raw = bounded(output_path, 1024 * 1024)
        require(sha(output_raw) == output.get('sha256') and len(output_raw) == output['bytes'],
            'Existing030 reviewer bytes changed; preserve them')
    if value['status'] == 'REVIEWER_OUTPUT_PRESERVED':
        require(len(stages) == 2 and admitted_synthetic(stages[0]) and admitted_science(stages[1]),
            'Existing030 completion lacks actual stage admission')
    return run / 'REPORT.json'


def verify_kernel_preflight_receipt(reference, *, run, pins, authorization):
    require(type(reference) is dict and set(reference) == {'path', 'sha256', 'observation'} and
            reference['path'] == RUN_NAME + '_KERNEL_PREFLIGHT/REPORT.json',
            '030 kernel prerequisite reference differs')
    path = run.parent / reference['path']
    raw = bounded(path)
    require(sha(raw) == reference['sha256'] and
            bounded(path.with_name('REPORT.sha256'), 65) == (sha(raw) + '\n').encode() and
            canonical(reference['observation']) == raw,
            '030 kernel prerequisite receipt differs')
    value = reference['observation']
    result = value.get('observation', {})
    require(value.get('kind') == 'P3_SEALED_CACHE_KERNEL_PREREQUISITE_030_v1' and
            value.get('pins') == pins and value.get('authorization') == authorization and
            result.get('kind') == 'P3_SEALED_CACHE_MOUNT_PREFLIGHT_030_v1' and
            result.get('status') == 'PASSED' and result.get('kernel_child_mount_verified') is True and
            result.get('synthetic_only') is True and
            result.get('real_cache_or_credential_contents_accessed') is False and
            type(result.get('native_clients_started')) is int and result['native_clients_started'] == 0 and
            type(result.get('model_turns_sent')) is int and result['model_turns_sent'] == 0,
            '030 kernel prerequisite was not passed under this exact scope')
    expected_checks = {'exact_snapshot_bytes', 'absent_cache_stays_absent',
        'synthetic_auth_not_mounted', 'snapshot_write_refused',
        'snapshot_truncate_refused', 'absent_cache_creation_refused'}
    checks = result.get('checks')
    diagnostic = result.get('synthetic_diagnostic')
    require(type(checks) is dict and set(checks) == expected_checks and
            all(item is True for item in checks.values()) and
            type(result.get('exit_code')) is int and result['exit_code'] == 0 and
            result.get('same_inode_source_mutation_performed') is True and
            type(result.get('sealed_inputs_after')) is dict and
            result['sealed_inputs_after'].get('all_inputs_intact') is True and
            type(diagnostic) is dict and 'failure_code' in diagnostic and
            diagnostic['failure_code'] is None and
            diagnostic.get('direct_child_reaped') is True and
            diagnostic.get('process_group_absent_after_cleanup') is True,
            '030 kernel prerequisite lacks complete actual checks or process cleanup')
    return reference


def kernel_preflight(scope, prior_scope, pins, authorization):
    """Once-only synthetic kernel prerequisite, before any Codex reservation.

    A failed or partial prerequisite is preserved and never automatically retried.
    No native client, model request, actual cache or credential content is used.
    """
    path = ROOT / 'delivery' / (RUN_NAME + '_KERNEL_PREFLIGHT')
    require(not os.path.lexists(path),
            'Existing030 kernel prerequisite must be preserved; no automatic probe retry: ' + str(path))
    metadata = module('gate0_postlogin_metadata')
    preflight = module('gate0_client_preflight')
    cache = module('p3_cache_inputs_030')
    facts = metadata.inventory(prior_scope, preflight)
    require(facts['runtime_before']['sha256'] == scope['runtime_sha256'] and
            facts['bwrap_before']['sha256'] == scope['bwrap_sha256'],
            'Native executables changed before kernel prerequisite')
    new_directory(path)
    exclusive_json(path / 'ATTEMPT.json', {'pins': pins, 'authorization': authorization,
        'maximum_synthetic_sandbox_processes': 1, 'native_clients_started': 0,
        'model_turns_sent': 0, 'automatic_retry': False})
    try:
        observed = cache.probe_sealed_mount(facts['bwrap'], ROOT / 'delivery')
    except KeyboardInterrupt:
        observed = {'kind': 'P3_SEALED_CACHE_MOUNT_PREFLIGHT_030_v1', 'status': 'UNVERIFIED',
            'reason': 'human_interrupted_kernel_prerequisite', 'native_clients_started': 0,
            'model_turns_sent': 0, 'real_cache_or_credential_contents_accessed': False,
            'synthetic_only': True, 'kernel_child_mount_verified': False}
    except Exception:
        observed = {'kind': 'P3_SEALED_CACHE_MOUNT_PREFLIGHT_030_v1', 'status': 'UNVERIFIED',
            'reason': 'protected_kernel_prerequisite_failed', 'native_clients_started': 0,
            'model_turns_sent': 0, 'real_cache_or_credential_contents_accessed': False,
            'synthetic_only': True, 'kernel_child_mount_verified': False}
    result = {'kind': 'P3_SEALED_CACHE_KERNEL_PREREQUISITE_030_v1',
        'created_utc': datetime.now(timezone.utc).isoformat(), 'pins': pins,
        'authorization': authorization, 'observation': observed, 'automatic_retry': False}
    raw = exclusive_json(path / 'REPORT.json', result)
    with (path / 'REPORT.sha256').open('x') as handle:
        handle.write(sha(raw) + '\n'); handle.flush(); os.fsync(handle.fileno())
    reference = {'path': path.name + '/REPORT.json', 'sha256': sha(raw), 'observation': result}
    require(observed.get('status') == 'PASSED',
            'Sealed cache kernel prerequisite did not pass; no Codex reservation; receipt: ' + str(path / 'REPORT.json'))
    return verify_kernel_preflight_receipt(reference,
        run=ROOT / 'delivery' / RUN_NAME, pins=pins, authorization=authorization)


def execute(scope, prior_scope, pins, authorization, packet_info):
    history = prior_history(pins)
    preflight_receipt = packet_preflight(ROOT, packet_info)
    approval_raw = bounded(ROOT / authorization['path'])
    require(sha(approval_raw) == authorization['sha256'], 'Approval changed before kernel prerequisite')
    kernel_receipt = kernel_preflight(scope, prior_scope, pins, authorization)
    require(bounded(ROOT / authorization['path']) == approval_raw, 'Approval changed before reservation')
    run = ROOT / 'delivery' / RUN_NAME
    new_directory(run)
    with (run / 'AUTHORIZATION.md').open('xb') as handle:
        handle.write(approval_raw); handle.flush(); os.fsync(handle.fileno())
    exclusive_json(run / 'ATTEMPT.json', {'created_utc': datetime.now(timezone.utc).isoformat(),
        'pins': pins, 'authorization': authorization, 'reserved_native_starts': 2, 'reserved_turns': 2,
        'automatic_retry': False, 'science_conditioned_on_synthetic': True,
        'sealed_cache_kernel_preflight': kernel_receipt})
    result = {'kind': REPORT_KIND, 'created_utc': datetime.now(timezone.utc).isoformat(),
        'pins': pins, 'authorization': authorization, 'history': history,
        'private_packet_preflight': preflight_receipt,
        'sealed_cache_kernel_preflight': kernel_receipt, 'status': 'STARTED',
        'stages': [], 'stage_attempts': [], 'unlinked_stage_receipts': [],
        'science_started': False, 'reviewer_output': None,
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
            'Scientific stage integrity requirements failed; preserve separate session and postcheck evidence')
        require(stage.get('failures') == [], 'Scientific stage has separately recorded failures')
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
    # A context-manager exit can fail after finalize_stage saved a complete
    # STAGE. Recover only exact existing bytes linked to SESSION; never invent
    # missing evidence or silently ignore a saved stage.
    for mode in result['stage_attempts'][len(result['stages']):]:
        saved = run / (mode + '_STAGE.json')
        if not os.path.lexists(saved):
            break
        try:
            saved_raw = bounded(saved)
            result['stages'].append(linked_stage(run, json.loads(saved_raw), mode))
        except Exception:
            result['status'] = 'STOPPED_WITHOUT_COMPLETED_REVIEW'
            result['reason'] = 'Saved stage linkage failed; preserve all independent evidence'
            result['unlinked_stage_receipts'].append({'path': saved.name,
                'exact_linkage_verified': False, 'no_missing_evidence_reconstructed': True})
            break
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
    # Preserve independent failure classes; a later local guard never erases the
    # session stop, even if no STAGE could be completed.
    result['primary_session_stops'] = primary_session_stops(observations)
    result['stage_failures'] = stage_failures(result['stages'])
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
        print('Inspection only. Prepared030 scope SHA256: ' + SCOPE_SHA256)
        print('Observed 10 starts / 7 sent turns exhaust the prior ceiling. Exact030 approval required for 12/9.')
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
