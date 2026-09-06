# Audit of a claimed causal-discovery obstruction

Status: bounded Phase 1 mathematical consultation; shared tools and filesystem, so this is not an independently isolated review. No experiments or mechanism proposals.

Source: Amartya Roy and Sonali Parbhoo, *Why LLMs Fail at Causal Discovery and How Interventional Agents Escape*, arXiv:2605.27567v1, 26 May 2026, **preprint**. [Versioned primary text](https://arxiv.org/html/2605.27567v1), accessed 2026-09-06. Inspected §3–5, Appendix B, the relevant Appendix C discussion, and Appendix D.2. This is not a complete paper review.

## Stated assumptions and disputed step

Definition 1 uses normalized kernel similarity. Theorem 1 nevertheless bounds the difference of unnormalized linear scores. The diagonal assumption is an upper bound, not equality of feature norms. Writing the paper's quantities as

\[
s_\pm=\langle w,\phi_\pm\rangle,\quad \|w\|\le B,\quad
a=\|\phi_+\|\le\kappa,\quad b=\|\phi_-\|\le\kappa,\quad
\frac{\langle\phi_+,\phi_-\rangle}{ab}\ge1-\delta,
\]

its asserted bound is

\[
s_+-s_-\le B\kappa\sqrt{2\delta}.
\]

Appendix D.2, Eq. 7, goes from

\[
\|\phi_+-\phi_-\|^2\le(a-b)^2+2\delta ab
\]

to an upper bound of \(2\kappa^2\delta\). The stated assumptions do not justify that last step.

## Our counterexample and deduction

Take the real one-dimensional feature space, \(\phi_+=1\), \(\phi_-=1/2\), \(w=1\), and \(B=\kappa=1\). The Gram matrix

\[
K=\begin{pmatrix}1&1/2\\1/2&1/4\end{pmatrix}
\]

is positive semidefinite: it is the outer product of \((1,1/2)\) with itself. Both diagonal bounds hold, and normalized similarity is exactly one. Thus the pair qualifies at \(\delta=0\), while its score gap is \(1/2>0\). It also qualifies at \(\delta=0.01\), for which the claimed upper bound is \(\sqrt{0.02}\approx0.1414<0.5\). Excluding zero therefore does not rescue the claim.

The distinction is angular versus radial: identical feature directions permit different feature magnitudes. Cauchy–Schwarz actually gives

\[
|s_+-s_-|\le B\sqrt{(a-b)^2+2\delta ab}.
\]

An additional equal-norm assumption would recover the asserted bound. No such assumption appears in the theorem or its cited definition and setup. Normalizing the similarity ratio does not itself normalize the scored features. The theorem expressly covers any scorer of its stated form; the counterexample does not need to model an actual trained language model to falsify that quantified statement.

## Oracle boundary and diagnostic decision

Algorithm 1 obtains answers from a frozen LLM given the premise and proposed intervention query. Appendix B and Appendix C explicitly say this substitutes for physical experiments. Assumption 1 supplies better-than-chance correctness about intervention effects.

**Our judgment:** exclude this theorem as support for a general claim that scaling or current learning paradigms cannot close the programme's gap. The counterexample establishes a defect in the stated theorem, not impossibility of any corrected theorem and not falsity of every empirical result. Separately, hypothetical answers from a fixed model do not, without additional evidence, demonstrate acquisition of previously unavailable facts through interaction with an unknown world. We have not audited the empirical results, code, or remaining convergence theorem.

Tool errors in this bounded audit: none.
