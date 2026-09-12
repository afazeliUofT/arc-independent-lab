# A bounded calibration of acquisition and historical conditioning

Date: **2026-09-12**. Status: **prospective design decision; no learner run, cost profile, experimental admission or independent verdict**. This document develops checkpoint041. It does not modify frozen035, approve `PROGRAMME.md`, or treat the original040 analytical GO as a treatment permission. The constants and thresholds below are declared design policies and algebraic deductions, not measurements. The complete experimental preregistration, executable accounting implementation, measured resource values and independently checked admission remain separate deliverables.

## 1. The scientific decision has narrowed

Use the041 transducer as an **acquisition and readout calibration**, not a substantive recombination experiment. Its target observations depend on a short familiar historical distinction. There are only ten possible complete `W=2` target windows in this construction, before choosing the action or goal: two final setter values times five possible preceding observation tokens. The same keys are obtainable through short acquisition words. Consequently a long unencountered whole history supplies a clean input boundary but does not establish composition of separately learned relations. This correction follows specification analysis; no unsuccessful or successful candidate run prompted it. [S1, S2]

The narrower question is still useful: does the exact N3 feedback policy obtain evidence that improves a later decision under a finite environmental allowance, and is an apparent advantage due to N1's selected partition, ordinary historical conditioning, or merely different counts? These are the first two diagnosis priorities, separated by their counterfactuals. None of the possible outcomes here establishes prevalence of a bottleneck in modern AI, retention across discontinuities, discovery of action primitives, or a new general learning mechanism. [S3]

A further limitation is architectural. For any fixed selected predicate vector `v`, current observation `o` and action `a`, N1 predicts by the observed joint key `(o,v,a)`. If that key is absent from its active transition table, add-one smoothing returns the uniform distribution. A learned predicate's meaning does not supply an additional transition rule for that absent combination. If all action keys for a target tuple are absent, the common chooser receives the same uniform distribution for every action and uses its supplied action-index tie break. There is no factorized composition of transition rules in this predictor. This does not prevent useful abstraction: different histories can map to a *seen* key. It does prevent treating successful key reuse as evidence that N1 composes predictions for arbitrary unseen feature combinations. [S2, direct deduction]

Accordingly, a calibration success would justify a bounded allocation or abstraction investigation with its claim named accurately. It would not authorize promotion of this toy to evidence that the funded recombination or retention problem has been repaired. A subsequent substantive instrument must require the stronger scientific demand explicitly; if the current prediction rule cannot express it, record that limitation and return to specification or ideation rather than retrofit a claim.

## 2. Fixed world and evaluation panel

The world, action roles, five-token observation alphabet, physical RESET contract and absence of acquisition goals are exactly the prospective041 construction. The reference configuration remains `W=2`, `S=3`, `K=4`, `L=5`, `V=2`, `q=4`. These are declared instrument parameters, not optimized values. No hidden register, role names, full world family or evaluator transition table enters a learner. Each world/arm begins with empty state, and no cross-instance learned state survives. [S1, S2]

### 2.1 A finite panel with explicit scope

Enumerate permutations of `[0,1,2,3,4]` in lexicographic order, indexed `r=0,...,119`. For each `r` and each initial register value `x0` in `{0,1}`, define one world:

- Map ordered action roles `(SET_0, SET_1, MASK, PROBE_0, PROBE_1)` to the opaque indices in permutation `r`.
- Map ordered observation roles `(CUE_0, CUE_1, NEUTRAL, MATCH, MISMATCH)` to permutation `(37*r+11) mod 120`.
- RESET sets the hidden register to `x0` and returns the mapped NEUTRAL token.

This defines **240 planned paired cases**, not 240 independent world laws. Since 37 is coprime to 120, all observation permutations occur marginally, as do all action permutations; the two initial values are crossed with each. The panel does **not** include the full crossing of action and observation orders, and may miss interactions between their tie orders. There is no sampling claim or confidence interval over all possible labelings. Its finite score describes this declared panel only. The explicit pairing rule was selected without treatment outcomes; it must not be changed in response to them.

