# Checkpoint038 packaging correction: one ZIP from WSL home

Date: 2026-09-11. This corrects the handoff for the completed038 source-integration step. It creates no new scientific checkpoint, changes no frozen operation or method assessment, and starts no independent review.

The previous ZIP required the user to extract it and open WSL in the extracted folder. That did not meet the now-explicit handoff requirement. The replacement is `ARC_Independent_Lab_038_HOME.zip`, containing both original PDFs, the original pinned public reading packet and unchanged staging helper, plus a Downloads bootstrap and an automatic installation launcher.

## Single command behavior

The published command is one Python here-document pasted at WSL home. Release tooling inserts the complete archive SHA-256 into the bootstrap template. The command reads the current Windows user Downloads setting through a read-only PowerShell call, translates that path with `wslpath`, and selects a ZIP whose bytes match that expected hash. Browser duplicate filenames are accepted only when their bytes match. WSL Downloads is also checked; conventional Windows Downloads paths are checked if Windows interoperability is unavailable. Nothing is executed from a wrong or incomplete archive.

The verified ZIP's launcher checks the existing canonical project, current Git origin and ignored/untracked delivery destination. It verifies the complete member inventory and checksums before writing private material. It copies the ZIP to:

```text
~/ARC_Independent_Lab/delivery/P3_CHECKPOINT_038_HOME/<archive-sha256>/PACKAGE.zip
```

It extracts the contents under the adjacent `bundle/` directory, preserving existing equal files and stopping on changed or unexpected files or links. It then executes the original038 source-staging helper with that bundle and the canonical project path. The helper obtains its public input bytes from content commit `aa39617b964b1b9ce96555128d59394c5de05361`, verifies the two original PDF hashes, stages them privately in `delivery/P3_SOURCE_PACKET_038`, and publishes only the existing source-integrity receipt and checksum through GitHub.

The new outer ZIP does not alter that manifest or its interpretation. If the original038 helper was already run successfully, the same source packet and receipt are reused. If its push failed, the unchanged helper can retry the exact receipt publication without creating another scientific run. No reviewer, model, candidate treatment or HPC job is part of this step.

## Source of the path discovery

The Windows Downloads known-folder identifier is `{374DE290-123F-4565-9164-39C4925E467B}`; the documented default is under the current Windows user's profile. Source: [Microsoft KNOWNFOLDERID documentation](https://learn.microsoft.com/en-us/windows/win32/shell/knownfolderid), accessed 2026-09-11. The script reads the user's current shell-folder setting and expands Windows environment variables instead of assuming the default path. This is an implementation choice; the laptop's actual resolved path is not claimed to have been observed here.

## Verification scope

The publication validation identifies the exact source hashes and local tests. Downloads-resolution tests substitute PowerShell and `wslpath` output, including redirected paths, spaces, Unicode and a BOM. Archive/launcher tests exercise actual local filesystem operations and substitute the invoked step where necessary. The original helper's Git integration tests cover its receipt-only publication and retry behavior. These checks are not a claim that this Linux workspace ran Windows interoperability or the user's WSL checkout. Actual source staging is established by the receipt returned to GitHub.

The user's standing workflow is recorded in `docs/USER_HANDOFF_PREFERENCES_2026-09-11.md`. All future deliverables must include the complete ZIP and a command that runs from WSL home, without asking the user to locate the extraction directory.
