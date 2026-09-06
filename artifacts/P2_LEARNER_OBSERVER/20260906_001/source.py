#!/usr/bin/env python3
"""Frozen, isolated learner-access diagnostic; no candidate evaluation or network."""
import argparse
import csv
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def dot(left, right):
    return sum(x * y for x, y in zip(left, right))


def extend_basis(basis, delta, tolerance):
    """Only actual update deltas enter; magnitude and global sign are discarded."""
    residual = list(delta)
    for column in basis:
        coefficient = dot(column, residual)
        residual = [x - coefficient * y for x, y in zip(residual, column)]
    norm = math.sqrt(dot(residual, residual))
    if norm <= tolerance:
        return [list(column) for column in basis]
    direction = [x / norm for x in residual]
    for component in direction:
        if abs(component) > tolerance:
            if component < 0:
                direction = [-x for x in direction]
            break
    return [list(column) for column in basis] + [direction]


def recover_from_current_map(theta, old_query, subsequent_feature, tolerance):
    """Generic geometry from the learner's own current, unlabeled feature API."""
    subsequent_norm = dot(subsequent_feature, subsequent_feature)
    if subsequent_norm <= tolerance:
        return {"status": "abstain_zero_subsequent_feature", "estimate": None}
    overlap = dot(old_query, subsequent_feature) / subsequent_norm
    projected = [a - overlap * b for a, b in zip(old_query, subsequent_feature)]
    denominator = dot(projected, old_query)
    if abs(denominator) <= tolerance:
        return {"status": "abstain_collinear_features", "estimate": None,
                "projection_denominator": denominator}
    coefficient = dot(projected, theta) / denominator
    return {"status": "recovered", "estimate": coefficient * dot(old_query, old_query),
            "projection_denominator": denominator}


def recover_from_update_spans(theta, old_basis, new_basis, old_query, tolerance):
    """No geometry ID, feature API, labels, gains or boundary snapshot is read."""
    if not old_basis:
        return {"status": "abstain_no_old_span", "estimate": None}
    columns = old_basis + new_basis
    if len(columns) > len(theta):
        return {"status": "abstain_overlapping_spans", "estimate": None}
    orthonormal, triangular = [], [[0.0] * len(columns) for _ in columns]
    for index, column in enumerate(columns):
        residual = list(column)
        for previous, direction in enumerate(orthonormal):
            triangular[previous][index] = dot(direction, residual)
            residual = [x - triangular[previous][index] * y
                        for x, y in zip(residual, direction)]
        length = math.sqrt(dot(residual, residual))
        if length <= tolerance:
            return {"status": "abstain_overlapping_spans", "estimate": None}
        triangular[index][index] = length
        orthonormal.append([x / length for x in residual])
    coefficients = [dot(direction, theta) for direction in orthonormal]
    for index in reversed(range(len(columns))):
        coefficients[index] = (coefficients[index] - sum(
            triangular[index][later] * coefficients[later]
            for later in range(index + 1, len(columns)))) / triangular[index][index]
    reconstructed = [sum(column[axis] * coefficient
                         for column, coefficient in zip(columns, coefficients))
                     for axis in range(len(theta))]
    residual = max(abs(x - y) for x, y in zip(theta, reconstructed))
    if residual > tolerance * 100:
        return {"status": "abstain_unexplained_state", "estimate": None,
                "reconstruction_residual": residual}
    old_component = [sum(old_basis[index][axis] * coefficients[index]
                         for index in range(len(old_basis)))
                     for axis in range(len(theta))]
    return {"status": "recovered", "estimate": dot(old_component, old_query),
            "reconstruction_residual": residual}


class FeatureAPI:
    """Supplied fixed learner model; context encoding never returns a response."""
    def __init__(self, old_feature, subsequent_feature):
        self._features = {"A": tuple(old_feature), "B": tuple(subsequent_feature)}

    def encode(self, context, action):
        return [action * value for value in self._features[context]]


def learner_step(theta, feature, response, learning_rate, enabled):
    prediction = dot(theta, feature)
    gradient = [(prediction - response) * value for value in feature]
    delta = [-learning_rate * value if enabled else 0.0 for value in gradient]
    return [weight + change for weight, change in zip(theta, delta)], prediction, delta


def transform(vector, geometry):
    cosine, sine = math.cos(geometry["angle_radians"]), math.sin(geometry["angle_radians"])
    x, y = vector
    if geometry["reflection"]:
        y = -y
    return [cosine * x - sine * y, sine * x + cosine * y]


