# N1–N3 semantics consultation — checkpoint037

2026-09-11. **PI analytical consultation, not an independent review or formal disposition.** This note deduces consequences of the unchanged checkpoint035 specification. It introduces no algorithm change, executable candidate, treatment result, efficacy claim or historical priority finding. The review target remains whether interaction produces knowledge useful in later acquisition, retention and recombination.

## Frozen basis and evidence class

The following local source bytes were checked against their recorded SHA-256 values. Sections, rather than publication titles alone, identify the operative evidence.

| Source | Relevant scope | SHA-256 |
|---|---|---|
| `docs/P2_SECOND_OPERATION_SPECIFICATIONS_035.md` | Shared execution; N1 grammar/update; N3 construction, scoring and status rules | `25f3148827d22abbe587a6c2ff0c5a3ff2db1883f70e678f640f16d0f07a7c69` |
| `evidence/P3_SECOND_N3_PRIMARY_AUDIT_036.md` | §3.1 reachable zero-credit history; §3.2 conditional positive confound; §5 block-boundary gap | `ff22c14dff9507fcaa080a17f7ee5ba81c121d61aa75b219945f60acb8d3a668` |
| `reports/P3_SECOND_NOVELTY_AUDIT_036.md` | Separation of component deductions, actual N1–N3 coupling and hypothetical joint controller | `142b9b3080ec71b3046ae962e5c55992574ae6dac792d90c0b436778822c8e2b` |

These sources are pinned at repository commit `91bbec3e2900f18d2c2baef325d575a26e362165`. The lemmas below are new PI deductions from that specification, not observed candidate behavior. No new external-method comparison is claimed.

## Single-block finite-credit lemma

Fix one stationary resettable block, a valid fixed feature limit `K`, completed N3 warm-up, and subsequent execution under the frozen rules without deletion or replacement of selected predicates. Let `k0 = |Phi_after_warmup|`. Count an event only when a subsequent experiment receives an available numeric utility different from zero; both positive and negative values count.

**Lemma.** The number of such events is at most `K − k0`.

**Proof.** N1 appends selected predicates and never removes an existing one within this execution. Its selected list has length at most `K`. N3 assigns numeric utility zero whenever the scored trial adds no predicate. Therefore each numerically nonzero event requires at least one predicate first selected during its own trial. Trials occur serially, so these additions are distinct across events. At most `K − k0` additions remain after warm-up. Assigning one such addition to each event proves the bound. A trial that selects several predicates still contributes only one utility event.

The inequality can be strict. A predicate-bearing trial may receive an exact zero score, unavailable credit or no credit because execution/validation is incomplete. Additions during live updates from validation, or completed transitions of a trial that remains incomplete, also consume the finite inventory without necessarily producing a credited event. `UNAVAILABLE` and incomplete credit are **not numeric zero** and do not increment a utility mean as though they were zero-valued observations.

If a trial **starts with** `|Phi| = K`, it cannot select another predicate. If that trial and validation complete with numeric predictions and available credit, its utility is therefore zero. The trial that first reaches capacity can itself still receive nonzero credit. A volatile memory reset does not replenish capacity because the selected list is persistent.

This bounds the lifetime of new nonzero credit, not the lifetime of exploration or learning. Previously acquired utility values and macros can continue to influence proposals. Completed new words can still enlarge `F`; coverage can still select unexecuted words; N1 can still acquire transitions and improve count estimates. Zero-credit words can also change the proposal set and parent-score competition. Once capacity is full, there is no further positive-credit macro promotion under these rules, but the existing macro library remains usable. No efficacy failure follows from the lemma alone.

## One completion per literal recipe

Within the same block, both ordinary proposal selection and the coverage rule exclude a word already executed as a complete trial. Proposal deduplication uses the flattened literal action word. Consequently, a particular literal recipe can receive **at most one post-warm-up numeric utility observation**: obtaining one already requires a completed trial, which excludes another scheduled completion. A completed trial with interrupted validation or `UNAVAILABLE` credit cannot acquire a later scheduled calibration sample merely by being proposed again. An incomplete trial may remain eligible, but supplies no numeric credit until the required completion and scoring conditions hold. Warm-up's initialized zero is not a measured post-warm-up credit observation.

Thus the stored utility sums/counts do not by themselves establish repeated within-block calibration of a recipe's learning value. Distinct recipes and common parents can still provide many different observations. This is not a multi-block lifetime theorem. The frozen specification does not settle utility retention/recalibration, warm-up restart, coverage history or all selected-syntax policies at a new block. The checkpoint036 audit already flags that boundary; this note neither clears old values nor carries them forward as current evidence. Any chosen successor semantics must be dated and audited separately.

## Existing witnesses and strongest counterarguments

The checkpoint036 §3.1 example is a **reachable analytical N3 history**: in an always-zero, one-action world, warm-up followed by `aa` changes the frozen reader's correct-outcome probability from `2/3` to `4/5`. With `V=1`, paired Brier improvement is `32/225`, yet utility is zero because no predicate was added. This was derived from the scheduler; it was not an executed experiment.

By contrast, §3.2's positive confound is a **conditional state/score construction**. A predicate added elsewhere can open the gate while count changes explain improvement at an unaffected validation key. A complete reachable N1–N3 scheduler trace realizing those joint conditions has not been established. The two evidence classes must remain distinct.

The strongest defense is that N3 deliberately prioritizes representation acquisition, not every useful count update; the specification already disclaims causal attribution by the gate. A finite burst of valuable predicates and macros could suffice in a bounded world. Stable earlier utilities might remain useful, and a later design could choose a sufficiently large `K`. A single paired validation block can legitimately estimate local progress on its actual cases, although it does not establish repeated calibration or comparability across recipe-dependent validation distributions. These defenses prevent a general failure verdict; they do not prove that the particular gate, finite credit budget or inherited recipe scores improve later knowledge use.

## Focused reviewer questions

1. Does the finite-credit proof respect every permitted update, incomplete status and persistent-state rule? Is there any conforming single-block execution that defeats it?
2. Can the conditional positive confound be realized from empty state through the exact warm-up, mutation/coverage scheduler, N1 grammar/ties and validation order? If not established, what narrower inference remains?
3. Does a finite burst of representation-gated credit address a concrete acquisition failure, and what evidence would distinguish that benefit from additional count fitting or mere coverage?
4. Do single-observation parent utilities and whole-trial fragment promotion support the intended reuse claim? Comparisons must charge the same information, interactions and computation; no future-task answers may be supplied to a selector.
5. Which block-boundary semantics require an explicit successor specification before multi-block implementation? Could a strictly single-block assessment answer the immediate scientific question without inventing those semantics?

The recommended next decision is a focused independent assessment of these bounded claims and the checkpoint036 findings. This consultation supplies review material; it grants no formal verdict and does not replenish reviewer allowance or authorize a candidate treatment.
