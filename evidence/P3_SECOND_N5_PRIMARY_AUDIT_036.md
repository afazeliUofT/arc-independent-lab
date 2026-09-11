# N5 primary-method audit: source-trained reading programs

Date and source access: **2026-09-10**. Research consultation for the PI, **not an independent review and not a formal GO/KILL verdict**. No candidate-model execution, native reviewer session or paid run was performed. Hosted research consultation did occur. This audit concerns only the frozen N5 and shared contract in `docs/P2_SECOND_OPERATION_SPECIFICATIONS_035.md`, SHA-256 `25f3148827d22abbe587a6c2ff0c5a3ff2db1883f70e678f640f16d0f07a7c69`, verified at repository base `17bd0df7a4d60f6ddfcffefc73049b1471a5ffd1`. The Phase 3 requirements in `docs/governing/02_RESEARCH_PROCESS.md`, the post-freeze flags, and the prior C3 correction were read. No other lab repository was accessed.

## Finding and exact scope

**The frozen N5 synthesis-and-query operation is supervised, complexity-penalized finite-DSL expression synthesis from retained historical response labels.** Its learned program is a reader of a post-update state and query; the desired outputs were generated from saved pre-update states. This is a substantive operation, not merely an arithmetic estimator. The relevant complete antecedents are inductive synthesis, exhaustive symbolic regression, learned synthesis search, and task-oriented model stitching. DreamCoder is relevant, but calling N5 a new DreamCoder-like library learner would misdescribe its frozen cache semantics.

An exact reduction to a matched supervised expression learner is given below. It establishes no distinctive output advantage over that learner. **F is a PI-constructed normalization comparator: its equivalence alone is not sufficient evidence for a historical novelty kill.** It does **not** establish that the inspected release of DreamCoder, ESR, BUSTLE, or a stitching implementation already executed every N5 source-episode, rational-encoding, cache, reset, and target-freeze convention. Named-method identity, family membership, and priority for a complete combination are separate claims.

The residual potentially useful contribution is a **specific experimental protocol and application**: learning a state-conditioned old-response reader on actual source learning trajectories, freezing it before target exposure, and testing whether its later answers depend on relation-specific information in the target carrier. No structural novelty in the search, objective, memoization, or historical-label supervision is evidenced here. The exact priority of the entire acquisition-and-transfer wrapper remains unestablished; that uncertainty is not positive evidence of novelty.

## Primary sources and reading coverage

All URLs below were accessed on **2026-09-10**. Method comparisons use full primary text, not abstracts. Short labels are local to this audit.

