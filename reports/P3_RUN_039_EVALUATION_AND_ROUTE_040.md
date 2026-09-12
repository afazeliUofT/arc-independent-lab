# Checkpoint039 return: no verdict; confirmed admission defect

Assessed 2026-09-12 from canonical GitHub commit `ee29a58cf57783984e848df83032541c929c4658`. This is a PI evaluation of execution evidence, not an independent scientific verdict.

## Scientific result

No `REVIEW_VERDICT.json` was returned. The original collector records the file as missing, the controller reports `STOPPED_WITHOUT_COMPLETED_REVIEW`, and the original scientific SESSION records no thread request, no model-turn request and no broker calls. All required scientific texts and both supplied papers remained undelivered. Consequently none of R1-R7 has an independent disposition, and this attempt changes no candidate novelty or efficacy conclusion. The first audit's earlier scoped GO does not cover this second audit. [R, S, B]

The controller's `science_started: true` means it entered the scientific native stage. It does not mean a scientific model turn began. The standalone SESSION is the relevant evidence for that distinction. [R, S]

## Actual use and limits

| Quantity | Synthetic stage | Scientific stage | Attempt total |
|---|---:|---:|---:|
| Native processes started | 1 | 1 | 2 |
| Model turns sent | 1 | 0 | 1 |
| Completed-turn events observed | 0 | 0 | 0 |
| Scientific verdicts | 0 | 0 | 0 |

These are recomputed from original standalone sessions and agree with the embedded records. The canary stops after the intended read/refusal witness, so its missing completed-turn event is consistent with its successful termination criterion. It still consumed a sent model turn. The collector's own zero-start/zero-turn fields describe collection, not the attempt. [R, Y, S, U]

Cumulative actual use is now sixteen native starts and twelve sent turns, against the039 ceilings of sixteen and thirteen. The native-start allowance is exhausted. The unused turn slot does not authorize restarting039. Both native processes were reaped by controlled termination; exit code minus fifteen is consistent with canary completion and the scientific admission stop. [R, Y, S, U]

Both initial Codex snapshots reported forty-three percent used in a 10,080-minute window, resetting at 2026-09-15 16:40:27 UTC. The live quota check admitted both stages. This was not a quota refusal or absence of the declared Sol Max catalog entry. Equal rounded percentages do not demonstrate zero consumption. Numerical token/rate-update payloads were discarded by the frozen session implementation; exact token counts, attributable quota changes, remaining tokens, monetary cost, and hosted ChatGPT allowance cannot be recovered from this return. Catalog presence alone is not a separate model-entitlement attestation. [Y, S, U]

## Execution boundary assessment

The synthetic stage passed the real bounded sequence: invalid numeric input refused, allowed canary text read, and path traversal refused. Its original receipts satisfy the unchanged controller admission predicate. The scientific stage passed recorded configuration, account and catalog checks, then stopped locally before creating a thread. [Y, S, B, V]

Recorded protected-host checks passed in both stages. Packet measurements before and after matched; the independently opened packet observer remained available. The science packet's hash checks establish available bytes, not delivery to or reading by a reviewer. No broker-boundary or native-event breach is recorded. [B, V]

That conclusion has specific limits. This attempt reused historical kernel evidence and did not produce a fresh kernel attestation. A complete runtime tool inventory, all backend instruction contents and full context freshness were not proven. The native process inherited host networking without an endpoint allowlist. Its existing credential mount remained writable for the previously scoped native route; the Python parent did not read credential contents, and unchanged credential metadata is not byte-integrity proof. Host model-cache timestamps changed during the canary without identifying the writer, while the separately captured sealed inputs remained intact. Those facts must not be flattened into “everything was unchanged” or a universal isolation certificate. [B]

## Earliest reliable cause and responsibility

The exact scientific `admission_reason` is `Unexpected reviewer dynamic tool spec`. The frozen broker advertises `source_access_receipt`. The inherited admission helper still admits the old `run_observer_audit` name and rejects the new name. The actual scientific call reaches this local validator after model selection and before `thread/start`; the canary passes because its tool list contains only `read_text`. Pure execution of those original functions reproduces the returned error without a native process. [S, B, V]

This was my package integration error. The previously reported offline tests passed their stated checks, but they did not exercise the full scientific tool list through the actual thread-admission function. Describing those checks as sufficient readiness was too strong. The ledger already documents an emitter/consumer integration-test gap in the030/032 work; this repeated the same class of mistake at another interface. The corrective lesson is to test the exact production producer and consumer together before consuming a native start, not merely increase a test count.

