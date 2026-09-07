#!/usr/bin/env python3
"""Bounded, no-model installed JSON-schema capture; no reviewer or server session.

Run without options in WSL. Only the fixed installed Codex 0.151.0 executable is
used. Results stay in a fresh ~/ARC_Independent_Lab/delivery directory. Importable
substituted runners/inspectors always produce HARNESS_SIMULATION reports.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import resource
import selectors
import signal
import stat
import subprocess
import time
import uuid
import zipfile

DEPENDENCY_SHA256 = "e8b6e4c52dfd81fc8b797ebb699297975a7026472f5c43de6e73267a31100e41"
RUNTIME_SHA256 = "9739cbc928b9c573be83256acd46668f5dd4f119d2d09e05246895ca2aaf0c9a"
PROBE_ID = "GATE0_REVIEWER_INTERFACE_SCHEMA_v1"
MAX_STREAM_BYTES = 1024 * 1024
MAX_SCHEMA_BYTES = 8 * 1024 * 1024
MAX_TREE_BYTES = 32 * 1024 * 1024
MAX_TREE_ENTRIES = 4096
MAX_TREE_DEPTH = 12
TIMEOUT_SECONDS = 40

DEPENDENCY = Path(__file__).resolve().with_name("gate0_reviewer_boundary_probe.py")
if hashlib.sha256(DEPENDENCY.read_bytes()).hexdigest() != DEPENDENCY_SHA256:
    raise RuntimeError("STOP: Pinned boundary-probe dependency differs; nothing was launched")
_spec = importlib.util.spec_from_file_location("arc_pinned_boundary", DEPENDENCY)
boundary = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(boundary)
sha256 = boundary.sha256
captured_bytes = boundary.captured_bytes
inspect_runtime_executable = boundary.inspect_runtime_executable
save_report = boundary.save_report


def tree_inventory(root: Path):
    """Bounded metadata walk; never follow links, including during generation."""
    records, pending, total = {}, [(root, 0)], 0
    while pending:
        directory, depth = pending.pop()
        if depth > MAX_TREE_DEPTH:
            raise ValueError("Schema directory depth exceeds limit")
        with os.scandir(directory) as entries:
            for entry in entries:
                if len(records) >= MAX_TREE_ENTRIES:
                    raise ValueError("Schema tree exceeds entry limit")
                if not re.fullmatch(r"[A-Za-z0-9_.-]+", entry.name) or entry.name in (".", ".."):
                    raise ValueError("Unsafe schema entry name")
                metadata = entry.stat(follow_symlinks=False)
                path = directory / entry.name
                relative = path.relative_to(root).as_posix()
                if stat.S_ISDIR(metadata.st_mode):
                    records[relative] = {"kind": "directory"}
                    pending.append((path, depth + 1))
                elif stat.S_ISREG(metadata.st_mode) and metadata.st_nlink == 1:
                    if metadata.st_size > MAX_SCHEMA_BYTES:
                        raise ValueError("Schema file exceeds per-file limit")
                    total += metadata.st_size
                    if total > MAX_TREE_BYTES:
                        raise ValueError("Schema tree exceeds monitored byte limit")
                    records[relative] = {"kind": "file", "bytes": metadata.st_size}
                else:
                    raise ValueError("Schema tree contains a link or nonordinary entry")
    return records


def _child_limits():
    # Hard per-file/CPU bounds; total tree size is a monitored, not atomic quota.
    resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_SCHEMA_BYTES, MAX_SCHEMA_BYTES))
    resource.setrlimit(resource.RLIMIT_CPU, (30, 31))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def run_bounded(argv, cwd, timeout_seconds=TIMEOUT_SECONDS, monitor_root=None):
    """Bounded stdout/stderr, own process group, and bounded pipe cleanup."""
    started = time.monotonic()
    result = {"argv": list(argv), "cwd": str(cwd), "timeout_seconds": timeout_seconds}
    buffers = {"stdout": bytearray(), "stderr": bytearray()}
    process, selector = None, selectors.DefaultSelector()
    status, stopping, killed = "completed", None, False
    try:
        process = subprocess.Popen(argv, cwd=cwd, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True,
            preexec_fn=_child_limits)
        for name in buffers:
            stream = getattr(process, name)
            os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_READ, name)
        while selector.get_map() or process.poll() is None:
            now = time.monotonic()
            try:
                if stopping is None and now - started > timeout_seconds:
                    status, stopping = "timeout", now
                if stopping is None and monitor_root is not None:
                    tree_inventory(monitor_root)
                events = selector.select(0.05)
                for key, _ in events:
                    block = os.read(key.fileobj.fileno(), 65536)
                    if not block:
                        selector.unregister(key.fileobj)
                        key.fileobj.close()
                        continue
                    target = buffers[key.data]
                    remaining = MAX_STREAM_BYTES - len(target)
                    target.extend(block[:remaining])
                    if len(block) > remaining and stopping is None:
                        status, stopping = "output_limit", time.monotonic()
                        result["output_truncated"] = True
            except KeyboardInterrupt:
                status, stopping = "interrupted", time.monotonic()
            except (OSError, ValueError) as exc:
                if stopping is None:
                    status, stopping = "output_tree_rejected", time.monotonic()
                result["monitor_error"] = {"type": type(exc).__name__, "message": str(exc)}
            if stopping is not None:
                if not result.get("termination_sent"):
                    try:
                        os.killpg(process.pid, signal.SIGTERM)
                    except ProcessLookupError:
                        pass
                    result["termination_sent"] = True
                if time.monotonic() - stopping >= 1 and not killed:
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    killed = True
                if time.monotonic() - stopping >= 3:
                    result["output_capture_incomplete"] = bool(selector.get_map())
                    result["descendant_exit_not_established"] = bool(selector.get_map())
                    break
        process.poll()
        result.update(status=status, exit_code=process.returncode)
    except OSError as exc:
        result.update(status="launch_error", exit_code=None,
                      error={"type": type(exc).__name__, "message": str(exc)})
    finally:
        for key in list(selector.get_map().values()):
            selector.unregister(key.fileobj)
            key.fileobj.close()
        selector.close()
    result.update({name: captured_bytes(bytes(value)) for name, value in buffers.items()})
    result["elapsed_seconds"] = time.monotonic() - started
    return result


def _read_schemas(root):
    before = tree_inventory(root)
    payload = {}
    for relative, record in sorted(before.items()):
        if record["kind"] != "file":
            continue
        if not relative.endswith(".json"):
            raise ValueError("Schema generator produced a non-JSON file")
        path = root / relative
        # Resolve each component relative to an open directory, rejecting links.
        descriptor = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            parts = Path(relative).parts
            for part in parts[:-1]:
                child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
                os.close(descriptor)
                descriptor = child
            file_descriptor = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=descriptor)
            with os.fdopen(file_descriptor, "rb") as stream:
                initial = os.fstat(stream.fileno())
                if not stat.S_ISREG(initial.st_mode) or initial.st_nlink != 1:
                    raise ValueError("Schema is no longer an ordinary unlinked file")
                data = stream.read(MAX_SCHEMA_BYTES + 1)
                final = os.fstat(stream.fileno())
                identity = lambda item: (item.st_dev, item.st_ino, item.st_size, item.st_mtime_ns, item.st_ctime_ns)
                if identity(initial) != identity(final):
                    raise ValueError("Schema changed during read")
        finally:
            os.close(descriptor)
        if len(data) != record["bytes"] or len(data) > MAX_SCHEMA_BYTES:
            raise ValueError("Schema file changed or exceeded its read limit")
        def reject_constant(value):
            raise ValueError("Non-JSON numeric constant: " + value)
        def reject_duplicate_keys(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError("Duplicate JSON object key")
                result[key] = value
            return result
        decoded = json.loads(data, parse_constant=reject_constant, object_pairs_hook=reject_duplicate_keys)
        if not isinstance(decoded, (dict, bool)):
            raise ValueError("Generated JSON is not an object/boolean schema")
        payload["schemas/" + relative] = data
    if not payload:
        raise ValueError("No JSON schemas were produced")
    if tree_inventory(root) != before:
        raise ValueError("Schema inventory changed during capture")
    return payload


def _help_options(text):
    out = bool(re.search(r"(?m)^\s*--out(?:\s|=)", text))
    match = re.search(r"(?ms)^\s*--experimental(?:\s|$)(.*?)(?=^\s*(?:-[A-Za-z]|--[A-Za-z])|\Z)", text)
    experimental = bool(match and re.search(r"(?is)include.{0,120}experimental.{0,80}(?:api|field|method)", match.group(0)))
    return {"out_advertised": out, "experimental_flag_advertised": bool(match),
            "experimental_inclusion_meaning_confirmed": experimental}


def run_probe(lab_root, command_runner=run_bounded, runtime_inspector=inspect_runtime_executable, *, runtime_path=None):
    lab_root = Path(lab_root)
    if not lab_root.is_absolute() or not lab_root.is_dir() or any(p.is_symlink() for p in [lab_root, *lab_root.parents]):
        raise ValueError("Lab must be an existing absolute directory without symlink ancestors")
    for relative in ("delivery", "delivery/gate0_interface"):
        directory = lab_root / relative
        if directory.is_symlink() or (directory.exists() and not directory.is_dir()):
            raise ValueError("Unsafe output directory")
        directory.mkdir(mode=0o700, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex
    root = lab_root / "delivery/gate0_interface" / run_id
    root.mkdir(mode=0o700)
    schemas = root / "schemas"
    schemas.mkdir(mode=0o700)
    report_path = root / "REPORT.json"
    runtime = Path(runtime_path) if runtime_path is not None else Path.home() / boundary.EXPECTED_RUNTIME_RELATIVE_PATH
    simulation = command_runner is not run_bounded or runtime_inspector is not inspect_runtime_executable
    protected = {str(path): sha256(path.read_bytes()) for path in (Path(__file__).resolve(), DEPENDENCY)}
    report = {"schema_version": 1, "probe": PROBE_ID, "run_id": run_id,
        "created_utc": datetime.now(timezone.utc).isoformat(), "status": "IN_PROGRESS",
        "script_sha256": protected[str(Path(__file__).resolve())], "dependency_sha256": DEPENDENCY_SHA256,
        "model_called": False, "server_session_started": False, "rpc_sent": False,
        "configuration_files_edited": False, "credential_or_configuration_files_read_by_script": False,
        "client_internal_file_access_not_traced": True, "include_managed_config": True,
        "command_runner_substituted": command_runner is not run_bounded,
        "runtime_inspector_substituted": runtime_inspector is not inspect_runtime_executable,
        "runtime_location": "explicit_local_copy_pinned_to_observed_sha" if runtime_path is not None else "fixed_WSL_installed_path",
        "explicit_local_copy_does_not_establish_WSL_startup_or_boundary": runtime_path is not None,
        "not_established": ["reviewer readiness", "fresh model context", "full-client tool and connector isolation",
                            "authoritative allowance", "all method sources available"],
        "limits": {"wall_seconds_per_command": TIMEOUT_SECONDS, "stream_bytes_each": MAX_STREAM_BYTES,
            "hard_per_file_bytes": MAX_SCHEMA_BYTES, "monitored_tree_bytes": MAX_TREE_BYTES,
            "monitored_tree_entries": MAX_TREE_ENTRIES, "tree_poll_seconds": 0.05,
            "tree_monitor_is_not_atomic_filesystem_quota": True, "hard_per_process_cpu_seconds": [30, 31]},
        "protected_inputs_before": protected, "commands": []}
    save_report(report_path, report)
    outcome, pre, payload = "PRECONDITION_FAILED", None, {}
    try:
        print("PROBE: exact pinned runtime identity and version; no model", flush=True)
        pre = runtime_inspector(runtime)
        report["runtime_preflight"] = pre
        if (pre.get("status") != "VERIFIED_RUNTIME_FILE" or pre.get("sha256") != RUNTIME_SHA256
                or pre.get("path") != str(runtime) or pre.get("canonical_path") != str(runtime)
                or any(key not in pre for key in boundary.RUNTIME_IDENTITY_FIELDS)):
            raise ValueError("Fixed runtime identity does not match the observed installed executable")
        version = command_runner([str(runtime), "--version"], schemas, 12, None)
        report["commands"].append(version)
        if version.get("status") != "completed" or version.get("exit_code") != 0 or version["stdout"]["utf8"].strip() != boundary.EXPECTED_CODEX_VERSION:
            outcome = "VERSION_NOT_ESTABLISHED"
        else:
            name = "arc_interface_" + uuid.uuid4().hex
            filesystem = {":root": "deny", ":minimal": "read", str(runtime): "read", str(schemas): "write"}
            policy = "permissions." + name + "={filesystem={" + ",".join(json.dumps(k) + "=" + json.dumps(v) for k,v in filesystem.items()) + "},network={enabled=false}}"
            report["requested_profile"] = {"name": name, "filesystem": filesystem, "network": {"enabled": False},
                "include_managed_config": True, "toml_assignment": policy}
            outer = [str(runtime), "sandbox", "-P", name, "--include-managed-config", "-C", str(schemas), "-c", policy, "--"]
            inner = [str(runtime), "app-server", "generate-json-schema"]
            print("PROBE: confined schema-command help only", flush=True)
            help_result = command_runner(outer + inner + ["--help"], schemas, TIMEOUT_SECONDS, schemas)
            report["commands"].append(help_result)
            if help_result.get("status") != "completed" or help_result.get("exit_code") != 0:
                outcome = "SCHEMA_HELP_NOT_ESTABLISHED"
            else:
                options = _help_options(help_result["stdout"]["utf8"])
                report["schema_options"] = options
                if not options["out_advertised"]:
                    outcome = "SCHEMA_OUT_OPTION_NOT_ADVERTISED"
                elif tree_inventory(schemas):
                    outcome = "UNEXPECTED_HELP_OUTPUT_FILES"
                else:
                    arguments = ["--out", str(schemas)]
                    if options["experimental_inclusion_meaning_confirmed"]:
                        arguments.append("--experimental")
                    report["experimental_scope"] = "explicitly_requested" if "--experimental" in arguments else "stable_capture_experimental_scope_unresolved"
                    print("PROBE: confined static JSON-schema generation; no server session", flush=True)
                    generated = command_runner(outer + inner + arguments, schemas, TIMEOUT_SECONDS, schemas)
                    report["commands"].append(generated)
                    if generated.get("status") != "completed" or generated.get("exit_code") != 0:
                        outcome = "SCHEMA_GENERATION_NOT_ESTABLISHED"
                    else:
                        outcome = "SCHEMA_VALIDATION_FAILED"
                        payload = _read_schemas(schemas)
                        report["schemas"] = [{"path": path, "bytes": len(data), "sha256": sha256(data)} for path,data in payload.items()]
                        report["schema_validation_scope"] = "Bounded ordinary files, safe paths, strict JSON parse, object/boolean roots; not semantic protocol compatibility"
                        outcome = "INTERFACE_SCHEMA_CAPTURED"
    except KeyboardInterrupt:
        outcome = "INTERRUPTED"
        report["reason"] = "Human interrupt; partial output retained"
    except Exception as exc:
        report["error"] = {"type": type(exc).__name__, "message": str(exc)}
    finally:
        if pre is not None:
            try:
                post = runtime_inspector(runtime)
                report["runtime_postflight"] = post
                unchanged = post.get("status") == "VERIFIED_RUNTIME_FILE" and all(post.get(k) == pre.get(k) for k in boundary.RUNTIME_IDENTITY_FIELDS)
                report["runtime_identity_unchanged"] = unchanged
                if not unchanged:
                    report["observation_before_runtime_check"] = outcome
                    outcome = "RUNTIME_INTEGRITY_NOT_ESTABLISHED"
            except (Exception, KeyboardInterrupt) as exc:
                report["runtime_postflight_error"] = {"type": type(exc).__name__, "message": str(exc)}
                outcome = "RUNTIME_INTEGRITY_NOT_ESTABLISHED"
        after = {path: sha256(Path(path).read_bytes()) for path in protected}
        report["protected_inputs_after"] = after
        report["protected_inputs_unchanged"] = after == protected
        if after != protected:
            outcome = "PROTECTED_INPUT_INTEGRITY_NOT_ESTABLISHED"
        report["observation_status"] = outcome
        report["status"] = "HARNESS_SIMULATION" if simulation else outcome
        report["finished_utc"] = datetime.now(timezone.utc).isoformat()
        digest = save_report(report_path, report, final=True)
        print("REPORT: " + str(report_path), flush=True)
        print("REPORT_SHA256: " + digest, flush=True)
        # Capture failure reports as well, but never package unvalidated schema bytes.
        archive_payload = {"REPORT.json": report_path.read_bytes()}
        if outcome == "INTERFACE_SCHEMA_CAPTURED":
            archive_payload.update(payload)
        hashes = "".join(sha256(data) + "  " + name + "\n" for name,data in sorted(archive_payload.items()))
        archive_payload["SHA256SUMS"] = hashes.encode("ascii")
        archive = root / "INTERFACE_CAPTURE.zip"
        with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED) as zipped:
            for name,data in sorted(archive_payload.items()):
                zipped.writestr(name, data)
        with zipfile.ZipFile(archive) as zipped:
            if zipped.namelist() != sorted(archive_payload) or any(zipped.read(name) != data for name,data in archive_payload.items()):
                raise OSError("ZIP readback differs from verified capture")
        print("BUNDLE: " + str(archive), flush=True)
        print("BUNDLE_SHA256: " + sha256(archive.read_bytes()), flush=True)
        print("STATUS: " + report["status"], flush=True)
        print("This captures an installed interface; reviewer readiness is not established.", flush=True)
    return report_path, report, archive


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    try:
        _, report, _ = run_probe(Path.home() / "ARC_Independent_Lab")
    except (OSError, ValueError) as exc:
        print("STOP: " + str(exc), flush=True)
        return 2
    return 0 if report["status"] == "INTERFACE_SCHEMA_CAPTURED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
