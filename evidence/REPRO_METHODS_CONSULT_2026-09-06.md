# Methods consultation: minimal sequential-regression failure

Date: 2026-09-06. Status: mathematical/adversarial consultation by a shared-workspace agent, **not an independent review or gate verdict**. No experiment was run for this note. Equations below are deductions from the proposed update, not external empirical findings.

## Initial proposal: exact expectations (superseded before execution)

Let the true gains be `m_A` and `m_B`; let A use `x=a(1,0)` and B use `x=a(1,1)`, with `a∈{−1,+1}` and `y=a*m_c`. Use the loss `L=(y−x·θ)^2/2` and the stated update with learning rate `η`. The action cancels out of every update.

Starting at zero, after `n_A` A samples:

`θ=(k,0)`, where `k=m_A[1−(1−η)^n_A]`.

During B, define `s=θ0+θ1` and `d=θ0−θ1`. After `n_B` B samples:

- `d=k` is invariant.
- `s=m_B+(k−m_B)(1−2η)^n_B`.
- `θ0=(s+k)/2`, `θ1=(s−k)/2`.

At `η=.1`, convergence is stable. B's prescribed prediction converges to its correct gain; A's prescribed prediction converges to `(k+m_B)/2`. Opposite gains produce pronounced A error after A was learned accurately. Same-sign gains slightly improve the finite-training A estimate, instead of forgetting it. The joint solution `(m_A,m_B−m_A)` exists, so representational capacity alone cannot explain the opposite-gain failure.

The observer decoder `d` recovers **the boundary estimate k**, not the exact true gain after finite A training. Its remaining error is `−m_A(1−η)^n_A`. Cross all four gain-sign combinations, use the same decoder without gain-dependent tuning, and retain finite-training error rather than describing it as zero. The invariant is exact in real arithmetic; numerical checks need a stated floating-point tolerance.

## What the demonstration can establish

The narrow finding is legitimate and useful: worse performance under the learner's prescribed readout need not mean that its parameters have lost all information about the earlier fitted value. Here the lost performance can be located precisely in changes to `θ0` while a known linear combination of parameters preserves the earlier estimate. Ordinary B updates have a component along the coordinate used for A predictions. The interference is immediate on entering the opposite-gain B block.

This is a constructed example of sequential supervised fitting. It can satisfy the brief's request to instrument a smallest failure **for this specific retention failure**, but it is not a replication of a particular paper's experimental result. Identify the literature claim it illustrates and retain that distinction. Analytic predictability does not invalidate the exercise; it does limit its evidential contribution to a mechanism illustration and a counterexample to equating behavioral decline with total erasure.

## Limits that belong beside the result

- Every noiseless observation reveals its context's gain through `y/a`. Action choice has no information value. This does not diagnose exploration, unknown context inference, causal discovery or knowledge acquisition under ambiguity.
- The context is supplied, the feature map is fixed, and the two rules never change. The discontinuity is a training-distribution switch, not interrupted execution or lost state.
- The observer knows the feature map, phase schedule, zero initialization and update structure. Its recovery calculation is not evidence that the learner can discover or use that decoder. Do not call this an implemented repair or learner-accessible memory.
- Preservation is special to the rank-one B updates and A-only initialization. It need not survive additional gradient directions, regularization, optimizer momentum or later phases. Those are limits, not extra experiments required for this small demonstration.
- This does not establish that observed forgetting in a modern model, an animal or a human has the same cause, nor does it rank this bottleneck against the programme's others.

## Instrumentation cautions

Record pre/post-update weights; phase and sample; prescribed A/B predictions and squared errors; `d`; decoder error against both `k` and `m_A`; and analytic residuals. Separate measured trace from the closed-form expectations. Include evaluations immediately before and immediately after the first B update.

Specify what “gradient overlap” means. Feature overlap is fixed (`x_A·x_B=1` for equal actions), but loss-gradient overlap depends on residuals. At an exactly fitted A solution its loss gradient is zero, although a B step can increase A loss. The exact change in half-squared A loss is

`ΔL_A=(θ0−m_A)Δθ0+(Δθ0)^2/2`.

Thus zero first-order overlap at the old optimum does not demonstrate harmlessness; the quadratic term matters. Action signs also make a raw cross-action feature dot product misleading unless their role is stated: the actual update and loss are action-sign invariant here.

An orthogonal-feature control is optional. “Same function class and parameter count” does not mean an optimizer-neutral comparison: changing coordinates changes SGD's metric, feature norms and potentially initial B predictions. If included, document those differences or match the relevant quantities. The four gain combinations plus exact trace are sufficient for the narrow illustrative claim; avoid expanding this into architecture testing during Phase 1.

## Pre-run amendment: normalized features and controls

The PI amended the planned shared-feature case to `x_A=a(1,0)` and `x_B=a(1,1)/√2`, with orthogonal and frozen controls. This amendment supersedes the initial proposal's run expectations; neither configuration had been executed when this consultation was written.

For the normalized shared case, A training still gives `(k,0)`. In B, `d=k` remains invariant, while

`s_n=√2*m_B+(k−√2*m_B)(1−η)^n_B`.

The B gain is `s_n/√2`; the A gain is `(s_n+k)/2`; the joint exact solution is `(m_A,√2*m_B−m_A)`. Both feature norms now equal one and the contextwise residual contracts by `1−η`. For equal action signs, feature overlap is `1/√2` rather than one. The observer-decoder argument and exact old-loss-change identity above remain valid.

Normalization changes the sign-control interpretation: **same-sign gains can now damage A too**, ultimately giving A gain approximately `±(1+√2)/2` when A training was accurate. Equal world gains no longer correspond to an A-trained parameter state that already nearly solves B. Same-sign cases are therefore not an expected “no-forgetting” control in this amended configuration. Opposite-sign cases remain the strongest directional conflict.

For the orthogonal case `x_A=a(1,0), x_B=a(0,1)`, the A gain remains `k`; the B gain after its block is `m_B[1−(1−η)^n_B]`. It has the same parameter count, function class, unit feature norms and scalar residual-contraction rate as the normalized shared case. However, at the B boundary its initial B prediction is zero, whereas the shared case's is `k/√2`. Report that difference; compare residual contraction relative to each boundary if comparing B learning curves. The control supports a role for representation/SGD geometry, without isolating a representation-independent property of “memory.”

For freezing the shared predictor after A, its A gain remains `k` and B gain remains `k/√2`. This locates the A change in subsequent updates and shows the corresponding absence of B adaptation; it is a control, not a successful solution of both contexts. Label clearly whether freezing applies only to the shared arm.

These bounded controls are proportionate to the diagnostic purpose. They do not change the central limitation: this is an instrumented fitting/retention subproblem, not a reproduction of the whole interactive-knowledge problem.
