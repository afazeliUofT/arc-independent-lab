# Checkpoint 003 local handoff method

2026-09-06. This is a transfer helper and a tested template, not a completed
checkpoint package. The principal investigator must finish the scientific files,
make the explicit payload selection, and verify the assembled ZIP before giving
the human final download hashes and commands.

`scripts/checkpoint003_handoff.py` never commits, pushes, fetches, or authenticates.
It uses Python's standard library and the existing Git. Its fixed laptop target
is `~/ARC_Independent_Lab`, with main based on the verified correction commit
`6c69eca83cadd0346d85110af470a61f3f075d5d`. The expected origin is
`https://github.com/afazeliUofT/arc-independent-lab.git`.

The helper's SHA-256 is
`f2e63214eeddf37150a72364fa5174d40429102d4ffae7bbf9bab3ced19b9a58`.
Previously delivered helpers remain unchanged.

## Package contract

The ZIP has exactly `HANDOFF.json` and one `files/<relative-path>` member for each
declared addition or replacement. It has no directory entries. `HANDOFF.json`
contains exactly:

```json
{
  "checkpoint_id": "P1_CHECKPOINT_003",
  "base_commit": "6c69eca83cadd0346d85110af470a61f3f075d5d",
  "files": {
    "relative/path": {
      "old_sha256": null,
      "sha256": "64 lowercase hexadecimal characters",
      "mode": "100644"
    }
  }
}
```

`old_sha256` is null only when that path is absent from the pinned base; otherwise
it is the SHA-256 of the actual base blob. The new hash covers the exact ZIP member
bytes. `100755` is also supported for new executable files; existing executable
modes must stay unchanged. There are no deletions. This handoff manifest is a
transport manifest, separate from the scientific `state/CHECKPOINT_003.json` if
one is included. The complete ZIP gets its own independently supplied SHA-256.

Select repository documents, code and evidence explicitly. Do not indiscriminately
package every untracked path. Downloaded papers, source extractions, temporary
fixtures and backups are excluded. The helper rejects delivery/private-source
paths, PDFs and `IDEAS_PARKED.md`; it never reads parked ideas. The original
checkpoint artifacts need no replacement. The exact existing artifact rule must
remain:

```gitattributes
# Preserve the exact bytes of scientific run artifacts.
/artifacts/** -text
```

## Human sequence

The final handoff supplies the helper, ZIP and both file hashes together. With the
actual ZIP hash substituted, the available commands are:

```bash
python3 -u "$ARC_CHECKPOINT_HELPER" "$ARC_CHECKPOINT_ZIP" --sha256 ACTUAL_ZIP_SHA256
python3 -u "$ARC_CHECKPOINT_HELPER" "$ARC_CHECKPOINT_ZIP" --sha256 ACTUAL_ZIP_SHA256 --apply
python3 -u "$ARC_CHECKPOINT_HELPER" "$ARC_CHECKPOINT_ZIP" --sha256 ACTUAL_ZIP_SHA256 --verify
```

The first invocation inspects the ZIP and local repository. The second backs up
replaced bytes and the original index, installs known transitions, stages only
listed files, then measures the actual staged blob SHA-256 values. The third
requires the complete intended working bytes and index. A successful inspection
makes no changes or network calls. No command in this helper is a scientific gate
approval or an answer written on the human's behalf.

After reviewing the staged diff and passing verification, the human runs an
ordinary foreground `git commit` using the final handoff's commit message. The
helper is then run with `--verify` again: a new HEAD must be the base's direct child
with exactly the entire intended tree. Only after that check, and confirming HEAD
is no longer the base commit, should the human run an ordinary foreground push.
The final commands must gate each step on success. Do not push merely because a
preceding commit command was attempted.

A failed push does not require another commit. Repeat verification of the existing
direct child and push that verified commit in the foreground. This leaves any
authentication prompt and Git's actual errors visible. The principal investigator
still reads the resulting public commit and its bytes before claiming durability.

## Refusals, retry and limits

The helper compares old hashes to the pinned base, rejects unknown staged bytes,
staged deletions, unrelated tracked edits, conflicting untracked destinations,
symlinks, and an unexpected branch, root, origin or history. Unrelated untracked
files are left alone. Payload files already holding the exact new bytes are
accepted, so an interrupted installation can resume. A completed exact child
commit is accepted without changing files or staging anything.

If Git transforms a payload during staging, verification stops before any commit.
The delivered worktree bytes and a timestamped pre-stage index backup remain in
`delivery/checkpoint003_backups/`. Do not commit that failed index, and do not
blindly overwrite it from a backup: report the exact error so the conflicting
attribute or conversion and current state can be diagnosed. Ordinary retry rejects
unknown transformed staged bytes. This is deliberate preservation of unresolved
state, not an automatic attempt to repair Git configuration.

Every failed Git subprocess prints a structured record containing the exact
command, exit code, stdout and stderr. The human should retain the terminal output
for the programme error ledger; the helper does not append an error log behind an
inspection command. Application failures can leave a partial known installation,
never an assistant-created commit. Avoid concurrent edits while applying. These
checks do not enforce reviewer isolation or defend against a malicious concurrent
process, configured Git hooks, or total loss of the laptop filesystem.

## Measured checks and boundaries

`evidence/CHECKPOINT_003_HANDOFF_VERIFICATION.json`, SHA-256
`2bdb5a5549c9ea2d464a2aa0c7527bd6b05ee93e450b6a4327870df75329a7f8`,
records contained synthetic-repository checks. The preserved test source is
`evidence/CHECKPOINT_003_HANDOFF_TEST_SOURCE.py`, SHA-256
`54df562c52262d5ab42d81b181003f343599741d405c837c977cdff453a6163e`.

The checks exercised inspection without index writes, partial installation and
repeat application, exact CRLF artifact staging under `core.autocrlf=input`,
completed-child retry, rejection of a staged deletion after commit, unrelated
working edits, hidden staged edits, an untracked collision, rejection of a text
payload normalized by Git, preservation after that refusal, the ZIP manifest and
a wrong ZIP hash. No Git subprocess failed; expected helper refusals are recorded
with their actual messages. Fixture commits were confined to temporary test
repositories. The real lab repository was neither committed nor pushed.

The test helper was imported with its base constant set to each synthetic fixture's
base; the shipped source retains the real fixed base and laptop target. These
checks establish the tested local behavior. They do not verify the final scientific
ZIP, laptop execution, authentication, publication or scientific correctness.

## Actual published-base rehearsal

The PI also staged the scientific/recovery payload twice in a contained clone of the real published base with `core.autocrlf=input`. Every intended staged blob matched, every untouched base entry retained its mode/blob identity, and the real lab HEAD/index stayed unchanged. Receipt: `evidence/CHECKPOINT_003_REAL_BASE_VERIFICATION.json`, SHA-256 `deeecf3cec83723314da793eff37ed3ff779268f80ac7458401e9724c818ca14`. Finalization subsequently adds only publication metadata, this receipt and state/ledger records. The final ZIP hash is supplied outside the ZIP to avoid self-reference.
