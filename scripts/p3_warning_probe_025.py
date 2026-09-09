#!/usr/bin/env python3
"""Bounded offline 024 diagnostics. No native process, auth, network or verdict.

This intentionally does not open SQLite: literal hits may be stale, deleted,
uncommitted or split across pages. They never identify the rejected warning.
Only receipt/source files are hashed. Raw logs/config/cache are never copied,
hashed, displayed or persisted. Metadata equality is not content equality.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import time
import uuid

REPORT_SHA256 = "60f7a041d8415990a28362459e4ddd1b6029f10c1066d92ab85e0c6efee25c5f"
SESSION_SHA256 = "ca0bcc98b2ba16f4eab396f79e5792deb0af1610d80c77546e1c2a751ad7b02e"
MODEL = "gpt-5.6-sol"
NATIVE_VERSION = "0.151.0"
RUN_REL = Path("delivery/P3_FINITE_REVIEW_024")
OUTPUT_REL = Path("delivery/P3_WARNING_DIAGNOSTIC_025")
RECEIPT_LIMIT = 2 * 1024 * 1024
SOURCE_LIMIT = 2 * 1024 * 1024
CONFIG_LIMIT = 512 * 1024
CACHE_LIMIT = 8 * 1024 * 1024
LOG_SCAN_LIMIT = 32 * 1024 * 1024  # per fixed file, independent of file size
CHUNK = 256 * 1024
MATCH_COUNT_LIMIT = 100
WALL_SECONDS = 25
SOURCE_PINS = {
    "artifacts/GATE0_CODEX_INTERFACE/20260907_001/config-schema.json":
        "ed663d6d4c6c8b36917596882414c93858f6cf9ca5449ea8c616fc76d1aac114",
    "artifacts/GATE0_TOOL_BOUNDARY_SOURCE/20260907_001/codex-rs/models-manager/src/cache.rs":
        "97d64ab915c9736f409ceef9c0e71f018c7bfeb4c14060d4bda0453ba835a152",
    "artifacts/P3_MODEL_CATALOG_SOURCE/20260909_001/codex-rs/protocol/src/openai_models.rs":
        "8ec03e1382ef5bc4350c93262d1eb8833c7462057e2e995887c6e147deb63758",
    "artifacts/P3_DEPRECATION_SOURCE/20260909_REBUILD024/source/codex-rs/features/src/lib.rs":
        "62ac7c6f6109a1e984a0257aa1096753094b5d9dca9d638d19d75dc07b0c7940",
}
UNDER_DEVELOPMENT_KEYS = (
    "transcript_v2", "shell_zsh_fork", "shell_snapshot_v2", "deferred_executor",
    "cwd_relative_turn_diffs", "executed_tool_call_metadata", "code_mode",
    "code_mode_prewarm", "code_mode_interrupt", "code_mode_only",
    "standalone_web_search", "runtime_metrics", "external_agent_memory_import",
    "local_thread_store_compression", "background_paginated_rollout_migration",
    "chronicle", "apply_patch_streaming_events", "apply_patch_preserve_line_endings",
    "exec_permission_approvals", "write_stdin_approval", "request_permissions_tool",
    "respect_system_proxy", "psp", "enable_mcp_apps", "mcp_2026_07_28",
    "deferred_tool_world_state", "non_prefixed_mcp_tool_names",
    "executor_capability_discovery", "skip_host_skill_discovery", "image_resize_notice",
    "unified_image_budget", "concurrent_reasoning_summaries",
    "default_mode_request_user_input", "terminal_visualization_instructions",
    "guardian_reuse_parent_compaction", "guardian_enhanced_node_repl_transcripts",
    "guardian_node_repl_transcript_images", "guardianv2", "guardian_ext",
    "token_budget", "rollout_budget", "current_time_reminder", "bedrock_setup_wizard",
    "artifact", "step_model_switching", "realtime_conversation",
    "retain_client_developer_messages", "use_agent_identity",
)
# Actual 024 source overrides; this is a description of archived controls, not
# a configuration change. All other keys remain unproven at effective-config level.
RECORDED_FALSE_UNDER_DEVELOPMENT = frozenset((
    "deferred_executor", "code_mode", "code_mode_prewarm", "code_mode_only",
    "external_agent_memory_import", "background_paginated_rollout_migration",
    "enable_mcp_apps", "token_budget", "current_time_reminder",
))
STRUCTURED_FEATURE_KEYS = frozenset((
    "code_mode", "non_prefixed_mcp_tool_names", "guardianv2", "token_budget",
    "rollout_budget", "current_time_reminder",
))
# FEATURES includes this canonical key, but the exact archived config schema
# does not advertise it; never call an encountered value schema-supported.
UNADVERTISED_SCHEMA_FEATURE_KEYS = frozenset(("artifact",))
# Independent exact source literals. Markers may exist without a WarningEvent;
# binary occurrences are only corroborating candidates, never actual attribution.
LOG_MARKERS = {
    "under_development_notice_literal": b"Under-development features enabled: ",
    "code_mode_unavailable_literal": b"Code Mode is unavailable because ",
    "code_mode_unsupported_model_literal": b"Code Mode is enabled in configuration, but model `",
    "fallback_model_metadata_literal": b"Defaulting to fallback metadata; this can degrade performance and cause issues.",
    "fallback_model_metadata_producer": b"This will use fallback model metadata.",
    "requirements_constrained_value_producer": b"configured value is disallowed by requirements; falling back to required value for ",
    "requirements_constrained_value_literal": b"is disallowed by requirements; falling back",
    "requirements_exact_override_producer": b"configured value is overridden by an exact requirement for ",
    "requirements_structured_override_producer": b"configured values are overridden by requirements for ",
    "requirements_feature_alias": b"Using legacy `features` requirement `",
    "requirements_feature_unknown": b"Ignoring unknown `features` requirement `",
    "hook_trust_bypass": b"`--dangerously-bypass-hook-trust` is enabled.",
    "project_config_keys_ignored": b"Ignored unsupported project-local config keys in ",
    "agent_role_malformed": b"Ignoring malformed agent role definition: ",
    "global_instructions_unreadable": b"Failed to read global AGENTS.md instructions from `",
    "otel_invalid_span_attributes": b"Ignoring invalid `otel.span_attributes` config: ",
    "otel_invalid_tracestate": b"Ignoring invalid `otel.tracestate` config: ",
    "filesystem_entries_missing": b"does not define any recognized filesystem entries for this version of Codex.",
    "filesystem_glob_unsupported": b"is not fully supported by this platform's sandboxing.",
    "filesystem_globstar_unsupported": b"Non-macOS sandboxing does not support unbounded `**` natively",
    "filesystem_special_path_unknown": b"is not recognized by this version of Codex and will be ignored.",
    "service_tier_unsupported": b"is not advertised as supported for model `",
    "model_resume_mismatch": b"resuming session with different model: ",
    "transport_fallback": b"Falling back from WebSockets to HTTPS transport.",
    "model_reroute": b"this request was routed to gpt-5.2 as a fallback.",
    "model_reroute_producer": b"server reported model ",
    "transcript_save_failed": b"failed to flush rollout before completing turn: ",
    "execpolicy_amendment_failed": b"Failed to apply execpolicy amendment: ",
    "network_policy_amendment_failed": b"Failed to apply network policy amendment: ",
    "generic_warning_method_only": b"app-server event: warning",
    "models_cache_hit": b"models cache: cache hit",
    "models_cache_stale": b"models cache: cache is stale",
    "models_cache_version_mismatch": b"models cache: cache version mismatch",
}


class UnsafePath(Exception):
    pass


class BoundExceeded(Exception):
    pass


class HistoricalReceiptMismatch(Exception):
    pass


class SourcePinMismatch(Exception):
    pass


class MetadataChanged(Exception):
    pass


class InvalidStructure(Exception):
    pass


def error_type(error):
    """Never expose exception text, paths, native values or unknown class names."""
    name = type(error).__name__
    return name if name in {
        "UnsafePath", "BoundExceeded", "HistoricalReceiptMismatch", "SourcePinMismatch",
        "MetadataChanged", "InvalidStructure", "FileNotFoundError", "PermissionError",
        "NotADirectoryError", "FileExistsError", "OSError", "UnicodeDecodeError",
        "JSONDecodeError", "TOMLDecodeError", "ModuleNotFoundError", "RecursionError",
        "MemoryError", "ValueError", "KeyError", "TypeError",
    } else "OtherError"


def check_time(deadline):
    if time.monotonic() > deadline:
        raise BoundExceeded()


def absolute(path):
    path = Path(path)
    if not path.is_absolute() or ".." in path.parts:
        raise UnsafePath()
    return path


def open_dir(path):
    """Open each component by descriptor, refusing parent and leaf symlinks."""
    path = absolute(path)
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    fd = os.open("/", flags)
    try:
        for component in path.parts[1:]:
            next_fd = os.open(component, flags, dir_fd=fd)
            os.close(fd)
            fd = next_fd
        return fd
    except BaseException:
        os.close(fd)
        raise


def open_regular(path):
    path = absolute(path)
    parent_fd = open_dir(path.parent)
    try:
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC |
                     os.O_NONBLOCK, dir_fd=parent_fd)
    finally:
        os.close(parent_fd)
    observed = os.fstat(fd)
    if not stat.S_ISREG(observed.st_mode) or observed.st_nlink != 1:
        os.close(fd)
        raise UnsafePath()
    return fd, observed


def signature(info):
    return {"device": info.st_dev, "inode": info.st_ino, "bytes": info.st_size,
            "mode": stat.S_IMODE(info.st_mode), "mtime_ns": info.st_mtime_ns,
            "ctime_ns": info.st_ctime_ns}


def bounded_read(path, limit, deadline, expected_metadata=None):
    check_time(deadline)
    fd, before = open_regular(path)
    try:
        if expected_metadata is not None and signature(before) != expected_metadata:
            raise MetadataChanged()  # before any content read
        if before.st_size > limit:
            raise BoundExceeded()
        result = bytearray()
        while True:
            check_time(deadline)
            chunk = os.read(fd, min(CHUNK, limit + 1 - len(result)))
            if not chunk:
                break
            result.extend(chunk)
            if len(result) > limit:
                raise BoundExceeded()
        if signature(os.fstat(fd)) != signature(before) or len(result) != before.st_size:
            raise MetadataChanged()
        return bytes(result)
    finally:
        os.close(fd)


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise InvalidStructure()
            result[key] = value
        return result

    def invalid_constant(_):
        raise InvalidStructure()

    result = json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid_constant)
    pending = [(result, 0)]
    count = 0
    while pending:
        item, depth = pending.pop()
        count += 1
        if depth > 48 or count > 100000:
            raise BoundExceeded()
        if isinstance(item, dict):
            pending.extend((value, depth + 1) for value in item.values())
        elif isinstance(item, list):
            pending.extend((value, depth + 1) for value in item)
    return result


def load_history(root, deadline):
    run = root / RUN_REL
    report_raw = bounded_read(run / "REPORT.json", RECEIPT_LIMIT, deadline)
    if hashlib.sha256(report_raw).hexdigest() != REPORT_SHA256:
        raise HistoricalReceiptMismatch()
    session_raw = bounded_read(run / "synthetic_SESSION.json", RECEIPT_LIMIT, deadline)
    if hashlib.sha256(session_raw).hexdigest() != SESSION_SHA256:
        raise HistoricalReceiptMismatch()
    report, session = strict_json(report_raw), strict_json(session_raw)
    stages = report.get("stages")
    if (report.get("kind") != "P3_FINITE_REVIEW_024_v1" or
            not isinstance(stages, list) or len(stages) != 1 or
            stages[0].get("stage") != "synthetic" or
            stages[0].get("observation") != session or
            session.get("kind") != "P3_FINITE_REVIEWER_SESSION_024_REBUILT_v1" or
            session.get("mode") != "synthetic" or
            session.get("last_notification_type") != "warning" or
            session.get("native_process_reaped") is not True or
            session.get("selected_binding") != {"model": MODEL, "id": MODEL, "effort": "max"} or
            report.get("preserved_session_receipts") !=
            [{"path": "synthetic_SESSION.json", "sha256": SESSION_SHA256}]):
        raise HistoricalReceiptMismatch()
    return stages[0]


def verify_sources(root, deadline):
    for name, digest in SOURCE_PINS.items():
        raw = bounded_read(root / name, SOURCE_LIMIT, deadline)
        if hashlib.sha256(raw).hexdigest() != digest:
            raise SourcePinMismatch()
    return True


def scan_log(path, deadline):
    result = {"status": "not_inspected", "bytes_scanned": 0,
              "candidate_literal_counts": {}, "candidate_count_cap": MATCH_COUNT_LIMIT,
              "file_changed_during_scan": None, "scan_complete_within_byte_bound": False,
              "raw_saved": False, "raw_hashed": False,
              "actual_rejected_warning_identified": False}
    fd = None
    counts = {}
    try:
        check_time(deadline)
        fd, before = open_regular(path)
        counts = {key: 0 for key in LOG_MARKERS}
        tail = b""
        overlap = max(map(len, LOG_MARKERS.values())) - 1
        remaining = min(before.st_size, LOG_SCAN_LIMIT)
        while remaining:
            check_time(deadline)
            chunk = os.read(fd, min(CHUNK, remaining))
            if not chunk:
                break
            blob = tail + chunk
            for family, needle in LOG_MARKERS.items():
                # Subtract matches wholly inside the previous tail to avoid
                # double-counting, while retaining cross-chunk matches.
                increment = blob.count(needle) - tail.count(needle)
                counts[family] = min(MATCH_COUNT_LIMIT, counts[family] + increment)
            result["bytes_scanned"] += len(chunk)
            remaining -= len(chunk)
            tail = blob[-overlap:]
        changed = signature(os.fstat(fd)) != signature(before)
        result.update(status="binary_literal_scan_completed", file_changed_during_scan=changed,
                      scan_complete_within_byte_bound=(not changed and
                          result["bytes_scanned"] == before.st_size),
                      candidate_literal_counts={key: value for key, value in counts.items() if value})
    except Exception as error:
        result.update(status="unavailable_or_partial", error_type=error_type(error))
    finally:
        result["candidate_literal_counts"] = {key: value for key, value in counts.items() if value}
        if fd is not None:
            os.close(fd)
    return result


def approved_metadata(stage, path, category):
    rows = stage.get(category)
    if not isinstance(rows, list) or len(rows) > 32:
        raise HistoricalReceiptMismatch()
    matches = [item for item in rows if isinstance(item, dict) and item.get("path") == str(path)]
    if len(matches) != 1 or matches[0].get("present") is not True:
        raise HistoricalReceiptMismatch()
    metadata = matches[0].get("metadata")
    fields = {"device", "inode", "bytes", "mode", "mtime_ns", "ctime_ns"}
    if (not isinstance(metadata, dict) or set(metadata) != fields or
            not all(type(value) is int and value >= 0 for value in metadata.values())):
        raise HistoricalReceiptMismatch()
    return metadata


def boolean_state(table, key, allow_structured=False):
    if key not in table:
        return "absent"
    value = table[key]
    if type(value) is bool:
        return "true" if value else "false"
    if allow_structured and isinstance(value, dict) and type(value.get("enabled")) is bool:
        return "true" if value["enabled"] else "false"
    return "not_a_supported_boolean"


def inspect_config(root, stage, deadline):
    result = {"status": "not_inspected", "metadata_matches_024": False,
              "content_hashed": False, "raw_saved": False,
              "effective_runtime_features_reconstructed": False,
              "current_file_metadata_is_not_historical_content_proof": True}
    try:
        path = root.parent / ".codex" / "config.toml"
        expected = approved_metadata(stage, path, "config_origins")
        if stage.get("host_checks", {}).get("config_metadata_unchanged") is not True:
            raise HistoricalReceiptMismatch()
        raw = bounded_read(path, CONFIG_LIMIT, deadline, expected)
        result["metadata_matches_024"] = True
        import tomllib
        data = tomllib.loads(raw.decode("utf-8"))
        features = data.get("features", {})
        if not isinstance(features, dict):
            raise InvalidStructure()
        states = {
            key: ("not_advertised_by_pinned_config_schema"
                  if key in features and key in UNADVERTISED_SCHEMA_FEATURE_KEYS else
                  boolean_state(features, key, key in STRUCTURED_FEATURE_KEYS))
            for key in sorted(UNDER_DEVELOPMENT_KEYS)}
        result.update(status="known_feature_states_extracted", known_features=states,
                      full_config_schema_validated=False,
                      recorded024_false_control_keys=sorted(RECORDED_FALSE_UNDER_DEVELOPMENT),
                      explicit_true_keys_not_overridden_false_in024=sorted(
                          key for key, value in states.items() if value == "true" and
                          key not in RECORDED_FALSE_UNDER_DEVELOPMENT),
                      suppress_unstable_features_warning=boolean_state(data, "suppress_unstable_features_warning"),
                      predicted_actual_warning=False)
    except Exception as error:
        result.update(status="unavailable", error_type=error_type(error))
    return result


def inspect_cache(root, stage, deadline):
    result = {"status": "not_inspected", "selected_model": MODEL,
              "metadata_matches_024": False, "content_hashed": False, "raw_saved": False,
              "runtime_fallback_metadata_indicator": "not_serialized_unknown",
              "actual024_internal_model_info_verified": False,
              "current_file_metadata_is_not_historical_content_proof": True}
    try:
        path = root.parent / ".codex" / "models_cache.json"
        expected = approved_metadata(stage, path, "cache_origins")
        if stage.get("host_checks", {}).get("cache_metadata_unchanged") is not True:
            raise HistoricalReceiptMismatch()
        raw = bounded_read(path, CACHE_LIMIT, deadline, expected)
        result["metadata_matches_024"] = True
        data = strict_json(raw)
        if not isinstance(data, dict) or set(data) - {"fetched_at", "etag", "client_version", "models"}:
            raise InvalidStructure()
        models = data.get("models")
        if not isinstance(models, list) or len(models) > 2000 or not all(isinstance(item, dict) for item in models):
            raise InvalidStructure()
        selected = [item for item in models if item.get("slug") == MODEL]
        result.update(client_version_matches_native=data.get("client_version") == NATIVE_VERSION,
                      selected_cache_entry_count=min(len(selected), 2),
                      cache_freshness_at_actual_run="not_established",
                      cache_lookup_selection_at_actual_run="not_established")
        if len(selected) != 1:
            result["status"] = "selected_entry_absent_or_ambiguous"
            return result
        row = selected[0]
        value = row.get("tool_mode")
        if "tool_mode" not in row:
            tool_mode = "absent"
        elif value is None:
            tool_mode = "null"
        elif type(value) is str and value in ("direct", "code_mode", "code_mode_only"):
            tool_mode = value
        else:
            tool_mode = "unknown_value_omitted_by_native_deserializer"
        result.update(status="selected_internal_fields_extracted", tool_mode=tool_mode,
                      serialized_fallback_marker=("present_but_ignored_by_native_deserializer"
                          if "used_fallback_model_metadata" in row else "absent_not_serialized"),
                      full_model_info_schema_validated=False)
    except Exception as error:
        result.update(status="unavailable", error_type=error_type(error))
    return result


def collect(project_root):
    deadline = time.monotonic() + WALL_SECONDS
    result = {"kind": "P3_WARNING_DIAGNOSTIC_025_v1",
              "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
              "status": "HISTORICAL_RECEIPT_VALIDATION_FAILED_NO_VERDICT",
              "canonical024_report_verified": False, "canonical024_session_verified": False,
              "source_schema_pins_verified": False, "native_processes_started": 0,
              "model_turns_sent": 0, "network_calls": 0, "credentials_opened": False,
              "installation_id_opened": False, "other_programme_accessed": False,
              "raw_logs_config_cache_saved_or_hashed": False,
              "actual_rejected_warning_identified": False, "verdict_generated": False,
              "reviewer_verdict": None, "permission_or_controller_changed": False,
              "limits": {"wall_seconds": WALL_SECONDS, "deadline_is_cooperative": True,
                         "log_bytes_per_file": LOG_SCAN_LIMIT,
                         "log_files": 2, "config_bytes": CONFIG_LIMIT, "cache_bytes": CACHE_LIMIT},
              "interpretation": {
                  "binary_hits_are_possible_source_family_corroboration_only": True,
                  "binary_data_may_be_stale_deleted_uncommitted_or_partial": True,
                  "binary_page_boundaries_and_utf16_may_hide_matches": True,
                  "wal_presence_does_not_make_binary_scan_a_committed_snapshot": True,
                  "no_match_does_not_exclude_any_warning_family": True,
                  "generic_warning_method_literal_does_not_identify_warning_body": True,
                  "config_and_cache_current_metadata_match_is_not_actual_run_identity": True,
                  "diagnostic_may_remain_inconclusive": True}}
    try:
        root = absolute(project_root)
        stage = load_history(root, deadline)
        result.update(canonical024_report_verified=True, canonical024_session_verified=True)
    except Exception as error:
        result["error_type"] = error_type(error)
        return result
    run = root / RUN_REL / "synthetic_native" / "runtime_state"
    result["logs"] = {"database": scan_log(run / "logs_2.sqlite", deadline),
                      "wal": scan_log(run / "logs_2.sqlite-wal", deadline)}
    try:
        result["source_schema_pins_verified"] = verify_sources(root, deadline)
    except Exception as error:
        result["source_schema_error_type"] = error_type(error)
        result["config"] = {"status": "not_opened_source_pins_unverified"}
        result["cache"] = {"status": "not_opened_source_pins_unverified"}
    else:
        result["config"] = inspect_config(root, stage, deadline)
        result["cache"] = inspect_cache(root, stage, deadline)
    result["status"] = "OFFLINE_DIAGNOSTIC_COMPLETE_NO_VERDICT"
    return result


def write_receipt(project_root, report):
    root = absolute(project_root)
    delivery_fd = open_dir(root / "delivery")
    try:
        try:
            os.mkdir("P3_WARNING_DIAGNOSTIC_025", mode=0o700, dir_fd=delivery_fd)
        except FileExistsError:
            pass
        parent_fd = os.open("P3_WARNING_DIAGNOSTIC_025",
                            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                            dir_fd=delivery_fd)
    finally:
        os.close(delivery_fd)
    try:
        name = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ_") + uuid.uuid4().hex
        os.mkdir(name, mode=0o700, dir_fd=parent_fd)
        output_fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                            dir_fd=parent_fd)
        try:
            raw = (json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")
            if len(raw) > 128 * 1024:
                raise BoundExceeded()
            fd = os.open("REPORT.pending", os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                         os.O_NOFOLLOW | os.O_CLOEXEC, 0o400, dir_fd=output_fd)
            with os.fdopen(fd, "wb") as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
            # link is atomic and refuses an existing target; REPORT.json is
            # visible only after its entire immutable receipt has been synced.
            os.link("REPORT.pending", "REPORT.json", src_dir_fd=output_fd,
                    dst_dir_fd=output_fd, follow_symlinks=False)
            os.unlink("REPORT.pending", dir_fd=output_fd)
            os.fsync(output_fd)
        finally:
            os.close(output_fd)
        os.fsync(parent_fd)
    finally:
        os.close(parent_fd)
    return root / OUTPUT_REL / name / "REPORT.json"


def main():
    # No arbitrary path, native executable or alternate-history CLI arguments.
    if len(sys.argv) != 1:
        print('{"status":"UNSUPPORTED_ARGUMENTS_NO_ACTION","verdict_generated":false}')
        return 2
    root = Path.home() / "ARC_Independent_Lab"
    report = collect(root)
    try:
        receipt = write_receipt(root, report)
    except Exception as error:
        print(json.dumps({"status": "RECEIPT_SAVE_FAILED_NO_VERDICT",
                          "error_type": error_type(error), "verdict_generated": False}))
        return 2
    # Only a locally generated project-relative receipt location is printed.
    print(json.dumps({"status": report["status"],
                      "report": str(receipt.relative_to(root)), "verdict_generated": False}))
    return 0 if report["canonical024_report_verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
