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

    def write_prior(self, passed=True):
        """Public synthetic receipt only; no native runtime files involved."""
        path = self.root / "delivery" / post.PRIOR_RUN_NAME / "REPORT.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        prior = {"pins": {"scope_sha256": post.SCOPE_SHA256,
                          "driver_sources": dict(post.DRIVER_PINS)},
                 "synthetic_boundary": {"passed": passed}}
        raw = (json.dumps(prior) + "\n").encode()
        path.write_bytes(raw)
        (path.parent / "REPORT.sha256").write_text(post.sha(raw) + "\n")
        return path, prior, post.sha(raw)

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

    def test_archived_permission_requires_empty_current_request_and_pinned_bytes(self):
        archive = self.root / post.APPROVAL_ARCHIVE
        archive.parent.mkdir(parents=True)
        answer = "## ANSWER\n" + self.scope["approval_id"] + "\nscope_sha256: " + post.SCOPE_SHA256 + "\n"
        archive.write_text(answer)
        with mock.patch.object(post, "APPROVAL_SHA256", post.sha(archive.read_bytes())):
            self.write_answer(" \n\t")
            post.approval(self.scope)
            # A new restriction cannot be bypassed by an earlier valid answer.
            self.write_answer("Do not launch. A new restriction requires review.\n")
            original_open = Path.open
            def guard_archive(path, *args, **kwargs):
                self.assertNotEqual(path, archive, "Nonempty current request was bypassed")
                return original_open(path, *args, **kwargs)
            with mock.patch.object(Path, "open", guard_archive):
                with self.assertRaises(post.Stop):
                    post.approval(self.scope)
            self.write_answer("")
            archive.write_text(answer + "Changed archive.\n")
            with self.assertRaisesRegex(post.Stop, "Archived approval differs"):
                post.approval(self.scope)

    def test_original_local_report_hash_checksum_and_prerequisite_are_guarded(self):
        path, prior, digest = self.write_prior()
        with mock.patch.object(post, "PRIOR_REPORT_SHA256", digest):
            self.assertEqual(post.prior_observation(), (path, prior))
            original = path.read_bytes()
            path.write_bytes(original + b" ")
            with self.assertRaisesRegex(post.Stop, "Original local failed report differs"):
                post.prior_observation()
            self.assertEqual(path.read_bytes(), original + b" ")
            path.write_bytes(original)
            (path.parent / "REPORT.sha256").write_text("0" * 64 + "\n")
            with self.assertRaisesRegex(post.Stop, "Original receipt checksum differs"):
                post.prior_observation()
        for failed in (False, None, 1):
            _, _, digest = self.write_prior(passed=failed)
            with mock.patch.object(post, "PRIOR_REPORT_SHA256", digest):
                with self.assertRaisesRegex(post.Stop, "Accepted prerequisite observation is unavailable"):
                    post.prior_observation()

    def test_load_bundle_guards_archived_failed_report_hash(self):
        self.scope.update({"signin_receipt_path": "signin.json", "signin_receipt_sha256": post.sha(b"{}\n")})
        (self.root / "signin.json").write_bytes(b"{}\n")
        scope_path = self.root / post.SCOPE_PATH
        scope_path.parent.mkdir(parents=True)
        raw = json.dumps(self.scope).encode()
        scope_path.write_bytes(raw)
        driver = self.root / "scripts/synthetic_driver.py"
        driver.write_bytes(b"# synthetic driver never invoked\n")
        (self.root / "scripts/gate0_postlogin_metadata.py").write_bytes(b"# synthetic wrapper source\n")
        archived = self.root / post.PRIOR_REPORT_PATH
        archived.parent.mkdir(parents=True)
        archived.write_bytes(b"{}\n")
        with mock.patch.object(post, "SCOPE_SHA256", post.sha(raw)), \
             mock.patch.object(post, "DRIVER_PINS", {"scripts/synthetic_driver.py": post.sha(driver.read_bytes())}), \
             mock.patch.object(post, "PRIOR_REPORT_SHA256", post.sha(archived.read_bytes())):
            _, pins = post.load_bundle()
            self.assertEqual(pins["prior_failed_report_sha256"], post.sha(b"{}\n"))
            archived.write_bytes(b"{ }\n")
            with self.assertRaisesRegex(post.Stop, "Accepted failed attempt differs"):
                post.load_bundle()

    def test_boundary_reuse_requires_original_driver_and_namespace_identity(self):
        _, prior, _ = self.write_prior()
        facts = {"bwrap_before": {"sha256": "52231e1caf55bcbc667b269f49c63599a6f7db4767ae6a039580d0ff853db712"}}
        reused = post.reuse_boundary(facts, prior)
        self.assertTrue(reused["passed"])
        self.assertFalse(reused["executed_this_attempt"])
        self.assertFalse(reused["fresh_kernel_or_full_reviewer_attestation"])
        for key in ("scripts/gate0_postlogin_boundary.py", "scripts/gate0_client_mount_plan.py"):
            changed = json.loads(json.dumps(prior))
            changed["pins"]["driver_sources"][key] = "different"
            with self.assertRaises(post.Stop):
                post.reuse_boundary(facts, changed)
        with self.assertRaisesRegex(post.Stop, "Namespace executable changed"):
            post.reuse_boundary({"bwrap_before": {"sha256": "different"}}, prior)

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
             mock.patch.object(post, "prior_observation", return_value=(None, {})), \
             mock.patch.object(post, "reuse_boundary", return_value={"passed": True}), \
             mock.patch.object(post, "run_once") as run_once, \
             mock.patch("sys.argv", ["gate0_postlogin_metadata.py", "--run-repaired-metadata"]), \
             contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as result:
                post.main()
            self.assertEqual(result.exception.code, 2)
            run_once.assert_not_called()
        self.assertFalse(self.run.exists())

    def test_default_inspection_never_asks_approval_or_enters_run(self):
        with mock.patch.object(post, "load_bundle", return_value=(self.scope, {})), \
             mock.patch.object(post, "module"), mock.patch.object(post, "inventory"), \
             mock.patch.object(post, "prior_observation", return_value=(None, {})), \
             mock.patch.object(post, "reuse_boundary", return_value={"passed": True}), \
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
             mock.patch.object(post, "inventory") as inventory, \
             mock.patch.object(post, "prior_observation") as prior_observation, \
             mock.patch.object(post, "approval") as approval, \
             mock.patch.object(post, "run_once") as run_once, \
             mock.patch("sys.argv", ["gate0_postlogin_metadata.py", "--run-repaired-metadata"]), \
             contextlib.redirect_stdout(io.StringIO()):
            post.main()
            module.assert_not_called()
            inventory.assert_not_called()
            prior_observation.assert_not_called()
            approval.assert_not_called()
            run_once.assert_not_called()

    def test_legacy_flag_only_shows_original_receipt_without_inventory_or_run(self):
        path, _, digest = self.write_prior()
        original = {p.name: p.read_bytes() for p in path.parent.iterdir()}
        with mock.patch.object(post, "load_bundle", return_value=(self.scope, {})), \
             mock.patch.object(post, "PRIOR_REPORT_SHA256", digest), \
             mock.patch.object(post, "show") as show, \
             mock.patch.object(post, "existing") as existing, \
             mock.patch.object(post, "module") as module, \
             mock.patch.object(post, "inventory") as inventory, \
             mock.patch.object(post, "approval") as approval, \
             mock.patch.object(post, "run_once") as run_once, \
             mock.patch("sys.argv", ["gate0_postlogin_metadata.py", "--run-metadata"]), \
             contextlib.redirect_stdout(io.StringIO()):
            post.main()
        show.assert_called_once_with(path)
        for operation in (existing, module, inventory, approval, run_once):
            operation.assert_not_called()
        self.assertEqual(original, {p.name: p.read_bytes() for p in path.parent.iterdir()})
        self.assertFalse(self.run.exists())

    def test_partial_receipt_is_preserved_and_not_retried(self):
        self.run.mkdir()
        attempt = self.run / "ATTEMPT.json"
        attempt.write_text('{"synthetic": true}\n')
        before = attempt.read_bytes()
        with mock.patch.object(post, "load_bundle", return_value=(self.scope, {})), \
             mock.patch.object(post, "run_once") as run_once, \
             mock.patch("sys.argv", ["gate0_postlogin_metadata.py", "--run-repaired-metadata"]), \
             contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit):
                post.main()
            run_once.assert_not_called()
        self.assertEqual(attempt.read_bytes(), before)
        self.assertFalse((self.run / "REPORT.json").exists())

    def test_unverified_prerequisite_refuses_before_creating_repair_directory(self):
        for boundary in ({"passed": False}, {"passed": 1}, {"passed": None}, {}, None):
            with self.subTest(boundary=boundary), mock.patch.object(post, "module") as module:
                with self.assertRaisesRegex(post.Stop, "Verified prior boundary is required"):
                    post.run_once(self.scope, {}, self.facts, object(), boundary)
                module.assert_not_called()
                self.assertFalse(self.run.exists())

    def test_repair_report_is_reusable_and_preserves_original_attempt_bytes(self):
        original_path, _, _ = self.write_prior()
        original = {p.name: p.read_bytes() for p in original_path.parent.iterdir()}
        self.facts.update({"auth_before": post.metadata(self.auth), "cache_origins": [],
                           "identifier_before": {"sha256": "identifier-fixture"}})
        signatures = {self.runtime: self.facts["runtime_before"],
                      self.bwrap: self.facts["bwrap_before"],
                      self.identifier: self.facts["identifier_before"]}
        preflight = types.SimpleNamespace(overrides=lambda run: {}, signature=lambda path: signatures[path])
        boundary = {"passed": True, "executed_this_attempt": False}
        protocol = types.SimpleNamespace(observe=mock.Mock(return_value={
            "status": "SYNTHETIC_ONLY_NO_NATIVE_LAUNCHED", "client_started": False,
            "thread_or_model_request_sent": False, "requests_sent": [], "responses": []}))
        modules = {"gate0_client_mount_plan": mount, "gate0_postlogin_protocol": protocol,
                   "gate0_account_metadata": object()}
        original_open = Path.open
        def guarded_open(path, *args, **kwargs):
            self.assertNotEqual(path, self.auth, "Parent opened the credential fixture")
            return original_open(path, *args, **kwargs)
        with mock.patch.object(post, "module", side_effect=modules.__getitem__), \
             mock.patch.object(Path, "open", guarded_open):
            path = post.run_once(self.scope, {"synthetic": True}, self.facts, preflight, boundary)
        protocol.observe.assert_called_once()
        value = json.loads(path.read_bytes())
        self.assertEqual(set(value), post.REPORT_KEYS)
        self.assertFalse(value["native_credential_refresh_may_have_occurred"])
        self.assertFalse(value["synthetic_boundary"]["executed_this_attempt"])
        self.assertEqual(original, {p.name: p.read_bytes() for p in original_path.parent.iterdir()})
        created = {p.name: p.read_bytes() for p in self.run.iterdir() if p.is_file()}
        with self.assertRaises(FileExistsError):
            post.run_once(self.scope, {"synthetic": True}, self.facts, preflight, boundary)
        self.assertEqual(created, {p.name: p.read_bytes() for p in self.run.iterdir() if p.is_file()})
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
