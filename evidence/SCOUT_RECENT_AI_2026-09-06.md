# Phase 1 source scout: current AI, 2026-09-06

Status: bounded source map, not a diagnosis, systematic review, independent review, or completed current-literature sweep. Five primary studies were selected for inspection. Three fall inside the requested 2026-03-06 through 2026-09-06 window. Full-text methods and relevant results were opened; this does not claim every appendix, linked dataset, code repository, or supplementary video was read. No repair is proposed or selected here.

## Search and access record

Search date/access date for every URL below: **2026-09-06**. Initial searches were `site.arxiv.org 2026 "interactive" "unknown" "learning" agent March April May`, `site.arxiv.org 2026 "continual learning" "loss of plasticity"`, and `site.arxiv.org 2026 "compositional generalization" interactive agent`. Follow-ups sought the exact titles of AdA, Reflexion, and the Nature plasticity study. Search results were leads only. Calendar eligibility was checked against arXiv submission/version metadata, not search-engine relative dates.

The recent window was genuinely searched but coverage is incomplete: predominantly arXiv, no exhaustive proceedings sweep, no citation snowball to saturation, and no evidence of a representative sample of 2026 systems. Unselected search hits are not evidence. No benchmark fact sheet was sought or opened.

## A. Held-out dynamics and positive scaling evidence

