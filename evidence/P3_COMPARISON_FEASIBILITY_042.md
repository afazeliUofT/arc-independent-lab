# Feasibility and limits of the proposed N1–N3 instrument

Date and source-access date: **2026-09-12**. This is a PI consultation on the prospective041 design, not an independent verdict or a candidate result. It leaves the frozen035 operations, original040 verdict and prospective041 document unchanged. No learner was implemented or executed, no target outcome panel was generated, and no parameter was selected using candidate performance. All numerical statements below are configuration values or algebraic deductions from the cited specifications; no finite enumeration or learner test was used.

**Assessment:** the instrument can support a bounded acquisition and short-history abstraction calibration. It cannot by itself support the programme's substantive recombination or retention claim. There is one concrete baseline omission to repair before any calibration is frozen: include ordinary full-window count readers at every history order from zero through the configured window limit. A comparison only against the empty partition and the longest literal window can make selecting a short useful history look more distinctive than it is.

## 1. Reading and authority

The governing documents and accepted amendments preserve the diagnosed unknown-world acquisition, retention and recombination objective; the same-tools consultation here is not the fresh restricted reviewing process required to issue a verdict. The complete frozen035 operation specification, complete prospective041 comparison, and complete scientific041 assessment were read. The present step is specification analysis permitted by041 section 7, before implementation or measurement. No new literature claim or earliest-priority claim is made.

Sources were read from the available source snapshot corresponding to returned GitHub commit `4976bc78c74908dc66da27d24b56c47aa4d6d5a6`. The root return-verification task checks remote identity separately. Exact source URLs and SHA-256 values appear in section 9.

## 2. Representable target distinctions, without a learnability guarantee

Write the world roles as in041, while remembering that the learner receives only opaque indices. At the target query after `u, SET_b, MASK`, the permitted history terms are

| Term | Value |
|---|---|
| current observation | `NEUTRAL` |
| observation lag one | `CUE_b` |
| observation lag two | the endpoint observation of `u` |
| action lag one | `MASK` |
| action lag two | `SET_b` |

Thus the equality leaf `p0 = [observation_lag_one == CUE_0]` distinguishes the two target histories once that token has actually been observed and is therefore available as a grammar constant. Equality tests are Boolean leaves in035, so this requires no Boolean composition and fits the proposed `S=3` bound. A corresponding action equality is also legal after the needed action token has been encountered. These are representability witnesses, not predicates supplied to an implemented learner. [A1, A2]

One bit separates the paired target histories but is not a sufficient guarantee about the predictor trained on an arbitrary transition table. In particular, `p0=false` also includes histories whose preceding observation is neither cue. For robust isolation of both target cases, the two legal leaves

`p0 = [observation_lag_one == CUE_0]`,

`p1 = [observation_lag_one == CUE_1]`

give vectors `(true,false)` and `(false,true)` at the respective queries. With current observation `NEUTRAL`, a preceding cue can arise only from its setter followed by `MASK`. Every acquisition record sharing the appropriate vector, current observation and next action consequently has that same register value, regardless of its earlier preparation. Other neutral histories with neither cue have vector `(false,false)` and do not contaminate either target cell. The proposed `K=4` has room for these two leaves. [A1, A2; direct deduction]

This is an existence argument. The online greedy rule can spend slots on other predicates, on training correlations, or during validation; it need not choose these two leaves. Extra selected predicates may additionally split otherwise useful target cells into unseen subcells. A sufficient partition existing in the grammar therefore establishes neither selection by N1 nor adequate counts under the partition N1 actually constructs.

## 3. The window cannot identify every history in this world

Immediately before the last action in either word

`SET_0, MASK, MASK, MASK, PROBE_c`

or

`SET_1, MASK, MASK, MASK, PROBE_c`,

all three available observations are `NEUTRAL` and both available past actions are `MASK`. The complete typed `W=2` windows are identical, but the fixed probe's next observation differs. Both words fit the proposed `L=5`. No Boolean expression of this window, regardless of syntax size or number of features, separates that pair. The full underlying histories still contain the earlier setter; it is the chosen feature interface that excludes it. [A1, A2; direct deduction]

