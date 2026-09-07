#!/usr/bin/env python3
"""Finite dynamic-tool message boundary; deliberately not a client launcher.

The trusted parent must establish process/context/tool isolation before attaching
this adapter. This validates messages on the broker channel only; native client
tools that bypass this channel require separate enforcement. No network, model,
configuration, authentication, approval or thread-start operation is provided.
Message shapes: exact Codex 0.151.0 embedded experimental schemas.
"""
from __future__ import annotations

import hashlib
import json
import time

TOOLS = frozenset(("read_text", "read_page_image", "hash_file",
                   "run_observer_audit", "submit_verdict"))
MAX_REQUEST_BYTES = 512 * 1024
MAX_RESPONSE_BYTES = 24 * 1024 * 1024


class ProtocolStop(RuntimeError):
    """Terminal boundary failure; a future parent must terminate its client."""


def _json_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ProtocolStop("Duplicate JSON field")
        value[key] = item
    return value


def _constant(_):
    raise ProtocolStop("Nonfinite JSON number")


def _identifier(value):
    return type(value) is str and 0 < len(value) <= 256 and all(ord(c) >= 32 for c in value)


class DynamicToolBoundary:
    """Bind a single turn's broker requests to identities supplied by the parent.

    Limits bound this adapter's work, not subscription consumption. They confer
    no entitlement or proof of attendance. A real parent must also apply a
    process deadline that fires even when no request arrives.
    """

    def __init__(self, broker, *, thread_id, turn_id, max_calls=256,
                 wall_seconds=1800, clock=time.monotonic):
        if not _identifier(thread_id) or not _identifier(turn_id):
            raise ProtocolStop("Invalid trusted thread/turn binding")
        if type(max_calls) is not int or not 1 <= max_calls <= 1024:
            raise ProtocolStop("Invalid call ceiling")
        if type(wall_seconds) is not int or not 1 <= wall_seconds <= 3600:
            raise ProtocolStop("Invalid adapter time ceiling")
        self.broker = broker
        self.thread_id, self.turn_id = thread_id, turn_id
        self.max_calls = max_calls
        self.clock, self.deadline = clock, clock() + wall_seconds
        self._request_ids, self._call_ids = set(), set()
        self.stopped = False
        self.finished = False
        self.receipts = []

    def handle(self, raw: bytes) -> bytes:
        """Accept exactly one server request, or fail terminally without dispatch.

        No raw request/error is logged: unknown methods can carry credentials.
        Receipts retain only fixed method/tool names, byte counts and digests.
        This is a single-threaded adapter; a future transport serializes input.
        """
        if self.stopped or self.finished:
            raise ProtocolStop("Boundary is closed")
        try:
            if type(raw) is not bytes or not 0 < len(raw) <= MAX_REQUEST_BYTES:
                raise ProtocolStop("Request byte limit/type")
            if self.clock() >= self.deadline or len(self._call_ids) >= self.max_calls:
                raise ProtocolStop("Adapter work ceiling reached")
            request = json.loads(raw, object_pairs_hook=_json_object, parse_constant=_constant)
            if type(request) is not dict or set(request) != {"id", "method", "params"}:
                raise ProtocolStop("Unexpected request envelope")
            rid = request["id"]
            if not ((type(rid) is int and 0 <= rid < 2**53) or _identifier(rid)):
                raise ProtocolStop("Invalid request identifier")
            if rid in self._request_ids:
                raise ProtocolStop("Replayed request identifier")
            if request["method"] != "item/tool/call":
                # Includes approval, auth refresh, permission escalation and all
                # future/unknown server requests. Never forward or approve them.
                raise ProtocolStop("Unadvertised server request; no action taken")
            p = request["params"]
            required = {"arguments", "callId", "threadId", "turnId", "tool"}
            if type(p) is not dict or set(p) not in (required, required | {"namespace"}):
                raise ProtocolStop("Unexpected tool request fields")
            if p.get("namespace") is not None:
                raise ProtocolStop("Unadvertised tool namespace")
            if p["threadId"] != self.thread_id or p["turnId"] != self.turn_id:
                raise ProtocolStop("Foreign thread or turn")
            if not _identifier(p["callId"]) or p["callId"] in self._call_ids:
                raise ProtocolStop("Invalid/replayed tool call")
            if type(p["tool"]) is not str or p["tool"] not in TOOLS:
                raise ProtocolStop("Unadvertised tool")
            if type(p["arguments"]) is not dict:
                raise ProtocolStop("Tool arguments must be an object")
            self._request_ids.add(rid)
            self._call_ids.add(p["callId"])
            result = self.broker.dispatch(p["tool"], p["arguments"])
            content = self._content(p["tool"], result)
            response = json.dumps({"id": rid, "result": {
                "contentItems": content, "success": True}},
                ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode()
            if len(response) > MAX_RESPONSE_BYTES:
                raise ProtocolStop("Response byte ceiling")
            self.receipts.append({"method": "item/tool/call", "tool": p["tool"],
                                  "request_bytes": len(raw),
                                  "request_sha256": hashlib.sha256(raw).hexdigest(),
                                  "response_bytes": len(response),
                                  "response_sha256": hashlib.sha256(response).hexdigest()})
            self.finished = p["tool"] == "submit_verdict"
            return response + b"\n"
        except Exception as error:
            self.stopped = True
            if isinstance(error, ProtocolStop):
                raise
            # Do not expose a client error, input text or path outside the packet.
            raise ProtocolStop("Broker or protocol validation failed") from None

    @staticmethod
    def _content(tool, result):
        if type(result) is not dict:
            raise ProtocolStop("Invalid broker result")
        if tool == "read_page_image":
            # Broker returns only verified PNG bytes; external URL forwarding is
            # deliberately absent. Exact key names are validated in tests.
            image = result.get("data_base64")
            if type(image) is not str or result.get("mimeType") != "image/png":
                raise ProtocolStop("Invalid pinned page image result")
            metadata = {k: v for k, v in result.items() if k != "data_base64"}
            return [{"type": "inputText", "text": json.dumps(metadata, allow_nan=False)},
                    {"type": "inputImage", "imageUrl": "data:image/png;base64," + image}]
        return [{"type": "inputText", "text": json.dumps(result, allow_nan=False)}]
