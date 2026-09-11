#!/usr/bin/env python3
"""Checkpoint039: one finite attended source-aware second-audit review.

Fresh synthetic admission precedes a distinct scientific process/thread. The
native transport, runtime/profile restrictions and protected host inputs retain
032 semantics. Only the analytical packet, broker/schema and accounting scope
change. No native retries, old approval reconstruction or candidate treatment.
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
SCOPE_PATH = 'configs/P3_FOCUSED_REVIEW_SCOPE_039.json'
SCOPE_SHA256 = 'fa94aee5482afa11f1a638ccf4759f630839cb38afaa25812746a81f428e7fd2'
RUN_NAME = 'P3_FOCUSED_REVIEW_039'
REPORT_KIND = 'P3_FOCUSED_REVIEW_039_v1'
SESSION_KIND = 'P3_FINITE_REVIEWER_SESSION_039_v1'
BINDING = {'model': 'gpt-5.6-sol', 'id': 'gpt-5.6-sol', 'effort': 'max'}
PROMPTS = {'synthetic':'configs/P3_SYNTHETIC_PROMPT_028.txt',
           'science':'configs/P3_FOCUSED_REVIEW_PROMPT_039.txt'}
SOURCE_PINS = {}
TERMINAL = ('REVIEWER_OUTPUT_PRESERVED', 'STOPPED_WITHOUT_REVIEWER_VERDICT',
            'STOPPED_WITHOUT_COMPLETED_REVIEW', 'INTERRUPTED_PARTIAL_PRESERVED')

class Stop(RuntimeError):
    """Fixed local reason only, safe to include in the public execution report."""

def require(condition, reason):
    if not condition:
        raise Stop(reason)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def canonical(value):
    return (json.dumps(value, indent=2, ensure_ascii=True, allow_nan=False) + '\n').encode()

def plain(path, directory=False):
    path = Path(path).absolute()
    require('..' not in path.parts, 'Noncanonical protected path')
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        require(not current.is_symlink(), 'Symlink in protected path')
    info = path.stat()
    require(stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode),
            'Protected path type differs')
    require(directory or info.st_nlink == 1, 'Hardlinked protected file refused')
    return path

def bounded(path, maximum=16 * 1024 * 1024):
    path = plain(path)
    before = path.stat()
    require(before.st_size <= maximum, 'Protected file exceeds byte ceiling')
    with path.open('rb') as handle:
        opened = os.fstat(handle.fileno())
        raw = handle.read(maximum + 1)
        after = os.fstat(handle.fileno())
    signature = lambda i: (i.st_dev, i.st_ino, i.st_mode, i.st_uid, i.st_nlink, i.st_size, i.st_mtime_ns, i.st_ctime_ns)
    require(signature(before) == signature(opened) == signature(after) == signature(path.stat()) and len(raw) == before.st_size,
            'Protected file changed during inspection')
    return raw

def module(name):
    path = ROOT / 'scripts' / (name + '.py')
    require('scripts/' + name + '.py' in SOURCE_PINS, 'Unpinned imported module')
    require(sha(bounded(path)) == SOURCE_PINS['scripts/' + name + '.py'],
            'Imported module differs from scope')
    existing = sys.modules.get(name)
    if existing is not None:
        require(Path(existing.__file__).resolve() == path, 'Conflicting imported module origin')
        return existing
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value

def exclusive_json(path, value):
    raw = canonical(value)
    with Path(path).open('xb') as handle:
        handle.write(raw); handle.flush(); os.fsync(handle.fileno())
    return raw

def new_directory(path):
    path = Path(path)
    plain(path.parent, True)
    path.mkdir(mode=0o700)
    return plain(path, True)

def synthetic_packet(run):
    packet = new_directory(run / 'synthetic_packet')
    raw = b'Synthetic canary; no research or user data.\n'
    with (packet / 'CANARY.txt').open('xb') as handle:
        handle.write(raw)
    manifest = {'schema_version':1, 'files':[{'path':'CANARY.txt','kind':'text','sha256':sha(raw)}]}
    digest = sha(exclusive_json(packet / 'BROKER_MANIFEST.json', manifest))
    return packet, digest

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
    broker_module = module('p3_focused_review_broker_039')
    session = module('p3_reviewer_session_039')
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
    plan.update({'kind': 'P3_FOCUSED_REVIEW_NATIVE_MOUNT_PLAN_039_v1',
                 'native_operation_scope_sha256': SCOPE_SHA256,
                 'full_reviewer_boundary_verified': False})
    prompt = bounded(ROOT / PROMPTS[mode], 64000).decode('utf-8')
    observer_output = new_directory(run / (mode + '_packet_observer'))
    with observer_module.PacketObserver(packet, manifest_sha256=manifest_sha,
            output_root=observer_output) as observer:
        with cache.capture_cache_inputs(facts['codex_home'], auth_metadata=facts['auth_before']) as cache_inputs:
            cache_inputs.verify_origins(facts['cache_origins'])
            plan = cache_inputs.apply_to_plan(plan)
            with broker_module.ReviewBroker(packet, manifest_sha256=manifest_sha, output_root=output, synthetic=(mode == 'synthetic')) as broker:
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
                try:
                    base['source_delivery_after'] = broker.source_access_receipt()
                except Exception:
                    base['source_delivery_after'] = {'status':'UNAVAILABLE_AFTER_STAGE',
                        'raw_source_text_or_exception_saved':False}
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
            emitter_path=ROOT / 'scripts/p3_reviewer_session_039.py',
            emitter_sha256=SOURCE_PINS['scripts/p3_reviewer_session_039.py'],
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
    return {'prior_native_starts':14,'prior_sent_turns':11,
        'observed_native_starts_this_attempt':starts,'observed_sent_turns_this_attempt':turns,
        'cumulative_observed_native_starts':14 + starts,'cumulative_observed_sent_turns':11 + turns,
        'reserved_native_starts_this_attempt':2,'reserved_turns_this_attempt':2,
        'cumulative_native_ceiling':16,'cumulative_sent_turn_ceiling':13,
        'maximum_cumulative_reservation_native_starts':16,'maximum_cumulative_reservation_turns':13,
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


def load_bundle():
    global SOURCE_PINS
    raw = bounded(ROOT / SCOPE_PATH)
    require(sha(raw) == SCOPE_SHA256, '039 scope differs from sealed release')
    scope = json.loads(raw)
    require(scope.get('scope_id') == 'P3_FOCUSED_REVIEW_SCOPE_039' and
            scope.get('report_directory') == 'delivery/' + RUN_NAME,
            '039 scope identity differs')
    sources = scope.get('source_pins')
    require(type(sources) is dict and len(sources) >= 20, 'Incomplete039 source closure')
    for name, digest in sources.items():
        require(type(name) is str and not name.startswith('/') and
                all(part not in ('', '.', '..') for part in name.split('/')) and
                type(digest) is str and len(digest) == 64,
                'Invalid sealed source entry')
        require(sha(bounded(ROOT / name)) == digest, '039 source dependency changed')
    SOURCE_PINS = sources.copy()
    baseline = json.loads(bounded(ROOT / scope['native_baseline_scope']['path']))
    require(sha(bounded(ROOT / scope['native_baseline_scope']['path'])) ==
            scope['native_baseline_scope']['sha256'], 'Native baseline scope changed')
    fixed = ('canonical_home', 'canonical_project', 'runtime_sha256', 'bwrap_sha256',
             'synthetic_seconds_including_cleanup', 'scientific_seconds_including_cleanup',
             'maximum_synthetic_broker_calls', 'maximum_scientific_broker_calls', 'model_policy')
    require(all(canonical(scope.get(k)) == canonical(baseline[k]) for k in fixed),
            '039 altered unchanged native controls')
    counts = {'native_starts_observed':14,'explicit_model_turns_observed':11,
              'additional_native_processes_maximum':2,'additional_explicit_model_turns_maximum':2,
              'cumulative_native_starts_maximum':16,'cumulative_explicit_model_turns_maximum':13,
              'no_automatic_retry':True,'count_sent_turn_even_without_reviewer_output':True}
    require(canonical(scope.get('prior_attempt_accounting')) == canonical(counts),
            '039 cumulative accounting differs')
    prior_raw = bounded(ROOT / scope['prior_native_scope']['path'])
    require(sha(prior_raw) == scope['prior_native_scope']['sha256'], 'Native host baseline differs')
    require(scope['private_packet_directory'] == 'delivery/P3_FOCUSED_REVIEW_PACKET_039',
            'Private packet location differs')
    require(scope['scientific_manifest']['path'] == 'evidence/P3_FOCUSED_REVIEW_MANIFEST_038.json' and
            sha(bounded(ROOT / scope['scientific_manifest']['path'])) == scope['scientific_manifest']['sha256'],
            'Scientific038 manifest changed')
    auth = scope['authorization']
    require(auth['path'] == 'state/authorizations/P3_FOCUSED_REVIEW_039_STANDING_AUTHORIZATION.md' and
            sha(bounded(ROOT / auth['path'])) == auth['sha256'], 'Standing authorization record changed')
    return scope, json.loads(prior_raw), {'scope_sha256':SCOPE_SHA256,
        'controller_sha256':sha(bounded(Path(__file__))), 'source_pins':sources.copy(),
        'packet_manifest_sha256':scope['private_packet_manifest_sha256'],
        'scientific_manifest_sha256':scope['scientific_manifest']['sha256']}


def prior_history(scope):
    records = {}
    for name, row in scope['historical_evidence'].items():
        archived = bounded(ROOT / row['path'])
        require(sha(archived) == row['sha256'], 'Historical public evidence changed')
        if 'actual_path' in row:
            actual = bounded(ROOT / row['actual_path'])
            require(actual == archived, 'Actual prior execution receipt differs; preserve and stop')
        records[name] = json.loads(archived)
    review = records['review032']
    counts = review.get('attempt_accounting', {})
    require(review.get('status') == 'REVIEWER_OUTPUT_PRESERVED' and
            counts.get('cumulative_observed_native_starts') == 14 and
            counts.get('cumulative_observed_sent_turns') == 11 and
            counts.get('missing_session_counts_are_only_minimum_observations') is False,
            'Prior032 native accounting lacks exact evidence')
    for mode in ('synthetic', 'science'):
        session = records[mode + '032']
        require(session.get('kind') == 'P3_FINITE_REVIEWER_SESSION_032_v1' and
                session.get('mode') == mode and all(session.get(k) is True for k in
                ('client_started','model_turn_request_sent','native_process_reaped')),
                'Prior032 original session differs')
    kernel = records['kernel030']['observation']
    require(kernel.get('status') == 'PASSED' and kernel.get('kernel_child_mount_verified') is True and
            kernel.get('synthetic_only') is True and kernel.get('real_cache_or_credential_contents_accessed') is False and
            kernel.get('native_clients_started') == 0 and kernel.get('model_turns_sent') == 0 and
            all(v is True for v in kernel.get('checks',{}).values()) and len(kernel.get('checks',{})) == 6,
            'Historical sealed-cache kernel prerequisite not established')
    return {'prior_native_starts':14,'prior_sent_turns':11,
            'actual032_original_receipts_reverified':True,
            'historical_evidence':scope['historical_evidence'],
            'new_kernel_probe_performed':False,'counters_reset':False,
            'historical_first_review_verdict_reused_for_second_review':False}


def packet_preflight(scope, packet):
    import tempfile
    require(Path(packet).absolute() == ROOT / scope['private_packet_directory'],
            'Packet must use the sealed canonical delivery location')
    packet = plain(packet, True)
    with tempfile.TemporaryDirectory(prefix='P3_039_packet_check_', dir=ROOT / 'delivery') as tmp:
        with module('p3_focused_review_broker_039').ReviewBroker(packet,
                manifest_sha256=scope['private_packet_manifest_sha256'], output_root=Path(tmp)) as broker:
            receipt = broker.verify_inputs()
    return {'packet_path':str(packet), 'manifest_sha256':scope['private_packet_manifest_sha256'],
            'verification':receipt, 'model_launched':False}


def execute(scope, prior_scope, pins, packet):
    require(ROOT == Path(scope['canonical_project']) and Path.home() == Path(scope['canonical_home']),
            'Use existing canonical WSL home and project')
    require(not bounded(ROOT / 'state/ESCALATION.md').strip(),
            'An unresolved current escalation requires inspection')
    history = prior_history(scope)
    packet_info = packet_preflight(scope, packet)
    authorization = scope['authorization']
    approval_raw = bounded(ROOT / authorization['path'])
    require(sha(approval_raw) == authorization['sha256'], 'Authorization changed before reservation')
    run = new_directory(ROOT / 'delivery' / RUN_NAME)
    with (run / 'AUTHORIZATION.md').open('xb') as handle:
        handle.write(approval_raw); handle.flush(); os.fsync(handle.fileno())
    exclusive_json(run / 'ATTEMPT.json', {'created_utc':datetime.now(timezone.utc).isoformat(),
        'pins':pins,'authorization':authorization,'reserved_native_starts':2,'reserved_turns':2,
        'prior_native_starts':14,'prior_sent_turns':11,
        'automatic_retry':False,'science_conditioned_on_synthetic':True,
        'manual_attended_invocation':True,'continuous_attendance_measured':False})
    result = {'kind':REPORT_KIND,'created_utc':datetime.now(timezone.utc).isoformat(),
        'pins':pins,'authorization':authorization,'history':history,
        'private_packet_preflight':packet_info,'status':'STARTED','stages':[],
        'stage_attempts':[],'science_started':False,'reviewer_output':None,
        'parent_credential_contents_read':False,'unattended_model_use_authorized':False,
        'continuous_human_attendance_verified':False,'scientific_verdict_chosen_by_parent':False,
        'automatic_retry_requested':False,'raw_native_logs_or_protocol_in_report':False,
        'analytical_review_only':True,'candidate_efficacy_experiment_performed':False}
    try:
        synthetic, manifest = synthetic_packet(run)
        result['stage_attempts'].append('synthetic')
        stage = run_stage(scope, prior_scope, run, 'synthetic', synthetic, manifest)
        linked_stage(run, stage, 'synthetic')
        require(admitted_synthetic(stage), 'Synthetic admission incomplete; no science started')
        collection = collect_receipts(run, ['synthetic'])
        require(collection.get('eligible_for_controller_admission_checks') is True,
                'Source-bound synthetic receipt collection failed; no science started')
        refreshed = load_bundle()
        require(refreshed == (scope,prior_scope,pins), 'Dependencies changed before science')
        ready = packet_preflight(scope, packet)
        require(ready == packet_info, 'Private packet changed before science')
        result['stage_attempts'].append('science')
        result['science_started'] = True
        stage = run_stage(scope, prior_scope, run, 'science', Path(ready['packet_path']),
            ready['manifest_sha256'], expected_binding=BINDING.copy())
        linked_stage(run, stage, 'science')
        require(admitted_science(stage), 'Scientific session or protected postcheck admission incomplete')
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
    if not os.path.lexists(run):
        return None
    plain(run, True)
    require(os.path.lexists(run / 'REPORT.json') and os.path.lexists(run / 'REPORT.sha256'),
            'Partial039 attempt preserved; no automatic native retry')
    raw = bounded(run / 'REPORT.json')
    require(bounded(run / 'REPORT.sha256',65) == (sha(raw)+'\n').encode(),
            'Existing039 report checksum differs')
    value = json.loads(raw)
    require(value.get('kind') == REPORT_KIND and value.get('status') in TERMINAL and value.get('pins') == pins,
            'Existing039 report belongs to a different or incomplete scope')
    attempt = json.loads(bounded(run / 'ATTEMPT.json'))
    require(attempt.get('pins') == pins and attempt.get('reserved_native_starts') == 2 and
            attempt.get('reserved_turns') == 2 and attempt.get('automatic_retry') is False,
            'Existing039 reservation differs')
    auth = value.get('authorization',{})
    require(sha(bounded(run / 'AUTHORIZATION.md')) == auth.get('sha256'),
            'Existing039 authorization bytes changed')
    observed = collect_receipts(run, value['stage_attempts'])
    require(observed == value['receipt_collection'], 'Existing original receipts changed')
    if value.get('status') == 'REVIEWER_OUTPUT_PRESERVED':
        require(admitted_synthetic(observed['stages'].get('synthetic')) and
                admitted_science(observed['stages'].get('science')), 'Existing039 admission no longer holds')
        output = value.get('reviewer_output',{})
        require(output.get('sha256') == sha(bounded(run / 'science_output/REVIEW_VERDICT.json')),
                'Existing039 reviewer output changed')
    return run / 'REPORT.json'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-attended-review', action='store_true')
    parser.add_argument('--packet', type=Path)
    args = parser.parse_args()
    try:
        scope, prior, pins = load_bundle()
        run = ROOT / 'delivery' / RUN_NAME
        receipt = existing(run, pins)
        if receipt is not None:
            print(json.dumps({'status':'EXISTING_REPORT_REUSED','report':str(receipt),'new_native_starts':0}))
            return 0
        if not args.run_attended_review:
            print(json.dumps({'status':'SEALED_SCOPE_INSPECTED','scope_sha256':SCOPE_SHA256,
                              'new_native_starts':0,'new_model_turns':0}))
            return 0
        packet = args.packet or ROOT / scope['private_packet_directory']
        receipt = execute(scope, prior, pins, packet)
        value = json.loads(bounded(receipt))
        print(json.dumps({'status':value['status'],'report':str(receipt),
                          'attempt_accounting':value['attempt_accounting']}))
        return 0 if value['status'] == 'REVIEWER_OUTPUT_PRESERVED' else 2
    except KeyboardInterrupt:
        print('STOP: Interrupted; preserve existing files; no automatic native retry')
        return 130
    except Exception as error:
        reason = str(error) if type(error) is Stop else 'Protected local preflight refused; no retry'
        print('STOP: ' + reason)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
