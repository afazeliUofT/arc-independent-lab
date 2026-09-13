# Checkpoint045 diagnostic adapters

Recorded **2026-09-13**. This step implements and checks previously missing diagnostic operations. It does not run the042 target instrument, establish a complete-work resource allowance, or rank candidates by measured efficacy. The frozen035 learner and043 accounting, N1 and N3 modules remain unchanged. The041 attribution requirements and042 ORDER0/1/2 corrections are the specification sources: [041 comparison](https://github.com/afazeliUofT/arc-independent-lab/blob/16976d8db11475f85ad2e96e5be786c1d4d50776/docs/P3_N1_N3_SUCCESSOR_COMPARISON_041.md) and [042 design](https://github.com/afazeliUofT/arc-independent-lab/blob/16976d8db11475f85ad2e96e5be786c1d4d50776/docs/P3_COMPARISON_DESIGN_042.md), accessed 2026-09-13. No additional primary-literature claim is introduced.

## Contract

| Operation | Exact behavior | Availability boundary |
|---|---|---|
| `PrescribedReader.fit(T,Phi)` | Validates the supplied typed grammar; copies exactly T; retains Phi in its supplied order; calls the frozen043 bulk-count implementation once. No append, feature enumeration or feature search. | Fits once. A refused fit remains nonnumeric and does not authorize another fit. |
| `partition_controls(T,Phi,session,...)` | Fits SELECTED, every individual predicate deletion while preserving all remaining predicates, and prescribed ORDER0/1/2 readers. Every copied table must have the identical canonical SHA-256. | Pending physical evidence is excluded because callers supply the actual retainedT. A failed required fit stops the operation. |
| `choose_goal(reader,history,goal,session)` | Requires opaque action indices 0–4 in order and the same Meter for reader and chooser. Requests all five forecasts, compares exact rational goal probabilities and uses the first action on a tie. It issues no physical action. | Any required nonnumeric forecast produces DECISION_UNAVAILABLE. A global refusal stops immediately; remaining unattempted actions are recorded. No favorable fallback. |
| `replay_acquisition(state,final_learner_state,session)` | Starts an empty single-block N1 with the recorded configuration. Validates event ordering, physical histories, RESET arrival, trial counters and warm-up words. Performs immediate trial updates, captures exact pre/post-trial states, then performs only the originally assimilated delayed-validation prefix. | Original pre/post snapshot hashes, table sizes, fresh-predicate provenance and final learner state must agree. Pending evidence is preserved. Mid-update resource progress that is not fully exposed by043 is reported unavailable. |
| `trial_decomposition(boundary,V,session,...)` | Fits P00 = (T0, Phi0), P10 = (T1, Phi0), P11 = (T1, Phi1), and predicts on identical original validation histories. Verifies numeric original pre/post forecasts, computes exact Brier differences, and checks count effect plus partition effect equals raw pre/post gain. | A partial validation prefix has no full V mean or credit. Nonnumeric components remain unavailable. A global refusal stops before another predictor or scoring operation. |

The empty-Phi key is exactly ORDER0. ORDER1 and ORDER2 retain the frozen043 typed-window serialization, including MISSING. These are fixed readout comparisons, not newly searched descriptions. A pair of complementary predicates in the fabricated table demonstrates that a single deletion can leave the partition unchanged; this must not be misreported as evidence that the full learned partition is unused.

`DiagnosticSession` retains its actual result objects and reader copies until close. Retained records must not be mutated by callers. The final replay report binds the source state, original and reconstructed final states, boundary tables and feature lists by hashes. It includes the replay operation order and retained pending suffix. Replay issues zero interface calls and zero scheduler calls; its newly computed state is never fed back to acquisition.

Replay is a check of N1 reconstruction and recorded update boundaries, not a reimplementation or proof of the entire N3 scheduler/library state. The043 event schema does not record every internal instruction or partially committed search/reset cursor. At a computation or memory interruption, a reconstructed final state can therefore be `FINAL_UPDATE_UNAVAILABLE`; it must not be relabeled VERIFIED or used to infer missing progress. Source authenticity still depends on the enclosing pinned return and hashes.

## Credit and attribution

Three different values are kept distinct:

1. The raw diagnostic Brier gain, including count-only improvements.
2. The credit recomputed by the unchanged fresh-predicate gate under the diagnostic allowance.
3. The credit actually available in the original acquisition and, where applicable, operative in its priority rule.

Recomputing a numeric value later does not retroactively award unavailable original credit. The report retains original credit status and value; `operative_priority_credit` is present only when the source credit was available and operative. Missing or nonnumeric original forecasts have explicit verification statuses, even if a separately budgeted diagnostic can reconstruct a numeric forecast later.

The constant fixture has exact mean count improvement 16/225, zero partition effect, and available gated credit 0. The separate fabricated fresh-predicate fixture has credit 7/144. These are finite arithmetic/conformance witnesses, not target effects, discovered world models, or evidence of useful retention/recombination. The fresh-predicate witness uses a two-action declared fixture; the common chooser is independently exercised with all five opaque actions.

## Named work and retained payloads

The adapters import the unchanged043 Meter, exact rational arithmetic and N1 prediction/count routines. They add named charges for predicate syntax/size checks, prescribed-Phi copying, table views and hashing, chooser input bytes/action requests/rational comparisons, replay source and boundary copies, event/trial validation scans, provenance materialization and Brier-identity comparisons. All imported count, prediction, predicate evaluation, copying, canonical serialization and rational arithmetic charges remain active.

Every reader is a separately retained copy. The diagnostic session retains source evidence, boundary table/partition views and reports; the Meter sees overlap with the replay learner and all P00/P10/P11 and selected/deletion/order readers that remain open. No unproved arena sharing discount is taken. Returned owner reservations and peak logical retained bytes are diagnostics under that convention.

**This is not complete resource accounting or a full-work profile.** Python temporary objects, dictionary/control-flow operations and some intermediate result construction are not comprehensively pre-reserved or individually metered. Canonical normalization and deepcopy materialize temporary objects before the eventual retained-state seal. A terminal refusal can return an explicitly unsealed partial record. Logical payload reservations are not Python allocator bytes or RSS. The unchanged043 snapshot envelope is a supplied development reservation, not a proved largest-run bound. These limitations remain part of the complete-work budget dependency;045 does not set B_comp or B_mem or assert experiment admission.

## First hosted conformance execution

The finite JSON fixtures were written before execution. A readonly staged closure contained exactly the configuration, diagnostics module, runner, focused tests and the three unchanged043 imports. The actual delivery runner executed once under a 300-second outer timeout, 270-second inner alarm, one CPU affinity and 2 GiB per-process address-space limit.

All **23 tests and 13 required case families passed on the first attempt**. There were no initial test failures to omit. Families cover prescribed fitting, all deletions, ORDER0/1/2, the five-action chooser, count-only and fresh-predicate decomposition, partial validation, RESET arrival, pending validation, pending issued actions, provenance tampering, nonnumeric decisions and accounting refusals. Tests call the real adapter paths; additional targeted substitutions provoke failures/unavailability at declared boundaries.

The hosted invocation used 0.300638702 seconds wall time, 0.299734601 seconds process CPU and 21,725,184 bytes peak process RSS. These measure only this small conformance suite, under uncontrolled hosted conditions. They are not laptop profile measurements or a projection for a 285-call acquisition or the target panel. The full result is `evidence/P3_DIAGNOSTIC_CONFORMANCE_045.json`, with source hashes, every test outcome, all 13 case summaries and actual metrics. The preceding source freeze is `evidence/P3_DIAGNOSTIC_SOURCE_FREEZE_045.json`.

The once-only user045 command runs the same bounded conformance source closure and publishes its evidence. It does not reset043/044 reservations or repeat their measured component rows. The next resource step still needs a consolidated fixture specification covering complete acquisition, every diagnostic operation, and their retained-object overlap before any complete-work profile is requested.
