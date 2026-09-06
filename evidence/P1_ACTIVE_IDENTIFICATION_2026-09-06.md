# Acquisition depends on the actions that produce evidence

Phase 1, PI methods note, 2026-09-06. All URLs accessed **2026-09-06**. No mechanism proposal or new experiment. This note separates a controlled old failure from any assertion about its prevalence in contemporary agents.

## Primary-method capsule

Klenske and Hennig, *Dual Control for Approximate Bayesian Reinforcement Learning*, **JMLR 17(127), 2016, published**. [Record](https://www.jmlr.org/papers/v17/15-162.html); [full paper](https://www.jmlr.org/papers/volume17/15-162/15-162.pdf).

The model supplies state/action variables, Gaussian uncertainty, a dynamics family, and a finite-horizon target/cost schedule. In the scalar example, action magnitude controls information about an unknown gain. Certainty-equivalent and one-step cautious policies omit the later benefit of learning. The authors revisit a 1973 approximation and extend its modeling scope. Simulated comparisons include a true-parameter oracle, certainty equivalence, a Bayesian exploration bonus and approximate dual control. Different future costs make different parameter uncertainties worth resolving. Section 6.4 assumes parameter drift in the learner while the true parameters remain fixed; it is not measured erasure. Comparisons are illustrative, not equal-computation frontier evaluations. The conclusion retains high numerical load as a limitation. The paper describes limited uptake and continued approximations, not wholesale abandonment.

Read the introductory/model and scalar-identification arguments in §§1–3, the §4 approximation overview, and the relevant experimental conditions/results in §6 and conclusion; inspected the model definitions used by those experiments. Appendix derivations and complete implementations were not independently audited. PDF SHA-256: `d63315c4ed81ec390979bfaea1bdcb8f3136020be8c9aa115e122b650bde2997`. Reading copy is ignored under `private_sources/p13_root/`.

## Our deduction: missing evidence can be caused by a policy

Take the supplied scalar observation model, written as a residual:

\[
y=x_{t+1}-a x_t=b u_t+\epsilon_t,\qquad
\epsilon_t\sim\mathcal N(0,Q),\quad Q>0.
\]

With a Gaussian prior on the unknown gain, the posterior precision is

\[
\sigma_{t+1}^{-2}=\sigma_t^{-2}+u_t^2/Q.
\]

This follows directly by collecting the quadratic terms in the Gaussian likelihood and prior. At zero action the observation is independent of the gain: no amount of fitting that observation identifies it. Nonzero action can supply information, at a cost. A controller can therefore generate a history that supports its own continued uncertainty even though an informative action was allowed. This is a deduction under the stated model, not our measurement of an AI agent.

The error is not automatically caution: a one-step objective has no later decision on which information could repay its cost. Nor is every informative action worth taking. Failure attribution needs an affordable distinguishing action whose information changes an attainable future decision enough to matter. Replacing that condition with “the agent did not explore much” would diagnose rational behavior as failure.

There is a different error after data exist: a learner may fit a relation that gives current predictions but does not support the intended changed use. The action-policy cause and the relation-selection cause should not be merged. Improving one does not logically repair the other.

## What the old work changes, and what it does not

The important historical contribution is an explicit coupling between acting and becoming informed. “Learning receives data” hides that an interacting policy partly chooses which data will ever exist. This gives an acquisition-stage alternative to explanations beginning with interference in already-acquired knowledge.

The 2016 work already revisited old approximations, and the companion Simpkins 2008 note documents an earlier numerical route. Thus lack of continued work is not an established historical fact. Wider computation can change feasible horizons and model sizes, but does not prove an inaccurate approximation becomes accurate, supply an absent model family, or reveal an unknown future objective. No hardware-only resurrection is established here as of 2026.

The supplied future cost schedule is a substantial advantage. If the later task were different, information dismissed as irrelevant could become important. The funded problem therefore needs a declared family of future demands, rather than an impossible promise to retain every possible historical distinction. This point connects the control problem to biological learning before reward, without claiming identical implementations.

## Our finite-state boundary, not a claim of inevitable practical failure

Suppose an agent observes one of all possible n-bit histories, retains only B bits with B<n, and later receives a query asking for any one historical bit. Assume no other channel can reveal the history. Two distinct histories must map to the same retained state; choose a bit on which they differ. The same query and state cannot guarantee the correct answer in both histories. Randomization cannot supply the missing world-specific distinction with certainty.

This elementary pigeonhole argument concerns worst-case exact answers and an unrestricted bit-query family. It is not a lower bound for natural intelligence, approximate usefulness, or a structured world. Its diagnostic purpose is to make future-task restrictions explicit. Once that family is restricted, the relevant question is whether the learner preserved what was sufficient for it, at the declared cost.

## Present inference and refuters

I assign high confidence to action-dependent identifiability in the stated model, and low confidence that this exact cause dominates current general agents. Positive interactive adaptation and human-assisted scientific workflows count against a blanket inability to obtain useful new evidence. Modern failures attributed to acquisition must still exclude an incorrect supplied model class, unavailable intervention, worthwhile risk avoidance, and later misuse of actually adequate observations.

The acquisition-policy claim is refuted for a case if the recorded observations already distinguish the necessary decision under the declared priors, or if no allowed affordable experiment could improve that decision. A matched change of obtainable information leaving the deficit intact would likewise push the explanation downstream. Merely adding computation or an answer-bearing hint would not isolate this cause.
