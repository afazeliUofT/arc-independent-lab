# A first comparison of acquired descriptions and experiment allocation

Date: **2026-09-12**. Status: **prospective scientific specification; nonexecutable; no treatment results**. This document takes the next design step recommended by the original checkpoint040 reviewer. It is not `PROGRAMME.md`, a frozen preregistration, an independent verdict, or permission inferred from `GO` to run a candidate. Numerical execution allowances, instance sampling, inferential thresholds, implementation and cost profiles remain to be fixed before a later experiment. The frozen035 operations and the original040 verdict are unchanged.

## 1. The decision this comparison can resolve

The immediate question is whether N3's local prediction-based feedback obtains evidence that lets N1 construct a useful historical distinction sooner, under a common finite allowance, than an otherwise matched selector without that feedback. The distinction must subsequently change a decision in a composition absent from acquisition. Success would justify investigating this bounded acquisition route further. Failure could identify an unhelpful credit signal, an inadequate description rule, insufficient evidence or an unsuitable instrument. Those are different outcomes.

This follows the diagnosis's separation of **which observations are acquired** from **what relation is learned from adequate observations**. It does not estimate the prevalence of either failure in contemporary AI. The approved diagnosis remains the scientific anchor; its original submission banner is historical. No memory deletion, interference, new physical block or long-gap process occurs here. Consequently even a positive result would leave the funded retention demand open. [S1, S2]

N1 is already normalized locally to unit-cost greedy pair coverage. N3 supplies a particular feedback and composition policy; it has no validated global novelty or efficacy claim. We are testing the utility of this explicit coupling, rather than treating its names as evidence of a new mechanism. The reviewer accepted the bounded analytical assessment and recommended **specification**, not a treatment run. [S3, S4]

## 2. A concrete initial instrument

### 2.1 Unknown deterministic world

Use a finite, stationary, resettable transducer with a hidden binary register `x` and a visible token `o`. The learner receives one categorical observation field and five opaque primitive-action indices. It receives five opaque observation-token indices. Only the evaluator knows which indices have the following roles:

| Evaluator role | Physical effect | Returned observation role |
|---|---|---|
| `SET_0` | Set `x=0` | `CUE_0` |
| `SET_1` | Set `x=1` | `CUE_1` |
| `MASK` | Keep `x` | `NEUTRAL` |
| `PROBE_0` | Keep `x` | `MATCH` if `x=0`, otherwise `MISMATCH` |
| `PROBE_1` | Keep `x` | `MATCH` if `x=1`, otherwise `MISMATCH` |
| Paid `RESET` | Restore the fixed initial register and observation of this block | `NEUTRAL` |

All action-role and observation-role bijections are admissible world instances; either register value may be the fixed initial value. The same instance is used for all paired arms. Role names above never enter learner state, prompts, action names, features or observation annotations. The learner receives the complete declared observation alphabet, including all five opaque token indices even if some have not yet appeared. It receives no indication that one token will become a MATCH or MISMATCH goal until the acquisition freeze. There is no reward channel during acquisition. It receives the N1–N3 grammar and finite interface, not this transition table, the hidden register or a supplied correct test. A recorded trace is just the permitted tokens, issued actions and boundaries.

This is an intentionally transparent diagnostic family. Its regularity makes the information requirement inspectable: after `SET_b, MASK`, the present observation is identical for both register values, while the correct probe for a later `MATCH` goal differs. A predicate involving the previous cue can distinguish those histories. This is a mathematical property of the specified instrument, not a measured discovery by N1. Whether the exact online greedy rule selects and uses an adequate predicate, and whether N3 obtains the needed contrasts efficiently, remain open.

The permutations mainly test sensitivity to supplied serialization and tie order. They are not independent causal laws or evidence of cross-domain transfer. The family also supplies strong representational support: finite tokens, deterministic resets and a short relevant history. A positive result cannot establish discovery of perception, physical action primitives, arbitrary latent causes or unrestricted compositional semantics.

### 2.2 Future demand and held-out composition

Acquisition receives no target goal. After the acquisition snapshot is sealed, the evaluator presents either the opaque `MATCH` token or the opaque `MISMATCH` token as the desired next observation. Both goals belong in the prospectively fixed evaluation panel. They are revealed only to the common downstream chooser, after acquisition.

Each evaluation history is produced by paying for a real `RESET`, executing a preparation word `u`, then `SET_b, MASK`. The chooser sees the resulting ordinary observation/action history and chooses one primitive action. The evaluator measures whether that next observation equals the revealed goal. It does not give the chooser hidden state, role labels or a menu restricted to the two correct probe types.

