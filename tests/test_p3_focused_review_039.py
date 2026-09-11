"""Offline boundary/receipt tests. No native client or model is launched."""
from __future__ import annotations
import ast
import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('focused_controller039_test', ROOT / 'scripts/p3_focused_review_039.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


class ControllerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scope, cls.prior, cls.pins = c.load_bundle()
        cls.session = c.module('p3_reviewer_session_039')
        cls.broker = c.module('p3_focused_review_broker_039')
        cls.protocol = c.module('p3_focused_review_protocol_039')

    def test_native_session_source_retains_transport_exactly(self):
        old = (ROOT / 'scripts/p3_reviewer_session_032.py').read_text()
        expected = old.replace('broker_module = _module("p3_review_interface_032")',
            'broker_module = _module("p3_focused_review_broker_039")').replace(
            'protocol = _module("p3_review_protocol_032")',
            'protocol = _module("p3_focused_review_protocol_039")').replace(
            'receipt_contract = _module("p3_receipt_collection_032")\nSESSION_KIND = receipt_contract.SESSION_KIND',
            'SESSION_KIND = "P3_FINITE_REVIEWER_SESSION_039_v1"')
        self.assertEqual((ROOT / 'scripts/p3_reviewer_session_039.py').read_text(), expected)

    def test_real_successor_protocol_canary_recovery_and_denial(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            packet, digest = c.synthetic_packet(root)
            out = root / 'out'; out.mkdir()
            with self.broker.ReviewBroker(packet, manifest_sha256=digest, output_root=out, synthetic=True) as b:
                witness = self.session._BrokerWitness(b, 'synthetic', time.monotonic() + 60)
                boundary = self.protocol.DynamicToolBoundary(witness, thread_id='t', turn_id='u', max_calls=16, wall_seconds=60)
                for i, args in enumerate((self.session.SYNTHETIC_INVALID_READ, self.session.SYNTHETIC_READ, self.session.SYNTHETIC_FORBIDDEN),1):
                    message = {'id':i,'method':'item/tool/call','params':{'threadId':'t','turnId':'u','callId':str(i),'tool':'read_text','arguments':args}}
                    boundary.handle(json.dumps(message).encode())
                self.assertTrue(witness.argument_error_observed)
                self.assertTrue(witness.allowed_read)
                self.assertTrue(witness.observed_refusal)
                self.assertEqual(boundary.recoverable_input_errors, 2)
                self.assertEqual([(r['successful'],r['error_code']) for r in boundary.receipts],
                    [(False,'integer_bounds'),(True,None),(False,'resource_path_traversal')])
                self.assertFalse((out / 'REVIEW_VERDICT.json').exists())

    def test_refuses_scope_with_changed_pin_before_any_model(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / 'configs').mkdir()
            (root / c.SCOPE_PATH).write_text('{}\n')
            with patch.object(c,'ROOT',root), patch.object(c,'run_stage') as run:
                with self.assertRaisesRegex(c.Stop,'sealed release'):
                    c.load_bundle()
                run.assert_not_called()

    def test_protected_read_allows_access_time_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'text.txt';path.write_bytes(b'bounded original input')
            os.utime(path,ns=(1,path.stat().st_mtime_ns))
            self.assertEqual(c.bounded(path),b'bounded original input')

    def test_partial_directory_is_not_a_retry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); run=root/c.RUN_NAME; run.mkdir()
            c.exclusive_json(run/'ATTEMPT.json',{'partial':True})
            with patch.object(c,'run_stage') as stage:
                with self.assertRaisesRegex(c.Stop,'Partial039'):
                    c.existing(run, self.pins)
                stage.assert_not_called()

    def test_missing_session_usage_remains_a_lower_bound(self):
        counts=c.accounting({}, ['synthetic'])
        self.assertEqual(counts['cumulative_observed_native_starts'],14)
        self.assertEqual(counts['maximum_cumulative_reservation_native_starts'],16)
        self.assertEqual(counts['maximum_cumulative_reservation_turns'],13)
        self.assertTrue(counts['missing_session_counts_are_only_minimum_observations'])
        self.assertTrue(counts['unobserved_reserved_capacity_is_not_automatically_released'])

    def simulated_pipeline(self, fail=None):
        """Run actual controller/collector against explicitly synthetic receipts."""
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root=Path(temporary.name)
        for folder in ('delivery','scripts','state/authorizations'):
            (root/folder).mkdir(parents=True,exist_ok=True)
        for name in ('p3_reviewer_session_039.py','p3_receipt_collection_032.py'):
            shutil.copyfile(ROOT/'scripts'/name,root/'scripts'/name)
        authorization=self.scope['authorization']
        shutil.copyfile(ROOT/authorization['path'],root/authorization['path'])
        (root/'state/ESCALATION.md').write_bytes(b'')
        scope=copy.deepcopy(self.scope)
        scope.update(canonical_project=str(root),canonical_home=str(Path.home()))
        packet=root/scope['private_packet_directory'];packet.mkdir()
        packet_info={'packet_path':str(packet),'manifest_sha256':scope['private_packet_manifest_sha256'],'model_launched':False}
        calls=[]
        def stage(scope, prior, run, mode, packet, manifest_sha, expected_binding=None):
            calls.append((mode,Path(packet),copy.deepcopy(expected_binding)))
            obs={'kind':c.SESSION_KIND,'mode':mode,'selected_binding':c.BINDING.copy(),
                 'cache_input_descriptors_verified':True,'client_started':True,
                 'model_turn_request_sent':True,'native_process_reaped':True,
                 'synthetic_allowed_read_observed':mode=='synthetic','observed_refusal':mode=='synthetic',
                 'synthetic_argument_error_observed':mode=='synthetic',
                 'verdict_submitted':mode=='science','status':'SYNTHETIC_REFUSAL_OBSERVED' if mode=='synthetic' else 'VERDICT_SUBMITTED',
                 'recoverable_input_errors':2 if mode=='synthetic' else 0,
                 'failed_broker_calls':2 if mode=='synthetic' else 0,'broker_boundary_failure':None,
                 'broker_receipts':[{'method':'item/tool/call','tool':'read_text','successful':ok,'error_code':error}
                     for ok,error in [(False,'integer_bounds'),(True,None),(False,'resource_path_traversal')]] if mode=='synthetic' else []}
            if fail==mode:
                obs.update(status='STOPPED_WITHOUT_VERDICT',verdict_submitted=False)
            before={'manifest_sha256':manifest_sha,'files_rehashed':1}
            value={'stage':mode,'observation':obs,'host_checks':{'all_noncredential_checks_pass':True},
                   'failures':[],'fresh_process_and_runtime_directories':True,'pi_conversation_imported':False,
                   'independent_packet_observer_opened_before_model':True,'packet_before':before,'packet_after':before}
            c.exclusive_json(run/(mode+'_SESSION.json'),obs)
            c.exclusive_json(run/(mode+'_STAGE.json'),value)
            if mode=='science' and fail!=mode:
                out=run/'science_output';out.mkdir()
                c.exclusive_json(out/'REVIEW_VERDICT.json',{'offline_fixture':True,'scientific_verdict':False})
            return value
        original_module=c.module
        collector_spec=importlib.util.spec_from_file_location('collector039_test',ROOT/'scripts/p3_receipt_collection_032.py')
        collector=importlib.util.module_from_spec(collector_spec);collector_spec.loader.exec_module(collector)
        with patch.object(c,'ROOT',root),patch.object(c,'module',side_effect=lambda n:collector if n=='p3_receipt_collection_032' else original_module(n)),\
             patch.object(c,'prior_history',return_value={'offline_fixture':True}),\
             patch.object(c,'packet_preflight',return_value=packet_info),\
             patch.object(c,'load_bundle',return_value=(scope,self.prior,self.pins)),\
             patch.object(c,'run_stage',side_effect=stage):
            report=c.execute(scope,self.prior,self.pins,packet)
            result=json.loads(report.read_text())
            repeat=c.existing(report.parent,self.pins)
            self.assertEqual(report,repeat)
        return calls,result,report

    def test_canary_failure_suppresses_science_and_reuses_report(self):
        calls,result,report=self.simulated_pipeline('synthetic')
        self.assertEqual([call[0] for call in calls],['synthetic'])
        self.assertFalse(result['science_started'])
        self.assertEqual(result['status'],'STOPPED_WITHOUT_COMPLETED_REVIEW')
        self.assertEqual(result['attempt_accounting']['cumulative_observed_native_starts'],15)
        self.assertEqual(result['attempt_accounting']['cumulative_observed_sent_turns'],12)

    def test_two_stage_fixture_has_fresh_packet_and_exact_accounting(self):
        calls,result,report=self.simulated_pipeline()
        self.assertEqual([call[0] for call in calls],['synthetic','science'])
        self.assertNotEqual(calls[0][1],calls[1][1])
        self.assertIsNone(calls[0][2])
        self.assertEqual(calls[1][2],c.BINDING)
        self.assertEqual(result['status'],'REVIEWER_OUTPUT_PRESERVED')
        self.assertEqual(result['attempt_accounting']['cumulative_observed_native_starts'],16)
        self.assertEqual(result['attempt_accounting']['cumulative_observed_sent_turns'],13)
        self.assertFalse(result['scientific_verdict_chosen_by_parent'])
        self.assertTrue(result['receipt_collection']['eligible_for_controller_admission_checks'])

    def test_science_failure_preserves_sent_turn_and_no_verdict(self):
        calls,result,report=self.simulated_pipeline('science')
        self.assertEqual(len(calls),2)
        self.assertEqual(result['status'],'STOPPED_WITHOUT_COMPLETED_REVIEW')
        self.assertEqual(result['attempt_accounting']['cumulative_observed_sent_turns'],13)
        self.assertIsNone(result['reviewer_output'])

if __name__=='__main__':
    unittest.main()
