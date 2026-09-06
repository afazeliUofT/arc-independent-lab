# Phase 3 novelty audit — first review packet

2026-09-06. **Primary-method audit completed for the approved operations and their shared proposition; independent verdict pending.** This is the PI's analysis, not a GO/KILL decision. No Phase 3 candidate treatment has been run, and no completed or approved `PROGRAMME.md` is claimed.

The audit finds strong reductions for the developed operations, and a substantive gap in their intended combination. That is a useful result: it tells us which mechanisms cannot yet justify a new-method programme and where the specification fails to express the scientific commitment that motivated it. It does not establish that the diagnosis was wrong or that a combination of known operations cannot matter.

## Authority and frozen object

The [published Phase 2 answer](https://github.com/afazeliUofT/arc-independent-lab/blob/d9200bd6061a63cf82037c2fc31f361fa0109cb3/state/ESCALATION.md), accessed 2026-09-06, approves `IDEAS.md`, SHA-256 `73cab9f6ab1f5eda80c7c2adc6d2ed556c63d5652fd65434e4cc4b24383dc3b8`, and imposes the three audit requirements addressed below. Its underlying operation specifications are `docs/P2_OPERATION_SPECIFICATIONS.md`, SHA-256 `d37a52eeb569461503b262d2790a656048624ede4790aeb49254e5a9f133c26f`. Both remain unchanged. The approved diagnosis also remains unchanged.

Public checkpoint and approval verification: `evidence/PHASE2_APPROVAL_AND_CHECKPOINT006_VERIFICATION.json`, SHA-256 `2eedb9d6ac2a6c63ee99d333e2ec334f1f7d474e6343933a30364645781d139c`. The answered escalation is preserved in `state/escalations/2026-09-06_PHASE2_APPROVED.md`.

## The audit at a glance

| Object | Primary comparison and reduction | What remains distinct or unresolved | PI disposition for review |
|---|---|---|---|
| **C1: retain compatible executable explanations** | Finite-automaton subset construction, with model/state pairs as states and action/observation pairs as input symbols; relational resets and future-output queries map explicitly | The reporting convention and supplied model construction are explicit, but no different inference operation appears | Exact state/query reduction certificate; no new-mechanism claim supported |
| **C2: select evidence by its future decision value** | Finite Bayesian belief planning with experiment trees, action-dependent world changes and terminal decision losses | Scope requires task-specific terminal decisions to be available; finite lookahead and out-of-model guards must be matched | Exact modeled-domain selector reduction; no novelty clearance from outperforming entropy-only acquisition |
| **C3: translate current features into an old interface** | Regularized representation matching and model stitching; additionally, exact all-history old-query equivalence to direct cached-response refitting | A particular historical executable need not share every cache/schedule convention; history and compute budgets differ across real comparison methods | No evidenced structural novelty in the recovery operation; cached-response refitting is mandatory comparison |
| **C4: select a scope using retained contradictions** | Bounded Boolean, untruncated AQ seed-star selection with matching preference and tie order | Published AQ's complete classifier and inconsistency policy differ; C4's alias/length and abstention wrapper is not established as a literal whole-method identity | Scope-selection core reduced; wrapper priority/behavior remains a bounded open audit issue, not a positive novelty finding |
| **T: preserve unresolved distinctions, act on them, distinguish knowing from choosing** | Integrated antecedents include KWIK-Rmax, Bayes-adaptive POMDPs and knowledge-based contingent planning | Approved components do not specify a full joint interface; C4 can collapse compatible scopes; a conservative completion requires explicit new wiring | Separate joint claim retained. Broad principle has prior art; exact approved combination lacks a complete specification and guarantee |

An exact reduction is a kill under the programme's rule once the required independent review validates the relevant scope. The PI has not issued that verdict. A reduction of an operation's core is not automatically a proof that every wrapper, output or combination has identical prior art. Equally, a different error label or fixed scheduling convention does not establish a new learning operation.

## Requirement 1: replace C3's wrong comparator

My Phase 2 flag was inadequate. Ridge regression identified the estimator and failed to identify the comparable method. The corrected audit reads the methods of representation equivalence/stitching, paired-anchor latent translation, feature-evolvable streaming, continual drift compensation and Zheng et al.'s supervised recovery. It maps their actual history channels, direction of transport, parameter updates and reader behavior. It does not treat all alignment methods as identical.

The strongest algebraic result concerns C3 itself. With cached old activations \(R\), fixed old reader \(W\), current anchor activations \(Z\), and its positive penalty \(\lambda\), set \(Y=RW\) and \(D=TW\). Then

\[
D=(Z^\top Z+\lambda I)^{-1}(Z^\top Y+\lambda W)
=\arg\min_D\{\|ZD-Y\|_F^2+\lambda\|D-W\|_F^2\}.
\]

Every old-query vector is therefore \(f_\theta(x)D=f_\theta(x)TW\), including between refreshes and after resets that preserve the declared state. This does not assume full-rank anchors or successful recovery. The cache contains old response vectors before fixed postprocessing, not merely final class labels. The transformed storage can have a different cost from literal C3, which the audit counts rather than hiding.

This is a behavioral reduction derived from our specification, not historical-priority proof by itself. Together with the primary matching/stitching family, it makes the proper comparison concrete: C3 cannot have an output advantage over an exactly matched cached-response refit. A discrepancy would need an input, objective, precision or implementation difference.

Full mapping, separating examples, source versions and limits: `evidence/P3_C3_PRIMARY_AUDIT.md`, SHA-256 `07116664720e544d8cc6d8dd979b3469d50ded587f1d2c1175ade5c8a87d3864`. Primary operational antecedents include [Lenc and Vedaldi, CVPR 2015](https://www.cv-foundation.org/openaccess/content_cvpr_2015/papers/Lenc_Understanding_Image_Representations_2015_CVPR_paper.pdf), [Csiszárik et al., NeurIPS 2021](https://proceedings.neurips.cc/paper/2021/file/2cb274e6ce940f47beb8011d8ecb1462-Paper.pdf), and [Maiorca et al., NeurIPS 2023](https://proceedings.neurips.cc/paper_files/paper/2023/file/ad5fa03c906ca15905144ca3fbf2a768-Paper-Conference.pdf), all accessed 2026-09-06; published papers. The detailed audit marks the HAL version actually read as a preprint.

## Requirement 2: separate C3 from the observer finding

I have chosen the explicitly authorized option of keeping C3 unchanged and stating its weaker historical-information requirement. C3 stores pre-boundary activations and an old readout. It is a different operation from recovering an estimate with the learner's current weights and callable feature map. No successful observer case validates C3.

The observer remains consequential because it separates information available under that learner's actual API from the ordinary response path that fails to use it. But “available” is not “autonomously discovered and invoked.” Its supplied training contract and fixed feature map remain material. The finding is not a demonstration that arbitrary old knowledge is recoverable from any current checkpoint.

The observer evidence remains frozen: `reports/P2_LEARNER_OBSERVER_001.md`, SHA-256 `5503b185549fcce4daa841a9f4445f53d4f94dc3a43a73440bf877b2d38d1f11`; `artifacts/P2_LEARNER_OBSERVER/20260906_001/results.json`, SHA-256 `9c6c95c115e9d350e26c43707092c65208020eac9b02b91d389d335fa3febd08`. The metadata-completion limitations remain documented in the existing report; no trace or approved interpretation was silently rewritten.

Zheng et al.'s biography procedure uses old supervised examples to fine-tune a checkpoint and tests on other old examples. It supplies a recovery comparison with a different information and parameter-update budget. The audit also records a scalar counterexample to the paper's displayed Lemma F.1; that narrow theoretical correction is separate from its empirical finding and is not used to dismiss it. [Published ICLR 2025 paper](https://proceedings.iclr.cc/paper_files/paper/2025/file/a774503daed55eb53c634847ae071ec7-Paper-Conference.pdf), accessed 2026-09-06; see the method and exact theoretical scope in the C3 audit.

## Requirement 3: audit the shared proposition

The auditable proposition is: **retain every still-compatible distinction, let its decision consequences govern feasible evidence acquisition, and release a factual answer as known only when the retained alternatives agree.** “Known” is conditional on the supplied class containing the world; an empty class signals model inconsistency, not universal knowledge. Selecting a Bayes action is a different output and can coexist with unresolved uncertainty.

This commitment has important integrated antecedents. KWIK-Rmax uses unknown predictions to change planning and updates the learner from actual experience. Bayes-adaptive POMDPs preserve uncertainty over model parameters alongside world state and plan through the resulting beliefs. Knowledge-based contingent planning distinguishes known facts, known negations and unavailable information. The full methods audit preserves their supplied-language, observation-access, inference-cost and reset assumptions. [Li et al., expanded journal paper](https://thomasjwalsh.net/pub/Li11Knows.pdf), [Ross et al., NIPS 2007](https://www.cs.cmu.edu/~sross1/publications/Ross-NIPS07-BAPOMDP.pdf), [Petrick and Bacchus, AIPS 2002](https://cdn.aaai.org/AIPS/2002/AIPS02-022.pdf), all accessed 2026-09-06; published papers.

The most consequential specification problem is inside C4. With seed signature `(1,1)`, negative `(0,0)`, atoms `A,B`, and one allowed literal, both scopes `A` and `B` fit the record. C4 picks one by its tie rule. If it picks `A`, it licenses the old relation at fresh `(1,0)`, even though a world with true scope `B` is still compatible. No aliasing or length failure is detected. This stipulated mathematical history refutes a guarantee that C4 preserves all unresolved scopes.

C1 could veto that use if the appropriate worlds were supplied and every rule application passed through its agreement test. But that coupling, shared hypothesis interpretation and precedence rule are not in the approved combined specification. A conservative reference completion is written out in `evidence/P3_THROUGHLINE_PROPOSITION.md`; it requires positive prior/reset support and explicit query semantics. It shows how to make the desired guarantee conditional and reviewable. It is not evidence that one prior paper published the exact whole package, and adding C4's own wrapper to a comparator cannot independently prove that wrapper's historical novelty or non-novelty.

The correct audit outcome therefore remains split: strong prior art for the broad closed loop; a counterexample to an unqualified guarantee from the approved components; and an unfinished exact historical audit of a specifically completed joint operation. Four component reductions are not being used as a substitute for that outcome. An unspecified composition is also not being awarded novelty by default.

Primary through-line record: `evidence/P3_THROUGHLINE_PRIOR_METHODS.md`, SHA-256 `2cfe2b3cfb38494a394134f7e017cab59ac994d6e70469d427f8361061374913`. The proposition and its append-only clarifications are separately pinned in the review manifest.

## Other component certificates

For C1, take the disjoint union of model/state pairs and let each actual action/observation select the compatible successors. A reset is another relational transition. Union and deduplication are exactly subset construction; the empty set remains absorbing. No separating history exists against that mapped state/query operation. A point predictor or a reset that refills discarded models is a weaker comparison. Full proof: `evidence/P3_C1_C4_PRIMARY_AUDIT.md`, SHA-256 `2de34586a2e902d5fc2c9ce71393ed92418dedd0a6c458c0a8db047b3144a784`. [Rabin and Scott, 1959 primary paper](https://raw.githubusercontent.com/CMU-HoTT/scott/main/pdfs/1959-Rabin-Scott-finite-automata.pdf), accessed 2026-09-06.

For C4, every negative defines the seed literals that could exclude it. An admissible scope hits every such difference set. A redundant literal never improves positive coverage and loses the length tie break, so the optimum can be chosen from the untruncated seed star. AQ's preference can reproduce it after the declared Boolean/length restrictions and matching tie rule. Its actual full classifier and handling of contradictions differ. The same certificate details that boundary and the cost of untruncated search. [AQ15 author technical report, 1986](https://www.mli.gmu.edu/papers/86-90/86-23.pdf), accessed 2026-09-06; technical report, not a claimed peer-reviewed article.

For C2, subtracting the expected terminal Bayes loss and experiment cost from a constant stop loss leaves the usual finite decision-planning ranking. The explicit construction handles a joint post-state/transcript kernel without exposing hidden state, and matches branchwise budgets and permitted policy trees. A task revealed only after experimentation must still be available before the task-specific terminal choice. Short trees plus replanning can miss jointly useful observations; world changes can have value without conveying information about the old world. Full proof and histories: `evidence/P3_C2_PRIMARY_AUDIT.md`, SHA-256 `d56c20d58d390130da2ef7091c1db550352e5593e6ce2e532aca48d91c42e4fc`. [Kaelbling et al., 1998](https://people.csail.mit.edu/lpk/papers/aij98-pomdp.pdf), [Huang et al., NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/file/c59f05d7ab3638b138cc61f32e1a7cd1-Paper-Conference.pdf), accessed 2026-09-06; published papers.

## Scientific decision and next gate

The best path is to review the reductions and the joint counterexample before launching candidate treatments. I am not allocating a large run to distinguish two operations whose permitted outputs have already been shown equal. I am also not closing the programme on that basis: the observer finding and the problem of retaining useful distinctions remain diagnostic leads, and the raw ideation population has not been exhausted.

The next work is an independently enforced review and the resource/control measurements needed for an honest programme design. The current shared-tools research consultations cannot issue that verdict. `docs/P3_DESIGN_DECISIONS.md` specifies the context-clearing controls, required comparator ladder, compute-accounting dimensions and route conditions. Laptop and HPC capabilities will be measured through one batched read-only inventory; no spending, treatment run or unattended model use is authorized by that inventory.

No additional paper request is needed for the arguments in this checkpoint: the decisive full methods were reached, and version-limited comparisons are labeled. The unavailable book from the earlier batch is not being made a dependency again. The withheld benchmark fact sheet will be requested if an interactive benchmark becomes an instrument choice; selecting one before the scientific route survives review would not help this decision.

The review should actively challenge whether a purported exact map merely imports the candidate into its comparator, whether a cache contains the answer-bearing history attributed to the current model, and whether the claimed joint knowledge guarantee actually reaches the final response. Those objections are addressed explicitly in the packet rather than left for a weak baseline to conceal.
