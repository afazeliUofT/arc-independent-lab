#!/usr/bin/env python3
"""Post-execution arithmetic/access consistency check, not independent review."""
import argparse
import ast
import hashlib
import json
import math
from pathlib import Path
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(run_dir):
    hashes = {}
    for line in (run_dir / "SHA256SUMS").read_text().splitlines():
        expected, name = line.split("  ", 1)
        assert name not in hashes and Path(name).name == name
        assert sha(run_dir / name) == expected, name
        hashes[name] = expected
    assert set(hashes) == {p.name for p in run_dir.iterdir()} - {"SHA256SUMS"}
    cfg = json.loads((run_dir / "resolved_config.json").read_text())
    result = json.loads((run_dir / "results.json").read_text())
    manifest = json.loads((run_dir / "manifest.json").read_text())
    freeze = json.loads((run_dir / "protocol_freeze.json").read_text())
    assert manifest["completion_status"] == result["completion_status"] == "completed"
    assert (run_dir / "stderr.log").read_bytes() == b""
    assert manifest["formal_gate_verdict"] is None
    assert manifest["model_calls"] == 0
    for name, expected in freeze["original_protected_hashes"].items():
        assert sha(ROOT / name) == expected, name
    for name, expected in freeze["frozen_input_hashes"].items():
        assert sha(ROOT / name) == expected, name
    assert hashes["source.py"] == freeze["frozen_input_hashes"]["scripts/run_learner_observer.py"]
    assert hashes["resolved_config.json"] == freeze["frozen_input_hashes"]["configs/P2_LEARNER_OBSERVER.json"]
    assert hashes["protocol.md"] == freeze["frozen_input_hashes"][cfg["protocol"]]
    atol, n = cfg["arithmetic_check_atol"], cfg["steps_per_context"]
    cases = {case["case_id"]: case for case in result["cases"]}
    count, api_reads, evaluator_probes, maximum = 0, 0, 0, 0.0
    previous = {}
    for line in (run_dir / "transitions.jsonl").read_text().splitlines():
        row = json.loads(line)
        case = cases[row["case_id"]]
        if row["phase_step"] == 1 and row["context"] == "A":
            previous[row["case_id"]] = [0.0, 0.0]
        assert row["theta_before"] == previous[row["case_id"]]
        feature = row["feature"]
        before = row["theta_before"]
        prediction = sum(x * y for x, y in zip(feature, before))
        expected_delta = [cfg["learning_rate"] * (row["response"] - prediction) * x
                          if row["update_enabled"] else 0.0 for x in feature]
        for actual, expected in zip(row["delta"], expected_delta):
            maximum = max(maximum, abs(actual - expected))
            assert abs(actual - expected) <= atol
        assert row["theta_after"] == [x + y for x, y in zip(before, row["delta"])]
        previous[row["case_id"]] = row["theta_after"]
        # Check geometric traces independently against actual supplied directions.
        for basis, context_feature in [(row["old_basis"], case["old_feature"]),
                                        (row["new_basis"], case["subsequent_feature"])]:
            assert len(basis) <= 1
            for column in basis:
                assert abs(sum(x*x for x in column) - 1) <= atol
                determinant = column[0] * context_feature[1] - column[1] * context_feature[0]
                assert abs(determinant) <= atol
                assert next(x for x in column if abs(x) > cfg["basis_rank_tolerance"]) > 0
        if row["context"] == "B":
            assert row["api_inputs"] == {"theta": row["theta_after"], "old_query": case["old_feature"],
                                          "subsequent_feature": case["subsequent_feature"]}
            assert row["trace_inputs"] == {"theta": row["theta_after"], "old_basis": row["old_basis"],
                                            "new_basis": row["new_basis"], "old_query": case["old_feature"]}
            for output in [row["api_output"], row["trace_output"]]:
                if case["family"] == "collinear":
                    assert output["estimate"] is None
                else:
                    # Uses an evaluator's known training recurrence, not either reader's formula.
                    norm2 = sum(x*x for x in case["old_feature"])
                    expected = case["old_gain"] * (1 - (1-cfg["learning_rate"]*norm2)**n)
                    residual = abs(output["estimate"] - expected)
                    maximum = max(maximum, residual)
                    assert residual <= atol
        count += 1
        api_reads += row["recovery_unlabeled_encoder_calls"]
        evaluator_probes += row["evaluator_probes"]
    assert count == manifest["action_budget"] == result["training_interactions"]
    assert api_reads == manifest["recovery_unlabeled_encoder_call_budget"]
    assert evaluator_probes == manifest["evaluator_probe_budget"]
    source_tree = ast.parse((run_dir / "source.py").read_text())
    restricted = {
        "recover_from_current_map": {"theta", "old_query", "subsequent_feature", "tolerance", "dot", "abs", "zip",
                                     "subsequent_norm", "overlap", "projected", "denominator", "coefficient", "a", "b"},
        "recover_from_update_spans": {"theta", "old_basis", "new_basis", "old_query", "tolerance", "dot", "len", "list",
                                      "range", "enumerate", "math", "zip", "reversed", "sum", "max", "abs", "columns",
                                      "orthonormal", "triangular", "index", "column", "residual", "previous", "direction",
                                      "length", "coefficients", "later", "reconstructed", "axis", "coefficient", "x", "y",
                                      "old_component", "_"}}
    interfaces = {}
    for name, allowed in restricted.items():
        node = next(n for n in source_tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
        loaded = {n.id for n in ast.walk(node) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
        assert loaded <= allowed, (name, sorted(loaded-allowed))
        assert not any(isinstance(n, (ast.Import, ast.ImportFrom, ast.Global, ast.Nonlocal)) for n in ast.walk(node))
        interfaces[name] = {"arguments": [arg.arg for arg in node.args.args], "loaded_names": sorted(loaded)}
    return {"artifact_hashes": hashes, "SHA256SUMS_sha256": sha(run_dir / "SHA256SUMS"),
            "transitions_checked": count, "recovery_unlabeled_encoder_calls": api_reads,
            "evaluator_probes": evaluator_probes, "maximum_arithmetic_residual": maximum,
            "absolute_tolerance": atol, "protected_original_files_checked": len(freeze["original_protected_hashes"]),
            "source_interfaces": interfaces}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    args = parser.parse_args()
    run_dir, receipt_path = args.run_dir.resolve(), args.receipt.resolve()
    if not run_dir.is_relative_to(ROOT / "artifacts") or not receipt_path.is_relative_to(ROOT):
        parser.error("Paths must remain in this lab; raw run must be under artifacts")
    if receipt_path.exists() or receipt_path.is_relative_to(run_dir):
        parser.error("Receipt must be new and outside the raw run")
    receipt = {"timestamp_utc": datetime.now(timezone.utc).isoformat(),
               "run_directory": str(run_dir.relative_to(ROOT)), "auditor_sha256": sha(Path(__file__)),
               "artifact_consistency_passed": False, "formal_gate_verdict": None,
               "limitations": ["Post-execution consistency check; not a prospective scientific gate.",
                               "Same tools/filesystem; not independent review or an enforced information-flow boundary.",
                               "Hashes prove byte equality, not externally attested execution or remote durability."]}
    try:
        receipt.update(audit(run_dir))
        receipt["artifact_consistency_passed"] = True
    except Exception as error:
        receipt["failure"] = {"type": type(error).__name__, "message": str(error)}
    with receipt_path.open("x") as output:
        json.dump(receipt, output, indent=2, allow_nan=False)
        output.write("\n")
    print(json.dumps({"receipt": str(receipt_path.relative_to(ROOT)),
                      "artifact_consistency_passed": receipt["artifact_consistency_passed"]}))
    return 0 if receipt["artifact_consistency_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
