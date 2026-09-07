# P3.8 — supported native sign-in exception

Date: 2026-09-07. No sign-in, new model call or scientific verdict has been executed.

The account observation is complete and found no available cached account in the authorized reviewer namespace. The next scientific dependency is a genuinely separate, restricted fresh-context review of the frozen novelty audit. Repeating the passing setup probes will not resolve account access.

I request one human-operated native ChatGPT browser sign-in through the existing installed client, under the exact scope in `configs/GATE0_SIGNIN_SCOPE_015.json`:

SHA-256 `6020d46ae6818f6c15341a7074ea4f7306b3764d8c64a92d0dcce745ed1c7ccd`.

Why permission is required: `04_RESOURCES_AND_SETUP.md` section 6 and `03_AUTONOMY_SPEC.md` section 6, reasons 1 and 5, require an explicit exception for native credential-file storage and outside-project effects. The observed file backend writes `~/.codex/auth.json`; native logs/support files and browser session state can also change. Your existing full-laptop permission and request to minimize approvals do not explicitly remove that credential-storage rule. The guard refuses an existing auth file without reading it, changed provenance, or an occupied callback port. No credential copying, backend/policy/home change, API-key login, spending, model invocation or unattended run is included.

The concrete command, native cleanup/token-storage effects, safeguards, source evidence and report instructions are prepared in `docs/GATE0_HUMAN_SIGNIN_015.md`. This is a decision on a reviewable action, not a request to approve unspecified setup.

**Answer by appending a section beginning `## ANSWER` to this same file, committing and pushing it.** To approve, follow that heading with a standalone line `APPROVE_G0_SIGNIN_015`, then a standalone line `scope_sha256: 6020d46ae6818f6c15341a7074ea4f7306b3764d8c64a92d0dcce745ed1c7ccd`. A copyable answer is provided in the sign-in instructions. The request itself contains no answer section.

Then pull that answer and run the guarded sign-in command in the linked instructions. The script checks this recorded approval. Share only its `REPORT.json`.

To decline, append `## ANSWER` followed by `DECLINE_G0_SIGNIN_015`. This access route will be suspended; the audit remains provisional and preserved. Any qualified answer will be read before choosing a different action. No permission to grade our own work is inferred.
