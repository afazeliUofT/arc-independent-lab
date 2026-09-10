"""Actual frozen-broker fixtures for request refusal; no model/native launch."""
from pathlib import Path
import copy
import hashlib
import json
import os
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
import p3_review_interface_032 as interface
import test_p3_review_interface_028 as fixtures

original = interface.original
PATH_CASES = (
    ('pages/missing.png', 'resource_not_manifested'),
    ('pages/page0001.png', 'resource_not_manifested'),
    ('../outside.png', 'resource_path_traversal'),
    ('/tmp/outside.png', 'resource_path_absolute'),
    ('', 'resource_path_empty'),
    ('x' * 1025, 'resource_path_too_long'),
    ('pages\\page.png', 'resource_path_backslash'),
    ('pages/page\n.png', 'resource_path_control'),
    ('pages//page.png', 'resource_path_noncanonical'),
    ('./pages/page.png', 'resource_path_noncanonical'),
    (3, 'resource_path_type'),
)


class Interface032Tests(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.Fixture()

    def tearDown(self):
        self.f.close()

    def broker(self):
        return interface.ReviewBroker(self.f.packet, manifest_sha256=self.f.pin,
                                      output_root=self.f.output)

    def assert_correctable(self, tool, args, code):
        with self.broker() as broker:
            with self.assertRaises(interface.ToolInputError) as caught:
                broker.dispatch(tool, args)
            self.assertEqual(caught.exception.code, code)
            self.assertEqual(broker.recoverable_input_errors, 1)
            self.assertFalse(broker._failed)
            self.assertEqual(broker.dispatch('hash_file', {'path': 'CANARY.txt'})['sha256'],
                             self.f.files['CANARY.txt']['sha256'])
            self.assertFalse((self.f.output / original.VERDICT_NAME).exists())

    def test_all_path_classes_refused_without_open_and_corrected_call_succeeds(self):
        for path, code in PATH_CASES:
            with self.subTest(code=code), self.broker() as broker:
                reads = []
                actual_read = broker._original._read_raw
                def record(name):
                    reads.append(name)
                    return actual_read(name)
                with mock.patch.object(broker._original, '_read_raw', side_effect=record):
                    with self.assertRaises(interface.ToolInputError) as caught:
                        broker.dispatch('read_page_image', {'path': path})
                self.assertEqual(caught.exception.code, code)
                self.assertNotIn(path, reads)
                self.assertEqual(set(reads), set(self.f.files) | {'BROKER_MANIFEST.json'})
                self.assertFalse(broker._failed)
                self.assertEqual(broker.dispatch('read_page_image', {'path': 'pages/page.png'})['mimeType'],
                                 'image/png')
                summary = broker.resource_path_refusal_receipt()
                self.assertEqual(summary['calls_refused'], 1)
                self.assertEqual(summary['calls_by_category'][code], 1)
                self.assertEqual(summary['last_refusal'], caught.exception.as_dict()['resource_path_refusal'])
                self.assertFalse(summary['last_refusal']['denied_resource_opened'])
                self.assertTrue(summary['last_refusal']['full_packet_revalidated_before_feedback'])

    def test_traversal_has_actual_original_path_guard_as_immediate_cause(self):
        with self.broker() as broker:
            with self.assertRaises(interface.ToolInputError) as caught:
                broker.dispatch('read_text', {'path': '../OUTSIDE.txt', 'offset': 0, 'length': 1000})
            error = caught.exception
            self.assertEqual(error.code, 'resource_path_traversal')
            self.assertIsInstance(error.__cause__, original.BrokerError)
            self.assertEqual(str(error.__cause__), 'Noncanonical resource path')
            trace, frames = error.__cause__.__traceback__, []
            while trace is not None:
                frames.append(trace.tb_frame.f_code)
                trace = trace.tb_next
            self.assertIn(original._path.__code__, frames)
            self.assertNotIn(original.ReviewBroker._read_raw.__code__, frames)

    def test_canonical_unknown_has_original_manifest_refusal_cause(self):
        with self.broker() as broker:
            with self.assertRaises(interface.ToolInputError) as caught:
                broker.dispatch('hash_file', {'path': 'unknown.txt'})
            cause = caught.exception.__cause__
            self.assertIsInstance(cause, original.BrokerError)
            self.assertEqual(str(cause), 'Unmanifested resource denied')
            trace, frames = cause.__traceback__, []
            while trace is not None:
                frames.append(trace.tb_frame.f_code); trace = trace.tb_next
            self.assertIn(original.ReviewBroker._read.__code__, frames)
            self.assertNotIn(original.ReviewBroker._read_raw.__code__, frames)

    def test_no_normalization_or_read_fallback(self):
        for path in ('./CANARY.txt', 'folder/../CANARY.txt', 'CANARY.txt/', '/CANARY.txt'):
            with self.subTest(path=path), self.broker() as broker:
                with self.assertRaises(interface.ToolInputError):
                    broker.dispatch('hash_file', {'path': path})
                self.assertEqual(broker.recoverable_input_errors, 1)

    def test_original_accepted_unicode_and_del_are_not_newly_rejected(self):
        for path in ('notes/α.txt', 'notes/a\x7f.txt'):
            self.f.add(path, b'valid synthetic resource', 'text')
        self.f.freeze()
        with self.broker() as broker:
            for path in ('notes/α.txt', 'notes/a\x7f.txt'):
                self.assertEqual(broker.dispatch('hash_file', {'path': path})['sha256'],
                                 self.f.files[path]['sha256'])

    def test_known_wrong_kind_and_non_path_legacy_argument_errors_share_limit(self):
        self.assert_correctable('read_page_image', {'path': 'CANARY.txt'}, 'resource_kind')
        self.assert_correctable('read_text', {'path': 'CANARY.txt', 'offset': 0, 'length': 0}, 'integer_bounds')
        self.assert_correctable('read_text', {'path': 'CANARY.txt', 'offset': 10000, 'length': 10}, 'text_offset_past_end')
        self.assert_correctable('run_observer_audit', {'command': 'never executed'}, 'argument_fields')

    def test_eight_mixed_errors_ninth_stops_success_does_not_reset(self):
        with self.broker() as broker:
            for i in range(8):
                args = {'path': '../outside', 'offset': 0, 'length': 1} if i % 2 else {
                    'path': 'CANARY.txt', 'offset': 0, 'length': 0}
                with self.assertRaises(interface.ToolInputError):
                    broker.dispatch('read_text', args)
                broker.dispatch('hash_file', {'path': 'CANARY.txt'})
            self.assertEqual(broker.recoverable_input_errors, 8)
            self.assertEqual(broker.resource_path_refusal_receipt()['calls_refused'], 4)
            with self.assertRaisesRegex(original.BrokerError, 'ceiling'):
                broker.dispatch('read_page_image', {'path': 'missing.png'})
            self.assertTrue(broker._failed)
            self.assertEqual(broker.resource_path_refusal_receipt()['calls_refused'], 4)
            with self.assertRaises(original.BrokerError):
                broker.dispatch('hash_file', {'path': 'CANARY.txt'})
            with self.assertRaises(AttributeError):
                broker._failed = False

    def test_invalid_path_cannot_hide_unrelated_changed_bytes(self):
        for path, code in PATH_CASES:
            fresh = fixtures.Fixture()
            try:
                with interface.ReviewBroker(fresh.packet, manifest_sha256=fresh.pin, output_root=fresh.output) as broker:
                    (fresh.packet / 'papers/full.pdf').write_bytes(b'mutated')
                    with self.assertRaises(original.BrokerError) as caught:
                        broker.dispatch('read_page_image', {'path': path})
                    self.assertEqual(interface.classify_broker_failure(caught.exception), 'integrity.resource')
                    self.assertTrue(broker._failed)
                    self.assertEqual(broker.recoverable_input_errors, 0)
                    self.assertEqual(broker.resource_path_refusal_receipt()['calls_refused'], 0)
            finally:
                fresh.close()

    def test_mutation_between_path_denial_and_feedback_is_fatal(self):
        with self.broker() as broker:
            checked = broker._check_paths
            def mutate_after_denial(tool, args):
                try:
                    return checked(tool, args)
                except interface.ToolInputError:
                    (self.f.packet / 'CANARY.txt').write_bytes(b'mutated')
                    raise
            with mock.patch.object(broker, '_check_paths', side_effect=mutate_after_denial):
                with self.assertRaises(original.BrokerError):
                    broker.dispatch('read_page_image', {'path': 'missing.png'})
            self.assertTrue(broker._failed)
            self.assertEqual(broker.recoverable_input_errors, 0)

    def test_existing_unknown_and_known_requests_both_respect_actual_integrity_failures(self):
        for requested in ('missing.png', 'pages/page.png'):
            for change in ('removed', 'replaced_same_bytes', 'symlink', 'hardlink'):
                fresh = fixtures.Fixture()
                try:
                    with interface.ReviewBroker(fresh.packet, manifest_sha256=fresh.pin, output_root=fresh.output) as broker:
                        target = fresh.packet / 'pages/page.png'
                        saved = target.read_bytes()
                        if change == 'removed':
                            target.unlink()
                        elif change == 'replaced_same_bytes':
                            target.unlink(); target.write_bytes(saved)
                        elif change == 'symlink':
                            other = fresh.root / 'outside.png'; other.write_bytes(saved)
                            target.unlink(); target.symlink_to(other)
                        else:
                            os.link(target, fresh.root / 'outside.png')
                        with self.assertRaises(original.BrokerError) as caught:
                            broker.dispatch('read_page_image', {'path': requested})
                        self.assertEqual(interface.classify_broker_failure(caught.exception), 'integrity.resource')
                        self.assertTrue(broker._failed)
                        self.assertEqual(broker.recoverable_input_errors, 0)
                finally:
                    fresh.close()

    def test_manifest_digest_change_remains_fatal_even_for_traversal(self):
        with self.broker() as broker:
            path = self.f.packet / 'BROKER_MANIFEST.json'
            path.write_bytes(path.read_bytes() + b' ')
            with self.assertRaises(original.BrokerError):
                broker.dispatch('read_page_image', {'path': '../outside'})
            self.assertTrue(broker._failed)
            self.assertEqual(broker.recoverable_input_errors, 0)

    def test_known_malformed_png_is_format_failure(self):
        self.f.add('pages/bad.png', b'not a png', 'image'); self.f.freeze()
        with self.broker() as broker:
            with self.assertRaises(original.BrokerError) as caught:
                broker.dispatch('read_page_image', {'path': 'pages/bad.png'})
            self.assertEqual(interface.classify_broker_failure(caught.exception), 'integrity.packet_format')
            self.assertTrue(broker._failed)

    def test_valid_known_call_still_performs_original_two_corpus_passes(self):
        with self.broker() as broker:
            with mock.patch.object(broker._original, 'verify_inputs', wraps=broker._original.verify_inputs) as verify:
                broker.dispatch('read_page_image', {'path': 'pages/page.png'})
                self.assertEqual(verify.call_count, 2)
                verify.reset_mock()
                with self.assertRaises(interface.ToolInputError):
                    broker.dispatch('read_page_image', {'path': 'missing.png'})
                self.assertEqual(verify.call_count, 1)
            self.assertEqual(broker._request_reads, {})

    def test_unknown_operation_is_terminal_without_process(self):
        with self.broker() as broker, mock.patch.object(original.subprocess, 'run') as runner:
            with self.assertRaises(original.BrokerError) as caught:
                broker.dispatch('exec', {'path': '../outside'})
            self.assertEqual(interface.classify_broker_failure(caught.exception), 'boundary.unknown_operation')
            self.assertTrue(broker._failed)
            self.assertEqual(broker.recoverable_input_errors, 0)
            runner.assert_not_called()

    def test_path_denial_is_checked_even_with_extra_keys_and_bad_shape(self):
        self.assert_correctable('read_text', {'path': '../outside', 'offset': -1, 'length': 0, 'extra': True},
                                'resource_path_traversal')

    def test_verdict_unknown_reference_is_correctable_with_no_output(self):
        payload = self.f.verdict()
        payload['dispositions'][0]['evidence'][0]['path'] = 'unknown.txt'
        self.assert_correctable('submit_verdict', payload, 'resource_not_manifested')

    def test_bad_path_cannot_hide_false_known_evidence_digest_any_order(self):
        for reversed_order in (False, True):
            payload = self.f.verdict()
            refs = [{'path': '../outside', 'sha256': '0' * 64},
                    {'path': 'CANARY.txt', 'sha256': '0' * 64}]
            if reversed_order:
                refs.reverse()
            payload['dispositions'][0]['evidence'] = refs
            with self.broker() as broker:
                with self.assertRaises(original.BrokerError) as caught:
                    broker.dispatch('submit_verdict', payload)
                self.assertEqual(interface.classify_broker_failure(caught.exception), 'integrity.claimed_sha256')
                self.assertTrue(broker._failed)
                self.assertEqual(broker.recoverable_input_errors, 0)

    def test_bad_path_cannot_hide_false_scope_manifest_digest(self):
        payload = self.f.verdict()
        payload['dispositions'][0]['evidence'][0]['path'] = 'unknown.txt'
        payload['applies_to']['original_manifest_sha256'] = '0' * 64
        with self.broker() as broker:
            with self.assertRaises(original.BrokerError) as caught:
                broker.dispatch('submit_verdict', payload)
            self.assertEqual(interface.classify_broker_failure(caught.exception), 'integrity.claimed_sha256')
            self.assertTrue(broker._failed)
            self.assertEqual(broker.recoverable_input_errors, 0)

    def test_shape_error_after_valid_verifiable_claims_is_correctable(self):
        payload = self.f.verdict(); payload['summary'] = ''
        self.assert_correctable('submit_verdict', payload, 'bounded_text')

    def test_corrected_verdict_is_unchanged_and_exclusive(self):
        payload = self.f.verdict()
        bad = copy.deepcopy(payload)
        bad['dispositions'][0]['evidence'][0]['path'] = 'missing.txt'
        with self.broker() as broker:
            with self.assertRaises(interface.ToolInputError):
                broker.dispatch('submit_verdict', bad)
            broker.dispatch('submit_verdict', payload)
            actual = json.loads((self.f.output / original.VERDICT_NAME).read_bytes())
            self.assertEqual(actual['reviewer_verdict'], payload)
            with self.assertRaises(original.BrokerError):
                broker.dispatch('submit_verdict', payload)

    def test_refusal_metadata_is_copy_and_contains_no_raw_path(self):
        secret = 'private-synthetic-marker-91e345.png'
        with self.broker() as broker:
            with self.assertRaises(interface.ToolInputError) as caught:
                broker.dispatch('read_page_image', {'path': secret})
            snapshot = broker.resource_path_refusal_receipt()
            snapshot['last_refusal']['category'] = 'changed outside'
            self.assertEqual(broker.resource_path_refusal_receipt()['last_refusal']['category'], 'resource_not_manifested')
            encoded = json.dumps([broker.resource_path_refusal_receipt(), caught.exception.as_dict()])
            self.assertNotIn(secret, encoded)
            self.assertNotIn(hashlib.sha256(secret.encode()).hexdigest(), encoded)
            for code in interface.INPUT_INSTRUCTIONS:
                self.assertEqual(interface.ToolInputError(code).as_dict()['code'], code)
            with self.assertRaises(original.BrokerError):
                interface.ToolInputError('untrusted_unknown_category')

    def test_tool_schema_and_original_authority_fields_are_unchanged(self):
        before = interface.prior.dynamic_tool_specs()
        after = interface.dynamic_tool_specs()
        self.assertEqual(len(before), len(after))
        for old, new in zip(before, after):
            self.assertEqual(old['inputSchema'], new['inputSchema'])
            self.assertEqual(old['name'], new['name'])
            self.assertIn('No denied path is normalized', new['description'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