This panel definition is a prospective estimand, not a commitment to execute a grid of unmeasured cost. The exact expanded manifest and its hash must be committed before profiles that execute any learner and before treatment; a manifest-only generator may verify membership without importing a learner. If cost makes the panel infeasible, preserve it as an unrun design and choose the computing route or terminate it under the resource rule in section6. Do not trim inconvenient label orders after observing performance.

### 2.2 Exactly balanced preparation windows

For each world, final register value `b` in `{0,1}`, preceding observation role `y` in the five-role alphabet, and goal `g` in `{MATCH,MISMATCH}`, evaluate one decision. Define a length-seven preparation

`u(b,y) = SET_(1-b), MASK, MASK, MASK, MASK, MASK, q(b,y)`,

where `q` is determined prospectively by this table:

| Desired final preparation observation `y` | Final preparation action `q(b,y)` |
|---|---|
| CUE_0 | SET_0 |
| CUE_1 | SET_1 |
| NEUTRAL | MASK |
| MATCH | PROBE_(1-b) |
| MISMATCH | PROBE_b |

Pay for RESET, execute `u(b,y)`, then execute `SET_b, MASK`. Present the mapped goal token to the frozen common chooser and execute its single selected primitive action. The evaluator uses role information to generate this declared diagnostic contrast; the chooser receives only the actual ordinary opaque-token history and goal. In particular, evaluator role names are never attached to history fields. All arms receive the same preparations and goals, independent of their acquired data.

The preparations yield each possible observation lag two exactly once for each final register and goal. They also include cases where a previously imposed opposite register is overwritten by the final setter. At the query, current observation is NEUTRAL, observation lag one is CUE_b, action lag one is MASK, action lag two is SET_b, and observation lag two is the chosen `y`. Thus this panel balances the ten target windows instead of overweighting repeated long preparations that collapse to the same key. It has **20 planned decisions per world**, with equal weights. [S2, algebraic construction]

The nine-action preparation-plus-suffix is longer than any acquisition episode: a trial has length at most five and its unreset validation block adds at most two. No exact evaluation whole history is an acquisition history. Nevertheless, its short target windows have familiar-word support. Every target `W=2` key for a probe can be produced by a length-four acquisition word `r, SET_b, MASK, PROBE_c`, where a suitable single primitive `r` produces the desired lag-two token from RESET. Even simpler, an ordinary order-one history key is supported by `SET_b, MASK, PROBE_c`. These are sufficiency deductions, not claims that an acquisition arm selects those words or that greedy N1 chooses the useful predicate. [S1, S2]

For this diagnostic family, two cue indicators suffice to distinguish both target states from other current-NEUTRAL records. They are legal equality leaves and fit the configuration. The online greedy learner can spend its available slots on something else; representability is not selection. Longer acquisition histories can also contain unresolved conflicts even under the complete `W=2` window—for example a hidden register can survive more masks than that window remembers. Residual conflicts alone therefore do not show a coding defect or failed identifiability of this narrower target.

## 3. Arm contrasts and a necessary baseline correction

Retain the four041 acquisition arms: `FULL`, `MACRO_OFF`, `FEEDBACK_NULL`, and direct `COVERAGE`. All retain the same N1 specification, interface, warm-up, scored-trial/validation contract and resource ceilings. The nested contrasts have one operative change: FULL versus MACRO_OFF removes post-warm-up promotion; MACRO_OFF versus FEEDBACK_NULL removes learned utility from proposal priority. FULL versus FEEDBACK_NULL is the combined feedback-package contrast, not identification of one edge. [S1]

FEEDBACK_NULL and COVERAGE select the same words until a documented computation or memory boundary changes what can complete. They are not independent replications of a baseline. Direct coverage is allowed its actual savings in proposal construction. A divergence in completed schedules before an accounted boundary is a conformance question requiring resolution before interpretation. [S1, schedule deduction]

