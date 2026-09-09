"""Offline source-model reproduction. Does not execute Codex or user config."""
import copy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
import p3_reviewer_admission as old
from gate0_client_preflight import overrides
from p3_reviewer_profile import reviewer_overrides


def source_origins(value, path=()):
    # Independent translation of pinned fingerprint.rs, not old._leaves.
    if type(value) is dict:
        for key, child in value.items():
            yield from source_origins(child, path + (key,))
    elif type(value) is list:
        for index, child in enumerate(value):
            yield from source_origins(child, path + (str(index),))
    elif type(value) is bool and len(path) == 2 and path[0] == 'features' and path[1] in ('multi_agent_v2', 'network_proxy'):
        if path[1] == 'network_proxy':
            yield '.'.join(path)
        yield '.'.join(path + ('enabled',))
    else:
        yield '.'.join(path)


p = reviewer_overrides(overrides(Path('/home/example/ARC_Independent_Lab/delivery/reviewer/runtime')),
    (ROOT / 'artifacts/GATE0_CODEX_INTERFACE/20260907_001/config-schema.json').read_bytes())
raw = {}
for dotted, value in p.items():
    node = raw
    pieces = dotted.split('.')
    for piece in pieces[:-1]:
        node = node.setdefault(piece, {})
    node[pieces[-1]] = copy.deepcopy(value)
meta = {'name': {'type': 'sessionFlags'}, 'version': 'sha256:' + '0' * 64}
origins = {path: copy.deepcopy(meta) for path in source_origins(raw)}
projected = copy.deepcopy(raw)
projected.pop('tools')
fixture = {'config': projected, 'origins': origins,
           'layers': [dict(meta, config=raw)]}
rows = []
for name, candidate in [('source_correct_origins', fixture),
                        ('only_array_defect_isolated_by_adding_legacy_boolean_key', copy.deepcopy(fixture))]:
    if name.startswith('only_array'):
        candidate['origins']['features.multi_agent_v2'] = copy.deepcopy(meta)
    try:
        old.validate_effective_config(candidate, p)
        outcome = {'admitted': True}
    except old.Stop as error:
        outcome = {'admitted': False, 'reason': str(error)}
    rows.append({'fixture': name, **outcome})
report = {
    'kind': 'P3_CONFIG_ORIGIN_OFFLINE_REPRODUCTION_021_v1',
    'native_client_executed': False,
    'model_request_sent': False,
    'user_configuration_read': False,
    'fixture_is_source_model_not_native_observation': True,
    'source_commit': '78c290807ce710180111df227df3b7a4fe845452',
    'validator_path': 'scripts/p3_reviewer_admission.py',
    'validator_sha256': hashlib.sha256((ROOT / 'scripts/p3_reviewer_admission.py').read_bytes()).hexdigest(),
    'missing_origin_paths_expected_by_old_validator': [path for dotted, value in p.items()
             for path, unused in old._leaves(dotted, value) if path not in origins],
    'required_source_paths_instead': ['features.multi_agent_v2.enabled',
             'features.code_mode.direct_only_tool_namespaces.0'],
    'outcomes': rows,
}
assert all(not row['admitted'] for row in rows)
target = ROOT / 'artifacts/P3_CONFIG_ORIGIN_SOURCE/20260909_001/OFFLINE_REPRODUCTION.json'
target.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
