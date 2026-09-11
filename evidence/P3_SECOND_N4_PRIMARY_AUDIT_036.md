# N4: observable-contrast recipes and active perception

This is a PI primary-method audit and analytical recommendation, not an independent verdict or an efficacy result. It concerns the exact N4 and shared contract in `docs/P2_SECOND_OPERATION_SPECIFICATIONS_035.md`, SHA-256 `25f3148827d22abbe587a6c2ff0c5a3ff2db1883f70e678f640f16d0f07a7c69`. The specification is unchanged. Public source access and local PDF reading occurred on **2026-09-10**.

## Finding and remaining claim

The broad proposition that an agent should act to improve subsequent sensing is established antecedent territory. N4's actual novelty claim would have to concern its particular acquisition procedure: grow a library of executed action words, schedule crossed comparisons, and retain a recipe that changes an empirically collapsed response contrast into a noncollapsed one. Calling that procedure active perception, biological feedback or restoration does not establish a new method.

The checked active-control and current imitation methods below are materially different algorithms with different supplied inputs. Neither supports an exact whole-N4 reduction. Conversely, difference from these two methods does not clear N4: both are weaker nearest-comparator choices for *learning procedural structure without interpreted primitives* than the inaccessible Pierce–Kuipers paper. That source is a concrete remaining dependency, not absent prior art. Its methods are requested before any affirmative N4 novelty claim.

N4 also retains the weakest link to the funded objective. It certifies a pattern among acquired procedure endpoints, not that the original information source survived, that hidden hypotheses became distinguishable, or that a later task benefits. The analytic construction below makes one of those limits concrete. This is a reason to deprioritize N4 as the first efficacy candidate, not a formal kill of every possible use.

## Exact operation decomposition

Let `E_b(w)` be the current block's completed-trial effect for word `w`, retaining its full trace provenance and empirical status. For an eligible tuple, the positive rule is exactly

`E_b(pq) != E_b(pr)`, `E_b(pcq) == E_b(pcr)`, and `E_b(pcuq) != E_b(pcur)`,

with all referenced cells repeatable. This is a fixed predicate supplied by the designer. The acquired content is which literal procedures satisfy it in this block. It is learning ground procedural facts; the specification does not learn the definition of a useful contrast or infer a general law from the positive examples.

| Field | N4's supplied or learned content | Consequence for an audit |
|---|---|---|
| State | Word library, all completed and partial trials, effect versions, FIFO tuple queue, catalogue, bounds and block provenance | The catalogue is not the whole memory allowance. |
| Input | Finite categorical observations, ordered primitive actions, known block boundaries, actual deterministic physical RESET | Tokenization and repeatable restart are substantive affordances. |
| Acquisition | Seeded primitive/empty trials; all executed contiguous fragments; exhaustive eligible tuples; coverage fallback | Candidate recipes arise through interaction, under a supplied composition grammar. |
| Update | Literal equalities/inequalities on the six repeatable cells; preserve every other pattern | The equality predicate has no model of task value or a latent causal variable. |
| Read | Recheck block and effect versions; return supported, variable and untried alternatives explicitly | An absent pattern within the acquired set does not mean no restorer exists. |
| Execution | Permit a restorer only following the exact logged preparation `pc`; charge its actions | Observational similarity to the preparation is insufficient. |
| Reset | Separate physical RESET from volatile-memory clearing; archive prior-block evidence | Retained history and provenance are charged even when inactive. |
| Resource cost | Potentially quintic tuple construction in library size; actual reset/word trials, all failed tuples and traces | A cached effect is free of new interaction only because its earlier acquisition is counted. |

There is a narrow exact implementation equivalence: given the same library, queue and complete effect/provenance state, the restoration catalogue can be recomputed at read time from the fixed predicate. A cached catalogue and that recomputation return the same supported tuples and statuses when they use the same current versions. Their time/storage trade-off differs. This is a **derived cache equivalence**, not a claim that a named older method implements the full N4 scheduler, and not sufficient for a historical novelty kill. It prevents the cache alone from being treated as an additional learned causal model.

