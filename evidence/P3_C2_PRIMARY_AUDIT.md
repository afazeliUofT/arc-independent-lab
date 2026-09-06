# C2 primary-method novelty audit

Date and source access date: 2026-09-06. Status: PI research consultation and proposed reduction certificate, **not an independently reviewed novelty verdict**. This consultation used the same filesystem and tools as the PI. No candidate experiment was run. The numbers in the constructed histories below are stipulated examples and exact deductions, not measured results.

## Finding and scope

The approved C2 decision rule is exactly a finite Bayesian decision-value calculation with action-dependent state transitions. A finite-horizon POMDP construction below reproduces its posterior, experiment ranking, terminal decisions, permissible policy trees, and costs. C2 is a restricted lookahead controller when the supplied experiment set omits longer policies. Replanning does not make it an unrestricted optimal planner.

The proper mathematical comparator is therefore **finite belief-state decision planning with a terminal decision loss**, not only Klenske and Hennig's particular approximate Gaussian controller. The latter is a useful historical and computational comparator, but its approximations are not part of C2. Decision relevance, action-dependent observation, finite task priors and a stop action do not individually escape the reduction. Nor does grouping primitive actions into an experiment tree.

There are two qualifications to the certificate. First, the approved objective assumes a terminal decision may depend on the future task identity; this is not valid if that identity remains hidden. Second, historical papers need not define the same typed exception or audit-log format for an event assigned zero probability. The exact scientific mapping established here is on the modeled domain, with explicit matching interface guards outside it. This is not evidence that one historical implementation had C2's identical error strings and file layout.

Audited object: the unchanged C2 section of `docs/P2_OPERATION_SPECIFICATIONS.md`, whole-file SHA-256 `d37a52eeb569461503b262d2790a656048624ede4790aeb49254e5a9f133c26f`. Its interface supplies the belief, hypothesis states, action/observation model, candidate experiment trees, task losses and task prior. It does not learn those objects. The through-line joining C1, C2 and C4 requires its own audit; this component reduction cannot settle it.

## Primary methods read

These source summaries report what was read; the subsequent C2 compilation is this audit's derivation from the approved specification.

