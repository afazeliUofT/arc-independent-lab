# The revised laptop command observation is complete

2026-09-07. The supplied final report is exactly the requested v2 observation. Its recorded status, `OBSERVED_REQUESTED_COMMAND_BOUNDARIES`, is supported by the captured events and external controls. This completes this particular command canary; no rerun is needed.

The unchanged input is `artifacts/GATE0_BOUNDARY_OBSERVATIONS/20260907_002/REPORT.json`, SHA-256 `386d912567deb1e953faa851c8eaded5ca32e2edc516aad99aadae35bd162cfd`. The recomputed checks are in `evidence/GATE0_BOUNDARY_OBSERVATION_002_VERIFICATION.json`, SHA-256 `374af08fd069efcc42a513560ae5849353e02f3c48ffc5046c0c9eb40ed5b455`. The report was produced by the exact delivered driver, with neither command-runner nor runtime-inspector substitution.

## What actually happened

- The confined child started, read its allowed canary and completed the full protocol.
- The tested forbidden reads and writes failed, including the symlink path, shell redirection and nested process operations.
- The protected fixture's inventory, bytes and modes stayed unchanged.
- The tested IPv4 loopback connection returned `PermissionError`/EPERM, while the unconfined child and outside controls before and after could exchange the expected nonces.
- The selected Codex executable passed host preflight and version checks, and its identity and hash stayed unchanged after execution. Its SHA-256 is `9739cbc928b9c573be83256acd46668f5dd4f119d2d09e05246895ca2aaf0c9a`.

The actual v2 observation resolves the preceding launch failure for this setup. It supports the runtime-visibility diagnosis, but v2 both invoked the selected binary directly and added the explicit file grant. This is not a single-factor causal experiment isolating those changes. The old failed observation remains valid evidence of the earlier setup.

## Publication verification

Checkpoint010 is verified at `9925b3697a2d829044539833f6ca1c26ac8d1702`. Its exact delivered changes, complete tree and scientific review manifests matched their recorded hashes and modes. Receipt: `evidence/REMOTE_CHECKPOINT_010_VERIFICATION.json`, SHA-256 `2693fe4609c2992ef7c8319d687cfb0630b12a9ca58f7b8a5939fcb7bda71f55`. [Published commit](https://github.com/afazeliUofT/arc-independent-lab/commit/9925b3697a2d829044539833f6ca1c26ac8d1702), accessed 2026-09-07.

The assistant adopted the verified human commit without creating a commit or push. This new positive report and its verification are prepared for the next substantive publication checkpoint; they are not claimed present in checkpoint010.

## What this does not establish

This is an engineering observation of the specified local command boundary. It does not establish all network routes, the full Codex client's tool or connector restrictions, a fresh reviewer context, subscription allowance, or a scientific verdict. Unattended model use remains disabled. The earlier unexplained hosted validation-file discrepancies are not retrospectively explained by this successful laptop run.

The next task is complete reviewer preparation. A fresh offline input core was assembled from the exact union of the two review manifests, including both manifests themselves. Available private PDFs were matched by hashes explicitly present in the frozen input documents and copied into a private packet. `evidence/P3_REVIEW_INPUT_CORE_AVAILABILITY.json`, SHA-256 `d4eb4bb4b531c5fb97aca7ff597b2c2f8242835449203a2cb588e0930ba458ae`, records the exact input inventory and source matches. This is availability and byte-integrity work; citations without pinned PDF hashes, relevant supplements and source-version coverage still require closure before review. Copyrighted papers are not added to the public repository.

The passing command canary is not repeated as a substitute for that work. A full-client preflight must establish startup/tool restrictions and a fresh context before the scientific prompt is sent. Any quota observation must identify its actual scope; a generic Codex bucket cannot silently stand for this hosted conversation's allowance. No additional human file or approval is required to confirm the present report.
