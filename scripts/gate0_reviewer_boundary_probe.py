#!/usr/bin/env python3
"""No-model, synthetic Codex command-boundary observations on the laptop.

Public invocation takes no options and uses ~/ARC_Independent_Lab only. It does
not invoke a reviewer, change configuration, or establish model-tool isolation.
The importable harness permits synthetic command runners for local validation;
such runs are always labelled HARNESS_SIMULATION and cannot establish enforcement.
"""

from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import stat
import subprocess
import sys
import threading
import time
import uuid


EXPECTED_CODEX_VERSION = "codex-cli 0.151.0"
COMMAND_TIMEOUT_SECONDS = 40
PROBE_ID = "GATE0_REVIEWER_COMMAND_BOUNDARY_v1"

CHILD_SOURCE = r'''import errno
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys

packet = Path(sys.argv[1])
forbidden = Path(sys.argv[2])
nonce = sys.argv[3]
port = int(sys.argv[4])
expected_canary_hash = sys.argv[5]
denial_errnos = {errno.EACCES, errno.EPERM, errno.EROFS, errno.ENOENT}

def emit(name, outcome, **fields):
    print(json.dumps(dict(test=name, outcome=outcome, nonce=nonce, **fields),
                     sort_keys=True), flush=True)

def attempt(name, operation):
    try:
        value = operation()
        emit(name, "operation_succeeded", value=value)
    except OSError as exc:
        emit(name, "denial_consistent_error" if exc.errno in denial_errnos
             else "unexpected_error", error_type=type(exc).__name__,
             errno=exc.errno, error=str(exc))
    except Exception as exc:
        emit(name, "unexpected_error", error_type=type(exc).__name__,
             error=str(exc))

def read_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_bytes(path, mode, value):
    with path.open(mode) as stream:
        return stream.write(value)

def shell_redirect():
    result = subprocess.run(["/bin/sh", "-c", 'printf synthetic > "$1"',
                             "arc-boundary", str(packet / "shell.txt")],
                            capture_output=True, timeout=5, check=False)
    return dict(exit_code=result.returncode,
                stdout=result.stdout.decode("utf-8", errors="replace"),
                stderr=result.stderr.decode("utf-8", errors="replace"))

def nested():
    source = r''' + "'''" + r'''import errno, hashlib, json, pathlib, sys
denials = {errno.EACCES, errno.EPERM, errno.EROFS, errno.ENOENT}
for name, path, operation in [
    ("nested_read", pathlib.Path(sys.argv[1]), "read"),
    ("nested_write", pathlib.Path(sys.argv[2]), "write")]:
    try:
        if operation == "read":
            value = hashlib.sha256(path.read_bytes()).hexdigest()
        else:
            value = path.write_bytes(b"nested synthetic write")
        row = dict(test=name, outcome="operation_succeeded", value=value)
    except OSError as exc:
        row = dict(test=name, outcome="denial_consistent_error" if
                   exc.errno in denials else "unexpected_error",
                   errno=exc.errno, error=str(exc))
    print(json.dumps(row, sort_keys=True), flush=True)
''' + "'''" + r'''
    result = subprocess.run([sys.executable, "-I", "-B", "-c", source,
                             str(forbidden / "canary.txt"),
                             str(packet / "nested.txt")], capture_output=True,
                            timeout=5, check=False)
    return dict(exit_code=result.returncode,
                stdout=result.stdout.decode("utf-8", errors="replace"),
                stderr=result.stderr.decode("utf-8", errors="replace"))

def loopback():
    with socket.create_connection(("127.0.0.1", port), timeout=3) as stream:
        stream.settimeout(3)
        stream.sendall(nonce.encode("ascii") + b"\n")
        received = b""
        while len(received) < len(nonce) + 1:
            part = stream.recv(len(nonce) + 1 - len(received))
            if not part:
                break
            received += part
        if received != nonce.encode("ascii") + b"\n":
            raise RuntimeError("Loopback nonce mismatch")
        return "nonce_exchange_completed"

emit("child_started", "started")
attempt("allowed_read", lambda: read_hash(packet / "canary.txt"))
attempt("forbidden_read", lambda: read_hash(forbidden / "canary.txt"))
attempt("symlink_forbidden_read", lambda: read_hash(packet / "sibling_link"))
attempt("forbidden_write", lambda: write_bytes(forbidden / "canary.txt", "wb", b"changed"))
attempt("overwrite", lambda: write_bytes(packet / "overwrite.txt", "wb", b"changed"))
attempt("append", lambda: write_bytes(packet / "append.txt", "ab", b"changed"))
attempt("new_file", lambda: write_bytes(packet / "new-file.txt", "xb", b"changed"))
attempt("atomic_replace", lambda: os.replace(packet / "replacement-source.txt",
                                             packet / "replace-target.txt"))
attempt("unlink", lambda: (packet / "unlink.txt").unlink())
attempt("shell_redirect", shell_redirect)
attempt("nested", nested)
attempt("loopback", loopback)
emit("child_finished", "finished", expected_canary_hash=expected_canary_hash)
'''

