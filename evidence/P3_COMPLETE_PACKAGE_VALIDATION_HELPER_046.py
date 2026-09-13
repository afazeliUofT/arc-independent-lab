"""Complete046 ZIP seam; explicit synthetic profile and local Git adapters, no learner execution."""
from pathlib import Path
import hashlib
import importlib.util
import io
import json
import stat
import subprocess
import sys
import tempfile
from unittest.mock import patch
import zipfile

sys.dont_write_bytecode = True
BASE = Path('/workspace/scratch/3ba2e8ad7d67')
ROOT = BASE / 'ARC_Independent_Lab'
WORK = BASE / 'work046'
ARCHIVE = BASE / 'output/ARC_Independent_Lab_046.zip'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False) + '\n').encode()


def main():
    launcher = load('complete046_launcher', ROOT / 'scripts/launch046_home.py')
    template = load('complete046_workflow_template', ROOT / 'scripts/checkpoint046_workflow.py')
    raw = ARCHIVE.read_bytes()
    files = launcher.archive_payloads(raw)
    release = json.loads(files['package_release.json'])
    manifest = json.loads(files['public/' + release['manifest_path']])
    assert sha(files['public/' + release['manifest_path']]) == release['manifest_sha256']
    assert all(sha(files['public/' + row['path']]) == row['sha256'] for row in manifest['inputs'])
    assert all(sha(files[row['path']]) == row['sha256'] for row in manifest['private_files'])
    assert files['launch046_home.py'] == files['public/scripts/launch046_home.py']
    for name in ('checkpoint046_workflow.py', 'stage_source_packet038.py'):
        assert files['scripts/' + name] == files['public/scripts/' + name]
    public = {name.removeprefix('public/'): body for name, body in files.items() if name.startswith('public/')}
    template.validate_baseline(public)
    parent = ROOT / 'delivery/tests046'
    parent.mkdir(parents=True, exist_ok=True)
    fixture = Path(tempfile.mkdtemp(prefix='complete_synthetic_seam_', dir=parent))
    home = fixture / 'home unicode é'
    lab = home / 'ARC_Independent_Lab'
    lab.mkdir(parents=True)
    remote = fixture / 'remote.git'

    def git(*args):
        return subprocess.run(['git', '-C', str(lab), *args], check=True, capture_output=True).stdout

    def write(path, body):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)

    subprocess.run(['git', 'init', '--bare', str(remote)], check=True, capture_output=True)
    git('init', '-b', 'main')
    git('config', 'user.name', 'Complete046 synthetic seam fixture')
    git('config', 'user.email', 'fixture@example.invalid')
    (lab / '.gitignore').write_text('/delivery/\n')
    for name in template.BASELINE_FILES:
        write(lab / name, public[name])
    git('add', '.')
    git('commit', '-m', 'Synthetic accepted ancestor containing exact accepted045 return bytes')
    ancestor = git('rev-parse', 'HEAD').decode().strip()
    entries = []
    for name, body in sorted(public.items()):
        write(lab / name, body)
        oid = subprocess.run(['git', '-C', str(lab), 'hash-object', '-w', '--stdin', '--no-filters'],
            input=body, check=True, capture_output=True).stdout.decode().strip()
        entries.append(('100644 ' + oid + '\t' + name + '\0').encode())
    subprocess.run(['git', '-C', str(lab), 'update-index', '-z', '--index-info'],
        input=b''.join(entries), check=True, capture_output=True)
    git('commit', '-m', 'Exact046 public package input bytes in fixture Git history')
    content = git('rev-parse', 'HEAD').decode().strip()
    git('remote', 'add', 'origin', launcher.REMOTE + '.git')
    git('push', str(remote), 'main')
    old_folder = lab / 'delivery/P3_045_RETURN_WORKFLOW' / '9685b38ec4c503e4944a1c3ae5d63c2ed6247541ef97bf85bcc78d9d9bf72e25'
    old_files = {old_folder / 'EXECUTION_RESERVED.json': b'{"scope":"SYNTHETIC_EXISTING_CONSUMED045_RESERVATION"}\n',
                 old_folder / 'SAVED_REPORT.json': public[template.BASELINE_REPORT]}
    for path, body in old_files.items():
        write(path, body)
    fixture_files = dict(files)
    fixture_files['package_release.json'] = canonical(dict(release, accepted_return_commit=ancestor, content_commit=content))
    fixture_files['SHA256SUMS'] = ''.join(sha(body) + '  ' + name + '\n'
        for name, body in sorted(fixture_files.items()) if name != 'SHA256SUMS').encode()
    assert {name for name in files if files[name] != fixture_files[name]} == {'package_release.json', 'SHA256SUMS'}
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, body in sorted(fixture_files.items()):
            info = zipfile.ZipInfo(name)
            info.external_attr = (stat.S_IFREG | 0o600) << 16
            archive.writestr(info, body, compress_type=zipfile.ZIP_DEFLATED)
    fixture_raw = buffer.getvalue()
    profile_calls, workflow_results, observed_commands = [], [], []
    fail_push = True
    actual_workflow = None
    original_popen = subprocess.Popen

    def observe(command, *args, **kwargs):
        assert command[0] == 'git', ('No model, learner, shell or other child is allowed in this synthetic seam', command)
        observed_commands.append(list(command))
        return original_popen(command, *args, **kwargs)

    def transport(command, **kwargs):
        nonlocal fail_push
        command = list(command)
        action = command[command.index('-C') + 2]
        if action == 'push' and fail_push:
            fail_push = False
            return subprocess.CompletedProcess(command, 1, b'', b'Explicit synthetic push interruption')
        if action in ('fetch', 'push', 'ls-remote'):
            command[command.index('origin')] = str(remote)
        return subprocess.run(command, **kwargs)

    def synthetic_profile(source, output):
        assert not profile_calls, 'Synthetic profile adapter must be reserved exactly once'
        names = {p.relative_to(source).as_posix() for p in source.rglob('*') if p.is_file()}
        assert names == actual_workflow.PROFILE_SOURCES and len(names) == 8
        assert all((source / name).read_bytes() == public[name] for name in names)
        assert not any('042' in name or name.endswith(('.pdf', '.png')) for name in names)
        assert not (source.parent / 'baseline_045').exists()
        fixture_helpers = load('complete046_synthetic_payload_builder', ROOT / 'tests/test_checkpoint046_handoff.py')
        report, worker_files = fixture_helpers.fixture_payload('INCOMPLETE', public)
        report['interruption'] = 'SYNTHETIC_HANDOFF_STOP_NO_LEARNER_EXECUTED'
        actual_workflow.validate_child_report(report)
        actual_workflow.validate_profile_scope(report, public)
        for name, raw in worker_files.items():
            write(output / name, raw)
        write(output / 'REPORT.json', canonical(report))
        profile_calls.append({'scope': 'SYNTHETIC_ADAPTER_ONLY', 'actual_profile_child_starts': 0})
        return {'child_start_observed': False, 'exit_code': 0, 'wall_seconds': 0.0,
            'termination': 'EXITED', 'synthetic_adapter_only': True}

    def execute(command, **kwargs):
        nonlocal actual_workflow
        assert command[1:3] == ['-B', '-u'] and Path(command[3]).name == 'checkpoint046_workflow.py'
        workflow = load('complete046_extracted_workflow', Path(command[3]))
        actual_workflow = workflow
        try:
            with patch.object(workflow, 'RETURN_COMMIT', ancestor):
                result = workflow.workflow(lab, Path(command[-1]), git_runner=transport,
                    profile_runner=synthetic_profile, emit=lambda text: None)
        except workflow.safe.StageStop as error:
            assert str(error) == 'git_push_failed', str(error)
            return subprocess.CompletedProcess(command, 1)
        workflow_results.append(result)
        with patch.object(workflow, 'workflow', return_value=result), patch.object(sys, 'argv', command[3:]), \
                patch('sys.stdout', new_callable=io.StringIO) as capture:
            code = workflow.main()
        assert code == 0 and 'successfully published' in capture.getvalue()
        assert 'PROFILE_INCOMPLETE' in capture.getvalue() and 'GitHub receipt:' in capture.getvalue()
        assert 'STOP:' not in capture.getvalue()
        return subprocess.CompletedProcess(command, code)

    with patch.object(subprocess, 'Popen', observe):
        try:
            launcher.launch(fixture_raw, home=home, runner=execute)
        except launcher.LaunchStop as error:
            assert 'Report publication or repository checks did not complete' in str(error)
        else:
            raise AssertionError('Synthetic first push failure must be reported')
        bundle = launcher.launch(fixture_raw, home=home, runner=execute)
        folder = lab / template.WORKFLOW / release['manifest_sha256']
        (folder / 'SAVED_REPORT.json').unlink()
        (folder / 'SAVED_RECEIPT.json').unlink()
        assert launcher.launch(fixture_raw, home=home, runner=execute) == bundle
        assert len(profile_calls) == 1 and len(workflow_results) == 2
        assert workflow_results[0] == workflow_results[1]
        result = workflow_results[0]
        assert result['profile_status'] == 'PROFILE_INCOMPLETE'
        assert git('diff', '--name-only', content, 'HEAD').decode().splitlines() == sorted([
            result['report_path'], result['receipt_path'], *result['worker_report_paths']])
        assert len(result['worker_report_paths']) == 2
        assert not git('status', '--porcelain') and not git('ls-files', '--', 'delivery/')
        assert all(path.read_bytes() == body for path, body in old_files.items())
        assert all((lab / name).read_bytes() == body for name, body in public.items())
        assert all((bundle / name).read_bytes() == body for name, body in fixture_files.items())
        assert (bundle.parent / 'PACKAGE.zip').read_bytes() == fixture_raw
        report_raw, receipt_raw = ((lab / result[key]).read_bytes() for key in ('report_path', 'receipt_path'))
        report, receipt = json.loads(report_raw), json.loads(receipt_raw)
        assert receipt['report_sha256'] == sha(report_raw)
        assert report['profile_scope']['accepted045_passed_tests'] == 23
        assert report['profile_scope']['original043044045_remeasured'] is False
        assert receipt['native_starts'] == receipt['model_turns_sent'] == 0
        assert receipt['target_experiment_started'] is False and receipt['complete_work_budget_admitted'] is False
        assert git('rev-parse', 'HEAD') == subprocess.run(['git', '--git-dir', str(remote), 'rev-parse', 'refs/heads/main'],
            check=True, capture_output=True).stdout
    (WORK / 'handoff_complete_fixture_report.json').write_bytes(report_raw)
    (WORK / 'handoff_complete_fixture_receipt.json').write_bytes(receipt_raw)
    evidence = {'kind': 'P3_COMPLETE_PACKAGE_VALIDATION_046_v1', 'status': 'PASSED',
        'scope': 'Actual complete draft046 ZIP through exact extracted launcher/workflow; synthetic profile and local Git adapters only',
        'draft_archive': {'name': ARCHIVE.name, 'sha256': sha(raw), 'bytes': len(raw), 'members': len(files)},
        'tested_manifest': {'path': release['manifest_path'], 'sha256': release['manifest_sha256']},
        'actual_public_snapshot_files': len(public), 'actual_private_packet_files': len(manifest['private_files']),
        'fixture_profile_runner_calls': len(profile_calls), 'actual_profile_worker_starts': 0,
        'checks': {'all_public_and_private_bytes_hash_verified': True, 'only_outer_release_ids_and_sums_adapted': True,
            'exact_staged_eight_sources_no_prior_report_or_private_inputs': True, 'accepted045_report_and_all_original_sources_preserved': True,
            'accepted045_return_sources_and_consumed_reservation_preserved': True,
            'published_partial_exits_zero_with_reason_and_receipt': True,
            'push_failure_and_missing_cache_recover_without_remeasurement': True,
            'only_fixed_allowlisted_index_receipt_and_worker_paths_committed': True,
            'partial_return_file_count': 4, 'maximum_return_files': 51,
            'private_delivery_ignored_untracked': True,
            'local_bare_remote_matches_publication': True, 'only_git_children_observed': True},
        'fixture_substitutions': ['Outer accepted/content Git IDs replaced by local history IDs; archive checksums updated',
            'Loaded workflow RETURN_COMMIT replaced by local ancestor containing exact accepted045 returns',
            'Canonical-origin transport routed to local bare remote; real Git object validation remains active',
            'Launcher child adapter injects synthetic profile_runner and bounded local Git transport; no profile child executes',
            'Synthetic payload uses explicitly synthetic finite resource row outcomes with real046 source pins'],
        'execution_boundary': {'native_starts': 0, 'model_turns_sent': 0, 'actual_profile_worker_starts': 0,
            'target_experiment_started': False, 'target_execution_admitted': False, 'complete_work_budget_admitted': False},
        'fixture_report_sha256': sha(report_raw), 'fixture_receipt_sha256': sha(receipt_raw),
        'limitations': ['Synthetic execution validates delivery and provenance, not laptop performance',
            'Final publication adds bookkeeping; final package hash and immutable sources require separate verification'],
        'helper_sha256': sha(Path(__file__).read_bytes())}
    target = WORK / 'handoff_complete_package_validation.json'
    target.write_bytes(canonical(evidence))
    print(json.dumps({'status': 'COMPLETE_SYNTHETIC_HANDOFF_SEAM_PASSED', 'evidence': str(target),
        'sha256': sha(target.read_bytes()), 'fixture_root': str(fixture)}, indent=2))


if __name__ == '__main__':
    main()
