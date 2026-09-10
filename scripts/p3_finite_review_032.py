#!/usr/bin/env python3
"""One attended finite review with source-bound receipts and independent postchecks.

Prior 12 starts / 9 explicit turns remain counted. This published correction adds
at most 2 / 2 to cumulative ceilings 14 / 11 under standing user authorization.
No historical report is reconstructed and no partial operation is retried.
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

ROOT = Path(__file__).resolve().parents[1]
SCOPE_PATH = 'configs/P3_FINITE_REVIEW_SCOPE_032.json'
SCOPE_SHA256 = '5d7d307d3be0ccd4a6825895795578a4c94fc801377d4f115368bafb07cb20ac'
SOURCE_PINS = {
    'scripts/p3_finite_review_030.py': '1f8a61e9fb98dc15d0478a067950f46aa512d0ae3e900d649f6bb5eb71a3948a',
    'scripts/p3_review_interface_032.py': '565f408c25c7b6235b6b56e1493cc48b6a29aa06893d49b54afa61e8d72aef55',
    'scripts/p3_review_protocol_032.py': 'c51576b8fe48c396d804f92d01cd3f9bc9acf348a944506338c175f1813284f8',
    'scripts/p3_reviewer_session_032.py': 'bd287ae1b6361f01b83bf1b39c266c0c1d2ea27d34f34497ca7d26cf6917387b',
    'scripts/p3_receipt_collection_032.py': '52b88345b8d707891fc33d37cd7040ca356178f400cc1396db9282951937b552',
    'scripts/p3_packet_observer_032.py': '1c28b532d90c7a40b57c37e4ea33fc2639fe5375572a28e0a0732ce236cc2326',
}
RUN_NAME = 'P3_FINITE_REVIEW_032'
REPORT_KIND = 'P3_FINITE_REVIEW_032_v1'
SESSION_KIND = 'P3_FINITE_REVIEWER_SESSION_032_v1'
HISTORY_ROOT = ('artifacts/P3_REVIEW_030_RETURN/'
    '9c806f9b65f6765c446fe16fa9edb106516195765473d3b69c8197ad7b87d22f/files/delivery')
HISTORY_PINS = {
 'P3_FINITE_REVIEW_030/ATTEMPT.json': 'cefb5a068fe51d0bc07459ada4df0bb9a7a41aa2c8d4655bcd73bae78eaf1974',
 'P3_FINITE_REVIEW_030/AUTHORIZATION.md': '58e0dc94a91bc05109b68edfed9285154047d3f511102326c2f25475914cbbe1',
 'P3_FINITE_REVIEW_030/science_SESSION.json': '1059b733db491fc9e5aee64113784cb95620bab487f76346f91ec243000f0da9',
 'P3_FINITE_REVIEW_030/science_STAGE.json': '0911d75d736e9286d6b7600588051fa471c4f610ed24236253539155bc3490b7',
 'P3_FINITE_REVIEW_030/synthetic_SESSION.json': '2df312ff31a243ce548d2a0065665166097e0e335fbe6967f146f117e91709c6',
 'P3_FINITE_REVIEW_030/synthetic_STAGE.json': '31e607a40347176376604d97479997aee1a461e612ba60573aa33266574d6efc',
 'P3_FINITE_REVIEW_030_KERNEL_PREFLIGHT/ATTEMPT.json': '58b04b19d1233219d49136186c376456da6170b7575adb6d51ce352e57cca2aa',
 'P3_FINITE_REVIEW_030_KERNEL_PREFLIGHT/REPORT.json': '94fae5b5c1a7c73066060a5423ea8cd2a566a6d8221b41ff3a9fe13004c64a00',
 'P3_FINITE_REVIEW_030_KERNEL_PREFLIGHT/REPORT.sha256': '9e268be5459926774f3555afc910e7ba6750f64eb621481b94bab3b3fce64713',
}
BINDING = {'model': 'gpt-5.6-sol', 'id': 'gpt-5.6-sol', 'effort': 'max'}
TERMINAL = ('REVIEWER_OUTPUT_PRESERVED', 'STOPPED_WITHOUT_REVIEWER_VERDICT',
            'STOPPED_WITHOUT_COMPLETED_REVIEW', 'INTERRUPTED_PARTIAL_PRESERVED')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value, indent=2, ensure_ascii=True, allow_nan=False) + '\n').encode()


def _prior_controller():
    path = ROOT / 'scripts/p3_finite_review_030.py'
    cursor = Path(path.anchor)
    for part in path.parts[1:]:
        cursor /= part
        if cursor.is_symlink():
            raise RuntimeError('Symlink in historical controller path')
    info = path.stat()
    if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > 16 * 1024 * 1024 or
            sha(path.read_bytes()) != SOURCE_PINS['scripts/p3_finite_review_030.py']):
        raise RuntimeError('Historical030 controller changed')
    name = 'p3_finite_review_030'
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
Stop, require, bounded, plain = old.Stop, old.require, old.bounded, old.plain
module, exclusive_json, new_directory = old.module, old.exclusive_json, old.new_directory
synthetic_packet, PROMPTS = old.synthetic_packet, previous.PROMPTS
packet_preflight = previous.packet_preflight


def load_bundle():
    scope030, prior, inherited = previous.load_bundle()
    raw = bounded(ROOT / SCOPE_PATH)
    require(sha(raw) == SCOPE_SHA256, 'Unfinished032 scope pin')
    for path, digest in SOURCE_PINS.items():
        require(sha(bounded(ROOT / path, 16 * 1024 * 1024)) == digest, '032 dependency changed')
    scope = json.loads(raw)
    mutable = {'scope_id', 'approval_id', 'report_directory', 'purpose', 'approval_protocol',
        'prior_attempt_accounting', 'interface_correction', 'authorized_native_effects',
        'constraints', 'limitations', 'receipt_contract_correction', 'packet_postcheck_correction',
        'resource_lookup_correction', 'kernel_prerequisite_reuse',
        'deprecation_notice_policy','disabled_codemode_warning_policy',
        'native_lifecycle_correction','kernel_mount_prerequisite'}
    require(set(scope) == set(scope030) | {'receipt_contract_correction', 'packet_postcheck_correction',
        'resource_lookup_correction', 'kernel_prerequisite_reuse'}, '032 scope keys differ')
    require(all(scope.get(k) == v and type(scope.get(k)) is type(v)
                for k, v in scope030.items() if k not in mutable), '032 changed inherited controls')
    for key in ('deprecation_notice_policy','disabled_codemode_warning_policy','native_lifecycle_correction'):
        expected_policy = dict(scope030[key])
        expected_policy['session'] = 'scripts/p3_reviewer_session_032.py'
        require(canonical(scope[key]) == canonical(expected_policy), '032 changed inherited lifecycle or notice controls')
    expected_kernel_reference = dict(scope030['kernel_mount_prerequisite'])
    expected_kernel_reference.update(reference_only_previously_executed=True,new_executions_authorized=0)
    require(canonical(scope['kernel_mount_prerequisite']) == canonical(expected_kernel_reference),
        '032 kernel reference must not authorize a new probe')
    require(scope['scope_id'] == 'P3_FINITE_REVIEW_SCOPE_032' and
            scope['approval_id'] == 'APPROVE_P3_FINITE_REVIEW_032_CORRECTION' and
            scope['report_directory'] == 'delivery/' + RUN_NAME, '032 identity differs')
    expected = {'native_starts_observed': 12, 'explicit_model_turns_observed': 9,
        'additional_native_processes_maximum': 2, 'additional_explicit_model_turns_maximum': 2,
        'cumulative_native_starts_maximum': 14, 'cumulative_explicit_model_turns_maximum': 11,
        'no_automatic_retry': True, 'count_sent_turn_even_without_reviewer_output': True}
    counts = scope['prior_attempt_accounting']
    require(all(type(counts.get(k)) is type(v) and counts[k] == v for k, v in expected.items()),
            '032 cumulative accounting differs')
    interface = dict(scope030['interface_correction'])
    interface.update(wrapper='scripts/p3_review_interface_032.py',
        protocol='scripts/p3_review_protocol_032.py', session='scripts/p3_reviewer_session_032.py')
    require(scope['interface_correction'] == interface, '032 interface controls differ')
    expected_receipt = {'collector':'scripts/p3_receipt_collection_032.py',
        'emitter':'scripts/p3_reviewer_session_032.py', 'session_kind': SESSION_KIND,
        'malformed_receipts_preserved_as_per_file_errors':True,
        'missing_receipt_counts_remain_lower_bounds':True,
        'main_report_finalization_guarded':True, 'no_historical_report_reconstruction':True}
    expected_observer = {'implementation':'scripts/p3_packet_observer_032.py',
        'separate_observer_opened_before_model':True,
        'operative_broker_failure_does_not_skip_postcheck':True,'same_manifest_exact_bytes_required':True}
    expected_lookup = {'refused_paths_never_opened':True,
        'path_refusals_count_as_recoverable_input_errors':True,
        'integrity_failures_remain_terminal':True,'unchanged_error_budget':8,
        'ninth_error_terminal':True,'no_new_file_authority':True}
    expected_kernel = {'actual030_receipt_required':True,'actual_same_cache_source_required':True,
        'runtime_and_bwrap_pins_unchanged':True,'no_additional_kernel_probe':True}
    for key, value in (('receipt_contract_correction', expected_receipt),
                       ('packet_postcheck_correction', expected_observer),
                       ('resource_lookup_correction', expected_lookup),
                       ('kernel_prerequisite_reuse', expected_kernel)):
        require(canonical(scope[key]) == canonical(value), '032 correction contract differs')
    session = module('p3_reviewer_session_032')
    collector = module('p3_receipt_collection_032')
    require(session.SESSION_KIND == SESSION_KIND == collector.SESSION_KIND,
            'Session emitter and collector schema constants differ')
    for path, digest in HISTORY_PINS.items():
        require(sha(bounded(ROOT / HISTORY_ROOT / path, 16 * 1024 * 1024)) == digest,
                'Archived030 returned evidence differs')
    return scope, prior, {'scope_sha256': SCOPE_SHA256,
        'controller_sha256': sha(bounded(Path(__file__))), 'source_pins': SOURCE_PINS,
        'inherited030_pins': inherited, 'actual030_file_pins': HISTORY_PINS,
        'packet_manifest_sha256': scope['private_packet_manifest_sha256']}


def approval(scope, *, manual_launch=False):
    require(manual_launch is True, 'Explicit --run-attended-review is required')
    raw = bounded(ROOT / 'state/ESCALATION.md')
    text = raw.decode('utf-8')
    require('<!--' not in text and '-->' not in text, 'HTML comment ambiguity in approval')
    fence, positions, lines = None, [], text.splitlines()
    for i, line in enumerate(lines):
        start = line.lstrip(' ')
        if len(line) - len(start) <= 3 and start.startswith(('```', '~~~')):
            char = start[0]; length = len(start) - len(start.lstrip(char))
            if fence is None: fence = (char, length)
            elif char == fence[0] and length >= fence[1] and not start[length:].strip(): fence = None
            continue
        if fence is None and line == '## ANSWER': positions.append(i)
    require(len(positions) == 1, 'Exactly one actual032 standing authorization record is required')
    require([line for line in lines[positions[0] + 1:] if line.strip()] ==
        ['APPROVE_P3_FINITE_REVIEW_032_CORRECTION', 'scope_sha256: ' + SCOPE_SHA256],
        'Recorded standing authorization differs from exact032 scope')
    return {'path':'state/ESCALATION.md', 'sha256':sha(raw)}


def prior_history(pins):
    inherited = pins['inherited030_pins']
    earlier = previous.prior_history(inherited)
    for relative, digest in HISTORY_PINS.items():
        archived = bounded(ROOT / HISTORY_ROOT / relative, 16 * 1024 * 1024)
        actual = bounded(ROOT / 'delivery' / relative, 16 * 1024 * 1024)
        require(sha(archived) == digest and actual == archived,
                'Actual030 separate evidence differs; never reconstruct missing receipts')
    run = ROOT / 'delivery' / previous.RUN_NAME
    require(not os.path.lexists(run / 'REPORT.json'),
            'Unexpected030 main REPORT exists; preserve it for inspection without a new reservation')
    require(not os.path.lexists(run / 'science_output/REVIEW_VERDICT.json'),
            'Unexpected030 verdict exists; preserve it before any new operation')
    attempt = json.loads(bounded(run / 'ATTEMPT.json'))
    require(attempt.get('pins') == inherited and
            type(attempt.get('reserved_native_starts')) is int and attempt['reserved_native_starts'] == 2 and
            type(attempt.get('reserved_turns')) is int and attempt['reserved_turns'] == 2 and
            attempt.get('automatic_retry') is False and attempt.get('science_conditioned_on_synthetic') is True,
            'Actual030 reservation differs')
    authorization = attempt.get('authorization', {})
    require(authorization.get('path') == 'state/ESCALATION.md' and
            authorization.get('sha256') == sha(bounded(run / 'AUTHORIZATION.md')),
            'Actual030 original authorization differs')
    sessions = {}
    stages = {}
    for mode in ('synthetic', 'science'):
        raw = bounded(run / (mode + '_SESSION.json'))
        observation = json.loads(raw)
        require(observation.get('kind') == 'P3_FINITE_REVIEWER_SESSION_030_OFFLINE_PROPOSAL_v1' and
            observation.get('mode') == mode and
            all(observation.get(k) is True for k in ('client_started','model_turn_request_sent','native_process_reaped')) and
            observation.get('verdict_submitted') is False,
            'Actual030 emitted session or measured counts differ')
        stage = json.loads(bounded(run / (mode + '_STAGE.json')))
        require(stage.get('stage') == mode and canonical(stage.get('observation')) == raw,
                'Actual030 original stage/session linkage differs')
        sessions[mode], stages[mode] = observation, stage
    require(previous.admitted_synthetic(stages['synthetic']), 'Historical030 synthetic outcome differs')
    science = sessions['science']
    require(science.get('status') == 'STOPPED_WITHOUT_VERDICT' and
        science.get('broker_boundary_failure') == {'layer':'dispatch','code':'boundary.resource_path',
            'tool':'read_page_image','raw_input_path_or_exception_saved':False} and
        stages['science'].get('packet_after') is None and
        stages['science'].get('host_checks',{}).get('all_noncredential_checks_pass') is True,
        'Historical030 failed science differs; never retroactively admit it')
    kernel = previous.verify_kernel_preflight_receipt(attempt.get('sealed_cache_kernel_preflight'),
        run=run, pins=inherited, authorization=authorization)
    return {'earlier_history':earlier, 'actual030_files_reverified':HISTORY_PINS,
        'actual030_main_report_missing':True,'historical030_main_report_reconstructed':False,
        'historical030_emitter_kind_mismatch_preserved':True,'historical030_science_admitted':False,
        'separate030_sessions_counted':True,'prior_native_starts':12,'prior_sent_turns':9,
        'previous_cumulative_native_ceiling':12,'previous_cumulative_sent_turn_ceiling':9,
        'new_cumulative_native_ceiling':14,'new_cumulative_sent_turn_ceiling':11,
        'kernel_prerequisite_reused_from_actual030':kernel,'new_kernel_probe_performed':False,
        'counters_reset':False}


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
    broker_module = module('p3_review_interface_032')
    session = module('p3_reviewer_session_032')
    cache = module('p3_cache_inputs_030')
    observer_module = module('p3_packet_observer_032')
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
    plan.update({'kind': 'P3_FINITE_REVIEW_NATIVE_MOUNT_PLAN_032_v1',
                 'native_operation_scope_sha256': SCOPE_SHA256,
                 'full_reviewer_boundary_verified': False})
    prompt = bounded(ROOT / PROMPTS[mode], 64000).decode('utf-8')
    observer_output = new_directory(run / (mode + '_packet_observer'))
    with observer_module.PacketObserver(packet, manifest_sha256=manifest_sha,
            output_root=observer_output) as observer:
        with cache.capture_cache_inputs(facts['codex_home'], auth_metadata=facts['auth_before']) as cache_inputs:
            cache_inputs.verify_origins(facts['cache_origins'])
            plan = cache_inputs.apply_to_plan(plan)
            with broker_module.ReviewBroker(packet, manifest_sha256=manifest_sha, output_root=output) as broker:
                before_inputs = broker.verify_inputs()
                require(before_inputs == observer.before, 'Independent packet observer differs before model')
                base = {'mount_plan': cache_inputs.report_plan(plan),
                        'credential_metadata_before': facts['auth_before'],
                        'config_origins': facts['origins'], 'cache_origins': facts['cache_origins'],
                        'cache_inputs_before': cache_inputs.receipt(), 'packet_before': before_inputs,
                        'fresh_process_and_runtime_directories': True, 'pi_conversation_imported': False,
                        'independent_packet_observer_opened_before_model': True,
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
                    # The dedicated reader was opened before the model and has
                    # never dispatched a tool. Operative broker failure cannot
                    # disable this independent exact-byte postcheck.
                    return observer.verify()
                def write_stage_receipt(path, value):
                    if path.name == mode + '_STAGE.json':
                        if value.get('packet_after') != before_inputs:
                            failure = {'phase':'packet','code':'independent_packet_postcheck_failed'}
                            if failure not in value['failures']: value['failures'].append(failure)
                    return exclusive_json(path, value)
                return evidence.finalize_stage(run, mode, observation,
                    host_checks_call=lambda: evidence.collect_postchecks(
                        facts, metadata, preflight, identity, cache_inputs),
                    packet_check_call=packet_after, base_fields=base, write_json=write_stage_receipt)



def synthetic_recovery_admitted(observation):
    receipts = observation.get('broker_receipts')
    return (observation.get('synthetic_argument_error_observed') is True and
        type(observation.get('recoverable_input_errors')) is int and observation['recoverable_input_errors'] == 2 and
        type(observation.get('failed_broker_calls')) is int and observation['failed_broker_calls'] == 2 and
        observation.get('broker_boundary_failure') is None and
        type(receipts) is list and len(receipts) == 3 and
        all(type(r) is dict and r.get('method') == 'item/tool/call' and r.get('tool') == 'read_text'
            for r in receipts) and
        [(r.get('successful'), r.get('error_code')) for r in receipts] ==
            [(False,'integer_bounds'),(True,None),(False,'resource_path_traversal')])


def packet_admitted(stage):
    before, after = stage.get('packet_before'), stage.get('packet_after')
    return (stage.get('independent_packet_observer_opened_before_model') is True and
        type(before) is dict and set(before) == {'manifest_sha256','files_rehashed'} and
        type(before.get('files_rehashed')) is int and before['files_rehashed'] > 0 and
        type(before.get('manifest_sha256')) is str and len(before['manifest_sha256']) == 64 and
        after == before)


def admitted_synthetic(stage):
    if type(stage) is not dict: return False
    observation = stage.get('observation', {})
    if type(observation) is not dict or type(stage.get('host_checks')) is not dict: return False
    return (stage.get('stage') == 'synthetic' and
        stage['host_checks'].get('all_noncredential_checks_pass') is True and stage.get('failures') == [] and
        stage.get('fresh_process_and_runtime_directories') is True and stage.get('pi_conversation_imported') is False and
        observation.get('kind') == SESSION_KIND and observation.get('status') == 'SYNTHETIC_REFUSAL_OBSERVED' and
        observation.get('selected_binding') == BINDING and observation.get('cache_input_descriptors_verified') is True and
        observation.get('verdict_submitted') is False and synthetic_recovery_admitted(observation) and
        packet_admitted(stage) and all(observation.get(k) is True for k in
            ('synthetic_allowed_read_observed','observed_refusal','native_process_reaped','client_started','model_turn_request_sent')))


def admitted_science(stage):
    if type(stage) is not dict: return False
    observation = stage.get('observation', {})
    if type(observation) is not dict or type(stage.get('host_checks')) is not dict: return False
    return (stage.get('stage') == 'science' and
        stage['host_checks'].get('all_noncredential_checks_pass') is True and stage.get('failures') == [] and
        stage.get('fresh_process_and_runtime_directories') is True and stage.get('pi_conversation_imported') is False and
        observation.get('kind') == SESSION_KIND and observation.get('selected_binding') == BINDING and
        observation.get('cache_input_descriptors_verified') is True and
        observation.get('status') == 'VERDICT_SUBMITTED' and packet_admitted(stage) and
        all(observation.get(k) is True for k in ('verdict_submitted','native_process_reaped','client_started','model_turn_request_sent')))


def linked_stage(run, stage, mode):
    require(type(stage) is dict and stage.get('stage') == mode and
        canonical(stage.get('observation')) == bounded(run / (mode + '_SESSION.json')),
        'Stage differs from separately preserved original SESSION')
    require(canonical(stage) == bounded(run / (mode + '_STAGE.json')),
        'Stage differs from separately preserved original STAGE')
    return stage


def collect_receipts(run, attempted_modes):
    """No receipt parser or emitter contract failure may suppress main REPORT."""
    try:
        result = module('p3_receipt_collection_032').collect(run,
            emitter_path=ROOT / 'scripts/p3_reviewer_session_032.py',
            emitter_sha256=SOURCE_PINS['scripts/p3_reviewer_session_032.py'],
            expected_kind=SESSION_KIND, expected_modes=tuple(attempted_modes))
        require(type(result) is dict and type(result.get('observations')) is dict and
            type(result.get('stages')) is dict and type(result.get('files')) is list and
            type(result.get('errors')) is list, 'Receipt collector result shape differs')
        return result
    except Exception:
        return {'kind':'P3_SOURCE_BOUND_RECEIPT_COLLECTION_032_v1',
            'observations':{},'stages':{},'files':[],
            'errors':[{'phase':'collection','code':'guarded_collection_failed','file':None}],
            'source_binding_verified':False,'complete':False,
            'eligible_for_controller_admission_checks':False,
            'execution_admission_evaluated':False,'missing_receipts_reconstructed':False}


def accounting(observations, attempted_modes):
    starts = sum(int(o['client_started']) for o in observations.values())
    turns = sum(int(o['model_turn_request_sent']) for o in observations.values())
    return {'prior_native_starts':12,'prior_sent_turns':9,
        'observed_native_starts_this_attempt':starts,'observed_sent_turns_this_attempt':turns,
        'cumulative_observed_native_starts':12 + starts,'cumulative_observed_sent_turns':9 + turns,
        'reserved_native_starts_this_attempt':2,'reserved_turns_this_attempt':2,
        'cumulative_native_ceiling':14,'cumulative_sent_turn_ceiling':11,
        'maximum_cumulative_reservation_native_starts':14,'maximum_cumulative_reservation_turns':11,
        'missing_session_counts_are_only_minimum_observations':
            any(mode not in observations for mode in attempted_modes),
        'sent_turn_counts_without_output':True,'backend_usage_or_charge':'unknown',
        'unobserved_reserved_capacity_is_not_automatically_released':True,'no_counter_reset':True}


def failure_summaries(collection):
    primary, failures = [], []
    for mode, observation in collection['observations'].items():
        if observation.get('status') not in ('SYNTHETIC_REFUSAL_OBSERVED','VERDICT_SUBMITTED'):
            primary.append({'stage':mode,
                'reason':observation.get('primary_failure',observation.get('reason'))})
    for mode, stage in collection['stages'].items():
        entries = stage.get('failures')
        if type(entries) is not list:
            failures.append({'stage':mode,'phase':'summary','code':'stage_failure_list_malformed'})
            continue
        for entry in entries:
            if type(entry) is dict and type(entry.get('phase')) is str and type(entry.get('code')) is str:
                failures.append({'stage':mode,'phase':entry['phase'],'code':entry['code']})
            else:
                failures.append({'stage':mode,'phase':'summary','code':'stage_failure_entry_malformed'})
    return primary, failures


def finalize_report(run, result):
    """Persist a terminal main report even when receipt collection is malformed.

    Physical failure to write the report still raises: no claim that unwritten
    evidence was saved. Already written SESSION/STAGE/verdict bytes are untouched.
    """
    collection = collect_receipts(run, result['stage_attempts'])
    result['receipt_collection'] = collection
    result['stages'] = [collection['stages'][mode] for mode in result['stage_attempts']
                        if mode in collection['stages']]
    result['preserved_session_receipts'] = [item for item in collection['files']
        if type(item) is dict and str(item.get('path','')).endswith('_SESSION.json')]
    try:
        result['primary_session_stops'], result['stage_failures'] = failure_summaries(collection)
        result['attempt_accounting'] = accounting(collection['observations'], result['stage_attempts'])
    except Exception:
        result['primary_session_stops'], result['stage_failures'] = [], [
            {'phase':'summary','code':'guarded_failure_or_count_summary_failed'}]
        result['attempt_accounting'] = accounting({}, result['stage_attempts'])
        collection['errors'].append({'phase':'summary','code':'guarded_summary_failed','file':None})
        collection['eligible_for_controller_admission_checks'] = False
    if collection.get('eligible_for_controller_admission_checks') is not True:
        result['status'] = 'STOPPED_WITHOUT_COMPLETED_REVIEW'
        result.setdefault('reason','Original receipt collection is incomplete or refused; preserve per-file evidence')
    if result['status'] == 'REVIEWER_OUTPUT_PRESERVED':
        try:
            require(result['stage_attempts'] == ['synthetic','science'] and
                admitted_synthetic(collection['stages'].get('synthetic')) and
                admitted_science(collection['stages'].get('science')),
                'Final source-bound receipts do not establish admission')
        except Exception:
            result['status'] = 'STOPPED_WITHOUT_COMPLETED_REVIEW'
            result.setdefault('reason','Final source-bound receipt admission failed')
    output = run / 'science_output/REVIEW_VERDICT.json'
    result['reviewer_output'] = None
    if os.path.lexists(output):
        try:
            raw = bounded(output, 1024 * 1024)
            result['reviewer_output'] = {'path':'science_output/REVIEW_VERDICT.json',
                'sha256':sha(raw),'bytes':len(raw),'parent_edited':False,
                'execution_admitted':result['status'] == 'REVIEWER_OUTPUT_PRESERVED'}
        except Exception:
            result['status'] = 'STOPPED_WITHOUT_COMPLETED_REVIEW'
            result.setdefault('reason','Reviewer output protected inspection failed; original bytes preserved')
            result['output_collection_error'] = 'protected_output_read_failed'
    elif result['status'] == 'REVIEWER_OUTPUT_PRESERVED':
        result['status'] = 'STOPPED_WITHOUT_COMPLETED_REVIEW'
        result.setdefault('reason','Admitted status lacks submitted reviewer output')
    raw = exclusive_json(run / 'REPORT.json', result)
    with (run / 'REPORT.sha256').open('x') as handle:
        handle.write(sha(raw) + '\n'); handle.flush(); os.fsync(handle.fileno())
    return run / 'REPORT.json'


def execute(scope, prior_scope, pins, authorization, packet_info):
    history = prior_history(pins)
    preflight_receipt = packet_preflight(ROOT, packet_info)
    approval_raw = bounded(ROOT / authorization['path'])
    require(sha(approval_raw) == authorization['sha256'], 'Authorization changed before reservation')
    run = new_directory(ROOT / 'delivery' / RUN_NAME)
    with (run / 'AUTHORIZATION.md').open('xb') as handle:
        handle.write(approval_raw); handle.flush(); os.fsync(handle.fileno())
    exclusive_json(run / 'ATTEMPT.json', {'created_utc':datetime.now(timezone.utc).isoformat(),
        'pins':pins,'authorization':authorization,'reserved_native_starts':2,'reserved_turns':2,
        'automatic_retry':False,'science_conditioned_on_synthetic':True,
        'actual030_kernel_reference':history['kernel_prerequisite_reused_from_actual030']})
    result = {'kind':REPORT_KIND,'created_utc':datetime.now(timezone.utc).isoformat(),
        'pins':pins,'authorization':authorization,'history':history,
        'private_packet_preflight':preflight_receipt,'status':'STARTED','stages':[],
        'stage_attempts':[],'science_started':False,'reviewer_output':None,
        'parent_credential_contents_read':False,'unattended_model_use_authorized':False,
        'continuous_human_attendance_verified':False,'scientific_verdict_chosen_by_parent':False,
        'automatic_retry_requested':False,'raw_native_logs_or_protocol_in_report':False}
    try:
        packet, manifest = synthetic_packet(run)
        result['stage_attempts'].append('synthetic')
        stage = run_stage(scope, prior_scope, run, 'synthetic', packet, manifest)
        linked_stage(run, stage, 'synthetic')
        require(admitted_synthetic(stage), 'Synthetic admission incomplete; no science started')
        collection = collect_receipts(run, ['synthetic'])
        require(collection.get('eligible_for_controller_admission_checks') is True,
            'Source-bound synthetic receipt collection failed; no science started')
        refreshed = load_bundle()
        require(refreshed == (scope,prior_scope,pins), 'Frozen dependencies changed before science')
        ready = module('install_p3_review_packet').verify_packet(ROOT)
        require(ready == packet_info and ready['manifest_sha256'] == pins['packet_manifest_sha256'],
            'Private packet changed before science')
        result['stage_attempts'].append('science')
        result['science_started'] = True
        stage = run_stage(scope, prior_scope, run, 'science', Path(ready['packet_path']),
            ready['manifest_sha256'], expected_binding=BINDING.copy())
        linked_stage(run, stage, 'science')
        require(admitted_science(stage), 'Scientific session or independent integrity admission incomplete')
        result['status'] = ('REVIEWER_OUTPUT_PRESERVED' if
            os.path.lexists(run / 'science_output/REVIEW_VERDICT.json') else 'STOPPED_WITHOUT_REVIEWER_VERDICT')
    except KeyboardInterrupt:
        result['status'] = 'INTERRUPTED_PARTIAL_PRESERVED'
        result['reason'] = 'Human interruption; no automatic retry'
    except Exception as error:
        result['status'] = 'STOPPED_WITHOUT_COMPLETED_REVIEW'
        result['reason'] = str(error) if type(error) is Stop else 'Guarded local stage stopped; preserve original receipts'
    return finalize_report(run,result)

def existing(run, pins):
    if not os.path.lexists(run): return None
    plain(run, True)
    raw = bounded(run / 'REPORT.json', 16 * 1024 * 1024)
    require(bounded(run / 'REPORT.sha256',65) == (sha(raw)+'\n').encode(),
            'Existing032 report checksum differs; preserve it')
    value = json.loads(raw)
    require(value.get('kind') == REPORT_KIND and value.get('pins') == pins and
        value.get('status') in TERMINAL and value.get('parent_credential_contents_read') is False and
        value.get('unattended_model_use_authorized') is False and
        value.get('scientific_verdict_chosen_by_parent') is False and
        value.get('automatic_retry_requested') is False, 'Existing032 provenance or terminal state differs')
    requested = value.get('stage_attempts')
    require(requested in ([],['synthetic'],['synthetic','science']), 'Existing032 stage order differs')
    require(value.get('science_started') is ('science' in requested), 'Existing032 science declaration differs')
    authorization = value.get('authorization')
    require(type(authorization) is dict and set(authorization) == {'path','sha256'} and
        authorization['path'] == 'state/ESCALATION.md' and
        authorization['sha256'] == sha(bounded(run / 'AUTHORIZATION.md')),
        'Existing032 preserved authorization differs')
    attempt = json.loads(bounded(run / 'ATTEMPT.json'))
    require(attempt.get('pins') == pins and attempt.get('authorization') == authorization and
        type(attempt.get('reserved_native_starts')) is int and attempt['reserved_native_starts'] == 2 and
        type(attempt.get('reserved_turns')) is int and attempt['reserved_turns'] == 2 and
        attempt.get('automatic_retry') is False and attempt.get('science_conditioned_on_synthetic') is True and
        attempt.get('actual030_kernel_reference') == value.get('history',{}).get('kernel_prerequisite_reused_from_actual030'),
        'Existing032 original reservation differs')
    collection = collect_receipts(run, requested)
    require(value.get('receipt_collection') == collection, 'Existing032 source-bound receipt inventory differs')
    require(value.get('stages') == [collection['stages'][m] for m in requested if m in collection['stages']],
        'Existing032 separate stage inventory differs')
    require(value.get('preserved_session_receipts') == [i for i in collection['files']
        if type(i) is dict and str(i.get('path','')).endswith('_SESSION.json')],
        'Existing032 original session references differ')
    primary, failures = failure_summaries(collection)
    require(value.get('primary_session_stops') == primary and value.get('stage_failures') == failures,
        'Existing032 independent failure summary differs')
    expected = accounting(collection['observations'],requested)
    require(canonical(value.get('attempt_accounting')) == canonical(expected),
        'Existing032 accounting differs from source-bound original sessions')
    if 'science' in requested:
        require(admitted_synthetic(collection['stages'].get('synthetic')),
            'Existing032 science lacks separately observed synthetic admission')
    else:
        require(not any(os.path.lexists(run / p) for p in ('science_native','science_output',
                'science_packet_observer','science_SESSION.json','science_STAGE.json')),
            'Existing032 unrequested scientific stage exists')
    output = value.get('reviewer_output')
    output_path = run / 'science_output/REVIEW_VERDICT.json'
    if output is None:
        require(value.get('status') != 'REVIEWER_OUTPUT_PRESERVED', 'Completed status lacks original reviewer output')
        require(not os.path.lexists(output_path) or value.get('output_collection_error') == 'protected_output_read_failed',
            'Existing032 unrecorded reviewer output exists')
    else:
        require(type(output) is dict and output.get('path') == 'science_output/REVIEW_VERDICT.json' and
            output.get('parent_edited') is False and
            output.get('execution_admitted') is (value['status'] == 'REVIEWER_OUTPUT_PRESERVED'),
            'Existing032 output provenance differs')
        output_raw = bounded(output_path,1024*1024)
        require(sha(output_raw) == output.get('sha256') and type(output.get('bytes')) is int and
            len(output_raw) == output['bytes'], 'Existing032 output bytes differ')
    if value['status'] == 'REVIEWER_OUTPUT_PRESERVED':
        require(collection.get('eligible_for_controller_admission_checks') is True and
            requested == ['synthetic','science'] and admitted_synthetic(collection['stages'].get('synthetic')) and
            admitted_science(collection['stages'].get('science')), 'Existing032 completion lacks complete stage admission')
    return run / 'REPORT.json'


def print_receipt(path):
    value = json.loads(bounded(path,16*1024*1024))
    require(value.get('status') in TERMINAL, 'Receipt status is not terminal')
    print('STATUS: '+value['status'])
    print('REPORT: '+str(path))
    print('REPORT_SHA256: '+sha(bounded(path,16*1024*1024)))
    if value.get('reviewer_output') is not None:
        print('REVIEW_VERDICT: '+str(path.parent / value['reviewer_output']['path']))
    else:
        print('No scientific verdict was submitted. The publication workflow collects the report and original receipts.')


def safe_stop_message(error):
    return str(error) if type(error) is Stop else (
        'Protected history, authorization, dependency or receipt check failed; existing work preserved.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-attended-review',action='store_true')
    args = parser.parse_args()
    scope, prior, pins = load_bundle()
    cached = existing(ROOT / 'delivery' / RUN_NAME,pins)
    if cached:
        print('VERIFIED TERMINAL RECEIPT; REUSED without a native process or new turn.')
        print_receipt(cached)
        return 0
    if not args.run_attended_review:
        print('Inspection only. Prepared032 scope SHA256: '+SCOPE_SHA256)
        print('Observed12starts/9sentturns remain counted. Additional maximum2/2 gives cumulative14/11.')
        print('Existing standing authorization plus the explicit attended command is required; no automatic retry.')
        return 0
    old.canonical_host(scope)
    authorization = approval(scope,manual_launch=True)
    packet_info = module('install_p3_review_packet').verify_packet(ROOT)
    require(packet_info['manifest_sha256'] == scope['private_packet_manifest_sha256'],'Wrong private evidence packet')
    path = execute(scope,prior,pins,authorization,packet_info)
    print_receipt(path)
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (Stop,OSError,ValueError,KeyError,TypeError) as error:
        print('STOP: '+safe_stop_message(error))
        raise SystemExit(1)
