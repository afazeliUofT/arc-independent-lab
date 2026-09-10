# Finite review correction027: retain direct broker access

Prepared 2026-09-10. This request is unsigned. Sol Max and existing host restrictions remain unchanged.

## Observed failure and concrete correction

The026 report is the requested diagnostic. Its pins match published checkpoint1380057c0e136446fb9ec8cc35ffa883c2e5aa78. It records a thread-bound Code Mode unavailable/fail-closed warning, then the local controller stopping before broker access or science. The original is artifacts/P3_WARNING_CAPTURE_OBSERVATIONS/20260910_027/REPORT.json, SHA-256 ccbfa9a5d6e356fa62a11499ad68dd3740159b96bffb106880b2295fdd871043. Its embedded observation matches the declared separate SESSION hash; the actual laptop file must still be verified at launch and never reconstructed.

The pinned source explicitly supports direct-only functions under CodeModeOnly. The unavailable executor does not disable these separate functions, and the warning does not itself abort a turn. See artifacts/P3_DIRECT_BROKER_SOURCE/20260910_027/FINDINGS.md and its source manifest for URL/access-date citations. The upstream direct-only test was read, not executed here. Actual Sol use of the broker remains unverified.

New027 acknowledges at most one exact source-derived disabled-host/fail-closed notice, bound to the active thread after the sole turn request is sent and the unchanged restrictive controls and Sol Max selection are verified. Other reasons, extra text, malformed/unbound notices and duplicates stop. Code Mode remains disabled. This changes local notice handling; it does not install a host, change model metadata, grant a tool, or attest the native tool inventory. The opaque internal026 reason was not retained: exact disabled-host wording is a source-derived expectation, not recovered verbatim text.

Six native starts and three sent turns have exhausted the approved6/3 ceiling. This request reserves at most two more starts and two more turns, raising cumulative ceilings to8/5. A sent turn counts even without output; backend usage/charge is unknown. First, a fresh synthetic direct broker read and real out-of-bounds refusal must succeed, with cleanup and unchanged protected inputs. Only then may a separately fresh scientific reviewer read the installed frozen paper packet. Existing stage limits remain10minutes synthetic and60minutes scientific, including cleanup. No automatic retry, spending or unattended continuation is authorized. Verified terminal receipts are reused; partial/changed attempts are preserved and refused.

The exact scope is configs/P3_FINITE_REVIEW_SCOPE_027.json, SHA-256 a69877f8bbeddfd4b638943d850e73a8eb2e978d9d1ce08600484d6c5a0df7a9. The ZIP contains implementation, source audit, offline validation and original026 report. No027 native/model operation has been performed by the PI. Scientific inputs, verifiers and prior attempts remain unchanged.

## Why this needs an answer

03_AUTONOMY_SPEC.md section6 item10 requires escalation at a budget ceiling; item16 covers a change to the control surface. This combines both in one concrete request. The old024 answer cannot authorize the new ceiling or exact notice policy. Already approved model and host access are not being requested again.

## How the funder answers

Record one actual section in state/ESCALATION.md beginning with the literal heading `## ANSWER`. Its only nonblank contents must be `APPROVE_P3_FINITE_REVIEW_027_CORRECTION` and `scope_sha256: a69877f8bbeddfd4b638943d850e73a8eb2e978d9d1ce08600484d6c5a0df7a9` on separate lines. No extra answer prose follows.

For convenience, explicitly running the delivered publication wrapper with `--approve-correction` is the funder's authorization of this exact request. It records that answer, updates its checkpoint inventory, commits and pushes. The PI has not applied the flag to the working repository. No separate GitHub edit or chat confirmation is needed. Without the flag, the wrapper only inspects. Publication cannot start a model.

After successful publication, separately run scripts/p3_finite_review_027.py with `--run-attended-review`. Attach REPORT.json, plus science_output/REVIEW_VERDICT.json only if present, from delivery/P3_FINITE_REVIEW_027. A stopped synthetic stage creates no science directory/verdict. Preserve earlier results; do not reconstruct missing files or rerun old checkpoints.

If declined, native review remains stopped without a scientific verdict. The PI preserves the evidence and continues only authorized work. Another failed direct broker attempt calls for reassessment; it does not authorize enabling the execution host or resetting counters.

## ANSWER
APPROVE_P3_FINITE_REVIEW_027_CORRECTION
scope_sha256: a69877f8bbeddfd4b638943d850e73a8eb2e978d9d1ce08600484d6c5a0df7a9
