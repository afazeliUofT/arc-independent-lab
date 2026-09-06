# Learner-access follow-up: recovery succeeds within the supplied model

Completed 2026-09-06 under the explicit follow-up in the human Phase 1 approval. This is an append-only diagnostic report, not a change to the approved `DIAGNOSIS.md`, a mechanism trial, or an independent verdict. Original diagnosis and reproduction inputs remain unchanged.

**The strongest access condition succeeds.** A newly programmed generic reader recovers the old boundary estimate using current weights and unlabeled features obtained from the learner's own supplied, executable feature map. It does not need an evaluator's coordinate-difference formula, an old label, a saved boundary estimate, a geometry ID, an arm ID or additional experience-dependent persistent memory. Coordinate transformations preserve this result.

That answers the original access objection more favorably than the approved diagnosis alone established: the hidden distinction is computationally usable under the learner's existing model structure. It does **not** establish that the ordinary learner invents, chooses or invokes this computation. The supplied zero-initialization, fixed-map and sequential rank-one update contract is still decisive. The evidence strengthens the **local accessibility claim**, not the prevalence or ranking of this bottleneck across current AI.

## What was fixed before execution

The [prospective protocol](../docs/followups/P2_LEARNER_OBSERVER_PROTOCOL.md) separates current model structure, additional surviving update traces and a deliberately stripped information view. Its config and source were frozen before the run in [`evidence/P2_LEARNER_OBSERVER_PROTOCOL_FREEZE.json`](../evidence/P2_LEARNER_OBSERVER_PROTOCOL_FREEZE.json), SHA-256 `eb308135cee0b1aefd9215cc35a1dbbb0cf43e7f4fc8854a1424b5d1df8f9588`. No cases or arithmetic tolerances were revised after execution.

The underlying predictor retains its original training observations, learning rate, context schedule and update rule. The readers are counterfactual computations that never alter that trajectory. Same-state recovery uses the learner's current encoder, which is already supplied structure required for ordinary prediction; permitting an unlabeled encoding of the other known context is not an additional world observation. In the original source this callable structure sits in `feature`/`predict` rather than inside the minimal `learner_step` function. Restricting access to `learner_step`'s argument list alone would remove part of the original model definition, so that narrower condition is reported separately.

## Observed results

Every number in this table is derived from [`artifacts/P2_LEARNER_OBSERVER/20260906_001/results.json`](../artifacts/P2_LEARNER_OBSERVER/20260906_001/results.json), SHA-256 `9c6c95c115e9d350e26c43707092c65208020eac9b02b91d389d335fa3febd08`; each recovery step is a B-stage readout, not an independent sample. Local access 2026-09-06.

| Family | Cases | Successful API readouts | Successful trace readouts | Maximum API error against boundary | Maximum trace error against boundary |
|---|---:|---:|---:|---:|---:|
| Original crossings and coordinate changes | 48 | 3072 | 3072 | 8.88178e-16 | 1.22125e-15 |
| Collinear controls | 4 | 0 | 0 | abstains | abstains |
| Ambiguous-history pair | 2 | 128 | 128 | 4.44089e-16 | 2.22045e-16 |

The identity-map follow-up matches the original weights, deltas and ordinary predictions with maximum absolute difference `0.0`. The largest API error and trace error above are ordinary floating-point residuals against a prospectively declared arithmetic tolerance of `1e-10`. All original protected inputs remain byte-identical. These are artifact and arithmetic checks, not scientific gate scores. Source: [`artifacts/P2_LEARNER_OBSERVER/20260906_001/results.json`](../artifacts/P2_LEARNER_OBSERVER/20260906_001/results.json), SHA-256 `9c6c95c115e9d350e26c43707092c65208020eac9b02b91d389d335fa3febd08`; local access 2026-09-06.

Complete learner observations, actual weight deltas, span updates, every reader input/output and evaluator-only comparisons are in [`artifacts/P2_LEARNER_OBSERVER/20260906_001/transitions.jsonl`](../artifacts/P2_LEARNER_OBSERVER/20260906_001/transitions.jsonl), SHA-256 `409e2eb4095d2358ae3ac53e379c3c273288f5d604c5c01ced63e704bd452b7d`; local access 2026-09-06. The result file records ordinary old-readout failures alongside successful recovery; the original training behavior was not improved by the diagnostic.

## Why the API result is possible

For supplied old and new feature vectors `a,b`, zero initialization followed by old-only updates puts the boundary state in the span of `a`. New-only updates add a vector in the span of `b`. The reader computes from its current feature API a vector orthogonal to `b`, projects the current weights onto it, and divides by the corresponding projection of `a`. It obtains the old coefficient and converts it to the current old-query prediction. This is a generic projection calculation, not an original-coordinate formula.

