# DIAGNOSIS — working document

**Phase 1, second checkpoint, 2026-09-06. Incomplete; not submitted for phase approval.**

A bounded instrumented failure reproduction is now complete. Broader failure attribution, evidence synthesis and bottleneck ranking remain outstanding. This document distinguishes definitions, deductions, source-supported observations and unanswered questions. It contains no proposed repair. User-supplied framing is a hypothesis, not evidence; see `docs/USER_AMENDMENTS_2026-09-06.md`.

## 1. The computational demand

### 1.1 Define what the agent is allowed to know

“An unknown world” is insufficiently specified to diagnose. At least the following can be unknown separately: the present physical state; the transition law; what observations refer to; which actions are interventions on which variables; the reward or goal; whether the world changed; and which past experience is relevant now. Knowing a transition law while not knowing one's location is different from discovering the law. An agent may face both, but evidence for one must not be credited as evidence for the other.

The governing phenomenon is therefore a conjunction of demands, not yet a claim that they share one cause:

| Demand | Operational meaning | What would leave it untested |
|---|---|---|
| Acquire through interaction | Consequences of selected actions supply information that matters to later decisions | Supplying the relevant rule in the prompt, simulator API, training labels or pretrained knowledge |
| Preserve across discontinuity | Past interaction changes later behaviour through a declared surviving channel | Calling an environment reset an agent-memory reset; restoring undeclared conversation or simulator state |
| Reuse in a novel arrangement | A specified relation between earlier experience and a held-out arrangement makes prior learning useful | Merely resampling a familiar task; treating every distribution shift as compositional novelty |
| Remain functional while learning | Learning and acting share a finite interaction and computation budget | Giving unlimited retries, unrestricted replay or offline fitting while counting only the final action |

For each study, I will record the world family and assumptions, initial knowledge, action/observation interface, surviving state, discontinuity, test novelty and resource allowances. These are descriptive requirements for interpretable evidence, not a commitment to any environment or architecture.

### 1.2 The minimum formal description

Let a world be a member \(w\) of an explicitly restricted family \(\mathcal W\). Let \(h_t\) be the interaction history available up to a decision, \(s_t\) the agent's complete computational state, and \(K_0\) its prior knowledge, including pretraining and supplied task structure. A discontinuity applies a declared transformation \(D\) to the agent, environment, or both. At a later decision the policy has only its post-discontinuity state, current observations, permitted tools, and remaining budget.

This notation does **not** require that the agent represent a causal graph, objects, modules, rules or “pieces.” A useful representation is defined here by the decisions it supports. Whether reusable pieces are discoverable, necessary or the right ontology remains open.

Different histories can support the same optimal decision; the programme should not demand preservation of all historical detail. Conversely, identical training predictions do not establish that two learned states support the same future interventions. Sufficiency is relative to a family of future demands, not a property conferred by compression or reconstruction quality alone.

### 1.3 Distinguish impossible inference from algorithmic failure

**Deduction, not an empirical finding.** Consider two allowed worlds that generate the same distribution of everything the agent has observed, given its actions and prior information, but require incompatible later decisions. If no permitted remaining interaction can distinguish them, no decision rule can guarantee the appropriate world-specific answer. Adding computation to the same evidence cannot remove that ambiguity. A claim that a learner failed must therefore say what informative evidence was available or obtainable, and at what cost.

This matters for interpreting causal-factor discovery. Locatello et al.'s theorem constructs observationally equivalent but differently entangled latent descriptions under its factorized-density assumptions. It concerns learning from samples of the observation distribution; it does not establish that intervention, temporal restrictions or every useful representation are futile. Source examined: §3 theorem and its scope, plus §4 experimental design; the complete proof has not been independently audited here. [Locatello et al., ICML 2019, published paper](https://proceedings.mlr.press/v97/locatello19a/locatello19a.pdf), accessed 2026-09-06.

Our diagnosis must distinguish a learner that never sought available distinguishing evidence from one that had no possible distinguishing evidence. It must also distinguish an adequate hypothesis class fitted badly from a supplied hypothesis class incapable of expressing the relevant distinction. These possibilities are questions to test, not a current ranking.

