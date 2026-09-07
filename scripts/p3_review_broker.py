#!/usr/bin/env python3
"""Closed, parent-owned evidence broker; no model, daemon or arbitrary shell.

This module is an implementation component, not proof that the surrounding
reviewer process is isolated. The caller must keep packet/output/control paths
outside the reviewer's write authority and authenticate dynamic tool messages.
No scientific verdict is chosen here. The only executable operation is the
unchanged, SHA-pinned historical arithmetic auditor on its original inventory.

The trusted parent supplies a manifest with exactly schema_version and files;
each file has path, sha256 and kind (text, image, binary). Paths are relative to
one packet root. The manifest itself is pinned externally, never by reviewer
arguments. Private paper derivatives must remain private when making a packet.
"""
from __future__ import annotations

import base64
import copy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import tempfile
import threading


AUDITOR = "scripts/audit_learner_observer.py"
AUDITOR_SHA256 = "871ab1e62a592d9b49f93d5d5d783e262f8db1cb15bcc0b8ba6191f0ca0d4b1e"
CLOSURE = "evidence/P3_REVIEW_EXECUTION_CLOSURE_2026-09-07.json"
CLOSURE_SHA256 = "28db528e70e361593545f94ca72b4bd2eaf4cc0ed0705edd5cfdcbb29c10a2a5"
RAW_DIR = "artifacts/P2_LEARNER_OBSERVER/20260906_001"
HISTORICAL_RECEIPT = "evidence/P2_LEARNER_OBSERVER_CONSISTENCY.json"
REVIEW_MANIFESTS = {
    "original_manifest_sha256": "evidence/P3_AUDIT_REVIEW_MANIFEST.json",
    "supplement_manifest_sha256": "evidence/P3_RESIDUAL_REVIEW_MANIFEST.json",
}
VERDICT_NAME = "REVIEW_VERDICT.json"
VERDICTS = ("GO", "REVISE_ONCE", "KILL", "SUSPEND_FOR_DEPENDENCY")
SUBJECTS = ("C1", "C2", "C3", "C4", "T", "observer")
MAX_FILE_BYTES = 128 * 1024 * 1024
MAX_IMAGE_BYTES = 16 * 1024 * 1024
SHA_RE = re.compile(r"[0-9a-f]{64}\Z")


class BrokerError(RuntimeError):
    """A closed-boundary or integrity check failed; caller must stop the turn."""


def _require(condition, message):
    if not condition:
        raise BrokerError(message)


def _keys(value, required):
    _require(type(value) is dict and set(value) == set(required), "Unexpected argument fields")


def _path(value):
    _require(type(value) is str and 0 < len(value) <= 1024, "Invalid resource path")
    _require("\\" not in value and not any(ord(c) < 32 for c in value), "Invalid resource path")
    parts = value.split("/")
    _require(all(part not in ("", ".", "..") for part in parts), "Noncanonical resource path")
    _require(not PurePosixPath(value).is_absolute(), "Absolute resource path denied")
    return value


def _sha(value):
    _require(type(value) is str and SHA_RE.fullmatch(value), "Invalid SHA-256")
    return value


def _text(value, maximum=30000):
    _require(type(value) is str and bool(value.strip()) and len(value) <= maximum,
             "Expected bounded nonempty text")
    return value


def _integer(value, lower, upper):
    _require(type(value) is int and lower <= value <= upper, "Invalid integer bound")
    return value


def _json(data):
    def pairs(items):
        result = {}
        for key, value in items:
            _require(key not in result, "Duplicate JSON key")
            result[key] = value
        return result
    def constant(value):
        raise BrokerError("Nonfinite JSON number denied")
    try:
        return json.loads(data, object_pairs_hook=pairs, parse_constant=constant)
    except (ValueError, UnicodeError) as error:
        raise BrokerError("Invalid JSON") from error


