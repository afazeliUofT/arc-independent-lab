"""Outcome-blind046 transport fixtures; no reference learner or target panel executes.

Synthetic reports test execution reservation, process caps and publication recovery.
Production source files and complete-source conformance are checked separately.
"""
import importlib.util
import copy
import base64
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import zlib

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


w = load('workflow046_test', ROOT / 'scripts/checkpoint046_workflow.py')
l = load('launcher046_test', ROOT / 'scripts/launch046_home.py')
b = load('bootstrap046_test', ROOT / 'scripts/downloads_bootstrap046.py')


def fixture_full_report(status='COMPLETED', public=None):
    if public is None:
        public = {name: ((ROOT / name).read_bytes() if (ROOT / name).exists() else
            b'# Explicit synthetic source fixture only.\n') for name in w.PROFILE_SOURCES}
    current = {name: w.safe.sha(public[name]) for name in w.PROFILE_SOURCES}
    config = json.loads(public['configs/P3_FULL_WORK_FIXTURES_046.json'])
    planned = w.planned_profile_rows(config)
    raw = w.safe.canonical({'scope': 'SYNTHETIC_HANDOFF_EVIDENCE_ONLY'})
    compressed = zlib.compress(raw, level=6)
    evidence = {'encoded_bytes': len(raw), 'sha256': w.safe.sha(raw), 'archive': {
        'encoding': 'zlib6+base64', 'data': base64.b64encode(compressed).decode('ascii'),
        'compressed_bytes': len(compressed), 'compressed_sha256': w.safe.sha(compressed),
        'uncompressed_bytes': len(raw), 'uncompressed_sha256': w.safe.sha(raw),
        'uncompressed_limit_bytes': 128 * 1024 ** 2}}
    rows = [dict(row, status=('COMPLETED' if status == 'COMPLETED' or index == 0 else 'NOT_STARTED'),
        synthetic_fixture_only=True, summary={('complete_evidence_serialization'
            if row['case'] == 'complete_chain' else 'overlap_serialization'): copy.deepcopy(evidence)})
        for index, row in enumerate(planned)]
    return {'kind': 'P3_CONSOLIDATED_RESOURCE_PROFILE_046_v1', 'status': status,
        'scope': 'SYNTHETIC_HANDOFF_FIXTURE_ONLY', 'target_experiment_started': False,
        'target_execution_admitted': False, 'native_started': False, 'outcome_blind': True,
        'complete_work_budget_admitted': False, 'automatic_rerun_permitted': False,
        'full_resource_profile_started': True, 'original043044045_remeasured': False,
        'instruction_accounting_complete': False, 'maximal_geometry_proved': False,
        'B_comp': None, 'B_mem': None, 'source_hashes': current, 'limits': config['limits'],
        'aggregate_metrics': {'scope': '046_RESOURCE_PROFILE_INVOCATION_ONLY', 'synthetic_fixture_only': True},
        'conformance': {'row_id': 'conformance', 'status': 'COMPLETED', 'source_hashes': current,
            'summary': {'passed': True, 'tests_run': 2,
            'test_outcomes': [{'name': name, 'status': 'PASSED', 'synthetic_fixture_only': True}
                for name in ['synthetic.case_a', 'synthetic.case_b']],
            'case_results': {'synthetic_fixture_only': True}}},
        'planned_rows': planned, 'profiles': rows,
        'complete_required_paths_measured': status == 'COMPLETED',
        'interruption': None if status == 'COMPLETED' else 'SYNTHETIC_COMPONENT_INTERRUPTION'}


def fixture_payload(status='COMPLETED', public=None):
    report = fixture_full_report(status, public)
    files = {}
    entries = [report['conformance'], *report['profiles']]
    for entry in entries:
        if entry['status'] == 'NOT_STARTED':
            entry['summary'] = None
            continue
        name = 'CONFORMANCE.json' if entry['row_id'] == 'conformance' else entry['row_id'] + '.json'
        worker = {'worker_kind': 'P3_FULL_WORK_ROW_046_v1', 'row_id': entry['row_id'],
            'status': entry['status'], 'source_hashes': report['source_hashes'],
            'summary': entry['summary'], 'metrics': {'synthetic_fixture_only': True}}
        raw = w.compact_json(worker)
        files[name] = raw
        entry['full_worker_report'] = {'filename': name, 'sha256': w.safe.sha(raw), 'bytes': len(raw)}
        if name != 'CONFORMANCE.json':
            entry['summary'] = None
    report['evidence_transport'] = 'EXACT_SEPARATE_WORKER_REPORTS_046_v1'
    return report, files