The panel contains both values of `b` and both goals, under the same predeclared set of preparation words. Default preparation length is `L+V`, where `L` and `V` are the acquisition parameters. Hence the history word ending in `SET_b, MASK` has length `L+V+2`, exceeding every possible acquisition episode of a trial followed by its validation block. Every next trial pays for RESET, and lags cannot cross that boundary; concatenating traces from different trials cannot defeat the length argument. No exact evaluation history can already be an acquisition history. This is a structural absence guarantee, not a filter applied after seeing which arm acquired which data.

At the query, N1's current observation is NEUTRAL, observation lag one is the final setter's cue, action lag one is MASK, and action lag two is the final setter. Observation lag two is the final observation of `u`. Those terms have exactly the frozen035 meaning; the action about to be chosen is a separate prediction-key argument. The sufficient historical distinction may therefore be learned from an opaque cue or a past action equality. The long whole history is held out, but its useful short history terms need not be. In particular, the full `W`-window reader may already generalize across some or all panel cases. That is an informative comparator outcome, not grounds for removing those cases after measurement. [S2]

Preparation words are fixed from opaque action indices before acquisition, independently of arm behavior and outcomes. Their explicit finite membership and weighting must be committed with the eventual instance panel. They should include preparations that overwrite the register and make its earlier value differ from the final setter; the relation tested is that the most recent setter remains predictive through masking despite that earlier composition. Evaluator role information may be used to construct this declared diagnostic contrast, never to annotate a learner's history. The same preparation/goal panel is given to every arm.

The claim is deliberately limited: reuse of an encounter-selected historical distinction in new whole histories composed from familiar primitives. A longer word alone is insufficient evidence of useful recombination. The provenance and same-trace interventions in section 5 must show that the acquired distinction controls the later decision. This instrument does not test learning a substitution algebra or composing independently learned high-level procedures. If that stronger demand is required for the next programme claim, a different instrument must be specified before results; success here cannot silently stand in for it.

### 2.3 Design defaults and unresolved feasibility

The concrete starting grammar defaults are `W=2`, `S=3`, `K=4`; word and validation defaults are `L=5`, `V=2`, `q=4`. These are proposed instrument choices, not measured optima or frozen thresholds. They permit a short historical equality test and leave additional predicate slots; none assumes that the greedy learner will spend those slots well. The original grammar's size conventions and all tie rules apply exactly. [S2]

Do not execute a treatment using these defaults yet. Before freezing the experiment, establish by specification analysis that the proposed history contrast is representable, that distinguishing trials are affordable under the eventual allowances, and that the evaluation reader can use a completed N1 snapshot. The exact finite instance/preparation panel, common `B_env`, `B_comp`, `B_mem`, serialization/accounting convention and runtime bounds are still design dependencies. Their selection must not be informed by a candidate's target success rate. No new paper is needed to settle these local semantics.

## 3. Common downstream reader and information boundary

At the acquisition stop, serialize the entire declared persistent state, with hashes and actual resource consumption. Freeze the N1 predicate list and active transition/count table. Evaluation histories do not append to the acquisition table, create constants, resume selection, add predicates, fit counts, credit recipes or grow libraries. The history supplied for the current decision is evaluation input, not additional training. Each panel decision begins from the same frozen acquisition snapshot.

For every permitted action `a`, the common chooser calls the frozen `Predict(history,a)`, selects the largest probability of the revealed goal token, and breaks ties by the original action-index order. It has no simulator, planning oracle, recipe-to-role map or auxiliary learned policy. The observation-space size and add-one smoothing are exactly N1's. `UNSEEN_KEY` is a defined numeric prediction; `COMPUTATION_INCOMPLETE` is not. If a required prediction cannot be computed within its evaluation allowance, emit `DECISION_UNAVAILABLE`; preserve its cause and charge the work. Do not replace it with a secretly favorable tie action.

Evaluation preparation, its RESET, all history bytes, all action predictions and the single selected action are charged in a separate identical per-decision evaluation allowance. Acquisition and evaluation costs are reported separately and in total. Different states reached during acquisition do not change the evaluation panel. No acquisition process reads target outcomes, and no later panel item can train from an earlier one.

This reader is intentionally weak enough to expose whether the learned description is useful to the specified predictor. A failure need not show that no other reader could exploit the full stored history. A separately budgeted same-trace full-history reader is a diagnostic comparator in section 5, not extra help given only to N1–N3.