**Correct the prospective baseline ladder before results.** On each frozen acquired trace, use generic typed count readers at history orders **0, 1 and 2**, with the same outcome alphabet, add-one prediction, goal-conditioned chooser and action tie rule. ORDER0 keys current observation and action. ORDER1 additionally keys observation lag one and action lag one. ORDER2 additionally keys observation lag two and action lag two. Each missing term uses the same typed MISSING convention as035. The canonical key stores terms in field/type/lag order and never stores evaluator roles.

ORDER1 is essential: at the target its cue term already separates the register values while omitting the irrelevant preparation observation. It can pool the nuisance histories without learning a semantic variable or being handed a useful cue label. N1 beating only ORDER0 and ORDER2 could be explained by omission of this ordinary conditioning baseline. Therefore the three readers are all prescribed; none is selected after observing which loses. This is a direct local comparator, not a claim about the oldest historical method. No new paper is needed to define or audit its count lookup.

The same-data selected-partition and predicate-deletion diagnostics from041 remain mandatory. Each reader receives exactly the same active transition table `T` at the acquisition freeze, identified by its hash, and the same history inputs for its comparison, under a common declared diagnostic budget. Observations retained in an unassimilated queue are not silently added to a comparator's training table. A separate all-observed-evidence diagnostic could inspect such a queue only under an explicitly different information allowance. No replay result or diagnostic readout is returned to online acquisition. Snapshot reuse must still charge the stored data. A full N1 trace replay checks semantic conformance and provenance, and is diagnostic computation, not another acquisition arm.

The ungated Brier modification remains outside this gate. If a later repair changes that gate, it is a new prospective candidate/contrast, with preserved original results and its own hypothesis. It is not an automatic response to a FULL failure.

## 4. Environmental allowance and completion semantics

Fix the primary acquisition allowance at **`B_env = 285`** calls per world/arm. This is a prospective calibration choice with a structural reason. Direct coverage uses ten calls for primitive warm-up, then `25*(1+2+2)=125` calls for all length-two scored words. Another `25*(1+3+2)=150` calls covers one fifth of the length-three words, giving `10+125+150=285` before other resource interruptions. The calibration deliberately asks about early acquisition before exhaustive short-word coverage. This budget does not represent a measured efficient regime or a claim about realistic-world interaction costs.

For orientation only, complete direct coverage through length four would cost `10 + 25*5 + 125*6 + 625*7 = 5260` calls. That is a support-sufficiency bound for the generic full-window target keys, not a planned second endpoint or extra condition to run. A small-budget advantage cannot be reported as an advantage after exhaustive coverage.

A trial may start only if its RESET and complete word fit the remaining environment allowance, as035 specifies. Validation actions also cost calls. If a complete trial fits but its full validation block does not, preserve the completed validation prefix, give the block INCOMPLETE status and no utility, and stop at the allowance. Do not secretly reserve a complete trial-plus-validation block when the reference only requires trial reservation. Do not fill remaining allowance by an unregistered fallback policy.

**Versioned completion clause, resolving an underspecification before implementation.**035 says that the live learner may append validation observations only after the block has been scored; it does not explicitly decide whether that permitted append is mandatory. For this comparison, finalize the validation result first, then append every completed validation transition to the live N1 in its recorded order, including a completed prefix after the block is finalized INCOMPLETE. No snapshot prediction is refitted before scoring, and no predicate selected during this delayed assimilation is credited to the preceding trial. This is the common reference adapter for every arm. It is chosen to respect the shared requirement that completed partial traces supply their individual transitions; it is not represented as already uniquely dictated by the original wording. [S2]

Complete warm-up is a prerequisite for a scored acquisition run. If a bound interrupts an N1 update, preserve its cursor, table version and spent work. The later evaluation must use the actual permitted frozen state, including any queued evidence. A separate evaluation budget may finish a required count rebuild for the already selected predicates, but may not resume feature selection, assimilate unprocessed observations, or acquire new evidence. A missing supported prediction remains nonnumeric; it is never replaced by stale counts.

