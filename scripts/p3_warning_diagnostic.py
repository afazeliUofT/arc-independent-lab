"""Bounded, non-authorizing diagnostics for Codex 0.151.0 warnings.

Source: openai/codex commit 78c290807ce710180111df227df3b7a4fe845452,
captured in artifacts/P3_WARNING_SOURCE/20260909_025 (access 2026-09-09).
https://github.com/openai/codex/tree/78c290807ce710180111df227df3b7a4fe845452
Every result requires stopping. Recognition is of text shape, never evidence
that the named producer ran, and never permission to continue. No raw message,
variable text, message digest, thread identifier, or model identifier is returned.
This module performs no I/O. The caller must not log its input or exceptions.
"""

import re

SOURCE_COMMIT = "78c290807ce710180111df227df3b7a4fe845452"
MAX_MESSAGE_BYTES = 16384
UNDER_DEVELOPMENT_KEYS = frozenset({
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
})

REQUIREMENT_FIELDS = frozenset({
    "cli_auth_credentials_store", "chatgpt_base_url", "sqlite_home", "log_dir",
    "model_catalog_json", "check_for_update_on_startup", "allow_login_shell",
    "windows.sandbox_private_desktop", "windows.sandbox", "approval_policy",
    "approvals_reviewer", "permission_profile", "web_search_mode", "feedback",
    "otel.span_attributes", "otel.tracestate",
})

UNDERDEV_PREFIX = "Under-development features enabled: "
UNDERDEV_MIDDLE = (
    ". Under-development features are incomplete and may behave unpredictably. "
    "To suppress this warning, set `suppress_unstable_features_warning = true` in "
)
CODE_MODE_PREFIX = "Code Mode is unavailable because "
CODE_MODE_SUFFIX = "; enable `features.code_mode_host` and install `codex-code-mode-host`."

# These open providers supply arbitrary text. No text-only classifier can
# distinguish them from unknown warnings or authenticate a source-shaped spoof.
UNCLASSIFIABLE_OPEN_FAMILIES = (
    "hooks.async_output_warning", "skills.host_warning",
)

# Full literal matching is possible only where the pinned producer is constant.
CONSTANTS = {
    "config.hook_trust_bypass": "`--dangerously-bypass-hook-trust` is enabled. Enabled hooks may run without review for this invocation.",
    "hooks.stop_without_prompt": "Stop hook requested continuation without a prompt; ignoring the block.",
    "context.compaction_accuracy": "Heads up: Long threads and multiple compactions can cause the model to be less accurate. Start a new thread when possible to keep threads small and targeted.",
    "model.rerouted": "Your account was flagged for potentially high-risk cyber activity and this request was routed to gpt-5.2 as a fallback. To regain access to gpt-5.3-codex, apply for trusted access: https://chatgpt.com/cyber or learn more: https://developers.openai.com/codex/concepts/cyber-safety",
}

