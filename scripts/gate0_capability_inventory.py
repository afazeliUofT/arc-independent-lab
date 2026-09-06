"""Bounded metadata inventory. Writes a new report only inside ~/ARC_Independent_Lab.

--mode laptop: Python/Git/Codex version/help and host resource metadata.
--mode slurm: Python/Git/Slurm versions, partitions and own associations/QOS.
No install, model task, login, setting change, job query, submission or Git write.
The invoked clients' help/version behavior is not an enforced isolation test.
"""
import argparse
import base64
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import pwd
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time

LOCAL_TIMEOUT = 12
SLURM_TIMEOUT = 30
TOTAL_COMMAND_SECONDS = 150
ASSOCIATION_ID_FIELDS = "Cluster,Account,User,Partition,DefaultQOS,QOS"
ASSOCIATION_LIMIT_FIELDS = "Cluster,Account,User,Partition,GrpTRES,GrpTRESMins,GrpTRESRunMins,MaxTRES,MaxTRESMins,MaxWall,MaxJobs,MaxSubmitJobs"
QOS_FIELDS = "Name,Flags,GrpTRES,GrpTRESMins,GrpTRESRunMins,MaxTRESPJ,MaxTRESPU,MaxTRESMinsPJ,MaxWall,MaxJobsPU,MaxSubmitJobsPU"
SINFO_FORMAT = "%P|%a|%l|%D|%c|%m|%G"


def ordinary_directory(path, create=False):
    path = path.absolute()
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError("Symlink directory refused: " + str(part))
    if create:
        path.mkdir(parents=True, exist_ok=True)
    if not path.is_dir() or path.resolve() != path:
        raise ValueError("Expected ordinary directory: " + str(path))
    return path


def bytes_record(body):
    return {"utf8": body.decode("utf-8", "backslashreplace"),
            "base64": base64.b64encode(body).decode("ascii"),
            "sha256": hashlib.sha256(body).hexdigest(), "bytes": len(body)}


def execute(argv, cwd, timeout):
    """No shell. On timeout, kill only this newly created process group."""
    started = time.monotonic()
    result = {"argv": argv, "timeout_seconds": timeout}
    try:
        process = subprocess.Popen(argv, cwd=cwd, stdin=subprocess.DEVNULL,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   start_new_session=True)
    except OSError as error:
        result.update(status="launch_error", exception=repr(error), exit_code=None)
        return result
    try:
        stdout, stderr = process.communicate(timeout=timeout)
        result["status"] = "ok" if process.returncode == 0 else "nonzero"
    except subprocess.TimeoutExpired as error:
        result["status"] = "timeout"
        result["timeout_exception"] = repr(error)
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        try:
            stdout, stderr = process.communicate(timeout=2)
        except subprocess.TimeoutExpired as final_error:
            # Detached descendants can retain pipes; do not wait without a bound.
            stdout, stderr = final_error.output or b"", final_error.stderr or b""
            result["pipe_cleanup_exception"] = repr(final_error)
            process.stdout.close()
            process.stderr.close()
            result["detached_descendants_not_verified"] = True
    result.update(exit_code=process.poll(), stdout=bytes_record(stdout),
                  stderr=bytes_record(stderr), elapsed_seconds=time.monotonic()-started)
    return result


def host_metadata(root):
    result = {"system": platform.system(), "release": platform.release(),
              "machine": platform.machine(), "logical_cpu_count": os.cpu_count(),
              "scope": "Current OS/WSL or login host; not a compute-node allocation."}
    if hasattr(os, "sched_getaffinity"):
        try:
            result["affinity_cpu_count"] = len(os.sched_getaffinity(0))
        except OSError as error:
            result["affinity_probe_error"] = repr(error)
    memory = {}
    if sys.platform.startswith("linux"):
        # Exact kernel resource counters only; no process or configuration files.
        try:
            for line in Path("/proc/meminfo").read_text().splitlines():
                key, _, value = line.partition(":")
                if key in {"MemTotal", "MemAvailable", "SwapTotal", "SwapFree"}:
                    memory[key] = value.strip()
        except OSError as error:
            result["memory_probe_error"] = {"probe": "/proc/meminfo", "exception": repr(error)}
    result["memory_kernel_counters"] = memory
    disk = shutil.disk_usage(root)
    result["lab_filesystem_bytes"] = {"total": disk.total, "used": disk.used, "free": disk.free}
    result["disk_scope"] = "Filesystem free bytes at lab path, not user quota or I/O performance."
    return result


def own_qos_names(record, user):
    if record.get("status") != "ok":
        return [], "Own association query did not succeed."
    names = set()
    for line in record["stdout"]["utf8"].splitlines():
        if not line.strip():
            continue
        fields = line.split("|")
        if len(fields) != 6 or fields[2] != user:
            return [], "Unexpected association columns or user; no broader query attempted."
        for value in (fields[4], *fields[5].split(",")):
            if not value:
                continue
            if not re.fullmatch(r"[A-Za-z0-9_.-]{1,128}", value):
                return [], "Unresolved QOS token; no broader query attempted."
            names.add(value)
    if len(names) > 64:
        return [], "More than 64 QOS names; no query expansion attempted."
    return sorted(names), None


