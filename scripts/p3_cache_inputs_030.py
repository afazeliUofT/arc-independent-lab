"""Offline proposal: exact noncredential cache bytes in sealed Linux memfds.

No CLI, process launch, network access, credential read, or authority grant.
Production use requires the future explicit cache/control-scope amendment.
See reports/P3_CACHE_DESIGN_030.md for the observation and integration limits.
"""
from __future__ import annotations

import copy
import fcntl
import hashlib
import json
import os
from pathlib import Path
import selectors
import signal
import stat
import subprocess
import sys
import tempfile
import time

CACHE_NAMES = ("cloud-config-bundle-cache.json", "models_cache.json")
MAX_CACHE_BYTES = 4 * 1024 * 1024
CHUNK_BYTES = 65536
PROBE_ACTIVE_SECONDS = 8
PROBE_CLEANUP_SECONDS = 2
# Stable Linux UAPI values are needed when Python was built with older headers.
# This does not supply kernel support: real fcntl calls must still succeed.
# Source: linux v6.8 include/uapi/{linux,asm-generic}/fcntl.h (2026-09-10).
F_ADD_SEALS = getattr(fcntl, "F_ADD_SEALS", 1033)
F_GET_SEALS = getattr(fcntl, "F_GET_SEALS", 1034)
F_SEAL_SEAL = getattr(fcntl, "F_SEAL_SEAL", 0x0001)
F_SEAL_SHRINK = getattr(fcntl, "F_SEAL_SHRINK", 0x0002)
F_SEAL_GROW = getattr(fcntl, "F_SEAL_GROW", 0x0004)
F_SEAL_WRITE = getattr(fcntl, "F_SEAL_WRITE", 0x0008)
SEALS = F_SEAL_WRITE | F_SEAL_GROW | F_SEAL_SHRINK | F_SEAL_SEAL


class CacheInputError(RuntimeError):
    """Safe fixed-code error. No source bytes or arbitrary names are included."""


def _require(condition, code):
    if not condition:
        raise CacheInputError(code)


def _meta(info):
    return {"device": info.st_dev, "inode": info.st_ino, "bytes": info.st_size,
            "mode": stat.S_IMODE(info.st_mode), "mtime_ns": info.st_mtime_ns,
            "ctime_ns": info.st_ctime_ns, "uid": info.st_uid,
            "gid": info.st_gid, "nlink": info.st_nlink,
            "type": stat.S_IFMT(info.st_mode)}


def _home_path(value):
    raw = os.fspath(value)
    _require(type(raw) is str and raw and "\0" not in raw, "invalid_home_path")
    path = Path(raw)
    _require(path.is_absolute() and str(path) == raw and ".." not in path.parts
             and path.name == ".codex" and len(path.parts) >= 3,
             "invalid_home_path")
    _require("ARC_AGI3_Plasticity_Lab" not in path.parts, "forbidden_programme")
    return path


def _open_home(path):
    """Walk from / with nofollow directory FDs, never Path.resolve()."""
    fd = os.open("/", os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        for part in path.parts[1:]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY |
                            os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=fd)
            os.close(fd)
            fd = child
        return fd
    except BaseException:
        os.close(fd)
        raise


def _observe(directory_fd, name):
    _require(name in CACHE_NAMES, "noncache_name_forbidden")
    try:
        info = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
    except FileNotFoundError:
        return {"present": False}
    return {"present": True, "metadata": _meta(info)}


def _regular(info):
    _require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1,
             "cache_not_single_link_regular_file")
    _require(info.st_uid == os.getuid() and not info.st_mode & 0o022,
             "cache_owner_or_write_permissions_refused")
    _require(0 < info.st_size <= MAX_CACHE_BYTES, "cache_size_refused")


def _read_bounded(fd):
    raw = bytearray()
    while len(raw) <= MAX_CACHE_BYTES:
        chunk = os.read(fd, min(CHUNK_BYTES, MAX_CACHE_BYTES + 1 - len(raw)))
        if not chunk:
            break
        raw.extend(chunk)
    _require(0 < len(raw) <= MAX_CACHE_BYTES, "cache_size_refused")
    return bytes(raw)


