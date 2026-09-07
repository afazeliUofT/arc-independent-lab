# Primary-method audit of the learner-access observer

2026-09-07. Research consultation within the PI process; the authoring agent shared the lab's tools and filesystem. This is not an independent reviewer verdict, a new candidate, or an efficacy trial. Frozen observer code, protocol and evidence are unchanged. External links below were accessed on **2026-09-07**. The audit compares what each procedure actually receives and computes, rather than treating all uses of projection as equivalent.

**The successful API reader is exactly a partial-regression coefficient computation under a supplied linear decomposition contract.** Its local scientific value survives that reduction: the learner's current state and callable model contain enough information to recover an old estimate that the ordinary readout fails to produce. What is unsupported is novelty of that computation, autonomous discovery of the contract, or the prevalence of this access failure across current AI.

## 1. Audited object and evidential boundary

The frozen function `recover_from_current_map(theta, old_query, subsequent_feature, tolerance)` receives current weights θ, an old unit-query feature a, and the later context's unit-feature b. The latter two are obtained by unlabeled calls to the learner's existing `FeatureAPI`, not by querying an evaluator for geometry or old answers. The known contract is zero initialization, fixed linear features, A-only updates followed by B-only updates, and identification of the old and subsequent contexts. This yields θ = a k + b d, where k is the old boundary coefficient and d accumulates later updates. The target is the old boundary prediction k aᵀa, not necessarily the true old label.

Its experience-dependent state remains θ. The fixed feature map, supplied schedule semantics and program are additional **structure**, not absent information. Accordingly, “current weights plus own model under the declared contract” is accurate; “weights alone, with no prior knowledge” is not. The separate learned-span reader uses historical update-derived bases and must retain its distinct state allowance.

| Frozen input | SHA-256 |
|---|---|
| `reports/P2_LEARNER_OBSERVER_001.md` | `5503b185549fcce4daa841a9f4445f53d4f94dc3a43a73440bf877b2d38d1f11` |
| `docs/followups/P2_LEARNER_OBSERVER_PROTOCOL.md` | `24c9e92f528a6cdc5e97a657fa7c8d0db3b4428434eb1d9cef4054d0d3b43bee` |
| `scripts/run_learner_observer.py` | `81682d063317df6f1fd0f0edfd5e86164b86416aac0b83f61aaa11f8f4ba191d` |
| `evidence/P2_OBSERVER_INTERPRETATION.md` | `718e010250f31501e17692845d708d70933c6d2c0f369ded6c2b29de408fb982` |