## 4. Arms and what their comparisons mean

Every acquisition arm starts from empty N1 state in the same block, completes the same primitive warm-up, obeys the same interface, history/grammar limits, paid RESET contract and hard resource ceilings. All arms make the same type of validation interactions and frozen before/after predictions, so disabling feedback does not remove that source of evidence or make an environmental call free. Validation results can be retained as observational provenance even when a control never uses them to prioritize or promote a word. The original N1 learning rule is unchanged.

| Arm | Next-word selection | Post-warm-up macros | Role in the comparison |
|---|---|---|---|
| `FULL` | Exact N3 utility priority, mutation grammar and coverage cadence | Exact positive-credit promotion | Frozen candidate [S2] |
| `MACRO_OFF` | Same utility priority and mutation/coverage rules | Keep only warm-up primitive macros | Single change from FULL: disable promotion |
| `FEEDBACK_NULL` | Same mutation/coverage code, but every proposal priority is zero | Warm-up primitive macros only | Single change from MACRO_OFF: disable utility-to-priority feedback |
| `COVERAGE` | First uncompleted primitive word in length/lexicographic order | No promoted macro used | Direct coverage implementation and cost comparator |

`FEEDBACK_NULL` still computes the common validation diagnostic but it cannot use the observed utility for selection or promotion. Logs must distinguish a shadow diagnostic from an operative proposal score. The paired `FULL` versus `FEEDBACK_NULL` endpoint is a total feedback-package contrast. It does not by itself identify which edge caused any difference. The nested contrasts isolate promotion with priority present, and priority with promotion absent. They do not establish an interaction effect or priority's effect under growing macros; a claim about either needs a prospectively added comparison.

**A schedule identity prevents a false baseline count.** Before resource or computation interruption, FEEDBACK_NULL's proposed word is exactly COVERAGE's word. Warm-up puts every primitive in `F` and `M`. Inductively let `w` be the first uncompleted word in length/lexicographic order. If it is not primitive, its nonempty shorter prefix was completed and is in `F`; insertion of its final primitive therefore proposes `w`. No uncompleted proposal can precede the globally first uncompleted word. Zero priorities use that same length/serialization tie rule, and coverage slots agree. Adding extra macros would not change this zero-priority argument. This deduction concerns selection order, not equality of computation costs. [S2, deduction in this document]

Thus the null and coverage arms are not two independent pieces of behavioral evidence. Their full trace should agree when both can finish the required work; a divergence before a documented boundary is an implementation or accounting question. Direct coverage can save proposal-enumeration work and may consequently progress farther under a common computation allowance. Those savings are relevant, not something to pad away. Include both records only where their implementation/cost distinction is being measured; do not inflate a success count by treating their common schedule as independent.

**Ungated Brier arm:** deferred. The first decision concerns the utility of the frozen loop, not whether a different credit gate repairs it. The accepted constant-world witness already shows that the current gate deliberately excludes count-only progress. If subsequent design makes gate-versus-count credit the actual question, add an otherwise identical ungated arm prospectively, with its own accounting and hypothesis, before any result used for that comparison. Do not introduce it after seeing an unfavorable FULL result and call it the original candidate. [S3, S4]

## 5. Acquired knowledge and causal diagnostics

The primary endpoint is later target-observation success of the common chooser. Pair coverage, library size, a positive local Brier difference or a filled predicate slot are diagnostics, not substitutes. Each claimed useful distinction needs an auditable chain:

1. The actual N3 trial and previous observations created a conflicting pair under the earlier partition.
2. N1 selected a specific executable predicate during a complete pass, with the exact histories, grammar constants, gains, ties, table version and spent work recorded.
3. Its provenance identifies whether the selecting experiment descended from a credited word or an acquired macro; a word's mere presence in `F` does not establish feedback dependence.
4. The predicate has different values on the paired held-out histories, and its use affects the common chooser's forecast or selected action in the needed direction.
5. Matched-data controls below separate that contribution from extra observations, a supplied answer or a favorable incidental partition.

### 5.1 Separate an allocation effect from a representation effect

Allocation arms are allowed to acquire different traces: this is the intervention. Replay each acquired trace, in its original order and at its original update boundaries, through the same N1 specification to check that the recorded description follows from those data. Charge replay as diagnostic analysis; do not return its newly computed state to an acquisition arm or give one arm free training compute.

