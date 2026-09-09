"""Offline safety/correctness tests; synthetic files, zero native/model/network use."""
from __future__ import annotations

import ast
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
import time
import unittest
from unittest import mock

import warning025_fixture_support as f

ROOT = Path(__file__).resolve().parents[1]
PROBE_PATH = ROOT / "scripts/p3_warning_probe_025.py"
SOURCE_REPO = ROOT
TEMP_ROOT = ROOT / "delivery"
TEMP_ROOT.mkdir(exist_ok=True)
SECRET = "PRIVATE_FIXTURE_PAYLOAD_DO_NOT_EXPORT_8e6c07f1"


def load_probe():
    spec = importlib.util.spec_from_file_location("warning025_fixture_module", PROBE_PATH)
    probe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(probe)
    return probe


class ProbeTests(unittest.TestCase):
    def setUp(self):
        self.p = load_probe()
        self.temp = tempfile.TemporaryDirectory(prefix="probe025-test-", dir=TEMP_ROOT)
        self.addCleanup(self.temp.cleanup)
        self.top = Path(self.temp.name)
        self.root = self.top / "ARC_Independent_Lab"

    def fixture(self, *, config=None, cache=None):
        config = config if config is not None else (
            'suppress_unstable_features_warning = false\nunknown_secret = "' + SECRET +
            '"\n[features]\ntranscript_v2 = true\ncode_mode = false\nunknown_feature = "' + SECRET + '"\n').encode()
        cache = cache if cache is not None else f.json_bytes({
            "client_version": "0.151.0", "fetched_at": SECRET, "etag": SECRET,
            "models": [{"slug": "gpt-5.6-sol", "tool_mode": "code_mode_only",
                        "description": SECRET, "used_fallback_model_metadata": True},
                       {"slug": SECRET, "tool_mode": SECRET}]})
        x = f.fixture_report(self.root, config_bytes=config, cache_bytes=cache)
        self.p.REPORT_SHA256 = f.digest(x["report_raw"])
        self.p.SESSION_SHA256 = f.digest(x["session_raw"])
        for name in self.p.SOURCE_PINS:
            dest = self.root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SOURCE_REPO / name, dest)
        self.x = x
        return x

    def safe_result(self, result):
        raw = json.dumps(result, sort_keys=True)
        self.assertTrue(SECRET not in raw, "No fixture secret may be exported")
        self.assertEqual(result["native_processes_started"], 0)
        self.assertEqual(result["model_turns_sent"], 0)
        self.assertEqual(result["network_calls"], 0)
        self.assertFalse(result["credentials_opened"])
        self.assertFalse(result["actual_rejected_warning_identified"])
        self.assertFalse(result["verdict_generated"])
        self.assertIsNone(result["reviewer_verdict"])

    def rewrite_history(self, *, report=None, session=None):
        report = report if report is not None else self.x["report"]
        if session is not None:
            raw = f.json_bytes(session)
            self.x["session_path"].write_bytes(raw)
            self.p.SESSION_SHA256 = f.digest(raw)
            report["preserved_session_receipts"][0]["sha256"] = self.p.SESSION_SHA256
        raw = f.json_bytes(report)
        self.x["report_path"].write_bytes(raw)
        self.p.REPORT_SHA256 = f.digest(raw)

    def test_production_receipt_and_source_pins_are_exact(self):
        self.assertEqual(self.p.REPORT_SHA256, f.EXPECTED_ATTACHED_SHA256)
        self.assertEqual(self.p.SESSION_SHA256, "ca0bcc98b2ba16f4eab396f79e5792deb0af1610d80c77546e1c2a751ad7b02e")
        self.assertTrue(self.p.verify_sources(SOURCE_REPO, time.monotonic() + 10))

    def test_static_no_native_network_sqlite_or_dynamic_execution_surface(self):
        tree = ast.parse(PROBE_PATH.read_text())
        imports = set()
        forbidden_calls = {"eval", "exec", "compile", "__import__"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.add((node.module or "").split(".")[0])
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                self.assertTrue(node.func.id not in forbidden_calls)
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                self.assertTrue(node.func.attr not in {"system", "popen", "spawnv", "spawnve", "execv", "execve", "fork"})
        self.assertFalse(imports & {"subprocess", "socket", "sqlite3", "requests", "urllib", "http", "ctypes"})

    def test_missing_logs_still_produce_persisted_receipt(self):
        self.fixture()
        result = self.p.collect(self.root)
        self.safe_result(result)
        self.assertEqual(result["status"], "OFFLINE_DIAGNOSTIC_COMPLETE_NO_VERDICT")
        for row in result["logs"].values():
            self.assertEqual(row["error_type"], "FileNotFoundError")
        target = self.p.write_receipt(self.root, result)
        self.assertEqual(json.loads(target.read_bytes()), result)
        self.assertEqual(target.stat().st_mode & 0o777, 0o400)

    def test_bad_report_digest_stops_before_session_logs_config_cache(self):
        self.fixture()
        self.x["report_path"].write_bytes(self.x["report_raw"] + b" ")
        with mock.patch.object(self.p, "scan_log", side_effect=AssertionError("must not scan")), \
             mock.patch.object(self.p, "inspect_config", side_effect=AssertionError("must not open config")), \
             mock.patch.object(self.p, "inspect_cache", side_effect=AssertionError("must not open cache")):
            result = self.p.collect(self.root)
        self.safe_result(result)
        self.assertEqual(result["error_type"], "HistoricalReceiptMismatch")
        self.assertFalse(result["canonical024_report_verified"])

    def test_missing_session_is_not_reconstructed_from_report(self):
        self.fixture()
        self.x["session_path"].unlink()
        result = self.p.collect(self.root)
        self.safe_result(result)
        self.assertFalse(result["canonical024_session_verified"])
        self.assertEqual(result["error_type"], "FileNotFoundError")
        self.assertNotIn("logs", result)
        target = self.p.write_receipt(self.root, result)
        self.assertTrue(target.exists())
        self.assertFalse(self.x["session_path"].exists())

    def test_valid_digest_cannot_hide_report_session_observation_mismatch(self):
        self.fixture()
        changed = dict(self.x["report"]["stages"][0]["observation"])
        changed["observed_refusal"] = True
        self.rewrite_history(session=changed)
        result = self.p.collect(self.root)
        self.safe_result(result)
        self.assertEqual(result["error_type"], "HistoricalReceiptMismatch")

    def test_source_pin_failure_prevents_config_cache_read(self):
        self.fixture()
        source = self.root / next(iter(self.p.SOURCE_PINS))
        source.write_bytes(source.read_bytes() + b" ")
        with mock.patch.object(self.p, "inspect_config", side_effect=AssertionError("must not open config")), \
             mock.patch.object(self.p, "inspect_cache", side_effect=AssertionError("must not open cache")):
            result = self.p.collect(self.root)
        self.safe_result(result)
        self.assertEqual(result["source_schema_error_type"], "SourcePinMismatch")
        self.assertEqual(result["config"]["status"], "not_opened_source_pins_unverified")

    def test_only_two_approved_nonsecret_host_files_are_opened_and_nothing_mutates(self):
        self.fixture()
        codex = self.root.parent / ".codex"
        for name in ("auth.json", ".env", "installation_id", "cloud-config-bundle-cache.json"):
            (codex / name).write_text(SECRET)
        log = self.x["native"] / "runtime_state/logs_2.sqlite"
        log.write_bytes(b"SQLite format 3\0" + SECRET.encode() + b" app-server event: warning")
        paths = [path for path in self.top.rglob("*") if path.is_file()]
        before = f.snapshot(paths)
        open_fn = os.open
        fd_paths = {}
        opened_files = []

        def checked_open(path, flags, *args, **kwargs):
            incoming = Path(path)
            resolved = incoming if incoming.is_absolute() else fd_paths[kwargs["dir_fd"]] / incoming
            if resolved.parent == codex and not flags & os.O_DIRECTORY:
                self.assertTrue(resolved.name in {"config.toml", "models_cache.json"}, "Unapproved host input open")
                opened_files.append(resolved.name)
            fd = open_fn(path, flags, *args, **kwargs)
            fd_paths[fd] = resolved
            return fd

        with mock.patch.object(self.p.os, "open", side_effect=checked_open):
            result = self.p.collect(self.root)
        self.safe_result(result)
        self.assertEqual(set(opened_files), {"config.toml", "models_cache.json"})
        self.assertTrue(before == f.snapshot(paths), "collect must preserve all source bytes and metadata")
        self.assertEqual(set(paths), {path for path in self.top.rglob("*") if path.is_file()})

    def test_metadata_change_blocks_content_read_before_read_syscall(self):
        self.fixture()
        path = self.x["selected"]["config.toml"]
        path.write_bytes(path.read_bytes() + b"# changed\n")
        with mock.patch.object(self.p.os, "read", side_effect=AssertionError("changed source must not be read")):
            result = self.p.inspect_config(self.root, self.x["report"]["stages"][0], time.monotonic() + 10)
        self.assertEqual(result["error_type"], "MetadataChanged")
        self.assertFalse(result["metadata_matches_024"])

    def test_report_cannot_redirect_fixed_config_path(self):
        self.fixture()
        other = self.root.parent / "different-private-input.toml"
        other.write_text(SECRET)
        row = next(row for row in self.x["report"]["stages"][0]["config_origins"]
                   if row.get("path") == str(self.x["selected"]["config.toml"]))
        row["path"] = str(other)
        self.rewrite_history()
        result = self.p.collect(self.root)
        self.safe_result(result)
        self.assertEqual(result["config"]["error_type"], "HistoricalReceiptMismatch")

    def test_config_and_cache_redact_values_and_do_not_attest_effective_state(self):
        self.fixture()
        result = self.p.collect(self.root)
        self.safe_result(result)
        self.assertEqual(result["config"]["known_features"]["transcript_v2"], "true")
        self.assertEqual(result["config"]["known_features"]["code_mode"], "false")
        self.assertFalse(result["config"]["effective_runtime_features_reconstructed"])
        self.assertFalse(result["config"]["predicted_actual_warning"])
        self.assertEqual(result["cache"]["tool_mode"], "code_mode_only")
        self.assertFalse(result["cache"]["actual024_internal_model_info_verified"])
        self.assertEqual(result["cache"]["serialized_fallback_marker"], "present_but_ignored_by_native_deserializer")

    def test_hashing_is_limited_to_receipts_and_pinned_sources(self):
        self.fixture()
        allowed = {self.x["report_raw"], self.x["session_raw"]}
        allowed.update((self.root / name).read_bytes() for name in self.p.SOURCE_PINS)
        original = self.p.hashlib.sha256
        observed = []

        def checked_sha(raw=b"", *args, **kwargs):
            observed.append(bytes(raw))
            self.assertTrue(bytes(raw) in allowed, "Unexpected input supplied to hashing")
            return original(raw, *args, **kwargs)

        with mock.patch.object(self.p.hashlib, "sha256", side_effect=checked_sha):
            result = self.p.collect(self.root)
        self.safe_result(result)
        self.assertEqual(len(observed), 2 + len(self.p.SOURCE_PINS))

    def test_config_known_boolean_shapes_follow_pinned_schema(self):
        self.fixture(config=b'suppress_unstable_features_warning = { enabled = true }\n'
                            b'[features]\ntranscript_v2 = { enabled = true }\n'
                            b'code_mode = { enabled = false }\nartifact = true\n')
        result = self.p.collect(self.root)
        self.safe_result(result)
        config = result["config"]
        self.assertEqual(config["suppress_unstable_features_warning"], "not_a_supported_boolean")
        self.assertEqual(config["known_features"]["transcript_v2"], "not_a_supported_boolean")
        self.assertEqual(config["known_features"]["code_mode"], "false")
        self.assertEqual(config["known_features"]["artifact"], "not_advertised_by_pinned_config_schema")
        self.assertFalse(config["full_config_schema_validated"])

    def test_db_wal_fragments_are_non_authoritative_and_chunk_boundary_match_is_found_once(self):
        self.fixture()
        needle = self.p.LOG_MARKERS["fallback_model_metadata_producer"]
        db = self.x["native"] / "runtime_state/logs_2.sqlite"
        wal = db.with_name(db.name + "-wal")
        db.write_bytes(b"x" * (self.p.CHUNK - 7) + needle + SECRET.encode())
        wal.write_bytes(b"uncommitted deleted page " + needle + b" " + SECRET.encode())
        result = self.p.collect(self.root)
        self.safe_result(result)
        for name in ("database", "wal"):
            self.assertEqual(result["logs"][name]["candidate_literal_counts"]["fallback_model_metadata_producer"], 1)
            self.assertFalse(result["logs"][name]["actual_rejected_warning_identified"])
        self.assertTrue(result["interpretation"]["wal_presence_does_not_make_binary_scan_a_committed_snapshot"])
        self.assertTrue(result["interpretation"]["binary_data_may_be_stale_deleted_uncommitted_or_partial"])
        self.assertTrue(result["interpretation"]["no_match_does_not_exclude_any_warning_family"])

    def test_scan_byte_and_count_caps(self):
        path = self.top / "fixture.sqlite"
        needle = self.p.LOG_MARKERS["generic_warning_method_only"]
        path.write_bytes((needle + b"\n") * 250)
        self.p.LOG_SCAN_LIMIT = len(needle + b"\n") * 150
        result = self.p.scan_log(path, time.monotonic() + 10)
        self.assertEqual(result["candidate_literal_counts"]["generic_warning_method_only"], 100)
        self.assertEqual(result["bytes_scanned"], self.p.LOG_SCAN_LIMIT)
        self.assertFalse(result["scan_complete_within_byte_bound"])
        self.assertFalse(result["actual_rejected_warning_identified"])

    def test_symlink_leaf_parent_hardlink_fifo_and_relative_paths_refused(self):
        original = self.top / "original"
        original.write_text(SECRET)
        link = self.top / "leaf"
        link.symlink_to(original)
        directory = self.top / "real"
        directory.mkdir()
        (directory / "inside").write_text(SECRET)
        parent_link = self.top / "parent"
        parent_link.symlink_to(directory, target_is_directory=True)
        hard = self.top / "hard"
        os.link(original, hard)
        fifo = self.top / "fifo"
        os.mkfifo(fifo)
        for path in (link, parent_link / "inside", hard, fifo, Path("relative"), self.top / ".." / "elsewhere"):
            with self.subTest(kind=path.name):
                result = self.p.scan_log(path, time.monotonic() + 10)
                self.assertEqual(result["status"], "unavailable_or_partial")
                self.assertEqual(result["bytes_scanned"], 0)
                self.assertTrue(SECRET not in json.dumps(result))

    def test_report_parent_symlink_refused_before_other_inputs(self):
        self.fixture()
        run = self.root / self.p.RUN_REL
        renamed = run.with_name("real-existing-run")
        run.rename(renamed)
        run.symlink_to(renamed, target_is_directory=True)
        result = self.p.collect(self.root)
        self.safe_result(result)
        self.assertFalse(result["canonical024_report_verified"])
        self.assertNotIn("logs", result)

    def test_repeated_receipts_never_overwrite_prior_receipt(self):
        self.fixture()
        result = self.p.collect(self.root)
        first = self.p.write_receipt(self.root, result)
        before = f.snapshot([first])
        second = self.p.write_receipt(self.root, result)
        self.assertNotEqual(first, second)
        self.assertTrue(before == f.snapshot([first]), "First receipt must remain immutable")
        self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_output_symlink_refuses_without_touching_target(self):
        self.fixture()
        other = self.top / "outside-output"
        other.mkdir()
        sentinel = other / "REPORT.json"
        sentinel.write_text(SECRET)
        (self.root / self.p.OUTPUT_REL).symlink_to(other, target_is_directory=True)
        before = f.snapshot([sentinel])
        with self.assertRaises(OSError):
            self.p.write_receipt(self.root, self.p.collect(self.root))
        self.assertTrue(before == f.snapshot([sentinel]))
        self.assertEqual(list(other.iterdir()), [sentinel])

    def test_receipt_publication_failure_never_exposes_partial_report(self):
        self.fixture()
        result = self.p.collect(self.root)
        with mock.patch.object(self.p.os, "link", side_effect=OSError(SECRET)):
            with self.assertRaises(OSError):
                self.p.write_receipt(self.root, result)
        reports = list((self.root / self.p.OUTPUT_REL).rglob("REPORT.json"))
        self.assertEqual(reports, [])

    def test_strict_json_rejects_duplicate_nonfinite_deep_and_malformed_config_without_leak(self):
        for raw in (b'{"a":1,"a":2}', b'{"a":NaN}', b'{"a":Infinity}', b"[" * 55 + b"0" + b"]" * 55):
            with self.assertRaises((self.p.InvalidStructure, self.p.BoundExceeded)):
                self.p.strict_json(raw)
        self.fixture(config=("[" + SECRET).encode(), cache=("{" + SECRET).encode())
        result = self.p.collect(self.root)
        self.safe_result(result)
        self.assertEqual(result["config"]["status"], "unavailable")
        self.assertEqual(result["cache"]["status"], "unavailable")

    def test_main_receipt_on_missing_history_and_no_arbitrary_cli_paths(self):
        (self.root / "delivery").mkdir(parents=True)
        output = io.StringIO()
        with mock.patch.object(self.p.Path, "home", return_value=self.top), \
             mock.patch.object(self.p.sys, "argv", ["p3_warning_probe_025.py"]), \
             contextlib.redirect_stdout(output):
            status = self.p.main()
        printed = json.loads(output.getvalue())
        self.assertEqual(status, 1)
        saved = self.root / printed["report"]
        self.assertTrue(saved.exists())
        self.safe_result(json.loads(saved.read_bytes()))
        output = io.StringIO()
        with mock.patch.object(self.p.sys, "argv", ["probe.py", "--project-root", SECRET]), \
             mock.patch.object(self.p, "collect", side_effect=AssertionError("must not collect")), \
             contextlib.redirect_stdout(output):
            status = self.p.main()
        self.assertEqual(status, 2)
        self.assertTrue(SECRET not in output.getvalue())


if __name__ == "__main__":
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ProbeTests)
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    work = ROOT / "artifacts/P3_WARNING_DIAGNOSTIC_VALIDATION/20260909_025"
    work.mkdir(parents=True, exist_ok=True)
    (work / "WARNING_PROBE_TEST_OUTPUT.txt").write_text(stream.getvalue())
    report = {"kind": "P3_WARNING_PROBE_025_ENGINEERING_VALIDATION_v1",
              "tests_run": result.testsRun, "failures": len(result.failures),
              "errors": len(result.errors), "successful": result.wasSuccessful(),
              "native_processes_auth_operations_model_turns_network_calls": 0,
              "science_or_controller_modified": False,
              "tests_use_synthetic_local_fixture_pins_only": True,
              "production_probe_sha256": f.digest(PROBE_PATH.read_bytes())}
    (work / "WARNING_PROBE_TEST_REPORT.json").write_bytes(f.json_bytes(report))
    print(json.dumps(report, indent=2))
    if not result.wasSuccessful():
        print(stream.getvalue())
    raise SystemExit(0 if result.wasSuccessful() else 1)
