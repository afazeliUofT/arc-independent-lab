#!/usr/bin/env python3
"""Run the frozen048 accounting conformance once and publish only its report/receipt."""
from __future__ import annotations

import argparse
import ctypes
import fcntl
import importlib.util
import os
from pathlib import Path
import resource
import signal
import stat
import subprocess
import sys
import time
import unittest

sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location('_checkpoint048_safe',
                                             Path(__file__).absolute().with_name('launch048_home.py'))
safe = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = safe
_spec.loader.exec_module(safe)
MAX_REPORT = 512 * 1024
MAX_LOG = 512 * 1024
COMMIT_MESSAGE = 'Checkpoint048: record frozen accounting kernel conformance and receipt'


def names(raw):
    return set(raw.decode('utf-8').split('\0')) - {''}


def ancestor(lab, first, second):
    return not safe.git(lab, 'rev-list', '--max-count=1', first, '^' + second).strip()


def source_inventory(source, release):
    safe.directory(source)
    actual = set()
    for parent, dirs, files in os.walk(source, followlinks=False):
        for name in dirs:
            safe.directory(Path(parent) / name)
        actual.update((Path(parent) / n).relative_to(source).as_posix() for n in files)
    safe.require(actual == set(safe.SOURCE_PATHS), 'source_inventory_differs')
    hashes = {p: safe.sha(safe.read_regular(source / p)) for p in safe.SOURCE_PATHS}
    safe.require(hashes == release['source_sha256'], 'frozen_source_bytes_differ')
    return hashes


def flatten(suite):
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            yield from flatten(test)
        else:
            yield test