# Anchored, bounded source-template shapes. Wildcard variables are discarded;
# matching a template is explicitly weaker than authenticating the producer.
# Single-line variables deliberately reject ambiguous/control-bearing values.
TEMPLATES = (
    ("config.project_keys_ignored", r"Ignored unsupported project-local config keys in [^\r\n]+: [^\r\n]+\. If you want these settings to apply, manually set them in your user-level config\.toml\."),
    ("config.windows_managed_ignored", r"Ignoring deprecated managed config file at [^\r\n]+; CODEX_HOME/managed_config\.toml is no longer supported on Windows\. Use %ProgramData%\\OpenAI\\Codex\\requirements\.toml for enforced settings or config\.toml for defaults\."),
    ("config.exact_requirement_override", r"Configured value for `(?P<field>[^`\r\n]+)` is overridden by the required value [^\r\n]+ from [^\r\n]+\."),
    ("config.feedback_requirement_override", r"Configured values under `(?P<field>feedback)` are overridden by requirements from [^\r\n]+\."),
    ("config.residency_header_ignored", r"Ignoring `[^`\r\n]+` in `model_providers\.[^`\r\n]+` because managed residency is required\."),
    ("config.sqlite_env_override", r"Environment value for `\$CODEX_SQLITE_HOME` is overridden by the required `sqlite_home` value [^\r\n]+ from [^\r\n]+\."),
    ("config.legacy_feature_requirement", r"Using legacy `features` requirement `[^`\r\n]+` from [^\r\n]+; prefer canonical feature key `[^`\r\n]+`"),
    ("config.unknown_feature_requirement", r"Ignoring unknown `features` requirement `[^`\r\n]+` from [^\r\n]+"),
    ("config.constrained_value_fallback", r"Configured value for `(?P<field>[^`\r\n]+)` is disallowed by requirements; falling back to required value [^\r\n]+\. Details: [^\r\n]+"),
    ("config.permission_profile_fallback", r"Configured value for `(?P<field>permission_profile)` is disallowed by requirements; falling back from `[^`\r\n]+` to required value `[^`\r\n]+`\."),
    ("config.permissions_missing_entries", r"Permissions profile `[^`\r\n]+` does not define any recognized filesystem entries for this version of Codex\. Filesystem access will remain restricted\. Upgrade Codex if this profile expects filesystem permissions\."),
    ("config.filesystem_glob_unsupported", r"Filesystem glob `[^`\r\n]+` uses `read` or `write` access, which is not fully supported by this platform's sandboxing\. Use an exact path or trailing `/\*\*` subtree rule instead\. `deny` globs are supported\."),
    ("config.filesystem_globstar_unsupported", r"Filesystem deny-read glob `[^`\r\n]+` uses `\*\*`\. Non-macOS sandboxing does not support unbounded `\*\*` natively; set `glob_scan_max_depth` in this filesystem profile to cap Linux glob expansion and silence this warning, or enumerate explicit depths such as `\*\.env`, `\*/\*\.env`, and `\*/\*/\*\.env`\."),
    ("config.filesystem_special_path_unknown", r"Configured filesystem path `[^`\r\n]+`(?: with nested entry `[^`\r\n]+`)? is not recognized by this version of Codex and will be ignored\. Upgrade Codex if this path is required\."),
    ("config.otel_invalid", r"Ignoring invalid `(?P<field>otel\.(?:span_attributes|tracestate))` config: [^\r\n]+"),
    ("model.service_tier_unsupported", r"Configured service tier `[^`\r\n]+` is not advertised as supported for model `(?P<model>[^`\r\n]+)` and will be omitted from requests\."),
    ("model.resume_mismatch", r"This session was recorded with model `(?P<previous>[^`\r\n]+)` but is resuming with `(?P<model>[^`\r\n]+)`\. Consider switching back to `(?P=previous)` as it may affect Codex performance\."),
    ("model.metadata_fallback", r"Model metadata for `(?P<model>[^`\r\n]+)` not found\. Defaulting to fallback metadata; this can degrade performance and cause issues\."),
    ("tools.code_mode_model_unsupported", r"Code Mode is enabled in configuration, but model `(?P<model>[^`\r\n]+)` does not advertise Code Mode support\. This may degrade model performance\. Disable `features\.code_mode` and `features\.code_mode_only`, or select a model whose metadata enables Code Mode\."),
)

# Exact producer-owned prefixes: open error suffixes are NEVER returned. A
# prefix candidate can be spoofed or malformed and never establishes cause.
PREFIXES = (
    ("config.agent_role_malformed", "Ignoring malformed agent role definition: "),
    ("config.global_instructions_read_failed", "Failed to read global AGENTS.md instructions from `"),
    ("model.transport_fallback", "Falling back from WebSockets to HTTPS transport. "),
    ("state.transcript_save_failed", "Failed to save the conversation transcript; Codex will continue retrying. Error: "),
    ("state.rollback_save_failed", "Rolled the thread back, but failed to save the rollback marker. Codex will continue retrying. Error: "),
    ("security.execpolicy_amendment_failed", "Failed to apply execpolicy amendment: "),
    ("security.network_amendment_failed", "Failed to apply network policy amendment: "),
)
HOOK_PREFIXES = (
    "loading hooks from both ", "failed to read hooks config ",
    "failed to parse hooks config ", "failed to normalize hooks config path ",
    "failed to parse TOML hooks in ", "invalid matcher ",
    "skipping empty hook command in ", "running async ",
    "ignoring additionalContextLimit for ", "skipping MCP tool hook in ",
    "skipping prompt hook in ", "skipping agent hook in ", "clamping ",
)

def family_coverage():
    """Static coverage only; arbitrary provider text is explicitly unclassifiable."""
    result = {family: "constant_text_shape" for family in CONSTANTS}
    result.update({family: "source_template_shape" for family, _ in TEMPLATES})
    result.update({family: "fixed_prefix_candidate" for family, _ in PREFIXES})
    result.update({"hooks.startup_discovery": "bounded_prefix_candidates_open_family",
                   "features.under_development": "full_template_with_finite_key_enums",
                   "tools.code_mode_unavailable": "full_template_with_finite_behavior_enum"})
    result.update({family: "unclassifiable_arbitrary_provider_text"
                   for family in UNCLASSIFIABLE_OPEN_FAMILIES})
    return result

def _bucket(size):
    if size == 0:
        return "empty"
    for limit in (256, 1024, 4096, MAX_MESSAGE_BYTES):
        if size <= limit:
            return "up_to_" + str(limit)
    return "over_limit"

