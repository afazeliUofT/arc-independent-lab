# Specification corrections before the second Phase 2 deliverable

2026-09-10. PI response to the shared-workspace semantic consultation. This records clarification of proposed algorithms; no candidate was executed and no formal scientific verdict is issued.

The final specification has SHA-256 `25f3148827d22abbe587a6c2ff0c5a3ff2db1883f70e678f640f16d0f07a7c69`. The consultation's earlier draft findings remain unchanged in `P2_SECOND_SPECIFICATION_CONSULTATION_035.md`. The resolution below is a new record rather than an edit that would conceal those findings.

| Draft problem | Final operation |
|---|---|
| N4 required repeatable effects but seeded each word only once, so its queue could never start. | Seed words receive `m` trials; an empty queue triggers finite-word coverage so compositions can reveal effects. Exhaustion is explicit. |
| RESET could ambiguously enter the prediction alphabet or cross lagged histories. | RESET is a charged, logged boundary; its observation begins a new history. Observation lag zero and action lag one have exact meanings. |
| N1 resumed scores could refer to old data; prediction counts could remain stale when feature search stopped. | Search cursors carry table/predicate/constant versions; stale search restarts with spent work recorded. Counts must be current, or the query returns a computation status. |
| N2 signatures and conjectures could retain revoked or old-block support. | Query validity, full context scheduling and current block/panel/effect versions are explicit; VARIABLE evidence takes precedence and historical roles remain historical. |
| N3's experiment clock and incomplete credit were ambiguous. | A post-warm-up reservation counter controls coverage and validation; incoherent predictions make credit unavailable. The local score is an exact rational Brier difference, eliminating an unspecified floating-point sign/tie convention. |
| N4 mixed catalogue statuses and later contradiction were ambiguous. | Same-block support is rechecked; supported, variable and incomplete candidate sets remain visible with explicit status precedence. Execution also requires the exact logged preparation. |
| N5's output shape and query source were unspecified. | The reference reader is scalar, with fixed state/query dimensions and a finite source-query list derived from the source episode's prior ordinary-prediction log. |
| N5 cache ordering referred to scores not yet computed, and target withholding was too narrow. | Canonical expanded-tree enumeration remains fixed; cache use is memoization only. Source membership, selection and synthesis are frozen before any target state/query exposure, as well as before target old answers. |

Storage for the next action/observation is reserved before an action is issued. Reaching a cap stops progress while preserving completed evidence. These corrections make the algorithms more explicit; they do not establish that the algorithms repair the diagnosed failures.

The final N5 is deliberately narrower than a new learned search-controller claim: it learns a reading expression, and its cache does not change the exhaustive optimum. N4 remains weak until an exposed contrast is shown to support a useful later distinction. Both qualifications survive into the deliverable.

The governing process requires specified operations before nearest-method flags: [Phase 2 process at the verified base](https://github.com/afazeliUofT/arc-independent-lab/blob/53768f9fc6b867834e1ab03b86248b487a19b617/docs/governing/02_RESEARCH_PROCESS.md), accessed **2026-09-10**. The local specification freeze records that order; it is not an external attestation of private reasoning.
