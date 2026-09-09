#!/usr/bin/env python3
"""One finite app-server stdio session behind a caller-validated process plan.

No launcher, authentication access, policy grant, persistence or automatic retry
is provided here. The parent owns original-source checks and the outer boundary.
Native diagnostics/configuration exist transiently; only filtered observations
and unchanged broker receipts are returned. Notification guards are retrospective
observations, not a claim that the native registered tool inventory is empty.
"""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import resource
import sys
import selectors
import time

import subprocess


def _module(name):
    path = Path(__file__).resolve().with_name(name + ".py")
    existing = sys.modules.get(name)
    if existing is not None:
        if Path(existing.__file__).resolve() != path:
            raise RuntimeError("Conflicting reviewer module origin")
        return existing
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


preflight = _module("gate0_client_preflight")
account = _module("gate0_account_metadata")
metadata = _module("gate0_postlogin_protocol")
broker_module = _module("p3_review_broker")
protocol = _module("p3_review_protocol")
_module("gate0_config_controls")
profile = _module("p3_reviewer_profile")
admission = _module("p3_reviewer_admission_021")
config_warning = _module("p3_config_warning")

CLEANUP_SECONDS = 4
METHOD_SECONDS = 30
STDERR_LIMIT = 64 * 1024 * 1024
SYNTHETIC_STDOUT_LIMIT = 64 * 1024 * 1024
SCIENCE_STDOUT_LIMIT = 512 * 1024 * 1024
FRAME_LIMIT = 24 * 1024 * 1024
TREE_LIMIT = 256 * 1024 * 1024
EARLY_FRAME_LIMIT = 64
EARLY_BYTE_LIMIT = 1024 * 1024
WRITE_QUEUE_LIMIT = 32 * 1024 * 1024
CATALOG_MAX_PAGES = 8
CATALOG_MAX_ENTRIES = 800
SYNTHETIC_READ = {"path": "CANARY.txt", "offset": 0, "length": 1000}
SYNTHETIC_FORBIDDEN = {"path": "../OUTSIDE.txt", "offset": 0, "length": 1000}
# Fixed local output labels for actionable refusals; no unknown native method,
# field name, warning text, arguments or payload value is copied into a report.
KNOWN_EVENT_NAMES = frozenset((
    "remoteControl/status/changed", "account/rateLimits/updated", "account/updated",
    "thread/started", "thread/status/changed", "thread/settings/updated",
    "thread/environment/connected", "thread/environment/disconnected", "thread/compacted",
    "turn/started", "turn/completed", "item/started", "item/completed",
    "item/agentMessage/delta", "item/reasoning/summaryTextDelta", "item/reasoning/textDelta",
    "item/reasoning/summaryPartAdded", "thread/tokenUsage/updated", "serverRequest/resolved",
    "model/verification", "model/rerouted", "model/safetyBuffering/updated",
    "turn/moderationMetadata", "hook/started", "hook/completed", "error", "warning",
    "configWarning", "guardianWarning", "deprecationNotice", "skills/changed",
    "command/exec/outputDelta", "process/outputDelta", "process/exited",
    "item/commandExecution/outputDelta", "item/commandExecution/terminalInteraction",
    "item/fileChange/outputDelta", "item/fileChange/patchUpdated", "fs/changed",
    "item/mcpToolCall/progress", "mcpServer/startupStatus/updated", "app/list/updated",
    "account/login/completed", "item/autoApprovalReview/started", "item/autoApprovalReview/completed"))


class Stop(RuntimeError):
    """Fixed local reason only; native message text must not be interpolated."""


def require(condition, reason):
    if not condition:
        raise Stop(reason)


def _identifier(value):
    return type(value) is str and 0 < len(value) <= 256 and all(32 <= ord(c) < 127 for c in value)


def _limits(mode):
    resource.setrlimit(resource.RLIMIT_FSIZE, (32 * 1024 * 1024,) * 2)
    cpu = 120 if mode == "synthetic" else 600
    resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu + 1))


