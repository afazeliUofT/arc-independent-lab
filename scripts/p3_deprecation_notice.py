"""Exact-source startup notice compatibility; no authority or native text retained.

Rebuilt correction, not recovered historical024 bytes. Upstream Codex commit
78c290807ce710180111df227df3b7a4fe845452, codex-rs/features/src/lib.rs
records deprecated key presence before testing its bool value (531-603), then
formats these notices (647-698). codex-rs/features/src/legacy.rs supplies the
alias/canonical mapping. The failed live report discarded the actual notice;
this allowlist does not claim to reconstruct which notice that client emitted.

Only the complete exact summary/details pair is compared, transiently. Returned
receipts contain fixed local labels and booleans, never content, paths, lengths
or hashes. This helper never edits configuration or enables a deprecated flag.
"""
from __future__ import annotations

POLICY_VERSION = "P3_DEPRECATION_NOTICE_024_REBUILT_v1"
SOURCE_COMMIT = "78c290807ce710180111df227df3b7a4fe845452"
MAX_NOTICES = 8
ALIASES = (
    ("codex_hooks", "hooks"),
    ("collab", "multi_agent"),
    ("connectors", "apps"),
    ("experimental_use_unified_exec_tool", "unified_exec"),
    ("memory_tool", "memories"),
)
WEB_ALIASES = ("web_search", "web_search_cached", "web_search_request")
REQUIRED_FALSE_CONTROLS = frozenset(
    "features." + key for pair in ALIASES for key in pair
) | frozenset("features." + key for key in WEB_ALIASES)
WEB_DETAILS = (
    'Set `web_search` to `"live"`, `"indexed"`, `"cached"`, or `"disabled"` '
    'at the top level (or under a profile) in config.toml if you want to override it.'
)
EXACT_PAIRS = {
    (f"`[features].{alias}` is deprecated. Use `[features].{canonical}` instead.",
     f"Enable it with `--enable {canonical}` or `[features].{canonical}` in config.toml. "
     "See https://developers.openai.com/codex/config-basic#feature-flags for details."):
    "disabled_legacy_alias_" + alias
    for alias, canonical in ALIASES
}
EXACT_PAIRS.update({
    (f"`[features].{alias}` is deprecated because web search is enabled by default.",
     WEB_DETAILS): "disabled_legacy_web_alias_" + alias
    for alias in WEB_ALIASES
})
CATEGORIES = frozenset(EXACT_PAIRS.values())


def classify(params, *, requested, profile_admitted, thread_requested,
             startup_window_open, accepted_categories):
    """Admit at most eight distinct exact notices after restrictive admission.

    The caller must have completed unchanged effective configuration admission.
    The related aliases and canonical controls must still all be literal False,
    including web feature aliases, with top-level web_search exactly disabled.
    Passing 0, a structured false value, a missing key, or a bool-like value
    never satisfies the control check. Duplicates are terminal, not ignored.
    """
    fields = params if type(params) is dict else {}
    summary, details = fields.get("summary"), fields.get("details")
    shape = {"parameters_object": type(params) is dict,
             "exact_parameter_keys": type(params) is dict and
                set(fields) == {"summary", "details"},
             "summary_string": type(summary) is str,
             "details_string": type(details) is str}
    strict_shape = all(shape.values())
    category = "malformed_deprecation_notice"
    if strict_shape:
        category = EXACT_PAIRS.get((summary, details), "unrecognized_deprecation_notice")
    profile_matches = (type(requested) is dict and
        all(requested.get(key) is False for key in REQUIRED_FALSE_CONTROLS) and
        type(requested.get("web_search")) is str and requested["web_search"] == "disabled")
    valid_history = (type(accepted_categories) is set and
        all(type(value) is str and value in CATEGORIES for value in accepted_categories) and
        len(accepted_categories) <= MAX_NOTICES)
    decision = "admitted_disabled_alias_startup_notice"
    if not strict_shape:
        decision = "unsupported_notice_shape"
    elif category not in CATEGORIES:
        decision = "unsupported_notice"
    elif profile_admitted is not True or not profile_matches:
        decision = "restrictive_profile_not_admitted"
    elif thread_requested is not True:
        decision = "thread_start_not_requested"
    elif startup_window_open is not True:
        decision = "startup_window_closed"
    elif not valid_history:
        decision = "invalid_notice_history"
    elif category in accepted_categories:
        decision = "repeated_notice"
    elif len(accepted_categories) >= MAX_NOTICES:
        decision = "notice_count_ceiling"
    return {"category": category, "decision": decision,
            "admitted": decision == "admitted_disabled_alias_startup_notice",
            "related_controls_verified_disabled": profile_matches,
            "raw_content_saved_or_hashed": False, "shape": shape}
