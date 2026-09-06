# Recent integrated agents: what persists, what transfers, and what remains unidentified

Phase 1 methods consultation, **2026-09-06**. Shared tools and filesystem; not an independent review. No experiment, candidate repair, or novelty screening. This bounded pass deliberately sought positive experience-derived results as well as failures. It does not estimate prevalence across contemporary agents.

Three selected studies were first submitted within **2026-03-06 through 2026-09-06**. All are **preprints**, all inspected at **v1**, and every linked source was accessed **2026-09-06**. The arXiv submission records establish chronology; no later publication is inferred from search metadata. The following capsules are deliberately compact; the coverage record identifies the underlying methods actually examined.

## 1. Primary evidence and state inventory

### I1 — Hu, Long and Wang, April 29, 2026

[*When Continual Learning Moves to Memory: A Study of Experience Reuse in LLM Agents*, full methods](https://arxiv.org/html/2604.27003v1); [submission record](https://arxiv.org/abs/2604.27003).

Frozen Qwen-Plus/ReAct acts in named ALFWorld/BabyAI tasks. External records survive episode changes and two 200-instance phases; 100-instance held-out probes assess each family. Successful and unsuccessful trajectories enter memory. BM25 retrieves top-one raw episodes or distilled guidance. Neither unknown action semantics nor controlled novel relational arrangements are established. Two runs support reported means.

ALFWorld raw-memory adaptation falls from 80.5% without the earlier family to 71.0% with it; distilled-memory transfer instead improves. Actual traces illustrate an omitted cleaning operation. Backward outcomes include preservation and improvement, not uniform forgetting. Appendix C explicitly acknowledges that retrieval-frequency conditions also accumulate different memory content; approximately equal insights per retrieval do not match total computation. No state-restoration intervention isolates a sole retrieval cause. Exact Qwen-Plus snapshot, prompt priors and per-instance reset implementation remain unaudited.

**Coverage:** §§2–3; relevant §4 definitions; Appendices A–F, including memory contents, admitted confounding and case analyses. No released-code or raw-log audit.

### I2 — Zhang and colleagues, April 19, 2026

[*SkillFlow: Benchmarking Lifelong Skill Discovery and Evolution for Autonomous Agents*, full methods](https://arxiv.org/html/2604.17308v1); [submission record](https://arxiv.org/abs/2604.17308).

Native terminal agents carry initially empty skill files/scripts through 8–9-task families; libraries reset between families. Actions inspect and edit supplied files. Post-task verifier rubrics and failed-test feedback supervise patches. Domains, formats and constraints vary while workflow topology stays fixed; heterogeneous interference is deliberately excluded. Exact per-task context-reset implementation remains unaudited.

Opus 4.6 completion rises 62.65%→71.08%; some other systems regress. Cross-model harnesses and total patch-generation computation are not matched. Appendix C.2's history-only control is numerically inconsistent: prose 47.41%, table 51.04%; neither value should be silently selected. The inspected trajectory finds no task-specific test file and reads its own skill's checker; this is not demonstrated hidden-test leakage. It also shows executable repair after formula corruption. Reported endpoint failures can concern verifier/toolchain compatibility rather than erased knowledge.

**Coverage:** §§2–3; Appendices A.5–A.7, B.2, C.1–C.2, complete displayed D.2 trajectory and D.3 failures. Full generated helper code in D.1 was not audited.

### I3 — Yang and colleagues, August 2, 2026

[*PATH-Bench: Path-Dependent Evaluation of Lifelong Agents*, full methods](https://arxiv.org/html/2608.01149v1); [submission record](https://arxiv.org/abs/2608.01149).

Frozen DeepSeek-V4-Flash agents retain external memories/skills across code-generation or multi-turn tool tasks. An unchanged probe is repeatedly evaluated without adding its outputs to memory. Five helpful warm-up tasks precede a 100-task intervening queue. Histories are selected using multi-model demonstration effects; this does not specify held-out causal composition. Exact tool priors, feedback exposure and per-task state reset require implementation inspection.

Results include positive transfer and declining probe performance. Negative-dominant histories degrade code probes more consistently than tool probes; the latter distinction is an explicit counterexample to uniform interference. Harnesses share a backbone but not equal computation. An added memory-processing call changes content and computation; it is not a clean causal isolation. Published forgetting and backward-transfer metrics separately clip negative and positive differences from the post-warm-up score. Storage survival is not verified by endpoint scores.

**Coverage:** §§3–4; Appendices A–F, including relationship validation, tool-domain counterevidence and exact added-call prompt. No code or raw-trajectory audit.

## 2. What follows for the diagnosis

The following are this consultation's methodological deductions and judgments, not additional measurements or the authors' claimed causes.

**The first-ranked claim must be scoped by the updated state.** Parameter-update disruption and changes to a memory collection are different interventions. A frozen backbone can rule out the former in a particular run while leaving the latter active. It does not follow that information survived simply because a system labels its files “memory.” To establish survival, the relevant record or recoverable relation must still be identified. To establish use failure, one must then locate where that identified information ceases to affect action. These papers provide stronger integrated symptoms than a one-shot benchmark, but their endpoint comparisons do not complete that causal chain.

**A good transfer score and a good retention score need not refer to the same fact.** A history may improve a held-out probe through a general strategy without ever storing the answer to that exact probe. Later decline would then concern loss of an acquired advantage, not necessarily erasure of an acquired world-specific relation. Conversely, learning a useful relation from another task is legitimate acquisition; requiring direct exposure to the eventual answer would define transfer out of existence. The correct demand is to identify what the earlier evidence contributed and what later test requires.

**Novel arrangements cannot be inferred from a new domain label.** Reusing an operational relation with changed entities can be meaningful transfer. It does not automatically test changed dependency topology or the discovery of a new relation. A paper that deliberately preserves topology is useful positive evidence for its intended subclass. It should narrow a broad impossibility claim, while leaving the broader composition question open.

**The readout distinction remains useful, but is not yet a dominance result.** The retrieved evidence is compatible with impaired access, inappropriate content, an invalid generalization, failure to execute a correct plan, and evaluator mismatch. Declaring all of these “knowledge survived but use failed” would turn the leading claim into an unfalsifiable umbrella. The falsifiable version requires a specific surviving distinction and a specified operation that ceased to express it. Current confidence should increase in the need for that distinction, not in a universal mediator.

**Positive results matter even when feedback is supplied.** The relevant comparison is not whether a human designed the environment or provided any feedback; all informative worlds impose structure. The question is whether that feedback already contains the relation whose discovery is being credited. A task instruction, an environmental response, a retrospective failure description and a full worked solution carry different information. Their provenance must be recorded separately. Real gains after declared feedback already refute the unrestricted claim that a frozen LLM agent cannot improve from experience.

## 3. A metric deduction that needs no new experiment

Let an unchanged agent's independently measured reference and later scores be Bernoulli variables \(X,Y\) with identical success probability \(p\). There is no learning or forgetting. Nevertheless,

\[
\mathbb E[\max(0,X-Y)] = p(1-p)>0 \qquad (0<p<1).
\]

The complementary positive-change metric has the same expectation. Thus a positive one-sided decline statistic alone can arise from sampling variation. Averaging repetitions reduces this issue but does not logically eliminate it. This is an illustrative mathematical null, not an estimate of bias in I3's reported values: its actual score aggregation, dependence and task mixture must be reconstructed before quantification.

Signed changes, task-matched uncertainty and a no-update reference are therefore needed to interpret an apparent decline. This does not invalidate genuine negative signed trends or controlled history effects. It prevents interpreting every positive clipped “forgetting” value as evidence that knowledge was lost. The distinction is particularly relevant when warm-up ability is an estimated quantity and when experiments select tasks with measurable headroom.

## 4. Remaining uncertainties and access record

The pass did not find a source establishing all of: acquisition of the decision-relevant unknown relation through selected interaction; verified preservation through declared discontinuity and unrelated learning; and use in a controlled novel relational arrangement. That is a limit of these three inspected studies, not evidence that no such system exists. It also does not justify demanding deletion of every legitimate external memory channel.

No paywall blocks these claims and no human paper request is needed for them. Further progress depends primarily on exact run provenance and code, not additional abstracts. The title lead “Lifelong-SWE” did not resolve to a primary paper in the bounded search; no claim rests on it. LifelongAgentBench was located as an older precursor, not relabelled a recent result.

EdgeBench, [arXiv:2607.05155v1](https://arxiv.org/html/2607.05155v1), **preprint**, accessed 2026-09-06, is a further positive lead. Only its task/measurement setup was inspected here; its continuation controls and scaling derivation remain outside this note's evidence. It was forwarded to the PI for a separate methods audit, rather than being used to support a headline.

Pinned source hashes are recorded in `evidence/P1_INTEGRATED_RECENT_SOURCE_HASHES_2026-09-06.json`. Raw third-party HTML and extracted text remain under ignored `private_sources/p13_recent/` and are not proposed for public publication. The missing optional Python package and successful standard-library fallback are recorded in `evidence/P1_INTEGRATED_RECENT_ERRORS_2026-09-06.jsonl`.
