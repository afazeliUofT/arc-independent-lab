#!/usr/bin/env python3
"""Read-only post-execution verification of actual published 032 evidence.

This is an engineering consistency check on exact copied receipts. It neither
executes the reviewer/auditor nor supplies an independent scientific verdict.
Only the derived report and a disposable byte-identical mirror are written.
"""
from __future__ import annotations
import collections
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
ARCHIVE = ('artifacts/P3_REVIEW_032_RETURN/'
           '94ddb570582a75780f03e54df5e3228a58dc9de23397d63eac4976928b9a2d11')
RUN = 'files/delivery/P3_FINITE_REVIEW_032'
OUTPUT = Path(__file__).resolve().parent / 'VERIFICATION.json'
EXPECTED_CONTROLLER = 'b1e5a8b083ec2776696c086c2a6ece56385922222e5d9ecd9b356f45a31bb0b3'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def raw(relative):
    path = ROOT / relative
    assert path.is_file() and not path.is_symlink()
    return path.read_bytes()


def get(relative):
    return json.loads(raw(relative))


def main():
    archive = ROOT / ARCHIVE
    manifest = get(ARCHIVE + '/MANIFEST.json')
    index = get(ARCHIVE + '/INDEX.json')
    index_digest = sha(raw(ARCHIVE + '/INDEX.json'))
    assert index_digest == archive.name == manifest['index_sha256'] == manifest['evidence_digest']
    checked = {}
    for entry in manifest['files']:
        path = Path(entry['path'])
        assert not path.is_absolute() and '..' not in path.parts
        content = raw(ARCHIVE + '/' + entry['path'])
        assert sha(content) == entry['sha256'] and len(content) == entry['bytes']
        checked[entry['path']] = {'sha256': sha(content), 'bytes': len(content)}
    assert set(checked) == {p.relative_to(archive).as_posix() for p in archive.rglob('*')
                            if p.is_file()} - {'MANIFEST.json'}
    for entry in index['sources']:
        assert entry['status'] == 'PRESENT'
        assert checked[entry['archive_path']] == {'sha256': entry['sha256'], 'bytes': entry['bytes']}
    controller_path = ROOT / 'scripts/p3_finite_review_032.py'
    assert sha(controller_path.read_bytes()) == EXPECTED_CONTROLLER
    with mock.patch.object(subprocess, 'Popen', side_effect=AssertionError('No subprocess permitted')) as guard:
        spec = importlib.util.spec_from_file_location('verified_original_controller032', controller_path)
        controller = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(controller)
        scope, prior, pins = controller.load_bundle()
        (ROOT / 'delivery').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='actual032_receipt_mirror_', dir=ROOT / 'delivery') as temporary:
            fixture_root = Path(temporary)
            mirror = fixture_root / 'delivery/P3_FINITE_REVIEW_032'
            shutil.copytree(archive / RUN, mirror)
            for path in mirror.rglob('*'):
                if path.is_file():
                    assert path.read_bytes() == (archive / RUN / path.relative_to(mirror)).read_bytes()
            verified_report_path = controller.existing(mirror, pins)
            assert verified_report_path == mirror / 'REPORT.json'
            report = json.loads(verified_report_path.read_bytes())
            assert report['status'] == 'REVIEWER_OUTPUT_PRESERVED'
            (fixture_root / 'state').mkdir()
            (fixture_root / 'state/ESCALATION.md').write_bytes((mirror / 'AUTHORIZATION.md').read_bytes())
            # Redirect only the approval file location to its exact original
            # preserved bytes. No source, pin, parser or predicate is replaced.
            with mock.patch.object(controller, 'ROOT', fixture_root):
                approval = controller.approval(scope, manual_launch=True)
            assert approval == report['authorization']
            synthetic, science = report['stages']
            assert controller.admitted_synthetic(synthetic)
            assert controller.admitted_science(science)
            assert controller.accounting(report['receipt_collection']['observations'],
                                         report['stage_attempts']) == report['attempt_accounting']
            original030 = ROOT / controller.HISTORY_ROOT / 'P3_FINITE_REVIEW_030'
            actual030 = json.loads((original030 / 'ATTEMPT.json').read_bytes())
            kernel = controller.previous.verify_kernel_preflight_receipt(
                actual030['sealed_cache_kernel_preflight'], run=original030,
                pins=pins['inherited030_pins'], authorization=actual030['authorization'])
            assert kernel == report['history']['kernel_prerequisite_reused_from_actual030']
            assert report['history']['new_kernel_probe_performed'] is False
            for path in mirror.rglob('*'):
                if path.is_file():
                    assert path.read_bytes() == (archive / RUN / path.relative_to(mirror)).read_bytes()
        assert guard.call_count == 0
    original_broker = controller.module('p3_review_broker')
    verdict_raw = raw(ARCHIVE + '/' + RUN + '/science_output/REVIEW_VERDICT.json')
    verdict = original_broker._json(verdict_raw)
    supplied = verdict['reviewer_verdict']
    assert verdict['packet_manifest_sha256'] == scope['private_packet_manifest_sha256']
    assert supplied['verdict'] in original_broker.VERDICTS
    assert {x['subject'] for x in supplied['dispositions']} == set(original_broker.SUBJECTS)
    assert len(supplied['dispositions']) == len(original_broker.SUBJECTS)
    public_refs, absent_private_refs = {}, {}
    disposition_refs = {}
    for item in supplied['dispositions']:
        for ref in item['evidence']:
            name = original_broker._path(ref['path'])
            digest = original_broker._sha(ref['sha256'])
            assert name not in disposition_refs or disposition_refs[name] == digest
            disposition_refs[name] = digest
    assert disposition_refs == verdict['actual_evidence_sha256']
    for name, digest in disposition_refs.items():
        if (ROOT / name).is_file():
            assert sha(raw(name)) == digest
            public_refs[name] = digest
        else:
            assert name.startswith(('private_papers/', 'pdf_pages/', 'scanned_pages/'))
            absent_private_refs[name] = digest
    manifest_entries = {}
    for field, name in original_broker.REVIEW_MANIFESTS.items():
        assert sha(raw(name)) == supplied['applies_to'][field]
        for entry in get(name)['files']:
            assert sha(raw(entry['path'])) == entry['sha256']
            manifest_entries[entry['path']] = entry['sha256']
    closure = get(original_broker.CLOSURE)
    assert sha(raw(original_broker.CLOSURE)) == original_broker.CLOSURE_SHA256
    for entry in closure['view_input_files']:
        assert sha(raw(entry['path'])) == entry['sha256']
    historical = get(original_broker.HISTORICAL_RECEIPT)
    assert historical['artifact_consistency_passed'] is True
    assert historical['transitions_checked'] == 6912
    assert historical['recovery_unlabeled_encoder_calls'] == 6912
    assert historical['evaluator_probes'] == 13824
    science_observation = science['observation']
    broker_receipts = science_observation['broker_receipts']
    auditor_calls = [r for r in broker_receipts if r['tool'] == 'run_observer_audit']
    assert len(auditor_calls) == 1 and auditor_calls[0]['successful'] is True
    assert supplied['verdict'] != 'SUSPEND_FOR_DEPENDENCY'
    assert broker_receipts[-1]['tool'] == 'submit_verdict' and broker_receipts[-1]['successful'] is True
    expected_auditor_hash = '81c4fa7c32b9a27a57dafb0e7675ef37024976e6e43668f4d48295f961a00d78'
    assert expected_auditor_hash in supplied['summary']
    assert not any('REEXECUTION_RECEIPT.json' in name for name in checked)
    for name, entry in checked.items():
        assert sha(raw(ARCHIVE + '/' + name)) == entry['sha256']
    workflow = get(ARCHIVE + '/files/delivery/P3_032_RETURN_WORKFLOW/WORKFLOW_REPORT.json')
    result = {
        'kind': 'P3_RUN_032_DERIVED_ENGINEERING_VERIFICATION_033_v1',
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'all_requested_published_receipt_checks_passed': True,
        'source_archive': ARCHIVE, 'archive_inventory': checked,
        'manifest_sha256': sha(raw(ARCHIVE + '/MANIFEST.json')),
        'verification_source_sha256': sha(Path(__file__).read_bytes()),
        'original_controller_sha256': EXPECTED_CONTROLLER,
        'unchanged_original_controller_load_bundle_passed': True,
        'unchanged_original_controller_existing_mirror_check_passed': True,
        'original_preserved_exact_scope_approval_passed': True,
        'synthetic_admitted_by_original_predicate': True,
        'science_admitted_by_original_predicate': True,
        'original030_kernel_prerequisite_rechecked_without_execution': True,
        'source_bound_receipt_collection_complete': report['receipt_collection']['complete'],
        'receipt_errors': report['receipt_collection']['errors'],
        'attempt_accounting_recomputed': report['attempt_accounting'],
        'report_status': report['status'], 'reviewer_output': report['reviewer_output'],
        'synthetic_elapsed_seconds': synthetic['observation']['elapsed_seconds'],
        'science_elapsed_seconds': science_observation['elapsed_seconds'],
        'whole_controller_elapsed_seconds': workflow['controller_outcome']['elapsed_seconds'],
        'science_calls_total': len(broker_receipts),
        'science_calls_successful': sum(r['successful'] is True for r in broker_receipts),
        'science_correctable_refusals': science_observation['recoverable_input_error_receipts'],
        'science_completed_compactions': science_observation['native_item_lifecycle']['context_compactions_completed'],
        'science_final_packet_receipt': science['packet_after'],
        'science_host_noncredential_checks_passed': science['host_checks']['all_noncredential_checks_pass'],
        'review_manifests_public_union_entries_rehashed': len(manifest_entries),
        'verdict_public_evidence_rehashed': public_refs,
        'verdict_private_evidence_not_retrieved_in_this_check': absent_private_refs,
        'observer_audit': {
            'successful_actual_broker_call_receipt': auditor_calls[0],
            'substantive_verdict_required_successful_actual_fixed_audit': True,
            'reported_actual_receipt_sha256': expected_auditor_hash,
            'actual_receipt_bytes_present_in_published_return': False,
            'actual_receipt_sha256_independently_rehashed_here': False,
            'actual_receipt_archive_capture': 'pending durability only; do not rerun or reconstruct',
            'historical_original_receipt_sha256': sha(raw(original_broker.HISTORICAL_RECEIPT)),
            'fixed_public_dependency_bytes_rehashed': len(closure['view_input_files']),
            'auditor_reexecuted_by_this_check': False},
        'original_return_source_bytes_unchanged': True,
        'mirror_disposable_exact_bytes_only': True,
        'new_native_or_model_processes': 0, 'new_model_turns': 0,
        'new_kernel_probes': 0, 'subprocess_attempts': 0,
        'credential_files_accessed': False, 'commits_or_pushes_executed': False,
        'independent_scientific_review_supplied_by_this_check': False,
        'limitations': [
            'This checks published receipts and source predicates, not independent external attestation of historical execution.',
            'Private paper/PDF-image bytes are outside this public return; their runtime checks are evidenced by the pinned broker and packet receipts, not rehashed here.',
            'The original auditor receipt is not in the fixed return allowlist. Successful run_observer_audit and substantive-verdict guard evidence execution/comparison; they are not retrieval of those original receipt bytes.',
            'Source-bound admission does not establish scientific correctness, mechanism novelty, efficacy, hosted ChatGPT allowance, or continuous human attendance.',
            'Fresh process, reported control checks and runtime boundary evidence are bounded to this approved operation; this shared-filesystem verification is not a second independent reviewer.']}
    with OUTPUT.open('x') as handle:
        json.dump(result, handle, indent=2, allow_nan=False)
        handle.write('\n')
    print(json.dumps({'verification': str(OUTPUT.relative_to(ROOT)),
                      'sha256': sha(OUTPUT.read_bytes()),
                      'published_receipt_checks_passed': True,
                      'original_auditor_receipt_durability_pending': True}))


if __name__ == '__main__':
    main()
