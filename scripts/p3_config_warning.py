"""Exact-source classification of one advisory, without retaining native text.

The literal below is MISSING_BWRAP_WARNING at upstream Codex commit
78c290807ce710180111df227df3b7a4fe845452, codex-rs/sandboxing/src/bwrap.rs.
The startup producer sets details=None, path=None, range=None; the wire
serializer omits path/range. This compatibility rule neither installs nor mounts
bubblewrap and does not change the outer sandbox, native policy or tool surface.

Every returned value is a fixed local label or boolean. Do not add warning text,
native paths, configuration values, lengths or content hashes to these receipts.
"""
from __future__ import annotations

POLICY_VERSION = "P3_CONFIG_WARNING_020_v1"
MISSING_BWRAP_SUMMARY = (
    "Codex could not find bubblewrap on PATH. "
    "Install bubblewrap with your OS package manager. "
    "See the sandbox prerequisites: "
    "https://developers.openai.com/codex/concepts/sandboxing#prerequisites. "
    "Codex will use the bundled bubblewrap in the meantime."
)
POLICY_PARSE_SUMMARY = "Error parsing rules; custom rules not applied."
SQLITE_RECOVERY_SUMMARY = "Codex rebuilt its local database."
DEFAULTS_FALLBACK_SUMMARY = "Invalid configuration; using defaults."
USER_NAMESPACE_SUMMARY = (
    "Codex's Linux sandbox uses bubblewrap and needs access to create user namespaces."
)
WSL1_SUMMARY = (
    "Codex's Linux sandbox uses bubblewrap, which is not supported on WSL1 "
    "because WSL1 cannot create the required user namespaces. "
    "Use WSL2 for sandboxed shell commands."
)
DISABLED_PROJECT_PREFIX = (
    "Project-local config, hooks, and exec policies are disabled in the following folders "
    "until the project is trusted, but skills still load.\n"
)
MANAGED_VALUE_PREFIX = "Configured value for `"
EXACT_FAMILIES = {
    MISSING_BWRAP_SUMMARY: "missing_system_bwrap_bundled_fallback_advisory",
    POLICY_PARSE_SUMMARY: "execution_policy_parse_failure",
    SQLITE_RECOVERY_SUMMARY: "sqlite_database_recovery",
    DEFAULTS_FALLBACK_SUMMARY: "invalid_configuration_defaults_fallback",
    USER_NAMESPACE_SUMMARY: "native_user_namespace_support_warning",
    WSL1_SUMMARY: "native_wsl1_namespace_warning",
}


def classify(params, *, initialized, thread_requested, previously_accepted):
    """Return a privacy-safe decision; permit one exact pre-thread advisory.

    Native malformed/unknown or consequential warnings are terminal at the
    caller. This function does not turn arbitrary free text into diagnostics or
    assume that an absent warning establishes sandbox availability.
    """
    is_object = type(params) is dict
    fields = params if is_object else {}
    summary = fields.get("summary")
    shape = {"parameters_object": is_object, "summary_string": type(summary) is str,
             "details_present": "details" in fields,
             "details_nonnull": fields.get("details") is not None,
             "path_present": "path" in fields, "path_nonnull": fields.get("path") is not None,
             "range_present": "range" in fields, "range_nonnull": fields.get("range") is not None,
             "unknown_fields_present": bool(set(fields) - {"summary", "details", "path", "range"})}
    category = "malformed_config_warning"
    if type(summary) is str:
        category = EXACT_FAMILIES.get(summary, "unrecognized_config_warning")
        # These diagnostic prefix matches never grant admission and never retain
        # the folder, configured value, required value, error or any remainder.
        if summary.startswith(DISABLED_PROJECT_PREFIX):
            category = "disabled_project_configuration"
        elif (summary.startswith(MANAGED_VALUE_PREFIX) and
              "` is disallowed by requirements; falling back" in summary):
            category = "managed_requirement_value_fallback"
    strict_advisory_shape = (is_object and set(fields) == {"summary", "details"}
        and type(summary) is str and fields["details"] is None)
    recognized = category == "missing_system_bwrap_bundled_fallback_advisory"
    context = "admitted_prethread_advisory"
    if not strict_advisory_shape:
        context = "unsupported_warning_shape"
    elif not recognized:
        context = "unsupported_warning"
    elif (initialized is not True or thread_requested is not False
          or type(previously_accepted) is not int or previously_accepted < 0):
        context = "unexpected_warning_context"
    elif previously_accepted != 0:
        context = "repeated_warning"
    return {"category": category, "decision": context,
            "admitted": context == "admitted_prethread_advisory",
            "raw_content_saved_or_hashed": False, "shape": shape}
