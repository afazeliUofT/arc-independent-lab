"""Real Python transport/broker/observer/emitter/collector seam; no native model.

The only submitted verdict is a clearly labelled synthetic dependency fixture.
"""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
import p3_reviewer_session_032 as session
import p3_packet_observer_032 as observer
import p3_receipt_collection_032 as collector
import p3_stage_evidence_030 as evidence
import test_p3_lifecycle_030 as fixtures

REPORTS = []


class PipelineTests(unittest.TestCase):
    setUp = fixtures.TransportTests.setUp
    tearDown = fixtures.TransportTests.tearDown
    verdict_call = fixtures.TransportTests.verdict_call

    def execute(self, mode='science', mutate_after=False):
        if mode == 'science':
            # Use the real successful synthetic emitter first: the collector
            # accepts the ordered two-stage operation, never science alone.
            preceding = PipelineTests(methodName=self._testMethodName)
            preceding.setUp()
            try:
                preceding.calls(
                    fixtures.prior.fixtures.tool_call(101,session.SYNTHETIC_INVALID_READ),
                    fixtures.prior.fixtures.tool_call(102,session.SYNTHETIC_READ),
                    fixtures.prior.fixtures.tool_call(103,session.SYNTHETIC_FORBIDDEN))
                prior_observation, prior_stage, _ = preceding.execute(mode='synthetic')
                self.assertEqual(prior_observation['status'],'SYNTHETIC_REFUSAL_OBSERVED')
                for name in ('synthetic_SESSION.json','synthetic_STAGE.json'):
                    (self.run/name).write_bytes((preceding.run/name).read_bytes())
            finally:
                preceding.tearDown()
        child = self.root / 'pipeline_fixture032.py'
        child.write_text(fixtures.prior.CHILD)
        fixture = self.root / 'fixture032.json'
        fixture.write_text(json.dumps(self.fixture))
        caches = self.root / 'cache_home/.codex'
        caches.mkdir(parents=True)
        (caches / 'models_cache.json').write_bytes(b'{"synthetic":true}\n')
        observer_output = self.root / 'packet_observer'
        observer_output.mkdir()
        with session.cache_module.capture_cache_inputs(caches,
                auth_metadata={'device':0,'inode':0}) as cache_inputs:
            with session.broker_module.ReviewBroker(self.packet,
                    manifest_sha256=self.manifest_sha, output_root=self.output) as broker:
                with observer.PacketObserver(self.packet, manifest_sha256=self.manifest_sha,
                        output_root=observer_output) as watcher:
                    before = broker.verify_inputs()
                    self.assertEqual(before, watcher.before)
                    observation = session.run_session(
                        {'argv':[sys.executable,'-I','-B',str(child),str(fixture)]},
                        self.run,self.requested,broker,mode=mode,prompt='synthetic prompt',
                        wall_seconds=10,max_calls=16,
                        expected_binding=fixtures.prior.BINDING if mode=='science' else None,
                        cache_inputs=cache_inputs)
                    if mutate_after:
                        (self.packet / 'CANARY.txt').write_bytes(b'changed after fixture session')
                    stage = evidence.finalize_stage(self.run,mode,observation,
                        host_checks_call=lambda:{'all_noncredential_checks_pass':cache_inputs.verify()['all_inputs_intact']},
                        packet_check_call=watcher.verify,
                        base_fields={'packet_before':before,'fixture_only':True},
                        write_json=lambda p,v:p.write_bytes(collector.canonical(v)))
        result = collector.collect(self.run,
            emitter_path=ROOT/'scripts/p3_reviewer_session_032.py',
            emitter_sha256=hashlib.sha256((ROOT/'scripts/p3_reviewer_session_032.py').read_bytes()).hexdigest(),
            expected_kind=session.SESSION_KIND,
            expected_modes=('synthetic',) if mode=='synthetic' else ('synthetic','science'))
        self.assertEqual(observation['kind'],collector.SESSION_KIND)
        self.assertTrue(result['complete'],result['errors'])
        self.assertTrue(observation['native_process_reaped'])
        self.assertTrue(observation['cache_input_descriptors_verified'])
        self.assertEqual(observation,result['observations'][mode])
        REPORTS.append({'test':self.id(),'synthetic_python_transport_only':True,
            'native_codex_or_model_used':False,'session':observation,
            'packet_after':stage['packet_after'],'stage_failures':stage['failures'],
            'collector_complete':result['complete']})
        return observation,stage,result

    def calls(self, *calls):
        self.fixture['after']['turn/start']=[fixtures.dynamic(calls[0]),calls[0]]
        self.fixture['after_read']=[]
        self.fixture['after_response']={str(call['id']):[
            fixtures.dynamic(call,'completed'),*fixtures.compaction('after-'+str(call['id'])),
            fixtures.dynamic(calls[i+1]),calls[i+1]] for i,call in enumerate(calls[:-1])}

    def test_unknown_page_then_corrected_read_and_dependency_verdict_survive_compaction(self):
        bad=fixtures.prior.fixtures.tool_call(101,{'path':'pages/unlisted-page.png'})
        bad['params']['tool']='read_page_image'
        good=fixtures.prior.fixtures.tool_call(102,session.SYNTHETIC_READ)
        final=self.verdict_call(103)
        self.calls(bad,good,final)
        observation,stage,_=self.execute()
        self.assertEqual(observation['status'],'VERDICT_SUBMITTED',observation.get('reason'))
        self.assertEqual(observation['recoverable_input_errors'],1)
        self.assertIsNone(observation['broker_boundary_failure'])
        self.assertEqual(observation['native_item_lifecycle']['context_compactions_completed'],2)
        self.assertEqual(stage['packet_after'],stage['packet_before'])
        self.assertEqual(stage['failures'],[])
        self.assertTrue((self.output/'REVIEW_VERDICT.json').exists())

    def test_synthetic_real_path_refusal_returns_feedback_and_shared_schema_receipt(self):
        self.calls(fixtures.prior.fixtures.tool_call(101,session.SYNTHETIC_INVALID_READ),
            fixtures.prior.fixtures.tool_call(102,session.SYNTHETIC_READ),
            fixtures.prior.fixtures.tool_call(103,session.SYNTHETIC_FORBIDDEN))
        observation,stage,_=self.execute(mode='synthetic')
        self.assertEqual(observation['status'],'SYNTHETIC_REFUSAL_OBSERVED',observation.get('reason'))
        self.assertTrue(observation['observed_refusal'])
        self.assertTrue(observation['synthetic_argument_error_observed'])
        self.assertEqual(observation['recoverable_input_errors'],2)
        self.assertEqual(observation['failed_broker_calls'],2)
        self.assertIsNone(observation['broker_boundary_failure'])
        self.assertEqual(stage['packet_after'],stage['packet_before'])
        self.assertFalse((self.output/'REVIEW_VERDICT.json').exists())

    def test_failed_ninth_path_call_does_not_disable_separate_integrity_check(self):
        calls=[]
        for i in range(101,110):
            call=fixtures.prior.fixtures.tool_call(i,{'path':'pages/unknown.png'})
            call['params']['tool']='read_page_image';calls.append(call)
        self.calls(*calls)
        observation,stage,_=self.execute()
        self.assertEqual(observation['status'],'STOPPED_WITHOUT_VERDICT')
        self.assertEqual(observation['recoverable_input_errors'],8)
        self.assertEqual(observation['failed_broker_calls'],9)
        self.assertEqual(stage['packet_after'],stage['packet_before'])
        self.assertEqual(stage['failures'],[{'phase':'session','code':'required_outcome_not_observed'}])

    def test_integrity_observer_detects_mutation_after_terminal_operation(self):
        calls=[]
        for i in range(101,110):
            call=fixtures.prior.fixtures.tool_call(i,{'path':'pages/unknown.png'})
            call['params']['tool']='read_page_image';calls.append(call)
        self.calls(*calls)
        observation,stage,_=self.execute(mutate_after=True)
        self.assertEqual(stage['packet_after']['status'],'FAILED')
        self.assertEqual(stage['packet_after']['error_code'],'input_identity_changed')
        self.assertIn({'phase':'packet','code':'packet_receipts_differ'},stage['failures'])


if __name__=='__main__':
    unittest.main(verbosity=2)
