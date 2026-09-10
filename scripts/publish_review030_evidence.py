#!/usr/bin/env python3
"""Collect the fixed, noncredential 030 evidence files; never run Git or a model.

The human publication wrapper calls collect(project_root) and stages only the
returned tracked_paths. Missing, refused and partial evidence are observations,
not reconstructed execution receipts. The archive is keyed by its exact index.
"""
from __future__ import annotations

import argparse
import errno
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import sys


VERSION = "P3_REVIEW_030_EVIDENCE_COLLECTION_031_v1"
MAIN = "delivery/P3_FINITE_REVIEW_030/"
KERNEL = "delivery/P3_FINITE_REVIEW_030_KERNEL_PREFLIGHT/"
WORKFLOW = "delivery/P3_030_RETURN_WORKFLOW/"
MIB = 1024 * 1024
SOURCE_LIMITS = {
    MAIN + "REPORT.json": 16 * MIB,
    MAIN + "REPORT.sha256": 65,
    MAIN + "ATTEMPT.json": 2 * MIB,
    MAIN + "AUTHORIZATION.md": 2 * MIB,
    MAIN + "synthetic_SESSION.json": 16 * MIB,
    MAIN + "synthetic_STAGE.json": 16 * MIB,
    MAIN + "science_SESSION.json": 16 * MIB,
    MAIN + "science_STAGE.json": 16 * MIB,
    MAIN + "science_output/REVIEW_VERDICT.json": MIB,
    KERNEL + "ATTEMPT.json": 2 * MIB,
    KERNEL + "REPORT.json": 4 * MIB,
    KERNEL + "REPORT.sha256": 65,
    WORKFLOW + "WORKFLOW_REPORT.json": MIB,
    WORKFLOW + "LAUNCH_RESERVED.json": MIB,
    WORKFLOW + "LAUNCH_OUTCOME.json": MIB,
}
ARCHIVE_PARENT = "artifacts/P3_REVIEW_030_RETURN"
MAX_AGGREGATE_BYTES = sum(SOURCE_LIMITS.values())
READ_CHUNK = 64 * 1024
DIR_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
FILE_FLAGS = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK


class CollectionError(RuntimeError):
    """Categorical error; exception messages never include captured file bytes."""


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True,
                       allow_nan=False) + "\n").encode("ascii")


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def _parts(relative):
    if type(relative) is not str or not relative or relative.startswith("/"):
        raise CollectionError("invalid_relative_path")
    parts = PurePosixPath(relative).parts
    if any(part in ("", ".", "..") for part in relative.split("/")):
        raise CollectionError("invalid_relative_path")
    return parts


