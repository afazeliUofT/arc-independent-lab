# C3 primary-method novelty audit

Date and source access: **2026-09-06**. This is a PI research consultation with shared tools and filesystem, **not an independent review or a formal GO/KILL verdict**. The approved operation is unchanged. The frozen specification is `docs/P2_OPERATION_SPECIFICATIONS.md`, SHA-256 `d37a52eeb569461503b262d2790a656048624ede4790aeb49254e5a9f133c26f`; approved `IDEAS.md` SHA-256 `73cab9f6ab1f5eda80c7c2adc6d2ed556c63d5652fd65434e4cc4b24383dc3b8`. The human's three requirements are preserved in `state/escalations/2026-09-06_PHASE2_APPROVED.md`.

## Finding and correction

**C3 is a cached, regularized representation stitch whose old-query behavior is exactly expressible as refitting a linear reader to cached old responses.** The Phase 2 flag naming ridge regression was inadequate: it named the fitting machinery and omitted the closest operational antecedents. The corrected comparison is to direct representation matching and model stitching, paired-anchor latent translation, continual feature-drift compensation, feature-evolvable streaming, and the supervised recovery procedure in Zheng et al. It is not enough to establish that C3 uses a familiar estimator; it is also not defensible to claim a new recovery operation merely because its regularizer or caching schedule differs.

The fitting and readout are exactly subsumed by a specialization of the regularized equivalence-matching family below. An exact input/output algebraic reduction is supplied separately. This does **not** assert that an inspected published implementation already used every C3 boundary, cache, regularizer and reset convention. Nor does it supply an independent verdict. The present audit finds **no evidenced structural novelty in C3's recovery operation**; the remaining literal differences are identified so a reviewer can dispute that conclusion precisely.

**C3 is a different operation, with a weaker claim about required historical information than our successful observer.** It requires pre-boundary activations and an old readout; it does not recover from the observer's current-state interface. We take the human's option to state this difference plainly rather than silently replacing the approved candidate during screening.

## Primary methods actually inspected

All links in this document were accessed **2026-09-06**. These are primary sources. Reading coverage is explicit; this is a targeted audit, not an exhaustive search or a claim of earliest historical priority. No comparison depends solely on an abstract.

