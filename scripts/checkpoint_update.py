"""Human-run, self-contained checkpoint 002 transfer template (Python stdlib).

Default execution inspects the embedded package only. --apply-and-push inspects
the exact laptop lab, installs only known transitions, records the printed human
answer, commits once and pushes without rewriting history. Existing checkpoint
001 transfer code is not used or changed. No dependencies or credentials are
created. The builder replaces only the PAYLOAD placeholder in a delivery copy.
"""

import argparse
import base64
import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import tempfile
import zlib

PAYLOAD = "__ARC_PAYLOAD__"
REMOTE = "https://github.com/afazeliUofT/arc-independent-lab.git"
CHECKPOINT_ID = "P1_CHECKPOINT_002"
MANIFEST = "state/CHECKPOINT_002.json"
ESCALATION = "state/ESCALATION.md"
ERROR_LOG = "state/handoff_002_errors.jsonl"
BACKUP_ROOT = "delivery/checkpoint002_backups"
COMMIT_MESSAGE = "P1.1: diagnostic trace and supplied-method corrections"
ANSWER = (
    "\n## ANSWER\n"
    "Human response supplied by running P1_CHECKPOINT_002.py --apply-and-push: "
    "Continue Phase 1 after the principal investigator independently verifies "
    "checkpoint 002 on GitHub. This answer does not approve DIAGNOSIS.md or "
    "authorize Phase 2.\n"
)
MAX_PACKAGE_BYTES = 128 * 1024 * 1024


def digest(body):
    return hashlib.sha256(body).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key: " + key)
        result[key] = value
    return result


def parse_json(body):
    return json.loads(body, object_pairs_hook=unique_object)


def safe_name(name):
    if not isinstance(name, str) or not name or any(ord(c) < 32 for c in name):
        raise ValueError("Payload path is empty or contains a control character")
    path = PurePosixPath(name)
    if (path.is_absolute() or path.as_posix() != name or "\\" in name
            or ":" in name or any(p.lower() in (".", "..", ".git") for p in path.parts)):
        raise ValueError("Unsafe payload path: " + name)
    if name == ERROR_LOG or name == "delivery" or name.startswith("delivery/"):
        raise ValueError("Payload occupies a reserved handoff path: " + name)
    return name


def unpack(payload):
    compressed = base64.b64decode(payload, validate=True)
    decoder = zlib.decompressobj()
    raw = decoder.decompress(compressed, MAX_PACKAGE_BYTES + 1)
    if (len(raw) > MAX_PACKAGE_BYTES or decoder.unconsumed_tail
            or not decoder.eof or decoder.unused_data):
        raise ValueError("Compressed package is oversized, truncated or has trailing data")
    package = parse_json(raw)
    if not isinstance(package, dict) or set(package) != {"base_commit", "files"}:
        raise ValueError("Package schema must contain exactly base_commit and files")
    if not re.fullmatch(r"[0-9a-f]{40}", package["base_commit"]):
        raise ValueError("base_commit must be a full lowercase Git SHA-1")
    if not isinstance(package["files"], dict) or not package["files"]:
        raise ValueError("Package has no file map")
    decoded = {}
    for name, entry in package["files"].items():
        safe_name(name)
        if not isinstance(entry, dict) or set(entry) != {"old_sha256", "sha256", "base64"}:
            raise ValueError("Invalid file entry: " + name)
        for key in ("old_sha256", "sha256"):
            value = entry[key]
            if key == "old_sha256" and value is None:
                continue
            if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
                raise ValueError("Invalid " + key + ": " + name)
        body = base64.b64decode(entry["base64"], validate=True)
        if digest(body) != entry["sha256"]:
            raise ValueError("Embedded content hash mismatch: " + name)
        decoded[name] = {"old_sha256": entry["old_sha256"], "sha256": entry["sha256"], "body": body}
    for name in decoded:
        if any(parent.as_posix() in decoded for parent in PurePosixPath(name).parents):
            raise ValueError("Payload file is also a parent directory: " + name)
    if MANIFEST not in decoded or ESCALATION not in decoded:
        raise ValueError("Checkpoint manifest and escalation question are required")
    manifest = parse_json(decoded[MANIFEST]["body"])
    if not isinstance(manifest, dict) or manifest.get("checkpoint_id") != CHECKPOINT_ID:
        raise ValueError("Embedded manifest does not identify checkpoint 002")
    question = decoded[ESCALATION]["body"].decode("utf-8")
    if not question.strip() or any(line.startswith("## ANSWER") for line in question.splitlines()):
        raise ValueError("Embedded escalation must be an unanswered question")
    return {"base_commit": package["base_commit"], "files": decoded}


