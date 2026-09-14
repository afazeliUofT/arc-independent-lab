"""Actual048 archive/workflow/conformance; publication uses disposable local Git."""
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / 'delivery/ARC_Independent_Lab_048_HOME.zip'
EXPECTED_SHA = '9169590117f675a65ef361414d9bc88170921ddf8de4d3be2691813a4e1e4b63'
BASE = 'f25777a324ac49b9828b4fdf155749c7d1b80626'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def git(root, *args):
    return subprocess.check_output(['git', '-c', 'core.hooksPath=/dev/null',
                                   '-C', str(root), *args], stderr=subprocess.PIPE, timeout=120)


def main():
    started = time.monotonic()
    launch = load('_final048_launch', ROOT / 'scripts/launch048_home.py')
    raw = ARCHIVE.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_SHA
    _, release = launch.archive_payloads(raw, EXPECTED_SHA)
    with tempfile.TemporaryDirectory(prefix='complete048_', dir=ROOT / 'delivery') as folder:
        base = Path(folder)
        home = base / 'home'
        home.mkdir()
        remote = base / 'remote.git'
        git(base, 'clone', '--bare', '--no-local', str(ROOT), str(remote))
        git(remote, 'update-ref', 'refs/heads/main', BASE)
        lab = home / 'ARC_Independent_Lab'
        git(home, 'clone', '--no-local', str(remote), str(lab))
        git(lab, 'config', 'user.name', 'Offline048 Validation')
        git(lab, 'config', 'user.email', 'offline048@example.invalid')
        git(remote, 'update-ref', 'refs/heads/main', release['release_commit'])
        launch.REMOTE = str(remote)
        calls, results = [], []

        def runner(command, **kwargs):
            package = Path(command[command.index('--package') + 1])
            workflow = load('_final048_extracted_workflow', package / 'source/scripts/checkpoint048_workflow.py')
            workflow.safe.REMOTE = str(remote)

            def actual_child(source, frozen, state, lock_fd):
                calls.append('ACTUAL_FROZEN_UNIT_SUITES')
                return workflow.run_conformance(source, frozen, state, lock_fd)

            results.append(workflow.workflow(lab, package, EXPECTED_SHA, runner=actual_child))
            return subprocess.CompletedProcess(command, 0)

        launch.launch(raw, EXPECTED_SHA, home=home, runner=runner)
        first_commit = git(lab, 'rev-parse', 'HEAD').decode().strip()
        launch.launch(raw, EXPECTED_SHA, home=home, runner=runner)
        assert len(calls) == 1 and results[0] == results[1]
        assert results[0]['status'] == 'KERNEL_CONFORMANCE_PASSED'
        assert git(remote, 'rev-parse', 'main').decode().strip() == first_commit
        changed = git(lab, 'diff', '--name-only', release['release_commit'], first_commit).decode().splitlines()
        expected = [results[0]['report_path'], results[0]['receipt_path']]
        assert sorted(changed) == sorted(expected)
        report_raw = (lab / results[0]['report_path']).read_bytes()
        receipt_raw = (lab / results[0]['receipt_path']).read_bytes()
        report, receipt = json.loads(report_raw), json.loads(receipt_raw)
        assert receipt['report_sha256'] == hashlib.sha256(report_raw).hexdigest()
        conformance = report['conformance_run']['conformance']
        assert conformance['tests_run'] == len(release['test_ids'])
        assert all(row['status'] == 'PASSED' for row in conformance['tests'])
        result = {'kind': 'P3_COMPLETE_PACKAGE_VALIDATION_048_v1', 'status': 'PASSED',
                  'archive_sha256': EXPECTED_SHA, 'archive_bytes': len(raw),
                  'release_commit': release['release_commit'],
                  'actual_extracted_workflow_used': True,
                  'actual_unit_invocations': len(calls),
                  'actual_conformance': conformance,
                  'repeated_command_reexecuted_tests': False,
                  'local_git_publication_exact_paths': sorted(changed),
                  'published_report_sha256': hashlib.sha256(report_raw).hexdigest(),
                  'published_receipt_sha256': hashlib.sha256(receipt_raw).hexdigest(),
                  'target_profile_native_or_hpc_runs': 0,
                  'accounting_correction_complete': False,
                  'target_admitted': False,
                  'substitutions': [
                      'Windows Downloads discovery replaced by exact supplied ZIP and temporary home',
                      'Authorized GitHub transport identity replaced in memory by disposable local bare Git',
                      'Launcher child handoff loads exact extracted workflow in-process; actual conformance remains an isolated subprocess'],
                  'scope': 'Actual complete048 package and tests; does not certify live WSL registry or GitHub authentication.',
                  'helper_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  'wall_seconds': time.monotonic() - started}
    output = ROOT / 'evidence/P3_PUBLISHED_PACKAGE_VALIDATION_048.json'
    assert not output.exists(), 'Preserve validation evidence'
    output.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'tests_run': conformance['tests_run'],
                      'actual_unit_invocations': len(calls), 'repeat_reused_result': True,
                      'wall_seconds': result['wall_seconds']}, indent=2))


if __name__ == '__main__':
    main()