def make_cases(cfg):
    cases = []
    for geometry in cfg["geometries"]:
        for number, (arm, old_gain, new_gain) in enumerate(itertools.product(
                cfg["arms"], cfg["old_gains"], cfg["new_gains"])):
            a = transform([1.0, 0.0], geometry)
            b = transform([0.0, 1.0] if arm == "orthogonal_control"
                          else [1 / math.sqrt(2), 1 / math.sqrt(2)], geometry)
            cases.append({"case_id": f'{geometry["id"]}_case_{number:02d}',
                          "family": "original_crossing", "geometry": geometry["id"],
                          "original_case_id": f"case_{number:02d}", "arm": arm,
                          "old_gain": old_gain, "new_gain": new_gain,
                          "old_feature": a, "subsequent_feature": b})
    if cfg["collinear_control"]:
        for number, (old_gain, new_gain) in enumerate(itertools.product(
                cfg["old_gains"], cfg["new_gains"])):
            cases.append({"case_id": f"collinear_{number:02d}", "family": "collinear",
                          "geometry": "identity", "original_case_id": None,
                          "arm": "collinear", "old_gain": old_gain, "new_gain": new_gain,
                          "old_feature": [1.0, 0.0], "subsequent_feature": [1.0, 0.0]})
    if cfg["ambiguous_history_pair"]:
        contraction = 1 - (1 - cfg["learning_rate"]) ** cfg["steps_per_context"]
        radius = (contraction + math.sqrt(contraction ** 2 + 4 * contraction ** 3)) / 2
        height = math.sqrt(radius ** 2 - contraction ** 2)
        for sign in (-1.0, 1.0):
            cases.append({"case_id": "ambiguity_negative" if sign < 0 else "ambiguity_positive",
                          "family": "ambiguity", "geometry": "constructed_unknown_B",
                          "original_case_id": None, "arm": "shared_unknown_geometry",
                          "old_gain": sign, "new_gain": 1.0,
                          "old_feature": [1.0, 0.0],
                          "subsequent_feature": [-sign * contraction / radius, height / radius],
                          "analytic_final_theta": [0.0, height]})
    return cases


def verify_frozen_inputs(config_path):
    cfg = json.loads(config_path.read_text())
    if cfg["experiment_id"] != "P2_LEARNER_OBSERVER":
        raise ValueError("Unexpected experiment identity")
    receipt_path = ROOT / cfg["freeze_receipt"]
    receipt = json.loads(receipt_path.read_text())
    for name, expected in receipt["frozen_input_hashes"].items():
        if sha(ROOT / name) != expected:
            raise ValueError("Prospective freeze mismatch: " + name)
    if receipt["frozen_input_hashes"][str(config_path.relative_to(ROOT))] != sha(config_path):
        raise ValueError("Config absent from prospective freeze")
    for name, expected in receipt["original_protected_hashes"].items():
        if sha(ROOT / name) != expected:
            raise ValueError("Original protected input mismatch: " + name)
    return cfg, receipt