def canonical_target():
    return Path.home() / "ARC_Independent_Lab"


def regular_path(target, name, allow_missing=True):
    """Inspect every component without accepting symbolic links or special files."""
    path = target
    parts = PurePosixPath(name).parts
    for index, part in enumerate(parts):
        path = path / part
        if path.is_symlink():
            raise ValueError("Symlink in destination: " + name)
        if not path.exists():
            if allow_missing:
                return target / name
            raise ValueError("Required path is missing: " + name)
        info = path.stat()
        if index < len(parts) - 1:
            if not stat.S_ISDIR(info.st_mode):
                raise ValueError("Destination parent is not a directory: " + name)
        elif not stat.S_ISREG(info.st_mode):
            raise ValueError("Destination is not a regular file: " + name)
    return path


def safe_directory(target, name, allow_missing=True):
    path = target
    for part in PurePosixPath(name).parts:
        path = path / part
        if path.is_symlink():
            raise ValueError("Symlink in required directory: " + name)
        if not path.exists():
            if allow_missing:
                return target / name
            raise ValueError("Required directory is missing: " + name)
        if not path.is_dir():
            raise ValueError("Required directory is not a directory: " + name)
    return path


def inspect_target(target):
    expected = canonical_target()
    if target != expected or target.is_symlink() or not target.is_dir():
        raise ValueError("Existing target must be exactly " + str(expected) + " and not a symlink")
    if target.resolve() != target.absolute():
        raise ValueError("A target ancestor resolves through a symlink")
    safe_directory(target, ".git", allow_missing=False)
    safe_directory(target, "state", allow_missing=False)
    state_path = regular_path(target, "state/PROJECT_STATE.json", allow_missing=False)
    current = parse_json(state_path.read_bytes())
    if not isinstance(current, dict) or current.get("current_gate") != "P1":
        raise ValueError("Current project state does not identify Phase 1")
    print("Existing state:", json.dumps({
        "current_gate": current.get("current_gate"),
        "gate_status": current.get("gate_status"),
        "active_task": current.get("active_task", {}).get("id"),
    }, sort_keys=True))
    regular_path(target, ERROR_LOG)
    safe_directory(target, BACKUP_ROOT)
    validate_error_log(target)


def validate_error_log(target):
    path = regular_path(target, ERROR_LOG)
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            entry = parse_json(line)
            if (not isinstance(entry, dict) or entry.get("checkpoint_id") != CHECKPOINT_ID
                    or not isinstance(entry.get("exit_code"), int) or not entry["exit_code"]):
                raise ValueError("Existing handoff error log is not this helper's log")


