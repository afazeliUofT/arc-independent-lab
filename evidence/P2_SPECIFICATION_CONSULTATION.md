# Phase 2 specification consultation

**2026-09-06. Shared tools and filesystem; not an independent reviewer or a formal gate verdict.** Read `docs/P2_OPERATION_SPECIFICATIONS.md` in full after the PI reported the raw population frozen. This consultation concerns implementability, diagnostic fit, and the diversity claim only. No literature search, novelty comparison, candidate experiment, affordability judgment, or screening was performed. The PI is separately refining C2's probabilistic transition notation; observations below distinguish that known revision from additional issues.

## Overall judgment

All four drafts identify the objects they alter, the upstream structure they require, a persistent state, and an intended diagnostic intervention. They are sufficiently concrete to expose real differences and remaining failure cases. Positive regularization makes C3's stated solve unique. C1's deterministic consistency rule deliberately declines noisy extensions. These are useful specification boundaries; they should remain explicit rather than receiving silent implementation repairs.

One definite logical error requires correction before the specifications are frozen: C4's explanation of an unresolved scope assumes an inseparable witness pair that need not exist. C2 also needs explicit treatment of impossible transcripts and branch-dependent costs, alongside the already planned transition-kernel refinement. The other observations below are bounded interface choices, not reasons to abandon the operations.

## 1. C4: failure to find a bounded conjunction does not certify an inseparable pair

The update requires a conjunction of at most k supplied atoms that accepts the seed and excludes every contradictory witness. The next paragraph says that failure should expose a positive/negative pair that current atoms cannot separate. That implication is false.

**Counterexample, our deduction.** Supply atoms x1, x2, x3 and seed 111. Let the three negative descriptors be 011, 101 and 110, and set k=2. Each negative is individually separable from the seed: x1 excludes the first, x2 the second, x3 the third. Every conjunction of at most two atoms nevertheless admits a negative. The full three-atom conjunction separates all witnesses. There is no required inseparable pair; the obstruction is the permitted conjunction length.

There is a second distinction. If atoms are usable only positively, differing atom truth vectors need not be separable by a seed-accepting conjunction even with unlimited length. For seed 00 and negative 11 with A={x1,x2}, none of the nonempty conjunctions accepts the seed. This is an expressive restriction of the condition language. It is not observational aliasing of the complete descriptor supplied by A.

**Required clarification.** Return `unresolved` with an explicit reason or witness-set certificate. Distinguish at least:

- A negative has exactly the same complete atom truth vector as the required seed: those supplied tests do not distinguish them.
- Distinguishing observations exist, but the allowed conjunction language or length bound cannot express a separator.
- Inputs needed to evaluate the declared tests are missing.

The first case can justify reporting a concrete observational ambiguity upstream. The second cannot honestly be described as evidence that a new perceptual distinction is missing. The existing operation may remain unresolved in every case; changing k, adding negated tests, or expanding A still requires an explicitly new version. No particular extension is recommended here.

Only the seed is mandatory positive coverage under the current objective. A conflict with an optional positive does not by itself establish that no admissible seed-containing condition exists. The certificate should respect that asymmetry.

## 2. C2: specify the belief update, unexpected transcript, and realized allowance

The current draft says each h predicts a transcript and a post-experiment state while also allowing probabilistic beliefs and transcript likelihoods. A transition kernel over `(transcript, successor state)` is the appropriate type-level clarification when the same starting hypothesis permits more than one successor for a transcript. The PI has already identified this issue. Posterior mass must flow to successor states rather than only reweighting a fixed identity while choosing an unspecified single successor.

Two additional choices matter even with that clarification:

**Zero predicted probability.** State what happens if the actual transcript has zero probability under every live model. Bayes' rule then supplies no posterior. The global typed `unresolved` convention is useful, but the implementation still needs to know whether the previous belief is retained only as an invalidated record, whether action selection stops, and what allowance has already been spent. It must not quietly renormalize, skip the observation, or restart a prior.

**Hard allowance versus expected cost.** The acquisition criterion penalizes expected cost. A policy tree can have acceptable expected cost but a branch exceeding the remaining interaction allowance. Define permitted execution by either a branchwise bound or an explicit abort/truncation rule that is included in the predictive experiment model. Charge the realized branch cost after execution. This concerns the mathematical experiment interface, not whether the programme can afford to implement it.

The value expression correctly includes changed physical state in final decision loss. That creates a useful diagnostic caution already acknowledged in the draft: maximizing the criterion can prefer a task-changing action whose gain is not information acquisition. The B2 attribution therefore needs the transcript and fixed-downstream-learner intervention described in the specification. A positive computed acquisition score alone should not be labeled information value.

## 3. C1: give resets a complete type and preserve inconsistency explicitly

Normal action-observation updates are executable as written. The live-pair set is sufficient for the declared deterministic family; retaining the program definitions is correctly counted.

