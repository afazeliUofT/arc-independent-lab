#!/usr/bin/env python3
"""Verify and aggregate the saved046 return without starting any measured work.

Only immutable Git objects and explicitly pinned return files are read. The only
write is the requested assessment JSON. Frozen workflow validation is reused;
no workflow, conformance suite, learner, profile, reviewer or model is invoked.
"""
from __future__ import annotations

import argparse
import base64
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import statistics
import subprocess
import sys
import zlib

sys.dont_write_bytecode = True
RETURN_COMMIT = "15574d706eab28c1e099aba8447d527eb5047d91"
CONTENT_COMMIT = "1ff59732974408bd64131691b2ae278f0c244444"
MANIFEST_SHA = "ac773177e0e1e884773982e1ecee089133c6bc4b0c7c520d45c1fbdd48663cc9"
MANIFEST_PATH = "evidence/P3_CHECKPOINT_046_MANIFEST.json"
RETURN_DIR = "artifacts/CHECKPOINT_046_RETURN/" + MANIFEST_SHA
REPORT_SHA = "48a2a92e89cee2b7e16018ec0051fa98561c9c673c1805e37ac6ff71c0ed7f07"
RECEIPT_SHA = "822845e33e6dc9f5070d109806e562922ce2f84d71c3176099a8dbdceb476a5f"
METRICS = ("wall_seconds", "process_cpu_seconds", "peak_rss_bytes", "logical_work",
           "peak_logical_retained_bytes", "output_bytes")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args])


def blob(root, commit, path):
    return git(root, "show", commit + ":" + path)