def classify_warning(params, *, expected_thread_id, expected_model=None,
                     expected_config_path=None):
    """Return only bounded enum/boolean metadata; callers must always stop.

    Params must be a plain JSON object with only `message` and optional
    `threadId`. Global/missing/mismatched thread targets are distinguished and
    stopped, without assigning their text to the active reviewer thread.
    Their safe text shape is still classified: this cannot authorize any action
    and avoids losing diagnostic information before thread/start responds.
    """
    result = {
        "schema": "arc.warning-diagnostic.v1",
        "action": "stop",
        "warning_admitted": False,
        "source_commit": SOURCE_COMMIT,
        "envelope": "invalid_object",
        "thread_binding": "not_checked",
        "text_attribution_to_active_thread": False,
        "message_utf8_size_bucket": "not_checked",
        "family": "unknown",
        "recognition": "none",
        "producer_identity_established": False,
        "details": {},
    }
    if type(params) is not dict:
        return result
    if set(params) - {"message", "threadId"} or "message" not in params:
        result["envelope"] = "unexpected_or_missing_fields"
        return result
    if type(params["message"]) is not str:
        result["envelope"] = "invalid_message_type"
        return result
    message = params["message"]
    if len(message) > MAX_MESSAGE_BYTES:
        result["envelope"] = "message_over_limit"
        result["message_utf8_size_bucket"] = "over_limit"
        return result
    try:
        size = len(message.encode("utf-8", errors="strict"))
    except UnicodeError:
        result["envelope"] = "invalid_message_unicode"
        return result
    result["message_utf8_size_bucket"] = _bucket(size)
    if size > MAX_MESSAGE_BYTES:
        result["envelope"] = "message_over_limit"
        return result
    if "threadId" not in params:
        result["thread_binding"] = "absent"
    elif params["threadId"] is None:
        result["thread_binding"] = "global_null"
    elif type(params["threadId"]) is not str:
        result["thread_binding"] = "invalid"
        result["envelope"] = "invalid_thread_type"
        return result
    elif not params["threadId"]:
        result["thread_binding"] = "empty"
    elif type(expected_thread_id) is not str or not expected_thread_id:
        result["thread_binding"] = "no_expected_thread"
    elif params["threadId"] != expected_thread_id:
        result["thread_binding"] = "mismatch"
    else:
        result["thread_binding"] = "exact"
    result["text_attribution_to_active_thread"] = result["thread_binding"] == "exact"
    result["envelope"] = ("valid_bound" if result["text_attribution_to_active_thread"]
                          else "valid_text_thread_not_bound")
    if any(ord(char) < 32 and char not in "\t\r\n" for char in message):
        result["recognition"] = "control_bearing_message_unclassified"
        return result

    for family, constant in CONSTANTS.items():
        if message == constant:
            result.update(family=family, recognition="constant_text_shape")
            return result

    if message.startswith(UNDERDEV_PREFIX):
        result.update(family="features.under_development",
                      recognition="fixed_prefix_candidate")
        remainder = message[len(UNDERDEV_PREFIX):]
        if remainder.count(UNDERDEV_MIDDLE) == 1 and remainder.endswith("."):
            feature_text, path_dot = remainder.split(UNDERDEV_MIDDLE)
            keys = feature_text.split(", ")
            path = path_dot[:-1]
            if (keys and len(keys) <= len(UNDER_DEVELOPMENT_KEYS)
                    and all(key in UNDER_DEVELOPMENT_KEYS for key in keys)
                    and keys == sorted(set(keys)) and path
                    and not any(ord(char) < 32 for char in path)):
                result["recognition"] = "full_template_with_finite_key_enums"
                result["details"] = {"canonical_feature_keys": keys,
                    "configuration_path_matches_expected": (
                        path == expected_config_path
                        if type(expected_config_path) is str else None)}
        return result

    if message.startswith(CODE_MODE_PREFIX):
        result.update(family="tools.code_mode_unavailable",
                      recognition="fixed_prefix_candidate")
        if message.endswith(CODE_MODE_SUFFIX):
            body = message[len(CODE_MODE_PREFIX):-len(CODE_MODE_SUFFIX)]
            for behavior, label in (
                    ("Falling back to direct tools", "fallback_to_direct_tools"),
                    ("Code mode will fail closed", "fail_closed")):
                separator = ". " + behavior
                if body.endswith(separator) and body[:-len(separator)]:
                    result["recognition"] = "full_template_with_finite_behavior_enum"
                    result["details"] = {"behavior": label,
                        "reason": "opaque_source_error_not_retained"}
                    break
        return result

    for family, pattern in TEMPLATES:
        match = re.fullmatch(pattern, message)
        if match is None:
            continue
        result.update(family=family, recognition="source_template_shape")
        groups = match.groupdict()
        if "field" in groups:
            result["details"]["configuration_field"] = (
                groups["field"] if groups["field"] in REQUIREMENT_FIELDS
                else "unknown_field_not_retained")
        if "model" in groups:
            result["details"]["model_matches_requested"] = (
                groups["model"] == expected_model if type(expected_model) is str else None)
        return result

    for family, prefix in PREFIXES:
        if message.startswith(prefix) and len(message) > len(prefix):
            result.update(family=family, recognition="fixed_prefix_candidate")
            return result
    if any(message.startswith(prefix) and len(message) > len(prefix)
           for prefix in HOOK_PREFIXES):
        result.update(family="hooks.startup_discovery",
                      recognition="fixed_prefix_candidate_open_family")
    return result