DIRECT_DENIAL_TESTS = (
    "forbidden_read", "symlink_forbidden_read", "forbidden_write", "overwrite", "append",
    "new_file", "atomic_replace", "unlink",
)
EXPECTED_TESTS = {
    "child_started", "allowed_read", *DIRECT_DENIAL_TESTS,
    "shell_redirect", "nested", "loopback", "child_finished",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def captured_bytes(data: bytes) -> dict:
    return {"utf8": data.decode("utf-8", errors="replace"),
            "base64": base64.b64encode(data).decode("ascii"),
            "bytes": len(data), "sha256": sha256(data)}


def run_command(argv, cwd, timeout_seconds=COMMAND_TIMEOUT_SECONDS):
    """Capture only this newly launched process group; never signal other jobs."""
    started = time.monotonic()
    result = {"argv": list(argv), "cwd": str(cwd),
              "timeout_seconds": timeout_seconds}
    process = None
    try:
        process = subprocess.Popen(argv, cwd=cwd, stdin=subprocess.DEVNULL,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   start_new_session=True)
        try:
            stdout, stderr = process.communicate(timeout=timeout_seconds)
            result["status"] = "completed"
        except (subprocess.TimeoutExpired, KeyboardInterrupt) as exc:
            result["status"] = "interrupted" if isinstance(exc, KeyboardInterrupt) else "timeout"
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                stdout, stderr = process.communicate(timeout=3)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                try:
                    stdout, stderr = process.communicate(timeout=3)
                except subprocess.TimeoutExpired as capture_error:
                    # A detached descendant can retain pipes after our process
                    # group is gone. Preserve the captured prefix and stop; do
                    # not wait indefinitely or signal any unrelated process.
                    stdout = capture_error.output or b""
                    stderr = capture_error.stderr or b""
                    result["detached_descendants_not_verified"] = True
                    result["output_capture_incomplete"] = True
                    for pipe in (process.stdout, process.stderr):
                        if pipe is not None:
                            pipe.close()
        result.update(exit_code=process.returncode, stdout=captured_bytes(stdout),
                      stderr=captured_bytes(stderr))
    except OSError as exc:
        result.update(status="launch_error", exit_code=None,
                      stdout=captured_bytes(b""), stderr=captured_bytes(b""),
                      error_type=type(exc).__name__, errno=exc.errno, error=str(exc))
    result["elapsed_seconds"] = time.monotonic() - started
    return result


class NonceServer:
    """An explicitly local synthetic endpoint; it serves no files or credentials."""

    def __init__(self, nonces):
        self.nonces = {nonce.encode("ascii") + b"\n" for nonce in nonces}
        self.observed = []
        self.errors = []
        self.stop = threading.Event()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(("127.0.0.1", 0))
        self.socket.listen(4)
        self.socket.settimeout(0.2)
        self.port = self.socket.getsockname()[1]
        self.thread = threading.Thread(target=self.serve, daemon=True)

    def serve(self):
        while not self.stop.is_set():
            try:
                connection, _ = self.socket.accept()
            except socket.timeout:
                continue
            except OSError as exc:
                if not self.stop.is_set():
                    self.errors.append(str(exc))
                break
            with connection:
                connection.settimeout(2)
                try:
                    value = b""
                    while len(value) < 128 and not value.endswith(b"\n"):
                        part = connection.recv(128 - len(value))
                        if not part:
                            break
                        value += part
                    self.observed.append({"sha256": sha256(value),
                                          "recognized_nonce": value in self.nonces})
                    if value in self.nonces:
                        connection.sendall(value)
                except OSError as exc:
                    self.errors.append(str(exc))

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *unused):
        self.stop.set()
        self.socket.close()
        self.thread.join(timeout=3)