| ID | Source and version actually inspected | Coverage |
|---|---|---|
| D | Ellis et al., [DreamCoder, 2020 arXiv v1](https://arxiv.org/pdf/2006.08381), plus [author-hosted full draft and supplement](https://www.cs.cornell.edu/~ellisk/documents/dreamcoder_with_supplement.pdf) | Wake/Sleep Program Learning; supplement S4.1–S4.5, Algorithms 1–4, and search/resource discussion. Both inspected texts are **prepublication versions**; the supplement calls itself a draft. |
| E | Bartlett, Desmond & Ferreira, [Exhaustive Symbolic Regression, arXiv v2, 2023](https://arxiv.org/pdf/2211.11461v2) | §§II.A–E, III and V: tree generation, duplicate handling, parameter fitting, ranking, scaling. Inspected accepted manuscript/preprint, not publisher PDF. [Version record](https://arxiv.org/abs/2211.11461) records acceptance and links [IEEE DOI](https://doi.org/10.1109/TEVC.2023.3280250). |
| B | Odena et al., [BUSTLE, full ICLR 2021 paper in arXiv v3](https://arxiv.org/pdf/2007.14381v3) | §§2.1–2.4, 3–3.2, Algorithm 1. The PDF identifies itself as published at ICLR 2021; the accessed host is arXiv. |
| S | Csiszárik et al., [Similarity and Matching of Neural Network Representations, NeurIPS 2021 published paper](https://proceedings.neurips.cc/paper/2021/file/2cb274e6ce940f47beb8011d8ecb1462-Paper.pdf) | §§3–4 and §5.1; implementation details also checked in [full author preprint, Appendix A.3](https://arxiv.org/pdf/2110.14633). |
| W | Zhou et al., [Permutation Equivariant Neural Functionals, arXiv v3](https://arxiv.org/html/2302.14040v3), September 2023 | Bounded follow-through: §§2.1–2.2, 3.4, Appendices D.4 and E.2. Full preprint methods; its [record](https://arxiv.org/abs/2302.14040) says to appear at NeurIPS 2023. No publisher-version comparison claimed. |
| T | Peebles et al., [Learning to Learn with Generative Models of Neural Network Checkpoints, arXiv v1](https://arxiv.org/pdf/2209.12892), September 2022 | Bounded follow-through: §§2–3, §4.1 and Appendix C. Full **preprint** methods; no conference/journal publication verified. |

DreamCoder publication correction: the author's [publication list](https://www.cs.cornell.edu/~ellisk/) identifies *DreamCoder: Bootstrapping Inductive Program Synthesis with Wake-Sleep Library Learning*, **PLDI 2021**, [DOI 10.1145/3453483.3454080](https://doi.org/10.1145/3453483.3454080). Its ACM routes returned access errors. The 2020 title/link in the flag is not silently relabeled as the PLDI paper. Full primary methods were nevertheless available in D. Literal claims about changes between the inspected draft and final PLDI version remain outside this audit.

## 1. The complete frozen operation

Write source episode `j`'s saved state as `s_j0`, actual update prefix as `u_jt`, and resulting state as `s_jt = Update*(s_j0,u_jt)`. The permitted source queries `Q_j` are the first `Q_max` distinct ordinary prediction queries already logged **before** that snapshot. The acquired row is

`((s_jt,x), y_jx)` where `y_jx = Base(s_j0,x)` and `x ∈ Q_j`.

Rows from odd acquisition episodes enter construction; even episodes enter checking. Prefixes from one episode cannot be split across both. The labels describe the base learner's old behavior, which can itself be wrong about the world. Base/Update code, state/query serialization and fixed dimensions are supplied priors; query semantics are not learned automatically by this procedure.

The hypothesis class contains every well-typed expanded tree of size at most `S_read`, using state/query components, constants `-1,0,1`, arithmetic, protected division and lazy `IF_LESS`. Exact rational evaluation and invalid propagation are part of the semantics. For construction multiset `C`,

`J_C(p) = (1/|C|) Σ_(z,y)∈C (p(z)-y)^2 + lambda·|p|_expanded`.

Any invalid construction output gives infinite score. Selection minimizes `(J_C(p), |p|_expanded, serialization(p))` lexicographically. Checking errors are recorded after selection and never select a replacement, choose fragments, or migrate into construction. Empty construction/checking partitions produce `INSUFFICIENT_SOURCE_LESSONS`; incomplete search reports its actual prefix, not an exhaustive optimum.

All source membership, source queries, grammar, parameters, selected program and checking record are frozen **before target state or query exposure**. Only the frozen `p` then consumes target `(s,x)` and emits a value with `SOURCE_TRAINED_CONJECTURE`, or `INVALID_READING`. No target fitting, raw-lesson lookup, target-directed source selection, cache update, or validation takes place. N5 does not include physical trial RESET from N2–N4; its source snapshots and learner-state discontinuities have the separate learning-state contract.

## 2. Exact mapping to supervised expression synthesis

This is an explicit construction and deduction from the frozen specification, not an assertion that a cited software package already has these defaults. Define comparator **F** as ordinary finite-DSL supervised expression synthesis with the following matched input/output protocol.

| Required axis | N5 variable or behavior | F mapping and consequence |
|---|---|---|
| State | Source episodes/provenance, updates, queries, lessons, selected program, checking errors, fragments, search cursor | Identical training-data acquisition records, regression dataset, fitted expression, validation log and enumerator/memo state. Merely renaming these objects loses no information. |
| Inputs | `s_jt`, `x`, historical `Base(s_j0,x)` | Flatten each input as `z=(s_jt,x)` and label as `y`. Preserve multiplicity: several prefixes repeating an old answer still contribute several rows. |
| Update | Exhaustive tree scoring, exact minimum and deterministic ties | Use exactly N5's grammar, arithmetic, invalid semantics, objective, expanded-size bound and tie order. Each scored tree and selected expression is identical. |
| Allocation | First `Q_max` pre-snapshot queries; odd/even episodes; fixed `S_read`, `lambda`, `K_read` | Use the same data-generation wrapper and resource ceilings. No comparator receives extra labels, queries, semantic names, teacher calls, or target states. |
| Reset and repetition | Persistent source/program/search state survives volatile clearing; new passes retain partition provenance | Retain identical fields; erase only identical volatile state. Forced deletion of source records/programs is the same explicit ablation. Successive source passes consume exactly the same newly acquired rows. |
| Target inference | Frozen program, input `(s,x)`, conjecture/invalid status | Evaluate the same expression on the same encoded input and attach the same status. No fitting or source-row lookup at target time. |
| Cost | Copies, Base/Update calls, enumeration, checking, bookkeeping, retained bytes, rational bit costs | Charge those same operations and buffers. A literally matched implementation can have identical accounting; flattening is an indexing convention, not a free alternate dataset. |

**Proof.** Initially matched acquisition state yields identical source rows. Inductively, every actual source prefix and permitted query yields the same pair `(z,y)` and parity assignment. At any completed pass, the candidate set, each candidate value, each score and all tie keys coincide. Thus the selected program and checking errors coincide. Identical frozen expressions then return identical target values on every permitted target sequence. Search interruptions can also match if the same cursor and operation accounting are used. F does not need a scientific interpretation of a label as an “old response” to compute this result.

Consequently **there is no separating history against F**. This is exact identity to an instantiated supervised-synthesis family with the acquisition wrapper held fixed. It is not an earliest-priority proof for that wrapper or an identification of N5 with unmodified E, D, B or S. An experiment reporting better answers than F would reveal different information, grammar, costs, ties, arithmetic, or an implementation defect.

The objective also has an exact bounded Bayesian-program interpretation. For a fixed construction size `n` and any fixed positive variance `sigma²`, use Gaussian label likelihood and prior `Pr(p) ∝ exp[-n·lambda·|p|/(2 sigma²)]` over the same finite grammar. Maximizing their product minimizes `MSE + lambda·size`, with the same explicit tie rule. Invalid programs receive zero likelihood. This is our mathematical specialization, not a claim that D ran that prior or dataset. In particular, N5's fixed `lambda` implies a prior strength depending on `n` in this interpretation; it does not equal D's entire evolving library/recognition algorithm.

### Cache boundary

A stored fragment always expands to its original tree, contributes full expanded size, and never changes canonical candidate order. Therefore `K_read=0` and `K_read>0` select the same optimum whenever both finish. A cache may change elapsed work and whether a bound permits completion; that is an implementation effect requiring measured cost. Erasing/recomputing memo entries cannot alter an already frozen program's output. Memoization must preserve lazy branch semantics: an unused invalid branch cannot invalidate `IF_LESS`.

This removes the proposed “new library learning” route to novelty in the reference. D's changing library/search distribution is a different object; adding that effect to N5 now would change the frozen operation.

## 3. Four complete method comparisons

These mappings distinguish the actual methods from F. Resource consequences below are analytical accounting, not measured cross-paper speed comparisons.

| Method | State and input mapping | Update and allocation | Reset and cost boundary |
|---|---|---|---|
| **E: ESR** | N5's `(z,y)` becomes equation-fitting data; candidate trees become functional forms. E's inspected implementation uses one input variable and free numeric parameters. | E enumerates bounded trees, handles algebraic duplicates, optimizes parameters using repeated BFGS, then ranks by description length. N5 has fixed rational terminals, multiple components, conditionals, no continuous fit and a different penalty. | E can reuse generated function catalogues across datasets. No N5 episode/reset protocol is supplied. Fitting, symbolic simplification and retained catalogue cost are additional to evaluations. |
| **D: DreamCoder** | N5 lessons could specify one synthesis task. D retains multiple task beams, a library and recognition network; these have no corresponding learned search state in N5. | D alternates program search, abstraction and recognition training; library compression changes the prior and search. N5 completes a fixed expanded-tree order and stores subtrees only for memoized evaluation. | D retains learned library/network across tasks, not N5's discontinuity protocol. Search, refactoring/version spaces, network training and synthetic-task generation must be charged. N5 cannot claim these capabilities or costs were included. |
| **B: BUSTLE** | N5 rows map to input-output examples; intermediate expression values map to B's value table. Its concrete DSL targets strings/integers, not exact rational scalar regression. | Algorithm 1 executes bottom-up combinations, deduplicates observationally equal values, and uses a trained classifier to reweight search; it returns a consistent expression. N5 scores all expanded trees and allows residual error. | Model parameters persist across problems; per-problem value tables rebuild. No episode parity or learner-reset rule is supplied. Classifier training/inference, property computation, values and searches all cost resources. |
| **S: task-oriented model stitching** | Source and reference networks supply paired activations; a stitch connects source representation to reference task map. Reference-model outputs already provide teacher supervision; the pair need not be chronological checkpoints. | The implemented stitch is affine; task matching trains only it using teacher-output cross-entropy. Direct matching instead uses least squares. N5 makes checkpoint coordinates runtime inputs across source episodes and searches expressions with MSE. | S fits a chosen pair/layer; it does not supply N5's cross-episode target freeze. Retained network portions, paired evaluations, adapter fitting/storage and adapter evaluation count. N5's snapshot/lesson construction replaces none of them for free. |

Sources: E §§II–III; D full algorithm and supplement S4; B §§2–3 and Algorithm 1; S §§3–4. The closest **search operation** is bounded symbolic expression synthesis, particularly E's exhaustive functional search, not an arithmetic estimator alone. The closest **historical-output translation operation** in this set is S's task-loss matching, not its estimator isolated from the surrounding networks and paired data.

## 4. Concrete differences and their meaning

The following are analytic histories, not runs or evidence of practical transfer.

### A. Conflicting historical labels: fitting versus consistency

Let `Base(s,0)=s` and an actual update overwrite state with `0`. Two odd-index source episodes start respectively with `s0=0` and `s0=1`; each previously logged query `0`. Their construction lessons are `((0,0),0)` and `((0,0),1)`. Separate even episodes provide a nonempty checking set. Choose `lambda=0`, `S_read≥5` and enough computation. N5's grammar contains `1/(1+1)`, so its completed minimum construction MSE is `1/4`, attained at output `1/2` on that input.

A deterministic **exact-consistency** PBE procedure cannot satisfy those two rows. B's consistency objective, and D's 0/1 input-output likelihood variant, therefore cannot return a consistent solution to the corresponding task, even if their grammars were given rational division. This separates objectives, not a new form of recovery: changing to a residual-error likelihood/objective is a standard synthesis formulation, and D's framework allows likelihoods beyond its exact-I/O variant. F already reproduces N5 exactly.

### B. Exact rational bounded syntax versus free parameters

Using the same overwrite update, give every construction label `2`, current state/query `0`, and choose `S_read=1`. N5 can only emit one of its permitted leaves and selects `1`. E's one-node parameter form can fit a constant `2` exactly. This compares available one-node fits, not E's final MDL winner. The difference is a restricted parameter language; allowing fitted constants or increasing N5's syntax budget changes it. It provides no structural-novelty defense.

E's actual description-length score also includes operator-vocabulary and parameter-precision terms absent from N5's single size coefficient. Those terms cannot be silently replaced by `lambda·size` while claiming literal algorithm identity. Conversely, a different complexity score does not make exhaustive supervised equation search newly invented.

### C. A nonlinear reader versus a fixed affine stitch

Let `s0=(a,0)`, `a∈{-1,1}`, and `Base((v,b),0)=v`. Actual source update types are `U0(a,0)=(a,0)` and `U1(a,0)=(-a,1)`. Arrange distinct odd construction episodes to cover all four `(a,U)` cases; even episodes are separate checks. Post-update state `(v,b)` then has old-response label `(1-2b)v`.

N5 represents this function as `IF_LESS(b,1,v,0-v)` (size 7). Fix the comparison interface to identity features of `(v,b)` and identity scalar output readout. No affine map `alpha·v + beta·b + gamma` fits all four balanced points: the needed slope in `v` is `+1` at `b=0` and `-1` at `b=1`. Its best MSE is `1`; the exhibited N5 program's score is `7·lambda`, so `S_read≥7` and `0≤lambda<1/7` make some nonaffine program beat every affine map under nonnegative size penalties.

No choice of affine penalty, rank or coefficients repairs this four-point obstruction under that fixed interface. This is a real **function-class** separation from the named affine implementation. It is not a separation from S's general unconstrained stitching framework, nonlinear surrounding networks, or contemporary nonlinear stitches. It also does not prove that the selected program generalizes outside these four source cases. Enlarging a translator's function class is distinct from inventing the supervised translation operation.

### D. Source history remains an information channel

Compare two allowed acquisitions with identical post-update inputs `(0,0)` but all old source responses `+1` in one and `-1` in the other; use the overwrite base/update above and nonempty independent checking episodes. With `S_read=1` the respective programs are `+1` and `-1`. At the same target state/query they give different answers. The extra distinguishing information arrived through the source history and survives in the program. No target old answer was used, but this is not an archive-free construction.

Separately, if two **target** histories produce identical `(s,x)` and require different old answers while sharing the same frozen source program, every deterministic N5 reader emits the same answer for both. Learned syntax cannot reverse a genuinely many-to-one loss of all relevant information. A state marker such as `b` in C makes that example decodable; it is a supplied observable coordinate of that example, not evidence that N5 discovers such markers universally.

## 5. What a recovery claim would and would not establish

The target-time ban on raw source-lesson inspection is meaningful: N5 evaluates a learned expression instead of retrieving a source row. The source labels, query encoding and expression are nonetheless channels that can carry task information. Freezing before target exposure prevents a particular leakage route; it does not make the learned program independent of its historical supervision.

The exact reduction says the procedure is supervised synthesis **from old answers on source episodes**. It does not say every target answer was previously present in those lessons, nor that lessons alone can determine answers for arbitrary unseen relations. A frozen reader may generalize a useful decoding rule when the target state retains information. That possibility requires evidence beyond source fit, and is compatible with the reduction to F.

The later protocol must hold target relation instances out of source episodes including update/query provenance; row or episode splits alone do not establish relation exclusion. Compare identical source training on a target carrier that acquired the relation versus a matched carrier that never acquired it, preserving query encoding and inference cost. Constants and source-only answer shortcuts must not explain the difference. Ordinary prediction, F, and a supplied decoder have distinct roles: F checks methodological identity; ordinary prediction measures changed access; a supplied decoder probes accessible information under the declared interface. None is a claim that source-trained responses are correct world knowledge.

An analyst-created observer that retained no old targets has a different information budget. N5 cannot inherit that earlier restricted-access result. Nor does it specify initial world-model learning, autonomous source-episode designation, boundary discovery, uncertainty calibration, or an integrated controller for N1–N5.

## 6. Historical constraints and verified continuations

The inspected D methods and supplement document combinatorial program search, memory growth in best-first search, and the work required to acquire useful search biases. B §1 identifies model-inference overhead and synthetic-program distribution mismatch. E §II documents exponential catalogue growth and duplicate-handling memory demands. These are concrete technical constraints. **Why a particular earlier research community set the approach aside, or an institutional history of abandonment, was not established by these sources.** No funding, hardware-era or disciplinary-preference explanation is invented. This audit did not perform a new full 1960–2010 primary-source genealogy, so earliest program-induction or memoization priority is not claimed.

The ideas were not shown to have disappeared. Two method-level continuations were inspected:

* Bowers et al., [Top-Down Synthesis for Library Learning, POPL 2023, author-hosted published text](https://mlb2251.github.io/stitch_jul11.pdf), §§2–4, develops corpus-guided abstraction search with branch-and-bound compression utility. This is **Stitch the library-learning tool**, distinct from neural model stitching. Its learned abstractions rewrite/compress programs; N5's expanded-size memo cache does not do that.
* Ford et al., [The functional form of galaxy and halo luminosity and mass functions, arXiv:2604.23236v1](https://arxiv.org/html/2604.23236v1), April 2026 **preprint**, §3.1, actually uses ESR with bounded functional enumeration, simplification, parameter fitting and description-length ranking. This establishes continuing use as of 2026, not an N5 reader result.

A further directly relevant continuation is Mai et al., [Revisiting Model Stitching in the Foundation Model Era, arXiv:2603.12433v3](https://arxiv.org/html/2603.12433v3), §§3.1–3.2.2. The inspected June 2026 **preprint** uses a two-layer ReLU MLP stitch between frozen networks, with final-feature MSE pretraining and subsequent task training. Its [version record](https://arxiv.org/abs/2603.12433) reports CVPR 2026 acceptance; no publisher-version comparison is claimed. Nonlinearity therefore cannot be treated as a missing capability of contemporary stitching. None of these inspected continuations establishes priority for N5's exact episode-and-target contract.

## 7. Resource accounting and remaining questions

If episode `j` has `k_j` update prefixes and `q_j≤Q_max` queries, its lesson count is `k_j q_j`. Generating those lessons requires actual source encounters, permitted state copies, update-prefix computation and old Base evaluations. Sequential prefix computation can avoid replaying every prefix from scratch; that is an implementation choice to declare. Caching `Base(s_j0,x)` can avoid repeated identical calls, but the labels remain retained resources. Literal state duplication per row and shared immutable state references have different byte costs and must be stated.

With `P_read` trees, `n_read` construction lessons and maximum expanded size `S_read`, direct scoring takes `O(P_read n_read S_read)` rational node operations; checking adds at most `O(n_check S_read)` for the chosen tree. This excludes neither numerator/denominator growth and arithmetic bit work nor acquisition, serialization, provenance and bookkeeping. Cache bytes, saved snapshots, update records, queries, lessons, selected trees and interrupted cursors count under the memory ceiling. No published wall-clock number here substitutes for profiling N5.

Residual questions for the PI and later independent review:

1. Is the exact F reduction and its information accounting accepted? It prevents an output-novelty claim against a properly matched supervised expression learner.
2. Is there a closer existing **whole procedure** for supervised readers conditioned on changing learner checkpoints, with historical teacher labels and source-to-target transfer? The four main comparisons and the two-method follow-through below do not settle that entire priority question.
3. Does any useful target reading generalize across relation instances and update types under the fixed interface, or is it source-task fitting? No experiment here answers that.
4. Can exhaustive rational search finish at useful state dimensions and expression sizes? This is unmeasured, and the source literature's scaling constraints make it a material question rather than an assumed capability.

These are consultation findings, not a formal gate decision or authorization to implement a new variant.

### 7.1 Bounded follow-through: learned functions of weights and trajectories

The PI requested this follow-through because constructing F does not independently establish an earlier complete operation. Two additional full methods were inspected, without proposing or running an N5 variant.

**W supplies a particularly close runtime precedent.** Its INR editing method learns `U' = U + gamma·NFN_phi(U)` and minimizes pixel MSE between `SIREN(q;U')` and an image-space transformed target. Thus the whole composition already has the form `(weights U, query q) → response`. Labels come from dilation/contrast processing of source images. NFN parameters are trained by backpropagation across image-specific INRs. Appendix E.2 separately learns scalar current-checkpoint accuracy from `(weights, test accuracy)` pairs, splitting by training run. Neither task labels a later checkpoint with an earlier checkpoint's query answers. [W §§3.4, D.4, E.2](https://arxiv.org/html/2302.14040v3).

**T supplies a trajectory-learning precedent.** G.pt samples two saved checkpoints from one actual optimization run with `t1<t2`. Its denoiser receives noised later weights, earlier weights, both performance metrics and diffusion time; its squared-error target is the later weights. At inference it conditions on starting weights, their metric and a requested metric, producing updated weights by denoising. The reported sampler uses 1,000 diffusion steps. The prompt is an optimization target, not N5's old-response query. [T §§2–3, §4.1, Appendix C](https://arxiv.org/pdf/2209.12892).

| Required mapping | W relative to N5 | T relative to N5 |
|---|---|---|
| State and runtime input | `U` corresponds to a learner-state tensor; coordinate `q` corresponds to a query; fitted `phi` replaces the reader program. | Earlier weights correspond to a starting learner state; metrics and noise have no matching N5 query role. |
| Supervision and update | Image transformation targets plus gradient training replace historical `Base(s0,x)` labels and exhaustive rational synthesis. | Later weights replace scalar earlier-response labels; diffusion training replaces expression selection. Temporal direction is forward. |
| Allocation and persistence | Source INRs, images, fitted NFN and generated weights carry information. Their retained bytes and any rebuilt state must be counted. | Source trajectories/metrics, fitted denoiser and generated parameters carry information. They are not free historical access. |
| Reset and cost | No N5 volatile-reset/episode-parity contract is specified. Training includes INR acquisition and optimization; runtime includes NFN and SIREN evaluation. | No N5 reset/parity contract is specified. Training-data acquisition, denoiser optimization and iterative sampling all count. |

The table's N5 correspondence and accounting are our deductions, not claims of matched published experiments. W demonstrates that making network state a learned reader's input is already an implemented operation; its factorization through edited weights does not itself separate it from an abstract reader `P(s,x)`. But **current-checkpoint prediction, desired image transformation, current-output reconstruction, and historical-output recovery after an update are different supervision contracts**. W does not provide N5's chronology. T provides chronology, but predicts future parameters rather than past responses. Changing these target constructions would be a method adaptation; it would not show that the inspected papers already performed N5.

This tightens the nearest-operation choice: compare N5 to source-trained neural weight functions as well as expression synthesis and fixed-pair stitching. It removes “a learned reader takes network weights and a query” as a defensible novelty claim. **No exact named historical-operation reduction or whole-combination priority conclusion follows from these two sources.** F remains useful for component identity and fair comparison, and the precise N5 historical-label/target-freeze wrapper remains a concrete priority gap, not an established invention.

## 8. Access record and source gaps

Full PDFs and extracted text are private working intermediates outside the repository under `delivery/rebuild036/n5_research/`; no full copyrighted paper is included in public evidence. Companion `P3_SECOND_N5_TOOL_ERRORS_036.jsonl` records retrieval errors and wrong-route checks. No credential use, payment or paywall circumvention occurred.

The exact final PLDI DreamCoder and IEEE ESR publication versions were not read. Their full prepublication methods were available and sufficient for the bounded comparisons above. **No paper request blocks this audit**, because no conclusion depends on an abstract or on asserting identity to an unseen final version. If a later claim depends on publication-version details, that specific dependency should be sent to the PI through the `04_RESOURCES_AND_SETUP.md §5` paper-request channel before claiming it resolved.

Downloaded working-source SHA-256 identifiers:

| Working source | SHA-256 |
|---|---|
| D 2020 arXiv PDF | `547027556f1220f22555c35f91d2527d78d825553a1b24201f58d56274ec0e80` |
| D author full draft/supplement | `97e74b45b3e38aa0e2e25f02e0be841484c4ecceb975ddfc187c638a0872484b` |
| E arXiv v2 PDF | `592f0aa261cd38ff3df56c6f1d9db0eeba0e72a96ef35a455cb9c80d0d136941` |
| B arXiv v3 / ICLR paper PDF | `0bbc4a9f37d81686786eacae4028e73073370469ad79e0343d93c01444e73d9e` |
| W arXiv v3 PDF | `068640b6b12e90ad82729aa82759131cca400e1bbb2d4839c7c895be33e55a2a` |

S, T and the continuation methods were read through primary web full text; no local-file hash is asserted for those tool-rendered sources. W was also downloaded as a private working PDF. Published-method claims in this report remain restricted to the reading coverage listed above.
