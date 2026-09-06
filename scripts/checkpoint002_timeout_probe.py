#!/usr/bin/env python3
"""Read-only Git diagnosis of checkpoint 002; writes only a local error log.

Place beside the unchanged P1_CHECKPOINT_002_REPAIR.py and run with Python 3
inside WSL. No repair, commit, push, configuration change or automatic retry.
Only the short terminal report is intended for sharing. Raw failure output,
which can contain private transport details, stays in the project error log.
"""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import types

REPAIR_SHA = "2d024c8cf2c042885414f53275bea836094a8ab4dd7d77da876abb83b703f9de"
# Inside Git metadata so raw transport output cannot enter a normal commit.
ERROR_LOG = ".git/checkpoint002_timeout_errors.jsonl"
COMMAND_SECONDS = 60
TOTAL_SECONDS = 300
READ_COMMANDS = {"rev-parse", "branch", "remote", "rev-list", "ls-tree",
                 "ls-files", "cat-file", "diff", "diff-tree", "check-attr", "ls-remote"}


def load_repair(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError("Place this probe beside the original P1_CHECKPOINT_002_REPAIR.py.")
    body = path.read_bytes()
    if hashlib.sha256(body).hexdigest() != REPAIR_SHA:
        raise ValueError("Original repair helper hash differs; it was not executed.")
    module = types.ModuleType("checkpoint002_pinned_repair")
    module.__file__ = str(path)
    exec(compile(body, str(path), "exec"), module.__dict__)
    return module


class ProbeGit:
    def __init__(self, module):
        self.module = module
        self.deadline = time.monotonic() + TOTAL_SECONDS
        self.calls = 0
        self.phase = "local inspection"
        self.failures = []

    def run(self, *args):
        if not args or args[0] not in READ_COMMANDS:
            raise ValueError("Probe refused a command outside its read-only command set.")
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise RuntimeError("Probe reached its total time limit before git " + " ".join(args))
        env = os.environ.copy()
        for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
                    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"):
            env.pop(key, None)
        env["GIT_TERMINAL_PROMPT"] = "0"
        env["GIT_OPTIONAL_LOCKS"] = "0"
        argv = ["git", "--no-optional-locks", "-C", str(self.module.ROOT), *args]
        started = time.monotonic()
        self.calls += 1
        p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             env=env, start_new_session=True)
        timed_out = False
        cleanup = None
        try:
            out, err = p.communicate(timeout=min(COMMAND_SECONDS, remaining))
        except subprocess.TimeoutExpired as first:
            timed_out = True
            # Kill only this newly created process group. Detached descendants
            # may escape that group; this is not an isolation guarantee.
            for sig in (signal.SIGTERM, signal.SIGKILL):
                try:
                    os.killpg(p.pid, sig)
                except ProcessLookupError:
                    pass
                try:
                    out, err = p.communicate(timeout=2)
                    cleanup = "owned process reaped; captured pipes closed"
                    break
                except subprocess.TimeoutExpired as later:
                    first = later
            else:
                out, err = first.output or b"", first.stderr or b""
                cleanup = "cleanup incomplete; detached descendants not inspected"
                p.stdout.close()
                p.stderr.close()
        elapsed = round(time.monotonic() - started, 3)
        if timed_out or p.returncode:
            self.failures.append({"ts": datetime.now(timezone.utc).isoformat(),
                "phase": self.phase, "command": list(args), "elapsed_seconds": elapsed,
                "timed_out": timed_out, "exit_code": p.returncode, "cleanup": cleanup,
                "stdout": out.decode(errors="replace"), "stderr": err.decode(errors="replace")})
            kind = "TIMEOUT" if timed_out else "EXIT " + str(p.returncode)
            print(kind + ": git " + " ".join(args), flush=True)
            print("Phase:", self.phase, "| elapsed seconds:", elapsed, flush=True)
            if cleanup:
                print("Cleanup:", cleanup, flush=True)
            # Allowlisted signatures convey common causes without printing raw
            # output, URLs from local configuration, headers or credentials.
            signatures = ("Could not resolve host", "Could not resolve proxy",
                          "Failed to connect", "Connection timed out",
                          "Authentication failed", "terminal prompts disabled",
                          "could not read Username", "could not read Password",
                          "SSL certificate problem", "Permission denied",
                          "Repository not found", "Could not read from remote repository")
            detected = [s for s in signatures if s.lower() in err.decode(errors="replace").lower()]
            print("Recognized error signatures:", json.dumps(detected), flush=True)
            raise RuntimeError("Diagnostic stopped at the named command; no repair or push was attempted.")
        return out

    def text(self, *args):
        return self.run(*args).decode("utf-8").strip()

    def save_failures(self):
        if not self.failures:
            return
        path = self.module.path_for(ERROR_LOG)
        flags = os.O_WRONLY | os.O_APPEND | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
        with os.fdopen(os.open(path, flags, 0o600), "a", encoding="utf-8") as handle:
            for failure in self.failures:
                handle.write(json.dumps(failure) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        print("Raw failure output saved locally to", ERROR_LOG + ". Do not paste that log.", flush=True)


def diagnose(module):
    git = ProbeGit(module)
    started = time.monotonic()
    print("START: verify present local state using the unchanged repair checks.", flush=True)
    try:
        head, repaired = module.inspect(git)
        print("Verified current local commit:", head, flush=True)
        print("Verified correction commit already exists:", json.dumps(repaired), flush=True)
        print("All original working checkpoint bytes match their declared hashes.", flush=True)
        print("Local inspection seconds:", round(time.monotonic() - started, 3),
              "| Git commands:", git.calls, flush=True)
        git.phase = "read remote main"
        print("START: git ls-remote --refs origin refs/heads/main (at most 60 seconds).", flush=True)
        remote = module.remote_head(git)
        if len(remote) != 40 or any(c not in "0123456789abcdef" for c in remote):
            raise ValueError("Remote returned an invalid commit identifier; raw output withheld.")
        print("Observed remote main:", remote, flush=True)
        print("Remote is an expected checkpoint state:",
              json.dumps(remote in {module.BASE, module.BAD_HEAD, head}), flush=True)
        print("DONE: both checks completed. This does not establish that commit or push will work.", flush=True)
    finally:
        git.save_failures()


def main():
    if len(sys.argv) != 1:
        raise ValueError("This probe takes no options and cannot repair or push.")
    if os.name != "posix":
        raise ValueError("Run this probe in the same WSL terminal as the repair.")
    original = Path(__file__).resolve().with_name("P1_CHECKPOINT_002_REPAIR.py")
    diagnose(load_repair(original))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, TypeError, UnicodeError) as error:
        print("STOP:", error, file=sys.stderr, flush=True)
        sys.exit(1)