Every evaluation decision separately receives **11 environment calls**: one RESET, nine preparation/suffix actions and one chosen action. Prediction over all five actions consumes computation but does not itself query the world. Every decision begins from the same acquisition snapshot; outcomes from earlier panel decisions never update it. Acquisition and evaluation counts are recorded separately and summed transparently. Diagnostic readers receive the same physical evaluation allowance for each of their own decisions; they do not receive free counterfactual outcomes as learner input.

In this world, primitive warm-up cannot contain a conflicting same-action pair, since each primitive is issued once. With completed warm-up, the selected predicate list is empty at its end. Hence K=4 allows at most four later trials with available nonzero fresh credit, and validation may consume slots without awarding such credit. Record the timing and provenance, but never remove cases where feedback fails to engage. A finite useful burst may be sufficient; fresh-credit exhaustion alone is not a kill rule. [S2; original040 R3]

## 5. Fixed estimand, availability rules and interpretation thresholds

These rules are declared before candidate results. Their role is to decide whether this bounded calibration merits further work. They are policy thresholds chosen for a transparent toy with a perfect role-informed evaluator solution, not literature-derived guarantees or estimates of significance.

For each world/arm, average the success indicator over its twenty predetermined decisions, then average equally over the 240 worlds. Success means the executed chosen action actually returned the revealed goal token. There is one fixed primary endpoint at B_env285. No best budget, best ordering, best goal or best preparation is selected. Permutations, goals and preparations are dependent blocks of this finite estimand. Report exact rational differences and world-level tables; do not use a p-value, binomial standard error or confidence interval treating them as independent environments.

Keep numeric failure distinct from unavailable inference. A completed action whose observation is not the goal is a failure. A required nonnumeric prediction, incomplete warm-up, or declared method resource stop that prevents a decision is DECISION_UNAVAILABLE with its literal cause. It is not a numeric zero and is never removed from the planned denominator. Infrastructure corruption, input leakage, a hash mismatch, an incorrect algorithm trace or missing original evidence invalidates the affected comparison rather than becoming a scientific loss.

If an arm has `s` observed successes and `u` unavailable decisions among the fixed `n=4800`, its success interval is `[s/n,(s+u)/n]`. This is a deterministic missing-outcome bound, not a confidence interval. For FULL minus comparator C, use the conservative interval `[lower_FULL-upper_C, upper_FULL-lower_C]`. Use corresponding intervals for same-trace readout contrasts. Preserve all causes and return both the raw observed fraction and bounds; the latter determine any continuation predicate.

Require **at least 95% numerically evaluable decisions in each required arm/reader contrast and at least 95% jointly evaluable paired decisions** before interpreting that contrast. This tolerance allows a small amount of declared resource abstention without silently discarding it; conservative bounds still charge all uncertainty against a positive conclusion. It does not tolerate corrupted implementations or missing evidence. Below that coverage, the calibration cannot settle the comparison: report a resource/implementation dependency and stop scientific interpretation, without substituting zeros or replacing cases.

### 5.1 Allocation signal worth following

The prospective allocation-continuation predicate requires all of:

1. FULL's conservative success lower bound is **at least 0.75**.
2. FULL's conservative paired advantage is **at least 0.10 over FEEDBACK_NULL and at least 0.10 over direct COVERAGE**.
3. Recorded intervention provenance shows that operative utility or a credited macro changed a selected acquisition word and that its actual evidence contributes to the later decision. Mere computation of a shadow score or presence of a word in F is insufficient.
4. Required conformance, information-boundary, availability and resource-matching checks succeed.

The 0.75 absolute criterion closes half the gap between the 0.5 maximum of a history-independent probe choice on the balanced final-register/goal panel and the role-informed perfect solution. It does not assume an observed baseline attains 0.5. The 0.10 advantage requires one additional successful future decision per ten planned decisions; an arbitrarily small favorable tie effect does not justify prolonging this branch. The two null comparisons guard the total feedback package and its avoidable proposal-computation overhead; their agreement is not counted twice as independent evidence.