def _sealed_copy(raw, mode):
    fd = os.memfd_create("arc-known-cache", os.MFD_CLOEXEC | os.MFD_ALLOW_SEALING)
    try:
        os.fchmod(fd, mode)
        offset = 0
        while offset < len(raw):
            written = os.write(fd, raw[offset:offset + CHUNK_BYTES])
            _require(written > 0, "snapshot_write_no_progress")
            offset += written
        fcntl.fcntl(fd, F_ADD_SEALS, SEALS)
        _require(fcntl.fcntl(fd, F_GET_SEALS) == SEALS,
                 "snapshot_seals_missing")
        _require(os.pread(fd, len(raw) + 1, 0) == raw, "snapshot_bytes_differ")
        os.lseek(fd, 0, os.SEEK_SET)
        return fd
    except BaseException:
        os.close(fd)
        raise


class CacheInputs:
    """Own live FDs until closed; receipts are safe JSON, descriptors are not.

    Never persist or replay pass_fds/argv containing descriptor numbers. Keep
    this context alive through child creation and integrity postchecks; close
    it on every launch failure and after child reap. No destructor authority.
    """

    def __init__(self, home, records, fds):
        self.home = home
        self._records = records
        self._fds = fds
        self._closed = False

    def __enter__(self):
        _require(not self._closed, "snapshot_closed")
        return self

    def __exit__(self, *_):
        self.close()

    def close(self):
        if not self._closed:
            self._closed = True
            for fd in self._fds.values():
                os.close(fd)
            self._fds.clear()

    @property
    def pass_fds(self):
        _require(not self._closed, "snapshot_closed")
        return tuple(self._fds[name] for name in CACHE_NAMES if name in self._fds)

    def receipt(self):
        return {"kind": "P3_CACHE_INPUT_SNAPSHOT_030_v1",
                "inputs": copy.deepcopy(self._records),
                "credential_contents_opened_hashed_or_copied": False,
                "cache_contents_saved_or_logged": False,
                "kernel_child_mount_verified": False,
                "capture_claim": "two_equal_reads_and_unchanged_observed_metadata",
                "not_a_filesystem_transaction_or_malicious_host_proof": True}

    def verify(self):
        _require(not self._closed, "snapshot_closed")
        results = []
        for name in CACHE_NAMES:
            record = self._records[name]
            if not record["source_before"]["present"]:
                results.append({"name": name, "present": False,
                                "snapshot_unchanged": True})
                continue
            fd = self._fds[name]
            length = record["source_before"]["metadata"]["bytes"]
            raw = os.pread(fd, length + 1, 0)
            ok = (fcntl.fcntl(fd, F_GET_SEALS) == SEALS
                  and len(raw) == length
                  and hashlib.sha256(raw).hexdigest() == record["sha256"])
            results.append({"name": name, "present": True,
                            "snapshot_unchanged": ok})
        _require(all(row["snapshot_unchanged"] for row in results),
                 "snapshot_integrity_failed")
        return {"all_inputs_intact": True, "inputs": results,
                "kernel_child_mount_verified": False}

    def source_after_observations(self):
        """Metadata only; record both paths even when one fails or changes.

        This is separate from verify(): a later host change neither modifies
        sealed bytes nor identifies its writer. No source file is opened here.
        """
        results = []
        try:
            directory_fd = _open_home(self.home)
        except OSError:
            return [{"name": name, "observation_succeeded": False,
                     "error": "cache_home_topology_unavailable"}
                    for name in CACHE_NAMES]
        try:
            for name in CACHE_NAMES:
                before = self._records[name]["source_before"]
                try:
                    after = _observe(directory_fd, name)
                    fields = ["present"] if before["present"] != after["present"] else []
                    if before["present"] and after["present"]:
                        fields += [key for key in before["metadata"]
                                   if before["metadata"][key] != after["metadata"][key]]
                    results.append({"name": name, "path": str(self.home / name),
                                    "observation_succeeded": True, "before": before,
                                    "after": after, "changed_fields": fields,
                                    "writer_identified": False,
                                    "sealed_input_invalidated_by_source_change": False})
                except OSError:
                    results.append({"name": name, "observation_succeeded": False,
                                    "error": "source_metadata_unavailable"})
        finally:
            os.close(directory_fd)
        return results

    def mount_args(self):
        self.verify()
        result = []
        for name in CACHE_NAMES:
            if name in self._fds:
                fd = self._fds[name]
                os.lseek(fd, 0, os.SEEK_SET)
                mode = self._records[name]["source_before"]["metadata"]["mode"]
                result.extend(["--perms", format(mode, "04o"), "--ro-bind-data",
                               str(fd), str(self.home / name)])
        return result

    def observe_sources(self):
        return self.source_after_observations()

    def apply_to_plan(self, plan):
        return transform_mount_plan(plan, self)

    def verify_origins(self, origins):
        """Compare already-authorized metadata inventory; never inspect auth."""
        _require(type(origins) is list and len(origins) == len(CACHE_NAMES),
                 "cache_origin_inventory_shape")
        by_path = {row.get("path"): row for row in origins if type(row) is dict}
        expected = {str(self.home / name) for name in CACHE_NAMES}
        _require(set(by_path) == expected, "cache_origin_paths_differ")
        keys = {"device", "inode", "bytes", "mode", "mtime_ns", "ctime_ns"}
        for name in CACHE_NAMES:
            before = self._records[name]["source_before"]
            old = by_path[str(self.home / name)]
            _require(type(old.get("present")) is bool and old["present"] == before["present"],
                     "cache_origin_presence_differ")
            if old["present"]:
                _require(type(old.get("metadata")) is dict and set(old["metadata"]) == keys,
                         "cache_origin_metadata_shape")
                _require(all(old["metadata"][key] == before["metadata"][key] for key in keys),
                         "cache_origin_metadata_differ")
        return True

    def report_plan(self, plan):
        """Nonreplayable audit copy; remove all live ro-bind-data FD numbers."""
        result = copy.deepcopy(plan)
        argv = result["argv"]
        stop = argv.index("--")
        for index in range(stop):
            if argv[index] == "--ro-bind-data":
                _require(index + 2 < stop and argv[index + 2] in
                         {str(self.home / name) for name in CACHE_NAMES},
                         "unexpected_data_mount_in_report")
                argv[index + 1] = "LIVE_SEALED_CACHE_FD_NOT_REPLAYABLE"
        result["replayable"] = False
        result["live_cache_descriptor_numbers_saved"] = False
        return result


