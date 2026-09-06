#!/usr/bin/env python3
"""Checkpoint 002 exact-byte recovery. Default: inspect only.

--repair-and-push creates an artifact line-ending rule, re-stages the intact
CSV, appends one correction commit, and performs an ordinary push. It neither
rewrites the original CSV nor changes global Git settings or existing history.
"""
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import zlib

EXPECTED = json.loads(zlib.decompress(base64.b64decode("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")))
ROOT = Path.home() / "ARC_Independent_Lab"
REMOTE = "https://github.com/afazeliUofT/arc-independent-lab.git"
BASE = "189f424e5cc9588d9774fd58850c44c9b182f813"
BAD_HEAD = "6b06dc1120b22d59ae7c9d550feb3f124ff656fa"
CSV = "artifacts/P1_LINEAR_INTERFERENCE/20260906_001/metrics.csv"
NORMALIZED_SHA = "f45b2c3d830f985629cb308a12ff11e94afbf7d4b2a436a5441d87595eafd34e"
ATTR = ".gitattributes"
ATTR_BYTES = (b"# Preserve the exact bytes of scientific run artifacts.\n"
              b"/artifacts/** -text\n")
ERROR_LOG = "state/handoff_002_repair_errors.jsonl"
MESSAGE = ("P1.1: preserve original artifact bytes in Git\n\n"
           "core.autocrlf=input normalized metrics.csv in the earlier local checkpoint.\n"
           "Add an artifact-specific -text rule and re-stage the intact original file.\n"
           "Preserve the earlier commit, raw working bytes and all checkpoint hashes.\n"
           "All declared checkpoint files are checked before and after this commit.")


def sha(body):
    return hashlib.sha256(body).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def path_for(name):
    path = ROOT
    parts = Path(name).parts
    require(not Path(name).is_absolute() and ".." not in parts, "Unsafe relative path")
    for index, part in enumerate(parts):
        path = path / part
        require(not path.is_symlink(), "Symlink refused: " + name)
        if path.exists():
            require(path.is_dir() if index < len(parts) - 1 else path.is_file(),
                    "Unexpected file type: " + name)
    return path


class Git:
    def __init__(self, write_errors=False):
        self.write_errors = write_errors
        self.deadline = time.monotonic() + 300

    def run(self, *args):
        require(time.monotonic() < self.deadline, "Repair reached its declared runtime limit")
        env = os.environ.copy()
        for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
                    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"):
            env.pop(key, None)
        env["GIT_TERMINAL_PROMPT"] = "0"
        env["GIT_OPTIONAL_LOCKS"] = "0"
        command = ["git", "--no-optional-locks", "-C", str(ROOT), *args]
        try:
            p = subprocess.run(command, capture_output=True, env=env,
                               timeout=min(60, max(1, self.deadline - time.monotonic())))
        except subprocess.TimeoutExpired as error:
            raise RuntimeError("Git timed out; local work is preserved. Retry this repair after checking the cause.") from error
        if p.returncode:
            if self.write_errors:
                log = path_for(ERROR_LOG)
                with log.open("a", encoding="utf-8") as f:
                    f.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(),
                        "operation": "checkpoint002_repair", "command": list(args),
                        "exit_code": p.returncode, "stdout": p.stdout.decode(errors="replace"),
                        "stderr": p.stderr.decode(errors="replace")}) + "\n")
            sys.stderr.write(p.stderr.decode(errors="replace"))
            raise RuntimeError("Git failed; no reset or rollback was performed. Local files and commits are preserved.")
        return p.stdout

    def text(self, *args):
        return self.run(*args).decode("utf-8").strip()


def tree(git, ref):
    result = {}
    for row in git.run("ls-tree", "-r", "-z", ref).split(b"\0"):
        if row:
            meta, name = row.split(b"\t", 1)
            mode, kind, oid = meta.decode("ascii").split()
            result[name.decode("utf-8")] = (mode, kind, oid)
    return result


