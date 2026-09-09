"""Source-derived origin contract regressions; no native client or model use."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import p3_reviewer_admission_021 as a
from gate0_client_preflight import overrides
from p3_reviewer_profile import reviewer_overrides


def profile():
    return reviewer_overrides(overrides(Path("/home/example/ARC_Independent_Lab/delivery/reviewer/runtime")),
        (ROOT / "artifacts/GATE0_CODEX_INTERFACE/20260907_001/config-schema.json").read_bytes())


def fixture():
    p, config = profile(), {}
    for dotted, value in p.items():
        node, bits = config, dotted.split(".")
        for bit in bits[:-1]:
            node = node.setdefault(bit, {})
        node[bits[-1]] = copy.deepcopy(value)
    meta = {"name": {"type": "sessionFlags"}, "version": "sha256:" + "a" * 64}
    # Literal source-derived exceptions. Never derive expected origins by calling
    # the validator or any origin helper from the implementation under test.
    ordinary = set(p) - {"features.multi_agent_v2", "features.code_mode"}
    native_paths = ordinary | {"features.multi_agent_v2.enabled", "features.code_mode.enabled",
                              "features.code_mode.direct_only_tool_namespaces.0"}
    origins = {path: copy.deepcopy(meta) for path in native_paths}
    projected = copy.deepcopy(config)
    projected.pop("tools")
    return {"config": projected, "origins": origins, "layers": [dict(meta, config=config)]}


class OriginContractTests(unittest.TestCase):
    def denied(self, result):
        with self.assertRaises(a.Stop) as caught:
            a.validate_effective_config(result, profile())
        observation = caught.exception.safe_observation
        self.assertFalse(observation["all_requested_controls_verified"])
        return observation

    def test_literal_native_origins_admitted(self):
        result = a.validate_effective_config(fixture(), profile())
        self.assertTrue(result["all_requested_controls_verified"])
        self.assertEqual(set(result["control_observations"]), set(profile()))
        self.assertTrue(result["projected_tool_controls"]["all_two_controls_verified_false"])
        self.assertFalse(result["runtime_tool_registry_verified"])

    def test_old_boolean_origin_does_not_substitute_for_native_enabled_origin(self):
        r = fixture(); origin = r["origins"].pop("features.multi_agent_v2.enabled")
        r["origins"]["features.multi_agent_v2"] = origin
        self.assertEqual(self.denied(r)["first_failure"]["control"], "features.multi_agent_v2")

    def test_whole_array_origin_does_not_substitute_for_indexed_origin(self):
        r = fixture(); origin = r["origins"].pop("features.code_mode.direct_only_tool_namespaces.0")
        r["origins"]["features.code_mode.direct_only_tool_namespaces"] = origin
        self.assertEqual(self.denied(r)["first_failure"]["control"], "features.code_mode")

    def test_indexed_origin_exact_version_required(self):
        r = fixture(); r["origins"]["features.code_mode.direct_only_tool_namespaces.0"]["version"] = "wrong"
        o = self.denied(r)["control_observations"]["features.code_mode"]["origins"]
        self.assertFalse(o["features.code_mode.direct_only_tool_namespaces.0"]["version_matches_session_layer"])

    def test_indexed_origin_source_required(self):
        r = fixture()
        r["origins"]["features.code_mode.direct_only_tool_namespaces.0"]["name"] = {
            "type": "user", "file": "SECRET_CONFIG_FILE"}
        o = self.denied(r)
        self.assertNotIn("SECRET_CONFIG_FILE", json.dumps(o))

    def test_empty_collections_have_no_native_origin(self):
        self.assertEqual(list(a._leaves("control", [])), [])
        self.assertEqual(list(a._leaves("control", {})), [])

    def test_nested_arrays_and_tables_use_scalar_indices(self):
        self.assertEqual(list(a._leaves("control", [{"x": [False, "v"]}, {}])),
                         [("control.0.x.0", False), ("control.0.x.1", "v")])

    def test_only_two_source_defined_structured_features_are_transformed(self):
        self.assertEqual(list(a._leaves("features.multi_agent_v2", False)),
                         [("features.multi_agent_v2.enabled", False)])
        self.assertEqual(list(a._leaves("features.network_proxy", False)),
                         [("features.network_proxy", False), ("features.network_proxy.enabled", False)])
        for path in ("features.code_mode_host", "features.code_mode", "features.token_budget"):
            self.assertEqual(list(a._leaves(path, False)), [(path, False)])

    def test_source_profile_feature_transformation_is_narrow(self):
        self.assertEqual(list(a._leaves("profiles.review.features.multi_agent_v2", False)),
                         [("profiles.review.features.multi_agent_v2.enabled", False)])
        self.assertEqual(list(a._leaves("other.features.multi_agent_v2", False)),
                         [("other.features.multi_agent_v2", False)])

    def test_same_value_higher_enabled_layer_still_stops(self):
        r = fixture(); r["layers"].insert(0, {"name": {"type": "legacyManagedConfigTomlFromMdm"},
            "version": "higher", "config": {"features": {"multi_agent_v2": False}}})
        self.assertEqual(self.denied(r)["first_failure"]["check"], "higher_enabled_shadow")

    def test_replacement_ancestor_still_stops(self):
        r = fixture(); r["layers"].insert(0, {"name": {"type": "legacyManagedConfigTomlFromMdm"},
            "version": "higher", "config": {"features": False}})
        self.assertEqual(self.denied(r)["first_failure"]["check"], "higher_enabled_shadow")

    def test_disabled_higher_shadow_is_not_effective(self):
        r = fixture(); r["layers"].insert(0, {"name": {"type": "legacyManagedConfigTomlFromMdm"},
            "version": "higher", "disabledReason": "private reason", "config": {"features": False}})
        self.assertTrue(a.validate_effective_config(r, profile())["all_requested_controls_verified"])

    def test_structured_multi_agent_projection_deliberate_stop(self):
        r = fixture(); r["config"]["features"]["multi_agent_v2"] = {"enabled": False}
        o = self.denied(r)
        self.assertEqual(o["first_failure"]["check"], "structured_projection_policy")
        self.assertTrue(o["control_observations"]["features.multi_agent_v2"]["all_scalar_origins_verified"])

    def test_code_mode_host_nested_fallback_not_admitted(self):
        for source in ("layer", "projection"):
            r = fixture(); cfg = r["layers"][0]["config"] if source == "layer" else r["config"]
            cfg["features"]["code_mode_host"] = {"enabled": False, "disable_in_process_fallback": True}
            self.denied(r)

    def test_unexpected_code_mode_table_member_stops(self):
        for source in ("layer", "projection"):
            r = fixture(); cfg = r["layers"][0]["config"] if source == "layer" else r["config"]
            cfg["features"]["code_mode"]["excluded_tool_namespaces"] = ["private"]
            self.denied(r)

    def test_missing_managed_requirement_origin_not_invented(self):
        r = fixture(); del r["origins"]["approval_policy"]
        self.assertEqual(self.denied(r)["first_failure"]["check"], "scalar_origin")

    def test_all_known_controls_observed_before_failure(self):
        r = fixture(); del r["origins"]["history.persistence"]
        r["config"]["features"]["code_mode_host"] = True
        o = self.denied(r)
        self.assertEqual(set(o["control_observations"]), set(profile()))
        self.assertFalse(o["control_observations"]["features.code_mode_host"]["projected_value_matches"])

    def test_malformed_origin_never_leaks_raw_values(self):
        for value in (None, "SECRET", [], {"name": {"type": ["SECRET"]}, "version": "SECRET"},
                      {"name": {"type": "sessionFlags"}, "version": "SECRET", "extra": "SECRET"}):
            r = fixture(); r["origins"]["features.multi_agent_v2.enabled"] = value
            self.assertNotIn("SECRET", json.dumps(self.denied(r)))

    def test_malformed_layer_and_top_level_fail_safely(self):
        for result in (None, [], {}, {"config": {}, "origins": {}, "layers": []}):
            self.assertFalse(a.observe_effective_config(result, profile())["all_requested_controls_verified"])
        r = fixture(); r["layers"][0]["name"]["type"] = ["SECRET"]
        self.assertNotIn("SECRET", json.dumps(self.denied(r)))

    def test_custom_instruction_checks_and_diagnostics_preserved(self):
        for source in ("layer", "projection", "origin"):
            r = fixture()
            if source == "layer": r["layers"][0]["config"]["model_instructions_file"] = "SECRET"
            elif source == "projection": r["config"]["developer_instructions"] = "SECRET"
            else: r["origins"]["compact_prompt"] = {"private": "SECRET"}
            self.assertNotIn("SECRET", json.dumps(self.denied(r)))

    def test_pinned_source_semantics_identified(self):
        evidence = ROOT / "artifacts/P3_CONFIG_ORIGIN_SOURCE/20260909_001"
        pins = {"codex-rs/config/src/fingerprint.rs": "efc9fb8365a1bfaf4d27933a495624f2763c429789bb1a6399c68ae271e305ca",
                "codex-rs/config/src/key_aliases.rs": "a99676453589c93c57288bc7c17c3a171f9ba13c2bfad5dbf1b067489df68a6c"}
        for path, pin in pins.items():
            self.assertEqual(hashlib.sha256((evidence / path).read_bytes()).hexdigest(), pin)


if __name__ == "__main__":
    unittest.main(verbosity=2)