Accordingly, residual conflicts in this calibration cannot be treated as proof that the greedy search is defective, nor can complete conflict resolution be an admission requirement. The target queries remain representable because they place the relevant cue inside the permitted window. Logs must distinguish target-cell contamination or missing evidence from these provably indistinguishable other windows.

## 4. What is held out, and what is already locally obtainable

The length argument in041 is correct: its target history word has length `L+V+2`, while each ordinary acquisition episode has at most `L+V` primitive actions before the next paid RESET. Hence no complete target history is present in the acquisition log. But the final `SET_b` erases every earlier preparation's effect on the register. For the next decision, the preparation contributes only a nuisance value to observation lag two; it does not require composition of independently acquired causal relations. [A1, A2]

For a full typed `W=2` count reader, all target queries fall into at most `2 * 5 = 10` history windows: the final setter choice and the preparation's endpoint observation. For each of the five possible endpoint tokens, some single primitive `r` returns that token from the fixed RESET state: a setter for either cue, `MASK` for neutral, and one of the probes for either probe outcome. Therefore each target window with either probe action is reproduced by a short acquisition word

`r, SET_b, MASK, PROBE_c`.

The first three actions give exactly the same typed before-window as the long target history. The fourth action supplies the relevant outcome. This witness needs no free reset, hidden-state reading or learner knowledge of which primitive is `r`; exhaustive coverage includes it without that knowledge. [A1, A2; direct deduction]

If every word through length four has completed and its observations have been assimilated, an otherwise complete full-window count reader has observed every required probe cell. These cells are pure because their setter/cue history fixes the register. For the correct goal-producing probe with `n >= 1` observations, add-one probability is `(n+1)/(n+5) > 1/5`; any other action's cell is either unobserved, with probability `1/5`, or has no goal observation, with probability `1/(n+5) < 1/5`. The common chooser therefore selects a goal-producing probe. This is a sufficient-data theorem about the specified instrument and count rule, not a measured baseline result or a claim that any resource-bounded implementation reaches this point. Validation can provide sufficient evidence earlier; the bound is not a necessary cost. [A1, A2]

For direct coverage, the five primitive warm-up trials cost `5*(1+1)=10` environment calls and receive no validation block. Each later word of length `k` costs its RESET, its `k` actions, and `V=2` validation actions. Completion of all words through length four therefore costs

`5*2 + 25*(1+2+2) + 125*(1+3+2) + 625*(1+4+2)`

`= 10 + 125 + 750 + 4375 = 5260` environment calls.

This formula assumes completed work, no interruptions and sufficient computation and memory. It counts validation observations as paid interactions, but never treats validation words as separately completed acquisition trials. It does not predict N1's selected partition or N3's acquisition order. [A1, A2; algebraic deduction]

These facts do not make a finite-budget calibration useless. It can ask whether acquisition priorities or learned pooling obtain usable cells sooner. They do mean that a positive result is not evidence for solving a novel composition of learned causal relations. The long prefix must not be presented as a stronger generalization barrier than it is.

## 5. A necessary lower-order count control

The proposed empty partition ignores useful recent history. The proposed longest-window reader conditions on an irrelevant preparation endpoint. A generic full typed order-one reader avoids both problems. Its key is

`(current_observation, observation_lag_one, action_lag_one, predicted_action)`.

At the target query this is `(NEUTRAL, CUE_b, MASK, a)`. It is not supplied any cue role or finished useful predicate. It simply uses every typed term in its shorter fixed window. Every acquisition record sharing this key has the same hidden register by the argument in section 2. A single observation of each relevant probe cell suffices for the same add-one chooser argument. The words `SET_b, MASK, PROBE_c`, of length three, supply those cells. [A1, A2; direct deduction]

Complete coverage through length three is a sufficient, not necessary, acquisition route with environment cost

`5*2 + 25*5 + 125*6 = 885`.

Again this is a cost identity for the specified schedule, not an execution result. It does not say that fewer calls cannot suffice, or that a count reader is admitted without its own computation and memory accounting.

**Fix before freezing:** prescribe full typed-window count readers at orders zero, one and two, all on each arm's identical acquired trace. Freeze their encodings, add-one rule, resource ceilings and incomplete status semantics together. Report every predeclared reader, never select the winning order using target outcomes and present it as prospectively chosen. Use the strongest relevant predeclared control when assessing whether learned abstraction explains an advantage. An N1 advantage over only order zero and order two is insufficient evidence against ordinary fixed short-history conditioning.

