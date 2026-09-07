#!/usr/bin/env python3
"""One approved native browser sign-in; default inspection writes nothing.

Native terminal/browser output belongs to the human and is never captured.
An existing complete receipt is reused before any host measurement or launch.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import signal
import socket
import stat
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
SCOPE = "configs/GATE0_SIGNIN_SCOPE_015.json"
SCOPE_SHA256 = "6020d46ae6818f6c15341a7074ea4f7306b3764d8c64a92d0dcce745ed1c7ccd"
REPORT_KIND = "GATE0_HUMAN_SIGNIN_015_RECEIPT_v1"
RECEIPT_SCOPE = "Human native sign-in receipt; exit/presence only, no secret or raw native output retained"
WRAPPER = "scripts/gate0_human_signin.py"
SECRET_ENV = ("OPENAI_API_KEY", "CODEX_API_KEY", "CODEX_ACCESS_TOKEN")


class Stop(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise Stop(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def plain(path, directory=False):
    path = Path(path).absolute()
    require(".." not in path.parts, "Noncanonical path")
    cursor = Path(path.anchor)
    for part in path.parts[1:]:
        cursor /= part
        require(not cursor.is_symlink(), "Symlink in required path")
    info = path.stat()
    require(stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode),
            "Required path has wrong type")
    require(directory or info.st_nlink == 1, "Hardlinked required file rejected")
    return path


def bounded(path, maximum=1048576):
    path = plain(path)
    require(path.stat().st_size <= maximum, "Input exceeds bounded size")
    return path.read_bytes()


def metadata(path):
    info = plain(path).stat()
    return {"device": info.st_dev, "inode": info.st_ino, "bytes": info.st_size,
            "mode": stat.S_IMODE(info.st_mode), "mtime_ns": info.st_mtime_ns,
            "ctime_ns": info.st_ctime_ns}


def load_bundle(root):
    raw = bounded(root / SCOPE)
    require(sha(raw) == SCOPE_SHA256, "Sign-in scope changed")
    scope = json.loads(raw)
    require(scope["timeout_seconds"] == 300 and scope["callback_port"] == 1455,
            "Unexpected bounded sign-in scope")
    require(scope["native_login_argv"] == ["$HOME/" + scope["runtime_relative_to_home"], "login"],
            "Unexpected native command")
    observed_raw = bounded(root / scope["observed_report_path"])
    require(sha(observed_raw) == scope["observed_report_sha256"], "Accepted account report changed")
    source_raw = bounded(root / scope["source_manifest"])
    require(sha(source_raw) == scope["source_manifest_sha256"], "Audited source manifest changed")
    source_dir = (root / scope["source_manifest"]).parent
    for entry in json.loads(source_raw)["files"]:
        require(sha(bounded(source_dir / entry["path"])) == entry["sha256"], "Audited source file changed")
    return scope, json.loads(observed_raw), {
        "scope_sha256": sha(raw), "wrapper_sha256": sha(bounded(root / WRAPPER)),
        "observed_report_sha256": sha(observed_raw),
        "runtime_sha256": scope["runtime_sha256"],
        "source_manifest_sha256": sha(source_raw),
    }


def approval(root, pins):
    text = bounded(root / "state/ESCALATION.md").decode("utf-8")
    raw_lines, starts, fence = text.splitlines(), [], None
    for index, line in enumerate(raw_lines):
        stripped = line.lstrip(" ")
        indentation = len(line) - len(stripped)
        if indentation <= 3 and (stripped.startswith("```") or stripped.startswith("~~~")):
            character = stripped[0]
            length = len(stripped) - len(stripped.lstrip(character))
            if fence is None:
                fence = (character, length)
            elif character == fence[0] and length >= fence[1]:
                fence = None
            continue
        if fence is None and line == "## ANSWER":
            starts.append(index)
    require(bool(starts), "No recorded ANSWER; inspection only is authorized")
    require(len(starts) == 1, "Ambiguous multiple ANSWER sections; no login")
    answer = [line for line in raw_lines[starts[0] + 1:] if line.strip()]
    require(answer == ["APPROVE_G0_SIGNIN_015", "scope_sha256: " + pins["scope_sha256"]],
            "Recorded ANSWER must contain only the exact approval token and scope hash; restrictions/other text require review")


def auth_present(path):
    """Presence only. Never open, hash, copy, resolve or deserialize this path."""
    try:
        path.lstat()
        return True
    except FileNotFoundError:
        return False
    except OSError:
        return None


def preflight(root, scope, observed):
    require(os.name == "posix" and os.uname().sysname == "Linux", "This sign-in targets the observed WSL Linux installation")
    home = plain(scope["canonical_home"], True)
    require(os.environ.get("HOME") == str(home) and Path.home() == home, "HOME provenance changed; do not reassign it")
    require(root == home / "ARC_Independent_Lab" == Path(scope["canonical_project"]), "Use canonical project")
    codex_home = plain(home / ".codex", True)
    require("CODEX_HOME" not in os.environ or os.environ["CODEX_HOME"] == str(codex_home),
            "CODEX_HOME provenance changed; do not reassign it")
    require(not any(name in os.environ for name in SECRET_ENV), "An API-key/access-token environment variable is present; no value was inspected or printed")
    auth = codex_home / "auth.json"
    require(auth_present(auth) is False, "Credential path already exists or cannot be inspected; preserved without reading")
    for item in observed["origin_inventory"]:
        path = Path(item["path"])
        require(not path.is_symlink(), "Configuration origin is a symlink")
        present = os.path.lexists(path)
        require(present == item["present"], "Configuration origin presence changed")
        if present:
            require(metadata(path) == item["metadata"], "Configuration origin metadata changed")
            require(path == codex_home / "config.toml", "Unexpected additional configuration origin")
    # Read only the supported control fields; no raw config value enters output.
    config_path = codex_home / "config.toml"
    config = tomllib.loads(bounded(config_path).decode("utf-8"))
    require(not any(key in config for key in ("profile", "profiles", "include", "includes", "extends")),
            "Configuration composition/profile requires separate resolution; no assumed log/backend inheritance")
    observed_config = next(item["metadata"] for item in observed["origin_inventory"]
                           if item["path"] == str(config_path) and item["present"])
    require(metadata(config_path) == observed_config, "Configuration changed during control inspection")
    require(config.get("cli_auth_credentials_store", "file") == "file", "Configured credential backend changed")
    configured_log = config.get("log_dir", str(codex_home / "log"))
    require(type(configured_log) is str, "Configured log directory has unexpected type")
    log_dir = Path(configured_log)
    require(log_dir.is_absolute() and ".." not in log_dir.parts, "Configured log directory is not canonical")
    require(log_dir.is_relative_to(codex_home) or log_dir.is_relative_to(root), "Configured log directory is outside the approved native scope")
    cursor = Path(log_dir.anchor)
    for part in log_dir.parts[1:]:
        cursor /= part
        require(not cursor.is_symlink(), "Symlink in configured log directory")
    runtime = plain(home / scope["runtime_relative_to_home"])
    require(sha(runtime.read_bytes()) == scope["runtime_sha256"], "Installed runtime differs from audited binary")
    require(observed["observation"]["account_configuration"]["configured_backend"] == "file", "Accepted observation is not file-backed")
    cwd = plain(root / "delivery", True)
    require(auth_present(auth) is False, "Credential path appeared during inspection; preserved")
    return [str(runtime), "login"], cwd, auth


def callback_available(port):
    # This is a transient local bind, not a connection or an atomic reservation.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        try:
            probe.bind(("127.0.0.1", port))
        except OSError:
            raise Stop("Callback port is occupied/unavailable; no native login was launched") from None


def validate_receipt(report, pins):
    expected = {"kind", "pins", "created_utc", "native_started", "native_exit_code",
                "timed_out", "interrupted", "launch_failed", "auth_file_present",
                "model_invoked_by_wrapper", "account_live_verified", "allowance_verified",
                "reviewer_boundary_verified", "scope"}
    require(type(report) is dict and set(report) == expected, "Receipt contains missing or unexpected fields; raw values withheld")
    require(report.get("kind") == REPORT_KIND and report.get("pins") == pins, "Completed receipt has different provenance")
    require(report["scope"] == RECEIPT_SCOPE and type(report["created_utc"]) is str
            and len(report["created_utc"]) <= 40, "Receipt scope/timestamp differs")
    datetime.fromisoformat(report["created_utc"])
    require(type(report.get("native_exit_code")) is int or report.get("native_exit_code") is None,
            "Receipt exit code has wrong type")
    for key in ("timed_out", "interrupted", "launch_failed", "native_started"):
        require(type(report.get(key)) is bool, "Receipt flag has wrong type")
    require(type(report.get("auth_file_present")) is bool or report.get("auth_file_present") is None,
            "Receipt auth presence has wrong type")
    require(report.get("model_invoked_by_wrapper") is False and report.get("account_live_verified") is False
            and report.get("allowance_verified") is False and report.get("reviewer_boundary_verified") is False,
            "Receipt overstates observation")


def reuse(run, pins):
    if not os.path.lexists(run):
        return None
    plain(run, True)
    require({p.name for p in run.iterdir()} == {"ATTEMPT.json", "REPORT.json", "SHA256SUMS"},
            "Prior attempt is incomplete or has unexpected files; preserved, no automatic retry")
    sums = bounded(run / "SHA256SUMS").decode("ascii").splitlines()
    require(len(sums) == 2, "Completed receipt checksum list differs")
    for line, name in zip(sums, ("ATTEMPT.json", "REPORT.json")):
        require(line == sha(bounded(run / name)) + "  " + name, "Completed receipt checksum mismatch")
    attempt = json.loads(bounded(run / "ATTEMPT.json"))
    report = json.loads(bounded(run / "REPORT.json"))
    require(attempt["pins"] == pins, "Prior attempt source/scope changed")
    validate_receipt(report, pins)
    return report


def exclusive_json(path, value):
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())


def terminate_native(process):
    if process.poll() is None:
        process.send_signal(signal.SIGTERM)
        try:
            process.wait(timeout=4)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=4)


def execute_native(argv, cwd, seconds, *, popen=subprocess.Popen):
    flags = dict(native_started=False, native_exit_code=None, timed_out=False,
                 interrupted=False, launch_failed=False)
    process = None
    try:
        # Inherit human TTY; never PIPE, redirect, tee or retain login output.
        process = popen(argv, cwd=str(cwd), stdin=None, stdout=None, stderr=None)
        flags["native_started"] = True
        flags["native_exit_code"] = process.wait(timeout=seconds)
    except subprocess.TimeoutExpired:
        flags["timed_out"] = True
        terminate_native(process)
        flags["native_exit_code"] = process.returncode
    except KeyboardInterrupt:
        flags["interrupted"] = True
        if process is not None:
            terminate_native(process)
            flags["native_exit_code"] = process.returncode
    except OSError:
        flags["launch_failed"] = True
        if process is not None:
            terminate_native(process)
            flags["native_exit_code"] = process.returncode
    return flags


def run(root, sign_in=False):
    scope, observed, pins = load_bundle(root)
    run_dir = root / scope["report_directory"]
    completed = reuse(run_dir, pins)
    if completed is not None:
        return {"status": "REUSED_VERIFIED_RECEIPT_NO_HOST_REMEASUREMENT", "report": str(run_dir / "REPORT.json"), **completed}
    if sign_in:
        approval(root, pins)
    argv, cwd, auth = preflight(root, scope, observed)
    if not sign_in:
        return {"status": "INSPECTION_ONLY_NO_WRITES_NETWORK_OR_LOGIN", "pins": pins,
                "native_argv_after_approval": argv, "native_cwd": str(cwd),
                "timeout_seconds": scope["timeout_seconds"],
                "callback_availability": "checked_only_immediately_before_approved_launch",
                "authorization": "requires_recorded_answer_for_exact_scope"}
    require(all(stream.isatty() for stream in (sys.stdin, sys.stdout, sys.stderr)), "Native login requires your interactive terminal; no redirected output")
    callback_available(scope["callback_port"])
    require(sha(bounded(root / WRAPPER)) == pins["wrapper_sha256"] and
            sha(bounded(root / SCOPE)) == pins["scope_sha256"], "Wrapper/scope changed during inspection")
    require(auth_present(auth) is False, "Credential path appeared before launch; preserved")
    run_dir.mkdir(mode=0o700)
    attempt = {"kind": "GATE0_HUMAN_SIGNIN_015_ATTEMPT_v1", "pins": pins,
               "created_utc": datetime.now(timezone.utc).isoformat(), "timeout_seconds": scope["timeout_seconds"]}
    exclusive_json(run_dir / "ATTEMPT.json", attempt)
    flags = execute_native(argv, cwd, scope["timeout_seconds"])
    report = {"kind": REPORT_KIND, "pins": pins,
              "created_utc": datetime.now(timezone.utc).isoformat(), **flags,
              "auth_file_present": auth_present(auth), "model_invoked_by_wrapper": False,
              "account_live_verified": False, "allowance_verified": False,
              "reviewer_boundary_verified": False,
              "scope": RECEIPT_SCOPE}
    validate_receipt(report, pins)
    exclusive_json(run_dir / "REPORT.json", report)
    with (run_dir / "SHA256SUMS").open("x", encoding="ascii") as handle:
        for name in ("ATTEMPT.json", "REPORT.json"):
            handle.write(sha(bounded(run_dir / name)) + "  " + name + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    return {"status": "RECORDED_HUMAN_SIGNIN_RECEIPT", "report": str(run_dir / "REPORT.json"), **report}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sign-in", action="store_true")
    args = parser.parse_args()
    try:
        result = run(ROOT, args.sign_in)
        print(json.dumps(result, indent=2))
        return 0
    except (Stop, OSError, ValueError, KeyError, TypeError):
        # No raw exception/config/native text: errors can contain private values.
        error = sys.exc_info()[1]
        print("STOP: " + (str(error) if isinstance(error, Stop) else "Input/state validation or native cleanup failed; preserved without retry"), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