def _identity(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


def _directory(path):
    """Open an existing absolute directory without following any symlink."""
    path = Path(path)
    _require(path.is_absolute() and ".." not in path.parts, "Trusted root must be absolute")
    _require(hasattr(os, "O_NOFOLLOW") and hasattr(os, "O_DIRECTORY"),
             "Descriptor-relative Linux/POSIX protection unavailable")
    fd = os.open("/", os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        for part in path.parts[1:]:
            next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                              dir_fd=fd)
            os.close(fd)
            fd = next_fd
        return fd
    except BaseException:
        os.close(fd)
        raise


class ReviewBroker:
    """One attended review's closed operations; state is never reviewer-settable.

    Read calls return plain dictionaries; read_page_image supplies measured PNG
    bytes as base64 for the caller's advertised image-content transport. Text
    offsets count decoded Unicode characters, not bytes. A failed operation is
    terminal for this instance. The parent must preserve any failure/partial
    output; no retry or overwrite of a verdict is provided.
    """

    def __init__(self, packet_root, *, manifest_sha256, output_root,
                 manifest_path="BROKER_MANIFEST.json"):
        self.packet_root = Path(packet_root)
        self.output_root = Path(output_root)
        _require(not self.output_root.is_relative_to(self.packet_root) and
                 not self.packet_root.is_relative_to(self.output_root),
                 "Input and output roots must be disjoint")
        self.manifest_path = _path(manifest_path)
        self.manifest_sha256 = _sha(manifest_sha256)
        self._root_fd = _directory(self.packet_root)
        self._output_fd = None
        self._failed = False
        self._verdict_written = False
        self._audited = False
        self._audit_succeeded = False
        self._lock = threading.Lock()
        self._identities = {}
        try:
            self._output_fd = _directory(self.output_root)
            raw, _ = self._read_raw(self.manifest_path)
            _require(hashlib.sha256(raw).hexdigest() == self.manifest_sha256,
                     "Packet manifest digest mismatch")
            manifest = _json(raw)
            _keys(manifest, ("schema_version", "files"))
            _require(type(manifest["schema_version"]) is int and manifest["schema_version"] == 1,
                     "Unsupported manifest version")
            _require(type(manifest["files"]) is list and 0 < len(manifest["files"]) <= 10000,
                     "Invalid file inventory")
            self._files = {}
            for entry in manifest["files"]:
                _keys(entry, ("path", "sha256", "kind"))
                name = _path(entry["path"])
                _require(name != self.manifest_path and name not in self._files,
                         "Duplicate/self manifest resource")
                _sha(entry["sha256"])
                _require(entry["kind"] in ("text", "image", "binary"), "Unsupported resource kind")
                self._files[name] = dict(entry)
            self.verify_inputs()
        except BaseException:
            self.close()
            raise

    def close(self):
        for name in ("_root_fd", "_output_fd"):
            fd = getattr(self, name, None)
            if fd is not None:
                os.close(fd)
                setattr(self, name, None)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def _open(self, path, flags):
        parts = _path(path).split("/")
        parent = os.dup(self._root_fd)
        try:
            for part in parts[:-1]:
                child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                                dir_fd=parent)
                os.close(parent)
                parent = child
            return os.open(parts[-1], flags | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=parent)
        except OSError as error:
            raise BrokerError("Resource opening denied") from error
        finally:
            os.close(parent)

    def _read_raw(self, path):
        fd = self._open(path, os.O_RDONLY | os.O_NONBLOCK)
        try:
            before = os.fstat(fd)
            _require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1,
                     "Resource must be a regular file without hardlink aliases")
            _require(before.st_size <= MAX_FILE_BYTES, "Resource exceeds byte bound")
            chunks, total = [], 0
            while True:
                chunk = os.read(fd, 1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                _require(total <= MAX_FILE_BYTES, "Resource exceeds byte bound")
                chunks.append(chunk)
            after = os.fstat(fd)
            _require(_identity(before) == _identity(after), "Resource changed during read")
            identity = _identity(after)
            if path in self._identities:
                _require(self._identities[path] == identity, "Input identity changed")
            else:
                self._identities[path] = identity
            return b"".join(chunks), identity
        finally:
            os.close(fd)

    def _read(self, path, kind=None):
        path = _path(path)
        _require(path in self._files, "Unmanifested resource denied")
        entry = self._files[path]
        if kind is not None:
            _require(entry["kind"] == kind, "Wrong resource kind")
        raw, _ = self._read_raw(path)
        measured = hashlib.sha256(raw).hexdigest()
        _require(measured == entry["sha256"], "Resource digest mismatch")
        return raw, measured

    def verify_inputs(self):
        """Actual whole-file rehash; call before every model turn as well."""
        _require(not self._failed and self._root_fd is not None, "Broker stopped")
        try:
            manifest, _ = self._read_raw(self.manifest_path)
            _require(hashlib.sha256(manifest).hexdigest() == self.manifest_sha256,
                     "Packet manifest changed")
            for path in self._files:
                self._read(path)
            return {"manifest_sha256": self.manifest_sha256, "files_rehashed": len(self._files)}
        except BaseException:
            self._failed = True
            raise

    def dispatch(self, tool, arguments):
        """No session/authentication implied: parent validates call identity first."""
        with self._lock:
            _require(not self._failed and not self._verdict_written, "Broker already stopped/completed")
            try:
                _require(type(tool) is str and tool in TOOL_SCHEMAS, "Unknown operation")
                self.verify_inputs()
                result = getattr(self, "_" + tool)(arguments)
                self.verify_inputs()
                return result
            except BaseException:
                self._failed = True
                raise

    def _read_text(self, args):
        _keys(args, ("path", "offset", "length"))
        offset = _integer(args["offset"], 0, MAX_FILE_BYTES)
        length = _integer(args["length"], 1, 100000)
        raw, measured = self._read(args["path"], "text")
        try:
            decoded = raw.decode("utf-8")
        except UnicodeError as error:
            raise BrokerError("Resource is not UTF-8 text") from error
        _require(offset <= len(decoded), "Text offset past end")
        return {"path": args["path"], "sha256": measured, "offset": offset,
                "text": decoded[offset:offset + length], "total_characters": len(decoded),
                "next_offset": min(offset + length, len(decoded)),
                "complete": offset + length >= len(decoded)}

    def _read_page_image(self, args):
        _keys(args, ("path",))
        raw, measured = self._read(args["path"], "image")
        _require(len(raw) <= MAX_IMAGE_BYTES and raw.startswith(b"\x89PNG\r\n\x1a\n"),
                 "Expected bounded manifested PNG page")
        return {"path": args["path"], "sha256": measured, "mimeType": "image/png",
                "data_base64": base64.b64encode(raw).decode("ascii")}

    def _hash_file(self, args):
        _keys(args, ("path",))
        raw, measured = self._read(args["path"])
        return {"path": args["path"], "sha256": measured, "bytes": len(raw),
                "measurement": "SHA-256 computed from complete actual file bytes"}

    def _expanded_inventory(self, closure):
        original = closure["original_raw_inventory"]
        additional = closure["post_run_additional_inventory"]
        _require(type(original) is dict and type(additional) is dict and
                 not (set(original) & set(additional)), "Archive partitions overlap")
        merged = {**original, **additional}
        directory = self._open(RAW_DIR, os.O_RDONLY | os.O_DIRECTORY)
        try:
            _require(set(os.listdir(directory)) == set(merged), "Expanded archive membership mismatch")
        finally:
            os.close(directory)
        for name, expected in merged.items():
            _require(_path(name) == PurePosixPath(name).name, "Archive name must be one component")
            _, measured = self._read(RAW_DIR + "/" + name)
            _require(measured == _sha(expected), "Archive partition digest mismatch")
        for checksum_name, inventory in (("SHA256SUMS", original),
                                          ("ADDITIONAL_SHA256SUMS", additional)):
            raw, _ = self._read(RAW_DIR + "/" + checksum_name)
            parsed = {}
            for line in raw.decode("utf-8").splitlines():
                pair = line.split("  ", 1)
                _require(len(pair) == 2 and pair[1] not in parsed, "Malformed checksum inventory")
                parsed[pair[1]] = _sha(pair[0])
            _require(parsed == {k: v for k, v in inventory.items() if k != checksum_name},
                     "Checksum inventory disagreement")
        raw, _ = self._read(RAW_DIR + "/manifest_completion.json")
        completion = _json(raw)
        _require(completion["record_type"] == "post_run_metadata_completion" and
                 completion["experiment_rerun"] is False and completion["existing_bytes_modified"] is False,
                 "Metadata timing/declaration mismatch")
        _require(completion["original_artifact_hashes"] == original, "Metadata original inventory mismatch")
        _require(completion["new_metadata_hashes"] == {
            key: value for key, value in additional.items()
            if key not in ("ADDITIONAL_SHA256SUMS", "manifest_completion.json")},
            "Metadata additional inventory mismatch")
        return {"original_files": len(original), "post_run_metadata_files": len(additional),
                "post_run_metadata_remains_post_run": True}

    def _run_observer_audit(self, args):
        _keys(args, ())
        _require(not self._audited, "The fixed archive audit has already run")
        self._audited = True
        raw, measured = self._read(CLOSURE, "text")
        _require(measured == CLOSURE_SHA256, "Execution-closure pin mismatch")
        closure = _json(raw)
        _require(self._files.get(AUDITOR, {}).get("sha256") == AUDITOR_SHA256,
                 "Only the unchanged historical auditor may execute")
        inventory_status = self._expanded_inventory(closure)
        entries = closure["view_input_files"]
        _require(type(entries) is list and len(entries) == closure["view_input_file_count"],
                 "View input count mismatch")
        names = [_path(entry["path"]) for entry in entries]
        _require(len(set(names)) == len(names) and AUDITOR in names, "Invalid view dependencies")
        expected_raw = {RAW_DIR + "/" + name for name in closure["original_raw_inventory"]}
        _require({name for name in names if name.startswith(RAW_DIR + "/")} == expected_raw,
                 "Original view must exclude later metadata")
        view = Path(tempfile.mkdtemp(prefix="observer-audit-", dir=self.output_root))
        os.chmod(view, 0o700)
        for entry in entries:
            raw, measured = self._read(entry["path"])
            _require(measured == entry["sha256"], "Frozen auditor dependency mismatch")
            destination = view / entry["path"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open("xb") as stream:
                stream.write(raw)
            destination.chmod(0o400)
        receipt = view / "evidence/REEXECUTION_RECEIPT.json"
        _require(not receipt.exists(), "Auditor receipt must be new")
        executable = str(Path(sys.executable).resolve(strict=True))
        command = [executable, "-I", "-B", str(view / AUDITOR), "--run-dir", str(view / RAW_DIR),
                   "--receipt", str(receipt)]
        result = subprocess.run(command, stdin=subprocess.DEVNULL, capture_output=True,
                                timeout=30, cwd=view, env={}, check=False)
        _require(len(result.stdout) + len(result.stderr) <= 1024 * 1024, "Auditor output exceeds bound")
        # Retain actual output before any scientific consistency check can fail.
        for name, content in (("AUDITOR_STDOUT.bin", result.stdout), ("AUDITOR_STDERR.bin", result.stderr)):
            with (view / name).open("xb") as stream:
                stream.write(content)
        _require(result.returncode == 0, "Pinned historical auditor failed")
        _require(receipt.is_file() and not receipt.is_symlink(), "Missing/invalid auditor receipt")
        receipt_bytes = receipt.read_bytes()
        actual = _json(receipt_bytes)
        historical, _ = self._read(HISTORICAL_RECEIPT, "text")
        expected = _json(historical)
        _require({k: v for k, v in actual.items() if k != "timestamp_utc"} ==
                 {k: v for k, v in expected.items() if k != "timestamp_utc"},
                 "Actual auditor receipt differs from historical receipt beyond timestamp")
        for entry in entries:
            path = view / entry["path"]
            _require(not path.is_symlink() and path.is_file() and
                     hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"],
                     "Auditor view input changed")
        _require(self._expanded_inventory(closure) == inventory_status, "Source inventory changed")
        self._audit_succeeded = True
        return {"receipt": actual, "receipt_sha256": hashlib.sha256(receipt_bytes).hexdigest(),
                "receipt_output_id": str(receipt.relative_to(self.output_root)),
                "compared_to_historical_receipt": "all fields except timestamp_utc equal",
                "source_archive": inventory_status, "new_experiment": False,
                "formal_verdict": None}

    def _submit_verdict(self, args):
        _keys(args, ("verdict", "applies_to", "summary", "dispositions", "strongest_objections",
                     "missing_dependencies", "required_corrections"))
        _require(type(args["verdict"]) is str and args["verdict"] in VERDICTS, "Invalid verdict vocabulary")
        _keys(args["applies_to"], ("scope", *REVIEW_MANIFESTS))
        _text(args["applies_to"]["scope"])
        for field, path in REVIEW_MANIFESTS.items():
            _, measured = self._read(path, "text")
            _require(measured == _sha(args["applies_to"][field]), "Review scope manifest mismatch")
        _require(args["verdict"] == "SUSPEND_FOR_DEPENDENCY" or self._audit_succeeded,
                 "A substantive verdict requires the actual fixed auditor receipt")
        _text(args["summary"])
        _require(type(args["dispositions"]) is list and len(args["dispositions"]) == len(SUBJECTS),
                 "Separate C1-C4, T and observer dispositions are required")
        subjects = []
        measured_evidence = {}
        for item in args["dispositions"]:
            _keys(item, ("subject", "disposition", "reason", "evidence"))
            _require(type(item["subject"]) is str and item["subject"] in SUBJECTS, "Unknown subject")
            subjects.append(item["subject"])
            _text(item["disposition"])
            _text(item["reason"])
            _require(type(item["evidence"]) is list and 0 < len(item["evidence"]) <= 200,
                     "Bounded artifact evidence references required")
            for reference in item["evidence"]:
                _keys(reference, ("path", "sha256"))
                _, measured = self._read(reference["path"])
                _require(measured == _sha(reference["sha256"]), "Verdict evidence digest mismatch")
                measured_evidence[reference["path"]] = measured
        _require(set(subjects) == set(SUBJECTS), "Duplicate/missing subject dispositions")
        for field in ("strongest_objections", "missing_dependencies", "required_corrections"):
            values = args[field]
            _require(type(values) is list and len(values) <= 100, "Invalid bounded text list")
            for value in values:
                _text(value)
        # The substantive statement is the reviewer's supplied object, unchanged.
        body = {"schema_version": 1, "received_utc": datetime.now(timezone.utc).isoformat(),
                "packet_manifest_sha256": self.manifest_sha256,
                "actual_evidence_sha256": measured_evidence, "reviewer_verdict": args,
                "broker_role": "transport and integrity only; no scientific verdict generated"}
        encoded = (json.dumps(body, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")
        _require(len(encoded) <= 1024 * 1024, "Verdict exceeds output bound")
        self.verify_inputs()
        fd = os.open(VERDICT_NAME, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                     0o400, dir_fd=self._output_fd)
        try:
            with os.fdopen(fd, "wb", closefd=False) as stream:
                stream.write(encoded)
                stream.flush()
                os.fsync(fd)
        finally:
            os.close(fd)
        os.fsync(self._output_fd)
        # Measure stored bytes, rather than labelling the intended buffer hash
        # as a successful output measurement. Failure preserves the new file.
        read_fd = os.open(VERDICT_NAME, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC,
                          dir_fd=self._output_fd)
        try:
            before = os.fstat(read_fd)
            _require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
                     before.st_size == len(encoded), "Verdict output identity/size mismatch")
            chunks = []
            remaining = len(encoded) + 1
            while remaining:
                chunk = os.read(read_fd, min(65536, remaining))
                if not chunk:
                    break
                chunks.append(chunk)
                remaining -= len(chunk)
            stored = b"".join(chunks)
            _require(_identity(before) == _identity(os.fstat(read_fd)) and stored == encoded,
                     "Verdict stored-byte verification failed")
        finally:
            os.close(read_fd)
        self._verdict_written = True
        return {"accepted": True, "output_id": VERDICT_NAME,
                "sha256": hashlib.sha256(stored).hexdigest(), "bytes": len(stored)}


def _object(properties):
    return {"type": "object", "properties": properties, "required": list(properties),
            "additionalProperties": False}


_STRING = {"type": "string", "minLength": 1, "maxLength": 30000}
_PATH = {"type": "string", "minLength": 1, "maxLength": 1024}
_EVIDENCE = _object({"path": _PATH, "sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"}})
_TEXT_LIST = {"type": "array", "items": _STRING, "maxItems": 100}
TOOL_SCHEMAS = {
    "read_text": _object({"path": _PATH, "offset": {"type": "integer", "minimum": 0,
                                                      "maximum": MAX_FILE_BYTES},
                          "length": {"type": "integer", "minimum": 1, "maximum": 100000}}),
    "read_page_image": _object({"path": _PATH}),
    "hash_file": _object({"path": _PATH}),
    "run_observer_audit": _object({}),
    "submit_verdict": _object({
        "verdict": {"type": "string", "enum": list(VERDICTS)},
        "applies_to": _object({"scope": _STRING, **{
            field: {"type": "string", "pattern": "^[0-9a-f]{64}$"} for field in REVIEW_MANIFESTS}}),
        "summary": _STRING,
        "dispositions": {"type": "array", "minItems": len(SUBJECTS), "maxItems": len(SUBJECTS),
            "items": _object({"subject": {"type": "string", "enum": list(SUBJECTS)},
                              "disposition": _STRING, "reason": _STRING,
                              "evidence": {"type": "array", "items": _EVIDENCE,
                                           "minItems": 1, "maxItems": 200}})},
        "strongest_objections": _TEXT_LIST, "missing_dependencies": _TEXT_LIST,
        "required_corrections": _TEXT_LIST})}


def dynamic_tool_specs():
    """Fresh specs for ThreadStartParams.dynamicTools; no native environment."""
    descriptions = {
        "read_text": "Read a manifested UTF-8 source by character offset; actual whole-file SHA-256 is returned.",
        "read_page_image": "Read one manifested rendered physical paper page as a PNG image.",
        "hash_file": "Recompute SHA-256 from complete actual bytes of one manifested file.",
        "run_observer_audit": "Execute the sole fixed, unchanged observer auditor and compare its actual receipt.",
        "submit_verdict": "Emit the reviewer's structured verdict once to the parent's predetermined output.",
    }
    return [{"type": "function", "name": name, "description": descriptions[name],
             "inputSchema": copy.deepcopy(schema)}
            for name, schema in TOOL_SCHEMAS.items()]
