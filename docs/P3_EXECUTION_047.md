# Checkpoint047 offline assessment handoff

Save **ARC_Independent_Lab_047_HOME.zip** in Windows Downloads and paste the supplied command from WSL home. The command resolves the Windows Downloads registry setting, verifies the whole archive, copies/extracts it within `~/ARC_Independent_Lab/delivery/`, and checks the complete bundle and pinned release. It requires the existing canonical checkout on `main` with its configured GitHub credentials.

The script verifies the already saved046 evidence in an isolated copy and checks that its assessment equals the published047 result. It then synchronizes the release by fast-forward only, adds exactly its new `REPORT.json` and `RECEIPT.json`, commits those files and pushes to the canonical GitHub repository. It preserves unrelated checkout changes, divergent history, earlier measurements, reservations and changed existing results.

This is a read-only evidence check plus authorized Git synchronization. It does not rerun Development046 or execute a learner, reviewer, model, target experiment or cluster job. The original046 reservation remains consumed. A completed047 assessment is reused if publication needs retrying. Read-only bookkeeping interrupted before producing a result may be safely retried; this grants no experimental repetition.

The ZIP contains all public Git history needed to reconstruct the assessment and its frozen inputs, plus the launcher and checksums. No private paper input is needed for this step. The results return through GitHub; no output attachment is requested.

This synchronization is optional: the next accounting implementation uses the already verified046 evidence and does not wait for the047 receipt. Read `reports/P3_RETURN_046_AND_RESOURCE_DECISION_047.md` and `docs/P3_ACCOUNTING_CORRECTION_PLAN_047.md`. The correction is specified but unimplemented, and scientific `B_comp`, `B_mem` and target admission remain unset.
