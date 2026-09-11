#!/usr/bin/env python3
"""Read-only verification of the focused review's file identity, not its science."""
import hashlib
import json
import sys
from pathlib import Path, PurePosixPath


def verify(root):
    manifest_path = root / "evidence/P3_FOCUSED_REVIEW_MANIFEST_037.json"
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    errors = []
    seen = set()
    entries = manifest["inputs"]
    if not entries:
        errors.append("Empty input inventory")
    for entry in entries:
        name = entry["path"]
        relative = PurePosixPath(name)
        if (not name or relative.is_absolute() or ".." in relative.parts
                or "\\" in name or name in seen or str(relative) != name):
            errors.append("Invalid or duplicate input path: " + name)
            continue
        seen.add(name)
        path = root.joinpath(*relative.parts)
        if any(parent.is_symlink() for parent in [path, *path.parents] if parent != root.parent):
            errors.append("Symlink input: " + name)
            continue
        if not path.is_file():
            errors.append("Missing input: " + name)
            continue
        observed = hashlib.sha256(path.read_bytes()).hexdigest()
        if observed != entry["sha256"]:
            errors.append("Hash mismatch: " + name)
    return {
        "kind": "FOCUSED_REVIEW037_INPUT_INTEGRITY_v1",
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "input_count": len(entries),
        "input_integrity": "PASS" if not errors else "FAIL",
        "errors": errors,
        "scientific_verdict": None,
        "independent_reviewer_execution": False,
    }


def main():
    root = Path(__file__).resolve().parents[1]
    try:
        result = verify(root)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"input_integrity": "FAIL", "errors": [str(exc)]}))
        return 1
    print(json.dumps(result, indent=2))
    return 0 if result["input_integrity"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
