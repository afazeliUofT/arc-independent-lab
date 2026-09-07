# Observer recovery: the exact query and its conditioning

PI analytical supplement, 2026-09-07. No new experiment, candidate, formal verdict or revision to the frozen observer protocol is made here. The proofs below delimit the existing result; they are elementary linear algebra, not claimed new theorems. The primary-method mapping is documented separately in `evidence/P3_OBSERVER_PRIMARY_AUDIT_2026-09-07.md`.

The useful diagnostic question is not simply whether old parameters survive. It is whether the particular old answer is determined by the current permitted interface, how much computation is needed to obtain it, and whether small errors destroy its usefulness. These are three different questions.

## 1. Query identifiability under a declared state family

Let the current state be

\[
\theta=c+u+v,\qquad u\in U,\quad v\in V,
\]

where the initial contribution \(c\) and the linear subspaces \(U,V\) are known. The desired historical answer is \(Lu\), for a known linear map \(L\). For this section, **every pair in the unrestricted product \(U\times V\) is an admissible history summary**. This domain assumption matters.

The answer is uniquely determined by \(\theta\) for every admissible pair if and only if

\[
U\cap V\subseteq\ker L.
\]

To prove sufficiency, suppose \(u_1+v_1=u_2+v_2\). Their difference \(w=u_1-u_2=v_2-v_1\) lies in \(U\cap V\). The condition gives \(Lu_1-Lu_2=Lw=0\). To prove necessity, take any \(w\in U\cap V\) with \(Lw\ne0\). The admissible pairs \((u,v)=(w,0)\) and \((0,w)\) produce identical current states and different answers. No decoder of that state and the same supplied interface can answer both correctly.

Recovering the complete old contribution, \(L=I\), requires \(U\cap V=\{0\}\). Recovering a query can require less. For example, let \(U=\operatorname{span}(e_1,e_2)\), \(V=\operatorname{span}(e_2)\), and \(Lu=u_1\). The second coordinate of the old contribution is ambiguous, but its first coordinate is exactly available. A claim that the whole historical state must be identifiable before any historical answer can be recovered is therefore too strong.

For an explicit decoder, let the columns of \(A\) be a basis for \(U\), and let \(P\) be orthogonal projection onto \(V^\perp\). Then \(P(\theta-c)=PA\alpha\) for \(u=A\alpha\). Under the condition above,

\[
Lu=LA(PA)^\dagger P(\theta-c).
\]