If FULL only meets the threshold relative to the expensive null but fails against direct coverage, the interpretation is that an implementation-expensive reference control was insufficient. It does not meet the proposed useful-allocation claim. If feedback never influences an action, report that as an informative mechanism trace, not a reason to relabel or exclude the world. If the comparison is adequately observed but the threshold is not met, the prescribed positive claim is unsupported on this panel and allowance; do not generalize a local negative to all budgets or worlds.

### 5.2 Additional condition for an N1-specific abstraction claim

An allocation effect can survive when an ordinary historical count reader makes the same downstream decisions. Therefore do not infer that learned partition construction is the useful repair from section5.1 alone. An N1-specific abstraction-continuation predicate additionally requires, on the **same FULL trace**:

- A conservative advantage of **at least 0.10** over ORDER0.
- A conservative advantage of **at least 0.05 over each of ORDER1 and ORDER2** under the common diagnostic reader allowances.
- Predicate provenance and frozen-state interventions establishing a partition-dependent forecast/action contribution on held-out decisions; count changes alone do not satisfy this condition.

The smaller 0.05 threshold asks that selected abstraction add at least one success per twenty planned decisions beyond ordinary historical conditioning; it prevents attributing the whole acquisition advantage to N1 when generic history tables explain it. Requiring both fixed reader orders avoids choosing a weak comparison after seeing results. Where one reader is unavailable, use the conservative bounds and coverage rule; an uncomputable control is not evidence that its predictions would be wrong.

If section5.1 passes but this additional predicate fails, any justified continuation is specifically an **allocation** lead. It is not an N1-specific learned-description result. The remaining contribution of N1 to N3's *credit formation* would still require its own one-variable experiment; these frozen-state reader interventions do not identify that online mediation. If ORDER1 accounts for the effect, state plainly that ordinary short-history conditioning suffices for the observed readout.

Neither predicate by itself establishes novelty, causal latent-variable discovery, general recombination, retention, or programme completion. These are machine-checkable proposed predicates for a future independent reviewer, not an independent GO/KILL issued by the author.

### 5.3 Where to locate a failure

Preserve and classify the actual trace instead of giving every low score the same diagnosis:

- No affordable distinguishing observation was acquired: evidence selection remains implicated, subject to the specified world and allowed actions.
- Distinguishing evidence was acquired, the generic permitted-history reader uses it, but N1 does not: description selection or its joint-key count readout is implicated for that trace.
- The useful partition is present and predicts correctly but the common chooser is incorrect: the chooser or its implementation is the local issue.
- Available grammar/history cannot distinguish the target under the actual trace, or the decisive data are genuinely absent: do not assert a preventable representation failure without its necessary support condition.
- Counts explain a trial's credited gain: report the exact `P00/P10/P11` decomposition from041. It is not automatically an online failure, but it defeats an attribution of that local gain solely to the new predicate.

Write the three strongest alternative explanations before requesting a verdict and test the strongest: ordinary ORDER1 conditioning, unequal counted resources/proposal overhead, and favorable tie-order or count-exposure effects are the current leading alternatives. Controls and exact trace preservation must precede results; optional later explanations cannot replace them.

## 6. Cost accounting is specified before a measured execution budget

Freeze the environment allowance and scientific interpretation above now. **Do not fabricate numerical B_comp, B_mem, wall-time or full-grid feasibility from an asymptotic bound.** The current repository has no measured cost of an exact N1/N3 implementation on the required small, typical and largest cases. The large symbolic grammar, repeated pair processing, snapshots and exact arithmetic make a laptop-time promise unjustified. This is the remaining admission dependency, not an unanswered question for Ali to guess.