def log_git_failure(target, argv, completed):
    validate_error_log(target)
    path = regular_path(target, ERROR_LOG)
    event = {
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "checkpoint_id": CHECKPOINT_ID,
        "command": argv,
        "exit_code": completed.returncode,
        "stdout": completed.stdout.decode("utf-8", errors="replace"),
        "stderr": completed.stderr.decode("utf-8", errors="replace"),
    }
    flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, 0o600)
    with os.fdopen(descriptor, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


class Git:
    def __init__(self, target):
        self.target = target

    def run(self, *args, input_bytes=None):
        env = os.environ.copy()
        # Repository-location overrides must not redirect these commands elsewhere.
        for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
                    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"):
            env.pop(key, None)
        env["GIT_TERMINAL_PROMPT"] = "0"
        argv = ["git", "-C", str(self.target), *args]
        completed = subprocess.run(argv, input=input_bytes, capture_output=True, env=env)
        if completed.returncode:
            log_git_failure(self.target, argv, completed)
            sys.stdout.write(completed.stdout.decode("utf-8", errors="replace"))
            sys.stderr.write(completed.stderr.decode("utf-8", errors="replace"))
            raise RuntimeError("Git step failed; exact output was appended to " + ERROR_LOG
                               + ". Local work is preserved. Fix the reported cause and retry the same helper.")
        return completed.stdout

    def text(self, *args):
        return self.run(*args).decode("utf-8").strip()


def tree_entries(git, commit):
    entries = {}
    raw = git.run("ls-tree", "-r", "--full-tree", "-z", commit)
    for record in raw.split(b"\0"):
        if not record:
            continue
        metadata, name = record.split(b"\t", 1)
        mode, kind, oid = metadata.decode("ascii").split()
        entries[name.decode("utf-8")] = (mode, kind, oid)
    return entries


def body_at(git, entries, name):
    if name not in entries:
        return None
    mode, kind, oid = entries[name]
    if mode not in ("100644", "100755") or kind != "blob":
        raise ValueError("Tracked payload path is not a regular file: " + name)
    return git.run("cat-file", "blob", oid)


def answered_body(name, entry):
    return entry["body"] + ANSWER.encode("utf-8") if name == ESCALATION else entry["body"]


def accepted_body(name, entry, actual):
    if actual is None:
        return entry["old_sha256"] is None
    return (actual == entry["body"] or actual == answered_body(name, entry)
            or (entry["old_sha256"] is not None and digest(actual) == entry["old_sha256"]))


def changed_names(git, *args):
    return {name.decode("utf-8") for name in git.run(*args).split(b"\0") if name}


def inspect_repository(git, package):
    target = git.target
    if Path(git.text("rev-parse", "--show-toplevel")) != target:
        raise ValueError("Git root differs from the exact target")
    if Path(git.text("rev-parse", "--absolute-git-dir")) != target / ".git":
        raise ValueError("Git directory differs from the contained .git directory")
    common = Path(git.text("rev-parse", "--git-common-dir"))
    if (target / common).resolve() != target / ".git":
        raise ValueError("Git common directory is outside the contained .git directory")
    if git.text("branch", "--show-current") != "main":
        raise ValueError("Current branch is not main")
    for options in (("--all",), ("--push", "--all")):
        if git.text("remote", "get-url", *options, "origin").splitlines() != [REMOTE]:
            raise ValueError("Origin must have exactly the expected fetch and push URL; no URL changed")
    if git.run("ls-files", "--unmerged", "-z"):
        raise ValueError("Unmerged index entries exist")
    staged_deletions = changed_names(git, "diff", "--cached", "--name-only",
                                     "--diff-filter=D", "--no-renames", "-z")
    if staged_deletions:
        raise ValueError("Staged deletions exist; no index change made: "
                         + ", ".join(sorted(staged_deletions)))
    allowed = set(package["files"]) | {ERROR_LOG}
    changed = changed_names(git, "diff", "--name-only", "--no-renames", "-z")
    changed |= changed_names(git, "diff", "--cached", "--name-only", "--no-renames", "-z")
    if changed - allowed:
        raise ValueError("Unrelated tracked or staged changes exist: " + ", ".join(sorted(changed - allowed)))
    # Index bytes can contain staged work different from the visible worktree.
    indexed_payload = set()
    for record in git.run("ls-files", "--stage", "-z").split(b"\0"):
        if not record:
            continue
        metadata, name_bytes = record.split(b"\t", 1)
        name = name_bytes.decode("utf-8")
        if name not in package["files"]:
            continue
        indexed_payload.add(name)
        mode, oid, stage = metadata.decode("ascii").split()
        if stage != "0" or mode not in ("100644", "100755"):
            raise ValueError("Payload index entry is not an ordinary file: " + name)
        if not accepted_body(name, package["files"][name], git.run("cat-file", "blob", oid)):
            raise ValueError("Unexpected staged content: " + name)
    for name, entry in package["files"].items():
        if name not in indexed_payload and entry["old_sha256"] is not None:
            raise ValueError("Existing payload file has been removed from the index: " + name)
    head = git.text("rev-parse", "HEAD")
    base = package["base_commit"]
    parents = git.text("rev-list", "--parents", "-n", "1", head).split()
    if head != base and parents != [head, base]:
        raise ValueError("HEAD must be the pinned base or its direct checkpoint-002 child")
    base_entries = tree_entries(git, base)
    for name, entry in package["files"].items():
        original = body_at(git, base_entries, name)
        if ((original is None) != (entry["old_sha256"] is None)
                or (original is not None and digest(original) != entry["old_sha256"])):
            raise ValueError("Pinned old hash does not match base commit: " + name)
    if head != base:
        committed = tree_entries(git, head)
        for name, entry in package["files"].items():
            if body_at(git, committed, name) != answered_body(name, entry):
                raise ValueError("Direct child does not contain the complete answered checkpoint: " + name)
        child_changes = changed_names(git, "diff-tree", "--no-commit-id", "--name-only",
                                      "--no-renames", "-r", "-z", base, head)
        if child_changes - allowed or MANIFEST not in child_changes:
            raise ValueError("Direct child includes unrelated changes or lacks the new manifest")
    print("Existing HEAD:", head, "(base)" if head == base else "(completed checkpoint child)")
    return head


def backup_name(name, old_body):
    return BACKUP_ROOT + "/" + digest(name.encode("utf-8")) + "-" + digest(old_body) + ".bak"


def preflight_files(target, files):
    """Validate every destination and existing backup before changing any payload file."""
    safe_directory(target, BACKUP_ROOT)
    snapshot = {}
    for name, entry in files.items():
        path = regular_path(target, name)
        actual = path.read_bytes() if path.exists() else None
        if not accepted_body(name, entry, actual):
            raise ValueError("Unexpected existing content; nothing overwritten: " + name)
        snapshot[name] = actual
        if actual is not None and actual != answered_body(name, entry):
            backup = regular_path(target, backup_name(name, actual))
            if backup.exists() and backup.read_bytes() != actual:
                raise ValueError("Existing backup content differs: " + str(backup))
    return snapshot


def require_ignored_backups(git):
    probe = (BACKUP_ROOT + "/inspection-probe.bak").encode("utf-8")
    raw = git.run("check-ignore", "--no-index", "--verbose", "-z", "--stdin", input_bytes=probe + b"\0")
    fields = raw.split(b"\0")
    if len(fields) != 5 or fields[3] != probe or not fields[2] or fields[2].startswith(b"!"):
        raise ValueError("Checkpoint backups are not ignored by Git")


def remote_preflight(git, base, head):
    lines = git.text("ls-remote", "--refs", "origin", "refs/heads/main").splitlines()
    if len(lines) != 1 or lines[0].split()[-1] != "refs/heads/main":
        raise ValueError("Remote main is missing or ambiguous")
    advertised = lines[0].split()[0]
    if advertised not in (base, head):
        raise ValueError("Remote main is neither the pinned base nor this local checkpoint commit")
    git.run("fetch", "--no-tags", "origin", "refs/heads/main")
    fetched = git.text("rev-parse", "FETCH_HEAD")
    if fetched != advertised or fetched not in (base, head):
        raise ValueError("Remote main changed during inspection; retry after checking repository state")
    return fetched


def exclusive_write(path, body, mode=0o600):
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, mode)
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(body)
        handle.flush()
        os.fsync(handle.fileno())


