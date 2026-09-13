"""Focused046 conformance: small actual paths, frozen geometry and fault seams."""
import base64
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zlib

from accounting043 import Meter, canonical
import fullwork046 as full
import profile046 as profile

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "configs/P3_FULL_WORK_FIXTURES_046.json").read_text())
CASE_RESULTS = {}


def get_results():
    return {"cases": copy.deepcopy(CASE_RESULTS), "full_resource_profile_started": False,
        "scope": "Focused small fabricated integrations and max-shape N3 component conformance; no36-row complete-acquisition profile",
        "target_experiment_started": False, "native_started": False}


def decoded_archive(archive):
    maximum = 128 * 1024 * 1024
    if archive["uncompressed_limit_bytes"] != maximum or not 0 <= archive["uncompressed_bytes"] <= maximum:
        raise ValueError("UNCOMPRESSED_LENGTH_LIMIT")
    compressed = base64.b64decode(archive["data"], validate=True)
    if len(compressed) != archive["compressed_bytes"] or hashlib.sha256(compressed).hexdigest() != archive["compressed_sha256"]:
        raise ValueError("COMPRESSED_HASH_MISMATCH")
    decoder = zlib.decompressobj()
    raw = decoder.decompress(compressed, archive["uncompressed_bytes"] + 1)
    if decoder.unconsumed_tail or not decoder.eof or decoder.unused_data or len(raw) != archive["uncompressed_bytes"]:
        raise ValueError("BOUNDED_DECOMPRESSION_MISMATCH")
    if hashlib.sha256(raw).hexdigest() != archive["uncompressed_sha256"]:
        raise ValueError("UNCOMPRESSED_HASH_MISMATCH")
    return json.loads(raw)


class CompletePathTests(unittest.TestCase):
    def test_all_four_small_chains_replay_all_trials_and_readouts(self):
        results = {}
        for arm in CONFIG["arms"]:
            meter = Meter()
            row = {"case": "complete_chain", "size": "small", "arm": arm}
            summary = full.workload(CONFIG, row, meter)
            self.assertEqual(summary["configuration"], CONFIG["mechanism"])
            self.assertEqual(summary["replay"]["status"], "VERIFIED")
            self.assertEqual(len(summary["diagnostics"]), summary["scored_trial_count_with_events"])
            self.assertEqual(summary["readout_count"], 4 + summary["selected_predicate_count"])
            self.assertEqual(summary["deletion_readout_count"], summary["selected_predicate_count"])
            self.assertTrue(all(len(rows) == 20 for rows in summary["choices"].values()))
            self.assertTrue(all(len(r["five_forecasts"]) == 5 for rows in summary["choices"].values() for r in rows))
            restored = decoded_archive(summary["complete_evidence_serialization"]["archive"])
            self.assertEqual(restored["acquisition"]["state"]["arm"], arm)
            self.assertEqual(len(restored["acquisition"]["state"]["events"]), summary["environment_calls"])
            self.assertEqual(restored["replay"]["source_final_state_sha256"], summary["replay"]["source_final_state_sha256"])
            results[arm] = {"status": "PASSED", "B_env": summary["B_env"], "environment_calls": summary["environment_calls"],
                "scored_trials": len(summary["diagnostics"]), "readouts": summary["readout_count"],
                "archive_uncompressed_bytes": summary["complete_evidence_serialization"]["archive"]["uncompressed_bytes"],
                "report_bytes": len(profile.encoded(summary)), "logical_work": meter.work,
                "peak_logical_bytes": meter.peak_retained_bytes}
        CASE_RESULTS["all_four_small_chains"] = results

    def test_terminal_reservation_and_zero_partial_full_validation(self):
        outcomes = {}
        for budget in (13, 14, 15):
            config = copy.deepcopy(CONFIG)
            config["sizes"][0]["B_env"] = budget
            summary = full.complete_chain(config, {"size": "small", "arm": "COVERAGE"}, Meter())
            self.assertEqual(summary["environment_calls"], budget)
            first = summary["diagnostics"][0]
            self.assertEqual(len(first["validation_rows"]), budget - 13)
            self.assertEqual(first["status"], "AVAILABLE" if budget == 15 else "INCOMPLETE_VALIDATION")
            self.assertEqual(summary["replay"]["status"], "VERIFIED")
            outcomes[str(budget)] = {"status": first["status"], "validation_rows": len(first["validation_rows"]),
                "scored_with_events": summary["scored_trial_count_with_events"]}
        CASE_RESULTS["environment_stop_boundaries"] = outcomes

    def test_fabricated_tape_is_resettable_action_agnostic_and_not_target(self):
        first, second = full.FabricatedTape(), full.FabricatedTape()
        self.assertEqual(first.reset(), second.reset())
        self.assertEqual([first.step(0) for _ in range(16)], [second.step(4) for _ in range(16)])
        self.assertEqual(first.reset(), (0,))
        self.assertEqual(first.step(3), (1,))
        self.assertEqual(set(full.FabricatedTape.tape), set(range(5)))
        CASE_RESULTS["fabricated_interface"] = {"resettable": True, "action_agnostic": True, "tokens": 5, "target_dynamics_imported": False}


