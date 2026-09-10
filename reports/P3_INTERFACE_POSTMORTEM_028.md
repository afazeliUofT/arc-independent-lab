# Why the reviewer handoffs kept failing

Prepared 2026-09-10. This is the PI's engineering diagnosis, not an independent scientific verdict.

The latest report is the requested evidence. It records a successful native synthetic read and real access refusal, followed by a fresh scientific session that stopped on its first broker request. The user followed the handoff correctly. The immediate underlying exception and arguments were discarded by our error handler, so the exact trigger is unknown. It would be wrong to claim that a particular requested read length caused this actual stop.

The source report is `artifacts/P3_SCIENTIFIC_BROKER_STOP_OBSERVATIONS/20260910_028/REPORT.json`, SHA-256 `6460fffe52e02b5388d871c328d3d7d72885d7222b086d664786b4a822084769`. Its review and provenance checks are recorded in `evidence/P3_FINITE_REVIEW_027_OBSERVATION_REVIEW.json`. Actual laptop SESSION files remain required at the next launch; the embedded copies do not authorize reconstructing them.

## The demonstrated design defect

The advertised tool schemas and the interface actually presented to the model diverge. At the pinned native Codex source commit, the dynamic-tool converter passes schemas through a Rust structure that omits numeric bounds, string lengths and patterns, and list lengths. Our original descriptions did not state those lost constraints. For example, an integer `read_text.length` of 200000 satisfies the projected schema, whereas our broker permits at most 100000 characters. The source-derived Python projection drops 36 constraint occurrences. This is source analysis and an offline reproduction, not execution of that Rust converter. Sources accessed 2026-09-10: [dynamic-tool conversion](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/tools/src/dynamic_tool.rs), [schema representation and parser](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/tools/src/json_schema.rs), [Responses conversion](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/tools/src/responses_api.rs).

The problem is compounded by two decisions in our code. First, ordinary argument mistakes permanently stop the broker instead of allowing the reviewer to correct them. Second, the outer protocol replaces the useful exception with a generic message before any receipt is recorded. Thus a recoverable input mistake can consume a model turn and require another human handoff without leaving enough evidence to diagnose it.

The complete source audit, exact source identities and local reproduction are under `artifacts/P3_INTERFACE_CONTRACT_SOURCE/20260910_028/`. Its `REPORT.json` has SHA-256 `c2848209ed39cd9f98226b5fe56b61621c0741709d4db1094ce6d7f424e90c4e`. Twenty offline cases exercise every original tool: all five valid controls pass, fourteen input/precondition cases become generic fatal stops, and one otherwise valid large verdict exceeds the outer protocol's request byte ceiling. These fixtures contain no model-authored scientific verdict. The unchanged historical arithmetic auditor is exercised on frozen inputs.

## Why the previous tests were insufficient

The native canary specifies already-valid arguments for one read, then an intended path denial. It proves those two operations; it does not prove the usability of five tools after native schema conversion. Earlier local checks also used predetermined valid calls or stubs. They tested broker rejection but did not test whether the model could see and satisfy the broker's full contract or recover from an ordinary mistake.

Earlier checkpoints also encountered different integration failures before reaching this layer. Passing one layer did not establish the next. Treating each stop as a separate narrow patch created a sequence of human-mediated discoveries. The engineering and the test coverage were my responsibility. The repeated delay is not a research result, and it does not establish that the candidate mechanisms are good or bad.

## The concrete correction and its limits

Checkpoint 028 prepares a separate interface adapter and transport/session implementation. The original broker, protocol, auditor, scientific prompts and frozen scientific evidence remain unchanged. Activation requires an explicit control/budget amendment.

The adapter carries constraints and examples in descriptions that survive the pinned native conversion. It validates ordinary input errors before invoking the original broker, returns a fixed actionable unsuccessful tool result, and permits at most eight such corrections per session. Every request still consumes the existing call and time budgets; a ninth ordinary error ends the session. There is no model restart or counter reset. Resource/path authority, evidence hashes, output integrity, foreign threads and replay checks remain terminal. The adapter does not supply or rewrite scientific content.

The new transport records a fixed failure layer, known tool name and categorical reason without exposing raw requests, unknown exception text, credentials or paper contents. Actual server requests are reported as requests rather than malformed notifications. This makes a future unexpected failure inspectable from the same report; it cannot recover the cause discarded in 027.

Local tests cover all five tools, the original fixed auditor, paginated text and page-image transport, structured verdict submission/readback, correction after ordinary errors, and terminal boundary failures. The actual installed private packet is not available in this hosted working copy. A deterministic packet preflight therefore runs on the laptop before any model starts. A fresh native synthetic challenge must demonstrate oversized-read feedback, corrected read, and the original real path refusal before a separately fresh scientific reviewer is admitted.

The actual cumulative allowance is exhausted at eight native starts and five sent turns. The proposed operation adds at most two starts and two turns, to ceilings of ten and seven: one synthetic session and only on success one scientific session. The stage deadlines remain ten and sixty minutes including cleanup. Publication cannot start a model; launch is a separate explicit human command. No spending, authentication change, new tool authority or unattended continuation is proposed.

This is a bounded attempt to close a demonstrated interface defect, not a promise of a verdict. If it fails, preserve the structured evidence and reassess the route before any new native request. Do not return to an indefinite sequence of model-funded diagnostic probes. A substantive reviewer may also legitimately report a missing dependency or reject the candidates.

## The research objective remains the deciding criterion

We are studying the causes of failures in acquiring knowledge through interaction, retaining it through discontinuity, and recombining it in unseen situations. The diagnosis and novelty-free ideas were approved. The multidisciplinary survey is complete within its recorded scope; it is not an exhaustive systematic review. PI novelty and residual audits exist, but the independent dispositions, final mechanism selection and `PROGRAMME.md` remain unfinished. There is no candidate efficacy finding.

Once the independent review is available, use it to decide whether any residual deserves an experimental programme. If the reviewed reductions eliminate the current candidates, explicitly return to novelty-free invention about how an agent acquires the descriptions, predicates or models that those candidates assume supplied. Do not turn transport debugging into the scientific objective or declare a preferred mechanism merely to end the delay.