An allocation benefit that remains with the order-one reader could still implicate useful acquisition order. It would not show that N1's encounter-selected description was necessary. Conversely, an N1 benefit over all these same-trace readers would support a narrower abstraction contribution in this calibration, subject to counts, costs and provenance. None of these readers is an unrestricted reader of the entire retained record. Use the term **full typed window** rather than **full history** for them; a broader reader claim would need an explicitly specified additional control.

## 6. Exact null schedule identity and bounded feedback opportunities

The041 identity between FEEDBACK_NULL and direct COVERAGE is correct before their differing computation or memory costs interrupt required work. After warm-up, every primitive is in `F` and `M`. Let `w` be the first uncompleted word in length/lexicographic order. If it is not primitive, its shorter prefix is already a completed trial in `F`; inserting the final primitive therefore proposes `w`. No uncompleted proposal precedes `w`. All null priorities are zero, so the frozen shortest-word/serialization tie rule chooses `w`; coverage slots choose the same word. This is induction over completed words, not a second independent success observation. Incomplete trials do not enter the completed exclusion set. [A1, A2]

For the particular primitive warm-up here, every action is issued only once as an ordinary transition. There is therefore no equal-key, different-outcome pair with the same action during warm-up, and the selected predicate list remains empty. With proposed `K=4`, the accepted fresh-credit injection bound gives at most four available nonzero-credit trials in this block. Validation selections may consume that capacity without opening any trial's credit gate. This is a strict constraint on possible feedback opportunities, not a proof that useful early feedback cannot occur. [A1–A3]

A calibration must retain runs in which operative feedback never engages. Removing them or replacing their action labels after observing that fact would tune the instrument to the candidate. Such records distinguish a nonexistent feedback intervention on that instance from a feedback intervention that occurred and failed to help.

The tentative environment cap discussed during042 design, `285`, has the transparent null schedule interpretation `10 + 25*5 + 25*6`: complete warm-up, all length-two trials, and the first twenty-five length-three trials, conditional on other allowances permitting completion. This is a deliberately early acquisition boundary and not a measured optimum. If used, report that structural choice and the resulting narrow budget-specific claim. No universal advantage follows from being tested before exhaustive shorter-word evidence has necessarily accumulated.

## 7. N1's predictor pools keys; it does not compose unseen key outputs

For frozen transition table `T` and partition `Phi`, N1's probability is determined solely by counts in the exact joint key `(current_observation, Phi(history), action)`. If that key has no observations, every one of the declared five possible outcomes has probability `1/5`. Neither the predicate syntax nor observations at different joint keys supply an alternative factorized forecast. [A1]

A new whole history can nevertheless receive a nonuniform prediction by mapping to a joint key already populated by another history. This is precisely the pooling that the calibration can test. In contrast, if the needed future relation requires a truly new joint key, the specified predictor has no rule for composing separately learned conditional relations into that key's outcome distribution.

This conclusion must be applied action by action. One unseen action key does **not** make the entire chooser uniform: other action keys may have observed, informative probabilities, and an unseen action's `1/5` can either outrank or lose to those values. Only when **all** candidate action keys are unseen does every action tie at `1/5`, forcing the lowest action index under the prescribed chooser. For the balanced two-register/two-goal target panel, such a fixed action succeeds in two of the four combinations if it is a probe, and in none if it is a setter or MASK. This is a simple algebraic consequence of the world table and tie rule, not a candidate outcome measured in this work. [A1, A2]

Thus one cannot strengthen this design by merely withholding every learned joint key and expecting the current N1 count predictor to infer the missing composition. That would require a new predictor or a different scientific claim, specified openly. Nor does this structural limit establish that the broader diagnosis is false or that all acquisition operations should be killed.

## 8. Changes required before any calibration is admitted