| ID | Source and version | Inspected methods and bounded relevance |
|---|---|---|
| S1 | Lenc & Vedaldi, *Understanding Image Representations by Measuring Their Equivariance and Equivalence*, CVPR 2015, [published PDF](https://www.cv-foundation.org/openaccess/content_cvpr_2015/papers/Lenc_Understanding_Image_Representations_2015_CVPR_paper.pdf) | §2 including §2.1 and the equivalence objective; §3.3 stitching. Regularized maps between two representations are evaluated by attaching the destination network's remaining computation. Their actual favored regularizers are sparsity-oriented; an identity-centered penalty is not claimed to be their evaluated variant. |
| S2 | Csiszárik et al., *Similarity and Matching of Neural Network Representations*, NeurIPS 2021, [published main paper](https://proceedings.neurips.cc/paper/2021/file/2cb274e6ce940f47beb8011d8ecb1462-Paper.pdf), [supplement](https://proceedings.neurips.cc/paper_files/paper/2021/file/2cb274e6ce940f47beb8011d8ecb1462-Supplemental.pdf) | Main §§3–4 and §5.1; supplement A.3 and relevant direct-matching details. Direct matching uses paired activation matrices and a least-squares stitch; task-loss matching trains the stitch through a frozen task map. The implemented unconstrained fit includes an affine bias. These are distinct objectives, not interchangeable evidence. |
| S3 | Maiorca et al., *Latent Space Translation via Semantic Alignment*, NeurIPS 2023, [published PDF](https://proceedings.neurips.cc/paper_files/paper/2023/file/ad5fa03c906ca15905144ca3fbf2a768-Paper-Conference.pdf) | §§3.1–3.2 and the §4 stitching procedure. Corresponding anchor sets support translation into an existing decoder's space. Their variants include affine, least-squares linear and orthogonal transformations; normalization uses anchor statistics. This directly counters novelty from paired anchors, closed-form translation, or reuse of an unchanged decoder. |
| S4 | Hou, Zhang & Zhou, *Learning with Feature Evolvable Streams*, NeurIPS 2017, [published PDF](https://proceedings.neurips.cc/paper/6740-learning-with-feature-evolvable-streams.pdf) | §§3–4, Algorithms 1–2 and the old-reader path. During a short overlap between old and new feature streams, paired measurements estimate a new-to-old linear map. An old predictor can then use reconstructed features. The complete FESL method also updates predictors and combines their outputs; it is not C3 verbatim. |
| S5 | Gomez-Villa et al., *Exemplar-free Continual Representation Learning via Learnable Drift Compensation*, ECCV 2024, [published PDF](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/01192.pdf), [supplement](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/01192-supp.pdf) | Main §§3.1–3.4, fitting details in §4, supplement Algorithm 1 and feature-storage ablation. LDC freezes old/current encoders during projector fitting on current-task inputs, maps old features forward, and updates stored class prototypes. It uses no current labels for alignment, but its prototypes are historical state. The introduction's shorthand about learning from prototypes alone is insufficient: the algorithm also needs current data and the previous encoder. |
| S6 | Cotogni et al., *Exemplar-Free Continual Learning of Vision Transformers via Gated Class-Attention and Cascaded Feature Drift Compensation*, IJCV 133 (2025), [published article](https://link.springer.com/article/10.1007/s11263-025-02374-x), [published PDF](https://link.springer.com/content/pdf/10.1007/s11263-025-02374-x.pdf) | §§3.2–3.5, especially Eqs. 6–8 and retained projection cascade. Current-to-previous feature projections feed older task interfaces. The training loss includes projected functional regularization, and the full method also uses masks and task classifiers. Retained adapters and multiple passes matter to its cost. |
| S7 | Chaudhry et al., *Using Hindsight to Anchor Past Knowledge in Continual Learning*: [AAAI 2021 publication record](https://ojs.aaai.org/index.php/AAAI/article/view/16861); inspected [arXiv:2002.08165v1 PDF](https://arxiv.org/pdf/2002.08165v1), **preprint, 2020** | Preprint §§2–3, Eqs. 5–9 and Appendix D pseudocode. Learned synthetic anchors and replay constrain the learner's parameter updates. This is anchor-based continual preservation, not a frozen-encoder post-update translation. Published-PDF access failed, so no claim of version equivalence or published implementation detail is made. |
| S8 | Zheng et al., *Spurious Forgetting in Continual Learning of Language Models*, ICLR 2025, [published PDF](https://proceedings.iclr.cc/paper_files/paper/2025/file/a774503daed55eb53c634847ae071ec7-Paper-Conference.pdf) | §§3.1–3.2, appendices C–E, and the displayed F.1 statement/derivation. Biography recovery fine-tunes an intervening checkpoint on one half of old QA data and evaluates the other half. Fine-tuning changes model parameters. This is substantial old supervision and parameter adaptation, not current-state-only decoding and not C3's fixed old reader. The formal-theory issue below is kept separate from this empirical procedure. |

The 2015–2025 methods above were not uniformly abandoned. Later work explicitly develops or tests earlier alignment operations. We have no evidence that an expired compute constraint prevented adoption of this particular C3 operation. Available compute makes larger comparative evaluations feasible; it does not repair absent anchors, ambiguous correspondences or erased distinctions. Historical neglect is not a novelty argument here.

## 1. Exact audited object

C3 receives a current encoder `f_theta`, a fixed old linear reader `W`, an externally declared boundary, deterministic pre-boundary anchor-selection rule, positive fixed `lambda`, and a fixed refresh schedule. It saves raw anchors `X`, boundary activations `R`, `W`, and initially `T = I`. Encoder training remains exactly the original training. At refresh it evaluates `Z = f_theta(X)` and solves

\[
T=(Z^\top Z+\lambda I)^{-1}(Z^\top R+\lambda I).
\]

An old query returns `f_theta(x) T W` followed by the originally fixed postprocessing. The encoder, new reader, `W`, `X` and `R` do not change as a result of fitting `T`. Declared persistent channels retain `X,R,W,T` over context clearing. Observation-semantic changes can invalidate their interpretation; C3 has no test that automatically detects that event.

No autonomous boundary discovery, anchor invention, query-family discovery, uncertainty estimate, environmental exploration, or self-selection of the repair is part of this object.

## 2. Mapping to regularized representation stitching

For S1 §2.1 use its *equivalence* case, rather than its image-transformation case. S2 supplies the explicit source-representation → stitch → destination-task-map composition. The following is our specialization, not a quotation of a previously published C3 implementation.

| Required axis | C3 | Mapping and exactness boundary |
|---|---|---|
| State | Current encoder; `X,R,W,T` | Source representation is the current checkpoint. Destination reference representation is the boundary checkpoint restricted to `X`. Its only required responses during fitting are memoized as `R`. Destination task map is `W` plus fixed postprocessing. Stitch is `T`. Caching removes the need to retain a callable old encoder after these evaluations. |
| Inputs | Current `Z`, cached `R`, fixed penalty and reader | Paired source/destination activation matrices. Correspondence is input identity: anchor `x_i` at the two checkpoints. No class label is needed to build the pairs; the destination activations are nevertheless historical targets. |
| Update | Unique identity-centered quadratic fit | In S1 Eq. 2 choose zero bias, squared Euclidean reconstruction loss, `R_pen(A)=||A-I||_F²`, and coefficient `lambda/n` because that source averages the sample loss. Use column convention `A=T^T`. Multiplication by `n` yields exactly C3's objective and normal equations. This is exact specialization of the stated regularized ERM family, not identity to S1's favored sparse solver. |
| Allocation | Externally fixed `n`, `d`, anchor rule | C3 adds no learned allocation rule. Restrict paired data to the selected anchors and restrict the stitch to a square linear map. Deterministic selection is a supplied experimental convention, not a new operation inferred from the history. |
| Reset | Keep `X,R,W,T` in the declared channel | A cached stitch retains those same data and coefficients. Erasing the destination cache breaks both. The primary stitching papers do not establish recovery after an arbitrary filesystem/model-memory erasure; C3's persistence contract supplies that boundary. |
| Repetition | Refit at predetermined refreshes while original training continues | Repeatedly apply the same fit to a new source checkpoint, keeping destination anchors fixed. The schedule introduces no feedback rule or new information. It is not an empirical claim that every cited paper tested this schedule. |
| Cost | `n` encoder evaluations, dense `O(nd²+d³)` fit; numeric storage `O(nd+d²)` plus `X,W`; query adds `O(d²)` | Literal cached specialization with the same dense solve and buffers has the same resource accounting. A source retaining the complete old encoder is not memory-matched; a source refitting on all old data is not evidence-matched. Caching and restricted queries must be charged explicitly when performing the reduction. |

**Exact claim:** the regularized matching objective and subsequent old-query computation are members of an already stated representation-equivalence/stitching family. There is no history on which C3 differs from that instantiated cached stitch: its state, data pairing, unique fit and query rule have been defined identically above.

**Claim not established:** that a particular earlier executable implements this exact cache/reset/schedule and identity prior. The source's actual zero-centered/sparse penalty, affine bias, full teacher and training-data access must not be quietly relabeled as those choices. Equally, the existence of differences from those particular settings does not show a new mechanism: they remain fitting, information-budget and scheduling specializations of the same operation.

## 3. A stronger exact output reduction: cached-response refitting

This deduction uses the approved equations, not an analogy to another paper. Let

\[
Y=RW,\qquad D=TW,\qquad A=Z^\top Z+\lambda I.
\]

Since `lambda > 0`, `A` is positive definite even for rank-deficient anchors. At every refresh,

\[
D=A^{-1}(Z^\top RW+\lambda W)
  =A^{-1}(Z^\top Y+\lambda W)
  =\arg\min_D\{\|ZD-Y\|_F^2+\lambda\|D-W\|_F^2\}.
\]

The last identity follows by differentiating the strictly convex quadratic. Hence the emitted vector on **every** old query is exactly

\[
f_\theta(x)D=f_\theta(x)TW.
\]

At the boundary, `T=I` corresponds to `D=W`. Between refreshes both remain fixed. At every allowed reset the transformed persistent state is retained. By induction this establishes identical old-query vectors, and therefore identical fixed postprocessing, over every allowed sequence. Neither full rank, invertibility of `W`, anchor generalization nor successful recovery is assumed.

The minimal transformed history is `X,Y,W,D`; `Y` is the old model's cached response vector before final postprocessing. If the final output uses softmax or another nonlinear rule, the cache needed here is its **input**, not just the final class or probability. This qualification is required for exactness.

The reduction is behavioral, not byte-for-byte identity of all internal state. It need not reconstruct `R` from `Y`, or `T` from `D`; C3's unused directions are quotiented out for its one fixed old reader. If multiple future readers were allowed, or `W` changed, that would leave the approved specification and this equivalence would need re-examination. A compression to `np+dp` response/reader scalars can change memory and query cost relative to `nd+d²` activation/stitch scalars; it is not uniformly smaller for all `p,d`. The literal C3 buffers and fit can be retained if identical resource charges are required. No resource saving has been measured here.

This does not by itself prove historical priority for the exact regularized cached-response implementation. It does establish that **C3 cannot have a distinctive output advantage over an exactly matched cached-response refit**. Such an advantage would indicate different inputs, objectives, precision, schedules or implementation errors. The name “translation” cannot exempt it from that comparator.

## 4. Differences from the actual continual/recovery methods

Source methods remain different enough that indiscriminate “all alignment is identical” would also be wrong.

| Comparator | State/input/update mapping | Allocation, reset and cost consequences; exact-reduction status |
|---|---|---|
| S3 paired-anchor latent translation | C3 `Z,R` map to corresponding anchor coordinates; `T` to the translator; `W` to the destination decoder. S3 includes anchor normalization and alternative transformation classes. | One pair of pretrained modules is reused, rather than C3's recurring refresh. Persisting an already fitted translator permits reuse; arbitrary memory erasure is not tested. Paired encoding and dense algebra must be counted. C3 is not the unmodified standardized/orthogonal variant. |
| S4 FESL | New features map to `Z`, old paired features to `R`, its mapping `M` to `T`, and old predictor to `W`. The overlap statistics are accumulated rather than a raw-anchor cache. | Old features really become unavailable; the mapping statistics survive that feature change. Its unregularized inverse requires a nonsingular Gram matrix as written. Subsequent predictor updates and ensemble weights are additional state/computation. C3 instead freezes `W`, refreshes from fixed raw anchors and imposes a positive identity prior. Only the recovered-old-reader subpath corresponds; the full methods are not identical. |
| S5 LDC | Paired old/current activations fit a projector, but the direction is **old to current**. Old prototypes are then changed. | Previous encoder, current data and prototype identities supply history/correspondence. Fitting freezes both encoders; the trained projector updates prototype state. C3 stores old inputs/activations and maps current queries backward. Matrix fitting, old-encoder availability and prototype storage must be charged. These are not the same state transformation or reader. |
| S6 backward projection cascade | Current features are projected to previous feature interfaces, closely matching C3's direction. Unlike C3, the projection regularizer also participates in encoder learning, and old task paths use retained masks/classifiers. | Persistent adapters accumulate across boundaries and can require multiple passes. Optional distillation changes that tradeoff and is not included in C3. Context clearing is harmless only if these states survive. Full training trajectories differ from C3's unmodified encoder training. |
| S7 HAL | Anchor preservation constrains `theta`; anchors themselves are optimized using a labeled replay memory. There is no post-update `T` playing C3's role. | Per-class/task anchors, replay state and nested optimization are additional allocation/cost. It preserves future behavior by changing learning, whereas C3 changes the old readout path after learning. Zero anchoring strength removes the intervention; it does not produce C3. This is a useful non-equivalence check, not the closest reduction. |
| S8 Zheng biography recovery | Intervening model checkpoint is retained; old supervised QA examples trigger fine-tuning. Map current checkpoint to C3's starting learner only, not its recovery updater. | Half-old-data access, further model updates and optimization state/cost differ from C3. Holding out the other half prevents direct answer replay to those evaluation questions, but it does not remove the recovery training channel. Erasing access to that training set disables the stated procedure. No exact reduction to C3 is claimed. |

The costs in this table are resource-accounting deductions from the methods, not cross-paper runtime comparisons. None of these sources demonstrates the entire funded conjunction of discovering an unknown world, retaining what matters across discontinuities and autonomously choosing its recombination.

## 5. Concrete separating histories and why they do not create novelty

The following are exact analytical constructions, not empirical runs or gate scores.

**A. Identity regularization separates C3 from unregularized matching, but is a tunable fit difference.** Take `d=p=n=1`, old anchor activation `R=1`, current activation `Z=2`, `W=1`, `lambda=1`. C3 has `T=3/5` and emits `6/5` for that anchor; unregularized least-squares matching has `T=1/2` and emits `1`. This rules out literal identity to the unregularized S2/S4 fit. It does not separate C3 from the regularized family in §2, which produces `3/5` under the stated specialization. Varying penalty strength/center is not a newly discovered recovery mechanism.

**B. Historical activation dependence separates C3 from current-state-only recovery.** Consider two possible boundary histories with identical current encoder, query feature `z=1`, anchor input, `W=1` and `lambda=1`, but cached `R=+1` versus `R=-1`. C3 returns `1` versus `0`. The difference is carried by the cache; a function restricted to identical current state cannot make that distinction. The imperfect second response reflects the regularizer and does not weaken the information-dependence argument.

**C. Erased feature distinctions cannot be restored by this readout.** Two old inputs have reference activations `0` and `2`, but the current encoder maps both to `1`; let `W=1`, `lambda=1`. C3 selects `T=1` and returns the same value on both. No `T`, any regularizer setting, or postcomposition by the same `W` can make identical current features yield the two distinct old responses. A raw-input lookup from the saved anchors could do so, but that is a different query operation and must not be silently added.

**D. Even invertible drift does not guarantee exact recovery with a positive identity prior.** With square reference anchors `R=I` and rotated current anchors `Z=Q`, where `Q` is orthogonal, C3 gives `T=(Q^T+lambda I)/(1+lambda)`. Then `ZT=(I+lambda Q)/(1+lambda)`, which is not `I` unless `Q=I` (or a zero-regularization limit). Thus current features can fully preserve the old distinction while this particular regularized fit fails to recover it exactly. Small regularization may make the error small; no empirical optimum is asserted.

**E. Finite anchors do not make C3 know when its translation is unidentified.** For `Z=R=[1,0]`, C3 selects `T=I` although the second direction has no paired evidence. It still answers a query with current feature `[0,1]` through `W`. No interval over mappings or abstention flag is returned. The human's uncertainty-preserving through-line concerns C1/C2/C4; importing that commitment into C3 would add an unapproved operation.

**F. No separating history exists against §3's response-refitting comparator within the approved domain.** The equality is algebraic at every refresh and query. Test outcomes separating them require an explicit departure from the shared state/update contract. This is stronger evidence than “both use regression,” and it identifies exactly what an experiment must hold fixed.

## 6. Relationship to the learner-access observation

Our observer recovered an old boundary estimate using current weights and unlabeled features obtained from the learner's own callable feature map. It retained no old target, boundary estimate or experience-dependent extra geometry in that strongest access condition. It still used a supplied fixed-feature, zero-initialization, sequential rank-one training contract. The recovery computation was designed by us; autonomous invention or invocation was not established. See `reports/P2_LEARNER_OBSERVER_001.md`, SHA-256 `5503b185549fcce4daa841a9f4445f53d4f94dc3a43a73440bf877b2d38d1f11`, and results `artifacts/P2_LEARNER_OBSERVER/20260906_001/results.json`, SHA-256 `9c6c95c115e9d350e26c43707092c65208020eac9b02b91d389d335fa3febd08`; local access 2026-09-06.

That observation demonstrates a usable computation absent from the ordinary response path under its declared access contract. C3 instead caches old activation values, treats them as fitting targets, and estimates one linear transport after encoder updates. Its history channel is strictly more permissive on that dimension; its encoder-drift setting is different. These differences do not yield a universal performance ordering between the two methods. They do invalidate treating C3 as a method that realizes the observer's no-additional-history finding.

The exact reduction in §3 sharpens the distinction further: all C3 outputs can be generated by a new current-feature reader refit to historical response targets. A C3 success on held-out inputs could demonstrate useful generalization from those targets using the current representation; it cannot establish recovery without them. The observer's strongest result remains a separate diagnostic contribution whose broader applicability and novelty require their own audit.

## 7. Strongest objections to this audit and required checks

1. **A new combination could remain even when alignment is known.** Correct in principle. Here the claimed C3 combination consists of deterministic old anchors, cached reference responses, an identity-centered linear fit, a fixed old reader and a fixed schedule. Section 2 maps each to an instantiated existing matching operation; §3 removes the allegedly special latent translation from its observable behavior. A genuinely new coupling or an inference rule about when repair is justified has not been specified. This does not judge the separate C1/C2/C4 through-line.
2. **Discarding the old encoder is a meaningful state improvement.** It is a meaningful resource choice, but it loses the ability to evaluate that encoder at arbitrary later inputs. It is exact memoization only because `X` is fixed and no other old-encoder calls are used. A memory claim must compare equal permitted calls and include raw anchors, targets, `W` and fit work. Saving a full teacher as an unnecessarily expensive baseline would inflate C3's advantage.
3. **Cached targets do not explain held-out recovery if current features contain no old information.** Correct: fixed current features can or cannot support generalization, depending on the task. The reduction does not prove that information was erased or that cached answers alone suffice for arbitrary new inputs. It proves that C3 uses a historical teaching signal and cannot beat the matched reader-refit operation. A never-acquired control, matched current-feature information destruction, anchor-disjoint probes and held-out relation tests would be needed to attribute a recovery result. No treatment is run here.

Before a formal judgment, an independently restricted reviewer should check the normal-equation reduction, the distinction between prior-family subsumption and literal published implementation identity, and whether the remaining cache/schedule choices contain any structural novelty omitted here. No workload or broad benchmark is justified solely to rediscover the algebraic equivalence. If C3 is killed as a new operation, the mapping and its information-budget correction remain reportable results.

## 8. Separate correction in a cited theoretical argument

S8's published Appendix F, Lemma F.1 states that `||prod_k(I+W_k)-I|| <= L delta` when `||W_k|| <= delta`. Its own derivation obtains `(1+delta)^L-1`, then replaces the first-order approximation by the claimed inequality. The displayed exact inequality is false for the scalar choice `L=2`, `W_1=W_2=delta>0`: the left side is `2 delta + delta²`, which exceeds `2 delta`. Arbitrarily small positive `delta` still separates them.

This is our counterexample to that displayed lemma, not a replication or a verdict on the paper as a whole. The empirical biography-recovery procedure does not depend on accepting that inequality. No C3 inference here relies on the lemma or claims a validated Transformer-level mechanism from it. Any future use of that theoretical chain must resolve its scope or correction first. Source: [published S8 PDF, Appendix F.1](https://proceedings.iclr.cc/paper_files/paper/2025/file/a774503daed55eb53c634847ae071ec7-Paper-Conference.pdf), accessed 2026-09-06.

## 9. Access, provenance and remaining dependency

Full downloaded papers and extracted reading text are private intermediates under `private_sources/P3_C3/`; they are not included as public repository evidence. No paywalled claim is used. S7 is explicitly limited to the accessible preprint, making an additional human paper request unnecessary for this non-equivalence comparison. This audit is limited to the sources inspected; it does not assert that no closer implementation exists elsewhere.

Verbatim access failures retained here: the initial Oxford 2015 PDF route returned `Internal Error`; web opening `https://arxiv.org/html/2311.00664v1` and `https://arxiv.org/pdf/2002.08165v1` returned `Internal Error`; the AAAI PDF web route reported `Failed to fetch https://ojs.aaai.org/index.php/AAAI/article/view/16861/16668: (400) Timeout fetching`; ordinary retrieval of that AAAI PDF reported `HTTP Error 502: Bad Gateway`. The CVPR published PDF, NeurIPS published PDF and ordinary arXiv preprint retrieval respectively supplied the necessary primary methods. No credentials, paywall circumvention or spending was used.

Downloaded source hashes, identifying the versions actually read:

| Local source ID | SHA-256 |
|---|---|
| S1 published PDF | `86451bd6586237fc8216266d250d4bc53d47abd62f1e6eafb2b1eed960a45692` |
| S2 published main PDF | `f78975e59bce5279fa5e200b4bd9dce81d606039c53ddd3d2fa4929e5605319d` |
| S2 supplement | `3ad83d5f86123687d7ed5929bdbe718ae3f2462d83731182402927cdf52ecd2c` |
| S3 published PDF | `46f5eedab58093f2dd4e0470c34d8090ab440cb0d095b288a31ed031bcee6943` |
| S4 published PDF | `dd66054de2136f66fb06976e1c68d700db15cc5bb600a75a4cce2912ad63b61c` |
| S5 published main PDF | `934249a6e53e8782d41b72b1379ca151941a34c0474dc70e81d4fb71cfc502ce` |
| S5 supplement | `349e6ec56de6aaa0b4f118067a68c2062a4aaae25b98c5c2fc2ad489aa675a91` |
| S6 published PDF | `a42d38b52865dac4048eeb1300853b812916ffbcae63b58ef85df22913867c58` |
| S7 inspected preprint v1 | `70c9e813a5208cd334a4f7b5e30eb71c093803d2c690bf4278cf5908096036fc` |
| S8 published PDF | `6ee0e363a851db324b6ca1dfb6e6c7937b7a6f7019ff75a8092de569ba62834f` |
