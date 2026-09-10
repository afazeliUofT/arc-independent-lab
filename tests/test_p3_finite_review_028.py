"""Offline028 controller checks. Every stage is a fixed local fixture, never a model.

Historical SESSION reconstructions occur only inside named temporary test roots.
They are not generated, delivered or installed as native execution evidence.
The earlier history guard is mocked where the fixture lacks canonical019–026 runs;
its027 receipt consumer, byte pins, new gate, counts and reuse checks remain real.
"""
from __future__ import annotations
from contextlib import redirect_stdout
import copy
import base64
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

LAB = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('p3_finite_review_028_controller_tested',
    LAB / 'scripts/p3_finite_review_028.py')
controller = importlib.util.module_from_spec(spec)
spec.loader.exec_module(controller)


def put(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)


class Controller028Tests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='finite028_controller_fixture_', dir=LAB / 'delivery')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        patch = mock.patch.object(subprocess, 'Popen', side_effect=AssertionError(
            'Native/model process execution forbidden in controller tests'))
        self.Popen = patch.start()
        self.addCleanup(patch.stop)
        self.scope027, self.prior, inherited = controller.previous.load_bundle()
        self.scope = json.loads((LAB / controller.SCOPE_PATH).read_bytes())
        self.pins = {'scope_sha256': controller.SCOPE_SHA256,
            'controller_sha256': controller.sha((LAB / 'scripts/p3_finite_review_028.py').read_bytes()),
            'source_pins': controller.SOURCE_PINS, 'inherited027_pins': inherited,
            'report027_sha256': controller.REPORT027_SHA256,
            'historical027_approval_sha256': controller.AUTH027_SHA256,
            'packet_manifest_sha256': self.scope['private_packet_manifest_sha256']}
        self.case = 0

    def authorization_text(self):
        return ('# Test fixture approval only\n\n## ANSWER\n'
            'APPROVE_P3_FINITE_REVIEW_028_CORRECTION\n'
            'scope_sha256: ' + controller.SCOPE_SHA256 + '\n').encode()

    def rewrite_report(self, path, value):
        raw = controller.canonical(value)
        path.write_bytes(raw)
        path.with_name('REPORT.sha256').write_text(controller.sha(raw) + '\n')

    def historical_fixture(self):
        raw = (LAB / controller.REPORT027_PATH).read_bytes()
        value = json.loads(raw)
        run = self.root / 'delivery' / controller.previous.RUN_NAME
        put(run / 'REPORT.json', raw)
        put(run / 'REPORT.sha256', (controller.sha(raw) + '\n').encode())
        # Explicit test-only reconstructions; never used as actual laptop evidence.
        for stage in value['stages']:
            mode = stage['stage']
            put(run / (mode + '_SESSION.json'), controller.canonical(stage['observation']))
            put(run / (mode + '_STAGE.json'), controller.canonical(stage))
        put(run / 'ATTEMPT.json', controller.canonical({'pins': value['pins'],
            'authorization': value['authorization'], 'reserved_native_starts': 2,
            'reserved_turns': 2, 'automatic_retry': False, 'science_conditioned_on_synthetic': True}))
        auth = (LAB / controller.AUTH027_PATH).read_bytes()
        put(run / 'AUTHORIZATION.md', auth)
        put(self.root / controller.REPORT027_PATH, raw)
        put(self.root / controller.AUTH027_PATH, auth)
        return run, value

    def history_call(self, value):
        with mock.patch.object(controller, 'ROOT', self.root), mock.patch.object(
                controller.previous, 'prior_history', return_value=value['history']) as guard, mock.patch.object(
                controller.old, 'approval', side_effect=AssertionError('Historical validator cannot call old approval')):
            result = controller.prior_history(self.pins)
        self.assertEqual(guard.call_count, 1)
        return result

    def execute_fixture(self, *, synthetic=None, science=None, error=None, error_mode='synthetic',
                        omit_session=None, omit_stage=None, session_mismatch=None,
                        packet_changed=False, bundle_changed=False, history_error=False,
                        write_verdict=True, preflight_error=False):
        self.case += 1
        root = self.root / ('case_' + str(self.case))
        (root / 'delivery').mkdir(parents=True)
        auth_raw = self.authorization_text()
        put(root / 'state/ESCALATION.md', auth_raw)
        authorization = {'path': 'state/ESCALATION.md', 'sha256': controller.sha(auth_raw)}
        packet_info = {'packet_path': str(root / 'fixture_private_packet'),
            'manifest_sha256': self.pins['packet_manifest_sha256'], 'fixture_only': True}
        stages = []
        def fixed_stage(scope, prior, run, mode, packet, manifest, expected_binding=None):
            self.assertEqual(scope, self.scope)
            self.assertEqual(prior, self.prior)
            self.assertEqual(expected_binding, None if mode == 'synthetic' else controller.BINDING)
            observation = {'kind': controller.SESSION_KIND, 'mode': mode,
                'client_started': True, 'model_turn_request_sent': True, 'native_process_reaped': True,
                'selected_binding': controller.BINDING.copy(), 'fixture_only': True,
                'status': 'SYNTHETIC_REFUSAL_OBSERVED' if mode == 'synthetic' else 'VERDICT_SUBMITTED',
                'synthetic_allowed_read_observed': mode == 'synthetic', 'observed_refusal': mode == 'synthetic',
                'synthetic_argument_error_observed': mode == 'synthetic',
                'recoverable_input_errors': 1, 'failed_broker_calls': 2,
                'broker_receipts': [{'method': 'item/tool/call', 'tool': 'read_text', 'successful': False,
                                    'error_code': 'integer_bounds'},
                                   {'method': 'item/tool/call', 'tool': 'read_text', 'successful': True,
                                    'error_code': None}],
                'broker_boundary_failure': {'layer': 'dispatch', 'code': 'boundary.resource_path',
                    'tool': 'read_text', 'raw_input_path_or_exception_saved': False},
                'verdict_submitted': mode == 'science'}
            stage = {'stage': mode, 'observation': observation,
                'host_checks': {'all_noncredential_checks_pass': True},
                'fresh_process_and_runtime_directories': True, 'pi_conversation_imported': False,
                'fixture_only': True}
            modifications = synthetic if mode == 'synthetic' else science
            for key, val in (modifications or {}).items():
                if key == 'host': stage['host_checks']['all_noncredential_checks_pass'] = val
                elif key in ('fresh_process_and_runtime_directories', 'pi_conversation_imported'): stage[key] = val
                else: observation[key] = val
            (run / (mode + '_native')).mkdir()
            (run / (mode + '_output')).mkdir()
            if mode == 'science' and write_verdict:
                put(run / 'science_output/REVIEW_VERDICT.json', b'{"fixture_only":true,"not_a_scientific_verdict":true}\n')
            if mode != omit_session:
                saved = copy.deepcopy(observation)
                if session_mismatch == mode: saved['fixture_changed'] = True
                controller.exclusive_json(run / (mode + '_SESSION.json'), saved)
            if mode != omit_stage:
                controller.exclusive_json(run / (mode + '_STAGE.json'), stage)
            stages.append(stage)
            if error is not None and mode == error_mode:
                raise error
            return stage
        bundle = (copy.deepcopy(self.scope), self.prior, self.pins)
        if bundle_changed: bundle[0]['maximum_native_processes'] = 9
        ready = copy.deepcopy(packet_info)
        if packet_changed: ready['manifest_sha256'] = '0' * 64
        installer = mock.Mock()
        installer.verify_packet.return_value = ready
        with mock.patch.object(controller, 'ROOT', root), mock.patch.object(
                controller, 'prior_history', return_value={'fixture_only': True},
                side_effect=controller.Stop('History fixture stopped') if history_error else None), mock.patch.object(
                controller, 'packet_preflight', return_value={'fixture_only': True,
                    'kind': 'P3_PRIVATE_PACKET_CONTENT_PREFLIGHT_028_v1',
                    'manifest_sha256': self.pins['packet_manifest_sha256'],
                    'model_called': False, 'native_process_started': False, 'auditor_executed': False},
                side_effect=controller.Stop('Packet preflight fixture stopped') if preflight_error else None), mock.patch.object(
                controller, 'run_stage', side_effect=fixed_stage) as stage_call, mock.patch.object(
                controller, 'load_bundle', return_value=bundle), mock.patch.object(
                controller, 'module', return_value=installer):
            if history_error or preflight_error:
                with self.assertRaises(controller.Stop):
                    controller.execute(self.scope, self.prior, self.pins, authorization, packet_info)
                self.assertFalse((root / 'delivery' / controller.RUN_NAME).exists())
                stage_call.assert_not_called()
                return None, None, 0
            path = controller.execute(self.scope, self.prior, self.pins, authorization, packet_info)
        self.Popen.assert_not_called()
        return path, json.loads(path.read_bytes()), stage_call.call_count

    def test_exact_real_bundle_is_ready_without_native_operation(self):
        scope, prior, pins = controller.load_bundle()
        self.assertEqual(scope, self.scope)
        self.assertEqual(prior, self.prior)
        self.assertEqual(pins, self.pins)
        self.assertEqual(len(pins['inherited027_pins']['inherited026_pins']['inherited024_pins']['source_pins']), 100)
        self.Popen.assert_not_called()

    def test_default_inspection_neither_launches_nor_reads_host(self):
        with mock.patch.object(controller, 'load_bundle', return_value=(self.scope, self.prior, self.pins)), mock.patch.object(
                controller.old, 'canonical_host', side_effect=AssertionError('No host inspection')), mock.patch.object(
                controller, 'execute', side_effect=AssertionError('No execution')), mock.patch.object(
                sys, 'argv', ['p3_finite_review_028.py']), redirect_stdout(io.StringIO()) as out:
            self.assertEqual(controller.main(), 0)
        self.assertIn('Inspection only', out.getvalue())

    def test_exact_approval_requires_literal_manual_launch(self):
        put(self.root / 'state/ESCALATION.md', self.authorization_text())
        with mock.patch.object(controller, 'ROOT', self.root):
            for manual in (False, None, 1, 'true'):
                with self.subTest(manual=manual), self.assertRaises(controller.Stop):
                    controller.approval(self.scope, manual_launch=manual)
            result = controller.approval(self.scope, manual_launch=True)
        self.assertEqual(result['sha256'], controller.sha(self.authorization_text()))

    def test_prior_approval_and_ambiguous_answers_cannot_approve028(self):
        good = self.authorization_text().decode()
        bad = (good.replace('_028_CORRECTION', '_024_CORRECTION'),
            good + '\n## ANSWER\n', '<!--\n' + good + '-->\n',
            '```\n' + good + '```\n', good.replace(controller.SCOPE_SHA256, 'wrong'),
            good + 'extra prose\n')
        with mock.patch.object(controller, 'ROOT', self.root):
            for text in bad:
                with self.subTest(text=text):
                    put(self.root / 'state/ESCALATION.md', text.encode())
                    with self.assertRaises(controller.Stop): controller.approval(self.scope, manual_launch=True)

    def test_actual027_receipt_consumer_accepts_explicit_historical_fixture(self):
        _, value = self.historical_fixture()
        result = self.history_call(value)
        self.assertEqual((result['prior_native_starts'], result['prior_sent_turns']), (8, 5))
        self.assertEqual((result['new_cumulative_native_ceiling'], result['new_cumulative_sent_turn_ceiling']), (10, 7))
        self.assertTrue(result['separate027_sessions_reverified'])

    def test_actual027_separate_session_missing_or_changed_stops_without_reconstruction(self):
        for missing in (True, False):
            with self.subTest(missing=missing):
                run, value = self.historical_fixture()
                path = run / 'synthetic_SESSION.json'
                if missing: path.unlink()
                else: path.write_bytes(path.read_bytes() + b' \n')
                with self.assertRaises((controller.Stop, OSError)): self.history_call(value)
                if missing: self.assertFalse(path.exists())

    def test_actual027_science_session_missing_or_changed_stops_without_reconstruction(self):
        for missing in (True, False):
            with self.subTest(missing=missing):
                run, value = self.historical_fixture()
                path = run / 'science_SESSION.json'
                if missing: path.unlink()
                else: path.write_bytes(path.read_bytes() + b' \n')
                with self.assertRaises((controller.Stop, OSError)): self.history_call(value)
                if missing: self.assertFalse(path.exists())

    def test_actual027_report_change_is_refused_with_recomputed_local_checksum(self):
        run, value = self.historical_fixture()
        changed = copy.deepcopy(value)
        changed['attempt_accounting']['cumulative_observed_sent_turns'] = 2
        self.rewrite_report(run / 'REPORT.json', changed)
        with self.assertRaises(controller.Stop): self.history_call(value)

    def test_unverified_history_precedes_directory_and_reservation(self):
        self.execute_fixture(history_error=True)

    def test_packet_preflight_failure_precedes_directory_reservation_and_native_stage(self):
        self.execute_fixture(preflight_error=True)

    def test_full_synthetic_admission_is_required_before_science(self):
        variants = ({'synthetic_argument_error_observed': False}, {'recoverable_input_errors': 0},
            {'recoverable_input_errors': True}, {'failed_broker_calls': 1}, {'broker_receipts': []},
            {'broker_boundary_failure': None}, {'synthetic_allowed_read_observed': False}, {'observed_refusal': False},
            {'native_process_reaped': False}, {'client_started': False, 'model_turn_request_sent': False},
            {'model_turn_request_sent': False}, {'host': False}, {'host': 1},
            {'fresh_process_and_runtime_directories': False}, {'pi_conversation_imported': True},
            {'selected_binding': {'model': 'other', 'id': 'other', 'effort': 'max'}})
        for changes in variants:
            with self.subTest(changes=changes):
                path, value, calls = self.execute_fixture(synthetic=changes)
                self.assertEqual(calls, 1)
                self.assertFalse(value['science_started'])
                self.assertFalse((path.parent / 'science_output').exists())
                self.assertEqual(value['status'], 'STOPPED_WITHOUT_COMPLETED_REVIEW')
                self.assertEqual(controller.existing(path.parent, self.pins), path)

    def test_synthetic_session_or_stage_linkage_failure_blocks_science(self):
        for options in ({'omit_session': 'synthetic'}, {'omit_stage': 'synthetic'},
                        {'session_mismatch': 'synthetic'}):
            with self.subTest(options=options):
                _, value, calls = self.execute_fixture(**options)
                self.assertEqual(calls, 1)
                self.assertEqual(value['status'], 'STOPPED_WITHOUT_COMPLETED_REVIEW')
                self.assertFalse(value['science_started'])

    def test_packet_or_frozen_bundle_change_blocks_science(self):
        for options in ({'packet_changed': True}, {'bundle_changed': True}):
            with self.subTest(options=options):
                _, value, calls = self.execute_fixture(**options)
                self.assertEqual(calls, 1)
                self.assertFalse(value['science_started'])

    def test_success_preserves_submitted_bytes_and_counts_all_sent_turns(self):
        path, value, calls = self.execute_fixture()
        self.assertEqual(calls, 2)
        self.assertEqual(value['status'], 'REVIEWER_OUTPUT_PRESERVED')
        self.assertEqual(value['stage_attempts'], ['synthetic', 'science'])
        self.assertTrue(value['reviewer_output']['execution_admitted'])
        count = value['attempt_accounting']
        self.assertEqual((count['cumulative_observed_native_starts'], count['cumulative_observed_sent_turns']), (10, 7))
        self.assertEqual(controller.existing(path.parent, self.pins), path)
        self.assertEqual((path.parent / 'science_output/REVIEW_VERDICT.json').read_bytes(),
            b'{"fixture_only":true,"not_a_scientific_verdict":true}\n')

    def test_science_without_output_is_not_a_completed_review(self):
        path, value, calls = self.execute_fixture(write_verdict=False,
            science={'verdict_submitted': False, 'status': 'STOPPED_WITHOUT_VERDICT'})
        self.assertEqual(calls, 2)
        self.assertEqual(value['status'], 'STOPPED_WITHOUT_REVIEWER_VERDICT')
        self.assertIsNone(value['reviewer_output'])
        self.assertEqual(controller.existing(path.parent, self.pins), path)

    def test_output_is_preserved_but_not_admitted_after_host_or_cleanup_failure(self):
        for changes in ({'host': False}, {'native_process_reaped': False},
                        {'model_turn_request_sent': False}, {'selected_binding': None}):
            with self.subTest(changes=changes):
                path, value, _ = self.execute_fixture(science=changes)
                self.assertEqual(value['status'], 'STOPPED_WITHOUT_COMPLETED_REVIEW')
                self.assertFalse(value['reviewer_output']['execution_admitted'])
                self.assertFalse(value['reviewer_output']['parent_edited'])
                self.assertEqual(controller.existing(path.parent, self.pins), path)

    def test_exception_keeps_actual_session_counts_and_withholds_raw_error(self):
        secret = 'SENSITIVE_NATIVE_ERROR_DO_NOT_RETAIN'
        path, value, calls = self.execute_fixture(error=RuntimeError(secret), omit_stage='synthetic')
        self.assertEqual(calls, 1)
        self.assertNotIn(secret, path.read_text())
        self.assertEqual(value['attempt_accounting']['cumulative_observed_sent_turns'], 6)
        self.assertEqual(controller.existing(path.parent, self.pins), path)

    def test_missing_session_retains_full_two_stage_reservation(self):
        path, value, _ = self.execute_fixture(error=RuntimeError('fixture'),
            omit_session='synthetic', omit_stage='synthetic')
        count = value['attempt_accounting']
        self.assertTrue(count['missing_session_counts_are_only_minimum_observations'])
        self.assertEqual((count['maximum_cumulative_reservation_native_starts'],
                          count['maximum_cumulative_reservation_turns']), (10, 7))
        self.assertTrue(count['unobserved_reserved_capacity_is_not_automatically_released'])
        self.assertEqual(controller.existing(path.parent, self.pins), path)

    def test_complete_receipt_reuse_never_launches_or_rechecks_host(self):
        path, _, _ = self.execute_fixture()
        before = {p.relative_to(path.parent): p.read_bytes() for p in path.parent.rglob('*') if p.is_file()}
        with mock.patch.object(controller, 'ROOT', path.parent.parent.parent), mock.patch.object(
                controller, 'load_bundle', return_value=(self.scope, self.prior, self.pins)), mock.patch.object(
                controller.old, 'canonical_host', side_effect=AssertionError('No host reread')), mock.patch.object(
                controller, 'execute', side_effect=AssertionError('No repeated operation')), mock.patch.object(
                sys, 'argv', ['p3_finite_review_028.py', '--run-attended-review']), redirect_stdout(io.StringIO()) as out:
            self.assertEqual(controller.main(), 0)
        self.assertIn('VERIFIED TERMINAL RECEIPT', out.getvalue())
        self.assertIn('REUSED', out.getvalue())
        self.assertIn('STATUS: REVIEWER_OUTPUT_PRESERVED', out.getvalue())
        self.assertIn('REVIEW_VERDICT: ' + str(path.parent / 'science_output/REVIEW_VERDICT.json'), out.getvalue())
        self.assertEqual({p.relative_to(path.parent): p.read_bytes() for p in path.parent.rglob('*') if p.is_file()}, before)

    def test_safe_stop_reason_keeps_only_exact_local_guard_text(self):
        self.assertEqual(controller.safe_stop_message(controller.Stop('Exact local guard reason')),
            'Exact local guard reason')
        class ForeignStop(controller.Stop):
            pass
        for error in (RuntimeError('SENSITIVE_NATIVE_ERROR'), OSError('SENSITIVE_NATIVE_ERROR'),
                      ForeignStop('SENSITIVE_NATIVE_ERROR')):
            with self.subTest(error=type(error).__name__):
                self.assertNotIn('SENSITIVE_NATIVE_ERROR', controller.safe_stop_message(error))
                self.assertIn('existing work preserved', controller.safe_stop_message(error))

    def test_stopped_receipt_reports_status_without_a_verdict_path(self):
        path, _, _ = self.execute_fixture(synthetic={'observed_refusal': False})
        with redirect_stdout(io.StringIO()) as out:
            controller.print_receipt(path)
        self.assertIn('STATUS: STOPPED_WITHOUT_COMPLETED_REVIEW', out.getvalue())
        self.assertIn('Attach REPORT.json only', out.getvalue())
        self.assertNotIn('REVIEW_VERDICT:', out.getvalue())

    def test_partial_directory_is_preserved_and_refused(self):
        run = self.root / 'delivery' / controller.RUN_NAME
        put(run / 'ATTEMPT.json', b'{"fixture_only":true}\n')
        before = (run / 'ATTEMPT.json').read_bytes()
        with self.assertRaises((controller.Stop, OSError)): controller.existing(run, self.pins)
        self.assertEqual((run / 'ATTEMPT.json').read_bytes(), before)
        self.assertFalse((run / 'REPORT.json').exists())

    def test_changed_session_stage_authorization_or_verdict_is_refused_on_reuse(self):
        for filename in ('synthetic_SESSION.json', 'science_SESSION.json', 'synthetic_STAGE.json',
                         'science_STAGE.json', 'AUTHORIZATION.md', 'science_output/REVIEW_VERDICT.json'):
            with self.subTest(filename=filename):
                path, _, _ = self.execute_fixture()
                changed = path.parent / filename
                changed.write_bytes(changed.read_bytes() + b' \n')
                with self.assertRaises(controller.Stop): controller.existing(path.parent, self.pins)

    def test_changed_attempt_reservation_cannot_be_released(self):
        for key, wrong in (('reserved_native_starts', 0), ('reserved_turns', True), ('automatic_retry', True)):
            with self.subTest(key=key):
                path, _, _ = self.execute_fixture()
                journal = path.parent / 'ATTEMPT.json'
                value = json.loads(journal.read_bytes()); value[key] = wrong
                journal.write_bytes(controller.canonical(value))
                with self.assertRaises(controller.Stop): controller.existing(path.parent, self.pins)

    def test_recomputed_report_cannot_forge_counts_stage_order_or_admission(self):
        mutations = (
            lambda v: v['attempt_accounting'].__setitem__('reserved_turns_this_attempt', True),
            lambda v: v['attempt_accounting'].__setitem__('cumulative_observed_sent_turns', 4),
            lambda v: v.__setitem__('science_started', False),
            lambda v: v.__setitem__('stage_attempts', ['science', 'synthetic']),
            lambda v: v['stages'][0]['observation'].__setitem__('observed_refusal', False),
            lambda v: v['reviewer_output'].__setitem__('execution_admitted', False),
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                path, value, _ = self.execute_fixture()
                mutation(value); self.rewrite_report(path, value)
                with self.assertRaises(controller.Stop): controller.existing(path.parent, self.pins)

    def test_unrecorded_session_or_stage_cannot_be_ignored(self):
        for filename in ('science_SESSION.json', 'science_STAGE.json'):
            with self.subTest(filename=filename):
                path, value, _ = self.execute_fixture(synthetic={'observed_refusal': False})
                put(path.parent / filename, controller.canonical({'kind': controller.SESSION_KIND,
                    'mode': 'science', 'client_started': True, 'model_turn_request_sent': True}))
                with self.assertRaises(controller.Stop): controller.existing(path.parent, self.pins)


class PacketContentPreflight028Tests(unittest.TestCase):
    """Uses actual public pinned auditor dependencies and synthetic bootstrap/page.

    This is an engineering packet fixture; it is never a replacement for the
    unavailable hosted private722-file packet and never executes the auditor.
    """
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='packet028_content_fixture_', dir=LAB / 'delivery')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.packet = self.root / 'delivery/packet'
        self.packet.mkdir(parents=True)
        self.original = controller.module('p3_review_broker')
        closure_raw = (LAB / self.original.CLOSURE).read_bytes()
        closure = json.loads(closure_raw)
        self.files = {}
        self.add(self.original.CLOSURE, closure_raw, 'text')
        for entry in closure['view_input_files']:
            self.add(entry['path'], (LAB / entry['path']).read_bytes(), 'text')
        for name in {**closure['original_raw_inventory'], **closure['post_run_additional_inventory']}:
            path = self.original.RAW_DIR + '/' + name
            self.add(path, (LAB / path).read_bytes(), 'text')
        for path in ('docs/P3_AUDIT_REVIEW_PACKET.md', 'docs/P3_RESIDUAL_REVIEW_SUPPLEMENT.md'):
            self.add(path, b'Engineering fixture bootstrap only.\n', 'text')
        self.add('pages/fixture.png', base64.b64decode(
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII='), 'image')
        self.add('papers/fixture.pdf', b'%PDF engineering fixture only\n', 'binary')
        self.add('PACKET_INDEX.json', controller.canonical({'files': [
            {**self.files['pages/fixture.png'], 'bytes': len((self.packet / 'pages/fixture.png').read_bytes())}]}), 'text')
        self.add('PDF_PAGE_INDEX.json', controller.canonical({'fixture_pages': ['pages/fixture.png']}), 'text')
        self.freeze()
        patch = mock.patch.object(subprocess, 'Popen', side_effect=AssertionError('No process in preflight'))
        self.Popen = patch.start(); self.addCleanup(patch.stop)

    def add(self, path, raw, kind):
        put(self.packet / path, raw)
        self.files[path] = {'path': path, 'sha256': controller.sha(raw), 'kind': kind}

    def freeze(self):
        raw = controller.canonical({'schema_version': 1, 'files': list(self.files.values())})
        put(self.packet / 'BROKER_MANIFEST.json', raw)
        self.info = {'packet_path': str(self.packet), 'manifest_sha256': controller.sha(raw)}

    def test_all_content_types_indexes_and_actual_auditor_dependencies_checked_without_process(self):
        value = controller.packet_preflight(self.root, self.info)
        self.assertEqual(value['files_rehashed'], len(self.files))
        self.assertEqual(value['content_kinds_verified']['image'], 1)
        self.assertFalse(value['auditor_executed'])
        self.assertFalse(value['native_process_started'])
        self.assertFalse(value['model_called'])
        self.Popen.assert_not_called()
        self.assertEqual(list((self.root / 'delivery').iterdir()), [self.packet])

    def test_unknown_index_layout_is_not_guessed_or_required(self):
        self.add('PACKET_INDEX.json', b'{"future_layout": []}\n', 'text')
        self.add('PDF_PAGE_INDEX.json', b'[]\n', 'text')
        self.freeze()
        self.assertTrue(controller.packet_preflight(self.root, self.info)[
            'index_descriptive_schema_not_claimed_validated'])

    def test_invalid_utf8_stops_before_any_process(self):
        self.add('bad_utf8.txt', b'\xff\xfe', 'text'); self.freeze()
        with self.assertRaisesRegex(controller.Stop, 'not UTF-8'):
            controller.packet_preflight(self.root, self.info)
        self.Popen.assert_not_called()

    def test_invalid_png_header_stops_before_any_process(self):
        self.add('pages/fixture.png', b'not a PNG', 'image'); self.freeze()
        with self.assertRaisesRegex(controller.Stop, 'bounded PNG'):
            controller.packet_preflight(self.root, self.info)

    def test_bootstrap_json_parse_failure_stops_before_any_process(self):
        self.add('PDF_PAGE_INDEX.json', b'{', 'text'); self.freeze()
        with self.assertRaisesRegex(controller.Stop, 'valid JSON'):
            controller.packet_preflight(self.root, self.info)

    def test_recognized_index_hash_conflict_stops_before_any_process(self):
        self.add('PACKET_INDEX.json', controller.canonical({'files': [
            {'path': 'pages/fixture.png', 'sha256': '0' * 64}]}), 'text'); self.freeze()
        with self.assertRaisesRegex(controller.Stop, 'hash disagrees'):
            controller.packet_preflight(self.root, self.info)

    def test_fixed_auditor_change_cannot_be_hidden_by_new_packet_manifest(self):
        self.add(self.original.AUDITOR, b'print("changed fixture")\n', 'text'); self.freeze()
        with self.assertRaisesRegex(controller.Stop, 'auditor executable changed'):
            controller.packet_preflight(self.root, self.info)

    def test_changed_actual_packet_bytes_are_rejected_with_safe_finite_reason(self):
        put(self.packet / 'PDF_PAGE_INDEX.json', b'CHANGED_SECRET_SHOULD_NOT_APPEAR')
        with self.assertRaises(controller.Stop) as result:
            controller.packet_preflight(self.root, self.info)
        self.assertNotIn('CHANGED_SECRET_SHOULD_NOT_APPEAR', str(result.exception))
        self.assertIn('preflight refused:', str(result.exception))


if __name__ == '__main__':
    unittest.main()
