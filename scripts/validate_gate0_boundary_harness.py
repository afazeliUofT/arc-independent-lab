"""Hosted harness validation only: all Codex invocations are substituted.

Exercises the real synthetic child unconfined, failed configuration, timeout,
and bounded cleanup with detached pipes. Never invokes Codex or a model.
Fresh reports are written below delivery/gate0_harness_validation/.
"""
import ast
from datetime import datetime, timezone
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tomllib
from unittest.mock import patch
import uuid


LAB = Path(__file__).resolve().parents[1]
SOURCE = LAB / "scripts/gate0_reviewer_boundary_probe.py"


def main():
    ast.parse(SOURCE.read_text())
    spec = importlib.util.spec_from_file_location("boundary", SOURCE)
    probe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(probe)
    compile(probe.CHILD_SOURCE, "synthetic-child.py", "exec")
    root = LAB / "delivery/gate0_harness_validation" / uuid.uuid4().hex
    root.mkdir(parents=True)
    report = {"schema_version": 1, "created_utc": datetime.now(timezone.utc).isoformat(),
              "scope": "HARNESS_SIMULATION; no actual Codex sandbox, reviewer or model",
              "validator_sha256": probe.sha256(Path(__file__).read_bytes()),
              "probe_sha256": probe.sha256(SOURCE.read_bytes()), "cases": []}

    def fabricated(argv, cwd, timeout, *, status="completed", code=0, out=b"", err=b""):
        return {"argv": argv, "cwd": str(cwd), "timeout_seconds": timeout,
                "status": status, "exit_code": code,
                "stdout": probe.captured_bytes(out), "stderr": probe.captured_bytes(err),
                "simulation": "Fabricated result; Codex was not invoked"}

    def runner_for(case):
        def runner(argv, cwd, timeout):
            if argv[1:] == ["--version"]:
                return fabricated(argv, cwd, timeout, out=b"codex-cli 0.151.0\n")
            if argv[1:] == ["doctor", "--help"]:
                return fabricated(argv, cwd, timeout, out=b"SYNTHETIC HELP ONLY\n")
            if "sandbox" not in argv:
                return probe.run_command(argv, cwd, timeout)
            policy = tomllib.loads(argv[argv.index("-c") + 1])
            profile = argv[argv.index("-P") + 1]
            assert policy["permissions"][profile] == {
                "filesystem": {":root": "deny", ":minimal": "read", str(cwd): "read"},
                "network": {"enabled": False}}
            assert "--include-managed-config" in argv
            if case == "intentionally_unconfined":
                result = probe.run_command(argv[argv.index("--") + 1:], cwd, timeout)
                result["simulation"] = "Actual synthetic child; intentionally no sandbox wrapper"
                return result
            if case == "configuration_rejected":
                return fabricated(argv, cwd, timeout, code=2,
                                  err=b"SYNTHETIC policy rejection before child launch\n")
            assert case == "wrapper_timeout"
            return fabricated(argv, cwd, timeout, status="timeout", code=-9,
                              err=b"SYNTHETIC timeout before child protocol\n")
        return runner

    for case, expected in [
        ("intentionally_unconfined", "FILESYSTEM_BOUNDARY_VIOLATION"),
        ("configuration_rejected", "SANDBOX_START_NOT_ESTABLISHED"),
        ("wrapper_timeout", "TIMEOUT"),
    ]:
        case_root = root / case
        case_root.mkdir()
        path, result = probe.run_harness(case_root, "/synthetic/not-executed-codex", runner_for(case))
        assert result["status"] == "HARNESS_SIMULATION"
        assert result["observation_status"] == expected
        assert result["unconfined_controls_passed"] is True
        assert result["parent_loopback_before"]["passed"] is True
        assert result["parent_loopback_after"]["passed"] is True
        if case == "intentionally_unconfined":
            assert result["loopback"]["status"] == "TESTED_LOOPBACK_ROUTE_ACCESSIBLE"
        report["cases"].append({"name": case, "status": "matched_expected",
                                "observation_status": expected,
                                "report_path": str(path.relative_to(LAB)),
                                "report_sha256": probe.sha256(path.read_bytes())})

    # Three simulated pipe timeouts: the final capture must not block forever.
    class DetachedPipes:
        pid = 987654321  # No real process; killpg is patched below.
        returncode = -9

        def __init__(self):
            self.stdout, self.stderr = io.BytesIO(), io.BytesIO()
            self.deadlines = []

        def communicate(self, timeout):
            self.deadlines.append(timeout)
            raise subprocess.TimeoutExpired(["synthetic"], timeout,
                                            output=b"preserved stdout", stderr=b"preserved stderr")

    fake = DetachedPipes()
    with patch.object(probe.subprocess, "Popen", return_value=fake), \
            patch.object(probe.os, "killpg") as signal_group:
        cleanup = probe.run_command(["synthetic"], root, 0.25)
    assert fake.deadlines == [0.25, 3, 3]
    assert [call.args for call in signal_group.call_args_list] == [
        (fake.pid, probe.signal.SIGTERM), (fake.pid, probe.signal.SIGKILL)]
    assert fake.stdout.closed and fake.stderr.closed
    assert cleanup["status"] == "timeout" and cleanup["output_capture_incomplete"] is True
    assert cleanup["detached_descendants_not_verified"] is True
    assert cleanup["stdout"]["utf8"] == "preserved stdout"
    assert cleanup["stderr"]["utf8"] == "preserved stderr"
    report["cases"].append({"name": "detached_pipe_cleanup_mock", "status": "matched_expected",
                            "communicate_timeouts": fake.deadlines,
                            "only_own_mock_process_group_signalled": True,
                            "pipes_closed": True, "partial_output_preserved": True,
                            "real_process_or_signal": False})
    report["status"] = "HARNESS_CHECKS_PASSED"
    report["actual_enforcement_established"] = False
    target = root / "VALIDATION.json"
    target.write_text(json.dumps(report, indent=2) + "\n")
    print("VALIDATION_REPORT:", target)
    print("VALIDATION_SHA256:", probe.sha256(target.read_bytes()))


if __name__ == "__main__":
    main()