def _quota_admitted(receipt):
    require(receipt.get("codex_bucket_observed") is True, "Codex limit bucket unavailable")
    snapshots = receipt.get("codex_snapshots", {})
    windows = [snapshot[name] for snapshot in snapshots.values() for name in ("primary", "secondary")
               if snapshot[name].get("present")]
    require(bool(windows) and all(w.get("shape_recognized") is True and
            type(w.get("usedPercent")) is int and 0 <= w["usedPercent"] < 100 for w in windows),
            "Codex limit headroom unavailable or malformed")
    # These are native-reported whole percentages. There is no estimate of
    # remaining tokens, paid credits, hosted ChatGPT allowance or unattended use.
    return {"codex_reported_windows_below_full": True,
            "hosted_chatgpt_allowance_verified": False,
            "remaining_tokens_estimated": False}


class _CatalogPages:
    """Bounded filtered collection; opaque native cursors never leave memory."""

    def __init__(self):
        self.filtered = None
        self._cursors, self._ids = set(), set()
        self.progress = {"maximum_pages": CATALOG_MAX_PAGES,
                         "maximum_entries": CATALOG_MAX_ENTRIES,
                         "pages_received": 0, "pages_validated": 0,
                         "total_entries_validated": 0, "complete": False,
                         "cursor_values_saved_or_hashed": False}

    def add(self, result):
        self.progress["pages_received"] += 1
        require(self.progress["pages_received"] <= CATALOG_MAX_PAGES,
                "Model catalog page ceiling")
        page = profile.safe_model_catalog(result, include_hidden_requested=True)
        rows = page["entries"]
        require(not any(row["id"] in self._ids for row in rows),
                "Duplicate model identity across catalog pages")
        require(len(self._ids) + len(rows) <= CATALOG_MAX_ENTRIES,
                "Model catalog entry ceiling")
        self._ids.update(row["id"] for row in rows)
        if self.filtered is None:
            self.filtered = page
        else:
            self.filtered["entries"].extend(rows)
            for name in ("discarded_unknown_response_field_count",
                         "discarded_unknown_entry_field_count",
                         "discarded_unknown_effort_field_count"):
                self.filtered[name] += page[name]
            for name in ("exact_requested_model_present_on_page", "exact_requested_id_present_on_page"):
                self.filtered[name] = self.filtered[name] or page[name]
        self.progress["pages_validated"] += 1
        self.progress["total_entries_validated"] = len(self._ids)
        self.filtered.update({"page_entry_count": len(rows),
            "total_entry_count": len(self._ids), "pages_validated": self.progress["pages_validated"],
            "scope": "bounded_returned_model_catalog_pages_may_use_cached_metadata",
            "page_complete_for_returned_catalog": False,
            "additional_page_available": page["additional_page_available"],
            "pagination_complete": False})
        cursor = result.get("nextCursor")
        if cursor is None:
            self.progress["complete"] = True
            self.filtered["page_complete_for_returned_catalog"] = True
            self.filtered["pagination_complete"] = True
            return None
        try:
            valid_cursor = (type(cursor) is str and 0 < len(cursor.encode("utf-8")) <= 4096 and
                            all(ord(char) >= 32 and ord(char) != 127 for char in cursor))
        except UnicodeError:
            valid_cursor = False
        require(valid_cursor and cursor not in self._cursors,
                "Invalid or repeated opaque model catalog cursor")
        self._cursors.add(cursor)
        require(self.progress["pages_validated"] < CATALOG_MAX_PAGES,
                "Model catalog exceeds bounded pagination scope")
        return cursor


