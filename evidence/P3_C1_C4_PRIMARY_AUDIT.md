# Phase 3 primary-method audit: C1 and C4

Date and source access date: **2026-09-06**. This is a PI-side research consultation in the shared workspace, not an independent reviewer verdict. No treatment experiment was run. The examples below are mathematical witnesses, not measured results. The approved specifications are left unchanged.

Audit target: `docs/P2_OPERATION_SPECIFICATIONS.md`, SHA-256 `d37a52eeb569461503b262d2790a656048624ede4790aeb49254e5a9f133c26f`, as incorporated in the approved `IDEAS.md`, SHA-256 `73cab9f6ab1f5eda80c7c2adc6d2ed556c63d5652fd65434e4cc4b24383dc3b8`.

## Findings and precise scope

**C1's complete live-state update, including declared relational resets, is an instance of finite-automaton subset construction.** Returning possible future output words reads the continuation language of that state. Neither keeping the model identity in the state nor evaluating the subset transition lazily supplies a different inference rule. Mitchell's version-space principle is a correct conceptual antecedent, but finite-state subset construction supplies the more exact dynamic mapping.

**C4's selected-scope optimization is a bounded Boolean instance of AQ's seed-star selection.** The literal published AQ15 classifier is not the complete C4 operation: its inconsistency handling and flexible classification differ from C4's explicit failure and abstention interface. The audit separates the exact selection reduction from these remaining interface differences. An exact published whole-method identity has not been established for C4. That is not affirmative evidence that its remaining wrapper is a new learning mechanism.

**C4 does not preserve every scope that present evidence leaves possible.** Its specified tie break can license a prediction on a point where another equally compatible scope would not. The shared programme proposition must therefore be audited separately; a consensus guarantee cannot be inferred from C4's name or from retaining its witnesses.

These are reviewable reduction certificates and counterexamples. They do not themselves enact a formal programme GO/KILL verdict or establish novelty of a combination.

## Primary-source methods actually inspected

The historical descriptions in this section are source reports. Subsequent equations, encodings and counterexamples are this audit's derivations from the approved specifications; they are not assertions that the older authors wrote the present encoding or operational vocabulary.

