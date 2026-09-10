"""Synthetic Linux cache tests; no native client, real caches or credentials."""
from __future__ import annotations

import copy
import errno
import fcntl
import hashlib
import importlib.util
import json
import mmap
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("cache030", ROOT / "scripts/p3_cache_inputs_030.py")
cache = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cache)


class CacheInputTests(unittest.TestCase):
    def setUp(self):
        (ROOT / "delivery").mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="cache030_fixture_", dir=ROOT / "delivery")
        self.home = Path(self.temp.name) / ".codex"
        self.home.mkdir(mode=0o700)
        self.auth = self.home / "auth.json"
        self.auth.write_bytes(b"SYNTHETIC CREDENTIAL SENTINEL")
        self.auth_metadata = {"device": self.auth.stat().st_dev, "inode": self.auth.stat().st_ino}
        self.path = self.home / "models_cache.json"
        self.raw = b'{"models":[],"fetched_at":"fixture-only"}\r\n'
        self.path.write_bytes(self.raw)
        self.path.chmod(0o640)

    def capture(self):
        return cache.capture_cache_inputs(self.home, auth_metadata=self.auth_metadata)

    def tearDown(self):
        self.temp.cleanup()

    def test_exact_bytes_mode_and_original_lookup_destination(self):
        with self.capture() as item:
            fd, = item.pass_fds
            self.assertEqual(os.pread(fd, 1024, 0), self.raw)
            record = item.receipt()["inputs"]["models_cache.json"]
            self.assertEqual(record["sha256"], hashlib.sha256(self.raw).hexdigest())
            self.assertEqual(record["source_before"]["metadata"]["mode"], 0o640)
            self.assertEqual(item.mount_args(), ["--perms", "0640", "--ro-bind-data", str(fd), str(self.path)])
            self.assertTrue(item.verify()["all_inputs_intact"])
            self.assertNotIn(self.raw.decode(), json.dumps(item.receipt()))

    def test_kernel_seals_refuse_write_resize_shared_map_and_further_seals(self):
        with self.capture() as item:
            fd, = item.pass_fds
            self.assertEqual(fcntl.fcntl(fd, cache.F_GET_SEALS), cache.SEALS)
            actions = [lambda: os.pwrite(fd, b"x", 0),
                       lambda: os.ftruncate(fd, 0),
                       lambda: os.ftruncate(fd, len(self.raw) + 1),
                       lambda: mmap.mmap(fd, len(self.raw), flags=mmap.MAP_SHARED,
                                         prot=mmap.PROT_READ | mmap.PROT_WRITE),
                       lambda: fcntl.fcntl(fd, cache.F_ADD_SEALS, cache.F_SEAL_WRITE)]
            for action in actions:
                with self.subTest(action=actions.index(action)):
                    with self.assertRaises(OSError) as stopped:
                        action()
                    self.assertEqual(stopped.exception.errno, errno.EPERM)
            self.assertTrue(item.verify()["all_inputs_intact"])

    def test_concurrent_same_inode_writer_after_capture_cannot_change_snapshot(self):
        with self.capture() as item:
            inode = self.path.stat().st_ino
            failures = []
            def writer():
                try:
                    for _ in range(100):
                        self.path.write_bytes(b"changed fixture " * 500)
                except BaseException as error:
                    failures.append(error)
            worker = threading.Thread(target=writer)
            worker.start()
            for _ in range(100):
                self.assertTrue(item.verify()["all_inputs_intact"])
            worker.join(5)
            self.assertFalse(worker.is_alive())
            self.assertFalse(failures)
            self.assertEqual(self.path.stat().st_ino, inode)
            observations = item.observe_sources()
            self.assertEqual(len(observations), 2)
            self.assertIn("bytes", observations[1]["changed_fields"])
            self.assertFalse(observations[1]["writer_identified"])
            self.assertFalse(observations[1]["sealed_input_invalidated_by_source_change"])

    def test_concurrent_atomic_replacement_after_capture_keeps_snapshot(self):
        with self.capture() as item:
            replacement = self.home / "synthetic_replacement"
            replacement.write_bytes(b"replacement fixture")
            worker = threading.Thread(target=lambda: os.replace(replacement, self.path))
            worker.start()
            worker.join(5)
            self.assertFalse(worker.is_alive())
            self.assertTrue(item.verify()["all_inputs_intact"])
            self.assertIn("inode", item.observe_sources()[1]["changed_fields"])

    def _change_during_first_read(self, operation):
        ready, changed = threading.Event(), threading.Event()
        original = cache._read_bounded
        count = 0
        failures = []
        def wrapped(fd):
            nonlocal count
            raw = original(fd)
            count += 1
            if count == 1:
                ready.set()
                if not changed.wait(5):
                    raise AssertionError("Synthetic concurrent writer timed out")
            return raw
        def writer():
            try:
                if not ready.wait(5):
                    raise AssertionError("Capture did not reach read")
                operation()
            except BaseException as error:
                failures.append(error)
            finally:
                changed.set()
        worker = threading.Thread(target=writer)
        worker.start()
        try:
            with mock.patch.object(cache, "_read_bounded", side_effect=wrapped):
                with self.assertRaises(cache.CacheInputError):
                    self.capture()
        finally:
            ready.set()
            worker.join(5)
        self.assertFalse(worker.is_alive())
        self.assertFalse(failures)

    def test_same_inode_write_during_capture_refused(self):
        self._change_during_first_read(lambda: self.path.write_bytes(b"x" * len(self.raw)))

    def test_atomic_rename_during_capture_refused(self):
        replacement = self.home / "synthetic_replacement"
        replacement.write_bytes(self.raw)
        self._change_during_first_read(lambda: os.replace(replacement, self.path))

    def test_absent_path_created_during_capture_refused(self):
        cloud = self.home / "cloud-config-bundle-cache.json"
        self._change_during_first_read(lambda: cloud.write_bytes(b"{}"))

    def test_absent_cache_remains_absent_in_plan_after_host_creation(self):
        with self.capture() as item:
            cloud = self.home / "cloud-config-bundle-cache.json"
            cloud.write_bytes(b"{}")
            self.assertNotIn(str(cloud), item.mount_args())
            self.assertEqual(item.observe_sources()[0]["changed_fields"], ["present"])
            self.assertTrue(item.verify()["all_inputs_intact"])

    def test_credentials_are_not_opened_or_hashed(self):
        # The only auth file here is an explicit synthetic sentinel fixture.
        auth = self.home / "auth.json"
        auth.write_bytes(b"SYNTHETIC SENTINEL NOT AN ACTUAL CREDENTIAL")
        opened = []
        original = os.open
        def traced(name, *args, **kwargs):
            opened.append(os.fspath(name))
            self.assertNotEqual(os.fspath(name), "auth.json")
            self.assertNotEqual(os.fspath(name), str(auth))
            return original(name, *args, **kwargs)
        with mock.patch.object(cache.os, "open", side_effect=traced):
            with self.capture() as item:
                item.observe_sources()
        self.assertIn("models_cache.json", opened)
        self.assertNotIn("auth.json", opened)
        with self.assertRaises(cache.CacheInputError):
            cache._observe(-1, "auth.json")

    def test_symlink_to_auth_refused_without_opening_target(self):
        self.path.unlink()
        self.path.symlink_to("auth.json")
        with self.assertRaises(cache.CacheInputError):
            self.capture()

    def test_auth_inode_alias_refused_before_cache_content_open(self):
        # Explicit metadata simulation: the candidate inode is declared to be
        # the existing auth inode, despite being a single-link regular fixture.
        forbidden = {"device": self.path.stat().st_dev, "inode": self.path.stat().st_ino}
        original = os.open
        def deny_candidate(name, *args, **kwargs):
            self.assertNotEqual(os.fspath(name), "models_cache.json")
            return original(name, *args, **kwargs)
        with mock.patch.object(cache.os, "open", side_effect=deny_candidate):
            with self.assertRaisesRegex(cache.CacheInputError, "credential_inode_alias_refused"):
                cache.capture_cache_inputs(self.home, auth_metadata=forbidden)

    def test_hardlink_and_nonregular_file_refused(self):
        os.link(self.path, self.home / "synthetic_hardlink")
        with self.assertRaises(cache.CacheInputError):
            self.capture()
        self.path.unlink()
        os.mkfifo(self.path)
        with self.assertRaises(cache.CacheInputError):
            self.capture()

    def test_symlinked_ancestor_and_noncanonical_home_refused(self):
        alias = Path(self.temp.name) / "alias"
        alias.symlink_to(self.home, target_is_directory=True)
        with self.assertRaises(cache.CacheInputError):
            cache.capture_cache_inputs(alias, auth_metadata=self.auth_metadata)
        nested = Path(self.temp.name) / "nested"
        nested.mkdir()
        (nested / ".codex").symlink_to(self.home, target_is_directory=True)
        with self.assertRaises(OSError):
            cache.capture_cache_inputs(nested / ".codex", auth_metadata=self.auth_metadata)
        with self.assertRaises(cache.CacheInputError):
            cache.capture_cache_inputs(str(self.home) + "/../.codex", auth_metadata=self.auth_metadata)

    def test_empty_oversized_and_shared_write_permissions_refused(self):
        for size, mode in [(0, 0o600), (cache.MAX_CACHE_BYTES + 1, 0o600), (10, 0o666)]:
            with self.subTest(size=size, mode=mode):
                self.path.write_bytes(b"x" * size)
                self.path.chmod(mode)
                with self.assertRaises(cache.CacheInputError):
                    self.capture()

    def test_created_memfd_closed_when_sealing_fails(self):
        created = []
        original_create, original_fcntl = os.memfd_create, fcntl.fcntl
        def remember(*args):
            fd = original_create(*args)
            created.append(fd)
            return fd
        def refuse(fd, operation, *args):
            if operation == cache.F_ADD_SEALS:
                raise OSError(errno.EPERM, "synthetic sealing refusal")
            return original_fcntl(fd, operation, *args)
        with mock.patch.object(cache.os, "memfd_create", side_effect=remember), \
             mock.patch.object(cache.fcntl, "fcntl", side_effect=refuse):
            with self.assertRaises(OSError):
                self.capture()
        self.assertEqual(len(created), 1)
        with self.assertRaises(OSError):
            os.fstat(created[0])

    def test_first_snapshot_closed_if_second_cache_fails(self):
        cloud = self.home / "cloud-config-bundle-cache.json"
        cloud.write_bytes(b"{}")
        self.path.chmod(0o666)
        created = []
        original = os.memfd_create
        def remember(*args):
            fd = original(*args)
            created.append(fd)
            return fd
        with mock.patch.object(cache.os, "memfd_create", side_effect=remember):
            with self.assertRaises(cache.CacheInputError):
                self.capture()
        self.assertEqual(len(created), 1)
        for fd in created:
            with self.assertRaises(OSError):
                os.fstat(fd)

    def test_explicit_pass_fds_survives_exec_and_context_closes_after_failure(self):
        with self.capture() as item:
            fd, = item.pass_fds
            code = "import hashlib,os,sys;print(hashlib.sha256(os.pread(int(sys.argv[1]),1000,0)).hexdigest())"
            result = subprocess.run([sys.executable, "-I", "-c", code, str(fd)],
                                    pass_fds=item.pass_fds, close_fds=True,
                                    capture_output=True, timeout=5, check=True)
            self.assertEqual(result.stdout.decode().strip(), hashlib.sha256(self.raw).hexdigest())
            omitted = subprocess.run([sys.executable, "-I", "-c", code, str(fd)],
                                     close_fds=True, capture_output=True, timeout=5)
            self.assertNotEqual(omitted.returncode, 0)
        with self.assertRaises(OSError):
            os.fstat(fd)
        with self.assertRaises(FileNotFoundError):
            with self.capture() as failed:
                failed_fd, = failed.pass_fds
                subprocess.Popen([str(Path(self.temp.name) / "does-not-exist")],
                                 pass_fds=failed.pass_fds, close_fds=True)
        with self.assertRaises(OSError):
            os.fstat(failed_fd)

    def _plan(self):
        auth = str(self.home / "auth.json")
        config = str(self.home / "config.toml")
        return {"kind": "fixture-approved-plan", "argv": ["/usr/bin/bwrap",
                "--tmpfs", "/", "--ro-bind", config, config,
                "--ro-bind", str(self.path), str(self.path),
                "--bind", auth, auth, "--remount-ro", "/", "--cap-drop", "ALL",
                "--", "/fixture/runtime", "app-server", "--strict-config", "--stdio"],
                "mounts": [{"source": config, "destination": config, "access": "read"},
                           {"source": str(self.path), "destination": str(self.path), "access": "read"},
                           {"source": auth, "destination": auth, "access": "write",
                            "kind": "approved_native_existing_credential_refresh_only"}],
                "other_policy": {"unchanged": True}}

    def test_transform_preserves_every_noncache_argument_and_mount(self):
        plan = self._plan()
        original = copy.deepcopy(plan)
        with self.capture() as item:
            changed = item.apply_to_plan(plan)
            expected = plan["argv"].copy()
            begin = expected.index(str(self.path)) - 1
            del expected[begin:begin + 3]
            where = expected.index("--remount-ro")
            expected[where:where] = item.mount_args()
            self.assertEqual(changed["argv"], expected)
            self.assertEqual(changed["mounts"][:2], [plan["mounts"][0], plan["mounts"][2]])
            self.assertEqual(changed["other_policy"], plan["other_policy"])
            self.assertEqual(plan, original)

    def test_transform_refuses_duplicate_missing_writable_or_new_absent_cache_grants(self):
        with self.capture() as item:
            for mutation in ["duplicate", "missing", "write", "new_absent"]:
                with self.subTest(mutation=mutation):
                    plan = self._plan()
                    if mutation == "duplicate":
                        plan["argv"][1:1] = ["--ro-bind", str(self.path), str(self.path)]
                    elif mutation == "missing":
                        begin = plan["argv"].index(str(self.path)) - 1
                        del plan["argv"][begin:begin + 3]
                    elif mutation == "write":
                        plan["argv"][plan["argv"].index(str(self.path)) - 1] = "--bind"
                    else:
                        absent = str(self.home / "cloud-config-bundle-cache.json")
                        plan["argv"][1:1] = ["--ro-bind", absent, absent]
                    with self.assertRaises(cache.CacheInputError):
                        item.apply_to_plan(plan)

    def test_origin_inventory_verified_and_descriptor_numbers_redacted(self):
        with self.capture() as item:
            keys = {"device", "inode", "bytes", "mode", "mtime_ns", "ctime_ns"}
            origins = []
            for name, record in item.receipt()["inputs"].items():
                before = record["source_before"]
                row = {"path": str(self.home / name), "present": before["present"]}
                if before["present"]:
                    row["metadata"] = {key: before["metadata"][key] for key in keys}
                origins.append(row)
            self.assertTrue(item.verify_origins(origins))
            origins[1]["metadata"]["inode"] += 1
            with self.assertRaises(cache.CacheInputError):
                item.verify_origins(origins)
            plan = item.apply_to_plan(self._plan())
            safe = item.report_plan(plan)
            where = safe["argv"].index("--ro-bind-data")
            self.assertEqual(safe["argv"][where + 1], "LIVE_SEALED_CACHE_FD_NOT_REPLAYABLE")
            self.assertFalse(safe["replayable"])
            self.assertNotEqual(plan["argv"][where + 1], safe["argv"][where + 1])

    def test_source_observation_reports_both_paths_after_multiple_changes(self):
        with self.capture() as item:
            (self.home / "cloud-config-bundle-cache.json").write_bytes(b"{}")
            self.path.unlink()
            observed = item.observe_sources()
            self.assertEqual(len(observed), 2)
            self.assertEqual([row["changed_fields"] for row in observed], [["present"], ["present"]])
            self.assertTrue(item.verify()["all_inputs_intact"])

    def test_mount_preflight_pass_requires_every_observed_child_check(self):
        keys = {"exact_snapshot_bytes", "absent_cache_stays_absent",
                "synthetic_auth_not_mounted", "snapshot_write_refused",
                "snapshot_truncate_refused", "absent_cache_creation_refused"}
        def fake_process(argv, pass_fds):
            # This is a mocked integration-shape test, not a kernel mount test.
            self.assertIn("--ro-bind-data", argv)
            self.assertIn("--unshare-all", argv)
            self.assertNotIn("--share-net", argv)
            self.assertEqual(len(pass_fds), 1)
            fd, = pass_fds
            self.assertEqual(fcntl.fcntl(fd, cache.F_GET_SEALS), cache.SEALS)
            result = subprocess.CompletedProcess(argv, 0, json.dumps(dict.fromkeys(keys, True)).encode(), b"")
            result.synthetic_diagnostic = {"failure_code": None, "direct_child_reaped": True,
                                           "process_group_absent_after_cleanup": True}
            return result
        with mock.patch.object(cache, "_run_synthetic_child", side_effect=fake_process):
            receipt = cache.probe_sealed_mount("/usr/bin/bwrap", ROOT / "delivery")
        self.assertEqual(receipt["status"], "PASSED")
        self.assertEqual(receipt["native_clients_started"], 0)
        for output in [dict.fromkeys(keys, False), {"invented": True}]:
            mocked = subprocess.CompletedProcess([], 0, json.dumps(output).encode(), b"")
            mocked.synthetic_diagnostic = {"failure_code": None, "direct_child_reaped": True,
                                           "process_group_absent_after_cleanup": True}
            with mock.patch.object(cache, "_run_synthetic_child", return_value=mocked):
                refused = cache.probe_sealed_mount("/usr/bin/bwrap", ROOT / "delivery")
            self.assertEqual(refused["status"], "FAILED")

    def test_mount_preflight_denial_is_unverified_without_a_fallback(self):
        with mock.patch.object(cache, "_run_synthetic_child", return_value=
                subprocess.CompletedProcess([], 1, b"", b"synthetic namespace unavailable")) as process:
            result = cache.probe_sealed_mount("/usr/bin/bwrap", ROOT / "delivery")
        self.assertEqual(process.call_count, 1)
        self.assertEqual(result["status"], "UNVERIFIED")
        self.assertFalse(result["kernel_child_mount_verified"])
        self.assertNotIn("synthetic namespace unavailable", json.dumps(result))

    def test_actual_synthetic_child_output_ceiling_and_deadline_reap(self):
        original = subprocess.Popen
        created = []
        def remember(*args, **kwargs):
            self.assertTrue(kwargs["start_new_session"])
            process = original(*args, **kwargs)
            created.append(process)
            return process
        with mock.patch.object(cache.subprocess, "Popen", side_effect=remember):
            result = cache._run_synthetic_child([sys.executable, "-I", "-c",
                                            "import os;os.write(1,b'x'*20000)"], ())
            self.assertEqual(result.synthetic_diagnostic["failure_code"], "synthetic_mount_output_limit")
            self.assertTrue(result.synthetic_diagnostic["stdout_truncated"])
        self.assertIsNotNone(created[-1].poll())

        started = time.monotonic()
        with mock.patch.object(cache.subprocess, "Popen", side_effect=remember), \
             mock.patch.object(cache, "PROBE_ACTIVE_SECONDS", 0.05), \
             mock.patch.object(cache, "PROBE_CLEANUP_SECONDS", 1):
            result = cache._run_synthetic_child([sys.executable, "-I", "-c",
                                            "import time;time.sleep(30)"], ())
            self.assertEqual(result.synthetic_diagnostic["failure_code"], "synthetic_mount_deadline")
            self.assertTrue(result.synthetic_diagnostic["direct_child_reaped"])
            self.assertTrue(result.synthetic_diagnostic["process_group_absent_after_cleanup"])
        self.assertLess(time.monotonic() - started, 2)
        self.assertIsNotNone(created[-1].poll())

    def test_actual_synthetic_stderr_is_bounded_retained_and_labeled(self):
        result = cache._run_synthetic_child([sys.executable, "-I", "-c",
                    "import os;os.write(2,b'SYNTHETIC-ONLY-DIAGNOSTIC'*1000)"], ())
        diagnostic = result.synthetic_diagnostic
        self.assertEqual(diagnostic["kind"], "synthetic_mount_diagnostic")
        self.assertTrue(diagnostic["stderr_truncated"])
        self.assertEqual(len(result.stderr), 16384)
        self.assertIn("SYNTHETIC-ONLY-DIAGNOSTIC", diagnostic["stderr_text"])
        self.assertTrue(diagnostic["direct_child_reaped"])


if __name__ == "__main__":
    unittest.main()
