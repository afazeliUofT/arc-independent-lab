#!/usr/bin/env python3
"""One-shot corrective continuation; original043 sources/measurements stay immutable."""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib
import itertools
import json
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
sys.path.insert(0, str(Path(__file__).resolve().parent))
import profile043 as frozen

KIND = "P3_DEVELOPMENT_PROFILE_044_v1"
CASES = frozen.CASES
SUITES = frozen.SUITES + ("test_profile044",)
SOURCES = frozen.SOURCES + ("scripts/profile044.py", "configs/P3_PROFILE_CONTINUATION_044.json", "tests/test_profile044.py")
BASELINE_SHA256 = "9de019e2d8649895627e7c25d1e46366f4e08c0c890404c3197da3bed0317f61"
BASELINE_COMMIT = "f025d2ffe0745e40b2d6718293bfe5d72b54b7ba"
encoded, atomic_json, sha256 = frozen.encoded, frozen.atomic_json, frozen.sha256
process_limits, bind_parent_lifetime = frozen.process_limits, frozen.bind_parent_lifetime
Interrupted, NamedResults = frozen.Interrupted, frozen.NamedResults
n1_case, ConstantDevelopmentInterface = frozen.n1_case, frozen.ConstantDevelopmentInterface


def source_hashes(root):
    return {name: sha256(root / name) for name in SOURCES}


def read_config(root):
    config = frozen.read_config(root)
    continuation = json.loads((root / "configs/P3_PROFILE_CONTINUATION_044.json").read_text())
    expected = {"kind": "P3_PROFILE_CONTINUATION_044_v1", "baseline_report_sha256": BASELINE_SHA256,
                "baseline_git_commit": BASELINE_COMMIT, "inherited_fixture_path": "configs/P3_PROFILE_FIXTURES_043.json",
                "imported_completed_row_indices": list(range(6)), "eligible_new_row_indices": list(range(6, 27)),
                "original_failed_row_indices": [6], "original_unstarted_row_indices": list(range(7, 27)),
                "original043_reservation_preserved": True, "imported_rows_remeasured": False,
                "automatic_remeasurement": False, "conformance_suites": list(SUITES),
                "full_work_budget_admitted": False, "target_execution_admitted": False, "native_allowance": 0}
    if any(continuation.get(key) != value for key, value in expected.items()):
        raise ValueError("CONTINUATION_CONFIG_MISMATCH")
    if continuation["new_per_invocation_limits"] != {key: value for key, value in config["limits"].items() if key != "automatic_remeasurement"}:
        raise ValueError("CONTINUATION_LIMIT_MISMATCH")
    if continuation["baseline_source_hashes"] != frozen.source_hashes(root):
        raise ValueError("FROZEN_043_SOURCE_CHANGED")
    return config, continuation


def first_scored_trial(trials):
    """Warm-up rows use counter_t=0 and intentionally lack scored-credit fields."""
    matches = [row for row in trials if row.get("counter_t") == 1 and row.get("phase") != "WARMUP"]
    if len(matches) != 1:
        raise AssertionError("EXPECTED_ONE_FIRST_SCORED_TRIAL")
    return matches[0]


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
        first = first_scored_trial(acquisition.trials)
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


def load_baseline(path, config, continuation):
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != BASELINE_SHA256:
        raise ValueError("BASELINE_REPORT_SHA256_MISMATCH")
    wrapper = json.loads(raw)
    if wrapper.get("kind") != "P3_DEVELOPMENT_PROFILE_EXECUTION_043_v1" or wrapper.get("status") != "PROFILE_INCOMPLETE":
        raise ValueError("BASELINE_REPORT_KIND_OR_STATUS_MISMATCH")
    prior = wrapper["profile_report"]
    if prior["source_hashes"] != continuation["baseline_source_hashes"]:
        raise ValueError("BASELINE_SOURCE_MISMATCH")
    canonical = hashlib.sha256(encoded(prior)).hexdigest()
    if canonical != wrapper["profile_report_canonical_sha256"]:
        raise ValueError("BASELINE_CHILD_HASH_MISMATCH")
    expected = frozen.planned_rows(config)
    if len(prior["profiles"]) != len(expected):
        raise ValueError("BASELINE_ROW_COUNT_MISMATCH")
    for index, (row, planned) in enumerate(zip(prior["profiles"], expected)):
        if any(row[key] != planned[key] for key in ("case", "size", "repetition")):
            raise ValueError("BASELINE_ROW_IDENTITY_MISMATCH")
        required = "COMPLETED" if index < 6 else "FAILED_CONFORMANCE" if index == 6 else "NOT_STARTED"
        if row["status"] != required or (index < 6 and row.get("metrics") is None):
            raise ValueError("BASELINE_ROW_STATUS_MISMATCH")
    if prior["profiles"][6]["interruption"] != "KeyError":
        raise ValueError("BASELINE_FAILURE_MISMATCH")
    return wrapper