The implementation must expose a common deterministic work counter with explicit charges for every actual primitive operation and arithmetic bit cost, as035 requires. Its versioned accounting specification must cover expression enumeration/evaluation, truth-cache accesses, conflicting-pair construction, count rebuilds, word mutation/deduplication/sorting, priority arithmetic, rational Brier operations, validation, copies, serialization and diagnostic reconstruction. Before publication of an executable, define the exact byte/key encoding and each counter increment in the accounting contract; verify optimized implementations against a simple reference on development fixtures. A bare count of model calls, Python instructions, successful trials or selected predicates is not B_comp. Wall-clock is an additional execution bound, not a replacement for common operation accounting.

Retained-memory accounting includes raw histories, transition tables, count tables, syntax, truth values, all provenance, F/M/queues/cursors, saved snapshots and diagnostic state. Freeze a canonical serialization and an explicit immutable-object-sharing policy before measurement. Count a shared immutable object's storage once in a process, not zero times; charge each actual copy. Logical retained bytes and observed resident memory are different quantities and must both be reported. A cap on one does not certify the other. External archived evidence remains retained programme storage and cannot silently disappear from cost reporting.

A prospective measured-budget procedure is fixed as follows:

1. Implement and conformance-check the exact reference adapters and every comparator. Keep target world outcomes and their learner scores inaccessible to the profiling driver.
2. Prepare three deterministic development fixture classes representing small, typical and maximum permitted retained records, constants, candidate inventories, proposal libraries and arithmetic sizes. These are fabricated mechanism-state/work fixtures, not samples of target success. Include conflict-heavy and no-positive-gain cases; do not profile only easy terminating examples. Freeze fixture inputs and hashes before any measurements.
3. Repeat each materially different implementation/profile case three times. Preserve descendant CPU time, wall time, peak resident memory, exact operation-counter totals, logical retained bytes, output bytes and interruption behavior. Benchmark both quiet and contended execution where laptop concurrency matters; if quiet conditions have not been established, label the observation rather than asserting it.
4. Set prospective per-run computation and retained-byte allowances from the **largest required, successfully validated complete-work fixture case**, with a **factor-two reserve**, using the same allowances for paired acquisition arms and separate common allowances for diagnostic readers. A one-update timing is not a full-acquisition work bound; the fixture specification must cover the declared maximum run and all required retained objects or explicitly project them by a validated bound. A profile that cannot establish a finite validated largest case does not authorize extrapolation from the median. The exact resulting integers, fixture identity, accounting code and derivation must be committed before any target learner run. These are finite scientific allowances, not guarantees that every target run finishes: any actual exhaustion uses the availability rules above. Deliberately reducing them to tune a candidate's performance would create a different estimand and requires a separately frozen design before outcomes.
5. Project the declared panel, every mandated comparator/diagnostic, verification and a **25% audit/rerun reserve** from the largest observed eligible case times the number of required cases, also applying the factor-two timing reserve. This is a conservative planning rule, not a guaranteed runtime. Preserve which repeats/fixtures set each maximum.
6. Use measured costs to choose the laptop or the available Alliance cluster. Do not assume GPU acceleration helps exact symbolic enumeration. If the cluster is appropriate, provide its contained dependency bundle, finite SLURM jobs, checkpoint/resume semantics and artifact-return package. Measure its materially different implementation/hardware before committing its grid. Do not reduce the panel, remove a nearest reader comparator, weaken a threshold or substitute a favorable cost quantile to fit a preferred machine.

The measured numerical ceiling selection in item4 is permissible only because the fixtures disclose no target treatment outcomes and the selection rule is prospective. It is not a loophole for scoring the candidate during “profiling.” Until those measurements, the design has no numerical computation/memory admission and this checkpoint contains no executable candidate. A profile-size or accounting defect discovered later must be recorded; it does not authorize editing a frozen ruler after treatment.

## 7. Revision and stopping boundary

One conformance correction may be proposed for this calibration gate, within the programme's maximum revision policy. Preserve the original source, evidence and failed attempt; distinguish a coding/accounting defect from a failed hypothesis. A correction cannot change the scientific world panel, B_env, learner semantics, candidate priority or positive thresholds to rescue an unfavorable result. Any changed scientific intervention is a new named design, reviewed before its results.

