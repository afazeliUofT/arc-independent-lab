#!/usr/bin/env python3
"""Assemble exact reviewer inputs locally. No model, client, network or Git writes.

Copyrighted papers and reading derivatives stay in ignored delivery/. The output
is new-only and every source is verified against an existing pinned inventory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
CORE = "delivery/P3_REVIEW_INPUT_CORE_20260907_001"
READING = "delivery/P3_REVIEW_METHOD_SUPPLEMENT_20260907_001"
PINS = {
    f"{CORE}/MANIFEST.json": "d4eb4bb4b531c5fb97aca7ff597b2c2f8242835449203a2cb588e0930ba458ae",
    f"{READING}/MANIFEST.json": "92088c800e7d2120774e894f402c33f0080eacc2b0148d7a7e50120056cd415a",
    "evidence/P3_REVIEW_METHOD_COVERAGE_2026-09-07.json": "9fdeec39cb84294cbe8a19c6f5511c5c5905bd25695d9832132ae0bc19e7a559",
    "evidence/P3_REVIEW_EXECUTION_CLOSURE_2026-09-07.json": "28db528e70e361593545f94ca72b4bd2eaf4cc0ed0705edd5cfdcbb29c10a2a5",
    "evidence/P3_AUDIT_REVIEW_MANIFEST.json": "8d475e93aa21db5d7210f337c036e2705e3a4b83b6d99d43d715161d63b7e374",
    "evidence/P3_RESIDUAL_REVIEW_MANIFEST.json": "f7249d53060349fdfbaca2102672457e3e8966ef510d6853322b10da75762128",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_parts(relative: str) -> tuple[str, ...]:
    p = PurePosixPath(relative)
    if not relative or p.is_absolute() or p.as_posix() != relative or any(
        x in ("", ".", "..") for x in relative.split("/")
    ) or "\\" in relative or "\x00" in relative:
        raise ValueError("Invalid relative packet path")
    return p.parts


def checked_source(root: Path, relative: str, expected: str) -> bytes:
    p = root
    for part in safe_parts(relative):
        p = p / part
        if p.is_symlink():
            raise ValueError(f"Source symlink rejected: {relative}")
    data = p.read_bytes()
    if digest(data) != expected:
        raise ValueError(f"Source hash mismatch: {relative}")
    return data


def assemble(output: Path) -> dict:
    output = output.absolute()
    relative = output.relative_to(ROOT)
    if len(relative.parts) != 2 or relative.parts[0] != "delivery":
        raise ValueError("Output must be one new directory directly under project delivery/")
    if output.exists() or output.is_symlink():
        raise ValueError("Output already exists; preserved without changes")
    if (ROOT / "delivery").is_symlink():
        raise ValueError("Delivery symlink rejected")
    docs = {p: json.loads(checked_source(ROOT, p, h)) for p, h in PINS.items()}
    core = docs[f"{CORE}/MANIFEST.json"]
    coverage = docs["evidence/P3_REVIEW_METHOD_COVERAGE_2026-09-07.json"]
    closure = docs["evidence/P3_REVIEW_EXECUTION_CLOSURE_2026-09-07.json"]
    payload: dict[str, tuple[bytes, str]] = {}

    def add(source_root: Path, path: str, expected: str, kind: str = "text") -> None:
        data = checked_source(source_root, path, expected)
        if path in payload and payload[path] != (data, kind):
            raise ValueError(f"Conflicting inventories for {path}")
        payload[path] = (data, kind)

    for e in core["public_inputs"]:
        add(ROOT / CORE / "public", e["path"], e["sha256"])
    for e in closure["view_input_files"]:
        add(ROOT, e["path"], e["sha256"])
    for p in ("evidence/P3_REVIEW_METHOD_COVERAGE_2026-09-07.json",
              "evidence/P3_REVIEW_EXECUTION_CLOSURE_2026-09-07.json"):
        add(ROOT, p, PINS[p])
    for e in coverage["source_entries"]:
        add(ROOT / CORE, e["offline_core_path"], e["source_sha256"], "binary")
    for e in docs[f"{READING}/MANIFEST.json"]["files"]:
        if e["path"].startswith("reading_text/") or e["path"].endswith(".png"):
            add(ROOT / READING, e["path"], e["sha256"],
                "image" if e["path"].endswith(".png") else "text")
    for p in ("evidence/P3_AUDIT_REVIEW_MANIFEST.json",
              "evidence/P3_RESIDUAL_REVIEW_MANIFEST.json"):
        for e in docs[p]["files"]:
            if digest(payload[e["path"]][0]) != e["sha256"]:
                raise ValueError("Scientific packet pin mismatch")
    index = {
        "scope": "Neutral resource index; claims are in the two frozen review packets. No verdict supplied.",
        "start_here": ["docs/P3_AUDIT_REVIEW_PACKET.md", "docs/P3_RESIDUAL_REVIEW_SUPPLEMENT.md"],
        "method_source_index": "evidence/P3_REVIEW_METHOD_COVERAGE_2026-09-07.json",
        "execution_dependencies": "evidence/P3_REVIEW_EXECUTION_CLOSURE_2026-09-07.json",
        "reading_limits": "Text/OCR is a fallible aid. Pinned original PDFs control; scanned method images are provided. Request missing inspection capability explicitly.",
        "files": [{"path": p, "sha256": digest(b), "kind": k, "bytes": len(b)}
                  for p, (b, k) in sorted(payload.items())],
    }
    payload["PACKET_INDEX.json"] = ((json.dumps(index, indent=2) + "\n").encode(), "text")
    manifest = {"schema_version": 1, "files": [
        {"path": p, "sha256": digest(b), "kind": k}
        for p, (b, k) in sorted(payload.items())]}
    manifest_bytes = (json.dumps(manifest, indent=2) + "\n").encode()
    # Validate the complete dependency graph before creating any destination.
    output.mkdir(mode=0o700)
    for p, (data, _kind) in sorted(payload.items()):
        dest = output.joinpath(*safe_parts(p))
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("xb") as f:
            f.write(data)
        os.chmod(dest, 0o600)
        if digest(dest.read_bytes()) != digest(data):
            raise ValueError(f"Destination readback mismatch: {p}")
    with (output / "BROKER_MANIFEST.json").open("xb") as f:
        f.write(manifest_bytes)
    return {"packet": output.relative_to(ROOT).as_posix(),
            "manifest_sha256": digest(manifest_bytes), "files": len(payload),
            "bytes": sum(len(b) for b, _ in payload.values()),
            "private_material": True, "public_redistribution_authorized": False,
            "model_called": False, "reviewer_boundary_verified": False}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    print(json.dumps(assemble(args.output), indent=2))


if __name__ == "__main__":
    main()