def _signature(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid,
            info.st_nlink, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def _identity(info):
    return info.st_dev, info.st_ino


def _safe_regular(info, limit):
    if not stat.S_ISREG(info.st_mode):
        raise CollectionError("not_regular_file")
    if info.st_nlink != 1:
        raise CollectionError("multiple_hardlinks_refused")
    if info.st_uid != os.getuid():
        raise CollectionError("unexpected_file_owner")
    if info.st_mode & 0o022:
        raise CollectionError("group_or_world_writable_file")
    if info.st_size > limit:
        raise CollectionError("file_byte_limit_exceeded")


def _open_absolute_directory(path):
    value = os.fspath(path)
    if not os.path.isabs(value) or ".." in value.split("/"):
        raise CollectionError("project_root_must_be_absolute_without_parent_steps")
    descriptor = os.open("/", DIR_FLAGS)
    try:
        for part in Path(value).parts[1:]:
            following = os.open(part, DIR_FLAGS, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = following
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def _directory(root_fd, parts, *, create=False):
    descriptor = os.dup(root_fd)
    try:
        for part in parts:
            if create:
                try:
                    os.mkdir(part, 0o755, dir_fd=descriptor)
                except FileExistsError:
                    pass
            following = os.open(part, DIR_FLAGS, dir_fd=descriptor)
            if create:
                info = os.fstat(following)
                if info.st_uid != os.getuid() or info.st_mode & 0o022:
                    os.close(following)
                    raise CollectionError("unsafe_archive_directory")
            os.close(descriptor)
            descriptor = following
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def _error_code(error):
    if isinstance(error, CollectionError):
        return str(error)
    if isinstance(error, FileNotFoundError):
        return "path_missing"
    if isinstance(error, OSError):
        return {
            errno.ELOOP: "symlink_refused",
            errno.ENOTDIR: "non_directory_or_symlink_ancestor_refused",
            errno.EACCES: "permission_refused",
            errno.EPERM: "permission_refused",
        }.get(error.errno, "filesystem_error")
    return "collection_error"


def _read_fixed(root_fd, relative, limit):
    parts = _parts(relative)
    parent = _directory(root_fd, parts[:-1])
    descriptor = None
    try:
        # Metadata inspection prevents opening a FIFO/device or multi-link alias.
        before = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
        if stat.S_ISLNK(before.st_mode):
            raise CollectionError("symlink_refused")
        _safe_regular(before, limit)
        descriptor = os.open(parts[-1], FILE_FLAGS, dir_fd=parent)
        opened = os.fstat(descriptor)
        _safe_regular(opened, limit)
        if _signature(before) != _signature(opened):
            raise CollectionError("source_changed_during_collection")
        chunks = []
        total = 0
        while True:
            part = os.read(descriptor, min(READ_CHUNK, limit - total + 1))
            if not part:
                break
            total += len(part)
            if total > limit:
                raise CollectionError("file_byte_limit_exceeded")
            chunks.append(part)
        after = os.fstat(descriptor)
        named = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
        if _signature(after) != _signature(opened) or _signature(named) != _signature(opened):
            raise CollectionError("source_changed_during_collection")
        raw = b"".join(chunks)
        if len(raw) != opened.st_size:
            raise CollectionError("source_changed_during_collection")
        return raw, _signature(opened), stat.S_IMODE(opened.st_mode)
    finally:
        if descriptor is not None:
            os.close(descriptor)
        os.close(parent)


def _stat_fixed(root_fd, relative):
    parts = _parts(relative)
    parent = _directory(root_fd, parts[:-1])
    try:
        return os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
    finally:
        os.close(parent)


def _check_root(project_root, root_fd):
    current = _open_absolute_directory(project_root)
    try:
        if _identity(os.fstat(current)) != _identity(os.fstat(root_fd)):
            raise CollectionError("project_root_changed_during_collection")
    finally:
        os.close(current)


def _ensure_exact(root_fd, relative, raw):
    parts = _parts(relative)
    parent = _directory(root_fd, parts[:-1], create=True)
    descriptor = None
    try:
        try:
            descriptor = os.open(parts[-1], os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                                 os.O_NOFOLLOW | os.O_CLOEXEC, 0o644, dir_fd=parent)
        except FileExistsError:
            existing, _, _ = _read_fixed(root_fd, relative, len(raw))
            if existing != raw:
                raise CollectionError("existing_archive_file_differs_preserved")
            return
        view = memoryview(raw)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise CollectionError("archive_write_incomplete")
            view = view[written:]
        os.fsync(descriptor)
        os.fsync(parent)
    finally:
        if descriptor is not None:
            os.close(descriptor)
        os.close(parent)
    verified, _, _ = _read_fixed(root_fd, relative, len(raw))
    if verified != raw:
        raise CollectionError("archive_write_verification_failed")


def _summary(entries):
    states = {entry["source_path"]: entry["status"] for entry in entries}
    report = states[MAIN + "REPORT.json"]
    kernel = states[KERNEL + "REPORT.json"]
    verdict = states[MAIN + "science_output/REVIEW_VERDICT.json"]
    count = sum(value == "PRESENT" for value in states.values())
    original_count = sum(states[path] == "PRESENT" for path in states
                         if not path.startswith(WORKFLOW))
    if any(value == "REFUSED" for value in states.values()):
        collection = "HAS_REFUSED_SOURCES"
    elif count == 0:
        collection = "NO_ALLOWED_SOURCE_FILES_PRESENT"
    elif original_count == 0:
        collection = "WORKFLOW_EVIDENCE_ONLY_NO_030_RECEIPTS"
    elif report != "PRESENT":
        collection = "PARTIAL_EVIDENCE_WITHOUT_MAIN_REPORT"
    else:
        collection = "MAIN_REPORT_PRESENT_FOR_REVIEW"
    return {"collection_status": collection, "main_report": report,
            "kernel_report": kernel, "verdict": verdict,
            "present_file_count": count,
            "original030_file_count": original_count,
            "workflow_report": states[WORKFLOW + "WORKFLOW_REPORT.json"],
            "workflow_launch_reservation": states[WORKFLOW + "LAUNCH_RESERVED.json"],
            "workflow_launch_outcome": states[WORKFLOW + "LAUNCH_OUTCOME.json"],
            "verdict_execution_admission": "NOT_EVALUATED_BY_COLLECTOR",
            "missing_files_do_not_establish_no_execution": True}


def collect(project_root):
    """Return explicit publication paths, with no Git/native/model operations.

    This observes a fixed list of files. It does not prove they form a complete
    or scientifically admitted run. A run in progress can yield a partial
    collection; repeat collection later makes a new archive if bytes change.
    """
    project_root = Path(project_root)
    root_fd = _open_absolute_directory(project_root)
    payloads = {}
    signatures = {}
    entries = []
    try:
        for relative, limit in SOURCE_LIMITS.items():
            entry = {"source_path": relative, "byte_limit": limit}
            try:
                raw, signature, mode = _read_fixed(root_fd, relative, limit)
                payloads[relative] = raw
                signatures[relative] = signature
                entry.update(status="PRESENT", bytes=len(raw), sha256=sha256(raw),
                             source_mode=format(mode, "04o"), archive_path="files/" + relative)
            except (OSError, CollectionError) as error:
                entry.update(status="MISSING" if isinstance(error, FileNotFoundError) else "REFUSED",
                             reason_code=_error_code(error))
            entries.append(entry)
        # Fresh no-follow walks detect replacement of any source ancestor after
        # its read. Changed bytes are discarded, never turned into a run receipt.
        for entry in entries:
            relative = entry["source_path"]
            if relative not in signatures:
                continue
            try:
                current = _stat_fixed(root_fd, relative)
                if _signature(current) != signatures[relative]:
                    raise CollectionError("source_changed_during_collection")
            except (OSError, CollectionError):
                payloads.pop(relative)
                entry.clear()
                entry.update(source_path=relative, byte_limit=SOURCE_LIMITS[relative],
                             status="REFUSED", reason_code="source_changed_during_collection")
        _check_root(project_root, root_fd)
        if sum(map(len, payloads.values())) > MAX_AGGREGATE_BYTES:
            raise CollectionError("aggregate_byte_limit_exceeded")
        summary = _summary(entries)
        index = {"kind": VERSION, "sources": entries, "summary": summary,
                 "fixed_allowlist_only": True, "source_files_modified": False,
                 "source_receipts_reconstructed": False, "recursive_discovery": False,
                 "credentials_or_cache_paths_read": False, "git_commands_executed": False,
                 "native_or_model_operations_executed": False,
                 "collection_is_not_execution_or_scientific_admission": True,
                 "consistency": "each present source stable through final metadata check; not an atomic run snapshot",
                 "timestamp_omitted_for_idempotence": True}
        index_raw = canonical(index)
        digest = sha256(index_raw)
        archive = ARCHIVE_PARENT + "/" + digest
        archive_files = {"INDEX.json": index_raw}
        archive_files.update({"files/" + path: raw for path, raw in payloads.items()})
        manifest = {"kind": VERSION + "_MANIFEST", "evidence_digest": digest,
                    "digest_basis": "exact INDEX.json bytes", "index_sha256": digest,
                    "files": [{"path": path, "sha256": sha256(raw), "bytes": len(raw)}
                              for path, raw in sorted(archive_files.items())],
                    "manifest_excluded_from_its_own_inventory": True}
        archive_files["MANIFEST.json"] = canonical(manifest)
        for relative, raw in sorted(archive_files.items()):
            _ensure_exact(root_fd, archive + "/" + relative, raw)
        _check_root(project_root, root_fd)
        return {"kind": VERSION + "_RESULT", "archive_relative_path": archive,
                "evidence_digest": digest, "tracked_paths": sorted(archive + "/" + path
                    for path in archive_files), "status_summary": summary,
                "manifest_sha256": sha256(archive_files["MANIFEST.json"]),
                "git_commands_executed": False, "native_or_model_operations_executed": False}
    finally:
        os.close(root_fd)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path.home() / "ARC_Independent_Lab")
    args = parser.parse_args()
    try:
        print(canonical(collect(args.project)).decode("ascii"), end="")
    except (CollectionError, OSError) as error:
        print("STOP: " + _error_code(error) + "; existing evidence preserved.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