**Bauer / Adaptive Agent Team et al. (2023), _Human-Timescale Adaptation in an Open-Ended Task Space_.** ICML 2023 proceedings, peer-reviewed. [Full paper](https://proceedings.mlr.press/v202/bauer23a/bauer23a.pdf). Accessed 2026-09-06. Read: §§2.1–2.4, 3.1; methods in E.4/G.8; reset and scaling details.

**Method:** XLand production rules can be visible or masked. Evaluation excludes training goal/rule combinations. Environment resets between trials; agent memory persists, then resets between episodes. Scores normalize against a task-fine-tuned reference.

**Score/observation:** More trials improve performance on over 80% of the test set. The fraction exceeding 0.8 normalized score rises from 40% at one trial to 72% at thirteen. Model-size scaling comparisons preserve memory depth; additional compute-matched analyses qualify the benefits. Human comparisons use 30 hand-authored tasks after a 23-task familiarization curriculum.

**Failure/cause boundary:** Some held-out tasks remain unsolved even after human demonstrations; distributional distance is suggested, not isolated experimentally. Positive adaptation and scaling results directly challenge universal incapacity claims. They establish neither arbitrary-world discovery nor retention after agent-memory erasure or prolonged interference. The reset boundary is part of the method, not an implementation footnote.

## B. Learning-efficiency deterioration, with scaling counterevidence

**Hernandez-Garcia, Figliolia & Millidge (2026), _Can Scale Save Us From Plasticity Loss in Large Language Models?_** **Preprint**, arXiv:2606.24752v1, submitted 2026-06-23. [Full text](https://arxiv.org/html/2606.24752v1). Accessed 2026-09-06. Read: §§III–V and experimental hyperparameters.

**Method:** GPT-style models span 5M–314M non-embedding parameters. Eight languages arrive in 5B-token blocks. Copies of successive checkpoints train on held-out Vietnamese; probe updates are discarded. The optimizer resets at task transitions. The outcome is validation-loss area under a fixed-budget probing curve.

**Score/observation:** Eventually worsening probing curves occur across tested sizes; larger models deteriorate later and initially benefit more from transfer. Stationary-mixture controls show deterioration in three smaller sizes.

**Failure/cause boundary:** This measures reduced adaptation efficiency, not disappearance of old knowledge, inability to update, or interactive world learning. Optimizer resets weaken a stale-state explanation. Parameter/dormancy measurements are correlates; the authors acknowledge no decisive cause. Their fitted sublinear onset relation is not evidence about frontier-scale limits outside the measured range. Scale helps materially inside the tested range even though it does not eliminate the observed effect there.

## C. Interaction-derived knowledge: benefit and contamination

**Zhang et al. (2026), _Training LLM Agents for Spontaneous, Reward-Free Self-Evolution via World Knowledge Exploration_.** **Preprint**, arXiv:2604.18131v1, 2026-04-20. [Full text](https://arxiv.org/html/2604.18131v1). Accessed 2026-09-06. Read: §§3–4.5, including evaluation and preprocessing.

**Method:** Training uses teacher exploration and downstream-task labels on 20 websites. At inference, interaction produces Markdown knowledge supplied to later task execution. Websites first receive graph-based preprocessing; known web actions and accessibility-tree observations constrain the setting. Evaluation filters pretrained-answerable questions and uses model judges on 1,427 questions.

**Score/observation:** For Qwen3-30B, WebWalker success is 22.04% without knowledge, 19.50% with base-model-generated knowledge, and 40.91% with the trained variant's knowledge (Table 1).

**Failure/cause boundary:** Lower performance with generated knowledge is consistent with harmful information, but does not isolate hallucination, compression, attention allocation, or exploration quality. Training, generated content, preprocessing and additional interaction are bundled. A headline claim of spontaneous learning must retain these scaffolding and supervision conditions. This is positive evidence for reusable interaction-derived information in this protocol; unknown physical dynamics, retention under interference, and novel recombination are not directly established.

## D. Generalization gain versus causal overinterpretation

**Yao et al. (2026), _Learning Generalizable Behaviors for Terminal Agents_.** **Preprint**, arXiv:2608.22631v2, revised 2026-08-26; v1 submitted 2026-08-23. [Full text](https://arxiv.org/html/2608.22631v2). Accessed 2026-09-06. Read: §§3.2–5.4; v1 initially opened, cited results checked against v2.

**Method:** Synthetic terminal-task training, four evaluation benchmarks, 64-turn budget; approximately 300 held-out tasks support domain-restriction comparisons. Trace-based skill annotations and behavior features support correlational analyses.

**Score/observation:** An 8B model's four-benchmark mean rises from 12.5±1.1 after SFT to 19.4±1.2 after the full training procedure (three seeds). RL on only Debug/System still improves other held-out domains. In separate runs, training reward increases while generalization degrades, accompanied by early termination. Repetition penalties improve performance; rewarding verification increases verification without additional performance gain.

**Failure/cause boundary:** Interventions provide more leverage than behavior-success correlations, but do not uniquely identify the latent cause. A failed verification intervention does not prove verification causally irrelevant. Domain holdouts and trace co-occurrence do not establish a controlled novel-combination split; pretrained skill exposure remains relevant. Different baseline harnesses also limit headline attribution.

## E. Retention across retries, carefully bounded

**Shinn et al. (2023), _Reflexion: Language Agents with Verbal Reinforcement Learning_.** NeurIPS 2023 proceedings, peer-reviewed. [Full paper](https://proceedings.neurips.cc/paper_files/paper/2023/file/1b44b878bb782e6954cd888628510e90-Paper-Conference.pdf). Accessed 2026-09-06. Read: §§3–4.1, algorithm, memory/reset procedure, ALFWorld results.

**Method:** Both arms retry ALFWorld environments. The experimental arm retains the last three textual reflections after reset; the baseline restarts without reflection. Two domain-specific demonstration trajectories are supplied. A heuristic triggers reflection/restart after repeated action/observation cycles or more than 30 actions.

**Score/observation:** 130 of 134 tasks are solved cumulatively across twelve trials. Baseline trajectories sometimes proceed as though an unacquired object is possessed; the paper attributes many failures to this mismatch and inability to backtrack.

**Failure/cause boundary:** The relevant contrast bundles retained content and an additional inference procedure. The reported success is cumulative retry performance, not first-attempt success or transfer to a new composition. Environment reset is survived because textual state is deliberately preserved. This supports a narrow possibility claim about learning from retries; it does not measure retention through intervening unrelated learning, content corruption, or loss of the preserved state. The causal failure labels rely substantially on trajectory interpretation.

## Questions this source map exposes

These are measurement distinctions to carry into diagnosis, not proposed repairs:

- What exactly is unknown: state, transition rule, reward, object identity, action semantics, or a future task demand?
- Which state survives a discontinuity: environment state, context, external records, weights, optimizer, or none? A successful trial reset can leave the relevant information channel intact.
- Does a reported improvement measure first-attempt performance, final-trial performance, cumulative success after retries, or speed of further training?
- Is novelty an excluded domain, an excluded rule combination, or an unmeasured claim about distance from pretraining?
- Does a failure label come from a score, inspected trajectories, a representation probe, or a matched intervention? What competing cause survives the same evidence?

An adequate review still needs direct longitudinal old-knowledge retention studies and stronger controlled novel-recombination tests, alongside broader 2026 coverage. These five papers alone cannot support a conclusion about the whole acquisition–retention–recombination category.

## Access limitations and human paper requests

No current source-dependent claim requires a human retrieval request: full-text methods for all five selected studies were accessible. Two unsuccessful opens are recorded in `evidence/SCOUT_RECENT_AI_ERRORS.jsonl`: the Nature plasticity article and an attempted arXiv HTML version. No method-dependent argument here relies on either. This is not a claim that university access will be unnecessary later.
