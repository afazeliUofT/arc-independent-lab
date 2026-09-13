"""Outcome-blind045 transport fixtures; no reference learner or target panel executes.

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

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


w = load('workflow045_test', ROOT / 'scripts/checkpoint045_workflow.py')
l = load('launcher045_test', ROOT / 'scripts/launch045_home.py')
b = load('bootstrap045_test', ROOT / 'scripts/downloads_bootstrap045.py')


def fixture_report(status='COMPLETED', public=None):
    if public is None:
        public = {name: ((ROOT / name).read_bytes() if (ROOT / name).exists() else
            b'# Explicit synthetic source fixture only.\n') for name in w.DIAGNOSTIC_SOURCES}
    current = {name: w.safe.sha(public[name]) for name in w.DIAGNOSTIC_SOURCES}
    families = json.loads(public['configs/P3_DIAGNOSTIC_FIXTURES_045.json'])['required_case_families']
    return {'kind': 'P3_DIAGNOSTIC_CONFORMANCE_045_v1', 'status': status,
        'scope': 'SYNTHETIC_HANDOFF_FIXTURE_ONLY', 'target_experiment_started': False,
        'target_execution_admitted': False, 'native_started': False, 'outcome_blind': True,
        'complete_work_budget_admitted': False, 'automatic_rerun_permitted': False,
        'full_resource_profile_started': False, 'original043044_remeasured': False,
        'B_comp': None, 'B_mem': None, 'source_hashes': current,
        'metrics': {'scope': '045_CONFORMANCE_INVOCATION_ONLY', 'synthetic_fixture_only': True},
        'planned_test_ids': ['synthetic.case_a', 'synthetic.case_b'],
        'test_outcomes': [{'test': name, 'status': 'PASSED', 'synthetic_fixture_only': True}
            for name in (['synthetic.case_a', 'synthetic.case_b'] if status == 'COMPLETED' else ['synthetic.case_a'])],
        'case_results': {'cases': {name: {'status': 'PASSED', 'synthetic_fixture_only': True} for name in families}},
        'required_case_families': families, 'passed': status == 'COMPLETED',
        'interruption': None if status == 'COMPLETED' else 'SYNTHETIC_COMPONENT_INTERRUPTION'}


class HandoffTests(unittest.TestCase):
    def setUp(self):
        parent = ROOT / 'delivery/tests045'
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
        self.git('config', 'user.name', 'Offline045 synthetic fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        (self.lab / '.gitignore').write_text('/delivery/\n')
        for name, workname in ((w.BASELINE_REPORT, 'REPORT_044.json'),
                               (w.BASELINE_RECEIPT, 'RECEIPT_044.json')):
            source = ROOT / name
            raw = source.read_bytes() if source.exists() else (ROOT.parent / 'work045' / workname).read_bytes()
            self.write(self.lab / name, raw)
        self.git('add', '.')
        self.git('commit', '-m', 'Synthetic045 accepted ancestor')
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
        self.commands, self.diagnostic_calls = [], 0
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
        manifest = {'kind': 'P3_CHECKPOINT_045_MANIFEST_v1',
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
        for name in ('checkpoint045_workflow.py', 'stage_source_packet038.py'):
            self.write(self.bundle / 'scripts' / name, self.public['scripts/' + name])
        self.write(self.bundle / 'launch045_home.py', self.public['scripts/launch045_home.py'])
        self.git('add', '.')
        self.git('commit', '-m', 'Synthetic045 frozen release')
        self.content = self.git('rev-parse', 'HEAD').decode().strip()
        self.release = {'kind': 'P3_CHECKPOINT_045_RELEASE_v1', 'repository': w.REPOSITORY,
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

    def diagnostic(self, source, output):
        self.diagnostic_calls += 1
        self.assertEqual({p.relative_to(source).as_posix() for p in source.rglob('*') if p.is_file()},
                         w.DIAGNOSTIC_SOURCES)
        self.assertFalse(any('042' in str(p) or p.suffix == '.pdf' for p in source.rglob('*')))
        self.assertFalse((source.parent / 'baseline_044').exists())
        self.write(output / 'REPORT.json', w.safe.canonical(fixture_report(public=self.public)))
        return {'child_start_observed': True, 'exit_code': 0, 'wall_seconds': 0.125,
                'termination': 'EXITED', 'fixture': True}

    def execute(self, module=w, bundle=None, diagnosticr=None):
        with patch.object(module, 'RETURN_COMMIT', self.accepted):
            return module.workflow(self.lab, bundle or self.bundle, git_runner=self.runner,
                diagnostic_runner=self.diagnostic if diagnosticr is None else diagnosticr, emit=lambda text: None)

    def test_one_reservation_preserves_full_report_and_exact_repeat(self):
        first, second = self.execute(), self.execute()
        self.assertEqual(first, second)
        self.assertEqual(self.diagnostic_calls, 1)
        report = json.loads((self.lab / first['report_path']).read_text())
        receipt = json.loads((self.lab / first['receipt_path']).read_text())
        self.assertEqual(report['diagnostic_report'], fixture_report(public=self.public))
        self.assertEqual(report['status'], 'DIAGNOSTICS_COMPLETED')
        self.assertEqual(receipt['report_sha256'], w.safe.sha((self.lab / first['report_path']).read_bytes()))
        self.assertEqual(receipt['cumulative_native_starts'], 18)
        self.assertEqual(receipt['cumulative_model_turns_sent'], 14)
        self.assertFalse(receipt['automatic_diagnostic_rerun_permitted'])
        self.assertFalse(receipt['target_experiment_started'])
        self.assertEqual(receipt['diagnostic_scope'], w.SCOPE)
        self.assertFalse(receipt['original043044_remeasured'])
        self.assertEqual(receipt['accepted044_report_sha256'], w.RETURN044_REPORT_SHA256)
        self.assertEqual(self.git('diff', '--name-only', self.content, 'HEAD').decode().splitlines(),
                         sorted([first['report_path'], first['receipt_path']]))
        self.assertNotIn('PRIVATE FIXTURE', (self.lab / first['report_path']).read_text())
        self.assertFalse(self.git('status', '--porcelain'))

    def test_failed_commit_and_push_never_reexecute_diagnostic(self):
        self.fail_action = 'commit'
        with self.assertRaisesRegex(w.safe.StageStop, 'git_commit_failed'):
            self.execute()
        self.assertEqual(self.diagnostic_calls, 1)
        self.fail_action = 'push'
        with self.assertRaisesRegex(w.safe.StageStop, 'git_push_failed'):
            self.execute()
        self.assertEqual(self.diagnostic_calls, 1)
        saved_head = self.git('rev-parse', 'HEAD')
        folder = self.lab / w.WORKFLOW / self.release['manifest_sha256']
        (folder / 'SAVED_REPORT.json').unlink()
        (folder / 'SAVED_RECEIPT.json').unlink()
        result = self.execute()
        self.assertEqual(self.diagnostic_calls, 1)
        self.assertEqual(saved_head, self.git('rev-parse', 'HEAD'))
        self.assertEqual(result['diagnostic_status'], 'DIAGNOSTICS_COMPLETED')

    def test_reservation_without_report_returns_interrupted_and_never_relaunches(self):
        def crash(source, output):
            self.diagnostic_calls += 1
            raise SystemExit('synthetic crash after reservation')
        with self.assertRaises(SystemExit):
            self.execute(diagnosticr=crash)
        result = self.execute()
        self.assertEqual(self.diagnostic_calls, 1)
        report = json.loads((self.lab / result['report_path']).read_text())
        self.assertEqual(report['status'], 'DIAGNOSTICS_INCOMPLETE')
        self.assertEqual(report['execution']['termination'], 'RESERVATION_FOUND_WITHOUT_SAVED_RESULT')
        self.assertIsNone(report['execution']['child_start_observed'])
        self.assertIsNone(report['diagnostic_report'])
        self.assertEqual(result, self.execute())
        self.assertEqual(self.diagnostic_calls, 1)

    def test_partial_child_report_survives_interruption_and_publication_retry(self):
        partial = fixture_report('INCOMPLETE', self.public)
        partial['interruption'] = 'FABRICATED_BUDGET_STOP'
        def interrupted(source, output):
            self.diagnostic_calls += 1
            self.write(output / 'REPORT.json', w.safe.canonical(partial))
            return {'child_start_observed': True, 'exit_code': -9, 'wall_seconds': 0.25,
                    'termination': 'PARENT_WALL_CAP'}
        self.fail_action = 'push'
        with self.assertRaises(w.safe.StageStop):
            self.execute(diagnosticr=interrupted)
        result = self.execute()
        report = json.loads((self.lab / result['report_path']).read_text())
        self.assertEqual(self.diagnostic_calls, 1)
        self.assertEqual(report['diagnostic_report'], partial)
        self.assertEqual(report['execution']['termination'], 'PARENT_WALL_CAP')
        self.assertEqual(report['status'], 'DIAGNOSTICS_INCOMPLETE')

    def test_exact_remote_report_reused_without_local_saved_cache(self):
        first = self.execute()
        folder = self.lab / w.WORKFLOW / self.release['manifest_sha256']
        # Explicit test of a separate installation's missing local report cache;
        # the once marker remains and the authoritative remote return is intact.
        (folder / 'SAVED_REPORT.json').unlink()
        (folder / 'SAVED_RECEIPT.json').unlink()
        self.assertEqual(first, self.execute())
        self.assertEqual(self.diagnostic_calls, 1)

    def test_changed_staged_output_is_preserved_without_second_diagnostic(self):
        self.fail_action = 'commit'
        with self.assertRaises(w.safe.StageStop):
            self.execute()
        report = next((self.lab / 'artifacts/CHECKPOINT_045_RETURN').rglob('REPORT.json'))
        report.write_text('{"human":"preserve"}\n')
        before = self.git('diff', '--cached', '--binary')
        with self.assertRaises(w.safe.StageStop):
            self.execute()
        self.assertEqual(self.diagnostic_calls, 1)
        self.assertEqual(before, self.git('diff', '--cached', '--binary'))
        self.assertIn('preserve', report.read_text())

    def test_published_incomplete_is_successful_command_with_clear_receipt(self):
        def incomplete(source, output):
            result = self.diagnostic(source, output)
            value = fixture_report('INCOMPLETE', self.public)
            value['interruption'] = 'SYNTHETIC_COMPONENT_INTERRUPTION'
            self.write(output / 'REPORT.json', w.safe.canonical(value))
            return result
        result = self.execute(diagnosticr=incomplete)
        with patch.object(w, 'workflow', return_value=result), patch.object(sys, 'argv',
                ['checkpoint045_workflow.py', '--bundle', str(self.bundle)]), \
                patch('sys.stdout', new_callable=io.StringIO) as capture:
            self.assertEqual(w.main(), 0)
        printed = capture.getvalue()
        self.assertIn('GitHub receipt:', printed)
        self.assertIn('DIAGNOSTICS_INCOMPLETE', printed)
        self.assertIn('successfully published', printed)
        self.assertIn('SYNTHETIC_COMPONENT_INTERRUPTION', printed)
        self.assertNotIn('STOP:', printed)
        self.assertEqual(result, self.execute())
        self.assertEqual(self.diagnostic_calls, 1)

    def test_accepted044_return_is_preserved_and_changed_baseline_refused(self):
        original = self.public[w.BASELINE_REPORT]
        self.execute()
        self.assertEqual((self.lab / w.BASELINE_REPORT).read_bytes(), original)
        self.assertFalse((self.lab / 'delivery/P3_043_RETURN_WORKFLOW').exists())
        changed = dict(self.public)
        changed[w.BASELINE_REPORT] = b'{}\n'
        with self.assertRaisesRegex(w.safe.StageStop, 'accepted044_baseline_hash_differs'):
            w.validate_baseline(changed)
        changed = dict(self.public)
        changed['scripts/profile043.py'] += b'# Changed frozen code\n'
        with self.assertRaisesRegex(w.safe.StageStop, 'accepted044_source_identity_not_preserved'):
            w.validate_baseline(changed)

    def test_child_with_remeasurement_claim_refused(self):
        bad = fixture_report(public=self.public)
        bad['original043044_remeasured'] = True
        with self.assertRaises(w.safe.StageStop):
            w.validate_child_report(bad)

    def test_changed_source_pin_publishes_rejection_without_poisoning_saved_state(self):
        bad = fixture_report(public=self.public)
        bad['source_hashes']['scripts/accounting043.py'] = '0' * 64
        raw = w.safe.canonical(bad)
        def malformed(source, output):
            self.diagnostic_calls += 1
            self.write(output / 'REPORT.json', raw)
            return {'child_start_observed': True, 'exit_code': 0, 'wall_seconds': 0.125,
                    'termination': 'EXITED', 'fixture': True}
        result = self.execute(diagnosticr=malformed)
        report = json.loads((self.lab / result['report_path']).read_text())
        self.assertEqual(result['diagnostic_status'], 'DIAGNOSTICS_INCOMPLETE')
        self.assertIsNone(report['diagnostic_report'])
        self.assertIn('diagnostic_sources_tests_or_usage_differs', report['child_report_failure_class'])
        self.assertEqual(base64.b64decode(report['rejected_child_report']['content']), raw)
        self.assertEqual(result, self.execute())
        self.assertEqual(self.diagnostic_calls, 1)

    def test_malformed_outcome_is_published_as_rejected_bytes_once(self):
        bad = fixture_report(public=self.public)
        bad['test_outcomes'] = [None]
        raw = w.safe.canonical(bad)
        def malformed(source, output):
            self.diagnostic_calls += 1
            self.write(output / 'REPORT.json', raw)
            return {'child_start_observed': True, 'exit_code': 0, 'wall_seconds': 0.1,
                'termination': 'EXITED', 'fixture': True}
        result = self.execute(diagnosticr=malformed)
        report = json.loads((self.lab / result['report_path']).read_text())
        self.assertEqual(report['status'], 'DIAGNOSTICS_INCOMPLETE')
        self.assertIsNone(report['diagnostic_report'])
        self.assertIn('test_plan_or_outcome_type_differs', report['child_report_failure_class'])
        self.assertEqual(base64.b64decode(report['rejected_child_report']['content']), raw)
        self.assertEqual(result, self.execute())
        self.assertEqual(self.diagnostic_calls, 1)

    def test_false_wrapper_completion_and_changed_invocation_accounting_refused(self):
        child = fixture_report('INCOMPLETE', self.public)
        value = w.execution_report(self.release, self.public,
            {'termination': 'EXITED', 'exit_code': 0, 'child_start_observed': True}, child, None)
        value['status'] = 'DIAGNOSTICS_COMPLETED'
        with self.assertRaisesRegex(w.safe.StageStop, 'wrapper_status_differs'):
            with patch.object(w, 'RETURN_COMMIT', self.accepted):
                value['baseline_return_commit'] = self.accepted
                w.validate_saved_report(w.safe.canonical(value), self.release, self.public)
        child['metrics']['scope'] = 'WRONGLY_COMBINED_PRIOR_INVOCATION'
        with self.assertRaisesRegex(w.safe.StageStop, 'diagnostic_sources_tests_or_usage_differs'):
            w.validate_diagnostic_scope(child, self.public)

    def test_actual_extracted_launcher_recovers_push_without_reexecution(self):
        files = {p.relative_to(self.bundle).as_posix(): p.read_bytes()
                 for p in self.bundle.rglob('*') if p.is_file()}
        files['README_045.md'] = b'Synthetic handoff fixture.\n'
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
            self.assertEqual(Path(command[3]).name, 'checkpoint045_workflow.py')
            module = load('extracted045_fixture', command[3])
            try:
                self.execute(module, Path(command[-1]))
                return subprocess.CompletedProcess(command, 0)
            except module.safe.StageStop:
                return subprocess.CompletedProcess(command, 1)
        self.fail_action = 'push'
        with self.assertRaises(l.LaunchStop):
            l.launch(raw, home=self.home, runner=execute)
        bundle = l.launch(raw, home=self.home, runner=execute)
        self.assertEqual(self.diagnostic_calls, 1)
        self.assertEqual((bundle.parent / 'PACKAGE.zip').read_bytes(), raw)
        self.assertFalse(self.git('ls-files', '--', 'delivery/'))

    def test_synthetic_child_uses_real_process_caps_and_wall_stop(self):
        source = self.lab / 'delivery/child_fixture_source'
        output = self.lab / 'delivery/child_fixture_output'
        code = ('import json,os,sys\nfrom pathlib import Path\n'
            'output=Path(sys.argv[sys.argv.index("--output")+1])\n'
            'report=' + repr(fixture_report()) + '\n'
            'report["fixture_affinity_count"]=len(os.sched_getaffinity(0))\n'
            'report["fixture_isolated_flags"]=[sys.flags.isolated,sys.flags.no_site,sys.dont_write_bytecode]\n'
            '(output/"REPORT.json").write_text(json.dumps(report))\n')
        self.write(source / w.VERIFIER, code.encode())
        result = w.run_diagnostic_child(source, output)
        self.assertEqual(result['exit_code'], 0)
        report, failure = w.read_child_report(output)
        self.assertIsNone(failure)
        self.assertEqual(report['fixture_affinity_count'], 1)
        self.assertEqual(report['fixture_isolated_flags'], [1, 1, True])
        self.assertEqual(result['stdout']['bytes'], 0)
        sleep_source = self.lab / 'delivery/sleep_fixture_source'
        sleep_output = self.lab / 'delivery/sleep_fixture_output'
        self.write(sleep_source / w.VERIFIER, b'import time\ntime.sleep(10)\n')
        with patch.dict(w.CAPS, {'parent_wall_seconds': 0.1}):
            stopped = w.run_diagnostic_child(sleep_source, sleep_output)
        self.assertEqual(stopped['termination'], 'PARENT_WALL_CAP')
        self.assertTrue(stopped['process_group_kill_attempted'])

    def test_actual_runner_preserves_named_failure_and_malformed_case_results(self):
        # Execute the exact runner with a tiny synthetic unittest module only.
        # Frozen reference sources are hashed but never imported by this fixture.
        for suffix, test_body, case_expression, expected in (
                ('success', 'self.assertEqual(2+2,4)', '{"cases":{"synthetic":{"status":"PASSED"}}}', 'COMPLETED'),
                ('failure', 'self.assertEqual(2+2,5)', '{"cases":{"synthetic":{"status":"PASSED"}}}', 'FAILED_CONFORMANCE'),
                ('bad_cases', 'self.assertTrue(True)', '{"bad":object()}', 'FAILED_CONFORMANCE'),
                ('missing_family', 'self.assertTrue(True)', '{"cases":{}}', 'FAILED_CONFORMANCE')):
            with self.subTest(suffix=suffix):
                source = self.lab / ('delivery/actual_runner_' + suffix)
                output = self.lab / ('delivery/actual_runner_output_' + suffix)
                public = {name: self.public[name] for name in w.DIAGNOSTIC_SOURCES}
                config = json.loads(public['configs/P3_DIAGNOSTIC_FIXTURES_045.json'])
                config['required_case_families'] = ['synthetic']
                public['configs/P3_DIAGNOSTIC_FIXTURES_045.json'] = w.safe.canonical(config)
                public['tests/test_diagnostics045.py'] = (
                    'import unittest\nclass Synthetic(unittest.TestCase):\n'
                    '    def test_case(self):\n        ' + test_body + '\n'
                    'def get_results():\n    return ' + case_expression + '\n').encode()
                for name, raw in public.items():
                    self.write(source / name, raw)
                outcome = w.run_diagnostic_child(source, output)
                self.assertEqual(outcome['exit_code'], 0)
                report, failure = w.read_child_report(output, public)
                self.assertIsNone(failure)
                self.assertEqual(report['status'], expected)
                self.assertEqual(len(report['test_outcomes']), 1)
                self.assertEqual(report['planned_test_ids'], ['test_diagnostics045.Synthetic.test_case'])
                self.assertFalse(report['target_experiment_started'])
                if suffix == 'failure':
                    self.assertEqual(report['test_outcomes'][0]['status'], 'FAILED')
                    self.assertIn('AssertionError', report['test_outcomes'][0]['failure']['traceback'])
                if suffix == 'missing_family':
                    self.assertEqual(report['interruption'], 'CASE_FAMILIES_INCOMPLETE')
                    self.assertFalse(report['passed'])
                if suffix == 'bad_cases':
                    self.assertEqual(report['interruption'], 'CASE_RESULTS_INVALID')
                    self.assertEqual(report['test_outcomes'][0]['status'], 'PASSED')
                    self.assertFalse(report['passed'])

    def test_downloads_registry_resolution_handles_spaces_and_duplicate_names(self):
        downloads = self.home / 'Windows Downloads é'
        downloads.mkdir()
        payload = io.BytesIO()
        with zipfile.ZipFile(payload, 'w') as archive:
            archive.writestr('launch045_home.py', b'# Explicit synthetic launcher fixture.\n')
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
