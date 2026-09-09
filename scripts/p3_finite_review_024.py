#!/usr/bin/env python3
"""Prepared finite Sol reviewer correction; a new exact human approval is required.

Owns scope, fresh process directories and the external read-only evidence broker.
No automatic retry, credential content access, scientific verdict choice or Git
mutation is implemented. All four prior attempts and historical
controllers remain unchanged. Prior022 approval cannot enlarge its cumulative limits.
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
SCOPE_PATH = 'configs/P3_FINITE_REVIEW_SCOPE_024.json'
SCOPE_SHA256 = 'bdf0d9cb689793656c8616f72f2f1a6a45a6bc4a6cf5abed3e0e0e4dde8ee0db'
PRIOR_SCOPE_SHA256 = '46301a69ae7a2d0cdac537eb2127415e8d4ac3c4ab5d7e8ea00ff1a1894a9f0f'
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
# Append-only024 dependencies; the82 historical022 pins above are unchanged.
# Every completed024 source snapshot and local manifest member is pinned here.
SOURCE_PINS.update({
    "artifacts/P3_DEPRECATION_SOURCE/20260909_REBUILD024/CONSULTATION.md": "d91e22cc4586d1ea61c3498eda5d62441b7771a742186c059ed093a86b0d1e5f",
    "artifacts/P3_DEPRECATION_SOURCE/20260909_REBUILD024/EXPECTED_NOTICES.json": "86077981a1e5f9634d70fc686ebaed36ed179138cef6b12c2d8bf1d12404b4cc",
    "artifacts/P3_DEPRECATION_SOURCE/20260909_REBUILD024/MANIFEST.json": "67df8a7a63436e3d27b02363833bb36be7203f57bbddc103cf56d0eb62adb6f5",
    "artifacts/P3_DEPRECATION_SOURCE/20260909_REBUILD024/SOURCE_METADATA.json": "7fef98fca0f85ce9fdbf21fb78bdbab998898c4029747e754a0cb3e06425c12f",
    "artifacts/P3_DEPRECATION_SOURCE/20260909_REBUILD024/source/codex-rs/Cargo.toml": "8d7b9cfcae32c9da39e2b9a3820db062fdb4ca31477ea0a471510fb76f6ce9dc",
    "artifacts/P3_DEPRECATION_SOURCE/20260909_REBUILD024/source/codex-rs/app-server-protocol/src/protocol/common.rs": "f67267aa0645d50ee997334036f26ef8d7b3ed42f7c79afa33e6ebb507c0c45d",
    "artifacts/P3_DEPRECATION_SOURCE/20260909_REBUILD024/source/codex-rs/app-server-protocol/src/protocol/v2/notification.rs": "a514af3960b8b18f716a894941aa170ef80660d86ba494ed625921b64cfae22a",
    "artifacts/P3_DEPRECATION_SOURCE/20260909_REBUILD024/source/codex-rs/app-server/src/bespoke_event_handling.rs": "787f086b232c147b60254886ce985f78b3fee61ffdb4b834b05eeb99a9129c26",
    "artifacts/P3_DEPRECATION_SOURCE/20260909_REBUILD024/source/codex-rs/core/src/session/session.rs": "904e6f3d9457273283742d4a0bd50101fd76c74ce826d8cadddbb4ff5c6df6a1",
    "artifacts/P3_DEPRECATION_SOURCE/20260909_REBUILD024/source/codex-rs/core/tests/suite/deprecation_notice.rs": "b52eda492b3977c8e9ed626451e2c72f308abd0b7adf3576489550097914d7e4",
    "artifacts/P3_DEPRECATION_SOURCE/20260909_REBUILD024/source/codex-rs/features/src/legacy.rs": "5899d34d8335ccaa45d8f34d9ed3d54e80e7c518c02733ad54e8014e5a5dd52a",
    "artifacts/P3_DEPRECATION_SOURCE/20260909_REBUILD024/source/codex-rs/features/src/lib.rs": "62ac7c6f6109a1e984a0257aa1096753094b5d9dca9d638d19d75dc07b0c7940",
    "artifacts/P3_FINITE_REVIEW_DEPRECATION_OBSERVATIONS/20260909_REBUILD024/REPORT.json": "ce5af6d5d8ae3e6a332ce5289af60a8b4633ef101892aba8d92b2c383e13372c",
    "configs/P3_FINITE_REVIEW_SCOPE_022.json": "46301a69ae7a2d0cdac537eb2127415e8d4ac3c4ab5d7e8ea00ff1a1894a9f0f",
    "scripts/p3_deprecation_notice.py": "bace2c079803f87c36e79784b7be7b84d715fb2d9443d96f6a19fe4c5f60188b",
    "scripts/p3_finite_review_022.py": "ef9b1bb0b19e3d8687aac88d70f268183f00c435c789420e47996211ea09e116",
    "scripts/p3_reviewer_session_024.py": "072e8376ab6e6e2c41b2dea2838d4126024b1fad615aa497c696dd704747551e",
    "state/escalations/2026-09-09_SOL_REVIEW_022_APPROVED.md": "19aecf27fc839b9a066fd099645de38880af8e3dd75b702caf32310ded8d082a"
})
REQUIRED_CORRECTION_PINS = frozenset({
    'scripts/p3_finite_review_022.py',
    'configs/P3_FINITE_REVIEW_SCOPE_022.json',
    'scripts/p3_deprecation_notice.py',
    'scripts/p3_reviewer_session_024.py',
    'artifacts/P3_DEPRECATION_SOURCE/20260909_REBUILD024/MANIFEST.json',
    'artifacts/P3_FINITE_REVIEW_DEPRECATION_OBSERVATIONS/20260909_REBUILD024/REPORT.json',
    'state/escalations/2026-09-09_SOL_REVIEW_022_APPROVED.md',
    'scripts/p3_finite_review_021.py',
    'scripts/p3_reviewer_profile_022.py',
    'scripts/p3_reviewer_session_022.py',
    'scripts/p3_reviewer_admission_022.py',
    'artifacts/P3_FINITE_REVIEW_MODEL_OBSERVATIONS/20260909_001/REPORT.json',
    'artifacts/P3_MODEL_CATALOG_SOURCE/20260909_001/MANIFEST.json',
})
RUN_NAME = 'P3_FINITE_REVIEW_024'
REPORT_KIND = 'P3_FINITE_REVIEW_024_v1'
PRIOR_REPORT_SHA256 = 'ce5af6d5d8ae3e6a332ce5289af60a8b4633ef101892aba8d92b2c383e13372c'
PRIOR_SESSION_SHA256 = '78577773614c0710e18d6e488635a71f15e59ead76fd1c39ca070b9ac50571f5'
PRIOR_AUTHORIZATION_SHA256 = '19aecf27fc839b9a066fd099645de38880af8e3dd75b702caf32310ded8d082a'
PRIOR_REPORT_ARCHIVE = 'artifacts/P3_FINITE_REVIEW_DEPRECATION_OBSERVATIONS/20260909_REBUILD024/REPORT.json'
PRIOR_APPROVAL_ARCHIVE = 'state/escalations/2026-09-09_SOL_REVIEW_022_APPROVED.md'
APPROVAL_ARCHIVE = 'state/escalations/2026-09-09_FINITE_REVIEW_024_APPROVED.md'
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
            REQUIRED_CORRECTION_PINS <= SOURCE_PINS.keys() and
            all(type(digest) is str and len(digest) == 64 and
                all(char in '0123456789abcdef' for char in digest)
                for digest in SOURCE_PINS.values()),
            'Unfinished or changed review scope/pins')
    for name, expected in SOURCE_PINS.items():
        require(sha(bounded(ROOT / name, 16 * 1024 * 1024)) == expected,
                'Pinned reviewer dependency changed')
    scope = json.loads(raw)
    require(scope.get('scope_id') == 'P3_FINITE_REVIEW_SCOPE_024' and
            scope.get('approval_id') == 'APPROVE_P3_FINITE_REVIEW_024_CORRECTION' and
            scope.get('model_policy', {}).get('requested_identity') == 'gpt-5.6-sol' and
            scope.get('model_policy', {}).get('requested_effort') == 'max' and
            scope.get('model_policy', {}).get('automatic_model_or_provider_fallback') is False and
            scope.get('report_directory') == 'delivery/' + RUN_NAME,
            'Scope does not prescribe this exact Sol reviewer option')
    require(scope['maximum_native_processes'] == 2 and scope['maximum_model_turns'] == 2,
            'Unexpected review process/turn limits')
    require(scope['synthetic_seconds_including_cleanup'] == 600 and
            scope['scientific_seconds_including_cleanup'] == 3600 and
            scope['cleanup_seconds_per_process'] == 4 and
            scope['maximum_run_attempts_per_invocation'] == 1,
            'Unexpected finite review timing or attempt limit')
    accounting = scope['prior_attempt_accounting']
    require(accounting['native_starts_observed'] == 4 and
            accounting['explicit_model_turns_observed'] == 1 and
            accounting['additional_native_processes_maximum'] == 2 and
            accounting['additional_explicit_model_turns_maximum'] == 2 and
            accounting['cumulative_native_starts_maximum'] == 6 and
            accounting['cumulative_explicit_model_turns_maximum'] == 3 and
            accounting['previous022_cumulative_native_starts_maximum'] == 5 and
            accounting['previous022_cumulative_explicit_model_turns_maximum'] == 2 and
            accounting['no_automatic_retry'] is True and
            accounting['count_sent_turn_even_without_reviewer_output'] is True,
            'Prior starts or sent turn cannot be reset')
    historical = module('p3_finite_review_022')
    require(all(SOURCE_PINS.get(name) == digest
                for name, digest in historical.SOURCE_PINS.items()) and
            historical.SCOPE_SHA256 == PRIOR_SCOPE_SHA256,
            'Historical022 dependency map or scope was changed')
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
    require(value.get('status') in (
        'REVIEWER_OUTPUT_PRESERVED', 'STOPPED_WITHOUT_REVIEWER_VERDICT',
        'STOPPED_WITHOUT_COMPLETED_REVIEW', 'INTERRUPTED_PARTIAL_PRESERVED'),
        'Previous review receipt is not terminal; preserve it')
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
    session = module('p3_reviewer_session_024')
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
    plan.update({'kind':'P3_FINITE_REVIEW_NATIVE_MOUNT_PLAN_024_v1',
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
    """Reverify actual canonical019/020/021/022 execution evidence; never rebuild it.

    The reattached report is an archive, not a replacement for the separate
    laptop execution SESSION. Unchanged022 validators recheck their own pins
    and all three earlier attempts before024 admits any fresh native start.
    """
    correction = module('p3_finite_review_022')
    try:
        _, _, correction_pins = correction.load_bundle()
        earlier_attempts = correction.prior_failed_attempt()
        path = correction.existing(ROOT / 'delivery' / correction.RUN_NAME, correction_pins)
        require(path is not None, 'The actual preserved022 attempt is required')
        raw = bounded(path)
        require(sha(raw) == PRIOR_REPORT_SHA256 and
                bounded(ROOT / PRIOR_REPORT_ARCHIVE) == raw,
                'Canonical022 report differs from the recorded reattachment; preserve it')
        session_raw = bounded(path.parent / 'synthetic_SESSION.json')
        require(sha(session_raw) == PRIOR_SESSION_SHA256,
                'Actual canonical022 SESSION differs or is missing; never reconstruct it')
        require(sha(bounded(ROOT / PRIOR_APPROVAL_ARCHIVE)) == PRIOR_AUTHORIZATION_SHA256,
                'Historical022 approval archive differs; preserve it')
    except (correction.Stop, OSError, ValueError, KeyError, TypeError):
        raise Stop('Prior019/020/021/022 actual receipts, pins or session files differ or are absent; preserve them') from None
    value = json.loads(raw)
    require(value.get('kind') == correction.REPORT_KIND and
            value.get('pins') == correction_pins and
            value.get('authorization') == {
                'path': 'state/ESCALATION.md', 'sha256': PRIOR_AUTHORIZATION_SHA256} and
            value.get('parent_credential_contents_read') is False and
            value.get('unattended_model_use_authorized') is False and
            value.get('scientific_verdict_chosen_by_parent') is False,
            'Prior022 kind, pins, authorization or scope differs')
    stages = value.get('stages')
    require(type(stages) is list and len(stages) == 1 and
            type(stages[0]) is dict and stages[0].get('stage') == 'synthetic' and
            value.get('reviewer_output') is None and
            value.get('status') == 'STOPPED_WITHOUT_COMPLETED_REVIEW' and
            value.get('preserved_session_receipts') == [{
                'path': 'synthetic_SESSION.json', 'sha256': PRIOR_SESSION_SHA256}],
            'Prior022 stage, session inventory or completion differs')
    observed = stages[0].get('observation')
    require(type(observed) is dict and
            observed.get('kind') == 'P3_FINITE_REVIEWER_SESSION_022_v1' and
            observed.get('mode') == 'synthetic' and
            observed.get('status') == 'STOPPED_WITHOUT_VERDICT' and
            observed.get('client_started') is True and
            observed.get('native_process_reaped') is True and
            observed.get('thread_request_sent') is True and
            observed.get('model_turn_request_sent') is True and
            observed.get('model_turn_request_queued') is True and
            observed.get('verdict_submitted') is False and
            observed.get('synthetic_allowed_read_observed') is False and
            observed.get('observed_refusal') is False and
            observed.get('automatic_retry_requested') is False and
            observed.get('server_requests_dispatched') == 0 and
            observed.get('broker_receipts') == [] and
            observed.get('last_notification_type') == 'deprecationNotice' and
            observed.get('reason') == 'Unadvertised native notification effect' and
            observed.get('selected_binding') == {
                'model': 'gpt-5.6-sol', 'id': 'gpt-5.6-sol', 'effort': 'max'},
            'Prior022 sent-turn, zero-broker stop or cleanup differs')
    turn_binding = observed.get('turn_binding')
    require(type(turn_binding) is dict and
            set(turn_binding) == {'thread_id', 'turn_id'} and
            all(type(turn_binding[key]) is str and turn_binding[key]
                for key in ('thread_id', 'turn_id')),
            'Prior022 accepted turn binding is absent')
    embedded_raw = (json.dumps(observed, indent=2, ensure_ascii=True,
                               allow_nan=False) + '\n').encode()
    require(sha(embedded_raw) == PRIOR_SESSION_SHA256 and
            session_raw == embedded_raw,
            'Actual022 SESSION and canonical embedded observation differ')
    require(stages[0].get('host_checks', {}).get('all_noncredential_checks_pass') is True and
            stages[0].get('pi_conversation_imported') is False and
            stages[0].get('fresh_process_and_runtime_directories') is True,
            'Prior022 host or context receipt differs')
    require(type(earlier_attempts) is dict and
            earlier_attempts.get('prior_failed_native_processes') == 3 and
            earlier_attempts.get('prior_explicit_model_turns') == 0 and
            earlier_attempts.get('proposed_access_scope_sha256') == PRIOR_SCOPE_SHA256 and
            value.get('prior_attempt') == earlier_attempts,
            'Prior019/020/021/022 cumulative receipt differs')
    return {'report_path': str(path.relative_to(ROOT)), 'report_sha256': sha(raw),
            'report_archive_path': PRIOR_REPORT_ARCHIVE,
            'session_path': 'delivery/P3_FINITE_REVIEW_022/synthetic_SESSION.json',
            'session_sha256': sha(session_raw),
            'actual_canonical_report_and_session_verified': True,
            'canonical_embedded_observation_matches_actual_session': True,
            'unchanged022_scope_pins_and_authorization_verified': True,
            'earlier_attempts': earlier_attempts,
            'prior_explicit_model_turns': 1, 'prior_failed_native_processes': 4,
            'prior_native_starts_observed': 4,
            'all_four_prior_attempts_preserved': True,
            'prior022_explicit_synthetic_turn_sent_and_accepted': True,
            'prior022_broker_calls_observed': 0,
            'prior022_reviewer_output_observed': False,
            'token_usage_or_subscription_charge': 'unknown',
            'access_scope_sha256': PRIOR_SCOPE_SHA256,
            'proposed_access_scope_sha256': SCOPE_SHA256,
            'new_scope_requires_exact_human_approval_and_launch': True,
            'new_invocation_native_processes_maximum': 2,
            'new_invocation_explicit_model_turns_maximum': 2,
            'previous022_cumulative_native_processes_maximum': 5,
            'previous022_cumulative_explicit_model_turns_maximum': 2,
            'cumulative_native_processes_maximum_including_failed_attempts': 6,
            'cumulative_explicit_model_turns_maximum': 3,
            'no_counter_reset': True}


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
        'model_policy':{'requested_identity':'gpt-5.6-sol', 'requested_effort':'max',
                        'unchanged_from022':True, 'automatic_fallback':False},
        'correction':{'deprecation_notice_handler':'P3_DEPRECATION_NOTICE_024_REBUILT_v1',
                      'fresh_synthetic_then_fresh_science_required':True,
                      'new_exact_scope_approval_required':True,
                      'prior_cumulative_limits':{'native_starts':5,'explicit_model_turns':2},
                      'new_cumulative_limits':{'native_starts':6,'explicit_model_turns':3},
                      'token_usage_or_subscription_charge':'unknown'}}
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
    observed_starts, observed_turns, recorded_modes = 0, 0, []
    for mode in ('synthetic', 'science'):
        path = run / (mode + '_SESSION.json')
        if path.exists():
            raw = bounded(path)
            result['preserved_session_receipts'].append({'path':path.name,'sha256':sha(raw)})
            observation = json.loads(raw)
            observed_starts += int(observation.get('client_started') is True)
            observed_turns += int(observation.get('model_turn_request_sent') is True)
            recorded_modes.append(mode)
    result['attempt_accounting'] = {
        'prior_native_starts_observed': 4,
        'prior_explicit_model_turns_observed': 1,
        'this_invocation_native_starts_observed_in_session_receipts': observed_starts,
        'this_invocation_explicit_model_turns_sent_in_session_receipts': observed_turns,
        'cumulative_native_starts_observed_in_session_receipts': 4 + observed_starts,
        'cumulative_explicit_model_turns_sent_in_session_receipts': 1 + observed_turns,
        'cumulative_native_starts_authorized_maximum': 6,
        'cumulative_explicit_model_turns_authorized_maximum': 3,
        'session_receipts_recorded_for_modes': recorded_modes,
        'counts_are_minimum_observations_if_an_attempt_has_no_session_receipt': True,
        'sent_turn_counts_even_without_model_output': True,
        'token_usage_or_subscription_charge': 'unknown',
        'no_counter_reset': True}
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
        print('Prepared Sol correction scope SHA256: '+SCOPE_SHA256)
        print('Preserves four starts and one sent turn; exact024 approval is required for cumulative limits6/3.')
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
