# Phase 2 prerequisite biology pass: acting while the feedback channel is uncertain

**Date and access date: 2026-09-06.** Focused consultation sharing the PI's tools and filesystem, **not independent review**. This pass precedes mechanism generation and contains no proposed artificial mechanism or novelty assessment. It uses one decisive primary study rather than expanding the survey after a usable methods source was found.

## Operational constraint and concrete system

The selected system is adult Bengalese finch vocal adaptation. The constraint for the programme is **feedback is an observation whose relevance must be established, not automatically a correct training target**. Acting produces the signal available for subsequent adaptation; an apparent mismatch can result from the action-producing system, the transmission/measurement channel, or their interaction. An adaptation rule that changes behaviour on every mismatch can alter an already serviceable behaviour in response to a sensor disturbance. Refusing every unfamiliar signal can instead prevent learning after a real change. This is a problem statement and a deduction about feedback ambiguity, not a claim that birds optimally resolve it.

This differs from the earlier biology pass's emphasis on inventories of surviving information. Its location is before a learning update: what does the observed discrepancy license the learner to change? It bears on the approved diagnosis's relation-selection and action-dependent-acquisition questions, without identifying their prevalence in current AI.

## Primary methods, result, and alternatives

**Sober, S. J. & Brainard, M. S. (2012), “Vocal learning is constrained by the statistics of sensorimotor experience.” Published PNAS article, not a preprint.** [DOI](https://doi.org/10.1073/pnas.1213622109); [institutional PDF](https://escholarship.org/content/qt66q5v3kn/qt66q5v3kn.pdf), accessed 2026-09-06.

**Evidence class:** animal behavioural intervention. Six adult males experienced pseudorandomly ordered pitch shifts through headphones. Feedback followed vocalization by 7–10 ms; each shift lasted 14–17 days, separated by recovery periods. Magnitudes were ±50, ±100, ±150 and ±300 cents. Acoustic measurements sampled fixed daily windows. Larger shifts produced slower, less complete compensation. One of 19 experiments was excluded after syllable structure changed substantially. Fits for five remaining individual experiments failed to converge. The overlap–compensation association was driven mainly by differences between shift sizes, not within-size variation. The authors consider both sensory reweighting and reinforcement through successful renditions; these are alternatives, not separated mediators.

**Reading coverage:** complete five-page article, including Methods, equations, Results, Discussion, figure legends and references, via PDF text extraction. Upstream apparatus protocols, raw data and graphical measurements were not independently audited. Screenshot calls exposed reference placeholders rather than inspectable image bytes; no visual figure audit is claimed.

## What can and cannot be inferred

**Nonempty result:** an intact adult learning system need not respond more strongly to a larger apparent error. Treating slow correction as a failure of plasticity before identifying the feedback channel would therefore be an inadequate diagnosis. This is a conceptual consequence of the measured mismatch–response relation, not a proof that reduced correction is always appropriate.

The physical feedback loop supports a specific inference: as behaviour changes, the data for the next update change too. It does not follow that the animal intentionally selects maximally informative experiments. The measured loop is compatible with continuing correction under an existing skill and objective. It is not evidence for discovering new action primitives, retaining arbitrary knowledge across unrelated tasks, or solving unfamiliar world models.

Several stronger readings remain unjustified:

- The observed response does not prove that the bird represents a separate sensor fault, assigns causal responsibility correctly, or performs optimal Bayesian attribution.
- A correlation between a distribution statistic and adaptation is insufficient to make that statistic the causal control variable. Different candidate explanations can reproduce the same ordering; varying the statistic independently of the perturbation would be relevant to separating them.
- Continuing to produce song is a narrower operational condition than preserving normal communication success. The latter was not established here. I do not convert absence of a measured end-to-end utility into a claim of protected functionality.
- An experiment with a finite observation period does not establish irrecoverable inability or a universal upper bound on learning. The argument needs neither.

## Exact artificial assumption being contrasted

The closest fully inspected artificial comparator is **our own Phase 1 diagnostic witness**, not an unspecified claim about all neural networks. Its world supplies a noiseless response `y = a * m_c`, a visible context `c`, and an aligned feature map. Each training response is then used directly in the update `theta += eta * (y - dot(x, theta)) * x`. The design explicitly calls this a sequential supervised-fitting subproblem: either nonzero noiseless action identifies the context gain to a suitable estimator. [Published design at the approved diagnosis commit](https://github.com/afazeliUofT/arc-independent-lab/blob/069bd7dc3db1cec6e9fc6ff67046547488f05353/docs/P1_REPRODUCTION_DESIGN.md), local file read 2026-09-06; the GitHub link identifies the version, not a newly performed remote byte verification.

That setup removes uncertainty about whether a response is a faithful outcome of the declared action in the declared context. The learner still does not receive the hidden gain itself. The removed demand is **feedback attribution**, not the existence of any learning problem. The witness remains valid for its interference question; the biological comparison does not invalidate its arithmetic or justify enlarging its conclusions.

A small formal example clarifies the distinction. Suppose an actor receives `z = g*a + b`, where `g` is an unknown action effect and `b` an unknown observation offset. At a single repeated nonzero action `a0`, the pairs `(g,b)` and `(g+delta,b-delta*a0)` produce identical feedback. More fitting to those same observations cannot uniquely decide which component changed. Variation in the permitted action, under additional assumptions about stationarity and noise, can provide distinguishing evidence. This is our deduction, not the bird study's estimated model, and not an artificial repair proposal. The point is that trustworthy training labels silently remove an identification burden that an acting system with uncertain feedback must face.

This comparison does **not** establish that contemporary reinforcement-learning systems uniformly remove the burden. The source does not contain a matched AI experiment. What survives for Phase 2 is a demand to reason about this burden explicitly, not a biological superiority claim.

## Question passed to generation, with screening still off

**How can a learner discover which observed consequences should change its behaviour, and which instead call the observation relation into question, when its own actions generate the available evidence and further learning must proceed through those same actions?**

A future answer must explain what evidence distinguishes those cases and what remains unidentifiable under its assumptions. It must not assume a correct error label, an independently calibrated observer, or an externally supplied diagnosis of which component changed unless those are declared resources. No answer or named design is supplied by this prerequisite pass.

## Access and stopping record

The initially chosen Tumer–Brainard 2007 and Andalman–Fee 2009 routes did not yield usable full methods during the bounded search. Their abstracts and later retellings are not evidence for any adopted claim. An author-hosted Mandelblat-Cerf et al. 2014 PDF was reachable, but only an initial portion was inspected; no result from it is adopted. The focused pass switched to the complete Sober–Brainard 2012 institutional PDF. The shift is a source-access decision, not a novelty judgment.

Canonical PMC pages returned browser checks, publisher routes returned access errors, and an ordinary download of the institutional PDF returned non-PDF bytes despite readable web extraction. No challenge was solved, access control bypassed, or source bytes placed in the public handoff. The record is `evidence/P2_BIOLOGY_ACTION_ERRORS_2026-09-06.jsonl`. No mandatory paper request remains for this bounded claim. No state file, approved diagnosis, earlier note, experimental artifact, or other programme was modified.