## Primary comparator: Simpkins, de Callafon and Todorov

[Simpkins et al., *Optimal trade-off between exploration and exploitation*, American Control Conference, 2008](https://roboti.us/lab/papers/SimpkinsACC08.pdf), published paper, accessed **2026-09-10**, §§II–IV. It augments a supplied linear-Gaussian plant with Kalman–Bucy mean/covariance dynamics, then approximates an HJB solution using predefined features and collocation. Its objective balances tracking, uncertainty and action costs. It does not learn N4's word language or six-cell criterion.

| Audit field | Prior method | N4 difference |
|---|---|---|
| State | Hand/target state and mapping posterior | Literal procedure and endpoint records |
| Inputs | Plant/observation equations, covariance assumptions, task cost | Categorical interface and restart affordance |
| Update | Filtering plus value-function fitting | Crossed finite-word trials and a fixed relation |
| Allocation | Feedback control from the fitted value gradient | FIFO tuple completion and coverage |
| Reset | Continuous evolution; no N4 block protocol | Explicit same-initial-state trials |
| Cost | Basis/collocation work and continuous control | Library search, trace storage and actual trials |

No tuning of its stated covariance or control-cost parameters installs N4's acquisition grammar and catalogue semantics. That would change the algorithm/interface. No common-domain action-by-action equivalence or counter-trajectory is certified here: discretizing this controller into N4's categorical reset interface would itself require an additional adapter. The comparison rejects an exact reduction to this particular flagged method; it does not establish priority over active perception generally.

## Current comparator: See2Act

[Wang et al., *Learning to See While Learning to Act: Diffusion Models for Active Perception in Robot Imitation*](https://arxiv.org/abs/2606.23625), **preprint**, version 1 dated **2026-06-22**, accessed **2026-09-10**. The [full PDF](https://arxiv.org/pdf/2606.23625), §§3.1–3.4 and Appendix A–B, was downloaded and read; its algorithm page was also visually checked. This is within the last six months. A failed web-text fetch did not prevent full-method access.

| Audit field | See2Act primary method | N4 difference |
|---|---|---|
| Learned state | Visual encoder and action denoiser weights | Acquired word/effect relation records |
| Supplied data | Demonstration action labels, scene states and rendering access | Actual primitive executions without those labels/models |
| Update | Noise-prediction loss using action-anchored camera poses | Fixed endpoint relation after repeated trials |
| Online allocation | Denoising alternates camera-pose updates and fresh observations | Explicit crossed recipe scheduler |
| Reset | Rollout camera initialization; no N4 physical-reset claim | Required physical RESET contract |
| Cost | Training/rendering and sensing at denoising steps | Word trials, queue work and retained evidence |

The supplied action labels carry task information absent from N4. Changing a denoising-step count cannot remove that dependency and yield the frozen recipe learner. The paper's stated sensing-latency limitation also shows that faster inference does not make real observation free. Its experiments are not evidence for N4, and their scores are not adopted here. The comparison establishes a current implemented alternative for active sensing, not a parameter-matched efficacy comparison.

## A concrete positive record that does not restore the original response

The complete mathematical construction is in `P3_SECOND_N4_ANALYTIC_WITNESS_036.json`; its hash is recorded in the checkpoint's audit manifest. It is an analytical witness, not an executed environment or a measured result.

Use a deterministic resettable system with modes `0,1,2`, primitive commands `c,q,r,u`, and initial observation `B`. Command `c` enters mode1 and emits `C`; `u` enters mode2 and emits `U`. Probes preserve the current mode. In mode0, `q,r` emit `0,1`; in mode1 both emit `Z`; in mode2 they emit `2,3`. Last-command state makes this an ordinary deterministic observable-output system. All outputs are finite categorical tokens.

Choose empty preparation `p`, with the primitive words as `c,q,r,u`. Control `c` qualifies because its endpoint differs from the empty trial. With a recipe bound permitting these compositions and enough completed trials, the six endpoint cells are:

| Trial | `q` | `r` | `cq` | `cr` | `cuq` | `cur` |
|---|---|---|---|---|---|---|
| Endpoint | `0` | `1` | `Z` | `Z` | `2` | `3` |

N4's positive test holds. Nevertheless, the post-restorer responses are a new pair, and `u` has entered a new mode. It has not recovered the original response function. The frozen specification already disclaims the stronger equality, so this is not a contradiction of its literal operation. It is a concrete reason not to let the name “restoration” carry a stronger scientific conclusion.

The distinction is between **responses to two different probe words from a preparation**, not automatically between **two hidden worlds under a common probe**. A useful experimental design would connect the changed response relation to a specified later decision and compare it with direct reacquisition. No argument follows that these procedural facts are never useful, or that every future task must fail. A benefit limited to a new signal is still a possible acquisition benefit; it must be named and counted correctly.

## Historical follow-through

[Bajcsy, Aloimonos and Tsotsos, *Revisiting Active Perception*](https://arxiv.org/abs/1603.02729), linked **2016 preprint**, [PDF](https://arxiv.org/pdf/1603.02729), accessed **2026-09-10**, §§3–4 and conclusions, is the original participants' retrospective. They describe costly construction/maintenance of active sensor heads and limited early computation, while explicitly treating their account as selective. That supports a historical engineering constraint, not proof that the field collectively abandoned the idea for one reason. I do not adopt their broader infant-comparison or “problem solved” rhetoric.

The 2008 primary controller explicitly identifies augmented-state dimensionality as a numerical limitation. Neither example establishes that computation was the only obstacle. By 2026, See2Act supplies a contemporary active-sensing implementation; blanket abandonment is therefore the wrong description. **PI inference:** improved hardware and renderers widen practical design space, while geometry, supervision, physical sensing costs and generalization remain substantive assumptions. Additional compute cannot supply an unobserved causal distinction or convert the N4 endpoint predicate into a task-utility measure.

## The biological prompt after this audit

The prior biological input was response-dependent antigen access, not evidence that an immune system literally runs a six-word recipe search. The dated primary-method account remains `P2_BIOLOGY_IMMUNE_CONSTRAINTS_2026-09-06.md`. That record distinguishes mouse intervention, a mathematical model and the PI's computational inference. No new biological measurement or stronger immune claim is introduced here.

The useful constraint survives: earlier action can change the later evidence process. Active control already studies that coupling. What remains scientifically demanding is learning which change matters for a future decision when the useful state variables and observation model are not supplied. N4 records one finite extensional relationship; it does not yet solve that larger problem.

## Source completeness and next decision

Simpkins's entire main paper, including method equations and solution procedure, was read. Numerical performance claims were not independently reproduced and are not relied on. See2Act's complete methods, both pseudocode algorithms, training details and stated latency limit were read; no score or broad superiority conclusion is adopted. Bajcsy et al.'s relevant historical and computational-constraint sections were read; their cited upstream historical works were not all audited.

Pierce and Kuipers, *Map learning with uninterpreted sensors and effectors*, Artificial Intelligence, 1997, [DOI](https://doi.org/10.1016/S0004-3702(96)00051-3), is **metadata verified, methods unread**. Crossref confirmed the title, authors and DOI. Author/institutional routes failed; the publisher route was not accessible. It is a required comparator lead for deciding whether an older procedure-discovery architecture already contains the relevant mechanism. No argument is built from its abstract. The batched paper request will specify the whole paper and the affected novelty claim.

Recommendation: retain the exact N4 record, close that source dependency before affirmative priority claims, and give acquisition/recombination candidates with a clearer downstream knowledge criterion precedence in programme design. No independent disposition, new candidate experiment, native reviewer invocation or final mechanism selection has occurred.
