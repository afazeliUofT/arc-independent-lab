#!/usr/bin/env python3
"""Finite authenticated tool transport with bounded, correctable input feedback.

No model launcher or authority is provided. Only prevalidated argument errors
from focused broker039 are recoverable; identity, authority and integrity failures
remain terminal. A failed call consumes both its call identity and call budget.
"""
from __future__ import annotations

import hashlib
import json
import time
import p3_focused_review_broker_039 as interface

TOOLS = frozenset(interface.TOOL_SCHEMAS)
MAX_REQUEST_BYTES = 512 * 1024
MAX_RESPONSE_BYTES = 24 * 1024 * 1024
MAX_RECOVERABLE_INPUT_ERRORS = 8


class ProtocolStop(RuntimeError):
    """Fixed local boundary failure; terminate the client when raised."""


def _json_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ProtocolStop("duplicate_json_field")
        value[key] = item
    return value


def _constant(_):
    raise ProtocolStop("nonfinite_json_number")


def _identifier(value):
    return type(value) is str and 0 < len(value) <= 256 and all(ord(c) >= 32 for c in value)


class DynamicToolBoundary:
    """One trusted turn, finite calls/time/bytes, eight correctable input errors."""
    def __init__(self, broker, *, thread_id, turn_id, max_calls=256,
                 wall_seconds=1800, clock=time.monotonic):
        if not _identifier(thread_id) or not _identifier(turn_id):
            raise ProtocolStop("invalid_trusted_binding")
        if type(max_calls) is not int or not 1 <= max_calls <= 1024:
            raise ProtocolStop("invalid_call_ceiling")
        if type(wall_seconds) is not int or not 1 <= wall_seconds <= 3600:
            raise ProtocolStop("invalid_time_ceiling")
        self.broker = broker
        self.thread_id, self.turn_id = thread_id, turn_id
        self.max_calls = max_calls
        self.clock, self.deadline = clock, clock() + wall_seconds
        self._request_ids, self._call_ids = set(), set()
        self.stopped = self.finished = False
        self.receipts = []
        self.recoverable_input_errors = 0
        self.failed_calls = 0
        self.last_failure = None

    def handle(self, raw: bytes) -> bytes:
        layer, tool, code = "envelope", None, "invalid_json"
        def require(condition, failure):
            nonlocal code
            if not condition:
                code = failure
                raise ProtocolStop(failure)
        try:
            require(not self.stopped and not self.finished, "boundary_closed")
            require(type(raw) is bytes and 0 < len(raw) <= MAX_REQUEST_BYTES, "request_byte_limit_or_type")
            require(self.clock() < self.deadline, "work_time_ceiling")
            require(len(self._call_ids) < self.max_calls, "work_call_ceiling")
            try:
                request = json.loads(raw, object_pairs_hook=_json_object, parse_constant=_constant)
            except ProtocolStop as error:
                # Parser raises only these two literal messages, never JSON text.
                code = str(error) if str(error) in {"duplicate_json_field", "nonfinite_json_number"} else "invalid_json"
                raise
            require(type(request) is dict and set(request) == {"id", "method", "params"}, "request_envelope")
            rid = request["id"]
            require((type(rid) is int and 0 <= rid < 2**53) or _identifier(rid), "request_identifier")
            require(rid not in self._request_ids, "replayed_request_identifier")
            require(request["method"] == "item/tool/call", "unadvertised_server_request")
            p = request["params"]
            required = {"arguments", "callId", "threadId", "turnId", "tool"}
            require(type(p) is dict and set(p) in (required, required | {"namespace"}), "tool_request_fields")
            require(p.get("namespace") is None, "unadvertised_namespace")
            require(p["threadId"] == self.thread_id and p["turnId"] == self.turn_id, "foreign_thread_or_turn")
            require(_identifier(p["callId"]) and p["callId"] not in self._call_ids, "invalid_or_replayed_call")
            require(type(p["tool"]) is str and p["tool"] in TOOLS, "unadvertised_tool")
            tool = p["tool"]
            require(type(p["arguments"]) is dict, "arguments_not_object")
            self._request_ids.add(rid)
            self._call_ids.add(p["callId"])
            layer, code = "dispatch", "unknown_dispatch_failure"
            successful, input_code = True, None
            try:
                result = self.broker.dispatch(tool, p["arguments"])
            except interface.ToolInputError as error:
                self.failed_calls += 1
                require(self.recoverable_input_errors < MAX_RECOVERABLE_INPUT_ERRORS,
                        "recoverable_input_error_ceiling")
                # Reconstruct through the finite class catalog, rather than
                # trusting exception text or an instance-overridden as_dict().
                result = interface.ToolInputError(error.code).as_dict()
                input_code = error.code
                self.recoverable_input_errors += 1
                successful = False
            except Exception as error:
                self.failed_calls += 1
                code = interface.classify_broker_failure(error)
                raise ProtocolStop("broker_dispatch_failed") from None
            layer, code = "content", "invalid_broker_content"
            content = self._content(tool if successful else "input_error", result)
            layer, code = "response", "invalid_response_encoding"
            response = json.dumps({"id": rid, "result": {
                "contentItems": content, "success": successful}},
                ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode()
            require(len(response) <= MAX_RESPONSE_BYTES, "response_byte_ceiling")
            self.receipts.append({"method": "item/tool/call", "tool": tool,
                "successful": successful, "error_code": input_code,
                "request_bytes": len(raw), "request_sha256": hashlib.sha256(raw).hexdigest(),
                "response_bytes": len(response), "response_sha256": hashlib.sha256(response).hexdigest()})
            self.finished = successful and tool == "submit_verdict"
            return response + b"\n"
        except Exception:
            self.stopped = True
            self.last_failure = {"layer": layer, "code": code, "tool": tool,
                "raw_input_path_or_exception_saved": False}
            raise ProtocolStop("Broker protocol or evidence validation refused") from None

    @staticmethod
    def _content(tool, result):
        if type(result) is not dict:
            raise ProtocolStop("invalid_broker_result")
        if tool == "read_page_image":
            image = result.get("data_base64")
            if type(image) is not str or result.get("mimeType") != "image/png":
                raise ProtocolStop("invalid_pinned_page_image_result")
            metadata = {k: v for k, v in result.items() if k != "data_base64"}
            return [{"type": "inputText", "text": json.dumps(metadata, allow_nan=False)},
                    {"type": "inputImage", "imageUrl": "data:image/png;base64," + image}]
        return [{"type": "inputText", "text": json.dumps(result, allow_nan=False)}]

