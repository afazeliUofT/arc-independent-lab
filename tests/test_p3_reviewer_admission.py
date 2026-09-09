"""Synthetic admission refusals and exact embedded native payload schemas."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import p3_reviewer_admission as a
from p3_review_broker import dynamic_tool_specs
from p3_reviewer_profile import reviewer_overrides
from gate0_client_preflight import overrides
try:
    import jsonschema
except ImportError:
    jsonschema = None


CWD = "/home/example/ARC_Independent_Lab/delivery/reviewer/runtime"
MODEL = "gpt-6-astra"
EFFORT = "ultra"
SCHEMAS = {
    "v2/ThreadStartParams.json": "25f490368ec6df52a2a3b82a5469d2413307eb93439121b309f415b5648eee7a",
    "v2/TurnStartParams.json": "b36fb37326b1cf69f75c8b306f1f886d53a57c4b1b985e08e298e2407ea2ad02",
}


def profile():
    return reviewer_overrides(overrides(Path(CWD)),
        (ROOT / "artifacts/GATE0_CODEX_INTERFACE/20260907_001/config-schema.json").read_bytes())


def nested(flat):
    out = {}
    for key, value in flat.items():
        target = out
        bits = key.split(".")
        for bit in bits[:-1]:
            target = target.setdefault(bit, {})
        target[bits[-1]] = copy.deepcopy(value)
    return out


def fixture():
    p = profile()
    config = nested(p)
    origins = {key: {"name": {"type": "sessionFlags"}, "version": "session-v1"}
               for dotted, value in p.items() for key, leaf in a._leaves(dotted, value)}
    raw = {"config": copy.deepcopy(config), "origins": origins,
           "layers": [{"name": {"type": "sessionFlags"}, "version": "session-v1",
                       "config": config, "disabledReason": None}]}
    raw["config"].pop("tools")
    return raw


def catalog():
    return {"response_shape_recognized": True, "page_complete_for_returned_catalog": True,
            "additional_page_available": False, "entries": [
                {"model": MODEL, "id": "model-native-id", "supported_efforts": ["low", "high", "ultra"],
                 "unrecognized_effort_count": 0}]}


def thread():
    return {"model": MODEL, "modelProvider": "openai", "reasoningEffort": EFFORT,
            "approvalPolicy": "never", "approvalsReviewer": "user",
            "activePermissionProfile": {"id": ":read-only", "extends": None},
            "sandbox": {"type": "readOnly", "networkAccess": False},
            "cwd": CWD, "runtimeWorkspaceRoots": [], "instructionSources": [],
            "thread": {"id": "thread-one", "sessionId": "session-one", "ephemeral": True,
                "cwd": CWD, "modelProvider": "openai", "cliVersion": "0.151.0", "turns": [],
                "preview": "", "status": {"type": "idle"}, "forkedFromId": None,
                "parentThreadId": None, "projectId": None, "path": None,
                "agentNickname": None, "agentRole": None}}


class AdmissionTests(unittest.TestCase):
    @unittest.skipIf(jsonschema is None, "Optional jsonschema package is unavailable")
    def test_exact_native_payload_schemas(self):
        raw = json.loads((ROOT / "artifacts/GATE0_CODEX_INTERFACE/20260907_001/schemas/experimental.json").read_text())
        payloads = {"v2/ThreadStartParams.json": a.thread_params(MODEL, EFFORT, CWD, dynamic_tool_specs(), profile()),
                    "v2/TurnStartParams.json": a.turn_params("thread-one", MODEL, EFFORT, "Read PACKET_INDEX.json.")}
        for name, expected in SCHEMAS.items():
            self.assertEqual(hashlib.sha256(raw[name].encode()).hexdigest(), expected)
            jsonschema.Draft7Validator(json.loads(raw[name])).validate(payloads[name])

    def test_embedded_schema_required_fields_and_enums(self):
        raw = json.loads((ROOT / "artifacts/GATE0_CODEX_INTERFACE/20260907_001/schemas/experimental.json").read_text())
        t = a.thread_params(MODEL, EFFORT, CWD, dynamic_tool_specs(), profile())
        v = a.turn_params("thread-one", MODEL, EFFORT, "Read PACKET_INDEX.json.")
        for name, payload in [("v2/ThreadStartParams.json", t), ("v2/TurnStartParams.json", v)]:
            self.assertEqual(hashlib.sha256(raw[name].encode()).hexdigest(), SCHEMAS[name])
            schema = json.loads(raw[name])
            self.assertLessEqual(set(schema.get("required", [])), set(payload))
            self.assertLessEqual(set(payload), set(schema["properties"]))
        ts = json.loads(raw["v2/ThreadStartParams.json"])
        self.assertIn(t["sessionStartSource"], ts["definitions"]["ThreadStartSource"]["enum"])
        turn = json.loads(raw["v2/TurnStartParams.json"])
        text_spec = next(x for x in turn["definitions"]["UserInput"]["oneOf"]
                         if x["properties"]["type"]["enum"] == ["text"])
        self.assertLessEqual(set(text_spec["required"]), set(v["input"][0]))
        self.assertEqual(text_spec["properties"]["text"]["type"], "string")

    def test_select_only_exact_model_highest_effort(self):
        c = catalog()
        c["entries"].insert(0, {"model": "other-model", "id": "other"})
        self.assertEqual(a.select_model(c), {"model": MODEL, "id": "model-native-id", "effort": "ultra"})

    def test_completed_multi_page_catalog_selects_exact_model(self):
        c = catalog()
        c["entries"] = [{"model": "other-model-" + str(i), "id": "other-" + str(i)}
                        for i in range(799)] + c["entries"]
        self.assertEqual(a.select_model(c)["model"], MODEL)
        c["entries"].insert(0, {"model": "overflow", "id": "overflow"})
        with self.assertRaises(a.Stop): a.select_model(c)

    def test_id_only_match_does_not_select(self):
        c = catalog(); c["entries"][0].update(model="other-model", id=MODEL)
        with self.assertRaises(a.Stop): a.select_model(c)

    def test_partial_catalog_denied(self):
        c = catalog(); c["additional_page_available"] = True
        with self.assertRaises(a.Stop): a.select_model(c)

    def test_ambiguous_model_denied(self):
        c = catalog(); c["entries"].append(copy.deepcopy(c["entries"][0]))
        with self.assertRaises(a.Stop): a.select_model(c)

    def test_unknown_effort_no_order_guess(self):
        c = catalog(); c["entries"][0]["unrecognized_effort_count"] = 1
        with self.assertRaises(a.Stop): a.select_model(c)

    def test_model_fallback_and_bad_path_denied(self):
        for model, path in [("other-model", CWD), (MODEL, CWD + "/../escape")]:
            with self.assertRaises(a.Stop):
                a.thread_params(model, EFFORT, path, dynamic_tool_specs(), profile())

    def test_payload_copies_profile_and_tools(self):
        p, tools = profile(), dynamic_tool_specs()
        params = a.thread_params(MODEL, EFFORT, CWD, tools, p)
        params["config"]["features.code_mode"]["enabled"] = True
        params["dynamicTools"][0]["inputSchema"]["properties"] = {}
        self.assertFalse(p["features.code_mode"]["enabled"])
        self.assertTrue(tools[0]["inputSchema"]["properties"])

    def test_unadvertised_dynamic_tool_denied(self):
        tools = dynamic_tool_specs(); tools[0]["name"] = "exec_command"
        with self.assertRaises(a.Stop): a.thread_params(MODEL, EFFORT, CWD, tools, profile())

    def test_profile_host_table_not_boolean_denied(self):
        p = profile(); p["features.code_mode_host"] = {"enabled": False, "disable_in_process_fallback": True}
        with self.assertRaises(a.Stop): a.thread_params(MODEL, EFFORT, CWD, dynamic_tool_specs(), p)

    def test_valid_thread_is_not_global_freshness_proof(self):
        r = a.validate_thread_response(thread(), model=MODEL, effort=EFFORT, cwd=CWD)
        self.assertEqual(r["thread_id"], "thread-one")
        self.assertFalse(r["full_fresh_context_verified"])

    def test_thread_provenance_control_refusals(self):
        changes = [("model", "other"), ("modelProvider", "paid-provider"),
                   ("reasoningEffort", "low"), ("approvalPolicy", "on-request"),
                   ("approvalsReviewer", "auto_review"), ("runtimeWorkspaceRoots", [CWD]),
                   ("instructionSources", ["/home/private/AGENTS.md"])]
        for key, value in changes:
            with self.subTest(key=key):
                r = thread(); r[key] = value
                with self.assertRaises(a.Stop): a.validate_thread_response(r, model=MODEL, effort=EFFORT, cwd=CWD)
        for key, value in [("ephemeral", False), ("parentThreadId", "parent"),
                           ("forkedFromId", "fork"), ("path", "/session.jsonl")]:
            with self.subTest(key=key):
                r = thread(); r["thread"][key] = value
                with self.assertRaises(a.Stop): a.validate_thread_response(r, model=MODEL, effort=EFFORT, cwd=CWD)

    def test_unpinned_instruction_allowlist_denied(self):
        with self.assertRaises(a.Stop):
            a.validate_thread_response(thread(), model=MODEL, effort=EFFORT, cwd=CWD,
                                       allowed_instruction_sources=("/unverified/AGENTS.md",))

    def test_bool_not_integer_network_control(self):
        r = thread(); r["sandbox"]["networkAccess"] = 0
        with self.assertRaises(a.Stop): a.validate_thread_response(r, model=MODEL, effort=EFFORT, cwd=CWD)

    def test_exact_readonly_wire_has_no_uninspected_access_extension(self):
        raw = json.loads((ROOT / "artifacts/GATE0_CODEX_INTERFACE/20260907_001/schemas/experimental.json").read_text())
        pins = {"v2/ThreadStartResponse.json": "b9a37d1a1d9349a2f034a68a943635ea6aaaec0165e69c4380564752324158ef",
                "v2/ThreadSettingsUpdatedNotification.json": "f7865eabaa34c7895a1ae345e51c1ba181a63c649237d36583b80f9d759b0f53"}
        for name, pin in pins.items():
            self.assertEqual(hashlib.sha256(raw[name].encode()).hexdigest(), pin)
            schema = json.loads(raw[name])
            readonly = next(item for item in schema["definitions"]["SandboxPolicy"]["oneOf"]
                            if item["properties"]["type"]["enum"] == ["readOnly"])
            self.assertEqual(set(readonly["properties"]), {"type", "networkAccess"})
            self.assertEqual(readonly["properties"]["networkAccess"], {"default": False, "type": "boolean"})
        r = thread(); r["sandbox"]["readOnlyAccess"] = {"type": "unverified"}
        with self.assertRaises(a.Stop):
            a.validate_thread_response(r, model=MODEL, effort=EFFORT, cwd=CWD)
        settings = self.settings_fixture()
        settings["threadSettings"]["sandboxPolicy"]["readOnlyAccess"] = {"type": "unverified"}
        with self.assertRaises(a.Stop):
            a.validate_thread_settings(settings, thread_id="thread-one", model=MODEL, effort=EFFORT, cwd=CWD)

    def test_effective_source_controls_and_api_omission(self):
        r = a.validate_effective_config(fixture(), profile())
        self.assertTrue(r["all_requested_controls_verified"])
        self.assertTrue(r["projected_tool_controls"]["all_two_controls_verified_false"])
        self.assertFalse(r["runtime_tool_registry_verified"])

    def test_higher_enabled_shadow_denied(self):
        r = fixture(); r["layers"].insert(0, {"name": {"type": "enterpriseManaged"},
            "version": "higher", "config": {"features": {"code_mode_host": True}}})
        with self.assertRaises(a.Stop): a.validate_effective_config(r, profile())

    def test_disabled_higher_shadow_is_not_effective(self):
        r = fixture(); r["layers"].insert(0, {"name": {"type": "project"}, "version": "disabled",
            "disabledReason": "synthetic untrusted", "config": {"features": {"code_mode_host": True}}})
        self.assertTrue(a.validate_effective_config(r, profile())["all_requested_controls_verified"])

    def test_layer_and_projected_nested_fallback_denied(self):
        for target in ("layer", "projection"):
            with self.subTest(target=target):
                r = fixture(); cfg = r["layers"][0]["config"] if target == "layer" else r["config"]
                cfg["features"]["code_mode_host"] = {"enabled": False, "disable_in_process_fallback": True}
                with self.assertRaises(a.Stop): a.validate_effective_config(r, profile())

    def test_source_version_and_origin_spoof_denied(self):
        for key, value in [("version", "incorrect"), ("name", {"type": "user", "file": "/secret"})]:
            r = fixture(); r["origins"]["features.code_mode.enabled"][key] = value
            with self.assertRaises(a.Stop): a.validate_effective_config(r, profile())

    def test_secret_instruction_fields_filtered_and_denied(self):
        secret = "SECRET_SHOULD_NOT_APPEAR"
        for source in ("layer", "projection"):
            r = fixture()
            if source == "layer":
                r["layers"].append({"name": {"type": "user", "file": "/private/config"},
                    "version": "user", "config": {"model_instructions_file": secret}})
            else:
                r["config"]["developer_instructions"] = secret
            with self.assertRaises(a.Stop) as caught: a.validate_effective_config(r, profile())
            self.assertNotIn(secret, str(caught.exception))

    def test_isolated_python_sibling_imports(self):
        completed = subprocess.run([sys.executable, "-I", "-B", str(ROOT / "scripts/p3_reviewer_admission.py")],
                                   capture_output=True, timeout=10)
        self.assertEqual(completed.returncode, 0, completed.stderr.decode())
        self.assertEqual(completed.stdout, b"")

    @staticmethod
    def settings_fixture():
        r = thread()
        return {"threadId": r["thread"]["id"], "threadSettings": {
            "activePermissionProfile": r["activePermissionProfile"],
            "approvalPolicy": r["approvalPolicy"], "approvalsReviewer": r["approvalsReviewer"],
            "cwd": CWD, "effort": EFFORT, "model": MODEL, "modelProvider": "openai",
            "sandboxPolicy": r["sandbox"], "multiAgentMode": "explicitRequestOnly",
            "collaborationMode": {"mode": "default", "settings": {
                "model": MODEL, "reasoning_effort": EFFORT, "developer_instructions": None}}}}

    def test_same_control_thread_settings_event_accepted(self):
        r = a.validate_thread_settings(self.settings_fixture(), thread_id="thread-one",
                                       model=MODEL, effort=EFFORT, cwd=CWD)
        self.assertTrue(r["settings_match_admitted_controls"])
        raw = json.loads((ROOT / "artifacts/GATE0_CODEX_INTERFACE/20260907_001/schemas/experimental.json").read_text())
        schema = json.loads(raw["v2/ThreadSettingsUpdatedNotification.json"])
        required = set(schema["definitions"]["ThreadSettings"]["required"])
        self.assertLessEqual(required, set(self.settings_fixture()["threadSettings"]))
        if jsonschema is not None:
            jsonschema.Draft7Validator(schema).validate(self.settings_fixture())

    def test_settings_control_changes_denied(self):
        changes = [("model", "other"), ("modelProvider", "other"), ("effort", "low"),
                   ("approvalPolicy", "on-request"), ("approvalsReviewer", "auto_review"),
                   ("cwd", "/elsewhere"), ("sandboxPolicy", {"type": "workspaceWrite"}),
                   ("activePermissionProfile", {"id": ":workspace"})]
        for key, value in changes:
            with self.subTest(key=key):
                r = self.settings_fixture(); r["threadSettings"][key] = value
                with self.assertRaises(a.Stop):
                    a.validate_thread_settings(r, thread_id="thread-one", model=MODEL, effort=EFFORT, cwd=CWD)
        r = self.settings_fixture(); r["threadId"] = "foreign"
        with self.assertRaises(a.Stop):
            a.validate_thread_settings(r, thread_id="thread-one", model=MODEL, effort=EFFORT, cwd=CWD)

    def test_settings_collaboration_and_secret_override_denied(self):
        for key, value in [("model", "other"), ("reasoning_effort", "low"),
                           ("developer_instructions", "SECRET_DO_NOT_REPORT")]:
            r = self.settings_fixture(); r["threadSettings"]["collaborationMode"]["settings"][key] = value
            with self.assertRaises(a.Stop) as caught:
                a.validate_thread_settings(r, thread_id="thread-one", model=MODEL, effort=EFFORT, cwd=CWD)
            self.assertNotIn("SECRET_DO_NOT_REPORT", str(caught.exception))

    def test_turn_input_rejects_surrogates(self):
        with self.assertRaises(a.Stop): a.turn_params("thread-one", MODEL, EFFORT, "bad\ud800")


if __name__ == "__main__":
    unittest.main()
