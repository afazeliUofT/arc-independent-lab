"""Source-bound warning decisions; no native executable or account access."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("warning_policy_unit",
    ROOT / "scripts/p3_config_warning.py")
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)


class WarningTests(unittest.TestCase):
    def params(self):
        return {"summary": w.MISSING_BWRAP_SUMMARY, "details": None}

    def classify(self, params, **kw):
        return w.classify(params, **{"initialized": True,
            "thread_requested": False, "previously_accepted": 0, **kw})

    def test_exact_literal_is_the_archived_upstream_constant(self):
        source = (ROOT / "artifacts/P3_CONFIG_WARNING_SOURCE/20260909_001/"
            "codex-rs/sandboxing/src/bwrap.rs").read_text()
        body = source.split("const MISSING_BWRAP_WARNING: &str = concat!(", 1)[1].split(");", 1)[0]
        literal = "".join(json.loads(value) for value in re.findall(r'"[^"\n]*"', body))
        self.assertEqual(w.MISSING_BWRAP_SUMMARY, literal)

    def test_exact_source_shape_is_the_single_accepted_advisory(self):
        receipt = self.classify(self.params())
        self.assertTrue(receipt["admitted"])
        self.assertEqual(receipt["category"], "missing_system_bwrap_bundled_fallback_advisory")
        self.assertFalse(receipt["raw_content_saved_or_hashed"])

    def test_whitespace_prefix_suffix_case_and_other_warning_are_unknown(self):
        for summary in (w.MISSING_BWRAP_SUMMARY + " ", " " + w.MISSING_BWRAP_SUMMARY,
                w.MISSING_BWRAP_SUMMARY.lower(), w.MISSING_BWRAP_SUMMARY + " SECRET_NEVER_SAVE",
                "Configuration failed to parse SECRET_NEVER_SAVE",
                "Managed requirements unavailable; falling back SECRET_NEVER_SAVE"):
            with self.subTest(summary_kind="synthetic"):
                receipt = self.classify({"summary": summary, "details": None})
                self.assertFalse(receipt["admitted"])
                self.assertEqual(receipt["category"], "unrecognized_config_warning")
                self.assertNotIn(summary, json.dumps(receipt))
                self.assertNotIn(hashlib.sha256(summary.encode()).hexdigest(), json.dumps(receipt))

    def test_no_native_details_paths_ranges_or_extra_fields_allowed(self):
        for params in (None, [], {}, {"summary": w.MISSING_BWRAP_SUMMARY},
                {**self.params(), "details": "SECRET_NEVER_SAVE"},
                {**self.params(), "details": ""}, {**self.params(), "path": None},
                {**self.params(), "path": "/SECRET_NEVER_SAVE"},
                {**self.params(), "range": None}, {**self.params(), "extra": "SECRET_NEVER_SAVE"},
                {"summary": 123, "details": None}):
            with self.subTest(params_kind=type(params).__name__):
                receipt = self.classify(params)
                self.assertFalse(receipt["admitted"])
                self.assertEqual(receipt["decision"], "unsupported_warning_shape")
                self.assertNotIn("SECRET_NEVER_SAVE", json.dumps(receipt))

    def test_known_consequential_families_keep_category_despite_details_or_paths(self):
        for summary, category in (
                (w.POLICY_PARSE_SUMMARY, "execution_policy_parse_failure"),
                (w.SQLITE_RECOVERY_SUMMARY, "sqlite_database_recovery"),
                (w.DEFAULTS_FALLBACK_SUMMARY, "invalid_configuration_defaults_fallback"),
                (w.USER_NAMESPACE_SUMMARY, "native_user_namespace_support_warning"),
                (w.WSL1_SUMMARY, "native_wsl1_namespace_warning")):
            for extras in ({"details": None}, {"details": "SECRET_NEVER_SAVE",
                    "path": "/SECRET_NEVER_SAVE", "range": {"SECRET_KEY": "SECRET_NEVER_SAVE"}}):
                receipt = self.classify({"summary": summary, **extras})
                self.assertEqual(receipt["category"], category)
                self.assertFalse(receipt["admitted"])
                self.assertNotIn(summary, json.dumps(receipt))
                self.assertNotIn("SECRET", json.dumps(receipt))
                self.assertNotIn(hashlib.sha256(summary.encode()).hexdigest(), json.dumps(receipt))

    def test_source_defined_prefixes_preserve_only_family_never_remainder(self):
        cases = [(w.DISABLED_PROJECT_PREFIX + " 1. /SECRET_NEVER_SAVE\n SECRET_REASON\n",
                  "disabled_project_configuration"),
                 (w.MANAGED_VALUE_PREFIX + "SECRET_FIELD` is disallowed by requirements; "
                  "falling back to required value SECRET_VALUE. Details: SECRET_ERROR",
                  "managed_requirement_value_fallback")]
        for summary, category in cases:
            receipt = self.classify({"summary": summary, "details": None})
            self.assertEqual(receipt["category"], category)
            self.assertFalse(receipt["admitted"])
            self.assertNotIn("SECRET", json.dumps(receipt))
            self.assertNotIn(hashlib.sha256(summary.encode()).hexdigest(), json.dumps(receipt))

    def test_diagnostic_constants_and_prefixes_match_the_archived_source(self):
        startup = (ROOT / "artifacts/GATE0_CODEX_STARTUP/20260907_001/codex-rs/app-server/src/lib.rs").read_text()
        bwrap = (ROOT / "artifacts/P3_CONFIG_WARNING_SOURCE/20260909_001/codex-rs/sandboxing/src/bwrap.rs").read_text()
        config = (ROOT / "artifacts/GATE0_CODEX_STARTUP/20260907_001/codex-rs/core/src/config/mod.rs").read_text()
        for literal in (w.POLICY_PARSE_SUMMARY, w.SQLITE_RECOVERY_SUMMARY, w.DEFAULTS_FALLBACK_SUMMARY):
            self.assertIn(json.dumps(literal), startup)
        self.assertIn(json.dumps(w.USER_NAMESPACE_SUMMARY), bwrap)
        body = bwrap.split("pub(crate) const WSL1_BWRAP_WARNING: &str = concat!(", 1)[1].split(");", 1)[0]
        self.assertEqual(w.WSL1_SUMMARY, "".join(json.loads(value) for value in re.findall(r'"[^"\n]*"', body)))
        body = startup.split("let mut message = concat!(", 1)[1].split(")", 1)[0]
        self.assertEqual(w.DISABLED_PROJECT_PREFIX, "".join(json.loads(value) for value in re.findall(r'"[^"\n]*"', body)))
        self.assertIn('"' + w.MANAGED_VALUE_PREFIX + '{field_name}` is disallowed by requirements; falling back', config)

    def test_only_validated_initialize_before_thread_with_zero_prior_advisory(self):
        for changes in ({"initialized": False}, {"initialized": 1},
                {"thread_requested": True}, {"thread_requested": None},
                {"previously_accepted": -1}, {"previously_accepted": False},
                {"previously_accepted": "0"}):
            with self.subTest(changes=changes):
                receipt = self.classify(self.params(), **changes)
                self.assertFalse(receipt["admitted"])
                self.assertEqual(receipt["decision"], "unexpected_warning_context")

    def test_duplicate_and_larger_count_stop(self):
        for count in (1, 2, 999999):
            receipt = self.classify(self.params(), previously_accepted=count)
            self.assertFalse(receipt["admitted"])
            self.assertEqual(receipt["decision"], "repeated_warning")

    def test_report_keys_are_fixed_and_never_include_the_native_literal(self):
        for params in (self.params(), {"summary": "SECRET_NEVER_SAVE", "details": None}):
            receipt = self.classify(params)
            self.assertEqual(set(receipt), {"category", "decision", "admitted", "raw_content_saved_or_hashed", "shape"})
            self.assertTrue(all(type(value) is bool for value in receipt["shape"].values()))
            self.assertNotIn(w.MISSING_BWRAP_SUMMARY, json.dumps(receipt))
            self.assertNotIn("SECRET_NEVER_SAVE", json.dumps(receipt))


if __name__ == "__main__":
    unittest.main()
