#!/usr/bin/env python3
"""Record exact-source synthetic evidence-return checks. No native/model/Git publication."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib
import io
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
NAMES = ('test_publish_review030_evidence', 'test_review030_workflow', 'test_publish_checkpoint031')


def main():
    out = ROOT / 'artifacts/P3_RETURN_WORKFLOW_VALIDATION/20260910_031'
    out.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(ROOT / 'tests'))
    rows = []
    for name in NAMES:
        module = importlib.import_module(name)
        trace = io.StringIO()
        result = unittest.TextTestRunner(stream=trace, verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromModule(module))
        path = out / (name + '.txt')
        path.write_text(trace.getvalue())
        rows.append({'suite':name, 'tests_run':result.testsRun,
            'failures':len(result.failures), 'errors':len(result.errors),
            'skipped':len(result.skipped), 'passed':result.wasSuccessful(),
            'trace':str(path.relative_to(ROOT)),
            'trace_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    paths = ['scripts/' + x for x in ('publish_checkpoint031.py', 'review030_workflow.py',
        'publish_review030_evidence.py', 'validate_review_return031.py')]
    paths += ['tests/' + name + '.py' for name in NAMES]
    report = {'kind':'P3_RETURN_WORKFLOW_OFFLINE_VALIDATION_031_v1',
        'created_utc':datetime.now(timezone.utc).isoformat(), 'suites':rows,
        'tests_run':sum(x['tests_run'] for x in rows),
        'passed':all(x['passed'] and x['skipped'] == 0 for x in rows),
        'sources':{p:hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths},
        'git_commits_or_pushes_performed':False, 'git_commits_and_pushes_in_tests_mocked':True,
        'native_clients_started':0, 'model_turns_sent':0,
        'independent_scientific_review':False,
        'actual_wsl_execution_or_github_push_verified_by_these_tests':False}
    path = out / 'REPORT.json'
    path.write_text(json.dumps(report, indent=2) + '\n')
    (out / 'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.name + '\n'
        for p in sorted(out.iterdir()) if p.is_file()))
    print(json.dumps({'report':str(path), 'tests_run':report['tests_run'], 'passed':report['passed'],
        'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
