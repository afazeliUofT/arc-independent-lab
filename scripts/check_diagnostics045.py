#!/usr/bin/env python3
"""Run the finite fabricated045 adapter conformance suite once, preserving outcomes.

No043/044 component is reprofiled. This is correctness evidence and process usage
for the conformance invocation, not a full-work resource or scientific result.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib
import json
import os
from pathlib import Path
import resource
import signal
import sys
import tempfile
import time
import traceback
import unittest

sys.dont_write_bytecode = True
SOURCES = ('configs/P3_DIAGNOSTIC_FIXTURES_045.json', 'scripts/accounting043.py',
    'scripts/check_diagnostics045.py', 'scripts/diagnostics045.py',
    'scripts/reference_n1_043.py', 'scripts/reference_n3_043.py', 'tests/test_diagnostics045.py')
KIND = 'P3_DIAGNOSTIC_CONFORMANCE_045_v1'
WALL_SECONDS = 270
ADDRESS_SPACE = 2 * 1024 ** 3


def canonical(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False) + '\n').encode()


def atomic_json(path, value):
    raw = canonical(value)
    fd, name = tempfile.mkstemp(prefix='.diagnostic045_', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
        parent = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(parent)
        finally:
            os.close(parent)
    finally:
        if os.path.lexists(name):
            os.unlink(name)


class Deadline(KeyboardInterrupt):
    pass


def expire(signum, frame):
    raise Deadline('INNER_WALL_LIMIT')


def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


class NamedResults(unittest.TestResult):
    def __init__(self, report, save):
        super().__init__()
        self.report, self.save = report, save
        self.current = None

    def startTest(self, test):
        super().startTest(test)
        self.current = {'test': test.id(), 'status': 'INTERRUPTED', 'failure': None, 'metrics': None}
        self.report['active_test'] = test.id()
        self.started, self.cpu_started = time.monotonic(), time.process_time()
        self.save()

    def record(self, status, error=None):
        self.current['status'] = status
        if error is not None:
            self.current['failure'] = {'class': error[0].__name__,
                'traceback': ''.join(traceback.format_exception(*error))[-16000:]}

    def addSuccess(self, test):
        super().addSuccess(test)
        self.record('PASSED')

    def addError(self, test, err):
        super().addError(test, err)
        self.record('ERROR', err)

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.record('FAILED', err)

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.record('SKIPPED')
        self.current['failure'] = {'class': 'Skip', 'reason': str(reason)}

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self.record('EXPECTED_FAILURE', err)

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self.record('UNEXPECTED_SUCCESS')

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is not None:
            self.record('FAILED' if issubclass(err[0], test.failureException) else 'ERROR', err)

    def stopTest(self, test):
        self.current['metrics'] = {'wall_seconds': time.monotonic() - self.started,
            'process_cpu_seconds': time.process_time() - self.cpu_started,
            'process_peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            'rss_scope': 'CUMULATIVE_PROCESS_HIGH_WATER_NOT_TEST_ALLOCATION'}
        self.report['test_outcomes'].append(self.current)
        self.report['active_test'] = None
        self.current = None
        self.save()
        super().stopTest(test)


def run(root, output):
    root, output = Path(root).resolve(), Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    target = output / 'REPORT.json'
    if target.exists():
        return json.loads(target.read_text())
    hashes = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in SOURCES}
    config = json.loads((root / 'configs/P3_DIAGNOSTIC_FIXTURES_045.json').read_text())
    families = config['required_case_families']
    if (config.get('kind') != 'P3_DIAGNOSTIC_FIXTURES_045_v1' or type(families) is not list or
            not families or not all(type(name) is str and name for name in families) or
            len(families) != len(set(families))):
        raise ValueError('INVALID_REQUIRED_CASE_FAMILIES')
    started, cpu_started = time.monotonic(), time.process_time()
    child_started = resource.getrusage(resource.RUSAGE_CHILDREN)
    report = {'kind': KIND, 'status': 'INCOMPLETE', 'passed': False, 'interruption': None,
        'source_hashes': hashes, 'planned_test_ids': [], 'test_outcomes': [], 'active_test': None,
        'case_results': {}, 'required_case_families': families, 'metrics': {}, 'target_experiment_started': False,
        'target_execution_admitted': False, 'native_started': False, 'outcome_blind': True,
        'complete_work_budget_admitted': False, 'full_resource_profile_started': False,
        'original043044_remeasured': False, 'automatic_rerun_permitted': False,
        'B_comp': None, 'B_mem': None,
        'limits': {'inner_wall_seconds': WALL_SECONDS, 'address_space_bytes_per_process': ADDRESS_SPACE,
            'available_cpus_used': 1, 'address_space_is_not_aggregate_rss_cap': True},
        'host': {'python': sys.version.split()[0], 'platform': sys.platform,
            'ambient_conditions': 'UNCONTROLLED_NOT_CLASSIFIED_QUIET_OR_CONTENDED'},
        'limitations': ['Finite fabricated adapter conformance; no target panel scoring or efficacy result',
            'Process metrics measure this suite, not complete acquisition/replay/snapshot-overlap cost',
            'Peak RSS is the invocation process high-water mark, not exact allocation accounting',
            'No043/044 measurement or consumed reservation is reset']}

    def save():
        usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        report['metrics'] = {'wall_seconds': time.monotonic() - started,
            'process_cpu_seconds': time.process_time() - cpu_started,
            'child_cpu_seconds': usage.ru_utime + usage.ru_stime - child_started.ru_utime - child_started.ru_stime,
            'process_peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            'scope': '045_CONFORMANCE_INVOCATION_ONLY'}
        atomic_json(target, report)

    try:
        with (output / 'EXECUTION_RESERVED.json').open('x') as stream:
            stream.write(canonical({'kind': KIND, 'source_hashes': hashes,
                'maximum_invocations': 1, 'automatic_rerun_permitted': False}).decode())
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError:
        report['interruption'] = 'PRIOR_RESERVATION_WITHOUT_REPORT'
        save()
        return report
    save()
    module = None
    try:
        cpus = sorted(os.sched_getaffinity(0))
        os.sched_setaffinity(0, {cpus[0]})
        resource.setrlimit(resource.RLIMIT_AS, (ADDRESS_SPACE,) * 2)
        signal.signal(signal.SIGALRM, expire)
        signal.setitimer(signal.ITIMER_REAL, WALL_SECONDS)
        sys.path[:0] = [str(root / 'scripts'), str(root / 'tests')]
        module = importlib.import_module('test_diagnostics045')
        suite = unittest.TestLoader().loadTestsFromModule(module)
        report['planned_test_ids'] = [test.id() for test in flatten(suite)]
        save()
        result = NamedResults(report, save)
        suite.run(result)
        report['passed'] = result.wasSuccessful() and not result.skipped and result.testsRun > 0 and \
            len(report['test_outcomes']) == len(report['planned_test_ids']) and \
            all(row['status'] == 'PASSED' for row in report['test_outcomes'])
        report['status'] = 'COMPLETED' if report['passed'] else 'FAILED_CONFORMANCE'
        if not report['passed']:
            report['interruption'] = 'CONFORMANCE_NOT_ALL_PASSED'
    except (Deadline, MemoryError) as error:
        report['interruption'] = type(error).__name__
    except Exception as error:
        report.update(status='FAILED_CONFORMANCE', interruption=type(error).__name__)
        report['runner_failure'] = {'class': type(error).__name__,
            'traceback': ''.join(traceback.format_exception(error))[-16000:]}
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        if module is not None and hasattr(module, 'get_results'):
            try:
                cases = module.get_results()
                if type(cases) is not dict:
                    raise TypeError('CASE_RESULTS_MUST_BE_DICTIONARY')
                canonical(cases)
                report['case_results'] = cases
                observed = cases.get('cases')
                coverage = type(observed) is dict and all(type(observed.get(name)) is dict and
                    observed[name].get('status') == 'PASSED' for name in families)
                if report['status'] == 'COMPLETED' and not coverage:
                    report.update(status='FAILED_CONFORMANCE', passed=False, interruption='CASE_FAMILIES_INCOMPLETE')
            except Exception as error:
                report.update(status='FAILED_CONFORMANCE', passed=False, interruption='CASE_RESULTS_INVALID')
                report['runner_failure'] = {'class': type(error).__name__,
                    'traceback': ''.join(traceback.format_exception(error))[-16000:]}
        if report['status'] == 'COMPLETED' and not report['case_results']:
            report.update(status='FAILED_CONFORMANCE', passed=False, interruption='CASE_FAMILIES_INCOMPLETE')
        save()
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = run(args.root, args.output)
    print(json.dumps({'status': report['status'], 'tests_returned': len(report['test_outcomes']),
        'tests_planned': len(report['planned_test_ids']), 'target_execution_admitted': False}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