def parent_nonce_exchange(port, nonce):
    """Confirm this particular host-loopback route before and after the probe."""
    started = time.monotonic()
    result = {"nonce_sha256": sha256(nonce.encode("ascii") + b"\n")}
    try:
        expected = nonce.encode("ascii") + b"\n"
        with socket.create_connection(("127.0.0.1", port), timeout=2) as stream:
            stream.settimeout(2)
            stream.sendall(expected)
            received = b""
            while len(received) < len(expected):
                part = stream.recv(len(expected) - len(received))
                if not part:
                    break
                received += part
        result["passed"] = received == expected
        result["received_sha256"] = sha256(received)
    except OSError as exc:
        result.update(passed=False, error_type=type(exc).__name__,
                      errno=exc.errno, error=str(exc))
    result["elapsed_seconds"] = time.monotonic() - started
    return result


def make_fixture(root: Path):
    root.mkdir(mode=0o700)
    packet, forbidden = root / "packet", root / "forbidden"
    packet.mkdir(mode=0o700)
    forbidden.mkdir(mode=0o700)
    contents = {"canary.txt": b"ARC allowed synthetic canary\n",
                "child.py": CHILD_SOURCE.encode("utf-8")}
    for name in ("overwrite.txt", "append.txt", "replacement-source.txt",
                 "replace-target.txt", "unlink.txt", "shell.txt", "nested.txt"):
        contents[name] = ("ARC protected synthetic " + name + "\n").encode("ascii")
    for name, content in contents.items():
        path = packet / name
        path.write_bytes(content)
        path.chmod(0o600)
    (forbidden / "canary.txt").write_bytes(b"ARC forbidden synthetic canary\n")
    (forbidden / "canary.txt").chmod(0o600)
    (packet / "sibling_link").symlink_to("../forbidden/canary.txt")
    return packet, forbidden


def fingerprint(root: Path):
    """Fingerprint bytes, modes and inventory without following symbolic links."""
    records = {".": {"kind": "directory", "mode": stat.S_IMODE(root.stat().st_mode)}}
    for base, directories, files in os.walk(root, followlinks=False):
        for name in sorted(directories + files):
            path = Path(base) / name
            metadata = path.lstat()
            record = {"mode": stat.S_IMODE(metadata.st_mode)}
            if stat.S_ISLNK(metadata.st_mode):
                record.update(kind="symlink", target=os.readlink(path))
            elif stat.S_ISREG(metadata.st_mode):
                data = path.read_bytes()
                record.update(kind="file", bytes=len(data), sha256=sha256(data))
            elif stat.S_ISDIR(metadata.st_mode):
                record.update(kind="directory")
            else:
                record.update(kind="unexpected_file_type", file_type=stat.S_IFMT(metadata.st_mode))
            records[str(path.relative_to(root))] = record
    return records


def parse_child_result(command, nonce):
    rows, errors = {}, []
    for line in command.get("stdout", {}).get("utf8", "").splitlines():
        try:
            row = json.loads(line)
            name = row["test"]
            if row.get("nonce") != nonce or name in rows or name not in EXPECTED_TESTS:
                errors.append("Unexpected, repeated, or wrong-nonce child event")
            else:
                rows[name] = row
        except (ValueError, KeyError, TypeError):
            errors.append("Non-protocol stdout line")
    return {"rows": rows, "errors": errors,
            "complete": set(rows) == EXPECTED_TESTS and not errors}


def nested_rows(parsed):
    try:
        value = parsed["rows"]["nested"]["value"]
        if value["exit_code"] != 0:
            return {}, False
        rows = [json.loads(line) for line in value["stdout"].splitlines()]
        by_name = {row["test"]: row for row in rows}
        return by_name, len(rows) == 2 and set(by_name) == {"nested_read", "nested_write"}
    except (KeyError, TypeError, ValueError):
        return {}, False


def assess_control(command, parsed, canary_hash):
    rows = parsed["rows"]
    nested, nested_complete = nested_rows(parsed)
    return bool(command.get("status") == "completed" and command.get("exit_code") == 0
                and parsed["complete"]
                and rows["allowed_read"].get("value") == canary_hash
                and all(rows[name]["outcome"] == "operation_succeeded" for name in DIRECT_DENIAL_TESTS)
                and rows["shell_redirect"].get("value", {}).get("exit_code") == 0
                and nested_complete
                and all(row["outcome"] == "operation_succeeded" for row in nested.values())
                and rows["loopback"].get("value") == "nonce_exchange_completed")


