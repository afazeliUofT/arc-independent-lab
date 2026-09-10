#!/usr/bin/env python3
"""Record offline engineering validation; never invoke a native client or model.

Only the named synthetic test suites run. Their output files are fixture evidence,
not independent scientific verdicts. An existing result directory is never reused.
"""
from datetime import datetime, timezone
import argparse
import hashlib
import importlib
import io
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SUITES = ('test_p3_cache_inputs_030', 'test_p3_lifecycle_030',
          'test_p3_stage_evidence_030', 'test_p3_finite_review_030')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.absolute()
    if not out.is_relative_to(ROOT / 'artifacts') or out.exists():
        raise SystemExit('Use a new artifact directory under this repository.')
    out.mkdir(parents=True)
    sys.path.insert(0, str(ROOT / 'scripts'))
    sys.path.insert(0, str(ROOT / 'tests'))
    records = []
    for name in SUITES:
        module = importlib.import_module(name)
        trace = io.StringIO()
        result = unittest.TextTestRunner(stream=trace, verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromModule(module))
        trace_path = out / (name + '.txt')
        trace_path.write_text(trace.getvalue())
        item = {'suite': name, 'tests_run': result.testsRun, 'failures': len(result.failures),
                'errors': len(result.errors), 'skipped': len(result.skipped),
                'successful': result.wasSuccessful(), 'trace': str(trace_path.relative_to(ROOT)),
                'trace_sha256': sha(trace_path)}
        if getattr(module, 'REPORTS', None):
            path = out / (name + '_OBSERVATIONS.json')
            path.write_text(json.dumps({'engineering_fixtures_only': True,
                'native_client_or_model_used': False, 'records': module.REPORTS}, indent=2) + '\n')
            item.update(observations=str(path.relative_to(ROOT)), observations_sha256=sha(path))
        records.append(item)
    paths = [p for p in (ROOT / 'scripts').glob('*030.py') if p.name != 'checkpoint030_handoff.py']
    paths += [ROOT / 'tests' / (name + '.py') for name in SUITES]
    paths += [ROOT / 'configs/P3_FINITE_REVIEW_SCOPE_030.json']
    report = {'kind': 'P3_OFFLINE_REDESIGN_VALIDATION_030_v1',
        'created_utc': datetime.now(timezone.utc).isoformat(), 'suites': records,
        'tests_run': sum(x['tests_run'] for x in records),
        'passed': all(x['successful'] and x['skipped'] == 0 for x in records),
        'sources': {str(p.relative_to(ROOT)): sha(p) for p in sorted(paths)},
        'new_native_clients_started': 0, 'model_turns_sent': 0,
        'credential_contents_accessed': False, 'independent_scientific_verdict': False,
        'actual_bubblewrap_mount_verified_here': False,
        'kernel_mount_preflight_required_on_target_before_native_reservation': True,
        'fixture_dependency_verdicts_are_not_scientific_reviews': True}
    path = out / 'REPORT.json'
    path.write_text(json.dumps(report, indent=2) + '\n')
    members = sorted(p for p in out.iterdir() if p.is_file())
    (out / 'SHA256SUMS').write_text(''.join(sha(p) + '  ' + p.name + '\n' for p in members))
    print(json.dumps({'report': str(path), 'sha256': sha(path),
                      'tests_run': report['tests_run'], 'passed': report['passed']}, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