def inventory(root, mode):
    root = ordinary_directory(root)
    output_dir = ordinary_directory(root / "delivery/gate0_inventory", create=True)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    output = output_dir / ("GATE0_CAPABILITY_" + mode.upper() + "_" + stamp + ".json")
    report = {
        "schema_version": 1, "inventory": "P3_GATE0_CAPABILITY_v1", "mode": mode,
        "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "read_only_probes": True, "report_write_exception": str(output),
        "command_budget_seconds": TOTAL_COMMAND_SECONDS, "commands": [],
        "capabilities_not_established": [
            "authoritative subscription allowance or remaining percentage",
            "reviewer context isolation, read scope or tool restrictions",
            "sandbox enforcement on this machine",
            "unattended model continuation or model affordability",
            "GPU execution, sustained throughput, power/hibernate behavior",
            "HPC remaining allocation, inherited account caps, user storage quota or queue availability"],
        "model_task_or_authentication_requested": False,
        "settings_or_git_changes_requested": False,
        "credential_or_configuration_files_read_by_script": False,
        "client_internal_file_access_not_traced": True,
    }
    # Reserve a fresh name; do not replace an earlier run's report.
    with output.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")

    def save():
        fd, temp_path = tempfile.mkstemp(prefix="report-", dir=output_dir)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, output)

    started = time.monotonic()

    def probe(program, args, seconds=LOCAL_TIMEOUT):
        remaining = TOTAL_COMMAND_SECONDS - (time.monotonic()-started)
        executable = sys.executable if program == "python" else shutil.which(program)
        if remaining <= 0:
            record = {"argv": [program, *args], "status": "skipped_budget", "exit_code": None}
        elif executable is None:
            record = {"argv": [program, *args], "status": "not_on_path", "exit_code": None}
        else:
            print("PROBE:", program, " ".join(args), flush=True)
            record = execute([executable, *args], root, min(seconds, remaining))
        report["commands"].append(record)
        save()
        print("RESULT:", program, record["status"], flush=True)
        return record

    try:
        report["host"] = host_metadata(root)
        save()
        probe("python", ["-I", "--version"])
        probe("git", ["--version"])
        if mode == "laptop":
            for args in (["--version"], ["--help"], ["exec", "--help"],
                         ["review", "--help"], ["sandbox", "--help"],
                         ["app-server", "--help"]):
                probe("codex", args)
        else:
            user = pwd.getpwuid(os.getuid()).pw_name
            if not re.fullmatch(r"[A-Za-z0-9_.-]{1,128}", user):
                raise ValueError("Unrecognized Unix username; no Slurm query attempted")
            report["slurm_user_filter"] = user
            probe("sinfo", ["--version"])
            probe("sacctmgr", ["--version"])
            probe("sinfo", ["--noheader", "--exact", "--format="+SINFO_FORMAT], SLURM_TIMEOUT)
            identity = probe("sacctmgr", ["--noheader", "--parsable2", "show", "association",
                              "where", "user="+user, "format="+ASSOCIATION_ID_FIELDS], SLURM_TIMEOUT)
            probe("sacctmgr", ["--noheader", "--parsable2", "show", "association",
                  "where", "user="+user, "format="+ASSOCIATION_LIMIT_FIELDS], SLURM_TIMEOUT)
            names, reason = own_qos_names(identity, user)
            report["qos_selection"] = {"names": names, "scope": "Only current user's returned QOS names", "limitation": reason}
            if names:
                probe("sacctmgr", ["--noheader", "--parsable2", "show", "qos", "where",
                      "name="+",".join(names), "format="+QOS_FIELDS], SLURM_TIMEOUT)
        report["status"] = "inventory_complete_with_explicit_unknowns"
    except (Exception, KeyboardInterrupt) as error:
        report["status"] = "inventory_interrupted_or_failed"
        report["exception"] = repr(error)
    finally:
        report["elapsed_seconds"] = time.monotonic()-started
        save()
    print("REPORT:", output, flush=True)
    print("REPORT_SHA256:", hashlib.sha256(output.read_bytes()).hexdigest(), flush=True)
    print("This inventory does not establish isolation, available allocation or model allowance.", flush=True)
    return 0 if report["status"] == "inventory_complete_with_explicit_unknowns" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("laptop", "slurm"), required=True)
    args = parser.parse_args()
    if os.name != "posix":
        parser.error("Run in WSL/Linux; this inventory does not launch Windows tooling")
    return inventory(Path.home() / "ARC_Independent_Lab", args.mode)


if __name__ == "__main__":
    sys.exit(main())
