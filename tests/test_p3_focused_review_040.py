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
spec = importlib.util.spec_from_file_location('focused_controller040_test', ROOT / 'scripts/p3_focused_review_040.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


class ControllerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scope, cls.prior, cls.pins = c.load_bundle()
        cls.session = c.module('p3_reviewer_session_040')
        cls.broker = c.module('p3_focused_review_broker_039')
        cls.protocol = c.module('p3_focused_review_protocol_039')

    def test_native_session_source_retains_transport_exactly(self):
        old = (ROOT / 'scripts/p3_reviewer_session_039.py').read_text()
        expected = old.replace('admission = _module("p3_reviewer_admission_022")',
            'admission = _module("p3_reviewer_admission_040")').replace(
            'SESSION_KIND = "P3_FINITE_REVIEWER_SESSION_039_v1"',
            'SESSION_KIND = "P3_FINITE_REVIEWER_SESSION_040_v1"')
        self.assertEqual((ROOT / 'scripts/p3_reviewer_session_040.py').read_text(), expected)

    def test_admission_preserves_every_other_function_and_control(self):
        old_tree = ast.parse((ROOT/'scripts/p3_reviewer_admission_022.py').read_text())
        new_tree = ast.parse((ROOT/'scripts/p3_reviewer_admission_040.py').read_text())
        functions = lambda tree: {node.name:ast.dump(node, include_attributes=False)
            for node in tree.body if isinstance(node,(ast.FunctionDef,ast.ClassDef))
            and node.name != 'thread_params'}
        self.assertEqual(functions(old_tree), functions(new_tree))
        values = lambda tree: {node.targets[0].id:ast.dump(node.value,include_attributes=False)
            for node in tree.body if isinstance(node,ast.Assign) and len(node.targets)==1
            and isinstance(node.targets[0],ast.Name) and node.targets[0].id.isupper()}
        old_values, new_values = values(old_tree), values(new_tree)
        self.assertEqual(old_values, {k:v for k,v in new_values.items()
                                     if k != 'FROZEN039_TOOL_CONTRACT_SHA256'})

    def test_actual_local_module_dependency_closure_is_source_pinned(self):
        pending = ['p3_focused_review_040']; seen = set()
        while pending:
            name = pending.pop()
            if name in seen:
                continue
            seen.add(name)
            path = ROOT/'scripts'/(name+'.py')
            if name != 'p3_focused_review_040':
                self.assertEqual(c.sha(path.read_bytes()),self.scope['source_pins']['scripts/'+name+'.py'])
            for node in ast.walk(ast.parse(path.read_text())):
                names = []
                if isinstance(node,ast.Constant) and isinstance(node.value,str):
                    names = [node.value]
                elif isinstance(node,ast.Import):
                    names = [alias.name for alias in node.names]
                elif isinstance(node,ast.ImportFrom) and node.module:
                    names = [node.module]
                for candidate in names:
                    if len(candidate) < 128 and '/' not in candidate and '\n' not in candidate and \
                            (ROOT/'scripts'/(candidate+'.py')).is_file():
                        pending.append(candidate)
        self.assertIn('p3_reviewer_admission_040',seen)
        self.assertIn('p3_review_broker',seen)
        self.assertNotIn('p3_reviewer_admission_022',seen)
        self.assertEqual(self.scope['historical_evidence']['scope039']['sha256'],
            c.sha((ROOT/'configs/P3_FOCUSED_REVIEW_SCOPE_039.json').read_bytes()))
        self.assertEqual(self.scope['historical_evidence']['return_manifest039']['sha256'],
            'd2920f175118de41a4769a3394f07a8211eb75b67e08916a0ea179ea5c42afb1')
        self.assertIn('/8b2bd233f9e585d4ef490dd5302ee488c14989d8badeb5ab2b3353c23c85049b/',
            self.scope['historical_evidence']['return_manifest039']['path'])

    def test_old_admission_reproduces_confirmed_science_stop(self):
        old_spec = importlib.util.spec_from_file_location('old_admission022_regression',
            ROOT / 'scripts/p3_reviewer_admission_022.py')
        old = importlib.util.module_from_spec(old_spec); old_spec.loader.exec_module(old)
        tools = self.broker.dynamic_tool_specs()
        profile = self.session.admission.REQUIRED_CONTROLS.copy()
        with self.assertRaisesRegex(old.Stop, 'Unexpected reviewer dynamic tool spec'):
            old.thread_params('gpt-5.6-sol', 'max', '/offline/reviewer', tools, profile)
        old.thread_params('gpt-5.6-sol', 'max', '/offline/reviewer',
                         [row for row in tools if row['name'] == 'read_text'], profile)

    def test_real_science_specs_and_synthetic_subset_pass_real_admission(self):
        admission = self.session.admission
        profile = admission.REQUIRED_CONTROLS.copy()
        science = self.broker.dynamic_tool_specs()
        for specs in (science, [row for row in science if row['name'] == 'read_text']):
            result = admission.thread_params('gpt-5.6-sol', 'max', '/offline/reviewer', specs, profile)
            self.assertEqual(result['dynamicTools'], specs)
            self.assertEqual(result['permissions'], ':read-only')
            self.assertEqual(result['environments'], [])
            self.assertEqual(result['runtimeWorkspaceRoots'], [])
            self.assertEqual(result['selectedCapabilityRoots'], [])
            self.assertTrue(result['ephemeral'])
            self.assertFalse(result['allowProviderModelFallback'])
            self.assertEqual(result['config'], {**profile, 'model_reasoning_effort':'max'})

    def test_unknown_observer_shell_duplicates_schema_or_subset_refused(self):
        admission = self.session.admission
        original = self.broker.dynamic_tool_specs()
        variants = {}
        for name in ('run_observer_audit', 'shell', 'unknown'):
            specs = copy.deepcopy(original); specs[3]['name'] = name; variants[name] = specs
        duplicate = copy.deepcopy(original); duplicate[3] = copy.deepcopy(duplicate[0]); variants['duplicate'] = duplicate
        schema = copy.deepcopy(original); schema[0]['inputSchema']['properties']['length']['maximum'] += 1; variants['schema'] = schema
        extra = copy.deepcopy(original); extra[3]['inputSchema']['additionalProperties'] = True; variants['relaxation'] = extra
        description = copy.deepcopy(original); description[3]['description'] += ' changed'; variants['description'] = description
        variants['missing_tool'] = copy.deepcopy(original[:-1])
        variants['reordered'] = list(reversed(copy.deepcopy(original)))
        for name, specs in variants.items():
            with self.subTest(name=name), self.assertRaises(admission.Stop):
                admission.thread_params('gpt-5.6-sol','max','/offline/reviewer',specs,
                                        admission.REQUIRED_CONTROLS.copy())

    def test_model_effort_permissions_and_profile_are_unchanged(self):
        admission = self.session.admission
        tools = self.broker.dynamic_tool_specs()
        for model, effort in (('gpt-6-astra','max'),('gpt-5.6-sol','high')):
            with self.subTest(model=model, effort=effort), self.assertRaises(admission.Stop):
                admission.thread_params(model,effort,'/offline/reviewer',tools,
                                        admission.REQUIRED_CONTROLS.copy())
        for key in admission.REQUIRED_CONTROLS:
            profile = copy.deepcopy(admission.REQUIRED_CONTROLS)
            del profile[key]
            with self.subTest(removed=key), self.assertRaises(admission.Stop):
                admission.thread_params('gpt-5.6-sol','max','/offline/reviewer',tools,profile)

    def test_pure_actual_payload_preflight_performs_no_native_start(self):
        with patch.object(self.session, 'run_session', side_effect=AssertionError('no native')) as launch:
            value = c.dynamic_tool_preflight(self.scope)
            launch.assert_not_called()
        self.assertEqual(value['native_clients_started'], 0)
        self.assertEqual(value['model_turns_sent'], 0)
        self.assertFalse(value['runtime_catalog_or_permissions_observed'])
        self.assertEqual(value['modes']['science']['tool_names'],
            ['read_text','read_page_image','hash_file','source_access_receipt','submit_verdict'])
        self.assertTrue(all(row['real_thread_params_admitted'] and row['requested_profile_preserved']
                            for row in value['modes'].values()))

    def test_actual_science_spec_failure_stops_before_attempt_or_canary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / 'state').mkdir(); (root / 'state/ESCALATION.md').write_bytes(b'')
            scope = copy.deepcopy(self.scope)
            scope.update(canonical_project=str(root), canonical_home=str(Path.home()))
            altered = self.broker.dynamic_tool_specs(); altered[3]['name'] = 'run_observer_audit'
            schema_path = 'artifacts/GATE0_CODEX_INTERFACE/20260907_001/config-schema.json'
            (root/schema_path).parent.mkdir(parents=True)
            (root/schema_path).write_bytes((ROOT/schema_path).read_bytes())
            modules = {name:c.module(name) for name in ('p3_focused_review_broker_039',
                'p3_reviewer_admission_040','p3_reviewer_profile_022','gate0_client_preflight')}
            with patch.object(c, 'ROOT', root), patch.object(c, 'run_stage') as launch, \
                 patch.object(c, 'prior_history') as history, \
                 patch.object(c, 'module', side_effect=lambda name: modules[name]), \
                 patch.object(self.broker, 'dynamic_tool_specs', return_value=altered):
                with self.assertRaises(self.session.admission.Stop):
                    c.execute(scope, self.prior, self.pins, root/'packet')
                launch.assert_not_called(); history.assert_not_called()
                self.assertFalse((root/'delivery'/c.RUN_NAME).exists())

    def test_original039_and032_receipts_establish_prior_usage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for row in self.scope['historical_evidence'].values():
                for destination in (row['path'], row.get('actual_path')):
                    if destination is None:
                        continue
                    target = root / destination; target.parent.mkdir(parents=True,exist_ok=True)
                    target.write_bytes((ROOT / row['path']).read_bytes())
            with patch.object(c,'ROOT',root):
                history = c.prior_history(self.scope)
            self.assertEqual(history['prior_native_starts'],16)
            self.assertEqual(history['prior_sent_turns'],12)
            self.assertTrue(history['actual039_original_receipts_reverified'])
            self.assertFalse(history['prior039_science_thread_or_model_turn_started'])
            self.assertFalse(history['prior039_verdict_available'])

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
                with self.assertRaisesRegex(c.Stop,'Partial040'):
                    c.existing(run, self.pins)
                stage.assert_not_called()

    def test_missing_session_usage_remains_a_lower_bound(self):
        counts=c.accounting({}, ['synthetic'])
        self.assertEqual(counts['cumulative_observed_native_starts'],16)
        self.assertEqual(counts['maximum_cumulative_reservation_native_starts'],18)
        self.assertEqual(counts['maximum_cumulative_reservation_turns'],14)
        self.assertTrue(counts['missing_session_counts_are_only_minimum_observations'])
        self.assertTrue(counts['unobserved_reserved_capacity_is_not_automatically_released'])

    def simulated_pipeline(self, fail=None):
        """Run actual controller/collector against explicitly synthetic receipts."""
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root=Path(temporary.name)
        for folder in ('delivery','scripts','state/authorizations'):
            (root/folder).mkdir(parents=True,exist_ok=True)
        for name in ('p3_reviewer_session_040.py','p3_receipt_collection_032.py'):
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
        collector_spec=importlib.util.spec_from_file_location('collector040_test',ROOT/'scripts/p3_receipt_collection_032.py')
        collector=importlib.util.module_from_spec(collector_spec);collector_spec.loader.exec_module(collector)
        with patch.object(c,'ROOT',root),patch.object(c,'module',side_effect=lambda n:collector if n=='p3_receipt_collection_032' else original_module(n)),\
             patch.object(c,'prior_history',return_value={'offline_fixture':True}),\
             patch.object(c,'packet_preflight',return_value=packet_info),\
             patch.object(c,'dynamic_tool_preflight',return_value={'offline_fixture':True}),\
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
        self.assertEqual(result['attempt_accounting']['cumulative_observed_native_starts'],17)
        self.assertEqual(result['attempt_accounting']['cumulative_observed_sent_turns'],13)

    def test_two_stage_fixture_has_fresh_packet_and_exact_accounting(self):
        calls,result,report=self.simulated_pipeline()
        self.assertEqual([call[0] for call in calls],['synthetic','science'])
        self.assertNotEqual(calls[0][1],calls[1][1])
        self.assertIsNone(calls[0][2])
        self.assertEqual(calls[1][2],c.BINDING)
        self.assertEqual(result['status'],'REVIEWER_OUTPUT_PRESERVED')
        self.assertEqual(result['attempt_accounting']['cumulative_observed_native_starts'],18)
        self.assertEqual(result['attempt_accounting']['cumulative_observed_sent_turns'],14)
        self.assertFalse(result['scientific_verdict_chosen_by_parent'])
        self.assertTrue(result['receipt_collection']['eligible_for_controller_admission_checks'])

    def test_science_failure_preserves_sent_turn_and_no_verdict(self):
        calls,result,report=self.simulated_pipeline('science')
        self.assertEqual(len(calls),2)
        self.assertEqual(result['status'],'STOPPED_WITHOUT_COMPLETED_REVIEW')
        self.assertEqual(result['attempt_accounting']['cumulative_observed_sent_turns'],14)
        self.assertIsNone(result['reviewer_output'])

if __name__=='__main__':
    unittest.main()
