"""Protocol refusal cases use synthetic messages, never a Codex/model process."""
import importlib.util
import json
from pathlib import Path
import unittest
import tempfile
import hashlib

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT / 'scripts'))
import p3_review_protocol_028 as m
import p3_review_interface_028 as interface



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


    def test_input_error_response_is_failed_bounded_and_correctable(self):
        b = self.boundary()
        b.broker.dispatch = lambda *_: (_ for _ in ()).throw(interface.ToolInputError('integer_bounds'))
        response = json.loads(b.handle(json.dumps(request()).encode()))
        self.assertFalse(response['result']['success'])
        error = json.loads(response['result']['contentItems'][0]['text'])
        self.assertEqual(error, interface.ToolInputError('integer_bounds').as_dict())
        self.assertFalse(b.finished)
        self.assertFalse(b.stopped)
        self.assertEqual(b.recoverable_input_errors, 1)
        self.assertEqual(b.failed_calls, 1)
        self.assertFalse(b.receipts[0]['successful'])
        b.broker = StubBroker()
        second = request(callId='call2'); second['id'] = 2
        self.assertTrue(json.loads(b.handle(json.dumps(second).encode()))['result']['success'])
        self.assertEqual(b.recoverable_input_errors, 1)

    def test_failed_submit_does_not_finish_and_valid_submit_does(self):
        b = self.boundary()
        b.broker.dispatch = lambda *_: (_ for _ in ()).throw(interface.ToolInputError('bounded_text'))
        first = request(tool='submit_verdict')
        self.assertFalse(json.loads(b.handle(json.dumps(first).encode()))['result']['success'])
        self.assertFalse(b.finished)
        b.broker = StubBroker()
        second = request(tool='submit_verdict', callId='call2'); second['id'] = 2
        self.assertTrue(json.loads(b.handle(json.dumps(second).encode()))['result']['success'])
        self.assertTrue(b.finished)

    def test_failed_valid_calls_consume_work_budget_and_identities(self):
        for replay in ('id', 'call', 'ceiling'):
            b = self.boundary(max_calls=1 if replay == 'ceiling' else 5)
            b.broker.dispatch = lambda *_: (_ for _ in ()).throw(interface.ToolInputError('bounded_text'))
            b.handle(json.dumps(request()).encode())
            second = request(callId='call2' if replay != 'call' else 'call1')
            second['id'] = 2 if replay != 'id' else 1
            with self.assertRaises(m.ProtocolStop): b.handle(json.dumps(second).encode())
            self.assertTrue(b.stopped)
            self.assertEqual(len(b.receipts), 1)

    def test_eight_errors_allowed_ninth_stops_even_for_noncounting_stub(self):
        b = self.boundary(max_calls=20)
        b.broker.dispatch = lambda *_: (_ for _ in ()).throw(interface.ToolInputError('argument_fields'))
        for number in range(1, 9):
            value = request(callId='call' + str(number)); value['id'] = number
            self.assertFalse(json.loads(b.handle(json.dumps(value).encode()))['result']['success'])
        ninth = request(callId='call9'); ninth['id'] = 9
        with self.assertRaises(m.ProtocolStop): b.handle(json.dumps(ninth).encode())
        self.assertEqual(b.recoverable_input_errors, 8)
        self.assertEqual(b.failed_calls, 9)
        self.assertEqual(b.last_failure['code'], 'recoverable_input_error_ceiling')

    def test_failure_layer_catalog_does_not_retain_unknown_error_or_tool(self):
        marker = 'PRIVATE_028_ARBITRARY_EXCEPTION_ef7617'
        b = self.boundary(); unknown = request(tool=marker)
        with self.assertRaises(m.ProtocolStop): b.handle(json.dumps(unknown).encode())
        self.assertEqual(b.last_failure['layer'], 'envelope')
        self.assertIsNone(b.last_failure['tool'])
        self.assertNotIn(marker, json.dumps(b.last_failure))
        b = self.boundary()
        b.broker.dispatch = lambda *_: (_ for _ in ()).throw(RuntimeError(marker))
        with self.assertRaises(m.ProtocolStop) as error: b.handle(json.dumps(request()).encode())
        self.assertEqual(b.last_failure['layer'], 'dispatch')
        self.assertNotIn(marker, json.dumps(b.last_failure))
        self.assertNotIn(marker, str(error.exception))
        self.assertEqual(b.receipts, [])

    def test_content_and_response_failures_classified_separately(self):
        b = self.boundary()
        b.broker.dispatch = lambda *_: None
        with self.assertRaises(m.ProtocolStop): b.handle(json.dumps(request()).encode())
        self.assertEqual(b.last_failure['layer'], 'content')
        b = self.boundary()
        b._content = lambda *_: [{'type': 'inputText', 'text': object()}]
        with self.assertRaises(m.ProtocolStop): b.handle(json.dumps(request()).encode())
        self.assertEqual(b.last_failure['layer'], 'response')

    def test_malformed_request_records_fixed_failure_even_before_dispatch(self):
        for raw, code in ((b'{"id":1,"id":2}', 'duplicate_json_field'),
                          (b'{"id":NaN}', 'nonfinite_json_number'),
                          (b'\xff', 'invalid_json')):
            b = self.boundary()
            with self.assertRaises(m.ProtocolStop): b.handle(raw)
            self.assertEqual(b.last_failure['layer'], 'envelope')
            self.assertEqual(b.last_failure['code'], code)


    def test_real_wrapper_integrity_failure_is_terminal_after_recoverable_error(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'delivery') as folder:
            root = Path(folder)
            packet, output = root / 'packet', root / 'output'
            packet.mkdir(); output.mkdir()
            resource = packet / 'proof.txt'
            raw = b'synthetic evidence only\n'
            resource.write_bytes(raw)
            manifest = json.dumps({'schema_version': 1, 'files': [{
                'path': 'proof.txt', 'sha256': hashlib.sha256(raw).hexdigest(), 'kind': 'text'}]}).encode()
            (packet / 'BROKER_MANIFEST.json').write_bytes(manifest)
            with interface.ReviewBroker(packet, manifest_sha256=hashlib.sha256(manifest).hexdigest(),
                    output_root=output) as broker:
                boundary = m.DynamicToolBoundary(broker, thread_id='thread1', turn_id='turn1')
                first = request(tool='read_text', arguments={'path': 'proof.txt', 'offset': 0, 'length': 200000})
                self.assertFalse(json.loads(boundary.handle(json.dumps(first).encode()))['result']['success'])
                resource.write_bytes(b'TAMPERED_SYNTHETIC_TEST_ONLY\n')
                second = request(callId='call2', tool='read_text',
                    arguments={'path': 'proof.txt', 'offset': 0, 'length': 1000})
                second['id'] = 2
                with self.assertRaises(m.ProtocolStop): boundary.handle(json.dumps(second).encode())
                self.assertEqual(boundary.last_failure['layer'], 'dispatch')
                self.assertEqual(boundary.last_failure['code'], 'integrity.resource')
                self.assertEqual(len(boundary.receipts), 1)
                self.assertEqual(list(output.iterdir()), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
