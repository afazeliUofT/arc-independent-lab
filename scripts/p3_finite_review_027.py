#!/usr/bin/env python3
"""One exactly approved synthetic admission and conditional fresh scientific review.

The new 8-start/5-sent-turn cumulative ceiling requires exact027 approval. Every
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

ROOT = Path(__file__).resolve().parents[1]
SCOPE_PATH = 'configs/P3_FINITE_REVIEW_SCOPE_027.json'
SCOPE_SHA256 = 'a69877f8bbeddfd4b638943d850e73a8eb2e978d9d1ce08600484d6c5a0df7a9'
SOURCE_PINS = {
    "artifacts/P3_DIRECT_BROKER_SOURCE/20260910_027/MANIFEST.json": "a79a0d2119f701ec1a0e3707b46611fb84c8e2f240bbf7c45dee676ff9b07e12",
    "artifacts/P3_DIRECT_BROKER_SOURCE/20260910_027/source/codex-rs/app-server/src/code_mode_host.rs": "39a0b682da90b7b567ef4dcbb4ba8b310401ce17a23345cb79084592b4daaf5d",
    "artifacts/P3_DIRECT_BROKER_SOURCE/20260910_027/source/codex-rs/code-mode-host/src/lib.rs": "377dedb6ba011ca7ce1a9f08106abf0722a1816a873707d719042e5131ada9db",
    "artifacts/P3_DIRECT_BROKER_SOURCE/20260910_027/source/codex-rs/code-mode-host/src/main.rs": "dcb976733c91cfd39f9c29c264c9ba81c1677f8a2a0f6cb7d2541ec3a85f9e89",
    "artifacts/P3_DIRECT_BROKER_SOURCE/20260910_027/source/codex-rs/code-mode-runtime/src/runtime/callbacks.rs": "79d2bf693103a238dfc5f7aee4f6b216955e9f01a4da4a90aebc32884a0f428c",
    "artifacts/P3_DIRECT_BROKER_SOURCE/20260910_027/source/codex-rs/code-mode-runtime/src/runtime/globals.rs": "e62df37ddd8d36f3f799d3a2713b225661e3706dcaf2fe97b3cf183427903c07",
    "artifacts/P3_DIRECT_BROKER_SOURCE/20260910_027/source/codex-rs/code-mode-runtime/src/runtime/mod.rs": "0c2cbbdf2dd94ad3bda1508dca676e385de578b32259c4b2d68c0799e6d77fef",
    "artifacts/P3_DIRECT_BROKER_SOURCE/20260910_027/source/codex-rs/code-mode-runtime/src/runtime/module_loader.rs": "6e58d68d43d8aefca0daf5ebbd3876cc9f3837f02a50a676089366fcbff62528",
    "artifacts/P3_DIRECT_BROKER_SOURCE/20260910_027/source/codex-rs/code-mode/Cargo.toml": "2646402e31d512209a03e1568ae81b5b5d85405f7f762d8aa169b3f0ac14959b",
    "artifacts/P3_DIRECT_BROKER_SOURCE/20260910_027/source/codex-rs/code-mode/src/lib.rs": "672628d0254daded50e508875039d7dcdb95d4d850209ae3ac3f95161b0e470d",
    "artifacts/P3_DIRECT_BROKER_SOURCE/20260910_027/source/codex-rs/code-mode/src/remote_session.rs": "30f866ccc860e3f0185da4a1e4e040b0042e06a6fc31041e4227721cbb29e3ce",
    "artifacts/P3_DIRECT_BROKER_SOURCE/20260910_027/source/codex-rs/code-mode/src/remote_session/connection.rs": "abda69cebf2e871ba21744aed1a6959d154a4ff3e4bcfa8f6acfd04bce9512d3",
    "artifacts/P3_DIRECT_BROKER_SOURCE/20260910_027/source/codex-rs/core/src/thread_manager.rs": "8413832bd97d1e216f4ba0444d3cbb9cde3cb922cb149c40cdf653c832266336",
    "artifacts/P3_DIRECT_BROKER_SOURCE/20260910_027/source/codex-rs/core/src/tools/code_mode/delegate.rs": "37b003daef2b909e124c171d676db9ba081a91c66805d5513852b268c3684a4e",
    "artifacts/P3_DIRECT_BROKER_SOURCE/20260910_027/source/codex-rs/core/src/tools/handlers/dynamic.rs": "5e315b42993b4637e5543bcfcc858b82336437f7fb3a367ff5dc911273fa97b4",
    "artifacts/P3_DIRECT_BROKER_SOURCE/20260910_027/source/codex-rs/core/src/tools/registry.rs": "72c1360168efa5a21cbf14aefadedb538ee2f23ec92ca6cab2f749bbf5d41ed7",
    "artifacts/P3_DIRECT_BROKER_SOURCE/20260910_027/source/codex-rs/core/src/tools/router.rs": "6f5b3e6fcc2473c85275e69d934faf3cb95b90e9c773a055944116d517986a90",
    "artifacts/P3_DIRECT_BROKER_SOURCE/20260910_027/source/codex-rs/core/src/tools/spec_plan.rs": "52f549a2ac0836aece71f159850a634e71d1fbe5cb3bb58b98cca9b5744d6f9d",
    "artifacts/P3_DIRECT_BROKER_SOURCE/20260910_027/source/codex-rs/core/src/tools/spec_plan_tests.rs": "e3184eec67ee091e794c96dbae8c967dcb4e2bf926f041aead574bb279aade0e",
    "artifacts/P3_DIRECT_BROKER_SOURCE/20260910_027/source/codex-rs/features/src/feature_configs.rs": "6e60306024c738e9d17a20b0ea0d2c5f91f66dccfd62bc708ebd9141e507b476",
    "artifacts/P3_DIRECT_BROKER_SOURCE/20260910_027/source/codex-rs/install-context/src/lib.rs": "c69b32ccf726bfdd8f18acdad99e4c5a4cdc844049c4750775d4178ec0f41ddf",
    "scripts/p3_disabled_codemode_notice.py": "f1ebf9a2485a6c89acac9f8e184c99e82a0816b756379d6b8670695d160e8771",
    "scripts/p3_reviewer_session_027.py": "cb87ebdf3b95d798b2ed0024c5e762ab57a941bf74e6b309333633b118ec49aa",
    "scripts/p3_warning_capture_026.py": "e1fc314d017f51da42829ce2e9e2f2fe7d43ac290c636afe1434798ac47b223c"
}
RUN_NAME = 'P3_FINITE_REVIEW_027'
REPORT_KIND = 'P3_FINITE_REVIEW_027_v1'
SESSION_KIND = 'P3_FINITE_REVIEWER_SESSION_027_v1'
REPORT026_PATH = 'artifacts/P3_WARNING_CAPTURE_OBSERVATIONS/20260910_027/REPORT.json'
REPORT026_SHA256 = 'ccbfa9a5d6e356fa62a11499ad68dd3740159b96bffb106880b2295fdd871043'
SESSION026_SHA256 = 'ff558c50623d260cc567ee2b5ef70636e40c5794107393e08aa6081dca94b4fc'
AUTH024_PATH = 'state/escalations/2026-09-09_SOL_REVIEW_024_APPROVED.md'
AUTH024_SHA256 = '741e40e1ab2e13be3d4cef989c342857ba21fb7de29029bd1e99e2e33771314d'
OLD_CONTROLLER_SHA256 = 'e1fc314d017f51da42829ce2e9e2f2fe7d43ac290c636afe1434798ac47b223c'
BINDING = {'model': 'gpt-5.6-sol', 'id': 'gpt-5.6-sol', 'effort': 'max'}
TERMINAL = ('REVIEWER_OUTPUT_PRESERVED', 'STOPPED_WITHOUT_REVIEWER_VERDICT',
            'STOPPED_WITHOUT_COMPLETED_REVIEW', 'INTERRUPTED_PARTIAL_PRESERVED')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value, indent=2, ensure_ascii=True, allow_nan=False) + '\n').encode()


def _prior_controller():
    path = ROOT / 'scripts/p3_warning_capture_026.py'
    cursor = Path(path.anchor)
    for part in path.parts[1:]:
        cursor /= part
        if cursor.is_symlink():
            raise RuntimeError('Symlink in historical controller path')
    info = path.stat()
    if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > 16 * 1024 * 1024 or
            sha(path.read_bytes()) != OLD_CONTROLLER_SHA256):
        raise RuntimeError('Historical026 controller changed')
    name = 'p3_warning_capture_026'
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
PROMPTS = old.PROMPTS


def load_bundle():
    _, scope024, prior, inherited = previous.load_bundle()
    raw = bounded(ROOT / SCOPE_PATH)
    require(sha(raw) == SCOPE_SHA256 and len(SOURCE_PINS) >= 3,
            'Unfinished027 scope or dependency pins')
    for path, digest in SOURCE_PINS.items():
        require(sha(bounded(ROOT / path, 16 * 1024 * 1024)) == digest,
                '027 dependency changed')
    scope = json.loads(raw)
    require(scope.get('scope_id') == 'P3_FINITE_REVIEW_SCOPE_027' and
            scope.get('approval_id') == 'APPROVE_P3_FINITE_REVIEW_027_CORRECTION' and
            scope.get('report_directory') == 'delivery/' + RUN_NAME,
            '027 scope identity differs')
    # The correction cannot expand a model, mount, tool, prompt or executable.
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
    require(all(scope.get(k) == scope024[k] and type(scope.get(k)) is type(scope024[k])
                for k in fixed), '027 changed the inherited operational controls')
    expected = {'native_starts_observed': 6, 'explicit_model_turns_observed': 3,
        'additional_native_processes_maximum': 2, 'additional_explicit_model_turns_maximum': 2,
        'cumulative_native_starts_maximum': 8, 'cumulative_explicit_model_turns_maximum': 5,
        'no_automatic_retry': True, 'count_sent_turn_even_without_reviewer_output': True}
    counts = scope.get('prior_attempt_accounting', {})
    require(all(counts.get(k) == v and type(counts.get(k)) is type(v) for k, v in expected.items()),
            '027 cumulative accounting or no-retry restriction differs')
    require(sha(bounded(ROOT / REPORT026_PATH)) == REPORT026_SHA256 and
            sha(bounded(ROOT / AUTH024_PATH)) == AUTH024_SHA256,
            '026 input or historical024 approval archive changed')
    return scope, prior, {'scope_sha256': SCOPE_SHA256,
        'controller_sha256': sha(bounded(Path(__file__))), 'source_pins': SOURCE_PINS,
        'inherited026_pins': inherited, 'report026_sha256': REPORT026_SHA256,
        'historical024_approval_sha256': AUTH024_SHA256,
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
    require(len(positions) == 1, 'Exactly one actual027 ANSWER is required')
    require([line for line in lines[positions[0] + 1:] if line.strip()] ==
            ['APPROVE_P3_FINITE_REVIEW_027_CORRECTION', 'scope_sha256: ' + SCOPE_SHA256],
            'Recorded answer differs from exact027 scope')
    return {'path': 'state/ESCALATION.md', 'sha256': sha(raw)}


def prior_history(pins):
    # These historical functions check receipts; neither invokes old.approval().
    inherited = pins['inherited026_pins']
    earlier = previous.prior_history(inherited)
    path = previous.existing(ROOT / 'delivery' / previous.RUN_NAME, inherited)
    require(path is not None, 'Actual026 receipt is required before new reservation')
    raw = bounded(path)
    session_raw = bounded(path.parent / 'synthetic_SESSION.json')
    require(sha(raw) == REPORT026_SHA256 and bounded(ROOT / REPORT026_PATH) == raw,
            'Actual026 report differs from archived original')
    require(sha(session_raw) == SESSION026_SHA256,
            'Actual026 SESSION missing or changed; never reconstruct it')
    require(sha(bounded(ROOT / AUTH024_PATH)) == AUTH024_SHA256,
            'Historical024 approval archive changed')
    value = json.loads(raw)
    stages = value.get('stages')
    require(value.get('history') == earlier and value.get('pins') == inherited and
            value.get('status') == 'STOPPED_DIAGNOSTIC_NO_SCIENCE' and
            value.get('science_started') is False and value.get('reviewer_output') is None and
            type(stages) is list and len(stages) == 1 and stages[0].get('stage') == 'synthetic',
            'Actual026 stage, history or provenance differs')
    observation = stages[0].get('observation')
    require(canonical(observation) == session_raw and
            all(observation.get(k) is True for k in ('client_started', 'model_turn_request_sent',
                                                     'native_process_reaped')) and
            observation.get('broker_receipts') == [] and observation.get('verdict_submitted') is False and
            stages[0].get('host_checks', {}).get('all_noncredential_checks_pass') is True and
            stages[0].get('fresh_process_and_runtime_directories') is True and
            stages[0].get('pi_conversation_imported') is False,
            'Actual026 separate session linkage or cleanup differs')
    counts = value['attempt_accounting']
    expected = {'cumulative_observed_native_starts': 6, 'cumulative_observed_sent_turns': 3,
        'cumulative_native_ceiling': 6, 'cumulative_sent_turn_ceiling': 3}
    require(all(type(counts.get(k)) is int and counts[k] == v for k, v in expected.items()),
            'Actual026 observed counts or exhausted ceiling differs')
    return {'actual019_to026_history_reverified': True, 'separate026_session_reverified': True,
        'report026_sha256': sha(raw), 'session026_sha256': sha(session_raw),
        'prior_native_starts': 6, 'prior_sent_turns': 3,
        'previous_cumulative_native_ceiling': 6, 'previous_cumulative_sent_turn_ceiling': 3,
        'new_cumulative_native_ceiling': 8, 'new_cumulative_sent_turn_ceiling': 5,
        'counters_reset': False, 'new_exact_approval_required': True}


def run_stage(scope, prior_scope, run, mode, packet, manifest_sha, expected_binding=None):
    """Fresh actual native process/state; only called after exact human approval."""
    metadata = module('gate0_postlogin_metadata')
    preflight = module('gate0_client_preflight')
    profile = module('p3_reviewer_profile_022')
    planner = module('gate0_client_mount_plan')
    broker_module = module('p3_review_broker')
    session = module('p3_reviewer_session_027')
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
    plan.update({'kind':'P3_FINITE_REVIEW_NATIVE_MOUNT_PLAN_027_v1',
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



def admitted_synthetic(stage):
    observation = stage.get('observation', {})
    return (stage.get('stage') == 'synthetic' and
        stage.get('host_checks', {}).get('all_noncredential_checks_pass') is True and
        stage.get('fresh_process_and_runtime_directories') is True and
        stage.get('pi_conversation_imported') is False and
        observation.get('status') == 'SYNTHETIC_REFUSAL_OBSERVED' and
        observation.get('selected_binding') == BINDING and
        observation.get('verdict_submitted') is False and
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
    return {'prior_native_starts': 6, 'prior_sent_turns': 3,
        'observed_native_starts_this_attempt': starts, 'observed_sent_turns_this_attempt': turns,
        'cumulative_observed_native_starts': 6 + starts, 'cumulative_observed_sent_turns': 3 + turns,
        'reserved_native_starts_this_attempt': 2, 'reserved_turns_this_attempt': 2,
        'cumulative_native_ceiling': 8, 'cumulative_sent_turn_ceiling': 5,
        'maximum_cumulative_reservation_native_starts': 8, 'maximum_cumulative_reservation_turns': 5,
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
            'Existing027 report checksum differs; preserve it')
    value = json.loads(raw)
    require(value.get('kind') == REPORT_KIND and value.get('pins') == pins and
        value.get('status') in TERMINAL and value.get('parent_credential_contents_read') is False and
        value.get('unattended_model_use_authorized') is False and
        value.get('scientific_verdict_chosen_by_parent') is False,
        'Existing027 provenance or terminal state differs')
    authorization = value.get('authorization')
    require(type(authorization) is dict and set(authorization) == {'path', 'sha256'} and
        authorization['path'] == 'state/ESCALATION.md' and
        type(authorization['sha256']) is str and len(authorization['sha256']) == 64 and
        all(c in '0123456789abcdef' for c in authorization['sha256']),
        'Existing027 authorization receipt malformed')
    attempt = json.loads(bounded(run / 'ATTEMPT.json'))
    require(attempt.get('pins') == pins and attempt.get('authorization') == authorization and
        type(attempt.get('reserved_native_starts')) is int and attempt['reserved_native_starts'] == 2 and
        type(attempt.get('reserved_turns')) is int and attempt['reserved_turns'] == 2 and
        attempt.get('automatic_retry') is False and attempt.get('science_conditioned_on_synthetic') is True,
        'Existing027 reservation journal differs from receipt')
    # Exact original approval bytes are kept beside the attempt, so later unrelated
    # answers cannot invalidate provenance or authorize a repeat operation.
    approval_raw = bounded(run / 'AUTHORIZATION.md')
    require(sha(approval_raw) == authorization['sha256'], 'Existing027 preserved authorization changed')
    requested = value.get('stage_attempts')
    require(requested in ([], ['synthetic'], ['synthetic', 'science']),
        'Existing027 attempted-stage order differs')
    stages = value.get('stages')
    require(type(stages) is list and len(stages) <= len(requested) and
        [s.get('stage') for s in stages] == requested[:len(stages)], 'Existing027 stage order differs')
    sessions, observations = collect_sessions(run)
    require(value.get('preserved_session_receipts') == sessions and
        all(mode in requested for mode in observations), 'Existing027 SESSION inventory differs')
    for stage in stages:
        linked_stage(run, stage, stage['stage'])
    require({mode for mode in ('synthetic', 'science') if os.path.lexists(run / (mode + '_STAGE.json'))}
            == {stage['stage'] for stage in stages}, 'Unrecorded027 STAGE receipt exists; preserve it')
    require(value.get('science_started') is ('science' in requested),
        'Existing027 science stage declaration differs')
    if 'science' in requested:
        require(stages and admitted_synthetic(stages[0]),
            'Existing027 science lacks separately observed synthetic admission')
    else:
        require(not any(os.path.lexists(run / p) for p in
            ('science_native', 'science_output', 'science_SESSION.json', 'science_STAGE.json')),
            'Unrecorded scientific-stage path exists')
    expected = accounting(observations, requested)
    count = value.get('attempt_accounting')
    require(type(count) is dict and set(count) == set(expected) and
        all(count[k] == v and type(count[k]) is type(v) for k, v in expected.items()),
        'Existing027 counts differ from actual SESSION or reserved capacity')
    output = value.get('reviewer_output')
    output_path = run / 'science_output/REVIEW_VERDICT.json'
    if output is None:
        require(not os.path.lexists(output_path), 'Unrecorded reviewer output exists; preserve it')
        require(value['status'] != 'REVIEWER_OUTPUT_PRESERVED', 'Completed status lacks reviewer output')
    else:
        require(type(output) is dict and output.get('path') == 'science_output/REVIEW_VERDICT.json' and
            output.get('parent_edited') is False and type(output.get('bytes')) is int and
            output.get('execution_admitted') is (value['status'] == 'REVIEWER_OUTPUT_PRESERVED'),
            'Existing027 reviewer output provenance differs')
        output_raw = bounded(output_path, 1024 * 1024)
        require(sha(output_raw) == output.get('sha256') and len(output_raw) == output['bytes'],
            'Existing027 reviewer bytes changed; preserve them')
    if value['status'] == 'REVIEWER_OUTPUT_PRESERVED':
        require(len(stages) == 2 and admitted_synthetic(stages[0]) and admitted_science(stages[1]),
            'Existing027 completion lacks actual stage admission')
    return run / 'REPORT.json'


def execute(scope, prior_scope, pins, authorization, packet_info):
    history = prior_history(pins)
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
        'pins': pins, 'authorization': authorization, 'history': history, 'status': 'STARTED',
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
        print('Inspection only. Prepared027 scope SHA256: ' + SCOPE_SHA256)
        print('Observed6starts/3sentturns exhaust prior ceiling. Exact027 approval required for8/5.')
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
