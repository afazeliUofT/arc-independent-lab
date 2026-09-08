"""Synthetic post-login control checks; no Codex, network or model is launched."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import types
import unittest
from unittest import mock


LAB = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, LAB / "scripts" / (name + ".py"))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


post = load("gate0_postlogin_metadata")
mount = load("gate0_client_mount_plan")


class PostloginControlTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="postlogin016_fixture_", dir=LAB / "delivery")
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name) / "home"
        self.root = self.home / "ARC_Independent_Lab"
        self.codex_home = self.home / ".codex"
        for path in (self.root / "state", self.root / "delivery", self.root / "scripts", self.codex_home):
            path.mkdir(parents=True, exist_ok=True)
        self.patch = mock.patch.object(post, "ROOT", self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.auth = self.codex_home / "auth.json"
        self.auth.write_bytes(b"synthetic nonsecret sentinel; wrapper must not open")
        self.auth.chmod(0o600)
        self.config = self.codex_home / "config.toml"
        self.config.write_text('cli_auth_credentials_store = "file"\n')
        self.runtime = self.codex_home / "runtime_fixture"
        self.runtime.write_bytes(b"not a real runtime")
        self.runtime.chmod(0o755)
        self.bwrap = Path(self.temp.name) / "bwrap_fixture"
        self.bwrap.write_bytes(b"not a real namespace executable")
        self.bwrap.chmod(0o755)
        self.identifier = self.codex_home / "installation_id"
        self.identifier.write_text("00000000-0000-0000-0000-000000000001\n")
        self.identifier.chmod(0o644)
        self.run = self.root / "delivery" / post.RUN_NAME
        self.scope = {
            "approval_id": "APPROVE_G0_POSTLOGIN_016",
            "canonical_home": str(self.home), "canonical_project": str(self.root),
            "runtime_sha256": "runtime-fixture", "bwrap_sha256": "bwrap-fixture",
            "prelogin_report_path": "prelogin.json",
        }
        self.old_origins = [
            {"path": str(self.config), "present": True, "metadata": post.metadata(self.config)},
            {"path": str(self.auth), "present": False},
        ]
        raw = json.dumps({"origin_inventory": self.old_origins}).encode()
        (self.root / "prelogin.json").write_bytes(raw)
        self.scope["prelogin_report_sha256"] = post.sha(raw)
        self.facts = {
            "home": self.home, "codex_home": self.codex_home,
            "runtime": self.runtime, "bwrap": self.bwrap,
            "runtime_before": {"sha256": "runtime-fixture"},
            "bwrap_before": {"sha256": "bwrap-fixture"},
            "identifier": self.identifier, "identifier_bytes": self.identifier.read_bytes(),
            "origins": [self.old_origins[0], {"path": str(self.auth), "present": True,
                                               "metadata": post.metadata(self.auth)}],
            "readonly_paths": [self.config, self.auth],
            "auth": self.auth, "network_inputs": [],
        }

    def write_answer(self, text=None):
        if text is None:
            text = "## ANSWER\n" + self.scope["approval_id"] + "\nscope_sha256: " + post.SCOPE_SHA256 + "\n"
        (self.root / "state/ESCALATION.md").write_text(text)

    def inventory(self):
        preflight = types.SimpleNamespace(inventory=lambda: self.facts)
        with mock.patch.object(post.Path, "home", return_value=self.home), \
             mock.patch.object(post.os, "environ", {"HOME": str(self.home)}), \
             mock.patch.object(post, "exact_network_inputs", return_value=[]):
            return post.inventory(self.scope, preflight)

    def test_only_real_unqualified_answer_authorizes(self):
        answer = "## ANSWER\n" + self.scope["approval_id"] + "\nscope_sha256: " + post.SCOPE_SHA256
        self.write_answer(answer)
        post.approval(self.scope)
        for wrong in ("```text\n" + answer + "\n```", "~~~\n" + answer + "\n~~~",
                      "\n".join("    " + line for line in answer.splitlines()),
                      answer + "\nOnly if no refresh occurs.", answer + "\n" + answer):
            with self.subTest(wrong=wrong):
                self.write_answer(wrong)
                with self.assertRaises(post.Stop):
                    post.approval(self.scope)

    def test_inventory_does_not_open_credential_or_cache_contents(self):
        cache = self.codex_home / "cloud-config-bundle-cache.json"
        cache.write_bytes(b"private synthetic policy metadata")
        original_open = Path.open
        forbidden = {self.auth, cache}
        def guarded_open(path, *args, **kwargs):
            self.assertNotIn(path, forbidden, "Credential or policy cache was opened by parent")
            return original_open(path, *args, **kwargs)
        with mock.patch.object(Path, "open", guarded_open):
            facts = self.inventory()
        self.assertIn(cache, facts["readonly_paths"])
        self.assertEqual(facts["auth"], self.auth)

    def test_auth_symlink_hardlink_and_mode_refusals(self):
        self.auth.chmod(0o644)
        with self.assertRaises(post.Stop):
            self.inventory()
        self.auth.chmod(0o600)
        link = self.codex_home / "synthetic_extra_link"
        os.link(self.auth, link)
        with self.assertRaises(post.Stop):
            self.inventory()
        link.unlink()
        self.auth.rename(link)
        self.auth.symlink_to(link)
        with self.assertRaises(post.Stop):
            self.inventory()

    def test_changed_configuration_origin_refuses(self):
        self.config.write_text('cli_auth_credentials_store = "keyring"\n')
        self.facts["origins"][0] = {"path": str(self.config), "present": True,
                                     "metadata": post.metadata(self.config)}
        with self.assertRaises(post.Stop):
            self.inventory()

    def test_live_plan_writes_only_exact_auth_id_backing_and_fresh_state(self):
        self.run.mkdir()
        for name in ("runtime_state", "runtime_logs"):
            (self.run / name).mkdir()
        copied = self.run / "installation_id_copy"
        copied.write_bytes(self.facts["identifier_bytes"])
        copied.chmod(0o644)
        original_open = Path.open
        def guarded_open(path, *args, **kwargs):
            self.assertNotEqual(path, self.auth, "Credential contents accessed while building plan")
            return original_open(path, *args, **kwargs)
        command = [str(self.runtime), "app-server", "--strict-config", "--stdio"]
        with mock.patch.object(Path, "open", guarded_open):
            plan = post.build_live_plan(self.facts, self.run, command, mount)
        writable = {item["destination"] for item in plan["mounts"] if item["access"] == "write"}
        self.assertEqual(writable, {str(self.auth), str(self.identifier),
                                    str(self.run / "runtime_state"), str(self.run / "runtime_logs")})
        self.assertNotIn(str(self.codex_home), writable)
        self.assertNotIn(str(self.home), writable)
        self.assertEqual(plan["argv"].count("--share-net"), 1)
        self.assertFalse(plan["network_endpoint_allowlist_enforced"])
        self.assertFalse(plan["full_reviewer_boundary_verified"])
        self.assertEqual(plan["argv"][plan["argv"].index("--") + 1:], command)

    def test_unapproved_main_never_enters_run(self):
        self.write_answer("No approval yet.\n")
        with mock.patch.object(post, "load_bundle", return_value=(self.scope, {})), \
             mock.patch.object(post, "module"), mock.patch.object(post, "inventory"), \
             mock.patch.object(post, "run_once") as run_once, \
             mock.patch("sys.argv", ["gate0_postlogin_metadata.py", "--run-metadata"]), \
             contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as result:
                post.main()
            self.assertEqual(result.exception.code, 2)
            run_once.assert_not_called()
        self.assertFalse(self.run.exists())

    def test_default_inspection_never_asks_approval_or_enters_run(self):
        with mock.patch.object(post, "load_bundle", return_value=(self.scope, {})), \
             mock.patch.object(post, "module"), mock.patch.object(post, "inventory"), \
             mock.patch.object(post, "approval") as approval, \
             mock.patch.object(post, "run_once") as run_once, \
             mock.patch("sys.argv", ["gate0_postlogin_metadata.py"]), \
             contextlib.redirect_stdout(io.StringIO()):
            post.main()
            approval.assert_not_called()
            run_once.assert_not_called()
        self.assertFalse(self.run.exists())

    def test_reused_report_precedes_new_inventory_approval_or_run(self):
        # Report-validation specifics are checked separately. This asserts the
        # controlling order after a completed report has already been validated.
        with mock.patch.object(post, "load_bundle", return_value=(self.scope, {})), \
             mock.patch.object(post, "existing", return_value=self.run / "REPORT.json"), \
             mock.patch.object(post, "show"), mock.patch.object(post, "module") as module, \
             mock.patch.object(post, "approval") as approval, \
             mock.patch.object(post, "run_once") as run_once, \
             mock.patch("sys.argv", ["gate0_postlogin_metadata.py", "--run-metadata"]), \
             contextlib.redirect_stdout(io.StringIO()):
            post.main()
            module.assert_not_called()
            approval.assert_not_called()
            run_once.assert_not_called()

    def test_partial_receipt_is_preserved_and_not_retried(self):
        self.run.mkdir()
        attempt = self.run / "ATTEMPT.json"
        attempt.write_text('{"synthetic": true}\n')
        before = attempt.read_bytes()
        with mock.patch.object(post, "load_bundle", return_value=(self.scope, {})), \
             mock.patch.object(post, "run_once") as run_once, \
             mock.patch("sys.argv", ["gate0_postlogin_metadata.py", "--run-metadata"]), \
             contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit):
                post.main()
            run_once.assert_not_called()
        self.assertEqual(attempt.read_bytes(), before)
        self.assertFalse((self.run / "REPORT.json").exists())

    def test_failed_synthetic_boundary_saves_reusable_report_without_native_access(self):
        self.facts.update({"auth_before": post.metadata(self.auth), "cache_origins": [],
                           "identifier_before": {"sha256": "identifier-fixture"}})
        signatures = {self.runtime: self.facts["runtime_before"],
                      self.bwrap: self.facts["bwrap_before"],
                      self.identifier: self.facts["identifier_before"]}
        preflight = types.SimpleNamespace(overrides=lambda run: {}, signature=lambda path: signatures[path])
        boundary = types.SimpleNamespace(check=mock.Mock(return_value={"passed": False}))
        protocol = types.SimpleNamespace(observe=mock.Mock())
        modules = {"gate0_client_mount_plan": mount, "gate0_postlogin_boundary": boundary,
                   "gate0_postlogin_protocol": protocol}
        original_open = Path.open
        def guarded_open(path, *args, **kwargs):
            self.assertNotEqual(path, self.auth, "Parent opened the credential fixture")
            return original_open(path, *args, **kwargs)
        with mock.patch.object(post, "module", side_effect=modules.__getitem__), \
             mock.patch.object(Path, "open", guarded_open):
            path = post.run_once(self.scope, {"synthetic": True}, self.facts, preflight)
        protocol.observe.assert_not_called()
        value = json.loads(path.read_bytes())
        self.assertEqual(set(value), post.REPORT_KEYS)
        self.assertFalse(value["native_credential_refresh_may_have_occurred"])
        self.assertEqual(post.existing(self.run, {"synthetic": True}), path)
        with self.assertRaises(post.Stop):
            post.existing(self.run, {"synthetic": False})
        del value["formal_verdict"]
        raw = (json.dumps(value) + "\n").encode()
        path.write_bytes(raw)
        (self.run / "REPORT.sha256").write_text(post.sha(raw) + "\n")
        with self.assertRaises(post.Stop):
            post.existing(self.run, {"synthetic": True})


if __name__ == "__main__":
    unittest.main()