### 1.4 A discontinuity needs a state inventory

The phrase “across episodes” hides several materially different manipulations:

| Discontinuity | Required distinction |
|---|---|
| Environment restart | Did world state reset while agent context, recurrent state or external notes survived? |
| Context clearing | Did weights, optimizer state, files, retrieval stores or cached tools still convey the experience? |
| Intervening learning | Was prior knowledge changed, access to it impaired, or its application made inappropriate by a changed world? |
| Long elapsed gap | What process actually operated during the gap—no computation, turnover, interference, drift or resource expiry? |
| New context | Is the old rule false, merely irrelevant, or still useful through a different observation interface? |

For retention claims, pretraining weights, learned weights, optimizer buffers, recurrent state, prompts, files, retrieval records and environment-side persistence all belong in the inventory. External memory is a legitimate surviving channel if declared and comparably available; an undeclared channel makes the claim uninterpretable. A frozen digital state does not forget because a wall-clock interval passed. Biological time and simulator steps therefore cannot be equated without naming the intervening process.

An essential distinction is **preservation versus access versus use**. Failure of one probe to decode a fact is not proof that the fact is absent. Success of an expensive probe is not proof that the acting policy can exploit it within budget. A report of “forgotten knowledge” must make that inferential gap visible.

### 1.5 Novelty must specify what changed and what stayed reusable

New appearances, a held-out combination of familiar relations, a new goal over familiar dynamics, changed dynamics, and an entirely new causal primitive make different demands. They may co-occur. For each evaluation I will ask what transfer would be warranted from the training support and what additional inference is necessary.

There is a particularly dangerous shortcut: give the agent the correct variables and operators, withhold some combinations, then infer that successful recombination explains how agents discover reusable variables and operators. That setup tests a real capability, but omits part of the funded question. The converse mistake is to declare recombination a failure when the test requires an unobserved primitive whose behaviour was unconstrained by all available experience.

### 1.6 What is already tractable, and under which supplied conditions?

