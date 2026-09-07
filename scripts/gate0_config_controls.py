"""Filter two controls lost by Codex 0.151.0's ConfigRead API projection.

Pure observation only: no files, subprocesses, client requests or changes.
Input must be a bounded, strictly parsed JSON ConfigReadResponse. Output never
contains configuration values, version strings, paths or arbitrary diagnostics.
The merged API ``config`` is not used as a substitute for unprojected layers.
"""
from __future__ import annotations


TOOL_CONTROL_PATHS = (
    "tools.update_plan.enabled",
    "tools.experimental_request_user_input.enabled",
)
SOURCE_TYPES = frozenset({
    "packagedDefaults", "mdm", "system", "enterpriseManaged", "user", "project",
    "sessionFlags", "legacyManagedConfigTomlFromFile", "legacyManagedConfigTomlFromMdm",
})
MAX_LAYERS = 256
MAX_VERSION_CHARS = 256


def _object(value):
    return type(value) is dict


def _version(value):
    return type(value) is str and 0 < len(value) <= MAX_VERSION_CHARS


def _source_type(name):
    if not _object(name):
        return None
    value = name.get("type")
    return value if type(value) is str and value in SOURCE_TYPES else None


def _session_name(name):
    return _object(name) and set(name) == {"type"} and name["type"] == "sessionFlags"


def _leaf(config, components):
    """Return fixed status and in-memory value; parent replacement is a shadow."""
    value = config
    for component in components:
        if not _object(value):
            return "shadow", None
        if component not in value:
            return "absent", None
        value = value[component]
    return "leaf", value


def observe_projected_tool_controls(config_read_result):
    """Verify explicit false controls through winning, enabled session layers.

    ``layers`` is ordered highest precedence first and includes disabled layers.
    Origins describe enabled layers only. A valid result needs one sessionFlags
    layer, the exact corresponding origin version, false booleans, and no enabled
    higher layer containing a replacement ancestor or the same leaf. A projected
    true value, if a client unexpectedly returns one, contradicts the observation.
    This establishes these configuration controls, not runtime tool exposure.
    """
    valid_result = _object(config_read_result)
    origins = config_read_result.get("origins") if valid_result else None
    layers = config_read_result.get("layers") if valid_result else None
    projected = config_read_result.get("config") if valid_result else None
    shape_valid = (
        _object(origins) and _object(projected)
        and type(layers) is list and 0 < len(layers) <= MAX_LAYERS
    )
    if shape_valid:
        shape_valid = all(
            _object(layer) and _object(layer.get("config"))
            and _source_type(layer.get("name")) is not None
            and _version(layer.get("version"))
            and (layer.get("disabledReason") is None
                 or type(layer.get("disabledReason")) is str)
            for layer in layers
        )

    results = {}
    for dotted in TOOL_CONTROL_PATHS:
        components = dotted.split(".")
        entry = {
            "response_shape_valid": bool(shape_valid),
            "origin_present": False,
            "origin_source_type": None,
            "origin_is_session_flags": False,
            "origin_version_valid": False,
            "unique_session_layer": False,
            "origin_version_matches_layer": False,
            "winning_layer_enabled": False,
            "winning_value_is_false_boolean": False,
            "higher_enabled_layers_do_not_shadow": False,
            "projected_value_does_not_contradict": False,
            "verified_false_control": False,
        }
        results[dotted] = entry
        if not shape_valid:
            continue
        origin = origins.get(dotted)
        entry["origin_present"] = _object(origin)
        if not _object(origin):
            continue
        entry["origin_source_type"] = _source_type(origin.get("name"))
        entry["origin_is_session_flags"] = _session_name(origin.get("name"))
        entry["origin_version_valid"] = _version(origin.get("version"))
        if not (set(origin) == {"name", "version"}
                and entry["origin_is_session_flags"] and entry["origin_version_valid"]):
            continue
        candidates = [index for index, layer in enumerate(layers)
                      if _source_type(layer["name"]) == "sessionFlags"]
        entry["unique_session_layer"] = len(candidates) == 1
        if len(candidates) != 1:
            continue
        index = candidates[0]
        winner = layers[index]
        entry["origin_version_matches_layer"] = (
            _session_name(winner["name"]) and winner["version"] == origin["version"]
        )
        entry["winning_layer_enabled"] = winner.get("disabledReason") is None
        kind, value = _leaf(winner["config"], components)
        entry["winning_value_is_false_boolean"] = kind == "leaf" and value is False
        entry["higher_enabled_layers_do_not_shadow"] = all(
            layer.get("disabledReason") is not None
            or _leaf(layer["config"], components)[0] == "absent"
            for layer in layers[:index]
        )
        kind, value = _leaf(projected, components)
        # A missing tools object or nested member is the known API projection.
        # A null tools member is also the API's optional ToolsV2 representation.
        projected_absent = kind == "absent" or (
            kind == "shadow" and projected.get("tools") is None
        )
        entry["projected_value_does_not_contradict"] = (
            projected_absent or (kind == "leaf" and value is False)
        )
        entry["verified_false_control"] = all(entry[key] for key in (
            "response_shape_valid", "origin_present", "origin_is_session_flags",
            "origin_version_valid", "unique_session_layer", "origin_version_matches_layer",
            "winning_layer_enabled", "winning_value_is_false_boolean",
            "higher_enabled_layers_do_not_shadow", "projected_value_does_not_contradict",
        ))
    return {
        "observation": "CODEX_0151_PROJECTED_TOOL_CONTROLS_v1",
        "controls": results,
        "all_two_controls_verified_false": all(
            item["verified_false_control"] for item in results.values()
        ),
        "runtime_tool_exposure_verified": False,
    }
