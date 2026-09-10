"""One exact disabled-host warning exception under already admitted controls.

No I/O, authority changes, tool registration, native launch or model call occurs.
The pinned source warning is compatible with the functions direct-only route;
recognizing its text neither authenticates its producer nor proves that route
works. The controller still requires a real broker read and traversal refusal
in a synthetic session before starting a separate scientific session.

Source: https://github.com/openai/codex/tree/78c290807ce710180111df227df3b7a4fe845452
Accessed 2026-09-10. See the checkpoint 027 source audit for the routing argument.
"""
from __future__ import annotations

POLICY_VERSION = "P3_DISABLED_CODEMODE_NOTICE_027_v1"
SOURCE_COMMIT = "78c290807ce710180111df227df3b7a4fe845452"
MAX_NOTICES = 1
EXACT_MESSAGE = (
    "Code Mode is unavailable because code-mode host is disabled. "
    "Code mode will fail closed; enable `features.code_mode_host` "
    "and install `codex-code-mode-host`."
)
EFFECTIVE_TRUE_FIELDS = (
    "profile_valid", "response_shape_valid", "source_layers_shape_valid",
    "unique_session_layer", "session_layer_enabled", "session_layer_name_exact",
    "all_requested_controls_verified", "source_sensitive_tables_verified",
    "nondefault_instruction_overrides_absent",
)


def _identifier(value):
    return (type(value) is str and 0 < len(value) <= 256
            and all(32 <= ord(char) < 127 for char in value))


def _profile_matches(requested):
    if type(requested) is not dict or not requested:
        return False
    value = requested.get("features.code_mode")
    return (type(value) is dict and set(value) == {"enabled", "direct_only_tool_namespaces"}
        and value["enabled"] is False
        and type(value["direct_only_tool_namespaces"]) is list
        and len(value["direct_only_tool_namespaces"]) == 1
        and type(value["direct_only_tool_namespaces"][0]) is str
        and value["direct_only_tool_namespaces"][0] == "functions"
        and requested.get("features.code_mode_host") is False
        and requested.get("features.code_mode_only") is False
        and all(type(key) is str for key in requested)
        and not any(key.startswith(("features.code_mode.", "features.code_mode_host."))
                    for key in requested))


def classify(params, *, notification_envelope_valid, expected_thread_id,
             requested, effective_config, profile_admitted, selected_binding,
             model_turn_sent, previously_admitted):
    """Compare complete literal text, shape, controls and one-session history.

    The supplied effective receipt must be from unchanged full configuration
    admission. Literal booleans are required; integer 1 is never a substitute.
    The turn need only have been fully sent; its response and turn/started may
    follow this source startup warning. Thread/status activity is not a startup
    barrier. The one-turn binding, not a quiet-pipe/window inference, limits the
    exception. No native or caller strings are saved.
    """
    shape = (type(params) is dict and set(params) == {"message", "threadId"}
             and type(params.get("message")) is str and _identifier(params.get("threadId")))
    exact = shape and params["message"] == EXACT_MESSAGE
    bound = (shape and _identifier(expected_thread_id)
             and params["threadId"] == expected_thread_id)
    profile_matches = _profile_matches(requested)
    effective = (type(effective_config) is dict
        and all(effective_config.get(key) is True for key in EFFECTIVE_TRUE_FIELDS)
        and effective_config.get("first_failure") is None
        and type(effective_config.get("controls")) is dict
        and type(requested) is dict
        and set(effective_config["controls"]) == set(requested)
        and all(value is True for value in effective_config["controls"].values()))
    selected = (type(selected_binding) is dict
        and set(selected_binding) == {"model", "id", "effort"}
        and type(selected_binding["model"]) is str
        and selected_binding["model"] == "gpt-5.6-sol"
        and type(selected_binding["effort"]) is str
        and selected_binding["effort"] == "max"
        and _identifier(selected_binding["id"]))
    decision = "admitted_exact_disabled_host_notice"
    if notification_envelope_valid is not True or not shape:
        decision = "unsupported_warning_shape"
    elif not exact:
        decision = "unsupported_warning_text"
    elif not bound:
        decision = "foreign_or_unbound_warning_thread"
    elif profile_admitted is not True or not profile_matches or not effective:
        decision = "restrictive_profile_not_admitted"
    elif not selected:
        decision = "exact_sol_max_binding_not_admitted"
    elif model_turn_sent is not True:
        decision = "model_turn_not_sent"
    elif type(previously_admitted) is not int or previously_admitted != 0:
        decision = "repeated_notice_or_invalid_history"
    return {
        "policy_version": POLICY_VERSION,
        "category": "exact_disabled_codemode_host" if exact else "unrecognized_warning",
        "decision": decision,
        "admitted": decision == "admitted_exact_disabled_host_notice",
        "exact_parameter_shape": shape,
        "exact_thread_binding": bound,
        "related_controls_verified_disabled": profile_matches and effective,
        "exact_sol_max_selected": selected,
        "native_tool_inventory_attested": False,
        "producer_identity_established": False,
        "direct_broker_route_proven": False,
        "raw_content_saved_or_hashed": False,
    }