Known-model partial observability is a useful boundary case. Kaelbling, Littman and Cassandra derive state estimation and planning using a given transition/observation model; belief-state sufficiency in that setting does not by itself solve learning an unknown model. This separates a well-defined planning problem from the larger acquisition problem. It does not make large POMDPs computationally easy. [Published paper, Artificial Intelligence, 1998, §§3.1–3.4](https://people.csail.mit.edu/lpk/papers/aij98-pomdp.pdf), accessed 2026-09-06.

The initial AI source map also contains positive adaptation, scaling and interaction-derived-memory results. Their reset boundaries, training support and retained channels are documented in `evidence/SCOUT_RECENT_AI_2026-09-06.md`. They already prevent treating “current AI cannot learn from interaction” as an uncontested premise. Generality and longitudinal persistence still need separate evidence.

Few laboratory demonstrations are not a complete learning budget for humans or animals. Species history, development, prior experience, instruction, apparatus familiarity and exclusions can all carry relevant structure. AI pretraining and human lifetime experience must both be acknowledged; neither can be honestly subtracted by calling an evaluation few-shot. The biology source map is a first check on this comparison, not evidence for a general species ordering.

### 1.7 What a diagnostic trace must localize

The reproduction must go beyond end-task success. For the chosen small failure, I will identify which observations and actions made the relevant distinction available; which learner state contained it before and after a discontinuity; and whether later action selection could use it. “The last point before failure became inevitable” is conditional on the remaining observation, intervention and computation budget. A bad early choice is not an irreversible information loss if the policy can still recover.

A controlled diagnostic intervention may reveal which explanation is compatible with a trace. Such an intervention is an explanatory control, not a candidate repair. The reproduction must also show a case where the same apparatus succeeds, or it cannot distinguish a scientific failure from a broken apparatus. Its eventual claim will remain confined to the reproduced system and assumptions.

## 2. The failure catalogue

Initial source map: `evidence/SCOUT_RECENT_AI_2026-09-06.md`. Each entry distinguishes reported score, observation and attribution. The recent window is 2026-03-06 through 2026-09-06; the scout marks the preprints that fall within it. This is not comprehensive coverage and not yet a synthesized catalogue.

Outstanding: direct longitudinal retention evidence; controlled novel-combination studies; stronger intervention-based failure attributions; broader recent proceedings coverage; explicit counterevidence for each eventual bottleneck.

## 3. Our reproduction

### 3.1 A behavioural deficit is not sufficient evidence of erased information

The prospective design and full report are `docs/P1_REPRODUCTION_DESIGN.md` and `reports/P1_REPRODUCTION_001.md`. We ran an online linear action-response predictor, first in a visible context A and then in B. Its persistent learned state consists only of its weights. Both rules are expressible within the same model class; nevertheless, fitting B through shared features degrades the ordinary A readout. A fixed observer still recovers the earlier estimate from a parameter difference. Crossing old and new gains and inspecting decoder inputs rule out a hardcoded target as the explanation.

For the illustrative opposite-gain case, the ordinary old prediction changes sign during B learning, while the observer's recovered estimate retains the old sign. The frozen control preserves the old prediction without learning B; the orthogonal control fits B while preserving A. These are observed properties of this construction, not a model ranking. Full values and every transition: `artifacts/P1_LINEAR_INTERFERENCE/20260906_001/results.json`, SHA-256 `837b6ce92176182d1e2878f585388824d3b0173d2585e69c749243ac0a626762`; `artifacts/P1_LINEAR_INTERFERENCE/20260906_001/transitions.jsonl`, SHA-256 `908f4b073a63a0c7019fe65173b461a2fc7f7ad0b51d68f05e7cfc083308a3a4`. Local access 2026-09-06. The report gives an explicitly cited numerical table and the loss-change decomposition.

**Attribution:** equal changes to the shared coordinates move the prescribed old readout but preserve their difference. The first B update can begin worsening old error; a later sign error is not irreversible loss, because the old estimate remains recoverable in the observed trace. There is therefore no irreversible information-loss point to report. An analyst who equates the first failed behavioural probe with erasure would misdiagnose this system.

**Scope:** this is a deliberately simple sequential fitting subproblem. A noiseless response already identifies its context gain; the learner's slow gradient fitting is imposed, not an environmental necessity. Context labels, feature geometry and initialization are supplied. The observer's geometric knowledge is also supplied and is not a learned capability. Exploration, causal-variable discovery, novel recombination, repeated context cycles, realistic noise and frontier models remain untested. The orthogonal control changes the optimization metric and B initialization even though feature norms and representational capacity are matched. It is an explanatory control, not a proposed repair.

This reproduction supports a distinction necessary for the diagnosis. It does not establish the prevalence of hidden recoverability in current large systems or determine the programme's bottleneck ranking. Its arithmetic audit is an artifact-consistency check, not an independent scientific verdict.

## 4. Interdisciplinary constraints

Initial evidence: `evidence/SCOUT_BIOLOGY_2026-09-06.md`. Synthesis pending. Constraints, intervention versus recording, species, task-specific controls and limitations must remain explicit. Biological findings supply questions and constraints, not engineering validation.

**Supplied-method update:** Ryan et al.'s published main article and a recovered deposited supplement permit a more careful storage/access distinction. Artificially evoked experience-dependent behaviour supports some surviving information despite impaired natural-cue retrieval. It does not establish complete preservation, a unique storage substrate or equivalence to normal retrieval. The categorical encoding-control interpretation in the provisional account must be narrowed; the detailed version and control qualifications are preserved in `evidence/RYAN_SUPPLIED_METHODS_2026-09-06.md`. [Published article](https://doi.org/10.1126/science.aaa5542), [supplement deposit](https://www.ebi.ac.uk/biostudies/studies/S-EPMC5583719), accessed 2026-09-06. The linear witness above and this biological intervention have different causal assumptions; their shared inferential caution does not establish a shared mechanism.

## 5. Archaeology

Initial evidence: `evidence/SCOUT_ARCHAEOLOGY_2026-09-06.md`. Synthesis pending. The historical alternatives are not being proposed as repairs. For each line, distinguish documented computational or representational limits from unverified stories of abandonment; ask which precise limit has changed by 2026. A continuing research tradition is not an abandoned one merely because it is outside today's dominant AI community.

**Drescher correction:** the supplied dissertation explicitly includes predictive maintenance of synthetic-item state and rules for resolving competing evidence. Describing the original specification as duration-only would be false. The later comparator's implementation fidelity and update timing remain unresolved. The thesis reports memory exhaustion and only partial development in an engineered microworld; this documents an old constraint without proving that present compute removes it. [Drescher dissertation, §§3.4.3, 4.3 and 6](https://dspace.mit.edu/handle/1721.1/77702), accessed 2026-09-06. Relevant sections, not the entire dissertation, were read; full coverage and limits are in `evidence/DRESCHER_SUPPLIED_METHODS_2026-09-06.md`.

**Minton qualification:** the complete expanded article separates search saved by retained control knowledge from the cost of applying it. Its utility validation directly measures matching cost and application frequency while retaining the original example's savings estimate. It does not supply a lifetime learning-plus-use cost account. It also assumes a supplied explanatory theory, so the result concerns useful reformulation rather than unknown-law discovery. [Minton, published journal article, §§4–8](https://doi.org/10.1016/0004-3702(90)90059-9), accessed 2026-09-06; full-method account in `evidence/MINTON_SUPPLIED_METHODS_2026-09-06.md`.

**Cross-era inference:** larger memory changes the feasible frontier of a bounded computation; it does not by itself remove combinatorial growth. Conversely, old complexity concerns do not prove that the same operation still dominates a present workload. These lines require documented uptake history and explicit present-day cost accounting before any “abandoned for a reason that has expired” conclusion. The first paper batch is resolved for its current bounded claims; conditional future retrieval needs are in `evidence/PAPER_REQUESTS_001_RESOLUTION.md`.

## 6. Ranked bottlenecks

**Intentionally not yet ranked.** The source base and own trace are insufficient. Each eventual entry must state a falsifiable cause, supporting and opposing evidence, an observation that would refute it, an unchecked prediction, and calibrated confidence with a route to raising it. Topic labels and restatements of failure will not count.

## 7. The hypothesis we were handed

Plasticity control over retain / protect / suppress / recompose remains one unranked hypothesis. The current demand account does not assume that suitable knowledge was acquired in the first place, that these four functions are independent, or that storage is where a failed decision originated. No rejection or endorsement is justified yet.

The own trace adds a constraint: update-induced performance interference can occur without erasure of the acquired estimate. A plasticity account of behaviour remains possible, but evidence for interference cannot automatically be relabeled evidence for storage loss. Historical construction limits and application costs also need distinct explanations; they cannot be absorbed into plasticity terminology without a testable causal argument.

## 8. What remains unresolved

- Whether the motivating phenomenon is one shared failure or a conjunction with distinct causes.
- The strongest evidence for and against persistent useful knowledge under controlled discontinuities.
- What current scaling results actually establish in the relevant settings.
- Whether the own trace's distinction transfers to stronger current systems under realistic observation and computation constraints.
- Historical uptake explanations and conditional implementation/version gaps recorded in the source-resolution notes. No immediate human paper request remains from the first batch.
- Authoritative usage observability, enforceable independent review, restart tests and large-output durability. The first small GitHub checkpoint round trip is now verified; these broader operational requirements remain open and are not scientific findings.

**Next scientific action:** deepen the failure catalogue around active evidence acquisition, longitudinal retention and controlled novel reuse, seeking matched successes and scaling counterevidence before ranking bottlenecks. Extend the archaeology beyond the resolved batch and distinguish documented limitations from unsupported abandonment stories. Do not enlarge the deterministic reproduction merely to generate more measurements. Continue within explicitly requested interactive work, after verifying this checkpoint's human publication.