def run(config_path, run_id):
    cfg, freeze = verify_frozen_inputs(config_path)
    if not re.fullmatch(r"[A-Za-z0-9_-]+", run_id):
        raise ValueError("Unsafe run id")
    limit = cfg["wallclock_limit_seconds"]
    if not 0 < limit <= 60:
        raise ValueError("Internal time limit must be in (0,60] seconds")
    out = ROOT / "artifacts" / cfg["experiment_id"] / run_id
    out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    timestamp = datetime.now(timezone.utc).isoformat()
    git_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    git_status = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True)
    (out / "git_state.txt").write_text(git_head + "\n" + git_status)
    (out / "resolved_config.json").write_bytes(config_path.read_bytes())
    (out / "protocol.md").write_bytes((ROOT / cfg["protocol"]).read_bytes())
    (out / "source.py").write_bytes(Path(__file__).read_bytes())
    (out / "protocol_freeze.json").write_bytes((ROOT / cfg["freeze_receipt"]).read_bytes())
    environment = {"python": sys.version, "platform": platform.platform(),
                   "implementation": platform.python_implementation(), "visible_cpus": os.cpu_count(),
                   "gpu_used": False, "hpc_used": False, "network_calls": 0, "model_calls": 0}
    dump(out / "environment_info.json", environment)
    cases, summaries, transitions = make_cases(cfg), [], 0
    steps, eta, atol = cfg["steps_per_context"], cfg["learning_rate"], cfg["arithmetic_check_atol"]
    rank_tolerance = cfg["basis_rank_tolerance"]
    original_rows = {}
    for line in (ROOT / cfg["original_run"] / "transitions.jsonl").read_text().splitlines():
        row = json.loads(line)
        original_rows[(row["case_id"], row["context"], row["phase_step"])] = row
    manifest = {"experiment_id": cfg["experiment_id"], "run_id": run_id, "timestamp_utc": timestamp,
                "git_commit": git_head, "dirty_tree": bool(git_status),
                "frozen_input_hashes": freeze["frozen_input_hashes"],
                "freeze_receipt_sha256": sha(ROOT / cfg["freeze_receipt"]),
                "original_protected_hashes": freeze["original_protected_hashes"],
                "environment": environment, "seed": None, "prompt_hash": None, "model_calls": 0,
                "action_budget": len(cases) * 2 * steps,
                "simulation_budget": len(cases) * 2 * steps,
                "evaluator_probe_budget": len(cases) * 4 * steps,
                "recovery_unlabeled_encoder_call_budget": len(cases) * 2 * steps,
                "persistent_state_access": cfg["reader_interfaces"],
                "wallclock_limit_seconds": limit, "completion_status": "running",
                "formal_gate_verdict": None, "independent_review": False}
    dump(out / "manifest.json", manifest)
    status, comparison_residual = "failed", 0.0
    with (out / "stdout.log").open("w") as stdout, (out / "stderr.log").open("w") as stderr, \
         (out / "transitions.jsonl").open("w") as trace, \
         (out / "metrics.csv").open("w", newline="") as metrics:
        fields = ["case_id", "context", "phase_step", "ordinary_old_prediction", "ordinary_new_prediction",
                  "api_estimate", "trace_estimate", "api_boundary_error", "trace_boundary_error"]
        writer = csv.DictWriter(metrics, fieldnames=fields)
        writer.writeheader()
        try:
            for case in cases:
                feature_api = FeatureAPI(case["old_feature"], case["subsequent_feature"])
                theta, old_basis, new_basis, boundary = [0.0, 0.0], [], [], None
                max_api_error, max_trace_error, api_success, trace_success = 0.0, 0.0, 0, 0
                ordinary_first_wrong = None
                for context, gain in [("A", case["old_gain"]), ("B", case["new_gain"])]:
                    for step in range(1, steps + 1):
                        if time.monotonic() - started >= limit:
                            raise TimeoutError("Declared internal runtime limit reached")
                        action = cfg["action_schedule"][(step - 1) % len(cfg["action_schedule"])]
                        feature = feature_api.encode(context, action)
                        response, before = action * gain, list(theta)
                        enabled = not (case["arm"] == "frozen_after_A" and context == "B")
                        theta, prediction, delta = learner_step(theta, feature, response, eta, enabled)
                        if context == "A":
                            old_basis = extend_basis(old_basis, delta, rank_tolerance)
                        else:
                            new_basis = extend_basis(new_basis, delta, rank_tolerance)
                        # Evaluation outputs cannot enter either reader or the update-span builder.
                        ordinary_old = dot(theta, feature_api.encode("A", 1.0))
                        ordinary_new = dot(theta, feature_api.encode("B", 1.0))
                        api_inputs = trace_inputs = api_output = trace_output = None
                        api_error = trace_error = None
                        if context == "B":
                            # These calls are unlabeled operations of the supplied learner model.
                            old_query = feature_api.encode("A", 1.0)
                            subsequent_feature = feature_api.encode("B", 1.0)
                            api_output = recover_from_current_map(theta, old_query, subsequent_feature, rank_tolerance)
                            trace_output = recover_from_update_spans(theta, old_basis, new_basis, old_query, rank_tolerance)
                            api_inputs = {"theta": theta, "old_query": old_query,
                                          "subsequent_feature": subsequent_feature}
                            trace_inputs = {"theta": theta, "old_basis": old_basis,
                                            "new_basis": new_basis, "old_query": old_query}
                            if api_output["estimate"] is not None:
                                api_error = abs(api_output["estimate"] - boundary["prediction"])
                                max_api_error, api_success = max(max_api_error, api_error), api_success + 1
                            if trace_output["estimate"] is not None:
                                trace_error = abs(trace_output["estimate"] - boundary["prediction"])
                                max_trace_error, trace_success = max(max_trace_error, trace_error), trace_success + 1
                            if ordinary_first_wrong is None and ordinary_old * case["old_gain"] <= 0:
                                ordinary_first_wrong = step
                        row = {"case_id": case["case_id"], "context": context, "phase_step": step,
                               "action": action, "feature": feature, "response": response,
                               "theta_before": before, "prediction_before": prediction,
                               "update_enabled": enabled, "delta": delta, "theta_after": list(theta),
                               "old_basis": old_basis, "new_basis": new_basis,
                               "ordinary_old_prediction": ordinary_old, "ordinary_new_prediction": ordinary_new,
                               "api_inputs": api_inputs, "trace_inputs": trace_inputs,
                               "api_output": api_output, "trace_output": trace_output,
                               "evaluator_boundary_prediction": None if boundary is None else boundary["prediction"],
                               "api_estimate": None if api_output is None else api_output["estimate"],
                               "trace_estimate": None if trace_output is None else trace_output["estimate"],
                               "api_boundary_error": api_error, "trace_boundary_error": trace_error,
                               "evaluator_probes": 2, "recovery_unlabeled_encoder_calls": 2 if context == "B" else 0}
                        trace.write(json.dumps(row, allow_nan=False) + "\n")
                        writer.writerow({name: row[name] for name in fields})
                        transitions += 1
                        if case["family"] == "original_crossing" and case["geometry"] == "identity":
                            reference = original_rows[(case["original_case_id"], context, step)]
                            for current, previous in [(theta, reference["theta_after"]), (delta, reference["delta"]),
                                                      ([ordinary_old], [reference["old_prediction"]]),
                                                      ([ordinary_new], [reference["new_prediction"]])]:
                                comparison_residual = max(comparison_residual,
                                                          *(abs(x - y) for x, y in zip(current, previous)))
                    if context == "A":
                        boundary = {"theta": list(theta), "prediction": ordinary_old,
                                    "evaluator_only": True}
                expected_recovery = case["family"] != "collinear"
                case_consistency = ((api_success == steps and trace_success == steps and
                                     max_api_error <= atol and max_trace_error <= atol)
                                    if expected_recovery else (api_success == 0 and trace_success == 0))
                summaries.append({**case, "boundary": boundary, "final_theta": list(theta),
                                  "final_ordinary_old_prediction": ordinary_old,
                                  "final_ordinary_new_prediction": ordinary_new,
                                  "final_api_output": api_output, "final_trace_output": trace_output,
                                  "old_basis": old_basis, "new_basis": new_basis,
                                  "max_api_boundary_error": max_api_error if api_success else None,
                                  "max_trace_boundary_error": max_trace_error if trace_success else None,
                                  "api_recovery_steps": api_success, "trace_recovery_steps": trace_success,
                                  "first_B_step_wrong_old_sign": ordinary_first_wrong,
                                  "declared_arithmetic_consistency": case_consistency})
                stdout.write(case["case_id"] + ": completed both contexts\n")
            ambiguity = [case for case in summaries if case["family"] == "ambiguity"]
            collision = {"claim_scope": "weights plus old query only, over the declared unknown-B-map class; not the original full API",
                         "gains": "Both histories use old gains in {-1,+1} and new gain +1; no continuous-gain extension is needed.",
                         "maximum_final_weight_difference": max(abs(x - y) for x, y in zip(
                             ambiguity[0]["final_theta"], ambiguity[1]["final_theta"])),
                         "boundary_prediction_difference": abs(ambiguity[0]["boundary"]["prediction"] -
                                                               ambiguity[1]["boundary"]["prediction"]),
                         "same_old_query": ambiguity[0]["old_feature"] == ambiguity[1]["old_feature"],
                         "different_subsequent_feature": ambiguity[0]["subsequent_feature"] != ambiguity[1]["subsequent_feature"]}
            protected_unchanged = all(sha(ROOT / name) == expected
                                      for name, expected in freeze["original_protected_hashes"].items())
            consistent = (all(case["declared_arithmetic_consistency"] for case in summaries)
                          and comparison_residual <= atol and protected_unchanged
                          and collision["maximum_final_weight_difference"] <= atol
                          and collision["same_old_query"] and collision["boundary_prediction_difference"] > atol)
            status = "completed" if consistent else "completed_with_arithmetic_disagreement"
        except Exception:
            traceback.print_exc(file=stderr)
            collision, protected_unchanged, consistent = None, False, False
        finally:
            dump(out / "results.json", {"completion_status": status, "cases": summaries,
                 "training_interactions": transitions, "arithmetic_check_atol": atol,
                 "original_identity_maximum_residual": comparison_residual,
                 "original_protected_files_unchanged": protected_unchanged,
                 "ambiguous_history_comparison": collision,
                 "declared_arithmetic_consistency": consistent,
                 "formal_gate_verdict": None, "statistical_inference": "None; exact constructions and arithmetic checks only",
                 "scope_exclusions": cfg["scope_exclusions"]})
            manifest.update(completion_status=status, wallclock_seconds=time.monotonic() - started,
                            training_interactions_actual=transitions, original_protected_files_unchanged=protected_unchanged)
            dump(out / "manifest.json", manifest)
    files = sorted(path for path in out.iterdir() if path.is_file())
    (out / "SHA256SUMS").write_text("".join(f"{sha(path)}  {path.name}\n" for path in files))
    print(json.dumps({"artifact_directory": str(out.relative_to(ROOT)), "status": status,
                      "manifest_sha256": sha(out / "manifest.json"),
                      "results_sha256": sha(out / "results.json")}))
    return 0 if status == "completed" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    sys.exit(run(args.config.resolve(), args.run_id))