def fixture_report(status='COMPLETED', public=None):
    return fixture_payload(status, public)[0]


class HandoffTests(unittest.TestCase):
    def setUp(self):
        parent = ROOT / 'delivery/tests046'
        parent.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name) / 'home unicode é'
        self.lab = self.home / 'ARC_Independent_Lab'
        self.lab.mkdir(parents=True)
        self.bundle = self.lab / 'delivery/fixture_bundle'
        self.bundle.mkdir(parents=True)
        self.remote = Path(self.temp.name) / 'remote.git'
        self.raw_git('init', '--bare', str(self.remote))
        self.git('init', '-b', 'main')
        self.git('config', 'user.name', 'Offline046 synthetic fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        (self.lab / '.gitignore').write_text('/delivery/\n')
        for name, workname in ((w.BASELINE_REPORT, 'REPORT_045.json'),
                               (w.BASELINE_RECEIPT, 'RECEIPT_045.json')):
            source = ROOT / name
            raw = source.read_bytes() if source.exists() else (ROOT.parent / 'work046' / workname).read_bytes()
            self.write(self.lab / name, raw)
        self.git('add', '.')
        self.git('commit', '-m', 'Synthetic046 accepted ancestor')
        self.accepted = self.git('rev-parse', 'HEAD').decode().strip()
        self.public = {}
        for name in w.REQUIRED_CODE:
            if name in w.BASELINE_FILES:
                self.public[name] = (self.lab / name).read_bytes()
            elif (ROOT / name).exists():
                self.public[name] = (ROOT / name).read_bytes()
            else:
                self.public[name] = b'# Explicit synthetic source fixture only.\n'
        for pin in json.loads(self.public[w.BASELINE_REPORT])['source_pins']:
            self.public[pin['path']] = (ROOT / pin['path']).read_bytes()
        self.public['state/PROJECT_STATE.json'] = b'{"scope":"fixture"}\n'
        self.private = {'private/BROKER_MANIFEST.json': b'PRIVATE FIXTURE NEVER PUBLISH\n'}
        self.commands, self.profile_calls = [], 0
        self.fail_action = None
        self.make_release()
        self.git('remote', 'add', 'origin', w.safe.REMOTE)
        self.git('push', str(self.remote), 'main')

    def raw_git(self, *args):
        return subprocess.run(['git', *args], check=True, capture_output=True).stdout

    def git(self, *args):
        return self.raw_git('-C', str(self.lab), *args)

    def write(self, path, raw):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)

    def make_release(self):
        manifest = {'kind': 'P3_CHECKPOINT_046_MANIFEST_v1',
            'inputs': [{'path': n, 'sha256': w.safe.sha(b)} for n, b in sorted(self.public.items())],
            'private_files': [{'path': n, 'sha256': w.safe.sha(b)} for n, b in sorted(self.private.items())]}
        raw = w.safe.canonical(manifest)
        for name, body in self.public.items():
            self.write(self.lab / name, body)
            self.write(self.bundle / 'public' / name, body)
        for name, body in self.private.items():
            self.write(self.bundle / name, body)
        self.write(self.lab / w.MANIFEST, raw)
        self.write(self.bundle / 'public' / w.MANIFEST, raw)
        for name in ('checkpoint046_workflow.py', 'stage_source_packet038.py'):
            self.write(self.bundle / 'scripts' / name, self.public['scripts/' + name])
        self.write(self.bundle / 'launch046_home.py', self.public['scripts/launch046_home.py'])
        self.git('add', '.')
        self.git('commit', '-m', 'Synthetic046 frozen release')
        self.content = self.git('rev-parse', 'HEAD').decode().strip()
        self.release = {'kind': 'P3_CHECKPOINT_046_RELEASE_v1', 'repository': w.REPOSITORY,
            'content_commit': self.content, 'accepted_return_commit': self.accepted,
            'manifest_path': w.MANIFEST, 'manifest_sha256': w.safe.sha(raw)}
        self.write(self.bundle / 'package_release.json', w.safe.canonical(self.release))

    def runner(self, command, **kwargs):
        command = list(command)
        self.commands.append(command[:])
        self.assertEqual(command[0], 'git')
        action = command[command.index('-C') + 2]
        if action == self.fail_action:
            self.fail_action = None
            return subprocess.CompletedProcess(command, 1, b'', b'fixture transport failure')
        if action in ('fetch', 'push', 'ls-remote'):
            command[command.index('origin')] = str(self.remote)
        return subprocess.run(command, **kwargs)

    def profile(self, source, output):
        self.profile_calls += 1
        self.assertEqual({p.relative_to(source).as_posix() for p in source.rglob('*') if p.is_file()},
                         w.PROFILE_SOURCES)
        self.assertFalse(any('042' in str(p) or p.suffix == '.pdf' for p in source.rglob('*')))
        self.assertFalse((source.parent / 'baseline_044').exists())
        report, workers = fixture_payload(public=self.public)
        for name, raw in workers.items():
            self.write(output / name, raw)
        self.write(output / 'REPORT.json', w.safe.canonical(report))
        return {'child_start_observed': True, 'exit_code': 0, 'wall_seconds': 0.125,
                'termination': 'EXITED', 'fixture': True}

    def execute(self, module=w, bundle=None, profiler=None):
        with patch.object(module, 'RETURN_COMMIT', self.accepted):
            return module.workflow(self.lab, bundle or self.bundle, git_runner=self.runner,
                profile_runner=self.profile if profiler is None else profiler, emit=lambda text: None)

    def test_one_reservation_preserves_full_report_and_exact_repeat(self):
        first, second = self.execute(), self.execute()
        self.assertEqual(first, second)
        self.assertEqual(self.profile_calls, 1)
        report = json.loads((self.lab / first['report_path']).read_text())
        receipt = json.loads((self.lab / first['receipt_path']).read_text())
        self.assertEqual(report['profile_report'], fixture_report(public=self.public))
        self.assertEqual(report['status'], 'PROFILE_COMPLETED')
        self.assertEqual(receipt['report_sha256'], w.safe.sha((self.lab / first['report_path']).read_bytes()))
        self.assertEqual(receipt['cumulative_native_starts'], 18)
        self.assertEqual(receipt['cumulative_model_turns_sent'], 14)
        self.assertFalse(receipt['automatic_profile_rerun_permitted'])
        self.assertFalse(receipt['target_experiment_started'])
        self.assertEqual(receipt['profile_scope'], w.SCOPE)
        self.assertFalse(receipt['original043044045_remeasured'])
        self.assertEqual(receipt['accepted045_report_sha256'], w.RETURN045_REPORT_SHA256)
        self.assertEqual(self.git('diff', '--name-only', self.content, 'HEAD').decode().splitlines(),
                         sorted([first['report_path'], first['receipt_path'], *first['worker_report_paths']]))
        self.assertEqual(len(first['worker_report_paths']), 49)
        self.assertEqual(receipt['return_file_count'], 51)
        self.assertFalse(report['worker_report_validation_failures'])
        self.assertEqual(report['worker_report_pins'], w.worker_pins(fixture_payload(public=self.public)[1]))
        self.assertNotIn('PRIVATE FIXTURE', (self.lab / first['report_path']).read_text())
        self.assertFalse(self.git('status', '--porcelain'))

    def test_failed_commit_and_push_never_reexecute_profile(self):
        self.fail_action = 'commit'
        with self.assertRaisesRegex(w.safe.StageStop, 'git_commit_failed'):
            self.execute()
        self.assertEqual(self.profile_calls, 1)
        self.fail_action = 'push'
        with self.assertRaisesRegex(w.safe.StageStop, 'git_push_failed'):
            self.execute()
        self.assertEqual(self.profile_calls, 1)
        saved_head = self.git('rev-parse', 'HEAD')
        folder = self.lab / w.WORKFLOW / self.release['manifest_sha256']
        (folder / 'SAVED_REPORT.json').unlink()
        (folder / 'SAVED_RECEIPT.json').unlink()
        result = self.execute()
        self.assertEqual(self.profile_calls, 1)
        self.assertEqual(saved_head, self.git('rev-parse', 'HEAD'))
        self.assertEqual(result['profile_status'], 'PROFILE_COMPLETED')

    def test_reservation_without_report_returns_interrupted_and_never_relaunches(self):
        def crash(source, output):
            self.profile_calls += 1
            raise SystemExit('synthetic crash after reservation')
        with self.assertRaises(SystemExit):
            self.execute(profiler=crash)
        result = self.execute()
        self.assertEqual(self.profile_calls, 1)
        report = json.loads((self.lab / result['report_path']).read_text())
        self.assertEqual(report['status'], 'PROFILE_INCOMPLETE')
        self.assertEqual(report['execution']['termination'], 'RESERVATION_FOUND_WITHOUT_SAVED_RESULT')
        self.assertIsNone(report['execution']['child_start_observed'])
        self.assertIsNone(report['profile_report'])
        self.assertEqual(result, self.execute())
        self.assertEqual(self.profile_calls, 1)

    def test_partial_child_report_survives_interruption_and_publication_retry(self):
        partial = fixture_report('INCOMPLETE', self.public)
        partial['interruption'] = 'FABRICATED_BUDGET_STOP'
        def interrupted(source, output):
            self.profile_calls += 1
            self.write(output / 'REPORT.json', w.safe.canonical(partial))
            return {'child_start_observed': True, 'exit_code': -9, 'wall_seconds': 0.25,
                    'termination': 'PARENT_WALL_CAP'}
        self.fail_action = 'push'
        with self.assertRaises(w.safe.StageStop):
            self.execute(profiler=interrupted)
        result = self.execute()
        report = json.loads((self.lab / result['report_path']).read_text())
        self.assertEqual(self.profile_calls, 1)
        self.assertEqual(report['profile_report'], partial)
        self.assertEqual(report['execution']['termination'], 'PARENT_WALL_CAP')
        self.assertEqual(report['status'], 'PROFILE_INCOMPLETE')

    def test_unindexed_worker_is_preserved_and_never_promotes_partial_index(self):
        partial, files = fixture_payload('INCOMPLETE', self.public)
        orphan = fixture_payload(public=self.public)[1]['row_03.json']
        files['row_03.json'] = orphan
        def interrupted(source, output):
            self.profile_calls += 1
            for name, raw in files.items():
                self.write(output / name, raw)
            self.write(output / 'REPORT.json', w.compact_json(partial))
            self.write(output / 'outside.json', b'UNDECLARED PRIVATE FIXTURE FILE\n')
            return {'child_start_observed': True, 'exit_code': -9, 'wall_seconds': 0.1,
                    'termination': 'PARENT_WALL_CAP'}
        result = self.execute(profiler=interrupted)
        report = json.loads((self.lab / result['report_path']).read_text())
        self.assertEqual(result['profile_status'], 'PROFILE_INCOMPLETE')
        self.assertIn({'filename': 'row_03.json', 'reason': 'UNINDEXED_RECOVERED_WORKER_EVIDENCE'},
                      report['worker_report_validation_failures'])
        returned = self.lab / Path(result['report_path']).parent / 'row_03.json'
        self.assertEqual(returned.read_bytes(), orphan)
        self.assertEqual(len(result['worker_report_paths']), 3)
        self.assertFalse(any(name.endswith('outside.json') for name in self.git('ls-files').decode().splitlines()))
        self.assertEqual(result, self.execute())
        self.assertEqual(self.profile_calls, 1)

    def test_changed_indexed_worker_bytes_are_published_as_rejected_evidence(self):
        broken = b'{"invalid_worker":\n'
        def changed(source, output):
            outcome = self.profile(source, output)
            self.write(output / 'row_00.json', broken)
            return outcome
        result = self.execute(profiler=changed)
        report = json.loads((self.lab / result['report_path']).read_text())
        self.assertEqual(result['profile_status'], 'PROFILE_INCOMPLETE')
        self.assertEqual(result['profile_reason'], 'WORKER_EVIDENCE_VALIDATION_FAILED')
        self.assertIn({'filename': 'row_00.json', 'reason': 'WORKER_DESCRIPTOR_OR_BYTES_DIFFER'},
                      report['worker_report_validation_failures'])
        self.assertEqual((self.lab / Path(result['report_path']).parent / 'row_00.json').read_bytes(), broken)
        self.assertEqual(len(result['worker_report_paths']), 49)
        self.assertEqual(result, self.execute())
        self.assertEqual(self.profile_calls, 1)

    def test_exact_remote_report_reused_without_local_saved_cache(self):
        first = self.execute()
        folder = self.lab / w.WORKFLOW / self.release['manifest_sha256']
        # Explicit test of a separate installation's missing local report cache;
        # the once marker remains and the authoritative remote return is intact.
        (folder / 'SAVED_REPORT.json').unlink()
        (folder / 'SAVED_RECEIPT.json').unlink()
        self.assertEqual(first, self.execute())
        self.assertEqual(self.profile_calls, 1)

    def test_changed_staged_output_is_preserved_without_second_profile(self):
        self.fail_action = 'commit'
        with self.assertRaises(w.safe.StageStop):
            self.execute()
        report = next((self.lab / 'artifacts/CHECKPOINT_046_RETURN').rglob('REPORT.json'))
        report.write_text('{"human":"preserve"}\n')
        before = self.git('diff', '--cached', '--binary')
        with self.assertRaises(w.safe.StageStop):
            self.execute()
        self.assertEqual(self.profile_calls, 1)
        self.assertEqual(before, self.git('diff', '--cached', '--binary'))
        self.assertIn('preserve', report.read_text())

    def test_published_incomplete_is_successful_command_with_clear_receipt(self):
        def incomplete(source, output):
            result = self.profile(source, output)
            value = fixture_report('INCOMPLETE', self.public)
            value['interruption'] = 'SYNTHETIC_COMPONENT_INTERRUPTION'
            self.write(output / 'REPORT.json', w.safe.canonical(value))
            return result
        result = self.execute(profiler=incomplete)
        with patch.object(w, 'workflow', return_value=result), patch.object(sys, 'argv',
                ['checkpoint046_workflow.py', '--bundle', str(self.bundle)]), \
                patch('sys.stdout', new_callable=io.StringIO) as capture:
            self.assertEqual(w.main(), 0)
        printed = capture.getvalue()
        self.assertIn('GitHub receipt:', printed)
        self.assertIn('PROFILE_INCOMPLETE', printed)
        self.assertIn('successfully published', printed)
        self.assertIn('SYNTHETIC_COMPONENT_INTERRUPTION', printed)
        self.assertNotIn('STOP:', printed)
        self.assertEqual(result, self.execute())
        self.assertEqual(self.profile_calls, 1)

    def test_accepted045_return_is_preserved_and_changed_baseline_refused(self):
        original = self.public[w.BASELINE_REPORT]
        self.execute()
        self.assertEqual((self.lab / w.BASELINE_REPORT).read_bytes(), original)
        self.assertFalse((self.lab / 'delivery/P3_043_RETURN_WORKFLOW').exists())
        changed = dict(self.public)
        changed[w.BASELINE_REPORT] = b'{}\n'
        with self.assertRaisesRegex(w.safe.StageStop, 'accepted045_baseline_hash_differs'):
            w.validate_baseline(changed)
        changed = dict(self.public)
        changed['scripts/diagnostics045.py'] += b'# Changed frozen code\n'
        with self.assertRaisesRegex(w.safe.StageStop, 'accepted045_source_identity_not_preserved'):
            w.validate_baseline(changed)

    def test_child_with_remeasurement_claim_refused(self):
        bad = fixture_report(public=self.public)
        bad['original043044045_remeasured'] = True
        with self.assertRaises(w.safe.StageStop):
            w.validate_child_report(bad)

    def test_changed_source_pin_publishes_rejection_without_poisoning_saved_state(self):
        bad = fixture_report(public=self.public)
        bad['source_hashes']['scripts/accounting043.py'] = '0' * 64
        raw = w.safe.canonical(bad)
        def malformed(source, output):
            self.profile_calls += 1
            self.write(output / 'REPORT.json', raw)
            return {'child_start_observed': True, 'exit_code': 0, 'wall_seconds': 0.125,
                    'termination': 'EXITED', 'fixture': True}
        result = self.execute(profiler=malformed)
        report = json.loads((self.lab / result['report_path']).read_text())
        self.assertEqual(result['profile_status'], 'PROFILE_INCOMPLETE')
        self.assertIsNone(report['profile_report'])
        self.assertIn('profile_sources_or_usage_differs', report['child_report_failure_class'])
        self.assertEqual(base64.b64decode(report['rejected_child_report']['content']), raw)
        self.assertEqual(result, self.execute())
        self.assertEqual(self.profile_calls, 1)

    def test_malformed_outcome_is_published_as_rejected_bytes_once(self):
        bad = fixture_report(public=self.public)
        bad['profiles'] = [None]
        raw = w.safe.canonical(bad)
        def malformed(source, output):
            self.profile_calls += 1
            self.write(output / 'REPORT.json', raw)
            return {'child_start_observed': True, 'exit_code': 0, 'wall_seconds': 0.1,
                'termination': 'EXITED', 'fixture': True}
        result = self.execute(profiler=malformed)
        report = json.loads((self.lab / result['report_path']).read_text())
        self.assertEqual(report['status'], 'PROFILE_INCOMPLETE')
        self.assertIsNone(report['profile_report'])
        self.assertIn('profile_row_shape_differs', report['child_report_failure_class'])
        self.assertEqual(base64.b64decode(report['rejected_child_report']['content']), raw)
        self.assertEqual(result, self.execute())
        self.assertEqual(self.profile_calls, 1)

    def test_false_wrapper_completion_and_changed_invocation_accounting_refused(self):
        child = fixture_report('INCOMPLETE', self.public)
        value = w.execution_report(self.release, self.public,
            {'termination': 'EXITED', 'exit_code': 0, 'child_start_observed': True}, child, None)
        value['status'] = 'PROFILE_COMPLETED'
        with self.assertRaisesRegex(w.safe.StageStop, 'wrapper_status_differs'):
            with patch.object(w, 'RETURN_COMMIT', self.accepted):
                value['baseline_return_commit'] = self.accepted
                w.validate_saved_report(w.execution_bytes(value), self.release, self.public)
        value['status'] = 'PROFILE_INCOMPLETE'
        value['profile_launches_observed'] = 0
        with self.assertRaisesRegex(w.safe.StageStop, 'observed_launch_accounting_differs'):
            with patch.object(w, 'RETURN_COMMIT', self.accepted):
                w.validate_saved_report(w.execution_bytes(value), self.release, self.public)
        child['aggregate_metrics']['scope'] = 'WRONGLY_COMBINED_PRIOR_INVOCATION'
        with self.assertRaisesRegex(w.safe.StageStop, 'profile_sources_or_usage_differs'):
            w.validate_profile_scope(child, self.public)

    def test_actual_extracted_launcher_recovers_push_without_reexecution(self):
        files = {p.relative_to(self.bundle).as_posix(): p.read_bytes()
                 for p in self.bundle.rglob('*') if p.is_file()}
        files['README_046.md'] = b'Synthetic handoff fixture.\n'
        files['SHA256SUMS'] = ''.join(l.digest(raw) + '  ' + name + '\n'
            for name, raw in sorted(files.items())).encode()
        output = io.BytesIO()
        with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
            for name, raw in files.items():
                info = zipfile.ZipInfo(name)
                info.external_attr = (stat.S_IFREG | 0o600) << 16
                archive.writestr(info, raw)
        raw = output.getvalue()
        def execute(command, **kwargs):
            self.assertEqual(command[1:3], ['-B', '-u'])
            self.assertEqual(Path(command[3]).name, 'checkpoint046_workflow.py')
            module = load('extracted046_fixture', command[3])
            try:
                self.execute(module, Path(command[-1]))
                return subprocess.CompletedProcess(command, 0)
            except module.safe.StageStop:
                return subprocess.CompletedProcess(command, 1)
        self.fail_action = 'push'
        with self.assertRaises(l.LaunchStop):
            l.launch(raw, home=self.home, runner=execute)
        bundle = l.launch(raw, home=self.home, runner=execute)
        self.assertEqual(self.profile_calls, 1)
        self.assertEqual((bundle.parent / 'PACKAGE.zip').read_bytes(), raw)
        self.assertFalse(self.git('ls-files', '--', 'delivery/'))

    def test_synthetic_child_uses_real_process_caps_and_wall_stop(self):
        source = self.lab / 'delivery/child_fixture_source'
        output = self.lab / 'delivery/child_fixture_output'
        code = ('import json,os,sys,resource\nfrom pathlib import Path\n'
            'output=Path(sys.argv[sys.argv.index("--output")+1])\n'
            'report=' + repr(fixture_report()) + '\n'
            'report["fixture_affinity_count"]=len(os.sched_getaffinity(0))\n'
            'report["fixture_isolated_flags"]=[sys.flags.isolated,sys.flags.no_site,sys.dont_write_bytecode]\n'
            'report["fixture_limits"]={name:list(resource.getrlimit(getattr(resource,name))) for name in ["RLIMIT_AS","RLIMIT_CPU","RLIMIT_FSIZE"]}\n'
            '(output/"REPORT.json").write_text(json.dumps(report))\n')
        self.write(source / w.VERIFIER, code.encode())
        result = w.run_profile_child(source, output)
        self.assertEqual(result['exit_code'], 0)
        report, failure = w.read_child_report(output)
        self.assertIsNone(failure)
        self.assertEqual(report['fixture_affinity_count'], 1)
        self.assertEqual(report['fixture_isolated_flags'], [1, 1, True])
        self.assertEqual(report['fixture_limits'], {
            'RLIMIT_AS': [w.CAPS['address_space_bytes']] * 2,
            'RLIMIT_CPU': [w.CAPS['cpu_soft_seconds'], w.CAPS['cpu_hard_seconds']],
            'RLIMIT_FSIZE': [w.CAPS['maximum_child_file_bytes']] * 2})
        self.assertEqual(result['stdout']['bytes'], 0)
        sleep_source = self.lab / 'delivery/sleep_fixture_source'
        sleep_output = self.lab / 'delivery/sleep_fixture_output'
        self.write(sleep_source / w.VERIFIER, b'import time\ntime.sleep(10)\n')
        with patch.dict(w.CAPS, {'parent_wall_seconds': 0.1}):
            stopped = w.run_profile_child(sleep_source, sleep_output)
        self.assertEqual(stopped['termination'], 'PARENT_WALL_CAP')
        self.assertTrue(stopped['process_group_kill_attempted'])

    def test_complete_profile_requires_every_distinct_row_and_successful_conformance(self):
        original = fixture_report(public=self.public)
        for label, change in (
                ('missing', lambda report: report['profiles'].pop()),
                ('duplicate', lambda report: report['profiles'].__setitem__(1, copy.deepcopy(report['profiles'][0]))),
                ('unfinished', lambda report: report['profiles'][0].__setitem__('status', 'INCOMPLETE')),
                ('conformance', lambda report: report['conformance']['summary'].__setitem__('passed', False)),
                ('accounting', lambda report: report.__setitem__('instruction_accounting_complete', True)),
                ('budget', lambda report: report.__setitem__('B_comp', 1)),
                ('limits', lambda report: report['limits'].__setitem__('driver_wall_seconds', 1)),
                ('coverage', lambda report: report.__setitem__('complete_required_paths_measured', False))):
            with self.subTest(label=label):
                bad=copy.deepcopy(original)
                change(bad)
                with self.assertRaises(w.safe.StageStop):
                    w.validate_child_report(bad)
                    w.validate_profile_scope(bad,self.public)

    def test_archive_validation_checks_every_byte_and_bounds_decompression(self):
        value = fixture_full_report(public=self.public)
        original = value['profiles'][0]['summary']['complete_evidence_serialization']
        w.validate_evidence_archive(original)
        for label, change in (
                ('compressed_hash', lambda item: item['archive'].__setitem__('compressed_sha256', '0' * 64)),
                ('decoded_hash', lambda item: item['archive'].__setitem__('uncompressed_sha256', '0' * 64)),
                ('limit', lambda item: item['archive'].__setitem__('uncompressed_limit_bytes', 256 * 1024 ** 2)),
                ('base64', lambda item: item['archive'].__setitem__('data', '$invalid'))):
            with self.subTest(label=label):
                changed = copy.deepcopy(original)
                change(changed)
                with self.assertRaises(w.safe.StageStop):
                    w.validate_evidence_archive(changed)
        for label, raw, claimed, trailing in (
                ('declared_small', b'x' * (2 * 1024 ** 2), 64, b''),
                ('trailing', b'{}', 2, b'garbage'),
                ('truncated', b'{}', 2, None)):
            with self.subTest(label=label):
                compressed = zlib.compress(raw)
                compressed = compressed[:-1] if trailing is None else compressed + trailing
                item = {'encoded_bytes': claimed, 'sha256': w.safe.sha(raw), 'archive': {
                    'encoding': 'zlib6+base64', 'data': base64.b64encode(compressed).decode(),
                    'compressed_bytes': len(compressed), 'compressed_sha256': w.safe.sha(compressed),
                    'uncompressed_bytes': claimed, 'uncompressed_sha256': w.safe.sha(raw),
                    'uncompressed_limit_bytes': 128 * 1024 ** 2}}
                with self.assertRaises(w.safe.StageStop):
                    w.validate_evidence_archive(item)
        # Archives in interrupted stage details are checked as well as complete rows.
        changed = fixture_report('INCOMPLETE', self.public)
        bad_archive = copy.deepcopy(original)
        bad_archive['archive']['compressed_sha256'] = '0' * 64
        changed['profiles'][1]['stage_progress'] = [{'detail': bad_archive}]
        with self.assertRaises(w.safe.StageStop):
            w.validate_profile_scope(changed, self.public)
        index, files = fixture_payload(public=self.public)
        worker = json.loads(files['row_00.json'])
        del worker['summary']['complete_evidence_serialization']['archive']
        files['row_00.json'] = w.compact_json(worker)
        failures = w.validate_worker_reports(index, files, self.public)
        self.assertTrue(any(row['reason'] == 'completed_worker_missing_complete_evidence_archive'
                            for row in failures))

    def test_near_cap_nested_child_remains_readable_through_saved_report_and_receipt(self):
        child = fixture_report('INCOMPLETE', self.public)
        nested = [''] * 70000
        for _ in range(128):
            nested = [nested]
        child['synthetic_nested_size_regression'] = nested
        child['synthetic_padding'] = ''
        child['synthetic_padding'] = 'x' * (w.CAPS['maximum_child_report_bytes'] -
            len(w.compact_json(child)) - 256)
        raw = w.compact_json(child)
        self.assertLessEqual(len(raw), w.CAPS['maximum_child_report_bytes'])
        output = self.lab / 'delivery/large_child_fixture'
        self.write(output / 'REPORT.json', raw)
        accepted, failure = w.read_child_report(output, self.public)
        self.assertIsNone(failure)
        with patch.object(w, 'RETURN_COMMIT', self.accepted):
            value = w.execution_report(self.release, self.public,
                {'termination': 'EXITED', 'exit_code': 0, 'child_start_observed': True}, accepted, None)
            # The old indent=2 outer representation exceeded its own32 MiB reader cap.
            self.assertGreater(len(w.safe.canonical(value)), w.safe.MAX_FILE)
            compact = w.execution_bytes(value)
            self.assertLess(len(compact), w.safe.MAX_FILE)
            saved = output / 'SAVED_REPORT.json'
            w.atomic_new(saved, compact)
            recovered = w.validate_saved_report(w.safe.read_regular(saved), self.release, self.public)
            self.assertEqual(recovered['profile_report'], accepted)
            returned = w.return_files(self.release, recovered, self.public, self.private)
            report_raw = next(body for name, body in returned.items() if name.endswith('/REPORT.json'))
            receipt = json.loads(next(body for name, body in returned.items() if name.endswith('/RECEIPT.json')))
            self.assertEqual(report_raw, compact)
            self.assertEqual(receipt['report_sha256'], w.safe.sha(compact))
            self.assertEqual(receipt['report_encoding'], 'SORTED_COMPACT_ASCII_JSON_046_v1')
        child['synthetic_padding'] += 'x' * 512
        with self.assertRaisesRegex(w.safe.StageStop, 'normalized_child_report_oversized'):
            w.validate_child_report(child)

    def test_downloads_registry_resolution_handles_spaces_and_duplicate_names(self):
        downloads = self.home / 'Windows Downloads é'
        downloads.mkdir()
        payload = io.BytesIO()
        with zipfile.ZipFile(payload, 'w') as archive:
            archive.writestr('launch046_home.py', b'# Explicit synthetic launcher fixture.\n')
        raw = payload.getvalue()
        (downloads / b.ZIP_NAME).write_bytes(b'Wrong earlier download')
        selected = downloads / b.ZIP_NAME.replace('.zip', ' (1).zip')
        selected.write_bytes(raw)
        calls, executed = [], []
        def discover(command, **kwargs):
            calls.append(command)
            if command[0] == 'wslpath':
                self.assertEqual(command, ['wslpath', '-u', r'C:\Users\Name With Spaces\Downloads'])
                return subprocess.CompletedProcess(command, 0, (str(downloads) + '\n').encode())
            self.assertIn('User Shell Folders', command[-1])
            return subprocess.CompletedProcess(command, 0,
                b'\xef\xbb\xbfC:\\Users\\Name With Spaces\\Downloads\r\n')
        def launch(code, namespace):
            executed.append(namespace)
        with patch.object(b, 'ZIP_SHA256', l.digest(raw)), \
                patch.object(b.subprocess, 'run', side_effect=discover), \
                patch.object(b, 'exec', create=True, side_effect=launch), \
                patch('sys.stdout', new_callable=io.StringIO):
            b.main()
        self.assertEqual(len(calls), 2)
        self.assertEqual(len(executed), 1)
        self.assertEqual(executed[0]['ARCHIVE_BYTES'], raw)
        self.assertEqual(executed[0]['ARCHIVE_PATH'], str(selected))


if __name__ == '__main__':
    unittest.main()
