# DIAGNOSIS

**Phase 1 submission for human review, 2026-09-06. Approval pending; Phase 2 has not begun.**

The motivating claim needs narrowing. Artificial systems can learn through interaction, retain useful context and generalize to withheld combinations under specified conditions. Scale and training diversity sometimes help substantially. The reviewed evidence does not establish that humans and animals effortlessly solve the full conjunction, or that scaling cannot close useful parts of the gap. What remains scientifically credible is a set of conditional failures whose causes can differ.

My current diagnosis is that a useful past experience can cease to control a later decision at several distinct stages: the available evidence may not identify the needed relation; fitting may select a relation that does not survive the intended change; subsequent learning may disrupt its usable expression; and a decision process may fail to apply information that remains available. Past training can also make further learning less efficient. These are competing and interacting explanations, not names for a single established defect. Section 6 gives the revised ranked, falsifiable claims and their refuters.

**Correction to checkpoint003:** I gave retained-information/readout disruption too much priority on the strength of a decisive but deliberately constructed witness. The integrated-agent audit does not establish that it governs the funded category. I move it from first to third priority, and place relation selection and action-dependent acquisition ahead of it. These are research priorities, not measured prevalence; the second has stronger formal than contemporary-agent evidence. This document distinguishes deductions, source-supported observations and unresolved attributions. It contains no proposed repair. User-supplied framing is a hypothesis, not evidence; see `docs/USER_AMENDMENTS_2026-09-06.md`. Scientific source notes are consultations sharing tools and files, not independently enforced reviews. The published reproduction and earlier corrections remain unchanged.

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

The source notes and catalogue record the world family and assumptions, initial knowledge, action/observation interface, surviving state, discontinuity, test novelty and resource allowances to the extent the inspected methods establish them. Missing run-level details are marked rather than assumed. These are descriptive requirements for interpretable evidence, not a commitment to any environment or architecture.

### 1.2 The minimum formal description

Let a world be a member \(w\) of an explicitly restricted family \(\mathcal W\). Let \(h_t\) be the interaction history available up to a decision, \(s_t\) the agent's complete computational state, and \(K_0\) its prior knowledge, including pretraining and supplied task structure. A discontinuity applies a declared transformation \(D\) to the agent, environment, or both. At a later decision the policy has only its post-discontinuity state, current observations, permitted tools, and remaining budget.

This notation does **not** require that the agent represent a causal graph, objects, modules, rules or “pieces.” A useful representation is defined here by the decisions it supports. Whether reusable pieces are discoverable, necessary or the right ontology remains open.

Different histories can support the same optimal decision; the programme should not demand preservation of all historical detail. Conversely, identical training predictions do not establish that two learned states support the same future interventions. Sufficiency is relative to a family of future demands, not a property conferred by compression or reconstruction quality alone.

### 1.3 Distinguish impossible inference from algorithmic failure

**Deduction, not an empirical finding.** Consider two allowed worlds that generate the same distribution of everything the agent has observed, given its actions and prior information, but require incompatible later decisions. If no permitted remaining interaction can distinguish them, no decision rule can guarantee the appropriate world-specific answer. Adding computation to the same evidence cannot remove that ambiguity. A claim that a learner failed must therefore say what informative evidence was available or obtainable, and at what cost.

This matters for interpreting causal-factor discovery. Locatello et al.'s theorem constructs observationally equivalent but differently entangled latent descriptions under its factorized-density assumptions. It concerns learning from samples of the observation distribution; it does not establish that intervention, temporal restrictions or every useful representation are futile. Source examined: §3 theorem and its scope, plus §4 experimental design; the complete proof has not been independently audited here. [Locatello et al., ICML 2019, published paper](https://proceedings.mlr.press/v97/locatello19a/locatello19a.pdf), accessed 2026-09-06.

Our diagnosis must distinguish a learner that never sought available distinguishing evidence from one that had no possible distinguishing evidence. It must also distinguish an adequate hypothesis class fitted badly from a supplied hypothesis class incapable of expressing the relevant distinction. These possibilities are separated in the conditional claims of §6; the information prerequisite is not itself proof that an algorithm failed.

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

New appearances, a held-out combination of familiar relations, a new goal over familiar dynamics, changed dynamics, and an entirely new causal primitive make different demands. They may co-occur. The diagnosis distinguishes transfer warranted by training support from additional inference that the held-out case requires.

There is a particularly dangerous shortcut: give the agent the correct variables and operators, withhold some combinations, then infer that successful recombination explains how agents discover reusable variables and operators. That setup tests a real capability, but omits part of the funded question. The converse mistake is to declare recombination a failure when the test requires an unobserved primitive whose behaviour was unconstrained by all available experience.

### 1.6 What is already tractable, and under which supplied conditions?