def continuation_rows(config, baseline, current_sources):
    prior = baseline["profile_report"]
    rows = frozen.planned_rows(config)
    for index, row in enumerate(rows):
        if index < 6:
            original = prior["profiles"][index]
            row.update(copy.deepcopy(original))
            row["measurement_provenance"] = {
                "release": "043", "imported": True, "remeasured": False,
                "baseline_report_sha256": BASELINE_SHA256, "baseline_git_commit": BASELINE_COMMIT,
                "original_row_index": index, "original_row_canonical_sha256": hashlib.sha256(encoded(original)).hexdigest(),
                "source_hashes": copy.deepcopy(prior["source_hashes"])}
        else:
            row["measurement_provenance"] = {
                "release": "044", "imported": False, "original_row_index": index,
                "original043_status": prior["profiles"][index]["status"],
                "source_hashes": copy.deepcopy(current_sources), "new_invocation_attempt_reserved": False}
    return rows


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
              "summary": None, "limits": None, "metrics": None, "profile_wrapper_version": "044"}
    try:
        config, _ = read_config(root)
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
            last = meter.refusals[-1].get("status")
            report["interruption"] = last if last in ("COMPUTATION_INCOMPLETE", "MEMORY_LIMIT") else "LOGICAL_RESOURCE_REFUSAL"
        else:
            report["status"], report["interruption"] = "FAILED_CONFORMANCE", type(error).__name__
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        child_now = resource.getrusage(resource.RUSAGE_CHILDREN)
        state = meter.state() if meter is not None else None
        report["metrics"] = {
            "wall_seconds": time.monotonic() - started, "process_cpu_seconds": time.process_time() - cpu_started,
            "child_cpu_seconds": (child_now.ru_utime + child_now.ru_stime) - (child_started.ru_utime + child_started.ru_stime),
            "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            "logical_work": state["work"] if state else None, "logical_retained_bytes": state["retained_bytes"] if state else None,
            "peak_logical_retained_bytes": state["peak_retained_bytes"] if state else None,
            "logical_memory_measure": "Meter owner reservations in canonical bytes; a reservation may be conservative and not sealed",
            "memory_measure_is_exact_allocation": False, "output_bytes": 0, "meter": state}
        for _ in range(8):
            length = len(encoded(report))
            if length == report["metrics"]["output_bytes"]:
                break
            report["metrics"]["output_bytes"] = length
        atomic_json(output, report)