def capture_cache_inputs(codex_home, *, auth_metadata):
    """Capture only the two hard-coded names. No arbitrary file argument.

    All content access is bounded. A changed observed source, path replacement,
    symlink, hard link, nonregular file, or failed sealing refuses the whole set.
    Successful capture freezes absence as well as presence for the child plan.
    """
    home = _home_path(codex_home)
    _require(sys.platform == "linux", "linux_memfd_required")
    _require(type(auth_metadata) is dict
             and type(auth_metadata.get("device")) is int
             and type(auth_metadata.get("inode")) is int,
             "existing_auth_identity_metadata_required")
    forbidden_identity = (auth_metadata["device"], auth_metadata["inode"])
    directory_fd = None
    fds = {}
    records = {}
    try:
        directory_fd = _open_home(home)
        directory_identity = (os.fstat(directory_fd).st_dev, os.fstat(directory_fd).st_ino)
        before_all = {name: _observe(directory_fd, name) for name in CACHE_NAMES}
        for name in CACHE_NAMES:
            before = before_all[name]
            record = {"path": str(home / name), "source_before": before}
            records[name] = record
            if not before["present"]:
                record["source_after_capture"] = _observe(directory_fd, name)
                _require(record["source_after_capture"] == before,
                         "source_changed_during_capture")
                continue
            # Validate the lstat before opening, then validate the opened inode.
            meta = before["metadata"]
            _require((meta["device"], meta["inode"]) != forbidden_identity,
                     "credential_inode_alias_refused")
            _require(meta["type"] == stat.S_IFREG and meta["nlink"] == 1,
                     "cache_not_single_link_regular_file")
            fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC |
                         os.O_NONBLOCK, dir_fd=directory_fd)
            try:
                info = os.fstat(fd)
                _regular(info)
                _require((info.st_dev, info.st_ino) != forbidden_identity,
                         "credential_inode_alias_refused")
                _require(_meta(info) == meta, "source_changed_before_open")
                raw = _read_bounded(fd)
                middle = _meta(os.fstat(fd))
                os.lseek(fd, 0, os.SEEK_SET)
                second = _read_bounded(fd)
                after = _meta(os.fstat(fd))
                record["source_after_capture"] = _observe(directory_fd, name)
                _require(middle == after == meta and raw == second
                         and len(raw) == meta["bytes"]
                         and record["source_after_capture"] == before,
                         "source_changed_during_capture")
                fds[name] = _sealed_copy(raw, meta["mode"])
                record.update({"sha256": hashlib.sha256(raw).hexdigest(),
                               "seals": SEALS, "two_reads_equal": True})
            finally:
                os.close(fd)
        # Re-walk ancestors to ensure the original spelling still names this
        # directory; compare both paths after the complete capture interval.
        fresh = _open_home(home)
        try:
            _require((os.fstat(fresh).st_dev, os.fstat(fresh).st_ino) == directory_identity,
                     "cache_home_replaced_during_capture")
            for name in CACHE_NAMES:
                _require(_observe(fresh, name) == before_all[name],
                         "source_changed_during_capture")
        finally:
            os.close(fresh)
        result = CacheInputs(home, records, fds)
        result.verify()
        return result
    except BaseException:
        for fd in fds.values():
            os.close(fd)
        raise
    finally:
        if directory_fd is not None:
            os.close(directory_fd)