## Route

Apply the L1 correction in a new040 scope. Keep the039 evidence immutable. The040 admission helper accepts only the exact already frozen canary and scientific tool contracts, including their nested schemas and descriptions; it does not admit the obsolete observer operation or arbitrary tools. A pure preflight constructs both actual thread payloads before any native process starts. Model, effort, profile, network/mount policy, source packet, broker, protocol and scientific prompt retain their existing scope.

The user receives one complete040 ZIP and one WSL-home command. The new finite maximum is two native starts and two sent turns, yielding cumulative ceilings eighteen and fourteen from the verified actual baseline. Existing039 is closed; repeated040 commands after a reservation only collect and publish its original evidence. The numerical limits and their evidence are specified in `state/authorizations/P3_FOCUSED_REVIEW_040_STANDING_AUTHORIZATION.md` and sealed in `configs/P3_FOCUSED_REVIEW_SCOPE_040.json`.

The next scientific decision remains whether the PI's bounded R1-R7 arguments survive independent scrutiny, including their strongest defenses and counterhistories. The original objective remains useful knowledge acquired through unknown interaction, preserved across discontinuities and recombined for new demands. No mechanism selection, experimental tuning, candidate treatment or HPC experiment is justified by this stopped attempt. No additional paper is needed to repair or perform the existing bounded assessment.

## Evidence register

All GitHub sources below were accessed 2026-09-12. Paths are immutable at the assessed commit. Local derived records include full per-stage provenance and hashes.

- **R:** `artifacts/P3_REVIEW_039_RETURN/8b2bd233f9e585d4ef490dd5302ee488c14989d8badeb5ab2b3353c23c85049b/files/delivery/P3_FOCUSED_REVIEW_039/REPORT.json`; SHA-256 `8a14ad9551e6f0f1840d05889574cb7763b330046c0a51474d62ceb3926c38cc`. [Original report](https://github.com/afazeliUofT/arc-independent-lab/blob/ee29a58cf57783984e848df83032541c929c4658/artifacts/P3_REVIEW_039_RETURN/8b2bd233f9e585d4ef490dd5302ee488c14989d8badeb5ab2b3353c23c85049b/files/delivery/P3_FOCUSED_REVIEW_039/REPORT.json).
- **Y:** same archived report directory, `synthetic_SESSION.json`; SHA-256 `b3ad48a0c7dcd519f1328e5b3f11f708c2c5248b206dbdddd33d77376417c598`. [Original synthetic session](https://github.com/afazeliUofT/arc-independent-lab/blob/ee29a58cf57783984e848df83032541c929c4658/artifacts/P3_REVIEW_039_RETURN/8b2bd233f9e585d4ef490dd5302ee488c14989d8badeb5ab2b3353c23c85049b/files/delivery/P3_FOCUSED_REVIEW_039/synthetic_SESSION.json).
- **S:** same archived report directory, `science_SESSION.json`; SHA-256 `d40b69e66d045fddb7b469c4e99f51ac2323606ca0f435b5ce5b99010d47cabc`. [Original scientific-stage session](https://github.com/afazeliUofT/arc-independent-lab/blob/ee29a58cf57783984e848df83032541c929c4658/artifacts/P3_REVIEW_039_RETURN/8b2bd233f9e585d4ef490dd5302ee488c14989d8badeb5ab2b3353c23c85049b/files/delivery/P3_FOCUSED_REVIEW_039/science_SESSION.json).
- **U:** `evidence/P3_USAGE_RETURN_ASSESSMENT_040.json`; SHA-256 `e6269b5e68d59b45b8d9ae1667a4c2dc600104dac138617fb41690880257878b`.
- **B:** `evidence/P3_BOUNDARY_RETURN_ASSESSMENT_040.json`; SHA-256 `5556f9b9d78a846d90b86bb9c3e22ba56d365f1221f727b27feff184bafcb42b`.
- **V:** `evidence/P3_RUN_039_RETURN_VERIFICATION_040.json`; SHA-256 `2a93b41bcad0c37fb1b3acd5e21b2a8a408386a4e1a9935bcc8cf8d9f5ff5bd5`. The frozen collector was re-executed and matched the original report's collection exactly; controller pins, accounting and stage-admission predicates were independently recomputed. The GitHub return added only its expected original archive files and preserved previous repository blobs/modes.
