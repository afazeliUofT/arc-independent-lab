"""Focused offline checks for the explicitly approved Sol/Max option.

Synthetic fixture children exercise stdio and the unchanged closed broker only.
No Codex, auth, model, scientific review, network or Git operation is invoked.
"""
from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import p3_reviewer_profile_022 as profile
import p3_reviewer_admission_022 as admission
import p3_reviewer_session_022 as session
import p3_reviewer_admission_021 as astra_admission
import p3_finite_review_022 as finite


def load_file(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def row(model='gpt-5.6-sol', efforts=('high', 'max', 'ultra')):
    return {'model': model, 'id': model, 'hidden': False, 'isDefault': False,
            'supportedReasoningEfforts': [{'reasoningEffort': e} for e in efforts],
            'defaultReasoningEffort': 'high'}


class SelectionTests(unittest.TestCase):
    def test_exact_sol_max_is_selected_even_when_ultra_is_advertised(self):
        catalog = profile.safe_model_catalog({'data': [row('gpt-6-astra'), row()]})
        self.assertEqual(admission.select_model(catalog),
                         {'model': 'gpt-5.6-sol', 'id': 'gpt-5.6-sol', 'effort': 'max'})
        self.assertEqual(astra_admission.select_model(catalog)['model'], 'gpt-6-astra')
        self.assertEqual(astra_admission.select_model(catalog)['effort'], 'ultra')

    def test_absent_sol_absent_max_and_unknown_effort_stop_without_fallback(self):
        for rows in ([row('gpt-6-astra')], [row(efforts=('high', 'ultra'))],
                     [row(efforts=('max', 'unknown-effort'))], []):
            with self.subTest(rows=rows), self.assertRaises(admission.Stop):
                admission.select_model(profile.safe_model_catalog({'data': rows}))
        with self.assertRaises(astra_admission.Stop):
            astra_admission.select_model(profile.safe_model_catalog({'data': [row()]}))

    def test_thread_and_turn_control_reject_model_or_effort_substitution(self):
        for model, effort in (('gpt-6-astra', 'max'), ('gpt-5.6-sol', 'ultra'),
                              ('gpt-5.6-sol', 'high')):
            with self.subTest(model=model, effort=effort), self.assertRaises(admission.Stop):
                admission.turn_params('synthetic-thread', model, effort, 'Synthetic test only')
        result = admission.turn_params('synthetic-thread', 'gpt-5.6-sol', 'max', 'Synthetic test only')
        self.assertEqual((result['model'], result['effort']), ('gpt-5.6-sol', 'max'))

    def test_profile_retains_all_original_restrictions_and_only_changes_model_identity(self):
        old = (ROOT / 'scripts/p3_reviewer_profile.py').read_text()
        expected = old.replace('REQUESTED_MODEL = "gpt-6-astra"', 'REQUESTED_MODEL = "gpt-5.6-sol"')
        self.assertEqual((ROOT / 'scripts/p3_reviewer_profile_022.py').read_text(), expected)
        self.assertEqual(finite.PROMPTS, {
            'synthetic': 'configs/P3_REVIEW_SYNTHETIC_019.txt',
            'science': 'configs/P3_REVIEW_SCIENTIFIC_019.txt'})


class ControllerTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix='sol_option_fixture_', dir=ROOT / 'delivery')
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        for name in ('state', 'delivery', 'configs'):
            (self.root / name).mkdir()
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(mock.patch.object(finite, 'ROOT', self.root))
        self.stack.enter_context(mock.patch.object(finite, 'SCOPE_SHA256', 'a' * 64))
        self.scope = {'approval_id': 'APPROVE_P3_FINITE_REVIEW_022_SOL'}
        self.pins = {'scope_sha256': finite.SCOPE_SHA256}

    def answer(self, approval_id, scope):
        (self.root / 'state/ESCALATION.md').write_text(
            '## ANSWER\n' + approval_id + '\nscope_sha256: ' + scope + '\n')

    def test_original_approval_never_authorizes_and_new_exact_approval_does(self):
        for identifier, scope in (('APPROVE_P3_FINITE_REVIEW_019', finite.PRIOR_SCOPE_SHA256),
                                  (self.scope['approval_id'], finite.PRIOR_SCOPE_SHA256),
                                  ('APPROVE_P3_FINITE_REVIEW_019', finite.SCOPE_SHA256)):
            self.answer(identifier, scope)
            with self.assertRaises(finite.Stop):
                finite.approval(self.scope)
        self.answer(self.scope['approval_id'], finite.SCOPE_SHA256)
        self.assertEqual(finite.approval(self.scope)['path'], 'state/ESCALATION.md')

    def test_old_approval_stops_launch_before_packet_or_native_operation(self):
        self.answer('APPROVE_P3_FINITE_REVIEW_019', finite.PRIOR_SCOPE_SHA256)
        with mock.patch.object(finite, 'load_bundle', return_value=(self.scope, {}, self.pins)), \
             mock.patch.object(finite, 'canonical_host'), \
             mock.patch.object(finite, 'module') as modules, \
             mock.patch.object(finite, 'execute') as execute, \
             mock.patch.object(sys, 'argv', ['p3_finite_review_022.py', '--run-attended-review']), \
             self.assertRaises(finite.Stop):
            finite.main()
        modules.assert_not_called()
        execute.assert_not_called()
        self.assertFalse((self.root / 'delivery' / finite.RUN_NAME).exists())

    def fixture_chain(self):
        modules = [load_file('option022_history_' + str(i), ROOT / 'scripts' / name) for i, name in
                   enumerate(('p3_finite_review.py', 'p3_finite_review_020.py', 'p3_finite_review_021.py'))]
        runs, reports = [], []
        for i, value in enumerate(modules):
            self.stack.enter_context(mock.patch.object(value, 'ROOT', self.root))
            pins = {'synthetic_historical_controller': i, 'scope_sha256': finite.PRIOR_SCOPE_SHA256}
            self.stack.enter_context(mock.patch.object(value, 'load_bundle', return_value=({}, {}, pins)))
            if i:
                self.stack.enter_context(mock.patch.object(value, 'module', return_value=modules[i-1]))
            run = self.root / 'delivery' / value.RUN_NAME
            run.mkdir()
            observation = {'client_started': True, 'native_process_reaped': True,
                           'thread_request_sent': False, 'model_turn_request_sent': False,
                           'model_turn_request_queued': False, 'verdict_submitted': False}
            session_raw = finite.exclusive_json(run / 'synthetic_SESSION.json', observation)
            report = {'kind': value.REPORT_KIND, 'pins': pins,
                      'status': 'STOPPED_WITHOUT_COMPLETED_REVIEW',
                      'unattended_model_use_authorized': False, 'parent_credential_contents_read': False,
                      'reviewer_output': None, 'preserved_session_receipts': [
                          {'path': 'synthetic_SESSION.json', 'sha256': finite.sha(session_raw)}],
                      'stages': [{'stage': 'synthetic', 'observation': observation}]}
            if i:
                report['prior_attempt'] = value.prior_failed_attempt()
            raw = finite.exclusive_json(run / 'REPORT.json', report)
            (run / 'REPORT.sha256').write_text(finite.sha(raw) + '\n')
            target = modules[i+1] if i < 2 else finite
            self.stack.enter_context(mock.patch.object(target, 'PRIOR_REPORT_SHA256', finite.sha(raw)))
            runs.append(run); reports.append(report)
        self.stack.enter_context(mock.patch.object(finite, 'module', return_value=modules[-1]))
        return modules, runs, reports

    def test_exact_three_receipt_chain_counts_and_scope_separation(self):
        _, runs, _ = self.fixture_chain()
        before = [{p.name: p.read_bytes() for p in r.iterdir()} for r in runs]
        receipt = finite.prior_failed_attempt()
        self.assertEqual(receipt['prior_failed_native_processes'], 3)
        self.assertEqual(receipt['prior_explicit_model_turns'], 0)
        self.assertEqual(receipt['new_invocation_native_processes_maximum'], 2)
        self.assertEqual(receipt['cumulative_native_processes_maximum_including_failed_attempts'], 5)
        self.assertEqual(receipt['cumulative_explicit_model_turns_maximum'], 2)
        self.assertEqual(receipt['access_scope_sha256'], finite.PRIOR_SCOPE_SHA256)
        self.assertEqual(receipt['proposed_access_scope_sha256'], finite.SCOPE_SHA256)
        self.assertEqual(before, [{p.name: p.read_bytes() for p in r.iterdir()} for r in runs])

    def test_any_prior_missing_or_changed_session_stops_without_creating_run(self):
        _, runs, _ = self.fixture_chain()
        for run in runs:
            for name in ('REPORT.json', 'REPORT.sha256', 'synthetic_SESSION.json'):
                with self.subTest(run=run.name, name=name):
                    path = run / name; raw = path.read_bytes()
                    path.write_bytes(raw + b'changed')
                    try:
                        with self.assertRaises(finite.Stop):
                            finite.prior_failed_attempt()
                        self.assertFalse((self.root / 'delivery' / finite.RUN_NAME).exists())
                    finally:
                        path.write_bytes(raw)

    def test_latest_prior_model_thread_science_or_wrong_scope_is_refused(self):
        _, runs, reports = self.fixture_chain()
        for field in ('model_turn_request_sent', 'model_turn_request_queued', 'thread_request_sent',
                      'verdict_submitted', 'native_process_reaped', 'science_stage', 'scope'):
            with self.subTest(field=field):
                report = copy.deepcopy(reports[-1])
                if field == 'science_stage': report['stages'].append({'stage': 'science'})
                elif field == 'scope': report['prior_attempt']['access_scope_sha256'] = finite.SCOPE_SHA256
                else: report['stages'][0]['observation'][field] = field != 'native_process_reaped'
                raw = (json.dumps(report) + '\n').encode()
                (runs[-1] / 'REPORT.json').write_bytes(raw)
                (runs[-1] / 'REPORT.sha256').write_text(finite.sha(raw) + '\n')
                with mock.patch.object(finite, 'PRIOR_REPORT_SHA256', finite.sha(raw)), \
                     self.assertRaises(finite.Stop):
                    finite.prior_failed_attempt()
                self.assertFalse((self.root / 'delivery' / finite.RUN_NAME).exists())

    def test_complete_receipt_reuse_is_read_only_before_any_new_approval_or_model(self):
        run = self.root / 'delivery' / finite.RUN_NAME; run.mkdir()
        report = {'kind': finite.REPORT_KIND, 'pins': self.pins,
                  'unattended_model_use_authorized': False, 'parent_credential_contents_read': False,
                  'reviewer_output': None, 'preserved_session_receipts': []}
        raw = finite.exclusive_json(run / 'REPORT.json', report)
        (run / 'REPORT.sha256').write_text(finite.sha(raw) + '\n')
        with mock.patch.object(finite, 'load_bundle', return_value=(self.scope, {}, self.pins)), \
             mock.patch.object(finite, 'canonical_host', side_effect=AssertionError('host queried')), \
             mock.patch.object(finite, 'approval', side_effect=AssertionError('approval queried')), \
             mock.patch.object(finite, 'prior_failed_attempt', side_effect=AssertionError('prior queried')), \
             mock.patch.object(finite, 'execute', side_effect=AssertionError('native started')), \
             mock.patch.object(sys, 'argv', ['p3_finite_review_022.py', '--run-attended-review']), \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(finite.main(), 0)
        self.assertEqual((run / 'REPORT.json').read_bytes(), raw)


class SessionIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old_fixture = load_file('sol022_source_origin_fixture', ROOT / 'tests/test_p3_reviewer_session_021.py')

    def invoke(self, *, response_model='gpt-5.6-sol', efforts=('high', 'max', 'ultra')):
        with mock.patch.object(self.old_fixture, 's', session):
            f = self.old_fixture.Fixture('success')
            try:
                path = f.root / 'fixture.json'
                native = json.loads(path.read_bytes())
                native['responses']['model/list']['data'] = [row(efforts=efforts)]
                native['thread']['model'] = response_model
                native['thread']['reasoningEffort'] = 'max'
                path.write_text(json.dumps(native))
                return f.invoke()
            finally:
                f.close()

    def test_literal_source_origins_sol_max_and_real_broker_synthetic_refusal(self):
        result = self.invoke()
        self.assertEqual(result['status'], 'SYNTHETIC_REFUSAL_OBSERVED')
        self.assertEqual(result['kind'], 'P3_FINITE_REVIEWER_SESSION_022_v1')
        self.assertEqual(result['selected_binding'],
                         {'model': 'gpt-5.6-sol', 'id': 'gpt-5.6-sol', 'effort': 'max'})
        self.assertTrue(result['model_turn_request_sent'])
        self.assertTrue(result['observed_refusal'])
        self.assertTrue(result['native_process_reaped'])
        self.assertNotIn('SECRET_DIAGNOSTIC_MUST_NOT_ESCAPE', json.dumps(result))

    def test_sol_without_max_stops_before_any_thread_or_model(self):
        result = self.invoke(efforts=('high', 'ultra'))
        self.assertEqual(result['status'], 'STOPPED_WITHOUT_VERDICT')
        self.assertFalse(result['thread_request_sent'])
        self.assertFalse(result['model_turn_request_sent'])
        self.assertFalse(result['model_turn_request_queued'])

    def test_server_model_substitution_stops_before_any_model_turn(self):
        result = self.invoke(response_model='gpt-6-astra')
        self.assertEqual(result['status'], 'STOPPED_WITHOUT_VERDICT')
        self.assertTrue(result['thread_request_sent'])
        self.assertFalse(result['model_turn_request_sent'])
        self.assertFalse(result['model_turn_request_queued'])


if __name__ == '__main__':
    unittest.main()
