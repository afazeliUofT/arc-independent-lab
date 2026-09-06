# Retention, access and continued trainability: methods pass

Date: **2026-09-06**. Phase 1 evidence, not a completed diagnosis or independent review. This consultation shares tools and filesystem with the PI. It proposes no repair and ranks no candidate mechanism. Earlier source notes remain unchanged.

The evidence supports distinguishing three failures: a previously useful response becomes unavailable; the information needed for that response is no longer recoverable under a specified intervention; and subsequent learning becomes less effective under a specified budget. These are different empirical claims. Calling all three “forgetting” would prevent causal attribution.

## Scope, versions and reading coverage

All URLs below were accessed **2026-09-06**. The requested recent window is **2026-03-06 through 2026-09-06**, inclusive. Two selected preprints were first submitted inside that window. This is a purposive methods pass, not a systematic or representative sample of current AI.

| ID | Primary study and version | Window | Reading coverage supporting this note |
|---|---|---|---|
| R1 | Dohare et al., *Loss of plasticity in deep continual learning*, Nature 632, 768–774 (2024), published article. [DOI](https://doi.org/10.1038/s41586-024-07711-7); [full published text at PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11338828/) | Outside | Main findings and limitations; full ImageNet, CIFAR-100 and permuted-MNIST methods; relevant representation diagnostics and extended discussion. Not a code audit or a full audit of every RL run. |
| R2 | Zheng et al., *Spurious Forgetting in Continual Learning of Language Models*, ICLR 2025. [Published paper](https://proceedings.iclr.cc/paper_files/paper/2025/file/a774503daed55eb53c634847ae071ec7-Paper-Conference.pdf); [preprint v1](https://arxiv.org/html/2501.13453v1), 2025-01-23 | Outside | Published §§3.1–3.2 and Figure 2 checked against preprint; preprint §§3–4, appendices B–E and relevant G/H details. No assertion that every appendix or proof has been audited. |
| R3 | Hernandez-Garcia, Figliolia and Millidge, *Can Scale Save Us From Plasticity Loss in Large Language Models?*, **preprint** [arXiv:2606.24752v1](https://arxiv.org/html/2606.24752v1), 2026-06-23. [Version record](https://arxiv.org/abs/2606.24752) | Inside | §§III–V, Appendix A training/architecture details, Appendix B onset estimation and fit, Appendix C diagnostic qualifications. |
| R4 | Asawa et al., *Continual Learning Bench: Evaluating Frontier AI Systems in Real-World Stateful Environments*, **preprint** [arXiv:2606.05661v1](https://arxiv.org/html/2606.05661v1), 2026-06-04. [Version record](https://arxiv.org/abs/2606.05661) | Inside | §§3–6, relevant task descriptions, per-task tables, Appendix C gain decomposition and Appendix D inspected examples. No external leaderboard or raw-log audit. |
| R5 | Lyle et al., *Disentangling the Causes of Plasticity Loss in Neural Networks*. [PMLR 274 publication record](https://proceedings.mlr.press/v274/lyle25a.html), 2025, for CoLLAs; inspected **preprint** [arXiv:2402.18762v1](https://arxiv.org/html/2402.18762v1), 2024-02-29 | Outside | Preprint §§2.2–3.3; Appendix B architecture, supervised and bandit protocols; D.1/D.4; E.1; F. Published-version equivalence is not assumed. |

Searches sought loss of plasticity, retained representations, spurious forgetting, recent language-model continual learning and frontier stateful evaluation. Citation follow-up selected R5 because a causal diagnosis needs more than ageing-correlate measurements. Full-text source access, rather than abstract availability, determined inclusion. No benchmark fact sheet was opened.

## R1 — past training can harm later fitting despite old data availability

**Method/state/reset:** ImageNet becomes sequential binary classifications; the trunk survives while output weights reset at boundaries. Each task uses 250 training epochs. In CIFAR-100, classes arrive incrementally, but all previously available training images remain accessible. ResNet-18 weights carry forward from the previous increment's best validation checkpoint; new outputs are added. A fresh network trained on the same available classes is the comparison.

**Score/failure:** Incremental CIFAR training initially helps, then eventually finishes about five percentage points below fresh training. This is deterioration relative to an increasingly difficult matched problem, not simply a falling raw score.

**Attribution:** Old-example unavailability cannot alone explain that comparison. Dormancy, representation rank and weight magnitude accompany deterioration; they do not uniquely identify its cause. The authors distinguish optimization failure from generalization failure and explicitly state that their plasticity method does not address forgetting.

**Contrary evidence:** Early transfer is beneficial, larger MNIST networks deteriorate less, and some tested variants maintain later-task performance. “Deep learning cannot continue learning” is therefore too broad. [R1, methods and extended discussion](https://pmc.ncbi.nlm.nih.gov/articles/PMC11338828/), accessed 2026-09-06.

## R2 — poor ordinary answers can coexist with recoverable old associations

**Method/state/reset:** A model trained from scratch learns synthetic biographies, then question answering, then new people's facts. Weights survive sequential training. Recovery starts from intervening checkpoints, trains on half the old task data for one epoch and tests the other half; it does not restore the old checkpoint.

**Score/failure:** Old-task first-token performance drops from near-perfect to roughly 10% early in new-task fitting, whereas recovered exact-match performance remains near-perfect and reaches roughly 96% after longer interference. These are different metrics, not an exactly matched percentage-point improvement.

**Attribution:** The authors say “loss of task alignment instead of underlying knowledge.” Recovery on withheld associations supports substantial surviving information, conditional on the synthetic split. Weight-angle and principal-component observations, plus a simplified residual-linear theory, do not uniquely establish the Transformer-level cause.

**Alternative/limit:** Recovery uses considerable old supervision and further parameter learning. It establishes neither autonomous access nor recovery without old data. Appendix C also specifies question-answer training on a subset of pretrained people, qualifying the main-text shorthand. [R2, §§3.1–3.2](https://proceedings.iclr.cc/paper_files/paper/2025/file/a774503daed55eb53c634847ae071ec7-Paper-Conference.pdf), [appendices C–E](https://arxiv.org/html/2501.13453v1), accessed 2026-09-06.

## R3 — scale delays measured deterioration; its eventual limit is unresolved

**Method/state/reset:** Eight-language training cycles update GPT-style weights. Optimizer state and learning-rate warmup reset between tasks. Checkpoint copies receive a fixed Vietnamese training budget; those probe updates are discarded. Models span 5M–314M non-embedding parameters. The outcome is validation-loss area under the probing curve.

**Score/failure:** Later checkpoints eventually have worse probing curves; larger models benefit more initially and deteriorate later. Small stationary-mixture controls also deteriorate.

**Attribution:** Stale optimizer state and abrupt task changes are insufficient as sole explanations. Authors acknowledge that the measured internal correlates do not yield a decisive cause. This is adaptation efficiency, not old-fact erasure.

**Scaling qualification:** Onset is a smoothed empirical minimum, with probing locations selected to reduce preceding-language transfer variation. The fitted exponent is 0.8269, standard error 0.1027. **Our statistical inference:** a conventional two-sided interval includes exponent one. Thus the point estimate alone does not establish sublinear scaling. Neither this fitted range nor cross-paper extrapolation settles frontier-scale limits. Probe-budget sensitivity and changing transfer remain alternatives to a universal loss of trainability. [R3, §§IV–V and Appendix B](https://arxiv.org/html/2606.24752v1), accessed 2026-09-06; **preprint**.

## R4 — accumulated experience helps, but a boundary score does not diagnose storage

**Method/state/reset:** Six domains compare stateful and stateless operation on matched instances. Survivors include conversation history, notes or retrieved records; some harnesses compact context. The study tests contextual adaptation, not weight updates. Sequences include changed variants.

**Score/failure:** Sonnet 4.6 with full-context learning reaches 25.4% normalized gain. This is a fraction of baseline headroom, not task success. Results vary by domain; an inspected cohort-study trace fails to apply previously observed cross-study information.

**Attribution:** The authors label first-instance-of-variant gain “stability” and subsequent gain “plasticity.” **Our inference:** these partitions localize reward in a schedule, not a causal process. A new variant may require different inference even with intact memory. Poor boundary gain cannot identify erasure; positive within-variant gain may use older information too.

**Contrary evidence/limits:** Retained context produces clear gains in several domains; specialized memory systems do not consistently dominate it. Context reduction, retrieval selection, content accuracy and reasoning are bundled. The trace supports nonapplication of prior evidence but not its unique cause. [R4, §§4–6 and Appendices C–D](https://arxiv.org/html/2606.05661v1), accessed 2026-09-06; **preprint**.

## R5 — controlled changes to the learning problem can alter later trainability

**Method/state/reset:** Sequential image-label tasks retain weights. Suddenness is varied while matching total label-change quantity. Another experiment varies the constant offset of regression pretraining targets before fitting new targets. Bandit probes use a fresh optimizer and checkpoint-relative targets; the behaviour policy is uniform, reducing exploration confounding.

**Score/failure:** Larger offsets impair later optimization; abrupt label changes are more damaging. Some degraded curves are shallower rather than demonstrably trapped at higher asymptotes.

**Attribution:** These controlled manipulations support causal effects of task construction within the tested setting. They do not prove a unique mediator. The authors' “independent” mechanisms mean one can remain when another is mitigated, not statistical independence or absence of interactions.

**Contrary evidence/limits:** Gradual changes and increased width can preserve more trainability; effective linearization can matter even where gradients remain nonzero. A single dead-unit count is insufficient for a universal explanation. The regression text names MNIST in §3.1 and CIFAR-10 in Appendix E.1; image identity needs code/version resolution if that distinction becomes consequential. [R5, §§2.2–3, Appendices B, D–F](https://arxiv.org/html/2402.18762v1), accessed 2026-09-06; inspected **preprint**.

## Diagnostic implications: deductions to test, not new empirical findings

These implications constrain the eventual diagnosis. They do not select a repair, demand a particular representation, or establish prevalence beyond the reviewed protocols.

**1. A storage-loss claim needs a declared class of recovery operations.** With an unrestricted decoder, the analyst could smuggle the answer into its parameters. With no alternative decoder, a failed default response cannot distinguish erased information from an inaccessible readout. A useful claim must constrain the decoder's information, supervision, computation and state changes. The appropriate target is whether historical distinctions still influence possible future decisions under those restrictions.

**Falsifier for an access-only explanation:** recovery that cannot see withheld historical associations performs no better from the supposedly informed checkpoint than from a matched checkpoint that never saw them, while a positive acquisition control verifies the association is learnable. This would weaken access-only attribution for that probe class. It would not prove absence under every conceivable computation. Conversely, successful recovery establishes a surviving channel; it does not prove that every historical detail survived.

**2. Loss of plasticity is a budget-relative property.** Given a fixed training budget, a checkpoint may be a worse starting point even if the model class still contains an adequate solution. That can be scientifically and operationally serious without being irreversible. Endpoint error, learning-curve slope, initial error, asymptotic error and generalization should not be merged into one unexplained score.

**Falsifier for a claimed inability to optimize:** when initial prediction error and update budget are controlled, the alleged deficit disappears, or sufficient further fitting reliably reaches the earlier attainable training error. The latter refutes permanent inability but leaves a finite-budget efficiency deficit intact. A validation-only deficit also permits a generalization explanation, which differs from inability to fit.

**3. Retaining examples and retaining a competent learner are distinct demands.** Availability of all old evidence does not logically ensure that a particular updater will fit it or use it appropriately. Conversely, an old fact cannot be required to remain useful when the environment has genuinely invalidated it. Data availability, state preservation, world validity and action relevance belong on separate causal paths.

**Falsifier for absence-of-evidence as the sole explanation:** a deficit persists with the relevant evidence explicitly available to both compared systems and enough budget to inspect it. Such a finding would still leave optimization, inference, attention allocation and incorrect interpretation open. It would not justify relabeling any one of those as the established cause.

**4. Changing a task can change both the desired answer and the optimization difficulty.** An experimentally innocuous transformation of target scale or presentation schedule need not be innocuous to the learner. The funded question concerns unknown worlds, but an observed failure may originate in a supplied training objective before world structure is ever inferred. The acquisition and learning-update accounts therefore require separate tests.

**Falsifier for a task-construction explanation:** the claimed sensitivity survives when the implicated property is held fixed across successful and unsuccessful histories, with a verified manipulation check. A correlation between two quantities that both drift with training time is particularly weak evidence for mediation.

**5. A scaling claim must name what is scaled and what remains fixed.** Extra parameters, more training tokens, a longer context, more test-time computation and broader task diversity are different interventions. Finite-horizon success is not indefinite retention; finite-horizon deterioration is not proof that scaling can never defer the problem beyond a useful horizon. Cross-model vendor comparisons are not controlled parameter-scaling experiments.

**Falsifier for a specific forecast:** held-out model sizes or training horizons systematically violate the preregistered onset prediction under the same protocol. Failure of one fitted law does not itself establish a plateau-free alternative. No extrapolation here licenses a claim that 2026 frontier systems inevitably fail the whole funded category.

## Relation to the lab's reproduction and remaining evidence gap

The existing lab witness constrains what behavioural decline alone establishes. R2 provides a distinct, substantially larger empirical recovery procedure whose extra supervision must stay visible. These do not share a proven cause. R1/R3/R5 concern the quality of later learning, a different object from the old-readout question. R4 combines evidence acquisition, preserved contextual state and decision making, but its outcome decomposition cannot isolate these processes.

The bounded pass therefore strengthens a **measurement distinction**, not a unifying biological or computational mechanism. We still lack an integrated, controlled longitudinal demonstration that traces acquired world knowledge through an explicit discontinuity, intervening learning and a genuinely held-out reuse demand in the same strong system. None of these papers alone meets that conjunction. This is an evidence gap, not evidence that no such system exists.

## Access and unresolved-method record

The Nature publisher route and web-reader PMC route failed, but ordinary HTTPS retrieval recovered the full published PMC article. It is not paywalled evidence and does not need another human paper request. OpenReview's browser challenge was resolved for R2 through the official ICLR proceedings PDF. R5's accessible preprint supplies the bounded methods claims; publication identity is recorded separately until the final PDF is checked.

Failures and their reported messages are in `evidence/P1_RETENTION_METHODS_ERRORS_2026-09-06.jsonl`; missing exit codes are left null. Locally extracted full texts under `delivery/retention_source_text/` are reading intermediates, not evidence to include in the public checkpoint. No paid or authenticated source access was attempted. No immediate human paper request is required by the claims in this note; a version-specific R5 claim or the unresolved dataset-identity distinction would require resolving the published source/code before relying on it.

### Addendum: R5 published-version check completed, same date

After the note above was written, ordinary HTTPS retrieved the [official PMLR-linked PDF](https://raw.githubusercontent.com/mlresearch/v274/main/assets/lyle25a/lyle25a.pdf), accessed 2026-09-06. It identifies itself as **CoLLAs 2024**, while the PMLR bibliographic year is **2025**. Published §3.1 and Appendices C.2–C.3, F.1 and G were checked. This resolves the access limitation above, not every version difference.

The offset, task-change, fresh-optimizer probe and independence qualifications remain supported. The published text explicitly says even gradual relabelling produces decline, sharpening the preprint's “minimally interferes” wording. The differing MNIST/CIFAR descriptions remain. Thus gradual change is a relative success condition, not evidence that deterioration disappears. No additional paper is requested.
