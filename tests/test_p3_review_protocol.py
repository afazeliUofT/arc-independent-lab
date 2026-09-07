"""Protocol refusal cases use synthetic messages, never a Codex/model process."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("p3_review_protocol", ROOT / "scripts/p3_review_protocol.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class StubBroker:
    def __init__(self):
        self.calls = []

    def dispatch(self, tool, args):
        self.calls.append((tool, args))
        if tool == "read_page_image":
            return {"mimeType": "image/png", "data_base64": "aW1hZ2U=", "sha256": "a" * 64}
        return {"sha256": "a" * 64}


def request(**changes):
    p = {"arguments": {"path": "proof.txt"}, "callId": "call1", "threadId": "thread1",
         "turnId": "turn1", "tool": "hash_file"}
    p.update(changes)
    return {"id": 1, "method": "item/tool/call", "params": p}


class BoundaryCases(unittest.TestCase):
    def boundary(self, **kwargs):
        return m.DynamicToolBoundary(StubBroker(), thread_id="thread1", turn_id="turn1", **kwargs)

    def test_valid_response_shape(self):
        b = self.boundary()
        response = json.loads(b.handle(json.dumps(request()).encode()))
        self.assertTrue(response["result"]["success"])
        self.assertEqual(response["result"]["contentItems"][0]["type"], "inputText")
        self.assertEqual(len(b.broker.calls), 1)

    def test_every_other_exact_server_request_refused_without_dispatch(self):
        schema = json.loads(json.loads((ROOT / "artifacts/GATE0_CODEX_INTERFACE/20260907_001/schemas/experimental.json").read_text())["ServerRequest.json"])
        methods = [x["properties"]["method"]["enum"][0] for x in schema["oneOf"]]
        self.assertIn("item/tool/call", methods)
        for method in methods + ["future/unknown"]:
            if method == "item/tool/call":
                continue
            with self.subTest(method=method):
                b = self.boundary(); value = request(); value["method"] = method
                with self.assertRaises(m.ProtocolStop): b.handle(json.dumps(value).encode())
                self.assertFalse(b.broker.calls)
                self.assertTrue(b.stopped)

    def test_foreign_bindings_unknown_namespace_and_tools(self):
        for change in ({"threadId": "other"}, {"turnId": "other"}, {"namespace": "other"},
                       {"tool": "exec_command"}, {"tool": ["hash_file"]}, {"arguments": "{}"},
                       {"callId": True}, {"extra": False}):
            with self.subTest(change=change):
                b = self.boundary()
                with self.assertRaises(m.ProtocolStop): b.handle(json.dumps(request(**change)).encode())
                self.assertFalse(b.broker.calls)

    def test_replay_call_or_rpc_identifier(self):
        for change_call in (False, True):
            b = self.boundary(); first = request()
            b.handle(json.dumps(first).encode())
            second = request()
            if change_call: second["params"]["callId"] = "call2"
            else: second["id"] = 2
            with self.assertRaises(m.ProtocolStop): b.handle(json.dumps(second).encode())
            self.assertEqual(len(b.broker.calls), 1)

    def test_duplicate_fields_and_nonfinite_and_boolean_id(self):
        messages = [b'{"id":1,"id":2}', b'{"id":NaN}', b'[]', b'\xff']
        value = request(); value["id"] = True; messages.append(json.dumps(value).encode())
        for raw in messages:
            with self.subTest(raw=raw):
                b = self.boundary()
                with self.assertRaises(m.ProtocolStop): b.handle(raw)
                self.assertFalse(b.broker.calls)

    def test_work_limits_and_terminal_failure(self):
        now = [0]
        b = self.boundary(clock=lambda: now[0], wall_seconds=1)
        now[0] = 1
        with self.assertRaises(m.ProtocolStop): b.handle(json.dumps(request()).encode())
        with self.assertRaises(m.ProtocolStop): b.handle(json.dumps(request()).encode())
        b = self.boundary(max_calls=1)
        b.handle(json.dumps(request()).encode())
        value = request(callId="call2"); value["id"] = 2
        with self.assertRaises(m.ProtocolStop): b.handle(json.dumps(value).encode())

    def test_oversized_request(self):
        b = self.boundary()
        with self.assertRaises(m.ProtocolStop): b.handle(b" " * (m.MAX_REQUEST_BYTES + 1))
        self.assertFalse(b.broker.calls)

    def test_image_transport_uses_data_uri(self):
        b = self.boundary()
        result = json.loads(b.handle(json.dumps(request(tool="read_page_image")).encode()))
        self.assertEqual(result["result"]["contentItems"][1]["imageUrl"], "data:image/png;base64,aW1hZ2U=")

    def test_exclusive_end_of_review(self):
        b = self.boundary()
        b.handle(json.dumps(request(tool="submit_verdict")).encode())
        self.assertTrue(b.finished)
        with self.assertRaises(m.ProtocolStop): b.handle(json.dumps(request()).encode())

    def test_error_contains_no_raw_input(self):
        b = self.boundary(); value = request(); value["method"] = "secret_marker"
        with self.assertRaises(m.ProtocolStop) as e: b.handle(json.dumps(value).encode())
        self.assertNotIn("secret_marker", str(e.exception))
        self.assertFalse(b.receipts)


if __name__ == "__main__":
    unittest.main(verbosity=2)
