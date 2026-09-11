# Checkpoint039: adversarial arguments before requesting a verdict

Date: 2026-09-11 UTC. This is PI preparation under autonomy requirement C5, not an independent scientific verdict. The current task is the seven propositions in `docs/P3_FOCUSED_REVIEW_BRIEF_038.md`. No candidate result is inferred from engineering tests.

## 1. A nominally fresh review could silently certify the wrong science

The previous transport successfully handled the first candidate audit. Reusing its first-audit verdict schema, supplying only supplements without their frozen premises, or mistaking synthetic success for scientific acceptance could turn a technically successful run into a false second-audit certificate. This is the strongest threat to this particular proposed step: it invalidates the inference even if the runtime behaves perfectly.

Test before release: the039 broker uses a separate scope and requires exactly R1-R7, explicit premises, evidence hashes, the CHV79/R1 and PK97/R6 source comparisons, and a bounded recommendation. It denies observer/arbitrary execution tools. Wrong evidence digests and mutated packets terminate the boundary; synthetic mode cannot submit a scientific verdict. Missing text ranges or required images cannot be converted into complete source delivery by hashing them. These cases are exercised by `tests/test_p3_focused_review_broker_039.py`. The native canary witness and distinct stage admission are exercised by `tests/test_p3_focused_review_039.py`.

Result: offline checks passed; the actual private packet passed integrity and complete required source-delivery calls, as recorded in `evidence/P3_FOCUSED_BROKER_REAL_PACKET_VALIDATION_039.json`. These tests verify enforcement and wiring, not the truth of a forthcoming review. The scientific prompt explicitly asks the reviewer to challenge PI supplements, distinguish conditional constructions from reachable histories, and refrain from global priority or efficacy claims. A real second verdict is still absent.

## 2. Full files can be present while decisive evidence is effectively missing

OCR/text extraction can obscure mathematical subscripts or a retention procedure. A large packet can also exceed effective context or time capacity even when its bytes are available. Therefore the packet includes the exact original PDFs, indexed text for every page, and readable page images. Required image delivery covers Chvatal's mathematical argument and the relevant Pierce-Kuipers methods and later discussion. Full text and all forty public research texts must actually be returned before a substantive disposition.

The broker records delivery rather than asserting comprehension. The unchanged native lifecycle may compact context; the prompt requires reopening decisive evidence as necessary. One hour is a finite resource envelope, not an estimate that the review must finish. A capacity or source dependency stop is an honest outcome. The packet's measured hashes and file inventory are in `evidence/P3_FOCUSED_REVIEW_MANIFEST_039.json`; source-delivery validation is separate from any scientific verdict. Further papers are unnecessary for the bounded two-source assessment, but a reviewer may identify a concrete additional dependency.

## 3. Failure recovery could conceal consumption or repeat an expensive attempt

A killed process, absent main report, or failed push could make a helper start the review twice or report zero consumption without evidence. The outer workflow writes an exclusive reservation before invoking the controller. Any later invocation with a reservation, controller directory, or previous stop report collects evidence and retries publication only. Missing session receipts imply lower-bound observations and unknown reserved consumption; they do not restore budget.

Local Git fixture tests in `tests/test_review039_workflow.py` cover failed commits, failed pushes, stopped controllers, prior reservations, and repeated commands. Controller fixtures exercise sent-turn accounting without a verdict and suppression of science after canary failure. Collection refuses source PDFs/raw streams and preserves original output bytes. A launcher defect that blocked exact staged-evidence recovery was found and corrected before release. These fixtures use no native client or model.

## Scientific decision that remains

The review must decide whether the PI's bounded second-audit propositions survive explicit defenses and counterhistories, and identify a justified next research decision. In particular, finite fresh credit is not total learning failure; a count-fitting example is not a demonstrated reachable whole-loop confound; a greedy selection identity is not a whole learner equivalence; and endpoint distinguishability is not yet useful knowledge for future action. No experimental programme, tuning, multi-block semantics, or broad novelty verdict is authorized by a successful technical run.

The synthetic/scientific deadlines, error limits, and byte ceilings are operational controls. They are not preregistered candidate success thresholds. Hosted engineering consultants share PI context and are not the independent reviewer.
