# Controlled recombination: methods and competing explanations

Phase 1 evidence pass, 2026-09-06. This is a bounded source analysis, not a proposal or independent review. The reader shared the programme's tools and filesystem. No experiment was run. No architecture is endorsed. The five studies below concern restricted computational demands; their results do not establish a general AI–human ordering.

## Source and reading scope

Every URL below was accessed **2026-09-06**. Publication status describes the work; an author-deposited arXiv version is identified separately from the proceedings version. Reading coverage is stated rather than implying complete proof or implementation audits.

| ID | Primary full-method source and status | Material examined |
|---|---|---|
| C1 | Kim & Linzen, [COGS, EMNLP 2020](https://aclanthology.org/2020.emnlp-main.731.pdf), published | Dataset construction, §§3–5 and 7; appendices A–E, G–H; per-case results. Full PDF available; no code audit. |
| C2 | Lake & Baroni, [Human-like systematic generalization through a meta-learning neural network, Nature 2023](https://www.nature.com/articles/s41586-023-06668-3), published | Main results and complete online Methods, including human exclusions, training grammar exclusion, benchmark permutation and support-selection procedures. Supplement-only novel-rule results are not relied on. |
| C3 | Ruis et al., [gSCAN, NeurIPS 2020 main paper](https://proceedings.neurips.cc/paper_files/paper/2020/file/e5a90182cc81e12ab5e72d66e0b46fe3-Paper.pdf) and [supplement containing the appendix PDF](https://proceedings.neurips.cc/paper_files/paper/2020/file/e5a90182cc81e12ab5e72d66e0b46fe3-Supplemental.zip), published | Main task, baselines and split analyses; complete appendix A–F, including world generation, augmentation effects, forward equations and hyperparameters. No code executed. |
| C4 | Redhardt, Akram & Schug, [Scaling can lead to compositional generalization, NeurIPS 2025](https://papers.nips.cc/paper_files/paper/2025/file/5047b64366bc0dbf5047de85f1e0c7be-Paper-Conference.pdf), published; [author arXiv v2](https://arxiv.org/html/2507.07207v2), 2025-10-23 | §§2–4, limitations and appendix C.1–C.6. Theorems' assumptions and conclusions examined, not independently proved. Core claims below concern the synthetic hyperteacher experiments, not the separately defined preference-grid family or text-to-image extension. |
| C5 | Tong et al., [Generalization in LLM Problem Solving: The Case of the Shortest Path, author arXiv v1](https://arxiv.org/html/2604.15306v1), 2026-04-16; [ICLR 2026 proceedings listing](https://proceedings.iclr.cc/paper_files/paper/2026), published conference work | §§2–7 and appendices A, D.1–D.5; inference settings and pretraining controls. The math extension is outside this note's conclusions. OpenReview's full page required browser verification; the author fulltext was accessible. |

**Recent window:** C5's April 2026 deposited version falls within 2026-03-06 through 2026-09-06. This does not establish that its findings first became public within that window: earlier OpenReview submission timing was not established here. C4 is a 2025 result, despite some search metadata displaying 2026. None of these five works should be labelled an unreviewed preprint merely because an arXiv copy was read.

## What the controlled contrasts establish

### C1 — COGS: successful fitting leaves transfer underspecified

**Setup/state:** Transformer/LSTM models train from scratch on supplied sentence–logical-form pairs; no web pretraining or active interaction. Grammar-generated holdouts change lexical roles, phrase placement or embedding depth. Weights survive; no longitudinal memory interruption is tested.

**Score and observation:** In-distribution performance is near-perfect while structural transfer is near zero; some lexical cases, notably active-to-passive, succeed. Increasing primitive exposure helps lexical transfer. The tested parameter increase alone does not reliably help. This limited sweep cannot establish a scaling ceiling.

**Attribution:** Authors suggest a “stronger structural bias.” Their error analysis rules out wrong variable indices as the sole explanation: premature stopping dominates depth errors. It does not causally isolate missing structure from a learned length prior or optimization. The experimenter supplies lexical meanings, output variables and a restricted grammar; selecting useful rules from examples remains learned. Human performance on exactly these holdouts is not directly measured. [C1, §§4–5, appendices D–H](https://aclanthology.org/2020.emnlp-main.731.pdf), accessed 2026-09-06.

### C2 — MLC: training support changes the answer, but does not remove every boundary

**Setup/state:** Frozen test weights process supplied support pairs alongside the query. Training grammars exclude the human-test grammar even under symbol remapping. Benchmark episodes use training-corpus support; COGS support deliberately overlaps query vocabulary. Lexical classes and a small semantic remapping rule are supplied. Human study items remain visible; this is not retention across clearing.

**Score and observation:** Lexical SCAN/COGS transfer becomes strong, while SCAN length and COGS structural splits still fail. Copy-only training provides a useful within-architecture contrast. Human-like error frequencies are partly training targets, not wholly spontaneous predictions.

**Attribution:** “optimized for their compositional skills” is supported as a training-regime effect. It does not prove that the network autonomously discovers the curriculum, ontology or useful evidence. COGS success is not wholly structure-free. Comparisons change objective/support use together, so they do not identify a unique internal cause. This is training-distribution counterevidence to architectural impossibility, not a clean model-size scaling experiment. [C2, Methods and benchmark results](https://www.nature.com/articles/s41586-023-06668-3), accessed 2026-09-06.

### C3 — gSCAN: grounding does not imply interactive discovery

**Setup/state:** Supervised instruction-to-action prediction receives the initial full grid as one-hot colour, shape, size and agent channels. The agent does not select observations or acquire the ontology. A fixed learned model generates each sequence; no across-task retention interruption is imposed.

**Score and observation:** Random-split execution and heavy-object push/pull transfer succeed; relative-size references, withheld direction combinations and longer outputs fail. Thus familiar-primitive availability alone does not predict every held-out relation.

**Attribution:** Authors describe a “complete failure of genuinely understanding ‘small’.” Near-chance selection and attention concentrated away from the target support a reference-resolution symptom, not a causal proof that no usable size relation is encoded. Attention is observed, not intervened on. The supplement shows that augmentation alters which objects and references occur; its gains and regressions are not a pure intervention on an abstract ability. More adverb demonstrations help little in the tested range; frontier-scale or comprehensive data-scaling conclusions are unavailable. [C3 main §§3–5](https://proceedings.neurips.cc/paper_files/paper/2020/file/e5a90182cc81e12ab5e72d66e0b46fe3-Paper.pdf), [appendix](https://proceedings.neurips.cc/paper_files/paper/2020/file/e5a90182cc81e12ab5e72d66e0b46fe3-Supplemental.zip), accessed 2026-09-06.

### C4 — scaling succeeds under controlled support

**Setup/state:** Synthetic teachers compose known experimental modules into regression functions. Students receive inputs plus task encodings, including nonlinear encodings and examples. Task combinations are withheld. Training uses fresh labelled samples, not online world exploration; learned weights survive unchanged into evaluation.

**Score and observation:** Increasing model size and distinct training tasks improves held-out composition. Absent or disconnected module support impairs it; rare-module exposure matters more than imbalance alone. These are substantial positive scaling findings in the specified task family.

**Attribution:** Authors suggest success “depends on linear representations of compositional structure.” Hidden-state decoding is correlated with performance, not a causal intervention or proof of linear necessity. The existence theorem establishes representability, not that SGD finds the solution; its learning guarantee remains open. Tested encodings do not establish success for every information-preserving encoding. Under disconnected support, alternative teachers can agree during training but disagree later: some failure is non-identification, not deficient recombination. [C4 §§2–4, limitations, appendix C](https://arxiv.org/html/2507.07207v2), accessed 2026-09-06.

### C5 — a recent positive transfer result has an essential pretraining boundary

**Setup/state:** Small LLaMA-style models first train on random walks over **all training and test maps**. Shortest-path SFT uses one map; evaluation supplies endpoint identifiers. Graph semantics survive in weights. “Unseen maps” means unseen in shortest-path training, not never encountered. No agent-driven discovery or memory clearing is tested.

**Score and observation:** Spatial transfer succeeds; longer paths degrade even conditional on separately solvable subpaths. Training-data allocation affects transfer. Tested RL and ten-sample inference improve some behaviour without eliminating length failure.

**Attribution:** Authors call this “recursive instability.” Conditional subpath analysis narrows the symptom but does not intervene on internal recursion. The distance probe is nonlinear and observational. Failure of the pretrained policy to generate shortest paths does not prove absence of useful shortest-path information. Adding examples beyond the target length removes that target's original extrapolation condition. These results constrain particular training/inference budgets; they establish neither a frontier-LLM ceiling nor impossibility of further scaling. [C5 §§2–7, appendices A and D.1–D.3](https://arxiv.org/html/2604.15306v1), accessed 2026-09-06.

## Competing falsifiable explanations

The following are **our diagnostic hypotheses and deductions**, not additional reported findings or selected programme mechanisms. They concern different causal stages; none is yet ranked globally.

| Claim | Evidence relation | What would refute or narrow it? | Unchecked prediction and confidence |
|---|---|---|---|
| **H1: Some withheld combinations are not identified by available evidence.** Distinct allowed generating rules agree on every permitted observation yet disagree on the test. | C4 supplies a restricted theoretical example. Merely listing every primitive is not an identification argument. | Exhibit a permitted observation/intervention that separates the proposed equivalent worlds; then the problem was failure to obtain/use evidence, not impossibility. | When the allowed world family is widened, apparent transfer may become prior-dependent. High confidence as a conditional deduction; prevalence unmeasured. |
| **H2: At fixed representational capacity, training rewards can select a predictor tied to local co-occurrences instead of relations stable across the intended substitutions.** | C1–C2 support sensitivity to support and objective. C4 prevents treating this as an immutable property of neural representations. | With identifiable evidence and adequate optimization, controlled changes to the relevant co-occurrences/objective have no effect, while a different isolated factor explains failures. | A held-out substitution may fail while an equally rare but training-aligned substitution succeeds. Moderate confidence in these task classes; internal implementation unresolved. |
| **H3: Some composition failures occur during use: local answers remain available but the longer decision process fails to select, bind or maintain their applicability.** | C3 and C5 motivate this, but do not uniquely localize it. The explanations include stopping, target selection, binding and state tracking; the current evidence does not choose among them. | Instrumentation shows that the needed local relation was never represented or becomes unavailable before the composite decision; or all excess failure is explained by measured local error. | Performance can diverge between separate local queries and the full query despite identical stored weights. Moderate confidence in the distinction; low confidence in any single internal cause. |
| **H4: The measured endpoint partly reflects an interface or scoring constraint rather than loss of task competence.** | Exact sequence output, valid-path and functional-goal criteria need separation. This is a competing explanation, not permission to dismiss the benchmark. | Task failure remains under a semantically appropriate evaluator and after inspecting the emitted state/trajectory, without supplying new task knowledge. | Error categories should separate invalid actions, wrong referents, non-optimal valid paths and premature termination. Moderate methodological confidence; explanatory share unresolved. |

The conjunction matters. H1 concerns whether sufficient evidence exists; H2 concerns which rule learning selects; H3 concerns whether the resulting state supports the required use; H4 concerns what the reported measurement actually detects. Renaming all four as “plasticity” would conceal distinct refuters. Conversely, any argument that current AI simply cannot recombine, or that scaling cannot help, is already too broad for C2 and C4.

## Remaining limits and paper requests

No paywall blocks the bounded claims above, so no new human paper request is required. The detailed preference-grid generator in C4, causal interventions on learned binding/selection, matched human performance on the exact C1/C3 holdouts, and genuinely unknown-world recombination remain unassessed. C5's first-publication chronology and code-level interpretation of its sampling selector remain unresolved. Do not treat the absence of those audits as negative evidence.

Retrieval errors and recovery are recorded in `evidence/P1_COMPOSITION_TOOL_ERRORS_2026-09-06.jsonl`. Public source PDFs/HTML were downloaded only to `tmp/composition_sources/` for reading; those raw third-party documents are not programme evidence artifacts to publish wholesale. The reproducible claim record is this note with pinned URLs, version dates and reading scope.