1. **Rabin and Scott, 1959, published research article**, *Finite Automata and Their Decision Problems*, IBM Journal of Research and Development 3(2), 114–125. Chapter II, §5, Definitions 9–11 and Theorem 11 with its proof were read in full. The nondeterministic machine permits a set of initial states and set-valued transitions. Its deterministic construction takes subsets as states and unions the successor sets for a symbol. This is the primary mathematical antecedent used below. [Author-paper archive copy](https://github.com/CMU-HoTT/scott/blob/main/pdfs/1959-Rabin-Scott-finite-automata.pdf); [direct PDF](https://raw.githubusercontent.com/CMU-HoTT/scott/main/pdfs/1959-Rabin-Scott-finite-automata.pdf). Accessed 2026-09-06. Local PDF SHA-256 `95e5e12c4206f598103557d311b41931750254924655d5fd7ecd22113a5d5de3`.

2. **Mitchell, 1977, published IJCAI paper**, *Version Spaces: A Candidate Elimination Approach to Rule Learning*, pp.305–310. All six pages were read. The method retains rules consistent with all positive and negative training instances, using general and specific boundaries. It separates that deduction from selecting a best hypothesis. Its limitations section identifies inconsistent evidence and large boundary sets; a collapsed version space signals that the supplied language and classifications admit no rule. It also discusses choosing informative instances and merging separately learned spaces. [Primary proceedings PDF](https://www.ijcai.org/Proceedings/77-1/Papers/048.pdf). Accessed 2026-09-06. Local PDF SHA-256 `726c620d1001371ea735a5a8d782af1673e5a9c917cbfa0552596ff513dbba39`.

3. **Kaelbling, Littman and Cassandra, 1998, published research article**, *Planning and Acting in Partially Observable Stochastic Domains*. Sections 3.1–3.4 were inspected for the model, belief state and state-estimation equations. A supplied transition/observation model updates a probability distribution from the last action and observation; the correctly updated belief summarizes the relevant history. This supplies a probabilistic cross-check, not the primary exact reduction for arbitrary C1 reset relations. [Author-hosted PDF](https://people.csail.mit.edu/lpk/papers/aij98-pomdp.pdf). Accessed 2026-09-06. Local PDF SHA-256 `71a6d1aee278e93c5fae8dd7d0c452c8b7b035af55d9dce2bc367d473bfc9645`.

4. **Michalski, Mozetič, Hong and Lavrač, July 1986, technical report**, *The AQ15 Inductive Learning System: An Overview and Experiments*, ISG 86-20 / UIUCDCS-R-86-1260. Methods §§2–4 were read completely after OCR; printed p.3 was visually checked. AQ generates maximally general complexes containing a positive seed and excluding negatives, then selects by user preference. A stated preference maximizes positive coverage, then minimizes selectors. `maxstar` truncates large intermediate stars; full-memory incremental learning retains prior examples and rules. The report also specifies ways to reassign/remove inconsistent examples and flexible decisions for multiple or absent matches. [Primary author-hosted report](https://www.mli.gmu.edu/papers/86-90/86-23.pdf). Accessed 2026-09-06. Local PDF SHA-256 `6afbe29e075cd9dea5591f2dffafeb83a72ae00c568c9e3a506c31d3f371dd0c`. This is a technical report, not a claimed peer-reviewed journal article.

5. **The same authors, 1986, published AAAI paper**, *The Multi-Purpose Incremental Learning System AQ15 and Its Testing Application to Three Medical Domains*, pp.1041–1045. All five pages were read. It corroborates the representation, full-memory mode and the distinction between strict matching and flexible classification. Its latter decision procedures should not be silently substituted for C4's abstention rules. [Author-hosted proceedings copy](https://kt.ijs.si/personal-pages/igor_mozetic/papers/Michetal-AQ15-AAAI-86.pdf). Accessed 2026-09-06. Local PDF SHA-256 `e107aaa12716e4a50ca810c90f5da4a2c44c5689921e67d1dd6bc74457c5c0b2`.

No cited source here is an unreviewed arXiv preprint. The 1986 report is explicitly identified by publication type. Full methods needed for these certificates were accessible; no human paper request is required for the claims made here.

## C1: exact reduction certificate

### Encoding and proof

Let the finite state universe be the disjoint union

\[
U=\{(h,q):h\in H_0,\ q\in Q_h\}.
\]

Use the alphabet \(\Sigma=(A\times O)\cup\{\rho\}\), where \(\rho\) is an explicitly declared world-reset event. Define a nondeterministic transition function:

\[
\Delta((h,q),(a,o))=
\begin{cases}
\{(h,T_h(q,a))\}, & O_h(q,a)=o,\\
\varnothing, &\text{otherwise},
\end{cases}
\]

\[
\Delta((h,q),\rho)=\{(h,q'):q'\in R_h(q)\}.
\]

The initial subset is \(S_0=\bigcup_h\{h\}\times I_h\). Apply the subset transition

\[
\widehat\Delta(S,z)=\bigcup_{s\in S}\Delta(s,z).
\]

This is exactly C1's specified update, not merely a matching input-output example. For an ordinary event, the union performs prediction checking, removal, transition and deduplication. For a reset, it takes the declared relational image while preserving the model tag. In particular \(\widehat\Delta(\varnothing,z)=\varnothing\) for every symbol: the absorbing inconsistent state needs no revival rule.

Inductively, after every observed history, the subset contains precisely the model/current-state pairs reachable by a path consistent with that history. Initialization supplies the base case. Each admitted next event extends exactly the compatible paths; the reset case uses the same relational extension. Histories reaching the same pair can be merged because all later emissions and transitions depend only on that pair. This justifies omitting the raw trace for this fixed finite model family. It does not justify omitting an undeclared sensor variable from a real world model.

For a proposed action word \(u=(a_1,\ldots,a_L)\), let

\[
\mathcal O(S,u)=\{(o_1,\ldots,o_L):
\widehat\Delta^{*}(S,((a_1,o_1),\ldots,(a_L,o_L)))\ne\varnothing\}.
\]

Because each component transducer is deterministic between declared resets, this is exactly the set C1 obtains by simulating the word from every live pair. Choosing every state as accepting turns it into a continuation-language query on the encoded automaton. A singleton licenses only the model-relative agreed output; an empty subset is an error/unsupported case, not universal agreement by vacuous truth.

### Complete variable and resource mapping

| Approved C1 object | Comparator object under the encoding | Consequence |
|---|---|---|
| Immutable programs, alphabets and initial states | Fixed transition structure, alphabet and initial subset | Supplied model construction remains external and charged. |
| Live `(h,q)` pairs | Current subset of the disjoint state universe | Model uncertainty and within-model state uncertainty are both ordinary state coordinates. |
| Actual action and observation | One observed alphabet symbol `(a,o)` | No unobserved outcome or evaluator label is introduced. |
| Prediction test, advance and deduplication | Union of successor sets | Identical state after every possible history under the supplied structures. |
| Empty-set flag and `unresolved` | Empty subset plus an explicit reporting convention | The null state is already absorbing; naming it adds no inference. |
| Allowed post-reset states | Transition relation for `rho` | Includes branching or empty reset images without a stochastic-normalization assumption. |
| Episode/context clearing | No transition of persistent automaton state | Persistence is a storage contract, not relearning. |
| Future possible output words | Continuation language with fixed action coordinates | Output enumeration is separately charged; no commitment policy is supplied. |
| Persistent allocation | Program definitions plus current subset | No dynamic hypothesis invention, hidden raw history or extra labels. |

Let \(M=|U|\) and \(K=|S|\). The online union can be evaluated only for the current subset; there is no need to allocate all \(2^M\) possible subset states. Using the same executable transitions gives the same \(O(Kc)\) ordinary update and \(O(KLc)\) direct query costs, plus deduplication and returned-output storage, as C1. A reset costs the actual number of enumerated successor entries plus deduplication; it need not have the ordinary deterministic update bound. A dense \(M\)-bit representation or sparse state-ID set are implementation choices with their actual costs. No asymptotic saving over the matched online construction is established by calling C1 a memory method.

### Distinguishing histories, and what they do not distinguish

Consider two supplied models with states \(q_0,q_1,q_2\). In both, action `a` at \(q_0\) emits `0` and advances to \(q_1\). At \(q_1\), action `b` emits `0` in model \(h_0\), `1` in model \(h_1\), and advances to \(q_2\). Supply harmless self-loop defaults elsewhere. Initially both models are possible.

After `(a,0)`, C1 returns `{0,1}` for the next `b`. After `(b,1)`, only \((h_1,q_2)\) survives. An explicit reset sending every remaining state to its model's \(q_1\) leaves only \((h_1,q_1)\); it does not restore \(h_0\). An impossible observation `2`, included in the observation alphabet but emitted by neither model, empties the subset. Any subsequent reset leaves it empty.

The encoded subset observer behaves identically at every stage. A point estimator can differ before `(b,1)`; an incorrect reset implementation can differ afterward. Those are contrasts against weakened or defective comparators, not against the matched antecedent. **There is no distinguishing history within C1's specified domain under the map above.** Adding stochastic corruption, new programs or unknown reset dynamics changes that domain and would require a newly specified variant.

### Probabilistic and version-space cross-checks

For positive initial weights, define the joint kernel
\(J((h,q'),o\mid(h,q),a)=\mathbf1[q'=T_h(q,a)]\mathbf1[o=O_h(q,a)]\).
The support of its unnormalized Bayesian update is the same nonempty subset. The cited POMDP paper writes its observation model conditional on the successor state; if that convention is used literally, augment a state with the emitted observation, rather than pretending C1's pre-transition output is already successor-state-only. Probabilities are irrelevant to C1's set query, but not to C2's expected-loss decisions. C1's empty case also must not be handled by normalizing zero mass. These are reasons to prefer the direct relational reduction above.

Mitchell's rules classify static instances; C1's hypotheses carry evolving states. Encoding an entire initial transducer run as a fixed trace-consistency hypothesis reproduces the candidate-elimination principle, but the dynamic subset map additionally explains the sufficient current state and reset behavior. Thus the audit does not equate C1 to an unmodified static boundary-maintenance implementation or infer equal computational cost from a conceptual resemblance.

## C4: exact scope-selection reduction and limits

### From scope refinement to a finite seed-star problem

For a fixed admitted evidence partition, write the seed as \(s\). For each Boolean atom \(A_i\), define its seed-compatible literal

\[
\ell_i(x)=\mathbf1[A_i(x)=A_i(s)].
\]

Every candidate scope is uniquely an index subset \(J\subseteq\{1,\ldots,m\}\), with \(|J|\le k\), interpreted as \(C_J(x)=\bigwedge_{i\in J}\ell_i(x)\). The empty conjunction is true. For each negative witness define

\[
D_n=\{i:A_i(n)\ne A_i(s)\}.
\]

Then the complete C4 optimization is

\[
\mathcal F_k=\{J:|J|\le k,\quad J\cap D_n\ne\varnothing\text{ for every }n\in N\},
\]

\[
J^*=\arg\min_{J\in\mathcal F_k}
\left(-\sum_{p\in P}\mathbf1[C_J(p)],\ |J|,\ \operatorname{lex}(J)\right).
\]

This transformation is lossless: satisfying the seed is built into every literal; rejecting a negative means selecting at least one literal on which it differs from the seed. The optimization chooses a seed-containing, negative-excluding complex by positive coverage, then size and identifier order.

For Boolean independent coordinates, an untruncated AQ star contains the inclusion-minimal hitting sets of the negative difference sets, expressed as maximally general complexes. C4 enumerates more conjunctions, but its optimum never needs a redundant literal: if deleting a literal preserves rejection of every negative, positive coverage cannot decrease and length improves. Repeated deletion reaches a minimal hitting set of no greater length. Consequently optimizing over the star elements with \(|J|\le k\) gives **exactly the same selected scope** as C4; use the same final lexicographic tie break.

The independent Boolean-coordinate construction deliberately treats the observed signature vector as the AQ attribute vector. If upstream relational atoms are logically dependent over real descriptors, the comparator is still the Boolean-vector instance with the same observed vectors and queries; it is not granted extra domain implications for free. Syntactically different but extensionally equivalent scopes retain C4's fixed ordering. Neither method discovers the atoms or \(F\) in this map.

The length restriction is part of this mapped problem, not a claim that `maxstar` means maximum conjunction length: **it does not**. `maxstar` is a bound on retained alternatives during search. To claim exactness, no intermediate star may be truncated. The hard \(k\) restriction and empty-feasible-set report must be imposed explicitly; the historical source is not evidence that a particular AQ15 executable exposed that exact configuration flag.

### State, inputs, updates and remaining interfaces

| Approved C4 object | Mapping or difference | Exactness status |
|---|---|---|
| Proposed \(F,a,t\) and fixed seed | A separately indexed binary concept instance with fixed positive seed | Exact input re-expression. Constructing \(F\) is still external. |
| Total Boolean atom library | Boolean-valued AQ attributes; seed determines selector polarity | Exact within the supplied feature representation. |
| `y=F(x)` / contradictory `y` | Positive / negative class of admitted evidence | Exact. This is observed relation agreement, not reward. |
| All retained witnesses | Full evidence store reused for each reconstruction | Same allowed memory channel; AQ15's full-memory mode is an antecedent, not evidence for zero cost. |
| Exhaustive bounded conjunction search | Untruncated seed-star generation, length restriction and matched preference | Same selected scope whenever feasible, by the proof above. Search traces and resource constants need not match. |
| Fixed seed through later updates | Rerun the mapped one-complex problem on the accumulated evidence with the same seed | Exact operational construction; not AQ's full repeated-seed cover-building loop. |
| Inconsistent signature / insufficient length | Explicit feasibility certificates below | C4 reporting distinction, not established as the published AQ15 whole-program interface. |
| Conflicting applicable rules | C4 returns unresolved | Different from the inspected AQ15 flexible classifier. |
| Unknown later precondition | C4 does not license composition | Explicit downstream proof obligation, not supplied by a positive-coverage score. |
| Persistence across context clearing | Store definitions, selected scope and evidence | Same representation suffices, but no reset discovers a changed world or makes old evidence current. |

Provenance partitioning is a declared routing function before the binary learning problem. It can stop two types of encounter entering one instance; it cannot identify an incorrect provenance tag. An absent outcome adds neither a positive nor a negative example. This is **three-way admission/use semantics around a two-valued learning core**, not an unspecified many-valued atom learner. Atoms on admitted descriptors are expressly total. At composition time a needed descriptor or condition may be unestablished; that does not permit silently filling it with a Boolean value.

### Exact infeasibility diagnosis

The two C4 failure types follow directly from the difference-set construction:

- If some \(D_n=\varnothing\), the seed and that negative have identical full signatures. Every expression built solely from these total tests gives the same value on the pair. No conjunction can separate them; indeed, allowing arbitrary Boolean combinations of the same tests cannot separate that pair either. This supports a representation-relative aliasing certificate, not the claim that the physical world supplies no distinguishing observation.
- Otherwise every \(D_n\ne\varnothing\), and \(J=\{1,\ldots,m\}\) hits them all. If \(\mathcal F_k=\varnothing\), separation exists in the full seed conjunction but needs more than the allowed number of literals. A new atom is not logically required merely by that failure.

For a concrete length-bound witness, let the seed signature be `(1,1)`, negatives `(0,1)` and `(1,0)`, and \(k=1\). Each pair is separable, but the negative difference sets are `{1}` and `{2}`: no singleton hits both. At \(k=2\), their conjunction works. In a separate aliasing case, a negative with signature `(1,1)` has an empty difference set, and increasing \(k\) cannot help. These are deduction certificates, not experiments.

The complete set of stored witnesses is sufficient to recompute both diagnoses. If positives or negatives are evicted, if corrupted labels are reclassified, or if the library grows, the object being audited has changed. The inspected AQ15 report offers ways to reassign or remove inconsistent examples; it therefore does not prove the identity of its full inconsistency behavior with C4. That difference is substantive for a proposed uncertainty guarantee, even though naming these two elementary feasibility cases does not by itself establish a new scope-learning principle.

### Two histories that prevent overclaiming

**C4 differs from all-positive candidate elimination.** With atoms `A,B`, seed `(1,1)`, an additional positive `(1,0)`, negative `(0,1)` and \(k=1\), C4 returns scope `A`. More generally, if no scope covers all positives but one covers the seed and some positives without covering negatives, C4 can still return it. For example add positive `(0,0)` to that same evidence: `A` still wins, but no single conjunction covering all three positives can exclude `(0,1)`. Mitchell's all-positive/all-negative version space is empty for the latter concept class. This distinguishes the specifications but does not distinguish C4 from the mapped one-complex AQ task, which is explicitly a partial-cover step.

**C4 also differs from a consensus scope rule.** Let \(P=\{(1,1)\}\), \(N=\{(0,0)\}\), \(k=1\), and order `A` before `B`. Both `A` and `B` cover the seed and reject the negative, with equal positive coverage and length. C4 selects `A` and licenses \(F\) at a fresh `(1,0)` point. The equally compatible scope `B` does not license that point. A real relation whose valid scope is `B` is consistent with the entire admitted record. Retaining the negative witness has therefore not established C4's selected scope as uniquely warranted.

This second witness was independently raised by the root PI during the shared-workspace consultation and checked here. It is not an isolated-review finding. It directly constrains the programme through-line: adding a requirement that C1 vet each C4 application against every compatible scope would require an explicit coupling and common hypothesis interpretation. The approved operations do not already specify that coupling. The audit should not invent it silently and then credit its guarantee to the approved C4.

### Resource comparison and search differences

Write \(B(m,k)=\sum_{j=0}^{\min(k,m)}\binom mj\). Direct enumeration evaluates this many candidate index sets. With cached atom signatures, a straightforward scalar implementation does \(O(B(m,k)N_w k)\) Boolean work, plus \(O(mN_w)\) atom evaluations/cache preparation and atom-evaluation cost. Word-packed masks can change those implementation bounds; they must be matched and counted. The approved specification states candidate/witness enumeration without claiming a measured runtime. Both it and a full-memory comparator retain witness descriptors. No old-label-free or bounded-memory result follows.

AQ's star construction need not enumerate the same search sequence or use the same peak working memory. A finite `maxstar` may discard a future-best complex; a comparison against that setting could show an exhaustive-search benefit. It would not establish a different scope objective. Conversely, granting C4 exhaustive search and comparing it to a cheaply truncated star without matched resources would conflate the operation with search allocation. A useful comparison must distinguish objective identity from compute, pruning and admission differences.

## What old limitations remain in 2026?

These sources do not establish that either lineage was universally abandoned. No historical claim about fashion is inferred from their age. They do establish methods and explicit computational/consistency restrictions that preceded these proposals.

The audit's present assessment is that more compute can move the feasible boundary for explicit subsets and untruncated stars. It cannot remove worst-case growth in the supplied state/language or make an absent true hypothesis representable. Nor does it turn contradictory labels into a reliable observation process. C1 still refuses noise it did not model. C4 still depends on externally provided tests and \(F\), and may choose an accidental training-compatible scope. These limitations follow from the approved rules and counterexamples, irrespective of hardware. A renewed empirical investigation could be worthwhile as a test of those tradeoffs; it would not, by itself, be a new inference operation.

## Items for the independent audit packet

1. Check the C1 encoding, particularly pre-transition emission, relational reset, persistent model tag and empty-set behavior. The proposed exact-reduction finding applies to the whole specified state/query operation, with its reporting convention.
2. Check the C4 dominance proof and the limits of the mapped AQ instance. Do not equate `maxstar` and \(k\), an AQ partial-cover step and its full classifier, or soft positive coverage and all-positive consistency.
3. Keep the C4 consensus counterexample in the separate through-line audit. An operation can abstain on one class of failure while still commit prematurely on another.
4. If the remaining C4 diagnostic/abstention wrapper is advanced as the actual novel proposition, specify that claim and audit its antecedents directly. The lack of a literal whole-AQ15 identity does not clear that claim. No novelty claim for rough-set, logical-abduction or three-valued planning interfaces is decided by this bounded audit.

No benchmark or treatment implementation is required to decide these algebraic mappings. Formal verdict issuance remains subject to the programme's independent-review boundary.

## Retrieval and process record

Full PDFs and local extraction/OCR intermediates are under `private_sources/P3_C1_C4/` and are not proposed for public repository redistribution. The report filename `aq15manual1986.pdf` is a local retrieval label; the actual title is the overview/experiments technical report identified above, not the separate AQ15 user's guide.

The web renderer reported `Failed to fetch https://www.mli.gmu.edu/papers/86-90/86-23.pdf: (400) Timeout fetching` for its first screenshot request, and `Failed to fetch https://raw.githubusercontent.com/CMU-HoTT/scott/main/pdfs/1959-Rabin-Scott-finite-automata.pdf: DisabledError` for its raw-PDF open request. Ordinary public HTTP downloads succeeded, and local extraction/visual inspection supplied the relevant methods; no access control was bypassed.

A premature text search while the OCR job was still running returned exit code 2 with the exact message `rg: private_sources/P3_C1_C4/aq15manual1986_ocr.txt: IO error for operation on private_sources/P3_C1_C4/aq15manual1986_ocr.txt: No such file or directory (os error 2)`. The OCR later completed for all 36 PDF pages and the search/read succeeded. This was a local sequencing error, not an absent source or a scientific result.
