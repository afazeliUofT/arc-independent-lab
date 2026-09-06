# Checkpoint 002 transfer: method and present verification scope

Date: **2026-09-06**. This is a new human execution aid, not an unattended supervisor, independent reviewer, scientific verifier or change to checkpoint 001's transfer script. Its public target is [afazeliUofT/arc-independent-lab](https://github.com/afazeliUofT/arc-independent-lab), URL supplied by the human and verified separately by the principal investigator. No public write was attempted in these helper checks.

The new Python-standard-library template is `scripts/checkpoint_update.py`, SHA-256 `87457aef2a7ab6dc9560839c3edf37c9431761885a31814dbdc1e7bc2bf4f795`. Its `PAYLOAD` remains a build-time placeholder. The delivery copy will embed base64-encoded, zlib-compressed JSON containing the pinned base commit and explicit old/new file hashes and new bytes. The principal investigator assembles that actual package after the scientific documents and state are finalized.

## Human operation

Running the generated file without a flag prints the exact target, repository, base commit, file transitions and human answer. It does not inspect or alter a local repository and makes no network call. `--apply-and-push` is the human's explicit execution instruction; it targets only `Path.home()/ARC_Independent_Lab`.

The fixed answer is appended only during execution, and only to the package's exact unanswered `state/ESCALATION.md`. It authorizes continuing Phase 1 after independent GitHub readback of checkpoint 002. It does not approve the diagnosis or authorize Phase 2. The script accepts the resulting answered bytes on a retry and does not append another answer.

## Transfer controls

Before payload writes, the script reads current project state, requires Phase 1, checks the contained ordinary `.git` directory, exact repository root, main branch and exactly the fixed origin fetch/push URLs. It rejects unrelated tracked or staged changes, unmerged index entries, unknown staged payload bytes and staged deletions of expected existing payload files.

It validates embedded hashes and paths, rejects file/parent collisions, traverses destination components to reject symlinks and special files, and checks every payload file against known old or new content before installing any. New files must be absent or already have the exact new bytes. Existing paths must match their pinned old hash or the new payload. Every old hash is also checked against the pinned base commit.

The only accepted local histories are the pinned base and its direct child containing the complete answered payload plus the checkpoint-002 manifest. That child may change only payload paths and the helper's own error log. The script inspects remote main, fetches it without checkout or merge, and requires both remote observations to agree with the pinned base or the accepted local child.

Known overwritten contents are backed up under ignored `delivery/checkpoint002_backups/`. Replacements are written and flushed to temporary files there and atomically moved into place. The script rechecks the accepted snapshot after network inspection and verifies installed bytes. It stages only explicit payload paths and, when creating the checkpoint commit, its own error log. The commit uses the per-command programme identity and the requested message; no Git configuration is changed. Pushes are ordinary non-force pushes, followed by remote ref readback. Independent principal-investigator readback remains required for the durability claim.

Real nonzero Git exits append the actual captured stdout/stderr, command and exit code to `state/handoff_002_errors.jsonl`. Predicate checks use commands that ordinarily return success rather than treating expected nonzero results as tool failures. An error after the checkpoint commit, such as a failed push, leaves a new local log entry. Retry pushes the existing verified child commit and preserves that later log entry for the next checkpoint: it neither amends history nor creates a duplicate checkpoint commit merely to include the failed-push log.

## Checks performed here and what they do not establish

The local fixture results are `evidence/CHECKPOINT_UPDATE_HELPER_CHECKS_2026-09-06.json`, SHA-256 `ec78ab0a78a8f2ec850bf41ea8d55e5a32af5635f06ca6a461cd969c5d934b7e`. The source was compiled before execution. A temporary fixture inside the lab's ignored delivery directory exercised read-only preflight, conflicting old/new destination rejection, backed-up installation, repeat installation with a single answer, destination-symlink rejection, unsafe path and file/parent collision rejection, embedded-hash rejection, and the default inspection-only entry point. The fixture was removed after checks. These checks made no Git or network operations.

They therefore **do not verify** the final package, a real user's repository, remote divergence, index conflicts, commit retry or push retry. The principal investigator will test the assembled payload against a local bare repository before delivery. That test can import the module and substitute the fixture path through `canonical_target` and a local remote through `REMOTE`; the distributed source retains the fixed real target and URL. Local-bare success will still not establish laptop execution or actual GitHub durability.

The helper assumes an ordinary locally controlled repository and no concurrent editor changing files during installation. It rechecks bytes but does not provide an enforced boundary against a concurrent malicious process, arbitrary configured Git hooks, sudden loss of the entire filesystem, or mutation by the agent. Atomic file replacement and preserved backups support retry; they are not claims of reviewer isolation or multi-file transactional storage.


## Append-only pre-delivery correction: staged deletion on retry, 2026-09-06

The original helper source pinned above (`87457aef2a7ab6dc9560839c3edf37c9431761885a31814dbdc1e7bc2bf4f795`) rejected absent index entries for files present in the base commit, but its staged-deletion protection was incomplete. For a file newly added by checkpoint 002, `old_sha256` remains null even after the checkpoint has been committed. On a direct-child retry, `git rm --cached -- scripts/run_reproduction.py` with the expected working bytes retained was accepted by repository preflight. The later payload staging would therefore undo that intentional index deletion. This is a failed preflight expectation, not a scientific result.

The minimal revision explicitly checks `git diff --cached --name-only --diff-filter=D --no-renames -z` and refuses any staged deletion before staging or payload installation. The same synthetic case is now rejected with its index and working bytes intact. The synthetic index was restored to its original clean state after each check; no original scientific source, configuration or raw artifact was changed. Root's initial broader suspicion that all absent index entries were unchecked was narrowed after inspecting the pinned source: the defect concerns newly added payload files on retry.

The superseding template SHA-256 is **`fa2053151ce56a21965ed3d83d99eaba2868680079162c00e8d33e3272251262`**. The exact initial failure, corrected observation, source hashes, harness source and limits are preserved in `evidence/CHECKPOINT_UPDATE_INDEX_REGRESSION_2026-09-06.json`, SHA-256 `0883f3c442b9b162ed1604b4b74d2d3406c42c8481fcf80adde40bd05bb9a577`. Earlier helper-check and local-roundtrip receipts remain unchanged and describe their original source. This regression verifies the targeted refusal; it does not itself re-run publication or establish real GitHub durability.
