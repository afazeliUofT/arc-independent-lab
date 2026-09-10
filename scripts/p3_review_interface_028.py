#!/usr/bin/env python3
"""Proposed bounded input-feedback shim; never a scientific reviewer.

The historical broker, file authority, audit and verdict grammar are unchanged.
Only ordinary argument mistakes receive fixed actionable feedback before the
terminal broker dispatch. Unknown resources, path denials and integrity failures
remain fatal. The parent authenticates requests and counts ALL calls, including
recoverable errors. This module grants no launch, network or authentication.
"""
from __future__ import annotations

import copy
import errno
import importlib.util
import json
from pathlib import Path
import sys
import threading


def _load_original():
    name = "p3_review_broker"
    path = Path(__file__).resolve().with_name(name + ".py")
    existing = sys.modules.get(name)
    if existing is not None:
        if Path(existing.__file__).resolve() != path:
            raise RuntimeError("Conflicting original broker origin")
        return existing
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


original = _load_original()
BrokerError = original.BrokerError
_path = original._path
REVIEW_MANIFESTS = original.REVIEW_MANIFESTS
SUBJECTS = original.SUBJECTS
VERDICT_NAME = original.VERDICT_NAME
MAX_RECOVERABLE_ERRORS = 8

# Enum keys and instructions contain only authored constants, never model text,
# file names, supplied hashes, OS exception messages or native diagnostics.
INPUT_INSTRUCTIONS = {
    "argument_fields": "Use exactly the documented argument keys, including all required keys; omit every extra key.",
    "integer_bounds": "read_text offset must be an integer from 0 to 134217728 and length an integer from 1 to 100000. Booleans and floats are invalid. Offsets count Unicode characters.",
    "resource_path_type": "Supply path as a canonical relative string of 1 to 1024 characters copied from the packet index; never use traversal or an unlisted resource.",
    "resource_kind": "Use read_text for a manifested text resource, read_page_image for a manifested PNG page, and hash_file for any manifested resource. Select the matching derivative from the packet index.",
    "text_offset_past_end": "The offset exceeds this text resource's character count. Restart at offset 0 and advance using returned next_offset and total_characters; each length is 1 to 100000.",
    "bounded_text": "Every text field must be a non-whitespace string of 1 to 30000 Unicode characters.",
    "sha256_format": "Every SHA-256 must contain exactly 64 lowercase hexadecimal characters, taken from actual broker measurements; do not guess a digest.",
    "verdict_vocabulary": "verdict must be exactly GO, REVISE_ONCE, KILL or SUSPEND_FOR_DEPENDENCY.",
    "subject_dispositions": "Provide exactly six dispositions, one each for C1, C2, C3, C4, T and observer, with no duplicate or omitted subject. Their order is unrestricted.",
    "evidence_list": "Each disposition needs an evidence list of 1 to 200 objects, each with exactly path and sha256 for manifested evidence actually measured.",
    "text_list": "strongest_objections, missing_dependencies and required_corrections must each be a list of 0 to 100 non-whitespace strings, each at most 30000 characters.",
    "audit_required": "GO, REVISE_ONCE and KILL require the actual fixed auditor receipt. Call run_observer_audit with {} first, then assess its receipt. Do not change a scientific conclusion merely to satisfy this dependency.",
    "audit_already_run": "The fixed audit has already run successfully in this review. Use its prior returned receipt; it will not be executed again.",
    "verdict_size": "The encoded verdict must fit within 1048576 bytes, including the broker envelope and measured evidence table. Shorten your own text while retaining the complete scientific assessment.",
}


class ToolInputError(ValueError):
    """Recoverable argument error, emitted only after whole-input revalidation."""
    def __init__(self, code):
        if code not in INPUT_INSTRUCTIONS:
            raise BrokerError("Unknown interface input-error code")
        self.code = code
        self.instruction = INPUT_INSTRUCTIONS[code]
        super().__init__(code)

    def as_dict(self):
        return {"schema": "arc.tool-input-error.v1", "code": self.code,
                "instruction": self.instruction, "retryable_with_corrected_arguments": True,
                "scientific_content_modified": False}


