# First diagnostic reproduction: performance loss without erasure of the old estimate

**Phase 1, P1.1; 2026-09-06. Exploratory diagnostic witness, not a mechanism trial, benchmark replication or independent verdict.**

The standard old-context readout deteriorates during learning in another context, while a fixed observer can still recover the previously acquired estimate from the same weights. The result makes an inference invalid: poor old-task performance alone cannot establish that all useful old information was erased. It does not show that this distinction explains most current AI failures.

## Evidence and reading order

The prospective reasoning is in [P1_REPRODUCTION_DESIGN.md](../docs/P1_REPRODUCTION_DESIGN.md). It was recorded before execution, including the normalized feature geometry, gain crossing, frozen and orthogonal controls, analytic predictions and limits. It was not remotely locked as a Phase 3 preregistration, and no formal gate threshold was applied.

All project-result numbers in this report are drawn from these immutable artifacts, accessed locally 2026-09-06:

- **R:** `artifacts/P1_LINEAR_INTERFERENCE/20260906_001/results.json`, SHA-256 `837b6ce92176182d1e2878f585388824d3b0173d2585e69c749243ac0a626762`.
- **T:** `artifacts/P1_LINEAR_INTERFERENCE/20260906_001/transitions.jsonl`, SHA-256 `908f4b073a63a0c7019fe65173b461a2fc7f7ad0b51d68f05e7cfc083308a3a4`.
- **M:** `artifacts/P1_LINEAR_INTERFERENCE/20260906_001/manifest.json`, SHA-256 `9337e7dbb3f0ee034e01fdd0bc595b4a8e9bffc2cbe5059785990cc77c2c4783`. M pins the executing code, prospective design, configuration and dependency lock.

R contains every crossed case; T records every observation, update, ordinary readout, observer decode and old-loss change. M honestly records a dirty working tree based on the already verified human commit, with exact source hashes. No later commit is claimed to have existed before the run.

## What the learner was asked to do

A scalar action produces a response whose unknown gain depends on a visible context. Train in A, retain the weights, switch to B and continue learning. The learner receives only the current feature vector and response. The complete learned persistent state is two weights. It has no replay, optimizer buffers, retained prompt, hidden context state or external memory.

The shared feature map is `(1,0)` in A and `(1,1)/sqrt(2)` in B, multiplied by the current action. The model class can express both context gains exactly: for gains `m_A,m_B`, weights `(m_A,sqrt(2)*m_B-m_A)` do so. Insufficient representational capacity is therefore not the cause of this constructed failure. Nevertheless, fitting B alone does not require returning to that joint solution.

**The world is deliberately easy.** One noiseless action reveals its context gain to a suitable estimator. Gradient fitting is imposed by our learner; its slow acquisition is not an information limit. Context identity and the feature map are supplied. Predetermined alternating actions do not pose an exploration problem. This witness covers intervening-learning interference, not discovery of unknown causal factors or novel recombination.

The crossed design uses the positive and negative gain in each context, with the same fixed learning schedule across arms. Configuration values and resource limits are specified in M's pinned config. Actual execution used 1536 training interactions and 3072 non-updating observer probes, with no experiment-time language-model calls. [R, M: paths and hashes above.] There is no stochastic seed uncertainty to estimate.

## Observed trajectory

The following slice fixes old gain positive and new gain negative. Predictions and decoder outputs are for unit positive action. All values are rounded; complete values are in R and T.

| Arm | Old prediction at boundary | Final old prediction | Final new prediction | Observer's recovered old estimate | First B update with wrong old sign |
|---|---:|---:|---:|---:|---:|
| shared_normalized | 0.998821 | -0.206274 | -0.997988 | 0.998821 | 17 |
| orthogonal_control | 0.998821 | 0.998821 | -0.998821 | 0.998821 | none |
| frozen_after_A | 0.998821 | 0.998821 | 0.706273 | 0.998821 | none |

