"""Offline controller tests: no native client, model, credential or Git execution.

Counter/admission fixtures are explicitly synthetic. Historical fixtures COPY
actual published030 receipt bytes; they never reconstruct missing030 REPORT.
"""
from contextlib import redirect_stdout
import copy
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

LAB = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('controller032_tested',LAB/'scripts/p3_finite_review_032.py')
c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)


def put(path,raw):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(raw)


class Controller032Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='controller032_fixture_',dir=LAB/'delivery')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.scope = json.loads((LAB/c.SCOPE_PATH).read_bytes())
        _,self.prior,inherited = c.previous.load_bundle()
        self.source_pins = dict(c.SOURCE_PINS)
        for name in self.source_pins:
            if (LAB/name).exists(): self.source_pins[name] = c.sha((LAB/name).read_bytes())
        self.pins = {'scope_sha256':c.SCOPE_SHA256,'controller_sha256':'fixture-controller',
            'source_pins':self.source_pins,'inherited030_pins':inherited,
            'actual030_file_pins':c.HISTORY_PINS,
            'packet_manifest_sha256':self.scope['private_packet_manifest_sha256']}
        self.original_module = c.module
        self.case = 0
        patch = mock.patch.object(subprocess,'Popen',side_effect=AssertionError('No native/model process in controller fixtures'))
        self.popen = patch.start(); self.addCleanup(patch.stop)

    def auth(self):
        return ('# Explicit offline fixture only\n\n## ANSWER\n'
            'APPROVE_P3_FINITE_REVIEW_032_CORRECTION\n'
            'scope_sha256: '+c.SCOPE_SHA256+'\n').encode()

    def history_fixture(self):
        for relative in c.HISTORY_PINS:
            raw = (LAB/c.HISTORY_ROOT/relative).read_bytes()
            put(self.root/'delivery'/relative,raw)
            put(self.root/c.HISTORY_ROOT/relative,raw)
        actual_attempt = json.loads((self.root/'delivery/P3_FINITE_REVIEW_030/ATTEMPT.json').read_bytes())
        self.pins['inherited030_pins'] = actual_attempt['pins']
        return self.root/'delivery/P3_FINITE_REVIEW_030'

    def history_call(self):
        with mock.patch.object(c,'ROOT',self.root),mock.patch.object(c.previous,'prior_history',return_value={'fixture_earlier_history':True}):
            return c.prior_history(self.pins)

    def observation(self,mode):
        return {'kind':c.SESSION_KIND,'mode':mode,'fixture_only':True,
            'client_started':True,'model_turn_request_sent':True,'native_process_reaped':True,
            'selected_binding':c.BINDING.copy(),'cache_input_descriptors_verified':True,
            'status':'SYNTHETIC_REFUSAL_OBSERVED' if mode=='synthetic' else 'VERDICT_SUBMITTED',
            'verdict_submitted':mode=='science','synthetic_argument_error_observed':mode=='synthetic',
            'synthetic_allowed_read_observed':mode=='synthetic','observed_refusal':mode=='synthetic',
            'recoverable_input_errors':2,'failed_broker_calls':2,'broker_boundary_failure':None,
            'broker_receipts':[{'method':'item/tool/call','tool':'read_text','successful':success,'error_code':code}
                for success,code in ((False,'integer_bounds'),(True,None),(False,'resource_path_traversal'))]}

    def execute_fixture(self,*,changes=None,changes_mode='synthetic',missing=None,malformed=None,
                        stage_error=None,error_mode='synthetic',verdict=True,
                        bundle_changed=False,packet_changed=False,collector_error=False,
                        history_error=False,preflight_error=False):
        self.case+=1
        root=self.root/('case_'+str(self.case)); (root/'delivery').mkdir(parents=True)
        put(root/'state/ESCALATION.md',self.auth())
        put(root/'scripts/p3_reviewer_session_032.py',(LAB/'scripts/p3_reviewer_session_032.py').read_bytes())
        auth={'path':'state/ESCALATION.md','sha256':c.sha(self.auth())}
        info={'packet_path':str(root/'delivery/private_fixture'),'manifest_sha256':self.pins['packet_manifest_sha256']}
        calls=[]
        def stage(scope,prior,run,mode,packet,manifest,expected_binding=None):
            calls.append(mode)
            observed=self.observation(mode)
            before={'manifest_sha256':manifest,'files_rehashed':1 if mode=='synthetic' else 722}
            result={'stage':mode,'observation':observed,'failures':[],
                'host_checks':{'all_noncredential_checks_pass':True},
                'fresh_process_and_runtime_directories':True,'pi_conversation_imported':False,
                'independent_packet_observer_opened_before_model':True,
                'packet_before':before,'packet_after':dict(before),'fixture_only':True}
            if mode==changes_mode:
                for key,value in (changes or {}).items():
                    if key=='host': result['host_checks']['all_noncredential_checks_pass']=value
                    elif key in ('failures','packet_after','independent_packet_observer_opened_before_model',
                                  'fresh_process_and_runtime_directories','pi_conversation_imported'):
                        result[key]=copy.deepcopy(value)
                    else: observed[key]=copy.deepcopy(value)
            for part in (mode+'_native',mode+'_output',mode+'_packet_observer'):(run/part).mkdir()
            if mode=='science' and verdict:put(run/'science_output/REVIEW_VERDICT.json',b'{"fixture_only":true}\n')
            for suffix,value in (('SESSION',observed),('STAGE',result)):
                filename=mode+'_'+suffix+'.json'
                if missing==filename:continue
                raw=b'{"truncated":' if malformed==filename else c.canonical(value)
                put(run/filename,raw)
            if mode==error_mode and stage_error is not None:raise stage_error
            return result
        installer=mock.Mock(); installer.verify_packet.return_value=copy.deepcopy(info)
        if packet_changed:installer.verify_packet.return_value['manifest_sha256']='0'*64
        def get_module(name):
            if name=='install_p3_review_packet':return installer
            if name=='p3_receipt_collection_032' and collector_error:
                return mock.Mock(collect=mock.Mock(side_effect=RuntimeError('PRIVATE_COLLECTOR_EXCEPTION')))
            return self.original_module(name)
        refreshed=(copy.deepcopy(self.scope),self.prior,self.pins)
        if bundle_changed:refreshed[0]['maximum_model_turns']=100
        history={'fixture_only':True,'kernel_prerequisite_reused_from_actual030':{'fixture_kernel':True}}
        with mock.patch.object(c,'ROOT',root),mock.patch.object(c,'SOURCE_PINS',self.source_pins),mock.patch.object(
                c,'prior_history',return_value=history,side_effect=c.Stop('Fixture history stopped') if history_error else None),mock.patch.object(
                c,'packet_preflight',return_value={'fixture_only':True},side_effect=c.Stop('Fixture preflight stopped') if preflight_error else None),mock.patch.object(
                c,'run_stage',side_effect=stage),mock.patch.object(c,'module',side_effect=get_module),mock.patch.object(c,'load_bundle',return_value=refreshed):
            if history_error or preflight_error:
                with self.assertRaises(c.Stop):c.execute(self.scope,self.prior,self.pins,auth,info)
                self.assertFalse((root/'delivery'/c.RUN_NAME).exists()); self.assertEqual(calls,[])
                return None,None,calls
            path=c.execute(self.scope,self.prior,self.pins,auth,info)
        self.popen.assert_not_called()
        return path,json.loads(path.read_bytes()),calls

    def reuse(self,path):
        with mock.patch.object(c,'ROOT',path.parents[2]),mock.patch.object(c,'SOURCE_PINS',self.source_pins):
            return c.existing(path.parent,self.pins)

    def test_exact_final_bundle_and_emitter_contract(self):
        scope,prior,pins=c.load_bundle()
        self.assertEqual(scope,self.scope); self.assertEqual(prior,self.prior)
        self.assertEqual(pins['source_pins'],c.SOURCE_PINS)
        self.assertEqual(c.SESSION_KIND,self.original_module('p3_reviewer_session_032').SESSION_KIND)
        self.assertEqual(c.SESSION_KIND,self.original_module('p3_receipt_collection_032').SESSION_KIND)
        self.popen.assert_not_called()

    def test_actual030_history_reads_original_files_without_reconstructing_report(self):
        run=self.history_fixture(); result=self.history_call()
        self.assertEqual((result['prior_native_starts'],result['prior_sent_turns']),(12,9))
        self.assertFalse(result['historical030_main_report_reconstructed'])
        self.assertFalse((run/'REPORT.json').exists())
        self.assertTrue(result['kernel_prerequisite_reused_from_actual030']['observation']['observation']['kernel_child_mount_verified'])

    def test_missing_changed_or_new_historical_evidence_stops(self):
        for kind in ('missing','changed','unexpected_report','unexpected_verdict'):
            with self.subTest(kind=kind):
                run=self.history_fixture()
                (run/'REPORT.json').unlink(missing_ok=True)
                (run/'science_output/REVIEW_VERDICT.json').unlink(missing_ok=True)
                if kind=='missing':(run/'science_SESSION.json').unlink()
                elif kind=='changed':(run/'science_SESSION.json').write_bytes(b'{}\n')
                elif kind=='unexpected_report':put(run/'REPORT.json',b'{}\n')
                else:put(run/'science_output/REVIEW_VERDICT.json',b'{}\n')
                with self.assertRaises((c.Stop,OSError)):self.history_call()

    def test_history_and_preflight_stop_before_reservation(self):
        self.execute_fixture(history_error=True); self.execute_fixture(preflight_error=True)

    def test_success_counts14_11_preserves_original_verdict_and_reuses_without_model(self):
        path,result,calls=self.execute_fixture()
        self.assertEqual(calls,['synthetic','science'])
        self.assertEqual(result['status'],'REVIEWER_OUTPUT_PRESERVED')
        self.assertEqual(result['attempt_accounting']['cumulative_observed_native_starts'],14)
        self.assertEqual(result['attempt_accounting']['cumulative_observed_sent_turns'],11)
        self.assertTrue(result['reviewer_output']['execution_admitted'])
        self.assertEqual(self.reuse(path),path)
        self.assertEqual((path.parent/'science_output/REVIEW_VERDICT.json').read_bytes(),b'{"fixture_only":true}\n')

    def test_full_synthetic_refusal_and_independent_packet_checks_required(self):
        changes=({'recoverable_input_errors':1},{'recoverable_input_errors':True},
            {'broker_boundary_failure':{'code':'boundary.resource_path'}},{'broker_receipts':[]},
            {'observed_refusal':False},{'synthetic_argument_error_observed':False},{'host':False},
            {'native_process_reaped':False},{'packet_after':None},
            {'independent_packet_observer_opened_before_model':False},
            {'selected_binding':{'model':'wrong'}},{'pi_conversation_imported':True})
        for change in changes:
            with self.subTest(change=change):
                path,result,calls=self.execute_fixture(changes=change)
                self.assertEqual(calls,['synthetic']); self.assertFalse(result['science_started'])
                self.assertEqual(result['status'],'STOPPED_WITHOUT_COMPLETED_REVIEW')
                self.assertEqual(self.reuse(path),path)

    def test_actual_emitter_kind_change_is_per_file_error_and_always_writes_report(self):
        path,result,calls=self.execute_fixture(changes={'kind':'P3_FINITE_REVIEWER_SESSION_030_OFFLINE_PROPOSAL_v1'})
        self.assertEqual(calls,['synthetic'])
        self.assertTrue(path.exists())
        self.assertEqual(result['status'],'STOPPED_WITHOUT_COMPLETED_REVIEW')
        self.assertIn('session_kind_differs_from_bound_emitter',[e['code'] for e in result['receipt_collection']['errors']])
        self.assertTrue(result['attempt_accounting']['missing_session_counts_are_only_minimum_observations'])
        self.assertEqual(result['attempt_accounting']['cumulative_native_ceiling'],14)
        self.assertEqual(self.reuse(path),path)

    def test_each_malformed_or_missing_receipt_preserves_report_and_original_bytes(self):
        for filename in ('synthetic_SESSION.json','synthetic_STAGE.json','science_SESSION.json','science_STAGE.json'):
            for action in ('missing','malformed'):
                with self.subTest(filename=filename,action=action):
                    path,result,calls=self.execute_fixture(**{action:filename})
                    self.assertTrue(path.exists());self.assertEqual(result['status'],'STOPPED_WITHOUT_COMPLETED_REVIEW')
                    self.assertFalse(result['receipt_collection']['eligible_for_controller_admission_checks'])
                    if action=='missing':self.assertFalse((path.parent/filename).exists())
                    else:self.assertEqual((path.parent/filename).read_bytes(),b'{"truncated":')
                    if filename.startswith('synthetic'):self.assertEqual(calls,['synthetic'])
                    self.assertEqual(self.reuse(path),path)

    def test_catastrophic_collector_exception_cannot_suppress_report_or_release_capacity(self):
        path,result,calls=self.execute_fixture(collector_error=True)
        self.assertEqual(calls,['synthetic'])
        self.assertEqual(result['receipt_collection']['errors'][0]['code'],'guarded_collection_failed')
        self.assertNotIn('PRIVATE_COLLECTOR_EXCEPTION',path.read_text())
        self.assertTrue(result['attempt_accounting']['missing_session_counts_are_only_minimum_observations'])
        self.assertEqual(result['attempt_accounting']['maximum_cumulative_reservation_native_starts'],14)

    def test_changed_bundle_or_packet_prevents_science(self):
        for args in ({'bundle_changed':True},{'packet_changed':True}):
            path,result,calls=self.execute_fixture(**args)
            self.assertEqual(calls,['synthetic']);self.assertFalse(result['science_started'])
            self.assertEqual(self.reuse(path),path)

    def test_stage_context_exit_failure_retains_existing_sessions_and_stages(self):
        for mode in ('synthetic','science'):
            path,result,calls=self.execute_fixture(stage_error=RuntimeError('PRIVATE_CONTEXT_EXIT'),error_mode=mode)
            self.assertEqual(result['status'],'STOPPED_WITHOUT_COMPLETED_REVIEW')
            self.assertEqual(set(result['receipt_collection']['stages']),set(calls))
            self.assertNotIn('PRIVATE_CONTEXT_EXIT',path.read_text())
            if mode=='science':self.assertFalse(result['reviewer_output']['execution_admitted'])
            self.assertEqual(self.reuse(path),path)

    def test_failed_science_retains_packet_check_and_every_failure(self):
        failures=[{'phase':'session','code':'broker_refusal'},{'phase':'packet','code':'independent_packet_postcheck_failed'}]
        path,result,calls=self.execute_fixture(changes_mode='science',changes={
            'status':'STOPPED_WITHOUT_VERDICT','verdict_submitted':False,
            'primary_failure':{'layer':'session','reason':'Fixture refusal'},
            'failures':failures,'packet_after':{'status':'FAILED','verified':False}},verdict=False)
        self.assertEqual(calls,['synthetic','science'])
        self.assertEqual(result['stage_failures'],[{'stage':'science',**f} for f in failures])
        self.assertEqual(result['primary_session_stops'][0]['reason']['reason'],'Fixture refusal')
        self.assertEqual(result['attempt_accounting']['cumulative_observed_sent_turns'],11)
        self.assertEqual(self.reuse(path),path)

    def test_malformed_failure_shapes_are_categorized_not_raised(self):
        for failures in (None,[None],[{'phase':[],'code':{}}]):
            path,result,calls=self.execute_fixture(changes_mode='science',changes={'failures':failures})
            self.assertEqual(calls,['synthetic','science'])
            self.assertTrue(result['stage_failures'][0]['code'].startswith('stage_failure_'))
            self.assertEqual(result['status'],'STOPPED_WITHOUT_COMPLETED_REVIEW')
            self.assertEqual(self.reuse(path),path)

    def test_human_interrupt_creates_terminal_report_without_retry(self):
        path,result,calls=self.execute_fixture(stage_error=KeyboardInterrupt())
        self.assertEqual(result['status'],'INTERRUPTED_PARTIAL_PRESERVED')
        self.assertEqual(calls,['synthetic']); self.assertEqual(self.reuse(path),path)

    def test_original_session_stage_or_verdict_change_refused_on_reuse(self):
        for filename in ('synthetic_SESSION.json','science_SESSION.json','synthetic_STAGE.json',
            'science_STAGE.json','science_output/REVIEW_VERDICT.json','AUTHORIZATION.md'):
            path,_,_=self.execute_fixture()
            target=path.parent/filename;target.write_bytes(target.read_bytes()+b' \n')
            with self.assertRaises(c.Stop):self.reuse(path)

    def test_coherently_rehashed_report_cannot_forge_counters_or_admission(self):
        for modify in (
            lambda v:v['attempt_accounting'].__setitem__('cumulative_observed_sent_turns',2),
            lambda v:v['attempt_accounting'].__setitem__('reserved_turns_this_attempt',True),
            lambda v:v.__setitem__('science_started',False),
            lambda v:v['reviewer_output'].__setitem__('execution_admitted',False),
            lambda v:v['stages'][0]['observation'].__setitem__('observed_refusal',False)):
            path,result,_=self.execute_fixture();modify(result)
            raw=c.canonical(result);path.write_bytes(raw);path.with_name('REPORT.sha256').write_text(c.sha(raw)+'\n')
            with self.assertRaises(c.Stop):self.reuse(path)

    def test_partial_existing_attempt_never_restarts_or_manufactures_report(self):
        run=self.root/'delivery'/c.RUN_NAME;put(run/'ATTEMPT.json',b'{"fixture_only":true}\n')
        with self.assertRaises((c.Stop,OSError)):c.existing(run,self.pins)
        self.assertFalse((run/'REPORT.json').exists())
        self.assertEqual((run/'ATTEMPT.json').read_bytes(),b'{"fixture_only":true}\n')

    def test_exact_recorded_standing_authorization_and_manual_command_required(self):
        put(self.root/'state/ESCALATION.md',self.auth())
        with mock.patch.object(c,'ROOT',self.root):
            for manual in (False,None,1,'true'):
                with self.assertRaises(c.Stop):c.approval(self.scope,manual_launch=manual)
            self.assertEqual(c.approval(self.scope,manual_launch=True)['sha256'],c.sha(self.auth()))
            for raw in (self.auth()+b'\n## ANSWER\n',b'```\n'+self.auth()+b'```\n',
                        self.auth().replace(b'_032_CORRECTION',b'_030_CORRECTION'),self.auth()+b'additional text\n'):
                put(self.root/'state/ESCALATION.md',raw)
                with self.assertRaises(c.Stop):c.approval(self.scope,manual_launch=True)

    def test_real_run_stage_preserves_failed_independent_postcheck_in_both_modes(self):
        for mode in ('synthetic','science'):
            with self.subTest(mode=mode):
                run=self.root/('real_stage_'+mode);run.mkdir()
                packet,manifest=c.synthetic_packet(run)
                facts={'runtime_before':{'sha256':self.scope['runtime_sha256']},
                    'bwrap_before':{'sha256':self.scope['bwrap_sha256']},
                    'runtime':Path('/synthetic-not-executed/runtime'),'identifier_bytes':b'fixture-nonsecret-id',
                    'codex_home':self.root/'synthetic-home','auth_before':{'device':0,'inode':0},
                    'cache_origins':{},'origins':[]}
                metadata=mock.Mock();metadata.inventory.return_value=facts
                metadata.build_live_plan.return_value={'argv':['SYNTHETIC_NEVER_EXECUTED']}
                preflight=mock.Mock();preflight.overrides.return_value={}
                profile=mock.Mock();profile.reviewer_overrides.return_value={};profile.cli_override_arguments.return_value=[]
                cache_inputs=mock.Mock();cache_inputs.apply_to_plan.side_effect=lambda plan:plan
                cache_inputs.report_plan.side_effect=lambda plan:plan;cache_inputs.receipt.return_value={'fixture_only':True}
                context=mock.MagicMock();context.__enter__.return_value=cache_inputs
                cache=mock.Mock();cache.capture_cache_inputs.return_value=context
                stage_evidence=mock.Mock(wraps=self.original_module('p3_stage_evidence_030'))
                stage_evidence.collect_postchecks.return_value={'all_noncredential_checks_pass':True,'failures':[]}
                session=mock.Mock()
                def observed_stage(*args,**kwargs):
                    (packet/'CANARY.txt').write_bytes(b'fixture packet mutation after session start')
                    return self.observation(mode)
                session.run_session.side_effect=observed_stage
                substitutions={'gate0_postlogin_metadata':metadata,'gate0_client_preflight':preflight,
                    'p3_reviewer_profile_022':profile,'gate0_client_mount_plan':mock.Mock(),
                    'p3_cache_inputs_030':cache,'p3_stage_evidence_030':stage_evidence,
                    'p3_reviewer_session_032':session}
                with mock.patch.object(c,'module',side_effect=lambda name:substitutions.get(name) or self.original_module(name)):
                    result=c.run_stage(self.scope,self.prior,run,mode,packet,manifest,
                        expected_binding=c.BINDING.copy() if mode=='science' else None)
                self.assertTrue(result['independent_packet_observer_opened_before_model'])
                self.assertEqual(result['packet_after']['status'],'FAILED')
                self.assertIn({'phase':'packet','code':'independent_packet_postcheck_failed'},result['failures'])
                self.assertEqual(json.loads((run/(mode+'_STAGE.json')).read_bytes()),result)
                self.assertTrue((run/(mode+'_SESSION.json')).exists())
                self.assertFalse(c.admitted_synthetic(result) if mode=='synthetic' else c.admitted_science(result))
                session.run_session.assert_called_once()
                self.popen.assert_not_called()

    def test_default_inspection_neither_launches_nor_reads_host(self):
        with (mock.patch.object(c,'load_bundle',return_value=(self.scope,self.prior,self.pins)),mock.patch.object(
            c,'ROOT',self.root),mock.patch.object(c.old,'canonical_host',side_effect=AssertionError('No host inspection')),
            mock.patch.object(c,'execute',side_effect=AssertionError('No execution')),mock.patch.object(
            sys,'argv',['p3_finite_review_032.py']),redirect_stdout(io.StringIO()) as out):
            self.assertEqual(c.main(),0)
        self.assertIn('Inspection only',out.getvalue())


