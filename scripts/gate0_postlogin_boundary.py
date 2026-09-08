"""Test one synthetic file bind before granting native credential refresh access.

Only fresh project fixture files and system runtime dependencies are mounted.
The child makes no network calls. Passing does not certify a reviewer boundary.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import selectors
import signal
import stat
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
TIMEOUT_SECONDS = 10
CLEANUP_SECONDS = 2
STREAM_LIMIT = 8192
REPLACEMENT = b"synthetic native-pattern replacement\n"
CONTROL = b"synthetic readonly control\n"
CHILD = '''import errno, json, os, sys
from pathlib import Path
parent = Path(sys.argv[1])
os.makedirs(parent, exist_ok=True)
fd = os.open(parent / "synthetic_auth.json", os.O_WRONLY | os.O_TRUNC | os.O_CREAT, 0o600)
os.write(fd, b"synthetic native-pattern replacement\\n")
os.fsync(fd)
os.close(fd)
def denied(path, flags):
    try:
        fd = os.open(path, flags, 0o600)
    except OSError as error:
        return error.errno in (errno.EPERM, errno.EACCES, errno.EROFS)
    os.close(fd)
    return False
checks = {
    "existing_parent_create_dir_all_completed": True,
    "same_file_write_completed": True,
    "sibling_create_denied": denied(parent / "forbidden_sibling", os.O_WRONLY | os.O_CREAT | os.O_EXCL),
    "readonly_file_write_denied": denied(parent / "readonly_control", os.O_WRONLY | os.O_TRUNC),
    "network_requests_made": False,
}
print(json.dumps(checks))
raise SystemExit(0 if checks["sibling_create_denied"] and checks["readonly_file_write_denied"] else 4)
'''
EXPECTED = {
    "existing_parent_create_dir_all_completed": True,
    "same_file_write_completed": True,
    "sibling_create_denied": True,
    "readonly_file_write_denied": True,
    "network_requests_made": False,
}


def _plain(path, directory=False):
    path = Path(path)
    if not path.is_absolute() or ".." in path.parts or path.resolve(strict=True) != path:
        raise ValueError("Noncanonical boundary-test path")
    info = path.stat()
    if directory:
        if not stat.S_ISDIR(info.st_mode):
            raise ValueError("Boundary-test directory unavailable")
    elif not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise ValueError("Boundary-test file is not one ordinary file")
    return path


def build_argv(bwrap, fixture):
    """Prepare the synthetic namespace; never grant actual home or credential paths."""
    argv = [str(bwrap), "--unshare-all", "--share-net", "--unshare-user",
            "--die-with-parent", "--new-session", "--tmpfs", "/", "--ro-bind", "/usr", "/usr"]
    for name in ("/lib", "/lib64", "/bin"):
        path = Path(name)
        if path.is_symlink():
            target = path.resolve(strict=True)
            if not target.is_relative_to(Path("/usr")) or not target.is_dir():
                raise ValueError("Unsupported system alias topology")
            argv += ["--symlink", os.readlink(path), name]
        elif path.is_dir():
            argv += ["--ro-bind", name, name]
    fake = fixture / "synthetic_auth.json"
    argv += ["--ro-bind", str(fixture), str(fixture), "--bind", str(fake), str(fake),
             "--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp", "--remount-ro", "/",
             "--cap-drop", "ALL", "--chdir", str(fixture), "--", "/usr/bin/python3", "-I",
             str(fixture / "child.py"), str(fixture)]
    return argv


def _parsed_checks(raw):
    def unique(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("Duplicate fixture result key")
            result[key] = value
        return result
    value = json.loads(raw, object_pairs_hook=unique)
    return (type(value) is dict and set(value) == set(EXPECTED)
            and all(type(value[key]) is bool and value[key] is expected
                    for key, expected in EXPECTED.items()))


def _execute(argv, fixture):
    result = {"exit_code": None, "timed_out": False, "stream_ceiling_exceeded": False,
              "launch_failed": False, "cleanup_finished": True, "child_checks_passed": False,
              "stdout_bytes": 0, "stderr_bytes": 0, "stderr_categories": {}}
    try:
        process = subprocess.Popen(argv, cwd=fixture, stdin=subprocess.DEVNULL,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"},
                                   start_new_session=True)
    except OSError:
        result["launch_failed"] = True
        return result
    selector = selectors.DefaultSelector()
    buffers = {"stdout": bytearray(), "stderr": bytearray()}
    for stream, name in ((process.stdout, "stdout"), (process.stderr, "stderr")):
        os.set_blocking(stream.fileno(), False)
        selector.register(stream, selectors.EVENT_READ, name)
    deadline = time.monotonic() + TIMEOUT_SECONDS
    try:
        while selector.get_map() or process.poll() is None:
            if time.monotonic() >= deadline:
                result["timed_out"] = True
                break
            for key, _ in selector.select(timeout=0.05):
                raw = os.read(key.fileobj.fileno(), 4096)
                if not raw:
                    selector.unregister(key.fileobj)
                    continue
                name = key.data
                result[name + "_bytes"] += len(raw)
                buffers[name].extend(raw[:max(0, STREAM_LIMIT - len(buffers[name]))])
                if result[name + "_bytes"] > STREAM_LIMIT:
                    result["stream_ceiling_exceeded"] = True
                    break
            if result["stream_ceiling_exceeded"]:
                break
    finally:
        if process.poll() is None:
            for signum in (signal.SIGTERM, signal.SIGKILL):
                try:
                    os.killpg(process.pid, signum)
                except ProcessLookupError:
                    pass
                try:
                    process.wait(timeout=CLEANUP_SECONDS / 2)
                    break
                except subprocess.TimeoutExpired:
                    continue
        result["cleanup_finished"] = process.poll() is not None
        result["exit_code"] = process.poll()
        selector.close()
        for stream in (process.stdout, process.stderr):
            stream.close()
    if not result["timed_out"] and not result["stream_ceiling_exceeded"]:
        try:
            result["child_checks_passed"] = _parsed_checks(buffers["stdout"])
        except (ValueError, UnicodeError):
            pass
    diagnostic = bytes(buffers["stderr"]).lower()
    result["stderr_categories"] = {
        "namespace_permission": b"operation not permitted" in diagnostic,
        "missing_overflowuid": b"/proc/sys/kernel/overflowuid" in diagnostic,
        "missing_dependency": b"no such file or directory" in diagnostic,
        "permission_denied": b"permission denied" in diagnostic,
    }
    return result


def check(facts, run):
    """Return a sanitized result; the caller must refuse native startup unless passed."""
    report = {"kind": "GATE0_POSTLOGIN_SYNTHETIC_BIND_v1", "passed": False,
              "native_codex_executed": False, "real_credential_granted": False,
              "real_credential_read_hashed_or_copied": False, "network_requests_sent": False,
              "network_mode": "inherited_host_network_without_child_network_calls",
              "full_reviewer_boundary_verified": False, "timeout_seconds": TIMEOUT_SECONDS,
              "cleanup_seconds": CLEANUP_SECONDS, "stream_limit_per_stream": STREAM_LIMIT}
    try:
        run = _plain(run, directory=True)
        root = _plain(ROOT, directory=True)
        if run == root or not run.is_relative_to(root):
            raise ValueError("Fixture must be a strict project descendant")
        bwrap = _plain(facts["bwrap"])
        if hashlib.sha256(bwrap.read_bytes()).hexdigest() != facts["bwrap_before"]["sha256"]:
            raise ValueError("Boundary executable differs from inspected bytes")
        fixture = run / "synthetic_boundary"
        fixture.mkdir(mode=0o700)
        for name, content in (("synthetic_auth.json", b"synthetic initial content\n"),
                              ("readonly_control", CONTROL), ("child.py", CHILD.encode())):
            with (fixture / name).open("xb") as stream:
                stream.write(content)
            (fixture / name).chmod(0o600)
        argv = build_argv(bwrap, fixture)
        report["argv"] = argv
        result = _execute(argv, fixture)
        report["observation"] = result
        fake_ok = (fixture / "synthetic_auth.json").read_bytes() == REPLACEMENT
        control_ok = (fixture / "readonly_control").read_bytes() == CONTROL
        sibling_absent = not os.path.lexists(fixture / "forbidden_sibling")
        report["host_fixture_checks"] = {"exact_replacement": fake_ok,
                                           "readonly_control_unchanged": control_ok,
                                           "sibling_absent": sibling_absent}
        report["passed"] = (result["exit_code"] == 0 and result["cleanup_finished"]
                            and result["child_checks_passed"] and not result["timed_out"]
                            and not result["stream_ceiling_exceeded"] and fake_ok and control_ok
                            and sibling_absent)
    except (OSError, ValueError, KeyError):
        report["reason"] = "Synthetic prerequisite or fixed fixture unavailable; no retry or native grant"
    return report