class GeometryTests(unittest.TestCase):
    def test_multigroup_max_shape_independent_keys_and_small_real_gain_pass(self):
        from collections import defaultdict
        groups = defaultdict(set)
        rows = full.geometry_transitions()
        for row in rows:
            key = (row.history.current, row.action, row.history.observations[-2])
            groups[key].add(row.outcome)
        self.assertEqual(len(rows), 245)
        self.assertEqual(len(groups), 122)
        self.assertEqual(sum(len(v) for v in groups.values()), 245)
        config = copy.deepcopy(CONFIG)
        config["stress"]["retained_records"] = 15
        result = full.multigroup_case(config, Meter())
        self.assertEqual((result["conflicting_groups"], result["outcome_entries"]), (7, 15))
        self.assertEqual(result["gain_calls"], 3002)
        self.assertEqual(result["readout_count"], 8)
        decoded_archive(result["overlap_serialization"]["archive"])
        CASE_RESULTS["multigroup_geometry"] = {"max_static_records": 245, "max_static_groups": 122,
            "max_static_outcome_entries": 245, "executed_records": 15, "executed_gain_calls": 3002,
            "actual_gain_pass_at_K4_reachable": False}

    def test_actual_greedy_selects_four_then_all_four_deletions(self):
        config = copy.deepcopy(CONFIG)
        config["stress"]["retained_records"] = 15
        result = full.k4_case(config, Meter())
        self.assertEqual(result["selected_predicate_count"], 4)
        self.assertEqual(len(result["construction_log"]), 4)
        self.assertEqual(set(result["choices"]), {"SELECTED", "DELETE_0", "DELETE_1", "DELETE_2", "DELETE_3", "ORDER0", "ORDER1", "ORDER2"})
        CASE_RESULTS["actual_K4_construction"] = {"updates": 15, "selected": 4, "grammar": 3002,
            "readouts": 8, "decisions_per_readout": 20}

    def test_long_raw_and_dense_N3_large_fraction_geometry(self):
        rows = {}
        for dense in (False, True):
            result = full.scheduler_case(CONFIG, Meter(), dense)
            self.assertEqual((result["F"], result["M"], result["raw_max_tokens"]), (55, 45, 10))
            self.assertEqual(result["raw_mutations_per_enumeration"], 27720)
            self.assertGreaterEqual(result["max_credit_numerator_bits"], 66)
            self.assertGreaterEqual(result["max_credit_denominator_bits"], 65)
            self.assertGreater(result["accepted_unique_proposals"], 0)
            restored = decoded_archive(result["overlap_serialization"]["archive"])
            self.assertEqual(len(restored["scheduler"]["recipes"]), 55)
            rows[result["case"]] = {k: result[k] for k in ("F", "M", "raw_mutations_per_enumeration", "raw_max_tokens",
                "accepted_unique_proposals", "retained_derivations", "max_credit_numerator_bits", "max_credit_denominator_bits")}
        self.assertGreater(rows["n3_dense"]["retained_derivations"], rows["n3_long_raw"]["retained_derivations"])
        CASE_RESULTS["N3_geometry"] = rows

    def test_archive_roundtrip_rejects_bad_length_and_tampering(self):
        payload = {"retained": [0, 1, 2], "text": "unchanged"}
        archive = full.serialize_retained(payload, Meter(), "test")["archive"]
        self.assertEqual(decoded_archive(archive), payload)
        for key, value in (("uncompressed_bytes", 134217729), ("uncompressed_bytes", 2), ("compressed_sha256", "0" * 64)):
            damaged = dict(archive, **{key: value})
            with self.assertRaises(ValueError):
                decoded_archive(damaged)
        CASE_RESULTS["complete_archive"] = {"exact_roundtrip": True, "bounded_decode": True, "tampering_rejected": True}


