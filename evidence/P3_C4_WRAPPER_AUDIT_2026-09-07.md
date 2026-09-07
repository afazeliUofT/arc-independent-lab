# C4's residual diagnostic and use interface: primary-method audit

PI-side research consultation, **2026-09-07**. This is an audit certificate for review, not an independent review, a treatment experiment, or a formal GO/KILL decision. The approved specifications remain unchanged.

Audit target: `docs/P2_OPERATION_SPECIFICATIONS.md`, SHA-256 `d37a52eeb569461503b262d2790a656048624ede4790aeb49254e5a9f133c26f`, incorporated in the approved `IDEAS.md`, SHA-256 `73cab9f6ab1f5eda80c7c2adc6d2ed556c63d5652fd65434e4cc4b24383dc3b8`. This extends `evidence/P3_C1_C4_PRIMARY_AUDIT.md` and respects the separate proposition in `evidence/P3_THROUGHLINE_PROPOSITION.md`.

## Finding

**The remaining C4 diagnostics have exact mathematical antecedents in indiscernibility and bounded discernibility selection. Its refusal to use an unestablished precondition has an explicit antecedent in knowledge-based planning.** The positive/contradictory evidence store and supplied provenance routing do not add an inference that escapes those mappings. A comparison that merely drops the witnesses, treats unknown conditions as true, or ignores the length restriction would weaken the comparator.

This audit does **not** establish that one earlier publication contains the complete C4 interface, with the same event admission, failure labels, returned witnesses, conflict policy, and seed-star preference. Whole-wrapper historical priority remains unestablished. That residual bibliographic fact is not evidence for a new learning operation or a reason to claim survival of the C4 knowledge guarantee. The prior C4 tie-break counterexample still applies.

One distinction is essential: a standard discernibility formula can intentionally omit empty entries. Applying that formula without a separate inconsistency check would erase exactly the aliasing case C4 promises to report. The mapping below preserves the check rather than claiming a false literal identity.

## Primary methods inspected

All URLs in this report were accessed **2026-09-07**. No listed source is an arXiv preprint.

