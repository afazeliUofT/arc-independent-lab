"""Offline receipt-contract and partial-evidence checks; no native/model client."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('collector032_tested', ROOT / 'scripts/p3_receipt_collection_032.py')
c = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(c)


class CollectionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='receipt032_', dir=ROOT / 'delivery')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.run = self.root / 'run'
        self.run.mkdir()
        self.source = self.root / 'scripts/p3_reviewer_session_032.py'
        self.source.parent.mkdir()
        self.source.write_bytes(b'# Explicit synthetic source-binding fixture, not a native session.\n')
        self.binding = dict(emitter_path=self.source, emitter_sha256=c.sha(self.source.read_bytes()),
                            expected_kind=c.SESSION_KIND)
        self.observations = {}
        for mode in c.MODES:
            value = {'kind': c.SESSION_KIND, 'mode': mode, 'client_started': True,
                     'model_turn_request_sent': True, 'verdict_submitted': False,
                     'status': 'SYNTHETIC_REFUSAL_OBSERVED' if mode == 'synthetic' else 'STOPPED_WITHOUT_VERDICT',
                     'fixture_only': True}
            self.save_pair(mode, value)

    def save_pair(self, mode, observation):
        self.observations[mode] = copy.deepcopy(observation)
        (self.run / (mode + '_SESSION.json')).write_bytes(c.canonical(observation))
        (self.run / (mode + '_STAGE.json')).write_bytes(c.canonical({
            'stage': mode, 'observation': observation, 'failures': []}))

    def collect(self, **kwargs):
        with mock.patch.object(subprocess, 'Popen', side_effect=AssertionError('No child process permitted')):
            result = c.collect(self.run, **(self.binding | kwargs))
        self.assertFalse(result['execution_admission_evaluated'])
        self.assertFalse(result['original_receipts_changed'])
        self.assertFalse(result['missing_receipts_reconstructed'])
        self.assertFalse((self.run / 'REPORT.json').exists())
        return result

    def codes(self, value):
        return [e['code'] for e in value['errors']]

    def test_exact_pairs_collected_without_claiming_successful_scientific_outcome(self):
        before = {p.name: p.read_bytes() for p in self.run.iterdir()}
        result = self.collect()
        self.assertTrue(result['complete'])
        self.assertTrue(result['eligible_for_controller_admission_checks'])
        self.assertEqual(result['observations'], self.observations)
        self.assertEqual(result['observations']['science']['status'], 'STOPPED_WITHOUT_VERDICT')
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.run.iterdir()})

    def test_bad_kind_preserves_other_mode_and_original_hash(self):
        value = self.observations['synthetic'] | {'kind': 'PRIVATE_UNEXPECTED_KIND'}
        self.save_pair('synthetic', value)
        raw = (self.run / 'synthetic_SESSION.json').read_bytes()
        result = self.collect()
        self.assertEqual(set(result['observations']), {'science'})
        self.assertFalse(result['complete'])
        error = next(e for e in result['errors'] if e['code'] == 'session_kind_differs_from_bound_emitter')
        self.assertEqual(error['file']['sha256'], c.sha(raw))
        self.assertNotIn('PRIVATE_UNEXPECTED_KIND', json.dumps(result['errors']))

    def test_missing_kind_or_nonboolean_counters_are_integrity_errors(self):
        bad_cases = [({'kind': None}, 'session_kind_differs_from_bound_emitter'),
                     ({'client_started': 1}, 'actual_execution_counters_not_boolean'),
                     ({'model_turn_request_sent': None}, 'actual_execution_counters_not_boolean'),
                     ({'client_started': False, 'model_turn_request_sent': True}, 'sent_turn_without_client_start')]
        for changes, code in bad_cases:
            with self.subTest(changes=changes):
                self.save_pair('synthetic', self.observations['science'] | {'mode': 'synthetic'} | changes)
                result = self.collect()
                self.assertIn(code, self.codes(result))
                self.assertIn('science', result['observations'])

    def test_missing_session_retains_independent_stage_hash_and_other_mode(self):
        (self.run / 'synthetic_SESSION.json').unlink()
        result = self.collect()
        self.assertIn('missing_file', self.codes(result))
        self.assertIn('separate_session_not_validated', self.codes(result))
        self.assertIn('science', result['stages'])
        self.assertFalse((self.run / 'synthetic_SESSION.json').exists())

    def test_truncated_json_preserves_hash_and_other_mode(self):
        raw = b'{"private": "UNFINISHED'
        (self.run / 'synthetic_SESSION.json').write_bytes(raw)
        result = self.collect()
        self.assertIn('invalid_json', self.codes(result))
        record = next(r for r in result['files'] if r['path'] == 'synthetic_SESSION.json')
        self.assertEqual(record['sha256'], c.sha(raw))
        self.assertNotIn('UNFINISHED', json.dumps(result))
        self.assertIn('science', result['observations'])

    def test_duplicate_and_nonfinite_json_are_refused(self):
        for raw, code in ((b'{"a":1,"a":2}', 'duplicate_json_key'),
                          (b'{"a":NaN}', 'nonfinite_json')):
            with self.subTest(code=code):
                (self.run / 'synthetic_SESSION.json').write_bytes(raw)
                self.assertIn(code, self.codes(self.collect()))

    def test_oversized_file_refused_before_content_read(self):
        path = self.run / 'synthetic_SESSION.json'
        with path.open('wb') as handle:
            handle.truncate(c.RECEIPT_LIMIT_BYTES + 1)
        result = self.collect()
        self.assertIn('file_byte_limit_exceeded', self.codes(result))
        record = next(r for r in result['files'] if r['path'] == path.name)
        self.assertIsNone(record['sha256'])
        self.assertIn('science', result['observations'])

    def test_final_symlink_is_not_followed(self):
        sentinel = self.root / 'sentinel'
        sentinel.write_bytes(b'PRIVATE_SENTINEL')
        path = self.run / 'synthetic_SESSION.json'
        path.unlink()
        path.symlink_to(sentinel)
        result = self.collect()
        self.assertIn('not_regular_file', self.codes(result))
        self.assertNotIn('PRIVATE_SENTINEL', json.dumps(result))
        self.assertEqual(sentinel.read_bytes(), b'PRIVATE_SENTINEL')

    def test_ancestor_symlink_is_not_followed(self):
        alias = self.root / 'alias'
        alias.symlink_to(self.run, target_is_directory=True)
        result = c.collect(alias, **self.binding)
        self.assertEqual(result['observations'], {})
        self.assertEqual(len(result['errors']), 4)
        self.assertTrue(all(e['code'] == 'protected_path_read_failed' for e in result['errors']))

    def test_hardlink_and_writable_file_are_refused(self):
        path = self.run / 'synthetic_SESSION.json'
        alias = self.root / 'hardlink'
        os.link(path, alias)
        self.assertIn('multiple_hardlinks_refused', self.codes(self.collect()))
        alias.unlink()
        path.chmod(0o666)
        self.assertIn('group_or_world_writable_file', self.codes(self.collect()))

    def test_source_binding_mismatch_keeps_file_refs_but_trusts_no_observations(self):
        result = self.collect(emitter_sha256='0' * 64)
        self.assertIn('emitter_source_hash_differs', self.codes(result))
        self.assertEqual(result['observations'], {})
        self.assertTrue(all(r['sha256'] for r in result['files']))
        self.assertFalse(result['eligible_for_controller_admission_checks'])

    def test_stage_content_mismatch_does_not_destroy_valid_session(self):
        stage = json.loads((self.run / 'science_STAGE.json').read_bytes())
        stage['observation']['model_turn_request_sent'] = False
        (self.run / 'science_STAGE.json').write_bytes(c.canonical(stage))
        result = self.collect()
        self.assertIn('science', result['observations'])
        self.assertNotIn('science', result['stages'])
        self.assertIn('stage_observation_differs_from_original_session_bytes', self.codes(result))

    def test_no_attempted_modes_accepts_absence_and_refuses_unexpected_files(self):
        self.assertIn('unrequested_stage_receipt_present', self.codes(self.collect(expected_modes=())))
        for path in self.run.iterdir():
            path.unlink()
        result = self.collect(expected_modes=())
        self.assertTrue(result['complete'])
        self.assertEqual(result['observations'], {})

    def test_synthetic_only_attempt_does_not_expect_science_receipts(self):
        for suffix in ('SESSION', 'STAGE'):
            (self.run / ('science_' + suffix + '.json')).unlink()
        result = self.collect(expected_modes=('synthetic',))
        self.assertTrue(result['complete'])
        self.assertEqual(set(result['observations']), {'synthetic'})

    def test_os_read_failure_is_independent_and_safely_categorical(self):
        with mock.patch.object(c.os, 'read', side_effect=OSError('PRIVATE_RAW_EXCEPTION')):
            result = self.collect()
        self.assertIn('protected_path_read_failed', self.codes(result))
        self.assertNotIn('PRIVATE_RAW_EXCEPTION', json.dumps(result))


class RealEmitterContractTests(unittest.TestCase):
    def emitter_seam(self, version, bound_kind, wrong_kind):
        sys.path.insert(0, str(ROOT / 'scripts'))
        session = __import__('p3_reviewer_session_' + version)
        with tempfile.TemporaryDirectory(prefix='real_emitter032_', dir=ROOT / 'delivery') as temporary:
            run = Path(temporary)
            # A malformed cache object is rejected by the real emitter before
            # spawning. We keep its actual returned schema and counters intact.
            with mock.patch.object(session.subprocess, 'Popen', side_effect=AssertionError('Must not launch')):
                for mode in c.MODES:
                    observation = session.run_session({'argv': ['never-launched']}, run,
                        {}, None, mode=mode, prompt='Synthetic schema-contract fixture',
                        wall_seconds=5, max_calls=1,
                        expected_binding={'model': 'gpt-5.6-sol', 'id': 'gpt-5.6-sol', 'effort': 'max'},
                        cache_inputs=object())
                    self.assertFalse(observation['client_started'])
                    self.assertFalse(observation['model_turn_request_sent'])
                    (run / (mode + '_SESSION.json')).write_bytes(c.canonical(observation))
                    (run / (mode + '_STAGE.json')).write_bytes(c.canonical({
                        'stage': mode, 'observation': observation, 'failures': []}))
            source = ROOT / ('scripts/p3_reviewer_session_' + version + '.py')
            binding = dict(emitter_path=source, emitter_sha256=c.sha(source.read_bytes()),
                           expected_kind=bound_kind)
            accepted = c.collect(run, **binding)
            self.assertTrue(accepted['complete'], accepted['errors'])
            rejected = c.collect(run, **(binding | {'expected_kind': wrong_kind}))
            self.assertFalse(rejected['complete'])
            self.assertEqual(rejected['observations'], {})
            self.assertEqual(sum(e['code'] == 'session_kind_differs_from_bound_emitter'
                                 for e in rejected['errors']), 2)
            self.assertFalse((run / 'REPORT.json').exists())

    def test_real030_run_session_output_round_trips_only_with_its_explicit_bound_kind(self):
        self.emitter_seam('030', 'P3_FINITE_REVIEWER_SESSION_030_OFFLINE_PROPOSAL_v1',
                          'P3_FINITE_REVIEWER_SESSION_030_v1')

    def test_real032_run_session_uses_shared_kind_and_round_trips_without_rewriting(self):
        self.emitter_seam('032', c.SESSION_KIND,
                          'P3_FINITE_REVIEWER_SESSION_030_OFFLINE_PROPOSAL_v1')


if __name__ == '__main__':
    unittest.main()