class _BrokerWitness:
    """Record the synthetic denial only at the real broker's dispatch boundary."""

    def __init__(self, broker, mode, active_end):
        self.broker, self.mode, self.active_end = broker, mode, active_end
        self.allowed_read = False
        self.observed_refusal = False
        self.verdict_submitted = False

    def dispatch(self, tool, arguments):
        if self.mode == "synthetic":
            require(tool == "read_text" and arguments in (SYNTHETIC_READ, SYNTHETIC_FORBIDDEN),
                    "Synthetic operation differs from the fixed challenge")
            require((not self.allowed_read and arguments == SYNTHETIC_READ) or
                    (self.allowed_read and arguments == SYNTHETIC_FORBIDDEN),
                    "Synthetic challenge order differs")
        if tool == "run_observer_audit":
            require(self.active_end - time.monotonic() >= 31,
                    "Insufficient remaining wall time for fixed auditor")
        if self.mode == "synthetic":
            self.broker.verify_inputs()
        try:
            # The unchanged broker rehashes its entire closure before and after
            # every dispatch. Do not add another full scientific corpus pass.
            result = self.broker.dispatch(tool, arguments)
        except broker_module.BrokerError as error:
            # The underlying broker has checked its frozen inputs immediately
            # above. Only its canonical-path refusal establishes this observation.
            if (self.mode == "synthetic" and self.allowed_read and tool == "read_text"
                    and arguments == SYNTHETIC_FORBIDDEN):
                traceback = error.__traceback__
                while traceback is not None:
                    if traceback.tb_frame.f_code is broker_module._path.__code__:
                        self.observed_refusal = True
                        break
                    traceback = traceback.tb_next
            raise
        if self.mode == "synthetic" and arguments == SYNTHETIC_READ:
            self.allowed_read = True
        if tool == "submit_verdict":
            self.verdict_submitted = True
        return result