- **Pawlak, 1982, published research article:** *Rough Sets*, International Journal of Computer and Information Sciences 11, 341–356. Complete §2, including the information-system example, was read. It defines attribute-relative indiscernibility, lower and upper approximations, and the boundary between certain inclusion and exclusion. The available description language cannot distinguish objects with identical attribute values. [Primary paper, university-hosted copy](https://wiki.eecs.yorku.ca/course_archive/2013-14/F/4403/_media/rough_sets.pdf). PDF SHA-256 `493193df7fa4e0dc30d8cef4bb5b08c13d423778447aa2734b97813ab47ed1ce`.
- **Pawlak and Skowron, 2007, published author survey and method exposition:** *Rough sets and Boolean reasoning*, Information Sciences 177, 41–73. Complete §§2.1 and 2.4 were read; the printed discernibility definition on p.43 was also visually checked. It specifies pairwise difference sets, their Boolean discernibility formula, and construction of minimal decision rules from a particular object's row. Its ordinary formula excludes empty entries; its decision-relative construction initially assumes a consistent table. This is a direct author exposition of the method, **not proof of its earliest publication date**. [Author-archive PDF](https://bcpw.bg.pw.edu.pl/Content/1970), [publication DOI](https://doi.org/10.1016/j.ins.2006.06.007). PDF SHA-256 `93126ade4f0879503bc807357ec8ce412eeeab52ca7f86719fe798f6f372f3ae`.
- **Petrick and Bacchus, 2002, published AIPS paper:** *A Knowledge-Based Approach to Planning with Incomplete Information and Sensing*, pp.212–221 in the inspected proceedings PDF. The representation, query, action, consistency, planning and plan-correctness sections were read completely. PKS distinguishes known-positive, known-negative and incomplete knowledge. Its action preconditions must be established; sensing enables branches when their result will be available. The paper expressly assumes correct knowledge and restricts both its representation and inference. [Primary proceedings PDF](https://cdn.aaai.org/AIPS/2002/AIPS02-022.pdf). PDF SHA-256 `2af08a6e888d5b68ae45399659cc2e27a8aa5d1ce6b25cb91ff7d8190c187e6a`.

The equations and histories below are derivations from the approved C4 definition using these explicit mathematical objects. They are not quotations or claims that the earlier authors wrote this programme's labels or wrapper. Skowron–Rauszer 1992 remains a historical lead; no decisive assertion here depends on obtaining its chapter. Reiter's diagnosis framework is not needed to prove the finite Boolean reduction, so a broad diagnosis analogy is not substituted for the more direct local mapping. No new human paper request is necessary for these scoped findings.

## 1. Aliasing is a local rough-boundary certificate

Fix one C4 instance `(F,a,t,seed)` and let its retained admitted universe be \(U=P\cup N\). Here \(U\) contains encounter rows, identified separately even when their descriptors or full atom signatures are identical. Each row carries its own observed outcome; rows with the same descriptor and opposite outcomes are distinct members of \(P\) and \(N\), so those sets remain a well-defined partition of the admitted rows. In the notation below, atom tests and \(F\) act on a row's descriptor. Define the signature

\[
\sigma(x)=(A_1(x),\ldots,A_m(x)),\qquad
x\sim_A x'\iff\sigma(x)=\sigma(x').
\]

Every member of \(U\) has an observed outcome, so its binary decision value \(d(x)=\mathbf1[y=F(x)]\) is defined. An encounter missing the required observation is outside this universe; it is not a negative decision value.

Take the positive set to be \(P\subseteq U\). Its lower approximation contains precisely those equivalence classes entirely inside \(P\); its upper approximation contains classes meeting \(P\). Because the seed \(s\) is positive,

\[
\exists n\in N:\sigma(n)=\sigma(s)
\iff [s]_A\not\subseteq P
\iff s\in\overline A(P)\setminus\underline A(P).
\]

This is exactly the predicate underlying C4's `observational_aliasing` label. Returning `s` and the first matching negative is a deterministic witness selection over the same finite class. The first-witness convention changes the returned identifier when the fixed ordering changes, but does not change feasibility.

The nonseparability proof is stronger than a conjunction-specific claim. For any Boolean expression \(g\) over the supplied total tests, equal signatures imply \(g(\sigma(s))=g(\sigma(n))\). Thus neither a longer conjunction nor arbitrary Boolean rearrangement of these same tests can distinguish the pair. The certificate is relative to the tests and admitted observations. It says nothing about whether the physical world contains a distinguishing signal outside this interface.

**State, update and memory.** The correspondence maps C4's witnesses to rows of a decision table; it does not substitute a summary that discards them. Adding an admitted encounter extends the same table, and recomputing the seed's equivalence class gives the same alias predicate after every history. The full class need not be built: a scan against the stored seed signature suffices. Keeping full descriptors, outcomes, action/provenance and fixed definitions costs the same memory channel as C4. A context clearing that preserves this table changes neither output; erasing it changes both. Neither a static rough-set definition nor C4 supplies a validity update for an unobserved physical world change.

**Robustness limit.** The word `aliasing` must not become the stronger diagnosis “a missing world variable caused this.” A positive and negative with the same signature can arise from a missing observable, corrupted outcome, erroneous provenance tag, stochastic response, world drift, or an unsuitable proposed \(F\). The same admitted record is compatible with these causes. A new predicate may be a permissible upstream request, but its usefulness and even its existence are not established by the certificate.

For example, compare a world with an unobserved binary condition that changes the outcome against a world where \(F\) is always correct but one recorded outcome is corrupted. Both can produce the same positive/negative signature pair. C4 and the matched boundary check report the same alias. No computation on that record chooses between the causal explanations. This is a mathematical indistinguishability witness, not a noise experiment.

## 2. The length diagnosis is bounded local discernibility, not missing information

For each negative row let

\[
D_n=\{i:A_i(n)\ne A_i(s)\},\qquad
\Phi_s(b)=\bigwedge_{n\in N}\bigvee_{i\in D_n}b_i,
\]

where \(b_i=1\) means selecting the literal agreeing with the seed on atom \(i\). Here an empty disjunction is **false** and an empty conjunction is **true**. This differs deliberately from a formula designed merely to preserve already-existing discernibility while omitting inseparable pairs.

C4's feasible conditions correspond exactly to the solutions of

\[
\Phi_s(b)=1,\qquad\sum_{i=1}^{m} b_i\le k.
\]

If any \(D_n=\varnothing\), unrestricted Φ is false and the alias certificate above applies. If every \(D_n\ne\varnothing\), setting all \(b_i=1\) satisfies Φ. Consequently, when complete bounded search finds no solution in the latter case, its failure is exactly a cardinality-bound failure:

\[
\tau(\{D_n\})>k,\qquad
\tau(\mathcal D)=\min\{|J|:J\cap D\ne\varnothing\text{ for all }D\in\mathcal D\}.
\]

The collection is a seed-specific row of discernibility constraints. C4's optimum is among its minimal hitting sets: removing a redundant selected atom cannot reduce positive coverage and improves the length tie break. Filter those alternatives by \(k\), then apply C4's exact positive-coverage/length/identifier preference. This preserves the selected condition, not merely its training accuracy. The prior AQ certificate already establishes the same selection objective from another direct antecedent.

There is a useful domain distinction. A globally inconsistent table may have a positive/negative signature collision **away from the fixed seed**, while the seed itself remains separable. C4 may still return a local scope. A comparator demanding global table consistency would reject too much. The exact construction uses the seed-to-negative rows and separately checks seed aliasing; it does not import an all-table consistency condition from a general reduct algorithm.

| C4 object | Matched discernibility object | Update or restriction |
|---|---|---|
| Fixed total atom library and seed | Fixed signature coordinates and seed row | Supplied structure; no learned predicate expansion |
| Negative encounter | One set \(D_n\) and its witness pointer | Conjoin its exclusion constraint |
| Positive encounter | One positive signature and retained descriptor | Update coverage preference; no new hard exclusion |
| Empty seed/negative difference set | Unsatisfiable local exclusion clause | Return the alias witness; do not omit this clause |
| No bounded solution, all clauses nonempty | No hitting set of size at most \(k\) | Return the retained witness collection and bound |
| Selected scope | Preferred bounded local prime implicant | Same coverage and deterministic tie order |
| Episode/context clearing | No change to the persistent table and definitions | No implicit reset or evidence eviction |
| New physical regime | No automatic mapping supplied | Old table may be stale; no correctness guarantee follows |

**Histories.** With seed `(1,1)`, negative `(0,1)`, and \(k=1\), the sole required difference set is `{1}` and the first atom suffices. Append negative `(1,0)`: the sets become `{1}` and `{2}`; every pair remains separable but the collection has no allowed one-literal scope. C4 and the bounded hitting-set predicate both report `length_bound`. In a separate instance with \(k=2\), the conjunction succeeds; this comparison changes a supplied bound and is not an in-instance automatic repair. Append a negative with seed signature `(1,1)` instead: the empty clause makes aliasing decisive at any bound. A raw discernibility implementation that discards this clause is not a matched comparator.

**Capacity is not computation failure.** An exact infeasibility statement needs an exhausted finite search or another checkable unsatisfiability certificate. A solver timeout or a truncated star is not evidence that τ exceeds \(k\). A witness set is enough to recompute the decision but is not automatically a small or cheaply checkable proof of bounded infeasibility. The approved operation names exhaustive search, so this audit does not silently grant an approximate solver that returns a stronger diagnostic than it established.

**Costs.** Let \(N_w=|P\cup N|\) and \(B(m,k)=\sum_{j=0}^{\min(k,m)}\binom mj\). Evaluating/caching all signatures costs \(mN_w\) atom evaluations, with their actual input-dependent cost. A simple seed-alias scan takes \(O(m|N|)\) scalar comparisons once the descriptors are present. Direct bounded selection uses \(O(B(m,k)N_w\max(1,k))\) scalar condition work and retains all witnesses plus signatures if cached. A solver or prime-implicant procedure may search differently; equal objective does not prove equal runtime or memory. C4 supplies no asymptotic improvement over the matched finite construction. The full difference matrix is unnecessary: only seed-to-negative entries are required, so charging the comparator a gratuitous \(N_w^2\) table would be unfair.

## 3. Unestablished conditions and contradictory proposals are different cases

PKS supplies an explicit historical antecedent for demanding knowledge of a precondition before relying on an action. The following restricted mapping concerns that **use test**, not an identity between C4's learner and the whole PKS planner.

Represent available descriptor facts in a consistent partial fact store \(D^+,D^-\), with neither membership meaning unknown. For a seed-compatible literal ℓ, require `established(ℓ)` before using it; for a conjunction require every component established. A known-false literal blocks the condition; an unknown literal also fails to establish it, without asserting its negation. On this ground-literal fragment, the condition guard corresponds to a conjunction of PKS knowledge queries. Insert a fact only from the same declared observation or warranted predecessor output supplied to C4; no new oracle or free proof is provided by the translation.

For a sequence, apply the same established-condition test at each step after its admitted effects become available. For example, a first rule licenses response \(v\), while the second requires an unrelated atom \(A(x)\). Merely receiving \(v\) does not establish \(A(x)\). If neither polarity of \(A(x)\) is available, C4's composition check and the restricted knowledge-precondition guard both stop licensing that step. A later legitimate observation establishing \(A(x)\) can enable it. Treating a total test as evaluable on an unavailable descriptor is precisely the interface error this guard excludes.

The map is only as exact as the supplied establishment relation. C4 does not specify a general inference calculus for what predecessor outputs warrant; PKS's full inference procedure is itself restricted. This audit does not claim equal behavior for arbitrary relational consequence finding, or turn an empirical C4 prediction into factive knowledge merely by writing \(K\) around it. That would assume the scientific guarantee under investigation.

**Conflict handling needs an additional reporting convention.** Let

\[
V(x,a,t)=\{F_r(x):r\text{ is an established, matching applicable stored rule}\}.
\]

For the part of the use interface that C4 specifies, multiple distinct elements trigger unresolved; one distinct element is the common proposed response. With no licensed proposal, none is fabricated. This is an exact set-aggregation expression of its conflict guard. A matched comparison retains rule identities and reports their distinct proposed outputs before release; it does not majority-vote, reward-rank, or erase disagreeing proposals.

It would be wrong to identify this directly with PKS's consistency maintenance. PKS assumes a consistent knowledge store; C4 can retain contradictory *observations or proposals*. Such observations can be represented consistently as statements about what each witness or rule reports, but the extra disagreement-to-unresolved guard is still an explicit wrapper. The inspected paper does not establish historical identity of that whole report interface.

With two rules both known applicable and proposing distinct responses, the guard reports unresolved even if one rule has far more prior reward. After a context clearing preserving those rules and observations, the disagreement remains. Deleting the losing rule would change the operation. Conversely, two alternative scopes for **one** rule that are not materialized as separate stored proposals are not two stored conflicting rules: C4's existing tie-break counterexample still licenses an unwarranted reuse. Their absence from the selected proposals is not erased information: the retained witnesses and atom definitions suffice to reconstruct both scopes. Strict conflict handling does not imply consensus over all evidence-compatible scopes. See the exact reconstruction correction in `evidence/P3_JOINT_AUDIT_BOUNDARY_2026-09-07.md`.

**Allocation and costs.** The comparison needs the same stored rule definitions and establishment evidence. For \(r\) queried rules with at most \(k\) literals, direct applicability checks cost \(O(r\max(1,k))\) primitive evidence queries plus actual \(F_r\) evaluation, output comparison, and any inference used to establish conditions. Sequential checking charges each step; PKS plan search is a different operation and is not a free component of this bound. C4 does not prescribe a new planning search or a cost improvement here.

## 4. Provenance routing and witness retention

The state is a keyed collection of local instances. The key `(F,a,t,seed)` selects which table an admitted event can update. Re-expressing that state as a map from declared keys to decision tables gives the same input admission, table update and query guard. The equality tests on action/provenance are outside the learned \(k\)-atom scope in C4; a comparator that spends two of its allowed \(k\) literals on those already-supplied guards would have a different language budget.

A missing observed outcome contributes no class label. An outcome under a different tag does not contradict this instance, even with an identical descriptor. Those are consequences of the supplied admission rule, not inferred judgments about sensor trustworthiness. They require no new latent variable and discover no provenance. Routing to many keys can retain redundant evidence; the total memory and indexing cost must be counted across all instances, not reported per rule while hiding proliferation.

For a concrete history, two identical signatures with opposite outcomes under the **same** declared tag create seed aliasing. Changing the negative's tag to a different supplied tag means it never enters this instance. C4 and the keyed-table construction agree. If the supplied tags were wrong, either routing could conceal a real contradiction or manufacture one. Keeping a provenance field does not validate it.

Witness retention is operationally meaningful: it makes the alias pair and the bounded problem reconstructible after discontinuity. The already-inspected AQ full-memory antecedent supplies a direct historical comparator for retaining examples. This audit does not claim that a rough-set table by itself entails a lifelong append-only event policy, nor that witness retention establishes truth. The matched construction keeps the same admitted encounters because those are C4's declared inputs and state, not because extra history is granted for free.

## 5. Whole-interface mapping, limits and scientific consequence

For a complete audit comparator, keep the same keyed witness tables and fixed definitions, compute seed indiscernibility, solve the bounded local discernibility selection with the previously matched preference, then apply the same explicit establishment and proposal-conflict guards. Preserve that state through the declared context clearing. An induction over admitted events shows equality: equal table and definitions imply equal signatures and feasible sets; equal preferences imply equal scopes; equal query evidence implies equal use guards and returned witnesses. Non-admitted events leave both states unchanged. No distinguishing history exists for this constructed comparator because every specified transition and reporting function is mapped.

This is a **constructive functional decomposition**, not proof that one historical package implemented the exact composition. The nontrivial historical claims are narrower: seed-relative indiscernibility and local discernibility selection have explicit antecedents; requiring an established precondition has an explicit planning antecedent; full-memory rule learning was already checked. The residual “all these labels in one interface” proposition has not been established as historically first, scientifically effective, or a new inference. No broad Reiter analogy or whole-PKS identity is needed to make those judgments.

The strongest alternative explanation for a future gain remains an unequal comparator: one implementation retains all evidence, completes more search, uses supplied provenance, or refuses more predictions while the other does not. A fair comparison would expose those differences separately and report coverage as well as error. Such an experiment could investigate the value of the contract, but it would not undo the reductions.

The second alternative is that the failure label identifies a physical cause. The same-record noise/missing-condition construction rules that out without extra evidence. The third is that this wrapper repairs premature commitment generally. The preserved two-scope tie-break counterexample rules that out for the approved operation. These analytical checks address the strongest claims before allocating a candidate treatment run.

## Historical restrictions and the 2026 decision

The sources do not show universal abandonment of rough sets or knowledge-based planning. They show that relevant work existed and state restrictions that matter. More compute can move the practical boundary for explicit conjunction or prime-implicant enumeration and can reconstruct alternative scopes from C4's retained witnesses. It does not by itself change the specified selected-scope response rule, make two equal observed signatures distinguishable, establish a missing precondition, or validate a provenance tag. The exact reconstruction correction in `evidence/P3_JOINT_AUDIT_BOUNDARY_2026-09-07.md` separates recoverable alternatives from the rule that actually releases a response. Larger retained tables can also increase the complete-search problem. These conclusions follow from the mapped operations, not from an unmeasured estimate of this laptop or Alliance allocation.

The appropriate next step is to include these scoped certificates and their caveats in the independent audit packet. **No treatment implementation, additional book request, or new scientific approval is needed merely to test whether the wrapper's named diagnostics perform these familiar operations.** Any later claim of a new joint uncertainty guarantee must still specify and audit the common state and answer path separately.

## Retrieval and process record

Private PDFs, extracted method text, rendered definition pages and `retrieval.json` are under `private_sources/P3_C4_WRAPPER/`; none is proposed for public redistribution. A fourth accessible author PDF, Yao and Zhao's *Discernibility Matrix Simplification for Constructing Attribute Reducts*, was retrieved as a potential additional comparator but is not relied on for the certificate; its full methods were not audited here. No argument depends on its abstract. All four public downloads succeeded. No command failed during this bounded subtask. Draft inspection caught lost inline-math escape delimiters and then overbroad replacement inside function arguments; these formatting errors were corrected before handoff. Long combined read output was truncated once; the omitted PKS method pages were subsequently read in explicit page-bounded excerpts before writing this report.
