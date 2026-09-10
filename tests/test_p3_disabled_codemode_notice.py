#!/usr/bin/env python3
"""Pure adversarial warning admission tests; no native or model operations."""
import copy
import hashlib
import json
import re
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
import p3_disabled_codemode_notice as notice
import test_p3_deprecation_correction_024 as fixtures

CANARY = 'UNKNOWN_NATIVE_PAYLOAD_027_46d01b'


def context():
    requested = fixtures.restrictive_profile()
    effective = fixtures.session.admission.validate_effective_config(
        fixtures.effective_config(requested), requested)
    return dict(notification_envelope_valid=True, expected_thread_id='thread-test',
        requested=requested, effective_config=effective, profile_admitted=True,
        selected_binding={'model': 'gpt-5.6-sol', 'id': 'gpt-5.6-sol', 'effort': 'max'},
        model_turn_sent=True, previously_admitted=0)


class NoticeTests(unittest.TestCase):
    def classify(self, params=None, **changes):
        args = context()
        args.update(changes)
        result = notice.classify(params if params is not None else {
            'message': notice.EXACT_MESSAGE, 'threadId': 'thread-test'}, **args)
        serialized = json.dumps(result)
        for secret in (CANARY, notice.EXACT_MESSAGE, 'thread-test'):
            self.assertNotIn(secret, serialized)
            self.assertNotIn(hashlib.sha256(secret.encode()).hexdigest(), serialized)
        self.assertFalse(result['producer_identity_established'])
        self.assertFalse(result['native_tool_inventory_attested'])
        self.assertFalse(result['direct_broker_route_proven'])
        self.assertFalse(result['raw_content_saved_or_hashed'])
        return result

    def test_exact_message_is_composed_from_pinned_upstream_producers(self):
        paths = (
            ROOT / 'artifacts/P3_DIRECT_BROKER_SOURCE/20260910_027/source/codex-rs/code-mode/src/remote_session.rs',
            ROOT / 'artifacts/P3_WARNING_SOURCE/20260909_025/source/codex-rs/core/src/tools/code_mode/mod.rs',
        )
        provider, formatter = [path.read_text() for path in paths]
        self.assertEqual(hashlib.sha256(paths[0].read_bytes()).hexdigest(),
            '30f866ccc860e3f0185da4a1e4e040b0042e06a6fc31041e4227721cbb29e3ce')
        reason = re.search(r'impl CodeModeSessionProvider for DisabledCodeModeSessionProvider.*?'
                           r'Err\("([^"\n]+)"\.to_string\(\)\)', provider, re.S).group(1)
        behavior = re.search(r'ToolMode::CodeMode \| ToolMode::CodeModeOnly => "([^"\n]+)"', formatter).group(1)
        template = re.search(r'"(Code Mode is unavailable because [^"\n]+)"', formatter).group(1)
        self.assertEqual(notice.EXACT_MESSAGE, template.format(error=reason, behavior=behavior))

    def test_exact_notice_full_admitted_config_and_sol_max_only(self):
        self.assertTrue(self.classify()['admitted'])

    def test_full_exact_text_no_prefix_family_trim_fallback_or_reason_match(self):
        for text in (notice.EXACT_MESSAGE + ' ', ' ' + notice.EXACT_MESSAGE,
                notice.EXACT_MESSAGE.lower(), notice.EXACT_MESSAGE + CANARY,
                notice.EXACT_MESSAGE.replace('code-mode host is disabled', CANARY),
                notice.EXACT_MESSAGE.replace('Code mode will fail closed', 'Falling back to direct tools'),
                notice.EXACT_MESSAGE[:-1], CANARY):
            with self.subTest(case=text != CANARY):
                self.assertFalse(self.classify({'message': text, 'threadId': 'thread-test'})['admitted'])

    def test_malformed_parameters_and_unknown_fields_refused_without_echo(self):
        for params in ([], False, {'message': notice.EXACT_MESSAGE},
                {'message': 1, 'threadId': 'thread-test'},
                {'message': notice.EXACT_MESSAGE, 'threadId': None},
                {'message': notice.EXACT_MESSAGE, 'threadId': 'thread-test', CANARY: CANARY}):
            self.assertFalse(self.classify(params)['admitted'])
        self.assertFalse(notice.classify(None, **context())['admitted'])

    def test_unbound_or_foreign_thread_never_admitted(self):
        for thread in (None, '', 1, CANARY):
            self.assertFalse(self.classify(expected_thread_id=thread)['admitted'])
        self.assertFalse(self.classify({'message': notice.EXACT_MESSAGE, 'threadId': CANARY})['admitted'])

    def test_context_literal_booleans_required(self):
        for key in ('notification_envelope_valid', 'profile_admitted', 'model_turn_sent'):
            for value in (False, None, 0, 1, 'true', {}):
                self.assertFalse(self.classify(**{key: value})['admitted'])

    def test_every_effective_receipt_control_literal_true_exact_coverage(self):
        base = context()['effective_config']
        for key in base['controls']:
            for value in (False, None, 1, 'true'):
                effective = copy.deepcopy(base)
                effective['controls'][key] = value
                self.assertFalse(self.classify(effective_config=effective)['admitted'])
        for mutate in ('missing', 'additional', 'not_dictionary'):
            effective = copy.deepcopy(base)
            if mutate == 'missing':
                effective['controls'].pop(next(iter(effective['controls'])))
            elif mutate == 'additional':
                effective['controls'][CANARY] = True
            else:
                effective['controls'] = []
            self.assertFalse(self.classify(effective_config=effective)['admitted'])

    def test_all_effective_admission_flags_literal_true_and_no_failure(self):
        base = context()['effective_config']
        for key in notice.EFFECTIVE_TRUE_FIELDS:
            for value in (False, None, 1, 'true'):
                effective = copy.deepcopy(base)
                effective[key] = value
                self.assertFalse(self.classify(effective_config=effective)['admitted'])
        effective = copy.deepcopy(base)
        effective['first_failure'] = {'reason': CANARY}
        self.assertFalse(self.classify(effective_config=effective)['admitted'])

    def test_code_mode_exact_structured_false_and_functions_namespace_required(self):
        candidates = (False, 0, {}, {'enabled': 0, 'direct_only_tool_namespaces': ['functions']},
            {'enabled': False, 'direct_only_tool_namespaces': ('functions',)},
            {'enabled': False, 'direct_only_tool_namespaces': ['functions', 'shell']},
            {'enabled': False, 'direct_only_tool_namespaces': ['Functions']},
            {'enabled': False, 'direct_only_tool_namespaces': ['functions'], CANARY: False})
        for value in candidates:
            ctx = context()
            ctx['requested']['features.code_mode'] = value
            self.assertFalse(self.classify(**ctx)['admitted'])
        for key in ('features.code_mode_host', 'features.code_mode_only'):
            for value in (None, True, 0, 'false', {'enabled': False}):
                ctx = context()
                ctx['requested'][key] = value
                self.assertFalse(self.classify(**ctx)['admitted'])
            ctx = context()
            del ctx['requested'][key]
            del ctx['effective_config']['controls'][key]
            self.assertFalse(self.classify(**ctx)['admitted'])

    def test_conflicting_nested_control_never_admitted(self):
        for key in ('features.code_mode.enabled', 'features.code_mode_host.enabled'):
            ctx = context()
            ctx['requested'][key] = False
            ctx['effective_config']['controls'][key] = True
            self.assertFalse(self.classify(**ctx)['admitted'])

    def test_exact_sol_max_and_valid_identity_required(self):
        for binding in (None, {}, {'model': 'gpt-5.6-sol', 'id': 'gpt-5.6-sol', 'effort': 'ultra'},
                {'model': CANARY, 'id': 'gpt-5.6-sol', 'effort': 'max'},
                {'model': 'gpt-5.6-sol', 'id': None, 'effort': 'max'},
                {'model': 'gpt-5.6-sol', 'id': 'gpt-5.6-sol', 'effort': 'max', CANARY: CANARY}):
            self.assertFalse(self.classify(selected_binding=binding)['admitted'])

    def test_one_notice_and_literal_zero_history_required(self):
        for value in (1, 2, -1, False, True, None, 0.0, '0', []):
            self.assertFalse(self.classify(previously_admitted=value)['admitted'])


if __name__ == '__main__':
    unittest.main()
