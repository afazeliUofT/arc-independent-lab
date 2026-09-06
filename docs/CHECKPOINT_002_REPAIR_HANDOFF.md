# Checkpoint 002: correct Git's transformed CSV and publish

Date: 2026-09-06. This repairs publication of existing Phase 1 evidence. It neither changes the scientific result nor approves the unfinished diagnosis.

## Confirmed cause

The user-run diagnostic confirms that the original CSV survives intact in the working directory, while Git's index and local checkpoint commit contain its LF-normalized form. The user's global `core.autocrlf=input` setting explains the conversion; the effective CSV text, filter, encoding and related attributes were unspecified. All other declared checkpoint bytes matched. The factual report is preserved in `evidence/CHECKPOINT_002_LAPTOP_DIAGNOSTIC_2026-09-06.json`, SHA-256 `f168ac553d2ac11d1b900ef7da7cc60a5c535bf0ec046f92b858506dcd8ee73c`.

The assistant's original handoff tests missed this Git configuration. The hash check caught the altered committed bytes before push. A clean `git status` was insufficient evidence of byte preservation.

## What running the repair does

Download `P1_CHECKPOINT_002_REPAIR.py`. It is a new, self-contained helper; the shipped checkpoint installers remain unchanged.

```bash
read -r -p "Full WSL path to downloaded P1_CHECKPOINT_002_REPAIR.py: " ARC_REPAIR_FILE
python3 "$ARC_REPAIR_FILE"
python3 "$ARC_REPAIR_FILE" --repair-and-push
```

The first invocation inspects your current project and prints the action. It makes no changes or network calls. The second:

1. Requires the measured local commit, or its already verified correction child, and the exact authorized repository. Unknown file contents, staged work, conversion attributes or remote history stop it.
2. Adds a repository rule that disables line-ending normalization for run artifacts. Your global Git setting remains unchanged. An unfamiliar existing attribute file is never overwritten.
3. Re-stages only the intact CSV under that rule. It does not rewrite the raw CSV or change its pinned hash. Every original checkpoint file is checked in the index before committing.
4. Adds a correction commit and verifies its complete changed-file set and all original checkpoint hashes. The existing local commit remains in history.
5. Pushes the verified commit without force and checks the remote ref. The principal investigator will independently read back actual GitHub file bytes afterward.

This fixes the Git representation of the original evidence; it does not rerun the scientific experiment. Git's `-text` attribute disables line-ending normalization, and path-restricted `git add --renormalize` reprocesses the specified tracked file using the new rule. Other transformations are checked separately. [Git attributes documentation](https://git-scm.com/docs/gitattributes), [Git add documentation](https://git-scm.com/docs/git-add), accessed 2026-09-06; local behavior was reproduced in the recorded fixtures.

## Retries and limits

If interrupted after the rule or staging step, rerun this repair once the reported cause is resolved. If the correction commit already exists, retry verifies and pushes that same commit. A completed push is safe to repeat. Do not rerun `P1_CHECKPOINT_002.py --apply-and-push`: that older helper deliberately expects a different history shape.

No reset, amend, force push, global setting change or hash relaxation occurs. Actual Git failures are recorded separately in `state/handoff_002_repair_errors.jsonl`; the log is retained for the next checkpoint rather than silently added to this narrowly scoped correction. As with the earlier helper, avoid editing this project while applying the repair. The checks support normal interruption recovery, not enforced isolation from concurrent hostile processes.

The original scoped human continuation answer is already part of the local checkpoint and is included in the byte checks. It need not be written again. This repair does not grant Phase 2 approval. After success, return the printed commit so the principal investigator can verify publication and resume Phase 1.

Recovery evidence, ledger entries and state written in the hosted workspace after the frozen checkpoint package must be retained and included at the next natural checkpoint. Adopting the corrected human commit must not reset away those additions.

## Completed local verification

The delivered helper has SHA-256 `2d024c8cf2c042885414f53275bea836094a8ab4dd7d77da876abb83b703f9de` and is byte-identical to the source tested in `evidence/CHECKPOINT_002_REPAIR_VERIFICATION.json`, SHA-256 `5d1ba6955e0b7dbf33a05c81678a6baab08c7f951d1833a4f126e57a6756bc71`. Local Git tests verified the corrected remote blobs, preservation of the original commit, successful retries after staging and a rejected push, refusal of the tested conflicts, and exact artifact bytes after fresh checkouts. These are local implementation checks, not an independent reviewer verdict or proof that the laptop repair has run. Detailed methods and limits: `evidence/CHECKPOINT_002_REPAIR_METHODS.md`.