class DriverTests(unittest.TestCase):
    def test_split_transport_preserves_full_bytes_without_aggregate_payload_growth(self):
        measured = {"worker_kind": "P3_FULL_WORK_ROW_046_v1", "row_id": "row_00", "status": "COMPLETED",
            "source_hashes": profile.source_hashes(ROOT), "metrics": {"logical_work": 123},
            "summary": {"complete_fabricated_evidence": "x" * 400000},
            "stage_progress": [{"stage": "finished", "status": "COMPLETED", "logical_work": 123,
                "detail": {"earlier_full_evidence": "y" * 400000}}]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "row_00.json"
            profile.atomic_json(path, measured)
            original = path.read_bytes()
            index = profile.compact_worker_report(measured, path)
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(index["full_worker_report"], {"filename": "row_00.json",
                "sha256": hashlib.sha256(original).hexdigest(), "bytes": len(original)})
            self.assertIsNone(index["summary"])
            self.assertNotIn("detail", index["stage_progress"][0])
            # Forty-eight individually valid large reports would exceed the
            # former aggregate cap. Exact separate bytes keep the index small.
            self.assertGreater(len(original) * 48, CONFIG["limits"]["report_bytes"])
            aggregate = {"profiles": [index for _ in range(48)]}
            self.assertLess(len(profile.encoded(aggregate)), 128 * 1024)
            profile.atomic_json(Path(directory) / "REPORT.json", aggregate)
            self.assertEqual(json.loads(original)["summary"], measured["summary"])
        CASE_RESULTS["split_full_evidence_transport"] = {"full_worker_bytes_preserved": True,
            "exact_descriptor_verified": True, "aggregate_large_payload_multiplication_removed": True,
            "48_index_rows_below_bytes": 131072}

    def test_reuse_recovers_orphan_worker_without_rerun_and_rejects_changed_bytes(self):
        sources = profile.source_hashes(ROOT)
        report = {"kind": profile.KIND, "source_hashes": sources, "profiles": profile.planned_rows(CONFIG),
            "conformance": None, "status": "INCOMPLETE", "interruption": None,
            "complete_required_paths_measured": False, "attempted_rows": 1, "completed_rows": 0}
        report["profiles"][0].update(status="RESERVED", attempt_reserved=True)
        worker = {"row_id": "row_00", "source_hashes": sources, "status": "COMPLETED",
            "metrics": {"logical_work": 29}, "summary": {"full_result": "retained"}, "stage_progress": []}
        with tempfile.TemporaryDirectory() as directory, patch.object(profile, "run_child", side_effect=AssertionError("no reexecution")):
            path = Path(directory)
            profile.atomic_json(path / "REPORT.json", report)
            profile.atomic_json(path / "row_00.json", worker)
            raw = (path / "row_00.json").read_bytes()
            with patch("builtins.print"):
                recovered = profile.run(ROOT, path)
            self.assertEqual(recovered["profiles"][0]["status"], "INCOMPLETE")
            self.assertEqual(recovered["profiles"][0]["full_worker_report"]["sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(recovered["profiles"][0]["metrics"]["logical_work"], 29)
            self.assertEqual((path / "row_00.json").read_bytes(), raw)
            previous_index = (path / "REPORT.json").read_bytes()
            (path / "row_00.json").write_bytes(raw + b" ")
            with self.assertRaisesRegex(ValueError, "SAVED_WORKER_REPORT_IDENTITY_CHANGED"):
                profile.run(ROOT, path)
            self.assertEqual((path / "REPORT.json").read_bytes(), previous_index)
        CASE_RESULTS["orphan_return_recovery"] = {"worker_restarted": False,
            "unknown_disposition_kept_incomplete": True, "exact_bytes_recovered": True,
            "changed_worker_bytes_rejected": True}

    def test_deadline_stops_suite_and_preserves_active_case(self):
        executed, retained = [], []
        class DeadlineFixture(unittest.TestCase):
            def first(self):
                executed.append("first")
                raise profile.Interrupted("DECLARED_TEST_DEADLINE")
            def second(self):
                executed.append("second")
        suite = unittest.TestSuite([DeadlineFixture("first"), DeadlineFixture("second")])
        result = profile.NamedResults(lambda value: retained.append(copy.deepcopy(value)))
        with self.assertRaises(profile.Interrupted):
            suite.run(result)
        self.assertEqual(executed, ["first"])
        self.assertEqual(result.testsRun, 1)
        self.assertFalse(retained[-1]["passed"])
        self.assertTrue(retained[-1]["current_test"].endswith(".first"))
        self.assertEqual(retained[-1]["test_outcomes"], [])
        CASE_RESULTS["terminal_suite_deadline"] = {"later_test_started": False,
            "active_test_preserved": True, "deadline_treated_as_ordinary_test_failure": False}

    def test_frozen_48_identities_have_required_multiplicities(self):
        rows = profile.planned_rows(CONFIG)
        self.assertEqual(len(rows), 48)
        self.assertEqual(len({r["row_id"] for r in rows}), 48)
        self.assertEqual(sum(r["case"] == "complete_chain" for r in rows), 36)
        self.assertTrue(all(sum(r["case"] == case for r in rows) == 3 for case in CONFIG["stress_cases"]))
        self.assertEqual(profile.read_config(ROOT), CONFIG)
        self.assertEqual(len(profile.source_hashes(ROOT)), 8)
        CASE_RESULTS["row_multiplicities"] = {"rows": 48, "chains": 36, "stress": 12, "repetitions": 3, "sources": 8}

    def test_worker_interruption_preserves_completed_stages_and_usage(self):
        def stopped(config, row, meter, progress):
            meter.charge("fixture_completed_stage", 31)
            progress("acquisition", "COMPLETED", {"environment_calls": 7})
            progress("replay", "STARTED", None)
            raise profile.Interrupted("FROZEN_FAULT_SEAM")
        with tempfile.TemporaryDirectory() as directory, patch.object(profile, "process_limits", return_value={}), patch.object(profile.signal, "setitimer"), patch.object(full, "workload", side_effect=stopped):
            path = Path(directory) / "ROW.json"
            profile.worker(ROOT, path, "row_00", 5)
            report = json.loads(path.read_text())
        self.assertEqual(report["status"], "INCOMPLETE")
        self.assertEqual(report["metrics"]["logical_work"], 31)
        self.assertEqual(report["stage_progress"][0]["detail"]["environment_calls"], 7)
        self.assertEqual(report["stage_progress"][-1]["stage"], "replay")
        CASE_RESULTS["worker_partial_evidence"] = {"retained_prior_stage": True, "retained_meter": True, "automatic_resume": False}

    def test_driver_salvages_interrupted_child_and_repeat_never_relaunches(self):
        sources = profile.source_hashes(ROOT)
        count = []
        def child(root, path, row_id, seconds):
            count.append(row_id)
            if row_id == "conformance":
                value = {"status": "COMPLETED", "row_id": row_id, "source_hashes": sources,
                    "summary": {"passed": True, "tests_run": 1, "test_outcomes": [{"name": "synthetic", "status": "PASSED"}]}}
                profile.atomic_json(path, value)
                return value
            profile.atomic_json(path, {"status": "INCOMPLETE", "row_id": row_id, "source_hashes": sources,
                "stage_progress": [{"stage": "fixture", "status": "COMPLETED", "detail": {"retained": True}}],
                "summary": None, "metrics": {"logical_work": 19}})
            raise profile.Interrupted("FROZEN_PARENT_FAULT_SEAM")
        with tempfile.TemporaryDirectory() as directory, patch.object(profile, "process_limits", return_value={}), patch.object(profile.signal, "setitimer"), patch.object(profile, "run_child", side_effect=child):
            with patch("builtins.print"):
                first = profile.run(ROOT, Path(directory))
                second = profile.run(ROOT, Path(directory))
        self.assertEqual(count, ["conformance", "row_00"])
        self.assertEqual(first, second)
        self.assertEqual(first["profiles"][0]["metrics"]["logical_work"], 19)
        self.assertEqual(first["profiles"][0]["status"], "INCOMPLETE")
        self.assertEqual(first["profiles"][1]["status"], "NOT_STARTED")
        CASE_RESULTS["once_only_and_salvage"] = {"attempted_rows": 1, "automatic_remeasurement": False, "partial_child_salvaged": True}

    def test_prior_reservation_without_report_is_consumed(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(profile, "run_child", side_effect=AssertionError("forbidden child")):
            path = Path(directory)
            (path / "RESERVATION.json").write_text("{}")
            result = profile.run(ROOT, path)
        self.assertEqual(result["interruption"], "PRIOR_RESERVATION_WITHOUT_REPORT")
        self.assertEqual(result["attempted_rows"], 0)
        CASE_RESULTS["consumed_reservation"] = {"child_started": False, "reservation_reset": False}

    def test_report_size_gate_preserves_existing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "REPORT.json"
            profile.atomic_json(path, {"retained": True})
            before = path.read_bytes()
            with self.assertRaisesRegex(ValueError, "REPORT_PAYLOAD_LIMIT"):
                profile.atomic_json(path, {"large": "x" * 100}, maximum=10)
            self.assertEqual(path.read_bytes(), before)
        CASE_RESULTS["file_size_gate"] = {"existing_evidence_preserved": True}


if __name__ == "__main__":
    unittest.main()
