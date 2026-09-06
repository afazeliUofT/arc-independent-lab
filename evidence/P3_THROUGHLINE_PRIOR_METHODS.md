# Phase 3 through-line: primary antecedents and limits of the mapping

Prepared 2026-09-06. This is a bounded PI research consultation with shared tools and filesystem, not an independent review or a formal novelty verdict. It audits the commitment that connects C1, C2 and C4, using the approved `docs/P2_OPERATION_SPECIFICATIONS.md` and `state/escalations/2026-09-06_PHASE2_APPROVED.md`. The approved operations are unchanged.

The broad commitment already has substantial integrated antecedents. The strongest match to “know versus do not know, then act to learn” is KWIK and KWIK-Rmax. Bayes-adaptive POMDPs supply the stronger comparator for decision-sensitive action under uncertainty about both world state and model, including retention through physical resets. These findings do not reduce an unspecified C1–C2–C4 composition to one old algorithm. They also do not establish that the approved operations, simply connected, satisfy that commitment.

## Scope and reading record

All source URLs below were accessed **2026-09-06**. These are published conference or journal papers, not preprints. Author or institutional copies are identified by their original publications; upload years are not treated as publication years. Methods, assumptions and relevant algorithm definitions were read beyond abstracts. No inaccessible method is supporting a claim in this note.

| Source | Primary method material inspected | Exact downloaded PDF SHA-256 |
|---|---|---|
| Mitchell, IJCAI 1977 | Entire six-page paper, especially §§2.2, 3.1, 3.2.1–3.2.2 | `726c620d1001371ea735a5a8d782af1673e5a9c917cbfa0552596ff513dbba39` |
| Li, Littman and Walsh, ICML 2008 | KWIK protocol, enumeration, navigation example, learner combinations, limitations | `8d55e38fbef963ee6edc3c00e482e9f57675d39851c21612b4284c10ed6960fd` |
| Li, Littman, Walsh and Strehl, Machine Learning 2011 | §§3.1–3.2, 4.1–4.2, §6 deterministic combinations, §7.2 including Algorithm 3 and practical caveats | `4d5eedc31e9988b9de3fcc546da31d210e5a735b6eccf46116461a2a7d3c42f9` |
| Ross, Chaib-draa and Pineau, NIPS 2007 | §§2–4 models, belief update and planning, §5 physical versus parameter reset | `e9c4e30a1a140b093f0bb57dc9fc986788e0033205f79ef87dcd4c0336c12d71` |
| Petrick and Bacchus, AIPS 2002 | Knowledge databases, primitive queries, action/update definitions, PlanPKS and correctness conditions | `2af08a6e888d5b68ae45399659cc2e27a8aa5d1ce6b25cb91ff7d8190c187e6a` |
| Angluin, Information and Computation 1987 | Teacher interface, observation table, closure/consistency, full L* update loop and termination argument | `1dde8daec314d13fa64126495b756cf0ef7042d9ad6e36f2c8845b9dffc06aa3` |

PDFs and extracted text were downloaded as private source working material, outside the public handoff. The table identifies what was read; it does not assert that every appendix of the longer journal paper was checked. Bibliographic correction: Strehl is a coauthor of the expanded 2011 paper, not of the three-author ICML 2008 paper.

## Primary integrated antecedents

### Mitchell 1977: disagreement, discriminating instances and accumulated knowledge

The method retains all rules compatible with admitted positive and negative examples, represented by extremal boundaries. New classifications remove incompatible versions. Section 3.2.1 proposes selecting instances on which competing versions differ; §3.2.2 combines separately learned version spaces by intersection. Empty space indicates inconsistency relative to the language, without distinguishing erroneous observations from inadequate expressiveness. This is already a connection between unresolved alternatives, future evidence selection and persistent accumulated constraints. The active selection is a proposed use, not the paper's implemented cost-sensitive experimental policy.

