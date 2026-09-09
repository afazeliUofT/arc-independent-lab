"""Finite-session integration using fake stdio children and the real closed broker.

No installed Codex process, credentials, login, network, paid operation or actual
model invocation occurs. Fake protocol messages do not certify native isolation.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import p3_reviewer_session_021 as s

BASE = ROOT / "delivery/p3_reviewer_session_021_tests"
BASE.mkdir(parents=True, exist_ok=True)
PROMPT = "Synthetic finite session fixture; no scientific input."
BINDING = {"model": "gpt-6-astra", "id": "astra-native-id", "effort": "ultra"}

FAKE = r'''
import copy,json,os,sys,time
f=json.load(open(sys.argv[1])); scenario=f['scenario']; model_page_index=0
def send(v):
 print(json.dumps(v,separators=(',',':')),flush=True)
def note(method,params): send({'method':method,'params':params,'emittedAtMs':1})
def call(rid=91,callid='call-one',path='CANARY.txt',**kw):
 p={'threadId':'thread-one','turnId':'turn-one','tool':'read_text',
 'callId':callid,'arguments':{'path':path,'offset':0,'length':1000}}
 p.update(kw); return {'id':rid,'method':'item/tool/call','params':p}
def started():
 note('turn/started',{'threadId':'thread-one','turn':{'id':'turn-one','items':[],'status':'inProgress'}})
for line in sys.stdin:
 m=json.loads(line)
 if 'method' not in m:
  if scenario=='science': time.sleep(10);continue
  if scenario=='replay_rpc': send(call(callid='call-two',path='../OUTSIDE.txt'))
  elif scenario=='replay_call': send(call(rid=92,path='../OUTSIDE.txt'))
  elif scenario=='wrong_forbidden': send(call(rid=92,callid='call-two',path='../DIFFERENT.txt'))
  else: send(call(rid=92,callid='call-two',path='../OUTSIDE.txt'))
  continue
 method=m['method']
 if method=='initialized': continue
 if scenario=='quiet': time.sleep(10);continue
 if method=='initialize':
  if f.get('warning_position')=='before_initialize': note('configWarning',f['warning_payload'])
  send({'id':m['id'],'result':{'userAgent':'synthetic','codexHome':os.environ.get('CODEX_HOME',os.environ['HOME']+'/.codex'),'platformFamily':'unix','platformOs':'linux'}})
  if f.get('warning_position')=='after_initialize':
   for _ in range(f.get('warning_count',1)): note('configWarning',f['warning_payload'])
  if scenario=='bad_timestamp': send({'method':'account/updated','params':{},'emittedAtMs':True})
  else: note('remoteControl/status/changed',{'status':'disabled','installationId':'withheld','serverName':'withheld'})
  print('SECRET_DIAGNOSTIC_MUST_NOT_ESCAPE',file=sys.stderr,flush=True)
 elif method=='model/list' and 'model_pages' in f:
  send({'id':m['id'],'result':f['model_pages'][model_page_index]});model_page_index+=1
 elif method in f['responses']:
  if scenario=='rpc_error' and method=='account/read':
   send({'id':m['id'],'error':{'code':-1,'message':'credential SECRET_ACCOUNT_MUST_NOT_ESCAPE'}})
  else: send({'id':m['id'],'result':f['responses'][method]})
 elif method=='thread/start':
  if f.get('warning_position')=='after_thread_requested': note('configWarning',f['warning_payload'])
  if f.get('warning_thread_silent'): time.sleep(10);continue
  t=f['thread']; note('thread/started',{'thread':t['thread']})
  send({'id':m['id'],'result':t})
 elif method=='turn/start':
  if scenario=='unknown_early': send({'id':91,'method':'config/write','params':{'secret':'NEVER_ECHO_NATIVE'}});continue
  if scenario=='early_overflow':
   for _ in range(65): note('thread/status/changed',{'threadId':'thread-one','status':{'type':'active','activeFlags':[]}})
  started()
  if scenario in ('same_settings','changed_settings'):
   st={'threadId':'thread-one','threadSettings':{
    'model':'gpt-6-astra','modelProvider':'openai','effort':'ultra','cwd':f['thread']['cwd'],
    'approvalPolicy':'never','approvalsReviewer':'user',
    'activePermissionProfile':{'id':':read-only','extends':None},
    'sandboxPolicy':{'type':'readOnly','networkAccess':False},
    'collaborationMode':{'mode':'default','settings':{'model':'gpt-6-astra','reasoning_effort':'ultra','developer_instructions':None}},
    'multiAgentMode':'explicitRequestOnly','personality':None,'summary':'auto','serviceTier':None}}
   if scenario=='changed_settings': st['threadSettings']['model']='other-model'
   note('thread/settings/updated',st)
  c=call()
  if scenario=='foreign_thread': c['params']['threadId']='foreign'
  if scenario=='foreign_turn': c['params']['turnId']='foreign'
  if scenario=='namespace': c['params']['namespace']='unsafe'
  if scenario=='forbidden_first': c=call(path='../OUTSIDE.txt')
  if scenario=='unknown_tool': c['params']['tool']='exec_command'
  if scenario=='unexpected_event': note('model/rerouted',{'threadId':'thread-one','turnId':'turn-one','toModel':'hidden'})
  if scenario=='unsafe_item': note('item/started',{'threadId':'thread-one','turnId':'turn-one','item':{'id':'item1','type':'commandExecution'}})
  if scenario=='science': c=call(tool='submit_verdict',arguments=f['verdict'])
  if scenario=='pipe_stall': c=call(tool='read_page_image',arguments={'path':'pages/large.png'})
  if scenario=='foreign_user_item': note('item/started',{'threadId':'thread-one','turnId':'turn-one','item':{'id':'u','type':'userMessage','content':[{'type':'text','text':'INJECTED_CONTENT'}]}})
  send(c)
  send({'id':m['id'] if scenario!='bad_response_id' else 600,'result':{'turn':{'id':'turn-one','items':[],'status':'inProgress'}}})
  if scenario=='pipe_stall': time.sleep(10)
'''


def nested(flat):
    result = {}
    for dotted, value in flat.items():
        node = result
        bits = dotted.split(".")
        for bit in bits[:-1]:
            node = node.setdefault(bit, {})
        node[bits[-1]] = copy.deepcopy(value)
    return result


class Fixture:
    def __init__(self, scenario):
        self.tmp = tempfile.TemporaryDirectory(prefix="synthetic-", dir=BASE)
        self.root = Path(self.tmp.name)
        self.run, self.packet, self.output = [self.root / n for n in ("run", "packet", "output")]
        for path in (self.run, self.packet, self.output): path.mkdir()
        self.profile = s.profile.reviewer_overrides(s.preflight.overrides(self.run),
            (ROOT / "artifacts/GATE0_CODEX_INTERFACE/20260907_001/config-schema.json").read_bytes())
        native = nested(self.profile)
        # Native scalar origins from fingerprint.rs, not the validator helper.
        # Every profile entry is scalar except this one literal Code Mode table.
        origins = {k: {"name": {"type": "sessionFlags"}, "version": "synthetic-v1"}
                   for k in self.profile if k not in ("features.multi_agent_v2", "features.code_mode")}
        for k in ("features.multi_agent_v2.enabled", "features.code_mode.enabled",
                  "features.code_mode.direct_only_tool_namespaces.0"):
            origins[k] = {"name": {"type": "sessionFlags"}, "version": "synthetic-v1"}
        raw = {"config": copy.deepcopy(native), "origins": origins,
            "layers": [{"name": {"type": "sessionFlags"}, "version": "synthetic-v1",
                        "config": native, "disabledReason": None}]}
        raw["config"].pop("tools")
        raw["config"]["cli_auth_credentials_store"] = "file"
        window = {"usedPercent": 1, "windowDurationMins": 10080, "resetsAt": 1789490427}
        models = {"data": [{"model": "gpt-6-astra", "id": "astra-native-id", "hidden": False,
            "isDefault": True, "supportedReasoningEfforts": [{"reasoningEffort": e} for e in ["low", "high", "ultra"]],
            "defaultReasoningEffort": "high"}], "nextCursor": None}
        if scenario == "no_model": models["data"][0]["model"] = "other-model"
        if scenario == "full_quota": window["usedPercent"] = 100
        if scenario == "bad_config": raw["config"]["features"]["code_mode_host"] = True
        if scenario == "api_account": account_kind = "apiKey"
        else: account_kind = "chatgpt"
        thread = {"model": "gpt-6-astra", "modelProvider": "openai", "reasoningEffort": "ultra",
            "approvalPolicy": "never", "approvalsReviewer": "user",
            "activePermissionProfile": {"id": ":read-only", "extends": None},
            "sandbox": {"type": "readOnly", "networkAccess": False}, "cwd": str(self.run),
            "runtimeWorkspaceRoots": [], "instructionSources": [],
            "thread": {"id": "thread-one", "sessionId": "session-one", "ephemeral": True,
                "cwd": str(self.run), "modelProvider": "openai", "cliVersion": "0.151.0", "turns": [],
                "preview": "", "status": {"type": "idle"}}}
        if scenario == "thread_fallback": thread["model"] = "other-model"
        files = {"CANARY.txt": b"Readable synthetic canary.\n", **{
            p: b'{"scope":"synthetic engineering only"}\n' for p in s.broker_module.REVIEW_MANIFESTS.values()}}
        if scenario == "pipe_stall": files["pages/large.png"] = b"\x89PNG\r\n\x1a\n" + b"X" * (512 * 1024)
        self.files = []
        for path, data in files.items():
            p = self.packet / path;p.parent.mkdir(parents=True, exist_ok=True);p.write_bytes(data)
            self.files.append({"path": path, "sha256": hashlib.sha256(data).hexdigest(),
                               "kind": "image" if path.endswith(".png") else "text"})
        (self.root / "OUTSIDE.txt").write_text("Must not be opened by broker.\n")
        manifest = json.dumps({"schema_version": 1, "files": self.files}).encode()
        (self.packet / "BROKER_MANIFEST.json").write_bytes(manifest)
        self.pin = hashlib.sha256(manifest).hexdigest()
        evidence_sha = self.files[0]["sha256"]
        hashes = {entry["path"]: entry["sha256"] for entry in self.files}
        self.verdict = {"verdict": "SUSPEND_FOR_DEPENDENCY", "applies_to": {
            "scope": "SYNTHETIC TEST ONLY", **{name: hashes[path] for name, path in s.broker_module.REVIEW_MANIFESTS.items()}},
            "summary": "Synthetic transport fixture.", "dispositions": [
                {"subject": subject, "disposition": "synthetic dependency", "reason": "No scientific model called.",
                 "evidence": [{"path": "CANARY.txt", "sha256": evidence_sha}]} for subject in s.broker_module.SUBJECTS],
            "strongest_objections": [], "missing_dependencies": ["Synthetic only"], "required_corrections": []}
        fake = {"scenario": scenario, "responses": {"config/read": raw,
            "configRequirements/read": {"requirements": None},
            "account/read": {"account": {"type": account_kind, "planType": "pro", "email": "DISCARDED_EMAIL"},
                             "requiresOpenaiAuth": True},
            "account/rateLimits/read": {"rateLimits": {"limitId": "codex", "primary": window, "secondary": None}},
            "model/list": models}, "thread": thread, "verdict": self.verdict}
        if scenario == "changed_plan":
            fake["responses"]["account/read"]["account"]["planType"] = "enterprise"
        if scenario in ("two_pages", "repeated_cursor", "duplicate_model_id", "invalid_cursor", "catalog_page_ceiling"):
            first = copy.deepcopy(models)
            first["data"][0].update({"model": "other-model", "id": "other-native-id"})
            first["nextCursor"] = "OPAQUE_CURSOR_NOT_FOR_REPORT_1"
            second = copy.deepcopy(models)
            fake["model_pages"] = [first, second]
            if scenario == "repeated_cursor": second["nextCursor"] = first["nextCursor"]
            if scenario == "duplicate_model_id": second["data"][0]["id"] = first["data"][0]["id"]
            if scenario == "invalid_cursor": first["nextCursor"] = "OPAQUE\nINVALID_CURSOR"
            if scenario == "catalog_page_ceiling":
                fake["model_pages"] = [{"data": [], "nextCursor": "OPAQUE_CURSOR_" + str(i)} for i in range(8)]
        if scenario == "managed_requirements":
            fake["responses"]["configRequirements/read"]["requirements"] = {
                "managedInstructionFiles": ["UNRETAINED_MANAGED_SOURCE"]}
        (self.root / "fixture.json").write_text(json.dumps(fake))
        (self.root / "fake.py").write_text(FAKE)
        self.plan = {"argv": [sys.executable, "-I", "-B", str(self.root / "fake.py"), str(self.root / "fixture.json")]}

    def invoke(self, mode="synthetic", *, wall_seconds=8, max_calls=16, expected_binding=None):
        with s.broker_module.ReviewBroker(self.packet, manifest_sha256=self.pin, output_root=self.output) as broker:
            return s.run_session(self.plan, self.run, self.profile, broker, mode=mode, prompt=PROMPT,
                                 wall_seconds=wall_seconds, max_calls=max_calls, expected_binding=expected_binding)

    def warning(self, params, *, position="after_initialize", count=1):
        path = self.root / "fixture.json"
        data = json.loads(path.read_bytes())
        data.update({"warning_payload": params, "warning_position": position, "warning_count": count})
        path.write_text(json.dumps(data))

    def close(self): self.tmp.cleanup()


class SessionTests(unittest.TestCase):
    def run_case(self, scenario="success", **kwargs):
        f = Fixture(scenario)
        try: return f.invoke(**kwargs)
        finally: f.close()

    def warning_case(self, params=None, *, scenario="success", position="after_initialize", count=1):
        f = Fixture(scenario)
        try:
            f.warning(params if params is not None else {
                "summary": s.config_warning.MISSING_BWRAP_SUMMARY, "details": None},
                position=position, count=count)
            return f.invoke()
        finally:
            f.close()

    def test_origin_failure_retains_all_safe_controls_without_model_turn(self):
        f = Fixture("success")
        try:
            path = f.root / "fixture.json"
            native = json.loads(path.read_bytes())
            config = native["responses"]["config/read"]
            config["origins"]["features.code_mode.direct_only_tool_namespaces.0"]["version"] = "SECRET_VERSION_DO_NOT_RETAIN"
            config["config"]["unknown_native_key"] = "SECRET_VALUE_DO_NOT_RETAIN"
            path.write_text(json.dumps(native))
            r = f.invoke()
            self.assertEqual(r["status"], "STOPPED_WITHOUT_VERDICT")
            self.assertFalse(r["thread_request_sent"])
            self.assertFalse(r["model_turn_request_sent"])
            self.assertTrue(r["native_process_reaped"])
            observation = r["config_control_observation"]
            self.assertEqual(set(observation["control_observations"]), set(f.profile))
            self.assertEqual(observation["first_failure"]["check"], "scalar_origin")
            self.assertEqual(observation["first_failure"]["control"], "features.code_mode")
            self.assertTrue(observation["controls"]["orchestrator.mcp.enabled"])
            serialized = json.dumps(r)
            for secret in ("SECRET_VERSION_DO_NOT_RETAIN", "SECRET_VALUE_DO_NOT_RETAIN", "unknown_native_key"):
                self.assertNotIn(secret, serialized)
        finally:
            f.close()

    def test_success_retains_source_correct_control_diagnostics(self):
        r = self.run_case()
        self.assertEqual(r["status"], "SYNTHETIC_REFUSAL_OBSERVED", r)
        observation = r["config_control_observation"]
        self.assertTrue(observation["all_requested_controls_verified"])
        self.assertIsNone(observation["first_failure"])
        self.assertEqual(set(observation["control_observations"]["features.multi_agent_v2"]["origins"]),
                         {"features.multi_agent_v2.enabled"})
        self.assertTrue(observation["control_observations"]["features.code_mode"]["origins"]
                        ["features.code_mode.direct_only_tool_namespaces.0"]["verified_session_origin"])

    def test_initialize_then_known_warning_keeps_all_checks_and_reaches_real_broker_refusal(self):
        r = self.warning_case()
        self.assertEqual(r["status"], "SYNTHETIC_REFUSAL_OBSERVED", r)
        self.assertEqual(r["notifications"]["configWarning"], 1)
        self.assertEqual(r["config_warnings"], [{
            "category": "missing_system_bwrap_bundled_fallback_advisory",
            "decision": "admitted_prethread_advisory", "admitted": True,
            "raw_content_saved_or_hashed": False, "shape": {
                "parameters_object": True, "summary_string": True,
                "details_present": True, "details_nonnull": False,
                "path_present": False, "path_nonnull": False,
                "range_present": False, "range_nonnull": False,
                "unknown_fields_present": False}}])
        self.assertTrue(r["synthetic_allowed_read_observed"])
        self.assertTrue(r["observed_refusal"])
        self.assertTrue(r["native_process_reaped"])
        self.assertEqual(r["requests_sent"], ["initialize", "config/read", "configRequirements/read",
            "account/read", "account/rateLimits/read", "model/list", "thread/start", "turn/start"])

    def test_unknown_policy_parse_and_managed_fallback_warnings_stop_before_model(self):
        summaries = [s.config_warning.MISSING_BWRAP_SUMMARY + " SECRET_WARNING_NEVER_SAVE",
            "Failed to load configuration SECRET_WARNING_NEVER_SAVE",
            "Failed to load cloud requirements; fallback SECRET_WARNING_NEVER_SAVE"]
        for summary in summaries:
            with self.subTest(kind="synthetic_unknown"):
                r = self.warning_case({"summary": summary, "details": None})
                self.assertEqual(r["status"], "STOPPED_WITHOUT_VERDICT", r)
                self.assertFalse(r["thread_request_sent"])
                self.assertFalse(r["model_turn_request_sent"])
                self.assertNotIn("model/list", r["requests_sent"])
                self.assertEqual(r["config_warnings"][0]["category"], "unrecognized_config_warning")
                self.assertTrue(r["native_process_reaped"])
                self.assertNotIn("SECRET_WARNING_NEVER_SAVE", json.dumps(r))
                self.assertNotIn(hashlib.sha256(summary.encode()).hexdigest(), json.dumps(r))

    def test_extra_fields_details_path_and_range_refused_without_raw_values(self):
        good = {"summary": s.config_warning.MISSING_BWRAP_SUMMARY, "details": None}
        for params in ({**good, "extra": "SECRET_WARNING_NEVER_SAVE"},
                {**good, "details": "SECRET_WARNING_NEVER_SAVE"},
                {**good, "path": "/SECRET_WARNING_NEVER_SAVE"}, {**good, "range": None},
                {"summary": good["summary"]}, ["SECRET_WARNING_NEVER_SAVE"]):
            r = self.warning_case(params)
            self.assertEqual(r["status"], "STOPPED_WITHOUT_VERDICT", r)
            self.assertFalse(r["model_turn_request_sent"])
            self.assertNotIn("model/list", r["requests_sent"])
            self.assertEqual(r["config_warnings"][0]["decision"], "unsupported_warning_shape")
            self.assertNotIn("SECRET_WARNING_NEVER_SAVE", json.dumps(r))

    def test_known_consequential_warning_categories_survive_terminal_refusal_without_values(self):
        cases = [(s.config_warning.POLICY_PARSE_SUMMARY, "execution_policy_parse_failure"),
            (s.config_warning.SQLITE_RECOVERY_SUMMARY, "sqlite_database_recovery"),
            (s.config_warning.DEFAULTS_FALLBACK_SUMMARY, "invalid_configuration_defaults_fallback"),
            (s.config_warning.USER_NAMESPACE_SUMMARY, "native_user_namespace_support_warning"),
            (s.config_warning.WSL1_SUMMARY, "native_wsl1_namespace_warning"),
            (s.config_warning.DISABLED_PROJECT_PREFIX + "/SECRET_NATIVE_FOLDER", "disabled_project_configuration"),
            (s.config_warning.MANAGED_VALUE_PREFIX + "SECRET_FIELD` is disallowed by requirements; "
             "falling back to required value SECRET_VALUE", "managed_requirement_value_fallback")]
        for summary, category in cases:
            with self.subTest(category=category):
                r = self.warning_case({"summary": summary, "details": "SECRET_WARNING_DETAIL",
                    "path": "/SECRET_NATIVE_PATH", "range": {"SECRET_POSITION_KEY": 42}})
                self.assertEqual(r["status"], "STOPPED_WITHOUT_VERDICT", r)
                receipt = r["config_warnings"][0]
                self.assertEqual(receipt["category"], category)
                self.assertFalse(receipt["admitted"])
                self.assertTrue(receipt["shape"]["details_nonnull"])
                self.assertTrue(receipt["shape"]["path_present"])
                self.assertTrue(receipt["shape"]["range_present"])
                self.assertNotIn("model/list", r["requests_sent"])
                self.assertFalse(r["thread_request_sent"])
                self.assertFalse(r["model_turn_request_sent"])
                self.assertTrue(r["native_process_reaped"])
                self.assertNotIn("SECRET", json.dumps(r))
                self.assertNotIn(summary, json.dumps(r))
                self.assertNotIn(hashlib.sha256(summary.encode()).hexdigest(), json.dumps(r))

    def test_warning_before_validated_initialize_cannot_be_admitted(self):
        r = self.warning_case(position="before_initialize")
        self.assertEqual(r["status"], "STOPPED_WITHOUT_VERDICT", r)
        self.assertEqual(r["config_warnings"][0]["decision"], "unexpected_warning_context")
        self.assertFalse(r["model_turn_request_sent"])
        self.assertNotIn("initialization", r)

    def test_warning_after_thread_request_stops_before_model_turn(self):
        r = self.warning_case(position="after_thread_requested")
        self.assertEqual(r["status"], "STOPPED_WITHOUT_VERDICT", r)
        self.assertTrue(r["thread_request_sent"])
        self.assertFalse(r["model_turn_request_sent"])
        self.assertEqual(r["config_warnings"][0]["decision"], "unexpected_warning_context")

    def test_late_warning_receipt_does_not_wait_for_or_depend_on_thread_response(self):
        f = Fixture("success")
        try:
            f.warning({"summary": s.config_warning.MISSING_BWRAP_SUMMARY, "details": None},
                position="after_thread_requested")
            path = f.root / "fixture.json"
            data = json.loads(path.read_bytes())
            data["warning_thread_silent"] = True
            path.write_text(json.dumps(data))
            r = f.invoke(wall_seconds=5)
        finally:
            f.close()
        self.assertEqual(r["status"], "STOPPED_WITHOUT_VERDICT", r)
        self.assertEqual(r["config_warnings"][0]["decision"], "unexpected_warning_context")
        self.assertNotIn("thread_admission", r)
        self.assertFalse(r["model_turn_request_sent"])
        self.assertTrue(r["native_process_reaped"])
        self.assertLess(r["elapsed_seconds"], 5.5)

    def test_second_advisory_is_terminal_and_preserves_both_classified_receipts(self):
        r = self.warning_case(count=2)
        self.assertEqual(r["status"], "STOPPED_WITHOUT_VERDICT", r)
        self.assertEqual(len(r["config_warnings"]), 2)
        self.assertTrue(r["config_warnings"][0]["admitted"])
        self.assertEqual(r["config_warnings"][1]["decision"], "repeated_warning")
        self.assertFalse(r["model_turn_request_sent"])
        self.assertNotIn("model/list", r["requests_sent"])

    def test_known_warning_is_preserved_when_subsequent_existing_admission_fails(self):
        for scenario in ("bad_config", "managed_requirements", "no_model", "full_quota", "api_account"):
            with self.subTest(scenario=scenario):
                r = self.warning_case(scenario=scenario)
                self.assertEqual(r["status"], "STOPPED_WITHOUT_VERDICT", r)
                self.assertTrue(r["config_warnings"][0]["admitted"])
                self.assertFalse(r["model_turn_request_sent"])
                self.assertFalse(r["observed_refusal"])
                self.assertTrue(r["native_process_reaped"])
                self.assertNotIn(s.config_warning.MISSING_BWRAP_SUMMARY, json.dumps(r))

    def test_real_broker_refuses_actual_forbidden_call_after_successful_read(self):
        r = self.run_case()
        self.assertEqual(r["status"], "SYNTHETIC_REFUSAL_OBSERVED", r)
        self.assertTrue(r["synthetic_allowed_read_observed"])
        self.assertTrue(r["observed_refusal"])
        self.assertEqual(r["server_requests_dispatched"], 1)
        self.assertEqual(len(r["broker_receipts"]), 1)
        self.assertEqual(r["selected_binding"], BINDING)
        self.assertGreaterEqual(r["early_frames_buffered"], 3)
        self.assertTrue(r["native_process_reaped"])
        self.assertFalse(r["native_tool_inventory_attested"])

    def test_all_fixed_metadata_and_only_fresh_start_turn(self):
        r = self.run_case()
        self.assertEqual(r["requests_sent"], ["initialize", "config/read", "configRequirements/read",
            "account/read", "account/rateLimits/read", "model/list", "thread/start", "turn/start"])
        self.assertTrue(r["model_catalog"]["include_hidden_requested"])
        self.assertFalse(r["unattended_model_use_authorized"])

    def test_required_model_and_profile_refusals_precede_thread_and_prompt(self):
        for case in ("no_model", "full_quota", "bad_config", "api_account", "rpc_error"):
            with self.subTest(case=case):
                r = self.run_case(case)
                self.assertEqual(r["status"], "STOPPED_WITHOUT_VERDICT")
                self.assertFalse(r["thread_request_sent"])
                self.assertFalse(r["model_turn_request_sent"])
                self.assertFalse(r["observed_refusal"])
        r = self.run_case("no_model")
        self.assertEqual(r["model_catalog"]["entries"][0]["model"], "other-model")

    def test_same_profile_startup_settings_event_and_changed_model_refusal(self):
        r = self.run_case("same_settings")
        self.assertEqual(r["status"], "SYNTHETIC_REFUSAL_OBSERVED", r)
        self.assertEqual(r["notifications"]["thread/settings/updated"], 1)
        r = self.run_case("changed_settings")
        self.assertEqual(r["status"], "STOPPED_WITHOUT_VERDICT")
        self.assertEqual(r["server_requests_dispatched"], 0)

    def test_nonnull_requirements_preserved_safely_and_stop_before_account_or_model(self):
        r = self.run_case("managed_requirements")
        self.assertEqual(r["status"], "STOPPED_WITHOUT_VERDICT")
        self.assertTrue(r["requirements"]["requirements_field_present"])
        self.assertTrue(r["requirements"]["requirements_present"])
        self.assertFalse(r["thread_request_sent"])
        self.assertFalse(r["model_turn_request_sent"])
        self.assertNotIn("account/read", r["requests_sent"])
        self.assertNotIn("UNRETAINED_MANAGED_SOURCE", json.dumps(r))
        self.assertTrue(r["native_process_reaped"])

    def test_two_page_catalog_finishes_before_selection_without_retaining_cursor(self):
        r = self.run_case("two_pages")
        self.assertEqual(r["status"], "SYNTHETIC_REFUSAL_OBSERVED", r)
        self.assertEqual(r["requests_sent"].count("model/list"), 2)
        self.assertEqual(r["model_catalog"]["total_entry_count"], 2)
        self.assertTrue(r["catalog_pagination"]["complete"])
        self.assertEqual(r["catalog_pagination"]["pages_validated"], 2)
        self.assertEqual(r["selected_binding"], BINDING)
        self.assertNotIn("OPAQUE_CURSOR", json.dumps(r))

    def test_catalog_cursor_identity_and_page_refusals_preserve_partial_progress(self):
        for case, count in (("repeated_cursor", 2), ("duplicate_model_id", 2),
                            ("invalid_cursor", 1), ("catalog_page_ceiling", 8)):
            with self.subTest(case=case):
                r = self.run_case(case)
                self.assertEqual(r["status"], "STOPPED_WITHOUT_VERDICT")
                self.assertEqual(r["catalog_pagination"]["pages_received"], count)
                self.assertFalse(r["catalog_pagination"]["complete"])
                self.assertFalse(r["model_catalog"]["pagination_complete"])
                self.assertFalse(r["thread_request_sent"])
                self.assertNotIn("OPAQUE", json.dumps(r))

    def test_changed_account_plan_is_preserved_and_stops_before_model(self):
        r = self.run_case("changed_plan")
        self.assertEqual(r["status"], "STOPPED_WITHOUT_VERDICT")
        self.assertEqual(r["contained_account"]["reported_plan_type"], "enterprise")
        self.assertNotIn("model/list", r["requests_sent"])
        self.assertFalse(r["model_turn_request_sent"])

    def test_thread_response_controls_fail_before_science_input(self):
        r = self.run_case("thread_fallback")
        self.assertTrue(r["thread_request_sent"])
        self.assertFalse(r["model_turn_request_sent"])
        self.assertEqual(r["status"], "STOPPED_WITHOUT_VERDICT")

    def test_early_foreign_ids_and_unknown_authority_never_dispatch(self):
        for case in ("foreign_thread", "foreign_turn", "namespace", "unknown_tool", "unknown_early",
                     "early_overflow", "unexpected_event", "unsafe_item", "foreign_user_item", "bad_response_id"):
            with self.subTest(case=case):
                r = self.run_case(case)
                self.assertEqual(r["status"], "STOPPED_WITHOUT_VERDICT", r)
                self.assertEqual(r["server_requests_dispatched"], 0)
                self.assertFalse(r["observed_refusal"])
                self.assertTrue(r["native_process_reaped"])

    def test_replay_or_wrong_challenge_never_count_as_observed_refusal(self):
        for case in ("replay_rpc", "replay_call", "wrong_forbidden", "forbidden_first"):
            with self.subTest(case=case):
                r = self.run_case(case)
                self.assertEqual(r["status"], "STOPPED_WITHOUT_VERDICT")
                self.assertFalse(r["observed_refusal"])

    def test_source_typed_timestamp_envelope_rejects_boolean(self):
        r = self.run_case("bad_timestamp")
        self.assertEqual(r["status"], "STOPPED_WITHOUT_VERDICT")
        self.assertFalse(r["model_turn_request_sent"])

    def test_no_native_diagnostics_or_account_fields_escape(self):
        for case in ("success", "rpc_error", "unknown_early"):
            r = self.run_case(case)
            text = json.dumps(r)
            for excluded in ("SECRET_DIAGNOSTIC", "SECRET_ACCOUNT", "DISCARDED_EMAIL", "NEVER_ECHO_NATIVE"):
                self.assertNotIn(excluded, text)
            self.assertFalse(r["streams"]["stdout"]["hashed"])
            self.assertFalse(r["streams"]["stderr"]["raw_saved"])

    def test_science_requires_accepted_synthetic_binding_before_process(self):
        r = self.run_case(mode="science")
        self.assertFalse(r["client_started"])
        self.assertEqual(r["status"], "STOPPED_WITHOUT_VERDICT")

    def test_science_binding_mismatch_stops_before_thread(self):
        r = self.run_case(mode="science", expected_binding={**BINDING, "effort": "high"})
        self.assertTrue(r["client_started"])
        self.assertFalse(r["thread_request_sent"])

    def test_real_broker_writes_exclusive_unmodified_verdict(self):
        f = Fixture("science")
        try:
            r = f.invoke(mode="science", expected_binding=BINDING)
            self.assertEqual(r["status"], "VERDICT_SUBMITTED", r)
            self.assertTrue(r["verdict_submitted"])
            saved = f.output / s.broker_module.VERDICT_NAME
            self.assertEqual(json.loads(saved.read_bytes())["reviewer_verdict"], f.verdict)
            self.assertEqual(saved.stat().st_mode & 0o777, 0o400)
            self.assertTrue(r["native_process_reaped"])
        finally: f.close()

    def test_timeout_kills_and_reaps_silent_child(self):
        r = self.run_case("quiet", wall_seconds=5)
        self.assertEqual(r["status"], "STOPPED_WITHOUT_VERDICT")
        self.assertTrue(r["native_process_reaped"])
        self.assertLess(r["elapsed_seconds"], 5.5)

    def test_large_broker_image_cannot_block_finite_stdin_deadline(self):
        r = self.run_case("pipe_stall", mode="science", expected_binding=BINDING, wall_seconds=5)
        self.assertEqual(r["status"], "STOPPED_WITHOUT_VERDICT")
        self.assertEqual(r["server_requests_dispatched"], 1)
        self.assertTrue(r["native_process_reaped"])
        self.assertLess(r["elapsed_seconds"], 5.5)

    def test_call_budget_is_terminal(self):
        r = self.run_case(max_calls=1)
        self.assertEqual(r["status"], "STOPPED_WITHOUT_VERDICT")
        self.assertFalse(r["observed_refusal"])

    def test_same_named_broker_error_elsewhere_is_not_canary_denial(self):
        f = Fixture("success")
        try:
            with s.broker_module.ReviewBroker(f.packet, manifest_sha256=f.pin, output_root=f.output) as b:
                witness = s._BrokerWitness(b, "synthetic", s.time.monotonic() + 100)
                witness.dispatch("read_text", s.SYNTHETIC_READ)
                with mock.patch.object(b, "dispatch", side_effect=s.broker_module.BrokerError("Not a path failure")):
                    with self.assertRaises(s.broker_module.BrokerError):
                        witness.dispatch("read_text", s.SYNTHETIC_FORBIDDEN)
                self.assertFalse(witness.observed_refusal)
        finally: f.close()

    def test_module_import_with_python_isolation_needs_no_script_search_path(self):
        code = "import importlib.util; p=" + repr(str(ROOT / "scripts/p3_reviewer_session_021.py")) + "; s=importlib.util.spec_from_file_location('session_isolation_test',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(m.CLEANUP_SECONDS)"
        result = subprocess.run([sys.executable, "-I", "-B", "-c", code], capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertEqual(result.stdout, b"4\n")


if __name__ == "__main__": unittest.main()
