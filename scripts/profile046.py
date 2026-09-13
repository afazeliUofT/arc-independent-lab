#!/usr/bin/env python3
"""Once-only consolidated046 resource observations on fabricated sources."""
from __future__ import annotations
import argparse
import ctypes
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time
import unittest

KIND = "P3_CONSOLIDATED_RESOURCE_PROFILE_046_v1"
SOURCES = ("configs/P3_FULL_WORK_FIXTURES_046.json", "scripts/accounting043.py",
    "scripts/reference_n1_043.py", "scripts/reference_n3_043.py", "scripts/diagnostics045.py",
    "scripts/fullwork046.py", "scripts/profile046.py", "tests/test_fullwork046.py")
BOUNDARIES = {"native_started": False, "target_experiment_started": False,
    "target_execution_admitted": False, "complete_work_budget_admitted": False,
    "outcome_blind": True, "automatic_rerun_permitted": False,
    "original043044045_remeasured": False, "full_resource_profile_started": True,
    "maximal_geometry_proved": False, "instruction_accounting_complete": False,
    "B_comp": None, "B_mem": None}


class Interrupted(KeyboardInterrupt):
    pass


def interrupt(signum, frame):
    raise Interrupted("PROCESS_SIGNAL_" + str(signum))


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False) + "\n").encode("ascii")