class _Events:
    """Validate known source-audited event effects without retaining native text."""

    def __init__(self, prompt):
        self.thread_id = self.turn_id = None
        self.prompt = prompt
        self.model = self.effort = self.cwd = None
        self.counts = {}
        self.last_type = None
        self.started_thread_seen = self.started_turn_seen = False
        self.finished_turn = False
        self.request_ids = set()
        self.initialized = self.thread_requested = False
        self.config_warnings = []

    def _bound(self, params, *, turn=True):
        require(self.thread_id is not None and params.get("threadId") == self.thread_id,
                "Foreign or unbound event thread")
        if turn:
            require(self.turn_id is not None and params.get("turnId") == self.turn_id,
                    "Foreign or unbound event turn")

    def item(self, item):
        require(type(item) is dict and _identifier(item.get("id")), "Malformed thread item")
        kind = item.get("type")
        require(type(kind) is str and kind in {
            "userMessage", "agentMessage", "reasoning", "dynamicToolCall", "functionCallOutput"},
            "Unadvertised native item effect")
        if kind == "userMessage":
            content = item.get("content")
            require(type(content) is list and len(content) == 1 and type(content[0]) is dict and
                    set(content[0]) <= {"type", "text", "text_elements"} and
                    content[0].get("type") == "text" and content[0].get("text") == self.prompt and
                    content[0].get("text_elements", []) == [], "Unexpected user input origin")
        elif kind == "agentMessage":
            require(type(item.get("text")) is str and item.get("memoryCitation") is None and
                    item.get("delivery") in (None, "async"), "Unexpected agent output origin")
        elif kind == "dynamicToolCall":
            require(type(item.get("tool")) is str and item["tool"] in protocol.TOOLS and
                    item.get("namespace") is None and type(item.get("arguments")) is dict,
                    "Unadvertised dynamic item authority")
        elif kind == "functionCallOutput":
            # Exact-source harmless output/wait handlers; never executed here.
            require(item.get("name") in ("send_user_message_async", "test_sync_tool") and
                    item.get("namespace") in (None, "functions"),
                    "Unadvertised function output authority")

    def turn(self, value, *, expected=None):
        require(type(value) is dict and _identifier(value.get("id")) and
                type(value.get("items")) is list and len(value["items"]) <= 4096 and
                value.get("status") in ("inProgress", "completed", "interrupted", "failed"),
                "Malformed turn state")
        if expected is not None:
            require(value["id"] == expected, "Foreign turn state")
        require(value.get("error") is None and value["status"] not in ("failed", "interrupted"),
                "Native turn failed or interrupted")
        for item in value["items"]:
            self.item(item)
        return value["id"]

    def accept(self, message):
        shape = metadata.notification_envelope_shape(message)
        require(shape["envelope_valid"], "Invalid notification envelope")
        method, params = message["method"], message.get("params")
        self.last_type = method if method in KNOWN_EVENT_NAMES else "unknown"
        if method == "configWarning":
            # Only fixed local labels leave this classifier. Native warning
            # text, paths, details and their hashes are never copied to receipts.
            receipt = config_warning.classify(params, initialized=self.initialized,
                thread_requested=self.thread_requested,
                previously_accepted=sum(row["admitted"] for row in self.config_warnings))
            self.config_warnings.append(receipt)
            require(receipt["admitted"], "Configuration warning admission refused")
            self.counts[method] = self.counts.get(method, 0) + 1
            return
        require(type(params) is dict, "Malformed notification parameters")
        if method == "remoteControl/status/changed":
            require(params.get("status") == "disabled", "Remote control is not disabled")
        elif method == "account/rateLimits/updated":
            # Sparse rolling metadata does not replace the explicit admission RPC.
            require(type(params.get("rateLimits")) is dict, "Malformed quota notification")
        elif method == "account/updated":
            require(self.thread_id is None and params.get("authMode") in (None, "chatgpt"),
                    "Account changed during reviewer session")
        elif method == "thread/started":
            value = params.get("thread")
            require(type(value) is dict and value.get("id") == self.thread_id and
                    self.thread_id is not None and value.get("ephemeral") is True and
                    value.get("turns") == [] and not self.started_thread_seen,
                    "Unexpected thread-start event")
            self.started_thread_seen = True
        elif method == "thread/settings/updated":
            admission.validate_thread_settings(params, thread_id=self.thread_id,
                model=self.model, effort=self.effort, cwd=self.cwd)
        elif method == "thread/status/changed":
            self._bound(params, turn=False)
            status = params.get("status")
            require(type(status) is dict and status.get("type") in ("idle", "active") and
                    status.get("activeFlags", []) == [], "Unexpected thread lifecycle state")
        elif method in ("turn/started", "turn/completed"):
            self._bound(params, turn=False)
            self.turn(params.get("turn"), expected=self.turn_id)
            require(self.turn_id is not None, "Turn event preceded trusted binding")
            if method == "turn/started":
                require(not self.started_turn_seen, "Replayed turn-start event")
                self.started_turn_seen = True
            else:
                require(not self.finished_turn and params["turn"]["status"] == "completed",
                        "Unexpected turn-completion event")
                self.finished_turn = True
        elif method in ("item/started", "item/completed"):
            self._bound(params)
            self.item(params.get("item"))
        elif method in ("item/agentMessage/delta", "item/reasoning/summaryTextDelta",
                        "item/reasoning/textDelta", "item/reasoning/summaryPartAdded"):
            self._bound(params)
            require(_identifier(params.get("itemId")), "Malformed output item identity")
            if method != "item/reasoning/summaryPartAdded":
                require(type(params.get("delta")) is str, "Malformed text delta")
        elif method == "thread/tokenUsage/updated":
            self._bound(params)
            require(type(params.get("tokenUsage")) is dict, "Malformed token usage event")
        elif method == "serverRequest/resolved":
            self._bound(params, turn=False)
            rid = params.get("requestId")
            require(type(rid) in (str, int) and rid in self.request_ids,
                    "Unbound server resolution event")
        elif method in ("model/verification", "turn/moderationMetadata"):
            self._bound(params)
        else:
            # Includes rerouting/environment/hooks/collaboration/MCP,
            # web/files/commands/images, errors (including willRetry), warnings,
            # compaction, login and every future/unknown event. No action follows.
            raise Stop("Unadvertised native notification effect")
        self.counts[method] = self.counts.get(method, 0) + 1


