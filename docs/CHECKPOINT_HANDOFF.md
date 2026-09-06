# First checkpoint handoff

The downloadable `P1_CHECKPOINT_001.py` is a self-contained copy of `scripts/checkpoint_transfer.py` with a compressed, hash-checked file payload. Running it without arguments only lists the exact files and hashes. It installs no packages and uses Python's standard library and existing git.

The action flag `--apply-and-push` means: install this exact checkpoint under your `~/ARC_Independent_Lab/`; append the displayed `## ANSWER` to the escalation file as your response; commit using the programme identity; and push to the exact public repository you created. It does not approve the unfinished diagnosis or start Phase 2. The script uses `ARC Independent Lab <arc-independent-lab@localhost>` for the commit only, without changing your git configuration.

It verifies payload hashes and refuses conflicting files, symlink destinations, unrelated staged changes, a different git remote, or divergent remote history. It does not delete files, overwrite work, merge, force-push, create credentials or modify the other programme. Repeating a successful handoff is idempotent. If authentication is unavailable, it preserves local files/commit and reports the actual git error; resolve authentication through your normal supported credential manager, then rerun. Do not send a token.

Run these commands in WSL. The prompt avoids guessing where the browser saved the download:

```bash
read -r -p "Full WSL path to downloaded P1_CHECKPOINT_001.py: " ARC_CHECKPOINT_FILE
python3 "$ARC_CHECKPOINT_FILE"
python3 "$ARC_CHECKPOINT_FILE" --apply-and-push
```

The first Python invocation is inspection. The second performs the explained action. The script prints the resulting commit. Its successful push is followed by the agent's independent GitHub readback; until then, state remains `awaiting_remote_verification`.

The payload includes the governing instruction pack, accepted amendments, state/ledger, source notes, working diagnosis, paper batch and transfer source. It contains no publisher full texts, environment, credentials, or reproduction results. The reproduction has not yet been run.

`state/CHECKPOINT_001.json` is the list for subsequent byte verification. Its scope excludes itself (to avoid a self-hash cycle) and `state/ESCALATION.md` (which receives your answer). The answer is checked separately for provenance and scope. Fetch files at a pinned commit; checking current HEAD after later work would verify a different checkpoint.
