# Checkpoint 002: localize the repair timeout

Date and access date: 2026-09-06. Publication recovery only; Phase 1 remains incomplete.

## Evidence and correction

The first read-only repair inspection passed at local commit `6b06dc1120b22d59ae7c9d550feb3f124ff656fa`. The subsequent action-mode run printed the same initial inspection and then the generic timeout. It did not print the failed Git command or a post-timeout HEAD. The supplied text therefore does **not** establish whether the correction commit now exists locally.

Both an independent Git transport read and the GitHub connector observed remote main still at `189f424e5cc9588d9774fd58850c44c9b182f813`. Source: [repository ref](https://api.github.com/repos/afazeliUofT/arc-independent-lab/git/ref/heads/main), accessed 2026-09-06. Preserved evidence: `evidence/CHECKPOINT_002_REPAIR_TIMEOUT_2026-09-06.json`, SHA-256 `80f145ddc5279ccc33387db0fc5bbf66df398e71cace30bb09be62b7dc59d020`.

The old helper sets a per-command cap of the lesser of 60 seconds and its remaining 300-second budget. After the initial print it can perform remote reads, local validations, staging, commit and push without further progress output. Its timeout handler discards the command name and partial output. That missing observability is our implementation defect. Network, authentication, signing/hooks and local delays remain hypotheses. Local fixture tests of rejected pushes did not test hangs or real GitHub authentication.

## One human action

Download `P1_CHECKPOINT_002_TIMEOUT_PROBE.py` beside the existing, unchanged `P1_CHECKPOINT_002_REPAIR.py` in your WSL home directory. Run:

```bash
python3 -u ~/P1_CHECKPOINT_002_TIMEOUT_PROBE.py
```

Return only its terminal output. Do not paste the raw local error log or credentials.

The probe checks the original repair helper's exact SHA before loading it, then calls its unchanged local inspection predicates. It reports whether the correction commit already exists and whether all original checkpoint bytes still match. It then makes one bounded `git ls-remote` call against the existing authorized origin and prints the observed remote commit or the named failing command. It cannot repair, stage, commit, push or change configuration; it does not retry automatically.

On failure it saves raw stdout/stderr in a private local error log inside Git metadata, outside ordinary committed content. Terminal output includes only fixed command arguments, timings, status and allowlisted error signatures. This is why the terminal report is requested and the raw log is not. A timeout terminates only the newly launched process group; detached descendants are not claimed to be isolated or contained. The subprocess launch uses the original helper's environment sanitation and disables Git terminal prompting as before. Git credential configuration, SSL settings, proxies and hooks are not changed.

## How the result changes the next action

- A failed local inspection supplies the current failed guard or timed-out local command. Resolve that measured condition before mutation.
- A remote-read timeout or failure narrows the problem to that read under the measured environment. Use its named error signature; do not equate all such failures with authentication.
- Successful local and remote reads determine the safe starting state for a narrowly instrumented continuation. They do not establish that commit or push will work. The original uninstrumented action helper should not be repeated blindly.
- If the remote has advanced, independently retrieve and verify actual checkpoint bytes and correction history before adopting it. Preserve hosted recovery overlays when reconciling the working copy.

The existing human continuation answer remains valid and is not requested again. The durability block clears only after publication and independent readback. No phase approval is implied by troubleshooting output.

## Engineering references

[Python subprocess documentation](https://docs.python.org/3/library/subprocess.html), accessed 2026-09-06, distinguishes timeout behavior for `run` and `Popen.communicate`; the new probe provides explicit bounded process cleanup. [Git environment documentation](https://git-scm.com/docs/git), accessed 2026-09-06, documents `GIT_TERMINAL_PROMPT`. These references explain implementation choices; neither diagnoses the user's unseen stalled process.

## Completed targeted verification

The delivered probe is byte-identical to `scripts/checkpoint002_timeout_probe.py`, SHA-256 `514182c02a44b532b5828c2e2b0565d963ff94ac889ed044bdca11990dcb1b91`. All eight targeted cases passed: healthy unrepaired/repaired states preserve working files, index, HEAD, configuration and remote; source hash and unrelated staged-change guards remain effective; a push command is refused; two distinct hanging-process/held-pipe cases name the failed command and clean up the tested owned processes; injected private error data remains outside terminal output. Receipt: `evidence/CHECKPOINT_002_TIMEOUT_PROBE_VERIFICATION.json`, SHA-256 `c43ff0ce91f54553992200485e205bd7c1a42c887273f29e93b9d23ec96f495a`. These are local fixture checks under shared tools and filesystem, not independent review or a diagnosis of the laptop.

The test harness initially recorded the command-log hash before its final successful version query appended a row. The original receipt was preserved and an explicit correction records the complete-log hash: `evidence/CHECKPOINT_002_TIMEOUT_PROBE_COMMAND_LOG_HASH_CORRECTION.json`, SHA-256 `9aa0da131bcbe83016f8946d6224797ca517f12185ebc0a33ac42535912bcb32`. The recorded old hash matches exactly the prefix before that single final row; test outcomes did not change.
