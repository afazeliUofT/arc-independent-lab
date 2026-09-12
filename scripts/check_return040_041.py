#!/usr/bin/env python3
"""Verify original040 bytes and source-bound receipts offline; never run a model.

Public inputs and the private packet may reside in the immutable041 ZIP view.
No native controller entry point, broker submission, or candidate is executed.
This checks evidence integrity/admission, not the scientific truth of a verdict.
"""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
COMMIT = '540370fdb73c8f87f6433e14463951673640d033'
ARCHIVE = 'artifacts/P3_REVIEW_040_RETURN/a31d934ca1d4c3b4d84dc7bbe757f5295834c8319301debd826897c768786eac'
INDEX_SHA = 'a31d934ca1d4c3b4d84dc7bbe757f5295834c8319301debd826897c768786eac'
REPORT_SHA = '877c4eeda0b31154d42885f8afbe7e01a56a5a452bdcef56a279b46cb2a7c372'
VERDICT_SHA = 'a31b9d8ec2103f09d81b963fd7f9ff51c4287490a0f0bf2f74f5dfbc1407d673'
PACKET_SHA = '1546dd761c3f3c1fa7b44f2d9df0ff2358e96ca37b2c1d3d3230aa6735927142'
SOURCE_PINS = {
 'scripts/p3_focused_review_040.py':'87b41859366e90ced768f4c7367ddf7349764bee9079b048025585b7c7f1e232',
 'scripts/p3_receipt_collection_032.py':'52b88345b8d707891fc33d37cd7040ca356178f400cc1396db9282951937b552',
 'scripts/p3_reviewer_session_040.py':'b3aa27b7349a51a9206d6cbfe87bb3264b6f9ee8dc497053078888fbacac1cf9',
 'configs/P3_FOCUSED_REVIEW_SCOPE_040.json':'682521fe5c47ffbd620064655bb8d9b1f6d365d5d84cac5a1e50ee72d0172f4e',
 'evidence/P3_FOCUSED_REVIEW_MANIFEST_040.json':'270244a9cc98193098d60ad021dedf4dbd91a44e4357e5b338aa5d1b3c30805e',
}

def require(ok, reason):
    if not ok: raise ValueError(reason)

def sha(raw): return hashlib.sha256(raw).hexdigest()

def unique_pairs(rows):
    obj = {}
    for key, value in rows:
        require(key not in obj, 'duplicate JSON key')
        obj[key] = value
    return obj

def parse(raw):
    return json.loads(raw, object_pairs_hook=unique_pairs,
        parse_constant=lambda x: (_ for _ in ()).throw(ValueError('nonfinite JSON')))

def read(root, name):
    require(type(name) is str and PurePosixPath(name).as_posix() == name and
        not name.startswith('/') and all(p not in ('', '.', '..', '.git') for p in name.split('/')),
        'invalid relative evidence path')
    path = Path(root)
    require(path.is_dir() and not path.is_symlink(), 'invalid evidence root')
    for part in name.split('/'):
        path /= part
        require(not path.is_symlink(), 'linked evidence refused')
    require(path.is_file() and path.stat().st_nlink == 1 and path.stat().st_size <= 32 * 1024 * 1024,
        'invalid evidence file')
    return path.read_bytes()

def load(root, name):
    path = Path(root) / 'scripts' / (name + '.py')
    previous = sys.modules.get(name)
    if previous is not None:
        require(Path(previous.__file__).resolve() == path.resolve(), 'conflicting module root')
        return previous
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

