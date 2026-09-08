# Correct the metadata notification parser

Prepared 2026-09-08T16:52:06.978294+00:00. This is an operational correction within the already-approved post-login metadata operation, not a new scientific result or access request.

The supplied report is the requested artifact and its exact original bytes are accepted. The WSL dummy-file test passed, and native initialization returned the original Codex home. The reader then rejected a notification before obtaining configuration, account, quota or model-catalog data. The report states that the native process was reaped and its host-input checks passed. Credential metadata is unchanged; credential contents were not checked. Acceptance: `evidence/GATE0_POSTLOGIN_016_OBSERVATION_REVIEW.json`, SHA-256 `eb9445c5383a981c0339edf74ae2168df69e5bc2fcb362107f91b2a96217081d`. Original report: `artifacts/GATE0_POSTLOGIN_OBSERVATIONS/20260908_001/REPORT.json`, SHA-256 `4aa0757da0d56a4db65ca7a33cf15d7454129c21fab7283457261d3a8ebcbba7`.

## Cause and correction

My parser modeled a notification as method/params only. The pinned native implementation emits an optional signed-integer `emittedAtMs` envelope field. That omission is a source-proven defect in my code and the synthetic fixtures; it is not evidence of failed sign-in. The discarded native message cannot be reconstructed, so I cannot claim its exact fields were directly observed. The exact source and a controlled reproduction establish a supported message shape sufficient to trigger the same failure. See `docs/GATE0_NOTIFICATION_ENVELOPE_SOURCE_2026-09-08.md`, SHA-256 `114dda0b7ecaada7cb97c598d6f25c0a02d66d86711aac073448afae35384ec0`, for primary-source URLs and access dates.

The repaired parser permits only that additional field, with the source's optional signed-integer type. It still rejects other extra fields, invalid types, duplicate keys, unsolicited server requests and misbound responses. Notifications remain undispatched and their contents are discarded. It records only predefined shape categories if a future envelope is rejected; no raw keys, method names, payloads, timestamp values or stream hashes enter the report.

The original stopped report is retained in its exact local folder and in the repository archive. The canonical entry point remains `scripts/gate0_postlogin_metadata.py`. The new explicit flag `--run-repaired-metadata` starts the corrected operation in `delivery/GATE0_POSTLOGIN_METADATA_016_REPAIR_001`. The old `--run-metadata` flag only reopens the original report. A completed correction report is verified and reused before host inspection or launch; a partial run is preserved and refused. No automatic retry occurs.

The already-passed dummy-file prerequisite is reused, bound to the accepted original report hash, unchanged boundary/planner source, and the currently verified namespace executable. This is explicitly reuse of a prior observation, not a fresh kernel attestation or full reviewer certification. There is no reason to ask the human to repeat the passed sign-in or dummy-file test to repair a protocol-only defect.

## Existing authorization

The human approved scope SHA-256 `fbd7ca325593c9c8de5573417faf1381dbf669b80218f85e4a31ae519beacc61` in commit `6cae5d3c8f1ac3ed2745415924eb478ee53e5951`. The exact answer is archived at `state/escalations/2026-09-08_POSTLOGIN_REFRESH_APPROVED.md`, SHA-256 `73d96a954fa9f13d5d286f2153b46326577904412450996857c6e175af24214a`.

The scope file is unchanged. This is a human-invoked correction of that failed operation. It does not widen the external credential-file grant, native network access, protocol requests, time/output limits, or model/spending permissions. The separate correction directory is an ordinary contained artifact location used to preserve the original completed failure. There is no new permission request. The controller checks the existing answer, including its original exact scope, and refuses to ignore any nonempty new escalation. An archived grant cannot override a later human restriction.

The live result is still unobserved. Quota, model entitlement, cloud-policy closure and the complete separate-reviewer boundary remain unresolved. No model or scientific verdict is produced by this repair. The next scientific objective remains independent review of the frozen novelty/residual audit, then deciding whether a mechanism warrants an experiment or whether description/predicate acquisition needs a new ideation pass.

## Validation

The final parser and controller hashes match the tested bytes. Targeted protocol and controller suites passed; command/output records, the prior parser copy and per-source hashes are preserved in `artifacts/GATE0_NOTIFICATION_REPAIR_ENGINEERING/20260908_001/MANIFEST.json`, SHA-256 `3757614b8daa856fd449e87545ff5064f7be1d14f0495dd0d4528769c822540a`. The controller suite checks that the old flag cannot launch a repair, archive approval cannot ignore a new restriction, prior receipt/pins must match, completed reports are reused, and partial attempts are preserved. These are engineering checks in a shared workspace, not an independent scientific verdict.