1. Describe the task as acquisition and short-history abstraction calibration. Preserve the absence of retention, memory discontinuity and substantive relation-composition evidence in every interpretation and advancement rule.
2. Add the complete order-zero/one/two reader ladder prospectively, with per-reader information and resource accounting. Separate allocation benefit from a necessity claim about learned representation.
3. Freeze the exact world-label and preparation panel without candidate outcomes. Marginal action/observation permutation balance does not cover their joint tie-order interactions; a selected deterministic panel supports a claim about that panel. Balanced goals and final register values are essential to prevent one probe or one target goal from becoming a favorable shortcut.
4. State evidence sufficiency at the actual selected key, including extra predicate splits, and distinguish inherently unresolvable W2 records from target description failures. Do not infer adequacy merely from the presence of both cue tokens somewhere in the log.
5. Complete the operational adapter for validation assimilation.035 says the live learner may append validation observations only after the block is scored, while its shared partial-trace contract and N1 transition rule require preserving completed transitions. Precisely specify when a completed or interrupted block is finalized and when its completed observations are assimilated, in chronological order, before the acquisition snapshot. This affects selection and counts and cannot remain an implementation choice. Never assimilate validation before frozen before/after scoring; never assimilate target observations.
6. Fix budgets, numeric advancement and suspension rules, unavailable decisions, panel weights and the treatment of never-engaged feedback before implementation or target measurements. Calibration scope does not waive these requirements. Profile exact arithmetic and search on non-target development fixtures before committing a grid; use the Alliance cluster if the resulting cost warrants it.

**Further papers:** none are required for these local deductions or the prospective window-count controls, which are defined directly. They make no historical novelty claim. A later faithful historical reimplementation, priority claim or broader method comparator may create a separate primary-method dependency.

## 9. Source identities

All links below are to the canonical repository at returned commit `4976bc78c74908dc66da27d24b56c47aa4d6d5a6`, accessed **2026-09-12**. The source hashes were recomputed locally. The publication manifest for042 supplies the hash of this new analysis; its derivations are not experimental measurements.

| ID | Source | SHA-256 |
|---|---|---|
| A1 | [docs/P2_SECOND_OPERATION_SPECIFICATIONS_035.md](https://github.com/afazeliUofT/arc-independent-lab/blob/4976bc78c74908dc66da27d24b56c47aa4d6d5a6/docs/P2_SECOND_OPERATION_SPECIFICATIONS_035.md) | `25f3148827d22abbe587a6c2ff0c5a3ff2db1883f70e678f640f16d0f07a7c69` |
| A2 | [docs/P3_N1_N3_SUCCESSOR_COMPARISON_041.md](https://github.com/afazeliUofT/arc-independent-lab/blob/4976bc78c74908dc66da27d24b56c47aa4d6d5a6/docs/P3_N1_N3_SUCCESSOR_COMPARISON_041.md) | `70424ad00f17056b1508a46e385b75496a7c25f51d5bb648377995761da4cef5` |
| A3 | [evidence/P3_SCIENTIFIC_VERDICT_ASSESSMENT_041.md](https://github.com/afazeliUofT/arc-independent-lab/blob/4976bc78c74908dc66da27d24b56c47aa4d6d5a6/evidence/P3_SCIENTIFIC_VERDICT_ASSESSMENT_041.md) | `d4a5e26406e1cc17d594ecb7d34b43172eca5cd317c1d735f4002d8a1b7d1429` |
| A4 | [docs/governing/01_THE_PROBLEM.md](https://github.com/afazeliUofT/arc-independent-lab/blob/4976bc78c74908dc66da27d24b56c47aa4d6d5a6/docs/governing/01_THE_PROBLEM.md) | `e89ddd629cfc839be31d0127acb59354b5e38d23e77859a8d8c7bbea87e00d3e` |
| A5 | [docs/governing/02_RESEARCH_PROCESS.md](https://github.com/afazeliUofT/arc-independent-lab/blob/4976bc78c74908dc66da27d24b56c47aa4d6d5a6/docs/governing/02_RESEARCH_PROCESS.md) | `7bf3c496962d0ede489ef10a237d3b70830fb439f3395235c3b8c18a23c4bc3d` |
| A6 | [docs/USER_AMENDMENTS_2026-09-06.md](https://github.com/afazeliUofT/arc-independent-lab/blob/4976bc78c74908dc66da27d24b56c47aa4d6d5a6/docs/USER_AMENDMENTS_2026-09-06.md) | `dc61574fa31f4e132f181b100e49df59cbb1272e82ec01cd08bb8c25ac4e1e15` |
