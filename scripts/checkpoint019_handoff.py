"""Local P3 checkpoint-019 ZIP handoff. No commit, push, fetch, or authentication.

Supply the ZIP and its published SHA-256. Default: inspect. --apply: install and
stage known transitions, then verify actual index blobs. --verify: require the
complete installed and staged payload, or its exact direct-child commit.
"""
import argparse
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
import zipfile

BASE = "728e57f85cc3e995cec10c3a6ee3b950d550d787"
REMOTE = "https://github.com/afazeliUofT/arc-independent-lab.git"
ATTRIBUTES = b"# Preserve the exact bytes of scientific run artifacts.\n/artifacts/** -text\n"
MAX_BYTES = 64 * 1024 * 1024


def sha(body):
    return hashlib.sha256(body).hexdigest()


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key: " + key)
        result[key] = value
    return result


def safe_name(name):
    if not isinstance(name, str) or not name or any(ord(c) < 32 for c in name):
        raise ValueError("Invalid package path")
    path = PurePosixPath(name)
    if (path.is_absolute() or path.as_posix() != name or "\\" in name or ":" in name
            or any(p.lower() in (".", "..", ".git") for p in path.parts)
            or path.parts[0] in ("delivery", "private_sources")
            or path.name == "IDEAS_PARKED.md" or path.suffix.lower() == ".pdf"):
        raise ValueError("Disallowed package path: " + name)
    return name


def load_package(path, expected_hash):
    if not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
        raise ValueError("Expected ZIP SHA-256 must have 64 lowercase hex characters")
    if path.stat().st_size > MAX_BYTES or sha(path.read_bytes()) != expected_hash:
        raise ValueError("ZIP size or SHA-256 differs from the supplied checkpoint")
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        names = [e.filename for e in entries]
        if len(names) != len(set(names)) or sum(e.file_size for e in entries) > MAX_BYTES:
            raise ValueError("Duplicate ZIP members or oversized uncompressed payload")
        manifest = json.loads(archive.read("HANDOFF.json"), object_pairs_hook=unique)
        if (set(manifest) != {"checkpoint_id", "base_commit", "files"}
                or manifest["checkpoint_id"] != "P3_CHECKPOINT_019"
                or manifest["base_commit"] != BASE
                or not isinstance(manifest["files"], dict) or not manifest["files"]):
            raise ValueError("Unexpected handoff manifest")
        files = manifest["files"]
        if set(names) != {"HANDOFF.json"} | {"files/" + n for n in files}:
            raise ValueError("ZIP must contain exactly the declared files and HANDOFF.json")
        for name, entry in files.items():
            safe_name(name)
            if set(entry) != {"old_sha256", "sha256", "mode"} or entry["mode"] not in ("100644", "100755"):
                raise ValueError("Unexpected entry: " + name)
            for key in ("old_sha256", "sha256"):
                if key == "old_sha256" and entry[key] is None:
                    continue
                if not isinstance(entry[key], str) or not re.fullmatch(r"[0-9a-f]{64}", entry[key]):
                    raise ValueError("Invalid content hash: " + name)
            entry["body"] = archive.read("files/" + name)
            if sha(entry["body"]) != entry["sha256"]:
                raise ValueError("Payload byte mismatch: " + name)
            if any(p.as_posix() in files for p in PurePosixPath(name).parents):
                raise ValueError("File/parent collision: " + name)
    if ".gitattributes" in files and files[".gitattributes"]["body"] != ATTRIBUTES:
        raise ValueError("Artifact byte-preservation rule must remain unchanged")
    return files


def ordinary(root, name, directory=False):
    path = root
    parts = PurePosixPath(name).parts
    for i, part in enumerate(parts):
        path = path / part
        if path.is_symlink():
            raise ValueError("Symlink refused: " + name)
        if not path.exists():
            return root / name
        want_dir = i < len(parts) - 1 or directory
        if not (path.is_dir() if want_dir else path.is_file()):
            raise ValueError("Unexpected filesystem object: " + name)
    return path


class Git:
    def __init__(self, root):
        self.root = root

    def run(self, *args):
        env = os.environ.copy()
        for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
                    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"):
            env.pop(key, None)
        env["GIT_OPTIONAL_LOCKS"] = "0"
        argv = ["git", "-C", str(self.root), *args]
        result = subprocess.run(argv, capture_output=True, env=env)
        if result.returncode:
            record = {"command": argv, "exit_code": result.returncode,
                      "stdout": result.stdout.decode("utf-8", "replace"),
                      "stderr": result.stderr.decode("utf-8", "replace")}
            # Exact output is printed even in inspection mode; no error-log write.
            print(json.dumps(record, ensure_ascii=True), file=sys.stderr)
            raise RuntimeError("Git failed; save the printed record. No commit was attempted.")
        return result.stdout

    def text(self, *args):
        return self.run(*args).decode().strip()

    def tree(self, revision):
        result = {}
        for record in self.run("ls-tree", "-r", "-z", revision).split(b"\0"):
            if record:
                metadata, name = record.split(b"\t", 1)
                mode, kind, oid = metadata.decode().split()
                result[name.decode()] = (mode, oid)
        return result

    def index(self):
        result = {}
        for record in self.run("ls-files", "--stage", "-z").split(b"\0"):
            if record:
                metadata, name = record.split(b"\t", 1)
                mode, oid, stage = metadata.decode().split()
                if stage != "0":
                    raise ValueError("Unmerged index entries exist")
                result[name.decode()] = (mode, oid)
        return result


