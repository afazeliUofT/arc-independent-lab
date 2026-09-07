# Retry the command observation with explicit runtime visibility

Prepared 2026-09-07 after the first actual WSL report. This supersedes the executable-visibility assumption in `docs/GATE0_REVIEWER_BOUNDARY_CHECK.md`; the original child tests and interpretation requirements are preserved.

## Why this retry

The first sandbox launch could not execute its own installed Codex binary. The verified observation and limits are in `reports/GATE0_BOUNDARY_OBSERVATION_001.md`. A favorable outcome is not assumed.

The revised driver verifies the exact version-specific executable identified in the actual error. It records file metadata and a content hash, runs that exact binary's version check, and uses the verified path for the sandbox command. It adds read permission only for that executable file. No read permission is added for its parent directories as whole trees. The original PATH launcher version remains a compatibility check; a wrapper path is not silently treated as the standalone binary.

The requested profile still denies the filesystem by default, grants minimal runtime and synthetic-packet reads, disables networking, and retains managed restrictions. The driver does not edit settings or try broader profiles after a failure. Exact binary inspection is the additional host read; no credential or configuration contents are collected.

## Run and return

Use the checkpoint010 publication-and-test instructions. They install the revised source before execution, keeping the failed observation and its original source durably traceable. The WSL command remains:

```bash
python3 -u "$HOME/ARC_Independent_Lab/scripts/gate0_reviewer_boundary_probe.py"
```

Every attempt uses a fresh directory. Return the resulting `REPORT.json`, including an unsuccessful or incomplete result. If the driver stops before producing a report, return the printed nonsecret error. No inventory rerun or scientific approval is needed.

Progress is saved separately as `IN_PROGRESS.json`. The final `REPORT.json` is created exclusively once, flushed and checked against its serialized bytes before its path and hash are printed. The driver will not replace an existing final report. This file protocol does not substitute for GitHub publication.

## What the result can establish

The unchanged synthetic child must actually start, read its allowed canary, complete every test and emit its completion event. The outside driver must confirm the protected fixture and runtime executable remain unchanged. A launch error or failed preflight is not evidence of protection. The connection result concerns only the tested IPv4 loopback route.

Even successful command restrictions do not establish complete reviewer isolation. Model context, other tools and connectors, evidence integrity and the verdict channel still require their own enforced configuration. This retry calls no model, reviewer or app-server, and cannot measure subscription allowance.

The delivered v2 driver SHA-256 is `e8b6e4c52dfd81fc8b797ebb699297975a7026472f5c43de6e73267a31100e41`. Hosted validation, including preserved collection discrepancies, is recorded in `evidence/GATE0_BOUNDARY_V2_HARNESS_VALIDATION.json`, SHA-256 `b5d49dd6aaffd2041db00d7cdb4795b8bd92762647c6b4059fb9001735bd1bd3`. These are simulated wrapper/runtime checks, not measurements of the laptop sandbox.
