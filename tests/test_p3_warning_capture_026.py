"""Offline controller contracts; native/model execution is forbidden in this suite.

Historical report copies and reconstructed SESSION bytes below are explicitly
temporary test fixtures. They are never installed as laptop execution evidence.
The unchanged old history guard is mocked only where that fixture lacks the
earlier canonical laptop directories. Its consumer and024 receipt checks stay real.
"""
from __future__ import annotations

from contextlib import redirect_stdout
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

LAB = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "p3_warning_capture_026_controller_tested", LAB / "scripts/p3_warning_capture_026.py")
controller = importlib.util.module_from_spec(spec)
spec.loader.exec_module(controller)


def canonical(value):
    return (json.dumps(value, indent=2, ensure_ascii=True, allow_nan=False) + "\n").encode()


def put(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)


class Controller026Tests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="warning026_controller_fixture_", dir=LAB)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        forbidden = mock.patch.object(subprocess, "Popen", side_effect=AssertionError(
            "Native/model process execution is forbidden in controller tests"))
        self.Popen = forbidden.start()
        self.addCleanup(forbidden.stop)
        self.scope, self.scope024, self.prior, self.pins = controller.load_bundle()
        self.case = 0

    def historical_fixture(self):
        raw = (LAB / controller.REPORT024_PATH).read_bytes()
        value = json.loads(raw)
        run = self.root / "delivery" / controller.old.RUN_NAME
        put(run / "REPORT.json", raw)
        put(run / "REPORT.sha256", (controller.sha(raw) + "\n").encode())
        # Test-only reconstruction, clearly confined to the named fixture root.
        put(run / "synthetic_SESSION.json", canonical(value["stages"][0]["observation"]))
        put(self.root / controller.REPORT024_PATH, raw)
        put(self.root / controller.REPORT025_PATH, (LAB / controller.REPORT025_PATH).read_bytes())
        return run, value

    def historical_call(self, value):
        with mock.patch.object(controller, "ROOT", self.root), mock.patch.object(
                controller.old, "prior_failed_attempt", return_value=value["prior_attempt"]) as old_guard:
            result = controller.prior_history(self.pins)
        self.assertEqual(old_guard.call_count, 1)
        return result

    def execute_fixture(self, *, started=True, sent=True, success=False,
                        host_pass=True, cleanup=True, save_session=True,
                        error=None, before_stage_error=False):
        self.case += 1
        execution_root = self.root / ("case_" + str(self.case))
        (execution_root / "delivery").mkdir(parents=True)
        observation = {
            "kind": "P3_WARNING_CAPTURE_SESSION_026_v1", "mode": "synthetic",
            "client_started": started, "model_turn_request_sent": sent,
            "native_process_reaped": cleanup,
            "status": "SYNTHETIC_REFUSAL_OBSERVED" if success else "STOPPED_WITHOUT_VERDICT",
            "synthetic_allowed_read_observed": success, "observed_refusal": success,
            "verdict_submitted": False,
            "warning_observations": [] if success else [{"category": "unknown", "admitted": False}],
            "fixture_only": True,
        }
        def stage(scope024, prior, run, mode, packet, manifest):
            self.assertEqual(mode, "synthetic")
            if save_session:
                controller.exclusive_json(run / "synthetic_SESSION.json", observation)
            if error:
                raise error
            return {"stage": mode, "observation": observation,
                    "host_checks": {"all_noncredential_checks_pass": host_pass},
                    "fixture_only": True}
        history = {"fixture_only": True, "prior_native_starts": 5, "prior_sent_turns": 2}
        authorization = {"fixture_only": True, "explicit_manual_launch": True}
        with mock.patch.object(controller, "ROOT", execution_root), mock.patch.object(
                controller, "prior_history", side_effect=controller.Stop("History fixture stopped")
                if before_stage_error else None, return_value=history), mock.patch.object(
                controller, "run_stage", side_effect=stage) as stage_mock:
            if before_stage_error:
                with self.assertRaises(controller.Stop):
                    controller.execute(self.scope, self.scope024, self.prior, self.pins, authorization)
                self.assertFalse((execution_root / "delivery" / controller.RUN_NAME).exists())
                stage_mock.assert_not_called()
                return None, None, stage_mock
            path = controller.execute(self.scope, self.scope024, self.prior, self.pins, authorization)
        self.assertEqual(stage_mock.call_count, 1)
        self.assertFalse(any((path.parent / name).exists() for name in (
            "science_native", "science_output", "science_SESSION.json")))
        self.Popen.assert_not_called()
        return path, json.loads(path.read_bytes()), stage_mock

    def rewrite_receipt(self, path, value):
        raw = canonical(value)
        path.write_bytes(raw)
        path.with_name("REPORT.sha256").write_text(controller.sha(raw) + "\n")

    def test_real_load_bundle_checks_inherited_and_new_pins_without_launch(self):
        self.assertEqual(len(self.pins["inherited024_pins"]["source_pins"]), 100)
        self.assertGreaterEqual(len(self.pins["source_pins"]), 3)
        self.assertEqual(self.scope["cumulative_native_ceiling"], 6)
        self.assertEqual(self.scope["cumulative_sent_turn_ceiling"], 3)
        self.assertIs(self.scope["science_allowed"], False)
        self.Popen.assert_not_called()

    def test_default_inspection_does_not_check_host_or_launch(self):
        with mock.patch.object(sys, "argv", ["p3_warning_capture_026.py"]), mock.patch.object(
                controller.old, "canonical_host", side_effect=AssertionError("Inspection cannot inspect host")), mock.patch.object(
                controller, "execute", side_effect=AssertionError("Inspection cannot execute")), redirect_stdout(io.StringIO()) as out:
            self.assertEqual(controller.main(), 0)
        self.assertIn("Inspection only", out.getvalue())
        self.Popen.assert_not_called()

    def test_actual_approval_requires_manual_launch_and_does_not_claim_new_digest_approval(self):
        for manual in (False, None, 1, "true"):
            with self.subTest(manual=manual), self.assertRaises(controller.Stop):
                controller.approval(self.scope, self.scope024, manual_launch=manual)
        result = controller.approval(self.scope, self.scope024, manual_launch=True)
        self.assertEqual(result["inherited024_access_approval"]["sha256"], controller.AUTH024_SHA256)
        self.assertIs(result["old_scope_digest_approves_new_code"], False)
        self.assertIs(result["new_budget_ceiling_requested"], False)
        self.assertIs(result["science_authorized_by_this_operation"], False)

    def test_changed_inherited_approval_is_refused(self):
        with mock.patch.object(controller.old, "approval", return_value={"path": "state/ESCALATION.md", "sha256": "0" * 64}):
            with self.assertRaises(controller.Stop):
                controller.approval(self.scope, self.scope024, manual_launch=True)

    def test_real024_receipt_consumer_and_history_linkage_pass_with_explicit_test_fixtures(self):
        run, value = self.historical_fixture()
        result = self.historical_call(value)
        self.assertTrue(result["separate024_session_reverified"])
        self.assertEqual(result["prior_native_starts"], 5)
        self.assertEqual(result["prior_sent_turns"], 2)
        self.assertEqual(hashlib.sha256((run / "synthetic_SESSION.json").read_bytes()).hexdigest(), controller.SESSION024_SHA256)

    def test_missing_separate024_session_is_not_reconstructed(self):
        run, value = self.historical_fixture()
        (run / "synthetic_SESSION.json").unlink()
        with self.assertRaises((controller.Stop, OSError)):
            self.historical_call(value)
        self.assertFalse((run / "synthetic_SESSION.json").exists())

    def test_changed_separate024_session_is_refused_and_preserved(self):
        run, value = self.historical_fixture()
        changed = (run / "synthetic_SESSION.json").read_bytes() + b" \n"
        (run / "synthetic_SESSION.json").write_bytes(changed)
        with self.assertRaises(controller.Stop):
            self.historical_call(value)
        self.assertEqual((run / "synthetic_SESSION.json").read_bytes(), changed)

    def test_changed024_report_even_with_recomputed_local_checksum_is_refused(self):
        run, value = self.historical_fixture()
        changed = copy.deepcopy(value)
        changed["attempt_accounting"]["cumulative_native_starts_observed_in_session_receipts"] = 4
        self.rewrite_receipt(run / "REPORT.json", changed)
        with self.assertRaises(controller.Stop):
            self.historical_call(value)

    def test_changed_offline025_receipt_is_refused(self):
        _, value = self.historical_fixture()
        target = self.root / controller.REPORT025_PATH
        changed = json.loads(target.read_bytes())
        changed["model_turns_sent"] = 1
        target.write_bytes(canonical(changed))
        with self.assertRaises(controller.Stop):
            self.historical_call(value)

    def test_unverified_history_stops_before_directory_reservation_or_stage(self):
        self.execute_fixture(before_stage_error=True)

    def test_no_launch_failure_still_retains_finite_reservation(self):
        path, value, _ = self.execute_fixture(started=False, sent=False)
        self.assertEqual(value["status"], "STOPPED_DIAGNOSTIC_NO_SCIENCE")
        count = value["attempt_accounting"]
        self.assertEqual((count["cumulative_observed_native_starts"], count["cumulative_observed_sent_turns"]), (5, 2))
        self.assertEqual((count["maximum_cumulative_reservation_native_starts"], count["maximum_cumulative_reservation_turns"]), (6, 3))
        self.assertTrue(count["unobserved_reserved_capacity_is_not_automatically_released"])
        self.assertIsNotNone(controller.existing(path.parent, self.pins))

    def test_sent_synthetic_turn_counts_without_output(self):
        _, value, _ = self.execute_fixture()
        count = value["attempt_accounting"]
        self.assertEqual((count["cumulative_observed_native_starts"], count["cumulative_observed_sent_turns"]), (6, 3))
        self.assertIsNone(value["reviewer_output"])
        self.assertIs(value["science_started"], False)

    def test_successful_synthetic_refusal_never_starts_science(self):
        path, value, _ = self.execute_fixture(success=True)
        self.assertEqual(value["status"], "SYNTHETIC_DIAGNOSTIC_COMPLETED_NO_SCIENCE")
        self.assertEqual(len(value["stages"]), 1)
        self.assertEqual(controller.existing(path.parent, self.pins), path)

    def test_cleanup_or_host_failure_never_reports_completion(self):
        for changes in ({"cleanup": False}, {"host_pass": False}):
            with self.subTest(changes=changes):
                _, value, _ = self.execute_fixture(success=True, **changes)
                self.assertEqual(value["status"], "STOPPED_DIAGNOSTIC_NO_SCIENCE")

    def test_stage_exception_preserves_written_session_and_suppresses_raw_error(self):
        secret = "DO_NOT_RETAIN_NATIVE_ERROR_5a43de"
        path, value, _ = self.execute_fixture(error=RuntimeError(secret))
        self.assertEqual(value["status"], "STOPPED_DIAGNOSTIC_NO_SCIENCE")
        self.assertNotIn(secret, path.read_text())
        self.assertEqual(value["attempt_accounting"]["cumulative_observed_sent_turns"], 3)
        self.assertEqual(len(value["preserved_session_receipts"]), 1)

    def test_missing_session_after_exception_keeps_full_reservation(self):
        _, value, _ = self.execute_fixture(save_session=False, error=RuntimeError("fixture"))
        self.assertEqual(value["status"], "STOPPED_DIAGNOSTIC_NO_SCIENCE")
        count = value["attempt_accounting"]
        self.assertTrue(count["missing_session_counts_are_only_minimum_observations"])
        self.assertEqual((count["maximum_cumulative_reservation_native_starts"], count["maximum_cumulative_reservation_turns"]), (6, 3))

    def test_success_without_preserved_session_must_not_report_completion(self):
        _, value, _ = self.execute_fixture(success=True, save_session=False)
        self.assertNotEqual(value["status"], "SYNTHETIC_DIAGNOSTIC_COMPLETED_NO_SCIENCE")

    def test_success_requires_actual_start_and_sent_turn_observations(self):
        for changes in ({"started": False, "sent": False}, {"sent": False}):
            with self.subTest(changes=changes):
                _, value, _ = self.execute_fixture(success=True, **changes)
                self.assertNotEqual(value["status"], "SYNTHETIC_DIAGNOSTIC_COMPLETED_NO_SCIENCE")

    def test_complete_receipt_is_reused_without_host_or_native_call(self):
        path, _, _ = self.execute_fixture()
        before = {p.relative_to(path.parent): p.read_bytes() for p in path.parent.rglob("*") if p.is_file()}
        with mock.patch.object(controller, "ROOT", path.parent.parent.parent), mock.patch.object(
                controller, "load_bundle", return_value=(self.scope, self.scope024, self.prior, self.pins)), mock.patch.object(
                controller.old, "canonical_host", side_effect=AssertionError("No repeat host check")), mock.patch.object(
                controller, "execute", side_effect=AssertionError("No repeat execution")), mock.patch.object(
                sys, "argv", ["p3_warning_capture_026.py", "--run-attended-diagnostic"]), redirect_stdout(io.StringIO()) as out:
            self.assertEqual(controller.main(), 0)
        self.assertIn("REUSED", out.getvalue())
        self.assertEqual({p.relative_to(path.parent): p.read_bytes() for p in path.parent.rglob("*") if p.is_file()}, before)

    def test_partial_directory_is_preserved_and_refused(self):
        run = self.root / "delivery" / controller.RUN_NAME
        put(run / "ATTEMPT.json", b'{"fixture_only":true}\n')
        before = (run / "ATTEMPT.json").read_bytes()
        with self.assertRaises((controller.Stop, OSError)):
            controller.existing(run, self.pins)
        self.assertEqual((run / "ATTEMPT.json").read_bytes(), before)
        self.assertFalse((run / "REPORT.json").exists())

    def test_modified_session_is_refused_on_reuse(self):
        path, _, _ = self.execute_fixture()
        with (path.parent / "synthetic_SESSION.json").open("ab") as f:
            f.write(b" \n")
        with self.assertRaises(controller.Stop):
            controller.existing(path.parent, self.pins)

    def test_forged_science_stage_path_is_refused(self):
        path, _, _ = self.execute_fixture()
        (path.parent / "science_output").mkdir()
        with self.assertRaises(controller.Stop):
            controller.existing(path.parent, self.pins)

    def test_changed_attempt_journal_is_refused_even_when_report_is_unchanged(self):
        path, _, _ = self.execute_fixture()
        journal = path.parent / "ATTEMPT.json"
        value = json.loads(journal.read_bytes())
        value["reserved_turns"] = 0
        journal.write_bytes(canonical(value))
        with self.assertRaises(controller.Stop):
            controller.existing(path.parent, self.pins)

    def test_accounting_must_agree_with_preserved_session_and_ceiling(self):
        for key, wrong in (("observed_native_starts_this_attempt", 999),
                           ("cumulative_observed_sent_turns", 2),
                           ("reserved_turns_this_attempt", True)):
            with self.subTest(key=key):
                path, value, _ = self.execute_fixture()
                value["attempt_accounting"][key] = wrong
                self.rewrite_receipt(path, value)
                with self.assertRaises(controller.Stop):
                    controller.existing(path.parent, self.pins)


if __name__ == "__main__":
    unittest.main()