def install_files(target, files, snapshot):
    # Recheck the entire accepted snapshot after network inspection and before writes.
    if preflight_files(target, files) != snapshot:
        raise ValueError("Files changed during preflight; no payload files changed")
    safe_directory(target, BACKUP_ROOT)
    backup_dir = target / BACKUP_ROOT
    backup_dir.mkdir(parents=True, exist_ok=True)
    for name, entry in sorted(files.items()):
        path = regular_path(target, name)
        actual = path.read_bytes() if path.exists() else None
        if actual != snapshot[name]:
            raise ValueError("File changed during installation: " + name)
        desired = answered_body(name, entry)
        if actual == desired:
            continue
        mode = stat.S_IMODE(path.stat().st_mode) if actual is not None else 0o644
        if actual is not None:
            backup = regular_path(target, backup_name(name, actual))
            if not backup.exists():
                exclusive_write(backup, actual)
            if backup.read_bytes() != actual:
                raise ValueError("Backup byte verification failed: " + name)
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temp_name = tempfile.mkstemp(prefix="replacement-", dir=backup_dir)
        temporary = Path(temp_name)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                os.fchmod(handle.fileno(), mode)
                handle.write(desired)
                handle.flush()
                os.fsync(handle.fileno())
            regular_path(target, name)
            os.replace(temporary, path)
        finally:
            if temporary.exists():
                temporary.unlink()
        if path.read_bytes() != desired:
            raise ValueError("Post-install byte verification failed: " + name)