def index(git):
    result = {}
    for row in git.run("ls-files", "--stage", "-z").split(b"\0"):
        if row:
            meta, name = row.split(b"\t", 1)
            mode, oid, stage = meta.decode("ascii").split()
            require(stage == "0", "Unmerged index entries exist")
            result[name.decode("utf-8")] = (mode, "blob", oid)
    return result


def blob(git, entries, name):
    if name not in entries:
        return None
    mode, kind, oid = entries[name]
    require(mode in ("100644", "100755") and kind == "blob", "Nonregular Git entry: " + name)
    return git.run("cat-file", "blob", oid)


def names(git, *args):
    return {x.decode("utf-8") for x in git.run(*args).split(b"\0") if x}


def attributes(git, cached=False, after=False):
    args = ["check-attr", "-z"] + (["--cached"] if cached else [])
    args += ["text", "eol", "filter", "ident", "working-tree-encoding", "--", CSV, ATTR]
    fields = git.run(*args).split(b"\0")
    require(fields[-1] == b"" and (len(fields) - 1) % 3 == 0, "Unexpected attribute response")
    values = {(fields[i].decode(), fields[i+1].decode()): fields[i+2].decode()
              for i in range(0, len(fields)-1, 3)}
    for name in (CSV, ATTR):
        for attribute in ("filter", "ident", "working-tree-encoding", "eol"):
            require(values[(name, attribute)] in ("unspecified", "unset"),
                    "Unexpected transformation attribute: " + name + " " + attribute)
    require(values[(CSV, "text")] in (("unset",) if after else ("unspecified", "unset")),
            "Artifact text attribute conflicts with this repair")
    return values


def inspect(git):
    require(ROOT.is_dir() and not ROOT.is_symlink() and ROOT.resolve() == ROOT.absolute(),
            "Expected ordinary project directory is missing or symlinked")
    require((ROOT / ".git").is_dir() and not (ROOT / ".git").is_symlink(),
            "A contained ordinary .git directory is required")
    require(Path(git.text("rev-parse", "--show-toplevel")) == ROOT, "Repository root differs")
    require(Path(git.text("rev-parse", "--absolute-git-dir")) == ROOT / ".git", "Git directory differs")
    require((ROOT / git.text("rev-parse", "--git-common-dir")).resolve() == ROOT / ".git",
            "Git common directory is not contained in this project")
    require(git.text("branch", "--show-current") == "main", "Expected branch main")
    for options in (("--all",), ("--push", "--all")):
        require(git.text("remote", "get-url", *options, "origin").splitlines() == [REMOTE],
                "Origin does not match the authorized repository; no URL changed")
    head = git.text("rev-parse", "HEAD")
    parents = git.text("rev-list", "--parents", "-n", "1", head).split()
    repaired = head != BAD_HEAD
    require(parents == ([head, BAD_HEAD] if repaired else [BAD_HEAD, BASE]),
            "HEAD is neither the measured commit nor its direct correction child")
    bad_tree = tree(git, BAD_HEAD)
    require(ATTR not in bad_tree, "Measured commit already has an unfamiliar attribute file")
    ht, ix = tree(git, head), index(git)
    require(ht.get(CSV, (None,))[0] == ix.get(CSV, (None,))[0] == "100644",
            "Unexpected CSV file mode")
    require(ATTR not in ix or ix[ATTR][0] == "100644", "Unexpected staged attribute mode")
    for name, expected in EXPECTED.items():
        working = path_for(name)
        require(working.is_file() and sha(working.read_bytes()) == expected,
                "Working checkpoint bytes differ: " + name)
        head_body, index_body = blob(git, ht, name), blob(git, ix, name)
        head_hash = sha(head_body) if head_body is not None else None
        index_hash = sha(index_body) if index_body is not None else None
        require(head_hash == (NORMALIZED_SHA if name == CSV and not repaired else expected),
                "Unexpected committed checkpoint bytes: " + name)
        allowed_index = {expected, NORMALIZED_SHA} if name == CSV and not repaired else {expected}
        require(index_hash in allowed_index, "Unexpected staged checkpoint bytes: " + name)
    attribute_path = path_for(ATTR)
    require(not attribute_path.exists() or attribute_path.read_bytes() == ATTR_BYTES,
            "Existing attribute file differs; nothing overwritten")
    require(blob(git, ix, ATTR) in (None, ATTR_BYTES), "Unfamiliar staged attribute file")
    changed = names(git, "diff", "--name-only", "--no-renames", "-z")
    changed |= names(git, "diff", "--cached", "--name-only", "--no-renames", "-z")
    require(not changed - {ATTR, CSV}, "Unrelated tracked or staged changes exist")
    if repaired:
        delta = names(git, "diff-tree", "--no-commit-id", "--name-only", "--no-renames", "-r", "-z", BAD_HEAD, head)
        require(delta == {ATTR, CSV}, "Correction child changed unexpected paths")
        require(blob(git, ht, ATTR) == ATTR_BYTES and blob(git, ix, ATTR) == ATTR_BYTES,
                "Correction attribute bytes differ")
        require(ht[ATTR][0] == ht[CSV][0] == "100644", "Unexpected correction file mode")
        require(not changed, "Correction child has tracked changes")
    attributes(git, after=repaired)
    attributes(git, cached=True, after=repaired)
    return head, repaired


