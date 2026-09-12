"""Outcome-blind043 transport fixtures; no reference learner or target panel executes.

Synthetic reports test execution reservation, process caps and publication recovery.
Production source files and complete-source conformance are checked separately.
"""
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import subprocess
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


w = load('workflow043_test', ROOT / 'scripts/checkpoint043_workflow.py')
l = load('launcher043_test', ROOT / 'scripts/launch043_home.py')


def fixture_report(status='COMPLETED'):
    return {'kind': 'P3_DEVELOPMENT_PROFILE_043_v1', 'status': status,
        'scope': 'SYNTHETIC_HANDOFF_FIXTURE_ONLY', 'target_experiment_started': False,
        'target_execution_admitted': False, 'native_started': False, 'outcome_blind': True,
        'complete_work_budget_admitted': False,
        'profiles': [{'fixture_count': 7, 'measured_value': 0.125}]}


class HandoffTests(unittest.TestCase):
    def setUp(self):
        parent = ROOT / 'delivery/tests043'
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
        self.git('config', 'user.name', 'Offline043 synthetic fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        (self.lab / '.gitignore').write_text('/delivery/\n')
        self.git('add', '.gitignore')
        self.git('commit', '-m', 'Synthetic043 accepted ancestor')
        self.accepted = self.git('rev-parse', 'HEAD').decode().strip()
        self.public = {name: (b'# Explicit synthetic source fixture only.\n'
            if name in w.PROFILE_SOURCES else (ROOT / name).read_bytes())
            for name in w.REQUIRED_CODE}
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
        manifest = {'kind': 'P3_CHECKPOINT_043_MANIFEST_v1',
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
        for name in ('checkpoint043_workflow.py', 'stage_source_packet038.py'):
            self.write(self.bundle / 'scripts' / name, self.public['scripts/' + name])
        self.write(self.bundle / 'launch043_home.py', self.public['scripts/launch043_home.py'])
        self.git('add', '.')
        self.git('commit', '-m', 'Synthetic043 frozen release')
        self.content = self.git('rev-parse', 'HEAD').decode().strip()
        self.release = {'kind': 'P3_CHECKPOINT_043_RELEASE_v1', 'repository': w.REPOSITORY,
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
        self.write(output / 'REPORT.json', w.safe.canonical(fixture_report()))
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
        self.assertEqual(report['profile_report'], fixture_report())
        self.assertEqual(report['status'], 'PROFILE_COMPLETED')
        self.assertEqual(receipt['report_sha256'], w.safe.sha((self.lab / first['report_path']).read_bytes()))
        self.assertEqual(receipt['cumulative_native_starts'], 18)
        self.assertEqual(receipt['cumulative_model_turns_sent'], 14)
        self.assertFalse(receipt['automatic_profile_rerun_permitted'])
        self.assertFalse(receipt['target_experiment_started'])
        self.assertEqual(self.git('diff', '--name-only', self.content, 'HEAD').decode().splitlines(),
                         sorted([first['report_path'], first['receipt_path']]))
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
        partial = fixture_report('INCOMPLETE')
        partial['profiles'][0]['interruption'] = 'FABRICATED_BUDGET_STOP'
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
        report = next((self.lab / 'artifacts').rglob('REPORT.json'))
        report.write_text('{"human":"preserve"}\n')
        before = self.git('diff', '--cached', '--binary')
        with self.assertRaises(w.safe.StageStop):
            self.execute()
        self.assertEqual(self.profile_calls, 1)
        self.assertEqual(before, self.git('diff', '--cached', '--binary'))
        self.assertIn('preserve', report.read_text())

    def test_actual_extracted_launcher_recovers_push_without_reexecution(self):
        files = {p.relative_to(self.bundle).as_posix(): p.read_bytes()
                 for p in self.bundle.rglob('*') if p.is_file()}
        files['README_043.md'] = b'Synthetic handoff fixture.\n'
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
            self.assertEqual(Path(command[3]).name, 'checkpoint043_workflow.py')
            module = load('extracted043_fixture', command[3])
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
        code = ('import json,os,sys\nfrom pathlib import Path\n'
            'output=Path(sys.argv[sys.argv.index("--output")+1])\n'
            'report=' + repr(fixture_report()) + '\n'
            'report["fixture_affinity_count"]=len(os.sched_getaffinity(0))\n'
            'report["fixture_isolated_flags"]=[sys.flags.isolated,sys.flags.no_site,sys.dont_write_bytecode]\n'
            '(output/"REPORT.json").write_text(json.dumps(report))\n')
        self.write(source / w.VERIFIER, code.encode())
        result = w.run_profile_child(source, output)
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
            stopped = w.run_profile_child(sleep_source, sleep_output)
        self.assertEqual(stopped['termination'], 'PARENT_WALL_CAP')
        self.assertTrue(stopped['process_group_kill_attempted'])


if __name__ == '__main__':
    unittest.main()
