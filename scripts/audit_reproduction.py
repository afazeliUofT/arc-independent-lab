#!/usr/bin/env python3
"""Read-only consistency audit of the Phase 1 trace; not independent review.

The runner is parsed, never imported. Only an explicitly new receipt is written.
All computations use Python's standard library and the recorded observations.
"""
import argparse
import ast
import csv
import hashlib
import io
import itertools
import json
import math
from pathlib import Path
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
RAW_NAMES = {
    "resolved_config.yaml", "git_state.txt", "environment_info.json", "manifest.json",
    "stdout.log", "stderr.log", "transitions.jsonl", "hypotheses.jsonl", "metrics.csv",
    "results.json", "SHA256SUMS",
}
SOURCE_NAMES = {
    "scripts/run_reproduction.py", "dependencies.lock.json",
    "docs/P1_REPRODUCTION_DESIGN.md", "configs/P1_LINEAR_INTERFERENCE.json",
}


class Inconsistency(Exception):
    pass


class Checks:
    def __init__(self, atol):
        self.atol = atol
        self.count = 0
        self.max_absolute_residual = 0.0

    def require(self, condition, label):
        self.count += 1
        if not condition:
            raise Inconsistency(label)

    def equal(self, actual, expected, label):
        if isinstance(expected, dict):
            self.require(isinstance(actual, dict), label + ": expected object")
            self.require(set(actual) == set(expected), label + ": field inventory")
            for key, value in expected.items():
                self.equal(actual[key], value, label + "." + key)
        elif isinstance(expected, (list, tuple)):
            self.require(isinstance(actual, (list, tuple)), label + ": expected array")
            self.require(len(actual) == len(expected), label + ": array length")
            for index, value in enumerate(expected):
                self.equal(actual[index], value, f"{label}[{index}]")
        elif isinstance(expected, float):
            self.require(type(actual) in (int, float) and math.isfinite(actual), label + ": finite number")
            error = abs(actual - expected)
            self.max_absolute_residual = max(self.max_absolute_residual, error)
            self.require(error <= self.atol, f"{label}: residual {error!r} > {self.atol!r}")
        else:
            self.require(type(actual) is type(expected) and actual == expected, label + ": value/type mismatch")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def reject_constant(value):
    raise Inconsistency("Nonfinite JSON constant: " + value)


def parse_json(data):
    return json.loads(data, parse_constant=reject_constant)


def inspect_interfaces(check, source):
    tree = ast.parse(source)
    functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    specifications = {
        "decode_old_estimate": (["arm", "theta"], {"arm", "theta"}),
        "learner_step": (["theta", "x", "response", "eta", "enabled"],
                         {"theta", "x", "response", "eta", "enabled", "sum", "zip",
                          "prediction", "gradient", "delta", "w", "v", "g", "d"}),
    }
    result = {}
    for name, (arguments, allowed_loads) in specifications.items():
        check.require(name in functions, "source function exists: " + name)
        node = functions[name]
        check.equal([arg.arg for arg in node.args.args], arguments, name + " argument names")
        check.require(not (node.args.posonlyargs or node.args.kwonlyargs or node.args.vararg or
                           node.args.kwarg or node.args.defaults or node.args.kw_defaults or
                           node.decorator_list), name + " has only stated positional interface")
        check.require(not any(isinstance(item, (ast.Global, ast.Nonlocal, ast.Import,
                                               ast.ImportFrom, ast.Attribute))
                              for item in ast.walk(node)), name + " has no explicit nonlocal/import/attribute access")
        loads = {item.id for item in ast.walk(node)
                 if isinstance(item, ast.Name) and isinstance(item.ctx, ast.Load)}
        check.require(loads <= allowed_loads, name + " unexpected loaded names: " + str(loads - allowed_loads))
        calls = [item for item in ast.walk(tree)
                 if isinstance(item, ast.Call) and isinstance(item.func, ast.Name) and item.func.id == name]
        check.require(len(calls) == 1, name + " has exactly one static call site")
        check.require(not calls[0].keywords and
                      all(isinstance(arg, ast.Name) for arg in calls[0].args), name + " direct call arguments")
        check.equal([arg.id for arg in calls[0].args], arguments, name + " call inputs")
        result[name] = {"arguments": arguments, "loaded_names": sorted(loads), "static_call_sites": len(calls)}
    return result