For representation attribution, hold a single trace fixed. Compare its selected N1 partition with an empty-predicate current-observation/action partition, using exactly the same retained transitions, outcome alphabet, add-one formula, history input and chooser. Also specify a full permitted-history count reader using the exact typed `W`-window as its key, with identical data and a common computation/memory allowance. The latter can expose whether N1's selected abstraction helps reuse beyond literal history matching, or whether ordinary history conditioning explains the apparent gain. It supplies no evaluator role or finished useful predicate. Its precise canonical serialization and incomplete-status behavior must be frozen with the eventual verifier. [S1, S2]

The empty-partition comparison removes all learned historical distinctions. If attributing an effect to a particular selected predicate, additionally remove that predicate while holding the remaining list and data fixed, rebuild the counts and recompute the same choices. Correlated predicates can mask a single deletion, so absence of a single-predicate effect is not proof that the whole learned partition is unused. Report the complete chosen feature vector and both forecast/action consequences. These are frozen-state explanatory interventions, not alternative online training histories.

### 5.2 Distinguish count fitting from partition change

For a credited trial let `T0,T1` be the pre-trial and post-trial transition tables, and `Phi0,Phi1` the corresponding predicate lists. Recompute on the identical validation histories three frozen predictors:

- `P00 = Predict(T0,Phi0)`;
- `P10 = Predict(T1,Phi0)`;
- `P11 = Predict(T1,Phi1)`.

The ordinary count effect at the old partition is `Brier(P00,y)-Brier(P10,y)`. The partition effect on the same new data is `Brier(P10,y)-Brier(P11,y)`. Their sum equals the original pre/post Brier difference wherever all predictions are numeric. This is one specified sequential decomposition; it does not claim order-independent causal mediation. New-partition cell counts are rebuilt from the same transitions, rather than pretending numeric cell counts remain identical after changing cells.

Apply the corresponding same-data partition comparison to held-out decisions. **An advantage surviving equal transition exposure can support a partition-dependent contribution.** An advantage unchanged when the relevant partition contribution is removed undermines that attribution. These are different interventions. This explicitly corrects the overbroad prospective disconfirmation wording in the original recommendation without modifying its verdict. [S4]

The accepted R4 positive-credit concern remains conditional: there is no fully established empty-state reachable witness of that exact confound in the frozen loop. Logging the decomposition is the proposed way to determine whether it occurs here. It must not be entered in results as if it already happened. An unavailable component is recorded as unavailable, never set to zero.

## 6. Matching, stopping and interpretation

Match **allowances and information access**, then report realized consumption. Do not claim equal realized action counts when a method stops sooner because its own compute or memory ran out. The common resource accounting includes primitive environment calls, RESET, validation, raw histories, failed proposals, expression enumeration, predicate evaluations, unordered-pair checks, count rebuilds, snapshots and copies, sorting, exact-arithmetic bit costs, queues, library entries, retained provenance and downstream use. Any sharing of immutable data must be measured once, not counted as free. Direct coverage is allowed its actual computational savings.

Preserve all original stop reasons: incomplete warm-up, incomplete prediction, grammar/feature bound, computation limit, memory limit, environment limit and finite-word exhaustion. A bounded method that cannot produce a decision can be a resource-feasibility failure, but an unavailable scientific comparison is not a numeric zero. The eventual preregistration must separately fix the intention-to-run denominator, treatment of declared abstention/resource failures, minimum evaluable coverage and the rule for suspending an uninterpretable contrast. Outcome-dependent removal of hard cases is forbidden.

A decision to continue this line requires all of the following: a predeclared meaningful advantage over the direct null/coverage route under the common budgets; useful-predicate provenance on held-out decisions; and evidence that the advantage is not explained entirely by count fitting, additional calls, a weaker reader or unequal resource access. The exact advantage threshold, aggregation, uncertainty procedure and multiplicity policy have not been chosen. They must be justified and frozen before treatment results exist. “Any positive difference” is not the default.

A matched null that equals or exceeds FULL can disconfirm the proposed advantage **in this instrument at these budgets**, once sufficient evaluable cases and intervention checks exist. A learned predicate that only improves its training partition does not satisfy the reuse endpoint. If adequate distinguishing evidence was obtained but the required decision still fails, the diagnosis shifts toward description selection/use for that case. If affordable distinguishing evidence was never obtained, acquisition order remains implicated. If the allowed grammar or evidence cannot support the decision, do not diagnose the wrong algorithmic stage.

Record when fresh nonzero credit ceases and whether later evidence is obtained by coverage, old priorities or ordinary count updates. **Fresh-credit exhaustion alone is not a kill condition:** R3 permits those routes to continue learning, and an early useful burst may suffice. The relevant test is the bounded advantage over the predeclared control at the common endpoint. [S3, S4]

