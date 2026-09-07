# First laptop boundary observation: child launch failed

2026-09-07. Checkpoint009 is verified on public `main` at `221f6c76ea4a72f7723d804dd68416cb86820aa4`. The publication is correct. The requested command-boundary observation did not reach its test child.

## Evidence and outcome

The supplied report is preserved byte for byte at `artifacts/GATE0_BOUNDARY_OBSERVATIONS/20260907_001/REPORT.json`, SHA-256 `3713ae45b7e3306841fb60b819083a2d9273a723107c22262e9597b3d7e74e19`. Its digest matches the terminal receipt. The delivered probe hash, embedded child hash, captured-stream encodings and digests, positive controls and failure classification were checked against the actual checkpoint009 source. Verification receipt: `evidence/GATE0_BOUNDARY_OBSERVATION_001_VERIFICATION.json`, SHA-256 `bed96ef0742a8be7da53ccb609802542fa9789078334dc8f721d980243278428`.

The version and help commands completed. The unconfined synthetic child completed its read, write, subprocess and loopback controls. Both outside loopback checks succeeded. The protected fixture stayed unchanged. However, the attempted confined command returned no child events and this error:

```text
bwrap: execvp /home/afazeli2006/.codex/packages/standalone/releases/0.151.0-x86_64-unknown-linux-musl/bin/codex: No such file or directory
```

The recorded `SANDBOX_START_NOT_ESTABLISHED` classification is correct. No protected child executed, so unchanged fixture bytes cannot establish write protection. No confined connection was attempted, so network enforcement remains inconclusive. There was no model call or independent review.

Publication verification separately checked the exact delivered changes and full tree against the checkpoint manifest, including both scientific review packets. Receipt: `evidence/REMOTE_CHECKPOINT_009_VERIFICATION.json`, SHA-256 `1672086f05539b3d73e4d456ba0105f32470819b4747c22ec61cd9be0ba92fcd`. [Published commit](https://github.com/afazeliUofT/arc-independent-lab/commit/221f6c76ea4a72f7723d804dd68416cb86820aa4), accessed 2026-09-07.

## Correction to my test design

My profile did not explicitly admit the installed Codex executable. I treated the generic `:minimal` runtime read allowance as sufficient for the first launch attempt, without measuring whether it included this user-installed binary. The resulting launch failure is an engineering defect in the proposed setup, not evidence for or against any scientific candidate.

The leading explanation is that the root-deny filesystem view hid the Codex executable that Bubblewrap needed to execute. The error identifies that particular path, but does not uniquely prove the cause: a missing binary or interpreter can also produce ENOENT. No mount inventory or actual binary metadata was captured by this first probe. The package's `linux-musl` name is not proof of static linking.

The next intervention is therefore narrow and explicit: verify the observed version-specific executable on the host, record its path, file metadata and hash, verify its version, invoke that same binary for the sandbox operation, and grant read access to that file. Root denial, minimal runtime reads, synthetic-packet reads, disabled network and managed requirements remain in the requested policy. Exact file grants and narrower exceptions under a restricted root are documented in [OpenAI permissions](https://learn.chatgpt.com/docs/permissions) and the [configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference), accessed 2026-09-07.

This intervention changes the proposed policy's runtime allowance before a new observation. It does not alter a managed rule or an existing configuration file. It grants no read access to the home directory, the Codex configuration directory, or the whole installation directory. A missing, unexpected or changed executable stops the retry; the driver will not learn progressively broader grants from subsequent errors.

## Next consequential step

The revised driver must be published and then measured on WSL. A valid observation still requires the original complete child protocol, allowed-read control, forbidden-operation checks, unchanged fixtures and live outside connection controls. The present report and original source remain traceable through checkpoint009.

The newly captured doctor help advertises installation/configuration/authentication diagnostics, without an explicit quota-only operation. I am not treating that help as an authoritative allowance reading. Unattended model use remains disabled. Full reviewer tool restrictions, fresh context and the verdict channel remain separate requirements after the command boundary is measured.

## Hosted validation and a separate output-integrity correction

The revised driver retains the original child source, tests and classification functions. Simulated unconfined execution is still detected as a violation; rejected configuration, timeout, missing runtime, changed runtime and interrupted postflight remain nonpassing outcomes. Fresh synthetic file checks cover the runtime inspector. The exact receipt and archived raw reports are in `evidence/GATE0_BOUNDARY_V2_HARNESS_VALIDATION.json`, SHA-256 `b5d49dd6aaffd2041db00d7cdb4795b8bd92762647c6b4059fb9001735bd1bd3`.

While collecting these hosted checks, the simulated runtime-change case twice had a final report whose digest was recorded by the validator, but a later read instead found the initial `IN_PROGRESS` contents at that path. The cause is unestablished. The two affected validation sets are not certified; their receipts and observed bytes are preserved under `artifacts/GATE0_BOUNDARY_HARNESS/20260907_discrepancy/` and mapped by the validation receipt. This discrepancy concerns generated hosted test evidence, not the supplied laptop observation or the frozen scientific packet.

The driver now writes progress to its own file and creates the final report exclusively once, with flush, fsync and byte readback before printing its digest. The validator compares saved JSON to the returned object and rechecks report digests before completion. A fresh run passed those checks and the later archive checks. This is an observed improvement in this collection path; it is not a causal explanation of the earlier discrepancy or a durability guarantee across workspace resets. The final package and GitHub readback remain necessary.