**Table evidence:** R and T, paths and SHA-256 digests above; cases `case_02`, `case_06`, `case_10`. A wrong sign is a descriptive event, not a retrospectively chosen gate criterion.

The mirrored opposite-gain case exhibits the corresponding reversal. Shared-feature cases with same-sign gains also lose old predictive accuracy, but retain the correct sign; they are not discarded. Orthogonal controls preserve the old readout while fitting the new one. Frozen controls preserve the old readout but deliberately fail to acquire the new rule. [R, T: paths and hashes above.]

## Where the failure occurs—and what never becomes inevitable

At the boundary write the weights as `(k,0)`. A shared-feature B update changes both coordinates equally, leaving `theta0-theta1=k`. The ordinary A prediction reads `theta0`; it changes during B learning. The observer instead reads the invariant difference. It receives only the arm and current weights; old labels, prior samples and the boundary snapshot are excluded from its inputs. The old/current gain crossing rules out a fixed positive or negative answer as the explanation.

For opposite gains, the first B update moves the ordinary A readout farther from its old target. The sign reversal occurs later, at the trace event reported in the table. That is the onset of a particular behavioural error, **not a point at which the old information becomes irrecoverable**. Its boundary estimate remains recoverable throughout the observed B trajectory. The experiment therefore does not contain a last irreversible information-loss event to locate. Calling the sign crossing such an event would overstate what was measured. [T, R: paths and hashes above.]

The exact old squared-loss change decomposes into `(theta0-m_A)*delta0 + delta0**2/2`. This identifies the update's effect beyond an endpoint comparison and avoids treating a zero first-order gradient as proof of no interference. Closed-form trajectory and invariant checks use the full recorded weights; their numerical residuals are in R, not inferred from a plot.

## Strongest alternative explanations and their status

**Observer leakage or a hardcoded answer.** The decoder is isolated at the function-input level and checked across both old gains and both new gains. The evaluator does possess truth and a boundary snapshot for scoring, but does not pass either to the decoder. This is inspectable source structure, not an independently enforced process boundary. The observer has supplied geometric and initialization knowledge; its success does not mean the original predictor knows how to recover its old estimate.

**Different capacity or extra experience in the successful control.** Both trainable maps use the same dimension, feature norms, action/response schedule and representable function class. However, the reparameterization changes the optimization metric and the B starting prediction. This control supports a geometry-dependent update explanation here; it does not establish an efficiency ranking, automatic factor discovery or a proposed repair.

**A broken learner or a reset secretly deleting weights.** The frozen arm receives the same B stream without changing its old weights, and the orthogonal arm fits both contexts. The recorded continuity and update equations localize the shared-arm failure to B updates. A shell process was not restarted; across-process retention is not being claimed.

## What changes in the diagnosis

The phrase “failed to keep knowledge” must be unpacked into the surviving information, the prescribed access path and the resulting decision. Even a transparent learner can separate these. This is compatible with a plasticity-control explanation of performance, but does not establish storage erasure or make plasticity control the dominant bottleneck. It says nothing by itself about scaling.

The next useful work is to apply the same distinction to stronger published evidence on active acquisition, longitudinal retention and held-out recombination, including counterexamples. More runs of this deterministic witness would not answer those questions. Phase 1 remains incomplete.

## Completed verification

The saved artifacts passed arithmetic, continuity, control, hash and summary-consistency checks. The audit reads the trace independently of the experiment runner and statically inspects learner/decoder interfaces; it does not execute the learner to recreate the reported answer. Receipt: `evidence/P1_REPRODUCTION_AUDIT_20260906_001.json`, SHA-256 `0fec7f01bcec518ad0f14ae26fd4591744e25dd7475e043fbf5512670b67bab4`; accessed locally 2026-09-06. This is same-workspace checking, with the limits listed in the receipt. It is not a scientific verdict or evidence of enforced reviewer isolation.
