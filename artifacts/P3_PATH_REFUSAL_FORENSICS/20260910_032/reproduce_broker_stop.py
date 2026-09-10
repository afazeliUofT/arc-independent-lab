#!/usr/bin/env python3
"""Synthetic forensic reproduction against the unchanged published controls.

No native client, model, credential access, subprocess, network or Git mutation.
All writable fixtures stay beneath this script's directory. This script does
not provide a reviewer, an operational correction or launch authorization.
"""
from pathlib import Path
from collections import Counter
import hashlib
import importlib.util
import json
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent / "rebuild031/repository"
sys.path.insert(0, str(ROOT / "scripts"))
import p3_review_interface_028 as interface
import p3_review_protocol_028 as protocol
import p3_stage_evidence_030 as evidence


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode()


def write_json(path, value):
    with Path(path).open("xb") as handle:
        handle.write(canonical(value))


def request(path):
    return json.dumps({"id": 1, "method": "item/tool/call", "params": {
        "threadId": "synthetic-thread", "turnId": "synthetic-turn",
        "callId": "synthetic-call", "tool": "read_page_image",
        "arguments": {"path": path}}}).encode()


def fixture(root, malformed_image=False):
    packet, output = root / "packet", root / "output"
    packet.mkdir(); output.mkdir()
    data = {"pages/page0001.png": (b"not png" if malformed_image else b"\x89PNG\r\n\x1a\nsynthetic only", "image"),
            "notes/evidence.txt": (b"synthetic evidence\n", "text")}
    entries = []
    for name, (raw, kind) in data.items():
        path = packet / name
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(raw)
        entries.append({"path": name, "sha256": sha(raw), "kind": kind})
    raw = canonical({"schema_version": 1, "files": entries})
    (packet / "BROKER_MANIFEST.json").write_bytes(raw)
    return packet, output, sha(raw)


def one_case(name, path, expected, mutation=None, malformed_image=False):
    with tempfile.TemporaryDirectory(prefix="synthetic-", dir=HERE) as tmp:
        root = Path(tmp)
        packet, output, pin = fixture(root, malformed_image)
        with interface.ReviewBroker(packet, manifest_sha256=pin, output_root=output) as broker, \
             interface.original.ReviewBroker(packet, manifest_sha256=pin, output_root=output) as forensic:
            baseline = broker.verify_inputs()
            initial = {p.relative_to(packet).as_posix(): sha(p.read_bytes())
                       for p in packet.rglob("*") if p.is_file()}
            if mutation == "changed_bytes":
                (packet / "notes/evidence.txt").write_bytes(b"CHANGED synthetic evidence\n")
            if mutation == "removed_page":
                (packet / "pages/page0001.png").unlink()
            raw_reads = []
            original_read = broker._original._read_raw
            def tracked_read(value):
                raw_reads.append(value)
                return original_read(value)
            broker._original._read_raw = tracked_read
            boundary = protocol.DynamicToolBoundary(broker, thread_id="synthetic-thread",
                                                   turn_id="synthetic-turn")
            action_error = None
            try:
                boundary.handle(request(path))
            except protocol.ProtocolStop as error:
                action_error = str(error)
            failure = boundary.last_failure
            if failure:
                actual = failure["code"]
            elif boundary.receipts[-1]["successful"]:
                actual = "success"
            else:
                actual = "input." + boundary.receipts[-1]["error_code"]
            assert actual == expected, (name, expected, actual)
            operational_postcheck_attempted = False
            def same_as_controller030_packet_after():
                nonlocal operational_postcheck_attempted
                # Exact ordering and predicate from controller030 run_stage.
                if broker._failed:
                    raise RuntimeError("Scientific broker closed before integrity postcheck")
                operational_postcheck_attempted = True
                return broker.verify_inputs()
            observation = {"status": "STOPPED_WITHOUT_VERDICT", "native_process_reaped": True,
                           "primary_failure": {"layer": "session", "reason": action_error}}
            stage = evidence.finalize_stage(output, "science", observation,
                host_checks_call=lambda: {"all_noncredential_checks_pass": True, "failures": []},
                packet_check_call=same_as_controller030_packet_after,
                base_fields={"packet_before": baseline}, write_json=write_json)
            independent_error = None
            try:
                independent_receipt = forensic.verify_inputs()
            except Exception as error:
                independent_receipt = None
                independent_error = interface.classify_broker_failure(error)
            final = {p.relative_to(packet).as_posix(): sha(p.read_bytes())
                     for p in packet.rglob("*") if p.is_file()}
            if failure:
                assert broker._failed is True
                assert operational_postcheck_attempted is False
                assert stage["packet_after"] is None
                assert "packet_after_check_failed" in stage["postcheck_exception_categories"]
            if mutation:
                assert initial != final and independent_receipt is None
            else:
                assert initial == final and independent_receipt == baseline
            if expected == "boundary.resource_path":
                assert raw_reads == [], (name, raw_reads)
            return {"case": name, "synthetic_argument": path, "expected_class": expected,
                "observed_class": actual, "failure": failure, "broker_failed_latch": broker._failed,
                "recoverable_errors": broker.recoverable_input_errors,
                "dispatch_actual_raw_reads": raw_reads,
                "original_packet_after_rehash_attempted": operational_postcheck_attempted,
                "packet_after": stage["packet_after"],
                "postcheck_exception_categories": stage["postcheck_exception_categories"],
                "independent_preopened_verifier_receipt": independent_receipt,
                "independent_preopened_verifier_error": independent_error,
                "synthetic_bytes_unchanged": initial == final,
                "verdict_exists": (output / "REVIEW_VERDICT.json").exists()}


