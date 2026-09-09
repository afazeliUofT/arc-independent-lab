#!/usr/bin/env python3
"""Prepared finite Sol reviewer option; a new exact human approval is required.

Owns scope, fresh process directories and the external read-only evidence broker.
No automatic retry, credential content access, scientific verdict choice or Git
mutation is implemented. The three failed Astra startup attempts and their
controllers remain unchanged. Original019 approval never admits this model change.
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
SCOPE_PATH = 'configs/P3_FINITE_REVIEW_SCOPE_022.json'
SCOPE_SHA256 = '46301a69ae7a2d0cdac537eb2127415e8d4ac3c4ab5d7e8ea00ff1a1894a9f0f'
PRIOR_SCOPE_SHA256 = '99d7f62d60b3384b5bb83923047b390f7f7e6e8d90c2654b33d996101755d5ea'
SOURCE_PINS = {
    "artifacts/GATE0_ACCOUNT_PLAN_SOURCE/20260908_001/MANIFEST.json": "f47ece02e29f93aeb14cc08ea1fc53109e13eb197465699c9ba6a4f516c70704",
    "artifacts/GATE0_CODEX_INTERFACE/20260907_001/config-schema.json": "ed663d6d4c6c8b36917596882414c93858f6cf9ca5449ea8c616fc76d1aac114",
    "artifacts/GATE0_CODEX_INTERFACE/20260907_001/schemas/experimental.json": "dd4014851ef7c60ecacfa5fa4d1a9f02d7dcc2aada93c83091a717b27b753d63",
    "artifacts/GATE0_CODEX_STARTUP/20260907_001/codex-rs/app-server/src/message_processor.rs": "14d505d87205a3a54515231770c38d56012316cb1f4b5a30e2c76c49341cc047",
    "artifacts/GATE0_CODEX_STARTUP/20260907_001/codex-rs/app-server/src/models_refresh_worker.rs": "f4946acbb956e73240b9df23ae5e7ee8c4516414c587834c2b1389f346de81ce",
    "artifacts/GATE0_CODEX_STARTUP/20260907_001/codex-rs/models-manager/src/manager.rs": "00a120284c6b1c6549fa39ae938a72cb6cfd40f683878fabdcc22f9216799f9c",
    "artifacts/GATE0_CODEX_STARTUP/20260907_002/codex-rs/core/src/client.rs": "113bde60551abdbf96e3603b4f1754a072886e712ef0d0049f360a64dddec375",
    "artifacts/GATE0_POSTLOGIN_OBSERVATIONS/20260908_001/REPORT.json": "4aa0757da0d56a4db65ca7a33cf15d7454129c21fab7283457261d3a8ebcbba7",
    "artifacts/GATE0_REVIEWER_EFFECT_SOURCE/20260908_001/MANIFEST.json": "88f6567051f17865584d5b0a90c9d655c3c0819b77a25d636333eb71363cdee1",
    "artifacts/GATE0_SUBSCRIPTION_SOURCE/20260907_001/codex-rs/app-server/src/models.rs": "9b40a490876faea4213a6e7617335f3642c50866434a61de362e52a1077e21fd",
    "artifacts/GATE0_SUBSCRIPTION_SOURCE/20260907_001/codex-rs/app-server/src/request_processors/catalog_processor.rs": "af01a1d91a6ccb3c384cea75aacd519846e60e45ae91b03cf80b928be8cd412f",
    "artifacts/GATE0_SUBSCRIPTION_SOURCE/20260907_001/codex-rs/model-provider/src/provider.rs": "d913ea476d4e93ecfa85b96719d2eaa82e8b4d8d796b0b963b6ab67535e4250a",
    "artifacts/GATE0_TOOL_BOUNDARY_SOURCE/20260907_001/codex-rs/core/src/session/multi_agents.rs": "2ea650cdededf56c2a94425be7a3c5323f200f675acc543cd281a3d1d0ea0c80",
    "artifacts/GATE0_TOOL_BOUNDARY_SOURCE/20260907_001/codex-rs/models-manager/src/cache.rs": "97d64ab915c9736f409ceef9c0e71f018c7bfeb4c14060d4bda0453ba835a152",
    "artifacts/P3_CONFIG_ORIGIN_SOURCE/20260909_001/ADMISSION_VALIDATION.json": "ecf42bc4d549595d3d93fd2864b94cebff18808bdccf9a90b1b3a9c27836aa9c",
    "artifacts/P3_CONFIG_ORIGIN_SOURCE/20260909_001/CONSULTATION.md": "be3f24b236d9c1e6d2bf2fbfe579d8651d63099d4424645f06f0441856297735",
    "artifacts/P3_CONFIG_ORIGIN_SOURCE/20260909_001/GITHUB_BLOB_IDENTITIES.json": "acd588523bd1d91b9f1562b195c46ecb2e7be1e4a6fc480a0312ff7b79ffc90d",
    "artifacts/P3_CONFIG_ORIGIN_SOURCE/20260909_001/LICENSE": "d17f227e4df5da1600391338865ce0f3055211760a36688f816941d58232d8dc",
    "artifacts/P3_CONFIG_ORIGIN_SOURCE/20260909_001/MANIFEST.json": "7bf4edcf21565174afd7abe9f3b5b13406823995145d871d50e9bc8ca7853a60",
    "artifacts/P3_CONFIG_ORIGIN_SOURCE/20260909_001/NOTICE": "9d71575ecfd9a843fc1677b0efb08053c6ba9fd686a0de1a6f5382fd3c220915",
    "artifacts/P3_CONFIG_ORIGIN_SOURCE/20260909_001/OFFLINE_REPRODUCTION.json": "babebe6316110bc8e8c1ff5368a916bced705b46ef31a19ea715526facb7cc05",
    "artifacts/P3_CONFIG_ORIGIN_SOURCE/20260909_001/SEARCH_OBSERVATIONS.json": "9f373cb22406d0436dbdf2e507c5c13ce440e36abc100b4696715df8efc6f3b5",
    "artifacts/P3_CONFIG_ORIGIN_SOURCE/20260909_001/codex-rs/config/src/config_layer_source.rs": "6816bf7bd44b1f2799aae30331b77a7e8231ccacdc4cd3d44d6485f9e1118364",
    "artifacts/P3_CONFIG_ORIGIN_SOURCE/20260909_001/codex-rs/config/src/fingerprint.rs": "efc9fb8365a1bfaf4d27933a495624f2763c429789bb1a6399c68ae271e305ca",
    "artifacts/P3_CONFIG_ORIGIN_SOURCE/20260909_001/codex-rs/config/src/key_aliases.rs": "a99676453589c93c57288bc7c17c3a171f9ba13c2bfad5dbf1b067489df68a6c",
    "artifacts/P3_CONFIG_ORIGIN_SOURCE/20260909_001/codex-rs/features/src/feature_configs.rs": "6e60306024c738e9d17a20b0ea0d2c5f91f66dccfd62bc708ebd9141e507b476",
    "artifacts/P3_CONFIG_ORIGIN_SOURCE/20260909_001/codex-rs/features/src/lib.rs": "62ac7c6f6109a1e984a0257aa1096753094b5d9dca9d638d19d75dc07b0c7940",
    "artifacts/P3_CONFIG_ORIGIN_SOURCE/20260909_001/reproduce_origin_contract_021.py": "e186cae205c3db8875caa1168e34eb82af6adb5795d385e32adcc611d98b2f47",
    "artifacts/P3_CONFIG_WARNING_SOURCE/20260909_001/CONSULTATION.md": "4386369bb2bd8c95f92babaf143494174b7236c02a633591972c0469f3816fab",
    "artifacts/P3_CONFIG_WARNING_SOURCE/20260909_001/ConfigWarningNotification.json": "533e713405b582cce4d772d0b4ebbc75e840f0fe71cedbb17c2c83da285a21d4",
    "artifacts/P3_CONFIG_WARNING_SOURCE/20260909_001/FETCH_ERRORS.json": "f9ffb8602d2affc348f78e19a4a8d1c68c029dd874a7f57c3afaea1a57d142ad",
    "artifacts/P3_CONFIG_WARNING_SOURCE/20260909_001/FETCH_METADATA.json": "194542d04d32398b04a0bb018692a786940418bfb74bae13baf08d99c9cbe92b",
    "artifacts/P3_CONFIG_WARNING_SOURCE/20260909_001/LICENSE": "d17f227e4df5da1600391338865ce0f3055211760a36688f816941d58232d8dc",
    "artifacts/P3_CONFIG_WARNING_SOURCE/20260909_001/MANIFEST.json": "b81d453cb840b243dad9f7e123a851be4144db94550573e8fcb149d5cef1c6c1",
    "artifacts/P3_CONFIG_WARNING_SOURCE/20260909_001/NOTICE": "9d71575ecfd9a843fc1677b0efb08053c6ba9fd686a0de1a6f5382fd3c220915",
    "artifacts/P3_CONFIG_WARNING_SOURCE/20260909_001/TREE_IDENTITY.json": "ac2a35580e4b6172c634058523ac908253870cb127e0908f83bc818cd7207777",
    "artifacts/P3_CONFIG_WARNING_SOURCE/20260909_001/codex-rs/app-server/src/request_processors/initialize_processor.rs": "6e73dce0275c7264b23ee0a312f215fead241ce55dc1a86fa1dbd109ad4278e0",
    "artifacts/P3_CONFIG_WARNING_SOURCE/20260909_001/codex-rs/sandboxing/src/bwrap.rs": "43abc86eb6a62689c6aa75dc27f6cd05101cab831b339d4e85e316c1c296d19c",
    "artifacts/P3_CONFIG_WARNING_SOURCE/20260909_001/codex-rs/sandboxing/src/lib.rs": "33d4349a394bd02f729d015d818da34bbd262cb7a1632ae58efb4b7881d9e7c6",
    "artifacts/P3_FINITE_REVIEW_CORRECTION_OBSERVATIONS/20260909_001/REPORT.json": "d9e52a7c7401651e482945c9d30786abde6f63d10fcb2412c7b92017b42635e7",
    "artifacts/P3_FINITE_REVIEW_MODEL_OBSERVATIONS/20260909_001/REPORT.json": "d024d5b1ec85cce7ec61f36e7f5594efe0b37d7e2eb6db7ca6d4b2094115631c",
    "artifacts/P3_FINITE_REVIEW_OBSERVATIONS/20260909_001/REPORT.json": "2725b63acd12a09a89041760ca9ea21f0f004a0ece1a6e4d2b7df125a48d54f6",
    "artifacts/P3_MODEL_CATALOG_SOURCE/20260909_001/CONSULTATION.md": "09fd45a3862c68a6cb441676b6e6e8ba768bed982fb76ddc457c11e9369ab01b",
    "artifacts/P3_MODEL_CATALOG_SOURCE/20260909_001/LICENSE": "d17f227e4df5da1600391338865ce0f3055211760a36688f816941d58232d8dc",
    "artifacts/P3_MODEL_CATALOG_SOURCE/20260909_001/MANIFEST.json": "45a8991fafa7937eeaab275d08bba172101b85c7a9b5396e54953a1f2176c068",
    "artifacts/P3_MODEL_CATALOG_SOURCE/20260909_001/ModelListParams.json": "de29a536c00a5b8f46f34dba417dabd93365305571a8ed200e33bea85db68b5a",
    "artifacts/P3_MODEL_CATALOG_SOURCE/20260909_001/ModelListResponse.json": "c7b58b332f6cf18fd64235409a6daf27bb9e6c09d12dcd0daa2f3dc628b55f6f",
    "artifacts/P3_MODEL_CATALOG_SOURCE/20260909_001/NOTICE": "9d71575ecfd9a843fc1677b0efb08053c6ba9fd686a0de1a6f5382fd3c220915",
    "artifacts/P3_MODEL_CATALOG_SOURCE/20260909_001/SHA256SUMS": "cda1c2e605d1966facb9415816d01184b0dcf0e890895555845b7bbd304a6dfb",
    "artifacts/P3_MODEL_CATALOG_SOURCE/20260909_001/SOURCE_RECHECK.json": "7862631b0004526a91904d64fdcea90de194a49c8c9dfd7b5271c45d95c1628a",
    "artifacts/P3_MODEL_CATALOG_SOURCE/20260909_001/SOURCE_REFERENCES.json": "7d503fcf0d957899864e2636a64c2b6eaf603b499b442a0ffd4b744aeaa08c73",
    "artifacts/P3_MODEL_CATALOG_SOURCE/20260909_001/SOURCE_TREE_SELECTION.json": "777d22266bd9bc02694c610d003f0c3a54a2c6001b05f766a0cb3f3c0d95f8da",
    "artifacts/P3_MODEL_CATALOG_SOURCE/20260909_001/TOOL_ERRORS.jsonl": "ae80503a3adc28ae20ff78ae4090d5e04fff9b5451a3917f113d77ea898b12d3",
    "artifacts/P3_MODEL_CATALOG_SOURCE/20260909_001/codex-rs/models-manager/models.json": "eb0d7b9a5dcaf103895c5f8a14c16b269df46e039b375a55ba97f6238542d2ed",
    "artifacts/P3_MODEL_CATALOG_SOURCE/20260909_001/codex-rs/models-manager/src/lib.rs": "b31b6e8fdaebedbbf07999b27c02201020e8d876ae293ac05a8fe4bf051244d3",
    "artifacts/P3_MODEL_CATALOG_SOURCE/20260909_001/codex-rs/protocol/src/openai_models.rs": "8ec03e1382ef5bc4350c93262d1eb8833c7462057e2e995887c6e147deb63758",
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
    "scripts/p3_config_warning.py": "60461b6493a37c917c86578b640de42fb780cd50246932058356594136048463",
    "scripts/p3_finite_review.py": "187cfab78d43736728294f45ee8a6004590766490fe0af98e8b711be71e734f1",
    "scripts/p3_finite_review_020.py": "a88512ebe176a593556dc728d562ab50f392e272f0347cf756db2addf26911f5",
    "scripts/p3_finite_review_021.py": "ee0189800a94643a52a7082b7c447f93bc0dd917b4ba45b492cb3fc052f14966",
    "scripts/p3_review_broker.py": "6f2118cb32573c7774db269c09694913040d06adb5eca9e8ca1a0fafe6089536",
    "scripts/p3_review_protocol.py": "9bc4315dc3d6af679890828db5a1ee5ef19f49e2c7214cc0dd384728a9cf754f",
    "scripts/p3_reviewer_admission.py": "9b589287b6b56ad56e12075d655d0c9935a570076a35544fa64a40973b6969cb",
    "scripts/p3_reviewer_admission_021.py": "f70408e71322ca582935f1b04431302a2a910ab1c561aa8fae5a261bdb361860",
    "scripts/p3_reviewer_admission_022.py": "329bccdfba14c93bb345841e6764b00f911b1ab8e3067636879a8a58194a783e",
    "scripts/p3_reviewer_profile.py": "669da4f8bae0cac3f43433ebc2b462da607be631b259d7ff08919b8f1130991f",
    "scripts/p3_reviewer_profile_022.py": "3c1d66ace2c3441d3c1ce1da98f2ec9bd253d3fe470b03d5ff54ec7ee7eeaa4d",
    "scripts/p3_reviewer_session.py": "6ab41524d9759fd26e4f63b75a8f5a4cdad867906434ecb57aee106a9e70066d",
    "scripts/p3_reviewer_session_020.py": "7d3d3b0533fe23a675c477aa2b753fc01b0486339a38b36b6ced2a69971da1a1",
    "scripts/p3_reviewer_session_021.py": "32f0eaff8b4c68a8ab270e691cae204c9f95e54618b2651173b825e9d5442c2e",
    "scripts/p3_reviewer_session_022.py": "fce5d0707ed16a0155cf0852e4e7d5e37d715ef14c33400c244a5f183b5c1730"
}
REQUIRED_CORRECTION_PINS = frozenset({
    'scripts/p3_finite_review_021.py',
    'scripts/p3_reviewer_profile_022.py',
    'scripts/p3_reviewer_session_022.py',
    'scripts/p3_reviewer_admission_022.py',
    'artifacts/P3_FINITE_REVIEW_MODEL_OBSERVATIONS/20260909_001/REPORT.json',
    'artifacts/P3_MODEL_CATALOG_SOURCE/20260909_001/MANIFEST.json',
})
RUN_NAME = 'P3_FINITE_REVIEW_022'
REPORT_KIND = 'P3_FINITE_REVIEW_022_v1'
PRIOR_REPORT_SHA256 = 'd024d5b1ec85cce7ec61f36e7f5594efe0b37d7e2eb6db7ca6d4b2094115631c'
APPROVAL_ARCHIVE = 'state/escalations/2026-09-09_FINITE_REVIEW_022_APPROVED.md'
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
    require(sha(raw) == SCOPE_SHA256 and bool(SOURCE_PINS) and
            REQUIRED_CORRECTION_PINS <= SOURCE_PINS.keys(),
            'Unfinished or changed review scope/pins')
    for name, expected in SOURCE_PINS.items():
        require(sha(bounded(ROOT / name, 16 * 1024 * 1024)) == expected,
                'Pinned reviewer dependency changed')
    scope = json.loads(raw)
    require(scope.get('scope_id') == 'P3_FINITE_REVIEW_SCOPE_022' and
            scope.get('approval_id') == 'APPROVE_P3_FINITE_REVIEW_022_SOL' and
            scope.get('model_policy', {}).get('requested_identity') == 'gpt-5.6-sol' and
            scope.get('model_policy', {}).get('requested_effort') == 'max' and
            scope.get('model_policy', {}).get('automatic_model_or_provider_fallback') is False and
            scope.get('report_directory') == 'delivery/' + RUN_NAME,
            'Scope does not prescribe this exact Sol reviewer option')
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
    profile = module('p3_reviewer_profile_022')
    planner = module('gate0_client_mount_plan')
    broker_module = module('p3_review_broker')
    session = module('p3_reviewer_session_022')
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
    plan.update({'kind':'P3_FINITE_REVIEW_NATIVE_MOUNT_PLAN_022_v1',
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


def prior_failed_attempt():
    """Verify all three preserved Astra attempts without any native operation.

    Historical controllers verify their own scope, pinned code and session files.
    The exact021 receipt must record the same two older receipts that its original
    validator rechecks now. The proposed022 approval is a distinct scope and may
    never replace the historical019 scope when verifying that evidence chain.
    """
    correction = module('p3_finite_review_021')
    try:
        _, _, correction_pins = correction.load_bundle()
        path = correction.existing(ROOT / 'delivery' / correction.RUN_NAME, correction_pins)
        require(path is not None, 'The preserved021 Astra attempt is required')
        raw = bounded(path)
        require(sha(raw) == PRIOR_REPORT_SHA256,
                'Correction021 report differs; preserve it and stop')
        earlier_attempts = correction.prior_failed_attempt()
    except (correction.Stop, OSError, ValueError, KeyError, TypeError):
        raise Stop('Prior019/020/021 receipts, pins or session files differ; preserve them') from None
    value = json.loads(raw)
    stages = value.get('stages')
    require(type(stages) is list and len(stages) == 1 and
            type(stages[0]) is dict and stages[0].get('stage') == 'synthetic' and
            value.get('reviewer_output') is None and
            value.get('status') == 'STOPPED_WITHOUT_COMPLETED_REVIEW',
            'Prior021 stage or completion differs; no new option admitted')
    observed = stages[0].get('observation')
    require(type(observed) is dict and
            observed.get('client_started') is True and
            observed.get('native_process_reaped') is True and
            observed.get('thread_request_sent') is False and
            observed.get('model_turn_request_sent') is False and
            observed.get('model_turn_request_queued') is False and
            observed.get('verdict_submitted') is False,
            'Prior021 operation or cleanup differs; no new option admitted')
    require(type(earlier_attempts) is dict and
            earlier_attempts.get('prior_failed_native_processes') == 2 and
            earlier_attempts.get('prior_explicit_model_turns') == 0 and
            earlier_attempts.get('access_scope_sha256') == PRIOR_SCOPE_SHA256 and
            value.get('prior_attempt') == earlier_attempts,
            'Prior019/020/021 cumulative receipt differs; no new option admitted')
    return {'report_path':str(path.relative_to(ROOT)), 'report_sha256':sha(raw),
            'unchanged_correction021_receipt_verified':True,
            'earlier_attempts':earlier_attempts,
            'prior_explicit_model_turns':0, 'prior_failed_native_processes':3,
            'all_three_prior_attempts_preserved':True,
            'access_scope_sha256':PRIOR_SCOPE_SHA256,
            'proposed_access_scope_sha256':SCOPE_SHA256,
            'new_scope_requires_exact_human_approval_and_launch':True,
            'new_invocation_native_processes_maximum':2,
            'cumulative_native_processes_maximum_including_failed_attempts':5,
            'cumulative_explicit_model_turns_maximum':2}


def execute(scope, prior_scope, pins, authorization, packet_info):
    prior_attempt = prior_failed_attempt()
    run = ROOT / 'delivery' / RUN_NAME
    new_directory(run)
    exclusive_json(run / 'ATTEMPT.json', {'created_utc':datetime.now(timezone.utc).isoformat(),
        'pins':pins,'authorization':authorization,'automatic_retry':False})
    result = {'kind':REPORT_KIND,'created_utc':datetime.now(timezone.utc).isoformat(),
        'pins':pins,'authorization':authorization,'status':'STARTED','stages':[],
        'parent_credential_contents_read':False,'unattended_model_use_authorized':False,
        'continuous_human_attendance_verified':False,'scientific_verdict_chosen_by_parent':False,
        'reviewer_output':None,'raw_native_logs_or_protocol_in_report':False,
        'actual_native_tool_denials_inferred_from_nonuse':False,'model_calls_authorized_maximum':2,
        'prior_attempt':prior_attempt,
        'model_change':{'prior_requested_identity':'gpt-6-astra',
                        'requested_identity':'gpt-5.6-sol', 'requested_effort':'max',
                        'automatic_fallback':False, 'new_exact_scope_approval_required':True}}
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
        print('Prepared Sol option scope SHA256: '+SCOPE_SHA256)
        print('Preserves all three Astra attempts; original019 approval does not admit this model change.')
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
