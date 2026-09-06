#!/usr/bin/env python3
"""Read-only checkpoint-002 diagnostic. No writes, staging, commits or network calls.
Prints hashes and narrow Git settings; never prints file contents or credentials.
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import zlib

EXPECTED = json.loads(zlib.decompress(base64.b64decode("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")))
BASE = "189f424e5cc9588d9774fd58850c44c9b182f813"
METRICS = "artifacts/P1_LINEAR_INTERFERENCE/20260906_001/metrics.csv"
ORIGINAL_HELPER_HASH = "f006b97b3a64c115c55cf21cb8614385014a4a38d64bcb80b24df8715f566dc1"
EXPECTED_REMOTE = "https://github.com/afazeliUofT/arc-independent-lab.git"
ROOT = Path.home() / "ARC_Independent_Lab"
DEADLINE = time.monotonic() + 60


def digest(body):
    return hashlib.sha256(body).hexdigest()


def command(*args):
    if time.monotonic() >= DEADLINE:
        raise RuntimeError("Read-only diagnostic reached its time limit")
    env = os.environ.copy()
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
                "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"):
        env.pop(key, None)
    env["GIT_OPTIONAL_LOCKS"] = "0"
    env["GIT_TERMINAL_PROMPT"] = "0"
    return subprocess.run(["git", "--no-optional-locks", "-C", str(ROOT), *args],
                          capture_output=True, env=env, timeout=10)


def text_result(*args):
    p = command(*args)
    return {"exit_code": p.returncode,
            "stdout": p.stdout.decode("utf-8", errors="replace").strip(),
            "stderr": p.stderr.decode("utf-8", errors="replace").strip()}


def read_working(name):
    path = ROOT
    for part in Path(name).parts:
        path = path / part
        if path.is_symlink():
            raise RuntimeError("Refusing symbolic-link path: " + name)
    return path.read_bytes() if path.is_file() else None


def describe(body):
    if body is None:
        return {"present": False}
    return {"present": True, "sha256": digest(body), "bytes": len(body),
            "crlf_pairs": body.count(b"\r\n"),
            "bare_lf": body.count(b"\n") - body.count(b"\r\n"),
            "sha256_after_crlf_to_lf": digest(body.replace(b"\r\n", b"\n"))}


def main():
    report = {"diagnostic": "P1_CHECKPOINT_002_READ_ONLY_v1", "read_only": True,
              "probe_sha256": digest(Path(__file__).read_bytes()), "expected_base": BASE}
    try:
        if ROOT.is_symlink() or ROOT.resolve() != ROOT.absolute() or not ROOT.is_dir():
            raise RuntimeError("Expected ordinary project directory is missing or symlinked")
        if (ROOT / ".git").is_symlink() or not (ROOT / ".git").is_dir():
            raise RuntimeError("Expected contained ordinary .git directory is missing")
        report["git_version"] = text_result("--version")
        report["head_and_parents"] = text_result("rev-list", "--parents", "-n", "1", "HEAD")
        report["branch"] = text_result("branch", "--show-current")
        report["tracked_status"] = text_result("status", "--porcelain=v1", "--untracked-files=no")
        # Do not print remote strings: a misconfigured URL could contain a credential.
        for label, options in (("fetch", ("--all",)), ("push", ("--push", "--all"))):
            p = command("remote", "get-url", *options, "origin")
            report[label + "_origin_matches_expected"] = (p.returncode == 0 and
                p.stdout.decode("utf-8", errors="replace").splitlines() == [EXPECTED_REMOTE])
        report["conversion_settings"] = text_result("config", "--show-origin", "--get-regexp",
            r"^core\.(autocrlf|eol|safecrlf|attributesfile)$")
        report["metrics_attributes"] = text_result("check-attr", "text", "eol", "filter", "ident",
                                                   "working-tree-encoding", "--", METRICS)
        helper = Path.home() / "P1_CHECKPOINT_002.py"
        report["original_helper_present_at_reported_path"] = helper.is_file() and not helper.is_symlink()
        if report["original_helper_present_at_reported_path"]:
            report["original_helper_sha256"] = digest(helper.read_bytes())
            report["original_helper_matches_delivered"] = report["original_helper_sha256"] == ORIGINAL_HELPER_HASH
        report["metrics_bytes"] = {"working": describe(read_working(METRICS))}
        for layer, spec in (("index", ":" + METRICS), ("HEAD", "HEAD:" + METRICS)):
            p = command("show", spec)
            report["metrics_bytes"][layer] = describe(p.stdout if p.returncode == 0 else None)
            report["metrics_bytes"][layer]["git_exit_code"] = p.returncode
        # Compare all declared checkpoint files; output only missing/differing paths and hashes.
        comparisons = {}
        for layer in ("working", "index", "HEAD"):
            mismatches = []
            for name, expected in sorted(EXPECTED.items()):
                if layer == "working":
                    body = read_working(name)
                else:
                    p = command("show", (":" if layer == "index" else "HEAD:") + name)
                    body = p.stdout if p.returncode == 0 else None
                actual = digest(body) if body is not None else None
                if actual != expected:
                    mismatches.append({"path": name, "expected_sha256": expected,
                                       "actual_sha256": actual})
            comparisons[layer] = {"declared_files_checked": len(EXPECTED), "mismatches": mismatches}
        report["checkpoint_comparison"] = comparisons
    except Exception as error:
        report["diagnostic_error"] = str(error)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