The Moore–Penrose inverse need not recover the actual coefficient vector \(\alpha\). Its error lies in \(\ker(PA)\), which is contained in \(\ker(LA)\); the queried answer is unaffected. More generally, for unrestricted latent vectors \(x\), the query \(Cx\) is determined by \(Mx\) exactly when \(\ker M\subseteq\ker C\). This is the same identifiability condition expressed without a two-subspace decomposition. The companion primary-method audit connects this condition to the implemented query-specific null-space test in [Lenth's published 2015 estimability paper](https://journal.r-project.org/articles/RJ-2015-016/RJ-2015-016.pdf), accessed 2026-09-07.

This construction assumes known subspaces and baseline. It does not learn the history contract, discover the decoder or establish that actual updates stay inside those subspaces. A stored historical basis is a memory channel. A basis obtained from a callable current model is supplied interface information, with a cost to obtain and process it. An unknown baseline or an unmodeled update direction changes the admissible state family; using the old decoder would no longer have the stated guarantee.

## 2. Exact recovery can be fragile

The frozen observer has nonzero old and subsequent feature vectors \(a,b\), zero initialization, and the update contract

\[
\theta=\kappa a+\delta b.
\]

Its old boundary answer is \(\kappa\,a^Ta\). With \(p=P_{b^\perp}a\), its implemented readout is

\[
\widehat y_A=\frac{p^T\theta}{p^Ta}\,a^Ta,
\qquad p^Ta=\|p\|^2.
\]

This formula equals the old answer whenever \(p\ne0\) in exact arithmetic. The actual implementation takes this arithmetic branch only when its squared-norm and denominator guards exceed the specified tolerance; otherwise it abstains. It is residualization, not evidence for a new recovery algorithm. The inspected historical primary mapping and its source-version limits are in the companion audit. [Frozen implementation](https://github.com/afazeliUofT/arc-independent-lab/blob/7da5cc4ce22fac3163408a4889517c86d386f407/scripts/run_learner_observer.py), accessed 2026-09-07.

Now perturb the current state by an arbitrary vector \(e\), keeping the supplied features exact. If \(a\) has unit norm and its angle to \(b\) is \(\phi\), the answer error satisfies

\[
|\Delta\widehat y_A|=\frac{|p^Te|}{\|p\|^2}
\le\frac{\|e\|}{|\sin\phi|}.
\]

The bound is attained by perturbations parallel to \(p\). For general \(a\), the factor is \(\|a\|/|\sin\phi|\). Thus two distinct directions suffice for exact recovery, while directions close to collinearity can make the readout arbitrarily sensitive. This is a deterministic perturbation bound, not a measured noise distribution, a claim of observed numerical failure or a complete floating-point error analysis. Errors in the supplied features require a separate bound.

The frozen coordinate rotations and reflections preserve the angle. They therefore test dependence on a privileged coordinate representation, not robustness to a collapsing angle. The frozen collinear branch abstains according to its tolerance; that abstention is part of the programmed reader. No extra angle sweep or threshold change has been run in this audit. [Protocol](https://github.com/afazeliUofT/arc-independent-lab/blob/7da5cc4ce22fac3163408a4889517c86d386f407/docs/followups/P2_LEARNER_OBSERVER_PROTOCOL.md), [reported result and limits](https://github.com/afazeliUofT/arc-independent-lab/blob/7da5cc4ce22fac3163408a4889517c86d386f407/reports/P2_LEARNER_OBSERVER_001.md), accessed 2026-09-07.

In the general decoder, sensitivity to an additive state error is bounded by the operator norm \(\|LA(PA)^\dagger P\|\). Numerical rank and small singular values therefore belong in any future operational recovery claim. Merely reporting zero reconstruction error in one well-conditioned construction does not settle this cost or stability question.

## 3. Do not overstate the impossibility result

The subspace theorem quantifies over every pair in \(U\times V\). Actual training may admit a smaller set \(\mathcal H\subset U\times V\): a finite gain codebook, constrained update schedule, or relation between coefficients can remove the ambiguous pairs used in its necessity proof. For a restricted family, the correct condition is simply that equal available states and interfaces imply equal queried answers **within that family**.

Even with collinear directions, a finite coefficient codebook can make every allowed sum correspond to one old coefficient. For example, if \(u\) has coefficient in \(\{0,1\}\) and \(v\) in \(\{0,3\}\) on the same known nonzero direction, the four possible sums distinguish the old coefficient. This analytical example is not an experiment and is not asserted to be the frozen run's particular codebook. It shows why the existing reader's collinear abstention alone cannot prove impossibility for every other allowed reader.

Likewise, the frozen stripped-interface counterhistory removes the subsequent feature access and considers a broader unknown-geometry family. Its conclusion belongs to that restricted-access comparison. It does not refute recovery with the full supplied API. A valid future negative certificate must list both admissible histories, the exact common accessible state and differing desired answers. It must not grant the negative case a larger history family than the positive case without saying so.

## 4. Consequence for the diagnosis

The positive learner-access result survives as a narrow diagnostic: a supplied program using the original permitted model API can extract an old answer from current weights when the ordinary answer path no longer reports it. It does not establish autonomous discovery or invocation of that program, unrestricted recoverability, numerical robustness, or prevalence in modern large models. No bottleneck rank is promoted here.

C4 exposes the same distinction by different mathematics. Its retained witnesses allow reconstruction of alternative scopes, but its selected-scope response does not consult all of them. That is a response-rule limitation, not proven erasure. The shared investigative target is therefore an explicit account of accessible evidence, admissible history, actual computation, and resource/stability cost. These constraints are inputs to future programme judgment, not a new mechanism invented to escape the novelty audit.
