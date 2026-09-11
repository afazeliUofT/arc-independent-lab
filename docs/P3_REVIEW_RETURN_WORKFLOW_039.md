# Checkpoint039 attended execution and automatic evidence return

Date: 2026-09-11. This is an engineering handoff for the new focused analytical review. It is not a returned review verdict, an efficacy experiment, or additional permission to reuse the exhausted032 scope.

The single delivered ZIP is run through its WSL Downloads launcher. The launcher calls:

```bash
python3 scripts/review039_workflow.py --lab "$HOME/ARC_Independent_Lab" --bundle <verified-extracted-bundle>
```

The launcher resolves the bundle path; the human does not replace that placeholder. The workflow verifies the canonical repository, clean tracked `main`, the release commit, the public manifest and the exact runtime bytes. It fetches only the canonical main branch and fast-forwards the checkout. It preserves unrelated work and commits. Failed publication may be retried when the staged archive or single unpublished commit exactly matches the returned evidence inventory.

The bundle contract is `RELEASE.json` plus `scripts/` and `packet/`. `RELEASE.json` has kind `P3_FOCUSED_REVIEW_039_RELEASE_v1`, repository `afazeliUofT/arc-independent-lab`, a 40-character `content_commit`, `manifest_path` equal to `evidence/P3_FOCUSED_REVIEW_MANIFEST_039.json`, and that manifest's SHA-256. The manifest declares public `inputs` and private `bundle_files`, each as `{path, sha256}`. Every private bundle path starts with `packet/`.

The private packet is installed at `delivery/P3_FOCUSED_REVIEW_PACKET_039`. Before copying, the workflow checks that this destination and both039 runtime directories are ignored and untracked. It preserves and refuses changed or unexpected packet files. Private papers, extracted source text, rendered pages and native streams are never part of the publication allowlist.

The workflow invokes `scripts/p3_focused_review_039.py --run-attended-review --packet <fixed-private-packet-directory>` once. An exclusive reservation is written and synchronized to storage before invocation. A nonblocking process lock also prevents concurrent wrapper calls. Any existing039 reservation, controller attempt, or prior workflow stop report makes a later call collect and publish only. A killed process or missing report does not authorize another launch. The new controller retains its own independent reservation and finite native-start/turn limits.

Only the bounded subprocess transport and filesystem/Git primitives are reused from032/038. The old032 workflow and old038 source-staging operation are not invoked. The new wrapper's ceiling is two starts and two turns, governed by the new039 scope; actual usage must be read from returned controller and native receipts. The wrapper allows 4,310 seconds before requesting controller cleanup, followed by the unchanged bounded interrupt/termination grace. It does not infer native-child cleanup from parent-process termination.

The collector admits exactly these source artifacts when present and ordinary:

| Directory | Allowed files |
|---|---|
| `delivery/P3_FOCUSED_REVIEW_039` | `REPORT.json`, `REPORT.sha256`, `ATTEMPT.json`, `AUTHORIZATION.md`, `synthetic_SESSION.json`, `synthetic_STAGE.json`, `science_SESSION.json`, `science_STAGE.json`, `science_output/REVIEW_VERDICT.json` |
| `delivery/P3_039_RETURN_WORKFLOW` | `WORKFLOW_REPORT.json`, `LAUNCH_RESERVED.json`, `LAUNCH_OUTCOME.json` |

The main report and each session/stage file have a 16 MiB limit, matching the existing receipt boundary. The scientific verdict has a 1 MiB limit. JSON files must contain valid objects. Linked, unstable, oversized or malformed files are recorded as refused and preserved locally. Missing receipts are recorded as missing. A partial collection is useful evidence and is published even if the controller never produced its final report or verdict.

The collector also checks verdict prose for an exact normalized passage of at least 200 contiguous words copied from either supplied private full text. A detected bulk copy leaves the original verdict private and returns a categorical refusal in the index. This narrow check does not certify shorter quotations, semantic copying, copyright status, or scientific accuracy. If a private text is unavailable, the screen is explicitly marked incomplete; it is not reported as a pass.

The public return is a content-addressed directory under `artifacts/P3_REVIEW_039_RETURN/<index-sha256>/`, containing an exact `INDEX.json`, `MANIFEST.json`, and admitted source artifacts under `files/`. The Git index is populated only with those exact bytes, bypassing text filters. The workflow checks committed contents before pushing and verifies the remote main reference afterward. It prints the exact GitHub archive URL. The PI must subsequently assess actual usage, source-delivery receipts, execution boundaries, the seven claim assessments and two source comparisons, and the scoped verdict.

The reusable offline tests use real temporary Git repositories with only network transport replaced by a local bare repository. They exercise a fake controller, never a native model. Test evidence is recorded in `evidence/P3_WORKFLOW_VALIDATION_039.json`.
