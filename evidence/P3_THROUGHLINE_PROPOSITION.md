# Phase 3: the shared proposition and the missing joint guarantee

PI analysis, 2026-09-06. This is a novelty-audit argument for review, not a reviewer verdict or an experimental result. The approved inputs are `IDEAS.md`, SHA-256 `73cab9f6ab1f5eda80c7c2adc6d2ed556c63d5652fd65434e4cc4b24383dc3b8`, and `docs/P2_OPERATION_SPECIFICATIONS.md`, SHA-256 `d37a52eeb569461503b262d2790a656048624ede4790aeb49254e5a9f133c26f`. They remain unchanged. Authority: [published Phase 2 approval](https://github.com/afazeliUofT/arc-independent-lab/blob/d9200bd6061a63cf82037c2fc31f361fa0109cb3/state/ESCALATION.md), accessed 2026-09-06; exact local archive `state/escalations/2026-09-06_PHASE2_APPROVED.md`.

## The claim worth auditing

**T0 — Preserve distinctions the evidence has not resolved, use their consequences to decide what evidence to obtain, and keep the status of a proposition separate from the action chosen under uncertainty.** A decision may be justified without its predicted outcome being known. A request for more observations may be unhelpful when the present description language cannot represent the missing distinction. Retaining an uncertainty representation across a discontinuity matters only if subsequent decisions actually consult it.

This is the common scientific commitment behind C1, C2 and C4. It is a substantive target even if each operation is familiar. Reducing individual operations does not, by itself, reduce the joint claim. Conversely, declaring that these operations express the same aspiration does not specify a joint algorithm. The approved specifications explicitly left combination conditional on later evidence; they do not contain the shared state, precedence rules or knowledge predicate needed for a complete combined operation.

The audit therefore distinguishes T0 from **T1**, a proposed system-level guarantee: for any permitted interaction history and query, the actual response path preserves every still-compatible alternative, states a relation as known only when those alternatives agree, selects feasible experiments using their decision consequences, and otherwise reports the applicable unresolved status. T1 is an auditable proposition, not a claim that the approved candidates already implement it. It is falsified by one permitted history on which their joint response collapses a still-live distinction.

## What “known” could mean here

Let \(S_t\) be the live set of model/state pairs after actual history \(h_t\). For a supported proposition \(\varphi\), define:

\[
\operatorname{status}(\varphi,S_t)=
\begin{cases}
\text{model-inconsistent}, & S_t=\varnothing,\\
\text{known-true relative to }H_0, & \forall s\in S_t:\varphi(s)=1,\\
\text{known-false relative to }H_0, & \forall s\in S_t:\varphi(s)=0,\\
\text{unresolved}, & \text{otherwise}.
\end{cases}
\]

An unsupported proposition also returns unresolved, with its unsupported interface identified. The empty set is checked first: vacuous truth must not make every proposition known after model failure. This definition is the audit's explicit interpretation of “know”; it was not an additional approved component.

The conditional correctness proof is short. If a true model/state belongs to the initial set, actual observations obey its specified dynamics, and each world-reset relation includes the actual successor, C1 never removes the true pair. An induction over observation and reset updates establishes this invariant. Universal agreement then includes that pair. No part of this proof establishes that the real world belongs to the supplied class. In particular, sensor changes omitted from the class, misreported outcomes and an unmodeled reset invalidate its premises. A result satisfying this invariant would establish conditional inference, not open-ended discovery of its own ontology.

Memory reset and world reset have different types. Clearing transient context can preserve \(S_t\) in a declared persistent channel. Clearing that channel erases this guarantee's premises unless another permitted source reconstructs the sufficient state. Resetting the world propagates retained models through their reset relations; it does not justify discarding what has been learned about those models.

## A concrete failure of the proposed joint guarantee

This is a mathematical witness constructed from the approved C4 rule, not a treatment run or a measured score. Consider total Boolean atoms \(A,B\), ordered with \(A\) first, maximum conjunction length one, one seed positive with signature \((1,1)\), and one contradictory encounter with signature \((0,0)\). All encounters have the same admitted action and provenance. Use a constant proposed response \(F\); the positive outcome equals \(F\), the negative does not.

| Permitted condition | Includes seed | Excludes negative | Positive coverage | Prediction licensed at fresh signature \((1,0)\) |
|---|---|---|---|---|
| \(A\) | yes | yes | seed | \(F\) |
| \(B\) | yes | yes | seed | none |

C4 chooses \(A\) by its fixed tie break. It licenses \(F\) at the fresh signature. A world where the valid scope is \(B\), and the fresh outcome differs from \(F\), fits the entire observed record. So does a world where the scope is \(A\). C4 does not return unresolved here: a valid bounded condition exists, no seed/negative signature aliases, and no pair of applicable *stored rules* need disagree. The unresolved distinction was between alternative scopes of the same rule, and the selection step discarded it.

If C1 contains both corresponding world descriptions, C1's query retains that disagreement. But merely putting C1 and C4 in the same agent does not say which response controls use of the rule. If C4 may authorize use on its own, the joint guarantee fails. If a new precedence rule requires C1 agreement before every C4-authorized use, this witness is blocked; that precedence rule must be stated and audited as part of the combination. It cannot be credited retroactively to the approved C4 specification.

The witness refutes an unconditional claim that the approved components collectively preserve every unresolved distinction. It does not refute C4's narrower, explicitly empirical claim about selecting a scope compatible with observed contradictions. It does expose a tension between that choice and T0.

## C2 chooses actions; it does not certify knowledge

For binary hypotheses that disagree about the best terminal decision, a sufficiently costly revealing experiment has negative C2 value. C2 then stops and selects the lower expected-loss decision under its supplied prior, even though the hypotheses still disagree. This is coherent cost-sensitive behavior. Calling that choice “knowledge” would be an error in the interface, not a failure of Bayesian decision theory.

Similarly, a physical action can lower future loss by changing the world without identifying its former state. C2's post-action loss correctly permits that value. Its numerical criterion alone therefore does not certify that a gain came from obtaining a distinction. The acquisition diagnosis requires a separate evidence-mediated attribution check, already called for in the approved specification.

The terminal rule \(\sum_g\mu(g)\min_d E[L_g]\) permits a separate decision for each eventual problem \(g\). It fits disclosure of \(g\) before the terminal decision, or equivalent independently selectable decisions. If one action must be selected while \(g\) remains hidden, that expression is optimistic; the minimum must be outside the sum. This is a domain restriction on the approved rule, not a silently corrected implementation.

## The missing interfaces, stated rather than hidden

| Interface needed for a joint operation | What is supplied by the approved candidates | What a claimed combination must additionally settle |
|---|---|---|
| Alternative worlds to action values | C1 has a set; C2 needs probabilities and transition/transcript kernels | Initial positive masses, posterior aggregation after merging states, and how C1 reset relations receive probabilities |
| Local rule to world-level proposition | C4 has supplied \(F\), atoms, action/provenance and one selected scope | How each live model evaluates the scope and response, including unsupported propositions |
| Precedence at query time | C1 returns alternatives; C4 can license a local response | Which condition controls release of an answer; an action recommendation must be distinct from a factual assertion |
| Scope failure to next experiment | C4 emits witness-based diagnostics; C2 receives a fixed experiment set | Whether any available experiment can change the relevant evidence; no predicate-construction capability is provided |
| Persistent state | Each operation names its own retained state | A single memory accounting and reset contract; duplicating witnesses or retaining reference activations cannot be free |
| Model failure | C1 and C2 can become inconsistent; C4 can lose an admissible condition | Stop versus repair policy; no candidate currently implements expansion of the model or atom class |

These are not cosmetic wiring details when they change certainty, action or retained information. Treating an unspecified choice as “implementation” would allow the audit to invent the very novelty it is meant to test.

## A conservative completion to use as an audit comparator

For the purpose of making the issue decidable, define a *reference completion*, T1-ref. This is a comparator construction, not an approved new invention. Supply a positive prior over C1's initial model/state pairs; supply probabilities for allowed resets; retain the model identity and current physical state. Bayesian filtering produces \(p_t\), and its positive support is C1's live set when transitions are deterministic between resets. C2 uses that same belief and finite experiment library. C4 maintains its witness sets and proposed scope, but never upgrades a factual answer beyond the universal-agreement predicate above. A proposed scope must be evaluable in the shared model language or remain unsupported. A Bayes action can still be chosen while its outcome is labeled unresolved.

For every admitted observation, the reference controller executes a single actual action/transcript, applies the common belief update, and feeds the relevant observed encounter to C4. It does not treat C4's prediction as a new observation. A world reset propagates belief through the declared reset kernel while preserving learned model identity; transient context clearing changes neither belief nor witnesses. Zero likelihood stops the inference path. A C4 aliasing diagnosis certifies nonseparability *in its supplied atom language*, not absolute unobservability of the world. A length diagnosis certifies failure within the declared bound, not the need for a new sensor. Neither diagnostic grants free model repair.

This reference completion establishes what a joint comparison would have to preserve. A conventional belief-state controller with precisely the same finite model, terminal decision loss, action restrictions, universal-support query test, and auxiliary C4 witness computation produces the same external responses. The correspondence is an induction on the complete joint state: equal initial beliefs and witnesses; equal action argmax and tie order; equal actual observation; equal posterior and witness update; equal answer/status function. Equality survives declared resets. Each operation has the same state and computational accounting under a literal implementation. This is a constructive joint reduction to an explicitly specified controller, **not** a historical assertion that one cited paper published this exact whole package or its diagnostic labels.

The important consequence is limited but real: simply adding this conservative coupling does not, by itself, exhibit a new computational operation beyond the belief/controller/query and witness machinery. A defensible novelty claim would need a specific further property—such as a new sufficient-state representation, attainable inference-cost reduction, or a new model-expansion rule—and a comparator and history testing that property. None is supplied by calling the combination a commitment to uncertainty.

## Primary antecedents and the limit of the reduction

Earlier work already connected unknown predictions to action and subsequent learning. Li, Littman and Walsh's ICML 2008 KWIK paper, particularly its enumeration algorithm and navigation example, gives a direct antecedent for maintaining agreement/disagreement and using unknowns to acquire informative experience. The expanded journal method by Li, Littman, Walsh and Strehl adds the explicit KWIK-Rmax loop. Its guarantees and query feedback assumptions are stronger and different from merely outputting an uncertainty label. The detailed primary-method mapping and limits are in `evidence/P3_THROUGHLINE_PRIOR_METHODS.md`. [ICML 2008 primary paper](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/published-9.pdf), [journal primary paper](https://thomasjwalsh.net/pub/Li11Knows.pdf), accessed 2026-09-06; published papers, not preprints.

Ross, Chaib-draa and Pineau's Bayes-adaptive POMDP method explicitly places uncertainty about dynamics alongside physical state and plans with that combined belief. It supplies a direct antecedent for evidence-sensitive control without an oracle for the hidden physical state. Its model class and finite observation/action interfaces are supplied; it does not discover arbitrary new variables. Its approximate solvers must not be conflated with an exact finite belief controller. [NIPS 2007 primary paper](https://www.cs.cmu.edu/~sross1/publications/Ross-NIPS07-BAPOMDP.pdf), accessed 2026-09-06, especially §§3–5; published conference paper, not a preprint.

These sources establish that T0's central closed loop is prior art. They do not establish exact identity between the approved C1/C2/C4 package and one published algorithm. In particular, optimistic exploration differs from C2's expected decision value, C4's diagnostic taxonomy is not KWIK-Rmax's output interface, and C4's greedy scope choice breaks a naive correspondence to a consensus predictor. These differences receive an explicit mapping, not an automatic novelty pass. The exact historical priority of the entire diagnostic wrapper remains unestablished; absence of an exact match in this bounded search is not a novelty result.

## What this means for programme design

The combined proposition must remain a separate audit row regardless of individual operation outcomes. The current evidence supports three statements of different strength: the broad principle has strong integrated antecedents; the approved operations do not yet imply the desired joint guarantee; a conservative completion has a constructive reduction to a conventional belief controller with explicit auxiliary diagnostics. None of those statements is a formal reviewer verdict.

The strongest objection to the counterexample is that C1 would naturally veto C4. The reference completion above grants precisely that veto and then shows what it buys and what it costs. The strongest objection to the prior-art conclusion is that useful combinations can be novel even when components are old. Agreed: the remaining burden is a specified joint operation and a behavior or resource property not obtained by the mapped comparator. The strongest objection to the whole line is realizability: an agent that knows when a finite supplied set disagrees may still confidently miss the true explanation. The induction explicitly exposes that assumption; a later instrument must include histories outside the supplied class rather than evaluate only cases where the answer was enumerated for the learner.

Next scientific decision: finish the component certificates, assess the observer result under its own current-state interface, and seek an independently enforced review of the complete audit. Do not launch a large mechanistic treatment or advertise a surviving novel architecture on the strength of this principle alone.

## Technical clarification of the reference completion — 2026-09-06

For the asserted support equality, every initially live pair must have strictly positive mass, and every allowed successor in a nonempty reset image must have strictly positive conditional mass. A reset model with zero probability on an allowed C1 successor would otherwise delete a possibility without evidence. T1-ref's simplest stochastic construction restricts reset images of live states to be nonempty. C1 itself permits empty images; extending the reference completion to those cases requires an explicit likelihood for the observed reset event and conditioning that eliminates incompatible pairs, or a stated unsupported-reset result. A zero-row transition must not be normalized by fiat. The unqualified relational reset reduction for C1 is instead supplied by `evidence/P3_C1_C4_PRIMARY_AUDIT.md`.

This clarification narrows the reference construction's domain and leaves the approved operations unchanged. It prevents a convenient Bayesian completion from quietly suppressing C1's possibilities. It also reinforces why a mathematical construction with explicitly matched interfaces is not proof that an unspecified complete package appeared in one prior paper. Source of the audited reset rule: [approved operation specifications](https://github.com/afazeliUofT/arc-independent-lab/blob/d9200bd6061a63cf82037c2fc31f361fa0109cb3/docs/P2_OPERATION_SPECIFICATIONS.md), accessed 2026-09-06.

## Response-rule correction after consultation — 2026-09-06

A shared-workspace consistency consultation found that “C4 never upgrades” was only a necessary condition and did not specify a unique joint output. T1-ref is now explicitly defined to emit a tuple: factual status **exactly** equal to `status(phi,S)` above; the independently computed C4 scope/diagnostic result; and the selected C2 experiment or stop. A C4 scope may propose a proposition for checking but cannot replace that factual status. A C4 failure is reported separately and does not veto a factual proposition that all live world models establish. This fixes one reference comparator's response rule; it is not a change to the approved candidates or a claim that this coupling is preferable in all applications. Without this clarification the earlier claim of equality of *all* external responses was under-specified.

The earlier sentence saying C2 “stops and selects” a terminal decision also overattributes its explicit output. C2 selects the experiment or `stop`; a downstream Bayes decision rule **can** select the lower expected-loss terminal action. If T1-ref includes that action in its output, it adds a separately declared downstream argmin with fixed tie order after the task identity becomes available. A factual status remains a different field. The decision-value reduction concerns the approved selector and its modeled terminal loss, and does not silently make that extra caller interface an invented part of C2.

The consultation checked the counterexample and reset-domain clarification and reported no defect in their stated logic. This is PI-side checking with the same available tools and filesystem, not independent review. These corrections are preserved rather than silently replacing the prior argument. Source of the relevant original interfaces: [approved specifications](https://github.com/afazeliUofT/arc-independent-lab/blob/d9200bd6061a63cf82037c2fc31f361fa0109cb3/docs/P2_OPERATION_SPECIFICATIONS.md), accessed 2026-09-06.
