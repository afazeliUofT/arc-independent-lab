"""Synthetic prerequisite controls only; native namespace success is not assumed."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

LAB = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("gate0_postlogin_boundary", LAB / "scripts/gate0_postlogin_boundary.py")
boundary = importlib.util.module_from_spec(spec)
spec.loader.exec_module(boundary)


class BoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="boundary016_fixture_", dir=LAB / "delivery")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.run = self.root / "run"
        self.run.mkdir()
        self.bwrap = self.root / "bwrap_fixture"
        self.bwrap.write_bytes(b"synthetic executable identity; never run")
        self.auth = self.root / "actual_auth_sentinel"
        self.auth.write_bytes(b"synthetic stand-in for a path that must never be granted or read")
        self.facts = {"bwrap": self.bwrap, "bwrap_before": {"sha256": hashlib.sha256(self.bwrap.read_bytes()).hexdigest()},
                      "auth": self.auth, "runtime": self.root / "forbidden_native_runtime"}
        patch = mock.patch.object(boundary, "ROOT", self.root)
        patch.start()
        self.addCleanup(patch.stop)

    @staticmethod
    def observation(**changes):
        value = {"exit_code": 0, "cleanup_finished": True, "child_checks_passed": True,
                 "timed_out": False, "stream_ceiling_exceeded": False}
        value.update(changes)
        return value

    def fake_success(self, argv, fixture):
        (fixture / "synthetic_auth.json").write_bytes(boundary.REPLACEMENT)
        return self.observation()

    def test_validated_fake_effects_and_only_one_fake_write_bind(self):
        original_open = Path.open
        def guard(path, *args, **kwargs):
            self.assertNotEqual(path, self.auth, "Real credential stand-in opened")
            return original_open(path, *args, **kwargs)
        with mock.patch.object(boundary, "_execute", side_effect=self.fake_success), \
             mock.patch.object(Path, "open", guard):
            report = boundary.check(self.facts, self.run)
        self.assertTrue(report["passed"])
        self.assertFalse(report["real_credential_granted"])
        self.assertFalse(report["full_reviewer_boundary_verified"])
        argv = report["argv"]
        self.assertNotIn(str(self.auth), argv)
        self.assertNotIn(str(self.facts["runtime"]), argv)
        binds = [argv[i + 1:i + 3] for i, arg in enumerate(argv) if arg == "--bind"]
        fake = str(self.run / "synthetic_boundary/synthetic_auth.json")
        self.assertEqual(binds, [[fake, fake]])
        self.assertEqual(argv.count("--share-net"), 1)

    def test_protocol_success_without_actual_effect_is_not_pass(self):
        with mock.patch.object(boundary, "_execute", return_value=self.observation()):
            report = boundary.check(self.facts, self.run)
        self.assertFalse(report["passed"])
        self.assertFalse(report["host_fixture_checks"]["exact_replacement"])

    def test_timeout_and_partial_fixture_never_retry(self):
        with mock.patch.object(boundary, "_execute", return_value=self.observation(timed_out=True)) as execute:
            first = boundary.check(self.facts, self.run)
            second = boundary.check(self.facts, self.run)
        self.assertFalse(first["passed"])
        self.assertFalse(second["passed"])
        execute.assert_called_once()
        self.assertIn("reason", second)

    def test_changed_binary_rejected_before_fixture_creation(self):
        self.bwrap.write_bytes(b"different synthetic executable")
        with mock.patch.object(boundary, "_execute") as execute:
            report = boundary.check(self.facts, self.run)
        self.assertFalse(report["passed"])
        self.assertFalse((self.run / "synthetic_boundary").exists())
        execute.assert_not_called()

    def test_reply_requires_exact_boolean_fields_and_no_extras(self):
        self.assertTrue(boundary._parsed_checks(json.dumps(boundary.EXPECTED)))
        variants = [dict(boundary.EXPECTED, same_file_write_completed=1),
                    dict(boundary.EXPECTED, extra=True),
                    {key: value for key, value in boundary.EXPECTED.items() if key != "network_requests_made"},
                    dict(boundary.EXPECTED, network_requests_made=True)]
        for value in variants:
            with self.subTest(value=value):
                self.assertFalse(boundary._parsed_checks(json.dumps(value)))
        with self.assertRaises(ValueError):
            boundary._parsed_checks('{"same_file_write_completed":true,"same_file_write_completed":false}')


if __name__ == "__main__":
    unittest.main()