| Source and publication status | Method coverage and relevance |
|---|---|
| Kaelbling, Littman and Cassandra, *Planning and Acting in Partially Observable Stochastic Domains*, Artificial Intelligence 101 (1998), published journal article. [Full primary paper](https://people.csail.mit.edu/lpk/papers/aij98-pomdp.pdf), accessed 2026-09-06. | Read §§3.1–3.4 and §4.1, pp. 105–111, including transition/observation definitions, Bayesian state estimation and finite policy-tree value equations; checked §4.4's backup equation. The framework carries a probability distribution over possible states and evaluates observation-conditioned action trees. This is the exact finite planning comparator used here, not a claim to reproduce its witness pruning implementation. |
| Huang, Guo, Acerbi and Kaski, *Amortized Bayesian Experimental Design for Decision-Making*, NeurIPS 2024, published conference paper. [Official full paper](https://proceedings.neurips.cc/paper_files/paper/2024/file/c59f05d7ab3638b138cc61f32e1a7cd1-Paper-Conference.pdf), accessed 2026-09-06. | Read §§2.3–4.1, pp. 4–7: decision utility, DUG/EDUG definitions, predictive head and policy training. Equations (5)–(6) already evaluate the expected improvement in the best downstream decision. C2's finite static-world, single-task, zero-cost instance has that criterion. Their trained Transformer Neural Decision Process is a different approximate implementation; C2 is not that architecture. |
| Klenske and Hennig, *Dual Control for Approximate Bayesian Reinforcement Learning*, JMLR 17 (2016), published journal article. [Full primary paper](https://www.jmlr.org/papers/volume17/15-162/15-162.pdf), accessed 2026-09-06. | Read §§2–4.3, pp. 2–11: state/parameter augmentation, Bellman objective, toy dual effect and the certainty-equivalent trajectory, local quadratic uncertainty correction and numerical outer optimization. This specific algorithm is not an exact description of finite enumeration in C2. Its introduction reports computational and conceptual barriers to older dual-control applications; the paper itself reconstructs and extends that tradition. |
| Grass and Zilberstein, *Value-Driven Information Gathering*, AAAI technical report WS-97-06 (1997), published workshop paper. [Full primary paper](https://cdn.aaai.org/Workshops/1997/WS-97-06/WS97-06-010.pdf), accessed 2026-09-06. | Read all six pages, especially §§2–3. Decision models determine which information sources are worth querying, with costs, response-time uncertainty and a stopping rule. The implementation assumes returned feature information is correct, bounds its feature focus set and models information acquisition rather than C2's general world-changing actions. It is an antecedent of the commitment to decision-relevant acquisition, not an exact reduction target for all of C2. |

An arXiv HTML version of Huang et al. was inspected during discovery: [arXiv:2411.02064v2, preprint version](https://arxiv.org/html/2411.02064v2), accessed 2026-09-06. The published conference PDF, including the actual objective and training method, was then read and is the version used above. No argument here depends on an abstract. No numerical performance claim from these sources is imported into this audit.

## Explicit reduction of the approved rule

This section is an original algebraic certificate. It does not assign new notation or extensions to an author's implementation.

Write C2's belief as \(p(h)\), its feasible experiments at remaining allowance \(b\) as \(E_b\), expected charged cost as \(\bar c(e,p)\), and the joint experiment kernel as \(Q_e(h',z\mid h)\). Define the terminal Bayes loss

\[
F(p)=\sum_g\mu(g)\min_{d\in D_g}\sum_h p(h)L_g(h,d).
\]

The approved objective and the corresponding cost are

\[
V(e)=F(p)-J_e(p),\qquad
J_e(p)=\lambda\bar c(e,p)+\sum_z P_e(z)F(p_e^z).
\]

The stop member has \(J_{stop}(p)=F(p)\). Because \(F(p)\) is the same number for every experiment, maximizing \(V\) is exactly minimizing \(J\). The subtraction introduces no different action policy.

Construct a finite decision process with an acquisition phase and a terminal decision phase. At acquisition, choose one of the admitted experiment trees, paying its actual resource costs through execution. Its resulting hidden state and observed transcript have exactly the supplied joint law \(Q_e\). At the terminal phase, draw \(g\sim\mu\) independently under the specified task prior, reveal \(g\), then choose \(d\), receiving reward \(-L_g(h',d)\). Experiment rewards are negative charged cost times \(\lambda\); use an undiscounted finite horizon. Stop goes directly to the terminal phase without changing \(h\).

For completeness, a general \(Q_e(h',z\mid h)\) need not factor into a transition on \(h'\) followed by an observation depending only on \(h'\). A standard finite state construction removes that concern: let the intermediate successor state be \((h',z)\), use transition probability \(Q_e(h',z\mid h)\), and emit its \(z\) component deterministically. Terminal losses depend only on \(h'\). This uses no privileged observation of \(h'\). If costs vary within otherwise identical transcripts, include the actually available cost record in the observable execution record and the corresponding finite accounting state; do not expose hidden costs as information.

Bayes' rule in that construction gives

\[
P_e(z)=\sum_{h,h'}p(h)Q_e(h',z\mid h),\qquad
p_e^z(h')=\frac{\sum_h p(h)Q_e(h',z\mid h)}{P_e(z)}.
\]

After observing \(z\) and then \(g\), the optimal terminal reward is
\(-\min_d\sum_{h'}p_e^z(h')L_g(h',d)\).
Taking expectations over the observable branches and task draw gives exactly \(-J_e(p)\). Thus both procedures select the same experiment and terminal decisions, with the same stipulated tie ordering, at every modeled history at which C2 is defined.

One can retain a primitive-action realization rather than treating an experiment as a macro transition. Augment the process with the selected experiment identifier, its current tree node, execution phase and remaining budget. Within that tree the next permitted action is the action prescribed by the selected node; observations choose successors. At each leaf, allow the terminal task-specific decision. This prevents a comparator from obtaining more within-experiment freedom than C2. Padding shorter trees with zero-cost terminal self-loops gives a common finite horizon. The model and policy-tree construction costs remain charged; this is an equivalence construction, not a practical solver recommendation.

### State, updates, allocation, resets and cost

| Approved C2 object or operation | Compiled decision-planning object | Consequence or qualification |
|---|---|---|
| \(h\) includes relevant physical state and unknown properties | Hidden state; unknown fixed model parameters may be part of that state with identity transitions | No requirement to know the true parameter. The supplied family and probabilities must still represent it. |
| Finite \(p(h)\) and immutable predictive definitions | Belief vector and transition/observation tables | Same retained uncertainty and prior information. A point-estimate comparator would discard information C2 receives. |
| Experiment \(e\), tree branches and \(Q_e\) | Restricted policy tree or the explicit phase/node construction | The tree commits to its contingent internal actions. It is not a free oracle observation. |
| Actual transcript update | Bayesian belief update above | Same supported-history state. No additional learner is inserted. |
| Future losses \(G,L_g\) and weights \(\mu\) | Terminal decision problem and task draw/revelation | The objective already supplies what future distinctions matter. This is a prior over demands, not the actual withheld schedule. |
| \(\lambda\) times expected cost | Negative experiment reward | Equality concerns expected utility. It does not enforce a hard resource bound by itself. |
| Every executable branch fits remaining allowance | Reject violating trees before value comparison; equivalently constrain actions in the budget-augmented tree | Match C2's actual branch definition, including any syntactic branch the implementation calls executable. A chance constraint or average-cost test is a weaker comparator. |
| Stop, and fixed lexicographic tie order | Immediate terminal transition; same tie order | Includes the possibility that no available experiment is worth its cost. |
| Replan after a completed consistent experiment | Reapply the same finite lookahead rule at the new belief/budget | This is generally receding-horizon control. It equals a full remaining-horizon optimum only when the supplied policies/terminal value justify that claim. |
| Zero-probability actual transcript | Checked Bayesian update returning a typed model-inconsistent result; execution log retains incurred costs | This explicitly extends the partial Bayesian update outside its modeled domain. The cited papers do not establish identical exception conventions; a comparison must state the same guard. It does not repair a misspecified model. |
| Memory clearing with persistent \(p\) and declared records | Preserve that controller memory | Erasing the belief does not preserve the claimed operation. Keeping experiment records is an additional counted channel. |
| Declared world reset | Apply the same reset kernel to each hypothesized state and propagate the belief | Parameter knowledge need not be erased by a world reset. An unknown reset needs a model or an unresolved result, not invented certainty. |
| Direct-enumeration work | Same finite summations and minimizations | \(O(JZ(KK'+GK'D))\), plus kernel/tree construction, model inference and accounting. No new complexity advantage appears in the reduction. |

The reduction does not require expanding an infinite unknown-model space. C2 is finite by definition. If a future implementation replaces its supplied finite models with learned approximate models, that changes the error and computational analysis; it does not turn this exact selector into a new principle.

### Task revelation is a material assumption

The order \(\sum_g\mu(g)\min_d\) means the final decision can be chosen separately for each \(g\). It is executable if the actual task is disclosed before the final decision, or if the application genuinely calls for a complete contingent decision policy. If the task remains hidden, the relevant loss is instead \(\min_d\sum_g\mu(g)\mathbb E_p L_g(h,d)\), which can be larger. The approved prose says to use the disclosed task when available but does not supply a shared-decision alternative when it is unavailable. This audit restricts the exact decision-value interpretation to the former interface; it does not silently repair the approved equation.

## Distinguishing histories and failed escape routes

### Decision value differs from entropy reduction, but that does not distinguish C2 from its proper comparator

Construct \(h=(x,y)\), where \(x\) is a fair bit and \(y\) is independent and uniform on four symbols. One interaction remains. Experiment \(e_x\) reveals \(x\); experiment \(e_y\) reveals \(y\). Neither changes the world. Each costs \(0.1\), with \(\lambda=1\). The future decision predicts \(x\) under zero-one loss.

The initial Bayes loss is \(0.5\). C2 gives \(V(e_x)=0.4\) and \(V(e_y)=-0.1\), choosing \(e_x\). A comparator maximizing entropy reduction of the *whole supplied state*, with the same equal action costs, chooses \(e_y\): it yields two bits instead of one. On the stipulated actual state \((x,y)=(1,3)\), C2 sees \(1\) and predicts \(1\); that information-only comparator sees \(3\), retains the fair uncertainty over \(x\), and predicts \(0\) under a lexicographic terminal tie.

This history separates C2 from a particular information-gain objective. The finite decision-planning comparator above produces C2's entire history exactly. A Bayesian design comparator can also select the supplied decision loss instead of whole-state entropy; that is a choice already available within decision-theoretic experimental design. Beating entropy gain would therefore show the consequence of specifying the appropriate objective, not novelty of C2.

### Repeated short lookahead can miss jointly useful observations

Let two independent fair bits determine a terminal parity decision. Each of two experiments reveals one bit at cost \(c\), where \(0<c<0.25\). If \(E\) contains only the two single-query trees and stop, each query alone leaves terminal Bayes loss \(0.5\) and has value \(-c\). C2 stops. A permitted tree querying both bits would have value \(0.5-2c>0\). Saying the controller will replan does not cure its failure to select the first query. If the longer tree is supplied, the known policy-tree calculation finds the benefit. Tree generation and horizon are consequential inputs, not implicit discoveries by C2.

### World-changing utility is not automatically acquired knowledge

Let \(x\) again be an unknown fair bit to be predicted. A permitted operation sets \(x\) to zero and returns the same uninformative transcript in either starting state, costing \(0.1\). Its post-operation Bayes loss is zero, so C2 assigns value \(0.4\), although the transcript reveals nothing about the old bit. The objective is correctly calculating a control benefit. The diagnostic claim that an acquired distinction caused better decisions would fail. C2's approved causal interpretation already excludes that inference; an experiment must enforce it.

## Historical and contemporary assessment

There is no support here for saying decision-relevant exploration was forgotten in the absolute sense or newly rediscovered by this programme. The older VDIG implementation and contemporary Huang et al. objective are counterexamples to that statement. What can lapse is attention to a method family, or practical application to demanding domains.

Grass and Zilberstein explicitly restrict joint feature-value calculations because their size grows exponentially; their world and sources were also supplied and simulated. Klenske and Hennig identify prohibitive inference/control computation and reconstruct older approximations. Those are documented barriers in the cited methods, not proof that fashions alone caused abandonment. Today's larger compute can move the feasible finite boundary; it cannot remove the tree's combinatorial growth or supply missing model classes, probabilities and utility functions. That last statement is a deduction from C2's declared inputs and enumeration, not a historical claim about why particular authors stopped working.

Huang et al.'s amortization is a contemporary response to repeated design cost, but it trains an approximate policy and predictive model. C2 has no corresponding amortization or approximation contribution. Merely running its finite enumeration on more compute would change the problem sizes attainable, not the mathematical novelty finding.

## Strongest remaining alternative explanations for an apparent repair

1. **The modeller supplied the decisive knowledge.** C2 receives predictive alternatives, action-dependent channels and a prior over terminal losses. Hold these objects fixed and equally available to comparison controllers. In a later instrument, disclose their construction and prevent withheld-task information from entering them. A successful supplied-model experiment does not establish ontology discovery.
2. **The action made the world easier without obtaining the alleged evidence.** Use controls that distinguish the physical consequence from the observation supplied to the downstream learner. Same-learner record replay can assess the evidence pathway only when the compared record and resulting decision problem are well defined; it cannot undo an uncontrolled physical-state change.
3. **The useful history had more resources or a longer effective horizon.** Compare the identical branchwise interaction limits, actual charged costs, available trees and inference calls. Charge model simulation and policy construction as well as actions. A weak one-step entropy baseline is insufficient when a supplied-tree decision-value baseline is available.

These are design requirements for any later effectiveness test, not preregistered thresholds or completed controls. No effectiveness study is necessary merely to establish the algebraic reduction.

## Access, uncertainty and reviewer handoff

The decisive primary methods are accessible. No human paper request is necessary for this C2 certificate. Howard (1966) and Raiffa–Schlaifer (1961) appeared in historical search results but were not relied upon: their original methods were not inspected here, and claiming an earlier first origin is unnecessary to the reduction. This avoids converting an optional priority search into a blocking book request.

The web text exposed the equations and all method sections used. A supplementary visual request failed twice; exact returned errors were:

```text
Unable to resolve screenshot call: screenshot({"ref_id":"https://people.csail.mit.edu/lpk/papers/aij98-pomdp.pdf","pageno":8,"height":null,"offset":null}) because content type is not application/pdf and web screenshot is not enabled
Unable to resolve screenshot call: screenshot({"ref_id":"https://proceedings.neurips.cc/paper_files/paper/2024/file/c59f05d7ab3638b138cc61f32e1a7cd1-Paper-Conference.pdf","pageno":4,"height":null,"offset":null}) because content type is not application/pdf and web screenshot is not enabled
```

The display limitation was then resolved by downloading the original PDFs and rendering locally. The Bayesian update on printed p. 107 of Kaelbling et al. and definitions (5)–(6) on p. 5 of Huang et al. were visually checked. The downloaded reading copies remain under `private_sources/`; no paper PDF is proposed for the public repository.

| Private reading copy | SHA-256 of downloaded original |
|---|---|
| `P3_C2_Kaelbling1998.pdf` | `71a6d1aee278e93c5fae8dd7d0c452c8b7b035af55d9dce2bc367d473bfc9645` |
| `P3_C2_Huang2024.pdf` | `acb0d65cad3a563a821a3b81c210f6aa0c83a7d730e2b4327bd373a06e5f00f3` |
| `P3_C2_Grass1997.pdf` | `5732a9494b2ae93bfb9b1b4fcbab26f9d7c8046bdb571c85708012f60968de73` |
| `P3_C2_Klenske2016.pdf` | `d63315c4ed81ec390979bfaea1bdcb8f3136020be8c9aa115e122b650bde2997` |

An independently restricted reviewer should check the joint-kernel construction, the task-revelation condition, the exact policy restriction and budget convention, and the separation between modeled behavior and out-of-model interface guards. The PI should not present this shared-workspace consultation as that review. If the scientific operation is exactly reduced after the required review, its removal is a positive diagnostic outcome. The component-level result must still be considered alongside the separately specified through-line audit.

## Appended output-interface clarification — 2026-09-06

The approved C2 explicitly outputs an experiment or `stop` and conditions its belief after the experiment. The terminal Bayes minimum is the value used to choose that experiment; it need not itself emit the terminal decision. References above to identical terminal decisions mean a **separately declared downstream Bayes argmin** with the same task disclosure and tie order. The selector/posterior reduction does not depend on silently adding that response interface to C2. This precision correction arose while checking the joint proposition, and does not alter its approved equation or the algebraic mapping. Source: [approved C2 specification](https://github.com/afazeliUofT/arc-independent-lab/blob/d9200bd6061a63cf82037c2fc31f361fa0109cb3/docs/P2_OPERATION_SPECIFICATIONS.md), accessed 2026-09-06.