class ActualEmitterControllerSeam032Tests(unittest.TestCase):
    def test_actual_synthetic_transport_receipt_satisfies_controller_recovery_contract(self):
        # This launches only the existing fixed Python protocol fixture. The real
        # new session emitter, protocol wrapper and broker supply all counters,
        # statuses, traversal cause witnesses and receipt kinds used below.
        sys.path.insert(0,str(LAB/'tests'))
        import test_p3_session_pipeline_032 as pipeline
        fixture=pipeline.PipelineTests('test_synthetic_real_path_refusal_returns_feedback_and_shared_schema_receipt')
        fixture.setUp()
        try:
            fixture.calls(pipeline.fixtures.prior.fixtures.tool_call(101,pipeline.session.SYNTHETIC_INVALID_READ),
                pipeline.fixtures.prior.fixtures.tool_call(102,pipeline.session.SYNTHETIC_READ),
                pipeline.fixtures.prior.fixtures.tool_call(103,pipeline.session.SYNTHETIC_FORBIDDEN))
            observation,stage,collection=fixture.execute(mode='synthetic')
            self.assertTrue(c.synthetic_recovery_admitted(observation),observation.get('broker_receipts'))
            self.assertEqual(observation['kind'],c.SESSION_KIND)
            self.assertTrue(collection['eligible_for_controller_admission_checks'])
            # These three stage-origin facts are synthetic fixture construction
            # facts. All admission-relevant native observations above are emitted.
            stage.update(fresh_process_and_runtime_directories=True,pi_conversation_imported=False,
                         independent_packet_observer_opened_before_model=True)
            self.assertTrue(c.admitted_synthetic(stage))
            altered=copy.deepcopy(stage);altered['observation']['recoverable_input_errors']=1
            self.assertFalse(c.admitted_synthetic(altered))
        finally:
            fixture.tearDown()


if __name__=='__main__':unittest.main()