def atomic_json(path, value, maximum=16 * 1024 * 1024):
    path = Path(path)
    raw = encoded(value)
    if len(raw) > maximum:
        raise ValueError("REPORT_PAYLOAD_LIMIT")
    tmp = path.with_name(path.name + ".tmp-" + str(os.getpid()))
    with tmp.open("wb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, path)
    return len(raw)


def source_hashes(root):
    return {name: hashlib.sha256((Path(root) / name).read_bytes()).hexdigest() for name in SOURCES}


def read_config(root):
    config = json.loads((Path(root) / SOURCES[0]).read_text())
    if config["kind"] != "P3_FULL_WORK_FIXTURES_046_v1" or config["repetitions"] != 3:
        raise ValueError("FIXTURE_KIND_OR_REPETITIONS")
    if config["arms"] != ["FULL", "MACRO_OFF", "FEEDBACK_NULL", "COVERAGE"]:
        raise ValueError("FIXTURE_ARMS")
    if config["mechanism"] != {"W": 2, "S": 3, "K": 4, "L": 5, "V": 2, "q": 4}:
        raise ValueError("FIXTURE_MECHANISM")
    if config["sizes"] != [{"name": "small", "B_env": 25}, {"name": "typical", "B_env": 105}, {"name": "largest", "B_env": 285}]:
        raise ValueError("FIXTURE_SIZES")
    if config["stress_cases"] != ["n1_multigroup", "n1_k4_selection", "n3_long_raw", "n3_dense"]:
        raise ValueError("FIXTURE_STRESSES")
    if config["stress"] != {"retained_records": 245, "completed_recipes": 55, "macro_words": 45,
        "raw_mutations_max": 27720, "raw_tokens_max": 10, "credit_denominator_bits": 65, "credit_numerator_bits": 66}:
        raise ValueError("FIXTURE_STRESS_GEOMETRY")
    expected_limits = {"inclusive_outer_wall_seconds": 14400, "driver_wall_seconds": 14100,
        "row_wall_seconds": 1200, "conformance_wall_seconds": 270, "address_space_bytes": 2147483648,
        "cpu_affinity_count": 1, "file_size_bytes": 33554432, "report_bytes": 16777216,
        "automatic_remeasurement": False}
    if config["limits"] != expected_limits or config["snapshot_reservation_bytes"] != 16777216 or config["decisions_per_readout"] != 20:
        raise ValueError("FIXTURE_LIMITS")
    return config


def planned_rows(config):
    identities = [("complete_chain", size["name"], arm, repetition)
        for size in config["sizes"] for arm in config["arms"] for repetition in range(config["repetitions"])]
    identities += [(case, "envelope", None, repetition) for case in config["stress_cases"] for repetition in range(config["repetitions"])]
    return [{"row_id": "row_%02d" % i, "case": case, "size": size, "arm": arm, "repetition": repetition,
        "status": "NOT_STARTED", "interruption": None, "summary": None, "metrics": None,
        "attempt_reserved": False} for i, (case, size, arm, repetition) in enumerate(identities)]


def process_limits(seconds, limits):
    available = os.sched_getaffinity(0)
    if not available:
        raise RuntimeError("CPU_AFFINITY_UNAVAILABLE")
    cpu = min(available)
    os.sched_setaffinity(0, {cpu})
    if os.sched_getaffinity(0) != {cpu}:
        raise RuntimeError("CPU_AFFINITY_NOT_SINGLE")
    applied = {"cpu_affinity": [cpu]}
    for kind, value, label in ((resource.RLIMIT_AS, limits["address_space_bytes"], "address_space_bytes"),
                              (resource.RLIMIT_FSIZE, limits["file_size_bytes"], "file_size_bytes")):
        _, hard = resource.getrlimit(kind)
        hard = value if hard == resource.RLIM_INFINITY else min(value, hard)
        resource.setrlimit(kind, (hard, hard))
        applied[label] = hard
    soft = max(1, math.ceil(seconds))
    _, hard = resource.getrlimit(resource.RLIMIT_CPU)
    hard = soft + 1 if hard == resource.RLIM_INFINITY else min(soft + 1, hard)
    resource.setrlimit(resource.RLIMIT_CPU, (min(soft, hard), hard))
    applied.update(cpu_soft_seconds=min(soft, hard), cpu_hard_seconds=hard, wall_seconds=seconds)
    for signum in (signal.SIGTERM, signal.SIGINT, signal.SIGXCPU, signal.SIGALRM, signal.SIGXFSZ):
        signal.signal(signum, interrupt)
    signal.setitimer(signal.ITIMER_REAL, max(0.01, seconds))
    return applied


def bind_parent_lifetime(expected_parent):
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(1, signal.SIGKILL) != 0 or os.getppid() != expected_parent:
        os._exit(125)


class NamedResults(unittest.TestResult):
    def __init__(self, save=None):
        super().__init__()
        self.outcomes = []
        self.current_test = None
        self.save = save

    def snapshot(self):
        return {"tests_run": self.testsRun, "test_outcomes": list(self.outcomes),
            "current_test": self.current_test,
            "passed": self.wasSuccessful() and not self.skipped and self.testsRun > 0
                and self.current_test is None and len(self.outcomes) == self.testsRun}

    def persist(self):
        if self.save is not None:
            self.save(self.snapshot())

    def startTest(self, test):
        super().startTest(test)
        self.started, self.cpu = time.monotonic(), time.process_time()
        self.current_test = test.id()
        self.persist()

    def record(self, test, status, detail=None):
        self.outcomes.append({"name": test.id(), "status": status, "detail": detail,
            "wall_seconds": time.monotonic() - self.started, "cpu_seconds": time.process_time() - self.cpu})
        self.current_test = None
        self.persist()

    def addSuccess(self, test):
        super().addSuccess(test)
        self.record(test, "PASSED")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.record(test, "FAILED", self._exc_info_to_string(err, test))

    def addError(self, test, err):
        super().addError(test, err)
        self.record(test, "ERROR", self._exc_info_to_string(err, test))

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.record(test, "SKIPPED", reason)


def conformance(save=None):
    module = importlib.import_module("test_fullwork046")
    def progress(value):
        if save is not None:
            save({**value, "case_results": module.get_results()})
    result = NamedResults(progress)
    unittest.defaultTestLoader.loadTestsFromModule(module).run(result)
    return {**result.snapshot(), "case_results": module.get_results()}


def worker(root, output, row_id, seconds):
    started, cpu = time.monotonic(), time.process_time()
    child_before = resource.getrusage(resource.RUSAGE_CHILDREN)
    meter = None
    report = {"status": "INCOMPLETE", "interruption": None, "error_detail": None,
        "summary": None, "metrics": None, "source_hashes": source_hashes(root), "limits": None,
        "worker_kind": "P3_FULL_WORK_ROW_046_v1", "row_id": row_id,
        "stage_progress": [], "partial_progress_scope": "Completed named stages and diagnostic effects; no reconstruction of an interrupted internal043 cursor"}
    try:
        config = read_config(root)
        report["limits"] = process_limits(seconds, config["limits"])
        sys.path[:0] = [str(root / "scripts"), str(root / "tests")]
        if row_id == "conformance":
            def save_conformance(value):
                report["summary"] = value
                atomic_json(output, report)
            report["summary"] = conformance(save_conformance)
            report["status"] = "COMPLETED" if report["summary"]["passed"] else "FAILED_CONFORMANCE"
        else:
            from accounting043 import Meter
            from fullwork046 import workload
            row = next(row for row in planned_rows(config) if row["row_id"] == row_id)
            meter = Meter(memory_limit=config["limits"]["address_space_bytes"])
            def progress(stage, status, detail):
                report["stage_progress"].append({"stage": stage, "status": status,
                    "wall_seconds": time.monotonic() - started, "process_cpu_seconds": time.process_time() - cpu,
                    "logical_work": meter.work, "logical_retained_bytes": meter.retained_bytes,
                    "peak_logical_retained_bytes": meter.peak_retained_bytes, "detail": detail})
                atomic_json(output, report)
            report["summary"] = workload(config, row, meter, progress)
            report["status"] = "COMPLETED"
            # Completed rows keep full diagnostics once in summary. Partial rows
            # preserve all completed-stage details without requiring a rerun.
            for stage in report["stage_progress"]:
                stage["detail"] = {"retained_in_completed_summary": True} if stage["status"] == "COMPLETED" else stage["detail"]
    except (Interrupted, MemoryError) as error:
        report["interruption"] = type(error).__name__
        report["error_detail"] = str(error)
    except Exception as error:
        report["interruption"] = type(error).__name__
        report["error_detail"] = str(error)
        report["status"] = "INCOMPLETE" if meter is not None and meter.refusals else "FAILED_CONFORMANCE"
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        child_now = resource.getrusage(resource.RUSAGE_CHILDREN)
        state = meter.state() if meter else None
        report["metrics"] = {"wall_seconds": time.monotonic() - started,
            "process_cpu_seconds": time.process_time() - cpu,
            "child_cpu_seconds": child_now.ru_utime + child_now.ru_stime - child_before.ru_utime - child_before.ru_stime,
            "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            "logical_work": state["work"] if state else None,
            "logical_retained_bytes": state["retained_bytes"] if state else None,
            "peak_logical_retained_bytes": state["peak_retained_bytes"] if state else None,
            "meter": state, "output_bytes": 0,
            "measurement_scope": "Worker including construction/diagnostics and explicit payload serialization; final report serialization cost recorded separately by parent",
            "logical_memory_is_python_allocation": False}
        for _ in range(8):
            count = len(encoded(report))
            if report["metrics"]["output_bytes"] == count:
                break
            report["metrics"]["output_bytes"] = count
        atomic_json(output, report)


def run_child(root, output, row_id, seconds):
    command = [sys.executable, "-I", "-B", "-S", str(root / "scripts/profile046.py"),
        "--root", str(root), "--output", str(output), "--worker", row_id,
        "--seconds", str(max(0.01, seconds - 3))]
    started = time.monotonic()
    parent = os.getpid()
    process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "PYTHONDONTWRITEBYTECODE": "1",
             "PYTHONHASHSEED": "0", "LC_ALL": "C.UTF-8"},
        preexec_fn=lambda: bind_parent_lifetime(parent))
    timed_out = False
    try:
        out, err = process.communicate(timeout=max(0.01, seconds - 1))
    except subprocess.TimeoutExpired:
        timed_out = True
        process.terminate()
        try:
            out, err = process.communicate(timeout=1)
        except subprocess.TimeoutExpired:
            process.kill()
            out, err = process.communicate()
    except BaseException:
        process.terminate()
        try:
            process.communicate(timeout=1)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()
        raise
    if output.is_file():
        if output.stat().st_size > 16 * 1024 * 1024:
            raise ValueError("WORKER_REPORT_OVERSIZE")
        raw = output.read_bytes()
        result = json.loads(raw)
    else:
        raw = b""
        result = {"status": "INCOMPLETE", "summary": None, "metrics": None,
            "interruption": "NO_WORKER_REPORT", "row_id": row_id}
    result["process_evidence"] = {"returncode": process.returncode,
        "parent_wall_seconds": time.monotonic() - started, "parent_timeout": timed_out,
        "stdout_bytes": len(out), "stderr_bytes": len(err),
        "stdout_sha256": hashlib.sha256(out).hexdigest(), "stderr_sha256": hashlib.sha256(err).hexdigest(),
        "worker_report_bytes": len(raw), "worker_report_sha256": hashlib.sha256(raw).hexdigest()}
    if process.returncode != 0 and result["status"] == "COMPLETED":
        result.update(status="INCOMPLETE", interruption="NONZERO_WORKER_EXIT")
    return result


