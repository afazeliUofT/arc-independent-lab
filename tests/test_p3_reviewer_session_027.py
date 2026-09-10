#!/usr/bin/env python3
"""Offline transport tests: fixed Python pipe fixtures and unchanged real broker.

No native Codex binary, auth file, network, science packet or model is used.
A synthetic dependency-verdict fixture tests output transport only; it is not
an independent review or a scientific verdict, and its temporary file is removed.
"""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
import p3_reviewer_session_027 as session
import test_p3_deprecation_correction_024 as fixtures
import test_p3_warning_session_026 as transport_fixture

CANARY = 'UNKNOWN_WARNING_PRIVATE_027_89cf71'
REPORTS = []
BINDING = {'model': 'gpt-5.6-sol', 'id': 'gpt-5.6-sol', 'effort': 'max'}


def warning(text=None, thread='thread-test', **extra):
    return {'method': 'warning', 'params': {'threadId': thread,
        'message': session.disabled_codemode_notice.EXACT_MESSAGE if text is None else text}, **extra}


class SessionTests(unittest.TestCase):
    setUp = fixtures.SessionTests.setUp
    tearDown = fixtures.SessionTests.tearDown

    def run_fixture(self, mode='synthetic', expected_binding=None, *, verdict_expected=False):
        source = self.root / 'offline_responder_027.py'
        source.write_text(transport_fixture.CHILD)
        fixture = self.root / 'fixture_027.json'
        fixture.write_text(json.dumps(self.fixture))
        with session.broker_module.ReviewBroker(self.packet,
                manifest_sha256=self.manifest_sha, output_root=self.output) as broker:
            report = session.run_session({'argv': [sys.executable, '-I', '-B', str(source), str(fixture)]},
                self.run, self.requested, broker, mode=mode, prompt='synthetic prompt',
                wall_seconds=10, max_calls=3, expected_binding=expected_binding)
        if report['client_started']:
            self.assertTrue(report['native_process_reaped'])
        self.assertEqual(report['verdict_submitted'], verdict_expected)
        if not verdict_expected:
            self.assertEqual(list(self.output.iterdir()), [])
        for secret in (CANARY, session.disabled_codemode_notice.EXACT_MESSAGE):
            self.assertNotIn(secret, json.dumps(report))
            self.assertNotIn(hashlib.sha256(secret.encode()).hexdigest(), json.dumps(report))
        self.assertFalse(report['startup_completion_barrier_claimed'])
        self.assertFalse(report['native_tool_inventory_attested'])
        self.assertFalse(report['disabled_codemode_notice_policy']['direct_broker_route_proven_by_notice'])
        REPORTS.append({'test': self.id(), 'engineering_fixture_only': True, 'observation': report})
        return report

    def assert_refusal(self, report):
        self.assertEqual(report['status'], 'SYNTHETIC_REFUSAL_OBSERVED', report.get('reason'))
        self.assertTrue(report['synthetic_allowed_read_observed'])
        self.assertTrue(report['observed_refusal'])
        self.assertEqual(report['server_requests_dispatched'], 1)
        self.assertEqual(report['requests_sent'].count('turn/start'), 1)
        self.assertEqual(report['warning_diagnostics'], [])

    def assert_warning_stop(self, report, *, turn_sent=True):
        self.assertEqual(report['status'], 'STOPPED_WITHOUT_VERDICT')
        self.assertEqual(report['reason'],
            'Disabled Code Mode warning admission refused; safe classification preserved')
        self.assertFalse(report['observed_refusal'])
        self.assertEqual(report['server_requests_dispatched'], 0)
        self.assertEqual(report['model_turn_request_sent'], turn_sent)
        self.assertEqual(len(report['warning_diagnostics']), 1)
        self.assertFalse(report['disabled_codemode_notices'][-1]['admitted'])
        self.assertEqual(report['warning_diagnostics'][0]['action'], 'stop')

    def test_exact_warning_before_turn_response_then_real_positive_and_denial(self):
        self.fixture['before']['turn/start'].append(warning())
        report = self.run_fixture()
        self.assert_refusal(report)
        self.assertEqual(len(report['deprecation_notices']), 8)
        self.assertTrue(report['disabled_codemode_notices'][0]['admitted'])
        self.assertEqual(report['notifications']['warning'], 1)

    def test_exact_warning_after_turn_response_before_turn_started(self):
        self.fixture['after']['turn/start'].insert(0, warning())
        self.assert_refusal(self.run_fixture())

    def test_exact_warning_after_thread_status_and_turn_started_stays_bound(self):
        self.fixture['after']['turn/start'][:0] = [
            {'method': 'thread/status/changed', 'params': {'threadId': 'thread-test',
                'status': {'type': 'active'}}},
            {'method': 'turn/started', 'params': {'threadId': 'thread-test',
                'turn': {'id': 'turn-test', 'items': [], 'status': 'inProgress'}}}, warning()]
        report = self.run_fixture()
        self.assert_refusal(report)
        self.assertFalse(report['deprecation_notice_policy']['startup_window_open'])

    def test_no_warning_preserves_prior_canary_and_deprecation_flow(self):
        report = self.run_fixture()
        self.assert_refusal(report)
        self.assertEqual(report['disabled_codemode_notices'], [])
        self.assertTrue(all(row['admitted'] for row in report['deprecation_notices']))

    def test_changed_reason_fallback_suffix_and_unknown_warning_stop(self):
        base = copy.deepcopy(self.fixture)
        for text in (CANARY, session.disabled_codemode_notice.EXACT_MESSAGE.replace(
                'code-mode host is disabled', CANARY),
                session.disabled_codemode_notice.EXACT_MESSAGE.replace(
                'Code mode will fail closed', 'Falling back to direct tools')):
            self.fixture = copy.deepcopy(base)
            self.fixture['before']['turn/start'].append(warning(text))
            self.assert_warning_stop(self.run_fixture())

    def test_duplicate_exact_warning_stops_before_broker(self):
        self.fixture['before']['turn/start'] += [warning(), warning()]
        report = self.run_fixture()
        self.assert_warning_stop(report)
        self.assertTrue(report['disabled_codemode_notices'][0]['admitted'])
        self.assertEqual(report['disabled_codemode_notices'][1]['decision'],
            'repeated_notice_or_invalid_history')

    def test_foreign_thread_warning_stops_before_broker(self):
        self.fixture['before']['turn/start'].append(warning(thread=CANARY))
        self.assert_warning_stop(self.run_fixture())

    def test_warning_before_thread_binding_or_before_turn_sent_stops(self):
        base = copy.deepcopy(self.fixture)
        for position in ('before', 'after'):
            self.fixture = copy.deepcopy(base)
            self.fixture[position]['thread/start'] = [warning()]
            report = self.run_fixture()
            self.assert_warning_stop(report, turn_sent=False)
            self.assertFalse(report['model_turn_request_queued'])

    def test_invalid_envelope_or_parameters_fail_without_raw_echo(self):
        base = copy.deepcopy(self.fixture)
        for message in (warning(emittedAtMs=True), warning(id=1000), warning(**{CANARY: CANARY}),
                {'method': 'warning', 'params': None},
                {'method': 'warning', 'params': {'message': CANARY, 'threadId': 'thread-test', CANARY: CANARY}}):
            self.fixture = copy.deepcopy(base)
            self.fixture['before']['turn/start'].append(message)
            self.assert_warning_stop(self.run_fixture())

    def test_tampered_literal_boolean_effective_receipt_stops_warning_admission(self):
        original = session.admission.validate_effective_config
        def tampered(*args):
            receipt = original(*args)
            receipt['controls']['features.code_mode_host'] = 1
            return receipt
        self.fixture['before']['turn/start'].append(warning())
        with mock.patch.object(session.admission, 'validate_effective_config', side_effect=tampered):
            report = self.run_fixture()
        self.assert_warning_stop(report)
        self.assertEqual(report['disabled_codemode_notices'][-1]['decision'],
                         'restrictive_profile_not_admitted')

    def test_changed_native_host_control_stops_before_thread_and_turn(self):
        self.fixture['results']['config/read']['config']['features']['code_mode_host'] = True
        self.fixture['before']['turn/start'].append(warning())
        report = self.run_fixture()
        self.assertFalse(report['thread_request_sent'])
        self.assertFalse(report['model_turn_request_sent'])
        self.assertEqual(report['disabled_codemode_notices'], [])

    def test_changed_model_or_effort_cannot_reach_warning_admission(self):
        base = copy.deepcopy(self.fixture)
        for key, value in (('model', 'other-model'), ('reasoningEffort', 'ultra')):
            self.fixture = copy.deepcopy(base)
            self.fixture['results']['thread/start'][key] = value
            report = self.run_fixture()
            self.assertFalse(report['model_turn_request_sent'])
            self.assertEqual(report['disabled_codemode_notices'], [])

    def test_unknown_native_effect_after_exact_notice_still_stops(self):
        self.fixture['before']['turn/start'].append(warning())
        self.fixture['after']['turn/start'].insert(0, {'method': 'item/started', 'params': {
            'threadId': 'thread-test', 'turnId': 'turn-test',
            'item': {'id': 'item-test', 'type': 'commandExecution'}}})
        report = self.run_fixture()
        self.assertEqual(report['status'], 'STOPPED_WITHOUT_VERDICT')
        self.assertEqual(report['reason'], 'Unadvertised native item effect')
        self.assertEqual(report['server_requests_dispatched'], 0)

    def test_science_requires_synthetic_binding_before_process_start(self):
        with mock.patch.object(session.subprocess, 'Popen',
                side_effect=AssertionError('Must not launch')) as popen:
            report = self.run_fixture(mode='science')
        popen.assert_not_called()
        self.assertFalse(report['client_started'])
        self.assertEqual(report['reason'], 'Science requires the accepted synthetic model binding')

    def test_science_unknown_warning_stops_without_verdict(self):
        self.fixture['before']['turn/start'].append(warning(CANARY))
        report = self.run_fixture(mode='science', expected_binding=BINDING)
        self.assert_warning_stop(report)

    def test_science_synthetic_binding_mismatch_stops_before_thread(self):
        report = self.run_fixture(mode='science', expected_binding={**BINDING, 'effort': 'ultra'})
        self.assertFalse(report['thread_request_sent'])
        self.assertFalse(report['model_turn_request_sent'])

    def test_science_transport_writes_unmodified_exclusive_synthetic_dependency_verdict(self):
        # Only generated engineering text is added to this temporary fixture.
        manifest = json.loads((self.packet / 'BROKER_MANIFEST.json').read_bytes())
        hashes = {}
        for name, path in session.broker_module.REVIEW_MANIFESTS.items():
            data = b'{"scope":"SYNTHETIC ENGINEERING FIXTURE ONLY"}\n'
            target = self.packet / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            hashes[name] = hashlib.sha256(data).hexdigest()
            manifest['files'].append({'path': path, 'sha256': hashes[name], 'kind': 'text'})
        raw = json.dumps(manifest).encode()
        (self.packet / 'BROKER_MANIFEST.json').write_bytes(raw)
        self.manifest_sha = hashlib.sha256(raw).hexdigest()
        verdict = {'verdict': 'SUSPEND_FOR_DEPENDENCY',
            'applies_to': {'scope': 'SYNTHETIC ENGINEERING FIXTURE ONLY', **hashes},
            'summary': 'Synthetic transport fixture; no independent scientific review.',
            'dispositions': [{'subject': subject, 'disposition': 'synthetic dependency',
                'reason': 'No scientific model called.', 'evidence': [{'path': 'CANARY.txt',
                'sha256': manifest['files'][0]['sha256']}]} for subject in session.broker_module.SUBJECTS],
            'strongest_objections': [], 'missing_dependencies': ['Synthetic fixture only'],
            'required_corrections': []}
        call = fixtures.tool_call(101, verdict)
        call['params']['tool'] = 'submit_verdict'
        self.fixture['before']['turn/start'].append(warning())
        self.fixture['after']['turn/start'] = [call]
        self.fixture['after_read'] = []
        report = self.run_fixture(mode='science', expected_binding=BINDING, verdict_expected=True)
        self.assertEqual(report['status'], 'VERDICT_SUBMITTED')
        path = self.output / session.broker_module.VERDICT_NAME
        self.assertEqual(json.loads(path.read_bytes())['reviewer_verdict'], verdict)
        self.assertEqual(path.stat().st_mode & 0o777, 0o400)
        self.assertTrue(report['disabled_codemode_notices'][0]['admitted'])


if __name__ == '__main__':
    unittest.main()
