#!/usr/bin/env python3
"""One explicitly approved, human-launched finite review; inspection by default.

Owns scope, fresh process directories and the external read-only evidence broker.
No automatic retry, credential content access, scientific verdict choice or Git
mutation is implemented. The existing metadata operation is never re-executed.
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
SCOPE_PATH = 'configs/P3_FINITE_REVIEW_SCOPE_019.json'
SCOPE_SHA256 = '99d7f62d60b3384b5bb83923047b390f7f7e6e8d90c2654b33d996101755d5ea'
SOURCE_PINS = {
    "artifacts/GATE0_ACCOUNT_PLAN_SOURCE/20260908_001/MANIFEST.json": "f47ece02e29f93aeb14cc08ea1fc53109e13eb197465699c9ba6a4f516c70704",
    "artifacts/GATE0_CODEX_INTERFACE/20260907_001/config-schema.json": "ed663d6d4c6c8b36917596882414c93858f6cf9ca5449ea8c616fc76d1aac114",
    "artifacts/GATE0_CODEX_INTERFACE/20260907_001/schemas/experimental.json": "dd4014851ef7c60ecacfa5fa4d1a9f02d7dcc2aada93c83091a717b27b753d63",
    "artifacts/GATE0_POSTLOGIN_OBSERVATIONS/20260908_001/REPORT.json": "4aa0757da0d56a4db65ca7a33cf15d7454129c21fab7283457261d3a8ebcbba7",
    "artifacts/GATE0_REVIEWER_EFFECT_SOURCE/20260908_001/MANIFEST.json": "88f6567051f17865584d5b0a90c9d655c3c0819b77a25d636333eb71363cdee1",
    "configs/P3_REVIEW_SCIENTIFIC_019.txt": "12978892ea087dad73ca57fda28d735254262ef3e883cdf9e4240be6dafb1d4d",
    "configs/P3_REVIEW_SYNTHETIC_019.txt": "e8bb9c827beff3ca9056e81c04062f3d93f2ac851ae992ff806ac5ada8e434ae",
    "scripts/audit_learner_observer.py": "871ab1e62a592d9b49f93d5d5d783e262f8db1cb15bcc0b8ba6191f0ca0d4b1e",
    "scripts/gate0_account_metadata.py": "13f4e87a7da463b6915f49df4f97b2cea271a7e8de9f16b21281db50842dac76",
    "scripts/gate0_client_mount_plan.py": "4500a10227a5209a525e5ab7534a1bd2e55e3574c91381c584e5a99c7095a107",
    "scripts/gate0_client_preflight.py": "a4d0c4be8d6ade00f82285381dfa68e0310146fca300752bac3fac74d6bd3038",
    "scripts/gate0_config_controls.py": "9dc478ba6c68e32be69079e154dde1f3debd4d8dbd998f7648577b5df2c4bf8d",
    "scripts/gate0_postlogin_boundary.py": "aab4cb14a30bb1ee9f7b1e0d983f54fe509977bdc9d8aad7a4d8e54fbec6d20f",
    "scripts/gate0_postlogin_metadata.py": "b7fc9db3af9004c89a8fd87961f3e83ae94bad707e05c355a7a30b6646502197",
    "scripts/gate0_postlogin_protocol.py": "222ed3eb698b947b0d7286991101308485f44554c823abb7723c9882d213877a",
    "scripts/install_p3_review_packet.py": "3e97c509a06dd1518b8ed0b121600b834e689df34d832aac26a6bc3d20ebc051",
    "scripts/p3_review_broker.py": "6f2118cb32573c7774db269c09694913040d06adb5eca9e8ca1a0fafe6089536",
    "scripts/p3_review_protocol.py": "9bc4315dc3d6af679890828db5a1ee5ef19f49e2c7214cc0dd384728a9cf754f",
    "scripts/p3_reviewer_admission.py": "9b589287b6b56ad56e12075d655d0c9935a570076a35544fa64a40973b6969cb",
    "scripts/p3_reviewer_profile.py": "669da4f8bae0cac3f43433ebc2b462da607be631b259d7ff08919b8f1130991f",
    "scripts/p3_reviewer_session.py": "6ab41524d9759fd26e4f63b75a8f5a4cdad867906434ecb57aee106a9e70066d"
}
RUN_NAME = 'P3_FINITE_REVIEW_019'
REPORT_KIND = 'P3_FINITE_REVIEW_019_v1'
APPROVAL_ARCHIVE = 'state/escalations/2026-09-08_FINITE_REVIEW_019_APPROVED.md'
PROMPTS = {'synthetic': 'configs/P3_REVIEW_SYNTHETIC_019.txt',
           'science': 'configs/P3_REVIEW_SCIENTIFIC_019.txt'}
FROZEN = {'evidence/P3_AUDIT_REVIEW_MANIFEST.json':
          '8d475e93aa21db5d7210f337c036e2705e3a4b83b6d99d43d715161d63b7e374',
          'evidence/P3_RESIDUAL_REVIEW_MANIFEST.json':
          'f7249d53060349fdfbaca2102672457e3e8966ef510d6853322b10da75762128'}


class Stop(RuntimeError):
    """Fixed locally authored nonsecret reason."""


def require(value, reason):
    if not value:
        raise Stop(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def module(name):
    expected = ROOT / 'scripts' / (name + '.py')
    existing = sys.modules.get(name)
    if existing is not None:
        require(Path(existing.__file__).resolve() == expected.resolve(),
                'Sibling module origin differs')
        return existing
    spec = importlib.util.spec_from_file_location(name, expected)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


def plain(path, directory=False):
    path = Path(path).absolute()
    require('..' not in path.parts, 'Noncanonical protected path')
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        require(not current.is_symlink(), 'Symlink in protected path')
    info = path.stat()
    require(stat.S_ISDIR(info.st_mode) if directory else
            stat.S_ISREG(info.st_mode) and info.st_nlink == 1,
            'Protected path has unexpected type or alias')
    return path


def bounded(path, maximum=4 * 1024 * 1024):
    path = plain(path)
    require(path.stat().st_size <= maximum, 'Protected input exceeds byte bound')
    return path.read_bytes()


def load_bundle():
    raw = bounded(ROOT / SCOPE_PATH)
    require(sha(raw) == SCOPE_SHA256 and bool(SOURCE_PINS), 'Unfinished or changed review scope/pins')
    for name, expected in SOURCE_PINS.items():
        require(sha(bounded(ROOT / name, 16 * 1024 * 1024)) == expected,
                'Pinned reviewer dependency changed')
    scope = json.loads(raw)
    require(scope['maximum_native_processes'] == 2 and scope['maximum_model_turns'] == 2,
            'Unexpected review process/turn limits')
    accepted = bounded(ROOT / scope['accepted_metadata_path'])
    require(sha(accepted) == scope['accepted_metadata_sha256'], 'Accepted metadata receipt changed')
    value = json.loads(accepted)
    require(value['observation']['status'] == 'OBSERVED_POSTLOGIN_METADATA_ONLY',
            'Accepted metadata completion is absent')
    prior = bounded(ROOT / scope['prior_native_scope_path'])
    require(sha(prior) == scope['prior_native_scope_sha256'], 'Original provenance scope changed')
    for path, digest in FROZEN.items():
        manifest = bounded(ROOT / path)
        require(sha(manifest) == digest, 'Frozen scientific manifest changed')
        for entry in json.loads(manifest)['files']:
            require(sha(bounded(ROOT / entry['path'], 128 * 1024 * 1024)) == entry['sha256'],
                    'Frozen scientific input changed')
    return scope, json.loads(prior), {
        'scope_sha256': sha(raw), 'controller_sha256': sha(bounded(Path(__file__))),
        'source_pins': SOURCE_PINS, 'accepted_metadata_sha256': sha(accepted),
        'frozen_manifests': FROZEN,
        'packet_manifest_sha256': scope['private_packet_manifest_sha256']}


def approval(scope):
    path = ROOT / 'state/ESCALATION.md'
    text = bounded(path).decode('utf-8')
    if not text.strip():
        path = ROOT / APPROVAL_ARCHIVE
        require(path.exists(), 'Recorded finite-review approval is required')
        text = bounded(path).decode('utf-8')
    fence, positions = None, []
    require('<!--' not in text and '-->' not in text,
            'HTML comment ambiguity in approval document')
    lines = text.splitlines()
    for i, line in enumerate(lines):
        start = line.lstrip(' ')
        if len(line) - len(start) <= 3 and start.startswith(('```', '~~~')):
            char = start[0]; length = len(start) - len(start.lstrip(char))
            if fence is None:
                fence = (char, length)
            elif char == fence[0] and length >= fence[1] and not start[length:].strip():
                fence = None
            continue
        if fence is None and line == '## ANSWER':
            positions.append(i)
    require(len(positions) == 1, 'Exactly one actual finite-review ANSWER is required')
    answer = [line for line in lines[positions[0] + 1:] if line.strip()]
    require(answer == [scope['approval_id'], 'scope_sha256: ' + SCOPE_SHA256],
            'Recorded answer differs from this exact finite-review scope')
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(bounded(path))}


def exclusive_json(path, value):
    raw = (json.dumps(value, indent=2, ensure_ascii=True, allow_nan=False) + '\n').encode()
    with path.open('xb') as f:
        f.write(raw); f.flush(); os.fsync(f.fileno())
    return raw


def existing(run, pins):
    if not os.path.lexists(run):
        return None
    plain(run, True)
    report = bounded(run / 'REPORT.json')
    require(bounded(run / 'REPORT.sha256', 65) == (sha(report) + '\n').encode(),
            'Previous review receipt checksum differs; preserve it')
    value = json.loads(report)
    require(value.get('kind') == REPORT_KIND and value.get('pins') == pins,
            'Previous review provenance differs; preserve it')
    require(value.get('unattended_model_use_authorized') is False and
            value.get('parent_credential_contents_read') is False,
            'Previous review scope differs')
    verdict = value.get('reviewer_output')
    if verdict is not None:
        require(type(verdict) is dict and verdict.get('path') == 'science_output/REVIEW_VERDICT.json',
                'Unexpected recorded verdict path')
        require(sha(bounded(run / verdict['path'], 1024 * 1024)) == verdict.get('sha256'),
                'Existing reviewer output changed; preserve it')
    else:
        require(not os.path.lexists(run / 'science_output/REVIEW_VERDICT.json'),
                'Unrecorded reviewer output exists; preserve it')
    sessions = value.get('preserved_session_receipts', [])
    require(type(sessions) is list, 'Malformed preserved session inventory')
    seen = set()
    for item in sessions:
        require(type(item) is dict and set(item) == {'path', 'sha256'} and
                item['path'] in ('synthetic_SESSION.json', 'science_SESSION.json') and
                item['path'] not in seen, 'Unexpected preserved session receipt')
        seen.add(item['path'])
        require(sha(bounded(run / item['path'])) == item['sha256'],
                'Preserved session receipt changed; preserve it')
    require({name for name in ('synthetic_SESSION.json', 'science_SESSION.json')
             if os.path.lexists(run / name)} == seen, 'Unrecorded session receipt exists; preserve it')
    return run / 'REPORT.json'


def canonical_host(scope):
    home = Path(scope['canonical_home'])
    require(ROOT == Path(scope['canonical_project']) and Path.home() == home and
            os.environ.get('HOME') == str(home), 'Use the canonical existing WSL lab and HOME')
    require('CODEX_HOME' not in os.environ or os.environ['CODEX_HOME'] == str(home / '.codex'),
            'CODEX_HOME provenance differs; do not reassign it')
    require(not any(k in os.environ for k in ('OPENAI_API_KEY','CODEX_API_KEY','CODEX_ACCESS_TOKEN')),
            'Credential environment variable is present; value not read')
    plain(ROOT, True); plain(ROOT / 'delivery', True)


def new_directory(path):
    plain(path.parent, True)
    require(not os.path.lexists(path), 'New review directory already exists; preserve it')
    path.mkdir(mode=0o700)
    return path


def synthetic_packet(run):
    packet = new_directory(run / 'synthetic_packet')
    body = b'SYNTHETIC_REVIEW_CANARY_ONLY\n'
    with (packet / 'CANARY.txt').open('xb') as f:
        f.write(body)
    raw = exclusive_json(packet / 'BROKER_MANIFEST.json', {'schema_version':1,'files':[
        {'path':'CANARY.txt','sha256':sha(body),'kind':'text'}]})
    return packet, sha(raw)


def host_checks(facts, metadata, preflight):
    origins = all(metadata.metadata(Path(item['path'])) == item['metadata'] if item['present']
                  else not os.path.lexists(item['path'])
                  for item in facts['origins'] if item['path'] != str(facts['auth']))
    caches = all(metadata.metadata(Path(item['path'])) == item['metadata'] if item['present']
                 else not os.path.lexists(item['path']) for item in facts['cache_origins'])
    result = {'config_metadata_unchanged':origins, 'cache_metadata_unchanged':caches,
              'runtime_unchanged':preflight.signature(facts['runtime']) == facts['runtime_before'],
              'bwrap_unchanged':preflight.signature(facts['bwrap']) == facts['bwrap_before'],
              'host_installation_id_unchanged':preflight.signature(facts['identifier']) == facts['identifier_before'],
              'credential_metadata_after':metadata.metadata(facts['auth']),
              'credential_contents_checked':False}
    result['all_noncredential_checks_pass'] = all(result[k] for k in (
        'config_metadata_unchanged','cache_metadata_unchanged','runtime_unchanged',
        'bwrap_unchanged','host_installation_id_unchanged'))
    return result


def run_stage(scope, prior_scope, run, mode, packet, manifest_sha, expected_binding=None):
    """Fresh actual native process/state; only called after exact human approval."""
    metadata = module('gate0_postlogin_metadata')
    preflight = module('gate0_client_preflight')
    profile = module('p3_reviewer_profile')
    planner = module('gate0_client_mount_plan')
    broker_module = module('p3_review_broker')
    session = module('p3_reviewer_session')
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
    plan.update({'kind':'P3_FINITE_REVIEW_NATIVE_MOUNT_PLAN_019_v1',
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


def execute(scope, prior_scope, pins, authorization, packet_info):
    run = ROOT / 'delivery' / RUN_NAME
    new_directory(run)
    exclusive_json(run / 'ATTEMPT.json', {'created_utc':datetime.now(timezone.utc).isoformat(),
        'pins':pins,'authorization':authorization,'automatic_retry':False})
    result = {'kind':REPORT_KIND,'created_utc':datetime.now(timezone.utc).isoformat(),
        'pins':pins,'authorization':authorization,'status':'STARTED','stages':[],
        'parent_credential_contents_read':False,'unattended_model_use_authorized':False,
        'continuous_human_attendance_verified':False,'scientific_verdict_chosen_by_parent':False,
        'reviewer_output':None,'raw_native_logs_or_protocol_in_report':False,
        'actual_native_tool_denials_inferred_from_nonuse':False,'model_calls_authorized_maximum':2}
    try:
        packet, manifest = synthetic_packet(run)
        stage = run_stage(scope, prior_scope, run, 'synthetic', packet, manifest)
        result['stages'].append(stage)
        require(stage['host_checks']['all_noncredential_checks_pass'], 'Synthetic stage changed protected host inputs')
        observed = stage['observation']
        require(observed.get('status') == 'SYNTHETIC_REFUSAL_OBSERVED' and
                all(observed.get(key) is True for key in (
                    'synthetic_allowed_read_observed', 'observed_refusal', 'native_process_reaped')),
                'Synthetic dynamic refusal admission incomplete; no science started')
        binding = stage['observation'].get('selected_binding')
        require(type(binding) is dict and set(binding) == {'model','id','effort'},
                'Accepted synthetic model binding is unavailable')
        # Complete frozen bytes and full private packet are rechecked immediately
        # before the entirely distinct scientific process/context.
        load_bundle()
        ready = module('install_p3_review_packet').verify_packet(ROOT)
        require(ready['manifest_sha256'] == pins['packet_manifest_sha256'], 'Private packet changed')
        stage = run_stage(scope, prior_scope, run, 'science', Path(ready['packet_path']),
                          ready['manifest_sha256'], expected_binding=binding)
        result['stages'].append(stage)
        require(stage['host_checks']['all_noncredential_checks_pass'], 'Scientific stage changed protected host inputs')
        output = run / 'science_output/REVIEW_VERDICT.json'
        if output.exists():
            observed = stage['observation']
            require(observed.get('status') == 'VERDICT_SUBMITTED' and
                    observed.get('verdict_submitted') is True and
                    observed.get('native_process_reaped') is True,
                    'Output exists without completed broker receipt; preserve for inspection')
            result['status'] = 'REVIEWER_OUTPUT_PRESERVED'
        else:
            result['status'] = 'STOPPED_WITHOUT_REVIEWER_VERDICT'
    except KeyboardInterrupt:
        result['status']='INTERRUPTED_PARTIAL_PRESERVED'
        result['reason']='Human interrupted finite review; no automatic retry'
    except (Stop, OSError, ValueError, KeyError) as error:
        result['status']='STOPPED_WITHOUT_COMPLETED_REVIEW'
        result['reason']=str(error) if isinstance(error,Stop) else 'Local integrity, input or I/O check stopped; raw error withheld'
    # Errors in a sibling guard may inherit RuntimeError; only local fixed reasons
    # above are exposed. Never serialize arbitrary native/credential diagnostics.
    except Exception:
        result['status']='STOPPED_WITHOUT_COMPLETED_REVIEW'
        result['reason']='Reviewer dependency or guarded session stopped; inspect preserved safe stage receipts'
    # Receipt preservation is independent of admission: a verdict can exist
    # before a later host or cleanup check fails. Never edit or discard it.
    output = run / 'science_output/REVIEW_VERDICT.json'
    if os.path.lexists(output):
        try:
            raw = bounded(output, 1024 * 1024)
            result['reviewer_output'] = {
                'path':'science_output/REVIEW_VERDICT.json', 'sha256':sha(raw),
                'bytes':len(raw), 'parent_edited':False,
                'execution_admitted':result['status'] == 'REVIEWER_OUTPUT_PRESERVED'}
        except (Stop, OSError):
            result['status']='STOPPED_WITHOUT_COMPLETED_REVIEW'
            result['reason']='Reviewer output exists but protected byte inspection failed; preserve it'
    result['preserved_session_receipts'] = []
    for mode in ('synthetic', 'science'):
        path = run / (mode + '_SESSION.json')
        if path.exists():
            raw = bounded(path)
            result['preserved_session_receipts'].append({'path':path.name,'sha256':sha(raw)})
    raw=exclusive_json(run / 'REPORT.json',result)
    with (run / 'REPORT.sha256').open('x') as f:
        f.write(sha(raw)+'\n');f.flush();os.fsync(f.fileno())
    return run / 'REPORT.json'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-attended-review',action='store_true')
    args=parser.parse_args()
    scope,prior,pins=load_bundle()
    run=ROOT/'delivery'/RUN_NAME
    old=existing(run,pins)
    if old:
        print('REUSED COMPLETE RECEIPT; no native process or host remeasurement.')
        print('REPORT: '+str(old));return 0
    if not args.run_attended_review:
        print('Scope SHA256: '+SCOPE_SHA256)
        print('Inspection only. No changes, network, account or model operation performed.')
        print('Private packet must be installed; recorded exact scope ANSWER precedes --run-attended-review.')
        return 0
    canonical_host(scope)
    authorization=approval(scope)
    info=module('install_p3_review_packet').verify_packet(ROOT)
    require(info['manifest_sha256']==scope['private_packet_manifest_sha256'], 'Wrong private evidence packet')
    report=execute(scope,prior,pins,authorization,info)
    print('REPORT: '+str(report));print('REPORT_SHA256: '+sha(bounded(report)))
    print('Open report folder in WSL: explorer.exe "$(wslpath -w '+str(report.parent)+')"')
    return 0


if __name__=='__main__':
    try:
        raise SystemExit(main())
    except (Stop,OSError,ValueError) as error:
        print('STOP: '+(str(error) if isinstance(error,Stop) else
                       'Protected local file check failed; existing work is preserved'))
        raise SystemExit(1)
