#!/usr/bin/env python3
"""Focused hosted validation: substituted Codex interfaces, never real isolation."""
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tomllib
import uuid
import zipfile

LAB = Path(__file__).resolve().parents[1]
SOURCE = LAB / "scripts/gate0_reviewer_interface_probe.py"
spec = importlib.util.spec_from_file_location("interface_probe", SOURCE)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


def fabricated(argv, cwd, timeout, *, code=0, status="completed", out=b"", err=b""):
    return {"argv": argv, "cwd": str(cwd), "timeout_seconds": timeout, "status": status,
            "exit_code": code, "stdout": probe.captured_bytes(out), "stderr": probe.captured_bytes(err),
            "simulation": "Fabricated Codex result; no installed CLI or model invoked"}


def inspector_for(case):
    calls = 0
    def inspect(path):
        nonlocal calls
        calls += 1
        return {"status": "VERIFIED_RUNTIME_FILE", "path": str(path), "canonical_path": str(path),
                "sha256": "0" * 64 if case == "runtime_changed" and calls > 1 else probe.RUNTIME_SHA256,
                "bytes": 270815680, "mode": 0o755, "device": 0, "inode": 0,
                "mtime_ns": 0, "ctime_ns": 0, "regular_file": True,
                "executable_for_current_user": True, "simulation": "Fabricated runtime identity"}
    return inspect


def runner_for(case):
    def runner(argv, cwd, timeout, monitor_root):
        if argv[1:] == ["--version"]:
            return fabricated(argv, cwd, timeout, out=b"codex-cli 0.151.0\n")
        runtime = str(Path.home() / probe.boundary.EXPECTED_RUNTIME_RELATIVE_PATH)
        assert argv[:2] == [runtime, "sandbox"]
        assert "--include-managed-config" in argv and "linux" not in argv
        profile = argv[argv.index("-P") + 1]
        parsed = tomllib.loads(argv[argv.index("-c") + 1])["permissions"][profile]
        assert parsed == {"filesystem": {":root": "deny", ":minimal": "read", runtime: "read", str(cwd): "write"}, "network": {"enabled": False}}
        inner = argv[argv.index("--") + 1:]
        assert inner[:3] == [runtime, "app-server", "generate-json-schema"]
        assert monitor_root == cwd
        if inner[3:] == ["--help"]:
            if case == "launch_failed":
                return fabricated(argv, cwd, timeout, code=1, err=b"SYNTHETIC sandbox launch failure\n")
            if case == "unsupported_help":
                return fabricated(argv, cwd, timeout, out=b"Usage: no supported output argument\n")
            result = b"Usage: codex app-server generate-json-schema [OPTIONS] --out <DIR>\n\nOptions:\n      --out <DIR>\n          Output directory\n"
            if case != "stable_only":
                result += b"      --experimental\n          Include experimental APIs in the generated schema\n"
            result += b"  -h, --help\n          Print help\n"
            return fabricated(argv, cwd, timeout, out=result)
        assert inner[3:5] == ["--out", str(cwd)]
        assert ("--experimental" in inner) == (case != "stable_only")
        if case == "generation_nonzero":
            return fabricated(argv, cwd, timeout, code=2, err=b"SYNTHETIC generation error\n")
        if case == "interrupted":
            return fabricated(argv, cwd, timeout, code=-15, status="interrupted")
        destination = Path(cwd) / "Protocol.json"
        if case == "invalid_json":
            destination.write_bytes(b'{"type":')
        elif case == "oversize":
            with destination.open("wb") as stream:
                stream.truncate(probe.MAX_SCHEMA_BYTES + 1)
        elif case == "symlink":
            destination.symlink_to("nonexistent-target")
        else:
            destination.write_text('{"$schema":"https://json-schema.org/draft/2020-12/schema","type":"object"}\n')
        return fabricated(argv, cwd, timeout)
    return runner


