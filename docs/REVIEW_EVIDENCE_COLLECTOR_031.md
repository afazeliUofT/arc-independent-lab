# Evidence collector 031

`publish_review030_evidence.collect(project_root)` accepts the absolute project
directory and returns `archive_relative_path`, `evidence_digest`,
`tracked_paths`, `manifest_sha256`, and `status_summary`. It executes no Git,
native client, model, network, or credential operation. The publication wrapper
must stage only the returned explicit file paths, never an entire directory.

The allowlist consists of the twelve named 030 main/kernel evidence files in
`SOURCE_LIMITS`, plus these three workflow files:

- `delivery/P3_030_RETURN_WORKFLOW/WORKFLOW_REPORT.json`
- `delivery/P3_030_RETURN_WORKFLOW/LAUNCH_RESERVED.json`
- `delivery/P3_030_RETURN_WORKFLOW/LAUNCH_OUTCOME.json`

Write the final workflow report before collection. Do not mutate it afterwards
and claim the published copy represents that later state. `CONSOLE.txt`, raw
client logs, credentials, cache files and private packet files are excluded.

The collector always writes an `INDEX.json` and `MANIFEST.json` when the project
and destination are safe and writable, including when no run/report exists.
Each fixed source is marked `PRESENT`, `MISSING`, or `REFUSED`. Present sources
are preserved byte for byte under `files/<original relative path>`; refused
sources record only a fixed categorical reason. An unsafe/unwritable archive
destination fails without falsely claiming that evidence was saved.

Archives reside at `artifacts/P3_REVIEW_030_RETURN/<SHA-256 of INDEX.json>`.
Equal source bytes/statuses produce the same archive and publication paths.
Existing different archive bytes are preserved and refused; later real evidence
creates a new archive. No execution receipt is synthesized, and a collected
verdict is never classified as scientifically admitted by this collector.

Directory traversal and file access use descriptor-relative no-follow opens,
including every ancestor of the absolute project root. Files must be bounded,
regular, owned by the current user, singly linked and not group/world writable.
Reads require matching before/after metadata and a final fresh named-path
metadata check. These checks detect ordinary replacement/concurrent writes;
they do not provide an atomic snapshot of a running review or protection from
a hostile privileged host. A report missing during collection does not prove
that no model ran.

Validation: `python3 -I -B test_publish_review030_evidence.py` passed 19 tests on
2026-09-10. Tests cover absent and partial reports, failed-run verdict retention,
fixed workflow files, idempotent and evolving evidence, exact bytes/hashes,
allowlist-only reads, symlinks, hardlinks, FIFO, permissions, bounds, source
mutation/replacement, destination refusal and containment. Tests used synthetic
files only and performed no Git mutation, model or native client operation.
