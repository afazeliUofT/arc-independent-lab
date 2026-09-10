"""Local checkpoint026 publication handoff. No native/model operation.

Default inspection; --apply installs/stages exact known transitions; --verify
checks the full expected tree. Human commits and pushes separately.
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

BASE = "f6bf890d5ef3b8ad7590f3ac05d6942bd0a27c99"
REMOTE = "https://github.com/afazeliUofT/arc-independent-lab.git"
ATTRIBUTES = b"# Preserve the exact bytes of scientific run artifacts.\n/artifacts/** -text\n"
CHECKPOINT_ID = "P3_CHECKPOINT_026"
CHECKPOINT_PATH = "state/CHECKPOINT_026.json"
MAX_BYTES = 64 * 1026 * 1026


def sha(body):
    return hashlib.sha256(body).hexdigest()


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=True, indent=2) + "\n").encode("utf-8")


def safe_name(name, payload=True):
    if not isinstance(name, str) or not name or any(ord(c) < 32 for c in name):
        raise ValueError("Invalid package path")
    path = PurePosixPath(name)
    if (not path.parts or path.is_absolute() or path.as_posix() != name or "\\" in name or ":" in name
            or any(p.lower() in (".", "..", ".git") for p in path.parts)):
        raise ValueError("Disallowed package path: " + name)
    if payload and (path.parts[0] in ("delivery", "private_sources")
                    or path.name == "IDEAS_PARKED.md" or path.suffix.lower() == ".pdf"):
        raise ValueError("Disallowed changed payload path: " + name)
    return name


def valid_hash(value):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def checkpoint_rows(body):
    checkpoint = json.loads(body, object_pairs_hook=unique)
    if (checkpoint.get("checkpoint_id") != CHECKPOINT_ID
            or checkpoint.get("base_commit") != BASE
            or CHECKPOINT_PATH not in checkpoint.get("exclusions", {})
            or not isinstance(checkpoint.get("files"), list)):
        raise ValueError("Unexpected checkpoint manifest")
    rows = {}
    for row in checkpoint["files"]:
        if (not isinstance(row, dict) or set(row) != {"path", "sha256", "mode"}
                or not valid_hash(row["sha256"]) or row["mode"] not in ("100644", "100755")):
            raise ValueError("Invalid checkpoint file entry")
        # Existing published files (including IDEAS_PARKED.md) are inventory
        # entries only. The stricter payload rule still prevents changing them.
        name = safe_name(row["path"], payload=False)
        if name in rows or name == CHECKPOINT_PATH:
            raise ValueError("Duplicate or self-hashed checkpoint entry")
        rows[name] = row
    return checkpoint, rows


def validate_unsigned(files):
    if CHECKPOINT_PATH not in files:
        raise ValueError("Checkpoint inventory absent")
    checkpoint, rows = checkpoint_rows(files[CHECKPOINT_PATH]["body"])
    for name, entry in files.items():
        if name == CHECKPOINT_PATH:
            continue
        if (name not in rows or rows[name]["sha256"] != entry["sha256"]
                or rows[name]["mode"] != entry["mode"]):
            raise ValueError("Checkpoint manifest differs from payload: " + name)
    return checkpoint


def load_package(path, expected_hash):
    if not valid_hash(expected_hash):
        raise ValueError("Expected ZIP SHA-256 must have 64 lowercase hex characters")
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise ValueError("ZIP must be an ordinary file within the size limit")
    raw = path.read_bytes()
    if sha(raw) != expected_hash:
        raise ValueError("ZIP SHA-256 differs from the supplied checkpoint")
    # Read the verified bytes, avoiding a second read of a replaceable ZIP path.
    import io
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        entries = archive.infolist()
        names = [entry.filename for entry in entries]
        if (len(names) != len(set(names))
                or sum(entry.file_size for entry in entries) > MAX_BYTES):
            raise ValueError("Duplicate ZIP members or oversized uncompressed payload")
        for entry in entries:
            mode = entry.external_attr >> 16
            if entry.is_dir() or (stat.S_IFMT(mode) not in (0, stat.S_IFREG)):
                raise ValueError("ZIP contains a nonregular member")
        manifest = json.loads(archive.read("HANDOFF.json"), object_pairs_hook=unique)
        if (set(manifest) != {"checkpoint_id", "base_commit", "files"}
                or manifest["checkpoint_id"] != CHECKPOINT_ID
                or manifest["base_commit"] != BASE
                or not isinstance(manifest["files"], dict) or not manifest["files"]):
            raise ValueError("Unexpected handoff manifest")
        files = manifest["files"]
        if set(names) != {"HANDOFF.json"} | {"files/" + name for name in files}:
            raise ValueError("ZIP must contain exactly the declared files and HANDOFF.json")
        for name, entry in files.items():
            safe_name(name)
            if (not isinstance(entry, dict) or set(entry) != {"old_sha256", "sha256", "mode"}
                    or entry["mode"] not in ("100644", "100755")):
                raise ValueError("Unexpected entry: " + name)
            if (not valid_hash(entry["sha256"])
                    or (entry["old_sha256"] is not None and not valid_hash(entry["old_sha256"]))):
                raise ValueError("Invalid content hash: " + name)
            entry["body"] = archive.read("files/" + name)
            if sha(entry["body"]) != entry["sha256"]:
                raise ValueError("Payload byte mismatch: " + name)
            if any(parent.as_posix() in files for parent in PurePosixPath(name).parents):
                raise ValueError("File/parent collision: " + name)
    if ".gitattributes" in files and files[".gitattributes"]["body"] != ATTRIBUTES:
        raise ValueError("Artifact byte-preservation rule must remain unchanged")
    validate_unsigned(files)
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

    def run(self, *args, input_bytes=None):
        env = os.environ.copy()
        for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
                    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"):
            env.pop(key, None)
        env["GIT_OPTIONAL_LOCKS"] = "0"
        result = subprocess.run(["git", "-C", str(self.root), *args],
                                input=input_bytes, capture_output=True, env=env)
        if result.returncode:
            # Git output/configuration can contain credential-bearing URLs or
            # helper diagnostics. Preserve credential configuration and print
            # no output, environment, arguments, or credential values.
            raise RuntimeError("Local Git operation failed (exit " + str(result.returncode)
                               + "); no commit, push, or authentication was attempted")
        return result.stdout

    def text(self, *args):
        return self.run(*args).decode("utf-8").strip()

    def tree(self, revision):
        result = {}
        for record in self.run("ls-tree", "-r", "-z", revision).split(b"\0"):
            if record:
                metadata, raw_name = record.split(b"\t", 1)
                mode, kind, oid = metadata.decode().split()
                name = raw_name.decode("utf-8")
                if kind != "blob" or mode not in ("100644", "100755") or name in result:
                    raise ValueError("Unsupported or duplicate tracked Git entry")
                result[name] = (mode, oid)
        return result

    def index(self):
        result = {}
        for record in self.run("ls-files", "--stage", "-z").split(b"\0"):
            if record:
                metadata, raw_name = record.split(b"\t", 1)
                mode, oid, stage = metadata.decode().split()
                name = raw_name.decode("utf-8")
                if stage != "0" or name in result:
                    raise ValueError("Unmerged or duplicate index entries exist")
                result[name] = (mode, oid)
        return result

    def blobs(self, oids):
        oids = sorted(set(oids))
        if not oids:
            return {}
        raw = self.run("cat-file", "--batch", input_bytes=("\n".join(oids) + "\n").encode())
        result, offset = {}, 0
        for oid in oids:
            end = raw.find(b"\n", offset)
            header = raw[offset:end].decode().split() if end >= 0 else []
            if len(header) != 3 or header[0] != oid or header[1] != "blob":
                raise ValueError("Actual Git blob could not be verified")
            size = int(header[2])
            if size < 0 or raw[end + 1 + size:end + 2 + size] != b"\n":
                raise ValueError("Invalid Git blob response")
            result[oid] = raw[end + 1:end + 1 + size]
            offset = end + size + 2
        if offset != len(raw):
            raise ValueError("Unexpected trailing Git blob response")
        return result


def blob_oid(body):
    return hashlib.sha1(b"blob " + str(len(body)).encode() + b"\0" + body).hexdigest()


def known_trees(git, unsigned_files, selected_files):
    base = git.tree(BASE)
    bodies = git.blobs(oid for mode, oid in base.values())
    unsigned, expected = dict(base), dict(base)
    for name, entry in unsigned_files.items():
        old = bodies[base[name][1]] if name in base else None
        if (sha(old) if old is not None else None) != entry["old_sha256"]:
            raise ValueError("Declared old hash differs from pinned base: " + name)
        unsigned[name] = (entry["mode"], blob_oid(entry["body"]))
    for name, entry in selected_files.items():
        expected[name] = (entry["mode"], blob_oid(entry["body"]))
    # The checkpoint's full file manifest is also checked against the actual
    # pinned base, preventing omitted files or invented unchanged-file hashes.
    _, rows = checkpoint_rows(selected_files[CHECKPOINT_PATH]["body"])
    if set(rows) != set(expected) - {CHECKPOINT_PATH}:
        raise ValueError("Checkpoint manifest does not cover the exact full expected tree")
    for name, row in rows.items():
        body = selected_files[name]["body"] if name in selected_files else bodies[base[name][1]]
        if row["mode"] != expected[name][0] or row["sha256"] != sha(body):
            raise ValueError("Checkpoint manifest differs from actual expected bytes or mode: " + name)
    return base, unsigned, expected, bodies


def classify_head(git, head, expected):
    if head == BASE:
        return "base025"
    if (git.text("rev-list", "--parents", "-n", "1", head).split() == [head, BASE]
            and git.tree(head) == expected):
        return "checkpoint026"
    raise ValueError("HEAD is neither the pinned base025 nor the exact selected026 child")


def working_value(path):
    if not path.exists():
        return None, None
    mode = "100755" if path.stat().st_mode & stat.S_IXUSR else "100644"
    return path.read_bytes(), mode


def inspect(root, files, complete=False, unsigned_files=None, quiet=False):
    unsigned_files = files if unsigned_files is None else unsigned_files
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
    base, unsigned, expected, base_bodies = known_trees(git, unsigned_files, files)
    head = git.text("rev-parse", "HEAD")
    disposition = classify_head(git, head, expected)
    complete = complete or disposition == "checkpoint026"
    index = git.index()
    if complete and index != expected:
        raise ValueError("Actual index differs from the complete expected tree")
    if set(index) - set(expected) or set(base) - set(index):
        raise ValueError("Unexpected index additions or staged deletions; preserved")
    for name, value in index.items():
        accepted = (expected.get(name),) if complete else (base.get(name), unsigned.get(name), expected.get(name))
        if value not in accepted:
            raise ValueError("Unrecognized staged content or mode; preserved: " + name)
    staged_bodies = git.blobs(oid for mode, oid in index.values())
    snapshot = {}
    for name in sorted(expected):
        old_body = base_bodies[base[name][1]] if name in base else None
        old_mode = base[name][0] if name in base else None
        selected_body = files[name]["body"] if name in files else old_body
        selected_mode = expected[name][0]
        allowed = [(selected_body, selected_mode)]
        if not complete:
            allowed.append((old_body, old_mode))
            if name in unsigned_files:
                allowed.append((unsigned_files[name]["body"], unsigned_files[name]["mode"]))
        if name in index:
            staged = (staged_bodies[index[name][1]], index[name][0])
            if staged not in allowed:
                raise ValueError("Actual staged blob bytes or mode differ; preserved: " + name)
        path = ordinary(root, name)
        current = working_value(path)
        if current not in allowed:
            raise ValueError("Unrecognized working bytes or mode; preserved: " + name)
        snapshot[name] = current
    if not quiet:
        print("Verified local HEAD:", head)
        print("Recognized checkpoint state:", disposition)
        print("Verified complete staged checkpoint." if complete else "Verified known base025/026 transitions.")
    return git, head, snapshot, disposition


def apply(root, files, unsigned_files=None):
    unsigned_files = files if unsigned_files is None else unsigned_files
    git, head, snapshot, disposition = inspect(root, files, unsigned_files=unsigned_files)
    if disposition == "checkpoint026":
        print("Checkpoint commit already exists; no files or index changed.")
        return
    expected = git.tree(BASE)
    expected.update({name: (entry["mode"], blob_oid(entry["body"]))
                     for name, entry in files.items()})
    if (git.index() == expected
            and all(snapshot[name] == (entry["body"], entry["mode"])
                    for name, entry in files.items())):
        inspect(root, files, complete=True, unsigned_files=unsigned_files, quiet=True)
        print("Selected checkpoint is already completely installed and staged; no changes made.")
        return
    index_path = ordinary(root, ".git/index")
    index_before = index_path.read_bytes()
    backup_parent = ordinary(root, "delivery/checkpoint026_backups", directory=True)
    backup_parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ-")
    backup = Path(tempfile.mkdtemp(prefix=stamp, dir=backup_parent))
    (backup / "index.before").write_bytes(index_before)
    for name, entry in files.items():
        body, mode = snapshot[name]
        if body is not None and (body, mode) != (entry["body"], entry["mode"]):
            dest = backup / "files" / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(body)
            dest.chmod(int(mode[-3:], 8))
    print("Backup:", backup)
    for name, entry in sorted(files.items()):
        path = ordinary(root, name)
        current = working_value(path)
        if current != snapshot[name]:
            raise ValueError("Working file changed during application; preserved: " + name)
        if current == (entry["body"], entry["mode"]):
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix="replacement-", dir=backup)
        with os.fdopen(fd, "wb") as handle:
            os.fchmod(handle.fileno(), int(entry["mode"][-3:], 8))
            handle.write(entry["body"])
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    # Recheck the entire tracked tree before staging, including unrelated bytes
    # that Git attributes, assume-unchanged, or skip-worktree could conceal.
    inspect(root, files, unsigned_files=unsigned_files, quiet=True)
    if git.text("rev-parse", "HEAD") != head or index_path.read_bytes() != index_before:
        raise ValueError("HEAD or index changed concurrently; installed files and backup preserved")
    records = []
    for name, entry in sorted(files.items()):
        oid = git.run("hash-object", "-w", "--stdin", "--no-filters", input_bytes=entry["body"]).decode().strip()
        if oid != blob_oid(entry["body"]):
            raise ValueError("Actual stored object differs from selected payload: " + name)
        records.append((entry["mode"] + " " + oid + "\t" + name + "\0").encode())
    # Direct index entries avoid clean filters and preserve exact payload bytes
    # and executable modes even when core.autocrlf/core.fileMode differ locally.
    git.run("update-index", "-z", "--index-info", input_bytes=b"".join(records))
    inspect(root, files, complete=True, unsigned_files=unsigned_files)
    print("READY: installed bytes and actual staged blobs match. No commit or push was attempted.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zip_path", type=Path, nargs="?")
    parser.add_argument("--sha256")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.zip_path is None and args.sha256 is None and not (args.apply or args.verify):
        print("Inspection only. Supply ZIP and --sha256; --apply installs/stages exact checkpoint bytes.")
        print("No files, network state, native process or model were changed or started.")
        return
    if args.zip_path is None or args.sha256 is None:
        parser.error("ZIP path and --sha256 are both required")
    files = load_package(args.zip_path, args.sha256)
    root = Path.home() / "ARC_Independent_Lab"
    print("Target:", root)
    print("Pinned base:", BASE)
    print("Checkpoint files to install or verify:", len(files))
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
