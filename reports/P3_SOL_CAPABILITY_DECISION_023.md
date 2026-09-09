# Sol capability decision and continuation

2026-09-09. PI decision applying the funder's latest authorization. The scientific task remains the independent Phase 3 novelty/residual review.

## Authorization and interpretation

The funder wrote in this conversation:

> I approve chatgpt sol 5.6, but need its highest (most capable) tier. If Ultra or pro are the highest sol 5.6 tiers, use them

This approves Sol subject to a capability requirement. It is not a verbatim approval of a particular hash, and the funder did not explicitly name Max. The PI selects **gpt-5.6-sol, explicit max effort** as the highest directly selectable individual reasoning effort supported by the measured, isolated native route. This applies the new instruction together with the continuing requirements for enforced reviewer isolation, existing subscription access and no additional spending. It does not establish that Max is the strongest Sol configuration on every product surface.

The approval record in state/ESCALATION.md is a disclosed PI transcription and implementation of that instruction. The human publication command commits that concrete record; no additional permission decision is requested. The unchanged reviewer controller still requires the exact scoped ANSWER and an explicit human launch. It does not accept the old Astra approval, infer a fallback, or run as part of publication.

## Why this setting

| Setting | Evidence | Decision for this review |
|---|---|---|
| Max | Highest direct individual reasoning effort advertised for exact Sol in the supplied native catalog. | Request explicitly, and reject a changed model or effort. |
| Ultra | A local delegation mode whose backend effort is mapped to a supported non-Ultra value. A metadata override takes precedence over Max. Delegation requires the effective V2 runtime, which the approved reviewer disables. | Do not claim that enabling the label would deliver additional isolated reasoning. Preserve the established tool boundary. |
| Pro reasoning mode | The API documents a separate mode, independent of effort. The pinned native client's outgoing Reasoning type has no mode field. | Do not claim Pro is selected, invent a configuration field, or switch to a paid API. |

OpenAI describes Max as additional reasoning on a task and Ultra as delegation. Its API documentation separately describes Pro execution with greater model work. These are different controls; a ChatGPT Pro account is not proof that a request used Pro reasoning. Sources accessed 2026-09-09: [Codex model settings](https://learn.chatgpt.com/docs/models), [API reasoning modes](https://developers.openai.com/api/docs/guides/reasoning#reasoning-mode).

The decisive implementation evidence is the exact installed-client source: [Reasoning serialization](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/codex-api/src/common.rs), [request construction](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/core/src/client.rs), and [delegation policy](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/core/src/session/multi_agents.rs), accessed 2026-09-09. The source consultation and hashes are archived in artifacts/P3_SOL_MODE_SOURCE/20260909_001/MANIFEST.json, SHA-256 `c723803c24b84a9317b722e4b3b4fb03760f3ad7fa080f60397cf51964ce8552`. The two newly fetched source files were independently rehashed by the PI, including Git blob identities. The consultation is engineering assistance in the same workspace, not the scientific reviewer.

Precision correction: the short progress update said Ultra maps to Max. More exactly, a supported metadata override can select another non-Ultra effort before the Max default. The retained safe catalog does not expose that override. Explicit Max avoids that ambiguity.

## Concrete operation

The prepared scope and reviewer implementation are unchanged:

- configs/P3_FINITE_REVIEW_SCOPE_022.json — SHA-256 `46301a69ae7a2d0cdac537eb2127415e8d4ac3c4ab5d7e8ea00ff1a1894a9f0f`.
- scripts/p3_finite_review_022.py — SHA-256 `ef9b1bb0b19e3d8687aac88d70f268183f00c435c789420e47996211ea09e116`.

The scope allows the synthetic admission stage and then a separate fresh scientific reviewer, at most two native processes and two explicit model turns, with respective deadlines of 600 and 3600 seconds including cleanup. Existing subscription only; no automatic retry. Complete receipts are reused; partial or altered attempts are preserved and stop. These limits come from the scope file and hash above.

No native or model operation was performed for this decision. Actual Sol access and a successful independent review remain unobserved. REPORT(10), preserved at artifacts/P3_FINITE_REVIEW_MODEL_OBSERVATIONS/20260909_001/REPORT.json, SHA-256 `d024d5b1ec85cce7ec61f36e7f5594efe0b37d7e2eb6db7ca6d4b2094115631c`, explains the missing verdict: catalog admission stopped before any model turn. The earlier three starts consumed zero explicit model turns; the chain is checked by the unchanged controller above. Hosted ChatGPT allowance remains unknown, so unattended continuation remains disabled.

Checkpoint023 carries the unpublished checkpoint022 content plus this decision and its approval record. The delivered checkpoint022 ZIP remains unchanged. Publication is separate from reviewer execution, so retrying a Git push does not repeat model work.

## Return to the research objective

The objective is to explain failures of interactive knowledge acquisition, retention through discontinuities and novel recombination, and only then identify useful repairs. Diagnosis and novelty-free ideation were approved. The multidisciplinary and historical study is complete within its recorded scope, not an exhaustive systematic review. The PI's candidate audit is prepared; independent dispositions, final mechanism selection and the experimental programme are unfinished. There are no mechanism efficacy results.

The next scientific action is the independent audit of the frozen candidates, their joint claim and the observer diagnostic. If the negative reductions survive review, return explicitly to novelty-free invention around acquisition of useful descriptions, predicates and models that the present constructions assume supplied. Do not turn operational setup into evidence for a mechanism or call the proposal finalized before this review.