def _need(condition, code):
    if not condition:
        raise ToolInputError(code)


def _keys(value, fields):
    _need(type(value) is dict and set(value) == set(fields), "argument_fields")


def _text(value):
    _need(type(value) is str and bool(value.strip()) and len(value) <= 30000,
          "bounded_text")


def _sha(value):
    _need(type(value) is str and original.SHA_RE.fullmatch(value) is not None,
          "sha256_format")


class ReviewBroker:
    """Serialize prevalidation and delegate valid calls to the original broker.

    Eight recoverable input errors are allowed per instance, not per tool or
    turn. No valid call resets that count. A ninth error terminates the broker.
    Path checks call the original descriptor-based read code; even an otherwise
    malformed request cannot hide a supplied forbidden resource reference.
    """
    def __init__(self, *args, **kwargs):
        self._original = original.ReviewBroker(*args, **kwargs)
        self._interface_lock = threading.Lock()
        self.recoverable_input_errors = 0

    @property
    def _failed(self):
        return self._original._failed

    @property
    def audit_completed(self):
        """Whether the original single audit invocation has been consumed.

        This reflects the original _audited flag, not proof of audit success;
        a failed audit already makes the broker terminal. A repeated successful
        audit request needs only feedback, so no new execution time is reserved.
        """
        return self._original._audited

    def close(self):
        self._original.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def verify_inputs(self):
        return self._original.verify_inputs()

    def _checked_read(self, path, *, keep_text=False):
        # Cache only within the current serialized prevalidation. Digests come
        # from actual original-broker reads, never a model claim or a previous
        # request. Retain bytes only for the one read_text target, avoiding a
        # verdict-sized collection of private PDF bytes in memory.
        prior = self._request_reads.get(path)
        if prior is not None and (not keep_text or prior[0] is not None):
            return prior
        raw, measured = self._original._read(path)
        value = (raw if keep_text else None, measured)
        self._request_reads[path] = value
        return value

    def _check_paths(self, tool, args):
        # Examine only advertised resource fields. Unknown extra fields are
        # rejected as shape errors and never interpreted as commands or paths.
        paths = []
        if type(args) is dict:
            if tool in ("read_text", "read_page_image", "hash_file") and "path" in args:
                paths.append(args["path"])
            if tool == "submit_verdict" and type(args.get("dispositions")) is list:
                for item in args["dispositions"]:
                    if type(item) is dict and type(item.get("evidence")) is list:
                        for reference in item["evidence"]:
                            if type(reference) is dict and "path" in reference:
                                paths.append(reference["path"])
        for path in paths:
            if type(path) is str:
                # This is the actual original broker read boundary. Canonical
                # path, manifest membership, identity and SHA checks all apply.
                self._checked_read(path, keep_text=tool == "read_text")
        if tool == "submit_verdict" and type(args) is dict:
            claims = args.get("applies_to")
            if type(claims) is dict:
                for field, path in REVIEW_MANIFESTS.items():
                    claim = claims.get(field)
                    if type(claim) is str and original.SHA_RE.fullmatch(claim):
                        _, measured = self._checked_read(path)
                        original._require(measured == claim, "Review scope manifest mismatch")
            if type(args.get("dispositions")) is list:
                for item in args["dispositions"]:
                    if type(item) is dict and type(item.get("evidence")) is list:
                        for reference in item["evidence"]:
                            if type(reference) is dict:
                                path, claim = reference.get("path"), reference.get("sha256")
                                if type(path) is str and type(claim) is str and original.SHA_RE.fullmatch(claim):
                                    _, measured = self._checked_read(path)
                                    original._require(measured == claim, "Verdict evidence digest mismatch")

    def _resource(self, path, kind=None):
        _need(type(path) is str, "resource_path_type")
        raw, measured = self._checked_read(path, keep_text=kind == "text")
        if kind is not None:
            _need(self._original._files[path]["kind"] == kind, "resource_kind")
        return raw, measured

    def _prevalidate(self, tool, args):
        schema = original.TOOL_SCHEMAS[tool]
        _keys(args, schema["required"])
        if tool in ("hash_file", "read_page_image", "read_text"):
            kind = {"read_text": "text", "read_page_image": "image"}.get(tool)
            raw, _ = self._resource(args["path"], kind)
            if tool == "read_text":
                _need(type(args["offset"]) is int and 0 <= args["offset"] <= original.MAX_FILE_BYTES
                      and type(args["length"]) is int and 1 <= args["length"] <= 100000,
                      "integer_bounds")
                # Invalid UTF-8 is packet-integrity/format failure, not a model
                # argument mistake. Let the original broker raise it unchanged.
                try:
                    text = raw.decode("utf-8")
                except UnicodeError:
                    return
                _need(args["offset"] <= len(text), "text_offset_past_end")
            # A manifested non-PNG/oversized image is a packet failure and is
            # left to the unchanged broker's terminal image validation.
            return
        if tool == "run_observer_audit":
            _need(not self._original._audited, "audit_already_run")
            return
        _need(type(args["verdict"]) is str and args["verdict"] in original.VERDICTS,
              "verdict_vocabulary")
        _keys(args["applies_to"], ("scope", *original.REVIEW_MANIFESTS))
        _text(args["applies_to"]["scope"])
        for field in original.REVIEW_MANIFESTS:
            _sha(args["applies_to"][field])
        _text(args["summary"])
        dispositions = args["dispositions"]
        _need(type(dispositions) is list and len(dispositions) == 6, "subject_dispositions")
        subjects, measured_evidence = [], {}
        for item in dispositions:
            _keys(item, ("subject", "disposition", "reason", "evidence"))
            _need(type(item["subject"]) is str and item["subject"] in original.SUBJECTS,
                  "subject_dispositions")
            subjects.append(item["subject"])
            _text(item["disposition"])
            _text(item["reason"])
            _need(type(item["evidence"]) is list and 1 <= len(item["evidence"]) <= 200,
                  "evidence_list")
            for reference in item["evidence"]:
                _keys(reference, ("path", "sha256"))
                _sha(reference["sha256"])
                _, measured = self._resource(reference["path"])
                # A syntactically valid false SHA claim remains a terminal
                # original broker integrity failure, never corrected feedback.
                if measured != reference["sha256"]:
                    raise BrokerError("Verdict evidence digest mismatch")
                measured_evidence[reference["path"]] = measured
        _need(set(subjects) == set(original.SUBJECTS), "subject_dispositions")
        for field in ("strongest_objections", "missing_dependencies", "required_corrections"):
            values = args[field]
            _need(type(values) is list and len(values) <= 100, "text_list")
            for value in values:
                _text(value)
        for field, path in original.REVIEW_MANIFESTS.items():
            _, measured = self._checked_read(path)
            original._require(measured == args["applies_to"][field], "Review scope manifest mismatch")
        _need(args["verdict"] == "SUSPEND_FOR_DEPENDENCY" or self._original._audit_succeeded,
              "audit_required")
        # Exact envelope structure and a maximum-length UTC timestamp provide a
        # conservative byte check before any output is created. No text changes.
        body = {"schema_version": 1, "received_utc": "2000-01-01T00:00:00.000000+00:00",
                "packet_manifest_sha256": self._original.manifest_sha256,
                "actual_evidence_sha256": measured_evidence, "reviewer_verdict": args,
                "broker_role": "transport and integrity only; no scientific verdict generated"}
        try:
            encoded = (json.dumps(body, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")
        except UnicodeError:
            raise ToolInputError("bounded_text")
        _need(len(encoded) <= 1024 * 1024, "verdict_size")

    def dispatch(self, tool, arguments):
        with self._interface_lock:
            self._request_reads = {}
            try:
                original._require(not self._failed and not self._original._verdict_written,
                                  "Broker already stopped/completed")
                original._require(type(tool) is str and tool in original.TOOL_SCHEMAS,
                                  "Unknown operation")
                self._check_paths(tool, arguments)
                try:
                    self._prevalidate(tool, arguments)
                except ToolInputError:
                    # Never turn a packet mutation into correctable feedback.
                    self.verify_inputs()
                    self.recoverable_input_errors += 1
                    original._require(self.recoverable_input_errors <= MAX_RECOVERABLE_ERRORS,
                                      "Recoverable input-error ceiling reached")
                    raise
                # The unchanged broker performs whole-input verification before
                # and after every valid call. Do not add a third corpus pass.
                return self._original.dispatch(tool, arguments)
            except ToolInputError:
                raise
            except BaseException:
                self._original._failed = True
                raise
            finally:
                self._request_reads.clear()


_FAILURE_GROUPS = {
    "boundary.resource_path": ("Invalid resource path", "Noncanonical resource path", "Absolute resource path denied", "Unmanifested resource denied"),
    "boundary.unknown_operation": ("Unknown operation",),
    "boundary.stopped": ("Broker stopped", "Broker already stopped/completed"),
    "boundary.input_error_ceiling": ("Recoverable input-error ceiling reached",),
    "integrity.resource": ("Resource opening denied", "Resource must be a regular file without hardlink aliases", "Resource exceeds byte bound", "Resource changed during read", "Input identity changed", "Resource digest mismatch", "Packet manifest changed", "Packet manifest digest mismatch"),
    "integrity.claimed_sha256": ("Review scope manifest mismatch", "Verdict evidence digest mismatch"),
    "integrity.packet_format": ("Resource is not UTF-8 text", "Expected bounded manifested PNG page", "Wrong resource kind"),
    "integrity.audit": ("Archive partitions overlap", "Expanded archive membership mismatch", "Archive name must be one component", "Archive partition digest mismatch", "Malformed checksum inventory", "Checksum inventory disagreement", "Metadata timing/declaration mismatch", "Metadata original inventory mismatch", "Metadata additional inventory mismatch", "Execution-closure pin mismatch", "Only the unchanged historical auditor may execute", "View input count mismatch", "Invalid view dependencies", "Original view must exclude later metadata", "Frozen auditor dependency mismatch", "Auditor receipt must be new", "Auditor output exceeds bound", "Pinned historical auditor failed", "Missing/invalid auditor receipt", "Actual auditor receipt differs from historical receipt beyond timestamp", "Auditor view input changed", "Source inventory changed"),
    "integrity.output": ("Verdict output identity/size mismatch", "Verdict stored-byte verification failed"),
    "input.original_broker_rejection": ("Unexpected argument fields", "Invalid SHA-256", "Expected bounded nonempty text", "Invalid integer bound", "Text offset past end", "The fixed archive audit has already run", "Invalid verdict vocabulary", "A substantive verdict requires the actual fixed auditor receipt", "Separate C1-C4, T and observer dispositions are required", "Unknown subject", "Bounded artifact evidence references required", "Duplicate/missing subject dispositions", "Invalid bounded text list", "Verdict exceeds output bound"),
}
_FAILURE_MESSAGES = {message: code for code, messages in _FAILURE_GROUPS.items() for message in messages}


def classify_broker_failure(error):
    """Return only a finite diagnostic enum; never expose exception text."""
    if isinstance(error, ToolInputError):
        return "input." + error.code
    if isinstance(error, BrokerError):
        return _FAILURE_MESSAGES.get(str(error), "broker.unclassified_failure")
    if isinstance(error, OSError):
        return {errno.EEXIST: "os.output_already_exists", errno.EACCES: "os.permission_denied",
                errno.EPERM: "os.permission_denied", errno.ELOOP: "os.symlink_denied",
                errno.ENOENT: "os.required_file_missing", errno.ENOSPC: "os.storage_full",
                errno.EDQUOT: "os.storage_quota"}.get(error.errno, "os.other_failure")
    return "broker.unclassified_failure"


def _describe_schema(schema):
    """Carry constraints into fields retained by the pinned JsonSchema enum."""
    kind = schema.get("type")
    parts = []
    if kind == "object":
        parts.append("Exactly these keys are required; no extra keys: " + ", ".join(schema["required"]) + "." if schema["required"] else "Empty object {}; no keys are allowed.")
        for child in schema["properties"].values():
            _describe_schema(child)
    elif kind == "integer":
        parts.append("Strict integer (not a boolean or float), inclusive range %s to %s." % (schema["minimum"], schema["maximum"]))
    elif kind == "array":
        parts.append("List length must be %s to %s inclusive." % (schema.get("minItems", 0), schema["maxItems"]))
        _describe_schema(schema["items"])
    elif kind == "string":
        if "enum" in schema:
            parts.append("Exact allowed values: " + ", ".join(schema["enum"]) + ".")
        if "pattern" in schema:
            parts.append("Exactly 64 lowercase hexadecimal characters [0-9a-f]; use an actual measured SHA-256.")
        if "maxLength" in schema:
            parts.append("Length %s to %s Unicode characters inclusive." % (schema["minLength"], schema["maxLength"]))
            if schema["maxLength"] == 30000:
                parts.append("Must contain a non-whitespace character.")
            else:
                parts.append("Copy a manifested relative path from the packet index; no absolute path, backslash, control character, empty component, dot or dot-dot component. Unknown resources are fatal.")
    schema["description"] = " ".join(parts)


def dynamic_tool_specs():
    specs = copy.deepcopy(original.dynamic_tool_specs())
    details = {
        "read_text": "Arguments exactly path, offset, length. Choose path from the task's supplied bootstrap paths or packet index; an example starting offset is 0 and length is 10000. length must be 1..100000; offset 0..134217728 and no greater than total_characters. Offsets count Unicode characters, not bytes. Continue with returned next_offset; the requested length may extend beyond EOF.",
        "read_page_image": "Arguments exactly path. Requires a manifested image-kind PNG of at most 16777216 bytes, selected from the packet index. It cannot read a PDF directly. Wrong known resource kind can be corrected; malformed packet image is fatal.",
        "hash_file": "Arguments exactly path. Any manifested resource kind is allowed; returns actual whole-file digest and bytes. No caller-provided SHA field or arbitrary path is accepted.",
        "run_observer_audit": "Arguments exactly {}. This is the sole fixed SHA-pinned historical auditor; no command, destination or options are accepted. Execute once, then reuse its receipt. GO, REVISE_ONCE and KILL require its actual successful receipt.",
        "submit_verdict": "Submit your own conclusion unchanged. Exactly six dispositions are required: C1, C2, C3, C4, T, observer, once each in any order. Each needs 1..200 manifested evidence references with actual 64-lowercase-hex SHA-256. Each free-text field is non-whitespace and at most 30000 characters; the three top-level text lists each allow 0..100 entries. Total stored envelope at most 1048576 UTF-8 bytes. The complete UTF-8 serialized tool request INCLUDING its RPC envelope has a separate 524288-byte ceiling; use compact submissions well below it. Use exactly the documented nested keys. Substantive verdicts require a successful fixed audit; SUSPEND_FOR_DEPENDENCY may precede it. Wrong actual digest is fatal. Output is exclusive and cannot be replaced; no caller destination is accepted.",
    }
    for spec in specs:
        _describe_schema(spec["inputSchema"])
        spec["description"] += " " + details[spec["name"]] + " Ordinary argument mistakes may receive fixed feedback, with eight total corrections allowed; authority, integrity and protocol failures remain terminal."
        if spec["name"] == "read_text":
            spec["inputSchema"]["properties"]["offset"]["description"] += " Counts Unicode characters; must not exceed the returned total_characters."
        if spec["name"] == "submit_verdict":
            spec["inputSchema"]["properties"]["dispositions"]["description"] += " Subjects must be unique and cover C1, C2, C3, C4, T, observer; any order."
    return specs
