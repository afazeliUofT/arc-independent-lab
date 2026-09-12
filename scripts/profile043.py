#!/usr/bin/env python3
"""One-shot, outcome-blind development conformance/component profile driver."""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import importlib
import io
import itertools
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
from fractions import Fraction

sys.dont_write_bytecode = True
KIND = "P3_DEVELOPMENT_PROFILE_043_v1"
CASES = ("n1_no_positive_gain", "n1_positive_selection", "n3_proposal_and_credit")
SUITES = ("test_reference_n1_043", "test_reference_n3_043", "test_profile043")
SOURCES = ("scripts/accounting043.py", "scripts/reference_n1_043.py",
           "scripts/reference_n3_043.py", "scripts/profile043.py",
           "configs/P3_PROFILE_FIXTURES_043.json") + tuple("tests/" + s + ".py" for s in SUITES)


class Interrupted(RuntimeError):
    pass


def _interrupt(signum, frame):
    raise Interrupted("PROCESS_SIGNAL_" + str(signum))


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True, allow_nan=False) + "\n").encode("ascii")


def atomic_json(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + ".tmp-" + str(os.getpid()))
    raw = encoded(value)
    with temporary.open("wb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    return len(raw)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_hashes(root):
    return {name: sha256(root / name) for name in SOURCES}


def planned_rows(config):
    return [{"case": case["name"], "size": size["name"], "repetition": repetition,
             "status": "NOT_STARTED", "interruption": None, "metrics": None}
            for size in config["sizes"] for case in config["cases"]
            for repetition in range(config["repetitions"])]


def read_config(root):
    config = json.loads((root / "configs/P3_PROFILE_FIXTURES_043.json").read_text())
    if config.get("kind") != "P3_DEVELOPMENT_PROFILE_FIXTURES_043_v1":
        raise ValueError("FIXTURE_KIND_MISMATCH")
    if tuple(c["name"] for c in config["cases"]) != CASES or tuple(config["conformance_suites"]) != SUITES:
        raise ValueError("FIXTURE_CASE_MISMATCH")
    if config["repetitions"] != 3 or [(s["name"], s["retained_records"], s["macro_library_size"], s["completed_recipe_count"]) for s in config["sizes"]] != [("small", 10, 5, 5), ("typical", 85, 20, 25), ("largest", 245, 45, 55)]:
        raise ValueError("FIXTURE_SIZE_MISMATCH")
    if config["limits"] != {"inclusive_outer_wall_seconds": 300, "driver_wall_seconds": 270,
                            "address_space_bytes": 2147483648, "cpu_affinity_count": 1,
                            "automatic_remeasurement": False}:
        raise ValueError("FIXTURE_LIMIT_MISMATCH")
    return config


def process_limits(seconds, address_space):
    available = os.sched_getaffinity(0)
    if not available:
        raise RuntimeError("CPU_AFFINITY_UNAVAILABLE")
    cpu = min(available)
    os.sched_setaffinity(0, {cpu})
    if os.sched_getaffinity(0) != {cpu}:
        raise RuntimeError("CPU_AFFINITY_NOT_SINGLE")
    _, old_hard = resource.getrlimit(resource.RLIMIT_AS)
    hard = address_space if old_hard == resource.RLIM_INFINITY else min(address_space, old_hard)
    resource.setrlimit(resource.RLIMIT_AS, (hard, hard))
    cpu_soft = max(1, math.ceil(seconds))
    _, cpu_hard = resource.getrlimit(resource.RLIMIT_CPU)
    cpu_hard = cpu_soft + 1 if cpu_hard == resource.RLIM_INFINITY else min(cpu_soft + 1, cpu_hard)
    resource.setrlimit(resource.RLIMIT_CPU, (min(cpu_soft, cpu_hard), cpu_hard))
    for signum in (signal.SIGTERM, signal.SIGINT, signal.SIGXCPU, signal.SIGALRM):
        signal.signal(signum, _interrupt)
    signal.setitimer(signal.ITIMER_REAL, max(0.01, seconds))
    return {"cpu_affinity": [cpu], "address_space_limit_bytes": hard,
            "cpu_soft_seconds": min(cpu_soft, cpu_hard), "cpu_hard_seconds": cpu_hard}


def history_fixture(History, previous=0):
    return History(tuple((v,) for v in (0, 0, 0, 0, 0, previous, 0)), (1, 2, 3, 4, 0, 0))


def n1_case(case, size, meter):
    from accounting043 import canonical
    from reference_n1_043 import GenericReader, History, N1
    learner = N1(meter=meter)
    n = size["retained_records"]
    for index in range(n):
        previous = 0 if case == "n1_no_positive_gain" else index % 2
        label = index % 5 if case == "n1_no_positive_gain" else previous
        result = learner.append(history_fixture(History, previous), 0, (label,), search=True)
        assert result["appended"] and result["counts_ready"], "fabricated table append incomplete"
        assert result["status"] in ("COMPLETE", "GRAMMAR_LIMITED"), "chronological component search incomplete"
    expected_status = "GRAMMAR_LIMITED" if case == "n1_no_positive_gain" else "COMPLETE"
    assert result["status"] == expected_status and learner.counts_ready, "feature search incomplete"
    p0 = learner.predict(history_fixture(History, 0), 0)
    p1 = learner.predict(history_fixture(History, 1), 0)
    if case == "n1_no_positive_gain":
        assert learner.Phi == [], "identical feature input acquired a separator"
        assert len(learner.inventory) == 3002, "full-constant grammar not enumerated"
        counts = {label: sum(i % 5 == label for i in range(n)) for label in range(5)}
        assert p0["probabilities"] == {(label,): Fraction(counts[label] + 1, n + 5) for label in range(5)}
    else:
        assert learner.Phi and p0["probabilities"] != p1["probabilities"], "declared distinction was not separated"
    selected_before = len(learner.Phi)
    snapshot = learner.snapshot()
    before = canonical(snapshot.state())
    frozen = snapshot.predict(history_fixture(History, 0), 0, log=False)
    learner.append(history_fixture(History, 0), 0, (4,), search=False)
    assert before == canonical(snapshot.state()), "snapshot changed when live table changed"
    assert snapshot.predict(history_fixture(History, 0), 0, log=False) == frozen
    readers = []
    for order in (0, 1, 2):
        reader = GenericReader(order, meter=meter)
        fit = reader.fit(snapshot.T)
        assert fit["status"] == "COMPLETE" and len(reader.T) == n
        readers.append({"order": order, "same_data_sha256": hashlib.sha256(canonical([t.state() for t in reader.T])).hexdigest(),
                        "numeric_prediction": reader.predict(history_fixture(History, 0), 0)["probabilities"] is not None})
        reader.close()
    table_sha = hashlib.sha256(canonical([t.state() for t in snapshot.T])).hexdigest()
    assert all(row["same_data_sha256"] == table_sha for row in readers)
    summary = {"retained_records_before_mutation": n, "grammar_candidates": len(snapshot.inventory),
               "selected_predicates": selected_before, "snapshot_isolation": True,
               "update_mode": "chronological_append_with_feature_search_on_every_completed_record",
               "measured_update_calls": n,
               "count_prediction_conformant": True, "active_table_sha256": table_sha,
               "memory_reservations": {"live": learner.retained_memory_report(),
                                       "snapshot": snapshot.retained_memory_report()},
               "same_data_readers": readers, "fabricated_input": True,
               "full_acquisition": False}
    meter.retain("profile.component_output", summary)
    snapshot.close()
    learner.close()
    return summary


class ConstantDevelopmentInterface:
    """A fabricated component interface with no hidden state or target task."""
    interface_contract = "FABRICATED_PROTOCOL_FIXTURE"

    def reset(self):
        return (0,)

    def step(self, action):
        return (0,)


def n3_case(size, meter):
    from reference_n1_043 import N1
    from reference_n3_043 import Acquisition, Scheduler, brier
    scheduler = Scheduler(tuple(range(5)), 5, 4, "FULL", meter)
    words = list(itertools.islice((w for length in range(1, 6) for w in itertools.product(range(5), repeat=length)), size["completed_recipe_count"]))
    for index, word in enumerate(words):
        credit = Fraction(1, index + 1) if 5 <= index < size["macro_library_size"] else None
        scheduler.add_completed(word, index, credit=credit, warmup=index < 5)
    assert len(scheduler.M) == size["macro_library_size"]
    assert len(scheduler.F) == size["completed_recipe_count"]
    selected = scheduler.select(1)
    queue_count = len(scheduler.queue)
    assert selected and selected["word"] not in scheduler.completed and 1 <= len(selected["word"]) <= 5
    assert all(1 <= len(p["word"]) <= 5 for p in scheduler.queue)
    forced = scheduler.select(4)
    assert forced["route"] == "COVERAGE" and forced["word"] not in scheduler.completed
    fabricated_prediction = {"status": "OBSERVED_CONFLICT", "probabilities": {(0,): Fraction(1, 2), (1,): Fraction(1, 2)}}
    assert brier(fabricated_prediction, (0,), meter) == Fraction(1, 2)
    assert brier({"status": "COMPUTATION_INCOMPLETE", "probabilities": None}, (0,), meter) is None
    credit_checks = []
    for budget in (14, 15):
        learner = N1(S=1, K=0, meter=meter)
        acquisition = Acquisition(ConstantDevelopmentInterface(), learner, arm="COVERAGE", L=5, V=2, q=4,
                                  B_env=budget, meter=meter, snapshot_reservation_bytes=16 * 1024 * 1024,
                                  block_id="fabricated-constant-interface")
        acquisition.run()
        first = acquisition.trials[0]
        assert acquisition.env_calls == budget and first["status"] == "COMPLETED"
        assert first["finalized_before_validation_assimilation"] is True
        assert all(e["assimilated"] for e in acquisition.events if e["phase"] == "VALIDATION")
        if budget == 14:
            assert first["credit_status"] == "INCOMPLETE" and first["credit"] is None and len(first["validation"]) == 1
        else:
            assert first["credit_status"] == "AVAILABLE" and first["credit"] == Fraction(0) and len(first["validation"]) == 2
        credit_checks.append({"fabricated_interface_calls": budget, "credit_status": first["credit_status"],
                              "completed_validation_observations": len(first["validation"]),
                              "credit_is_nonnumeric": first["credit"] is None,
                              "finalized_before_assimilation": True})
        learner.close()
        meter.release(acquisition.owner)
        meter.release(acquisition.scheduler.owner)
    summary = {"macro_words": len(scheduler.M), "completed_recipes": len(scheduler.F),
               "unique_proposals": queue_count, "selected_word": list(selected["word"]),
               "synthetic_scheduler_credits_are_constructed_state": True,
               "coverage_cadence_conformant": True, "brier_conformant": True,
               "credit_protocol": credit_checks, "full_acquisition": False}
    meter.retain("profile.component_output", summary)
    meter.release(scheduler.owner)
    return summary


class NamedResults(unittest.TestResult):
    def __init__(self):
        super().__init__()
        self.outcomes = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.outcomes.append({"test": test.id(), "status": "PASSED"})

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.outcomes.append({"test": test.id(), "status": "FAILED", "exception_class": err[0].__name__})

    def addError(self, test, err):
        super().addError(test, err)
        self.outcomes.append({"test": test.id(), "status": "ERROR", "exception_class": err[0].__name__})

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.outcomes.append({"test": test.id(), "status": "SKIPPED"})


def conformance():
    result = NamedResults()
    loader = unittest.TestLoader()
    suite = unittest.TestSuite(loader.loadTestsFromModule(importlib.import_module(name)) for name in SUITES)
    suite.run(result)
    return {"tests_run": result.testsRun, "test_outcomes": result.outcomes,
            "passed": result.wasSuccessful() and not result.skipped and result.testsRun > 0 and len(result.outcomes) == result.testsRun}


def worker(root, output, case, size_name, seconds):
    started, cpu_started = time.monotonic(), time.process_time()
    child_started = resource.getrusage(resource.RUSAGE_CHILDREN)
    meter = None
    report = {"status": "INCOMPLETE", "case": case, "size": size_name, "interruption": None,
              "summary": None, "limits": None, "metrics": None}
    try:
        config = read_config(root)
        report["limits"] = process_limits(seconds, config["limits"]["address_space_bytes"])
        sys.path[:0] = [str(root / "scripts"), str(root / "tests")]
        if case == "conformance":
            report["summary"] = conformance()
            report["status"] = "COMPLETED" if report["summary"]["passed"] else "FAILED_CONFORMANCE"
        else:
            from accounting043 import Meter
            meter = Meter(memory_limit=config["limits"]["address_space_bytes"])
            size = next(s for s in config["sizes"] if s["name"] == size_name)
            report["summary"] = n3_case(size, meter) if case == "n3_proposal_and_credit" else n1_case(case, size, meter)
            report["status"] = "COMPLETED"
    except (Interrupted, MemoryError) as error:
        report["interruption"] = type(error).__name__
    except Exception as error:
        if meter is not None and meter.refusals:
            report["status"] = "INCOMPLETE"
            last = meter.refusals[-1].get("status")
            report["interruption"] = last if last in ("COMPUTATION_INCOMPLETE", "MEMORY_LIMIT") else "LOGICAL_RESOURCE_REFUSAL"
        else:
            report["status"] = "FAILED_CONFORMANCE"
            report["interruption"] = type(error).__name__
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        child_now = resource.getrusage(resource.RUSAGE_CHILDREN)
        state = meter.state() if meter is not None else None
        report["metrics"] = {
            "wall_seconds": time.monotonic() - started,
            "process_cpu_seconds": time.process_time() - cpu_started,
            "child_cpu_seconds": (child_now.ru_utime + child_now.ru_stime) - (child_started.ru_utime + child_started.ru_stime),
            "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            "logical_work": state["work"] if state else None,
            "logical_retained_bytes": state["retained_bytes"] if state else None,
            "peak_logical_retained_bytes": state["peak_retained_bytes"] if state else None,
            "logical_memory_measure": "Meter owner reservations in canonical bytes; a reservation may be conservative and not sealed",
            "memory_measure_is_exact_allocation": False,
            "output_bytes": 0, "meter": state}
        for _ in range(8):
            length = len(encoded(report))
            if length == report["metrics"]["output_bytes"]:
                break
            report["metrics"]["output_bytes"] = length
        atomic_json(output, report)


def run_child(root, output, case, size_name, remaining):
    command = [sys.executable, "-I", "-B", "-S", str(root / "scripts/profile043.py"), "--root", str(root),
               "--output", str(output), "--worker", case, "--size", size_name,
               "--seconds", str(max(0.01, remaining - 3))]
    started = time.monotonic()
    expected_parent = os.getpid()
    process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               preexec_fn=lambda: bind_parent_lifetime(expected_parent),
                               env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "PYTHONDONTWRITEBYTECODE": "1",
                                    "PYTHONHASHSEED": "0", "LC_ALL": "C.UTF-8"})
    terminated = False
    try:
        out, err = process.communicate(timeout=max(0.01, remaining - 1))
    except subprocess.TimeoutExpired:
        terminated = True
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
        result = json.loads(output.read_text())
    else:
        result = {"case": case, "size": size_name, "status": "INCOMPLETE", "summary": None,
                  "metrics": None, "interruption": "NO_WORKER_REPORT"}
    result["process_evidence"] = {"returncode": process.returncode, "parent_wall_seconds": time.monotonic() - started,
                                  "parent_timeout": terminated, "stdout_bytes": len(out), "stderr_bytes": len(err),
                                  "stdout_sha256": hashlib.sha256(out).hexdigest(), "stderr_sha256": hashlib.sha256(err).hexdigest()}
    if process.returncode != 0 and result["status"] == "COMPLETED":
        result["status"], result["interruption"] = "INCOMPLETE", "NONZERO_WORKER_EXIT"
    return result


