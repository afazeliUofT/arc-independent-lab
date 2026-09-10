# Checkpoint 030: one finite reviewer correction

Prepared 2026-09-10T04:35:25.085456+00:00. This is an unsigned request under `03_AUTONOMY_SPEC.md` §6, items 10 and 16: the approved native allowance is exhausted, and the proposed implementation changes the reviewer control surface. The prior run's actual approval is preserved in `state/escalations/2026-09-10_FINITE_REVIEW_028_APPROVED.md`; the checkpoint 029 pause is preserved in `state/escalations/2026-09-10_FORENSIC_029_NATIVE_PAUSE.md`.

## What I need and why

Approve the exact scope `configs/P3_FINITE_REVIEW_SCOPE_030.json`, SHA-256 `5abc5794f3adadeebc0e3df3e1ffd5bc4416806d2d1212f0a6b73db96d177060`, for one manually initiated, attended operation. It permits at most **two additional native starts and two additional explicit model turns**, increasing the cumulative ceilings from **10/7 to 12/9**: one synthetic admission stage and, only if that passes, one separately fresh scientific review. The reviewer remains **gpt-5.6-sol / max** under the previously accepted identity and effort policy. No automatic retry or fallback is included.

This amendment addresses the defects established by run 028 and the source audit. The run made 88 successful scientific broker calls, then stopped on an unadvertised native item. A separate later cache-metadata check failed. Its missing event type, changed cache path/field and writer remain unknown. There was no verdict, and the new design does not retroactively admit that run. [Published forensic record](https://github.com/afazeliUofT/arc-independent-lab/blob/b2f47e9442cbc5bd06490dd0d9fb0475a860aae9/reports/P3_RUN_028_REVIEW_AND_ROUTE_DECISION.md), accessed 2026-09-10.

## The concrete changes

1. A source-derived item registry handles context compaction, text plans and passive safety-buffering metadata bound to the same thread, turn and model. It retains item and broker witnesses across compaction. It does not follow faster-model suggestions. Unknown events, disabled tool effects, model rerouting and additional parent turns remain terminal. The item registry is capped at 4096; passive metadata stays under the existing 24 MiB frame limit without invented per-string ceilings.
2. Only the two already admitted noncredential caches are captured as exact, sealed memory contents, at most 4 MiB each, and supplied read-only at the original native paths. Source changes are recorded individually and do not mutate the reviewer's sealed inputs. Source identity, capture stability, cache absence and sealed-input integrity are checked. The existing same-path native credential-refresh bind is unchanged; the parent never opens, hashes or copies credentials. Authentic configuration/model-policy checks remain mandatory.
3. The session observation is saved before postchecks. Host, packet and cleanup findings remain separate. Any failed integrity check still blocks admission; any submitted reviewer object is preserved unchanged, without converting its existence into a pass.
4. Before reserving either Codex start, the same execution command performs one synthetic-only bubblewrap/Python prerequisite lasting at most 10 seconds including cleanup. It must establish exact sealed input bytes, original-source mutation independence, write/truncation refusal, absence preservation, an unmounted synthetic auth sentinel and complete process cleanup. It reads no actual cache or credentials and sends no model request. Failure or partial evidence is retained and stops without retry or Codex reservation.

The original scientific prompt, 722-file packet, broker, original observer auditor, model, configuration origins and per-stage ceilings remain fixed. The synthetic stage permits at most 600 seconds and 16 broker calls; the scientific stage permits at most 3600 seconds and 512 broker calls. Cleanup remains included. No additional spending, paid API, account replacement, new login or unattended model use is authorized. The exact source, process, byte, request and cleanup limits are in the scope file.

## Work completed before this request

All **108 offline tests passed, with no skips**. They cover actual Linux memory seals and descriptor inheritance; same-inode and replacement cache changes; lifecycle and broker recovery; early verdict submission; concurrent failures; receipt-write failures; and coherent false prerequisite receipts. The report is `artifacts/P3_REDESIGN_VALIDATION/20260910_030_001/REPORT.json`, SHA-256 `f4599a5710ba975875e7e51e3dc5ad5aaa37b39b3ce6d215d405761e3df047f7`. The source manifest and limitations are in `evidence/P3_REDESIGN_030_PREPARATION.json`, SHA-256 `600951b7cefe751510e30d153a077b6779f5cb6b74cae985db293dd1ea2e1cd3`. All 100 existing protected scientific documents, scripts, configurations and preregistrations checked against checkpoint 029 remain byte-identical. These checks are engineering evidence, not independent scientific review.

A successful target bubblewrap mount is not established in this hosted environment. That is why the integrated prerequisite occurs before any new native reservation. Source classification is not a guarantee that every future client event will be admitted or that a verdict will be produced. Internal compaction may invoke inference; the explicit-turn ceiling is not a backend inference or token meter. The native Codex bucket snapshot does not measure hosted ChatGPT allowance, which remains unavailable.

The one ZIP also includes validation of the exact installation and human approval variant. Publishing cannot launch a model, so a Git push retry cannot repeat model use. Existing complete execution receipts are verified and reused; partial or changed attempts stop. The separate canonical run 028 SESSION files must be present and match their recorded hashes; they are never reconstructed from an embedded report.

## How to answer, and what happens next

The required answer belongs in **this file**, appended under a section beginning `## ANSWER`. A chat message alone does not satisfy the contract. To reduce human steps, the delivered wrapper's explicit `--approve-correction` flag writes that exact section, updates its checkpoint checksum, and performs the human commit and push. It records the approval identifier `APPROVE_P3_FINITE_REVIEW_030_CORRECTION` and `scope_sha256: 5abc5794f3adadeebc0e3df3e1ffd5bc4416806d2d1212f0a6b73db96d177060`. The unsigned release does not already contain an answer. Running the wrapper without the flag is inspection only.

After that publication succeeds, the separate `scripts/p3_finite_review_030.py --run-attended-review` command can execute the approved operation. Keep the terminal open and available to interrupt. The report location is printed; if the kernel prerequisite stops first, its separate report folder is opened by the supplied instructions. Attach its REPORT.json. A scientific verdict is requested only if the file actually exists.

If approved, I will verify the returned receipts, evaluate any unchanged independent verdict and proceed with Phase 3 dispositions. If declined, I will leave native execution paused, preserve this preparation and assess a different independent-review route without new model calls. If a narrower alternative is specified, I will assess it before preparing a revised executable scope. Another unexplained failure does not authorize another attempt.

## Objective continuity

The objective remains understanding and remedying failures to acquire knowledge through interaction, retain it across discontinuities and recombine it in unfamiliar situations. Diagnosis and novelty-free ideas are approved. The multidisciplinary study is complete within its recorded scope, not exhaustive. PI novelty/residual audits are written; independent dispositions, final mechanism selection and PROGRAMME.md remain unfinished. There is no mechanism efficacy result. If independent review confirms the reductions eliminate the current candidates, explicitly return to novelty-free invention about acquiring useful descriptions, predicates and models, rather than treating supplied representations as a solved problem.

## ANSWER
APPROVE_P3_FINITE_REVIEW_030_CORRECTION
scope_sha256: 5abc5794f3adadeebc0e3df3e1ffd5bc4416806d2d1212f0a6b73db96d177060
