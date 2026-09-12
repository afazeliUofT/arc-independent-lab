"""Focused report/fixture contracts; never invokes a full component profile."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import profile043


class ProfileContract(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]

    def test_frozen_rows_and_exact_order(self):
        config = profile043.read_config(self.root)
        rows = profile043.planned_rows(config)
        self.assertEqual(27, len(rows))
        self.assertEqual(("small", "n1_no_positive_gain", 0), (rows[0]["size"], rows[0]["case"], rows[0]["repetition"]))
        self.assertEqual(("largest", "n3_proposal_and_credit", 2), (rows[-1]["size"], rows[-1]["case"], rows[-1]["repetition"]))
        self.assertEqual(27, len({(r["case"], r["size"], r["repetition"]) for r in rows}))

    def test_fixture_has_full_constants_without_W2_difference(self):
        from reference_n1_043 import History
        history = profile043.history_fixture(History)
        self.assertEqual({0, 1, 2, 3, 4}, set(history.actions))
        self.assertEqual((0, 0), history.actions[-2:])
        self.assertEqual(((0,), (0,), (0,)), history.observations[-3:])
        changed = profile043.history_fixture(History, 1)
        self.assertEqual(history.current, changed.current)
        self.assertEqual((1,), changed.observations[-2])

    def test_atomic_output_matches_report(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "REPORT.json"
            report = {"status": "INCOMPLETE", "observed": None}
            count = profile043.atomic_json(path, report)
            self.assertEqual(count, path.stat().st_size)
            self.assertEqual(report, json.loads(path.read_text()))
            self.assertEqual([path], list(Path(temp).iterdir()))

    def test_existing_report_is_never_remeasured(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "REPORT.json"
            original = {"kind": profile043.KIND, "status": "INCOMPLETE", "profiles": []}
            profile043.atomic_json(path, original)
            before = path.read_bytes()
            with mock.patch.object(profile043, "run_child", side_effect=AssertionError("remeasurement")), contextlib.redirect_stdout(io.StringIO()):
                returned = profile043.run(self.root, Path(temp))
            self.assertEqual(original, returned)
            self.assertEqual(before, path.read_bytes())

    def test_reserved_without_report_records_all_unmeasured_rows(self):
        with tempfile.TemporaryDirectory() as temp:
            (Path(temp) / "RESERVATION.json").write_text("{}")
            with mock.patch.object(profile043, "run_child", side_effect=AssertionError("remeasurement")), contextlib.redirect_stdout(io.StringIO()):
                returned = profile043.run(self.root, Path(temp))
            self.assertEqual("PRIOR_RESERVATION_WITHOUT_REPORT", returned["interruption"])
            self.assertEqual(27, len(returned["profiles"]))
            self.assertTrue(all(r["status"] == "NOT_STARTED" and r["metrics"] is None for r in returned["profiles"]))

    def test_named_conformance_failure_remains_categorical(self):
        class Fails(unittest.TestCase):
            def runTest(self):
                self.fail("Fabricated fixture text must not become a raw exception payload")
        result = profile043.NamedResults()
        Fails().run(result)
        self.assertFalse(result.wasSuccessful())
        self.assertEqual("FAILED", result.outcomes[0]["status"])
        self.assertEqual({"test", "status", "exception_class"}, set(result.outcomes[0]))

    def test_worker_parent_death_signal_and_race_check(self):
        library = mock.Mock()
        library.prctl.return_value = 0
        with mock.patch.object(profile043.ctypes, "CDLL", return_value=library), mock.patch.object(profile043.os, "getppid", return_value=18), mock.patch.object(profile043.os, "_exit", side_effect=RuntimeError("categorical stop")):
            profile043.bind_parent_lifetime(18)
            library.prctl.assert_called_once_with(1, profile043.signal.SIGKILL, 0, 0, 0)
            with self.assertRaises(RuntimeError):
                profile043.bind_parent_lifetime(19)

    def test_worker_resource_refusal_is_incomplete_not_conformance_failure(self):
        def refuse(case, size, meter):
            meter.memory_limit = 0
            meter.reserve("deliberate_development_refusal", 1)
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "component.json"
            with mock.patch.object(profile043, "process_limits", return_value={}), mock.patch.object(profile043.signal, "setitimer"), mock.patch.object(profile043, "n1_case", side_effect=refuse):
                profile043.worker(self.root, output, "n1_no_positive_gain", "small", 1)
            returned = json.loads(output.read_text())
            self.assertEqual("INCOMPLETE", returned["status"])
            self.assertEqual("MEMORY_LIMIT", returned["interruption"])
            self.assertEqual(0, returned["metrics"]["logical_retained_bytes"])


if __name__ == "__main__":
    unittest.main()
