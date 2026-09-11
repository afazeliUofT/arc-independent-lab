# N2 primary-method audit: finite context signatures and substitution

Prepared 2026-09-10 for the PI. This is a research consultation using shared context, tools and filesystem, not an independent review or a formal GO/KILL decision. No candidate model, native reviewer, benchmark or paid-API run was performed. Hosted research consultation did occur. The histories below are deductions from the frozen rules, not execution results.

**Supported residual claim:** N2 specifies a bounded, physically charged interface for acquiring and retaining finite contextual signatures of executed action fragments and issuing explicitly defeasible substitution proposals. Context signatures, substring-derived categories and recombination from their relations already belong to established observation-table and distributional-grammar families. The signature operation itself is not a new learning principle. N2 is not exactly the complete published learners audited below, but those differences do not establish whole-package priority or useful acquisition–retention–recombination through interaction.

## Frozen basis and reading record

The repository HEAD was verified as `17bd0df7a4d60f6ddfcffefc73049b1471a5ffd1`. The inspected `docs/P2_SECOND_OPERATION_SPECIFICATIONS_035.md` SHA-256 was `25f3148827d22abbe587a6c2ff0c5a3ff2db1883f70e678f640f16d0f07a7c69`. N2 and the shared contract are unchanged. Phase 3 requirements in `docs/governing/02_RESEARCH_PROCESS.md`, paper-request format in `docs/governing/04_RESOURCES_AND_SETUP.md` §5, and the post-freeze nearest-method flags were read.

All public URLs in this audit were accessed **2026-09-10**. These are full-method sources, not abstract-only comparators. A second research consultant checked the recent continuation; that consultation had the same limitations of independence as this audit.

