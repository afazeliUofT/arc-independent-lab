"""Pure synthetic ConfigRead tests. No Codex, subprocess or network use."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "gate0_config_controls", ROOT / "scripts/gate0_config_controls.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def fixture():
    """Representative ConfigReadResponse using exact embedded wire shapes."""
    return {
        "config": {"tools": {"web_search": None}},
        "origins": {path: {"name": {"type": "sessionFlags"}, "version": "v-session"}
                    for path in m.TOOL_CONTROL_PATHS},
        "layers": [
            {"name": {"type": "sessionFlags"}, "version": "v-session", "config": {
                "tools": {"update_plan": {"enabled": False},
                          "experimental_request_user_input": {"enabled": False}}}},
            {"name": {"type": "user", "file": "/private/config.toml", "profile": None},
             "version": "v-private", "config": {
                 "private_setting": "SECRET_DO_NOT_PRINT",
                 "tools": {"update_plan": {"enabled": True}}}},
        ],
    }


def cases():
    """Return reproducible inputs and expectations for the archived harness."""
    out = [("typed_false_in_winning_session_layer", fixture(), True)]

    def add(name, mutate, expected=False):
        item = fixture()
        mutate(item)
        out.append((name, item, expected))

    add("missing_api_tools_is_projection", lambda x: x["config"].pop("tools"), True)
    add("null_api_tools_is_projection", lambda x: x["config"].update(tools=None), True)
    add("origin_missing", lambda x: x["origins"].pop(m.TOOL_CONTROL_PATHS[0]))
    add("origin_version_mismatch", lambda x: x["origins"][m.TOOL_CONTROL_PATHS[0]].update(version="SECRET_DO_NOT_PRINT"))
    add("origin_version_not_string", lambda x: x["origins"][m.TOOL_CONTROL_PATHS[0]].update(version=1))
    add("origin_source_wrong", lambda x: x["origins"][m.TOOL_CONTROL_PATHS[0]].update(name={"type": "user", "file": "/private/config.toml"}))
    add("origin_source_unknown", lambda x: x["origins"][m.TOOL_CONTROL_PATHS[0]].update(name={"type": "SECRET_DO_NOT_PRINT"}))
    add("origin_unexpected_fields", lambda x: x["origins"][m.TOOL_CONTROL_PATHS[0]].update(secret="SECRET_DO_NOT_PRINT"))
    add("session_name_unexpected_fields", lambda x: x["layers"][0]["name"].update(secret="SECRET_DO_NOT_PRINT"))
    add("winning_layer_disabled", lambda x: x["layers"][0].update(disabledReason="SECRET_DO_NOT_PRINT"))
    add("duplicate_session_layer", lambda x: x["layers"].append(copy.deepcopy(x["layers"][0])))
    add("true_is_rejected", lambda x: x["layers"][0]["config"]["tools"]["update_plan"].update(enabled=True))
    add("zero_is_not_false_boolean", lambda x: x["layers"][0]["config"]["tools"]["update_plan"].update(enabled=0))
    add("false_string_is_not_boolean", lambda x: x["layers"][0]["config"]["tools"]["update_plan"].update(enabled="false"))
    add("null_is_not_boolean", lambda x: x["layers"][0]["config"]["tools"]["update_plan"].update(enabled=None))
    add("missing_winner_leaf", lambda x: x["layers"][0]["config"]["tools"]["update_plan"].pop("enabled"))
    add("projected_true_contradiction", lambda x: x["config"]["tools"].update(update_plan={"enabled": True}))
    add("projected_nonbool_contradiction", lambda x: x["config"]["tools"].update(update_plan={"enabled": 0}))
    add("projected_false_consistent", lambda x: x["config"]["tools"].update(update_plan={"enabled": False}), True)

    def higher(x, config, disabled=False):
        layer = {"name": {"type": "legacyManagedConfigTomlFromFile", "file": "/managed.toml"},
                 "version": "v-managed", "config": config}
        if disabled:
            layer["disabledReason"] = "disabled synthetic layer"
        x["layers"].insert(0, layer)

    add("higher_enabled_true_shadows", lambda x: higher(x, {"tools": {"update_plan": {"enabled": True}}}))
    add("higher_enabled_false_origin_conflict", lambda x: higher(x, {"tools": {"update_plan": {"enabled": False}}}))
    add("higher_enabled_ancestor_replaces", lambda x: higher(x, {"tools": "SECRET_DO_NOT_PRINT"}))
    add("higher_disabled_layer_ignored", lambda x: higher(x, {"tools": {"update_plan": {"enabled": True}}}, True), True)
    add("higher_unrelated_leaf_ignored", lambda x: higher(x, {"tools": {"other_tool": {"enabled": True}}}), True)
    add("malformed_layer_config", lambda x: x["layers"][1].update(config=[]))
    add("unknown_layer_source", lambda x: x["layers"][1].update(name={"type": "SECRET_DO_NOT_PRINT"}))
    add("malformed_disabled_flag", lambda x: x["layers"][1].update(disabledReason=False))
    add("too_many_layers", lambda x: x.update(layers=x["layers"] * 129))
    add("layers_absent", lambda x: x.pop("layers"))
    out.extend(("invalid_envelope_" + str(i), value, False)
               for i, value in enumerate([None, [], "SECRET_DO_NOT_PRINT", True]))
    return out


class ConfigControlCases(unittest.TestCase):
    def test_all_cases_and_no_input_mutation_or_raw_leak(self):
        for name, response, expected in cases():
            with self.subTest(name=name):
                before = copy.deepcopy(response)
                result = m.observe_projected_tool_controls(response)
                self.assertEqual(result["all_two_controls_verified_false"], expected)
                self.assertFalse(result["runtime_tool_exposure_verified"])
                self.assertEqual(response, before)
                output = json.dumps(result)
                for secret in ("SECRET_DO_NOT_PRINT", "/private/config.toml", "v-session", "v-private", "/managed.toml"):
                    self.assertNotIn(secret, output)
                self.assertEqual(set(result["controls"]), set(m.TOOL_CONTROL_PATHS))
                for control in result["controls"].values():
                    for key, value in control.items():
                        if key == "origin_source_type":
                            self.assertTrue(value is None or value in m.SOURCE_TYPES)
                        else:
                            self.assertIs(type(value), bool)

    def test_fixture_wire_shape_matches_pinned_schema(self):
        path = ROOT / "artifacts/GATE0_CODEX_INTERFACE/20260907_001/schemas/experimental.json"
        schemas = json.loads(path.read_text())
        schema = json.loads(schemas["v2/ConfigReadResponse.json"])
        defs = schema["definitions"]
        self.assertEqual(set(defs["ToolsV2"]["properties"]), {"web_search"})
        self.assertNotIn("additionalProperties", defs["ToolsV2"])
        self.assertEqual(defs["ConfigLayer"]["properties"]["config"], True)
        self.assertEqual(set(fixture()), {"config", "origins", "layers"})
        self.assertTrue(set(schema["required"]) <= set(fixture()))


if __name__ == "__main__":
    unittest.main()