def main():
    cases = [
        ("valid_known_image", "pages/page0001.png", "success", None, False),
        ("canonical_unknown_page", "pages/page0002.png", "boundary.resource_path", None, False),
        ("canonical_typographical_alias", "pages/page001.png", "boundary.resource_path", None, False),
        ("traversal", "../private.png", "boundary.resource_path", None, False),
        ("absolute", "/tmp/private.png", "boundary.resource_path", None, False),
        ("empty_string", "", "boundary.resource_path", None, False),
        ("overlength_string", "x" * 1025, "boundary.resource_path", None, False),
        ("backslash", "pages\\page0001.png", "boundary.resource_path", None, False),
        ("control_character", "pages/page\n0001.png", "boundary.resource_path", None, False),
        ("double_slash", "pages//page0001.png", "boundary.resource_path", None, False),
        ("non_string", 3, "input.resource_path_type", None, False),
        ("known_wrong_kind", "notes/evidence.txt", "input.resource_kind", None, False),
        ("known_missing_file", "pages/page0001.png", "integrity.resource", "removed_page", False),
        ("mutation_during_known_request", "pages/page0001.png", "integrity.resource", "changed_bytes", False),
        ("unknown_request_can_mask_concurrent_mutation", "pages/page0002.png", "boundary.resource_path", "changed_bytes", False),
        ("manifested_malformed_png", "pages/page0001.png", "integrity.packet_format", None, True),
    ]
    outcomes = [one_case(*case) for case in cases]
    historical_root = HERE.parent / "returned"
    session_path = next(historical_root.rglob("science_SESSION.json"))
    stage_path = next(historical_root.rglob("science_STAGE.json"))
    session_raw, stage_raw = session_path.read_bytes(), stage_path.read_bytes()
    session, stage = json.loads(session_raw), json.loads(stage_raw)
    receipts = session["broker_receipts"]
    historical = {
        "session_relative_path": session_path.relative_to(HERE.parent).as_posix(),
        "session_sha256": sha(session_raw), "stage_sha256": sha(stage_raw),
        "status": session["status"], "broker_boundary_failure": session["broker_boundary_failure"],
        "successful_calls": len([r for r in receipts if r["successful"]]),
        "receipt_tool_counts": dict(Counter(r["tool"] for r in receipts)),
        "failed_broker_calls": session["failed_broker_calls"],
        "recoverable_input_errors": session["recoverable_input_errors"],
        "context_compactions_completed": session["native_item_lifecycle"]["context_compactions_completed"],
        "native_event_failure": session["native_event_failure"],
        "elapsed_seconds": session["elapsed_seconds"],
        "native_process_reaped": session["native_process_reaped"],
        "host_checks_pass": stage["host_checks"]["all_noncredential_checks_pass"],
        "packet_before": stage["packet_before"], "packet_after": stage["packet_after"],
        "postcheck_exception_categories": stage["postcheck_exception_categories"],
        "failed_raw_path_recoverable_from_receipt": False,
        "current_private_packet_not_present_here_or_read": True,
    }
    source_paths = ["scripts/p3_review_broker.py", "scripts/p3_review_interface_028.py",
        "scripts/p3_review_protocol_028.py", "scripts/p3_finite_review_030.py",
        "scripts/p3_stage_evidence_030.py"]
    result = {"kind": "P3_BROKER_STOP_FORENSICS_032_SYNTHETIC_v1", "passed": True,
        "case_count": len(outcomes), "cases": outcomes, "historical_observation": historical,
        "sources": [{"path": p, "sha256": sha((ROOT / p).read_bytes())} for p in source_paths],
        "reproduction_sha256": sha(Path(__file__).read_bytes()),
        "native_clients_started": 0, "model_turns_sent": 0, "credentials_accessed": False,
        "historical_files_modified": False, "engineering_only_not_independent_scientific_review": True}
    write_json(HERE / "REPORT.json", result)
    (HERE / "SHA256SUMS").write_text("".join(sha((HERE / p).read_bytes()) + "  " + p + "\n"
        for p in ("reproduce_broker_stop.py", "REPORT.json")))
    print(json.dumps({"passed": True, "case_count": len(outcomes), "report": str(HERE / "REPORT.json")}))


if __name__ == "__main__":
    main()
