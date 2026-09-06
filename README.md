# ARC Independent Lab

Autonomous research programme funded by Ali Fazeli. Current phase: **Phase 1 — diagnosis**. `DIAGNOSIS.md` is a working document, incomplete and not submitted for approval. No candidate repair has been proposed, selected or tested.

## Resume without conversation memory

Read `state/PROJECT_STATE.json` and `state/BUDGET.json`, then the last ledger entries. Check `state/ESCALATION.md` before work. The preserved governing pack is in `docs/governing/`; read its six files in the order in `00_START_HERE.md`. `docs/USER_AMENDMENTS_2026-09-06.md` records the later user instructions and overrides stale restrictions where explicit.

Verify repository state and checkpoint hashes before building on it. If blocked, only the human's `## ANSWER` section in `state/ESCALATION.md` clears the conversational-authority dependency. A prepared package is not proof that GitHub contains it.

## Scientific navigation

- `DIAGNOSIS.md`: computational demand and required incomplete sections, in the mandated order.
- `evidence/SCOUT_RECENT_AI_2026-09-06.md`: bounded methods-based AI source map, including recent preprints and counterevidence.
- `evidence/SCOUT_BIOLOGY_2026-09-06.md`: bounded biological constraints with evidence classes and limits.
- `evidence/SCOUT_ARCHAEOLOGY_2026-09-06.md`: historical methods, unresolved uptake explanations and explicit correction record.
- `docs/PAPER_REQUESTS_2026-09-06.md`: initial human full-text request batch.
- `evidence/PAPER_REQUESTS_001_RESOLUTION.md`: supplied-method corrections and remaining scientific limits; no immediate fetch outstanding from this batch.
- `reports/P1_REPRODUCTION_001.md`: instrumented performance/interference witness, raw-artifact hashes and scope.
- `docs/TOOLING_EVIDENCE.md`: what has actually been checked about this runtime.

The bounded Phase 1 reproduction is complete; the broader diagnosis and bottleneck ranking remain unfinished. Phase 2 requires Ali's approval of the completed diagnosis. Ideas that occur during Phase 1 go into the parked file without development or rereading. The other programme and withheld benchmark fact sheet are outside the permitted evidence base.

The canonical experiment entry point is `scripts/run_reproduction.py`. Reproduce with `python3 scripts/run_reproduction.py --config configs/P1_LINEAR_INTERFERENCE.json --run-id YOUR_NEW_RUN_ID`. Existing raw-run directories are never overwritten. No packages, GPU, cluster or model API are required for this witness. See its report before interpreting the result.

Original research code and associated project documentation use MIT-0. Referenced papers retain their own copyrights and are not redistributed here. No paid API, extra credits, hosted compute rental or unattended model loop is configured.
