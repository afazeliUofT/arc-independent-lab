# First reproduction: behavioural interference versus recoverable state

Written before code execution on 2026-09-06. This is a bounded Phase 1 diagnostic witness, not a mechanism proposal, a confirmatory experiment or a reproduction of a published benchmark's score. Configuration: `configs/P1_LINEAR_INTERFERENCE.json`; preserve it unchanged with the run.

## Why this small failure

We need to avoid equating a drop in old-task performance with erasure of old information. A transparent gradient-trained predictor permits inspecting all of its state and deriving exactly where interference begins. A minimal case can invalidate that inference without establishing how frequent the distinction is in current large systems.

The standard behavioural phenomenon is sequential learning followed by degraded performance on earlier tasks. Goodfellow et al. investigate it with neural-network task pairs and performance tradeoffs; they do not measure all information recoverable from the resulting weights. Our algebraic witness addresses the interpretation of that symptom, not their empirical rankings. [Goodfellow et al., arXiv:1312.6211, preprint version, PDF header v3, 2015 revision](https://arxiv.org/pdf/1312.6211), accessed 2026-09-06; methods/results sections inspected for the behavioural definition and scope.

## World, learner and reset inventory

An action `a` produces `y = a * m_c`, where the visible context `c` selects an unknown gain. The learner observes only the current context/action and the resulting response; evaluation labels are not training inputs. Its complete persistent state is a pair of weights. It predicts through a fixed feature map and applies online squared-error gradient descent.

The main feature map is `a * (1,0)` in A and `a * (1,1)/sqrt(2)` in B. It can represent any pair of context gains. Gradient updates are `theta += eta * (y - dot(x,theta)) * x`. Both contexts have equal feature norm for the chosen actions.

Train A, clear transient variables and switch to B, retaining weights. Probing A at each step never updates the learner and is accounted separately from its training interactions. This tests interference from intervening learning. It does not test retaining an undisclosed context cue across a boundary.

**Major limitation:** the action-response wrapper makes this a sequential supervised-fitting subproblem. Either noiseless action reveals the gain in one observation to an appropriate estimator. The predictor's slower gradient fitting is imposed by the chosen learner. Exploration, discovery of reusable causal factors and recombination are absent. The feature map and context labels are supplied, and the diagnosis must say so.

## Predictions before execution

At the A/B boundary write `k = theta_A0`; `theta_A1` is zero. In B, updates change the two coordinates equally. Thus `d = theta0 - theta1 = k` is invariant. Let `s = theta0 + theta1`. After `n` B updates,

`s_n = sqrt(2)*m_B + (k - sqrt(2)*m_B)*(1-eta)^n`.

The prescribed A readout is `(s_n + k)/2`, so it can deteriorate while `d` still recovers the boundary estimate. The ordinary B readout is `s_n/sqrt(2)`. This is a prospective algebraic expectation, not a reported numerical result.

The observer decoder receives only the current weights and the arm's known setup. It returns their difference for the shared arm and the first coordinate for the orthogonal control. Its comparison with the boundary estimate occurs only in evaluation. It is not installed into the learner's action/prediction path and is not presented as a repair.

This recovery depends on the chosen feature geometry, zero initialization of the unused coordinate and the B-only update direction. It establishes an explicitly readable old estimate in this construction, not all old observations or a generally available recovery algorithm. Finite precision and repeated context changes may change the conclusion.

## Controls and competing explanations

- Cross both old and new gains over their configured values. A decoder returning a hardcoded old target must fail this crossing.
- Freeze updates after A while keeping the same incoming B experiences. This isolates update-induced change from the boundary or passive passage of steps; it intentionally does not learn B.
- Use orthogonal context features with the same dimension, norms, observations and representable function class. This isolates feature/optimizer geometry, but changes the implicit optimization metric and the B starting prediction. It is a diagnostic reparameterization control; no efficiency or learned-factor-discovery claim follows.
- Check the recorded update equation and the closed-form B trajectory against the trace. Check exact representability of both gains by the stated feature maps. These are arithmetic/implementation checks, not pass thresholds for a scientific gate.

No seed uncertainty or population confidence interval is appropriate for this deterministic construction. The relevant evidence is the full trace and the scope of the algebra, not a significance test. No hyperparameter sweep, seed expansion or larger model will be added merely to make a small witness look substantial.

The exact old-loss change for a B update is `(theta0-m_A)*delta0 + delta0**2/2`. Record both terms. A zero old-loss gradient at an exact fit does not imply a finite update is harmless: the quadratic term remains. Feature overlap and loss-gradient overlap are different quantities.

## What would defeat the proposed interpretation?

If the observer decoder needs stored old samples/labels, if the invariant fails beyond floating-point arithmetic, or if ordinary A prediction does not change as derived, the intended trace explanation is not established. If the ordinary A readout remains accurate, that case is a counterexample to claiming universal interference, not a reason to discard the case. Even a clean match does not establish a ranked bottleneck across current AI; additional empirical work is required.