def main():
    root = LAB / "delivery/gate0_interface_validation" / uuid.uuid4().hex
    root.mkdir(parents=True)
    archive_root = LAB / "artifacts/GATE0_INTERFACE_HARNESS/20260907_001"
    if archive_root.exists():
        raise RuntimeError("Evidence directory already exists; do not overwrite prior validation")
    archive_root.mkdir(parents=True)
    report = {"schema_version": 1, "created_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "HARNESS_SIMULATION; no Codex, app-server service, reviewer, model or enforced sandbox",
        "probe_sha256": probe.sha256(SOURCE.read_bytes()),
        "dependency_sha256": probe.DEPENDENCY_SHA256,
        "validator_sha256": probe.sha256(Path(__file__).read_bytes()), "cases": []}
    expected_cases = [("valid_experimental", "INTERFACE_SCHEMA_CAPTURED"),
        ("stable_only", "INTERFACE_SCHEMA_CAPTURED"), ("unsupported_help", "SCHEMA_OUT_OPTION_NOT_ADVERTISED"),
        ("launch_failed", "SCHEMA_HELP_NOT_ESTABLISHED"), ("generation_nonzero", "SCHEMA_GENERATION_NOT_ESTABLISHED"),
        ("runtime_changed", "RUNTIME_INTEGRITY_NOT_ESTABLISHED"), ("invalid_json", "SCHEMA_VALIDATION_FAILED"),
        ("oversize", "SCHEMA_VALIDATION_FAILED"), ("symlink", "SCHEMA_VALIDATION_FAILED"),
        ("interrupted", "SCHEMA_GENERATION_NOT_ESTABLISHED")]
    for case, expected in expected_cases:
        case_root = root / case
        case_root.mkdir()
        path, result, zipped_path = probe.run_probe(case_root, runner_for(case), inspector_for(case))
        assert result["status"] == "HARNESS_SIMULATION"
        assert result["observation_status"] == expected, (case, result)
        assert result["protected_inputs_unchanged"] is True
        assert result["model_called"] is result["server_session_started"] is result["rpc_sent"] is False
        assert json.loads(path.read_bytes()) == result
        with zipfile.ZipFile(zipped_path) as zipped:
            assert zipped.read("REPORT.json") == path.read_bytes()
            assert any(name.startswith("schemas/") for name in zipped.namelist()) == (expected == "INTERFACE_SCHEMA_CAPTURED")
            for line in zipped.read("SHA256SUMS").decode().splitlines():
                digest, name = line.split("  ", 1)
                assert probe.sha256(zipped.read(name)) == digest
        destination = archive_root / case
        destination.mkdir()
        shutil.copyfile(path, destination / "REPORT.json")
        shutil.copyfile(zipped_path, destination / "INTERFACE_CAPTURE.zip")
        report["cases"].append({"name": case, "status": "matched_expected", "observation_status": expected,
            "report_path": str((destination / "REPORT.json").relative_to(LAB)),
            "report_sha256": probe.sha256(path.read_bytes()), "bundle_sha256": probe.sha256(zipped_path.read_bytes())})

    # Actual host subprocesses below run only synthetic Python, without Codex.
    large = probe.run_bounded([sys.executable, "-I", "-c", "import os; os.write(1, b'x' * 2097152)"], root, 3)
    assert large["status"] == "output_limit" and large["stdout"]["bytes"] == probe.MAX_STREAM_BYTES
    short = probe.run_bounded([sys.executable, "-I", "-c", "import time; time.sleep(20)"], root, 0.1)
    assert short["status"] == "timeout" and short["elapsed_seconds"] < 5
    absent = probe.run_bounded([str(root / "nonexistent-executable")], root, 0.1)
    assert absent["status"] == "launch_error"
    # Detached child holds a pipe; cleanup must return without signalling other groups.
    detached = probe.run_bounded([sys.executable, "-I", "-c",
        "import subprocess,sys; subprocess.Popen([sys.executable,'-I','-c','import time; time.sleep(4)'],start_new_session=True)"], root, 0.1)
    assert detached["status"] == "timeout" and detached["elapsed_seconds"] < 5
    assert detached.get("output_capture_incomplete") is True
    for name, result in [("bounded_stdout", large), ("bounded_timeout", short), ("missing_executable", absent), ("detached_pipe", detached)]:
        path = archive_root / (name + ".json")
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        report["cases"].append({"name": name, "status": "matched_expected",
            "scope": "Actual synthetic host subprocess only; not Codex or enforcement",
            "observation_status": result["status"], "report_path": str(path.relative_to(LAB)), "report_sha256": probe.sha256(path.read_bytes())})
    report["status"] = "HARNESS_CHECKS_PASSED"
    evidence = LAB / "evidence/GATE0_INTERFACE_HARNESS_VALIDATION_2026-09-07.json"
    with evidence.open("x") as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write("\n")
    sums = "".join(probe.sha256(path.read_bytes()) + "  " + path.relative_to(archive_root).as_posix() + "\n"
        for path in sorted(archive_root.rglob("*")) if path.is_file())
    (archive_root / "SHA256SUMS").write_text(sums)
    print(json.dumps({"status": report["status"], "cases": len(report["cases"]),
        "evidence": str(evidence), "evidence_sha256": probe.sha256(evidence.read_bytes()),
        "probe_sha256": report["probe_sha256"], "validator_sha256": report["validator_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
