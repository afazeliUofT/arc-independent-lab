#!/usr/bin/env python3
"""Finite, filtered app-server metadata transport; never requests a model turn.

The caller supplies an independently validated launch/mount plan. This module
does not authorize that plan, establish its network boundary, or read credentials.
Native output exists transiently in memory for framing/filtering only. Neither
stream, nor a hash of either stream, is included in its returned observation.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import selectors
import signal
import subprocess
import time

WALL_SECONDS = 90
CLEANUP_SECONDS = 4
METHOD_SECONDS = 20
STREAM_LIMIT = 2 * 1024 * 1024
TREE_LIMIT = 64 * 1024 * 1024
REQUESTED_MODEL = "gpt-6-astra"
# The native schema deliberately permits any nonempty reasoning-effort string.
# This is our output allowlist, not a claim that the native enum is closed.
EFFORTS = ("none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra")
ERROR_CATEGORIES = ("auth", "credential", "keyring", "refresh", "network",
                    "permission", "config", "rate", "limit", "timeout")
OPTIONAL_METHODS = ("account/rateLimits/read", "model/list")


class Stop(RuntimeError):
    """Only locally authored, nonsecret reasons may be included in this error."""


def require(condition, message):
    if not condition:
        raise Stop(message)


def _integer(value, bits=64):
    return type(value) is int and -(2 ** (bits - 1)) <= value < 2 ** (bits - 1)


def _window(value):
    if value is None:
        return {"present": False, "shape_recognized": True}
    if type(value) is not dict:
        return {"present": True, "shape_recognized": False}
    used = value.get("usedPercent")
    duration, reset = value.get("windowDurationMins"), value.get("resetsAt")
    recognized = (_integer(used, 32)
                  and (duration is None or _integer(duration))
                  and (reset is None or _integer(reset)))
    return {"present": True, "shape_recognized": recognized,
            "usedPercent": used if _integer(used, 32) else None,
            "windowDurationMins": duration if _integer(duration) else None,
            "resetsAt": reset if _integer(reset) else None}


def _codex_snapshot(value):
    require(type(value) is dict, "Invalid Codex rate-limit snapshot")
    # No credit balances, opaque credit identifiers, names or spend-control text.
    return {"primary": _window(value.get("primary")),
            "secondary": _window(value.get("secondary"))}


def safe_rate_limits(result):
    require(type(result) is dict and type(result.get("rateLimits")) is dict,
            "Invalid rate-limits response")
    buckets = result.get("rateLimitsByLimitId")
    require(buckets is None or type(buckets) is dict, "Invalid rate-limit bucket map")
    single = result["rateLimits"]
    codex = {}
    unknown_count = 0
    if buckets is not None:
        for key, value in buckets.items():
            if key == "codex":
                # A contradictory internal ID is not silently relabelled Codex.
                require(type(value) is dict and value.get("limitId") in (None, "codex"),
                        "Conflicting Codex rate-limit identity")
                codex["explicit_codex_map_entry"] = _codex_snapshot(value)
            else:
                unknown_count += 1
    if single.get("limitId") == "codex":
        codex["explicit_codex_legacy_entry"] = _codex_snapshot(single)
    return {"response_shape_recognized": True,
            "codex_bucket_observed": bool(codex),
            "codex_snapshots": codex,
            "unrecognized_bucket_count": unknown_count,
            "legacy_bucket_identity_recognized": single.get("limitId") == "codex",
            "scope": "Codex_rate_limit_metadata_returned_by_account_rateLimits_read",
            "hosted_chatgpt_allowance_verified": False,
            "requested_model_entitlement_verified": False,
            "reset_credits_used": False,
            "unattended_model_use_authorized": False}


def safe_models(result):
    require(type(result) is dict and type(result.get("data")) is list,
            "Invalid model-catalog response")
    rows = result["data"]
    require(len(rows) <= 100 and all(type(row) is dict for row in rows),
            "Invalid or oversized model-catalog page")
    cursor = result.get("nextCursor")
    require(cursor is None or type(cursor) is str, "Invalid catalog pagination field")
    matches = []
    for row in rows:
        model_match, id_match = row.get("model") == REQUESTED_MODEL, row.get("id") == REQUESTED_MODEL
        if not (model_match or id_match):
            continue
        efforts = row.get("supportedReasoningEfforts")
        require(type(efforts) is list and all(type(item) is dict for item in efforts),
                "Invalid requested-model effort metadata")
        require(type(row.get("isDefault")) is bool and type(row.get("hidden")) is bool,
                "Invalid requested-model boolean metadata")
        supported = {name: any(item.get("reasoningEffort") == name for item in efforts)
                     for name in EFFORTS}
        default = row.get("defaultReasoningEffort")
        matches.append({"exact_model_field_match": model_match,
                        "exact_id_field_match": id_match,
                        "is_default": row["isDefault"], "hidden": row["hidden"],
                        "recognized_efforts": supported,
                        "unrecognized_effort_count": sum(
                            not (type(item.get("reasoningEffort")) is str
                                 and item["reasoningEffort"] in EFFORTS) for item in efforts),
                        "default_effort_recognized": type(default) is str and default in EFFORTS,
                        "default_effort": default if type(default) is str and default in EFFORTS else None})
    return {"response_shape_recognized": True, "page_entry_count": len(rows),
            "additional_page_available": cursor is not None,
            "page_complete_for_returned_catalog": cursor is None,
            "exact_requested_model_present_on_page": any(m["exact_model_field_match"] for m in matches),
            "exact_requested_id_present_on_page": any(m["exact_id_field_match"] for m in matches),
            "matching_entries": matches,
            "effort_names_are_local_output_allowlist": True,
            "scope": "returned_model_catalog_page_may_use_cached_metadata",
            "model_entitlement_verified": False,
            "model_tool_registry_verified": False,
            "scientific_reviewer_boundary_verified": False}


def safe_requirements(result):
    require(type(result) is dict, "Invalid requirements response")
    value = result.get("requirements")
    require(value is None or type(value) is dict, "Invalid requirements field")
    return {"requirements_field_present": "requirements" in result,
            "requirements_present": value is not None,
            "requirements_type_recognized": True,
            "requirements_verified": False,
            "cloud_policy_provenance_verified": False,
            "scope": "single_configRequirements_read_response_no_policy_origin_attestation"}


def safe_error(error):
    require(type(error) is dict and _integer(error.get("code"))
            and type(error.get("message")) is str, "Invalid protocol error shape")
    message = error["message"].lower()
    return {"code": error["code"],
            "categories_observed": {word: word in message for word in ERROR_CATEGORIES}}


def _stop_process(process, deadline):
    """Bound cleanup too; report inability to reap instead of waiting forever."""
    # The leader may exit before its children. Signal its session's process
    # group even after direct-child completion, then reap the direct child.
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        process.wait(timeout=max(0, min(2, deadline - time.monotonic())))
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    try:
        process.wait(timeout=max(0, min(2, deadline - time.monotonic())))
        return True
    except subprocess.TimeoutExpired:
        return False


def observe(plan, run, requested, preflight, account_module):
    """Return only filtered metadata from one validated, bounded native session.

