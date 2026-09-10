"""Synthetic engineering evidence only: no native client, credentials or model."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('stage030', ROOT / 'scripts/p3_stage_evidence_030.py')
stage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stage)


def signature(path):
    return {**stage.observe_path(path)['metadata'],
            'sha256': hashlib.sha256(Path(path).read_bytes()).hexdigest()}


class CacheFixture:
    def verify(self):
        return {'all_inputs_intact': True}

    def observe_sources(self):
        return [{'name': 'models_cache.json', 'changed_fields': ['mtime_ns'],
                 'source_unchanged': False, 'observation_succeeded': True},
                {'name': 'cloud-config-bundle-cache.json', 'changed_fields': [],
                 'source_unchanged': True, 'observation_succeeded': True}]


class StageEvidenceTests(unittest.TestCase):
    def setUp(self):
        (ROOT / 'delivery').mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix='stage030_', dir=ROOT / 'delivery')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ('runtime', 'bwrap', 'identity', 'private_identity', 'config', 'auth_fixture'):
            (self.root / name).write_bytes(b'synthetic fixture only')
        self.facts = {'auth': self.root / 'auth_fixture', 'origins': [],
                      'identifier_bytes': b'synthetic fixture only'}
        for key, name in (('runtime', 'runtime'), ('bwrap', 'bwrap'), ('identifier', 'identity')):
            self.facts[key] = self.root / name
            self.facts[key + '_before'] = signature(self.root / name)
        for name in ('config', 'auth_fixture'):
            self.facts['origins'].append({'path': str(self.root / name),
                                         **stage.observe_path(self.root / name)})
        self.preflight = types.SimpleNamespace(signature=signature)

    def collect(self, cache=None):
        return stage.collect_postchecks(self.facts, None, self.preflight,
                                        self.root / 'private_identity', cache or CacheFixture())

    def test_source_drift_is_separate_from_sealed_input_integrity(self):
        result = self.collect()
        self.assertTrue(result['all_noncredential_checks_pass'])
        self.assertFalse(result['cache_source_observations'][0]['source_unchanged'])
        self.assertFalse(result['cache_source_change_is_writer_attribution'])

    def test_all_changed_inputs_are_recorded(self):
        (self.root / 'config').write_bytes(b'changed')
        (self.root / 'runtime').write_bytes(b'changed')
        (self.root / 'private_identity').write_bytes(b'changed')
        result = self.collect()
        self.assertFalse(result['all_noncredential_checks_pass'])
        self.assertEqual({r['code'] for r in result['failures']},
                         {'config_metadata_unchanged', 'runtime_unchanged',
                          'private_installation_id_matches'})
        self.assertTrue(result['bwrap_unchanged'])
        self.assertTrue(result['credential_metadata_observed'])

    def test_postcheck_exceptions_do_not_short_circuit(self):
        cache = CacheFixture()
        def fail():
            raise OSError('SYNTHETIC_SECRET_DO_NOT_PRINT')
        cache.verify = fail
        cache.observe_sources = fail
        result = self.collect(cache)
        self.assertFalse(result['cache_inputs_intact'])
        self.assertTrue(result['runtime_unchanged'])
        self.assertTrue(result['credential_metadata_observed'])
        self.assertNotIn('SYNTHETIC_SECRET', json.dumps(result))
        self.assertEqual(len(result['failures']), 2)

    def test_parent_never_reads_credential_content(self):
        original = Path.read_bytes
        seen = []
        def guarded(path):
            seen.append(path)
            if path == self.facts['auth']:
                self.fail('Credential content accessed')
            return original(path)
        with patch.object(Path, 'read_bytes', guarded):
            result = self.collect()
        self.assertFalse(result['credential_contents_checked'])
        self.assertNotIn(self.facts['auth'], seen)

    def test_per_path_observation_failure_is_retained_and_refused(self):
        cache = CacheFixture()
        cache.observe_sources = lambda: [
            {'name': 'models_cache.json', 'observation_succeeded': False},
            {'name': 'cloud-config-bundle-cache.json', 'observation_succeeded': True}]
        result = self.collect(cache)
        self.assertFalse(result['all_noncredential_checks_pass'])
        self.assertTrue(result['cache_inputs_intact'])
        self.assertEqual(result['failures'][0]['code'], 'cache_source_observations_unavailable')

    def test_final_and_ancestor_symlinks_are_refused(self):
        (self.root / 'leaf').symlink_to(self.root / 'config')
        (self.root / 'alias').symlink_to(self.root, target_is_directory=True)
        for path in (self.root / 'leaf', self.root / 'alias/config'):
            with self.assertRaises((ValueError, OSError)):
                stage.observe_path(path)

    def test_every_configuration_comparison_survives_one_error(self):
        (self.root / 'config').unlink()
        (self.root / 'config').symlink_to(self.root / 'runtime')
        self.facts['origins'].append({'path': str(self.root / 'bwrap'),
                                      **stage.observe_path(self.root / 'bwrap')})
        result = self.collect()
        self.assertEqual(len(result['config_comparisons']), 2)
        self.assertFalse(result['config_comparisons'][0]['observed'])
        self.assertTrue(result['config_comparisons'][1]['unchanged'])

    def finish(self, observation, host, packet, writer=None):
        if writer is None:
            def writer(path, value):
                with path.open('x') as stream:
                    json.dump(value, stream)
        return stage.finalize_stage(self.root, 'science', observation,
            host_checks_call=host, packet_check_call=packet,
            base_fields={'packet_before': {'intact': True}}, write_json=writer)

    def test_session_saved_before_independent_postchecks(self):
        observation = {'status': 'STOPPED_WITHOUT_VERDICT', 'native_process_reaped': True,
                       'primary_failure': 'native_item_refused', 'reason': 'later cleanup detail'}
        called = []
        def host():
            self.assertEqual(json.loads((self.root / 'science_SESSION.json').read_text()), observation)
            called.append('host')
            raise RuntimeError('SECRET host error')
        def packet():
            called.append('packet')
            raise RuntimeError('SECRET packet error')
        result = self.finish(observation, host, packet)
        self.assertEqual(called, ['host', 'packet'])
        self.assertEqual(result['primary_session_reason'], 'native_item_refused')
        self.assertEqual([r['phase'] for r in result['failures']], ['session', 'postcheck', 'packet'])
        self.assertNotIn('SECRET', json.dumps(result))
        self.assertEqual(json.loads((self.root / 'science_STAGE.json').read_text()), result)

    def test_receipt_write_failure_is_not_claimed_saved(self):
        seen = []
        def writer(path, value):
            raise OSError('fixture disk failure')
        with self.assertRaises(OSError):
            self.finish({}, lambda: seen.append('host'), lambda: seen.append('packet'), writer)
        self.assertEqual(seen, [])

    def test_failed_stage_write_preserves_session(self):
        def writer(path, value):
            if path.name.endswith('_STAGE.json'):
                raise OSError('fixture disk failure')
            path.write_text(json.dumps(value))
        observation = {'status': 'VERDICT_SUBMITTED', 'native_process_reaped': True}
        with self.assertRaises(OSError):
            self.finish(observation, lambda: self.collect(), lambda: {'intact': True}, writer)
        self.assertEqual(json.loads((self.root / 'science_SESSION.json').read_text()), observation)

    def test_success_does_not_select_scientific_content(self):
        observation = {'status': 'VERDICT_SUBMITTED', 'native_process_reaped': True}
        result = self.finish(observation, lambda: self.collect(), lambda: {'intact': True})
        self.assertEqual(result['observation'], observation)
        self.assertEqual(result['failures'], [])
        self.assertFalse((self.root / 'REVIEW_VERDICT.json').exists())

    def test_packet_change_and_cleanup_failure_both_survive(self):
        observation = {'status': 'STOPPED_WITHOUT_VERDICT', 'native_process_reaped': False,
                       'reason': 'first event failure'}
        result = self.finish(observation, lambda: self.collect(), lambda: {'intact': False})
        self.assertEqual({r['phase'] for r in result['failures']}, {'session', 'cleanup', 'packet'})
        self.assertEqual(result['primary_session_reason'], 'first event failure')


if __name__ == '__main__':
    unittest.main(verbosity=2)