| Source | Status and method coverage in this pass |
|---|---|
| [Angluin, *Learning Regular Sets from Queries and Counterexamples*][A], 1987; [verified institutional PDF][AM] | Published journal paper. Newly opened the institutional 20-page PDF and read §§1.1–1.2, 2.1–2.2, complete Figure 1 learner, time analysis and §4 sampling variant. Prior durable notes were read first: `P3_THROUGHLINE_PRIOR_METHODS.md` and `P3_REVIEW_METHOD_COVERAGE_2026-09-07.json`. Their prior PDF hash is `1dde8daec314d13fa64126495b756cf0ef7042d9ad6e36f2c8845b9dffc06aa3`; today's web copy was not downloaded or byte-hashed. A successful new institutional opening is distinct from rereading those notes and from the prior DOI-redirect failure. |
| [Clark and Eyraud, *Polynomial Identification in the Limit of Substitutable Context-free Languages*][S], 2007 | Published JMLR paper, 21 pages. Definitions, complete SGL Algorithms 1–2, §3.3 cost, §4 assumptions/proof, §5 reduction-system alternative and §§7.3–8 limitations inspected. No claim that the shorter 2005 version is identical. |
| [Clark, Eyraud and Habrard, *Using Contextual Representations to Efficiently Learn Context-Free Languages*][C], 2010 | Published JMLR paper, 38 pages. §§2–4 definitions, finite features, grammar construction, fiduciality, finite kernel, complete Algorithm 1 and identification argument; final practical limitations inspected. The expressiveness catalogue and appendix grammar are not relied upon. |
| [Laumen, Snel and Vaandrager, *An L# Based Algorithm for Active Learning of Minimal Separating Automata*][R], 2026 | **Preprint v1, 2026-05-14**, inside the last six months, 2026-03-10–2026-09-10. Versioned full HTML. Consultant read §§1–6 and selected Appendix B lemmas; lead researcher additionally checked teacher semantics, §§2–3 complete rules/SMT encoding/query theorem and §§5.2–6 limitations. Artifact not inspected. |

PDF algorithm pages were also opened through the screenshot route; text/formula claims above rely on the readable full-text extraction. No full copyrighted paper or extracted full text is included in this deliverable.

## What the N2 relation actually computes

Let `A` be the supplied primitive alphabet. Within a resettable deterministic block, write `h(w)` for the actual final observation after RESET followed by `w`. This is notation for an unknown physical response, not an available simulator. Let `P=((u_1,v_1),...,(u_j,v_j))` be the current panel, with `j <= J`. On fragments whose panel cells are all valid and repeatable, N2 stores

`sigma_P(f) = (h(u_1 f v_1),...,h(u_j f v_j))`

and defines `f ~_P g` exactly when these complete vectors are equal. This is an equivalence relation on the currently classified subset. It is not an equivalence on partially observed fragments, and it is not a congruence of the world.

The exact finite-table correspondence is: objects = acquired fragments; tests = panel hole-contexts; cells = observed endpoints; categories = equal rows. This is component identity under renaming, not merely thematic resemblance. Boolean language membership is recovered by fixing an endpoint `y` and considering `K_y={w in A+:h(w)=y}`. Restricting these grammar-comparison languages to nonempty words respects the grammar papers' empty-word convention; every queried composition here contains a nonempty fragment. N2's categorical row corresponds to the collection of membership rows for all endpoint classes. The adapter is an audit construction; N2 does not receive the languages `K_y`, their grammars or their labels for unexecuted words.

Universal endpoint contextual equivalence would require `h(ufv)=h(ugv)` for **every** context `(u,v)`. N2 observes finitely many such equalities, imposes length `L`, and explicitly does not assume the universal premise. Even agreement on every valid word up to `L` would not imply unrestricted equivalence. Context-feature representations and their relationship to syntactic congruence are already explicit in [Clark and colleagues][C]; the new contribution cannot be the act of writing down such a vector.

| Variable/dimension | Frozen N2 state and operation |
|---|---|
| State | Ordered fragment library `F`; acquired hole-contexts `C`; complete and incomplete traces; word-effect records; panel/version; signatures; failed substitutions; block provenance; resource counters. |
| Input | Finite action and observation alphabets, exact serialization, resettable stationary block, `L,J,m`, three resource ceilings; actual observations; validated `(u,v,f,g)` queries. No equivalence teacher or supplied structural grammar. |
| Update | Actual words add all nonempty contiguous fragments and hole decompositions. Only `m` completed agreeing trials support an endpoint. Complete panel vectors are regrouped after relevant version changes. Direct effects override a conjecture; VARIABLE overrides deterministic inference. |
| Allocation | Seed each primitive once. Prioritize the oldest valid acquired `C × F` combination missing repetitions, then the first unexecuted primitive word. Panel selection is the first `J` distinct contexts, not a discrepancy-driven search. |
| Reset/retention | Physical RESET costs one call per trial. Volatile clearing retains all specified persistent fields. A new block archives old empirical evidence and starts new active effects; old roles are hypotheses. This is retention by an explicit storage contract, not demonstrated recovery after deleting that storage. |
| Cost | Each new trial of `w` costs `1+|w|` environment calls. Shared decompositions reuse the same actual trace records. Direct cell accounting gives an upper bound `m sum_valid_cells(1+|ufv|)`, not an obligation to duplicate already acquired trials. Signature work is `O(J|F|)` endpoint comparisons plus grouping/order work. All traces, archives, cursors and checks count; no memory/computation bound is free. |

The full word space has `sum_(ell=1)^L |A|^ell` nonempty words. Exhaustive finite coverage can therefore be expensive even before fragment/context bookkeeping. If the panel contains any nonempty context, a length-`L` fragment cannot have a complete signature in that panel. Enlarging `J` can eliminate coverage rather than merely improve precision. These are deductions from the frozen limits.

## Exact comparator mapping

The comparator cells below are intentionally compact; the consequences and histories are this audit's deductions. No teacher cost is equated with physical interaction cost.

### Angluin 1987: a complete observation-table learner

| Dimension | Published variable/procedure | N2 correspondence or obstruction |
|---|---|---|
| State | `(S,E,T)`, DFA `M` | Fragments can index rows and contexts can index tests, but N2 has no DFA transition construction. |
| Input | Alphabet; membership and equivalence teacher | `Trial(w)` can implement a charged membership observation for `K_y`; no equivalence oracle is supplied. |
| Update | Close/repair consistency; add counterexample prefixes | N2 regroups existing panel rows; it does not repair transition consistency. |
| Allocation | Missing table entries; distinguishing suffixes | N2's acquired-context order is a different scheduler. |
| Reset | Query protocol; retained table | N2 must add physical resets, repetitions, interruption and block semantics. |
| Cost | At most `(k+1)(n+d(n-1))n` table strings; lengths at most `d+2n-1` | Here `n` is target DFA size, `k` alphabet size, `d` longest counterexample, not N2's repetition count. Physical query implementation and equivalence testing remain additional costs. |

These facts follow from [Angluin §§1–2][A]. Its sampling variant still needs an independent labeled-example source and changes the guarantee. Neither random examples nor exact equivalence are generated merely by N2 having a reset command.

**Not an exact whole-learner reduction:** disabling consistency, equivalence and adaptive suffix growth changes the algorithm. Nevertheless, equality of finite response rows is the old component, and freezing/charging it does not itself supply a new inference principle.

### Clark–Eyraud 2007: Substitution Graph Learner (SGL)

| Dimension | Published variable/procedure | N2 correspondence or obstruction |
|---|---|---|
| State | Positive sample, substring graph, components, grammar | `F` matches substring nodes; a role is not generally a graph component. |
| Input | Positive presentation; substitutable target language | Endpoint-specific positive samples require an explicit adapter; N2 assumes no substitutable target. |
| Update | Shared-context edges, component closure, binary split productions | N2 demands complete vectors and constructs no recursive grammar. |
| Allocation | Rebuild when the next positive word is ungenerated | N2 actively selects reset-and-word trials. |
| Reset | No physical execution/reset model | N2 adds a physical acquisition contract. |
| Cost | With total sample length `N`, maximum length `ell`, count `r`: at most `N²` nodes; graph work `O(ell²r²)` under stated indexing; at most `ell N²` productions | This is sample-processing cost, not N2's environment-call budget. |

The full definitions and Algorithms 1–2 are in [SGL §§2–4][S]. Its target restriction licenses shared positive context to imply universal substitution; N2 deliberately lacks that restriction. Replacing graph closure with complete-vector equality changes the merge rule, although both remain distributional-category learning.

### Clark–Eyraud–Habrard 2010: finite contextual features and learned composition

| Dimension | Published variable/procedure | N2 correspondence or obstruction |
|---|---|---|
| State | `D,K,F`, feature sets, CBFG productions | `K` corresponds to acquired fragments; paper `F` corresponds to N2 panel, **not** N2 `F`. |
| Input | Positive presentation, membership oracle | Reset trials can supply charged labels; externally complete positive presentation is extra access. |
| Update | `F_L(w)=C_L(w) intersect F`; productions from observed splits; inclusion-based parsing | N2 row equality is the symmetric special case of matching finite context features; N2 has no recursive parser. |
| Allocation | Enlarge basis/features after undergeneration or fiduciality violation | First-`J` panel never adopts an arbitrarily later distinguishing context after filling. |
| Reset | Accumulated examples/oracle; no physical reset | Block provenance and paid physical trials require an adapter. |
| Cost | Polynomial update in sample size; parsing `O(|F||P||w|³)` | Neither polynomial target-size learning nor physical query cost follows. |

See [complete CBFG learner, §§3–4][C]. **Finite feature sets are already part of this method**, not a distinction N2 can claim. Fiduciality is the additional condition connecting finite inclusions to all-context inclusions; N2's panel is not certified fiducial. Ordinary truncation can explain a weaker finite signature component. N2's complete status-bearing, block-aware query interface is not identical to Algorithm 1, but that interface difference is a candidate engineering/package contribution, not established new acquisition machinery.

### May 2026 continuation: apartness with incomplete teaching

| Dimension | Published variable/procedure | N2 correspondence or obstruction |
|---|---|---|
| State | Observation tree, cached don't-care states, apart basis, candidate matches, size bound | These are possible correspondents of retained trials and distinction witnesses, not substitution roles. |
| Input | `+/-/don't-care` membership; validity teacher | `UNTESTED` is not an oracle's don't-care answer. |
| Update | Tree expansion, witness elimination, SMT hypotheses | N2 performs signature grouping, without solver or hypothesis automaton. |
| Allocation | Promotion, extension, identification, validity rules | Query heuristics differ from N2's fixed oldest-cell scheduler. |
| Reset | No separately charged physical reset guarantee located | Retaining observations is not evidence of learned retention across erased memory. |
| Cost | Membership `O(kN 2^(kN log N))`; validity at most `2^((k-1+o(1))N log N)` | Query counts omit physical implementation costs. |

[The preprint's §§2–3][R] supplies this continuation. A queried don't-care is cached as uninformative for repetition; an N2 cell missing its required trials remains eligible for acquisition. Equating those statuses would alter the meaning of the data. On the wrong-context history below, a suffix witness establishes apartness while N2's fixed panel remains unchanged. This supports continuity of active distinction learning, not an N2 procedure-role theorem.

## Concrete contrasting histories

### H1: reachable wrong-context conjecture and a role that does not split

Take `A={a<b}`, `J=1`, `m=2`, `L=3`, adequate memory/computation, and a deterministic resettable world with `h(ab)=1` and `h(w)=0` for every other word. A finite machine retaining whether the current word is exactly a prefix of `ab` implements this world; no hidden-state access is given to the learner.

The N2 scheduler reaches the completed-trial history:

| Trial words in acquisition order | Endpoints | Environment calls |
|---|---|---:|
| `a,b,a,b,aa,aa` | `0,0,0,0,0,0` | `2+2+2+2+3+3 = 14` |

The panel is `[(empty,empty)]`; `a` and `b` have equal complete signature `(0)`. Query `(u=a,v=empty,f=a,g=b)` has source `aa`, replacement `ab`. It returns `TRANSFER_CONJECTURE(0)`. The true replacement endpoint is 1. Thus this valid finite evidence licenses N2's explicitly defeasible output, but cannot justify universal substitution. A second constant-zero world produces the same acquired history and would make that conjecture correct. No algorithm can distinguish these worlds from that history alone.

After actual `ab` trials, N2's direct query returns unequal effects. **Its role `a ~_P b` still holds:** the panel cells remain `h(a)=h(b)=0`. A failed non-panel substitution does not change the already full first-`J` panel. In particular, the specification must not be described as globally splitting a role after every counterexample.

For comparison, map membership to `K_1={ab}`. L* initially proposes a rejecting automaton and can receive counterexample `ab`; consistency then requires suffix `b`, because `T(b)=0` and `T(ab)=1`. It distinguishes the rows reached by `a` and `b`. This is a constructed application of [L*'s update][A], not a fair-cost superiority result: the counterexample teacher is additional access, and its physical replacement must be charged. Given the suffix observations themselves, the update difference remains even without crediting a free teacher. The recent apartness learner likewise has witness `b` once `ab` and `bb` are classified.

For CBFG, use the **ordered positive presentation prefix `(a,b,aa)`**, with oracle `K_0=A+ minus {ab}`. This is an analytical application of Algorithm 1, not a run. Write `c0=(empty,empty)`, `cL=(a,empty)` and `cR=(empty,a)`. Checking its updates in that order gives:

| New positive | Why the undergeneration branch executes | State after the update |
|---|---|---|
| `a` | Initial grammar generates nothing. | `D=K={a}`, paper feature set `F={c0}`; only the lexical production for `a`. |
| `b` | The previous grammar cannot generate `b`. | `D=K={a,b}`, `F={c0}`; two lexical productions and no binary production. |
| `aa` | The previous grammar has no binary production, so cannot generate `aa`. | `D=K={a,b,aa}`, `F=Con(D)={c0,cL,cR}`. |

The oracle then gives `F_(K_0)(a)=F_(K_0)(aa)={c0,cL,cR}`, while `F_(K_0)(b)={c0,cR}`: `aa` is positive but `ab` is negative. Thus the finite features distinguish `a` from `b`; N2 with `J=1` does not. With `alpha={c0,cL,cR}` and `beta={c0,cR}`, the third grammar has lexical rules `alpha -> a`, `beta -> b`, and the only binary rule `alpha -> alpha alpha`. This verifies the asserted operation contrast for the stated sequence; it is not an order-independent assertion from the set `D` alone. The derivation uses [CBFG Definition 11 and Algorithm 1][C]. Supplying its oracle labels costs extra trials unless they are already shared evidence. Increasing N2's `J` can erase this particular difference; it cannot establish that every fixed first-`J` panel implements CBFG's discrepancy-dependent growth. This is a schedule/coverage distinction, not proof of a new family.

### H2: a complete-panel requirement differs from SGL even on a valid target

Take `A={a}`, `J=2`, `m=2`, `L=3` and constant-zero endpoints. After N2 trials `a,a,aa,aa`, the first two distinct contexts are `(empty,empty)` and one of `(empty,a)/(a,empty)`; either ordering gives the same example. `a` has signature `(0,0)`. Fragment `aa` lacks the `aaa` effect and is unclassified. Query `(a,empty,a,aa)` therefore returns `UNRESOLVED` for replacing `aa` by `aaa`.

The natural positive sample for SGL is `{a,aa}`. Its substring graph places both words in the empty-context component and its split construction admits `aaa`. This is an original application of the audited rule; the target `a+` is substitutable, so no invalid-target assumption is needed to produce the contrast. One can make N2 match at this particular moment with `J=1`, but that is not an exact reduction across the frozen N2 family. Conversely, SGL's willingness to use one shared context does not make it a safe implementation of N2 with missing cells. The distinction is evidence policy, with a possible cost in delayed useful reuse.

### H3: partial overlap must not become transitive equality

This is a role-update illustration, not a claim about a particular scheduler prefix:

| Fragment | Context `c1` | Context `c2` |
|---|---|---|
| `f` | repeatable 0 | untested |
| `g` | repeatable 0 | repeatable 1 |
| `h` | untested | repeatable 1 |

N2 classifies only `g`; neither `f ~ g`, `g ~ h` nor their transitive conclusion is supported. SGL's graph closure is justified by its additional target-language assumption, not by treating absent cells as evidence. Nor may the recent learner's semantic don't-care answers be substituted for N2's pending measurements. Complete vector equality is transitive; overlap compatibility on different subsets is not.

## Historical follow-through and what still holds in 2026

| Lineage | Documented limitation or adoption evidence | 2026 assessment, explicitly an inference |
|---|---|---|
| L* | Angluin already identifies equivalence access and membership-query burden as practical concerns; the May 2026 preprint directly implements an active-learning continuation. [A][A], [R][R] | The family was not simply abandoned. Larger compute does not supply a physical equivalence oracle or free resets. Independent adoption of the new preprint is unknown. |
| SGL | The authors report excessive nonterminals, possible expensive reduction parsing, and overgeneration on realistic language data. [S][S] | More storage can postpone representation pressure; it cannot make arbitrary endpoint languages substitutable. Why a whole community set this aside is unknown; these are documented technical objections, not a sociological explanation. |
| CBFG | The authors motivate richer overlapping categories and acknowledge sparse contexts and possibly exponential kernels. [C][C] | Acquiring contexts can improve coverage, but neither faster hardware nor retaining all traces certifies a fixed panel as sufficient. Evidence of this exact learner's widespread adoption is unknown. |
| Recent continuation | Its implemented validity approximation can miss counterexamples. [R][R] | Modern tooling changes practical computation, while the teacher-versus-physical-evidence distinction remains. No reported benchmark performance is promoted to evidence of N2's funded objective. |

The oldest-priority question is not answered here. These papers suffice to establish the pre-existing families and components. Harris is discussed in the grammar papers, but his original 1954 article was not newly read; no first-invention or abandonment claim is attributed to it.

## Consequence for the funded objective

The correct object of a later test is whether acquired relations make **new, useful action compositions** available under matched history, interaction, computation and retained bytes. Remembering a literal table is not yet a retention advantage, and an endpoint match says nothing about intermediate behavior, costs or future continuations. N2 has neither a universal joint controller nor a learned procedure for choosing an adequate panel. Its words are acquired procedure syntax; its roles are learned relations over that syntax. They are not discovered physical objects or automatically reusable skills.

| Claim level | Supported conclusion |
|---|---|
| Existing family | Active observation-based distinction learning and distributional substring/context recombination are established. |
| Component identity | N2's complete-signature classifier is finite response-row equality; categorical endpoints do not remove the correspondence. Finite contextual features and learned composition rules were already explicit before N2. |
| Exact whole algorithm | No exact reduction to the complete L*, SGL, CBFG or recent separating-DFA learner is established. Their interfaces, update rules, allocation and outputs differ in the stated histories. |
| Merely a tuned special case? | Several differences are ordinary truncation, equality-versus-inclusion choice, repetition and provenance wrappers. A new label or fixed budget does not establish mechanism novelty. The complete published learners cannot be recovered by silently granting N2 their missing teachers or target assumptions. |
| Whole-package priority | Not established by four sources or by failure to find an exact same implementation. |
| Residual empirical proposition | Under explicit limits, an acquired finite substitution relation may improve useful recombination over matched literal retrieval and composition search. H1 shows why success is contingent; no result currently supports that improvement. |

The most informative residual comparison would expose whether a discrepancy-responsive context learner repairs an incorrect extension that N2 continues to license through its unchanged panel. That is a proposed later diagnostic question, not authorization to implement, tune or run it, and not a formal disposition of N2.

## Source gaps and PI-only paper channel

There is **no missing primary paper blocking the bounded conclusions above**. The successful Angluin institutional access means the already covered 1987 methods do not need to be requested again. The recent preprint abstract route and linked Zenodo artifact failed; full methods succeeded. Artifact reproduction and independent adoption remain unverified, not negative evidence.

No §5 `PAPER REQUEST` batch is raised: no inaccessible method is carrying a required claim. If a later priority claim depends on an unaudited source, it must first be mapped from full methods or requested from the PI in the governing format; this audit does not treat that open search as a proof of novelty. Every tool failure and negative retrieval used here is retained in `evidence/P3_SECOND_N2_TOOL_ERRORS_036.jsonl` for the PI's append-only error record.

## Post-draft source and history correction — 2026-09-10

The PI's source check identified incidental calendar parameters in the first institutional Angluin URL. Opening the **same document path without any query parameters** succeeded: the returned resource was `application/pdf`, 20 pages, with the paper's exact title, Dana Angluin as author, and *Information and Computation* 75, 87–106 (1987) on its first page. Its body contains §2.1 observation tables and §2.2/Figure 1, the complete L* update, as in the earlier newly accessed response. This verifies document identity and full-method access, not byte identity with the previously archived PDF. Citation `[A]` now uses the canonical paper DOI; `[AM]` gives the verified query-free institutional PDF. The effective route returned by the web tool is the same query-free path with `%28` normalized to `(`; the encoded link preserves that route without Markdown-parenthesis ambiguity. It is a PDF resource despite having no `.pdf` filename extension.

The CBFG portion of H1 previously abbreviated its positive input as a set. It now states the ordered prefix `(a,b,aa)`, shows all three undergeneration updates, and calculates the resulting feature sets and productions. The supported contrast is unchanged, but it is explicitly limited to that sequence and its additional oracle observations. No additional search, algorithm implementation or experiment was performed for these checks.

[A]: https://doi.org/10.1016/0890-5401(87)90052-6
[AM]: https://swt.informatik.uni-freiburg.de/teaching/WS2019-20/AutomataTheory/Learning%20Automata%20%28Caveat%20not%20related%20to%20Machine%20Learning
[S]: https://www.jmlr.org/papers/volume8/clark07a/clark07a.pdf
[C]: https://jmlr.org/papers/volume11/clark10a/clark10a.pdf
[R]: https://arxiv.org/html/2605.15294v1
