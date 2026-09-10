# Review of actual run 028 and route decision

Date: 2026-09-10. This records engineering findings, not a scientific verdict.

The report is authentic to the delivered, approved checkpoint. GitHub commit `309b2330819b55fc5573e57163d4ae6e09c5d21d` contains the exact approved variant, and all 1085 file identities and modes were verified. The attached run report is preserved at `artifacts/P3_REVIEW_SESSION_STOP_OBSERVATIONS/20260910_029/REPORT.json`, SHA-256 `b96152d5f07f502a41b7e218417d20d6775b9751c7440f94de1015dc39cd336a`. All numbers describing this run below derive from that artifact; `evidence/P3_FINITE_REVIEW_028_OBSERVATION_REVIEW.json` contains the checks.

## What worked

The new synthetic challenge passed: the native reviewer received the deliberate argument error, corrected its read, then triggered the real path refusal. A separately fresh scientific session made 88 successful broker calls: 34 text reads, 49 file hashes, four page-image reads and one invocation of the unchanged auditor. It reported no failed scientific broker calls or recoverable scientific argument errors. The scientific packet passed both complete verifications with 722 manifested files and identical before/after receipts. The private-packet preflight reported 104 text files, 589 images and 29 binaries. This supersedes earlier estimates of the installed derivative-page count; no smaller historical packet is substituted for the actual installed packet.

The code/interface correction therefore made a material operational difference. It did not produce a scientific verdict. The receipt reports that the reviewer never submitted one, and there is no output file to recover or approve as a verdict.

## The two distinct failures

First, the scientific session terminated on `Unadvertised native item effect`, during an `item/started` notification after about 434 seconds. This is the session lifecycle validator, not the broker input validator. The exact item type was not included in the saved report. The broker failure field is null because no broker operation failed.

Second, the controller's later host check found `cache_metadata_unchanged: false`. That produced the top-level message `Scientific stage changed protected host inputs`. The wording overstates attribution: the predicate does not identify a writer. Other recorded host predicates passed, including configuration metadata, executable hashes and installation identity. The later cache failure does not explain the earlier session stop. Both findings must remain in the record.

The latest diagnostics were useful for distinguishing the broker from the lifecycle stop, but I overstated their completeness in the preceding handoff. The native-item filter still discarded the specific type, and the cache check still discarded individual after-values. Successful fixed-input and broker tests did not cover the complete lifecycle of an extended scientific review. That engineering gap is my responsibility.

## What the source establishes, and what remains unknown

The pinned client legitimately emits a `contextCompaction` item through `item/started`. Our current validator rejects it. This is a demonstrated lifecycle incompatibility. It makes compaction a plausible explanation for the stop, but it does not establish the missing actual item type. Elapsed time and the number of successful reads are not proof of compaction. The source forensic report preserves the complete distinction and a local reproduction. [Pinned item definitions](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/app-server-protocol/src/protocol/v2/item.rs), [pinned event handling](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/app-server/src/bespoke_event_handling.rs), accessed 2026-09-10.

The two host-cache predicates compare metadata, not file contents. Their aggregate false identifies neither the changed path nor field. Reading them now cannot reconstruct the missing end-of-run state or identify the writer. A read-only bind limits writes through the reviewer mount; it does not freeze the underlying file against another host process. The pinned model-cache writer uses an in-place file write, so an immutable old-inode snapshot must not be assumed. There is no basis for declaring the change harmless or blaming a reviewer escape. [Linux mount documentation](https://man7.org/linux/man-pages/man2/mount.2.html), [pinned cache implementation](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/models-manager/src/cache.rs), accessed 2026-09-10. See `artifacts/P3_CACHE_FORENSICS/20260910_029/FINDINGS.md` and its source-hash report.

## Decision

Stop native attempts under this harness. The actual cumulative allowance is exhausted at ten native starts and seven sent turns. Do not rerun 028, reset counters, fabricate a verdict, waive the cache predicate, or add an event exception on the assumption that the missing type was compaction. This checkpoint requests no additional native/model allowance and launches no diagnostic operation.

The next engineering task is a complete design for an extended review: classify the supported client lifecycle, preserve fixed categorical reasons for every refusal, and supply demonstrably stable noncredential cache inputs under the existing policy. The scientific reviewer must retain the same restricted authority and authentic configuration/model-policy validation. Credentials must never be copied into an input snapshot. The native-event failure and each protected-input comparison must be reported separately, including when several fail. Tests must exercise extended-session lifecycle and concurrent modification, rather than only a successful canary and broker calls.

A new execution request is justified only after that design is concrete and its controls have been tested offline. Any required control or numerical-budget amendment must then be one combined, reviewable request. The present work is the completed forensic reassessment, not a claim that this later design has already been implemented. There is no further human probe requested to rediscover evidence the existing report omitted.

## Research continuity

The scientific objective remains explaining and improving acquisition of knowledge through interaction, retention through discontinuity and recombination in unseen situations. Phase 1 diagnosis and Phase 2 novelty-free ideas are approved. The multidisciplinary study is complete within its documented scope, not exhaustive. PI novelty and residual audits are written; independent dispositions, final mechanism selection and `PROGRAMME.md` remain unfinished. The successful auditor invocation and transport progress do not establish candidate efficacy or an independent novelty verdict.

If independent review eventually confirms that the reductions eliminate the present candidates, explicitly return to novelty-free invention about acquiring the descriptions, predicates and models those candidates assume supplied. Do not select a mechanism merely to end the engineering delay.
