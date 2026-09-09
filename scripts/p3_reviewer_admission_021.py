#!/usr/bin/env python3
"""Pure admission and payload construction for one separately controlled reviewer.

No files, processes, credentials or model operations are accessed. The caller
owns actual scope authority, preserved config/policy origins, the empty native
filesystem view, fresh process state and the scientific packet. These helpers
validate only the supplied observations; they never claim a complete tool
registry or establish scientific independence from an empty response field.
Wire spelling is pinned to the Codex 0.151.0 embedded experimental schemas.
"""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import re
import sys


def _module(name):
    """Load fixed sibling implementations under isolated Python startup.

    The parent separately pins these files. Reuse only the same canonical source
    path; never obtain a same-named package from ambient sys.path.
    """
    path = Path(__file__).resolve().with_name(name + ".py")
    existing = sys.modules.get(name)
    if existing is not None:
        origin = getattr(existing, "__file__", None)
        if type(origin) is not str or Path(origin).resolve() != path:
            raise RuntimeError("Conflicting reviewer admission dependency origin")
        return existing
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return module


_controls = _module("gate0_config_controls")
_profile_module = _module("p3_reviewer_profile")
MAX_LAYERS, SOURCE_TYPES = _controls.MAX_LAYERS, _controls.SOURCE_TYPES
TOOL_CONTROL_PATHS = _controls.TOOL_CONTROL_PATHS
observe_projected_tool_controls = _controls.observe_projected_tool_controls
EFFORTS, REQUESTED_MODEL = _profile_module.EFFORTS, _profile_module.REQUESTED_MODEL

PROVIDER = "openai"
PERMISSIONS = ":read-only"
IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,255}\Z", re.ASCII)
CODE_MODE = {"enabled": False, "direct_only_tool_namespaces": ["functions"]}
REQUIRED_CONTROLS = {
    "agents.enabled": False, "features.multi_agent_v2": False,
    "features.multi_agent": False, "features.code_mode_host": False,
    "features.code_mode": CODE_MODE, "features.image_generation": False,
    "features.deferred_executor": False, "features.current_time_reminder": False,
    "orchestrator.mcp.enabled": False, "orchestrator.skills.enabled": False,
    "memories.use_memories": False, "memories.generate_memories": False,
    "tools.update_plan.enabled": False,
    "tools.experimental_request_user_input.enabled": False,
    "web_search": "disabled", "history.persistence": "none",
    "approval_policy": "never",
}
# ConfigRead serializes an ApiConfig projection. It omits model-instruction-file
# fields and the two nested tools controls; inspect enabled native layers too.
INSTRUCTION_FIELDS = (
    "instructions", "developer_instructions", "model_instructions_file",
    "compact_prompt", "experimental_compact_prompt_file",
    "experimental_realtime_start_instructions", "experimental_realtime_ws_backend_prompt",
)


class Stop(RuntimeError):
    """Fixed local category; received values must never enter diagnostics."""


def require(condition, reason):
    if not condition:
        raise Stop(reason)


def _identifier(value):
    require(type(value) is str and IDENTIFIER.fullmatch(value) is not None,
            "Invalid bounded session identifier")
    return value


def _path(value):
    require(type(value) is str and 1 < len(value) <= 4096 and value.startswith("/")
            and not any(ord(c) < 32 for c in value) and "\\" not in value
            and all(x not in ("", ".", "..") for x in value.split("/")[1:]),
            "Invalid canonical absolute reviewer path")
    return value


def _equal(actual, expected):
    if type(actual) is not type(expected):
        return False
    if type(expected) is dict:
        return set(actual) == set(expected) and all(_equal(actual[k], v)
                                                  for k, v in expected.items())
    if type(expected) is list:
        return len(actual) == len(expected) and all(_equal(a, b) for a, b in zip(actual, expected))
    return actual == expected