def verify(root, packet):
    root, packet = Path(root).absolute(), Path(packet).absolute()
    for name, digest in SOURCE_PINS.items():
        require(sha(read(root, name)) == digest, 'sealed source differs: ' + name)
    release = parse(read(root, 'evidence/P3_FOCUSED_REVIEW_MANIFEST_040.json'))
    for row in release['inputs']:
        require(sha(read(root, row['path'])) == row['sha256'], '040 input differs: ' + row['path'])
    index_raw = read(root, ARCHIVE + '/INDEX.json')
    require(sha(index_raw) == INDEX_SHA, 'original index differs')
    index = parse(index_raw)
    inventory = parse(read(root, ARCHIVE + '/MANIFEST.json'))
    require(inventory['evidence_digest'] == inventory['index_sha256'] == INDEX_SHA, 'index identity differs')
    checks = []
    for row in inventory['files']:
        name = ARCHIVE + '/' + row['path']; raw = read(root, name)
        require(len(raw) == row['bytes'] and sha(raw) == row['sha256'], 'archived bytes differ: ' + name)
        checks.append({'path': name, 'bytes': len(raw), 'sha256': sha(raw)})
    require(len(checks) == len({r['path'] for r in checks}) == 13, 'archive inventory differs')
    expected = {r['path'] for r in checks} | {ARCHIVE + '/MANIFEST.json'}
    actual = {p.relative_to(root).as_posix() for p in (root / ARCHIVE).rglob('*') if p.is_file()}
    require(actual == expected, 'extra or missing original return member')
    require(len(index['sources']) == 12 and all(r['status'] == 'PRESENT' for r in index['sources']), 'source absence')
    for row in index['sources']:
        raw = read(root, ARCHIVE + '/' + row['archive_path'])
        require(len(raw) == row['bytes'] and sha(raw) == row['sha256'], 'original source index differs')
    run_rel = ARCHIVE + '/files/delivery/P3_FOCUSED_REVIEW_040'
    report_raw = read(root, run_rel + '/REPORT.json')
    verdict_raw = read(root, run_rel + '/science_output/REVIEW_VERDICT.json')
    require(sha(report_raw) == REPORT_SHA and sha(verdict_raw) == VERDICT_SHA, 'original report/verdict differs')
    require(read(root, run_rel + '/REPORT.sha256') == (REPORT_SHA + '\n').encode(), 'report checksum file differs')
    report, verdict = parse(report_raw), parse(verdict_raw)
    controller = load(root, 'p3_focused_review_040')
    scope, prior, pins = controller.load_bundle()
    require(report['pins'] == pins and report['authorization'] == scope['authorization'], 'controller binding differs')
    require(sha(read(root, run_rel + '/AUTHORIZATION.md')) == scope['authorization']['sha256'], 'authorization differs')
    attempt = parse(read(root, run_rel + '/ATTEMPT.json'))
    require(attempt['pins'] == pins and attempt['reserved_native_starts'] == attempt['reserved_turns'] == 2,
        'attempt binding/reservation differs')
    collector = controller.module('p3_receipt_collection_032')
    collection = collector.collect(root / run_rel, emitter_path=root / 'scripts/p3_reviewer_session_040.py',
        emitter_sha256=SOURCE_PINS['scripts/p3_reviewer_session_040.py'],
        expected_kind='P3_FINITE_REVIEWER_SESSION_040_v1', expected_modes=('synthetic', 'science'))
    require(collection == report['receipt_collection'] and collection['complete'] and not collection['errors'],
        'unchanged collector does not reproduce original report')
    require(report['stages'] == [collection['stages'][m] for m in ('synthetic', 'science')], 'embedded stages differ')
    require(controller.admitted_synthetic(collection['stages']['synthetic']) and
        controller.admitted_science(collection['stages']['science']), 'frozen controller admission fails')
    require(report['status'] == 'REVIEWER_OUTPUT_PRESERVED' and not report['primary_session_stops'] and
        not report['stage_failures'] and report['reviewer_output']['execution_admitted'] is True and
        report['reviewer_output']['parent_edited'] is False, 'original admitted outcome differs')
    counts = controller.accounting(collection['observations'], ['synthetic', 'science'])
    require(counts == report['attempt_accounting'] and counts['cumulative_observed_native_starts'] == 18 and
        counts['cumulative_observed_sent_turns'] == 14 and not counts['missing_session_counts_are_only_minimum_observations'],
        'accounting differs')

    packet_raw = read(packet, 'BROKER_MANIFEST.json')
    require(sha(packet_raw) == verdict['packet_manifest_sha256'] == PACKET_SHA, 'packet identity differs')
    packet_manifest = parse(packet_raw)
    files = {r['path']: r for r in packet_manifest['files']}
    require(len(files) == len(packet_manifest['files']) == 171, 'packet inventory differs')
    for name, row in files.items():
        require(sha(read(packet, name)) == row['sha256'], 'packet bytes differ: ' + name)
    actual_packet = {p.relative_to(packet).as_posix() for p in packet.rglob('*') if p.is_file()}
    require(actual_packet == set(files) | {'BROKER_MANIFEST.json'}, 'extra or missing packet member')
    descriptor_raw = read(packet, 'FOCUSED_SCOPE.json')
    descriptor = parse(descriptor_raw)
    delivery = verdict['source_delivery_receipt']
    require(delivery == collection['stages']['science']['source_delivery_after'] and
        delivery['descriptor_sha256'] == sha(descriptor_raw) and delivery['packet_manifest_sha256'] == PACKET_SHA,
        'source delivery binding differs')
    ranges, images, text_calls = {}, set(), 0
    for event in delivery['delivery_events']:
        name = event['path']; require(event['sha256'] == files[name]['sha256'], 'delivery hash differs')
        if event['tool'] == 'read_text':
            text_calls += 1
            length = len(read(packet, name).decode('utf-8'))
            start, end = event['offset'], event['next_offset']
            require(type(start) is type(end) is int and 0 <= start <= end <= length, 'invalid delivered character range')
            ranges.setdefault(name, []).append((start, end))
        else:
            require(event['tool'] == 'read_page_image' and files[name]['kind'] == 'image', 'unknown delivery operation')
            images.add(name)
    merged = {}
    for name, intervals in ranges.items():
        result = []
        for start, end in sorted(intervals):
            if result and start <= result[-1][1]: result[-1][1] = max(result[-1][1], end)
            else: result.append([start, end])
        merged[name] = result
        require(result == [[0, len(read(packet, name).decode('utf-8'))]], 'incomplete delivered text')
    require(merged == delivery['text_ranges_delivered'] and len(merged) == 43 and text_calls == 85 and
        len(delivery['delivery_events']) == 97, 'delivery range/call records differ')
    for row in descriptor['required_texts']:
        name = row['path'] if isinstance(row, dict) else row
        require(name in merged, 'missing required public text')
    broker = controller.module('p3_focused_review_broker_039')
    for paper_id, requirements in broker.PAPERS.items():
        require('reading/' + paper_id + '/full_text.txt' in merged, 'full methods not delivered')
        for page in requirements['images']:
            require(f'reading/{paper_id}/page_{page:03}.png' in images, 'required paper image not delivered')
    require(not delivery['missing_required_texts'] and delivery['all_required_delivery_complete'] is True,
        'source delivery incomplete')
    scientific = verdict['reviewer_verdict']
    broker._check_schema(scientific, broker.TOOL_SCHEMAS['submit_verdict'])
    require(scientific['applies_to'] == {'scope_id': broker.SCOPE_ID,
        'scientific_manifest_sha256': pins['scientific_manifest_sha256']}, 'scientific scope differs')
    require(scientific['verdict'] == 'GO' and not scientific['required_corrections'] and not scientific['missing_dependencies'],
        'original scientific outcome differs')
    require(sorted(r['claim_id'] for r in scientific['claim_assessments']) == list(broker.CLAIMS) and
        sorted((r['source_id'], r['claim_id']) for r in scientific['source_comparisons']) == [('CHV79', 'R1'), ('PK97', 'R6')],
        'claim/source contract differs')
    cited = {}
    for field in ('claim_assessments', 'source_comparisons'):
        for row in scientific[field]:
            require(row['assessment'] == 'SUPPORTED_WITH_SCOPE', 'assessment differs')
            for ref in row['evidence']:
                name = ref['path']; require(ref['sha256'] == files[name]['sha256'], 'cited evidence differs')
                if files[name]['kind'] == 'text': require(name in merged, 'cited text not delivered')
                cited[name] = ref['sha256']
    require(cited == verdict['actual_evidence_sha256'] and len(cited) == 24, 'actual cited-source map differs')
    for row in scientific['source_comparisons']:
        digest = broker.PAPERS[row['source_id']]['sha256']
        require({'path': 'private_papers/' + digest + '.pdf', 'sha256': digest} in row['evidence'], 'paper citation absent')
    require(scientific['recommendation']['route'] == 'SPECIFY_SUCCESSOR_COMPARISON', 'route differs')
    return {'kind': 'P3_ORIGINAL_RETURN_VERIFICATION_041_v1', 'integrity_verified': True,
        'github_commit': COMMIT, 'access_date': '2026-09-12', 'return_archive': ARCHIVE,
        'source_pins': SOURCE_PINS, 'return_file_checks': checks,
        'return_manifest': {'path': ARCHIVE + '/MANIFEST.json', 'sha256': sha(read(root, ARCHIVE + '/MANIFEST.json'))},
        'frozen_release_inputs_verified': len(release['inputs']), 'packet_files_verified': len(files),
        'source_bound_collector_reexecution_matches_original': True, 'frozen_stage_admissions_recomputed': True,
        'original_report_sha256': REPORT_SHA, 'original_verdict_sha256': VERDICT_SHA,
        'original_receipts_modified': False, 'source_delivery_independently_recomputed': True,
        'cited_source_hashes_verified': len(cited), 'source_delivery_is_not_comprehension': True,
        'actual_attempt_usage': {'native_starts': 2, 'sent_turns': 2},
        'actual_cumulative_usage': {'native_starts': 18, 'sent_turns': 14},
        'scope040_exhausted': True, 'scientific_verdict': 'GO',
        'scope': 'R1-R7 analytical assessment only; no novelty/efficacy/PROGRAMME/integrated guarantee',
        'full_boundary_or_fresh_context_attested': False,
        'native_starts_by_this_verifier': 0, 'model_turns_by_this_verifier': 0, 'candidate_runs_by_this_verifier': 0}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--packet', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.root, args.packet), indent=2, ensure_ascii=True))
