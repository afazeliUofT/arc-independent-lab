# Interactive acquisition: evidence availability, commitment and evaluation

Phase 1, 2026-09-06. PI methods analysis; no mechanism proposal or independent verdict. All linked sources accessed **2026-09-06**. This note separates reported observations from our causal inferences. It does not claim exhaustive coverage of scientific agents.

## A1. DiscoveryWorld: an end-to-end deficit does not locate its cause

Jansen et al., *DiscoveryWorld: A Virtual Environment for Developing and Evaluating Automated Scientific Discovery Agents*, published NeurIPS 2024 Datasets and Benchmarks paper. [Proceedings record](https://proceedings.neurips.cc/paper_files/paper/2024/hash/13836f251823945316ae067350a5c366-Abstract-Datasets_and_Benchmarks_Track.html); [inspected author version v2](https://arxiv.org/html/2406.06769v2). Outside the recent six-month window. Read §§3–5, Appendix C.2, D.1–D.4, E's scoring instructions and F; not every task implementation or example trajectory.

**Methods and observation:** the GPT-4o agents operate through supplied object/action interfaces. Tasks reset independently; experience does not transfer between tasks. ReAct discards old trajectory entries, while Hypothesizer repeatedly summarizes measurement/hypothesis records. Procedural execution, completion and expressed scientific knowledge receive different scores. Neither unit skills nor complete discovery succeeds uniformly.

**Attribution limit:** navigation, experimental choice, memory editing, inference and execution are bundled. Poor final performance identifies no unique mediator. Human participants were selected scientists with game familiarity; their knowledge notes were manually scored, while agent notes used an LLM evaluator. The populations, interfaces and prior experience differ. This is evidence of difficulty under these conditions, not a controlled human–AI capacity ordering or a test of persistent cross-task learning.

## A2. CausaLab: useful contrasts, unresolved causal specificity

Yang et al., *CausaLab: A Scalable Environment for Interactive Causal Discovery Toward AI Scientists*. **Preprint**, [arXiv:2605.26029v2](https://arxiv.org/html/2605.26029v2), 2026-05-28; [version record](https://arxiv.org/abs/2605.26029), first submitted 2026-05-25. Within 2026-03-06–2026-09-06. Read §§3–5, limitations, Appendix A's methods and tables; the HTML omits prompt bodies, so both complete prompt templates were read in the [PDF](https://arxiv.org/pdf/2605.26029v2), pp.16–24. Full implementation and paired outcome audit remain separate work.

**Methods and observation:** agents receive named variables, functional families and baseline records; actions shift equation intercepts rather than sever incoming causes. A separate crystal shares the generating mechanism. Reported final hypotheses can contradict collected measurements. A verification step increases a small-model task score. Stronger models improve several outcomes; mixed observational/interventional evidence improves explicit graph recovery in some comparisons.

**Attribution limit:** authors call the commitment pattern “overconfidence.” Extra computation, instructions and evidence use are not separately controlled. The printed controller restricts hypothesis revision to new evidence and freezes it during reactor operation; entering the reactor also closes further experimentation. Graph recovery and task prediction need different interpretations. A graph unnecessary for the assigned prediction is not automatically decision-relevant missing knowledge. Version-specific scoring and verification details require further audit before a stronger attribution.

## Our deductions and competing explanations

**D1. Full world reconstruction is neither necessary nor sufficient for an assigned decision.** A predictor can answer correctly while leaving other relations unknown. That is a limitation when a later task needs those relations; it is not itself failure of the original task. Conversely, a correct explicit graph can coexist with wrong coefficients or faulty execution. A diagnostic evaluation must identify which missing distinction would change a permitted future decision. This argument does not assert that any particular agent has such a sufficient representation.

**D2. Evidence that contradicts a committed answer is stronger than unused budget alone.** Finishing early can be rational if the remaining uncertainty cannot affect the decision. An answer that violates already available measurements supplies a sharper failure location: obtaining additional observations was not the only possible problem. It still does not locate the cause within reading, bookkeeping, interpretation, arithmetic, hypothesis selection or stopping. The source's natural-language psychological description does not settle that choice.

**D3. Irreversibility depends on the interface.** In the printed CausaLab protocol, a transition can remove access to further experiments. Before that transition, an error might still be recoverable; afterwards, the remaining information and permitted actions determine recoverability. This is an externally imposed discontinuity, not evidence of a learned memory erasing itself. A reported commitment defect may partly reflect instructions about when revision is allowed. This alternative remains untested.

**D4. A causal claim needs a controlled counterfactual at the same information boundary.** A verification intervention can improve a whole agent package while leaving its mediator unresolved. Comparing it with equal-budget reconsideration, checking whether raw measurements remain accessible, and distinguishing parsed hypotheses from action-generating state would discriminate explanations. These are explanatory controls to seek in evidence, not a new agent design or a Phase 3 preregistration.

**D5. Adaptive interaction and an offline trace are not automatically matched.** Selected observations, presentation order, opportunities to revise and token budgets can all change. An online advantage would establish the effect of the tested package; attributing it specifically to ownership of the experiment requires tighter control. Likewise, a vendor-model comparison is not a parameter-only scaling experiment.

## Evidence exclusion and unresolved positive coverage

A separate [theory audit](P1_CAUSAL_THEORY_AUDIT_2026-09-06.md) rejects a May 2026 preprint's stated kernel bound: normalized similarity and an upper norm bound do not imply the asserted score-gap inequality. Its hypothetical LLM queries also supply no external observations. It cannot substantiate a claim that scaling is incapable of closing the funded gap. This is a narrow mathematical exclusion, not a judgment on all results in that paper. [Audited preprint](https://arxiv.org/html/2605.27567v1), accessed 2026-09-06.

The Nature page for *A multi-agent system for automating scientific discovery* did not open on the attempted route. No scientific claim here relies on its abstract or presumed methods. Positive real-world discovery systems remain a useful coverage target; failing to retrieve one route is not negative evidence about them. [Attempted primary page](https://www.nature.com/articles/s41586-026-10652-y), accessed 2026-09-06.

Reading copies remain in ignored `delivery/acquisition_sources/`; no source paper is included in the public handoff. No experiment or paid model call was run for this pass.

## Addendum: released metric code changes the interpretation

The completed `P1_CAUSALAB_METRIC_AUDIT_2026-09-06.md` inspects the live companion repository at commit `42ba47fb88e60dc1eca17bd29c47ace4e8e9960e`. One released evaluation path asks separate post-run model questions for roots and graph reporting; another derives roots from the logged graph. The exact table-linked path remains unverified. A mismatch between perfect edge scoring and imperfect root scoring therefore need not be a metric bug or an absent relation in the acquired graph. It can concern a different elicited use of the available information. This is a plausible explanation, not verified provenance for the paper's table. [Pinned evaluation code](https://github.com/DylanZSZ/CausaLab-Benchmark/blob/42ba47fb88e60dc1eca17bd29c47ace4e8e9960e/causalab_reeval/reeval_core.py), accessed 2026-09-06.

Released validation instructions request checking at every step, while the paper describes a single check; an exact execution manifest was not located. The reported procedural gain remains evidence to investigate, with equal computation and specific mediation unresolved. No accusation of a scoring or implementation error follows from missing provenance.