def load_module(path):
    spec = importlib.util.spec_from_file_location("_assessment046_frozen_workflow", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def extrema(rows):
    result = {}
    for name in METRICS:
        values = [row["metrics"][name] for row in rows]
        maximum = max(values)
        result[name] = {"minimum": min(values), "median": statistics.median(values),
                        "maximum": maximum,
                        "maximum_row_ids": [row["row_id"] for row in rows
                                            if row["metrics"][name] == maximum]}
    return result


def stage_summary(worker):
    started, result = {}, {}
    for event in worker["stage_progress"]:
        stage = event["stage"]
        if event["status"] == "STARTED":
            require(stage not in started, "duplicate stage start")
            started[stage] = event
        elif event["status"] == "COMPLETED":
            require(stage in started, "stage completion without start")
            initial = started.pop(stage)
            group = "trial_decomposition" if stage.startswith("trial_decomposition_") else stage
            item = result.setdefault(group, {"completed_stages": 0, "wall_seconds": 0.0,
                                             "process_cpu_seconds": 0.0, "logical_work": 0})
            item["completed_stages"] += 1
            for key in ("wall_seconds", "process_cpu_seconds", "logical_work"):
                delta = event[key] - initial[key]
                require(delta >= 0, "nonmonotone stage measurement")
                item[key] += delta
    require(not started, "uncompleted stage in completed worker")
    return result


def fraction(value):
    return Fraction(value["numerator"], value["denominator"])


def verify_chain_summary(summary, payload, config):
    state = payload["acquisition"]["state"]
    require(summary["configuration"] == config["mechanism"], "mechanism differs")
    require(summary["environment_calls"] == summary["B_env"] == state["environment_calls"]
            == len(state["events"]), "environment event counts differ")
    require(summary["retained_transitions"] == len(payload["learner"]["transitions"]),
            "retained transition count differs")
    require(summary["physical_target_evaluation_calls"] == 0
            and summary["target_11_call_protocol_measured"] is False
            and summary["target_scores_generated"] is False, "target boundary differs")
    replay = summary["replay"]
    require(replay == payload["replay"] and replay["status"] == "VERIFIED"
            and replay["source_final_state_sha256"] == replay["replayed_final_state_sha256"]
            and replay["environment_calls_issued_by_replay"] == 0
            and replay["scheduler_calls_by_replay"] == 0, "saved replay assertions differ")
    diagnostics = summary["diagnostics"]
    require(len(diagnostics) == summary["scored_trial_count_with_events"]
            == len(replay["boundaries"]), "trial/boundary counts differ")
    require([d["trial_id"] for d in diagnostics] ==
            [b["trial_id"] for b in replay["boundaries"]], "trial identities differ")
    count_only_nonzero = validation_count = 0
    for diagnostic, boundary in zip(diagnostics, replay["boundaries"]):
        require(diagnostic["T0_sha256"] == boundary["pre_table_sha256"]
                and diagnostic["T1_P10_sha256"] == diagnostic["T1_P11_sha256"]
                == boundary["post_table_sha256"], "stored boundary table hashes differ")
        require(diagnostic["identity_verified"] is True, "unverified decomposition")
        if (fraction(diagnostic["gated_credit"]) == 0
                and diagnostic["mean_count_effect"] is not None
                and fraction(diagnostic["mean_count_effect"]) != 0):
            count_only_nonzero += 1
        for row in diagnostic["validation_rows"]:
            validation_count += 1
            require(row["identity_verified"] is True, "unverified validation identity")
            count_effect, partition_effect = fraction(row["count_effect"]), fraction(row["partition_effect"])
            raw_gain = fraction(row["raw_gain"])
            brier = {key: fraction(value) for key, value in row["brier"].items()}
            require(count_effect == brier["P00"] - brier["P10"]
                    and partition_effect == brier["P10"] - brier["P11"]
                    and raw_gain == count_effect + partition_effect, "stored numeric identity differs")
    readouts = summary["readout_count"]
    require(readouts == len(payload["readers"]) == len(summary["choices"])
            == 4 + summary["selected_predicate_count"]
            and summary["deletion_readout_count"] == summary["selected_predicate_count"],
            "selected/order/deletion readout counts differ")
    require(all(len(choices) == config["decisions_per_readout"]
                for choices in summary["choices"].values()), "chooser decision counts differ")
    require(summary["five_action_prediction_count"] == readouts * 20 * 5
            and summary["retained_reader_count_including_replay_and_trial_fits"]
            == 1 + 3 * len(diagnostics) + readouts, "reader or forecast counts differ")
    return {"validation_events": validation_count,
            "count_effect_nonzero_with_zero_gated_credit_trials": count_only_nonzero,
            "diagnostic_status_counts": dict(sorted(Counter(d["status"] for d in diagnostics).items())),
            "stored_numeric_identities_checked": validation_count,
            "verification_scope": "Saved values and graph consistency; no learner or forecast recomputation"}


def decode_archive(container, workflow):
    workflow.validate_evidence_archive(container)
    archive = container["archive"]
    decoder = zlib.decompressobj()
    pending, pieces = base64.b64decode(archive["data"], validate=True), []
    total = 0
    while pending:
        part = decoder.decompress(pending, 1024 ** 2)
        total += len(part)
        require(total <= archive["uncompressed_bytes"] <= 128 * 1024 ** 2,
                "bounded archive expansion exceeded")
        pieces.append(part)
        pending = decoder.unconsumed_tail
    require(decoder.eof and not decoder.unused_data and total == archive["uncompressed_bytes"],
            "bounded archive stream differs")
    raw = b"".join(pieces)
    require(sha(raw) == archive["uncompressed_sha256"], "decoded hash differs")
    return json.loads(raw), {key: value for key, value in archive.items() if key != "data"}


def assess(root, git_root=None):
    git_root = root if git_root is None else git_root
    manifest_raw = blob(git_root, CONTENT_COMMIT, MANIFEST_PATH)
    require(sha(manifest_raw) == MANIFEST_SHA, "manifest bytes differ")
    manifest = json.loads(manifest_raw)
    public = {pin["path"]: blob(git_root, CONTENT_COMMIT, pin["path"]) for pin in manifest["inputs"]}
    require(all(sha(public[pin["path"]]) == pin["sha256"] for pin in manifest["inputs"]),
            "public manifest input differs")
    public[MANIFEST_PATH] = manifest_raw
    # Import only the unchanged validator and its helper, never the profile module.
    for path in ("scripts/checkpoint046_workflow.py", "scripts/stage_source_packet038.py"):
        require((root / path).read_bytes() == public[path], "validator/helper checkout differs")
    workflow = load_module(root / "scripts/checkpoint046_workflow.py")
    release = {"kind": "P3_CHECKPOINT_046_RELEASE_v1", "repository": workflow.REPOSITORY,
               "content_commit": CONTENT_COMMIT, "accepted_return_commit": workflow.RETURN_COMMIT,
               "manifest_path": MANIFEST_PATH, "manifest_sha256": MANIFEST_SHA}
    report_raw = blob(git_root, RETURN_COMMIT, RETURN_DIR + "/REPORT.json")
    receipt_raw = blob(git_root, RETURN_COMMIT, RETURN_DIR + "/RECEIPT.json")
    require(sha(report_raw) == REPORT_SHA and sha(receipt_raw) == RECEIPT_SHA, "return pins differ")
    files = {name: blob(git_root, RETURN_COMMIT, RETURN_DIR + "/" + name)
             for name in sorted(workflow.WORKER_NAMES)}
    report = workflow.validate_saved_report(report_raw, release, public, files)
    receipt = json.loads(receipt_raw)
    require(report["status"] == "PROFILE_COMPLETED", "profile not completed")
    # This reconstruction checks receipt claims/counts. Private packet bytes are
    # deliberately neither read nor re-audited; their count is manifest metadata.
    expected_return = workflow.return_files(release, report, public, manifest["private_files"], files)
    require(expected_return[RETURN_DIR + "/RECEIPT.json"] == receipt_raw, "receipt reconstruction differs")
    source_pins = report["source_pins"]
    for pin in source_pins:
        require(blob(git_root, RETURN_COMMIT, pin["path"]) == public[pin["path"]],
                "returned source bytes differ")
    parents = git(git_root, "show", "-s", "--format=%P", RETURN_COMMIT).decode().split()
    require(len(parents) == 1, "return is not a single-parent commit")
    diff = git(git_root, "diff-tree", "--no-commit-id", "--name-status", "-r", RETURN_COMMIT).decode().splitlines()
    require(sorted(diff) == sorted("A\t" + path for path in expected_return),
            "return commit does not add exactly the 51 allowed files")
    git(git_root, "merge-base", "--is-ancestor", CONTENT_COMMIT, parents[0])
    historical_diff = git(git_root, "diff", "--name-only", workflow.RETURN_COMMIT, RETURN_COMMIT,
                          "--", "artifacts/CHECKPOINT_043_RETURN", "artifacts/CHECKPOINT_044_RETURN",
                          "artifacts/CHECKPOINT_045_RETURN").decode().splitlines()
    require(not historical_diff, "043/044/045 return bytes changed")
    require(report["reservation_consumed"] is True and report["profile_launches_observed"] == 1
            and receipt["profile_launches_observed"] == 1
            and all(row["attempt_reserved"] is True for row in report["profile_report"]["profiles"]),
            "once-reserved execution claims differ")
    config = json.loads(public["configs/P3_FULL_WORK_FIXTURES_046.json"])
    rows = report["profile_report"]["profiles"]
    require(len(rows) == 48, "wrong completed row count")
    row_details, archive_pins = [], []
    for row in rows:
        worker = json.loads(files[row["row_id"] + ".json"])
        require(row["status"] == worker["status"] == "COMPLETED", "row completion differs")
        for key in ("metrics", "source_hashes", "error_detail", "interruption"):
            require(row[key] == worker[key], "worker/index " + key + " differs")
        # Frozen profile046.compact_worker_report drops only stage.detail from
        # the index; full detail remains in the separately hash-pinned worker.
        compact_stages = [{key: value for key, value in stage.items() if key != "detail"}
                          for stage in worker["stage_progress"]]
        require(row["stage_progress"] == compact_stages, "worker/index stage projection differs")
        require(row["process_evidence"]["returncode"] == 0
                and row["process_evidence"]["parent_timeout"] is False
                and not worker["metrics"]["meter"]["refusals"], "worker process/refusal differs")
        summary = worker["summary"]
        container = summary["complete_evidence_serialization" if row["case"] == "complete_chain"
                            else "overlap_serialization"]
        payload, archive = decode_archive(container, workflow)
        archive_pins.append({"row_id": row["row_id"], **archive})
        scalar = {key: value for key, value in summary.items() if not isinstance(value, (dict, list))}
        checks = verify_chain_summary(summary, payload, config) if row["case"] == "complete_chain" else {}
        row_details.append({"row_id": row["row_id"], "case": row["case"], "size": row["size"],
                            "arm": row["arm"], "repetition": row["repetition"],
                            "worker_sha256": row["full_worker_report"]["sha256"],
                            "summary": scalar, "checks": checks, "stages": stage_summary(worker)})
    groups = defaultdict(list)
    for row in rows:
        groups[(row["case"], row["size"], row["arm"] or "NONE")].append(row)
    archive_by_id = {entry["row_id"]: entry for entry in archive_pins}
    group_results = []
    for (case, size, arm), group in sorted(groups.items()):
        hashes = [archive_by_id[row["row_id"]]["uncompressed_sha256"] for row in group]
        group_results.append({"case": case, "size": size, "arm": None if arm == "NONE" else arm,
                              "row_ids": [row["row_id"] for row in group], "metrics": extrema(group),
                              "decoded_evidence_identical_across_repetitions": len(set(hashes)) == 1,
                              "cpu_max_min_ratio": max(r["metrics"]["process_cpu_seconds"] for r in group)
                              / min(r["metrics"]["process_cpu_seconds"] for r in group)})
    largest = [row for row in rows if row["case"] == "complete_chain" and row["size"] == "largest"]
    largest_details = [row for row in row_details if row["case"] == "complete_chain"
                       and row["size"] == "largest"]
    stage_totals = {}
    for stage in sorted({stage for row in largest_details for stage in row["stages"]}):
        values = [(row["row_id"], row["stages"][stage]) for row in largest_details
                  if stage in row["stages"]]
        stage_totals[stage] = {"row_count": len(values),
                               "completed_stages": sum(value["completed_stages"] for _, value in values)}
        for metric in ("wall_seconds", "process_cpu_seconds", "logical_work"):
            maximum = max(value[metric] for _, value in values)
            stage_totals[stage][metric] = {"sum": sum(value[metric] for _, value in values),
                                           "maximum_per_row": maximum,
                                           "maximum_row_ids": [row_id for row_id, value in values
                                                               if value[metric] == maximum]}
    maxima = extrema(largest)
    projections = {}
    for metric in ("wall_seconds", "process_cpu_seconds", "output_bytes"):
        maximum = maxima[metric]["maximum"]
        projections[metric] = {"observed_maximum": maximum,
                               "source_row_ids": maxima[metric]["maximum_row_ids"],
                               "times_960": maximum * 960,
                               "times_960_times_2": maximum * 960 * 2,
                               "times_960_times_2_times_1_25": maximum * 960 * 2 * 1.25}
    conformance = json.loads(files["CONFORMANCE.json"])
    all_return_pins = [{"path": path, "bytes": len(raw), "sha256": sha(raw)}
                       for path, raw in sorted(expected_return.items())]
    return {"kind": "P3_CHECKPOINT_046_RETURN_VERIFICATION_047_v1", "status": "VERIFIED_SCOPED_PROFILE",
            "assessment_script_sha256": sha(Path(__file__).read_bytes()),
            "assessment_scope": "Collaborative read-only saved-evidence audit; not independent scientific review",
            "return_commit": RETURN_COMMIT, "content_commit": CONTENT_COMMIT,
            "source_pins": source_pins, "manifest_sha256": MANIFEST_SHA,
            "frozen_validator_sha256": sha(public["scripts/checkpoint046_workflow.py"]),
            "frozen_validator_helper_sha256": sha(public["scripts/stage_source_packet038.py"]),
            "verification": {"frozen_validate_saved_report": "PASSED", "exact_receipt_reconstruction": "PASSED",
                             "public_manifest_input_files_checked": len(manifest["inputs"]),
                             "public_snapshot_files_including_manifest": len(public),
                             "private_packet_file_count_from_manifest_only": len(manifest["private_files"]),
                             "private_packet_bytes_reaudited": False, "raw_worker_files_checked": len(files),
                             "bounded_archives_checked": len(archive_pins), "completed_rows": len(rows),
                             "conformance_tests_passed": conformance["summary"]["tests_run"],
                             "return_commit_only_adds_exact_51_allowed_files": True,
                             "return_parent": parents[0], "historical043044045_artifacts_unchanged": True,
                             "one_reserved_profile_launch_reported": True,
                             "launch_count_scope": "Cross-checked frozen report/receipt/process evidence; no private runtime reservation file access",
                             "new_profile_or_conformance_execution": False},
            "usage": {"new_native_starts": 0, "new_model_turns_sent": 0,
                      "cumulative_native_starts": receipt["cumulative_native_starts"],
                      "cumulative_model_turns_sent": receipt["cumulative_model_turns_sent"],
                      "reviewer_started": False, "target_experiment_started": False,
                      "scope": "Receipt-pinned historical and invocation usage; this assessment invokes no model/reviewer tool"},
            "execution": report["execution"], "aggregate_metrics": report["profile_report"]["aggregate_metrics"],
            "host": report["profile_report"]["host"], "global_row_extrema": extrema(rows),
            "groups": group_results, "rows": row_details, "archive_pins": archive_pins,
            "largest_chain_stage_aggregates": stage_totals,
            "return_file_pins": all_return_pins,
            "disk": {"actual_return_files": len(all_return_pins),
                     "actual_return_bytes": sum(pin["bytes"] for pin in all_return_pins),
                     "actual_worker_and_conformance_bytes": sum(len(raw) for raw in files.values()),
                     "decoded_archive_bytes_total": sum(pin["uncompressed_bytes"] for pin in archive_pins)},
            "planning_arithmetic": {"scope": "Illustrative scaling of observed fabricated largest-chain maxima only; NOT an admitted target bound, budget or worst-case guarantee",
                                    "acquisitions": 960, "illustrated_reserve_factor": 2,
                                    "illustrated_grid_audit_factor": 1.25, "values": projections,
                                    "memory": "Sequential acquisitions do not multiply peak RSS by960. Per-process RSS is neither logical B_mem nor aggregate process-tree memory.",
                                    "exclusions": ["Physical target eleven-call evaluator and evaluator archival output",
                                                   "Different target labels/geometries and hardware/host conditions",
                                                   "Complete scientific operation, temporary allocation and refusal accounting"],
                                    "scientific_reserve_applicability": "042 reserve factors remain conditional on eligible validated complete-work measurements; this arithmetic does not satisfy that prerequisite"},
            "stage_scope": "Differences between named start/completion checkpoints; unassigned setup/checkpoint/final-report overhead remains outside stage sums",
            "coverage_limitations": report["profile_report"]["coverage_limitations"],
            "next_decision": "Accept046 physical fabricated-graph observations; finish one bounded versioned full-accounting correction, then scientific preregistration/verifier and restricted independently metered review required by042",
            "B_comp": None, "B_mem": None, "target_execution_admitted": False,
            "complete_work_budget_admitted": False, "maximal_geometry_proved": False,
            "independent_scientific_review_completed": False, "candidate_ranking_or_efficacy_inferred": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--git-repo", type=Path,
                        help="Separate read-only Git object repository for a staged source snapshot")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.repo.resolve()
    output = args.output or root / "evidence/P3_CHECKPOINT_046_RETURN_VERIFICATION_047.json"
    result = assess(root, args.git_repo.resolve() if args.git_repo else None)
    output.write_text(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print("046 saved-evidence verification: VERIFIED_SCOPED_PROFILE; 48 rows,49 workers,48 bounded archives; no experiments started.")
    print("Assessment SHA-256:", sha(output.read_bytes()))


if __name__ == "__main__":
    main()
