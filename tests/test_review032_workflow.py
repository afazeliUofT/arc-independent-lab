import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('workflow032_tested', HERE.parent / 'scripts' / 'review032_workflow.py')
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.calls, self.collections = [], []
        self.pins = {}
        for name in w.PINS:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            raw = ('fixture:' + name).encode()
            path.write_bytes(raw)
            self.pins[name] = w.sha(raw)

    def collect(self, root):
        report = json.loads((root / w.WORKFLOW / 'WORKFLOW_REPORT.json').read_text())
        self.collections.append(report)
        return {'tracked_paths': ['artifacts/fixture/REPORT.json'], 'status_summary': {}}

    def run_child(self, root, emit):
        self.calls.append(root)
        return {'controller_started': True, 'controller_reaped': True, 'exit_code': 0}

    def drive(self, **kwargs):
        return w.run_workflow(self.root, runner=kwargs.pop('runner', self.run_child),
            inspector=kwargs.pop('inspector', lambda root, emit: {'fixture_read_only_inspection': True}),
            collector=kwargs.pop('collector', self.collect), pins=kwargs.pop('pins', self.pins),
            emit=lambda value: None, **kwargs)

    def report(self, name='WORKFLOW_REPORT.json'):
        return json.loads((self.root / w.WORKFLOW / name).read_text())

    def test_absent_runs_launch_once_and_preserve_original_outcome_on_rerun(self):
        first = self.drive()
        initial = (self.root / w.WORKFLOW / 'LAUNCH_OUTCOME.json').read_bytes()
        second = self.drive()
        self.assertTrue(first['controller_invoked'])
        self.assertFalse(second['controller_invoked'])
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(len(self.collections), 2)
        self.assertEqual((self.root / w.WORKFLOW / 'LAUNCH_OUTCOME.json').read_bytes(), initial)
        self.assertFalse(self.report()['observed_at_return'][w.MAIN + '/REPORT.json'])

    def test_historical030_kernel_path_does_not_block_new032_authorized_operation(self):
        old = self.root / 'delivery/P3_FINITE_REVIEW_030_KERNEL_PREFLIGHT'
        old.mkdir(parents=True)
        (old / 'REPORT.json').write_text('{"historical":"preserved"}')
        before = (old / 'REPORT.json').read_bytes()
        self.assertTrue(self.drive()['controller_invoked'])
        self.assertEqual((old / 'REPORT.json').read_bytes(), before)

    def test_each_existing_partial_path_prevents_controller_launch(self):
        for relative in (w.MAIN, w.WORKFLOW + '/LAUNCH_RESERVED.json'):
            with self.subTest(relative=relative):
                path = self.root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch()
                result = self.drive()
                self.assertFalse(result['controller_invoked'])
                self.assertEqual(self.calls, [])
                path.unlink()

    def test_symlink_attempt_is_treated_as_existing_never_followed(self):
        (self.root / 'delivery').mkdir(exist_ok=True)
        (self.root / w.MAIN).symlink_to('/does/not/exist')
        self.assertFalse(self.drive()['controller_invoked'])
        self.assertEqual(self.calls, [])

    def test_changed_published_answer_cannot_launch_and_creates_report(self):
        (self.root / 'state/ESCALATION.md').write_text('APPROVED SOME OTHER SCOPE')
        result = self.drive()
        self.assertEqual(result['status'], 'WORKFLOW_STOPPED_EVIDENCE_PRESERVED')
        self.assertEqual(self.report()['reason_code'], 'approved032_pinned_input_mismatch')
        self.assertEqual(self.calls, [])
        self.assertEqual(len(self.collections), 1)

    def test_missing_controller_dependency_cannot_lose_workflow_report(self):
        def fail(root, emit):
            raise ModuleNotFoundError('DO_NOT_PUBLISH_THIS_MESSAGE')
        self.drive(runner=fail)
        report = self.report()
        self.assertEqual(report['error_class'], 'ModuleNotFoundError')
        self.assertNotIn('DO_NOT_PUBLISH_THIS_MESSAGE', json.dumps(report))
        self.assertEqual(self.report('LAUNCH_OUTCOME.json')['error_class'], 'ModuleNotFoundError')
        self.assertFalse(self.drive()['controller_invoked'])
        self.assertEqual(len(self.collections), 2)

    def test_interruption_still_persists_report_outcome_and_collects(self):
        def interrupt(root, emit):
            raise KeyboardInterrupt()
        self.drive(runner=interrupt)
        self.assertEqual(self.report()['status'], 'WORKFLOW_INTERRUPTED_EVIDENCE_PRESERVED')
        self.assertEqual(len(self.collections), 1)
        self.assertFalse(self.drive()['controller_invoked'])

    def test_collector_failure_still_leaves_report_and_prevents_repeat(self):
        def broken_collector(root):
            raise OSError('DO_NOT_PUBLISH_THIS_MESSAGE')
        result = self.drive(collector=broken_collector)
        self.assertIsNone(result['collection'])
        self.assertEqual(self.report()['collection_failure_class'], 'OSError')
        self.assertNotIn('DO_NOT_PUBLISH_THIS_MESSAGE', json.dumps(self.report()))
        self.assertFalse(self.drive()['controller_invoked'])

    def test_existing_report_target_symlink_does_not_overwrite_outside_file(self):
        folder = self.root / w.WORKFLOW
        folder.mkdir(parents=True)
        sentinel = self.root / 'sentinel'
        sentinel.write_text('unchanged')
        (folder / 'WORKFLOW_REPORT.json').symlink_to(sentinel)
        with self.assertRaises(w.WorkflowStop):
            self.drive()
        self.assertEqual(sentinel.read_text(), 'unchanged')
        self.assertEqual(self.calls, [])

    def test_launch_marker_is_present_and_durable_before_runner(self):
        def inspect(root, emit):
            marker = json.loads((root / w.WORKFLOW / 'LAUNCH_RESERVED.json').read_text())
            self.assertFalse(marker['native_start_or_model_turn_proven'])
            self.assertFalse(marker['automatic_retry'])
            return {'controller_reaped': True, 'exit_code': 1}
        self.drive(runner=inspect)

    def test_attempt_appearing_during_pin_verification_prevents_launch(self):
        original = w.read_fixed
        def race(root, relative, maximum=4 * 1024 * 1024):
            raw = original(root, relative, maximum)
            (root / w.MAIN).mkdir(parents=True, exist_ok=True)
            return raw
        w.read_fixed = race
        try:
            result = self.drive()
        finally:
            w.read_fixed = original
        self.assertEqual(result['status'], 'COLLECT_ONLY_ATTEMPT_APPEARED_BEFORE_LAUNCH')
        self.assertEqual(self.calls, [])

    def test_existing_evidence_collected_even_when_pins_differ(self):
        (self.root / w.MAIN).mkdir(parents=True)
        result = self.drive(pins={w.CONTROLLER: '0' * 64})
        self.assertFalse(result['controller_invoked'])
        self.assertEqual(len(self.collections), 1)
        self.assertEqual(self.report()['inspection_outcome']['status'], 'SKIPPED_INSPECTION_PRECONDITION_FAILED')

    def test_collect_only_inspection_is_separate_from_model_launch(self):
        (self.root / w.MAIN).mkdir(parents=True)
        inspected = []
        def inspect(root, emit):
            inspected.append(True)
            return {'native_start_or_model_turn_requested': False,
                    'controller_status_lines': ['STOP: Partial receipt exists']}
        result = self.drive(inspector=inspect)
        self.assertFalse(result['controller_invoked'])
        self.assertEqual(len(inspected), 1)
        self.assertFalse(result['inspection_outcome']['native_start_or_model_turn_requested'])
        self.assertEqual(len(self.collections), 1)


class TransportTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def command(self, source):
        script = self.root / 'synthetic_controller.py'
        script.write_text(source)
        return [sys.executable, '-I', '-B', '-u', str(script)]

    def test_pre_report_python_exit_has_safe_diagnostics_without_raw_error(self):
        source = 'print("STOP: A fixed protected check failed", flush=True)\nraise ImportError("PRIVATE_SENTINEL")\n'
        result = w.run_controller(self.root, lambda text: None, command=self.command(source), wall_seconds=3)
        self.assertEqual(result['exit_code'], 1)
        self.assertTrue(result['controller_reaped'])
        self.assertIn('ImportError', result['stderr_exception_classes'])
        self.assertEqual(result['stderr_frames'][0]['module_basename'], 'synthetic_controller.py')
        self.assertNotIn('PRIVATE_SENTINEL', json.dumps(result))
        self.assertEqual(result['controller_status_lines'], ['STOP: A fixed protected check failed'])

    def test_ctrl_c_reaches_child_handler_then_receipt_is_collected(self):
        source = ('import signal,time\n'
                  'def stop(a,b):\n print("STOP: Synthetic interruption cleanup",flush=True)\n raise SystemExit(0)\n'
                  'signal.signal(signal.SIGINT,stop)\nprint("READY",flush=True)\ntime.sleep(30)\n')
        sent = []
        def emit(text):
            if 'READY' in text and not sent:
                sent.append(True)
                raise KeyboardInterrupt()
        result = w.run_controller(self.root, emit, command=self.command(source), wall_seconds=3)
        self.assertTrue(result['interrupted'])
        self.assertTrue(result['controller_reaped'])
        self.assertFalse(result['forced_controller_cleanup'])
        self.assertEqual(result['exit_code'], 0)
        self.assertIn('STOP: Synthetic interruption cleanup', result['controller_status_lines'])

    def test_outer_guard_requests_interrupt_before_forced_cleanup(self):
        source = ('import signal,time\n'
                  'signal.signal(signal.SIGINT,lambda a,b:exit(0))\nprint("READY",flush=True)\ntime.sleep(30)\n')
        result = w.run_controller(self.root, lambda text: None, command=self.command(source), wall_seconds=0.2)
        self.assertTrue(result['outer_guard_reached'])
        self.assertTrue(result['controller_reaped'])
        self.assertFalse(result['forced_controller_cleanup'])

    def test_capture_and_terminal_delivery_are_bounded(self):
        observed = []
        source = 'import sys\nsys.stdout.write("x"*2200000)\nsys.stdout.flush()\n'
        result = w.run_controller(self.root, observed.append, command=self.command(source), wall_seconds=3)
        self.assertTrue(result['stream_capture_truncated']['stdout'])
        self.assertEqual(result['stream_bytes_observed']['stdout'], 2200000)
        self.assertLessEqual(sum(len(x) for x in observed), w.CAPTURE_BYTES)
        self.assertEqual(result['controller_status_lines'], [])

    def test_raw_stderr_messages_and_source_lines_are_discarded(self):
        result = w.safe_diagnostics(b'other private stdout\nSTATUS: SAFE\n',
            b'Traceback (most recent call last):\n  File "/private/folder/module.py", line 4, in start\n    SECRET_SOURCE\nValueError: SECRET_VALUE\n')
        self.assertEqual(result['controller_status_lines'], ['STATUS: SAFE'])
        self.assertEqual(result['stderr_exception_classes'], ['ValueError'])
        self.assertEqual(result['stderr_frames'], [{'module_basename': 'module.py', 'line': 4}])
        self.assertNotIn('SECRET', json.dumps(result))
        self.assertNotIn('/private/', json.dumps(result))

    def test_unexpected_terminal_error_cleans_up_child(self):
        source = ('import signal,time\n'
                  'signal.signal(signal.SIGINT,lambda a,b:exit(0))\nprint("READY",flush=True)\ntime.sleep(30)\n')
        def fail(text):
            raise OSError('PRIVATE_TERMINAL_ERROR')
        result = w.run_controller(self.root, fail, command=self.command(source), wall_seconds=3)
        self.assertTrue(result['controller_reaped'])
        self.assertEqual(result['transport_failure_class'], 'OSError')
        self.assertNotIn('PRIVATE_TERMINAL_ERROR', json.dumps(result))

    def test_inspection_never_passes_manual_native_launch_flag(self):
        controller = self.root / w.CONTROLLER
        controller.parent.mkdir(parents=True)
        controller.write_text('import sys\nassert len(sys.argv)==1\nprint("STATUS: INSPECTION_ONLY")\n')
        result = w.run_inspection(self.root, lambda value: None)
        self.assertEqual(result['exit_code'], 0)
        self.assertFalse(result['native_start_or_model_turn_requested'])
        self.assertEqual(result['controller_status_lines'], ['STATUS: INSPECTION_ONLY'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