class PublicResult(unittest.TextTestResult):
    """Retain test identities/status, never raw exception values, in public output."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rows = {}

    def startTest(self, test):
        self.rows[test.id()] = {'test_id': test.id(), 'status': 'STARTED'}
        super().startTest(test)

    def record(self, test, status, error=None):
        row = self.rows[test.id()]
        row['status'] = status
        if error is not None:
            name = error[0].__name__
            row['error_type'] = name if safe.re.fullmatch('[A-Za-z_][A-Za-z_0-9]{0,79}', name) else 'Exception'

    def addSuccess(self, test):
        self.record(test, 'PASSED')
        super().addSuccess(test)

    def addFailure(self, test, err):
        self.record(test, 'FAILED', err)
        super().addFailure(test, err)

    def addError(self, test, err):
        self.record(test, 'ERROR', err)
        super().addError(test, err)

    def addSkip(self, test, reason):
        self.record(test, 'SKIPPED')
        super().addSkip(test, reason)

    def addExpectedFailure(self, test, err):
        self.record(test, 'EXPECTED_FAILURE', err)
        super().addExpectedFailure(test, err)

    def addUnexpectedSuccess(self, test):
        self.record(test, 'UNEXPECTED_SUCCESS')
        super().addUnexpectedSuccess(test)

    def addSubTest(self, test, subtest, err):
        if err is not None:
            self.record(test, 'FAILED' if issubclass(err[0], test.failureException) else 'ERROR', err)
        super().addSubTest(test, subtest, err)


def conformance_child(source, release):
    start, cpu_start = time.monotonic(), time.process_time()
    before = source_inventory(source, release)
    suite = unittest.TestSuite()
    for path in safe.SUITES:
        name = Path(path).stem
        spec = importlib.util.spec_from_file_location(name, source / path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
    ids = [test.id() for test in flatten(suite)]
    safe.require(sorted(ids) == sorted(release['test_ids']) and len(ids) == len(set(ids)),
                 'loaded_tests_differ_from_frozen_manifest')
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2, resultclass=PublicResult).run(suite)
    after = source_inventory(source, release)
    rows = [result.rows.get(i, {'test_id': i, 'status': 'NOT_RUN'}) for i in release['test_ids']]
    passed = result.wasSuccessful() and all(r['status'] == 'PASSED' for r in rows)
    report = {'kind': 'P3_ACCOUNTING_048_FROZEN_CONFORMANCE_v1',
              'status': 'KERNEL_CONFORMANCE_PASSED' if passed else 'KERNEL_CONFORMANCE_FAILED',
              'release_commit': release['release_commit'], 'suites': list(safe.SUITES),
              'expected_test_count': len(ids), 'tests_run': result.testsRun, 'tests': rows,
              'source_sha256_before': before, 'source_sha256_after': after,
              'wall_seconds': time.monotonic() - start, 'cpu_seconds': time.process_time() - cpu_start,
              'accounting_correction_complete': False, 'target_admitted': False,
              'no_target_runs': True, 'no_profile_runs': True,
              'reviewer_started': False, 'model_started': False}
    raw = safe.canonical(report)
    safe.require(len(raw) <= MAX_REPORT, 'child_report_size_limit')
    sys.stdout.buffer.write(raw)
    sys.stdout.buffer.flush()
    return 0 if passed else 1


def validate_child_report(report, release):
    safe.require(type(report) is dict and set(report) == {
        'kind', 'status', 'release_commit', 'suites', 'expected_test_count', 'tests_run', 'tests',
        'source_sha256_before', 'source_sha256_after', 'wall_seconds', 'cpu_seconds',
        'accounting_correction_complete', 'target_admitted', 'no_target_runs', 'no_profile_runs',
        'reviewer_started', 'model_started'} and
                 report.get('kind') == 'P3_ACCOUNTING_048_FROZEN_CONFORMANCE_v1'
                 and report.get('release_commit') == release['release_commit']
                 and report.get('suites') == list(safe.SUITES)
                 and report.get('expected_test_count') == len(release['test_ids'])
                 and report.get('source_sha256_before') == release['source_sha256']
                 and report.get('source_sha256_after') == release['source_sha256']
                 and report.get('accounting_correction_complete') is False
                 and report.get('target_admitted') is False
                 and report.get('no_target_runs') is True and report.get('no_profile_runs') is True
                 and report.get('reviewer_started') is False and report.get('model_started') is False,
                 'child_report_identity_or_scope_differs')
    rows = report.get('tests')
    safe.require(type(rows) is list and len(rows) == len(release['test_ids']) and
                 all(type(r) is dict for r in rows) and
                 [r.get('test_id') for r in rows] == release['test_ids'] and
                 all(type(r) is dict and set(r) <= {'test_id', 'status', 'error_type'} and
                     r.get('status') in ('PASSED', 'FAILED', 'ERROR', 'SKIPPED', 'EXPECTED_FAILURE',
                                         'UNEXPECTED_SUCCESS', 'STARTED', 'NOT_RUN') and
                     ('error_type' not in r or (type(r['error_type']) is str and
                        safe.re.fullmatch('[A-Za-z_][A-Za-z_0-9]{0,79}', r['error_type'])))
                     for r in rows), 'child_test_rows_differ')
    passed = all(r['status'] == 'PASSED' for r in rows)
    safe.require(report.get('status') == ('KERNEL_CONFORMANCE_PASSED' if passed else 'KERNEL_CONFORMANCE_FAILED')
                 and type(report.get('tests_run')) is int and 0 <= report['tests_run'] <= len(rows)
                 and (not passed or report['tests_run'] == len(rows)), 'child_status_differs')
    for key in ('wall_seconds', 'cpu_seconds'):
        safe.require(type(report.get(key)) in (int, float) and 0 <= report[key] <= 600,
                     'invalid_child_time')


def validate_outcome(outcome, release):
    base = {'kind', 'release_commit', 'status', 'invocation_count', 'raw_logs_public'}
    measured = {'returncode', 'wall_seconds', 'cpu_seconds', 'stdout_bytes', 'stdout_sha256',
                'stderr_bytes', 'stderr_sha256'}
    safe.require(type(outcome) is dict and outcome.get('kind') == 'P3_CHECKPOINT_048_RUN_v1' and
                 outcome.get('release_commit') == release['release_commit'] and
                 type(outcome.get('invocation_count')) is int and outcome['invocation_count'] == 1 and
                 outcome.get('raw_logs_public') is False, 'invalid_saved_run_identity')
    status = outcome.get('status')
    if status == 'INTERRUPTED_NO_AUTOMATIC_RERUN':
        safe.require(set(outcome) == base, 'invalid_interrupted_run_schema')
        return
    safe.require(status in ('KERNEL_CONFORMANCE_PASSED', 'KERNEL_CONFORMANCE_FAILED',
                             'CONFORMANCE_TIMEOUT', 'CONFORMANCE_PROCESS_FAILED', 'CONFORMANCE_INVALID_REPORT'),
                 'invalid_saved_run_status')
    has_report = status in ('KERNEL_CONFORMANCE_PASSED', 'KERNEL_CONFORMANCE_FAILED')
    safe.require(set(outcome) == base | measured | ({'conformance'} if has_report else set()),
                 'invalid_saved_run_schema')
    safe.require(type(outcome['returncode']) is int and -128 <= outcome['returncode'] <= 255,
                 'invalid_saved_run_returncode')
    for key in ('wall_seconds', 'cpu_seconds'):
        safe.require(type(outcome[key]) in (int, float) and 0 <= outcome[key] <= 600,
                     'invalid_saved_run_time')
    for key in ('stdout', 'stderr'):
        safe.require(type(outcome[key + '_bytes']) is int and 0 <= outcome[key + '_bytes'] <= MAX_LOG and
                     type(outcome[key + '_sha256']) is str and
                     safe.re.fullmatch('[0-9a-f]{64}', outcome[key + '_sha256']),
                     'invalid_saved_log_identity')
    if has_report:
        validate_child_report(outcome['conformance'], release)
        safe.require(outcome['conformance']['status'] == status and
                     outcome['returncode'] == (0 if status == 'KERNEL_CONFORMANCE_PASSED' else 1),
                     'saved_exit_status_differs')
    elif status == 'CONFORMANCE_INVALID_REPORT':
        safe.require(outcome['returncode'] in (0, 1), 'invalid_report_exit_differs')
    elif status == 'CONFORMANCE_PROCESS_FAILED':
        safe.require(outcome['returncode'] not in (0, 1), 'failed_process_exit_differs')


def private_log(path):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    safe.require(stat.S_ISREG(os.fstat(fd).st_mode) and os.fstat(fd).st_nlink == 1,
                 'unsafe_private_log')
    return fd


def run_conformance(source, release, state, lock_fd):
    parent_pid = os.getpid()
    def limits():
        # The child cannot outlive a killed parent on the supported Linux/WSL host.
        libc = ctypes.CDLL(None, use_errno=True)
        if libc.prctl(1, signal.SIGKILL, 0, 0, 0) != 0 or os.getppid() != parent_pid:
            os._exit(125)
        resource.setrlimit(resource.RLIMIT_AS, (2 * 1024 ** 3,) * 2)
        resource.setrlimit(resource.RLIMIT_CPU, (300, 300))
        resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_LOG,) * 2)
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    start = time.monotonic()
    usage_start = resource.getrusage(resource.RUSAGE_CHILDREN)
    stdout_fd, stderr_fd = private_log(state / 'stdout.raw'), private_log(state / 'stderr.raw')
    try:
        env = {key: value for key, value in os.environ.items()
               if key in ('PATH', 'LANG', 'LC_ALL', 'TZ')}
        child = subprocess.Popen([sys.executable, '-I', '-S', '-B', '-u',
                                  str(source / 'scripts/checkpoint048_workflow.py'),
                                  '--conformance-child', '--source', str(source),
                                  '--release', str(source.parent / 'package_release.json')],
                                 cwd=source, stdin=subprocess.DEVNULL, stdout=stdout_fd, stderr=stderr_fd,
                                 env=env, preexec_fn=limits, start_new_session=True, pass_fds=(lock_fd,))
        timed_out = False
        try:
            code = child.wait(timeout=300)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(child.pid, signal.SIGKILL)
            code = child.wait(timeout=10)
        except BaseException:
            if child.poll() is None:
                os.killpg(child.pid, signal.SIGKILL)
            child.wait(timeout=10)
            raise
    finally:
        os.close(stdout_fd)
        os.close(stderr_fd)
    source_inventory(source, release)
    stdout = safe.read_regular(state / 'stdout.raw', MAX_LOG)
    stderr = safe.read_regular(state / 'stderr.raw', MAX_LOG)
    usage_end = resource.getrusage(resource.RUSAGE_CHILDREN)
    outcome = {'kind': 'P3_CHECKPOINT_048_RUN_v1', 'release_commit': release['release_commit'],
               'returncode': code, 'wall_seconds': time.monotonic() - start,
               'cpu_seconds': usage_end.ru_utime + usage_end.ru_stime - usage_start.ru_utime - usage_start.ru_stime,
               'stdout_bytes': len(stdout), 'stdout_sha256': safe.sha(stdout),
               'stderr_bytes': len(stderr), 'stderr_sha256': safe.sha(stderr),
               'raw_logs_public': False, 'invocation_count': 1,
               'status': 'CONFORMANCE_TIMEOUT' if timed_out else 'CONFORMANCE_PROCESS_FAILED'}
    if not timed_out and code in (0, 1):
        try:
            report = safe.parse(stdout)
            validate_child_report(report, release)
            safe.require((code == 0) == (report['status'] == 'KERNEL_CONFORMANCE_PASSED'),
                         'child_exit_status_differs')
            outcome.update(status=report['status'], conformance=report)
        except (safe.Stop, ValueError, UnicodeError, TypeError, AttributeError):
            outcome['status'] = 'CONFORMANCE_INVALID_REPORT'
    validate_outcome(outcome, release)
    return outcome


def conformance_once(state, source, release, lock_fd, runner):
    reservation = safe.canonical({'kind': 'P3_CHECKPOINT_048_RESERVATION_v1',
        'release_commit': release['release_commit'], 'source_sha256': release['source_sha256'],
        'suites': list(safe.SUITES), 'test_ids': release['test_ids'],
        'max_invocations': 1, 'max_seconds': 300, 'automatic_reexecution': False})
    result_path = state / 'RUN.json'
    if os.path.lexists(result_path):
        safe.require(safe.read_regular(state / 'RESERVED.json') == reservation,
                     'changed_saved_reservation_preserved')
        outcome = safe.parse(safe.read_regular(result_path, MAX_REPORT))
        validate_outcome(outcome, release)
        for kind in ('stdout', 'stderr'):
            if kind + '_sha256' in outcome:
                raw = safe.read_regular(state / (kind + '.raw'), MAX_LOG)
                safe.require(safe.sha(raw) == outcome[kind + '_sha256'] and
                             len(raw) == outcome[kind + '_bytes'], 'changed_private_log_preserved')
                if kind == 'stdout' and 'conformance' in outcome:
                    safe.require(raw == safe.canonical(outcome['conformance']),
                                 'saved_conformance_differs_from_private_stdout')
        return outcome
    if os.path.lexists(state / 'RESERVED.json'):
        safe.require(safe.read_regular(state / 'RESERVED.json') == reservation,
                     'changed_saved_reservation_preserved')
        outcome = {'kind': 'P3_CHECKPOINT_048_RUN_v1', 'release_commit': release['release_commit'],
                   'status': 'INTERRUPTED_NO_AUTOMATIC_RERUN', 'invocation_count': 1,
                   'raw_logs_public': False}
    else:
        safe.same_or_new(state / 'RESERVED.json', reservation)
        outcome = runner(source, release, state, lock_fd)
    validate_outcome(outcome, release)
    safe.same_or_new(result_path, safe.canonical(outcome))
    return outcome


def expected_outputs(release, outcome):
    validate_outcome(outcome, release)
    base = 'artifacts/CHECKPOINT_048_CONFORMANCE/' + release['release_commit']
    report = {'kind': 'P3_CHECKPOINT_048_REPORT_v1', 'status': outcome['status'],
              'release_commit': release['release_commit'], 'parent_commit': release['parent_commit'],
              'source_sha256': release['source_sha256'], 'conformance_run': outcome,
              'execution_scope': 'FROZEN_ACCOUNTING_KERNEL_AND_STATIC_BOUND_CONFORMANCE_ONLY',
              'accounting_correction_complete': False, 'target_admitted': False,
              'no_target_runs': True, 'no_profile_runs': True,
              'reviewer_started': False, 'model_started': False}
    raw = safe.canonical(report)
    safe.require(len(raw) <= MAX_REPORT, 'public_report_size_limit')
    receipt = {'kind': 'P3_CHECKPOINT_048_RECEIPT_v1', 'status': 'CONFORMANCE_RECORDED',
               'conformance_status': outcome['status'], 'release_commit': release['release_commit'],
               'repository': safe.REPOSITORY, 'report_path': base + '/REPORT.json',
               'report_sha256': safe.sha(raw), 'accounting_correction_complete': False,
               'target_admitted': False, 'raw_logs_public': False}
    return {base + '/REPORT.json': raw, base + '/RECEIPT.json': safe.canonical(receipt)}


def check_checkout(lab, expected):
    safe.repository_check(lab)
    for args in (('diff', '--name-only', '-z'), ('diff', '--cached', '--name-only', '-z'),
                 ('ls-files', '--others', '--exclude-standard', '-z')):
        changed = names(safe.git(lab, *args))
        safe.require(changed <= set(expected), 'dirty_canonical_checkout_preserved')
        for name in changed:
            safe.require(safe.read_regular(lab / name, MAX_REPORT) == expected[name],
                         'changed048_output_preserved')
            if '--cached' in args:
                safe.require(safe.git(lab, 'show', ':' + name) == expected[name], 'changed048_index_preserved')
    for name, body in expected.items():
        if os.path.lexists(lab / name):
            safe.require(safe.read_regular(lab / name, MAX_REPORT) == body,
                         'changed_existing048_result_preserved')


def sync_release(lab, source, release, outputs):
    check_checkout(lab, outputs)
    safe.git(lab, 'fetch', '--no-tags', 'origin', 'refs/heads/main')
    remote = safe.git(lab, 'rev-parse', 'FETCH_HEAD').decode().strip()
    commit = release['release_commit']
    safe.require(ancestor(lab, release['parent_commit'], commit) and ancestor(lab, commit, remote),
                 'published_release_ancestry_differs')
    for name in safe.SOURCE_PATHS:
        safe.require(safe.git(lab, 'show', commit + ':' + name) == safe.read_regular(source / name),
                     'package_source_differs_from_release_commit')
    head = safe.git(lab, 'rev-parse', 'HEAD').decode().strip()
    for ahead in safe.git(lab, 'rev-list', remote + '..' + head).decode().splitlines():
        parents = safe.git(lab, 'rev-list', '--parents', '-n', '1', ahead).decode().split()
        changed = names(safe.git(lab, 'diff-tree', '--no-commit-id', '--name-only', '-r', '-z', ahead))
        safe.require(outputs and len(parents) == 2 and changed == set(outputs) and
                     safe.git(lab, 'show', '-s', '--format=%s', ahead).decode().strip() == COMMIT_MESSAGE and
                     all(safe.git(lab, 'show', ahead + ':' + name) == body for name, body in outputs.items()),
                     'unrelated_unpublished_local_commit_preserved')
    for name in names(safe.git(lab, 'ls-tree', '-r', '--name-only', '-z', remote, '--', *sorted(outputs))) if outputs else ():
        safe.require(name in outputs and safe.git(lab, 'show', remote + ':' + name) == outputs[name],
                     'changed_remote048_result_preserved')
    if ancestor(lab, head, remote):
        safe.git(lab, 'merge', '--ff-only', '--no-overwrite-ignore', remote)
    else:
        safe.require(ancestor(lab, remote, head), 'canonical_and_remote_diverged_saved_conformance_preserved')
    check_checkout(lab, outputs)


def publish(lab, source, release, outputs):
    sync_release(lab, source, release, outputs)
    for name, raw in outputs.items():
        safe.same_or_new(lab / name, raw)
    paths = sorted(outputs)
    safe.git(lab, 'add', '--', *paths)
    staged = names(safe.git(lab, 'diff', '--cached', '--name-only', '-z'))
    safe.require(staged <= set(outputs), 'unrelated_staged_files_preserved')
    if staged:
        safe.git(lab, 'commit', '-m', COMMIT_MESSAGE, '--', *paths)
    for name, raw in outputs.items():
        safe.require(safe.git(lab, 'show', 'HEAD:' + name) == raw, 'committed048_result_differs')
    safe.git(lab, 'push', 'origin', 'HEAD:refs/heads/main')
    head = safe.git(lab, 'rev-parse', 'HEAD').decode().strip()
    remote = safe.git(lab, 'ls-remote', '--exit-code', 'origin', 'refs/heads/main').decode().split()
    safe.require(remote == [head, 'refs/heads/main'], 'remote_publication_not_confirmed')
    return head


def workflow(lab, package, archive_sha256, *, runner=None):
    lab, package = Path(lab).absolute(), Path(package).absolute()
    safe.require(package == lab / 'delivery/P3_CHECKPOINT_048' / archive_sha256 / 'package',
                 'package_not_at_expected_delivery_location')
    files, release = safe.archive_payloads(safe.read_regular(package.parent / 'PACKAGE.zip'), archive_sha256)
    for name, body in files.items():
        safe.require(safe.read_regular(package / name) == body, 'extracted_package_differs')
    source = package / 'source'
    source_inventory(source, release)
    safe.repository_check(lab)
    state = lab / '.git/checkpoint048' / archive_sha256
    safe.directory(state, create=True)
    lock = state / 'WORKFLOW.lock'
    if os.path.lexists(lock):
        safe.read_regular(lock)
    fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        safe.require(stat.S_ISREG(os.fstat(fd).st_mode) and os.fstat(fd).st_nlink == 1,
                     'unsafe_workflow_lock')
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise safe.Stop('048_workflow_or_child_already_running')
        # Publication retries admit only previously saved exact output paths.
        outputs = {}
        if os.path.lexists(state / 'RUN.json'):
            prior = conformance_once(state, source, release, fd, runner)
            outputs = expected_outputs(release, prior)
        sync_release(lab, source, release, outputs)
        outcome = conformance_once(state, source, release, fd,
                                   run_conformance if runner is None else runner)
        source_inventory(source, release)
        outputs = expected_outputs(release, outcome)
        marker = safe.canonical({'release_commit': release['release_commit'],
                                 'outputs': {n: safe.sha(b) for n, b in outputs.items()}})
        safe.same_or_new(state / 'COMPLETE.json', marker)
        commit = publish(lab, source, release, outputs)
        return {'status': outcome['status'], 'commit': commit,
                'report_path': next(n for n in outputs if n.endswith('/REPORT.json')),
                'receipt_path': next(n for n in outputs if n.endswith('/RECEIPT.json'))}
    finally:
        os.close(fd)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lab', type=Path, default=Path.home() / 'ARC_Independent_Lab')
    parser.add_argument('--package', type=Path)
    parser.add_argument('--archive-sha256')
    parser.add_argument('--conformance-child', action='store_true')
    parser.add_argument('--source', type=Path)
    parser.add_argument('--release', type=Path)
    args = parser.parse_args()
    if args.conformance_child:
        safe.require(args.source is not None and args.release is not None, 'child_source_and_release_required')
        return conformance_child(args.source.absolute(), safe.parse(safe.read_regular(args.release)))
    safe.require(args.package is not None and args.archive_sha256 is not None, 'package_and_hash_required')
    result = workflow(args.lab, args.package, args.archive_sha256)
    print('Checkpoint048: ' + result['status'])
    print('GitHub report: https://github.com/' + safe.REPOSITORY + '/blob/' + result['commit'] + '/' + result['report_path'])
    print('GitHub receipt: https://github.com/' + safe.REPOSITORY + '/blob/' + result['commit'] + '/' + result['receipt_path'])
    print('Only accounting kernel/static conformance was admitted. The full correction and target experiment remain unadmitted.')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (safe.Stop, OSError, ValueError, UnicodeError, TypeError, subprocess.SubprocessError) as error:
        reason = str(error) if isinstance(error, safe.Stop) else type(error).__name__
        print('STOP: ' + reason + '. Existing files and saved conformance are preserved.', file=sys.stderr)
        raise SystemExit(1)