Known-model partial observability is a useful boundary case. Kaelbling, Littman and Cassandra derive state estimation and planning using a given transition/observation model; belief-state sufficiency in that setting does not by itself solve learning an unknown model. This separates a well-defined planning problem from the larger acquisition problem. It does not make large POMDPs computationally easy. [Published paper, Artificial Intelligence, 1998, §§3.1–3.4](https://people.csail.mit.edu/lpk/papers/aij98-pomdp.pdf), accessed 2026-09-06.

The initial AI source map also contains positive adaptation, scaling and interaction-derived-memory results. Their reset boundaries, training support and retained channels are documented in `evidence/SCOUT_RECENT_AI_2026-09-06.md`. They already prevent treating “current AI cannot learn from interaction” as an uncontested premise. Generality and longitudinal persistence still need separate evidence.

Few laboratory demonstrations are not a complete learning budget for humans or animals. Species history, development, prior experience, instruction, apparatus familiarity and exclusions can all carry relevant structure. AI pretraining and human lifetime experience must both be acknowledged; neither can be honestly subtracted by calling an evaluation few-shot. The biology source map is a first check on this comparison, not evidence for a general species ordering.

### 1.7 What a diagnostic trace must localize

The completed reproduction goes beyond end-task success (§3): it identifies the available evidence, tracks the complete learned state through later updates, and compares the prescribed response with a fixed observer of that same state. “The last point before failure became inevitable” is conditional on the remaining observation, intervention and computation budget. A bad early choice is not an irreversible information loss if the policy can still recover.

A controlled diagnostic intervention may reveal which explanation is compatible with a trace. Such an intervention is an explanatory control, not a candidate repair. The reproduction includes successful controls that distinguish the failure from a broken apparatus. Its claim remains confined to the reproduced system and assumptions.

### 1.8 Acquisition must anticipate a restricted family of later demands

Evidence can be irrelevant to today's reward and useful after tomorrow's goal changes. This does not imply retaining everything. **Our deduction:** if all n-bit histories are possible, only B<n bits survive, no other channel conveys the history, and the later query may ask for any historical bit, some distinct histories must share a retained state. A query on a differing bit then cannot be answered correctly in both cases with certainty. This worst-case argument is not a limit on useful learning in structured worlds.

The defensible demand is therefore preservation sufficient for a declared future family, with specified approximation and cost. An unknown future task need not mean an arbitrary adversarial question about every detail of the past. Conversely, supplying the full future goal schedule gives a learner information about what is worth acquiring now. The control-theory cases below have that advantage; biological preconditioning instead changes the later value of earlier relations within a small cue family. Neither covers unlimited future demands.

This distinction also changes where a trace can break. A policy may never generate distinguishing observations, a learner may discard an apparently irrelevant distinction, or later processing may fail to use a distinction that survived. The same failed endpoint does not identify which occurred. The derivation and assumptions are in `evidence/P1_ACTIVE_IDENTIFICATION_2026-09-06.md`.

## 2. The failure catalogue

### 2.1 Scope and evidence standard

The recent window is **2026-03-06 through 2026-09-06**. This is a purposive search across interactive agents, continued learning, composition and scaling, followed by methods inspection. It is not a systematic prevalence estimate. An older controlled result can supply stronger causal evidence than a recent leaderboard. Neither receives automatic priority because of its date.

Methods, versions, preserved state and alternative explanations are recorded in `evidence/P1_ACQUISITION_METHODS_2026-09-06.md`, `evidence/P1_RETENTION_METHODS_2026-09-06.md` and `evidence/P1_COMPOSITION_METHODS_2026-09-06.md`; the earlier AI scout supplies the AdA and memory-agent accounts. All external links in this section were accessed **2026-09-06**. Literature values are the cited authors' results, not measurements made by this programme.

### 2.2 Acquisition and use of evidence

| Study and supplied conditions | Reported outcome | Observed failure or success | Causal attribution supported, and limit |
|---|---|---|---|
| [DiscoveryWorld, NeurIPS 2024; inspected author v2](https://arxiv.org/html/2406.06769v2). Supplied actions/objects; independent tasks; some histories truncated or summarized. | Discovery completion is poor relative to selected human scientists; individual procedural skills also fail. | End-to-end scientific interaction is difficult in these agent configurations. | No single cause is isolated. Acquisition, navigation, record editing and execution co-vary. Cross-task learning is absent by protocol. Human and agent knowledge evaluators differ. |
| [CausaLab, May 2026, preprint v2](https://arxiv.org/html/2605.26029v2). Named variables and equation families; actual simulator perturbations shift intercepts. | Task prediction and reported mechanism-recovery scores diverge; a verification intervention improves a small-model score. | Some committed hypotheses contradict collected measurements. Stronger models also succeed much more often. | Authors call this “overconfidence.” Extra computation, prompt rules and evidence processing remain competing explanations. A global-graph error need not impair the assigned prediction. Exact metric provenance needs the companion audit. |
| [AdA, ICML 2023](https://proceedings.mlr.press/v202/bauer23a/bauer23a.pdf). Extensive task-distribution training; recurrent state survives trials within an episode. | Adaptation and scaling improve held-out task performance. | Useful behaviour changes after additional interaction in a task. | Positive evidence for acquired adaptation under the training family. It does not test survival after erasing that memory or after substantial unrelated learning. |

The diagnostic question is whether an agent had, could obtain, or actually used evidence that distinguishes the required actions. Unused experimental budget alone does not establish a defect: further experiments may be irrelevant. A hypothesis inconsistent with already available data is more revealing, although it still leaves reading, record maintenance, interpretation and commitment as alternatives. These are our inferences, not a claim that the benchmark identifies an internal psychological state.

The CausaLab PDF's controller instructions make revision conditional on new evidence and freeze the hypothesis during reactor operation; transition also closes further experimentation. That makes the supplied interface a plausible contributor to a commitment failure. It is not an experimentally established mediator. The companion audit must distinguish a hypothesis emitted while acting from answers elicited afterwards. [Exact prompt templates, Appendix A.4](https://arxiv.org/pdf/2605.26029v2), accessed 2026-09-06; **preprint**.

### 2.3 Retention, access and continued trainability

| Study and surviving state | Reported outcome | Observed failure or success | Causal attribution supported, and limit |
|---|---|---|---|
| [Dohare et al., Nature 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC11338828/). Sequentially retained weights; incremental CIFAR retains all earlier training data. | Eventually the incremental learner performs worse than a freshly trained comparison. | Earlier training can make a later matched learning problem harder, despite old-data availability. | Missing old examples cannot be the sole cause. Dormancy and representation statistics are not a unique causal explanation. Early transfer and some larger models improve. |
| [Zheng et al., ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/file/a774503daed55eb53c634847ae071ec7-Paper-Conference.pdf). Synthetic biographies, sequential weight updates. | Ordinary old-task answers deteriorate; training a recovery procedure restores substantial held-out performance. | Some old associations remain useful after poor ordinary retrieval. | Authors propose “loss of task alignment instead of underlying knowledge.” Recovery supports surviving information but uses old supervision and further learning. It does not establish autonomous or supervision-free access. |
| [Hernandez-Garcia et al., June 2026, preprint v1](https://arxiv.org/html/2606.24752v1). Continued language training; optimizer resets; discarded fixed-budget probe updates. | Later checkpoints eventually learn the probe less efficiently; larger models delay the onset. | Finite-budget adaptation can deteriorate even without stale optimizer state. | Neither permanent inability nor old-fact erasure follows. The uncertainty of the fitted onset exponent does not establish sublinear scaling conclusively; frontier extrapolation remains unsupported. |
| [Continual Learning Bench, June 2026, preprint v1](https://arxiv.org/html/2606.05661v1). Context/notes persist; some harnesses compact them; weights are unchanged. | Experience improves several domains, with uneven gains across task changes. | Available prior evidence is sometimes not applied; preserving context can help. | The authors' boundary “stability” measure also includes transfer to a changed variant. It cannot isolate erasure. Retrieval, content and reasoning are bundled. |
| [Lyle et al., CoLLAs 2024, PMLR 2025 published version](https://raw.githubusercontent.com/mlresearch/v274/main/assets/lyle25a/lyle25a.pdf). Controlled target offsets and relabelling schedules. | Task construction alters subsequent optimization; gradual change is relatively less damaging. | Histories with different offsets or suddenness yield different later learning curves. | These are causal manipulations within a restricted setting, not proof of a unique mediator. Even gradual relabelling can deteriorate. A shallower curve does not prove an unattainable solution. |

A stored record and a competent updater are different resources. Keeping all evidence does not ensure that a particular optimization process will use it well; losing an ordinary response does not show that the evidence's information vanished. A recovery procedure must disclose its old labels, external knowledge, parameter updates and computation. Otherwise the analyst can unknowingly provide the answer that appears to have survived.

### 2.4 Controlled recombination

| Study and prior structure | Reported outcome | Observed failure or success | Causal attribution supported, and limit |
|---|---|---|---|
| [COGS, EMNLP 2020](https://aclanthology.org/2020.emnlp-main.731.pdf). Supplied sentence/meaning pairs and grammar-generated holdouts. | Excellent ordinary fitting coexists with weak structural transfer; some lexical transfer succeeds. | Different held-out substitutions have different difficulty. | Exposure and output-length effects matter. Authors' proposed “stronger structural bias” is not a unique causal finding. The tested size sweep is not a scaling impossibility result. |
| [Lake and Baroni, Nature 2023](https://www.nature.com/articles/s41586-023-06668-3). Meta-learning and supplied support examples. | Lexical compositional transfer becomes strong; length and structural splits remain difficult. | The same broad neural family can succeed when the training regime changes. | Training support and objective have a causal role as a package. Useful ontology, examples and curriculum are supplied; their autonomous discovery remains untested. |
| [gSCAN, NeurIPS 2020](https://proceedings.neurips.cc/paper_files/paper/2020/file/e5a90182cc81e12ab5e72d66e0b46fe3-Paper.pdf). Full initial grid with encoded object properties; supervised actions. | Some action-class transfer succeeds; relative references and withheld directions fail. | A familiar object property may not be correctly used in a new relation. | Observed attention is not an intervention on representation. Grounded input here does not entail active discovery of the supplied categories. |
| [Redhardt et al., NeurIPS 2025](https://papers.nips.cc/paper_files/paper/2025/file/5047b64366bc0dbf5047de85f1e0c7be-Paper-Conference.pdf). Synthetic teacher functions and task encodings. | Scaling model size and training-task diversity improves withheld compositions under connected support. | Positive systematic transfer is possible; missing support changes identifiability. | This directly opposes a categorical no-composition premise. Observational decoding does not prove a necessary internal format; representability is not an SGD guarantee. |
| [Tong et al., ICLR 2026; April author version](https://arxiv.org/html/2604.15306v1). Random-walk pretraining includes every train and test map. | Shortest-path training transfers to maps seen only in random-walk pretraining; longer paths still degrade. | Separately solvable subpaths do not guarantee a correct whole path. | Authors call this “recursive instability,” but do not isolate internal recursion causally. Test maps are new to shortest-path training, not new to pretraining. |

The last study is published conference work with a deposited version inside the requested six-month window; the first public disclosure date was not established here. It is not labeled an unreviewed preprint simply because the accessible copy is on arXiv.

These contrasts make two claims untenable: that neural systems categorically cannot recombine, and that scale never helps. They do not establish reliable open-ended reuse after discovering an unknown ontology and surviving interference. The distinction is substantive: successful recombination of supplied relations cannot be silently credited as their discovery, and a failure on unsupported relations cannot automatically be blamed on recombination.

### 2.5 What the recent window changes

The May and June preprints above add interactive causal testing, stateful frontier evaluations and a measured scaling benefit for continued trainability. Earlier scouting also inspected [April 2026 reward-free web exploration](https://arxiv.org/html/2604.18131v1) and [August 2026 terminal-agent training](https://arxiv.org/html/2608.22631v2), both **preprints**, accessed 2026-09-06. They show useful gains under training and retained-memory packages, with unresolved attribution. They do not jointly test the funded conjunction.

A superficially congenial May preprint claiming a causal-discovery scaling barrier was excluded as support for that barrier: its stated kernel inequality has a direct counterexample, and its hypothetical queries do not acquire environmental observations. The narrow algebraic audit is `evidence/P1_CAUSAL_THEORY_AUDIT_2026-09-06.md`. This corrects a possible inference from the source; it is not evidence that every other result in the paper is false. [Audited preprint](https://arxiv.org/html/2605.27567v1), accessed 2026-09-06.

### 2.6 Integrated experience and positive real-world evidence

The methods audit deliberately sought successes that might overturn the leading diagnosis. All URLs below were accessed **2026-09-06**; source coverage and code-versus-paper qualifications are recorded in `evidence/P1_INTEGRATED_AGENT_CONTROLS_2026-09-06.md`, `evidence/P1_INTEGRATED_RECENT_2026-09-06.md` and `evidence/P1_REAL_WORLD_DISCOVERY_2026-09-06.md`.

| Study and declared surviving channel | Reported outcome | Observed capability or failure | What the contrast identifies |
|---|---|---|---|
| [CLIN, COLM 2024](https://www.cis.upenn.edu/~ccb/publications/clin-continual-learning-from-interactions.pdf): summaries across reset trials; frozen model. | Initial new-environment reward improves with transferred memory; later adaptation improves further. | Useful transfer, with harmful specific memories in some cases. | Memory-package utility. Related tasks share objects/locations; electricity tasks violating familiar conventions are excluded. Best later performance also includes relearning. |
| [Voyager, author v2 of subsequently published TMLR 2024 study](https://arxiv.org/html/2305.16291v2): learned code survives new world/inventory. | Transfer succeeds with the library; the no-library control already succeeds in eleven of twelve attempts. | Experience chiefly improves speed/reliability in this small comparison. | A legitimate surviving-channel benefit under familiar game semantics, not unfamiliar-law discovery or intact-but-unreadable knowledge. Final journal-version equality is unverified. |
| [Hu et al., April 2026, preprint v1](https://arxiv.org/html/2604.27003v1): external experiences across task phases. | Forward effects can be helpful or harmful; backward outcomes include gains. | Some retrieved prior experience promotes inappropriate actions. | Conditional interference; Appendix C admits retrieval timing and accumulated content co-vary. No unique retrieval mediator. |
| [SkillFlow, April 2026, preprint v1](https://arxiv.org/html/2604.17308v1): skill files/scripts persist within families. | Some agents improve, others regress. | Useful reuse across changed domains/formats, and executable/toolchain failures. | Workflow topology is deliberately fixed; heterogeneous interference is excluded. History-control prose/table disagree. Feedback includes post-task verifier information; the audited example does not establish hidden-test leakage. |
| [PATH-Bench, August 2026, preprint v1](https://arxiv.org/html/2608.01149v1): external state changes; the same task is probed without probe-driven memory updates. | Earlier gains can decline; effects differ by task domain. | A stronger longitudinal symptom than comparing two different tasks. | History effects, not verified storage loss. Filtering changes content and computation. Its clipped decline metric requires a stochastic null before being called erasure. |
| [Robin, Nature, May 2026 publication of work first posted in 2025](https://www.nature.com/articles/s41586-026-10652-y): continuing research records and new laboratory data. | Analyses inform further hypotheses and experiments. | Positive empirical feedback in a human-supported scientific project. | Humans supply protocols, execution and analysis prompts; no controlled interference/recombination test. The data-analysis comparator lacks the dataset and execution tools, so package gains cannot isolate reasoning. |

**Our causal judgment:** these results refute a categorical inability to acquire useful experience, preserve a declared channel and benefit later. They do not establish robustness across every combination of unfamiliar laws, interference and structural novelty. Nor do they jointly show that a useful relation was acquired, remained valid and recoverable, yet stopped controlling action in the same failed case. Joining one paper's successful memory with another paper's failed response would manufacture that causal chain.

The distinction is concrete in pinned code: CLIN can keep raw history on the host while providing only a recent portion to its actor; Voyager exposes retrieved descriptions to the model while making a broader code library executable. These are different access boundaries. Their existence does not prove that either caused a published error; released-code and result-producing configurations are not fully reconciled.

**Our metric check:** for independent unchanged Bernoulli performance measurements X and Y with success probability p, the expected clipped decline E[max(0,X−Y)] is p(1−p), although no learning occurred. This is an illustrative null, not an estimate of PATH-Bench's actual bias. Signed history effects can still be real. A nonzero clipped score alone cannot locate erasure. The full deduction and scope are in the recent-integrated note.

## 3. Our reproduction

### 3.1 A behavioural deficit is not sufficient evidence of erased information

The prospective design and full report are `docs/P1_REPRODUCTION_DESIGN.md` and `reports/P1_REPRODUCTION_001.md`. We ran an online linear action-response predictor, first in a visible context A and then in B. Its persistent learned state consists only of its weights. Both rules are expressible within the same model class; nevertheless, fitting B through shared features degrades the ordinary A readout. A fixed observer still recovers the earlier estimate from a parameter difference. Crossing old and new gains and inspecting decoder inputs rule out a hardcoded target as the explanation.

For the illustrative opposite-gain case, the ordinary old prediction changes sign during B learning, while the observer's recovered estimate retains the old sign. The frozen control preserves the old prediction without learning B; the orthogonal control fits B while preserving A. These are observed properties of this construction, not a model ranking. Full values and every transition: `artifacts/P1_LINEAR_INTERFERENCE/20260906_001/results.json`, SHA-256 `837b6ce92176182d1e2878f585388824d3b0173d2585e69c749243ac0a626762`; `artifacts/P1_LINEAR_INTERFERENCE/20260906_001/transitions.jsonl`, SHA-256 `908f4b073a63a0c7019fe65173b461a2fc7f7ad0b51d68f05e7cfc083308a3a4`. Local access 2026-09-06. The report gives an explicitly cited numerical table and the loss-change decomposition.

**Attribution:** equal changes to the shared coordinates move the prescribed old readout but preserve their difference. The first B update can begin worsening old error; a later sign error is not irreversible loss, because the old estimate remains recoverable in the observed trace. There is therefore no irreversible information-loss point to report. An analyst who equates the first failed behavioural probe with erasure would misdiagnose this system.

**Scope:** this is a deliberately simple sequential fitting subproblem. A noiseless response already identifies its context gain; the learner's slow gradient fitting is imposed, not an environmental necessity. Context labels, feature geometry and initialization are supplied. The observer's geometric knowledge is also supplied and is not a learned capability. Exploration, causal-variable discovery, novel recombination, repeated context cycles, realistic noise and frontier models remain untested. The orthogonal control changes the optimization metric and B initialization even though feature norms and representational capacity are matched. It is an explanatory control, not a proposed repair.

This reproduction supports a distinction necessary for the diagnosis. It does not establish the prevalence of hidden recoverability in current large systems or determine the programme's bottleneck ranking. Its arithmetic audit is an artifact-consistency check, not an independent scientific verdict.

## 4. Interdisciplinary constraints

### 4.1 What biology does and does not establish

Biology supplies constraints on an explanation of competence, not validation of an artificial design. The useful question is which variable persists, through which process, and what later behaviour that persistence supports. All sources in this section are published work and all links were accessed **2026-09-06**. Detailed methods and limits are in `evidence/SCOUT_BIOLOGY_2026-09-06.md`, the corrected Ryan note, and `evidence/P1_BIOLOGICAL_CONSTRAINTS_2026-09-06.md`.

| Biological evidence and class | Computational constraint suggested | What it does not establish |
|---|---|---|
| [Schulz and Bonawitz, 2007](https://eccl.scripts.mit.edu/papers/bonawitzandschulzseriousfun.pdf). Human behavioural manipulation of confounded evidence. | Exploration can depend on what remains ambiguous, rather than novelty alone. | The authors explicitly did not test whether the children learned the causal relation. Informative action and acquired knowledge are different outcomes. |
| [Taylor et al., 2014](https://www.alisongopnik.com/Papers_Alison/Taylor%20et%20al%20Proceedings.pdf). Crow and toddler action-transfer experiments. | Observing an effect, executing a shaped action and spontaneously generating a changed action make different demands. | Different success rates do not identify a unique causal representation or a general species ordering. Prior experience, affordances and exclusions matter. The later interpretive dispute remains unadjudicated. |
| [Ryan et al., Science 2015](https://doi.org/10.1126/science.aaa5542), with [deposited supplement](https://www.ebi.ac.uk/biostudies/studies/S-EPMC5583719). Mouse intervention plus neural measurements. | An impaired natural retrieval route can coexist with an artificially evoked, experience-dependent response. | No complete episodic inventory, unique storage substrate or normal autonomous recovery is established. A recording of connectivity is not itself a causal storage test. |
| [Hammarlund et al., 2017](https://www.nature.com/articles/s41467-017-01901-w). Rhesus intervention and longitudinal immune measurements. | Short-lived outputs can be maintained by long-lived production capability. | Antibody persistence does not show wholesale replacement of memory-carrying cells, nor causal world modelling. Depletion and tissue sampling are incomplete constraints. |
| [Beisson and Sonneborn, 1965](https://pmc.ncbi.nlm.nih.gov/articles/PMC219507/). Ciliate grafting and lineage microscopy. | Spatial arrangement can be an inherited state variable. | Reversion and lineage selection qualify persistence. Molecular replacement was not inventoried; a surgically imposed pattern is not learned causal knowledge. |
| [Goehring et al., 2011](https://doi.org/10.1083/jcb.201011094). Embryonic-cell imaging and perturbation. | A stable spatial distribution can coexist with movement and exchange of its members. | Exchange with a surviving cytoplasm is not destruction and resynthesis of every carrier. Developmental organization remains supplied. |
| [Lambert and Kussell, 2014](https://doi.org/10.1371/journal.pgen.1004556). Bacterial environmental switches, reporters and expression interventions. | History effects can depend on residual physiological capacity and expire through dilution. | The organism did not invent its metabolic response system. A growth-lag assay does not establish arbitrary rule learning or recombination. |
| [Boussard et al., 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC6553583/). Slime-mould salt exposure, dormancy, chemical assay and induction. | Stopping activity need not remove the material carrying a history effect. Different behavioural readouts can dissociate. | Inducing expansion without the corresponding latency change is incomplete restoration. Dormancy is not erasure, and salt carry-over is not an acquired world model. |

**Correction retained:** the early categorical description of Ryan's encoding controls was too strong. The supplied paper and deposited supplement support the narrower experience-dependent dissociation above; version and schedule qualifications remain in `evidence/RYAN_SUPPLIED_METHODS_2026-09-06.md`. Our linear trace and this mouse intervention have different assumptions. Their agreement about what a failed behavioural probe cannot prove does not establish a shared biological mechanism.

### 4.2 Constraints on the diagnosis, rather than anatomical analogies

**First, preservation is functional and relational.** A system need not keep every microscopic component unchanged to preserve a useful response. It must keep some causal route by which the earlier history changes the later decision. That route can depend on an arrangement, an existing carrier population or a latent distinction accessed by a different cue. The mathematical state inventory must therefore include relations and surrounding persistent state, not only a count of components.

**Second, all discontinuities are selective.** Removing a stimulus leaves an organism, its chemistry and evolved regulation. Clearing a conversation can leave weights and files. Neither is equivalent to deleting every experience-dependent variable. Comparisons that give biology surviving organization while describing the artificial system as completely cleared have changed the information problem. The reviewed studies constrain such comparisons; they do not prove that current AI universally violates a particular biological rule.

**Third, the acquisition budget includes pre-existing structure.** The last few exposures may adjust a response supported by extensive development or evolution. Those exposures cannot fairly be compared with an artificial learner required to discover the action interface and useful variables from scratch. Conversely, broad AI pretraining is a real prior and must not disappear from its accounting either.

**Fourth, successful expression and useful knowledge need separate tests.** A response induced by an experimenter can show that some history dependence remains without showing that the organism can select it appropriately. Exploration can be informative without measured learning. A population-average physiological advantage can occur without each individual representing a causal rule. These distinctions prevent a biological success from being silently enlarged into the whole funded demand.

My present conclusion is that biology strongly motivates careful state, access and prior accounting. It does not yet supply evidence for one missing operation that explains the artificial failures. The broad “humans and animals do this easily” premise is not an established result of this review.

### 4.3 Positive relational reuse, with acquisition and use separated

The earlier biology pass emphasized persistence qualifications more heavily than positive acquisition and reuse. That imbalance is corrected here. These **published animal/human interventions** come from overlapping collaborators, not three independent replications. All links accessed **2026-09-06**; complete reading coverage is in `evidence/P1_BIOLOGICAL_REUSE_2026-09-06.md`.

| Study | Positive result and timing | Constraint and limit |
|---|---|---|
| [Sharpe et al., 2017](https://doi.org/10.1038/nn.4538) | Initially unrewarded rat cue relationships later support responding sensitive to outcome devaluation; dopamine perturbations during initial transitions change later behavior. | Acquisition before established appetitive utility is possible. Short cue chains, broad interventions and a small devaluation contrast do not identify all integration timing. |
| [Hart et al., 2020](https://doi.org/10.7554/eLife.59998) | Inhibiting OFC during initially unrewarded pairings impairs later inferred responding, without significant direct-conditioning impairment. | An early-stage perturbation can cause a later reuse deficit. Prior food-cup shaping, attention and context remain relevant; this is not a demonstrated unique storage substrate. |
| [Wang et al., 2020](https://doi.org/10.1523/JNEUROSCI.1680-20.2020) | Human participants combine learned symbol pairs with later odor outcomes; post-learning stimulation impairs inferred predictions. | Later processing matters, but subjects were explicitly instructed to infer. A nonsignificant recognition-memory difference does not exclude memory mediation. |

**Jones source resolution.** The newly supplied [Jones et al., Science 2012 main article](https://doi.org/10.1126/science.1227489), read with both figures on **2026-09-06**, reports a late OFC-inactivation effect on responding to indirectly reward-associated cues, with directly trained responding relatively spared. Its blocking experiment also reports an effect during subsequent compound learning. The separate Supporting Online Material remains unavailable. Exact exclusions, infusion details, subset history and its argument against mediated learning are unverified. Accordingly, I use this as main-article evidence of a later processing dependency, not proof that intact component memories are uniquely recombined online. No new biological comparison with AI follows. `evidence/JONES_SUPPLIED_METHODS_2026-09-06.md` records the procedures actually readable, source hash, controls and limitations.

These experiments show useful relations learned before their eventual outcome significance, within a continuing organism and a small supplied grammar. They contain no matched modern-AI comparison, substantial unrelated interference, or wholesale state reset. Nevertheless, dismissing their competence because some priors and instructions are supplied would be as unfair as dismissing declared AI memory gains.

The diagnostic constraint is functional: when a later goal depends on an earlier relation, some information distinguishing that relation must survive and affect behavior. A response never rewarded during initial exposure is meaningful reuse; it does not by itself prove that all composition occurred online at the final probe. Perturbation timing helps separate acquisition and use, but does not identify every mediator.

### 4.4 Control and system identification expose an earlier failure location

[Klenske and Hennig, JMLR 2016](https://www.jmlr.org/papers/volume17/15-162/15-162.pdf) and [Simpkins et al., ACC 2008](https://roboti.us/lab/papers/SimpkinsACC08.pdf), accessed **2026-09-06**, make action-dependent information explicit within supplied model families. Movement or excitation determines which unknown coefficients observations constrain. A one-step task criterion can therefore choose actions whose data leave a later-relevant distinction unknown. This is theory plus restricted numerical evidence; Simpkins' small preliminary human comparison does not establish general biological optimality.

Our scalar derivation makes the boundary clear: with observation y=bu+noise and known positive Gaussian noise variance Q, Gaussian posterior precision increases by u²/Q. At u=0 it receives no information about b. An allowed informative action may still be too costly to justify. The failure claim begins only when its expected decision benefit matters within the permitted horizon and budget. Detailed assumptions and refuters are in `evidence/P1_ACTIVE_IDENTIFICATION_2026-09-06.md`; the full six-page Simpkins audit has a separate note.

## 5. Archaeology

### 5.1 What was set aside, and what actually expired?

The unit of analysis is a particular operation or assumption, not an era. A community can reject an expensive implementation while continuing to pursue its objective. The following judgments combine the initial archaeology, supplied Drescher/Minton methods and `evidence/P1_ARCHAEOLOGY_DEEPENING_2026-09-06.md`. All linked sources were accessed **2026-09-06**. These are historical evidence, not proposed repairs or a novelty audit.

| Line and primary source | Documented restriction or reason for revision | Does that reason hold in 2026? |
|---|---|---|
| [Drescher's schema mechanism, 1987 dissertation](https://dspace.mit.edu/handle/1721.1/77702) | Supplied sensory/action primitives; expanding schema/item bookkeeping exhausted the reported memory budget before complete development. This documents an implementation limit, not why a whole community stopped. | The old machine's capacity is not a present bound. Growth and credit-assignment demands remain; no modern resource-accounted reproduction establishes where the limit now falls. Later continuations prevent calling the lineage wholly abandoned. |
| [Minton's explanation-based learning, 1990](https://doi.org/10.1016/0004-3702(90)90059-9) | Retained control rules can save search yet cost more to match than they save. The explanation theory is supplied. Utility selection addresses an observed application-cost problem. | Raw storage expansion does not itself reduce the work of finding applicable knowledge. Modern indexing and workloads could change the balance; present end-to-end costs are unmeasured here. Supplied theory remains an acquisition assumption. |
| [MAC/FAC analogical retrieval, 1995](https://groups.psych.northwestern.edu/gentner/papers/ForbusGentnerLaw94.2b.pdf) | The authors rejected an earlier match network per memory item on timing/computation grounds. The replacement's first filter omits argument bindings. | Hardware changes feasible comparison volume. It does not restore relational distinctions absent from that filter's input. Whether they matter in a particular task is empirical. This is revision within analogy research, not proof that analogy was abandoned. |
| [SME lineage, documented in Forbus et al., 2017](https://groups.psych.northwestern.edu/gentner/papers/ForbusFergusonLovett%26Gentner_2017.pdf) | Early restrictions included exhaustive merging, small comparisons and hand-built descriptions. Later versions replaced exhaustive with greedy merging and instrumented larger corpora. | The blanket exhaustive-enumeration objection **has expired for the revised implementation**. This happened through algorithm development. Worst-case bounds overstated many measured intermediate sizes. Search optimality and acquiring useful descriptions remain separate questions. |
| [Classifier systems: Wilson, 1995](https://www.eskimo.com/~wilson/ps/xcs.pdf); [Holmes et al. historical manuscript](https://www.eskimo.com/~wilson/ps/ipl2000.ps.gz) | Participant testimony links decline to complicated systems and few successful applications, followed by revival through simpler models. Wilson analyzes a payoff criterion that can conflate accurate and overgeneral rules. | The claim that the whole family lacks analyzable alternatives was already outdated in the revival account. Extra compute alone does not change an uninformative criterion. The XCS comparison also changes action selection, limiting fitness-only attribution. |
| [Version spaces: Hirsh, 1994](https://link.springer.com/content/pdf/10.1023/A%3A1022600917598.pdf) | Strict consistency can empty the feasible hypothesis set under noise or misspecification. The extension changes the assumed observation neighborhoods, with ambiguity and cost tradeoffs. | “Cannot handle any inconsistent observations” was already too broad in that paper. Unchanged contradictory constraints remain contradictory regardless of compute. No defensible community-wide abandonment cause was established. |
| [Dual control: Simpkins et al., 2008](https://roboti.us/lab/papers/SimpkinsACC08.pdf), with the [1973-lineage revisit by Klenske and Hennig, 2016](https://www.jmlr.org/papers/volume17/15-162/15-162.pdf) | Planning must account for how actions change later uncertainty, expanding the computational state. Both papers pursue approximations; the later paper reports limited attention to the older expansion. | Continued research contradicts wholesale abandonment. More compute changes feasible approximations, not their accuracy guarantees or supplied model/goal assumptions. No measured 2026 hardware-only removal of the relevant cost is established. |

The Holmes source is an **author manuscript/preprint** of work subsequently published in 2002; publisher wording was not verified. Its history is testimony from participants with an advocacy interest, not measured causal attribution across the field. The SME source is a later primary account of changes to an older system; this is why it legitimately informs the 1960–2010 archaeology.

The earlier pass also examined adaptive resonance, expensive production chunks and qualitative process reasoning. Their scope distinctions remain important: a category-stability result under supplied features is not discovery of world variables; branching partial matches can be costly even with short rules; and qualitative conclusions depend on an adequate supplied ontology. The source-level accounts and continued-work checks remain in `evidence/SCOUT_ARCHAEOLOGY_2026-09-06.md`. These lines are neither endorsed nor dismissed as families.

### 5.2 Corrections that change the historical diagnosis

**Drescher:** the supplied thesis includes predictive maintenance and resolution of competing evidence. A description of the original as duration-only would be false. A later comparator cannot be treated as a faithful implementation without checking its update semantics. Relevant thesis sections, rather than the entire dissertation, were read. `evidence/DRESCHER_SUPPLIED_METHODS_2026-09-06.md` preserves the exact scope and correction. [Thesis §§3.4.3, 4.3 and 6](https://dspace.mit.edu/handle/1721.1/77702), accessed 2026-09-06.

**Minton:** later utility validation remeasures matching cost and use frequency while retaining the original example's savings estimate. It does not measure the entire lifetime cost of learning and using the rules. The result diagnoses useful reformulation under supplied explanatory knowledge. `evidence/MINTON_SUPPLIED_METHODS_2026-09-06.md` preserves this qualification. [Published article §§4–8](https://doi.org/10.1016/0004-3702(90)90059-9), accessed 2026-09-06.

### 5.3 What the archaeology contributes to the causal account

Several old problems concern **which distinctions a learning criterion can reward**, **which stored relation the access procedure can find**, and **what it costs to apply knowledge**. None reduces automatically to storage capacity. If a rule selection statistic assigns the same value to a reliable narrow rule and an unreliable broad rule, additional repetitions do not by themselves make that statistic discriminate reliability. If a candidate is excluded before structural comparison, improving only the later comparison cannot retrieve it. These are conditional consequences of the specified operations; their prevalence in current systems is unmeasured.

There is also an important correction to my earlier cross-era caution. “Combinatorial growth remains” is true but insufficient. Later SME measurements show why a worst-case objection can misidentify practical cost, and the old exhaustive operation was actually replaced. The correct question is what the implemented version does on a specified workload, including the cost of constructing its inputs.

I have not established a hardware-only resurrection with matched present-day measurements. That remains unresolved; I will not manufacture an expired reason to make the archaeology more attractive. What is established is that some objections expired through continued work, some address unchanged information assumptions, and some old resource constraints require measurement on today's hardware. An old failure is evidence about its conditions, not a refutation of its objective.

## 6. Ranked bottlenecks

### 6.1 How to read this ranking

This is a ranking of **current priorities for causal investigation**, weighing connection to the funded demand, explanatory specificity and available evidence. It is not a measured ordering of prevalence across AI, or a ranking of proposed repairs. Confidence in a local cause and confidence that it explains the broader phenomenon are stated separately. The ranking can change as contrary evidence arrives.

**Ranking correction:** checkpoint003 placed our best-instrumented local cause first. That overweighted certainty within the witness relative to relevance to the full demand. Selection of an inappropriate relation now comes first; failure to obtain useful distinguishing evidence is second; disrupted expression of a surviving relation is third. History-dependent trainability is fourth, evidence commitment fifth, and access cost sixth. None is established as the dominant cause across current AI. The two acquisition priorities have different counterfactuals: change which observations are obtained versus change what is learned from adequate observations.

The numbered entries are falsifiable **attributions to declared cases**, not propositions that no conceivable system can ever exhibit the stated effect. Where a witness establishes existence, a failed attribution to another agent does not refute that witness. The object of each refuter is the claimed explanation of a particular failure under specified evidence, state and budget.

| Priority | What is established within inspected conditions | Unresolved attribution or extension |
|---|---|---|
| 1: relation selection | Exposure/support and training packages change generalization. | An inappropriate selected relation mediates the relevant structural failures; the package contrasts do not uniquely identify it. |
| 2: evidence acquisition | In supplied control models, actions determine which unknown distinctions become identifiable. | This explains a consequential share of strong unfamiliar-world agent failures. |
| 3: retained information, disrupted expression | Our complete toy trace identifies this cause; larger recovery results support conditional survival. | The same cause governs integrated agent decline, with affordable autonomous access. |
| 4: later trainability | Particular learning histories worsen subsequent finite-budget fitting. | The mediator across systems and the extent to which scale changes the useful learning horizon remain unresolved. |
| 5: evidence commitment | A benchmark reports inconsistency and a beneficial procedure change. | Commitment rather than computation, interface or scoring causes the reported deficit. |
| 6: access cost | Historical systems exhibit search-saving/application-cost tradeoffs. | Valid retained information is excluded by access cost in a relevant modern workload. |

The order is my scientific judgment about which uncertainties most directly bear on the funded demand. It is not an empirical finding that the first two explain more failures or will yield better repairs. The detailed supporting and opposing sources follow with each entry.

There is a prerequisite that should not be mistaken for a bottleneck in a particular algorithm. If permitted evidence cannot distinguish two worlds requiring different actions, uncertainty is unavoidable. No architecture has thereby failed. The empirical question starts when distinguishing evidence is obtainable, or when the restricted future demand is already identified. This condition applies to every claim below.

### 6.2 Rank 1 — training can select relations that fit present evidence but are inappropriate under the intended reuse

**Falsifiable causal claim.** At fixed representational capacity, the distribution and objective of training can favor a predictor tied to co-occurrences, output lengths or local roles that cease to hold at reuse. Where the relevant distinction is identifiable, failure can arise from what learning selects, before interference or retrieval becomes necessary. Merely showing that all primitive names appeared in training does not establish that their reusable relations were learned.

**Evidence for.** Controlled changes to exposure and support affect COGS and meta-learning outcomes; lexical success coexists with structural or length failure. [COGS](https://aclanthology.org/2020.emnlp-main.731.pdf), [Lake and Baroni, 2023](https://www.nature.com/articles/s41586-023-06668-3), accessed 2026-09-06. Historical rule-selection work provides an explicit example of a criterion conflating differently reliable rules, but not a proven shared neural mechanism. [Wilson, 1995](https://www.eskimo.com/~wilson/ps/xcs.pdf), accessed 2026-09-06.

**Evidence against / live alternative.** Broader task support and scale can produce compositional transfer. [Redhardt et al., 2025](https://arxiv.org/html/2507.07207v2), accessed 2026-09-06. A failure may instead reflect non-identifiability, insufficient optimization or faulty use of a relation that was learned correctly. Training packages often change more than one factor, so they do not identify a unique internal representation.

**Refuter.** With identifiable, equally accessible evidence and successful fitting, varying the implicated co-occurrences or selection objective leaves the deficit unchanged, while an isolated downstream factor explains it. Evidence that the learner already possesses and can apply the required invariant relation before a later access failure would also move that case out of this account.

**Unchecked prediction.** Two equally rare held-out substitutions can have sharply different outcomes depending on whether the rewarded training relation remains valid. A more diverse but no larger training set can sometimes change that ordering; a parameter-only increase may not. This is a conditional prediction, not a claim that data diversity always beats scale.

**Confidence and what would raise it.** Moderate for training-support effects in the inspected families; low-to-moderate for the proposed mediation through an inappropriate selected relation. A controlled intervention linking training variation to the specific learned distinction and then to held-out behaviour would raise confidence. The key unresolved extension is discovery of the useful variables themselves, which many benchmarks supply.

### 6.3 Rank 2 — actions chosen for current performance can fail to obtain evidence needed for later decisions

**Falsifiable causal claim.** In an identifiable world family, a policy that neglects the later decision value of observations can select a history under which relevant alternatives remain indistinguishable, despite affordable actions that would distinguish them. The failure originates in the action-to-evidence dependency, before any allegedly forgotten relation was acquired. More accurate fitting of the resulting uninformative data cannot repair that particular absence.

**Evidence for.** The supplied-model control examples isolate this dependency mathematically; Simpkins also contrasts movement/estimation behavior under different control criteria. [Simpkins et al., 2008](https://roboti.us/lab/papers/SimpkinsACC08.pdf), [Klenske and Hennig, 2016](https://www.jmlr.org/papers/volume17/15-162/15-162.pdf), accessed 2026-09-06. Our precision derivation is in §4.4. Biological preconditioning shows why usefulness need not be revealed at initial exposure, but does not measure this artificial failure.

**Evidence against / live alternative.** AdA and Robin demonstrate useful acquisition under their support (§§2.2, 2.6). A task may offer no worthwhile experiment, the model family may be wrong, or adequate observations may already exist and be misused. Classical control commonly supplies future costs and variables. Its specific criterion is not known to describe a contemporary language agent. Calling every poor exploration trace myopic would exceed the evidence.

**Refuter.** Actual accessible observations already distinguish the required decision under the allowed priors, or no permitted affordable action could improve it. If correcting evidence availability leaves the deficit while an isolated downstream operation explains it, acquisition is not the relevant cause for that case.

**Unchecked prediction.** Two policies can have comparable initial task performance yet diverge later because their early action distributions identify different decision-relevant distinctions. That divergence should be explained by the actual evidence acquired, rather than an extra hint, larger state allowance or different future goal disclosure.

**Confidence and what would raise it.** High for the conditional information dependency; low for dominance in strong integrated agents. This is second as an investigative priority because the funded problem begins with selected interaction and the previous ranking largely began after data were available. A modern trace linking missed affordable discrimination to a consequential later error would raise empirical confidence. If that evidence remains absent, this must stay a conditional alternative rather than a claimed general diagnosis.

### 6.4 Rank 3 — subsequent updates can disrupt the usable expression of a retained distinction

**Falsifiable causal claim.** In some sequentially trained systems, updates needed for the new task move the input-to-answer mapping for an older, still-valid relation, even though a history-dependent distinction sufficient for that older answer survives elsewhere in the resulting state. Behaviour deteriorates because the prescribed use of the state changes incompatibly with what the state still contains. This is a stronger and narrower claim than “systems forget.”

**Evidence for.** Our reproduction identifies the update direction and the old readout it moves, while a fixed parameter difference preserves the old estimate. The artifact citations and exact scope are in §3. The language-model recovery study supplies larger-scale evidence compatible with surviving old associations, though its recovery uses old supervision. [Zheng et al., ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/file/a774503daed55eb53c634847ae071ec7-Paper-Conference.pdf), accessed 2026-09-06. The analogy is inferential; the studies do not establish the same internal cause.

**Evidence against / live alternative.** Genuine erasure, a changed world, or absence of acquisition can explain other old-task deficits. Our witness's observer is supplied with the feature geometry. Recovery training in the larger study may reconstruct some associations rather than merely expose them. Evidence for surviving information is not evidence for cheap, appropriate access by the acting system.

**Refuter.** Under a declared recovery class that cannot import withheld old answers, the supposedly informed state provides no benefit over a matched state that never saw those answers, while acquisition and recovery controls work. That would undermine the retained-distinction account for that recovery class. Alternatively, if the old relation reaches the action process in usable form and the failure occurs afterwards, the claimed location is wrong. No finite set of failed decoders proves information absence under every imaginable decoder.

**Unchecked prediction.** The same post-interference state should support different outcomes under semantically equivalent old-task probes, with some failures localized to the conversion from surviving information into the required response. This must persist after accounting for extra evidence or computation in the successful probe.

**Confidence and what would raise it.** High for the constructed witness; moderate for substantial survival in the biography setting; low for prevalence in strong interactive agents. A controlled recovery contrast after actual world learning, with no restored history or leaked old answers and matched computation, would raise the last assessment. Its demotion concerns programme relevance, not the validity of the witness. CLIN, Voyager and the recent external-memory studies do not connect verified surviving knowledge to failed expression after interference in the same case (§2.6).

### 6.5 Rank 4 — learning history can make later updates less effective even when evidence and representational capacity remain available

**Falsifiable causal claim.** The state produced by earlier optimization can be a worse starting point for later fitting than a suitable comparison state, under a declared update budget. The deficit can arise from history-dependent optimization, rather than lack of old examples or an inability of the model class to express the solution. This concerns the efficiency of changing knowledge, not necessarily preservation of old knowledge.

**Evidence for.** The retained-data comparison, fresh-optimizer probes and controlled changes to target offset or task suddenness rule out several simple sole causes. [Dohare et al., 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC11338828/), [Lyle et al., published version](https://raw.githubusercontent.com/mlresearch/v274/main/assets/lyle25a/lyle25a.pdf), accessed 2026-09-06. These establish effects of particular histories and task constructions; they do not select one universal mediator among conditioning, representation change and other properties.

**Evidence against / live alternative.** Early learning often transfers positively, increased width or scale helps some settings, and some degraded learning curves could eventually reach the same solution. A validation deficit can reflect generalization rather than failed optimization. The recent language-model scaling work measures a finite-budget probe and changing transfer, not an irreversible limit. [June 2026 preprint](https://arxiv.org/html/2606.24752v1), accessed 2026-09-06.

**Refuter.** After matching the relevant evidence, initial difficulty and update allowance, the alleged disadvantage of the old state disappears. If only validation performance deteriorates while the required fitting proceeds normally, the optimization attribution needs revision. Sufficient additional fitting reaching the prior attainable error refutes permanent inability, although a finite-budget slowdown can remain consequential.

**Unchecked prediction.** Some histories will preserve old responses while making new learning inefficient; others will disrupt old responses without comparable new-learning slowdown. This dissociation should survive accounting for initialization error and task transfer if plasticity loss and forgetting are separate causes.

**Confidence and what would raise it.** Moderate-to-high for history-dependent finite-budget deterioration in the tested systems; low for a universal mediator or unavoidable frontier-scale failure. Controlled learning curves and interventions that isolate the responsible state variable, across matched histories, would raise the mechanistic assessment. A correlation drifting with training time is insufficient.

### 6.6 Rank 5 — an agent can close its evidence-gathering loop before reconciling its answer with evidence already available

**Falsifiable causal claim.** In some interactive configurations, the commitment procedure permits an answer that contradicts available observations and ends further inquiry. The failure therefore need not originate in exhausted experimental access or absent stored data. It may arise in the procedure governing when an interpretation becomes an action.

**Evidence for.** CausaLab reports inconsistent final hypotheses and improvement after a verification intervention. Its printed interface makes entry into the reactor consequential for further experimentation. [May 2026 preprint, §§3–5 and Appendix A](https://arxiv.org/html/2605.26029v2), accessed 2026-09-06. This supports a candidate location and a whole-procedure effect, not a unique mental state called overconfidence.

**Evidence against / live alternative.** Extra computation, record copying, arithmetic, restrictive prompt instructions and post-run scoring can explain part of the contrast. An unneeded global causal edge may be irrelevant to the assigned decision. A released metric can interrogate a model separately from its acting trajectory. Exact table and validation-run provenance remain unresolved; see `evidence/P1_CAUSALAB_METRIC_AUDIT_2026-09-06.md`.

**Refuter.** The alleged inconsistency disappears when actual accessible measurements and action-time outputs are reconstructed, or equal-budget reconsideration explains the entire reported intervention effect. If no permitted experiment could alter the decision, early stopping alone is not the claimed defect. If a correct interpretation was available but execution failed later, this attribution is misplaced.

**Unchecked prediction.** Some failed episodes should already contain a decision-relevant contradiction before the action that closes further inquiry. Their failure rate should depend on the commitment rule even when observation content and inference allowance are held fixed.

**Confidence and what would raise it.** Low-to-moderate for this particular protocol; low for generalization. Raw action-time evidence, exact scoring provenance and an equal-computation contrast would raise confidence. This is ranked below the more controlled effects because an author's explanation of a trace is not yet a causal isolation.

### 6.7 Rank 6 — retained knowledge can be unusable because access and application consume the decision budget

**Falsifiable causal claim.** Enlarging a retained knowledge collection can reduce performance when matching or applying candidates consumes the budget before the relevant relation affects the decision. The collection may contain more correct information while the acting system obtains less useful information in time. The causal issue is the cost and selectivity of use, rather than whether storage succeeded.

**Evidence for.** Minton measures the tradeoff between search saved and rule-application cost. MAC/FAC specifies an earlier access filter distinct from later relational comparison. [Minton, 1990](https://doi.org/10.1016/0004-3702(90)90059-9), [MAC/FAC, 1995](https://groups.psych.northwestern.edu/gentner/papers/ForbusGentnerLaw94.2b.pdf), accessed 2026-09-06. These establish concrete old computational issues, not present prevalence. Minton's validation ablation also changes the resulting knowledge and later learning; it does not isolate a modern fixed-budget exclusion of otherwise valid information.

**Evidence against / live alternative.** Retained context improves many current tasks. Memory-package comparisons alter content, retrieval and reasoning together, so an observed loss can be misinformation or changed instructions rather than access cost. Later SME measurements show why worst-case matching arguments can exaggerate practical limitations. [Continual Learning Bench, June 2026 preprint](https://arxiv.org/html/2606.05661v1), [SME extension, 2017](https://groups.psych.northwestern.edu/gentner/papers/ForbusFergusonLovett%26Gentner_2017.pdf), accessed 2026-09-06.

**Refuter.** Relevant information reaches the decision process with comparable cost and adequate remaining budget, yet the deficit persists; or enlarging the collection has no predicted cost/selectivity effect under controlled content. That would shift explanation to interpretation or execution for that case.

**Unchecked prediction.** Adding valid but currently irrelevant knowledge can worsen performance under a fixed decision budget, with a measured delay or exclusion at the access stage preceding the wrong action. The prediction is stronger than observing that a longer prompt performs worse.

**Confidence and what would raise it.** High that the historical cost phenomenon exists under its conditions; low that it dominates the funded category today. A present workload tracing candidate access, computation and final decisions with content held valid would raise confidence. Modern hardware measurements could either strengthen this priority or remove the practical obstacle.

### 6.8 Why a single cause is not yet justified

These claims have different counterfactuals. Protecting the literal old state would not make unidentified relations identifiable, nor make an incorrect learned relation valid. Preserving old answers need not preserve the capacity to learn new ones. Adding more evidence cannot help a decision process that fails to read or reconcile it within its budget. Conversely, none of those deductions shows that a particular existing system fails for that reason.

The common issue is the dependence of later decisions on earlier experience under changed conditions. That describes the scientific target, not its mechanism. Turning it into a single “knowledge management” faculty would merely rename the original question. The integrated audit has narrowed the claim without establishing a dominant cause. A completed Phase1 diagnosis may legitimately retain that uncertainty; it must not pretend that more literature alone will supply an unavailable causal intervention.

## 7. The hypothesis we were handed

The retain / protect / suppress / recompose framing points at important functions, but is too permissive to serve as the leading causal explanation. If any failure to learn, remember or act is called a plasticity-control failure, nothing could refute it. It has to name which existing operation makes which relevant distinction unavailable or ineffective.

**Where it sits after correction.** Update-related disruption is now third and history-dependent trainability fourth. Their local evidence remains intact, but the stronger integrated agents do not establish the first effect's dominance. Frozen-backbone systems can also benefit or suffer from changing external records; relabeling every such change as neural plasticity would erase the distinction being tested.

The first two priorities point earlier: learning may select a relation unsuitable for reuse, or action selection may never obtain the evidence needed to establish it. The fifth concerns commitment and reconciliation; the sixth concerns access cost. These cannot be explained merely by assigning them to “suppress” or “recompose.” The handed framing presupposes useful pieces and their relevant conditions; discovering those distinctions is part of the question.

**What would support a narrower plasticity account?** The required relation is demonstrably acquired, remains true and matters to the new decision; the failure follows intervening updates; and a controlled diagnostic intervention attributes it to how those updates change useful state or its expression. Competing information, objective and execution explanations would have to be excluded in that case. This is a criterion for causal evidence, not a proposed controller.

**What would move the diagnosis elsewhere?** Failures occurring before suitable distinctions are acquired, or with unchanged usable knowledge that is incorrectly interpreted or executed, would weaken plasticity as the dominant explanation. Strong matched successes from scaling or training support would also narrow where a new operation is needed. Those successes already exist in restricted families, so “scaling does not close the gap” cannot remain a general premise.

My current judgment is therefore: retain plasticity as a serious, conditional line of diagnosis, but reject it as an established unifying account. The evidence requires establishing what was acquired and how it remained usable before assigning a failure to protection of stored content. My decision to give the two acquisition hypotheses investigative priority is a judgment under uncertainty, not a measured comparison of their prevalence with plasticity failures.

## 8. What remains unresolved

### 8.1 Questions that could change the diagnosis

| Unresolved question | Consequence and required evidence |
|---|---|
| Which acquisition cause governs unfamiliar-world failures? | Action-time observations, allowed experiments and initial priors must distinguish missing information from selection or misuse of adequate information. Training-package sensitivity does not identify the selected-relation mediator. Old control examples identify a precise conditional cause, not present-agent prevalence. |
| Does retained-information/readout disruption explain integrated decline? | The same case must show acquisition, continuing validity, surviving information and failed access/use. A memory-package gain and an unrelated endpoint deficit cannot establish this chain. |
| How broad is biological acquisition before later utility? | The verified cue-learning studies establish a bounded positive result. Tolman–Honzik's original work remains unavailable after the funder's search; active maze acquisition is not imported from textbook retellings. Jones' source coverage and remaining interpretation limits are recorded in §4.3 and its methods note. |
| How much of scientific-agent failure belongs to its interface or scoring? | Exact result-producing prompts, acting trajectories and scorer versions remain necessary for stronger CausaLab attribution. Robin's positive empirical loop does not isolate autonomy or equal-evidence reasoning. |
| Which scaling/resource conclusions generalize? | Positive scaling benefits are established in restricted families. Useful-horizon extrapolation and modern end-to-end costs for old operations remain unmeasured. Neither a historical machine limit nor worst-case growth decides present practical cost. |

### 8.2 Why I am submitting this diagnosis

The methods and consistency passes support a scoped Phase1 deliverable. The reproduction identifies one actual cause within its declared construction; the catalogue separates observations from proposed mediators; the interdisciplinary and historical evidence changes the interpretation; and each ranked claim states what would defeat its attribution to a particular case. Positive evidence narrows the original premise. These constitute diagnostic progress rather than a list of mechanisms to try.

My central judgment is that the funded category should not be treated as a single established deficit in plasticity control. For any claimed failure, the explanation depends on whether a useful distinction was obtainable, selected by learning, preserved, accessible and applicable under the new demand. Those stages have different counterfactuals. Their common dependence on experience is the problem to explain, not an explanation by itself.

I give relation selection and action-dependent acquisition priority because they interrogate an assumption that a protection-centered account otherwise takes for granted: that the required knowledge was acquired in a usable form. **That ordering is my scientific judgment under uncertainty.** The current evidence does not show that these causes occur more often or promise a more successful programme than the lower-ranked causes. Rank1's mediator and rank2's relevance to strong general agents are particularly important uncertainties to carry forward honestly.

The original-paper request has been resolved at the available scope in `evidence/PAPER_REQUESTS_002_RESOLUTION.md`. Unavailability is not contrary evidence. The Jones claim is restricted to its inspected material and controls; the absence of Tolman–Honzik does not invalidate the narrower verified biology. I will not require a universal causal proof, an exhaustive survey, or another toy run before presenting the diagnosis. None would follow from the phase requirements, and another local witness would not establish general prevalence.

**Decision requested:** approve this scoped diagnosis as the basis for Phase2, or identify the scientific claim that needs revision. Approval accepts a direction for investigation with the uncertainties above; it does not make those uncertainties disappear. Phase2 will begin only after explicit approval, with invention separated from novelty screening as required by `02_RESEARCH_PROCESS.md`. No repair has been proposed, ranked or defended in this phase.

### 8.3 Operational facts separate from scientific findings

Human commit `980b99cbaa90096679eec35c230f3069a255357d` and checkpoint004's complete declared contents were verified through GitHub and local Git readback; `evidence/REMOTE_CHECKPOINT_004_VERIFICATION.json` records the receipt. All original scientific artifact bytes remain unchanged. The present submission, source resolution and continuation records are prepared as checkpoint005 for the human commit/push. Publication and scientific phase approval are distinct actions.

Authoritative subscription usage, unattended continuation, enforced reviewer isolation, restart recovery and large-output transfer remain unverified. Unattended model use stays disabled. Shared-filesystem consultations are not independent reviewers. Laptop/HPC limits and substantial-output durability remain operational-gate work before relevant runs; no laptop-sized experimental programme has been assumed. The completed local reproduction and methods work require no new GPU or cluster job. No additional spending was incurred.