def _profile(profile):
    require(type(profile) is dict and len(profile) <= 128 and all(type(k) is str for k in profile),
            "Invalid restrictive reviewer profile")
    require(all(_equal(profile.get(k), v) for k, v in REQUIRED_CONTROLS.items()),
            "Required restrictive reviewer control differs")
    require(not any(k in profile for k in INSTRUCTION_FIELDS),
            "Custom reviewer instruction override denied")
    require(not any(k.startswith(("features.code_mode.", "features.code_mode_host."))
                    for k in profile), "Conflicting nested reviewer feature override")


def select_model(catalog):
    """Choose only the requested exact model and its highest advertised effort.

    Input is a completed safe_model_catalog page or the caller's bounded,
    validated combination of up to eight pages, not raw account/config data.
    Catalog presence is not entitlement; the caller retains catalog on denial.
    """
    require(type(catalog) is dict and catalog.get("response_shape_recognized") is True,
            "Missing recognized reviewer model catalog")
    require(catalog.get("page_complete_for_returned_catalog") is True and
            catalog.get("additional_page_available") is False,
            "Reviewer catalog is incomplete")
    entries = catalog.get("entries")
    require(type(entries) is list and len(entries) <= 800,
            "Invalid bounded reviewer catalog entries")
    matches = [row for row in entries if type(row) is dict and row.get("model") == REQUESTED_MODEL]
    require(len(matches) == 1, "Requested exact reviewer model absent or ambiguous")
    row = matches[0]
    require(row.get("unrecognized_effort_count") == 0 and
            type(row.get("unrecognized_effort_count")) is int,
            "Reviewer effort ordering has unrecognized values")
    supported = row.get("supported_efforts")
    require(type(supported) is list and supported and
            all(type(value) is str and value in EFFORTS for value in supported) and
            len(set(supported)) == len(supported), "Invalid advertised reviewer efforts")
    return {"model": REQUESTED_MODEL, "id": _identifier(row.get("id")),
            "effort": max(supported, key=EFFORTS.index)}


def _model_effort(model, effort):
    require(model == REQUESTED_MODEL and type(model) is str,
            "Reviewer model fallback denied")
    require(type(effort) is str and effort in EFFORTS, "Unsupported reviewer effort")


def thread_params(model, effort, cwd, dynamic_tools, profile):
    """Build exactly one ephemeral environmentless startup; no history import."""
    _model_effort(model, effort)
    _path(cwd)
    _profile(profile)
    require(type(dynamic_tools) is list and 0 < len(dynamic_tools) <= 5,
            "Invalid bounded reviewer dynamic tools")
    allowed = {"read_text", "read_page_image", "hash_file", "run_observer_audit", "submit_verdict"}
    names = []
    for spec in dynamic_tools:
        require(type(spec) is dict and set(spec) == {"type", "name", "description", "inputSchema"}
                and spec.get("type") == "function" and spec.get("name") in allowed
                and type(spec.get("description")) is str and len(spec["description"]) <= 4096
                and type(spec.get("inputSchema")) is dict, "Unexpected reviewer dynamic tool spec")
        names.append(spec["name"])
    require(len(set(names)) == len(names), "Duplicate reviewer dynamic tool")
    config = copy.deepcopy(profile)
    config["model_reasoning_effort"] = effort
    return {"model": model, "modelProvider": PROVIDER,
            "allowProviderModelFallback": False, "ephemeral": True,
            "sessionStartSource": "startup", "cwd": cwd, "runtimeWorkspaceRoots": [],
            "permissions": PERMISSIONS, "approvalPolicy": "never", "approvalsReviewer": "user",
            "environments": [], "selectedCapabilityRoots": [], "experimentalRawEvents": False,
            "dynamicTools": copy.deepcopy(dynamic_tools), "config": config}


