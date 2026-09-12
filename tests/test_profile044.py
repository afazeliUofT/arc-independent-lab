"""Continuation integrity tests using synthetic orchestration; no component remeasurement."""
import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import profile044


class ContinuationContract(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]
        self.config, self.continuation = profile044.read_config(self.root)
        rows = profile044.frozen.planned_rows(self.config)
        for index, row in enumerate(rows):
            row["status"] = "COMPLETED" if index < 6 else "FAILED_CONFORMANCE" if index == 6 else "NOT_STARTED"
            row["interruption"] = None if index < 6 else "KeyError" if index == 6 else "BLOCKED_BY_PRIOR_STOP"
            row["metrics"] = {"wall_seconds": index + 0.125, "fixture": "SYNTHETIC_ORCHESTRATION_ONLY"} if index <= 6 else None
            row["summary"] = {"synthetic": True} if index < 6 else None
        prior = {"source_hashes": self.continuation["baseline_source_hashes"], "profiles": rows,
                 "aggregate_metrics": {"wall_seconds": 7.5, "synthetic": True}, "limitations": ["SYNTHETIC"],
                 "host": {"python": "SYNTHETIC_BASELINE", "platform": "linux"}}
        self.baseline = {"kind": "P3_DEVELOPMENT_PROFILE_EXECUTION_043_v1", "status": "PROFILE_INCOMPLETE",
                         "profile_report": prior, "profile_report_canonical_sha256": hashlib.sha256(profile044.encoded(prior)).hexdigest(),
                         "execution": {"wall_seconds": 8.0, "synthetic": True}}

    def patches(self):
        stack = contextlib.ExitStack()
        stack.enter_context(mock.patch.object(profile044, "load_baseline", return_value=copy.deepcopy(self.baseline)))
        stack.enter_context(mock.patch.object(profile044, "process_limits", return_value={}))
        stack.enter_context(mock.patch.object(profile044.signal, "setitimer"))
        stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
        return stack

    def test_first_scored_trial_skips_warmup_without_positional_assumption(self):
        warmup = [{"counter_t": 0, "phase": "WARMUP", "status": "COMPLETED"} for _ in range(5)]
        first = {"counter_t": 1, "status": "COMPLETED", "finalized_before_validation_assimilation": True}
        self.assertIs(first, profile044.first_scored_trial(warmup + [first]))
        self.assertIs(first, profile044.first_scored_trial([first] + warmup))
        with self.assertRaises(KeyError):
            _ = warmup[0]["finalized_before_validation_assimilation"]

    def test_missing_duplicate_or_mislabelled_first_scored_trial_rejected(self):
        for rows in ([], [{"counter_t": 0}], [{"counter_t": 1}, {"counter_t": 1}], [{"counter_t": 1, "phase": "WARMUP"}]):
            with self.subTest(rows=rows), self.assertRaisesRegex(AssertionError, "EXPECTED_ONE_FIRST_SCORED_TRIAL"):
                profile044.first_scored_trial(rows)

    def test_frozen_source_hashes_and_new_source_closure(self):
        sources = profile044.source_hashes(self.root)
        self.assertEqual(11, len(sources))
        self.assertEqual(self.continuation["baseline_source_hashes"], {k: sources[k] for k in profile044.frozen.SOURCES})
        self.assertEqual(list(range(6, 27)), self.continuation["eligible_new_row_indices"])

    def test_exact_baseline_hash_gate_before_row_import(self):
        raw = profile044.encoded(self.baseline)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "prior.json"
            path.write_bytes(raw)
            with self.assertRaisesRegex(ValueError, "BASELINE_REPORT_SHA256_MISMATCH"):
                profile044.load_baseline(path, self.config, self.continuation)
            with mock.patch.object(profile044, "BASELINE_SHA256", hashlib.sha256(raw).hexdigest()):
                self.assertEqual(self.baseline, profile044.load_baseline(path, self.config, self.continuation))

    def test_baseline_row_identity_and_child_hash_rejected(self):
        for mutation, error in (("identity", "BASELINE_ROW_IDENTITY_MISMATCH"), ("hash", "BASELINE_CHILD_HASH_MISMATCH")):
            value = copy.deepcopy(self.baseline)
            value["profile_report"]["profiles"][0]["repetition"] = 42
            if mutation == "identity":
                value["profile_report_canonical_sha256"] = hashlib.sha256(profile044.encoded(value["profile_report"])).hexdigest()
            raw = profile044.encoded(value)
            with tempfile.TemporaryDirectory() as temp:
                path = Path(temp) / "prior.json"
                path.write_bytes(raw)
                with mock.patch.object(profile044, "BASELINE_SHA256", hashlib.sha256(raw).hexdigest()), self.assertRaisesRegex(ValueError, error):
                    profile044.load_baseline(path, self.config, self.continuation)

    def test_import_preserves_every_original_field_and_source_identity(self):
        rows = profile044.continuation_rows(self.config, self.baseline, {"NEW": "SOURCE"})
        for index, row in enumerate(rows[:6]):
            restored = copy.deepcopy(row)
            provenance = restored.pop("measurement_provenance")
            original = self.baseline["profile_report"]["profiles"][index]
            self.assertEqual(original, restored)
            self.assertEqual(hashlib.sha256(profile044.encoded(original)).hexdigest(), provenance["original_row_canonical_sha256"])
            self.assertEqual("043", provenance["release"])
            self.assertFalse(provenance["remeasured"])
        self.assertTrue(all(r["status"] == "NOT_STARTED" and r["metrics"] is None for r in rows[6:]))
        rows[0]["metrics"]["wall_seconds"] = 999
        self.assertEqual(0.125, self.baseline["profile_report"]["profiles"][0]["metrics"]["wall_seconds"])

    def test_only_21_eligible_rows_are_attempted_and_totals_separate(self):
        calls = []
        def child(root, output, case, size, remaining):
            calls.append((output.name, case, size))
            return {"status": "COMPLETED", "summary": {"synthetic": True}, "metrics": {"wall_seconds": 0.0}}
        with tempfile.TemporaryDirectory() as temp, self.patches(), mock.patch.object(profile044, "run_child", side_effect=child):
            result = profile044.run(self.root, Path(temp), Path(temp) / "unread_synthetic_prior")
        self.assertEqual("COMPLETED", result["status"])
        self.assertEqual(22, len(calls))
        self.assertEqual("CONFORMANCE.json", calls[0][0])
        self.assertEqual(["COMPONENT_%02d.json" % i for i in range(6, 27)], [c[0] for c in calls[1:]])
        self.assertEqual(21, result["continuation"]["new_rows_attempted"])
        self.assertEqual(21, result["continuation"]["new_rows_completed"])
        self.assertEqual([self.baseline["profile_report"]["profiles"][6]], result["continuation"]["prior_failed_attempts"])
        self.assertEqual(self.baseline["profile_report"]["aggregate_metrics"], result["invocation_metrics"]["original043"]["aggregate_metrics"])
        self.assertEqual(result["aggregate_metrics"], result["invocation_metrics"]["continuation044"])
        self.assertEqual(self.baseline["profile_report"]["host"], result["invocation_metrics"]["original043"]["host"])
        self.assertEqual("044_INVOCATION_ONLY", result["host"]["scope"])
        self.assertIsNone(result["B_comp"])
        self.assertIsNone(result["B_mem"])
        self.assertFalse(result["target_execution_admitted"])

    def test_failed_new_row_stops_and_preserves_all_27_rows(self):
        calls = []
        def child(root, output, case, size, remaining):
            calls.append(case)
            return {"status": "COMPLETED" if case == "conformance" else "INCOMPLETE", "interruption": "SYNTHETIC_LIMIT", "metrics": None}
        with tempfile.TemporaryDirectory() as temp, self.patches(), mock.patch.object(profile044, "run_child", side_effect=child):
            result = profile044.run(self.root, Path(temp), Path(temp) / "unread_synthetic_prior")
        self.assertEqual(["conformance", "n3_proposal_and_credit"], calls)
        self.assertEqual("INCOMPLETE", result["status"])
        self.assertEqual(27, len(result["profiles"]))
        self.assertEqual(6, sum(r["status"] == "COMPLETED" for r in result["profiles"]))
        self.assertEqual(20, sum(r["status"] == "NOT_STARTED" for r in result["profiles"]))
        self.assertEqual(1, result["continuation"]["new_rows_attempted"])

    def test_existing_report_never_remeasures_or_rewrites(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "REPORT.json"
            original = {"kind": profile044.KIND, "status": "INCOMPLETE", "profiles": []}
            profile044.atomic_json(path, original)
            before = path.read_bytes()
            with mock.patch.object(profile044, "run_child", side_effect=AssertionError("remeasurement")), mock.patch.object(profile044, "load_baseline", side_effect=AssertionError("unnecessary reload")), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(original, profile044.run(self.root, Path(temp), Path(temp) / "missing"))
            self.assertEqual(before, path.read_bytes())

    def test_reserved_without_report_preserves_imports_but_never_launches(self):
        with tempfile.TemporaryDirectory() as temp:
            (Path(temp) / "RESERVATION.json").write_text("{}")
            with self.patches(), mock.patch.object(profile044, "run_child", side_effect=AssertionError("remeasurement")):
                result = profile044.run(self.root, Path(temp), Path(temp) / "unread_synthetic_prior")
        self.assertEqual("PRIOR_RESERVATION_WITHOUT_REPORT", result["interruption"])
        self.assertEqual(6, sum(r["status"] == "COMPLETED" for r in result["profiles"]))
        self.assertEqual(0, result["continuation"]["new_rows_attempted"])
        self.assertTrue(all(r["interruption"] == "PRIOR_RESERVATION_WITHOUT_REPORT" for r in result["profiles"][6:]))


if __name__ == "__main__":
    unittest.main()