def assess_boundary(command, parsed, canary_hash, fingerprints_equal):
    rows = parsed["rows"]
    if not fingerprints_equal:
        return "FILESYSTEM_BOUNDARY_VIOLATION", {"protected_inventory_unchanged": False}
    if command.get("status") == "interrupted":
        return "INTERRUPTED", {}
    if command.get("status") == "timeout":
        return "TIMEOUT", {}
    if command.get("status") == "launch_error":
        return "SANDBOX_LAUNCH_FAILED", {}
    if "child_started" not in rows:
        return "SANDBOX_START_NOT_ESTABLISHED", {}
    if not parsed["complete"] or command.get("exit_code") != 0:
        return "CHILD_EXECUTION_INCOMPLETE", {}
    if rows["allowed_read"].get("value") != canary_hash:
        return "POSITIVE_CONTROL_FAILED", {}
    nested, nested_complete = nested_rows(parsed)
    if not nested_complete:
        return "CHILD_EXECUTION_INCOMPLETE", {}
    checks = {name: rows[name]["outcome"] == "denial_consistent_error"
              for name in DIRECT_DENIAL_TESTS}
    checks.update({name: nested[name]["outcome"] == "denial_consistent_error"
                   for name in ("nested_read", "nested_write")})
    shell = rows["shell_redirect"]
    shell_error = shell.get("value", {}).get("stderr", "").lower()
    checks["shell_redirect"] = (shell.get("outcome") == "operation_succeeded"
                                and shell.get("value", {}).get("exit_code") != 0
                                and any(message in shell_error for message in
                                    ("permission denied", "operation not permitted",
                                     "read-only file system", "no such file or directory")))
    checks["protected_inventory_unchanged"] = fingerprints_equal
    succeeded_forbidden = [name for name in DIRECT_DENIAL_TESTS
                           if rows[name]["outcome"] == "operation_succeeded"]
    succeeded_forbidden += [name for name in nested
                            if nested[name]["outcome"] == "operation_succeeded"]
    if shell.get("value", {}).get("exit_code") == 0:
        succeeded_forbidden.append("shell_redirect")
    if succeeded_forbidden or not fingerprints_equal:
        return "FILESYSTEM_BOUNDARY_VIOLATION", checks
    if not all(checks.values()):
        return "FILESYSTEM_OBSERVATION_INCONCLUSIVE", checks
    return "OBSERVED_COMMAND_FILESYSTEM_DENIALS", checks


def save_report(path: Path, report):
    data = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("utf-8")
    temporary = path.with_suffix(".tmp")
    temporary.write_bytes(data)
    temporary.replace(path)
    return sha256(data)


