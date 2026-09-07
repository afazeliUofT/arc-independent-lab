# Startup report accepted; next contained account observation

2026-09-07. PI engineering status, not an independent scientific verdict.

The uploaded `REPORT(2).json` is exactly the report requested for checkpoint012's startup observation. Its archived bytes are `artifacts/GATE0_CLIENT_PREFLIGHT_OBSERVATIONS/20260907_001/REPORT.json`, SHA-256 `53b98a9e4c99603de49b3e464f3aeaa5bd950492253c69809934f079fcbb90f3`. The recorded launch vector matches the delivered network-disabled mount plan and requested control arguments; initialize, configuration read and requirements read returned. Exit code -15 is the parent's planned SIGTERM after those responses. The recorded original runtime, bwrap, installation identifier and configuration-origin metadata checks passed.

This is acceptance of the requested **startup observation**, not a pass for independent review. The report intentionally excludes raw configuration and diagnostic payloads; their stream hashes do not let us reconstruct them. We verify the supplied filtered evidence, not independently replay unseen response contents. Nonempty stderr had no matches among the probe's selected diagnostic strings; that is not proof that every possible warning was absent.

The exact comparison receipt is `evidence/GATE0_CLIENT_PREFLIGHT_OBSERVATION_012_REVIEW.json`, SHA-256 `8cf8d7f29445ef75413bf0d768c14d36ae3160e2014633352acae427fff372cc`. The public checkpoint was verified at [commit 4363226a2fa5fd1aef45d8b458fb5b7fce3e586b](https://github.com/afazeliUofT/arc-independent-lab/commit/4363226a2fa5fd1aef45d8b458fb5b7fce3e586b), accessed 2026-09-07, against every full-tree byte and mode and the exact delivered ZIP transition. Receipt: `evidence/REMOTE_CHECKPOINT_012_VERIFICATION.json`, SHA-256 `d083ed0de2e413b3c9e7407e7216e3c1150c2b18166c1c5c692f5d410a23715a`. Both approved scientific deliverables and frozen review manifests are unchanged.

## What the missing controls mean

The only unobserved requested fields were `tools.update_plan.enabled` and `tools.experimental_request_user_input.enabled`. Exact source shows that `config/read` projects core configuration into a public typed `tools` object that omits these two fields. Absence is therefore not evidence that the overrides failed. The old report did not retain the winning layer values, so it also does not prove their effective values. Keep the original report unchanged.

The next necessary account observation includes narrowly filtered winning layer/origin checks for these two values, requiring actual false booleans. The source explanation is `docs/GATE0_CONFIG_PROJECTION_2026-09-07.md`, SHA-256 `0220acd3ac8f4c88a0846236f064dd82615bd24eb11cf66da0d1874b539d868d`, with exact upstream URLs and access dates. A public merged config object cannot be treated as a complete tool-exposure attestation.

## Repeated commands

The user reports repeating the prior block because GitHub publication failed. Its `&&` condition prevents a failed publication from launching the startup probe. A successful repeated invocation can create another timestamped run. The supplied report describes the run at `delivery/GATE0_CLIENT_PREFLIGHT_20260907T183401.226510Z`; it does not establish how many other invocations completed. Preserve any other run directories, but no further upload or repetition of the passed startup-only probe is required now.

Checkpoint013 separates `publish` and `observe`. Publication retries never launch the client. The observation uses the fixed new directory `delivery/GATE0_ACCOUNT_METADATA_013`; a completed repeat checks its recorded digest and driver hashes and returns the same report without executing a client. A partial or altered run stops; it is never silently overwritten or rerun.

## The advancing step

Implemented `scripts/gate0_account_metadata.py`, sharing the existing bounded transport and mount planner. Its only extra protocol request is `account/read` with `refreshToken=false`. It keeps the original network denial, exact runtime pin, read-only input mounts and fresh writable runtime locations. It neither accesses a host keyring socket, copies authentication, changes login/configuration nor sends a thread/model/rate-limit request. Output records recognized enums and booleans; email, tokens and arbitrary configuration/error strings are discarded. Unknown error responses retain only a numeric code and fixed diagnostic categories.

This establishes which cached account metadata is available **inside the existing namespace**. Missing `auth.json` or a null contained account does not establish host logout. A source default is labelled as inference. A returned plan string is not mapped by name similarity to the funder's stated subscription. Entitlement, hosted subscription allowance, managed policy applicability and full reviewer independence remain unverified. Exact source analysis: `docs/GATE0_SUBSCRIPTION_ROUTE_2026-09-07.md`, SHA-256 `f3c24aa0a8547dfa01ed7c13fe3cb8069fe3579c7d3d352bcef91adaa7be86d1`, with upstream URLs and access dates.

Validation used finite synthetic subprocesses, real pipe transport, error/secret filtering and completed/partial/tampered receipt cases. The original startup-only behavior was also checked. Evidence: `artifacts/GATE0_ACCOUNT_METADATA_HARNESS/20260907_001_8ed998b1/REPORT.json`, SHA-256 `3efb3992250259119cfeb7b4bb9f17aabdb071439a3d37a7d58200c66f41f85d`. No actual client, model, network-enabled service or scientific reviewer was run here. The pure layer filter has its own pinned case report under `artifacts/GATE0_CONFIG_CONTROLS_HARNESS/20260907_001/`.

## Scientific implication and next decision

The objective remains understanding failures of interactive knowledge acquisition, retention across discontinuities and recombination. Engineering progress does not strengthen the science. The PI's component reductions and joint-algorithm incompleteness remain provisional pending an enforced independent review; no novel complete operation currently justifies a treatment run. This step does not reopen or silently change approved ideation and does not substitute a shared-context consultant for the reviewer.

After the account report, classify the actual route once. A usable contained ChatGPT account permits preparation of the remaining supported policy/model/allowance observation; it does not itself permit a model call. An absent or unsupported route requires a concrete supported account-access decision, not another generic inventory or speculative login. Exact source indicates ordinary login can revoke prior authentication, and raw status can reveal an API-key fragment; neither is a blind next instruction. Continue to pause unattended model use while the authoritative meter is unavailable.

The handoff includes Bash/WSL commands opening both the download destination and exact report folder, as requested. Ali continues to execute commits and pushes; no further scientific approval is requested.

## Checkpoint preparation correction

While recording the new folder-opening preference, I appended it to the historical user-amendment document, overlooking that this document is in the frozen review inputs. The mandatory hash comparison caught the change before checkpoint construction. I restored the exact original bytes and placed the preference in a new dated file; neither the frozen manifest nor any approved scientific content was revised. No model or review used the temporary bytes. The error and correction are preserved in `evidence/FROZEN_AMENDMENT_APPEND_CORRECTION_2026-09-07.json`, SHA-256 `bf526525d8b8404bbb174ac6e7fd7dad500d6c52aed8d6aa64cd268be39e934c`. This demonstrates why the manifest check is needed; it does not establish an enforced edit interception in this hosted workspace.
