# Checkpoint046 result transport amendment

Recorded 2026-09-13 before the full48-row user profile. This prospectively amends the return-path restriction in `P3_DEVELOPMENT_EXECUTION_PLAN_046.md`. That original pre-execution record remains unchanged.

The PI authorizes a compact profile index and separate full worker reports. The user requires all results to be available directly from GitHub. Combining48 complete worker payloads under one16 MiB ceiling has no validated capacity bound. Separating those payloads removes that aggregate multiplication without changing the scientific workload, its thresholds, its operational allowance or the once-only reservation.

The only eligible return files are `REPORT.json`, `RECEIPT.json`, `CONFORMANCE.json` and `row_00.json` through `row_47.json` under the single manifest-addressed `artifacts/CHECKPOINT_046_RETURN/` directory. This is at most51 paths, each staged explicitly. The receipt pins the execution report SHA256 and the exact worker inventory with byte lengths and SHA256 values; it records the total return-file count. Missing or interrupted worker reports remain explicit; unrelated files, private papers and reservations are excluded from Git publication.

Each saved worker JSON retains its full summary and compressed, recoverable source evidence. The compact index carries row identities, status, usage, stage costs and the exact full-report descriptor. A worker report already written when its parent is interrupted is preserved as recovery evidence even if the parent did not finish indexing it. Such uncertainty cannot produce a completed verdict. Publication retries reuse these bytes and the first reserved invocation; they do not rerun measurements.

Individual worker reports remain bounded at16 MiB, compressed evidence decoding at128 MiB and the compact outer execution report at32 MiB. These are explicit output limits. Full48-row output and runtime have not been observed here. Any limit refusal is an incomplete result with available earlier evidence preserved; it is not permission to increase a scientific budget or claim target admission.

Validation is limited to the changed transport and recovery boundaries, with source identities frozen before execution. Prior successful conformance versions and the reasons for their corrections remain recorded. Hosted validation is distinct from the user's still-pending full resource profile. No native reviewer, model call, target experiment or HPC job is authorized by this amendment.
