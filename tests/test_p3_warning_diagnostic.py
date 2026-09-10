"""Offline privacy and fail-closed tests; no native process, auth, or model."""
import copy
import hashlib
import io
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("warning_diagnostic", ROOT / "scripts/p3_warning_diagnostic.py")
warning = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(warning)
SOURCE = ROOT / "artifacts/P3_WARNING_SOURCE/20260909_025"
SENTINEL = "PRIVATE_VARIABLE_SENTINEL_DO_NOT_PERSIST"

def classify(message, **kwargs):
    return warning.classify_warning({"threadId": "bound-thread", "message": message},
        expected_thread_id="bound-thread", expected_model="gpt-5.6-sol", **kwargs)

class WarningTests(unittest.TestCase):
    def assert_stopped_private(self, result):
        self.assertEqual(result["action"], "stop")
        self.assertIs(result["warning_admitted"], False)
        self.assertIs(result["producer_identity_established"], False)
        self.assertNotIn(SENTINEL, json.dumps(result))
        self.assertNotIn("bound-thread", json.dumps(result))
        self.assertNotIn("gpt-5.6-sol", json.dumps(result))
        self.assertEqual(set(result), {"schema", "action", "warning_admitted",
            "source_commit", "envelope", "thread_binding", "message_utf8_size_bucket",
            "family", "recognition", "producer_identity_established", "details",
            "text_attribution_to_active_thread"})

    def test_catalog_all_35_families_accounted_for(self):
        catalog = json.loads((SOURCE / "WARNING_FAMILIES.json").read_text())
        self.assertEqual(len(catalog["families"]), 35)
        self.assertEqual(set(warning.family_coverage()), {x["id"] for x in catalog["families"]})
        self.assertEqual(set(warning.UNCLASSIFIABLE_OPEN_FAMILIES),
                         {"hooks.async_output_warning", "skills.host_warning"})

    def test_all_48_canonical_keys_match_source(self):
        catalog = json.loads((SOURCE / "UNDER_DEVELOPMENT_FEATURES.json").read_text())
        self.assertEqual(warning.UNDER_DEVELOPMENT_KEYS, {x["key"] for x in catalog})
        self.assertEqual(len(warning.UNDER_DEVELOPMENT_KEYS), 48)

    def test_catalog_formatter_shapes_all_recognized_without_private_variables(self):
        catalog = json.loads((SOURCE / "WARNING_FAMILIES.json").read_text())
        substitutions = {
            "field_name": "feedback", "config_key": "otel.tracestate",
            "sorted_canonical_keys": "code_mode, transcript_v2",
            "behavior": "Code mode will fail closed",
            "CYBER_VERIFY_URL": "https://chatgpt.com/cyber",
            "CYBER_SAFETY_URL": "https://developers.openai.com/codex/concepts/cyber-safety",
        }
        import re
        for family in catalog["families"]:
            family_id = family["id"]
            if family_id in warning.UNCLASSIFIABLE_OPEN_FAMILIES:
                continue
            template = family["template"]
            if family_id == "hooks.startup_discovery":
                template = "failed to parse hooks config " + SENTINEL + ": " + SENTINEL
            elif family_id == "config.filesystem_special_path_unknown":
                template = "Configured filesystem path `{path}` is not recognized by this version of Codex and will be ignored. Upgrade Codex if this path is required."
            elif family_id == "config.permission_profile_fallback":
                substitutions["field_name"] = "permission_profile"
            message = re.sub(r"\{([^{}]+)\}", lambda m: substitutions.get(m.group(1), SENTINEL), template)
            with self.subTest(family=family_id):
                result = classify(message)
                self.assertEqual(result["family"], family_id)
                self.assert_stopped_private(result)

    def test_underdev_all_keys_full_template_and_sorted_unique(self):
        keys = sorted(warning.UNDER_DEVELOPMENT_KEYS)
        message = warning.UNDERDEV_PREFIX + ", ".join(keys) + warning.UNDERDEV_MIDDLE + "/private/" + SENTINEL + "."
        result = classify(message, expected_config_path="/private/" + SENTINEL)
        self.assertEqual(result["recognition"], "full_template_with_finite_key_enums")
        self.assertEqual(result["details"]["canonical_feature_keys"], keys)
        self.assertTrue(result["details"]["configuration_path_matches_expected"])
        self.assert_stopped_private(result)

    def test_underdev_invalid_keys_or_order_never_exported(self):
        for keys in ("transcript_v2, code_mode", "code_mode, code_mode", SENTINEL,
                     "code_mode, " + SENTINEL, "", "code_mode,transcript_v2"):
            with self.subTest(case=keys != SENTINEL):
                result = classify(warning.UNDERDEV_PREFIX + keys + warning.UNDERDEV_MIDDLE + "/config.")
                self.assertEqual(result["recognition"], "fixed_prefix_candidate")
                self.assertEqual(result["details"], {})
                self.assert_stopped_private(result)

    def test_underdev_truncation_suffix_and_control_never_full_template(self):
        base = warning.UNDERDEV_PREFIX + "code_mode" + warning.UNDERDEV_MIDDLE
        for tail in ("", "/config", "/config.\n", "/config\x00."):
            result = classify(base + tail)
            self.assertNotEqual(result["recognition"], "full_template_with_finite_key_enums")
            self.assertNotIn("canonical_feature_keys", result["details"])
            self.assert_stopped_private(result)

    def test_code_mode_both_behaviors_opaque_reason(self):
        for behavior, label in (("Falling back to direct tools", "fallback_to_direct_tools"),
                                ("Code mode will fail closed", "fail_closed")):
            result = classify(warning.CODE_MODE_PREFIX + SENTINEL + ". " + behavior + warning.CODE_MODE_SUFFIX)
            self.assertEqual(result["recognition"], "full_template_with_finite_behavior_enum")
            self.assertEqual(result["details"], {"behavior": label, "reason": "opaque_source_error_not_retained"})
            self.assert_stopped_private(result)

    def test_code_mode_unsupported_suffix_or_missing_error_stays_candidate(self):
        for message in (warning.CODE_MODE_PREFIX + SENTINEL,
                        warning.CODE_MODE_PREFIX + ". Code mode will fail closed" + warning.CODE_MODE_SUFFIX,
                        warning.CODE_MODE_PREFIX + SENTINEL + ". Other behavior" + warning.CODE_MODE_SUFFIX):
            result = classify(message)
            self.assertEqual(result["recognition"], "fixed_prefix_candidate")
            self.assertEqual(result["details"], {})
            self.assert_stopped_private(result)

    def test_model_comparison_is_boolean_not_identifier(self):
        for slug, equal in (("gpt-5.6-sol", True), (SENTINEL, False)):
            result = classify(f"Model metadata for `{slug}` not found. Defaulting to fallback metadata; this can degrade performance and cause issues.")
            self.assertEqual(result["details"], {"model_matches_requested": equal})
            self.assert_stopped_private(result)

    def test_requirement_known_field_enum_and_unknown_redaction(self):
        for field, expected in (("approval_policy", "approval_policy"), (SENTINEL, "unknown_field_not_retained")):
            result = classify(f"Configured value for `{field}` is overridden by the required value {SENTINEL} from {SENTINEL}.")
            self.assertEqual(result["details"], {"configuration_field": expected})
            self.assert_stopped_private(result)

    def test_missing_null_mismatched_thread_classified_but_not_attributed(self):
        for target in (None, SENTINEL, ""):
            result = warning.classify_warning({"message": warning.CONSTANTS["config.hook_trust_bypass"], "threadId": target}, expected_thread_id="bound-thread")
            self.assertEqual(result["envelope"], "valid_text_thread_not_bound")
            self.assertEqual(result["family"], "config.hook_trust_bypass")
            self.assertIs(result["text_attribution_to_active_thread"], False)
            self.assert_stopped_private(result)
        result = warning.classify_warning({"message": warning.CONSTANTS["config.hook_trust_bypass"]}, expected_thread_id="bound-thread")
        self.assertEqual(result["thread_binding"], "absent")
        self.assertEqual(result["family"], "config.hook_trust_bypass")
        self.assertIs(result["text_attribution_to_active_thread"], False)
        self.assert_stopped_private(result)

    def test_invalid_thread_type_unclassified(self):
        for target in (7, True, {}, []):
            result = warning.classify_warning({"message": warning.CONSTANTS["config.hook_trust_bypass"], "threadId": target}, expected_thread_id="bound-thread")
            self.assertEqual(result["envelope"], "invalid_thread_type")
            self.assertEqual(result["thread_binding"], "invalid")
            self.assertEqual(result["family"], "unknown")
            self.assert_stopped_private(result)

    def test_malformed_envelopes_never_echo_fields_or_values(self):
        for params in (None, [], SENTINEL, {}, {"message": 5},
                       {"message": SENTINEL, SENTINEL: SENTINEL},
                       {"message": SENTINEL, "threadId": "bound-thread", "id": 1}):
            result = warning.classify_warning(params, expected_thread_id="bound-thread")
            self.assertNotEqual(result["envelope"], "valid_bound")
            self.assert_stopped_private(result)

    def test_no_expected_thread_never_attributes_text(self):
        for expected in (None, "", 0, True):
            result = warning.classify_warning({"message": warning.CONSTANTS["config.hook_trust_bypass"], "threadId": "bound-thread"}, expected_thread_id=expected)
            self.assertEqual(result["envelope"], "valid_text_thread_not_bound")
            self.assertEqual(result["thread_binding"], "no_expected_thread")
            self.assertEqual(result["family"], "config.hook_trust_bypass")
            self.assertIs(result["text_attribution_to_active_thread"], False)
            self.assert_stopped_private(result)

    def test_size_bounds_count_utf8_and_invalid_unicode(self):
        for message in ("x" * (warning.MAX_MESSAGE_BYTES + 1), "\U0001f600" * 4097):
            result = classify(message)
            self.assertEqual(result["envelope"], "message_over_limit")
            self.assertEqual(result["message_utf8_size_bucket"], "over_limit")
            self.assert_stopped_private(result)
        result = classify("\ud800")
        self.assertEqual(result["envelope"], "invalid_message_unicode")
        self.assert_stopped_private(result)

    def test_constant_tampering_and_unknown_provider_output_remain_unknown(self):
        for message in (SENTINEL, "\n" + warning.CONSTANTS["config.hook_trust_bypass"],
                        warning.CONSTANTS["context.compaction_accuracy"] + SENTINEL,
                        "arbitrary hook warning: " + SENTINEL,
                        "Model metadata for `" + SENTINEL + "` not found."):
            result = classify(message)
            self.assertEqual(result["family"], "unknown")
            self.assert_stopped_private(result)

    def test_prefix_candidates_do_not_authenticate_source(self):
        for family, prefix in warning.PREFIXES:
            result = classify(prefix + SENTINEL + "\n" + SENTINEL)
            self.assertEqual(result["family"], family)
            self.assertEqual(result["recognition"], "fixed_prefix_candidate")
            self.assert_stopped_private(result)

    def test_both_filesystem_special_path_source_variants(self):
        for nested in ("", f" with nested entry `{SENTINEL}`"):
            message = f"Configured filesystem path `{SENTINEL}`{nested} is not recognized by this version of Codex and will be ignored. Upgrade Codex if this path is required."
            result = classify(message)
            self.assertEqual(result["family"], "config.filesystem_special_path_unknown")
            self.assert_stopped_private(result)

    def test_inputs_unchanged(self):
        params = {"threadId": "bound-thread", "message": SENTINEL}
        before = copy.deepcopy(params)
        warning.classify_warning(params, expected_thread_id="bound-thread")
        self.assertEqual(params, before)

