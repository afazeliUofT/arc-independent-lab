"""Synthetic finite process tests. No Codex, bwrap, model or network executes."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("gate0_client_preflight", ROOT / "scripts/gate0_client_preflight.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

CHILD = r'''
import sys,json
for line in sys.stdin:
 p=json.loads(line)
 if 'id' not in p: continue
 if p['method']=='config/read': result={'config':{'features':{'plugins':False},'secret':'must_not_leak'},'origins':{},'layers':[]}
 elif p['method']=='configRequirements/read': result={'requirements':None}
 else: result={'userAgent':'synthetic'}
 print(json.dumps({'id':p['id'],'result':result}),flush=True)
'''


class PreflightCases(unittest.TestCase):
    def execute(self, child):
        with tempfile.TemporaryDirectory(dir=ROOT / "delivery", prefix="client-preflight-test-") as d:
            return m.observe({"argv": [sys.executable, "-I", "-B", "-c", child]}, Path(d),
                             {"features.plugins": False})

    def test_only_three_allowed_requests_and_no_raw_config(self):
        result = self.execute(CHILD)
        self.assertEqual(result["requests_sent"], ["initialize", "config/read", "configRequirements/read"])
        self.assertEqual(result["status"], "OBSERVED_STARTUP_AND_CONFIG_RESPONSES_ONLY")
        self.assertFalse(result["requirements_verified"])
        self.assertNotIn("must_not_leak", json.dumps(result))
        self.assertFalse(result["thread_or_model_request_sent"])

    def test_server_approval_auth_tool_request_rejected(self):
        for method in ("item/tool/call", "account/chatgptAuthTokens/refresh", "item/permissions/requestApproval"):
            with self.subTest(method=method):
                child = "import json,time; print(json.dumps({'id':44,'method':" + repr(method) + ",'params':{'secret':'must_not_leak'}}),flush=True);time.sleep(2)"
                result = self.execute(child)
                self.assertEqual(result["status"], "STOPPED_WITHOUT_REVIEW")
                self.assertEqual(result["server_requests_dispatched"], 0)
                self.assertNotIn("must_not_leak", json.dumps(result))

    def test_foreign_response_and_error_without_disclosure(self):
        for payload in ({"id": 9, "result": {}}, {"id": 1, "error": {"message": "must_not_leak"}},
                        {"id": True, "result": {}}, {"id": 1, "result": []}):
            with self.subTest(payload=payload):
                result = self.execute("import json;print(" + repr(json.dumps(payload)) + ",flush=True)")
                self.assertEqual(result["status"], "STOPPED_WITHOUT_REVIEW")
                self.assertNotIn("must_not_leak", json.dumps(result))

    def test_deadline_output_limit_and_early_exit(self):
        old_wall, old_stream = m.WALL_SECONDS, m.STREAM_LIMIT
        try:
            m.WALL_SECONDS, m.STREAM_LIMIT = .25, 1024
            for child in ("import time;time.sleep(2)", "print('x'*2048,flush=True)", "raise SystemExit(3)"):
                result = self.execute(child)
                self.assertEqual(result["status"], "STOPPED_WITHOUT_REVIEW")
        finally:
            m.WALL_SECONDS, m.STREAM_LIMIT = old_wall, old_stream

    def test_duplicate_json_and_nonfinite_rejected(self):
        for payload in (b'{"id":1,"id":2}', b'{"id":NaN}', b'[]'):
            with self.assertRaises(m.Stop): m.parse_line(payload)

    def test_config_filter_does_not_serialize_unexpected_values(self):
        result = m.safe_config({"config": {"features": {"plugins": "must_not_leak"}}}, {"features.plugins": False})
        self.assertFalse(result["all_requested_controls_observed"])
        self.assertNotIn("must_not_leak", json.dumps(result))

    def test_environment_keeps_original_home_excludes_credentials(self):
        from unittest.mock import patch
        with patch.dict(m.os.environ, {"HOME": "/unchanged", "CODEX_HOME": "/also-unchanged", "OPENAI_API_KEY": "must_not_leak"}):
            result = m.restricted_env()
            self.assertEqual(result["HOME"], "/unchanged")
            self.assertEqual(result["CODEX_HOME"], "/also-unchanged")
            self.assertNotIn("OPENAI_API_KEY", result)

    def test_override_paths_types_and_enums_match_pinned_schema(self):
        # Narrow validation of exactly the scalar overrides we emit. This is
        # intentionally not a general JSON Schema implementation/dependency.
        schema = json.loads((ROOT / "artifacts/GATE0_CODEX_INTERFACE/20260907_001/config-schema.json").read_text())
        def expand(node):
            if "$ref" in node:
                return expand(schema["definitions"][node["$ref"].split("/")[-1]])
            if "allOf" in node:
                result = dict(node)
                for child in node["allOf"]: result.update(expand(child))
                result.pop("allOf", None)
                return result
            return node
        def accepts(node, value):
            node = expand(node)
            for keyword in ("anyOf", "oneOf"):
                if keyword in node: return any(accepts(child, value) for child in node[keyword])
            if "enum" in node and value not in node["enum"]: return False
            kind = node.get("type")
            if kind == "boolean": return type(value) is bool
            if kind == "string": return type(value) is str
            return False
        for key, value in m.overrides(ROOT / "delivery/synthetic").items():
            node = schema
            for component in key.split("."):
                node = expand(node)["properties"][component]
            self.assertTrue(accepts(node, value), key)


if __name__ == "__main__": unittest.main(verbosity=2)