The completed numerical evidence remains in `artifacts/P2_LEARNER_OBSERVER/20260906_001/results.json`, SHA-256 `9c6c95c115e9d350e26c43707092c65208020eac9b02b91d389d335fa3febd08`. This audit adds no observations and makes no statistical inference from repeated readouts. Local source access: 2026-09-07. Public source anchor: [frozen observer at checkpoint 007](https://github.com/afazeliUofT/arc-independent-lab/blob/7da5cc4ce22fac3163408a4889517c86d386f407/scripts/run_learner_observer.py).

## 2. Exact partial-regression mapping

The original methods source obtained is Michael C. Lovell's **1963 Cowles Discussion Paper 151, a working paper/preprint**, *Seasonal Adjustment of Economic Time Series and Multiple Regression*. Its §5, Theorem 5.1 and appendix prove equality of relevant least-squares coefficients when nuisance columns are included explicitly or removed by least-squares projection. The version read is not silently identified with the final JASA typesetting or theorem numbering. The complete method and proof are in printed pp. 26–30 and 43–45; key formulas were checked against page images. [Primary working paper](https://cowles.yale.edu/sites/default/files/2022-08/d0151.pdf).

The following mapping and proof are the PI team's algebra applied to the frozen program. Put M_b = I − b(bᵀb)⁻¹bᵀ, for b ≠ 0. Consider the ordinary least-squares problem

\[
\min_{k,d}\|\theta-a k-b d\|^2.
\]

This regression's response entries are **coordinates of current θ**, not old training labels. The design columns a and b come from the callable feature map. Eliminating d from its normal equation gives

\[
\widehat k=(a^\top M_b a)^{-1}a^\top M_b\theta.
\]

The code constructs p = M_b a, sets `coefficient = dot(p,theta)/dot(p,a)`, and returns `coefficient * dot(a,a)`. Since M_b is symmetric and idempotent, this is precisely the partial-regression coefficient followed by conversion to the old query's prediction. It also equals the first coefficient of the joint least-squares fit to [a b]. No fitted old-label probe is inserted by this mapping.

| Operation aspect | Frozen API reader | Matched partial-regression computation |
|---|---|---|
| Persistent experience | Current θ | Same θ used as response vector |
| Supplied inputs | Unlabeled a, b from current fixed model | Regressor a and nuisance regressor b |
| Update | Does not alter the original learner | Same; evaluate regression only when queried |
| Allocation | Inner products and one residual vector | Same rank-one residualization; dense projector is unnecessary |
| Output | k̂ aᵀa | First coefficient multiplied by aᵀa |
| Reset | Works if θ and the callable fixed model/contract survive | Identical condition; discard transient fit after query |
| Singularity | Abstains at specified denominator tolerance | Use the same rank/tolerance guard; no arbitrary coefficient chosen |

Lovell's theorem explicitly assumes more rows than total independent columns. The two-coordinate observer has two columns, so a literal application to that printed hypothesis can append one **known zero coordinate** to θ, a and b. All inner products, ranks and outputs remain unchanged, and the strict row inequality holds. This adds no evidence or unknown parameter. The normal-equation derivation above itself needs only full column rank. No variance or degrees-of-freedom inference is being imported into the deterministic witness.

For every admissible noncollinear history, θ = a k + b d implies M_b θ = M_b a k. Thus the mapped computation and frozen reader return the same old boundary prediction throughout B. There is no distinguishing history within that contract. Under the same tolerance they also make the same rank-based abstentions. On arbitrary inputs, the formulas remain equal even when their interpretation as an old boundary estimate is false.

That last qualification matters. A contract violation may add an unmodeled component c to θ. The function can still return a number when aᵀM_b a is nonzero; it does not establish that initialization was zero, that the schedule was A-then-B, or that c was absent. A full-rank design in the original two-dimensional space can explain every θ, so a small algebraic fit residual cannot certify the training-history contract.

**Cost mapping, derived from the code:** for d-dimensional feature vectors, each rank-one readout uses O(d) arithmetic and O(d) transient vector storage, plus two encoder calls in the runner. It need not allocate an O(d²) projector. No extra experience-dependent persistent state is needed when the map can be called again. These are algorithmic counts, not a measured new runtime claim. Near collinearity, aᵀM_b a = ‖a‖² sin²(angle(a,b)); exact uniqueness therefore does not imply numerical robustness under arbitrary perturbations.

## 3. Estimability is a prior method for deciding which query can be answered

Russell V. Lenth's **2015** *Estimability Tools for Package Developers* gives an implemented method: obtain a null-space basis from the model matrix's QR decomposition, test each requested linear functional for orthogonality to that null space, and mark non-estimable predictions as unavailable. The entire five-page paper was read, including the construction and tolerance rule on printed p. 198. This is a published software-method paper, not a preprint. [Primary R Journal paper](https://journal.r-project.org/articles/RJ-2015-016/RJ-2015-016.pdf).

Applied to the observer's own supplied decomposition, the unknown coefficient vector is z = (k,d), the visible state is θ = [a b]z, and the query row is C = (aᵀa,0). For unrestricted real-valued coefficients, the answer is identifiable exactly when every n in ker([a b]) satisfies Cn = 0. This is the same query-specific estimability condition; determining every coefficient is stronger than determining one query. The old prediction here is non-estimable for nonzero collinear a and b over that unrestricted class. The frozen function's abstention has a classical counterpart.

The criterion is conditional on the supplied design and admissible coefficient domain. A null-space vector alone is not an impossibility proof for a restricted finite gain codebook or a restricted set of realizable training histories. Both colliding possibilities must actually be allowed. The frozen protocol correctly treats its erased-geometry collision separately: it removes the B feature API and admits a broader map family. That proof does not deny the positive result under the original full interface.

An automated null-space check can certify a consequence **of** a supplied contract. It does not autonomously learn which contract describes a learner's past. This distinction prevents the next proposed research question from being declared solved merely because classical estimability code can emit an abstention.

## 4. Subspace continual learning changes a different causal operation

Farajtabar, Azizan, Mott and Li's **AISTATS 2020** Orthogonal Gradient Descent (OGD) constructs and stores a basis of old model-output gradients at a task boundary, then projects new loss gradients away from that basis. Its §3 and Algorithm 1 were read in full. The nonlinear argument explicitly uses a local approximation to old gradients; retained bases are historical state. [Published primary paper](https://proceedings.mlr.press/v108/farajtabar20a/farajtabar20a.pdf).

For the frozen scalar linear predictor, the old output gradient is a. An exact linear specialization of OGD would change a proposed B update δb to δM_a b, preserving the ordinary old prediction aᵀθ. The observer instead lets the original δb occur and changes only its later query computation. With aᵀb ≠ 0 and δ ≠ 0, the subsequent parameter states differ immediately. This is a concrete distinguishing history, not a terminological distinction.

The learned-span reader's Gram–Schmidt basis retention resembles the geometric data structure, but retains actual update directions and solves a posthoc decomposition. It does not enforce OGD's projected learning trajectory. Even if both bases happen to identify the same one-dimensional old span in this toy model, the input streams, use of state and interventions are different. Consequently OGD is a necessary comparator for claims about subspace memory, but is not an exact reduction of the frozen API observer.

Derived cost comparison: retaining a rank-r basis in d parameter coordinates takes O(dr) scalar storage and a dense projection O(dr) arithmetic per new update, in addition to basis-construction/model-gradient costs. Unlike the current-map API condition, these bases must survive the boundary. These generic counts are not claims about the paper's measured memory or speed.

## 5. Recovery and probing antecedents do not provide the same information

Zheng et al.'s **ICLR 2025** *Spurious Forgetting in Continual Learning of Language Models* was inspected at §3.2, §5.1, Appendix D.2, E, H and I.1. The biography recovery fine-tunes on one half of old-task QA data and evaluates the other half. Its task-vector comparison additionally uses saved checkpoints to subtract scaled trajectory differences. The safety recovery uses responses generated by a model from before the intervening fine-tuning. These are three distinct recovery information channels. [Published primary paper](https://proceedings.iclr.cc/paper_files/paper/2025/file/a774503daed55eb53c634847ae071ec7-Paper-Conference.pdf).

None is the observer's own-feature-API computation. Old supervised QA, pre-boundary teacher outputs, and checkpoint differences are unavailable in that access condition. At the same time, the paper studies richer models with different assumptions; the observer's stricter history access does not make it a generally superior recovery method. A history in which historical supervision or checkpoints have been discarded still permits the frozen API reader under its contract, whereas the cited instantiated recovery procedures cannot be executed as written. Conversely their experimental regimes do not supply the observer's exact fixed rank-one decomposition contract.

Davari et al.'s *Probing Representation Forgetting in Supervised and Unsupervised Continual Learning* explicitly fits a linear classifier to frozen activations using original-task training inputs **and labels** (§3.1), then compares held-out performance across checkpoints. Its fast-remembering discussion (§3.4) uses exemplars. The version examined here is **arXiv v2, a preprint dated 2022-04-05**, whose metadata says accepted at CVPR 2022; the inaccessible final CVF copy is not represented as read. [Primary author preprint](https://arxiv.org/pdf/2203.13381v2).

This is a direct antecedent for interpreting a gap between an ordinary head and a newly available readout. Its supervised fitting channel makes it a different access experiment. The observer's labels enter initial training, as they must, but no old labels enter recovery. For a matched comparison, old-label refitting would require a separate declared arm with its data, retained state and optimization costs charged. Neither a successful probe nor a successful analytic readout demonstrates that the original learner notices the need, selects a decoder or invokes it at the correct time.

## 6. Historical relevance and the remaining scientific question

No evidence here supports saying that residualization or estimability was abandoned. Lovell's own working paper discusses computational expense and explicitly ties economy to available technology (printed pp. 24–25); Lenth's implemented prediction check demonstrates continued use. The relevant expired constraint would be the cost of a particular numerical implementation, not the logical requirement that the nuisance structure be known. Modern compute can make much larger decompositions feasible; it cannot identify an old answer from two genuinely indistinguishable admissible states. [Lovell working paper](https://cowles.yale.edu/sites/default/files/2022-08/d0151.pdf); [Lenth method](https://journal.r-project.org/articles/RJ-2015-016/RJ-2015-016.pdf).

The observer therefore supports a sharply scoped diagnostic result: under its original full model interface, ordinary-output failure is not sufficient evidence of loss of the old estimate. The recovery calculation itself reduces to an established linear method. A stronger programme claim would have to concern discovering or maintaining the information needed to justify recovery, choosing the relevant query and invoking it under a finite resource allowance, or measuring this failure mode in a meaningful wider system. Those are open questions here, not certified gaps in the entire literature. This audit neither substitutes a new candidate for C3 nor transfers the observer's success to C3's stored-anchor operation.

## 7. Source access and reproducibility record

All source access below: **2026-09-07**. Downloaded primary documents and extraction/OCR are private working material; the public audit contains short method summaries and the lab's mappings. The historical priority question is not made dependent on inaccessible originals.

| Primary source actually obtained | Private PDF SHA-256 | Method coverage |
|---|---|---|
| [Lovell 1963 Cowles working paper/preprint](https://cowles.yale.edu/sites/default/files/2022-08/d0151.pdf) | `77ca6a277eb55ac3c9c4329492a6d3c71e644ff503b33de51ae79ea031508313` | §5 theorem, regression variants and appendix proof; key page images checked |
| [Lenth 2015](https://journal.r-project.org/articles/RJ-2015-016/RJ-2015-016.pdf) | `65983cd639bffadb3c0700d2c8314d01f2ffaf31e22bb482ac2255ebb5e5a9a5` | Complete paper, QR/null-basis procedure and query test |
| [Farajtabar et al. 2020](https://proceedings.mlr.press/v108/farajtabar20a/farajtabar20a.pdf) | `d148f051634d1839ff77635b3be79422f03e4a68325ce75b65f57d89fc6b18d5` | Complete §3 and Algorithm 1, assumptions and historical state |
| [Zheng et al. 2025](https://proceedings.iclr.cc/paper_files/paper/2025/file/a774503daed55eb53c634847ae071ec7-Paper-Conference.pdf) | `6ee0e363a851db324b6ca1dfb6e6c7937b7a6f7019ff75a8092de569ba62834f` | Recovery methods listed in §5 above; no claim all appendix experiments re-audited |
| [Davari et al. 2022 author preprint v2](https://arxiv.org/pdf/2203.13381v2) | `498e39ae54157e6fe7843325c5b3a034b1c2fb1b27cc5fca6df53a2211cfee3d` | §3.1 and §3.4 information access and fit definition |

Frisch and Waugh's 1933 *Partial Time Regressions as Compared with Individual Trends* was located bibliographically at [JSTOR](https://www.jstor.org/stable/1907330), but its full methods were not obtained. No claim about the exact scope of their original proof is used. Lovell's final [1963 JASA article](https://doi.org/10.1080/01621459.1963.10480682) was likewise not obtained; the accessible working paper settles the operative comparison. No human paper request is necessary for the conclusions above. The first Yale download address returned HTTP 403; a legitimate migrated Cowles URL supplied the paper. OCR initially timed out on one page; retry with bounded OCR threads completed. Detailed errors are retained privately in `private_sources/P3_OBSERVER/ACCESS_AND_ERRORS.md`.
