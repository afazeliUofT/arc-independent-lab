# Checkpoint005: Phase1 submission

Prepared 2026-09-06 from verified human commit `980b99cbaa90096679eec35c230f3069a255357d` in [arc-independent-lab](https://github.com/afazeliUofT/arc-independent-lab), accessed 2026-09-06. This checkpoint contains the Phase1 diagnosis submitted for review, Jones main-article audit, batch002 resolution, checkpoint004 verification and continuation records. Publishing it is not scientific approval.

The helper `scripts/checkpoint005_handoff.py` conservatively adapts the previously used checkpoint004 helper with only description, base, checkpoint identity and backup path changes. Old helpers and manifests are unchanged. Default mode inspects the hashed ZIP and known local file transitions; `--apply` backs up replaced bytes and the index, installs and stages explicit payload files; `--verify` checks the complete index or exact direct-child commit. It performs no fetch, commit, push or authentication.

The human commits and pushes with normal visible Git authentication. The push uses one complete explicit-SHA refspec on one physical line. A failed push leaves the verified local commit available for retry; do not create duplicate commits or rewrite history.

`state/CHECKPOINT_005.json` inventories the complete intended public tree except its own hash. The ZIP transition manifest pins the manifest's bytes. Download instructions outside the archive pin the final ZIP hash, avoiding self-reference. Original scientific run artifacts, previously published evidence and opaque parked-ideas bytes are preserved. Copyrighted PDFs, extracted text, images, private reading files and local verification clones are excluded.

The final actual archive is applied in a contained clone of the exact base with `core.autocrlf=input`; its staged blobs and modes are compared with the complete manifest before delivery. This verifies transport bytes, not scientific correctness or independent review. The assistant does not commit or push the real project. Actual public readback remains necessary after the human push.

All project deliverables use the existing GitHub bridge for durability. The prior runtime backup-upload failure remains documented; no credential is requested or read and no repeat of the failed upload path is required for this handoff.
