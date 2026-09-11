# Checkpoint038 source packet and continuation

Prepared 2026-09-11. This step makes the newly supplied primary methods available
in a durable local reading packet and returns a public integrity receipt. The
scientific progress in this checkpoint is the accompanying method-level source
integration. Source staging does not itself evaluate a candidate.

## Private ZIP layout and command

The extracted ZIP has this layout:

| Path | Purpose |
|---|---|
| `stage_source_packet038.py` | Human-run staging and receipt publication helper |
| `RELEASE.json` | Exact public content commit, input-manifest path and digest |
| `private_papers/70e60317cc1e7815118aac54b00d3aadf5558f7bc219ca2d3b6e3396c2611086.pdf` | User-supplied Chvátal paper, original bytes |
| `private_papers/873998cb1f647756e12f061f5c9152c2bae9fa3b37b0efa45432aa4b7e9df570.pdf` | User-supplied Pierce–Kuipers paper, original bytes |

Public documents may also be included for convenience. The helper uses their
verified Git objects at the release's content commit as its source of record.
Keep the extracted private ZIP outside the tracked checkout or inside its
ignored `delivery` directory. From the extracted ZIP directory, run in WSL:

```bash
python3 stage_source_packet038.py --lab "$HOME/ARC_Independent_Lab" --bundle .
```

The command checks the existing `main` branch and exact approved GitHub origin,
refuses unrelated tracked edits or staged changes, fetches `main`, and permits
only a fast-forward sync. An already prepared, exact source-receipt commit may
be retried after a failed push. Other unpublished commits are preserved and stop
publication rather than being silently included.

The helper reads the public input manifest and each declared public source from
the pinned published commit. It checks that the content commit is in the remote
and local histories. It verifies both original PDF hashes and proves the private
destination is ignored and untracked before copying. Copies go only to
`delivery/P3_SOURCE_PACKET_038`, retaining their exact source bytes. Existing
equal files are reused; changed files, unexpected entries and links stop the
operation and are preserved.

The only new Git-tracked output is this two-file receipt:

```text
artifacts/P3_SOURCE_PACKET_038/<public-manifest-sha256>/RECEIPT.json
artifacts/P3_SOURCE_PACKET_038/<public-manifest-sha256>/SHA256SUMS
```

The receipt inventories the verified private and public input bytes without
publishing paper content. Its claim is source integrity and local staging, not
review completion or a scientific verdict. Publication succeeds only after the
remote ref is checked. A failed push preserves the local commit; repeating the
same command retries publication after verifying the existing source packet.
Once the command reports that GitHub is updated, the PI can read the receipt
directly. No report attachment is needed.

## Why this does not invoke the completed032 controller

The inspected repository base was
`be9bcf12d0a147a06e30f05877189313fdbf9c2a`, accessed 2026-09-11.
The actual032 independent review completed at a cumulative 14 native starts and
11 explicitly sent turns. Its finite scope is exhausted. Standing user approval
continues to govern the programme; this fact does not change the identity or
limits of a completed execution scope.

The existing controller is also tied to a different scientific task:

| Existing source | Concrete restriction |
|---|---|
| `scripts/p3_finite_review_032.py` and `configs/P3_FINITE_REVIEW_SCOPE_032.json` | Exact historical032 identity, 019 private packet digest, inherited original science prompt, runtime pins and historical accounting |
| `scripts/p3_review_broker.py` | Fixed C1–C4, T and observer subjects, original and supplement manifest fields, and a compulsory first-set observer-auditor receipt before a substantive verdict |
| `scripts/p3_finite_review_030.py` packet preflight inherited by032 | Requires the original first-set packet bootstrap documents and fixed auditor closure |
| `scripts/review032_workflow.py` and `scripts/publish_review032_evidence.py` | Fixed032 run directories, controller/approval pins and returned-evidence allowlist |

Changing only a packet name or reusing an old approval file cannot turn these
components into the R1–R7 focused analytical review. The frozen scripts remain
unchanged.

## Next engineering task

Prepare a versioned focused-review adapter with a claim-level R1–R7 output
schema, successor brief, new closed input manifest and source inventory,
separately pinned read-only verifier, fresh context and output-only write
boundary. Adapt the controller, packet preflight, broker schema and output
collector to that exact task while reusing unchanged transport and boundary
components only where their actual source contracts still apply. A new exact
finite scope must retain the cumulative historical accounting, current native
resource admission, fixed model/effort policy and no automatic retry.

The adapter must provide each primary method needed for a literature-dependent
claim through an inventoried lawful reading route. The two PDFs staged here
close the newly identified paper-access gaps; they do not by themselves supply
every other paper used in the programme. Internal mathematical claims can be
reviewed independently of unresolved historical comparisons. This is concrete
implementation work under the standing instruction, not an additional request
for user permission.

No native client, reviewer model, treatment, GPU or HPC job is launched by the
source-staging helper. It issues no verdict and creates no new native allowance.

## Verification performed here

Nine local Git integration tests passed. They substitute a local bare repository
for network transport while exercising actual Git history, indexing, ignore,
commit and source-object operations. The checks cover private-source corruption,
ignored/untracked destinations, symlink refusal, preserving changed packet
bytes, source commit pinning despite a newer checkout, preserving unrelated
work, receipt-only publication, repeated invocation and failed-push recovery.
These tests establish the helper's tested behavior; actual WSL staging is
established only by its returned receipt.

Sources inspected at the pinned base, accessed 2026-09-11:
[032 controller](https://github.com/afazeliUofT/arc-independent-lab/blob/be9bcf12d0a147a06e30f05877189313fdbf9c2a/scripts/p3_finite_review_032.py),
[032 scope](https://github.com/afazeliUofT/arc-independent-lab/blob/be9bcf12d0a147a06e30f05877189313fdbf9c2a/configs/P3_FINITE_REVIEW_SCOPE_032.json),
[original broker](https://github.com/afazeliUofT/arc-independent-lab/blob/be9bcf12d0a147a06e30f05877189313fdbf9c2a/scripts/p3_review_broker.py),
[030 controller](https://github.com/afazeliUofT/arc-independent-lab/blob/be9bcf12d0a147a06e30f05877189313fdbf9c2a/scripts/p3_finite_review_030.py),
[032 wrapper](https://github.com/afazeliUofT/arc-independent-lab/blob/be9bcf12d0a147a06e30f05877189313fdbf9c2a/scripts/review032_workflow.py),
[032 collector](https://github.com/afazeliUofT/arc-independent-lab/blob/be9bcf12d0a147a06e30f05877189313fdbf9c2a/scripts/publish_review032_evidence.py).