An independent restricted reviewer must assess the final design, budget, verifier and result evidence under an actual separately metered allowance. Same-workspace PI consultants do not provide that independence. Original040 is complete; its review calls must not be rerun or treated as an open allowance. The returned041 offline verification started no reviewer, model or experiment; it leaves the historical native usage totals unchanged.

The next concrete work is to finish the versioned accounting and reference-adapter contract, implement a source-separated conformance/profile package, measure it on development fixtures, and complete the relevant `PROGRAMME.md` plus immutable preregistration and verifier before a treatment. The scientific panel, environmental allowance, control correction and interpretation above can be reviewed now. Their actual execution remains unadmitted. No further paper is presently required; any later historical-priority or new-comparator claim must obtain its own primary-method evidence.

## 8. Source identities and access

Repository inputs were inspected at the available snapshot of returned commit `4976bc78c74908dc66da27d24b56c47aa4d6d5a6`, accessed **2026-09-12**. No new external literature retrieval, candidate execution or measured experiment is claimed in this document.

| ID | Source | Frozen scientific identity |
|---|---|---|
| S1 | [Prospective041 comparison](https://github.com/afazeliUofT/arc-independent-lab/blob/4976bc78c74908dc66da27d24b56c47aa4d6d5a6/docs/P3_N1_N3_SUCCESSOR_COMPARISON_041.md) | Historical source preserved; this document explicitly corrects its calibration framing and baseline omission before treatment |
| S2 | [Frozen035 operations](https://github.com/afazeliUofT/arc-independent-lab/blob/4976bc78c74908dc66da27d24b56c47aa4d6d5a6/docs/P2_SECOND_OPERATION_SPECIFICATIONS_035.md) | SHA-256 `25f3148827d22abbe587a6c2ff0c5a3ff2db1883f70e678f640f16d0f07a7c69` |
| S3 | [Diagnosis, priorities1 and2](https://github.com/afazeliUofT/arc-independent-lab/blob/4976bc78c74908dc66da27d24b56c47aa4d6d5a6/DIAGNOSIS.md) | SHA-256 `e3106d737f5b50a688d1d5147a015dc091d2986493848b68d33d61949dfa4cc3` |
| S4 | [Original040 verdict](https://github.com/afazeliUofT/arc-independent-lab/blob/4976bc78c74908dc66da27d24b56c47aa4d6d5a6/artifacts/P3_REVIEW_040_RETURN/a31d934ca1d4c3b4d84dc7bbe757f5295834c8319301debd826897c768786eac/files/delivery/P3_FOCUSED_REVIEW_040/science_output/REVIEW_VERDICT.json) | SHA-256 `a31b9d8ec2103f09d81b963fd7f9ff51c4287490a0f0bf2f74f5dfbc1407d673`; scoped analytical support, not efficacy |
| S5 | [Research process](https://github.com/afazeliUofT/arc-independent-lab/blob/4976bc78c74908dc66da27d24b56c47aa4d6d5a6/docs/governing/02_RESEARCH_PROCESS.md), [autonomy contract](https://github.com/afazeliUofT/arc-independent-lab/blob/4976bc78c74908dc66da27d24b56c47aa4d6d5a6/docs/governing/03_AUTONOMY_SPEC.md), [resources](https://github.com/afazeliUofT/arc-independent-lab/blob/4976bc78c74908dc66da27d24b56c47aa4d6d5a6/docs/governing/04_RESOURCES_AND_SETUP.md) | Governing prospective threshold, accounting, profile, independent-review and compute constraints |

The publication manifest supplies this new document's hash. All numeric policies above belong to this prospective design, while all reported future result numbers must cite their original artifact path and SHA-256. The limited old-paper conclusions established by036–040 remain intact; this document makes no broader novelty or abandonment-history claim.
