# Missing 030 main report: derived engineering findings

Access date: 2026-09-10. This is a read-only forensic analysis of original published receipts and unchanged code. It is not a replacement execution receipt, an independent scientific review, or permission for another native/model operation.

The main report is absent because the shipped session producer and the final report collector disagree on the receipt kind. The producer emits `P3_FINITE_REVIEWER_SESSION_030_OFFLINE_PROPOSAL_v1`; the consumer requires `P3_FINITE_REVIEWER_SESSION_030_v1`. Both actual returned SESSION files carry the producer's value. The word `OFFLINE_PROPOSAL` is an incorrect shipped label; the actual flags in both receipts record a client start and a sent model turn. Those observations must not be relabelled or treated as unconsumed allowance.

`reproduce_collect_sessions_failure.py` imported the unchanged controller, passed its frozen bundle checks, and called its unchanged `collect_sessions` on exact copies of the returned receipts. The combined set, synthetic-only set and science-only set each raised `Stop: SESSION kind or actual execution counters differ`. Both original separate SESSION/STAGE byte-linkage checks passed. All original receipt and source hashes were unchanged afterward. No process, model, Git commit or push was invoked; no main `REPORT.json` or verdict was reconstructed.

Source inspection establishes why this local validation error loses the final report: the main execution try/except ends at line 788; `collect_sessions` is called outside it at line 815; the final report write occurs later at line 822. Thus the mismatch deterministically prevents that write on these exact returned receipts. The original console traceback was not returned, so this proof reproduces the failure and establishes the reachable code path rather than claiming possession of that historical traceback. This reporting error is separate from the scientific session's original broker/packet failure.

The original emitted receipt flags establish two additional native starts and two additional explicit sent turns. With the unchanged controller's recorded prior counts of 10 starts and 7 turns, the derived cumulative observation is **12 starts and 9 turns**, exactly the approved ceiling. Both native processes are recorded as reaped. Both receipts state `verdict_submitted: false`. Synthetic elapsed time is 15.571611 seconds; science elapsed time is 649.667418 seconds. These are earlier execution durations, not the duration of the subsequent collect-only publication.

## Why the previous tests missed it

The recorded 030 validation contains 108 passing tests: cache 25, lifecycle/session 26, stage evidence 12, controller 45. Passing that set did not establish the producer-consumer contract. The controller fixtures replace the real `run_stage` and manufacture their session observations with `kind: controller.SESSION_KIND` at line 119. They therefore derive the expected field from the consumer under test instead of consuming the real session emitter's output. Session transport tests exercise the emitter but do not feed its returned receipt to the unchanged final collector. The exact-bundle test verifies file hashes, not agreement between two source constants. This was an integration-test omission, despite substantial unit/fault coverage.

The 031 validation contains 57 passing tests: evidence collector 19, workflow 19, publication 19. Its task was to preserve and publish original files, including absent reports, without rerunning existing attempts. Workflow tests use a synthetic runner or simple Python transport child; collection tests deliberately preserve opaque original JSON and mark verdict execution admission `NOT_EVALUATED_BY_COLLECTOR`. They did not test or change the underlying 030 session/report contract. In this return, publishing the independently saved SESSION/STAGE files succeeded and exposed the original defect.

## Minimal future correction

1. Give a future receipt schema a single owned kind constant used by both its producer and consumer. Preserve original 030 files and source bytes. An offline historical adapter may understand this exact known shipped kind with pinned provenance; it must describe its output as derived analysis and must not rewrite the original kind or fabricate the missing main report.
2. Add a test that runs the real future `run_session` with a fixed synthetic Python protocol transport and supplies the returned bytes directly to the real future `collect_sessions`. No mocked session-kind field should be inserted. Exercise both synthetic and scientific labels, including a failed scientific outcome; no model or native client is needed for this contract check.
3. Guard final receipt aggregation independently. If schema/linkage/accounting collection fails, preserve that categorical error and the hashes of already saved original receipts in a distinct failure record. Never silently claim successful admission or release reserved capacity. A negative test should make aggregation fail after SESSION/STAGE persistence and verify that some final controller failure evidence remains publishable.

Fixing only this receipt mismatch would make the missing report explainable and publishable; it would not resolve the scientific broker/packet failure and does not justify another trial by itself.

## Evidence

- Derived proof: `DERIVED_FORENSIC_PROOF.json`, SHA-256 `06568763624e41466fd45e534d3dcd57013f5fc18e1e20e4fee090f6515a0f28`.
- Original synthetic SESSION: `2df312ff31a243ce548d2a0065665166097e0e335fbe6967f146f117e91709c6`.
- Original science SESSION: `1059b733db491fc9e5aee64113784cb95620bab487f76346f91ec243000f0da9`.
- Original synthetic STAGE: `31e607a40347176376604d97479997aee1a461e612ba60573aa33266574d6efc`.
- Original science STAGE: `0911d75d736e9286d6b7600588051fa471c4f610ed24236253539155bc3490b7`.
- Recorded 030 validation: `artifacts/P3_REDESIGN_VALIDATION/20260910_030_001/REPORT.json`, SHA-256 `f4599a5710ba975875e7e51e3dc5ad5aaa37b39b3ce6d215d405761e3df047f7`.
- Recorded 031 validation: `artifacts/P3_RETURN_WORKFLOW_VALIDATION/20260910_031/REPORT.json`, SHA-256 `91b55ba6ac5e4087b6d3bb73e61361a1162827e779fae4f44794d0cf3a03cdf2`.

Published source URLs, accessed 2026-09-10:

- [Original controller](https://github.com/afazeliUofT/arc-independent-lab/blob/39eae612ddb72a97979f001cd7f2385df8420bd1/scripts/p3_finite_review_030.py)
- [Original session emitter](https://github.com/afazeliUofT/arc-independent-lab/blob/39eae612ddb72a97979f001cd7f2385df8420bd1/scripts/p3_reviewer_session_030.py)
- [Controller fixtures](https://github.com/afazeliUofT/arc-independent-lab/blob/39eae612ddb72a97979f001cd7f2385df8420bd1/tests/test_p3_finite_review_030.py)
- [Return workflow tests](https://github.com/afazeliUofT/arc-independent-lab/blob/39eae612ddb72a97979f001cd7f2385df8420bd1/tests/test_review030_workflow.py)
- [Evidence collector tests](https://github.com/afazeliUofT/arc-independent-lab/blob/39eae612ddb72a97979f001cd7f2385df8420bd1/tests/test_publish_review030_evidence.py)
