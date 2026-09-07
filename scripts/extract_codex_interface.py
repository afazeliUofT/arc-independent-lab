#!/usr/bin/env python3
"""Extract pinned Codex protocol data without executing the Codex binary.

Inputs are the official 0.151.0 musl release TAR and exact-tag source files.
The binary exists only in memory. No model/client/service/configuration is run.
"""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import tarfile

import zstandard

TAR_BYTES = 103937941
TAR_SHA256 = "605b4b183f22c645f5def63a5b7191767407fb66a6feaec4eaf10b5b7e0058f6"
BINARY_BYTES = 270815680
BINARY_SHA256 = "9739cbc928b9c573be83256acd46668f5dd4f119d2d09e05246895ca2aaf0c9a"
COMMIT = "78c290807ce710180111df227df3b7a4fe845452"
BLOBS = {
    "stable": (143100, "56895c586151628e8f5448e43c21f65b933d5be4bec62c8beea7d96a07b3dd42", 301),
    "experimental": (147559, "0fbf7cf19643e220e6e6e57553b8745ef73554ab023fcd58810058bd2a1ccd2a", 413),
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def parse(data):
    return json.loads(data, object_pairs_hook=unique_pairs)


def pinned_read(path, size, digest):
    with path.open("rb") as stream:
        data = stream.read(size + 1)
    if len(data) != size or sha(data) != digest:
        raise ValueError(f"pinned bytes mismatch: {path.name}")
    return data


def relative(name):
    path = PurePosixPath(name)
    if (not name or path.is_absolute() or "\\" in name or ":" in name
            or any(part in ("", ".", "..") for part in name.split("/"))):
        raise ValueError(f"invalid export path: {name!r}")
    return Path(*path.parts)


def write_new(root, name, data):
    path = root / relative(name)
    path.parent.mkdir(parents=True, exist_ok=True)
    if any(parent.is_symlink() for parent in [path, *path.parents]):
        raise ValueError("symlink in export path")
    with path.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    if path.read_bytes() != data:
        raise ValueError(f"saved bytes differ: {name}")
    return {"path": name, "bytes": len(data), "sha256": sha(data)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-tar", type=Path, required=True)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    output = args.output.resolve()
    if not output.is_relative_to(repo) or output == repo or output.exists():
        raise ValueError("output must be a new directory inside this repository")
    tar_bytes = pinned_read(args.release_tar, TAR_BYTES, TAR_SHA256)
    with tarfile.open(fileobj=io.BytesIO(tar_bytes), mode="r:gz") as archive:
        members = archive.getmembers()
        if (len(members) != 1 or not members[0].isfile()
                or members[0].name != "codex-x86_64-unknown-linux-musl"
                or members[0].size != BINARY_BYTES):
            raise ValueError("unexpected release TAR member")
        with archive.extractfile(members[0]) as stream:
            binary = stream.read(BINARY_BYTES + 1)
    if len(binary) != BINARY_BYTES or sha(binary) != BINARY_SHA256:
        raise ValueError("release binary does not match observed laptop executable")
    # Validate everything before creating the export directory.
    payloads = []
    blob_receipts = []
    schema_entries = []
    for kind, (size, digest, count) in BLOBS.items():
        name = f"app-server-exports-{kind}.json.zst"
        compressed = pinned_read(args.sources / name, size, digest)
        offset = binary.find(compressed)
        if offset < 0 or binary.count(compressed) != 1:
            raise ValueError(f"{kind} source blob not uniquely embedded in exact binary")
        with zstandard.ZstdDecompressor().stream_reader(io.BytesIO(compressed)) as stream:
            decoded = stream.read(16 * 1024 * 1024 + 1)
        if len(decoded) > 16 * 1024 * 1024:
            raise ValueError("decompressed export exceeds bound")
        exports = parse(decoded)
        schemas = exports["json_schema"]
        if not isinstance(schemas, dict) or len(schemas) != count:
            raise ValueError("unexpected schema map")
        payloads.append((f"sources/{name}", compressed))
        for name, contents in sorted(schemas.items()):
            relative(name)
            if not name.endswith(".json") or not isinstance(contents, str):
                raise ValueError("unexpected schema type")
            parse(contents)
            schema_bytes = contents.encode("utf-8")
            schema_entries.append({"set": kind, "path": name,
                                   "bytes": len(schema_bytes), "sha256": sha(schema_bytes)})
        # Keep original filenames and exact schema strings in one map per set.
        # This avoids hundreds of tiny Git files and preserves reconstructibility.
        payloads.append((f"schemas/{kind}.json",
                         (json.dumps(schemas, indent=2) + "\n").encode("utf-8")))
        blob_receipts.append({
            "kind": kind, "compressed_bytes": size, "compressed_sha256": digest,
            "binary_offset": offset, "occurrences": 1,
            "decompressed_bytes": len(decoded), "decompressed_sha256": sha(decoded),
            "json_schema_files": count,
        })
    sources = parse((args.sources / "SOURCE_DOWNLOADS.json").read_bytes())
    for item in sources:
        data = pinned_read(args.sources / item["local_name"], item["bytes"], item["sha256"])
        payloads.append(("sources/" + item["local_name"], data))
    for name in ("SOURCE_DOWNLOADS.json", "release-api.json", "tag-ref.json", "tag-object.json"):
        data = (args.sources / name).read_bytes()
        if len(data) > 2 * 1024 * 1024:
            raise ValueError("metadata exceeds bound")
        parse(data)
        payloads.append(("sources/" + name, data))
    config = pinned_read(args.sources / "config-schema.json", 193737,
                         "ed663d6d4c6c8b36917596882414c93858f6cf9ca5449ea8c616fc76d1aac114")
    parse(config)
    payloads.append(("config-schema.json", config))
    names = [name for name, _ in payloads]
    if len(names) != len(set(names)) or len(names) > 1000:
        raise ValueError("duplicate or excessive output paths")
    output.mkdir(parents=True)
    files = [write_new(output, name, data) for name, data in payloads]
    receipt = {
        "schema_version": 1, "access_date": "2026-09-07",
        "method": "Read verified release TAR into memory; verify exact laptop binary; match embedded blobs; decode data without executing binary",
        "release_url": "https://github.com/openai/codex/releases/tag/rust-v0.151.0",
        "release_api_url": "https://api.github.com/repos/openai/codex/releases/tags/rust-v0.151.0",
        "release_commit": COMMIT, "release_tar_bytes": TAR_BYTES,
        "release_tar_sha256": TAR_SHA256, "binary_bytes": BINARY_BYTES,
        "binary_sha256": BINARY_SHA256, "binary_executed": False,
        "model_called": False, "client_or_service_started": False,
        "source_method": "Exact-tag generator copies json_schema string map from embedded precomputed stable/experimental exports",
        "limitations": ["Static interface evidence only; no effective laptop configuration, entitlement, startup or full-tool enforcement measurement"],
        "extractor_sha256": sha(Path(__file__).read_bytes()),
        "blobs": blob_receipts, "schema_entries": schema_entries, "files": files,
    }
    receipt_bytes = (json.dumps(receipt, indent=2) + "\n").encode()
    write_new(output, "MANIFEST.json", receipt_bytes)
    for item in files:
        pinned_read(output / item["path"], item["bytes"], item["sha256"])
    print(json.dumps({"output": str(output), "manifest_sha256": sha(receipt_bytes),
                      "declared_files": len(files), "schema_files": sum(x[2] for x in BLOBS.values()),
                      "binary_executed": False}))


if __name__ == "__main__":
    main()
