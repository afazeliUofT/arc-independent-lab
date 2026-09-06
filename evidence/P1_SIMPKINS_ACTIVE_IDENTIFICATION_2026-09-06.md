# Simpkins et al. (2008): active identification under supplied structure

All external sources accessed **2026-09-06**. Phase 1 consultation using shared tools/filesystem; not an independent review. No experiments, model API calls or mechanism proposals. The earlier CLIN/Voyager notes are unchanged.

**Source and reading extent.** Alex Simpkins, Raymond de Callafon and Emanuel Todorov, *Optimal trade-off between exploration and exploitation*, **published proceedings of the 2008 American Control Conference**, pp. 33–38, June 11–13, 2008. [Full author-hosted primary paper](https://roboti.us/lab/papers/SimpkinsACC08.pdf). Read all six pages, including methods, results, captions and references. Rendered page 35 to check the equations against the text extraction. Local PDF: `private_sources/p13_agents/simpkins_acc08.pdf`, SHA-256 `831ce4b14c80b0cf3d27ebc1dd89f112b4dc83e6c9a24512fe653cace520bc9e`. No unavailable methods or abstract-only claims.

## Compact primary-source capsule

The agent controls hand position while tracking a visible target through an uncertain linear mapping. The mapping family, Brownian drift, noise covariances and Gaussian initial prior are supplied; observations depend on hand position. Kalman-Bucy estimation tracks mapping mean/covariance; the controller approximates a discounted tracking-and-effort objective. The belief-augmented state has eight dimensions in the studied two-input/one-output case; a three-input/two-output example would have 32. Grid discretization motivates function approximation. Features include supplied cost terms, quadratic terms and Gaussian corrections; convergence/error guarantees are absent. Comparators are certainty-equivalent estimation/control, nonadaptive feedback, and random input. Reported tracking and uncertainty contrasts favor the proposed controller, but comparator gain/stability matters. The paper warns that small Bellman residual does not ensure best control performance. Four humans completed 24 one-minute trials, following an explicit visual tracking instruction. Qualitative movement similarities are preliminary; the controller omits human delay/biomechanics, and human exploration cost was unmeasured. No cross-task retention or novel recombination test is reported. [Primary paper, §§II–VI, Table I and Figures 1–3](https://roboti.us/lab/papers/SimpkinsACC08.pdf).

## Information and action: our deductions from the stated model

Let a local constant mapping be a vector \(m\), hand position \(h\), and an observed scalar cursor coordinate \(z=h^\top m+\epsilon\). Movement has two consequences: it changes the cursor and changes the measurement of the unknown mapping. This is a dependency between action and obtainable evidence, not a psychological label for curiosity.

Suppose every chosen hand position lies in a subspace \(S\). For any nonzero \(v\) orthogonal to \(S\), the two maps \(m\) and \(m+v\) predict identical noiseless observations on all those positions. With the same additive noise model their likelihoods remain identical. Unless the prior already excludes one map, the observation sequence cannot distinguish them. A later hand position outside \(S\) can make their predictions differ. This construction is a deduction, not a simulation result or a claim about the numerical controller in the paper.

The implication is precise: a learner can estimate as well as possible from its chosen observations yet lack a distinction needed later. The missing distinction is then an acquisition problem. It is not evidence that retained information was erased or became unreadable. Conversely, reducing uncertainty in every possible direction is not automatically worth its control cost. A direction irrelevant to today's action can become relevant under a changed goal or feasible-action set. Relevance must therefore be indexed to the declared future demand; it is not an intrinsic property of a stored parameter.

These conclusions depend on the information-generating relation, not on a proposed architecture. They also identify the supplied knowledge that must not be credited as discovered: the coordinates, linear form, available intervention, observation semantics and uncertainty family. Unknown coefficients within a known family are a real learning demand, but a narrower one than discovering that family.

## Algebraic caution: do not copy the printed formulas as an audited implementation

The page image confirms two apparent transpose errors, rather than extraction artifacts. This observation does not invalidate the underlying expectation identity or establish how the authors implemented their simulations.

1. With the paper's declared dimensions \(H\in\mathbb R^{n_s\times n_sn_h}\) and \(\Sigma\in\mathbb R^{n_sn_h\times n_sn_h}\), the printed covariance term in Eq. (12), \(\operatorname{tr}(H^\top\Sigma H)\), is dimensionally incompatible in the demonstrated redundant case. Independently expanding the squared error gives

   \[
   \mathbb E[\|Hm-s\|^2]
   =\|H\hat m-s\|^2+\operatorname{tr}(H\Sigma H^\top).
   \]

2. Given dynamics containing \(Bu\), with \(B\in\mathbb R^{n_x\times n_h}\), differentiating \(\tfrac12u^\top u+(Bu)^\top\nabla v\) yields \(u^*=-B^\top\nabla v\). Eq. (16) prints \(-B\nabla v\).

Both corrected identities above are our algebra, not silently repaired quotations. I have not audited every stochastic-calculus step or obtained result-producing code. Accordingly, this paper supports the conditional action/evidence dependency and its reported restricted comparisons; it is not treated as a certified general optimality result.

## Historical and biological implications

This is evidence of an active research tradition revisiting an old difficulty, not evidence that dual control had disappeared. The computational problem is visible before any modern agent vocabulary: decisions influence what can subsequently be estimated, but representing and optimizing over uncertainty increases the state that must be considered. The present paper's reference to earlier dual-control work is a historical lead; it is not a substitute for reading those originals.

Our 2026 judgment is conditional. Faster arithmetic and larger memory can relax the cost of a specified finite approximation. They do not by themselves change a grid's exponential dependence on state dimension, certify an inaccurate value approximation, or discover an unsupplied model class. Whether the historically limiting operation is still costly enough to matter requires an actual implemented workload and hardware measurement. This audit supplies no such measurement and claims no hardware-only resurrection.

The human comparison is behavioral evidence that people can adapt their movements in this particular task. Similar movement timing can arise from several learning and control processes; it does not identify a unique internal algorithm. A score comparison that omits the organism's delays and physical constraints cannot establish an artificial-versus-biological competence ordering. The study neither demonstrates human retention across a substantial discontinuity nor the full funded conjunction.

**Effect on the provisional diagnosis.** Preserve a distinct acquisition explanation: apparently competent action under current evidence can fail to generate evidence needed for a later decision. Do not merge this with forgetting or loss of access. This paper supplies a precise restricted model and an older numerical demonstration; it does not establish the explanation's prevalence in frontier agents. No new paper request is needed for these scoped conclusions.

## Retrieval/rendering error

The PDF download and text extraction succeeded. The first visual-rendering attempt exited **127**, with this exact output:

```text
/opt/codex/runtimes/codex-primary-runtime/dependencies/native/poppler/poppler/bin/pdftoppm: error while loading shared libraries: libpoppler.so.160: cannot open shared object file: No such file or directory
```

Fallback rendering with installed PyMuPDF succeeded; the resulting page image was inspected. This was a local dependency error, not missing scientific evidence.