def run_child(root, output, case, size_name, remaining):
    command = [sys.executable, "-I", "-B", "-S", str(root / "scripts/profile044.py"), "--root", str(root),
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


def run(root, output, prior_report):
    root, output = Path(root).resolve(), Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    report_path = output / "REPORT.json"
    if report_path.exists():
        retained = json.loads(report_path.read_text())
        print(json.dumps({"status": "RETAINED_FIRST_REPORT", "report_status": retained.get("status")}))
        return retained
    # Validate the exact baseline before consuming the new reservation.
    config, continuation_config = read_config(root)
    baseline = load_baseline(prior_report, config, continuation_config)
    current_sources = source_hashes(root)
    rows = continuation_rows(config, baseline, current_sources)
    reservation = output / "RESERVATION.json"
    reserved_without_report = False
    try:
        with reservation.open("x") as stream:
            json.dump({"kind": KIND, "automatic_remeasurement": False, "baseline_report_sha256": BASELINE_SHA256,
                       "eligible_new_row_indices": continuation_config["eligible_new_row_indices"]}, stream)
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError:
        reserved_without_report = True
    started, cpu_started = time.monotonic(), time.process_time()
    prior_child_usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    report = {"kind": KIND, "status": "INCOMPLETE", "interruption": None,
              "target_experiment_started": False, "target_execution_admitted": False, "native_started": False,
              "outcome_blind": True, "complete_work_budget_admitted": False, "automatic_remeasurement": False,
              "B_comp": None, "B_mem": None, "projection_status": "UNADMITTED_COMPONENTS_ONLY",
              "limitations": copy.deepcopy(baseline["profile_report"]["limitations"]) + [
                  "The combined27-row table has two source versions; imported043 rows are not measurements of patched044 source",
                  "Aggregate metrics describe this044 invocation only; original043 invocation metrics are reported separately",
                  "A failed043 row is attempted under a new explicit044 continuation reservation, never by resetting043"],
              "conformance": None, "profiles": rows, "source_hashes": current_sources, "limits": None,
              "host": {"python": sys.version.split()[0], "platform": sys.platform,
                       "ambient_conditions": "UNCONTROLLED_NOT_CLASSIFIED_QUIET_OR_CONTENDED", "scope": "044_INVOCATION_ONLY"},
              "continuation": {"baseline_report_sha256": BASELINE_SHA256, "baseline_git_commit": BASELINE_COMMIT,
                               "imported_completed_rows": 6, "eligible_new_rows": 21, "imported_rows_remeasured": False,
                               "original043_reservation_preserved": True, "new_rows_attempted": 0, "new_rows_completed": 0,
                               "prior_failed_attempts": [copy.deepcopy(baseline["profile_report"]["profiles"][6])]},
              "invocation_metrics": {"original043": {"aggregate_metrics": copy.deepcopy(baseline["profile_report"]["aggregate_metrics"]),
                                                     "wrapper_execution": copy.deepcopy(baseline["execution"]),
                                                     "host": copy.deepcopy(baseline["profile_report"]["host"])}, "continuation044": None}}
    if reserved_without_report:
        report["interruption"] = "PRIOR_RESERVATION_WITHOUT_REPORT"
        for row in rows[6:]:
            row["interruption"] = report["interruption"]
        atomic_json(report_path, report)
        print(json.dumps({"status": report["status"], "interruption": report["interruption"]}))
        return report
    atomic_json(report_path, report)
    try:
        report["limits"] = process_limits(config["limits"]["driver_wall_seconds"], config["limits"]["address_space_bytes"])
        atomic_json(report_path, report)
        deadline = started + config["limits"]["driver_wall_seconds"]
        report["conformance"] = run_child(root, output / "CONFORMANCE.json", "conformance", "all", deadline - time.monotonic())
        atomic_json(report_path, report)
        if report["conformance"]["status"] != "COMPLETED":
            report["status"] = "FAILED_CONFORMANCE" if report["conformance"]["status"] == "FAILED_CONFORMANCE" else "INCOMPLETE"
            report["interruption"] = "CONFORMANCE_NOT_COMPLETED"
        else:
            for index in continuation_config["eligible_new_row_indices"]:
                row = rows[index]
                remaining = deadline - time.monotonic()
                if remaining < 5:
                    report["interruption"] = "AGGREGATE_WALL_LIMIT"
                    break
                row["status"] = "RESERVED"
                row["measurement_provenance"]["new_invocation_attempt_reserved"] = True
                report["continuation"]["new_rows_attempted"] += 1
                atomic_json(report_path, report)
                result = run_child(root, output / ("COMPONENT_%02d.json" % index), row["case"], row["size"], remaining)
                row.update(result)
                if row["status"] == "COMPLETED":
                    report["continuation"]["new_rows_completed"] += 1
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
        metrics = {"wall_seconds": time.monotonic() - started,
                   "driver_process_cpu_seconds": time.process_time() - cpu_started,
                   "child_cpu_seconds": (usage.ru_utime + usage.ru_stime) - (prior_child_usage.ru_utime + prior_child_usage.ru_stime),
                   "peak_child_rss_bytes": usage.ru_maxrss * 1024,
                   "driver_peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
                   "scope": "044_INVOCATION_ONLY_EXCLUDES_IMPORTED_043_MEASUREMENTS"}
        report["aggregate_metrics"] = metrics
        report["invocation_metrics"]["continuation044"] = copy.deepcopy(metrics)
        for row in rows[6:]:
            if row["status"] == "NOT_STARTED":
                row["interruption"] = "BLOCKED_BY_PRIOR_STOP" if report["interruption"] else "NOT_MEASURED"
            elif row["status"] == "RESERVED":
                row["status"], row["interruption"] = "INCOMPLETE", "DRIVER_INTERRUPTED_WHILE_RESERVED"
        atomic_json(report_path, report)
    print(json.dumps({"status": report["status"], "imported_completed_rows": 6,
                      "new_completed_rows": report["continuation"]["new_rows_completed"],
                      "completed_component_rows": sum(r["status"] == "COMPLETED" for r in rows),
                      "planned_component_rows": len(rows), "complete_work_budget_admitted": False}))
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--prior-report", type=Path)
    parser.add_argument("--worker", choices=("conformance",) + CASES)
    parser.add_argument("--size", default="all")
    parser.add_argument("--seconds", type=float, default=260)
    args = parser.parse_args()
    if args.worker:
        worker(args.root.resolve(), args.output.resolve(), args.worker, args.size, args.seconds)
    else:
        if args.prior_report is None:
            parser.error("--prior-report is required for a continuation invocation")
        run(args.root, args.output, args.prior_report)


if __name__ == "__main__":
    main()
