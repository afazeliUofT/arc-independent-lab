# Joint audit: what the current evidence actually decides

Prepared 2026-09-07 as a bounded PI-side consultation with shared tools and filesystem. This is not independent review, a formal GO/KILL verdict, a new candidate or an experimental result. No approved specification was changed.

The through-line remains a separately auditable object. The existing evidence establishes a strong integrated antecedent for its broad commitment and a concrete failure of an unguarded C4 response. It does **not** establish historical identity of an approved complete C1–C2–C4 system: no such complete system was specified. Nor does implementing the proposed wrapper inside a conventional controller establish that the wrapper itself is old.

One further distinction matters scientifically: C4 retains enough witness information to reconstruct the alternative scope in the counterexample. Its selected response fails to expose or consult that alternative. The mathematical witness demonstrates premature commitment at the response interface, not erasure of the relevant evidence from persistent state.

## Audited inputs and reading record

All URLs in this note were accessed **2026-09-07**. The source papers below are published research, not preprints. Public repository references are pinned to published checkpoint `7da5cc4ce22fac3163408a4889517c86d386f407`.

| Input read | SHA-256 of the local bytes inspected |
|---|---|
| [Approved operation specifications](https://github.com/afazeliUofT/arc-independent-lab/blob/7da5cc4ce22fac3163408a4889517c86d386f407/docs/P2_OPERATION_SPECIFICATIONS.md), especially C1, C2, C4 and combination restriction | `d37a52eeb569461503b262d2790a656048624ede4790aeb49254e5a9f133c26f` |
| [Through-line proposition](https://github.com/afazeliUofT/arc-independent-lab/blob/7da5cc4ce22fac3163408a4889517c86d386f407/evidence/P3_THROUGHLINE_PROPOSITION.md), including both technical clarification appendices | `a4504d2730a8bbfdf4e07e6f04ed2c6073bc1140e6a3e28a401f348b3b40918a` |
| [Prior-method audit](https://github.com/afazeliUofT/arc-independent-lab/blob/7da5cc4ce22fac3163408a4889517c86d386f407/evidence/P3_THROUGHLINE_PRIOR_METHODS.md), completely | `2cfe2b3cfb38494a394134f7e017cab59ac994d6e70469d427f8361061374913` |
| Li, Littman, Walsh and Strehl, journal version, *Knows what it knows: a framework for self-aware learning*, 2011; §§3.1, 4.1 and 7.2 including Algorithm 3, its assumptions and practical caveats | PDF `4d5eedc31e9988b9de3fcc546da31d210e5a735b6eccf46116461a2a7d3c42f9` |
| Petrick and Bacchus, AIPS 2002, *A Knowledge-Based Approach to Planning with Incomplete Information and Sensing*; representation semantics, query language, PlanPKS, plan-correctness conditions and stated inference restriction | PDF `2af08a6e888d5b68ae45399659cc2e27a8aa5d1ce6b25cb91ff7d8190c187e6a` |
| Ross, Chaib-draa and Pineau, NIPS 2007, *Bayes-Adaptive POMDPs*; §§2–3 including exact update and supplied model interface, cross-checked against the prior audit | PDF `e9c4e30a1a140b093f0bb57dc9fc986788e0033205f79ef87dcd4c0336c12d71` |

The primary PDFs were reopened through public URLs and the specified method sections read in local extracted text. The longer proofs delegated by those papers to other work were not newly verified here. In particular, this note reports PKS's explicitly stated sound/incomplete inference interface; it does not claim a new verification of the inference algorithm's proof in the separate 1998 paper. No abstract supplies a method claim.

## Separate propositions, separate evidential burdens

| Proposition | What would establish or refute it | Present finding |
|---|---|---|
| **J0: An operative known/unknown distinction can direct world interaction and later learning.** | A previously specified integrated loop suffices to establish an antecedent for this broad principle. | KWIK-Rmax is such a loop. J0 cannot carry the programme's novelty claim alone. |
| **J1: The approved operations already imply that every actual factual release respects all alternatives compatible with the record.** | Derive this from their specified interfaces, or give a permitted release that violates it. | The C4 witness defeats the implication when C4's licensing rule controls release. No approved joint precedence rule supplies a veto. |
| **J2: A particular complete C1–C2–C4 controller, including diagnostics and resource behavior, appeared in a prior method.** | A historical method and a complete state/input/update/response/reset/resource map, without importing the proposed wrapper into the comparator. | Not established. The approved complete controller is unspecified, and the inspected integrated priors differ in consequential interfaces. |
| **J3: T1-ref reproduces a controller given the same belief operation, exact query predicate and identical auxiliary C4 computation.** | An induction on equal joint states and response rules. | The clarified reference construction can establish this implementation equivalence on its stated domain. It does not establish J2. |
| **J4: A class-relative knowledge guarantee tells the agent that its model class contains the true world.** | An admissible evidence-based test of class adequacy, or a proof under explicit stronger assumptions. | False without extra assumptions. Indistinguishable histories below expose the boundary. |

These propositions are this consultation's formal organization of the audit, not additional approved algorithms. They keep a broad antecedent, a failed implication, an implementation identity and an unestablished priority claim from receiving one undifferentiated verdict.

## Strongest genuine integrated antecedents

**KWIK-Rmax is the strongest direct antecedent for J0.** In Algorithm 3, transition and reward learners return predictions or an unknown marker. Unknown state-action pairs receive optimistic planning values; the resulting policy obtains an actual transition and reward, which update the learners that abstained. The method's performance guarantee is conditional on the specified learnable MDP class and approximation requirements. Its planning rule is optimistic, not C2's expected decision value. It does not supply C4's scope diagnostics. This is a published closed loop, not a diagram connecting otherwise isolated components. [Li et al., published journal method, §§3.1 and 7.2, Algorithm 3](https://thomasjwalsh.net/pub/Li11Knows.pdf), accessed 2026-09-07.

**PKS supplies the stronger antecedent for epistemic conditions on execution.** Its represented knowledge has possible-world semantics; action addition tests knowledge preconditions, and conditional branches require information that will be available when executed. PlanPKS searches both relevant branches. Initial facts, action effects and domain update rules are supplied. Its inference deliberately sacrifices completeness: failure to establish a query need not mean the represented possible worlds genuinely disagree. It therefore constrains both the novelty claim and the meaning of an unknown report, without being an exact learned-scope comparator. [Petrick and Bacchus, published AIPS 2002 paper, query interface and Table 2](https://cdn.aaai.org/AIPS/2002/AIPS02-022.pdf), accessed 2026-09-07.

**Bayes-adaptive POMDPs supply a concrete learned-model control antecedent.** The augmented state includes physical state and transition/observation counts. Its belief update conditions on actual observations; planning evaluates consequences under uncertainty about both model and state. Finite state/action/observation interfaces and the prior family are supplied. This is more specific than saying every algorithm can be encoded as a POMDP. However, its ordinary output is a control policy, not the complete joint factual-status and C4 diagnostic interface. Its approximate solvers must not be credited with exact preservation of every alternative. [Ross et al., published NIPS 2007 paper, §§2–3](https://www.cs.cmu.edu/~sross1/publications/Ross-NIPS07-BAPOMDP.pdf), accessed 2026-09-07.

These method matches suffice for this bounded question. Searching more topics merely to find a paper with similar language would not close J2's missing specification. No further paper request is needed here. No claim that these approaches were universally abandoned, or why, follows from their age.

## Counterhistory: admissible, consequential, and narrower than erasure

Use total atoms A and B, ordered A first, fixed target response F=1, length bound k=1, one admitted seed with signature (1,1) and outcome 1, and one admitted negative with signature (0,0) and outcome 0. Action and provenance match throughout. Both scopes A and B cover the seed, exclude the negative and have equal size and coverage. C4 therefore selects A.

At a fresh observed descriptor (1,0), A licenses F. Two deterministic worlds remain compatible with the entire record: one has response 1 exactly in scope A, the other exactly in scope B. They disagree at this descriptor. They can be represented by finite transducers with an explicit finite descriptor schedule, so this is not a counterhistory requiring an unbounded or unsupported world family. C1 can retain both when supplied those models. No noise, missing atom, length exhaustion, contradicting provenance or rule conflict is required.

The conclusion has three layers:

1. **C4's own specified narrower operation remains well-defined.** It selects an empirically compatible scope, which the approved specification expressly does not equate with a causal invariant. The witness is not an implementation error or a refutation of that narrower description.
2. **An unguarded knowledge claim fails.** If the joint caller treats C4 licensing as establishing F, it declares known what the admitted evidence leaves unresolved. A C1 veto would block the witness, but that is a separately declared joint rule, not a consequence of co-location.
3. **Relevant information remains in C4's persistent state.** The stored seed, P, N and atom definitions suffice to reconstruct both A and B. What is missing is their use in the actual release rule. Thus the phrase “discarded the alternative” should be read as discarded from the selected response, not irreversibly deleted from memory. The witness is directly pertinent to the programme's distinction between retained information and the answer path that accesses it.

The state sufficiency claim is exact. From the retained seed, each atom's permitted polarity is fixed. From retained N, the learner can recompute every conjunction that excludes every admitted negative; retained P determines each one's coverage and the stored ordering resolves ties. In this witness, recomputation obtains A and B, each with coverage one and length one, from those bytes alone. No evicted encounter, true future outcome or evaluator-provided scope is required. The selected C=A therefore fails to expose information that remains recoverable in the specified state. This is a mathematical consequence of the retention contract, not a newly measured recovery result.

Recomputation is not free. For m atoms and bound k, direct reconstruction checks up to B(m,k)=sum from j=0 to min(k,m) of binomial(m,j) scopes. With cached atom signatures a direct scalar check costs O(B(m,k) Nw max(1,k)) work, plus O(m Nw) atom evaluations/cache construction and the actual cost of those tests; explicitly materializing the alternative scopes also requires output storage. Approved C4 already charges exhaustive scope selection, but it does not return that population at every query. A different release path must account for whether it retains or recomputes the population and the resulting query cost. This observation licenses neither a zero-cost recovery claim nor an unapproved change to C4.

The witness refutes J1's implication from component specifications to an unconditional joint guarantee. It cannot refute every possible completion of the components. The corrected T1-ref, whose factual field is exactly the common support predicate and whose C4 field is separate, does not make the faulty factual release. [Approved C4 use/state rules](https://github.com/afazeliUofT/arc-independent-lab/blob/7da5cc4ce22fac3163408a4889517c86d386f407/docs/P2_OPERATION_SPECIFICATIONS.md), accessed 2026-09-07. The history and these deductions are PI mathematics, not measured outcomes.

## Correction to the strength of the reference-completion argument

The existing reference completion is useful as a typed comparator. Its equality argument says that identical belief, witness, query and action computations produce identical external tuples. It can prevent a future implementation from receiving free information or hiding incompatible response semantics. It does not show that adding C4's auxiliary computation is itself a reduction to previously published machinery: that component was explicitly placed inside the comparator.

Accordingly, the prior note's sentence that the conservative coupling does not exhibit a new computational operation should receive this narrower interpretation: **the note identifies no new specified operation beyond those it explicitly supplies, and its matched implementation offers no additional algorithmic distinction.** This is not a proof that the entire supplied diagnostic wrapper was previously published or lacks any potentially useful new property. To settle that stronger claim, independently identify the prior wrapper or reduce the remaining property without installing that property by definition.

Likewise, general POMDP expressibility cannot decide novelty. A representation formalism may contain many distinct algorithms. A meaningful reduction must preserve the claimed behavior, information access and relevant cost, using a comparator specified without importing the candidate's disputed contribution. The existing C1/component mappings and the joint wrapper need different conclusions when the evidence has different scope.

## The remaining joint specification is exact and finite

The unresolved work is not “combine the ideas somehow.” An auditable joint claim must settle:

- **Shared model identity and weights.** Which C4 scope proposition each C1 model evaluates; how C2 probabilities attach to the same live state/model pairs; whether every still-admitted pair has positive mass. State merges and reset images must preserve that relation.
- **Common event semantics.** Which actual action/observation prefixes update each component; how C2's transcript kernels are generated from that same model; which fields and provenance admit a C4 witness. An inferred response must never enter as a new observed outcome.
- **Exact response precedence.** Whether the output is factual status, empirical rule proposal, action recommendation or all three, and which computation determines each. The corrected T1-ref supplies one possible choice, explicitly as a comparator.
- **Diagnostic consequence.** Whether a reported inconsistency, alias or length failure only annotates the response or changes future actions. A fixed C2 experiment library does not construct a missing predicate, expand a class or prove an informative experiment is physically reachable.
- **Persistence and resource property.** The one declared persistent state, agent-memory and physical reset semantics, and complete costs. A novelty claim about practical retention or inference requires a particular resource advantage or behavior; the commitment to uncertainty alone does not supply one.

Choosing these interfaces to create a new research candidate during the audit would mix invention back into screening. This note does not do that. The approved specifications explicitly condition combination on later evidence. [Approved specification, final section](https://github.com/afazeliUofT/arc-independent-lab/blob/7da5cc4ce22fac3163408a4889517c86d386f407/docs/P2_OPERATION_SPECIFICATIONS.md), accessed 2026-09-07.

## Different reasons for “unknown” must remain different

The following are audit distinctions derived from the current definitions, not a new diagnostic algorithm or a claim of novelty for these labels.

| Condition | What the available evidence warrants | What it does not warrant |
|---|---|---|
| Two live supplied models disagree | A class-relative prediction is unresolved. | The true model is in the class, or more observation will necessarily resolve it. |
| No supplied model fits the admitted record | The model/evidence/reset contract is inconsistent. | Which premise failed, or that a particular new variable is missing. |
| The proposition lacks a model-language interpretation | The present query interface is unsupported. | Its truth or physical observability. |
| An incomplete or interrupted inference has not established a query | This computation has not established the answer. | Semantic disagreement or impossibility of establishing it with the same evidence. |
| C4 seed and a negative have identical full atom signatures | Those atom values cannot separate the admitted pair. | Absence of a physical distinction, or exclusion of an outcome/provenance error. |
| No conjunction within k works, while the full seed conjunction does | Failure within the specified expression-length bound. | Missing evidence, a missing sensor, or inability of a richer expression to separate the witnesses. |
| C2 stops while alternatives disagree | Expected modeled benefit fails to justify another feasible experiment. | Knowledge of the factual answer, or a proof that further evidence is impossible. |

Even exact, unlimited inference cannot diagnose every silent class error. Let a finite history be identical in two deterministic worlds. The supplied class contains h0, which agrees with that history and predicts 0 at an unobserved query. A second world h1, outside the class, agrees with the complete history but predicts 1 there. Any learner with the same admitted history, model and retained state produces the same report in both cases; a randomized learner has the same report distribution. Until distinguishing evidence becomes available, no computation can certify which world actually generated the record. The support may remain nonempty and unanimous throughout. This is an elementary indistinguishability argument, not an empirical claim that all real tasks are impossible.

This boundary identifies a substantive unresolved part of the founding diagnosis: retaining alternatives in a supplied class is different from recognizing that the class omitted a later-relevant distinction. It also prevents conflating computational inability to derive an available answer with absence of evidence. Neither distinction automatically supplies a surviving novel mechanism.

## Best scientific next path under the current evidence

Keep the joint row open at its proper scope: strong prior art for the broad loop, a demonstrated response-interface limitation, and no established historical identity or novelty for an unspecified complete wrapper. Correct the erasure implication and the overly strong interpretation of T1-ref before using the audit to decide programme direction.

Complete a review packet that asks the reviewer to assess these separate propositions and their counterhistories, rather than approve a single broad “not novel” label. No hardware experiment is necessary to decide the finite mathematical witness or to repair the priority argument. A same-workspace consultation does not satisfy the programme's reviewer boundary.

If subsequent programme judgment calls for further invention, the most consequential unresolved demands exposed here are class adequacy and the actual use of distinctions already retained. They should become explicit diagnostic constraints in a separate invention phase, with novelty screening switched off while that phase generates ideas. This note neither invents replacements nor grants a phase transition. It does not recommend spending GPU allocation to distinguish methods already related by an exact mapping.

## Dependencies and errors

No inaccessible paper, user command, paid service or new external permission was required for this consultation. No laptop/HPC treatment job was run. All local tool commands used here exited successfully; there is no new nonzero tool error to report. Some large intermediate read outputs were truncated by the output budget; the particular method sections needed for the claims above were then read separately. No completeness claim is made for unread source appendices. Private source PDFs remain excluded from public deliverables.