def remote_head(git):
    rows = git.text("ls-remote", "--refs", "origin", "refs/heads/main").splitlines()
    require(len(rows) == 1 and rows[0].endswith("\trefs/heads/main"), "Unexpected remote main")
    return rows[0].split()[0]


def execute(apply):
    git = Git(write_errors=apply)
    head, repaired = inspect(git)
    print("Verified local commit:", head)
    print("All original working checkpoint bytes match their declared hashes.")
    print("Proposed artifact rule:", ATTR_BYTES.decode().strip())
    print("Action: append a correction commit if needed, then push the verified commit.")
    if not apply:
        print("Inspection only. No changes or network calls were made.")
        return
    require(remote_head(git) in {BASE, BAD_HEAD, head}, "Remote advanced unexpectedly; nothing changed")
    # Recheck the complete state after the network read and before any mutation.
    require(inspect(git) == (head, repaired), "Local state changed during preflight")
    if not repaired:
        attr = path_for(ATTR)
        if not attr.exists():
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
            with os.fdopen(os.open(attr, flags, 0o644), "wb") as handle:
                handle.write(ATTR_BYTES)
                handle.flush()
                os.fsync(handle.fileno())
        git.run("add", "--", ATTR)
        attributes(git, after=True)
        attributes(git, cached=True, after=True)
        git.run("add", "--renormalize", "--", CSV)
        # Inspect exact index bytes for every original declared file BEFORE commit.
        ix = index(git)
        for name, expected in EXPECTED.items():
            require(sha(blob(git, ix, name)) == expected, "Staging did not preserve exact bytes: " + name)
        require(blob(git, ix, ATTR) == ATTR_BYTES, "Staged attribute bytes differ")
        require(names(git, "diff", "--cached", "--name-only", "--no-renames", "-z") == {ATTR, CSV},
                "Correction would include unexpected staged changes")
        require(not names(git, "diff", "--name-only", "--no-renames", "-z"),
                "Working tree changed while preparing correction")
        git.run("-c", "user.name=ARC Independent Lab", "-c", "user.email=arc-independent-lab@localhost",
                "commit", "-m", MESSAGE)
    final, verified_repaired = inspect(git)
    require(verified_repaired, "No verified correction commit exists")
    require(remote_head(git) in {BASE, BAD_HEAD, final}, "Remote advanced; correction preserved locally")
    git.run("push", "origin", final + ":refs/heads/main")
    require(remote_head(git) == final, "Remote ref does not match the pushed correction")
    print("Repair and push completed. Commit:", final)
    print("The original commit is preserved. All original checkpoint hashes match.")
    print("The principal investigator must independently read back GitHub before continuing Phase 1.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repair-and-push", action="store_true")
    args = parser.parse_args()
    try:
        execute(args.repair_and_push)
    except (OSError, ValueError, RuntimeError, TypeError) as error:
        print("STOP:", error, file=sys.stderr)
        sys.exit(1)