def inspect(root, files, complete=False):
    if root.is_symlink() or root.resolve() != root.absolute() or not root.is_dir():
        raise ValueError("Target must be the existing ordinary ~/ARC_Independent_Lab directory")
    if not ordinary(root, ".git", directory=True).is_dir():
        raise ValueError("Expected a contained ordinary .git directory")
    git = Git(root)
    if (Path(git.text("rev-parse", "--show-toplevel")) != root
            or Path(git.text("rev-parse", "--absolute-git-dir")) != root / ".git"
            or (root / git.text("rev-parse", "--git-common-dir")).resolve() != root / ".git"
            or git.text("branch", "--show-current") != "main"):
        raise ValueError("Repository root, Git directory, or main branch differs")
    for options in (("--all",), ("--push", "--all")):
        if git.text("remote", "get-url", *options, "origin").splitlines() != [REMOTE]:
            raise ValueError("Origin differs from the fixed project URL; no URL changed")
    if ordinary(root, ".gitattributes").read_bytes() != ATTRIBUTES:
        raise ValueError("Expected exact artifact byte-preservation rule")
    base = git.tree(BASE)
    expected = dict(base)
    for name, entry in files.items():
        old = git.run("cat-file", "blob", base[name][1]) if name in base else None
        if (sha(old) if old is not None else None) != entry["old_sha256"]:
            raise ValueError("Declared old hash differs from pinned base: " + name)
        oid = hashlib.sha1(b"blob " + str(len(entry["body"])).encode() + b"\0" + entry["body"]).hexdigest()
        expected[name] = (entry["mode"], oid)
    head = git.text("rev-parse", "HEAD")
    if head != BASE:
        if git.text("rev-list", "--parents", "-n", "1", head).split() != [head, BASE] or git.tree(head) != expected:
            raise ValueError("HEAD is neither the pinned base nor its exact checkpoint child")
        complete = True
    index = git.index()
    if complete:
        if index != expected:
            raise ValueError("Actual index differs from the complete expected tree")
        for name, entry in files.items():
            if sha(git.run("cat-file", "blob", index[name][1])) != entry["sha256"]:
                raise ValueError("Actual staged blob SHA-256 differs: " + name)
    else:
        if set(index) - set(expected) or set(base) - set(index):
            raise ValueError("Unexpected index additions or staged deletions")
        for name, value in index.items():
            if value not in (base.get(name), expected.get(name)):
                raise ValueError("Unrecognized staged content or mode: " + name)
    dirty = {n.decode() for n in git.run("diff", "--name-only", "--no-renames", "-z").split(b"\0") if n}
    if dirty - set(files):
        raise ValueError("Unrelated tracked working changes: " + ", ".join(sorted(dirty - set(files))))
    snapshot = {}
    for name, entry in files.items():
        path = ordinary(root, name)
        body = path.read_bytes() if path.exists() else None
        actual = sha(body) if body is not None else None
        accepted = {entry["sha256"]} if complete else {entry["old_sha256"], entry["sha256"]}
        if actual not in accepted:
            raise ValueError("Unrecognized working bytes; preserved: " + name)
        if path.exists() and ("100755" if path.stat().st_mode & stat.S_IXUSR else "100644") != entry["mode"]:
            raise ValueError("Unexpected working executable mode: " + name)
        snapshot[name] = body
    print("Verified local HEAD:", head)
    print("Verified complete staged checkpoint." if complete else "Verified known old/new transitions.")
    return git, head, snapshot


def apply(root, files):
    git, head, snapshot = inspect(root, files)
    if head != BASE:
        print("Checkpoint commit already exists; no files or index changed.")
        return
    backup_parent = ordinary(root, "delivery/checkpoint019_backups", directory=True)
    backup_parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ-")
    backup = Path(tempfile.mkdtemp(prefix=stamp, dir=backup_parent))
    # Preserve the pre-stage index and every replaced file, including control files.
    index_path = ordinary(root, ".git/index")
    (backup / "index.before").write_bytes(index_path.read_bytes())
    for name, body in snapshot.items():
        if body is not None and body != files[name]["body"]:
            dest = backup / "files" / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(body)
    print("Backup:", backup)
    for name, entry in sorted(files.items()):
        path = ordinary(root, name)
        current = path.read_bytes() if path.exists() else None
        if current != snapshot[name]:
            raise ValueError("Working file changed during application: " + name)
        if current == entry["body"]:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix="replacement-", dir=backup)
        with os.fdopen(fd, "wb") as handle:
            os.fchmod(handle.fileno(), int(entry["mode"][-3:], 8))
            handle.write(entry["body"])
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    git.run("add", "--", *sorted(files))
    inspect(root, files, complete=True)
    print("READY: installed bytes and actual staged blobs match. No commit or push was attempted.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zip_path", type=Path)
    parser.add_argument("--sha256", required=True)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    files = load_package(args.zip_path, args.sha256)
    root = Path.home() / "ARC_Independent_Lab"
    print("Target:", root)
    print("Pinned base:", BASE)
    for name, entry in sorted(files.items()):
        print(name, entry["old_sha256"] or "absent", "->", entry["sha256"])
    if args.apply:
        apply(root, files)
    else:
        inspect(root, files, complete=args.verify)
        print("Inspection only. No changes or network calls were made.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, OSError, KeyError, TypeError, zipfile.BadZipFile) as error:
        print("STOP:", error, file=sys.stderr)
        sys.exit(1)