def turn_params(thread_id, model, effort, prompt):
    _identifier(thread_id)
    _model_effort(model, effort)
    require(type(prompt) is str and 0 < len(prompt) <= 100000,
            "Invalid bounded reviewer input")
    try:
        prompt.encode("utf-8", errors="strict")
    except UnicodeError:
        raise Stop("Invalid reviewer input Unicode") from None
    return {"threadId": thread_id, "input": [{"type": "text", "text": prompt}],
            "environments": [], "model": model, "effort": effort,
            "permissions": PERMISSIONS, "approvalPolicy": "never", "approvalsReviewer": "user"}


def validate_thread_response(result, *, model, effort, cwd, allowed_instruction_sources=()):
    """Validate measured controls without mistaking empty turns for fresh context.

    The minimal controller admits no native instruction file. Any future nonempty
    allowlist needs a separately source/content-pinned contract, not arbitrary
    path equality through this helper. Built-in model/policy instructions remain
    native; effective user-supplied instruction fields are checked separately.
    """
    _model_effort(model, effort)
    _path(cwd)
    require(allowed_instruction_sources == (), "Unpinned native instruction allowlist denied")
    require(type(result) is dict and type(result.get("thread")) is dict,
            "Missing reviewer thread response")
    require(result.get("model") == model and result.get("modelProvider") == PROVIDER and
            result.get("reasoningEffort") == effort, "Reviewer model provider or effort differs")
    require(result.get("approvalPolicy") == "never" and result.get("approvalsReviewer") == "user",
            "Reviewer approval controls differ")
    active, sandbox = result.get("activePermissionProfile"), result.get("sandbox")
    require(type(active) is dict and set(active) <= {"id", "extends"} and
            active.get("id") == PERMISSIONS and active.get("extends") is None,
            "Reviewer permission profile differs")
    require(type(sandbox) is dict and set(sandbox) <= {"type", "networkAccess"} and
            sandbox.get("type") == "readOnly" and sandbox.get("networkAccess", False) is False,
            "Reviewer native sandbox differs")
    require(result.get("cwd") == cwd and result.get("runtimeWorkspaceRoots") == [],
            "Reviewer cwd or workspace roots differ")
    require(result.get("instructionSources") == [], "Unexpected reviewer instruction file origin")
    thread = result["thread"]
    require(thread.get("ephemeral") is True and thread.get("cwd") == cwd and
            thread.get("modelProvider") == PROVIDER and thread.get("cliVersion") == "0.151.0",
            "Reviewer thread provenance differs")
    require(all(thread.get(name) is None for name in
                ("forkedFromId", "parentThreadId", "projectId", "path", "agentNickname", "agentRole")),
            "Reviewer thread has unexpected inherited provenance")
    require(thread.get("turns") == [] and thread.get("preview") == "" and
            thread.get("status") == {"type": "idle"}, "Reviewer thread is not an idle startup")
    return {"thread_id": _identifier(thread.get("id")),
            "session_id": _identifier(thread.get("sessionId")),
            "returned_controls_match": True, "native_instruction_files_absent": True,
            "thread_response_history_field_is_not_freshness_proof": True,
            "full_fresh_context_verified": False, "full_tool_registry_verified": False}



