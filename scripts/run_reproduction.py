#!/usr/bin/env python3
"""Canonical experiment entry point. Phase 1 diagnostic witness only.

The learner is deliberately transparent: only theta persists between updates.
The diagnostic decoder is an observer, never part of learning or prediction.
"""
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


def dump(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n")


def feature(arm, context, action):
    if context == "A":
        return (action, 0.0)
    if arm == "orthogonal_control":
        return (0.0, action)
    return (action / math.sqrt(2.0), action / math.sqrt(2.0))


def predict(theta, arm, context, action=1.0):
    x = feature(arm, context, action)
    return sum(w * v for w, v in zip(theta, x))


def learner_step(theta, x, response, eta, enabled):
    """No old label, boundary snapshot or context history is accessible here."""
    prediction = sum(w * v for w, v in zip(theta, x))
    gradient = [(prediction - response) * v for v in x]
    delta = [-eta * g if enabled else 0.0 for g in gradient]
    return [w + d for w, d in zip(theta, delta)], prediction, gradient, delta


def decode_old_estimate(arm, theta):
    """Observer-only fixed decoder, called only by evaluation code."""
    return theta[0] if arm == "orthogonal_control" else theta[0] - theta[1]


def run(config_path, run_id):
    cfg = json.loads(config_path.read_text())
    if cfg["experiment_id"] != "P1_LINEAR_INTERFERENCE":
        raise ValueError("Unsupported experiment")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", run_id):
        raise ValueError("Unsafe run id")
    limit = cfg["wallclock_limit_seconds"]
    if not 0 < limit <= 300:
        raise ValueError("Declared runtime must be in (0,300] seconds")
    out = ROOT / "artifacts" / cfg["experiment_id"] / run_id
    out.mkdir(parents=True, exist_ok=False)  # Raw runs are never overwritten.
    started = time.monotonic()
    created = datetime.now(timezone.utc).isoformat()
    (out / "resolved_config.yaml").write_bytes(config_path.read_bytes())
    git_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    git_status = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True)
    (out / "git_state.txt").write_text(git_head + "\n" + git_status)
    environment = {"python": sys.version, "implementation": platform.python_implementation(),
                   "platform": platform.platform(), "machine": platform.machine(),
                   "visible_cpu_count": os.cpu_count(), "gpu_used": False}
    dump(out / "environment_info.json", environment)
    cases = list(itertools.product(cfg["arms"], cfg["old_gains"], cfg["new_gains"]))
    n, eta = cfg["steps_per_context"], cfg["learning_rate"]
    sources = ["scripts/run_reproduction.py", "dependencies.lock.json",
               "docs/P1_REPRODUCTION_DESIGN.md", "configs/P1_LINEAR_INTERFERENCE.json"]
    manifest = {"experiment_id": cfg["experiment_id"], "run_id": run_id, "timestamp": created,
                "git_commit": git_head, "dirty_tree": bool(git_status),
                "language_version": sys.version, "dependency_lock_hash": sha(ROOT / sources[1]),
                "config_hash": sha(config_path), "source_hashes": {p: sha(ROOT / p) for p in sources},
                "generator_version": cfg["generator_version"], "seed": cfg["seed"],
                "model_identifier": "online linear predictor; no language-model calls",
                "prompt_hash": None, "token_budget": 0,
                "action_budget": len(cases) * 2 * n, "simulation_budget": len(cases) * 2 * n,
                "observer_probe_budget": len(cases) * 2 * n * 2,
                "persistent_state_cap": "2 float64-equivalent Python floats per learner; no other learned state",
                "hardware": environment, "wallclock_limit_seconds": limit,
                "completion_status": "running", "formal_gate_verdict": None}
    dump(out / "manifest.json", manifest)
    records, summaries = 0, []
    status = "failed"
    with (out / "stdout.log").open("w") as stdout, (out / "stderr.log").open("w") as stderr, \
         (out / "transitions.jsonl").open("w") as trace, \
         (out / "hypotheses.jsonl").open("w") as hypotheses, \
         (out / "metrics.csv").open("w", newline="") as metrics:
        writer = csv.DictWriter(metrics, fieldnames=["case_id", "context", "phase_step", "old_prediction",
                              "new_prediction", "old_loss", "new_loss", "decoded_old_estimate",
                              "decoder_boundary_error", "old_loss_change"])
        writer.writeheader()
        try:
            for case_number, (arm, old_gain, new_gain) in enumerate(cases):
                case_id = f"case_{case_number:02d}"
                theta = [0.0, 0.0]
                boundary = None
                first_sign_error = None
                max_decoder_error = 0.0
                max_closed_error = 0.0
                for context, gain in [("A", old_gain), ("B", new_gain)]:
                    for step in range(1, n + 1):
                        if time.monotonic() - started >= limit:
                            raise TimeoutError("Declared internal wall-clock limit reached")
                        # Environment sends only the current x and response to learner_step.
                        action = cfg["action_schedule"][(step - 1) % len(cfg["action_schedule"])]
                        x = feature(arm, context, action)
                        response = action * gain
                        before = theta[:]
                        enabled = not (arm == "frozen_after_A" and context == "B")
                        theta, prediction, gradient, delta = learner_step(theta, x, response, eta, enabled)
                        old_prediction = predict(theta, arm, "A")
                        new_prediction = predict(theta, arm, "B")
                        old_loss = 0.5 * (old_prediction - old_gain) ** 2
                        new_loss = 0.5 * (new_prediction - new_gain) ** 2
                        old_loss_before = 0.5 * (before[0] - old_gain) ** 2
                        linear_term = (before[0] - old_gain) * delta[0]
                        quadratic_term = 0.5 * delta[0] ** 2
                        decoded = decode_old_estimate(arm, theta)
                        decoder_error = None
                        analytic_theta = None
                        if context == "B":
                            k = boundary[0]
                            decoder_error = abs(decoded - k)
                            max_decoder_error = max(max_decoder_error, decoder_error)
                            if arm == "shared_normalized":
                                s = math.sqrt(2.0) * new_gain + (k - math.sqrt(2.0) * new_gain) * (1 - eta) ** step
                                analytic_theta = [(s + k) / 2, (s - k) / 2]
                            elif arm == "orthogonal_control":
                                analytic_theta = [k, new_gain * (1 - (1 - eta) ** step)]
                            else:
                                analytic_theta = boundary[:]
                            max_closed_error = max(max_closed_error, *(abs(w - e) for w, e in zip(theta, analytic_theta)))
                            if first_sign_error is None and old_prediction * old_gain <= 0:
                                first_sign_error = step
                        row = {"case_id": case_id, "arm": arm, "old_gain": old_gain, "new_gain": new_gain,
                               "context": context, "phase_step": step, "action": action,
                               "feature": list(x), "response": response, "update_enabled": enabled,
                               "theta_before": before, "prediction_before": prediction,
                               "gradient": gradient, "delta": delta, "theta_after": theta[:],
                               "old_prediction": old_prediction, "new_prediction": new_prediction,
                               "old_loss": old_loss, "new_loss": new_loss,
                               "old_loss_change": old_loss - old_loss_before,
                               "old_loss_change_linear_term": linear_term,
                               "old_loss_change_quadratic_term": quadratic_term,
                               "decoded_old_estimate": decoded, "decoder_boundary_error": decoder_error,
                               "analytic_theta_after": analytic_theta,
                               "observer_probes": 2}
                        trace.write(json.dumps(row, allow_nan=False) + "\n")
                        writer.writerow({key: row[key] for key in writer.fieldnames})
                        records += 1
                    if context == "A":
                        boundary = theta[:]
                        hypotheses.write(json.dumps({"case_id": case_id, "stage": "A_boundary",
                            "learner_theta": theta, "supplied_hypothesis_class": "context-linear action response",
                            "boundary_operation": "Only weights retained by learner; no previous x, response or prediction reused.",
                            "observer_snapshot_not_available_to_learner_or_decoder": True}) + "\n")
                summaries.append({"case_id": case_id, "arm": arm, "old_gain": old_gain, "new_gain": new_gain,
                    "boundary_theta": boundary, "final_theta": theta,
                    "boundary_old_prediction": boundary[0], "final_old_prediction": old_prediction,
                    "final_new_prediction": new_prediction, "final_old_loss": old_loss,
                    "final_new_loss": new_loss, "final_decoded_old_estimate": decoded,
                    "first_B_step_wrong_old_sign": first_sign_error,
                    "max_decoder_boundary_error": max_decoder_error,
                    "max_closed_form_coordinate_error": max_closed_error})
                stdout.write(f"{case_id} {arm}: completed both contexts\n")
            status = "completed"
        except Exception:
            traceback.print_exc(file=stderr)
        finally:
            dump(out / "results.json", {"completion_status": status, "cases": summaries,
                "training_interactions": records, "observer_probes": records * 2,
                "statistical_inference": "None; deterministic crossed cases, no population sampling",
                "scope": cfg["scope_exclusions"]})
            manifest.update(completion_status=status, wallclock_seconds=time.monotonic() - started,
                            training_interactions_actual=records, observer_probes_actual=records * 2)
            dump(out / "manifest.json", manifest)
    files = sorted(p for p in out.iterdir() if p.is_file())
    (out / "SHA256SUMS").write_text("".join(f"{sha(p)}  {p.name}\n" for p in files))
    print(json.dumps({"artifact_directory": str(out.relative_to(ROOT)), "status": status,
                      "manifest_sha256": sha(out / "manifest.json")}))
    return 0 if status == "completed" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    sys.exit(run(args.config.resolve(), args.run_id))