def verify_installed(target, files):
    for name, entry in files.items():
        path = regular_path(target, name, allow_missing=False)
        if path.read_bytes() != answered_body(name, entry):
            raise ValueError("Installed payload differs: " + name)


def publish(target, package):
    inspect_target(target)
    git = Git(target)
    head = inspect_repository(git, package)
    snapshot = preflight_files(target, package["files"])
    require_ignored_backups(git)
    remote_preflight(git, package["base_commit"], head)
    install_files(target, package["files"], snapshot)
    verify_installed(target, package["files"])
    require_ignored_backups(git)
    # Index updates are restricted to the explicit payload. New post-commit error
    # records remain for the next checkpoint, so retry never amends or duplicates.
    git.run("add", "--", *sorted(package["files"]))
    if head == package["base_commit"]:
        validate_error_log(target)
        if (target / ERROR_LOG).exists():
            git.run("add", "--", ERROR_LOG)
        staged = changed_names(git, "diff", "--cached", "--name-only", "--no-renames", "-z")
        if not staged or staged - set(package["files"]) - {ERROR_LOG}:
            raise ValueError("Index is empty or contains unrelated paths; refusing commit")
        git.run("-c", "user.name=ARC Independent Lab", "-c", "user.email=arc-independent-lab@localhost",
                "commit", "-m", COMMIT_MESSAGE)
    final_head = inspect_repository(git, package)
    if final_head == package["base_commit"]:
        raise ValueError("Checkpoint commit was not created")
    git.run("push", "origin", "HEAD:refs/heads/main")
    refs = git.text("ls-remote", "--refs", "origin", "refs/heads/main").splitlines()
    if refs != [final_head + "\trefs/heads/main"]:
        raise ValueError("Post-push remote readback does not match the checkpoint commit")
    print("Push completed. Checkpoint commit:", final_head)
    pending = changed_names(git, "diff", "--name-only", "--no-renames", "-z")
    pending |= changed_names(git, "diff", "--cached", "--name-only", "--no-renames", "-z")
    if ERROR_LOG in pending:
        print("Post-commit error records remain locally in", ERROR_LOG,
              "for the next checkpoint; no extra commit was created.")
    print("The principal investigator must independently read back GitHub before claiming durability.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply-and-push", action="store_true")
    args = parser.parse_args()
    package = unpack(PAYLOAD)
    print("Target:", canonical_target())
    print("Remote:", REMOTE)
    print("Pinned base commit:", package["base_commit"])
    print("Payload transitions (old SHA-256 -> new SHA-256):")
    for name, entry in sorted(package["files"].items()):
        print(" ", name, entry["old_sha256"] or "ABSENT", "->", entry["sha256"])
    print("Human answer added only by --apply-and-push:")
    print(ANSWER.strip())
    if not args.apply_and_push:
        print("Inspection only: no local repository, files, commits or remote were modified.")
        return
    publish(canonical_target(), package)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, KeyError, TypeError, zlib.error) as error:
        print("STOP:", error, file=sys.stderr)
        sys.exit(1)
