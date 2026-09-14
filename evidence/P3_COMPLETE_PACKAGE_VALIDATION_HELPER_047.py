"""Final real047 bundle/parser seam, with publication only to disposable local Git."""
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
ARCHIVE = ROOT / 'delivery/ARC_Independent_Lab_047_HOME.zip'
EXPECTED_SHA = '8a8da78dccdd152367135430b43d3776dba95c975326437dff45a399d7397540'
BASE = '15574d706eab28c1e099aba8447d527eb5047d91'


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
    launch = load('_full047_launch', ROOT / 'scripts/launch047_home.py')
    raw = ARCHIVE.read_bytes()
    payloads, release = launch.archive_payloads(raw, EXPECTED_SHA)
    with tempfile.TemporaryDirectory(prefix='complete047-', dir=ROOT / 'delivery') as folder:
        base = Path(folder)
        home = base / 'home'
        home.mkdir()
        remote = base / 'remote.git'
        git(base, 'clone', '--bare', '--no-local', str(ROOT), str(remote))
        git(remote, 'update-ref', 'refs/heads/main', BASE)
        lab = home / 'ARC_Independent_Lab'
        git(home, 'clone', '--no-local', str(remote), str(lab))
        git(lab, 'config', 'user.name', 'Offline047 Validation')
        git(lab, 'config', 'user.email', 'offline047@example.invalid')
        launch.REMOTE = str(remote)
        calls, outputs = [], []

        def runner(command, **kwargs):
            package = Path(command[command.index('--package') + 1])
            workflow = load('_full047_extracted_workflow', package / 'checkpoint047_workflow.py')
            workflow.safe.REMOTE = str(remote)
            def actual_parser(snapshot, output):
                calls.append('ACTUAL_READ_ONLY_ASSESSOR')
                workflow.run_assessor(snapshot, output)
            outputs.append(workflow.workflow(lab, package, EXPECTED_SHA, assessor=actual_parser))
            return subprocess.CompletedProcess(command, 0)

        launch.launch(raw, EXPECTED_SHA, home=home, runner=runner)
        first_commit = git(lab, 'rev-parse', 'HEAD').decode().strip()
        launch.launch(raw, EXPECTED_SHA, home=home, runner=runner)
        assert len(calls) == 1 and outputs[0] == outputs[1]
        assert git(remote, 'rev-parse', 'main').decode().strip() == first_commit
        changed = git(lab, 'diff', '--name-only', release['release_commit'], first_commit).decode().splitlines()
        expected = [outputs[0]['receipt_path'], outputs[0]['report_path']]
        assert sorted(changed) == sorted(expected)
        result = {'kind': 'P3_COMPLETE_PACKAGE_VALIDATION_047_v1', 'status': 'PASSED',
                  'archive_sha256': EXPECTED_SHA, 'archive_bytes': len(raw),
                  'release_commit': release['release_commit'],
                  'bundle_sha256': release['bundle_sha256'],
                  'assessment_sha256': release['assessment_sha256'],
                  'actual_saved_data_parser_invocations': len(calls),
                  'repeated_command_reexecuted_parser': False,
                  'actual_extracted_workflow_used': True,
                  'all_snapshot_files_and_git_history_checked': True,
                  'actual_parser_matches_published_assessment': True,
                  'local_git_publication_exact_paths': sorted(changed),
                  'original_profile_runs': 0, 'new_profile_runs': 0,
                  'native_model_or_reviewer_runs': 0, 'target_experiment_runs': 0,
                  'substitutions': ['Windows Downloads resolution replaced by supplied exact ZIP bytes and temporary home',
                                    'Authorized GitHub origin identity replaced in memory by disposable local bare Git',
                                    'Launcher child handoff loads exact extracted workflow in-process; actual parser still uses its real isolated subprocess'],
                  'scope': 'Actual complete public bundle and read-only parser; synthetic local Git transport. Does not certify WSL registry or live GitHub authentication.',
                  'helper_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  'wall_seconds': time.monotonic() - started}
    output = ROOT / 'evidence/P3_COMPLETE_PACKAGE_VALIDATION_047.json'
    assert not output.exists(), 'Preserve existing validation evidence'
    output.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