def validate_thread_settings(params, *, thread_id, model, effort, cwd):
    """Accept only a bound notification preserving every admitted control.

    Same-value explicit turn overrides can participate in native settings
    processing. Receiving this event is not itself a permission change. The
    deprecated multiAgentMode compatibility constant is not agent-isolation
    evidence; actual collaboration controls were admitted from configuration.
    """
    _identifier(thread_id)
    _model_effort(model, effort)
    _path(cwd)
    require(type(params) is dict and set(params) == {"threadId", "threadSettings"}
            and params["threadId"] == thread_id, "Foreign or malformed reviewer settings event")
    settings = params["threadSettings"]
    allowed = {"activePermissionProfile", "approvalPolicy", "approvalsReviewer", "collaborationMode",
               "cwd", "effort", "model", "modelProvider", "multiAgentMode", "personality",
               "sandboxPolicy", "serviceTier", "summary"}
    required = {"approvalPolicy", "approvalsReviewer", "collaborationMode", "cwd", "model",
                "modelProvider", "sandboxPolicy"}
    require(type(settings) is dict and required <= set(settings) <= allowed,
            "Unexpected reviewer settings shape")
    require(settings.get("model") == model and settings.get("modelProvider") == PROVIDER
            and settings.get("effort") == effort and settings.get("cwd") == cwd,
            "Reviewer settings model effort or cwd differs")
    require(settings.get("approvalPolicy") == "never" and settings.get("approvalsReviewer") == "user",
            "Reviewer settings approval controls differ")
    active, sandbox = settings.get("activePermissionProfile"), settings.get("sandboxPolicy")
    require(type(active) is dict and set(active) <= {"id", "extends"}
            and active.get("id") == PERMISSIONS and active.get("extends") is None,
            "Reviewer settings permission profile differs")
    require(type(sandbox) is dict and set(sandbox) <= {"type", "networkAccess"}
            and sandbox.get("type") == "readOnly" and sandbox.get("networkAccess", False) is False,
            "Reviewer settings native sandbox differs")
    mode = settings["collaborationMode"]
    require(type(mode) is dict and set(mode) == {"mode", "settings"} and mode["mode"] == "default",
            "Reviewer settings collaboration mode differs")
    nested = mode["settings"]
    require(type(nested) is dict and set(nested) <= {"model", "reasoning_effort", "developer_instructions"}
            and nested.get("model") == model and nested.get("reasoning_effort") == effort
            and nested.get("developer_instructions") is None,
            "Reviewer settings collaboration overrides differ")
    require(settings.get("multiAgentMode", "explicitRequestOnly") == "explicitRequestOnly",
            "Reviewer settings compatibility metadata differs")
    require(settings.get("personality") in (None, "none", "friendly", "pragmatic")
            and settings.get("summary") in (None, "auto", "concise", "detailed", "none"),
            "Unrecognized reviewer presentation setting")
    tier = settings.get("serviceTier")
    require(tier is None or (type(tier) is str and 0 < len(tier) <= 128),
            "Invalid reviewer native service tier metadata")
    return {"thread_id": thread_id, "settings_match_admitted_controls": True,
            "custom_collaboration_instructions_absent": True,
            "settings_event_is_not_tool_registry_attestation": True}


def _leaf(value, path):
    for component in path.split("."):
        if type(value) is not dict:
            return "shadow", None
        if component not in value:
            return "absent", None
        value = value[component]
    return "leaf", value


def _structured_boolean_path(path):
    parts = path.split(".")
    feature = None
    if len(parts) == 2 and parts[0] == "features":
        feature = parts[1]
    elif len(parts) == 4 and parts[0] == "profiles" and parts[2] == "features":
        feature = parts[3]
    return feature if feature in ("multi_agent_v2", "network_proxy") else None


def _leaves(prefix, value):
    """Native scalar origin paths, including array indices and boolean aliases.

    Exact-release fingerprint.rs recursively visits every table and array,
    emits no collection-origin entry, and transforms only the two structured
    boolean features declared by merge.rs. This is not a projection rule:
    code_mode_host still must be literal false and Code Mode full-table equality
    is checked separately. No requested control uses either native key alias.
    """
    if type(value) is dict:
        for key, child in value.items():
            yield from _leaves(prefix + "." + key, child)
    elif type(value) is list:
        for index, child in enumerate(value):
            yield from _leaves(prefix + "." + str(index), child)
    elif type(value) is bool and _structured_boolean_path(prefix) is not None:
        if _structured_boolean_path(prefix) == "network_proxy":
            yield prefix, value
        yield prefix + ".enabled", value
    else:
        yield prefix, value


def _shape(value):
    return {dict: "object", list: "array", bool: "boolean", str: "string",
            int: "integer", float: "number", type(None): "null"}.get(type(value), "other")