def bind_parent_lifetime(expected_parent):
    """Linux process cleanup only, not a claim of sandbox/isolation strength."""
    library = ctypes.CDLL(None, use_errno=True)
    if library.prctl(1, signal.SIGKILL, 0, 0, 0) != 0:  # PR_SET_PDEATHSIG
        os._exit(125)
    if os.getppid() != expected_parent:
        os._exit(125)


def run(root, output):
    root, output = Path(root).resolve(), Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    report_path = output / "REPORT.json"
    if report_path.exists():
        retained = json.loads(report_path.read_text())
        print(json.dumps({"status": "RETAINED_FIRST_REPORT", "report_status": retained.get("status")}))
        return retained
    reservation = output / "RESERVATION.json"
    try:
        with reservation.open("x") as stream:
            json.dump({"kind": KIND, "automatic_remeasurement": False}, stream)
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError:
        report = {"kind": KIND, "status": "INCOMPLETE", "interruption": "PRIOR_RESERVATION_WITHOUT_REPORT",
                  "target_experiment_started": False, "target_execution_admitted": False, "native_started": False,
                  "outcome_blind": True, "complete_work_budget_admitted": False, "profiles": planned_rows(read_config(root)),
                  "automatic_remeasurement": False}
        for row in report["profiles"]:
            row["interruption"] = "PRIOR_RESERVATION_WITHOUT_REPORT"
        atomic_json(report_path, report)
        print(json.dumps({"status": report["status"], "interruption": report["interruption"]}))
        return report
    started, cpu_started = time.monotonic(), time.process_time()
    report = {"kind": KIND, "status": "INCOMPLETE", "interruption": None,
              "target_experiment_started": False, "target_execution_admitted": False, "native_started": False,
              "outcome_blind": True, "complete_work_budget_admitted": False, "automatic_remeasurement": False,
              "B_comp": None, "B_mem": None, "projection_status": "UNADMITTED_COMPONENTS_ONLY",
              "limitations": ["Component observations do not establish a validated complete-work budget or runtime projection",
                              "Meter memory values are owner reservations, not exact Python allocations; interrupted state may be conservatively reserved and not sealed",
                              "The 2 GiB address-space limit is per process; RSS is measured separately and aggregate process-tree RSS is not capped by a cgroup",
                              "Largest denotes declared fixture cardinality, not a proof of maximal proposal geometry or arithmetic bit lengths",
                              "Host contention is uncontrolled and neither quiet nor contended execution is established"],
              "conformance": None, "profiles": [], "source_hashes": {}, "limits": None,
              "host": {"python": sys.version.split()[0], "platform": sys.platform,
                       "ambient_conditions": "UNCONTROLLED_NOT_CLASSIFIED_QUIET_OR_CONTENDED"}}
    atomic_json(report_path, report)
    try:
        config = read_config(root)
        report["profiles"] = planned_rows(config)
        report["source_hashes"] = source_hashes(root)
        report["limits"] = process_limits(config["limits"]["driver_wall_seconds"], config["limits"]["address_space_bytes"])
        atomic_json(report_path, report)
        deadline = started + config["limits"]["driver_wall_seconds"]
        conformance_path = output / "CONFORMANCE.json"
        report["conformance"] = run_child(root, conformance_path, "conformance", "all", deadline - time.monotonic())
        atomic_json(report_path, report)
        if report["conformance"]["status"] != "COMPLETED":
            report["status"] = "FAILED_CONFORMANCE" if report["conformance"]["status"] == "FAILED_CONFORMANCE" else "INCOMPLETE"
            report["interruption"] = "CONFORMANCE_NOT_COMPLETED"
        else:
            for index, row in enumerate(report["profiles"]):
                remaining = deadline - time.monotonic()
                if remaining < 5:
                    report["interruption"] = "AGGREGATE_WALL_LIMIT"
                    break
                row["status"] = "RESERVED"
                atomic_json(report_path, report)
                result = run_child(root, output / ("COMPONENT_%02d.json" % index), row["case"], row["size"], remaining)
                row.update(result)
                atomic_json(report_path, report)
                if row["status"] != "COMPLETED":
                    report["status"] = "FAILED_CONFORMANCE" if row["status"] == "FAILED_CONFORMANCE" else "INCOMPLETE"
                    report["interruption"] = "COMPONENT_" + row["status"]
                    break
            else:
                report["status"] = "COMPLETED"
    except (Interrupted, MemoryError) as error:
        report["interruption"] = type(error).__name__
    except Exception as error:
        report["status"], report["interruption"] = "FAILED_CONFORMANCE", type(error).__name__
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        report["aggregate_metrics"] = {"wall_seconds": time.monotonic() - started,
                                       "driver_process_cpu_seconds": time.process_time() - cpu_started,
                                       "child_cpu_seconds": usage.ru_utime + usage.ru_stime,
                                       "peak_child_rss_bytes": usage.ru_maxrss * 1024,
                                       "driver_peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024}
        for row in report["profiles"]:
            if row["status"] == "NOT_STARTED":
                row["interruption"] = "BLOCKED_BY_PRIOR_STOP" if report["interruption"] else "NOT_MEASURED"
            elif row["status"] == "RESERVED":
                row["status"], row["interruption"] = "INCOMPLETE", "DRIVER_INTERRUPTED_WHILE_RESERVED"
        atomic_json(report_path, report)
    print(json.dumps({"status": report["status"], "completed_component_rows": sum(r["status"] == "COMPLETED" for r in report["profiles"]),
                      "planned_component_rows": len(report["profiles"]), "complete_work_budget_admitted": False}))
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--worker", choices=("conformance",) + CASES)
    parser.add_argument("--size", default="all")
    parser.add_argument("--seconds", type=float, default=260)
    args = parser.parse_args()
    if args.worker:
        worker(args.root.resolve(), args.output.resolve(), args.worker, args.size, args.seconds)
    else:
        run(args.root, args.output)


if __name__ == "__main__":
    main()