The supplied objects are the rule language, matcher and reliable classifications. Generating an instance does not establish that a physical learner can reach or label it. There is no world-transition or reset kernel. Cost can grow with the extremal sets; the paper identifies unreliable data and branching representation size as obstacles. **2026 assessment, an inference:** more compute can extend finite enumeration, but does not make labels reliable or the supplied language adequate. The paper documents obstacles, not a demonstrated historical abandonment of the entire approach. [Primary paper, §§2–3](https://www.ijcai.org/Proceedings/77-1/Papers/048.pdf), accessed 2026-09-06.

### Li, Littman and Walsh 2008: the unknown result is an operative interface

KWIK requires accurate non-abstaining predictions, conditional on realizability, and bounds abstentions. Its basic protocol supplies feedback when the learner returns the unknown symbol. Enumeration keeps a version space, predicts only on agreement, and recognizes exhaustion. The navigation example connects this distinction to physical exploration: unobserved edge costs that remain inferable from previous linear measurements count as known; unresolved costs motivate traversal. A guessed parameter vector can instead trap the example learner in repeated suboptimal traversal.

This is an antecedent for conditional knowledge and action-dependent data, not merely confidence annotation. The formal supervised protocol has stronger feedback access than arbitrary world interaction; the navigation example states a graph and linear cost structure. Its episodes reset position while acquired information is reused. No C4 aliasing-versus-length diagnosis is specified. **2026 assessment, an inference:** better optimization alone does not remove the difference between guessing a fitting parameter and determining what that evidence licenses. [Primary ICML paper, §§2–5](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/published-9.pdf), accessed 2026-09-06.

### Li et al. 2011: KWIK-Rmax closes the loop

Algorithm 3 queries transition and reward learners. A state-action pair is known only when both provide valid predictions. Unknown pairs receive an optimistic planning surrogate: maximal reward and a self-loop. Planning selects an action; actual next state and reward update the learners that abstained. The new knownness changes subsequent planning. Section 6 also composes learners while propagating uncertainty.

The supplied objects include state/action interfaces, discount, model classes and accuracy parameters. Accuracy requires the true functions to belong to those classes. This RL loop observes actual transitions rather than requesting an arbitrary state's label. It optimizes an optimistic surrogate, not C2's posterior expected reduction in future decision loss. It does not generate C4's diagnostic certificates. The tabular transition representation costs O(|S|²|A|); the paper separates learning from potentially expensive planning. Model state persists during interaction; arbitrary agent-memory erasure is not provided for.

**2026 assessment, an inference:** the underlying question survives increased compute: representation and planning must remain affordable, and class-relative knownness does not discover missing ontology. This establishes an older integrated approach, not evidence of why a whole community ceased using it. [Primary expanded paper, §§3–4, 6–7](https://thomasjwalsh.net/pub/Li11Knows.pdf), accessed 2026-09-06.

### Ross et al. 2007: model uncertainty and state uncertainty are acted on together

Bayes-adaptive POMDP state augments the hidden physical state with transition and observation count vectors. The belief is over those joint states. Algorithm 3.1 propagates candidate next states and counts, weights them by predicted transition/observation probabilities, and normalizes after real evidence. Planning evaluates actions through their subsequent beliefs and rewards. It supplies finite state/action/observation spaces, Dirichlet priors and a reward function; unknown parameters do not mean an unknown ontology.

The Tiger experiment resets physical state between episodes while retaining the count-vector distribution. Thus retention across a declared world reset is already inside an integrated learning/planning procedure. It supplies no typed knowledge/abstention or C4 diagnostic interface. Approximate particle methods can discard alternatives. Exact belief growth and planning are explicit obstacles; online lookahead costs O((|A||Z|)^D Cb), with belief-update cost Cb.

**2026 assessment, an inference:** compute growth changes useful horizon and support size, not the fact that unrestricted support/horizon expansion remains costly. This source is a direct comparator for interaction with uncertain sensor and transition parameters, not proof of open-ended variable discovery. [Primary paper, §§2–5](https://www.cs.cmu.edu/~sross1/publications/Ross-NIPS07-BAPOMDP.pdf), accessed 2026-09-06.

### Petrick and Bacchus 2002: knowledge is a precondition for using a plan

PKS represents known facts, known-whether facts, known values and restricted disjunctive knowledge. Knowledge means truth across the represented possible worlds. Sensing can establish that a fact's value will be available at execution without assigning that value at planning time. PlanPKS adds executable actions or branches on such available knowledge, requiring success along the branches. Effects and update rules change the knowledge databases.

The initial description, action effects, goals and domain update rules are supplied. The planner does not learn them from contrasts. Its representation and inference deliberately sacrifice completeness for tractability; an unsuccessful query is not an exact diagnosis that the world is inherently ambiguous. Search and databases have real costs. No general agent-memory reset recovery is specified.

This is a prior operational distinction between knowing a condition, knowing its negation and lacking the information required to execute a branch. **2026 assessment, an inference:** improved search could retain more distinctions, but does not make a supplied action model learned or make incomplete inference complete. [Primary paper, knowledge representation and PlanPKS](https://cdn.aaai.org/AIPS/2002/AIPS02-022.pdf), accessed 2026-09-06.

### Angluin 1987: distinguishing experiments require an access contract

L* maintains prefix/suffix sets and a table of queried classifications. Equal rows are provisional state identifications; consistency and closure violations add distinguishing suffixes or prefixes. A closed, consistent table yields an automaton conjecture; a teacher either confirms equivalence or supplies a counterexample that expands the table. The algorithm supplies a concrete evidence–representation–query–revision loop.

The alphabet and teacher interface are supplied. Exact membership answers and equivalence/counterexample queries are stronger access than an irreversible physical trajectory. Polynomial learner time is measured relative to automaton size and counterexample length under that interface. The table persists; arbitrary physical resets and their cost are outside the query protocol. The paper itself questions the practical strength of equivalence access and develops a sampling alternative with changed guarantees.

**2026 assessment, an inference:** a simulator may implement repeatable queries cheaply; a non-resettable world may not. More compute alone does not provide either access. This is relevant to future executable-description discovery but does not equal C1's fixed supplied transducer population or C2's loss-sensitive policy. [Primary journal paper](https://doi.org/10.1016/0890-5401(87)90052-6), [institutional full text](https://swt.informatik.uni-freiburg.de/teaching/WS2019-20/AutomataTheory/Learning%20Automata%20%28Caveat%20not%20related%20to%20Machine%20Learning?month%3Aint=1&orig_query=&year%3Aint=2025), accessed 2026-09-06.

## Audit consequences derived from the approved specifications

The following are deductions about our candidates, not extra claims attributed to the preceding papers.

### An action decision and a knowledge declaration are different outputs

For C1's nonempty live support S and a query proposition φ, define a proposed audit predicate `KNOWN(φ)` only if every live pair satisfies φ. If both truth values remain possible, the query is unresolved. If S is empty, the result is model-inconsistent; universal quantification over an empty set must not accidentally license every proposition. This makes the intended commitment testable relative to the supplied class. It still cannot certify that the class contains the true world.

C2 instead computes an action according to weighted losses. It can rationally stop with residual uncertainty if further evidence costs more than the decision improvement. That action does not make the underlying proposition known. A joint system that converts the selected decision into `KNOWN(φ)` has broken its own epistemic contract.

For a symbolic example, consider two live worlds with different binary answers and equal weights. A perfect experiment reduces unit-error Bayes risk from 1/2 to zero. If its charged cost exceeds 1/2, C2 selects stop. The correct audit output remains “unresolved, stopped on cost”; neither a confident answer nor “evidence cannot resolve this” follows. This is a constructed distinguishing case, not an empirical result.

### C4's selected scope does not preserve every admissible scope

Let two atoms be A and B, the positive seed have signature (1,1), one contradictory encounter have signature (0,0), and k=1. Both A and B are admissible scopes and cover the seed. C4's fixed ordering selects one, say A. At an unobserved input (1,0), selected A licenses F while the alternative scope B would not. Merely composing this selected rule with C2 does not restore the discarded distinction. Retaining both scopes or asking C1 to certify the application would require an explicit joint interface; neither is specified by C4's selection rule.

The aliasing certificate also needs its exact scope. A positive/negative pair with the same full atom signature proves those tests cannot separate the pair under the admitted labeling/provenance assumptions. It does not prove that the true physical world lacks a distinguishing variable, nor distinguish a missing variable from corrupt admitted outcomes. The length-bound certificate is different: it states failure within k despite separation by the full seed-compatible conjunction. These are checkable properties of a supplied representational problem.

### Minimum mapping required before any exact joint reduction

| Joint interface question | What an auditable composition must specify |
|---|---|
| Identity of a live explanation | Whether C4 rule scopes are hypotheses within C1, annotations on them, or separately chosen proposals; any correspondence must be explicit. |
| Prior and support | How C2's weights attach to C1 alternatives; whether positive-support alternatives can acquire zero weight or be pruned without contradictory evidence. |
| Experiment predictions | How executable C1 descriptions supply C2's transcript kernels and post-experiment state, including observations made unavailable by actions. |
| Outcome routing | Which actual observations enter C1, C2 and C4; matching provenance/action admission cannot be assumed to occur automatically. |
| Declaration versus action | The exact rule licensing a knowledge declaration, separately from Bayes-optimal action or cost-limited stopping. |
| Diagnostic control | Whether inconsistency, atom aliasing and length exhaustion merely report, or initiate actions; how any repair respects the frozen class and budget. |
| Discontinuity | Which learned support, weights, witnesses and definitions survive a context clearing; which physical reset transitions occur without erasing accumulated model knowledge. |
| Cost | Stored definitions/witnesses, belief propagation, query simulation, search, solver work and real interaction; no free teacher or discarded alternatives hidden behind an abstraction. |

The approved specifications leave several of these links open and explicitly do not claim a combined mechanism. Therefore four component reductions would be insufficient to establish a joint reduction. Conversely, the absence of one old paper containing every proposed diagnostic tag would be insufficient to establish a novel learning operation. A novel tag needs a demonstrated behavioral, inference or resource consequence; an unspecified connection supplies no such consequence.

## Dependencies and honest limits

No human paper request is necessary for this bounded comparison. No hardware or paid service was used. This note does not claim exhaustive historical coverage, current prevalence, an independent review, a candidate efficacy result or a formal GO/KILL decision. Specific historical barriers are identified with present-day reasoning; evidence that an entire idea was abandoned for one particular social reason has not been established.

The earlier three-author paper and the expanded journal version contain different formulations. This note relies on their explicit protocols, algorithm prose and interfaces, not an unchecked transplant of every displayed complexity formula or proof. The source reading is adequate for identifying these antecedents; a subsequent exact reduction certificate must cite the particular source algorithm/version actually mapped.

Local retrieval error, preserved verbatim: `ModuleNotFoundError: No module named 'requests'`. This occurred before the first download. Retrieval then succeeded using Python's standard-library `urllib.request` and the already installed PDF extractor. No package was installed, no paper method was inferred from the failure, and no governing or state file was changed by this consultation.

## Appended hardware-scope clarification — 2026-09-06

The phrase “No hardware or paid service was used” above means no laptop/HPC job or paid external service was used. The research did use this hosted runtime and its ordinary tools. No claim of computation without hardware is intended. Programme context: [authorized repository](https://github.com/afazeliUofT/arc-independent-lab), accessed 2026-09-06.
