#!/usr/bin/env python3
"""Derived forensic evidence from exact returned receipts; no native/model launch.

This never creates or reconstructs P3_FINITE_REVIEW_030/REPORT.json. It copies
only the four named original SESSION/STAGE receipts into explicit forensic
fixtures and invokes the unchanged controller's read-only receipt consumer.
"""
from __future__ import annotations

import ast
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import traceback
from unittest import mock


HERE = Path(__file__).resolve().parent
LAB = HERE.parents[2]
REPO = LAB / 'delivery/rebuild031/repository'
RETURN = (LAB / 'delivery/rebuild032/returned/artifacts/P3_REVIEW_030_RETURN/'
          '9c806f9b65f6765c446fe16fa9edb106516195765473d3b69c8197ad7b87d22f/'
          'files/delivery/P3_FINITE_REVIEW_030')
FILES = ('synthetic_SESSION.json', 'synthetic_STAGE.json',
         'science_SESSION.json', 'science_STAGE.json')


def digest(path):
    raw = path.read_bytes()
    return {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}


def write(path, value):
    with path.open('x') as handle:
        json.dump(value, handle, indent=2)
        handle.write('\n')


def main():
    if (HERE / 'DERIVED_FORENSIC_PROOF.json').exists():
        raise SystemExit('Existing forensic proof preserved; no automatic repeat.')
    source_paths = ('scripts/p3_finite_review_030.py', 'scripts/p3_reviewer_session_030.py',
                    'tests/test_p3_finite_review_030.py', 'tests/test_p3_lifecycle_030.py',
                    'tests/test_review030_workflow.py', 'tests/test_publish_review030_evidence.py')
    source_before = {name: digest(REPO / name) for name in source_paths}
    input_before = {name: digest(RETURN / name) for name in FILES}
    assert not (RETURN / 'REPORT.json').exists()
    assert not (RETURN / 'science_output/REVIEW_VERDICT.json').exists()
    fixture = HERE / 'EXACT_RETURNED_RECEIPT_COPIES'
    fixture.mkdir()
    for name in FILES:
        (fixture / name).write_bytes((RETURN / name).read_bytes())

    controller_path = REPO / 'scripts/p3_finite_review_030.py'
    spec = importlib.util.spec_from_file_location('unchanged_controller030_forensic', controller_path)
    controller = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = controller
    with mock.patch.object(subprocess, 'Popen', side_effect=AssertionError('Process creation forbidden')) as launch:
        spec.loader.exec_module(controller)
        controller.load_bundle()
        observations = {}
        linked = {}
        for mode in ('synthetic', 'science'):
            observations[mode] = json.loads((fixture / (mode + '_SESSION.json')).read_bytes())
            stage = json.loads((fixture / (mode + '_STAGE.json')).read_bytes())
            linked[mode] = controller.linked_stage(fixture, stage, mode) == stage
        traces = []
        exceptions = []
        for label, folder in [('both', fixture), ('synthetic_only', HERE / 'SYNTHETIC_ONLY_COPY'),
                              ('science_only', HERE / 'SCIENCE_ONLY_COPY')]:
            if folder != fixture:
                folder.mkdir()
                mode = label.removesuffix('_only')
                (folder / (mode + '_SESSION.json')).write_bytes((fixture / (mode + '_SESSION.json')).read_bytes())
            try:
                controller.collect_sessions(folder)
            except controller.Stop as error:
                exceptions.append({'exact_copy_set': label, 'exception_class': type(error).__name__,
                                   'reason': str(error)})
                traces.append(label + '\n' + traceback.format_exc())
            else:
                raise AssertionError('Unchanged controller unexpectedly accepted the original receipt kind')
        expected_error = 'SESSION kind or actual execution counters differ'
        assert len(exceptions) == 3 and all(x['reason'] == expected_error for x in exceptions)
        for mode, observation in observations.items():
            assert observation['mode'] == mode
            assert observation['client_started'] is True
            assert observation['model_turn_request_sent'] is True
            assert observation['native_process_reaped'] is True
            assert observation['verdict_submitted'] is False
        counts = controller.accounting(observations, ['synthetic', 'science'])
        launch.assert_not_called()

    # Source-level proof that the failing collection lies outside execute's
    # session exception guard and precedes its only final report write.
    tree = ast.parse(controller_path.read_text())
    execute = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'execute')
    guarded = next(n for n in execute.body if isinstance(n, ast.Try))
    collection = next(n for n in execute.body if isinstance(n, ast.Assign) and
                      isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name) and
                      n.value.func.id == 'collect_sessions')
    final_write = next(n for n in execute.body if isinstance(n, ast.Assign) and
                      isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name) and
                      n.value.func.id == 'exclusive_json' and n.lineno > collection.lineno)
    assert guarded.end_lineno < collection.lineno < final_write.lineno
    emitter = ast.parse((REPO / 'scripts/p3_reviewer_session_030.py').read_text())
    run_session = next(n for n in emitter.body if isinstance(n, ast.FunctionDef) and n.name == 'run_session')
    assignment = next(n for n in run_session.body if isinstance(n, ast.Assign) and
                      any(isinstance(t, ast.Name) and t.id == 'report' for t in n.targets))
    emitted_kind = next(v.value for k, v in zip(assignment.value.keys, assignment.value.values)
                        if isinstance(k, ast.Constant) and k.value == 'kind')
    assert emitted_kind != controller.SESSION_KIND
    assert all(o['kind'] == emitted_kind for o in observations.values())
    sources_after = {name: digest(REPO / name) for name in source_paths}
    inputs_after = {name: digest(RETURN / name) for name in FILES}
    assert sources_after == source_before and inputs_after == input_before
    assert all(digest(fixture / name) == input_before[name] for name in FILES)
    assert not (RETURN / 'REPORT.json').exists() and not (fixture / 'REPORT.json').exists()
    (HERE / 'UNCHANGED_CONSUMER_TRACE.txt').write_text('\n'.join(traces))
    report = {
        'kind': 'P3_030_MISSING_REPORT_DERIVED_FORENSIC_PROOF_032_v1',
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'derived_engineering_analysis_not_native_execution_receipt': True,
        'original_main_report_created_or_reconstructed': False,
        'original_verdict_created_or_reconstructed': False,
        'native_clients_started_by_this_forensic_work': 0,
        'model_turns_sent_by_this_forensic_work': 0,
        'git_commits_or_pushes_performed': False,
        'original_sources_unchanged': source_before == sources_after,
        'original_returned_receipts_unchanged': input_before == inputs_after,
        'fixed_sources': source_before,
        'exact_original_receipts': input_before,
        'exact_copies_match_originals': True,
        'unchanged_frozen_bundle_checks_passed': True,
        'unchanged_separate_stage_linkage_checks': linked,
        'unchanged_collector_reproductions': exceptions,
        'emitter_kind': emitted_kind,
        'consumer_expected_kind': controller.SESSION_KIND,
        'source_location': {'emitter_report_assignment': assignment.lineno,
                            'guarded_execute_try_end': guarded.end_lineno,
                            'unguarded_collection': collection.lineno,
                            'final_report_write_not_reached': final_write.lineno},
        'derived_accounting_from_original_true_execution_flags': counts,
        'actual_original_execution_summary': {
            mode: {key: value.get(key) for key in ('kind', 'mode', 'status', 'client_started',
                'model_turn_request_sent', 'native_process_reaped', 'verdict_submitted',
                'elapsed_seconds', 'server_requests_dispatched', 'failed_broker_calls', 'primary_failure')}
            for mode, value in observations.items()},
        'scope_of_causal_claim': 'The original emitter-consumer mismatch deterministically makes the '
            'unchanged final collector throw on exact returned receipts before main report creation. '
            'This is a separate post-session reporting failure and does not explain the scientific '
            'session stop or establish a scientific verdict.'
    }
    write(HERE / 'DERIVED_FORENSIC_PROOF.json', report)
    members = [HERE / 'DERIVED_FORENSIC_PROOF.json', HERE / 'UNCHANGED_CONSUMER_TRACE.txt', Path(__file__)]
    (HERE / 'SHA256SUMS').write_text(''.join(digest(p)['sha256'] + '  ' + p.name + '\n' for p in members))
    print(json.dumps({'derived_proof': str(HERE / 'DERIVED_FORENSIC_PROOF.json'),
                      'proof_sha256': digest(HERE / 'DERIVED_FORENSIC_PROOF.json')['sha256'],
                      'reproductions': len(exceptions), 'original_receipts_unchanged': True,
                      'cumulative_observed_starts': counts['cumulative_observed_native_starts'],
                      'cumulative_observed_turns': counts['cumulative_observed_sent_turns']}, indent=2))


if __name__ == '__main__':
    main()
