# Chvatal primary-method supplement for N1

2026-09-11. PI-side source analysis, not a formal independent disposition or an empirical result. This supplement closes the method-access dependency recorded in `evidence/P3_SECOND_N1_PRIMARY_AUDIT_036.md`; it does not edit that frozen audit or the operation specification. No candidate treatment was implemented or run for this analysis.

## 1. Source identity and complete reading

**Source:** Vaclav Chvatal, *A Greedy Heuristic for the Set-Covering Problem*, **Mathematics of Operations Research 4(3), August 1979, pp.233-235**, published journal article, not a preprint. [DOI: 10.1287/moor.4.3.233](https://doi.org/10.1287/moor.4.3.233); [JSTOR stable record](https://www.jstor.org/stable/3689577). **Access date: 2026-09-11, through the user-supplied complete PDF.** These URLs identify the publication; the supplied PDF, rather than publisher metadata or an abstract, is the method evidence.

| Item | Verified identity or reading scope |
|---|---|
| Supplied filename | `Chvatal-GreedyHeuristicSetCovering-1979.pdf` |
| Supplied PDF SHA-256 | `70e60317cc1e7815118aac54b00d3aadf5558f7bc219ca2d3b6e3396c2611086` |
| PDF page 1 | Archive cover and bibliographic identity; no printed journal page number |
| PDF page 2 / printed p.233 | Problem definition, all three algorithm steps, harmonic-factor example and definition of largest-set parameter |
| PDF page 3 / printed p.234 | Theorem, stronger fractional-cover inequality, incidence-matrix formulation and charging proof setup |
| PDF page 4 / printed p.235 | Completion of charging proof, harmonic summation and references |
| Actual scope | All four PDF pages read; all three substantive journal pages rendered and visually inspected, including equations obscured in extracted text |

Only original analysis and bibliographic information are included here. The supplied PDF, extracted paper text and rendered pages remain outside the public project.

**Compared frozen inputs, read 2026-09-11:**

- [Second operation specification, N1 and shared contract](https://github.com/afazeliUofT/arc-independent-lab/blob/17bd0df7a4d60f6ddfcffefc73049b1471a5ffd1/docs/P2_SECOND_OPERATION_SPECIFICATIONS_035.md), SHA-256 `25f3148827d22abbe587a6c2ff0c5a3ff2db1883f70e678f640f16d0f07a7c69`.
- [Checkpoint036 N1 primary audit](https://github.com/afazeliUofT/arc-independent-lab/blob/91bbec3e2900f18d2c2baef325d575a26e362165/evidence/P3_SECOND_N1_PRIMARY_AUDIT_036.md), SHA-256 `0cef34db2488ec13fb37a9700582cce136538a9569d7c6f7fe96bcb36e602ebc`.

## 2. What the original algorithm actually selects

Chvatal starts with a fixed finite collection of sets and strictly positive set costs. Its required universe is their union, so a cover exists. At each iteration it selects a set with maximum **remaining uncovered cardinality divided by that set's cost**, charges the selected cost, removes the newly covered elements from every set, and repeats until no uncovered element remains. The costs do not change as residual sets shrink. The algorithm begins with an empty selected collection. [Chvatal, printed p.233 / PDF p.2, accessed 2026-09-11](https://doi.org/10.1287/moor.4.3.233).

The paper leaves ties between ratio maximizers unspecified. Any maximizing choice is admitted; its proof uses a non-strict maximizing inequality and does not need one special tie order. With every cost equal to one, the selection becomes maximum uncovered cardinality. Equal positive costs give the same selection ordering after common scaling. This is the relevant reduction to N1, **not** assigning expression length or computational expense as Chvatal's set cost. [Chvatal, printed pp.233-235 / PDF pp.2-4, accessed 2026-09-11](https://doi.org/10.1287/moor.4.3.233).

In N1, smaller syntax size matters only among predicates with identical integer gain. Maximizing `gain(p)/size(p)` can prefer a smaller-gain predicate and changes the frozen algorithm. Neither actual predicate evaluation cost nor memory expenditure is optimized by the equal-unit-cost reduction. Those expenditures remain explicit resource charges in the N1 wrapper.

## 3. Exact selection-step mapping and its conditions

The following equations are deductions from frozen N1, extending the explicit pair construction in the checkpoint036 audit. Fix one active-block table version, grammar/token-inventory version and retained selected prefix. Keep acquisition identities even for rows with duplicate contents. Let `E` be all unordered row pairs having the same current observation and issued prediction action, but different observed next observations. For candidate `p`, define

\[
C_p=\{\{i,j\}\in E:p(h_i)\ne p(h_j)\},\qquad
U_\Phi=\bigcup_{\phi\in\Phi}C_\phi,\qquad
R=E\setminus U_\Phi.
\]

A pair conflicts under the full N1 key precisely when it belongs to `R`. Its gain rule is therefore

\[
\operatorname{gain}(p)=|C_p\cap R|.
\]

For the next selection, use Chvatal residual sets `P_p = C_p ∩ R` for all not-yet-selected legal grammar trees, each at cost one. Choose a maximum-cardinality nonempty residual set. Among ties apply N1's syntax-size and serialization ordering. After choosing `p`, replace every residual set by its difference with `P_p`. This is exactly N1's next positive-gain selection and residual update. Iteration reproduces the committed prefix for as long as the frozen version and sufficient resources persist. [N1 specification and checkpoint036 audit, read 2026-09-11; links and hashes in section 1.]

| Required matching condition | Consequence if omitted |
|---|---|
| Same base observation/action key and pair acquisition identities | Different required pair multiplicities or unnecessary feature-budget charges |
| Same finite grammar, encountered constants, types, history limits, Boolean semantics and serialized syntax identities | A different candidate set, even when some candidates agree on sampled histories |
| Equal positive cost per candidate; N1's explicit gain/size/serialization priority | Weighted gain/cost or another tie order can choose a different predicate |
| Same retained selected prefix | A fresh batch run on the final data need not reproduce N1's irreversible online history |
| Complete candidate pass before commitment, with the same version/cursor rules | Partial or stale evaluations can change the maximizer |
| Same caps, count reconstruction, evidence retention and boundary contract | Selection-step identity alone does not reproduce N1's outputs and statuses |

One can choose the original paper's arbitrary maximizer according to N1's tie rule. That establishes a compatible specialization, not historical evidence that the 1979 implementation used N1's tie rule. The original paper provides neither N1's history grammar nor its online schedule, count-based predictor, interruption statuses, block archives or persistence interface. The full trace-equivalence comparator remains the explicit **constructed wrapper** in the checkpoint036 audit; attributing that whole package to Chvatal would overstate the source.

**Uncoverable pairs are a substantive boundary.** Let

\[
R_{\mathrm{coverable}}=\bigcup_{p\ \mathrm{unselected}}(C_p\cap R).
\]

Chvatal's universe for the residual construction is this union. N1's unresolved evidence also contains `R \ R_coverable`, which no currently legal predicate separates. The original set-cover procedure need not represent those extra pairs; N1 must preserve and report them. Reaching zero positive gain can certify complete coverage of the coverable union while leaving N1 conflicts unresolved. It does not certify a consistent predictor or latent-state identification. Computing this distinction still requires the completed grammar search; resource interruption is not proof of uncoverability.

## 4. What the approximation theorem does and does not transfer

For a fixed finite feasible instance, let `d` be the largest **initial** set cardinality and `H(d) = sum_{k=1}^d 1/k`. Chvatal proves that completed greedy cover cost is at most `H(d)` times the minimum cover cost. The proof actually establishes a stronger inequality against every nonnegative fractional cover: each comparison-set cost receives its own factor `H(|P_j|)`. It assigns each newly covered element an equal share of the chosen set's cost and bounds the resulting charge on any comparison set by a harmonic sum. [Chvatal, theorem and proof, printed pp.234-235 / PDF pp.3-4, accessed 2026-09-11](https://doi.org/10.1287/moor.4.3.233).

With unit set costs, a compatible **complete batch** N1 selection from an empty prefix on an unchanged, fully coverable pair instance inherits a bound on the **number of selected predicates** relative to the minimum number of available predicates covering that same instance. The empty universe is the separate trivial case with no additions. The bound is neither on predictive error nor on search runtime, memory, required interactions, causal correctness or transfer.

For an arbitrary retained N1 prefix `Phi_0`, a narrower conditional statement is available. Freeze the present table and grammar; initialize residual sets as in section 3; and suppose the greedy continuation completes their cover before any feature or resource limit interrupts it. If `d_R` is the maximum size of those initialized residual sets and `OPT_add` is the minimum number of available additions covering their union, then

\[
|\Phi_{\mathrm{add}}|\le H(d_R)\,\mathrm{OPT}_{\mathrm{add}}.
\]

This is an application of the source theorem to a newly defined residual instance. It charges **additional** predicates only. It does not bound the quality of the previously accumulated prefix, establish a total-prefix approximation to a fresh global optimum, or cover any retained inseparable pair outside that union.

The frozen online operation does not satisfy those completion conditions automatically:

1. **New data change the universe.** Appended transitions introduce required pairs. Newly observed tokens can activate candidate columns. N1 retains earlier selections instead of restarting the paper's static optimization.
2. **The grammar restricts feasibility.** Finite history and expression bounds can leave conflicting pairs outside every candidate set. Even a completed cover of available distinctions need not cover all conflicts.
3. **Caps can stop before coverage.** `K`, memory and computation limits can leave coverable pairs unresolved. Chvatal's completed-cover cost theorem is not a maximum-coverage guarantee for a truncated selection. Any such claim would require a separately stated objective and proof.
4. **Versions and resets matter.** A valid resumed static pass can preserve the selection identity; a changed table or token inventory invalidates its cursor. A new world block changes active empirical evidence and cannot be treated as the same optimization instance.

The checkpoint036 witness in which pair count falls while outcome distributions remain unchanged is unaffected. A set-cover approximation theorem concerns coverage cost on supplied sets; it supplies no missing connection between raw pair gain and useful predictive information.

## 5. Dependency disposition and programme relevance

**Closed:** original-method access for Chvatal's greedy rule, its equal-cost specialization, tie latitude and harmonic approximation theorem. The checkpoint036 conditional request is satisfied by the complete user-supplied paper. The earlier algebraic N1 decomposition is supported at the level of a named historical selection rule; it no longer needs to suspend that limited attribution for lack of method access.

**Not established:** earliest priority for every component; a historical implementation of N1's entire online package; efficacy in acquiring reusable world knowledge; or a formal independent novelty verdict. On printed p.233 the author explicitly attributes the equal-cost theorem to Johnson and Lovasz, and p.235 identifies their 1974 and 1975 papers. That is **Chvatal's attribution**, not a claim that their original methods were inspected here. It prevents calling the unweighted rule or theorem uniquely original to Chvatal. Earliest-priority reconstruction would require those originals, but it is not needed to close this dependency or to assess the frozen N1 claim.

**Further papers required for this dependency: none.** Do not expand the user's paper request merely to collect every cited predecessor. Request Johnson or Lovasz only if a later, concrete claim actually turns on their original formulation or historical priority.

The paper identifies optimization difficulty as the reason to study approximation; it does not establish that the method was abandoned, nor explain subsequent uptake. A 2026 inference is limited to this: additional compute can permit more candidate construction and evaluation, but it does not change the selection objective or turn sample pair coverage into retained, recombinable knowledge. The scientific next step remains the programme's independent assessment of the frozen candidate and its supplied-object and predictive-use limits, now with this method dependency closed.