The caller supplies no old target or retained old prediction. The mathematical relation is chosen by the researcher; the original SGD learner does not discover it. Fixed rotations and a reflection challenge dependence on the original coordinate formula, while preserving the same underlying geometry. They do not challenge fixed linear features, known context labels or the rank-one training contract. Where the two feature directions are collinear, these readers correctly abstain because their decomposition is singular. This is not a universal impossibility result for an algorithm allowed additional priors such as the finite evaluation gain codebook.

## What additional update memory changes

The second reader learns canonical unit bases from the actual A and B weight-delta stream. It never receives the response, target, gain, old boundary weights or subsequent context's feature-map setup. Basis normalization discards update magnitude; canonical orientation discards its global sign. The current old query is still supplied when it must be answered. The reader decomposes current weights into the learned old/new spans and reads out the old component.

This conditional reader adds at most four floating scalars of geometric state plus rank/context metadata in these cases, beyond the predictor's two weights. Those are logical scalar counts, not a measured Python memory footprint. The declared budget is in [`configs/P2_LEARNER_OBSERVER.json`](../configs/P2_LEARNER_OBSERVER.json), SHA-256 `87e452f0c05381aee1451bdbc05a60567fc8295089d27ef85bfbd7a5f8d281c1`; local access 2026-09-06. It is not a memory saving over storing a boundary estimate in this small system, and it does not establish spontaneous selection of what to retain. Its success is a separate access condition, not support smuggled into the same-state result.

## What removing both sources of geometry changes

The erased view retains only current weights and the current unlabeled old query. It removes both the span trace **and the other context's callable feature map**, so it is strictly weaker than the original supplied-map learner. We constructed two histories from the same old-gain evaluation family and the same new gain, with different unknown B feature directions. Their exact-arithmetic final weights and old query coincide, but their required old boundary predictions differ. Consequently no function of that stripped input alone can return the correct answer for both histories.

The numerical pair's maximum final-coordinate discrepancy is `4.971066960846038e-17`, while its boundary predictions differ by `1.9976419630844524`. Their old queries match and their B features differ. Source: [`artifacts/P2_LEARNER_OBSERVER/20260906_001/results.json`](../artifacts/P2_LEARNER_OBSERVER/20260906_001/results.json), SHA-256 `9c6c95c115e9d350e26c43707092c65208020eac9b02b91d389d335fa3febd08`; local access 2026-09-06. The exact derivation is in the prospective protocol; floating-point closeness alone is not an information-theoretic proof. No continuous old-gain family is needed for the construction; the B geometry class is deliberately broader than the original three arms. The full API reader and surviving-span reader distinguish these histories and recover their separate boundary estimates.

This negative boundary result therefore does not refute the positive original-access result. It identifies information that would have to remain available if the model's own callable map were removed.

## Strongest alternative explanations and checks

- **The answer remains engineered into supplied structure.** Correct in a qualified sense: the feature map and training contract remain supplied. The generic readout computes the relation without the evaluator's original coordinate formula. The coordinate changes and collinear controls test formula dependence and rank conditions, but do not establish a discovered ontology or broad adaptability.
- **Additional memory, rather than original-state accessibility, explains success.** That applies to the span reader. The separately reported API reader retains the original experience-dependent state budget and succeeds without that trace. It still spends additional transient computation and uses the supplied model.
- **The evaluator leaks an old target or boundary estimate.** Reader signatures and full calls contain neither. A post-execution check independently compares readouts with the training recurrence, verifies actual deltas and canonical span geometry, and checks original hashes. It is ordinary same-process instrumentation, not an enforced security/data-flow boundary or independent review.

The post-execution consistency receipt is [`evidence/P2_LEARNER_OBSERVER_CONSISTENCY.json`](../evidence/P2_LEARNER_OBSERVER_CONSISTENCY.json), SHA-256 `8b6797ed549b8f7eb35a626a270c6a4e046b1b53b0b8e9b5f40cdf7841816062`. It passed its declared artifact checks. The raw run completed with `6912` training interactions in `0.4210946059974958` seconds internally, with no model calls, GPU or HPC use. Run/resource source: [`artifacts/P2_LEARNER_OBSERVER/20260906_001/manifest.json`](../artifacts/P2_LEARNER_OBSERVER/20260906_001/manifest.json), SHA-256 `b2f06a14433f546ea24d2f49990d38c13ec7b8e1ed945c9b8e09ac17927acac9`; local access 2026-09-06. This tiny diagnostic offers no reason to reserve cluster resources for it; no inference about later programme requirements follows.

## Consequence for the programme

The earlier caution about supplied geometry was valid, but supplied model structure should not be conflated with an evaluator-only secret. Under the original full model interface, the missing readout can be explicitly computed. The fixed ordinary readout still fails in the relevant cases, so the local cause is now more clearly an available computation absent from the ordinary prediction path. What remains unestablished is autonomous recognition of that need, discovery of the right recovery computation, and prevalence in systems facing the funded conjunction.

Do not automatically promote rank 3 on this evidence. Preserve the approved ranking and carry this narrower correction forward. The diagnostic is complete; it supplies no novelty or feasibility veto on Phase 2 ideas.
