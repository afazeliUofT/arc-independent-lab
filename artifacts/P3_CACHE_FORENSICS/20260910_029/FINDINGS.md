# Checkpoint 028 cache postcheck: passive forensic findings

Date: 2026-09-10. This is an engineering consultation in the shared workspace. No native client or model was started, no host cache was inspected here, and no credential content was read. The attached report and already archived public source are the evidence.

## What the report establishes

Both stages began with the same recorded cache state: `cloud-config-bundle-cache.json` absent; `models_cache.json` present, device 2096, inode 686455, 179710 bytes, mode 0644, mtime/ctime 1789009937930214443. That timestamp is 2026-09-10T03:12:17.930214Z.

The 13.96-second synthetic stage passed its host metadata comparisons. The 434.41-second scientific session stopped with `Unadvertised native item effect`. After the session returned, the controller obtained `cache_metadata_unchanged: false`, then raised `Scientific stage changed protected host inputs`. This final text attributes change to the stage more strongly than the check supports. The report retains the earlier session reason inside the scientific observation, so it is recoverable despite the outer summary masking it.

The inherited `host_checks` implementation compares **host path metadata**, not content, across two cache paths. It saves no post-run cache metadata and uses short-circuiting `all()`. Consequently, the false result means at least one comparison failed. It does not identify the path, field, content change, writer, or time of change. A newly created cloud-cache path alone would make the aggregate false without evaluating the model-cache comparison. A model-cache permission or timestamp change alone also suffices. `atime` is not compared; normal read-induced atime changes are not an explanation for this predicate.

The scientific input packet still passed its after-read verification in the report; cache provenance is a separate issue from packet file integrity. The cache predicate must not be silently waived to admit a result.

Code references: `scripts/p3_finite_review_024.py` function `host_checks`, inherited by 027 and 028; `scripts/gate0_postlogin_metadata.py` functions `metadata` and `inventory`; `scripts/p3_finite_review_028.py` `run_stage` and the subsequent scientific host-check assertion. Exact local source hashes are in the sibling `REPORT.json`.

## What the read-only bind does and does not establish

The recorded argv gives the present model-cache file a same-path `--ro-bind`, starts from an empty root, provides no broad host home or Codex-home mount, remounts the namespace root read-only, and drops capabilities. The cloud-cache file was absent and is not bound. This describes a restrictive mount plan; the stage explicitly does not claim a fresh kernel mount attestation.

A read-only bind restricts writes **through that mount**. It does not make the underlying file globally immutable. Another process with a writable host mount can change the same underlying file. The Linux mount documentation explicitly states that setting a bind mount read-only does not affect other mounts of that filesystem. Therefore a host-path metadata change is not, by itself, evidence that the reviewer escaped or wrote through its read-only mount. Conversely, a read-only bind alone cannot prove that the reviewer saw immutable input bytes throughout the session. [Linux mount documentation](https://man7.org/linux/man-pages/man2/mount.2.html), accessed 2026-09-10.

It would be incorrect to claim that this cache is an immutable old-inode snapshot because a concurrent client necessarily uses atomic replacement. The pinned Codex `save_file` calls `tokio::fs::write(cache_path, json)`, which replaces the contents of the existing file; it does not implement temporary-file-plus-rename replacement. A concurrent host write can therefore modify the file visible through the read-only bind. The actual writer and operation in this run remain unknown. [Pinned Codex cache source](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/models-manager/src/cache.rs), [Tokio write documentation](https://docs.rs/tokio/latest/tokio/fs/fn.write.html), accessed 2026-09-10.

The model manager defaults to a 300-second cache TTL. An equal-ETag refresh can update `fetched_at` and save the file once sufficiently old; ordinary online refresh can save a new catalog. These source facts make host-client cache maintenance plausible, but elapsed session time exceeding 300 seconds is not evidence that such maintenance caused this failure. The TTL is a freshness policy, not proof of a periodic timer or of a particular process running. [Pinned manager source](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/models-manager/src/manager.rs), [pinned cache source](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/models-manager/src/cache.rs), accessed 2026-09-10.

## Bounded passive follow-up, if useful

A human-run metadata-only check can inspect **only** the two named cache paths, validating path components without following symlinks and taking `lstat` metadata. It can compare presence, device, inode, size, mode, mtime and ctime against the saved before state, and report the current observation time and differing field names. It must not open, hash or print cache contents, inspect `auth.json`, list the home directory, enumerate processes, launch Codex, or change any file.

This would identify which path differs **now** and whether the current inode is different. It cannot recover the missing end-of-stage state, establish a writer retrospectively, prove that a past same-inode write did not occur, or certify what the reviewer actually read. If that modest information would not affect the next decision, omit the probe rather than burden the user.

For future instrumentation, save per-path before/after metadata and all failed field comparisons. Preserve native session stop and postcheck failures separately instead of letting a later aggregate failure replace the earlier reason. Neither change supplies a scientific verdict or retroactively repairs this run.

If a future native operation is proposed, the protected-input design needs an explicit decision: a verified exact-byte immutable input snapshot, or another enforceable provenance mechanism, rather than assuming read-only binds provide snapshot isolation. Such a design must preserve authentic configuration/model-policy bytes, original lookup paths and native validation; it must never copy credentials, fabricate metadata, weaken managed policy, or treat a changed cache as automatically benign. This report proposes no new execution or access authorization.

## Operational disposition

Actual cumulative starts/turns are 10/7, exhausting the approved ceiling. Do not retry 028. Retain the report, both original SESSION files, packet and runtime evidence. There is no independent scientific verdict to admit. The separate native-item failure must also be explained before considering whether any new run is justified.