## 7. What must precede implementation and execution

The next scientific action is a short design-feasibility pass on this exact instrument: verify representability, information sufficiency, schedule identities, the fixed evaluation panel and the meaning of each ablation. It must resolve the open values and analysis rules above, or reject this instrument with reasons. It may revise this prospective design before a gate is frozen; it cannot silently change035 or reinterpret an executed result.

Then complete the relevant `PROGRAMME.md` design, preregister thresholds and revision rules, pin the verifier, and obtain the required fresh restricted review of that experiment design. Standing human authorization should be used as recorded; do not ask Ali again for a decision already made. A new native reviewer call still requires an actual allowance and verified execution boundary; the completed040 review is not an unmetered extension.

Implementation must preserve the exact reference semantics. Profile small, typical and largest permitted cases before committing the experimental grid, using development fixtures that cannot disclose the target outcome panel. Charge diagnostic copies and comparators. Project from the largest measured case with an explicit reserve. Choose laptop versus Alliance HPC from that measurement; the finite interface is chosen for causal clarity, not because the cluster is inconvenient. If the planned grid needs HPC, provide one complete submission-and-return package for Ali. No GPU advantage is presumed for exact symbolic enumeration. [S5]

No further paper is currently required for this specification. A claim about the earliest historical version, a faithful historical implementation or a newly introduced method comparator would create a separate primary-method dependency. This document makes none of those claims. The supplied Chvátal and Pierce–Kuipers papers already resolved the bounded source questions needed for040.

## 8. Source identities

All repository sources below were inspected from the available source snapshot at returned commit `540370fdb73c8f87f6433e14463951673640d033`, accessed **2026-09-12**. These links identify source versions; no new external literature search is claimed. Counts and constants defining the proposed instrument above are design choices or explicit deductions, not experimental measurements.

| ID | Source | SHA-256 where a scientific frozen input is used |
|---|---|---|
| S1 | [DIAGNOSIS.md, §§1 and 6](https://github.com/afazeliUofT/arc-independent-lab/blob/540370fdb73c8f87f6433e14463951673640d033/DIAGNOSIS.md) | `e3106d737f5b50a688d1d5147a015dc091d2986493848b68d33d61949dfa4cc3` |
| S2 | [P2_SECOND_OPERATION_SPECIFICATIONS_035.md, shared contract and N1/N3](https://github.com/afazeliUofT/arc-independent-lab/blob/540370fdb73c8f87f6433e14463951673640d033/docs/P2_SECOND_OPERATION_SPECIFICATIONS_035.md) | `25f3148827d22abbe587a6c2ff0c5a3ff2db1883f70e678f640f16d0f07a7c69` |
| S3 | [Original checkpoint040 REVIEW_VERDICT.json](https://github.com/afazeliUofT/arc-independent-lab/blob/540370fdb73c8f87f6433e14463951673640d033/artifacts/P3_REVIEW_040_RETURN/a31d934ca1d4c3b4d84dc7bbe757f5295834c8319301debd826897c768786eac/files/delivery/P3_FOCUSED_REVIEW_040/science_output/REVIEW_VERDICT.json) | `a31b9d8ec2103f09d81b963fd7f9ff51c4287490a0f0bf2f74f5dfbc1407d673` |
| S4 | Checkpoint041 PI consultation: `evidence/P3_SCIENTIFIC_VERDICT_ASSESSMENT_041.md`, §§2–4, accompanying this specification | Original new assessment in this checkpoint; the publication manifest supplies its hash |
| S5 | [Governing research process](https://github.com/afazeliUofT/arc-independent-lab/blob/540370fdb73c8f87f6433e14463951673640d033/docs/governing/02_RESEARCH_PROCESS.md), [resources and setup](https://github.com/afazeliUofT/arc-independent-lab/blob/540370fdb73c8f87f6433e14463951673640d033/docs/governing/04_RESOURCES_AND_SETUP.md), and [objective continuity](https://github.com/afazeliUofT/arc-independent-lab/blob/540370fdb73c8f87f6433e14463951673640d033/docs/OBJECTIVE_CONTINUITY_2026-09-07.md) | Governing constraints and accepted amendments, not treatment findings |

The original mathematical witnesses and source interpretations remain in the immutable036–040 evidence. This document adds a prospective instrument and explicit comparison semantics. It reports no new candidate result and supplies no end-to-end N1–N5 controller.