def transform_mount_plan(plan, snapshots):
    """Pure narrow plan edit; only known cache ro-bind grants are replaced.

    Input must be the already validated, approved plan. This function is not
    a general mount-policy validator. Returned argv is process-local and must
    not be persisted/replayed with live descriptor numbers. Use pass_fds from
    the same live CacheInputs object in Popen(close_fds=True, pass_fds=...).
    The exact same-path auth grant, config policy, runtime and command survive.
    """
    _require(type(plan) is dict and type(plan.get("argv")) is list
             and type(plan.get("mounts")) is list, "invalid_plan")
    argv = plan["argv"]
    _require(all(type(arg) is str for arg in argv) and argv.count("--") == 1,
             "invalid_plan_argv")
    stop = argv.index("--")
    _require(argv[:stop].count("--remount-ro") == 1, "invalid_plan_remount")
    targets = {str(snapshots.home / name): name for name in CACHE_NAMES}
    kept = []
    counts = {name: 0 for name in CACHE_NAMES}
    index = 0
    while index < stop:
        if argv[index] == "--ro-bind" and index + 2 < stop:
            source, destination = argv[index + 1:index + 3]
            if source in targets or destination in targets:
                _require(source == destination and source in targets,
                         "unexpected_cache_mount")
                counts[targets[source]] += 1
                index += 3
                continue
        _require(argv[index] not in targets, "unexpected_cache_path_argument")
        kept.append(argv[index])
        index += 1
    mounts = []
    mount_counts = {name: 0 for name in CACHE_NAMES}
    for item in plan["mounts"]:
        _require(type(item) is dict, "invalid_mount_entry")
        source, destination = item.get("source"), item.get("destination")
        if source in targets or destination in targets:
            _require(source == destination and source in targets
                     and item.get("access") == "read", "unexpected_cache_mount")
            mount_counts[targets[source]] += 1
        else:
            mounts.append(copy.deepcopy(item))
    for name in CACHE_NAMES:
        expected = int(snapshots._records[name]["source_before"]["present"])
        _require(counts[name] == mount_counts[name] == expected,
                 "cache_grants_differ_from_capture")
        if expected:
            mounts.append({"source": "sealed_exact_noncredential_cache_bytes",
                           "destination": str(snapshots.home / name), "access": "read",
                           "kind": "proposed_cache_snapshot_030"})
    where = kept.index("--remount-ro")
    kept[where:where] = snapshots.mount_args()
    updated = copy.deepcopy(plan)
    updated["argv"] = kept + argv[stop:]
    updated["mounts"] = mounts
    return updated


