#!/usr/bin/env python3
"""Pure preparation helpers for a later bounded reviewer startup.

These functions do not launch a client, read files, choose a model, alter an
account or policy, or establish an effective runtime boundary. The caller must
obtain the existing source-audited base overrides and pinned schema separately.
The returned catalog is one complete filtered *page*, not proof of entitlement.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re

CONFIG_SCHEMA_SHA256 = "ed663d6d4c6c8b36917596882414c93858f6cf9ca5449ea8c616fc76d1aac114"
REQUESTED_MODEL = "gpt-6-astra"
EFFORTS = ("none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra")
EXTRA_FALSE_FEATURES = ("code_mode_host", "image_generation", "deferred_executor",
                        "current_time_reminder")
IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,95}\Z", re.ASCII)
BARE_KEY = re.compile(r"[A-Za-z0-9_-]+\Z", re.ASCII)
# Exact ModelListResponse.Model properties from the pinned experimental schema,
# SHA256 dd4014851ef7c60ecacfa5fa4d1a9f02d7dcc2aada93c83091a717b27b753d63.
# Recognized but unselected fields are discarded without inspecting their text.
MODEL_FIELDS = frozenset((
    "additionalSpeedTiers", "availabilityNux", "defaultReasoningEffort",
    "defaultServiceTier", "description", "displayName", "hidden", "id",
    "inputModalities", "isDefault", "model", "modelSpecialty", "multiAgentVersion",
    "serviceTiers", "supportedReasoningEfforts", "supportsPersonality", "upgrade",
    "upgradeInfo",
))


class Stop(RuntimeError):
    """Only fixed local reasons; never interpolate received field names/values."""


def require(condition, reason):
    if not condition:
        raise Stop(reason)


def _accepts_boolean(schema, definitions):
    if schema.get("type") == "boolean":
        return True
    reference = schema.get("$ref")
    if reference:
        schema = definitions[reference.removeprefix("#/definitions/")]
    return any(item == {"type": "boolean"} for item in schema.get("anyOf", []))


def reviewer_overrides(base_overrides, config_schema_bytes):
    """Extend a supplied preflight profile; retain its other values unchanged.

    The exact schema pin is checked in memory. Host Code Mode must be literal
    false: its object form can retain nested fallback settings. A structured
    Code Mode false keeps the functions namespace direct if model metadata
    nevertheless requests Code Mode. Neither control is an execution receipt.
    """
    require(type(config_schema_bytes) is bytes and
            hashlib.sha256(config_schema_bytes).hexdigest() == CONFIG_SCHEMA_SHA256,
            "Pinned reviewer configuration schema differs")
    require(type(base_overrides) is dict and all(type(k) is str for k in base_overrides),
            "Invalid supplied base profile")
    require(base_overrides.get("features.code_mode") is False,
            "Expected source-audited false Code Mode base control")
    require(not any(k.startswith(("features.code_mode.", "features.code_mode_host."))
                    for k in base_overrides), "Conflicting nested Code Mode override")
    schema = json.loads(config_schema_bytes)
    definitions = schema["definitions"]
    features = schema["properties"]["features"]["properties"]
    require(all(_accepts_boolean(features[name], definitions)
                for name in EXTRA_FALSE_FEATURES), "Unsupported restrictive feature syntax")
    code_mode = definitions["CodeModeConfigToml"]["properties"]
    require(code_mode["enabled"] == {"type": "boolean"} and
            code_mode["direct_only_tool_namespaces"]["type"] == "array" and
            code_mode["direct_only_tool_namespaces"]["items"] == {"type": "string"},
            "Unsupported direct namespace syntax")
    require(definitions["OrchestratorToml"]["properties"]["mcp"] ==
            {"$ref": "#/definitions/OrchestratorFeatureToml"} and
            definitions["OrchestratorFeatureToml"]["properties"]["enabled"] ==
            {"type": "boolean"}, "Unsupported orchestrator MCP syntax")
    result = copy.deepcopy(base_overrides)
    result.update({"features." + name: False for name in EXTRA_FALSE_FEATURES})
    result["orchestrator.mcp.enabled"] = False
    result["features.code_mode"] = {
        "enabled": False, "direct_only_tool_namespaces": ["functions"]}
    return result


def _toml_literal(value, depth=0):
    """Render the finite configuration value types as TOML, never shell text."""
    require(depth <= 4, "Configuration value nesting exceeds profile bound")
    if type(value) is bool:
        return "true" if value else "false"
    if type(value) is int:
        require(-(2 ** 63) <= value < 2 ** 63, "Configuration integer exceeds TOML range")
        return str(value)
    if type(value) is str:
        require(len(value) <= 4096, "Configuration string exceeds profile bound")
        try:
            value.encode("utf-8", errors="strict")
        except UnicodeError:
            raise Stop("Invalid configuration Unicode value") from None
        # JSON basic-string escaping is valid for these TOML strings after DEL
        # is escaped. Keep Unicode scalar values literal, avoiding JSON's UTF16
        # surrogate-pair escapes, which are not valid TOML Unicode scalars.
        return json.dumps(value, ensure_ascii=False).replace("\x7f", "\\u007f")
    if type(value) is list:
        require(len(value) <= 100, "Configuration list exceeds profile bound")
        return "[" + ", ".join(_toml_literal(item, depth + 1) for item in value) + "]"
    if type(value) is dict:
        require(len(value) <= 32 and all(type(key) is str and BARE_KEY.fullmatch(key)
                                        for key in value), "Invalid inline configuration table")
        return "{" + ", ".join(key + " = " + _toml_literal(item, depth + 1)
                                 for key, item in value.items()) + "}"
    raise Stop("Unsupported configuration value type")


def cli_override_arguments(overrides):
    """Return an argv list for -c values; do not join or pass it through a shell.

    In particular, JSON dictionary syntax must never be used for TOML inline
    tables. The existing metadata reader's json.dumps(value) approach is not
    suitable for the structured features.code_mode value prepared here.
    """
    require(type(overrides) is dict and len(overrides) <= 128, "Invalid override profile")
    result = []
    for key, value in overrides.items():
        require(type(key) is str and len(key) <= 128 and
                all(BARE_KEY.fullmatch(part) for part in key.split(".")),
                "Invalid dotted configuration key")
        result.extend(("-c", key + "=" + _toml_literal(value)))
    return result


def _identifier(value):
    require(type(value) is str and IDENTIFIER.fullmatch(value) is not None,
            "Invalid or oversized model identifier")
    return value


def safe_model_catalog(result, requested_model=REQUESTED_MODEL, *, include_hidden_requested=None):
    """Retain bounded identifiers and enum values for every row on one page.

    This is a strict local output contract, not a replacement native schema.
    Unknown fields are counted and discarded, as the native schema leaves its
    objects open. Malformed selected metadata fails without echoing data.
    Native effort names are open strings: unknown names are counted, never
    copied, and never silently mapped to a supported effort. Optional null
    metadata outside the selected fields is discarded like other unused data.
    """
    requested_model = _identifier(requested_model)
    require(include_hidden_requested is None or type(include_hidden_requested) is bool,
            "Invalid caller pagination scope")
    require(type(result) is dict and len(result) <= 16,
            "Invalid or oversized model-catalog response")
    rows = result.get("data")
    require(type(rows) is list and len(rows) <= 100, "Invalid or oversized catalog page")
    cursor = result.get("nextCursor")
    require(cursor is None or (type(cursor) is str and 0 < len(cursor) <= 1024),
            "Invalid or oversized catalog cursor")
    entries, identifiers = [], set()
    unknown_row_fields, unknown_effort_fields = 0, 0
    for row in rows:
        require(type(row) is dict and len(row) <= 64,
                "Invalid or oversized model-catalog entry")
        unknown_row_fields += len(set(row) - MODEL_FIELDS)
        model, identifier = _identifier(row.get("model")), _identifier(row.get("id"))
        require(identifier not in identifiers, "Duplicate catalog identifier")
        identifiers.add(identifier)
        require(type(row.get("isDefault")) is bool and type(row.get("hidden")) is bool,
                "Invalid model boolean metadata")
        efforts, default = row.get("supportedReasoningEfforts"), row.get("defaultReasoningEffort")
        require(type(efforts) is list and len(efforts) <= 32,
                "Invalid or oversized effort metadata")
        require(type(default) is str and 0 < len(default) <= 128,
                "Invalid default effort metadata")
        recognized, unknown = set(), 0
        for item in efforts:
            require(type(item) is dict and len(item) <= 16,
                    "Invalid or oversized effort metadata object")
            unknown_effort_fields += len(set(item) - {"description", "reasoningEffort"})
            name = item.get("reasoningEffort")
            require(type(name) is str and 0 < len(name) <= 128,
                    "Invalid effort metadata")
            if name in EFFORTS:
                recognized.add(name)
            else:
                unknown += 1
        entries.append({
            "model": model, "id": identifier, "is_default": row["isDefault"],
            "hidden": row["hidden"],
            "supported_efforts": [name for name in EFFORTS if name in recognized],
            "unrecognized_effort_count": unknown,
            "default_effort": default if default in EFFORTS else None,
            "default_effort_recognized": default in EFFORTS,
            "default_effort_in_supported_list": default in recognized,
        })
    return {
        "response_shape_recognized": True, "page_entry_count": len(entries),
        "entries": entries, "additional_page_available": cursor is not None,
        "page_complete_for_returned_catalog": cursor is None,
        "include_hidden_requested": include_hidden_requested,
        "discarded_unknown_response_field_count": len(set(result) - {"data", "nextCursor"}),
        "discarded_unknown_entry_field_count": unknown_row_fields,
        "discarded_unknown_effort_field_count": unknown_effort_fields,
        "exact_requested_model_present_on_page": any(
            entry["model"] == requested_model for entry in entries),
        "exact_requested_id_present_on_page": any(
            entry["id"] == requested_model for entry in entries),
        "effort_names_are_local_output_allowlist": True,
        "model_selection_performed": False,
        "scope": "returned_model_catalog_page_may_use_cached_metadata",
        "model_entitlement_verified": False,
        "model_tool_registry_verified": False,
        "scientific_reviewer_boundary_verified": False,
    }