def _origin_observation(origin, winner):
    obj = type(origin) is dict
    name = origin.get("name") if obj else None
    version = origin.get("version") if obj else None
    source = name.get("type") if type(name) is dict else None
    source = source if type(source) is str and source in SOURCE_TYPES else None
    entry = {
        "present": origin is not None,
        "metadata_shape_valid": obj and set(origin) == {"name", "version"},
        "source_type": source,
        "exact_session_source": name == {"type": "sessionFlags"},
        "version_shape_valid": type(version) is str and 0 < len(version) <= 256,
        "version_matches_session_layer": type(winner) is dict and
            type(version) is str and version == winner.get("version"),
    }
    entry["verified_session_origin"] = all(entry[k] for k in (
        "metadata_shape_valid", "exact_session_source", "version_shape_valid",
        "version_matches_session_layer"))
    return entry


def observe_effective_config(result, requested):
    """Safe complete observation, including on failed admission.

    Only caller-owned requested control names and fixed categories/booleans are
    returned. Native values, path strings, layer names, versions, unknown keys
    and diagnostics are neither retained nor hashed. Every control is examined
    before returning a failed result; no failed model admission is waived.
    """
    report = {"observation": "P3_REVIEWER_EFFECTIVE_CONFIG_021_v1",
        "controls": {}, "control_observations": {}, "instruction_observations": {},
        "profile_valid": False, "response_shape_valid": False,
        "source_layers_shape_valid": False, "unique_session_layer": False,
        "session_layer_enabled": False, "session_layer_name_exact": False,
        "all_requested_controls_verified": False, "source_sensitive_tables_verified": False,
        "nondefault_instruction_overrides_absent": False,
        "full_instruction_context_verified": False, "runtime_tool_registry_verified": False,
        "raw_native_values_saved_or_hashed": False,
        "projected_structured_multi_agent_v2_is_deliberate_dependency_stop": True,
        "first_failure": None}

    def failure(check, reason, control=None):
        if report["first_failure"] is None:
            report["first_failure"] = {"check": check, "reason": reason, "control": control}

    try:
        _profile(requested)
        report["profile_valid"] = True
    except Stop:
        failure("requested_profile", "Invalid restrictive reviewer profile")
        return report
    valid = type(result) is dict and type(result.get("config")) is dict and \
        type(result.get("origins")) is dict and type(result.get("layers")) is list and \
        0 < len(result["layers"]) <= MAX_LAYERS
    report["response_shape_valid"] = valid
    if not valid:
        failure("response_shape", "Missing effective reviewer configuration sources")
        return report
    config, origins, layers = result["config"], result["origins"], result["layers"]
    valid_layers = all(type(layer) is dict and type(layer.get("config")) is dict and
        type(layer.get("name")) is dict and type(layer["name"].get("type")) is str and
        layer["name"]["type"] in SOURCE_TYPES and
        type(layer.get("version")) is str and 0 < len(layer["version"]) <= 256 and
        (layer.get("disabledReason") is None or type(layer.get("disabledReason")) is str)
        for layer in layers)
    report["source_layers_shape_valid"] = valid_layers
    if not valid_layers:
        failure("source_layers_shape", "Invalid reviewer configuration source layer")
        return report
    indices = [i for i, layer in enumerate(layers) if layer["name"]["type"] == "sessionFlags"]
    report["unique_session_layer"] = len(indices) == 1
    if len(indices) != 1:
        failure("unique_session_layer", "Ambiguous reviewer session configuration layer")
        return report
    idx, winner = indices[0], layers[indices[0]]
    report["session_layer_enabled"] = winner.get("disabledReason") is None
    report["session_layer_name_exact"] = winner["name"] == {"type": "sessionFlags"}
    if not (report["session_layer_enabled"] and report["session_layer_name_exact"]):
        failure("enabled_session_layer", "Reviewer session configuration layer is not enabled")
    tools = observe_projected_tool_controls(result)
    report["projected_tool_controls"] = tools
    if not tools["all_two_controls_verified_false"]:
        failure("projected_tool_controls", "Projected reviewer tool controls are not verified")
    for dotted, expected in requested.items():
        kind, actual = _leaf(winner["config"], dotted)
        entry = {"winning_value_kind": kind, "winning_value_shape": _shape(actual),
                 "winning_value_matches": kind == "leaf" and _equal(actual, expected),
                 "higher_enabled_layers_do_not_shadow": all(
                     layer.get("disabledReason") is not None or
                     _leaf(layer["config"], dotted)[0] == "absent" for layer in layers[:idx]),
                 "origins": {path: _origin_observation(origins.get(path), winner)
                             for path, unused in _leaves(dotted, expected)}}
        entry["all_scalar_origins_verified"] = all(
            item["verified_session_origin"] for item in entry["origins"].values())
        pkind, pvalue = _leaf(config, dotted)
        entry["projected_value_kind"], entry["projected_value_shape"] = pkind, _shape(pvalue)
        entry["projected_value_matches"] = (tools["controls"][dotted]["verified_false_control"]
            if dotted in TOOL_CONTROL_PATHS else pkind == "leaf" and _equal(pvalue, expected))
        entry["structured_projection_requires_separate_admission"] = (
            dotted == "features.multi_agent_v2" and pkind == "leaf" and type(pvalue) is dict)
        entry["verified"] = all(entry[k] for k in ("winning_value_matches",
            "higher_enabled_layers_do_not_shadow", "all_scalar_origins_verified",
            "projected_value_matches"))
        report["control_observations"][dotted] = entry
        report["controls"][dotted] = entry["verified"]
        if not entry["winning_value_matches"]:
            failure("winning_value", "Winning reviewer control differs", dotted)
        elif not entry["higher_enabled_layers_do_not_shadow"]:
            failure("higher_enabled_shadow", "Higher configuration layer shadows reviewer control", dotted)
        elif not entry["all_scalar_origins_verified"]:
            failure("scalar_origin", "Reviewer control origin is not the prescribed session layer", dotted)
        elif entry["structured_projection_requires_separate_admission"]:
            failure("structured_projection_policy", "Structured multi-agent projection requires separate admission", dotted)
        elif not entry["projected_value_matches"]:
            failure("projected_value", "Projected reviewer control differs", dotted)
    for field in INSTRUCTION_FIELDS:
        entry = {"projected_null_or_absent": config.get(field) is None,
                 "enabled_custom_source_absent": all(layer.get("disabledReason") is not None or
                    layer["name"]["type"] == "packagedDefaults" or
                    _leaf(layer["config"], field)[0] == "absent" for layer in layers),
                 "custom_origin_absent": origins.get(field) is None}
        entry["verified_absent"] = all(entry.values())
        report["instruction_observations"][field] = entry
        if not entry["projected_null_or_absent"]:
            failure("instruction_projection", "Custom projected instruction requires separate admission", field)
        elif not entry["enabled_custom_source_absent"]:
            failure("instruction_source", "Custom instruction source requires separate admission", field)
        elif not entry["custom_origin_absent"]:
            failure("instruction_origin", "Custom instruction origin requires separate admission", field)
    report["nondefault_instruction_overrides_absent"] = all(
        row["verified_absent"] for row in report["instruction_observations"].values())
    report["all_requested_controls_verified"] = report["first_failure"] is None
    report["source_sensitive_tables_verified"] = report["all_requested_controls_verified"]
    return report


def validate_effective_config(result, requested):
    """Admit the source-correct observation or retain it on a fixed local stop."""
    observation = observe_effective_config(result, requested)
    if not observation["all_requested_controls_verified"]:
        failure = Stop(observation["first_failure"]["reason"])
        failure.safe_observation = observation
        raise failure
    return observation

