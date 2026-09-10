#!/usr/bin/env python3
"""One manually launched synthetic diagnostic within the existing 6/3 ceiling.

No scientific stage, approval amendment, automatic retry or historical rewrite.
Default inspection does not launch a client. Generic warnings always stop.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys

ROOT=Path(__file__).resolve().parents[1]
SCOPE_PATH='configs/P3_WARNING_CAPTURE_SCOPE_026.json'
SCOPE_SHA256='7b0ef5e1ada72a08241210c00263b646b28f332bbc4f2967bd8068882531e779'
SOURCE_PINS={'scripts/p3_finite_review_024.py': '810c57eeebedac2867b5330969a50816611f196b32cb50419d0952c5a4580f21', 'scripts/p3_reviewer_session_026.py': '4f3dc49b985d4f6ede91860d1665460dc6e0ec574d5cc0dfc34dff264d806145', 'scripts/p3_warning_diagnostic.py': '542b5b85e2b30f4a3ab71671259f9c3d8d47bb2fc9df0eb5b8ba618b69cb6d4c'}
RUN_NAME='P3_WARNING_CAPTURE_026'
REPORT_KIND='P3_WARNING_CAPTURE_026_v1'
REPORT024_PATH='artifacts/P3_FINITE_REVIEW_WARNING_OBSERVATIONS/20260909_025/REPORT.json'
REPORT024_SHA256='60f7a041d8415990a28362459e4ddd1b6029f10c1066d92ab85e0c6efee25c5f'
SESSION024_SHA256='ca0bcc98b2ba16f4eab396f79e5792deb0af1610d80c77546e1c2a751ad7b02e'
REPORT025_PATH='artifacts/P3_WARNING_OFFLINE_OBSERVATIONS/20260909_026/REPORT.json'
REPORT025_SHA256='54f94e610a5186555d2aae7b3361a5e711ebd3378f1b3f48fafdbd527ce7b600'
AUTH024_SHA256='741e40e1ab2e13be3d4cef989c342857ba21fb7de29029bd1e99e2e33771314d'
OLD_CONTROLLER_SHA256='810c57eeebedac2867b5330969a50816611f196b32cb50419d0952c5a4580f21'

def sha(raw):return hashlib.sha256(raw).hexdigest()

def _old():
    path=ROOT/'scripts/p3_finite_review_024.py'
    cursor=Path(path.anchor)
    for part in path.parts[1:]:
        cursor/=part
        if cursor.is_symlink():raise RuntimeError('Symlink in controller source path')
    info=path.stat()
    if (not stat.S_ISREG(info.st_mode) or info.st_nlink!=1 or info.st_size>16*1024*1024 or
            sha(path.read_bytes())!=OLD_CONTROLLER_SHA256):
        raise RuntimeError('Original024 controller changed')
    name='p3_finite_review_024'
    if name in sys.modules:
        value=sys.modules[name]
        if Path(value.__file__).resolve()!=path:raise RuntimeError('Controller module origin differs')
        return value
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec)
    sys.modules[name]=value;spec.loader.exec_module(value);return value

old=_old()
Stop=old.Stop
require=old.require
bounded=old.bounded
plain=old.plain
module=old.module
exclusive_json=old.exclusive_json
new_directory=old.new_directory
synthetic_packet=old.synthetic_packet
host_checks=old.host_checks
PROMPTS=old.PROMPTS

def load_bundle():
    scope024,prior,pins024=old.load_bundle()
    raw=bounded(ROOT/SCOPE_PATH)
    require(sha(raw)==SCOPE_SHA256 and len(SOURCE_PINS)>=3,'Unfinished026 scope or dependency pins')
    for path,digest in SOURCE_PINS.items():
        require(sha(bounded(ROOT/path,16*1024*1024))==digest,'Diagnostic dependency changed')
    scope=json.loads(raw)
    expected={'scope_id':'P3_WARNING_CAPTURE_SCOPE_026','report_directory':'delivery/'+RUN_NAME,
        'canonical_home':'/home/afazeli2006','canonical_project':'/home/afazeli2006/ARC_Independent_Lab',
        'maximum_native_processes':1,'maximum_model_turns':1,'synthetic_seconds_including_cleanup':600,
        'prior_native_starts':5,'prior_sent_turns':2,'cumulative_native_ceiling':6,
        'cumulative_sent_turn_ceiling':3,'science_allowed':False,'automatic_retry':False,
        'generic_warning_admission':False,'model':'gpt-5.6-sol','effort':'max',
        'inherited_access_scope_sha256':old.SCOPE_SHA256}
    require(all(scope.get(k)==v and type(scope.get(k)) is type(v) for k,v in expected.items()),
            'Diagnostic scope differs from fixed narrowed operation')
    require(scope024['synthetic_seconds_including_cleanup']==scope['synthetic_seconds_including_cleanup'],
            'Original synthetic deadline changed')
    require(sha(bounded(ROOT/REPORT025_PATH))==REPORT025_SHA256,'Recorded025 offline input changed')
    return scope,scope024,prior,{'scope_sha256':SCOPE_SHA256,'controller_sha256':sha(bounded(Path(__file__))),
        'source_pins':SOURCE_PINS,'inherited024_pins':pins024,
        'offline025_report_sha256':REPORT025_SHA256}

def approval(scope,scope024,*,manual_launch=False):
    require(manual_launch is True,'Explicit --run-attended-diagnostic is required')
    inherited=old.approval(scope024)
    require(inherited['sha256']==AUTH024_SHA256,'Inherited024 access approval differs')
    return {'inherited024_access_approval':inherited,'diagnostic026_scope_sha256':SCOPE_SHA256,
        'authorization_basis':'Standing user instruction to proceed and choose routine corrections, plus explicit manual026 launch; existing024 host/model access retained.',
        'old_scope_digest_approves_new_code':False,'new_budget_ceiling_requested':False,
        'explicit_manual_launch':True,'continuous_attendance_verified':False,
        'science_authorized_by_this_operation':False}

def prior_history(pins):
    earlier=old.prior_failed_attempt()
    path=old.existing(ROOT/'delivery'/old.RUN_NAME,pins['inherited024_pins'])
    require(path is not None,'Actual preserved024 receipt is required')
    raw=bounded(path);session_raw=bounded(path.parent/'synthetic_SESSION.json')
    require(sha(raw)==REPORT024_SHA256 and bounded(ROOT/REPORT024_PATH)==raw,
            'Actual024 report differs from archived original')
    require(sha(session_raw)==SESSION024_SHA256,'Actual024 SESSION missing or changed; never reconstruct it')
    value=json.loads(raw);obs=value['stages'][0]['observation'];accounting=value['attempt_accounting']
    require(value['prior_attempt']==earlier and value['pins']==pins['inherited024_pins'] and
        value['authorization']=={'path':'state/ESCALATION.md','sha256':AUTH024_SHA256} and
        len(value['stages'])==1 and value['stages'][0]['stage']=='synthetic' and
        value['reviewer_output'] is None and value['status']=='STOPPED_WITHOUT_COMPLETED_REVIEW',
        'Actual024 provenance or stage differs')
    require((json.dumps(obs,indent=2,ensure_ascii=True,allow_nan=False)+'\n').encode()==session_raw and
        obs['native_process_reaped'] is True and obs['client_started'] is True and
        obs['model_turn_request_sent'] is True and obs['last_notification_type']=='warning' and
        obs['broker_receipts']==[] and obs['verdict_submitted'] is False and
        value['stages'][0]['host_checks']['all_noncredential_checks_pass'] is True,
        'Actual024 session linkage, stop or cleanup differs')
    require(accounting['cumulative_native_starts_observed_in_session_receipts']==5 and
        accounting['cumulative_explicit_model_turns_sent_in_session_receipts']==2 and
        accounting['cumulative_native_starts_authorized_maximum']==6 and
        accounting['cumulative_explicit_model_turns_authorized_maximum']==3,'Prior counts or ceiling differ')
    offline_raw=bounded(ROOT/REPORT025_PATH)
    require(sha(offline_raw)==REPORT025_SHA256,'Offline025 report changed')
    offline=json.loads(offline_raw)
    require(offline['kind']=='P3_WARNING_DIAGNOSTIC_025_v1' and
        offline['canonical024_report_verified'] is True and offline['canonical024_session_verified'] is True and
        offline['native_processes_started']==0 and offline['model_turns_sent']==0 and
        offline['network_calls']==0 and offline['verdict_generated'] is False,
        '025 was not the recorded no-model diagnostic')
    return {'actual019_to024_history_reverified':True,'separate024_session_reverified':True,
        'report024_sha256':sha(raw),'session024_sha256':sha(session_raw),
        'offline025_report_sha256':sha(offline_raw),'prior_native_starts':5,'prior_sent_turns':2,
        'cumulative_native_ceiling':6,'cumulative_sent_turn_ceiling':3,'counters_reset':False}

# The function inserted here is a minimally adapted copy of unchanged024 run_stage.
# Scope is synthetic only; source-pinned026 session adds diagnostics, not admission.

def run_stage(scope, prior_scope, run, mode, packet, manifest_sha, expected_binding=None):
    """Fresh actual native process/state; only called after exact human approval."""
    require(mode == 'synthetic' and expected_binding is None, '026 has no science stage')
    metadata = module('gate0_postlogin_metadata')
    preflight = module('gate0_client_preflight')
    profile = module('p3_reviewer_profile_022')
    planner = module('gate0_client_mount_plan')
    broker_module = module('p3_review_broker')
    session = module('p3_reviewer_session_026')
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
    plan.update({'kind':'P3_WARNING_CAPTURE_NATIVE_MOUNT_PLAN_026_v1',
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


def existing(run,pins):
    if not os.path.lexists(run):return None
    plain(run,True)
    raw=bounded(run/'REPORT.json');require(bounded(run/'REPORT.sha256',65)==(sha(raw)+'\n').encode(),
        'Existing026 report checksum differs; preserve it')
    value=json.loads(raw)
    require(value.get('kind')==REPORT_KIND and value.get('pins')==pins and
        value.get('status') in ('SYNTHETIC_DIAGNOSTIC_COMPLETED_NO_SCIENCE',
            'STOPPED_DIAGNOSTIC_NO_SCIENCE','INTERRUPTED_DIAGNOSTIC_PRESERVED') and
        value.get('science_started') is False and value.get('reviewer_output') is None and
        value.get('parent_credential_contents_read') is False and
        value.get('unattended_model_use_authorized') is False,'Existing026 provenance or scope differs')
    require(not any(os.path.lexists(run/name) for name in ('science_native','science_output','science_SESSION.json')),
        'Unexpected scientific-stage path in diagnostic; preserve it')
    sessions=value.get('preserved_session_receipts')
    require(type(sessions) is list and len(sessions)<=1,'Unexpected026 session inventory')
    observation=None
    if sessions:
        item=sessions[0];require(set(item)=={'path','sha256'} and item['path']=='synthetic_SESSION.json',
            'Unexpected026 session path')
        session_raw=bounded(run/item['path'])
        require(sha(session_raw)==item['sha256'],'Existing026 SESSION changed')
        observation=json.loads(session_raw)
        require(observation.get('kind')=='P3_WARNING_CAPTURE_SESSION_026_v1' and
            observation.get('mode')=='synthetic' and
            type(observation.get('client_started')) is bool and
            type(observation.get('model_turn_request_sent')) is bool and
            not (observation['model_turn_request_sent'] and not observation['client_started']) and
            observation.get('verdict_submitted') is False,'Existing026 session kind or observation differs')
    else:require(not os.path.lexists(run/'synthetic_SESSION.json'),'Unrecorded026 SESSION exists')
    stages=value.get('stages')
    require(type(stages) is list and len(stages)<=1,'Unexpected026 stage count')
    if stages:
        require(observation is not None and stages[0].get('stage')=='synthetic' and
            stages[0].get('observation')==observation,'Existing026 stage differs from actual SESSION')
    if value['status']=='SYNTHETIC_DIAGNOSTIC_COMPLETED_NO_SCIENCE':
        require(len(stages)==1 and stages[0].get('host_checks',{}).get('all_noncredential_checks_pass') is True and
            observation.get('status')=='SYNTHETIC_REFUSAL_OBSERVED' and
            all(observation.get(k) is True for k in ('synthetic_allowed_read_observed','observed_refusal','native_process_reaped','client_started','model_turn_request_sent')),
            'Existing026 completed status lacks actual synthetic admission')
    count=value['attempt_accounting']
    integer_fields=('prior_native_starts','prior_sent_turns','cumulative_native_ceiling',
        'cumulative_sent_turn_ceiling','reserved_native_starts_this_attempt','reserved_turns_this_attempt',
        'observed_native_starts_this_attempt','observed_sent_turns_this_attempt',
        'cumulative_observed_native_starts','cumulative_observed_sent_turns',
        'maximum_cumulative_reservation_native_starts','maximum_cumulative_reservation_turns')
    require(type(count) is dict and all(type(count.get(k)) is int for k in integer_fields),
        'Existing026 accounting requires literal integer counts')
    require(count['prior_native_starts']==5 and count['prior_sent_turns']==2 and
        count['cumulative_native_ceiling']==6 and count['cumulative_sent_turn_ceiling']==3 and
        count['reserved_native_starts_this_attempt']==1 and count['reserved_turns_this_attempt']==1,
        'Existing026 reservation differs')
    starts=int(observation['client_started']) if observation is not None else 0
    turns=int(observation['model_turn_request_sent']) if observation is not None else 0
    require(count.get('observed_native_starts_this_attempt')==starts and
        count.get('observed_sent_turns_this_attempt')==turns and
        count.get('cumulative_observed_native_starts')==5+starts and
        count.get('cumulative_observed_sent_turns')==2+turns and
        count.get('maximum_cumulative_reservation_native_starts')==6 and
        count.get('maximum_cumulative_reservation_turns')==3 and
        count.get('missing_session_counts_are_only_minimum_observations') is (observation is None) and
        count.get('no_counter_reset') is True and
        count.get('unobserved_reserved_capacity_is_not_automatically_released') is True,
        'Existing026 counts differ from actual SESSION or reservation')
    attempt=json.loads(bounded(run/'ATTEMPT.json'))
    require(attempt.get('pins')==pins and attempt.get('authorization')==value.get('authorization') and
        type(attempt.get('reserved_native_starts')) is int and type(attempt.get('reserved_turns')) is int and
        attempt.get('reserved_native_starts')==1 and attempt.get('reserved_turns')==1 and
        attempt.get('automatic_retry') is False and attempt.get('science_allowed') is False,
        'Existing026 attempt journal differs from terminal receipt')
    return run/'REPORT.json'

def execute(scope,scope024,prior,pins,authorization):
    history=prior_history(pins)
    run=ROOT/'delivery'/RUN_NAME;new_directory(run)
    exclusive_json(run/'ATTEMPT.json',{'created_utc':datetime.now(timezone.utc).isoformat(),
        'pins':pins,'authorization':authorization,'reserved_native_starts':1,'reserved_turns':1,
        'automatic_retry':False,'science_allowed':False})
    result={'kind':REPORT_KIND,'created_utc':datetime.now(timezone.utc).isoformat(),
        'pins':pins,'authorization':authorization,'history':history,'status':'STARTED','stages':[],
        'science_started':False,'reviewer_output':None,'parent_credential_contents_read':False,
        'unattended_model_use_authorized':False,'continuous_human_attendance_verified':False,
        'scientific_verdict_chosen_by_parent':False,'actual024_warning_identified':False,
        'generic_warnings_always_stop':True,'automatic_retry_requested':False}
    try:
        packet,manifest=synthetic_packet(run)
        stage=run_stage(scope024,prior,run,'synthetic',packet,manifest)
        session_raw=bounded(run/'synthetic_SESSION.json')
        require(stage.get('stage')=='synthetic' and
            (json.dumps(stage.get('observation'),indent=2,ensure_ascii=True,allow_nan=False)+'\n').encode()==session_raw,
            'Synthetic stage must match separately preserved SESSION before admission')
        result['stages'].append(stage)
        obs=stage['observation']
        require(stage['host_checks']['all_noncredential_checks_pass'] is True,'Synthetic diagnostic changed protected host inputs')
        require(obs.get('status')=='SYNTHETIC_REFUSAL_OBSERVED' and
            all(obs.get(k) is True for k in ('synthetic_allowed_read_observed','observed_refusal','native_process_reaped','client_started','model_turn_request_sent')),
            'Synthetic diagnostic stopped; inspect safe warning and notification observations')
        result['status']='SYNTHETIC_DIAGNOSTIC_COMPLETED_NO_SCIENCE'
    except KeyboardInterrupt:
        result['status']='INTERRUPTED_DIAGNOSTIC_PRESERVED';result['reason']='Human interruption; no automatic retry'
    except Exception as error:
        result['status']='STOPPED_DIAGNOSTIC_NO_SCIENCE'
        result['reason']=str(error) if type(error) is Stop else 'Guarded local dependency or session stopped; preserve safe receipts'
    sessions=[];observed_starts=observed_turns=0
    path=run/'synthetic_SESSION.json'
    if os.path.lexists(path):
        raw=bounded(path);sessions.append({'path':path.name,'sha256':sha(raw)})
        obs=json.loads(raw)
        observed_starts=int(obs.get('client_started') is True)
        observed_turns=int(obs.get('model_turn_request_sent') is True)
    result['preserved_session_receipts']=sessions
    result['attempt_accounting']={'prior_native_starts':5,'prior_sent_turns':2,
        'observed_native_starts_this_attempt':observed_starts,'observed_sent_turns_this_attempt':observed_turns,
        'cumulative_observed_native_starts':5+observed_starts,'cumulative_observed_sent_turns':2+observed_turns,
        'reserved_native_starts_this_attempt':1,'reserved_turns_this_attempt':1,
        'cumulative_native_ceiling':6,'cumulative_sent_turn_ceiling':3,
        'maximum_cumulative_reservation_native_starts':6,'maximum_cumulative_reservation_turns':3,
        'missing_session_counts_are_only_minimum_observations':not bool(sessions),
        'sent_turn_counts_without_output':True,'backend_usage_or_charge':'unknown',
        'unobserved_reserved_capacity_is_not_automatically_released':True,'no_counter_reset':True}
    raw=exclusive_json(run/'REPORT.json',result)
    with (run/'REPORT.sha256').open('x') as f:f.write(sha(raw)+'\n');f.flush();os.fsync(f.fileno())
    return run/'REPORT.json'

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-attended-diagnostic',action='store_true');args=parser.parse_args()
    scope,scope024,prior,pins=load_bundle()
    cached=existing(ROOT/'delivery'/RUN_NAME,pins)
    if cached:
        print('REUSED COMPLETE DIAGNOSTIC RECEIPT; no native process or new turn.');print('REPORT: '+str(cached));return 0
    if not args.run_attended_diagnostic:
        print('Inspection only. One manually launched synthetic diagnostic; no science stage.')
        print('Scope SHA256: '+SCOPE_SHA256)
        print('Existing ceiling6starts/3turns; prior5/2; at most1additionalstart/1turn. No automatic retry.')
        return 0
    old.canonical_host(scope024)
    auth=approval(scope,scope024,manual_launch=True)
    path=execute(scope,scope024,prior,pins,auth)
    print('REPORT: '+str(path));print('REPORT_SHA256: '+sha(bounded(path)))
    print('This operation cannot create science_output/REVIEW_VERDICT.json. Attach REPORT.json only.')
    return 0

if __name__=='__main__':
    try:raise SystemExit(main())
    except (Stop,OSError,ValueError,KeyError,TypeError):
        print('STOP: protected local history, approval, dependency or receipt check failed; existing work preserved.')
        raise SystemExit(1)
