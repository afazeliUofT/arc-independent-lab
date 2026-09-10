#!/usr/bin/env python3
"""Offline classification only; imports frozen session and invokes no native process."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

def main():
    repo = Path(sys.argv[1]).resolve()
    out = Path(__file__).resolve().parent
    script = repo / 'scripts/p3_reviewer_session_028.py'
    spec = importlib.util.spec_from_file_location('forensic_session028', script)
    session = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(session)
    schemas = json.loads((repo / 'artifacts/GATE0_CODEX_INTERFACE/20260907_001/schemas/experimental.json').read_text())
    schema = json.loads(schemas['v2/ItemStartedNotification.json'])
    variants = schema['definitions']['ThreadItem']['oneOf']
    observed = []
    for variant in variants:
        kind = variant['properties']['type']['enum'][0]
        item = {'id': 'fixture-item', 'type': kind}
        if kind == 'userMessage':
            item['content'] = [{'type': 'text', 'text': 'fixed synthetic prompt'}]
        elif kind == 'agentMessage':
            item['text'] = 'fixture output'
        elif kind == 'functionCallOutput':
            item.update(name='test_sync_tool', namespace=None, output='fixture')
        elif kind == 'dynamicToolCall':
            item.update(tool='read_text', namespace=None, arguments={'path': 'CANARY.txt', 'offset': 0, 'length': 1000})
        events = session._Events('fixed synthetic prompt')
        events.thread_id, events.turn_id = 'fixture-thread', 'fixture-turn'
        frame = {'method': 'item/started', 'params': {'threadId': 'fixture-thread', 'turnId': 'fixture-turn', 'item': item}}
        try:
            events.accept(frame)
            result = {'status': 'accepted'}
        except session.Stop as error:
            result = {'status': 'stopped', 'reason': str(error)}
        observed.append({'source_variant': kind, 'required_fields': variant.get('required', []), 'fixture_complete_schema_claim': kind == 'contextCompaction', **result})
    report = {
        'kind': 'P3_028_EVENT_GUARD_OFFLINE_FORENSIC_v1',
        'scientific_review': False, 'native_process_started': False,
        'credentials_read': False, 'unknown_native_content_read': False,
        'session_sha256': hashlib.sha256(script.read_bytes()).hexdigest(),
        'source_variants': len(observed), 'variants': observed,
        'context_compaction_full_minimal_source_schema_fixture_stops': any(x['source_variant'] == 'contextCompaction' and x.get('reason') == 'Unadvertised native item effect' for x in observed),
        'actual_028_item_type_identified': False,
        'note': 'All 19 discriminants checked. ContextCompaction fixture includes every required field and is source-schema complete. Other denied fixtures intentionally exercise discriminant guard before their payload validation; they are not claimed complete ThreadItem instances.'
    }
    assert report['source_variants'] == 19
    assert report['context_compaction_full_minimal_source_schema_fixture_stops']
    assert sum(x['status'] == 'accepted' for x in observed) == 5
    (out / 'REPRODUCTION.json').write_text(json.dumps(report, indent=2) + '\n')
    print('19 source discriminants checked; 5 admitted, 14 rejected; complete contextCompaction fixture reproduces exact guard. No native/model/auth activity.')

if __name__ == '__main__':
    main()
