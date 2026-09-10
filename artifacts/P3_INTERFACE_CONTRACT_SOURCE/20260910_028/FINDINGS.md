# Broker contract audit, 10 September 2026

This is an engineering audit by a shared-workspace agent, not an independent scientific review. It invokes no Codex process, model, authentication or network-backed experiment. The only executable scientific component used is the unchanged historical arithmetic auditor on its original frozen inputs inside a disposable engineering fixture. No scientific finding or verdict is generated.

## Observed failure versus demonstrated defect

The attached 027 report establishes that the native model completed the synthetic permitted read and the intended refusal. The scientific stage began but failed on its first broker request, with no successful broker receipt. Its exact tool arguments and underlying exception were not retained. Therefore neither this audit nor the parent can honestly name the exact failed argument in the actual run.

There is nevertheless a demonstrated systemic interface defect: **the constraints in the Python tool schemas are not the constraints the model receives.** At the pinned Codex source commit, `parse_dynamic_tool` passes `input_schema` to `parse_tool_input_schema`; that parser deserializes through a limited Rust `JsonSchema` structure. The structure retains type, description, enum, object fields and composition but has no fields for `minimum`, `maximum`, `minLength`, `maxLength`, `pattern`, `minItems` or `maxItems`. It has no flattened catch-all field. The unrepresented constraints are discarded. The resulting Responses tool uses `strict: false`. Sources, all accessed **2026-09-10**:

- [Dynamic schema conversion](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/tools/src/dynamic_tool.rs)
- [Schema structure and parser](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/tools/src/json_schema.rs), structure lines 41–74, parser lines 189–217, compaction lines 220–259.
- [Responses conversion](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/tools/src/responses_api.rs), `tool_definition_to_responses_api_tool`.

The offline source-derived projection of the five actual schemas loses **36 keyword occurrences**. Projected schemas range from 76 to 1,244 compact JSON bytes, all below the 5,000-byte native schema compaction threshold; no large-schema compaction is needed to establish this defect. This Python projection is explicitly a transcription of the applicable source subset, not an execution of native Codex or Rust.

For example, the model-visible schema permits `read_text` with `length: 200000`, while the broker accepts at most 100000. The description says only “Read a manifested UTF-8 source by character offset; actual whole-file SHA-256 is returned.” It does not tell the model the length bound. The actual frozen scientific prompt supplies no numeric `read_text` bounds either. A plausible request respecting the presented interface consequently aborts the entire review.

## Reproductions

`reproduce_contract.py` exercises the unchanged broker and protocol with actual synthetic files, hashes, PNG bytes, and the unchanged fixed auditor. All expected-outcome assertions pass in `REPORT.json` and `TRACE.txt`.

| Case | Broker result | Protocol result |
|---|---|---|
| Valid index read, image, hash, fixed audit, dependency verdict | Five successes | Five successes with one receipt each |
| Read length 200000 or 0, integral floating offset 0.0 | Input rejection | Generic fatal stop; no receipt |
| Missing required offset | Input rejection | Same generic fatal stop |
| Canonical mistyped path, `./` path, offset after EOF, wrong resource kind | Input rejection | Same generic fatal stop |
| Repeated fixed audit | State precondition rejection | Same generic fatal stop |
| Whitespace summary, 30001-character summary, missing/duplicate subjects, substantive verdict before audit | Input/precondition rejection | Same generic fatal stop |
| 600000 characters across 20 allowed objection strings | Accepted directly by broker | Request-size rejection before dispatch |

Except for the omitted required offset, all reproduced argument objects satisfy the source-derived model-visible schema. Some also satisfy the original Python schema. The request-size case satisfies the original Python schema and broker yet exceeds the protocol's 512 KiB request ceiling. This is another interface-level limit requiring explicit instruction and prevalidation, though it cannot explain the current generic broker failure because its protocol error string differs.

The first local reproduction incorrectly reused a successful dependency-verdict output directory between the direct and protocol checks. The exclusive-output guard correctly rejected that reuse. `PRE_FINAL_REPORT.json` preserves this fixture error. The final reproduction uses separate output directories, and all five valid paths pass. Six downloaded primary source files were checked against their exact Git blob SHA-1 identities after removing a local patch-added terminal newline; `source/PROVENANCE.json` records the verified source identities and SHA-256 hashes.

## Why earlier tests missed this

The earlier synthetic challenge specifies exact, already-valid arguments to a single text-read tool. It proves permitted transport and an intended denial, not usability of all five scientific tools through the model-facing schema. Broker tests deliberately verify rejection of malformed inputs. Protocol tests largely use stub brokers or predetermined arguments. None closes the path from **native schema conversion to plausible model arguments to broker behavior**. More tests of predetermined calls do not cover that omitted interface.

The design then treats every broker failure as a terminal integrity breach and removes its safe cause. This combines an incomplete interface, an unnecessarily catastrophic response to ordinary input mistakes, and insufficient diagnostics. These engineering choices, rather than the user's execution or research difficulty, are responsible for the repeated handoff pattern. The exact latest trigger remains unresolved because its evidence was discarded.

## Recommended complete correction before any model run

1. Add a separate adapter; do not change the frozen scientific broker, protocol, auditor or prompt. Present exact argument constraints and pagination examples in concise tool descriptions that survive native conversion. Include all five tools, preconditions, path rules, verdict total byte limit, and one-time output behavior. Test the source-projected descriptions/schema, not only the originally submitted JSON.
2. Before calling the immutable broker, validate ordinary input errors against immutable manifest metadata and operation state. Return a bounded, fixed-code unsuccessful tool result that lets the model correct its request within the same turn. Enforce a small finite input-error ceiling and the existing total call/deadline budgets. Never catch a poisoned broker and pretend it is usable; avoid dispatching invalid arguments in the first place.
3. Keep foreign/replayed requests, unknown operations, traversal/absolute paths, changed input bytes/identities, unexpected exceptions, unauthorized destinations, and output integrity failures terminal. No new tools, paths, mount rights, models, credentials or automatic model restarts are required. Canonical missing paths and wrong kinds can be recoverable refusals without disclosing anything outside the manifested inventory; traversal remains terminal.
4. Record fixed phase/tool/error-category metadata before losing the exception, without raw requests, unknown strings, credentials or paper contents. Distinguish argument validation, evidence integrity, fixed-auditor failure, output writing, response serialization, deadline and unsupported message. This allows the next unexpected stop to be actionable without another diagnostic-only model run.
5. Exercise a full offline scientific-shaped path: index pagination, original packet and supplementary index discovery, both manifest hashes, actual historical audit, PNG image transport, verdict serialization and readback. Cover ordinary-error recovery plus every terminal boundary adversarially, and verify the frozen science hashes stay unchanged. A reviewer should not have to produce flawless tool syntax for an hour to avoid losing all work.

An additional mounted-packet preflight can deterministically read all required bootstrap resources and verify all resource kinds, actual sizes, UTF-8 decoding, PNG dimensions, auditor dependencies and verdict capacity **before** any model is started. The full current private 019 packet is unavailable in this hosted copy; the earlier smaller packet does not justify claiming an exact current-packet integration test. Such checks can run within the same final human submission bundle, without consuming model allowance.

No new native/model probe is recommended until this complete interface and failure-policy correction has passed offline testing. Even then, a successful engineering test cannot guarantee the scientific review's eventual verdict or adequacy.