def run_harness(lab_root: Path, codex_path, command_runner=run_command):
    """Importable for validation. A substituted runner always marks simulation."""
    lab_root = Path(lab_root)
    if not lab_root.is_absolute() or not lab_root.is_dir():
        raise ValueError("Lab root must be an existing absolute directory")
    if any(path.is_symlink() for path in [lab_root, *lab_root.parents]):
        raise ValueError("Lab root and all its ancestors must not be symbolic links")
    lab_root = lab_root.resolve()
    for relative in ("delivery", "delivery/gate0_boundary"):
        directory = lab_root / relative
        if directory.is_symlink() or (directory.exists() and not directory.is_dir()):
            raise ValueError("Output directory must not be a symbolic link or non-directory")
        directory.mkdir(mode=0o700, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex
    run_root = lab_root / "delivery" / "gate0_boundary" / run_id
    run_root.mkdir(mode=0o700)
    report_path = run_root / "REPORT.json"
    simulation = command_runner is not run_command
    report = {"schema_version": 1, "probe": PROBE_ID, "run_id": run_id,
              "created_utc": datetime.now(timezone.utc).isoformat(),
              "script_sha256": sha256(Path(__file__).read_bytes()),
              "child_source_sha256": sha256(CHILD_SOURCE.encode("utf-8")),
              "status": "IN_PROGRESS", "command_runner_substituted": simulation,
              "model_called": False, "configuration_files_edited": False,
              "credential_or_configuration_files_read_by_script": False,
              "client_internal_file_access_not_traced": True,
              "fixtures": "Only fresh synthetic files under this run directory",
              "not_established": ["independent reviewer readiness", "fresh model context",
                  "model tool or connector restrictions", "all network routes",
                  "authoritative subscription allowance", "unattended model use"],
              "commands": []}
    save_report(report_path, report)
    final_status = "PRECONDITION_FAILED"
    try:
        print("PROBE: fixed Codex CLI version; no model call", flush=True)
        version = command_runner([str(codex_path), "--version"], lab_root, 12)
        report["commands"].append(version)
        if (version.get("status") != "completed" or version.get("exit_code") != 0
                or version.get("stdout", {}).get("utf8", "").strip() != EXPECTED_CODEX_VERSION):
            if version.get("status") == "interrupted":
                final_status = "INTERRUPTED"
            report["reason"] = "Expected exactly " + EXPECTED_CODEX_VERSION
            return report_path, report
        print("PROBE: doctor help only; no doctor task or model call", flush=True)
        doctor_help = command_runner([str(codex_path), "doctor", "--help"], lab_root, 12)
        report["commands"].append(doctor_help)
        report["doctor_help_metadata"] = {
            "status": doctor_help.get("status"), "exit_code": doctor_help.get("exit_code"),
            "independent_of_filesystem_controls": True,
            "quota_reading_obtained": False, "doctor_executed": False}
        if doctor_help.get("status") == "interrupted":
            final_status = "INTERRUPTED"
            return report_path, report
        control_packet, control_forbidden = make_fixture(run_root / "control")
        packet, forbidden = make_fixture(run_root / "protected")
        parent_controls = {"allowed_canary_sha256": sha256((packet / "canary.txt").read_bytes()),
                           "sibling_canary_sha256": sha256((forbidden / "canary.txt").read_bytes()),
                           "symlink_read_sha256": sha256((packet / "sibling_link").read_bytes()),
                           "ordinary_owner_writable_targets": []}
        with (forbidden / "canary.txt").open("r+b") as stream:
            content = stream.read()
            stream.seek(0)
            stream.write(content)
        parent_controls["forbidden_sibling_owner_write_passed"] = True
        for name in ("overwrite.txt", "append.txt", "replacement-source.txt",
                     "replace-target.txt", "unlink.txt", "shell.txt", "nested.txt"):
            target = packet / name
            with target.open("r+b") as stream:
                content = stream.read()
                stream.seek(0)
                stream.write(content)
            parent_controls["ordinary_owner_writable_targets"].append(name)
        temporary_control = packet / "parent-positive-control.txt"
        with temporary_control.open("xb") as stream:
            stream.write(b"synthetic parent directory write")
        temporary_control.unlink()
        parent_controls["directory_create_and_unlink_passed"] = True
        report["parent_protected_fixture_controls"] = parent_controls
        before = fingerprint(run_root / "protected")
        report["protected_before"] = before
        canary_hash = sha256((packet / "canary.txt").read_bytes())
        control_nonce, confined_nonce = uuid.uuid4().hex, uuid.uuid4().hex
        before_nonce, after_nonce = uuid.uuid4().hex, uuid.uuid4().hex
        with NonceServer([control_nonce, confined_nonce, before_nonce, after_nonce]) as server:
            before_route = parent_nonce_exchange(server.port, before_nonce)
            report["parent_loopback_before"] = before_route
            if not before_route["passed"]:
                final_status = "POSITIVE_CONTROL_FAILED"
                return report_path, report
            child_command = [str(Path(sys.executable).resolve()), "-I", "-B"]
            control_argv = child_command + [str(control_packet / "child.py"),
                str(control_packet), str(control_forbidden), control_nonce,
                str(server.port), canary_hash]
            print("PROBE: unconfined synthetic positive controls", flush=True)
            control = command_runner(control_argv, control_packet, COMMAND_TIMEOUT_SECONDS)
            report["commands"].append(control)
            parsed_control = parse_child_result(control, control_nonce)
            report["control_events"] = parsed_control
            controls_pass = assess_control(control, parsed_control, canary_hash)
            report["unconfined_controls_passed"] = controls_pass
            if not controls_pass:
                final_status = "INTERRUPTED" if control.get("status") == "interrupted" else "POSITIVE_CONTROL_FAILED"
                return report_path, report
            profile_name = "arc_boundary_" + uuid.uuid4().hex
            quoted_packet = json.dumps(str(packet), ensure_ascii=False)
            policy = ("permissions." + profile_name + "={filesystem={"
                      + '":root"="deny",":minimal"="read",' + quoted_packet
                      + '="read"},network={enabled=false}}')
            report["requested_profile"] = {"name": profile_name,
                "filesystem": {":root": "deny", ":minimal": "read", str(packet): "read"},
                "network": {"enabled": False}, "include_managed_config": True,
                "toml_assignment": policy}
            argv = [str(codex_path), "sandbox", "-P", profile_name,
                    "--include-managed-config", "-C", str(packet), "-c", policy, "--"]
            argv += child_command + [str(packet / "child.py"), str(packet), str(forbidden),
                                     confined_nonce, str(server.port), canary_hash]
            print("PROBE: explicit managed-compatible synthetic sandbox", flush=True)
            result = command_runner(argv, packet, COMMAND_TIMEOUT_SECONDS)
            report["commands"].append(result)
            after_route = parent_nonce_exchange(server.port, after_nonce)
            report["parent_loopback_after"] = after_route
            parsed = parse_child_result(result, confined_nonce)
            report["confined_events"] = parsed
            after = fingerprint(run_root / "protected")
            report["protected_after"] = after
            final_status, checks = assess_boundary(result, parsed, canary_hash, before == after)
            report["filesystem_status"] = final_status
            report["filesystem_checks"] = checks
            network = parsed["rows"].get("loopback", {})
            confined_nonce_hash = sha256(confined_nonce.encode("ascii") + b"\n")
            report["loopback"] = {"host": "127.0.0.1", "port": server.port,
                "control_nonce_exchange_passed": True,
                "parent_before": before_route, "parent_after": after_route,
                "confined_event": network, "listener_events": list(server.observed),
                "listener_errors": list(server.errors),
                "scope": "Only this IPv4 host-loopback nonce route; no external network claim"}
            if (network.get("outcome") == "operation_succeeded"
                    or any(row["sha256"] == confined_nonce_hash for row in server.observed)):
                report["loopback"]["status"] = "TESTED_LOOPBACK_ROUTE_ACCESSIBLE"
            elif (before_route["passed"] and after_route["passed"]
                  and network.get("outcome") in ("denial_consistent_error", "unexpected_error")
                  and network.get("error_type") in ("PermissionError", "OSError",
                       "ConnectionRefusedError", "TimeoutError", "FileNotFoundError")):
                report["loopback"]["status"] = "TESTED_LOOPBACK_ROUTE_NOT_COMPLETED_WITH_LIVE_CONTROLS"
            else:
                report["loopback"]["status"] = "LOOPBACK_OBSERVATION_INCONCLUSIVE"
            if final_status == "OBSERVED_COMMAND_FILESYSTEM_DENIALS":
                if report["loopback"]["status"] == "TESTED_LOOPBACK_ROUTE_ACCESSIBLE":
                    final_status = "TESTED_LOOPBACK_BOUNDARY_VIOLATION"
                elif report["loopback"]["status"] == "TESTED_LOOPBACK_ROUTE_NOT_COMPLETED_WITH_LIVE_CONTROLS":
                    final_status = "OBSERVED_REQUESTED_COMMAND_BOUNDARIES"
                else:
                    final_status = "LOOPBACK_OBSERVATION_INCONCLUSIVE"
    except KeyboardInterrupt:
        final_status = "INTERRUPTED"
        report["reason"] = "Human interrupt; synthetic fixtures and captured outputs preserved"
    except Exception as exc:
        final_status = "HARNESS_ERROR"
        report["error"] = {"type": type(exc).__name__, "message": str(exc)}
    finally:
        report["observation_status"] = final_status
        report["status"] = "HARNESS_SIMULATION" if simulation else final_status
        report["finished_utc"] = datetime.now(timezone.utc).isoformat()
        digest = save_report(report_path, report)
        print("REPORT: " + str(report_path), flush=True)
        print("REPORT_SHA256: " + digest, flush=True)
        print("STATUS: " + report["status"], flush=True)
        print("This is a synthetic command test, not independent-review readiness.", flush=True)
    return report_path, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    lab_root = Path.home() / "ARC_Independent_Lab"
    codex = shutil.which("codex")
    if codex is None:
        print("STOP: Codex is not on PATH. No probe was launched.", file=sys.stderr)
        return 2
    try:
        _, report = run_harness(lab_root, codex)
    except (OSError, ValueError) as exc:
        print("STOP: " + str(exc), file=sys.stderr)
        return 2
    return 0 if report["status"] == "OBSERVED_REQUESTED_COMMAND_BOUNDARIES" else 2


if __name__ == "__main__":
    raise SystemExit(main())