def run_session(plan, run, requested, broker, *, mode, prompt, wall_seconds,
                max_calls, expected_binding=None):
    """Run one fresh thread and at most one turn, never resuming or retrying.

    ``expected_binding`` is the accepted synthetic ``selected_binding`` and is
    mandatory for science. The parent has validated the source/mount/policy
    receipts; this function neither infers nor grants those capabilities.
    """
    run = Path(run)
    report = {"kind": "P3_FINITE_REVIEWER_SESSION_021_v1", "mode": mode,
              "requests_sent": [], "requests_queued": [], "responses": [], "client_started": False,
              "thread_request_sent": False, "model_turn_request_sent": False,
              "model_turn_request_queued": False,
              "synthetic_allowed_read_observed": False, "observed_refusal": False,
              "verdict_submitted": False, "server_requests_dispatched": 0,
              "early_frames_buffered": 0, "automatic_retry_requested": False,
              "raw_config_auth_or_diagnostics_saved": False,
              "native_tool_inventory_attested": False,
              "full_boundary_proven_by_notifications": False,
              "hosted_chatgpt_allowance_verified": False,
              "unattended_model_use_authorized": False}
    start = time.monotonic()
    totals = {"stdout": 0, "stderr": 0}
    process = None
    selector = selectors.DefaultSelector()
    incoming, outgoing = bytearray(), bytearray()
    outgoing_segments = []
    early, early_bytes = [], 0
    events = _Events(prompt)
    catalog = _CatalogPages()
    report["catalog_pagination"] = catalog.progress
    witness = boundary = None
    selected = None
    pending_method = None
    pending_id = 0
    method_end = active_end = deadline = start
    done = False

    def enqueue(raw, method=None):
        require(type(raw) is bytes and len(outgoing) + len(raw) <= WRITE_QUEUE_LIMIT,
                "Outbound byte ceiling")
        outgoing.extend(raw)
        outgoing_segments.append([len(raw), method])
        try:
            selector.get_key(process.stdin)
        except KeyError:
            selector.register(process.stdin, selectors.EVENT_WRITE, "stdin")

    def request(method, params):
        nonlocal pending_method, pending_id, method_end
        require(pending_method is None, "Overlapping parent requests")
        pending_id += 1
        pending_method = method
        if method == "thread/start":
            events.thread_requested = True
        method_end = min(active_end, time.monotonic() + METHOD_SECONDS)
        enqueue(json.dumps({"id": pending_id, "method": method, "params": params},
                           allow_nan=False, separators=(",", ":")).encode() + b"\n", method)
        report["requests_queued"].append(method)
        if method == "turn/start":
            report["model_turn_request_queued"] = True

    def dispatch_message(message, line):
        nonlocal done
        if "id" in message:
            require(boundary is not None, "Server request preceded trusted turn binding")
            require(message.get("method") == "item/tool/call", "Unadvertised server request")
            try:
                response = boundary.handle(line)
            except protocol.ProtocolStop as error:
                if witness.observed_refusal:
                    report["status"] = "SYNTHETIC_REFUSAL_OBSERVED"
                    done = True
                    return
                report["broker_protocol_reason"] = str(error)
                raise Stop("Broker protocol or evidence validation refused") from None
            report["server_requests_dispatched"] += 1
            events.request_ids.add(message["id"])
            enqueue(response)
            if witness.verdict_submitted:
                report["status"] = "VERDICT_SUBMITTED"
                done = True
        else:
            events.accept(message)
            if events.finished_turn:
                raise Stop("Turn completed without the required broker outcome")

    def drain_early():
        nonlocal early_bytes
        queued = early[:]
        early.clear()
        early_bytes = 0
        for message, line in queued:
            if not done:
                dispatch_message(message, line)

    def accept_response(message):
        nonlocal pending_method, selected, boundary, witness
        require(pending_method is not None and set(message) <= {"id", "result", "error"}
                and type(message.get("id")) is int and message["id"] == pending_id and
                (("result" in message) != ("error" in message)), "Unbound response envelope")
        method = pending_method
        pending_method = None
        if "error" in message:
            report["responses"].append({"method": method, "success": False,
                                        "error": metadata.safe_error(message["error"])})
            raise Stop("Required reviewer request returned an error")
        result = message["result"]
        require(type(result) is dict, "Malformed response result")
        report["responses"].append({"method": method, "success": True})
        if method == "initialize":
            expected_home = os.environ.get("CODEX_HOME", str(Path(os.environ["HOME"]) / ".codex"))
            require(all(type(result.get(k)) is str and result[k] for k in
                        ("userAgent", "codexHome", "platformFamily", "platformOs")) and
                    result["codexHome"] == expected_home, "Initialized configuration home differs")
            report["initialization"] = {"codex_home_equals_original_environment": True}
            events.initialized = True
            enqueue(b'{"method":"initialized","params":{}}\n')
            request("config/read", {"cwd": str(run), "includeLayers": True})
        elif method == "config/read":
            # Save only fixed control names and filtered booleans/categories before
            # admission can stop. Never persist native values, origins or versions.
            report["config_control_observation"] = admission.observe_effective_config(result, requested)
            report["effective_config"] = admission.validate_effective_config(result, requested)
            report["account_configuration"] = account.safe_account_config(result)
            require(report["account_configuration"]["configured_backend"] == "file",
                    "Native credential backend differs from approved file backend")
            request("configRequirements/read", {})
        elif method == "configRequirements/read":
            report["requirements"] = metadata.safe_requirements(result)
            require(report["requirements"]["requirements_field_present"],
                    "Managed requirements response field missing")
            # This finite route was prepared against the observed Pro account
            # with null requirements. A nonnull managed object may introduce
            # instruction files not represented by ConfigRead's projection.
            # Preserve its safe presence receipt and stop; never hide it, clear
            # it or infer instruction closure merely from field presence.
            require(result["requirements"] is None,
                    "Nonnull managed requirements need a separately closed instruction scope")
            report["requirements"]["null_requirements_admitted_for_observed_pro_route"] = True
            request("account/read", {"refreshToken": False})
        elif method == "account/read":
            receipt = account.safe_account(result)
            require(receipt["response_shape_recognized"] and receipt["account_kind"] == "chatgpt",
                    "ChatGPT subscription account unavailable")
            receipt["scope"] = "cached_account_read_in_this_network_enabled_session"
            report["contained_account"] = receipt
            require(receipt["reported_plan_type"] == "pro",
                    "Account plan differs from the source-closed Pro route")
            request("account/rateLimits/read", {})
        elif method == "account/rateLimits/read":
            report["rate_limits"] = metadata.safe_rate_limits(result)
            report["quota_admission"] = _quota_admitted(report["rate_limits"])
            report["live_rate_limits_response_received"] = True
            request("model/list", {"limit": 100, "includeHidden": True})
        elif method == "model/list":
            try:
                cursor = catalog.add(result)
            finally:
                if catalog.filtered is not None:
                    report["model_catalog"] = catalog.filtered
            if cursor is not None:
                request("model/list", {"limit": 100, "includeHidden": True, "cursor": cursor})
                return
            selected = admission.select_model(report["model_catalog"])
            report["selected_binding"] = selected
            if expected_binding is not None:
                require(selected == expected_binding, "Selected model binding differs from synthetic session")
            specs = broker_module.dynamic_tool_specs()
            if mode == "synthetic":
                specs = [spec for spec in specs if spec["name"] == "read_text"]
            params = admission.thread_params(selected["model"], selected["effort"], str(run), specs, requested)
            request("thread/start", params)
        elif method == "thread/start":
            trusted = admission.validate_thread_response(result, model=selected["model"],
                    effort=selected["effort"], cwd=str(run), allowed_instruction_sources=())
            events.thread_id = trusted["thread_id"]
            events.model, events.effort, events.cwd = selected["model"], selected["effort"], str(run)
            report["thread_admission"] = trusted
            report["reported_model_provider"] = admission.PROVIDER
            # Rehash unchanged closed evidence immediately before the sole turn.
            broker.verify_inputs()
            drain_early()
            request("turn/start", admission.turn_params(events.thread_id, selected["model"],
                                                       selected["effort"], prompt))
        elif method == "turn/start":
            turn_id = events.turn(result.get("turn"))
            require(result["turn"]["status"] == "inProgress", "Turn was not admitted in progress")
            events.turn_id = turn_id
            witness = _BrokerWitness(broker, mode, active_end)
            boundary = protocol.DynamicToolBoundary(witness, thread_id=events.thread_id,
                       turn_id=turn_id, max_calls=max_calls,
                       wall_seconds=max(1, min(3600, int(active_end - time.monotonic()))))
            report["turn_binding"] = {"thread_id": events.thread_id, "turn_id": turn_id}
            drain_early()

    try:
        require(mode in ("synthetic", "science") and type(prompt) is str and
                0 < len(prompt.encode("utf-8")) <= 256 * 1024, "Invalid finite session input")
        require(type(wall_seconds) is int and 5 <= wall_seconds <= 3600 and
                type(max_calls) is int and 1 <= max_calls <= 1024, "Invalid finite session budget")
        require(mode != "science" or (type(expected_binding) is dict and
                set(expected_binding) == {"model", "id", "effort"}),
                "Science requires the accepted synthetic model binding")
        require(type(plan) is dict and type(plan.get("argv")) is list and plan["argv"] and
                all(type(x) is str and x for x in plan["argv"]), "Invalid supplied process plan")
        report["limits"] = {
            "wall_seconds_including_cleanup": wall_seconds, "cleanup_seconds": CLEANUP_SECONDS,
            "parent_request_seconds": METHOD_SECONDS, "max_broker_calls": max_calls,
            "stdout_bytes": SCIENCE_STDOUT_LIMIT if mode == "science" else SYNTHETIC_STDOUT_LIMIT,
            "stderr_bytes": STDERR_LIMIT, "frame_bytes": FRAME_LIMIT,
            "outbound_queue_bytes": WRITE_QUEUE_LIMIT, "runtime_tree_bytes": TREE_LIMIT,
            "early_frame_count": EARLY_FRAME_LIMIT, "early_frame_bytes": EARLY_BYTE_LIMIT,
            "catalog_maximum_pages": CATALOG_MAX_PAGES, "catalog_maximum_entries": CATALOG_MAX_ENTRIES,
            "child_cpu_seconds": 120 if mode == "synthetic" else 600,
            "child_file_bytes": 32 * 1024 * 1024,
            "limits_are_not_subscription_allowance_estimates": True}
        deadline = start + wall_seconds
        active_end = deadline - CLEANUP_SECONDS
        broker.verify_inputs()
        process = subprocess.Popen(plan["argv"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE, cwd=run, env=preflight.restricted_env(),
                   start_new_session=True, preexec_fn=lambda: _limits(mode))
        report["client_started"] = True
        for stream, name in ((process.stdin, "stdin"), (process.stdout, "stdout"),
                             (process.stderr, "stderr")):
            os.set_blocking(stream.fileno(), False)
            if name != "stdin":
                selector.register(stream, selectors.EVENT_READ, name)
        request("initialize", {"clientInfo": {"name": "arc_finite_reviewer", "version": "1"},
                "capabilities": {"experimentalApi": True, "extensions": {}}})
        next_tree_check = start
        while not done:
            now = time.monotonic()
            require(now < active_end, "Finite reviewer wall deadline reached")
            require(pending_method is None or now < method_end, "Reviewer request deadline reached")
            if now >= next_tree_check:
                require(preflight.tree_size(run) <= TREE_LIMIT, "Runtime tree byte ceiling")
                next_tree_check = now + 0.25
            for key, _ in selector.select(timeout=min(0.1, max(0, active_end - now))):
                if key.data == "stdin":
                    try:
                        written = os.write(key.fileobj.fileno(), outgoing[:65536])
                    except BlockingIOError:
                        continue
                    require(written > 0, "Native input pipe made no progress")
                    del outgoing[:written]
                    remaining = written
                    while remaining:
                        count, method = outgoing_segments[0]
                        taken = min(remaining, count)
                        count -= taken
                        remaining -= taken
                        if count:
                            outgoing_segments[0][0] = count
                        else:
                            outgoing_segments.pop(0)
                            if method is not None:
                                report["requests_sent"].append(method)
                                if method == "thread/start":
                                    report["thread_request_sent"] = True
                                elif method == "turn/start":
                                    report["model_turn_request_sent"] = True
                    if not outgoing:
                        selector.unregister(key.fileobj)
                    continue
                try:
                    data = os.read(key.fileobj.fileno(), 65536)
                except BlockingIOError:
                    continue
                if not data:
                    selector.unregister(key.fileobj)
                    continue
                name = key.data
                totals[name] += len(data)
                require(totals[name] <= report["limits"][name + "_bytes"], "Native stream byte ceiling")
                if name == "stderr":
                    continue
                incoming.extend(data)
                require(len(incoming) <= FRAME_LIMIT, "Native frame byte ceiling")
                while b"\n" in incoming and not done:
                    line, _, tail = incoming.partition(b"\n")
                    incoming = bytearray(tail)
                    line = bytes(line)
                    message = preflight.parse_line(line)
                    if "method" not in message:
                        accept_response(message)
                        continue
                    if "id" in message:
                        require(message.get("method") == "item/tool/call",
                                "Unadvertised server request; no action taken")
                    else:
                        require(metadata.notification_envelope_shape(message)["envelope_valid"],
                                "Invalid notification envelope")
                    is_global = message.get("method") in {"remoteControl/status/changed",
                               "account/rateLimits/updated", "account/updated", "configWarning"} and "id" not in message
                    if pending_method in ("thread/start", "turn/start") and not is_global:
                        require(len(early) < EARLY_FRAME_LIMIT and
                                early_bytes + len(line) <= EARLY_BYTE_LIMIT, "Early frame buffer ceiling")
                        early.append((message, bytes(line)))
                        early_bytes += len(line)
                        report["early_frames_buffered"] += 1
                    else:
                        dispatch_message(message, line)
            require(process.poll() is None or done, "Native client exited before required outcome")
    except (Stop, metadata.Stop, preflight.Stop, admission.Stop, profile.Stop,
            broker_module.BrokerError, protocol.ProtocolStop, OSError, ValueError,
            TypeError, KeyError, RecursionError) as error:
        report["status"] = "STOPPED_WITHOUT_VERDICT"
        if type(error) is Stop:
            report["reason"] = str(error)
        elif isinstance(error, admission.Stop):
            report["reason"] = "Reviewer model, profile or thread admission refused"
            report["admission_reason"] = str(error)
        else:
            report["reason"] = "Reviewer transport, metadata or evidence validation failed"
    finally:
        if witness is not None:
            report["synthetic_allowed_read_observed"] = witness.allowed_read
            report["observed_refusal"] = witness.observed_refusal
            report["verdict_submitted"] = witness.verdict_submitted
        report["config_warnings"] = events.config_warnings
        report["config_warning_policy"] = {"version": config_warning.POLICY_VERSION,
            "maximum_admitted_advisories": 1, "raw_content_saved_or_hashed": False}
        report["notifications"] = events.counts
        report["last_notification_type"] = events.last_type
        report["broker_receipts"] = boundary.receipts if boundary is not None else []
        if process is not None:
            try:
                report["native_process_reaped"] = metadata._stop_process(process, deadline)
            except OSError:
                report["native_process_reaped"] = False
            report["client_exit_code"] = process.returncode
            if not report["native_process_reaped"]:
                report["status"] = "STOPPED_WITHOUT_VERDICT"
                report["reason"] = "Native process cleanup was not verified"
            for stream in (process.stdin, process.stdout, process.stderr):
                try:
                    stream.close()
                except OSError:
                    pass
        report["streams"] = {name: {"bytes_observed": total, "raw_saved": False, "hashed": False}
                             for name, total in totals.items()}
        report["elapsed_seconds"] = round(time.monotonic() - start, 6)
        selector.close()
        incoming.clear()
        outgoing.clear()
        outgoing_segments.clear()
        early.clear()
    return report
