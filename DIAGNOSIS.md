# DIAGNOSIS — working document

**Phase 1, initial checkpoint, 2026-09-06. Incomplete; not submitted for phase approval.**

The required failure reproduction, evidence synthesis and bottleneck ranking are outstanding. This document distinguishes definitions, deductions, source-supported observations and unanswered questions. It contains no proposed repair. User-supplied framing is a hypothesis, not evidence; see `docs/USER_AMENDMENTS_2026-09-06.md`.

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

**Not yet built or run.** No result, metric or mechanistic conclusion is claimed. The hosted Python execution route is available. Reproduction selection follows the computational-demand account and will target a failure whose onset can be inspected; it will not be chosen to validate a parked idea.

## 4. Interdisciplinary constraints

Initial evidence: `evidence/SCOUT_BIOLOGY_2026-09-06.md`. Synthesis pending. Constraints, intervention versus recording, species, task-specific controls and limitations must remain explicit. Biological findings supply questions and constraints, not engineering validation.

## 5. Archaeology

Initial evidence: `evidence/SCOUT_ARCHAEOLOGY_2026-09-06.md`. Synthesis pending. The historical alternatives are not being proposed as repairs. For each line, distinguish documented computational or representational limits from unverified stories of abandonment; ask which precise limit has changed by 2026. A continuing research tradition is not an abandoned one merely because it is outside today's dominant AI community.

## 6. Ranked bottlenecks

**Intentionally not yet ranked.** The source base and own trace are insufficient. Each eventual entry must state a falsifiable cause, supporting and opposing evidence, an observation that would refute it, an unchecked prediction, and calibrated confidence with a route to raising it. Topic labels and restatements of failure will not count.

## 7. The hypothesis we were handed

Plasticity control over retain / protect / suppress / recompose remains one unranked hypothesis. The current demand account does not assume that suitable knowledge was acquired in the first place, that these four functions are independent, or that storage is where a failed decision originated. No rejection or endorsement is justified yet.

## 8. What remains unresolved

- Whether the motivating phenomenon is one shared failure or a conjunction with distinct causes.
- The strongest evidence for and against persistent useful knowledge under controlled discontinuities.
- What current scaling results actually establish in the relevant settings.
- The own-system trace required before causal bottlenecks can be ranked.
- Historical primary-source gaps listed in the paper-request file once the initial scout is consolidated.
- A verified GitHub round trip, authoritative usage observability and enforceable independent review. These operational uncertainties cannot be represented as scientific findings.

**Next scientific action:** choose and specify the small failure reproduction with an explicit evidence-access and reset inventory; trace it locally before extending the catalogue or ranking bottlenecks. Continue other unblocked literature investigation only within recorded attended work.
