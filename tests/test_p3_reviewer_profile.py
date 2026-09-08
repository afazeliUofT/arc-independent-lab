#!/usr/bin/env python3
"""Offline profile/catalog tests; no native client, network, auth or model use."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


profile = load("p3_reviewer_profile")
preflight = load("gate0_client_preflight")
CANARY = "SYNTHETIC_PRIVATE_TEXT_DO_NOT_RETAIN"


def row(model="gpt-example", identifier="example"):
    return {"model": model, "id": identifier, "isDefault": False, "hidden": False,
            "description": CANARY, "displayName": CANARY,
            "defaultReasoningEffort": "high",
            "supportedReasoningEfforts": [{"reasoningEffort": "high", "description": CANARY}]}


class ProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = (ROOT / "artifacts/GATE0_CODEX_INTERFACE/20260907_001/config-schema.json").read_bytes()

    def test_overlay_preserves_base_and_adds_only_exact_controls(self):
        base = preflight.overrides(Path("/synthetic/lab/review"))
        before = copy.deepcopy(base)
        result = profile.reviewer_overrides(base, self.schema)
        self.assertEqual(base, before)
        additions = {"features." + name for name in profile.EXTRA_FALSE_FEATURES}
        additions.add("orchestrator.mcp.enabled")
        self.assertEqual(set(result) - set(base), additions)
        for key in set(base) - {"features.code_mode"}:
            self.assertEqual(result[key], base[key], key)
        for key in additions:
            self.assertIs(result[key], False)
        self.assertEqual(result["features.code_mode"], {
            "enabled": False, "direct_only_tool_namespaces": ["functions"]})
        self.assertFalse(any(key.startswith(("model", "auth", "chatgpt", "requirements"))
                             for key in result))

    def test_changed_schema_or_nested_conflict_refused(self):
        base = {"features.code_mode": False}
        with self.assertRaises(profile.Stop):
            profile.reviewer_overrides(base, self.schema + b" ")
        for field in ("features.code_mode.enabled", "features.code_mode_host.disable_in_process_fallback"):
            with self.subTest(field=field), self.assertRaises(profile.Stop):
                profile.reviewer_overrides({**base, field: False}, self.schema)

    def test_enabled_or_missing_base_control_refused(self):
        for value in (True, None, 0, {"enabled": False}):
            with self.subTest(value=value), self.assertRaises(profile.Stop):
                profile.reviewer_overrides({"features.code_mode": value}, self.schema)

    def test_every_final_cli_override_roundtrips_as_toml(self):
        result = profile.reviewer_overrides(preflight.overrides(Path("/synthetic/lab/review")), self.schema)
        arguments = profile.cli_override_arguments(result)
        self.assertEqual(arguments[::2], ["-c"] * len(result))
        for (key, expected), assignment in zip(result.items(), arguments[1::2], strict=True):
            actual = tomllib.loads(assignment)
            for component in key.split("."):
                actual = actual[component]
            self.assertEqual(actual, expected, key)
        code_mode = arguments[1::2][list(result).index("features.code_mode")]
        self.assertEqual(code_mode,
                         'features.code_mode={enabled = false, direct_only_tool_namespaces = ["functions"]}')
        with self.assertRaises(tomllib.TOMLDecodeError):
            tomllib.loads("features.code_mode=" + json.dumps(result["features.code_mode"]))

    def test_cli_strings_preserve_escaping_unicode_and_shell_metacharacters(self):
        values = ['quotes " and \\ slash', 'line\nnext\ttab\x7f', "model \U0001f600",
                  "$(must_not_execute) `same` ${HOME}"]
        for value in values:
            arguments = profile.cli_override_arguments({"log_dir": value})
            self.assertEqual(arguments[0], "-c")
            self.assertEqual(tomllib.loads(arguments[1])["log_dir"], value)

    def test_invalid_cli_keys_values_and_surrogates_refused(self):
        for value in ({"x.y": None}, {"x\nsecret": False}, {"x": "\ud800"},
                      {"x": 2 ** 64}, {"x": float("nan")}, {"x": {"bad.key": False}}):
            with self.subTest(kind=list(value)), self.assertRaises(profile.Stop):
                profile.cli_override_arguments(value)


class CatalogTests(unittest.TestCase):
    def filtered(self, rows, cursor=None):
        return profile.safe_model_catalog({"data": rows, "nextCursor": cursor})

    def assert_private_failure(self, value):
        with self.assertRaises(profile.Stop) as raised:
            profile.safe_model_catalog(value)
        self.assertNotIn(CANARY, str(raised.exception))

    def test_every_model_retained_without_silent_selection(self):
        entries = [row(), row("gpt-6-astra", "astra"), row("gpt-other", "other")]
        entries[-1]["hidden"] = True
        entries[0]["isDefault"] = True
        result = self.filtered(entries)
        self.assertEqual([r["model"] for r in result["entries"]], [r["model"] for r in entries])
        self.assertTrue(result["entries"][0]["is_default"])
        self.assertTrue(result["entries"][-1]["hidden"])
        self.assertTrue(result["exact_requested_model_present_on_page"])
        self.assertFalse(result["exact_requested_id_present_on_page"])
        for key in ("model_selection_performed", "model_entitlement_verified",
                    "model_tool_registry_verified", "scientific_reviewer_boundary_verified"):
            self.assertIs(result[key], False)
        self.assertNotIn(CANARY, json.dumps(result))

    def test_optional_nulls_and_unselected_text_are_not_retained(self):
        entry = row()
        for name in ("multiAgentVersion", "upgrade", "upgradeInfo", "availabilityNux",
                     "defaultServiceTier", "modelSpecialty"):
            entry[name] = None
        entry["serviceTiers"] = [{"id": CANARY, "name": CANARY, "description": CANARY}]
        result = self.filtered([entry])
        self.assertNotIn(CANARY, json.dumps(result))
        self.assertNotIn("multiAgentVersion", result["entries"][0])

    def test_unknown_efforts_suppressed_not_mapped_to_fallback(self):
        entry = row()
        entry["defaultReasoningEffort"] = CANARY
        entry["supportedReasoningEfforts"] += [
            {"reasoningEffort": CANARY, "description": CANARY},
            {"reasoningEffort": "ultra", "description": CANARY}]
        result = self.filtered([entry])["entries"][0]
        self.assertEqual(result["supported_efforts"], ["high", "ultra"])
        self.assertEqual(result["unrecognized_effort_count"], 1)
        self.assertIsNone(result["default_effort"])
        self.assertFalse(result["default_effort_recognized"])
        self.assertFalse(result["default_effort_in_supported_list"])
        self.assertNotIn(CANARY, json.dumps(result))

    def test_hostile_identifiers_refused_without_echo(self):
        for value in ("", " " + CANARY, CANARY + "\n", "../" + CANARY,
                      "https://" + CANARY, "name@" + CANARY, "é", "x" * 97, None, True):
            for field in ("model", "id"):
                with self.subTest(field=field, kind=type(value).__name__):
                    entry = row()
                    entry[field] = value
                    self.assert_private_failure({"data": [entry]})

    def test_open_schema_unknown_fields_discarded_without_echo(self):
        entry = row()
        entry[CANARY] = {CANARY: CANARY}
        entry["supportedReasoningEfforts"][0][CANARY] = CANARY
        result = profile.safe_model_catalog({"data": [entry], CANARY: CANARY})
        self.assertNotIn(CANARY, json.dumps(result))
        for name in ("response", "entry", "effort"):
            self.assertEqual(result["discarded_unknown_" + name + "_field_count"], 1)

    def test_required_null_or_wrong_shape_metadata_refused(self):
        for field in ("isDefault", "hidden", "supportedReasoningEfforts", "defaultReasoningEffort"):
            for value in (None, 0):
                with self.subTest(field=field, value=value):
                    self.assert_private_failure({"data": [{**row(), field: value}]})
        for value in (None, True, "", "x" * 129):
            entry = row()
            entry["supportedReasoningEfforts"][0]["reasoningEffort"] = value
            self.assert_private_failure({"data": [entry]})

    def test_duplicate_identifiers_and_resource_bounds_refused(self):
        self.assert_private_failure({"data": [row(), row("gpt-other")]})
        self.assert_private_failure({"data": [row(identifier=str(i)) for i in range(101)]})
        entry = row()
        entry["supportedReasoningEfforts"] *= 33
        self.assert_private_failure({"data": [entry]})
        self.assert_private_failure({"data": [], "nextCursor": CANARY * 100})

    def test_cursor_is_not_retained_and_partial_page_is_not_complete(self):
        result = self.filtered([row()], CANARY)
        self.assertTrue(result["additional_page_available"])
        self.assertFalse(result["page_complete_for_returned_catalog"])
        self.assertNotIn(CANARY, json.dumps(result))
        self.assertTrue(self.filtered([])["page_complete_for_returned_catalog"])

    def test_hidden_inclusion_is_caller_observation_not_inferred_from_page(self):
        self.assertIsNone(self.filtered([])["include_hidden_requested"])
        for requested in (False, True):
            result = profile.safe_model_catalog({"data": []}, include_hidden_requested=requested)
            self.assertIs(result["include_hidden_requested"], requested)
        with self.assertRaises(profile.Stop):
            profile.safe_model_catalog({"data": []}, include_hidden_requested=1)

    def test_selected_field_contract_matches_exact_embedded_schema(self):
        raw = (ROOT / "artifacts/GATE0_CODEX_INTERFACE/20260907_001/schemas/experimental.json").read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         "dd4014851ef7c60ecacfa5fa4d1a9f02d7dcc2aada93c83091a717b27b753d63")
        embedded = json.loads(json.loads(raw)["v2/ModelListResponse.json"])
        self.assertEqual(profile.MODEL_FIELDS, set(embedded["definitions"]["Model"]["properties"]))
        self.assertEqual(embedded["definitions"]["ReasoningEffort"]["type"], "string")
        self.assertNotIn("enum", embedded["definitions"]["ReasoningEffort"])


if __name__ == "__main__":
    unittest.main()
