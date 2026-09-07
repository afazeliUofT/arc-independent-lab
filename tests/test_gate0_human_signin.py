"""Refusal and retry checks using project-contained stubs; never launch Codex."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

LAB = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("gate0_signin", LAB / "scripts/gate0_human_signin.py")
signin = importlib.util.module_from_spec(spec)
spec.loader.exec_module(signin)


class SigninTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="signin015_fixture_", dir=LAB / "delivery")
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name) / "home"
        self.root = self.home / "ARC_Independent_Lab"
        for path in (self.home / ".codex", self.root / "delivery", self.root / "state",
                     self.root / "configs", self.root / "scripts", self.root / "source"):
            path.mkdir(parents=True, exist_ok=True)
        self.runtime = self.home / ".codex/codex_fixture"
        self.runtime.write_bytes(b"not executable; fixture only")
        self.config = self.home / ".codex/config.toml"
        self.config.write_text('cli_auth_credentials_store = "file"\n')
        (self.root / signin.WRAPPER).write_bytes((LAB / signin.WRAPPER).read_bytes())
        (self.root / "source/native.rs").write_bytes(b"// public fixture source\n")
        manifest = {"files": [{"path": "native.rs", "sha256": signin.sha((self.root / "source/native.rs").read_bytes())}]}
        source_raw = json.dumps(manifest).encode()
        (self.root / "source/MANIFEST.json").write_bytes(source_raw)
        self.observed = {"origin_inventory": [
            {"path": str(self.config), "present": True, "metadata": signin.metadata(self.config)},
            {"path": str(self.home / ".codex/auth.json"), "present": False}],
            "observation": {"account_configuration": {"configured_backend": "file"}}}
        observed_raw = json.dumps(self.observed).encode()
        (self.root / "observed.json").write_bytes(observed_raw)
        self.scope = {"timeout_seconds": 300, "callback_port": 1455,
            "canonical_home": str(self.home), "canonical_project": str(self.root),
            "runtime_relative_to_home": ".codex/codex_fixture",
            "runtime_sha256": signin.sha(self.runtime.read_bytes()),
            "native_login_argv": ["$HOME/.codex/codex_fixture", "login"],
            "observed_report_path": "observed.json", "observed_report_sha256": signin.sha(observed_raw),
            "source_manifest": "source/MANIFEST.json", "source_manifest_sha256": signin.sha(source_raw),
            "report_directory": "delivery/GATE0_HUMAN_SIGNIN_015"}
        scope_raw = json.dumps(self.scope).encode()
        (self.root / signin.SCOPE).write_bytes(scope_raw)
        self.scope_sha = signin.sha(scope_raw)
        self.patch = mock.patch.object(signin, "SCOPE_SHA256", self.scope_sha)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        (self.root / "state/ESCALATION.md").write_text("Pending human authorization.\n")
        self.pins = signin.load_bundle(self.root)[2]
        self.run_dir = self.root / self.scope["report_directory"]

    def approve(self):
        (self.root / "state/ESCALATION.md").write_text(
            "## ANSWER\nAPPROVE_G0_SIGNIN_015\nscope_sha256: " + self.scope_sha + "\n")

    def host_check(self):
        # Pure in-process test views, not runtime environment reassignment.
        with mock.patch.object(signin.os, "environ", {"HOME": str(self.home)}), \
             mock.patch.object(signin.Path, "home", return_value=self.home):
            return signin.preflight(self.root, self.scope, self.observed)

    def receipt(self, **changes):
        report = {"kind": signin.REPORT_KIND, "pins": self.pins,
            "created_utc": "2026-09-07T00:00:00+00:00", "scope": signin.RECEIPT_SCOPE,
            "native_started": True, "native_exit_code": 0, "timed_out": False,
            "interrupted": False, "launch_failed": False, "auth_file_present": True,
            "model_invoked_by_wrapper": False, "account_live_verified": False,
            "allowance_verified": False, "reviewer_boundary_verified": False}
        report.update(changes)
        return report

    def save_receipt(self, report):
        self.run_dir.mkdir()
        signin.exclusive_json(self.run_dir / "ATTEMPT.json", {"pins": self.pins})
        signin.exclusive_json(self.run_dir / "REPORT.json", report)
        (self.run_dir / "SHA256SUMS").write_text("".join(
            signin.sha((self.run_dir / name).read_bytes()) + "  " + name + "\n"
            for name in ("ATTEMPT.json", "REPORT.json")))

    def test_unapproved_no_launch_or_directory_writes(self):
        with mock.patch.object(signin, "preflight") as preflight, \
             mock.patch.object(signin, "execute_native") as execute:
            with self.assertRaises(signin.Stop):
                signin.run(self.root, sign_in=True)
            preflight.assert_not_called()
            execute.assert_not_called()
        self.assertFalse(self.run_dir.exists())

    def test_fenced_or_indented_template_is_not_approval(self):
        answer = "## ANSWER\nAPPROVE_G0_SIGNIN_015\nscope_sha256: " + self.scope_sha
        for example in ("```text\n" + answer + "\n```\n", "~~~\n" + answer + "\n~~~\n",
                        "\n".join("    " + line for line in answer.splitlines())):
            (self.root / "state/ESCALATION.md").write_text(example)
            with self.assertRaises(signin.Stop):
                signin.approval(self.root, self.pins)
        # The real current request contains no human approval either.
        (self.root / "state/ESCALATION.md").write_bytes((LAB / "state/ESCALATION.md").read_bytes())
        with self.assertRaises(signin.Stop):
            signin.approval(self.root, {"scope_sha256": "6020d46ae6818f6c15341a7074ea4f7306b3764d8c64a92d0dcce745ed1c7ccd"})

    def test_approval_restrictions_are_not_silently_ignored(self):
        self.approve()
        signin.approval(self.root, self.pins)
        with (self.root / "state/ESCALATION.md").open("a") as handle:
            handle.write("Only if no credential file is created.\n")
        with self.assertRaises(signin.Stop):
            signin.approval(self.root, self.pins)
        self.approve()
        with (self.root / "state/ESCALATION.md").open("a") as handle:
            handle.write("```text\nOnly if no credential file is created.\n```\n")
        with self.assertRaises(signin.Stop):
            signin.approval(self.root, self.pins)

    def test_default_inspection_never_launches_binds_or_writes(self):
        with mock.patch.object(signin, "preflight", return_value=([str(self.runtime), "login"], self.root / "delivery", self.home / ".codex/auth.json")), \
             mock.patch.object(signin, "callback_available") as callback, \
             mock.patch.object(signin, "execute_native") as execute:
            result = signin.run(self.root)
            self.assertEqual(result["status"], "INSPECTION_ONLY_NO_WRITES_NETWORK_OR_LOGIN")
            callback.assert_not_called()
            execute.assert_not_called()
        self.assertFalse(self.run_dir.exists())

    def test_completed_receipt_reused_without_host_measurement_or_launch(self):
        self.save_receipt(self.receipt(native_exit_code=1))
        with mock.patch.object(signin, "preflight") as preflight, \
             mock.patch.object(signin, "callback_available") as callback, \
             mock.patch.object(signin, "execute_native") as execute:
            result = signin.run(self.root, sign_in=True)
            self.assertEqual(result["native_exit_code"], 1)
            self.assertTrue(result["status"].startswith("REUSED_"))
            preflight.assert_not_called()
            callback.assert_not_called()
            execute.assert_not_called()

    def test_partial_attempt_or_modified_receipt_preserved(self):
        self.run_dir.mkdir()
        (self.run_dir / "ATTEMPT.json").write_text("{}")
        with self.assertRaises(signin.Stop):
            signin.run(self.root, sign_in=True)
        self.assertEqual((self.run_dir / "ATTEMPT.json").read_text(), "{}")

    def test_approved_run_records_once_and_reuses_after_answer_archived(self):
        self.approve()
        auth = self.home / ".codex/auth.json"
        tty = mock.Mock()
        tty.isatty.return_value = True
        def fake_native(argv, cwd, seconds):
            self.assertEqual(argv, [str(self.runtime), "login"])
            self.assertEqual(seconds, 300)
            self.assertTrue((self.run_dir / "ATTEMPT.json").is_file())
            auth.write_bytes(b"nonsecret fixture; never read by wrapper")
            return {"native_started": True, "native_exit_code": 0,
                    "timed_out": False, "interrupted": False, "launch_failed": False}
        with mock.patch.object(signin, "preflight", return_value=([str(self.runtime), "login"], self.root / "delivery", auth)), \
             mock.patch.object(signin, "callback_available") as callback, \
             mock.patch.object(signin, "execute_native", side_effect=fake_native) as execute, \
             mock.patch.object(signin.sys, "stdin", tty), \
             mock.patch.object(signin.sys, "stdout", tty), \
             mock.patch.object(signin.sys, "stderr", tty):
            first = signin.run(self.root, sign_in=True)
            self.assertEqual(first["status"], "RECORDED_HUMAN_SIGNIN_RECEIPT")
            self.assertTrue(first["auth_file_present"])
            execute.assert_called_once()
            callback.assert_called_once_with(1455)
        (self.root / "state/ESCALATION.md").rename(self.root / "state/archived_answer.md")
        self.config.write_text("fixture changed after completed observation")
        self.runtime.write_bytes(b"fixture changed after completed observation")
        original_read = Path.read_bytes
        def guarded_read(path):
            self.assertNotIn(path, (auth, self.config, self.runtime))
            return original_read(path)
        with mock.patch.object(signin, "preflight") as preflight, \
             mock.patch.object(signin, "execute_native") as execute, \
             mock.patch.object(Path, "read_bytes", guarded_read):
            reused = signin.run(self.root, sign_in=True)
            self.assertTrue(reused["status"].startswith("REUSED_"))
            preflight.assert_not_called()
            execute.assert_not_called()

    def test_changed_source_and_scope_refuse(self):
        source = self.root / "source/native.rs"
        source.write_text("changed public fixture source")
        with self.assertRaises(signin.Stop):
            signin.load_bundle(self.root)
        source.write_bytes(b"// public fixture source\n")
        with (self.root / signin.SCOPE).open("a") as handle:
            handle.write(" ")
        with self.assertRaises(signin.Stop):
            signin.load_bundle(self.root)

    def test_changed_wrapper_blocks_completed_report_reuse(self):
        self.save_receipt(self.receipt())
        with (self.root / signin.WRAPPER).open("a") as handle:
            handle.write("\n# change\n")
        with self.assertRaises(signin.Stop):
            signin.run(self.root, sign_in=True)

    def test_existing_auth_never_opened_or_replaced(self):
        auth = self.home / ".codex/auth.json"
        auth.write_bytes(b"nonsecret fixture sentinel")
        original_read = Path.read_bytes
        def guarded_read(path):
            self.assertNotEqual(path, auth, "Credential path was opened")
            return original_read(path)
        with mock.patch.object(Path, "read_bytes", guarded_read):
            with self.assertRaises(signin.Stop):
                self.host_check()
        self.assertEqual(auth.read_bytes(), b"nonsecret fixture sentinel")

    def test_origin_metadata_runtime_and_log_directory_changes_refuse(self):
        self.host_check()
        self.config.write_text('cli_auth_credentials_store = "file"\n# changed\n')
        with self.assertRaises(signin.Stop):
            self.host_check()

        self.observed["origin_inventory"][0]["metadata"] = signin.metadata(self.config)
        self.runtime.write_bytes(b"changed runtime fixture")
        with self.assertRaises(signin.Stop):
            self.host_check()
        self.runtime.write_bytes(b"not executable; fixture only")
        self.config.write_text('log_dir = "/outside-approved-scope"\n')
        self.observed["origin_inventory"][0]["metadata"] = signin.metadata(self.config)
        with self.assertRaises(signin.Stop):
            self.host_check()

    def test_profile_selection_or_composition_requires_explicit_resolution(self):
        for value in ('profile = "selected"\n', '[profiles.selected]\nlog_dir = "/outside"\n',
                      'include = "another.toml"\n'):
            self.config.write_text(value)
            self.observed["origin_inventory"][0]["metadata"] = signin.metadata(self.config)
            with self.assertRaises(signin.Stop):
                self.host_check()
    def test_receipt_types_do_not_accept_boolean_exit_or_string_flags(self):
        for changes in ({"native_exit_code": True}, {"timed_out": "false"},
                        {"auth_file_present": 1}, {"account_live_verified": True},
                        {"unexpected_raw_field": "nonsecret fixture must not be displayed"}):
            with self.assertRaises(signin.Stop):
                signin.validate_receipt(self.receipt(**changes), self.pins)

    def test_timeout_and_nonzero_use_stubs_no_native_execution(self):
        process = mock.Mock()
        process.wait.return_value = 7
        factory = mock.Mock(return_value=process)
        result = signin.execute_native(["fixture-only", "login"], self.root, 300, popen=factory)
        self.assertEqual(result["native_exit_code"], 7)
        self.assertFalse(result["timed_out"])
        self.assertIsNone(factory.call_args.kwargs["stdout"])
        self.assertIsNone(factory.call_args.kwargs["stderr"])
        process = mock.Mock()
        process.wait.side_effect = [subprocess.TimeoutExpired("fixture", 300), -15]
        process.poll.return_value = None
        process.returncode = -15
        result = signin.execute_native(["fixture-only", "login"], self.root, 300,
                                       popen=mock.Mock(return_value=process))
        self.assertTrue(result["timed_out"])
        self.assertEqual(result["native_exit_code"], -15)
        process.send_signal.assert_called_once()


if __name__ == "__main__":
    unittest.main()