def audit(run_dir, receipt):
    check = Checks(1e-12)
    receipt["checks"] = {}
    try:
        entries = list(run_dir.iterdir())
        check.require(all(p.is_file() and not p.is_symlink() for p in entries), "raw directory contains regular files only")
        check.equal(sorted(p.name for p in entries), sorted(RAW_NAMES), "raw file inventory")
        raw = {p.name: p.read_bytes() for p in entries}
        inventory = {}
        for line in raw["SHA256SUMS"].decode().splitlines():
            parts = line.split("  ")
            check.require(len(parts) == 2, "hash inventory line format")
            expected_hash, name = parts
            check.require(name in RAW_NAMES - {"SHA256SUMS"} and name not in inventory,
                          "hash inventory membership/uniqueness")
            check.equal(digest(raw[name]), expected_hash, "raw SHA256: " + name)
            inventory[name] = expected_hash
        check.equal(sorted(inventory), sorted(RAW_NAMES - {"SHA256SUMS"}), "complete raw hash inventory")
        receipt["raw_inventory_sha256"] = digest(raw["SHA256SUMS"])
        receipt["verified_raw_file_hashes"] = inventory
        cfg = parse_json(raw["resolved_config.yaml"])
        manifest = parse_json(raw["manifest.json"])
        results = parse_json(raw["results.json"])
        environment = parse_json(raw["environment_info.json"])
        check.equal(cfg["arithmetic_check_atol"], 1e-12, "frozen arithmetic tolerance")
        check.equal(cfg["experiment_id"], "P1_LINEAR_INTERFERENCE", "experiment identity")
        check.equal(cfg["arms"], ["shared_normalized", "orthogonal_control", "frozen_after_A"], "crossed arms")
        check.equal(cfg["old_gains"], [-1.0, 1.0], "old gain crossing")
        check.equal(cfg["new_gains"], [-1.0, 1.0], "new gain crossing")
        check.equal(cfg["action_schedule"], [-1.0, 1.0], "action schedule")
        check.equal(cfg["learning_rate"], 0.1, "declared learning rate")
        check.equal(cfg["steps_per_context"], 64, "declared phase length")
        check.equal(manifest["completion_status"], "completed", "manifest completion")
        check.equal(manifest["formal_gate_verdict"], None, "no formal gate verdict")
        check.equal(manifest["experiment_id"], cfg["experiment_id"], "manifest experiment")
        check.equal(manifest["run_id"], run_dir.name, "run directory identity")
        check.equal(manifest["generator_version"], cfg["generator_version"], "generator version")
        check.equal(manifest["seed"], cfg["seed"], "deterministic seed declaration")
        check.equal(manifest["config_hash"], digest(raw["resolved_config.yaml"]), "resolved config hash")
        check.equal(sorted(manifest["source_hashes"]), sorted(SOURCE_NAMES), "source hash inventory")
        source_bytes = {}
        for name, expected_hash in manifest["source_hashes"].items():
            source_bytes[name] = (ROOT / name).read_bytes()
            check.equal(digest(source_bytes[name]), expected_hash, "current source SHA256: " + name)
        check.equal(manifest["dependency_lock_hash"], digest(source_bytes["dependencies.lock.json"]), "lock hash")
        check.equal(source_bytes["configs/P1_LINEAR_INTERFERENCE.json"].hex(),
                    raw["resolved_config.yaml"].hex(), "source/resolved config bytes")
        receipt["verified_current_source_hashes"] = manifest["source_hashes"]
        receipt["source_interface_inspection"] = inspect_interfaces(check, source_bytes["scripts/run_reproduction.py"])
        check.equal(manifest["hardware"], environment, "environment duplication")
        git_lines = raw["git_state.txt"].decode().splitlines()
        check.equal(manifest["git_commit"], git_lines[0], "recorded git commit")
        check.equal(manifest["dirty_tree"], bool(git_lines[1:]), "recorded dirty tree flag")
        check.equal(raw["stderr.log"].decode(), "", "empty runner stderr")
        check.equal(manifest["wallclock_limit_seconds"], cfg["wallclock_limit_seconds"], "declared runtime limit")
        check.require(0 <= manifest["wallclock_seconds"] <= cfg["wallclock_limit_seconds"], "recorded runtime within limit")
        check.equal(manifest["token_budget"], 0, "no model token budget")
        check.equal(manifest["prompt_hash"], None, "no prompt hash")

        rows = [parse_json(line) for line in raw["transitions.jsonl"].splitlines()]
        snapshots = [parse_json(line) for line in raw["hypotheses.jsonl"].splitlines()]
        csv_reader = csv.DictReader(io.StringIO(raw["metrics.csv"].decode()))
        metrics = list(csv_reader)
        fields = ["case_id", "context", "phase_step", "old_prediction", "new_prediction", "old_loss",
                  "new_loss", "decoded_old_estimate", "decoder_boundary_error", "old_loss_change"]
        check.equal(csv_reader.fieldnames, fields, "metrics field inventory")
        cases = list(itertools.product(cfg["arms"], cfg["old_gains"], cfg["new_gains"]))
        n, eta = cfg["steps_per_context"], cfg["learning_rate"]
        total = len(cases) * 2 * n
        check.equal(len(rows), total, "transition count")
        check.equal(len(metrics), total, "metric count")
        check.equal(len(snapshots), len(cases), "boundary snapshot count")
        check.equal(len(results["cases"]), len(cases), "summary case count")
        expected_stdout = []
        sqrt2 = math.sqrt(2.0)
        for index, (arm, old_gain, new_gain) in enumerate(cases):
            case_id = f"case_{index:02d}"
            expected_stdout.append(f"{case_id} {arm}: completed both contexts\n")
            previous = [0.0, 0.0]
            boundary = None
            first_wrong = None
            max_decoder = max_closed = 0.0
            for offset in range(2 * n):
                row_index = index * 2 * n + offset
                row = rows[row_index]
                context = "A" if offset < n else "B"
                step = offset % n + 1
                gain = old_gain if context == "A" else new_gain
                action = (-1.0, 1.0)[(step - 1) % 2]
                if context == "A":
                    x = [action, 0.0]
                elif arm == "orthogonal_control":
                    x = [0.0, action]
                else:
                    x = [action / sqrt2, action / sqrt2]
                response = action * gain
                check.equal(row["theta_before"], previous, f"{case_id} {context}{step} state continuity")
                before = row["theta_before"]
                prediction = before[0] * x[0] + before[1] * x[1]
                enabled = context == "A" or arm != "frozen_after_A"
                gradient = [(prediction - response) * component for component in x]
                delta = [eta * (response - prediction) * component if enabled else 0.0 for component in x]
                after = [before[j] + delta[j] for j in (0, 1)]
                old_prediction = after[0]
                new_prediction = after[1] if arm == "orthogonal_control" else (after[0] + after[1]) / sqrt2
                old_loss = (old_prediction - old_gain) ** 2 / 2
                new_loss = (new_prediction - new_gain) ** 2 / 2
                linear = (before[0] - old_gain) * delta[0]
                quadratic = delta[0] ** 2 / 2
                old_loss_change = old_loss - (before[0] - old_gain) ** 2 / 2
                check.equal(old_loss_change, linear + quadratic, f"{case_id} {context}{step} exact loss increment")
                decoded = after[0] if arm == "orthogonal_control" else after[0] - after[1]
                decoder_error = analytic = None
                if context == "A":
                    check.equal(after, [old_gain * (1 - (1 - eta) ** step), 0.0], f"{case_id} A closed form")
                else:
                    k = boundary[0]
                    if arm == "shared_normalized":
                        summed = sqrt2 * new_gain + (k - sqrt2 * new_gain) * (1 - eta) ** step
                        analytic = [(summed + k) / 2, (summed - k) / 2]
                        check.equal(delta[0], delta[1], f"{case_id} equal B coordinate increments")
                        check.equal(after[0] - after[1], k, f"{case_id} B invariant")
                    elif arm == "orthogonal_control":
                        analytic = [k, new_gain * (1 - (1 - eta) ** step)]
                        check.equal(delta[0], 0.0, f"{case_id} orthogonal unchanged old coordinate")
                    else:
                        analytic = boundary[:]
                        check.equal(delta, [0.0, 0.0], f"{case_id} frozen B no update")
                    check.equal(after, analytic, f"{case_id} B closed form")
                    decoder_error = abs(decoded - k)
                    max_decoder = max(max_decoder, decoder_error)
                    max_closed = max(max_closed, *(abs(after[j] - analytic[j]) for j in (0, 1)))
                    if first_wrong is None and old_prediction * old_gain <= 0:
                        first_wrong = step
                expected = {
                    "case_id": case_id, "arm": arm, "old_gain": old_gain, "new_gain": new_gain,
                    "context": context, "phase_step": step, "action": action, "feature": x,
                    "response": response, "update_enabled": enabled, "theta_before": before,
                    "prediction_before": prediction, "gradient": gradient, "delta": delta,
                    "theta_after": after, "old_prediction": old_prediction, "new_prediction": new_prediction,
                    "old_loss": old_loss, "new_loss": new_loss, "old_loss_change": old_loss_change,
                    "old_loss_change_linear_term": linear, "old_loss_change_quadratic_term": quadratic,
                    "decoded_old_estimate": decoded, "decoder_boundary_error": decoder_error,
                    "analytic_theta_after": analytic, "observer_probes": 2,
                }
                check.equal(row, expected, f"transition[{row_index}]")
                csv_row = metrics[row_index]
                check.equal(sorted(csv_row), sorted(fields), f"metrics[{row_index}] fields")
                for field in fields:
                    value = expected[field]
                    if value is None:
                        check.equal(csv_row[field], "", f"metrics[{row_index}].{field}")
                    elif type(value) is float:
                        check.equal(float(csv_row[field]), value, f"metrics[{row_index}].{field}")
                    else:
                        check.equal(csv_row[field], str(value), f"metrics[{row_index}].{field}")
                # Use the actual serialized state for the next continuity check.
                previous = row["theta_after"]
                if context == "A" and step == n:
                    boundary = previous[:]
                    snapshot = snapshots[index]
                    check.equal(snapshot["case_id"], case_id, "snapshot identity")
                    check.equal(snapshot["stage"], "A_boundary", "snapshot stage")
                    check.equal(snapshot["learner_theta"], boundary, "snapshot boundary state")
                    check.equal(snapshot["observer_snapshot_not_available_to_learner_or_decoder"], True,
                                "snapshot observer-only declaration")
            expected_summary = {
                "case_id": case_id, "arm": arm, "old_gain": old_gain, "new_gain": new_gain,
                "boundary_theta": boundary, "final_theta": after, "boundary_old_prediction": boundary[0],
                "final_old_prediction": old_prediction, "final_new_prediction": new_prediction,
                "final_old_loss": old_loss, "final_new_loss": new_loss, "final_decoded_old_estimate": decoded,
                "first_B_step_wrong_old_sign": first_wrong, "max_decoder_boundary_error": max_decoder,
                "max_closed_form_coordinate_error": max_closed,
            }
            check.equal(results["cases"][index], expected_summary, case_id + " summary")
        check.equal(raw["stdout.log"].decode(), "".join(expected_stdout), "completion log")
        check.equal(results["completion_status"], "completed", "results completion")
        check.equal(results["training_interactions"], total, "results interaction count")
        check.equal(results["observer_probes"], total * 2, "results probe count")
        check.equal(results["scope"], cfg["scope_exclusions"], "results scope")
        for name in ("action_budget", "simulation_budget", "training_interactions_actual"):
            check.equal(manifest[name], total, "manifest " + name)
        for name in ("observer_probe_budget", "observer_probes_actual"):
            check.equal(manifest[name], total * 2, "manifest " + name)
        # Detect replacement during the audit without touching raw output.
        for name, data in raw.items():
            check.equal(digest((run_dir / name).read_bytes()), digest(data), "unchanged during audit: " + name)
        check.equal(sorted(p.name for p in run_dir.iterdir()), sorted(RAW_NAMES), "raw inventory unchanged during audit")
        receipt["counts"] = {"cases": len(cases), "transitions": total, "observer_probes": total * 2}
        receipt["artifact_consistency_passed"] = True
    finally:
        receipt["checks"] = {"assertions_evaluated": check.count,
                             "absolute_tolerance": check.atol,
                             "maximum_observed_absolute_residual": check.max_absolute_residual}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    run_dir, receipt_path = args.run_dir.resolve(), args.receipt.resolve()
    if not run_dir.is_relative_to(ROOT / "artifacts"):
        parser.error("--run-dir must be inside this lab's artifacts directory")
    if not receipt_path.is_relative_to(ROOT) or receipt_path.is_relative_to(run_dir):
        parser.error("--receipt must be inside the lab and outside the raw run directory")
    if receipt_path.exists() or args.receipt.is_symlink():
        parser.error("--receipt must identify a new file; overwriting is forbidden")
    if not receipt_path.parent.is_dir():
        parser.error("--receipt parent directory must already exist")
    receipt = {
        "audit_type": "artifact consistency checking; not independent scientific review",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "run_directory": str(run_dir.relative_to(ROOT)),
        "auditor_source_sha256": digest(Path(__file__).read_bytes()),
        "python_version": sys.version,
        "artifact_consistency_passed": False,
        "formal_gate_verdict": None,
        "limitations": [
            "Same shared workspace and operator; no enforced reviewer isolation.",
            "Checks arithmetic, recorded counts and file consistency, not scientific importance or external validity.",
            "Source inspection is static and limited; it is not an enforced memory/access boundary or general dataflow proof.",
            "Hashes establish equality to declared/current files, not trusted execution provenance or durable remote storage.",
            "Wall-clock, platform, git-state and no-model-call declarations are internally checked where possible, not externally attested.",
            "No statistical inference: deterministic constructed cases and floating-point tolerance only.",
        ],
    }
    try:
        audit(run_dir, receipt)
    except Exception as exc:
        receipt["failure"] = {"type": type(exc).__name__, "message": str(exc)}
    # Exclusive creation: a concurrent receipt cannot be silently overwritten.
    with receipt_path.open("x") as output:
        json.dump(receipt, output, indent=2, allow_nan=False)
        output.write("\n")
    print(json.dumps({"receipt": str(receipt_path.relative_to(ROOT)),
                      "artifact_consistency_passed": receipt["artifact_consistency_passed"]}))
    return 0 if receipt["artifact_consistency_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
