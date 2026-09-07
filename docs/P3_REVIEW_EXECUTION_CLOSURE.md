# Exact execution dependencies for the observer archive check

2026-09-07. PI preparation for the frozen Phase3 audit. This closes a packet omission: the original 49-file review core included the observer runner and records but omitted the historical consistency auditor and some files that it checks relative to its own `ROOT`. Adding those inputs makes the existing check executable. It does not change the scientific specification, checker, thresholds or review conclusions.

The authoritative dependency list and receipt pins are in `evidence/P3_REVIEW_EXECUTION_CLOSURE_2026-09-07.json`. The unchanged auditor's SHA-256 is `871ab1e62a592d9b49f93d5d5d783e262f8db1cb15bcc0b8ba6191f0ca0d4b1e`, identical to `auditor_sha256` in the preserved original successful receipt, `evidence/P2_LEARNER_OBSERVER_CONSISTENCY.json`. Every input is checked against its recorded digest and the published checkpoint010 bytes at `9925b3697a2d829044539833f6ca1c26ac8d1702`. [Published original auditor](https://github.com/afazeliUofT/arc-independent-lab/blob/9925b3697a2d829044539833f6ca1c26ac8d1702/scripts/audit_learner_observer.py), accessed 2026-09-07.

The file, inventory and transition counts below cite the dependency manifest, SHA-256 `28db528e70e361593545f94ca72b4bd2eaf4cc0ed0705edd5cfdcbb29c10a2a5`, and `evidence/P3_REVIEW_EXECUTION_CLOSURE_CHECK.json`, SHA-256 `b3a48f115ec122dfabfbc86a9845b12a776edace4943e97f811d47906cada096`.

## The two archive inventories must stay distinct

The original checker requires exact raw-directory membership. The observer's original `SHA256SUMS` names 12 files; that checksum file itself makes a 13-file original view. The subsequent metadata completion added `hypotheses.jsonl`, `resolved_config.yaml`, `manifest_completion.json`, and their separate `ADDITIONAL_SHA256SUMS`. The current 17-file archive therefore has two declared, disjoint inventories.

The unchanged auditor is expected to reject the expanded directory. The existing completion report already records that limitation. This preparation did not run it against the expanded directory again, remove the metadata, alter its membership check, or pretend that the later files were emitted during the run. [Published metadata-completion account](https://github.com/afazeliUofT/arc-independent-lab/blob/9925b3697a2d829044539833f6ca1c26ac8d1702/reports/P2_LEARNER_OBSERVER_METADATA_COMPLETION.md), accessed 2026-09-07.

Instead, the parent process verified the complete expanded archive against **both** inventories and the completion manifest, then copied only the original 13 files into a new original-inventory view. Every copied byte equals the corresponding published byte. The later metadata remains in the authoritative archive and frozen scientific packet, where the reviewer must read its timing limitation.

## Exact broker operation

The prepared view is `delivery/P3_REVIEW_EXECUTION_CLOSURE_20260907_001/view/`. It contains 36 exact input files; 19 are additional read dependencies beyond the original 49-file core. Its relative paths reproduce the original lab layout because the historical auditor resolves `ROOT` from its own script path.

1. Read and verify the frozen `protocol_freeze.json`. Copy every `original_protected_hashes` and `frozen_input_hashes` dependency at its exact relative path, including the Phase1 protected files and dependency lock. Also copy the unchanged auditor and preserved original successful receipt. Do not execute the training runner or Phase1 programs.
2. Under the view's `artifacts/P2_LEARNER_OBSERVER/20260906_001/`, copy exactly the original inventory members and original `SHA256SUMS`. Check the complete source archive separately as described above.
3. Invoke the exact unchanged auditor with isolated Python and bytecode writing disabled:

```text
python -I -B <VIEW>/scripts/audit_learner_observer.py --run-dir <VIEW>/artifacts/P2_LEARNER_OBSERVER/20260906_001 --receipt <VIEW>/evidence/REEXECUTION_RECEIPT.json
```

4. The receipt must be new, outside the raw-run directory and within the view, as the original auditor itself requires. The parent broker owns receipt creation and collection. A future reviewer may request this one fixed operation; it must not receive arbitrary command editing, source-writing authority or unrestricted receipt-path selection. Give it read access to the verified receipt through the agreed output boundary.
5. Require process success, inspect the actual receipt, verify all copied inputs afterward, and verify both inventories in the authoritative source again. Compare the new receipt with the historical one: every field except the check timestamp must match.

The preparation script and exact command receipt are preserved alongside the view. This describes the necessary broker operation and its file layout; it does **not** establish that a future runtime has enforced every required restriction. The PI's present process is not an independent reviewer or an enforced read-only tool boundary.

## Result and limits

The unchanged historical auditor passed on the exact original view. The new receipt is `evidence/P3_REVIEW_EXECUTION_CLOSURE_CHECK.json`; the dependency manifest pins its SHA-256. It checked the same 6,912 recorded transitions, with the same recorded counts, tolerances, arithmetic residual and static source-interface results. All receipt fields except timestamp equal the preserved original receipt.

This is a repeat of a deterministic check over existing records. It produced no new training run, model call, metric, hypothesis or scientific verdict. Static argument/name inspection does not prove runtime information-flow isolation. Hash equality does not attest the historical execution. Metadata exported after the run remains post-run metadata; this recheck cannot make it prospective or repair the original runtime-emission omission.

The execution-closure files supplement the original scientific manifests; they do not replace them. Full reviewer context, tools, model access and output control must still be verified separately before requesting the independent scientific verdict.