def compact_worker_report(measured, path):
    """Bound the aggregate index independently of48 full evidence payloads.

    The exact worker JSON remains a separate required return artifact. Status
    and process disposition may be stricter in this index than in raw bytes.
    """
    if measured.get("row_id") not in {"conformance"} | {"row_%02d" % i for i in range(48)}:
        raise ValueError("WORKER_REPORT_ROW_ID_INVALID")
    keep = ("status", "interruption", "error_detail", "metrics", "limits", "source_hashes",
            "worker_kind", "row_id", "process_evidence", "partial_progress_scope")
    result = {key: measured[key] for key in keep if key in measured}
    result["stage_progress"] = [{key: value for key, value in stage.items() if key != "detail"}
        for stage in measured.get("stage_progress", [])]
    result["summary"] = measured.get("summary") if measured.get("row_id") == "conformance" else None
    path = Path(path)
    expected_name = "CONFORMANCE.json" if measured["row_id"] == "conformance" else measured["row_id"] + ".json"
    if path.name != expected_name:
        raise ValueError("WORKER_REPORT_FILENAME_MISMATCH")
    if path.is_file():
        if path.stat().st_size > 16 * 1024 * 1024:
            raise ValueError("WORKER_REPORT_OVERSIZE")
        raw = path.read_bytes()
        result["full_worker_report"] = {"filename": path.name, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
    elif measured["status"] == "COMPLETED":
        raise ValueError("COMPLETED_WORKER_REPORT_MISSING")
    else:
        result["full_worker_report"] = None
    return result


def recover_saved_reports(report, output, sources, config):
    """Attach saved child evidence after interruption without any child start."""
    identity = ("row_id", "case", "size", "arm", "repetition")
    expected = planned_rows(config)
    if len(report.get("profiles", [])) != len(expected) or any(
        any(row.get(key) != planned[key] for key in identity)
        for row, planned in zip(report["profiles"], expected)):
        raise ValueError("RETAINED_PROFILE_ROW_IDENTITY_MISMATCH")
    changed = False
    candidates = [(row, row["row_id"], row["row_id"] + ".json") for row in report["profiles"]]
    candidates.append((report.get("conformance"), "conformance", "CONFORMANCE.json"))
    for index, row_id, filename in candidates:
        path = output / filename
        if not path.is_file() or path.stat().st_size > config["limits"]["report_bytes"]:
            continue
        descriptor = index.get("full_worker_report") if index else None
        if descriptor is not None:
            raw = path.read_bytes()
            if descriptor != {"filename": filename, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}:
                raise ValueError("SAVED_WORKER_REPORT_IDENTITY_CHANGED")
            continue
        raw = path.read_bytes()
        try:
            saved = json.loads(raw)
        except ValueError:
            continue  # Handoff preserves unknown fixed-name files separately.
        if saved.get("row_id") != row_id or saved.get("source_hashes") != sources:
            continue
        compact = compact_worker_report(saved, path)
        compact.update(status="INCOMPLETE", interruption="SAVED_CHILD_DISPOSITION_UNVERIFIED",
            salvaged_worker_report_sha256=hashlib.sha256(raw).hexdigest())
        if row_id == "conformance":
            report["conformance"] = compact
        else:
            index.update(compact)
        changed = True
    if changed:
        report["status"] = "INCOMPLETE"
        report["complete_required_paths_measured"] = False
        report["completed_rows"] = sum(row["status"] == "COMPLETED" for row in report["profiles"])
        report["interruption"] = report.get("interruption") or "SAVED_CHILD_DISPOSITION_UNVERIFIED"
    return changed


def run(root, output):
    root, output = Path(root).resolve(), Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    report_path = output / "REPORT.json"
    config, sources = read_config(root), source_hashes(root)
    if report_path.exists():
        retained = json.loads(report_path.read_text())
        if retained.get("kind") != KIND or retained.get("source_hashes") != sources:
            raise ValueError("RETAINED_REPORT_SOURCE_OR_KIND_MISMATCH")
        if recover_saved_reports(retained, output, sources, config):
            atomic_json(report_path, retained)
        print(json.dumps({"status": "RETAINED_FIRST_REPORT", "report_status": retained.get("status")}))
        return retained
    try:
        with (output / "RESERVATION.json").open("x") as stream:
            json.dump({"kind": KIND, "source_hashes": sources, "automatic_remeasurement": False}, stream)
            stream.flush()
            os.fsync(stream.fileno())
        first = True
    except FileExistsError:
        first = False
    started, cpu = time.monotonic(), time.process_time()
    child_before = resource.getrusage(resource.RUSAGE_CHILDREN)
    report = {"kind": KIND, **BOUNDARIES, "status": "INCOMPLETE", "interruption": None,
        "source_hashes": sources, "profiles": planned_rows(config), "conformance": None,
        "limits": config["limits"], "applied_driver_limits": None,
        "complete_required_paths_measured": False, "attempted_rows": 0, "completed_rows": 0,
        "coverage_limitations": config["coverage_limitations"], "aggregate_metrics": None,
        "evidence_transport": "EXACT_SEPARATE_WORKER_REPORTS_046_v1",
        "host": {"python": sys.version.split()[0], "platform": sys.platform,
            "ambient_conditions": "UNCONTROLLED_NOT_CLASSIFIED_QUIET_OR_CONTENDED"}}
    atomic_json(report_path, report)
    if not first:
        report["interruption"] = "PRIOR_RESERVATION_WITHOUT_REPORT"
        atomic_json(report_path, report)
        return report
    try:
        report["applied_driver_limits"] = process_limits(config["limits"]["driver_wall_seconds"], config["limits"])
        deadline = started + config["limits"]["driver_wall_seconds"]
        atomic_json(report_path, report)
        conformance_path = output / "CONFORMANCE.json"
        measured = run_child(root, conformance_path, "conformance", config["limits"]["conformance_wall_seconds"])
        report["conformance"] = compact_worker_report(measured, conformance_path)
        atomic_json(report_path, report)
        if report["conformance"]["status"] != "COMPLETED":
            report["status"] = report["conformance"]["status"]
            report["interruption"] = "CONFORMANCE_NOT_COMPLETED"
        else:
            for row in report["profiles"]:
                remaining = deadline - time.monotonic()
                if remaining < 5:
                    report["interruption"] = "AGGREGATE_WALL_LIMIT"
                    break
                reservation = output / (row["row_id"] + "_RESERVATION.json")
                with reservation.open("x") as stream:
                    json.dump({k: row[k] for k in ("row_id", "case", "size", "arm", "repetition")}, stream)
                    stream.flush()
                    os.fsync(stream.fileno())
                row.update(status="RESERVED", attempt_reserved=True)
                report["attempted_rows"] += 1
                atomic_json(report_path, report)
                measured = run_child(root, output / (row["row_id"] + ".json"), row["row_id"], min(remaining, config["limits"]["row_wall_seconds"]))
                if measured.get("source_hashes") not in (None, sources) or measured["row_id"] != row["row_id"]:
                    raise ValueError("WORKER_SOURCE_OR_IDENTITY_MISMATCH")
                row.update(compact_worker_report(measured, output / (row["row_id"] + ".json")))
                if row["status"] == "COMPLETED":
                    report["completed_rows"] += 1
                atomic_json(report_path, report)
                print(json.dumps({"row_id": row["row_id"], "status": row["status"], "completed_rows": report["completed_rows"]}), flush=True)
                if row["status"] != "COMPLETED":
                    report["status"] = row["status"]
                    report["interruption"] = "ROW_NOT_COMPLETED"
                    break
            else:
                report.update(status="COMPLETED", complete_required_paths_measured=True)
    except (Interrupted, MemoryError) as error:
        report["interruption"] = str(error) or type(error).__name__
    except Exception as error:
        report.update(status="FAILED_CONFORMANCE", interruption=type(error).__name__, error_detail=str(error))
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        recover_saved_reports(report, output, sources, config)
        child_now = resource.getrusage(resource.RUSAGE_CHILDREN)
        report["aggregate_metrics"] = {"wall_seconds": time.monotonic() - started,
            "driver_process_cpu_seconds": time.process_time() - cpu,
            "child_cpu_seconds": child_now.ru_utime + child_now.ru_stime - child_before.ru_utime - child_before.ru_stime,
            "peak_child_rss_bytes": child_now.ru_maxrss * 1024,
            "driver_peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            "scope": "046_RESOURCE_PROFILE_INVOCATION_ONLY",
            "aggregate_memory_is_cgroup_capped": False}
        for row in report["profiles"]:
            if row["status"] == "RESERVED":
                row.update(status="INCOMPLETE", interruption="DRIVER_INTERRUPTED_WHILE_RESERVED")
            elif row["status"] == "NOT_STARTED":
                row["interruption"] = "BLOCKED_BY_PRIOR_STOP"
        atomic_json(report_path, report)
    print(json.dumps({"status": report["status"], "completed_rows": report["completed_rows"],
        "planned_rows": len(report["profiles"]), "complete_work_budget_admitted": False}), flush=True)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--worker")
    parser.add_argument("--seconds", type=float, default=270)
    args = parser.parse_args()
    if args.worker:
        worker(args.root.resolve(), args.output.resolve(), args.worker, args.seconds)
    else:
        run(args.root, args.output)


if __name__ == "__main__":
    main()