The six requests below and the initialized notification are the entire outbound
protocol. A server request always stops the observation without any response.
The caller is responsible for the credential/network plan and artifact handling.
"""
    run = Path(run)
    steps = [
        ("initialize", {"clientInfo": {"name": "arc_postlogin_metadata", "version": "1"},
                        "capabilities": {"experimentalApi": True, "extensions": {}}}),
        ("config/read", {"cwd": str(run), "includeLayers": True}),
        ("configRequirements/read", {}),
        ("account/read", {"refreshToken": False}),
        ("account/rateLimits/read", {}),
        ("model/list", {"limit": 100, "includeHidden": False}),
    ]
    report = {"requests_sent": [], "responses": [], "notifications_received": 0,
              "server_requests_dispatched": 0, "thread_or_model_request_sent": False,
              "login_config_write_or_credit_operation_sent": False,
              "live_rate_limits_response_received": False,
              "model_entitlement_verified": False,
              "authoritative_hosted_chatgpt_allowance_verified": False,
              "scientific_reviewer_boundary_verified": False,
              "unattended_model_use_authorized": False}
    totals = {"stdout": 0, "stderr": 0}
    stdout_buffer = bytearray()
    selector = selectors.DefaultSelector()
    process = None
    start = time.monotonic()
    deadline, active_end = start + WALL_SECONDS, start + WALL_SECONDS - CLEANUP_SECONDS
    index = 0
    method_end = active_end

    def send_next():
        nonlocal method_end
        method, params = steps[index]
        payload = json.dumps({"id": index + 1, "method": method, "params": params}).encode() + b"\n"
        process.stdin.write(payload)
        process.stdin.flush()
        report["requests_sent"].append(method)
        method_end = min(active_end, time.monotonic() + METHOD_SECONDS)

    def accept_result(method, result):
        require(type(result) is dict, "Invalid metadata result shape")
        if method == "initialize":
            require(all(type(result.get(key)) is str and bool(result[key]) for key in
                        ("userAgent", "codexHome", "platformFamily", "platformOs"))
                    and Path(result["codexHome"]).is_absolute(),
                    "Invalid initialization response")
            expected_home = os.environ.get("CODEX_HOME", str(Path(os.environ["HOME"]) / ".codex"))
            require(result["codexHome"] == expected_home,
                    "Initialized Codex home differs from the original environment")
            report["initialization"] = {"required_field_types_recognized": True,
                                        "codex_home_field_absolute": True,
                                        "codex_home_equals_original_environment": True}
        elif method == "config/read":
            report["effective_config"] = preflight.safe_config(result, requested)
            report["account_configuration"] = account_module.safe_account_config(result)
        elif method == "configRequirements/read":
            report["requirements"] = safe_requirements(result)
        elif method == "account/read":
            account = account_module.safe_account(result)
            require(account["response_shape_recognized"], "Invalid account response")
            account["scope"] = "cached_account_available_inside_this_network_enabled_session"
            # account/read(refreshToken=false) is not itself a live auth check.
            account["live_authentication_verified"] = False
            report["contained_account"] = account
        elif method == "account/rateLimits/read":
            report["rate_limits"] = safe_rate_limits(result)
            report["live_rate_limits_response_received"] = True
        elif method == "model/list":
            report["model_catalog"] = safe_models(result)

    try:
        process = subprocess.Popen(plan["argv"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, cwd=run, env=preflight.restricted_env(),
                                   start_new_session=True, preexec_fn=preflight.child_limits)
        report["client_started"] = True
        for stream, name in ((process.stdout, "stdout"), (process.stderr, "stderr")):
            os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_READ, name)
        send_next()
        while index < len(steps):
            require(time.monotonic() < active_end, "Metadata observation deadline")
            if time.monotonic() >= method_end:
                report["timed_out_method"] = steps[index][0]
                raise Stop("Metadata request deadline; outstanding request was not retried")
            require(preflight.tree_size(run) <= TREE_LIMIT, "Runtime tree byte ceiling")
            events = selector.select(timeout=min(0.1, max(0, method_end - time.monotonic())))
            for key, _ in events:
                data = os.read(key.fileobj.fileno(), 65536)
                if not data:
                    selector.unregister(key.fileobj)
                    continue
                name = key.data
                totals[name] += len(data)
                require(totals[name] <= STREAM_LIMIT, "Protocol/diagnostic stream ceiling")
                if name == "stderr":
                    # Discard immediately: no diagnostic buffer, file or hash.
                    continue
                stdout_buffer.extend(data)
                while b"\n" in stdout_buffer:
                    line, _, rest = stdout_buffer.partition(b"\n")
                    stdout_buffer = bytearray(rest)
                    msg = preflight.parse_line(line)
                    require(not ("method" in msg and "id" in msg),
                            "Unexpected server request; no response dispatched")
                    if "method" in msg:
                        require(set(msg) <= {"method", "params"} and type(msg["method"]) is str,
                                "Invalid notification envelope")
                        report["notifications_received"] += 1
                        continue
                    require(index < len(steps) and set(msg) <= {"id", "result", "error"}
                            and type(msg.get("id")) is int and msg["id"] == index + 1
                            and (("result" in msg) != ("error" in msg)),
                            "Unbound or invalid response envelope")
                    method = steps[index][0]
                    if "error" in msg:
                        response = {"method": method, "received": True, "success": False,
                                    "error": safe_error(msg["error"])}
                        report["responses"].append(response)
                        require(method in OPTIONAL_METHODS, "Required metadata request returned an error")
                    else:
                        accept_result(method, msg["result"])
                        report["responses"].append({"method": method, "received": True, "success": True})
                        if method == "account/read":
                            require(report["contained_account"]["account_kind"] == "chatgpt",
                                    "Cached ChatGPT account unavailable; live metadata not requested")
                    index += 1
                    if index == 1:
                        process.stdin.write(b'{"method":"initialized","params":{}}\n')
                        process.stdin.flush()
                    if index < len(steps):
                        send_next()
            require(process.poll() is None or index == len(steps),
                    "Client exited before metadata observation completed")
        report["status"] = "OBSERVED_POSTLOGIN_METADATA_ONLY"
    except (Stop, preflight.Stop, OSError, ValueError, RecursionError) as error:
        report["status"] = "STOPPED_WITHOUT_REVIEW"
        report["reason"] = str(error) if isinstance(error, (Stop, preflight.Stop)) else "Host process or pipe operation failed"
    finally:
        report.setdefault("client_started", False)
        if process is not None:
            try:
                report["native_process_reaped"] = _stop_process(process, deadline)
            except OSError:
                report["native_process_reaped"] = False
            if not report["native_process_reaped"]:
                report["status"] = "STOPPED_WITHOUT_REVIEW"
                report["reason"] = "Native process cleanup was not verified"
            report["client_exit_code"] = process.returncode
            for stream in (process.stdin, process.stdout, process.stderr):
                try:
                    stream.close()
                except OSError:
                    pass
        selector.close()
        stdout_buffer.clear()
        report["streams"] = {name: {"bytes_observed": total, "raw_saved": False, "hashed": False}
                             for name, total in totals.items()}
        report["raw_config_auth_or_diagnostics_saved"] = False
        report["elapsed_seconds"] = round(time.monotonic() - start, 6)
    return report