def _run_synthetic_child(argv, pass_fds):
    """Bounded synthetic diagnostics only; no raw native protocol is involved."""
    start = time.monotonic()
    active_end = start + PROBE_ACTIVE_SECONDS
    deadline = active_end + PROBE_CLEANUP_SECONDS
    process = None
    selector = selectors.DefaultSelector()
    output = {"stdout": bytearray(), "stderr": bytearray()}
    caps = {"stdout": 4096, "stderr": 16384}
    diagnostic = {"kind": "synthetic_mount_diagnostic", "phase": "launch",
                  "failure_code": None, "stdout_truncated": False,
                  "stderr_truncated": False, "group_kill_attempted": False,
                  "direct_child_reaped": False, "process_group_absent_after_cleanup": False,
                  "no_native_client_or_real_cache_or_auth_input": True}
    try:
        process = subprocess.Popen(argv, pass_fds=pass_fds, close_fds=True,
                         stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, start_new_session=True,
                         env={"PATH": "/usr/bin:/bin", "LC_ALL": "C"})
        diagnostic["phase"] = "read_synthetic_output"
        for stream, name in [(process.stdout, "stdout"), (process.stderr, "stderr")]:
            os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_READ, name)
        while selector.get_map():
            _require(time.monotonic() < active_end, "synthetic_mount_deadline")
            for key, _ in selector.select(timeout=0.05):
                raw = os.read(key.fileobj.fileno(), 4096)
                if not raw:
                    selector.unregister(key.fileobj)
                    continue
                room = caps[key.data] - len(output[key.data])
                output[key.data].extend(raw[:room])
                if len(raw) > room:
                    diagnostic[key.data + "_truncated"] = True
                    raise CacheInputError("synthetic_mount_output_limit")
        diagnostic["phase"] = "wait_synthetic_child"
        process.wait(timeout=max(0.01, active_end - time.monotonic()))
    except CacheInputError as error:
        diagnostic["failure_code"] = str(error)
    except subprocess.TimeoutExpired:
        diagnostic["failure_code"] = "synthetic_mount_deadline"
    except OSError as error:
        diagnostic["failure_code"] = "synthetic_process_os_error"
        diagnostic["os_errno"] = error.errno
    finally:
        diagnostic["last_active_phase"] = diagnostic["phase"]
        diagnostic["phase"] = "cleanup"
        try:
            if process is not None:
                try:
                    diagnostic["group_kill_attempted"] = True
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    process.wait(timeout=max(0.01, deadline - time.monotonic()))
                    diagnostic["direct_child_reaped"] = process.returncode is not None
                    while time.monotonic() < deadline:
                        try:
                            os.killpg(process.pid, 0)
                        except ProcessLookupError:
                            diagnostic["process_group_absent_after_cleanup"] = True
                            break
                        time.sleep(0.01)
                except (OSError, subprocess.TimeoutExpired):
                    diagnostic["failure_code"] = "synthetic_cleanup_unverified"
                finally:
                    for stream in (process.stdout, process.stderr):
                        stream.close()
        finally:
            selector.close()
    if not diagnostic["direct_child_reaped"] or not diagnostic["process_group_absent_after_cleanup"]:
        diagnostic["failure_code"] = diagnostic["failure_code"] or "synthetic_cleanup_unverified"
    diagnostic["phase"] = "finished"
    diagnostic["elapsed_seconds"] = round(time.monotonic() - start, 6)
    diagnostic["stderr_text"] = bytes(output["stderr"]).decode("utf-8", errors="replace")
    diagnostic["stderr_byte_limit"] = caps["stderr"]
    completed = subprocess.CompletedProcess(argv, process.returncode if process else None,
                       bytes(output["stdout"]), bytes(output["stderr"]))
    completed.synthetic_diagnostic = diagnostic
    return completed


