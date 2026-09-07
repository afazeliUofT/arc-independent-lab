#!/usr/bin/env python3
"""Bounded, network-disabled app-server startup observation on the canonical WSL lab.

Default is inspection. --run-preflight creates only a new delivery directory and
executes the existing pinned client inside a direct bubblewrap namespace. It
sends initialize, config/read and configRequirements/read only. No thread,
scientific input, model request, login, config write or quota operation exists.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import selectors
import resource
import shutil
import signal
import stat
import subprocess
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_SHA256 = "9739cbc928b9c573be83256acd46668f5dd4f119d2d09e05246895ca2aaf0c9a"
SCHEMA_SHA256 = "ed663d6d4c6c8b36917596882414c93858f6cf9ca5449ea8c616fc76d1aac114"
WALL_SECONDS = 60
STREAM_LIMIT = 2 * 1024 * 1024
TREE_LIMIT = 64 * 1024 * 1024
FALSE_FEATURES = (
    "plugins", "remote_plugin", "plugin_hooks", "apps", "connectors", "enable_mcp_apps",
    "hooks", "codex_hooks", "memories", "memory_tool", "external_agent_memory_import",
    "goals", "remote_control", "multi_agent", "multi_agent_v2", "collab", "enable_fanout",
    "send_async_message", "code_mode", "code_mode_only", "code_mode_prewarm", "js_repl",
    "shell_tool", "unified_exec", "experimental_use_unified_exec_tool", "apply_patch_freeform",
    "view_image", "web_search", "web_search_cached", "web_search_request", "browser_use",
    "computer_use", "tool_search", "token_budget", "skill_search", "shell_snapshot",
    "background_paginated_rollout_migration", "auth_elicitation", "unbounded_connection_retries",
)


class Stop(RuntimeError):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise Stop(message)


def plain(path, directory=False):
    path = Path(path).absolute()
    require(".." not in path.parts, "Noncanonical path")
    current = Path("/")
    for component in path.parts[1:]:
        current /= component
        require(not current.is_symlink(), "Symlink in required path; no automatic expansion")
    info = path.stat()
    require(stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode),
            "Required path has wrong type")
    require(directory or info.st_nlink == 1, "Hardlinked required file rejected")
    return path


def signature(path, content=True):
    info = path.stat()
    result = {"device": info.st_dev, "inode": info.st_ino, "bytes": info.st_size,
              "mode": stat.S_IMODE(info.st_mode), "mtime_ns": info.st_mtime_ns,
              "ctime_ns": info.st_ctime_ns}
    if content:
        result["sha256"] = digest(path.read_bytes())
    return result


def identity_bytes(path):
    path = plain(path)
    require(path.stat().st_size <= 64 and stat.S_IMODE(path.stat().st_mode) == 0o644,
            "Existing installation identifier must be bounded and already mode0644")
    raw = path.read_bytes()
    try:
        parsed = uuid.UUID(raw.decode("utf-8").strip())
    except (ValueError, UnicodeError):
        raise Stop("Existing installation identifier is invalid; no repair authorized") from None
    require(str(parsed) == raw.decode("utf-8").strip(), "Identifier must be canonical UUID text")
    return raw


def inventory():
    require(os.name == "posix" and os.uname().sysname == "Linux", "This observation targets WSL Linux")
    home = plain(Path.home(), True)
    require(ROOT == home / "ARC_Independent_Lab", "Run only in canonical ~/ARC_Independent_Lab")
    require(os.environ.get("HOME") == str(home), "Existing HOME is unexpected; do not reassign it")
    codex_home = plain(Path(os.environ.get("CODEX_HOME", str(home / ".codex"))), True)
    runtime = plain(codex_home / "packages/standalone/releases/0.151.0-x86_64-unknown-linux-musl/bin/codex")
    require(digest(runtime.read_bytes()) == RUNTIME_SHA256, "Runtime differs from source-audited binary")
    found = shutil.which("bwrap")
    require(found is not None, "System bwrap is unavailable; no client was launched")
    bwrap = plain(Path(found).resolve(strict=True))
    identifier = plain(codex_home / "installation_id")
    raw_id = identity_bytes(identifier)
    identifier_before = signature(identifier)
    require(digest(raw_id) == identifier_before["sha256"],
            "Installation identifier changed during inspection; no copy or launch")
    # Metadata only for auth: the parent never reads/copies credential bytes.
    existing = []
    observations = []
    candidates = [Path("/etc/codex/config.toml"), Path("/etc/codex/requirements.toml"),
                  Path("/etc/codex/managed_config.toml"), codex_home / "config.toml",
                  codex_home / ".env", codex_home / "auth.json"]
    # Observe each ancestor config that could be selected at the future run cwd.
    plain(ROOT / "delivery", True)
    for ancestor in (ROOT / "delivery", ROOT, *ROOT.parents):
        candidates.append(ancestor / ".codex/config.toml")
    for path in dict.fromkeys(candidates):
        require(not path.is_symlink(), "Symlink at configuration origin; stop for exact resolution")
        present = path.exists()
        item = {"path": str(path), "present": present}
        if present:
            plain(path)
            existing.append(path)
            # Even config/.env can contain secrets. Only metadata enters report.
            item["metadata"] = signature(path, content=False)
        observations.append(item)
    return {"home": home, "codex_home": codex_home, "runtime": runtime,
            "bwrap": bwrap, "identifier": identifier, "identifier_bytes": raw_id,
            "readonly_paths": existing, "origins": observations,
            "runtime_before": signature(runtime), "bwrap_before": signature(bwrap),
            "identifier_before": identifier_before}


def overrides(run):
    schema_path = ROOT / "artifacts/GATE0_CODEX_INTERFACE/20260907_001/config-schema.json"
    require(digest(schema_path.read_bytes()) == SCHEMA_SHA256, "Pinned config syntax source changed")
    schema = json.loads(schema_path.read_bytes())
    require(set(FALSE_FEATURES) <= set(schema["properties"]["features"]["properties"]),
            "Unsupported feature override in source-audited schema")
    result = {"sqlite_home": str(run / "runtime_state"), "log_dir": str(run / "runtime_logs"),
              "history.persistence": "none", "web_search": "disabled", "agents.enabled": False,
              "memories.generate_memories": False, "memories.use_memories": False,
              "orchestrator.skills.enabled": False, "tools.update_plan.enabled": False,
              "tools.experimental_request_user_input.enabled": False,
              "analytics.enabled": False, "approval_policy": "never"}
    result.update({"features." + name: False for name in FALSE_FEATURES})
    return result


def restricted_env():
    # Preserve the actual values, never repurpose HOME/CODEX_HOME. No API keys,
    # proxy settings, inherited command hooks or credential env are forwarded.
    result = {"HOME": os.environ["HOME"], "PATH": "/usr/bin:/bin", "LANG": "C.UTF-8",
              "RUST_LOG": "off", "CODEX_INTERNAL_APP_SERVER_REMOTE_CONTROL_DISABLED": "1"}
    if "CODEX_HOME" in os.environ:
        result["CODEX_HOME"] = os.environ["CODEX_HOME"]
    return result


def _strict_object(items):
    value = {}
    for key, item in items:
        require(key not in value, "Duplicate protocol field")
        value[key] = item
    return value


def parse_line(raw):
    def invalid(_):
        raise Stop("Nonfinite protocol number")
    try:
        result = json.loads(raw, object_pairs_hook=_strict_object, parse_constant=invalid)
    except (ValueError, UnicodeError):
        raise Stop("Invalid protocol JSON; raw content withheld") from None
    require(type(result) is dict, "Protocol envelope must be an object")
    return result


def safe_config(result, requested):
    require(type(result) is dict and type(result.get("config")) is dict,
            "Missing structured effective config")
    config = result["config"]
    controls = {}
    for dotted, expected in requested.items():
        value = config
        for component in dotted.split("."):
            value = value.get(component) if type(value) is dict else None
        # Never serialize unexpected raw string/object values from config.
        controls[dotted] = {"present": value is not None,
                            "equals_requested": type(value) is type(expected) and value == expected}
    return {"controls": controls,
            "all_requested_controls_observed": all(v["equals_requested"] for v in controls.values()),
            "origins_object_present": type(result.get("origins")) is dict,
            "layers_array_present": type(result.get("layers")) is list,
            "managed_requirements_verified": False}


def tree_size(root):
    total, count = 0, 0
    for directory, dirs, files in os.walk(root, followlinks=False):
        for name in dirs + files:
            path = Path(directory) / name
            info = path.lstat(); count += 1
            require(count <= 4096, "Runtime tree entry ceiling")
            if stat.S_ISREG(info.st_mode): total += info.st_size
            require(not stat.S_ISLNK(info.st_mode), "Unexpected runtime symlink")
    return total


def child_limits():
    resource.setrlimit(resource.RLIMIT_FSIZE, (8 * 1024 * 1024, 8 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_CPU, (30, 31))


def observe(plan, run, requested):
    """Real finite subprocess transport. No raw configuration/auth transcript file."""
    steps = [("initialize", {"clientInfo": {"name": "arc_reviewer_preflight", "version": "1"},
                             "capabilities": {"experimentalApi": True, "extensions": {}}}),
             ("config/read", {"cwd": str(run), "includeLayers": True}),
             ("configRequirements/read", {})]
    report = {"requests_sent": [], "responses": [], "server_requests_dispatched": 0,
              "thread_or_model_request_sent": False}
    try:
        process = subprocess.Popen(plan["argv"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, cwd=run, env=restricted_env(),
                                   start_new_session=True, preexec_fn=child_limits)
    except OSError:
        return {**report, "status": "STOPPED_WITHOUT_REVIEW",
                "reason": "Outer executable could not start", "client_started": False}
    selector = selectors.DefaultSelector()
    buffers = {"stdout": bytearray(), "stderr": bytearray()}
    totals = {"stdout": 0, "stderr": 0}
    hashes = {key: hashlib.sha256() for key in totals}
    for stream, name in ((process.stdout, "stdout"), (process.stderr, "stderr")):
        os.set_blocking(stream.fileno(), False); selector.register(stream, selectors.EVENT_READ, name)
    end = time.monotonic() + WALL_SECONDS
    index = 0

    def send_next():
        method, params = steps[index]
        payload = json.dumps({"id": index + 1, "method": method, "params": params}).encode() + b"\n"
        process.stdin.write(payload); process.stdin.flush()
        report["requests_sent"].append(method)

    try:
        send_next()
        while index < len(steps):
            require(time.monotonic() < end, "Startup observation deadline")
            require(tree_size(run) <= TREE_LIMIT, "Runtime tree byte ceiling")
            events = selector.select(timeout=0.1)
            for key, _ in events:
                data = os.read(key.fileobj.fileno(), 65536)
                if not data:
                    selector.unregister(key.fileobj); continue
                name = key.data; totals[name] += len(data); hashes[name].update(data)
                require(totals[name] <= STREAM_LIMIT, "Protocol/diagnostic stream ceiling")
                buffers[name].extend(data)
                if name != "stdout": continue
                while b"\n" in buffers[name]:
                    line, _, rest = buffers[name].partition(b"\n"); buffers[name] = bytearray(rest)
                    msg = parse_line(line)
                    require(not ("method" in msg and "id" in msg),
                            "Unexpected server request; no permission/auth response sent")
                    if "method" in msg:
                        # Startup notices do not authorize anything. Record count
                        # only; their parameters are not public output.
                        report["notifications_received"] = report.get("notifications_received", 0) + 1
                        continue
                    require(index < len(steps), "Unexpected response after completion")
                    require(set(msg) <= {"id", "result", "error"} and type(msg.get("id")) is int
                            and msg["id"] == index + 1, "Unbound/foreign response")
                    require("error" not in msg and type(msg.get("result")) is dict,
                            "Client returned an error; raw payload withheld")
                    method = steps[index][0]
                    if method == "config/read":
                        report["effective_config"] = safe_config(msg["result"], requested)
                    elif method == "configRequirements/read":
                        require(type(msg["result"]) is dict, "Invalid requirements response")
                        report["requirements_present"] = msg["result"].get("requirements") is not None
                        report["requirements_verified"] = False
                    report["responses"].append({"method": method, "received": True})
                    index += 1
                    if index == 1:
                        process.stdin.write(b'{"method":"initialized","params":{}}\n'); process.stdin.flush()
                    if index < len(steps): send_next()
            require(process.poll() is None or index == len(steps), "Confined client exited before completion")
        report["status"] = "OBSERVED_STARTUP_AND_CONFIG_RESPONSES_ONLY"
    except (Stop, OSError) as error:
        report["status"] = "STOPPED_WITHOUT_REVIEW"
        report["reason"] = str(error) if isinstance(error, Stop) else "Host subprocess/pipe operation failed"
    finally:
        # No retry, continuation, thread or scientific verdict on any outcome.
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGTERM)
            try: process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL); process.wait(timeout=2)
        selector.close()
        for stream in (process.stdin, process.stdout, process.stderr): stream.close()
        report["client_exit_code"] = process.returncode
        report["streams"] = {name: {"bytes_observed": totals[name], "sha256_observed": hashes[name].hexdigest()}
                             for name in totals}
        report["raw_config_auth_or_diagnostics_saved"] = False
        diagnostic = bytes(buffers["stderr"]).lower()
        report["diagnostic_categories_observed"] = {
            label: needle in diagnostic for label, needle in (
                ("permission_denied", b"permission denied"),
                ("missing_dependency", b"no such file or directory"),
                ("unknown_cli_argument", b"unexpected argument"),
                ("configuration_load_error", b"failed to load"),
                ("default_fallback_warning", b"falling back"),
                ("namespace_permission", b"operation not permitted"))}
    return report


def run_preflight(facts):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    # Validate the existing parent before the first write: mount-plan validation
    # happens later and cannot undo a mkdir through a symlinked delivery folder.
    plain(ROOT, True)
    delivery = plain(ROOT / "delivery", True)
    run = delivery / ("GATE0_CLIENT_PREFLIGHT_" + stamp)
    run.mkdir(mode=0o700)
    for name in ("runtime_state", "runtime_logs"):
        (run / name).mkdir(mode=0o700)
    copy = run / "installation_id_copy"
    with copy.open("xb") as stream: stream.write(facts["identifier_bytes"])
    copy.chmod(0o644)
    requested = overrides(run)
    command = [str(facts["runtime"])]
    for key, value in requested.items(): command += ["-c", key + "=" + json.dumps(value)]
    command += ["app-server", "--strict-config", "--stdio"]
    spec = importlib.util.spec_from_file_location("gate0_client_mount_plan", ROOT / "scripts/gate0_client_mount_plan.py")
    helper = importlib.util.module_from_spec(spec); spec.loader.exec_module(helper)
    plan = helper.build_mount_plan(bwrap_path=facts["bwrap"], runtime_path=facts["runtime"],
                lab_root=ROOT, run_root=run, home_path=facts["home"], codex_home_path=facts["codex_home"],
                identity_copy_path=copy, readonly_paths=facts["readonly_paths"],
                writable_paths=[run / "runtime_state", run / "runtime_logs"], command_argv=command)
    report = {"schema_version": 1, "created_utc": datetime.now(timezone.utc).isoformat(),
              "scope": "No-model outer-startup observation; not complete reviewer isolation",
              "origin_inventory": facts["origins"], "mount_plan": plan,
              "runtime_before": facts["runtime_before"], "bwrap_before": facts["bwrap_before"],
              "limits": {"wall_seconds": WALL_SECONDS, "per_stream_bytes": STREAM_LIMIT,
                         "runtime_tree_bytes_polled": TREE_LIMIT},
              "model_called_by_protocol": False, "formal_verdict": None,
              "unattended_model_use_authorized": False}
    report["observation"] = observe(plan, run, requested)
    report["host_runtime_unchanged"] = signature(facts["runtime"]) == facts["runtime_before"]
    report["host_bwrap_unchanged"] = signature(facts["bwrap"]) == facts["bwrap_before"]
    report["host_installation_id_unchanged"] = signature(facts["identifier"]) == facts["identifier_before"]
    report["identifier_copy_matches_original"] = copy.read_bytes() == facts["identifier_bytes"]
    report["original_observed_origin_metadata_unchanged"] = all(
        signature(Path(item["path"]), content=False) == item["metadata"]
        for item in facts["origins"] if item["present"])
    data = (json.dumps(report, indent=2) + "\n").encode()
    path = run / "REPORT.json"
    with path.open("xb") as stream:
        stream.write(data); stream.flush(); os.fsync(stream.fileno())
    require(path.read_bytes() == data, "Final report readback mismatch")
    print("REPORT: " + str(path))
    print("REPORT_SHA256: " + digest(data))
    print("No scientific review or model turn was requested. Full reviewer boundary remains unverified.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-preflight", action="store_true")
    args = parser.parse_args()
    try:
        facts = inventory()
        print("Verified exact installed runtime; inspected required paths without reading credentials.")
        print("Plan: direct bwrap network denial; same installation identifier in lab backing file; host originals read-only.")
        if args.run_preflight:
            run_preflight(facts)
        else:
            print("Inspection only. No client, network or filesystem change was made.")
    except (Stop, OSError, ValueError) as error:
        print("STOP: " + (str(error) if isinstance(error, Stop) else "Required local dependency is unavailable; no automatic repair."))
        raise SystemExit(2)


if __name__ == "__main__":
    main()