The world-reset paragraph delegates the reset to an external declaration. That is an acceptable supplied interface if its type is made explicit: for example, a reset relation mapping each live `(h,q)` to allowed successor states without changing h. Retaining only the surviving h identifiers and applying all of their original initial states is a specific reset assumption, not a generic reset. No arbitrary reset inference is required in Phase 2.

Clarify that an empty survivor set and its inconsistency flag remain unresolved through ordinary query/update calls. If a later reset can restore consistency, that restoration must be part of the declared reset semantics and cannot be a silent refill from H0. The current text strongly suggests this behavior but leaves the interaction of reset and the flag implicit.

This is diagnostic bookkeeping, not a proposal for a recovery mechanism. Unknown reset semantics may remain an explicit failure condition.

## 4. C3: sufficiently specified at this phase, with a narrow attribution boundary

The stored anchors, reference activations, old reader, translation and refresh solve are explicit. The candidate correctly counts reference activations as historical information rather than describing them as label-free recovery from current weights alone. Fixed positive lambda removes rank-deficiency ambiguity in the linear solve; insufficient rank can still limit what the translation accomplishes.

The remaining refresh interval, anchor-selection rule, numerical tolerance and resource constants are ordinary parameters explicitly deferred to Phase 3. They need not be chosen to conduct this ideation consultation. The formal operation remains a family indexed by those parameters until they are frozen.

The important diagnostic distinction is already present: training the translation on historical reference activations can improve old answers without demonstrating that a usable old distinction remained in current weights independently of the retained references. Queries beyond anchors and a comparison that removes the alleged current representation distinction are necessary to interpret the proposed access claim. This note adds no new experiment and does not certify that the proposed controls will isolate every mediator.

## 5. Do C1 and C4 count as distinct moves?

**They are distinct narrow interventions, but belong to one broad relation-selection family.** C1 retains multiple complete executable explanations and exports their unresolved predictive disagreement. C4 receives a fixed target relation and constructs a single condition under which it will be used, keeping contradictory encounters in the fitting constraints. C4 does not preserve all consistent scopes, and C1 does not explicitly optimize a local applicability condition. Their effects can therefore differ on identical evidence.

That is enough to keep both specifications visible as separate candidates. It does not make them four wholly orthogonal ideas when counted together with C2 and C3. Both rely on supplied representational languages and consistency with observed evidence; both primarily address B1. The difference should not be justified solely by saying one object is a “world” and another a “rule.” The differing state update and output behavior is the defensible distinction.

**Conservative diversity accounting:** four developed operations across three broad intervention families: preserving/limiting learned relations (C1/C4), changing evidence acquisition (C2), and changing access through the old response interface (C3). Even counting C1/C4 together leaves three underlying families, satisfying the requested 3–5 breadth without inflating diversity. No forced merge or candidate deletion is needed. A later combined implementation would still need to separate their contributions before assigning a cause.

This is not a novelty claim or an assertion that other methods do or do not contain these operations. No such comparison was made.

## Scope of the consultation

Only this new consultation note was written. The specification, raw population, diagnosis, state, code and earlier evidence were not edited. The logical examples above are deductions over the declared interfaces, not empirical results. The note does not decide a scientific gate, authorize Phase 3 execution, or claim an enforced reviewer boundary.

## Revision readback during this consultation

After the observations above were sent, the PI revised the specifications. I read the affected passages; this is a correction record, not a claim of separate independent review.

- **C4 resolved the definite logical error.** Tests are now total Boolean functions, both polarities are allowed, and only seed-compatible literals enter a condition. An impossible bounded separator is distinguished by full-signature equality (`observational_aliasing`) versus an insufficient length bound (`length_bound`). With both polarities allowed, the full seed-compatible conjunction separates the seed from every negative with a different signature; that makes the stated distinction valid. The earlier positive-only language counterexample no longer applies. Missing requisite fields are excluded at admission. The original finding remains recorded above to explain the change.
- **C2 now supplies the joint kernel** Q_e(hprime,z|h), updates posterior mass over successor states, and returns `model-inconsistent` for an actual zero-probability transcript. This resolves the main state-transition ambiguity and establishes an explicit failure outcome. The branchwise interpretation of a hard remaining allowance and charging realized cost are still worth an explicit sentence; expected-cost penalization alone does not enforce the allowance.
- **C3 now gives W dimensions and the multiplication order** f_theta(x) T W, with fixed postprocessing and its reader cost. This is an adequate type clarification.
- **Diversity is now described conservatively** as four operations spanning three broad causal families. No merge or invented extra family is required.

No new search or experiment was undertaken for this readback. The remaining C1 reset and C2 hard-allowance clarifications are interface issues. Parameters already explicitly deferred to Phase 3 do not need to be assigned solely to close this consultation.
