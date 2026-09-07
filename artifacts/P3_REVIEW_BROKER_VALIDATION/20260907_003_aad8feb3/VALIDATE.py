"""Final local validation; no client, model or scientific verdict. New-only output."""
from pathlib import Path
import hashlib
import json
import subprocess
import datetime
import importlib.util

r = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
prior = out.parent / "20260907_001"

def sha(body): return hashlib.sha256(body).hexdigest()
def ref(path): return {"path": str(path.relative_to(r)), "sha256": sha(path.read_bytes())}
def module(name):
    spec = importlib.util.spec_from_file_location(name, r / "scripts" / (name + ".py"))
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value); return value

checks = []
for name, count in [("tests/test_p3_review_broker.py", 24), ("tests/test_p3_review_protocol.py", 10),
                    ("tests/test_gate0_client_preflight.py", 8)]:
    tag = Path(name).stem
    err = (prior / (tag + ".stderr")).read_text()
    assert f"Ran {count} tests" in err and err.rstrip().endswith("OK")
    checks.append({"test_source": ref(r / name), "tests": count,
                   "command": ["python3", "-I", "-B", name], "exit_code": 0,
                   "stdout": ref(prior / (tag + ".stdout")), "stderr": ref(prior / (tag + ".stderr")),
                   "reuse": "Passing suite from immediately prior validation; source unchanged"})
name = "scripts/test_gate0_client_mount_plan.py"
p = subprocess.run(["python3", "-I", "-B", name], cwd=r, capture_output=True, timeout=30)
for suffix, data in [("stdout", p.stdout), ("stderr", p.stderr)]:
    with (out / ("mount_tests." + suffix)).open("xb") as f: f.write(data)
assert p.returncode == 0, p.stderr.decode()
assert "Ran 12 tests" in p.stderr.decode()
checks.append({"test_source": ref(r / name), "tests": 12, "exit_code": p.returncode,
               "stdout": ref(out / "mount_tests.stdout"), "stderr": ref(out / "mount_tests.stderr")})
b, p = module("p3_review_broker"), module("p3_review_protocol")
packet = r / "delivery/P3_BROKER_PACKET_20260907_001"
pin = "81940ef910efebd9ea67add1c04b54f6b8fa2c2bf81793f435acb0429263ee23"
privateout = r / "delivery" / ("P3_BROKER_PROTOCOL_INTEGRATION_" + out.name)
privateout.mkdir()
manifest = json.loads((packet / "BROKER_MANIFEST.json").read_bytes())
imagepath = next(x["path"] for x in manifest["files"] if x["kind"] == "image")
with b.ReviewBroker(packet, manifest_sha256=pin, output_root=privateout) as broker:
    channel = p.DynamicToolBoundary(broker, thread_id="synthetic-integration", turn_id="synthetic-turn")
    results = []
    for i, (tool, args) in enumerate([
        ("hash_file", {"path": "IDEAS.md"}),
        ("read_text", {"path": "PACKET_INDEX.json", "offset": 0, "length": 1000}),
        ("read_page_image", {"path": imagepath}), ("run_observer_audit", {})], 1):
        request = {"id": i, "method": "item/tool/call", "params": {
            "arguments": args, "callId": "call" + str(i), "threadId": "synthetic-integration",
            "turnId": "synthetic-turn", "tool": tool}}
        response = json.loads(channel.handle(json.dumps(request).encode()))
        results.append({"tool": tool, "success": response["result"]["success"],
                        "content_types": [x["type"] for x in response["result"]["contentItems"]]})
        if tool == "run_observer_audit":
            audit = json.loads(response["result"]["contentItems"][0]["text"])
            receipt = privateout / audit["receipt_output_id"]
            for dest, source in [("ACTUAL_AUDITOR_RECEIPT.json", receipt),
                                 ("AUDITOR_STDOUT.bin", receipt.parent.parent / "AUDITOR_STDOUT.bin"),
                                 ("AUDITOR_STDERR.bin", receipt.parent.parent / "AUDITOR_STDERR.bin")]:
                with (out / dest).open("xb") as f: f.write(source.read_bytes())
    report = {
        "schema_version": 1, "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "scope": "PI engineering validation, not independent review or observed real-client isolation",
        "unit_tests": checks, "test_count": sum(x["tests"] for x in checks),
        "sources": [ref(r / name) for name in ["scripts/p3_review_broker.py", "scripts/p3_review_protocol.py",
                    "scripts/prepare_p3_broker_packet.py", "scripts/gate0_client_preflight.py", "scripts/gate0_client_mount_plan.py"]],
        "packet": {"manifest_sha256": pin, "files": len(manifest["files"]), "private_contents_not_published": True},
        "actual_broker_protocol_routes": results, "protocol_receipts": channel.receipts, "auditor": audit,
        "public_actual_auditor_receipt": ref(out / "ACTUAL_AUDITOR_RECEIPT.json"),
        "real_codex_or_bwrap_executed": False, "model_called": False, "scientific_verdict_issued": False,
        "limitations": ["Synthetic transport is not full client enforcement.",
                        "Only manifested rendered pages are visually exposed; text/OCR remains fallible.",
                        "Auditor output size is checked after fixed-process capture, not streamed.",
                        "No allowance, subscription entitlement or reviewer verdict was observed."],
        "previous_failed_harness": ref(prior / "REPORT.json"),
        "prospective_correction": "All substantive verdicts require actual fixed audit; dependency verdict may report inability. No verdict has run."}
    with (out / "REPORT.json").open("x") as f: f.write(json.dumps(report, indent=2) + "\n")
with (out / "SHA256SUMS").open("x") as f:
    f.write("".join(sha(x.read_bytes()) + "  " + x.name + "\n" for x in sorted(out.iterdir()) if x.is_file() and x.name != "SHA256SUMS"))
print(json.dumps(ref(out / "REPORT.json")))