if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(WarningTests)
    trace = io.StringIO()
    result = unittest.TextTestRunner(stream=trace, verbosity=2).run(suite)
    print(trace.getvalue(), end="")
    report = {"kind": "P3_WARNING_DIAGNOSTIC_OFFLINE_VALIDATION_026_v1",
        "scope": "Engineering validation only; no native process, credentials or model access",
        "tests_run": result.testsRun, "errors": len(result.errors),
        "failures": len(result.failures), "passed": result.wasSuccessful(),
        "source_commit": warning.SOURCE_COMMIT, "family_coverage": warning.family_coverage(),
        "source_url": "https://github.com/openai/codex/tree/" + warning.SOURCE_COMMIT,
        "source_access_date": "2026-09-09",
        "generic_warnings_ever_admitted": False,
        "actual_024_warning_identified": False}
    report["source_pins"] = {
        path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        for path in (
            "scripts/p3_warning_diagnostic.py",
            "tests/test_p3_warning_diagnostic.py",
            "artifacts/P3_WARNING_SOURCE/20260909_025/WARNING_FAMILIES.json",
            "artifacts/P3_WARNING_SOURCE/20260909_025/UNDER_DEVELOPMENT_FEATURES.json",
        )
    }
    output = ROOT / "artifacts/P3_WARNING_CAPTURE_VALIDATION/20260909_026_CLASSIFIER"
    output.mkdir(parents=True, exist_ok=True)
    (output / "REPORT.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    (output / "TEST_TRACE.txt").write_text(trace.getvalue())
    (output / "SHA256SUMS").write_text("".join(
        hashlib.sha256((output / name).read_bytes()).hexdigest() + "  " + name + "\n"
        for name in ("REPORT.json", "TEST_TRACE.txt")
    ))
    raise SystemExit(0 if result.wasSuccessful() else 1)