def probe_sealed_mount(bwrap_path, project_delivery):
    """One bounded, synthetic-only namespace preflight; never a native client.

    A future authorized controller must require PASSED BEFORE reserving any
    native/model allowance. The caller first verifies its pinned bwrap binary.
    This function does not inspect actual home/cache/auth paths or use network.
    A denied or unsupported kernel returns UNVERIFIED; there is no fallback.
    """
    result = {"kind": "P3_SEALED_CACHE_MOUNT_PREFLIGHT_030_v1",
              "status": "UNVERIFIED", "native_clients_started": 0,
              "model_turns_sent": 0, "real_cache_or_credential_contents_accessed": False,
              "synthetic_only": True, "kernel_child_mount_verified": False}
    _require(os.fspath(bwrap_path) == "/usr/bin/bwrap", "probe_bwrap_path_refused")
    delivery = Path(project_delivery)
    _require(delivery.is_absolute() and str(delivery) == os.fspath(project_delivery)
             and ".." not in delivery.parts and delivery.name == "delivery"
             and "ARC_AGI3_Plasticity_Lab" not in delivery.parts,
             "probe_delivery_path_refused")
    directory_fd = _open_home(delivery)
    os.close(directory_fd)
    child_code = r'''
import hashlib,json,os,sys
from pathlib import Path
p=Path(sys.argv[1]); absent=p.parent/'cloud-config-bundle-cache.json'
checks={'exact_snapshot_bytes':hashlib.sha256(p.read_bytes()).hexdigest()==sys.argv[2],
        'absent_cache_stays_absent':not absent.exists(),
        'synthetic_auth_not_mounted':not (p.parent/'auth.json').exists()}
for name,operation in [('snapshot_write_refused',lambda:p.write_bytes(b'forbidden')),
                       ('snapshot_truncate_refused',lambda:os.truncate(p,0)),
                       ('absent_cache_creation_refused',lambda:absent.write_bytes(b'forbidden'))]:
    try:
        operation(); checks[name]=False
    except OSError:
        checks[name]=True
print(json.dumps(checks,sort_keys=True))
sys.exit(0 if all(checks.values()) else 3)
'''
    expected_keys = {"exact_snapshot_bytes", "absent_cache_stays_absent",
                     "synthetic_auth_not_mounted", "snapshot_write_refused",
                     "snapshot_truncate_refused", "absent_cache_creation_refused"}
    try:
        with tempfile.TemporaryDirectory(prefix="cache_mount030_", dir=delivery) as directory:
            home = Path(directory) / ".codex"
            home.mkdir(mode=0o700)
            source = home / "models_cache.json"
            raw = b'{"synthetic_cache":"original"}\n'
            source.write_bytes(raw)
            source.chmod(0o600)
            auth = home / "auth.json"
            auth.write_bytes(b"synthetic sentinel, not a credential")
            auth_identity = {"device": auth.stat().st_dev, "inode": auth.stat().st_ino}
            with capture_cache_inputs(home, auth_metadata=auth_identity) as snapshots:
                # Same-inode host write after capture must not reach the child.
                inode = source.stat().st_ino
                source.write_bytes(b'{"synthetic_cache":"host changed after capture"}\n')
                result["same_inode_source_mutation_performed"] = source.stat().st_ino == inode
                argv = [str(bwrap_path), "--unshare-all", "--die-with-parent",
                        "--tmpfs", "/", "--ro-bind", "/usr", "/usr",
                        "--symlink", "usr/bin", "/bin", "--symlink", "usr/lib", "/lib",
                        "--symlink", "usr/lib64", "/lib64"]
                argv += snapshots.mount_args()
                argv += ["--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp",
                         "--remount-ro", "/", "--cap-drop", "ALL", "--",
                         "/usr/bin/python3", "-I", "-c", child_code, str(source),
                         hashlib.sha256(raw).hexdigest()]
                completed = _run_synthetic_child(argv, snapshots.pass_fds)
                result["exit_code"] = completed.returncode
                diagnostic = getattr(completed, "synthetic_diagnostic", None)
                result["synthetic_diagnostic"] = diagnostic
                result["synthetic_process_reaped"] = bool(diagnostic and diagnostic.get("direct_child_reaped"))
                result["stdout_bytes"] = len(completed.stdout)
                result["stderr_bytes"] = len(completed.stderr)
                result["bounded_synthetic_stderr_saved"] = True
                result["raw_native_logs_or_protocol_saved"] = False
                result["sealed_inputs_after"] = snapshots.verify()
                if (completed.returncode == 0 and len(completed.stdout) <= 4096
                        and type(diagnostic) is dict and diagnostic.get("failure_code") is None
                        and diagnostic.get("direct_child_reaped") is True
                        and diagnostic.get("process_group_absent_after_cleanup") is True):
                    checks = json.loads(completed.stdout)
                    if (type(checks) is dict and set(checks) == expected_keys
                            and all(value is True for value in checks.values())
                            and result["same_inode_source_mutation_performed"]):
                        result.update({"status": "PASSED", "checks": checks,
                                       "kernel_child_mount_verified": True})
                    else:
                        result.update({"status": "FAILED", "reason": "invalid_or_failed_synthetic_checks"})
                else:
                    result["reason"] = "bubblewrap_or_synthetic_child_did_not_complete"
    except subprocess.TimeoutExpired:
        result["reason"] = "synthetic_mount_deadline"
    except (CacheInputError, OSError, ValueError, json.JSONDecodeError):
        result["reason"] = "synthetic_mount_or_memfd_unavailable"
    return result
