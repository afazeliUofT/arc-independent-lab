# Reviewer capability effects: bounded engineering consultation

2026-09-08. This is PI-side engineering consultation by a same-workspace sub-agent, not an independent reviewer or a measured client/model run. No native client, credential, scientific model turn or other programme was accessed. The exact installed-source commit is `78c290807ce710180111df227df3b7a4fe845452`.

## Finding and correction

A missing all-tools catalog RPC remains a limit of the interface. It does not follow that every residual registered tool must be absent before a read-only reviewer is possible. Judge the retained effect authority. The previously identified async-message and test-sync handlers have narrower effects than filesystem or arbitrary-execution tools:

- `send_user_message_async` parses a single message and emits ordinary AgentMessage started/completed events. It does not open a file, select a network destination, spawn a reviewer, or supply a user answer. A bounded parent can capture this as output and never forward a response. It is still a registered non-broker tool if advertised by the selected model.
- `test_sync_tool` sleeps, waits on process-local barriers or waits for current-turn Git-enrichment state, and returns `ok`. It cannot select a file or external destination. Parent wall/process/output limits must still bound stalls. Its presence is not proof of evidence-write authority.

Sources: [async message handler](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/core/src/tools/handlers/send_user_message_async.rs), [test-sync handler](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/core/src/tools/handlers/test_sync.rs), accessed 2026-09-08. Complete exact bytes and Git blob IDs are in this archive.

## Code Mode can be closed independently of model metadata

The existing warning that model metadata can override `features.code_mode=false` is correct. There is a narrower execution gate that the earlier tool-plan analysis did not finish tracing:

1. `ThreadManager::new` selects `ProcessOwnedCodeModeSessionProvider` only when resolved `Feature::CodeModeHost` is enabled **or** resolved `disable_in_process_fallback` is true. Otherwise it selects `DisabledCodeModeSessionProvider` (thread_manager.rs, lines 461–468).
2. The code-mode configuration resolver reads nested host fields only when `features.code_mode_host` is a table. Effective **boolean false** at this complete feature key leaves no nested host configuration and defaults `disable_in_process_fallback` to false. This should be verified from actual winning configuration layers, not assumed from a projected feature boolean.
3. The disabled provider's `availability` and `create_session` both return an error. Its `create_session_with_limits` delegates to the same refusal. No JavaScript host session is created by this provider.
4. The CodeMode service calls that provider when a cell requests a session. It does not manufacture another provider. With unavailable service, a model-declared ordinary CodeMode can fall back to Direct through `effective_tool_mode`; CodeModeOnly does not take that fallback, but any attempted exec still fails to obtain a session.
5. App-server must retain its ordinary local host selection; do not supply a remote gRPC host override. The exact app-server source already archived in `artifacts/GATE0_CODEX_STARTUP/20260907_001/` distinguishes its Local=None selection from an explicit remote provider.

Sources: [thread manager](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/core/src/thread_manager.rs), [disabled provider](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/code-mode/src/remote_session.rs), [code-mode service](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/core/src/tools/code_mode/mod.rs), accessed 2026-09-08. [Configuration resolver](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/core/src/config/mod.rs) and [effective tool mode](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/core/src/tools/mod.rs), previously accessed 2026-09-07 and reinspected locally 2026-09-08.

This is a source argument for a candidate closure, not a claim that these controls were included in the successful metadata report or observed at reviewer invocation.

## Keep the evidence broker usable

The supported configuration table

```toml
[features.code_mode]
enabled = false
direct_only_tool_namespaces = ["functions"]
```

keeps existing default-namespace broker tools exposed directly, including in a model-declared CodeModeOnly session. `apply_direct_model_only_namespace_overrides` converts matching code-mode-available tools to DirectModelOnly. `is_hidden_by_code_mode_only` hides only tools still available in Code Mode. This does not add a registered runtime or relax its authority. The current broker emits default-namespace dynamic tools and rejects a non-null namespace in incoming tool requests; that protocol need not be changed just to introduce this visibility override. The native normalized namespace for selection is `functions`.

Source: [tool-plan finalization](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/core/src/tools/spec_plan.rs), [dynamic handler](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/core/src/tools/handlers/dynamic.rs), previously accessed 2026-09-07 and reinspected locally 2026-09-08. Exact embedded schema `CodeModeConfigToml` describes `direct_only_tool_namespaces` as remaining top-level in code-mode-only sessions, in the already pinned config schema.

Do not override model metadata, choose a lower model merely to make this work, spoof a guardian session, hide actual managed policy, or advertise a broker-only registration inventory. There is no need to enable the Code Mode host, copy its executable into the mount plan, or inspect its entire JavaScript sandbox to prove refusal by the disabled provider.

## Minimal next implementation

Implement **one finite human-launched reviewer controller** using the existing verified startup/broker pieces, not another account/login probe and not a general supervisor.

- Accept and preserve the successful post-login report. Do not repeat its passing sign-in or generic command canary.
- In the actual reviewer controller, add and verify restrictive controls missing from the metadata-only profile: `features.code_mode_host=false` as a boolean; `features.image_generation=false`; `features.deferred_executor=false`; `features.current_time_reminder=false`; `orchestrator.mcp.enabled=false`; and the code-mode table above. Keep the complete existing effective controls, no selected capabilities/executor roots, no client-contributed extensions/MCP, and explicit `environments=[]` on thread and turns. Verify source-sensitive scalar/table winners. These are ephemeral restrictions, not edits to persistent configuration.
- Add adversarial synthetic tests to the new controller for routing, closed native methods, forbidden namespace/call replay, context construction and permit transitions. The existing broker and protected verifier should be reused unchanged; its passing cases need not be recreated.
- In the same finite handoff, obtain allowlisted actual model identifiers and supported effort values as part of final admission. The prior literal-match filter discarded these harmless fields. Never interpret absence of one literal identifier as absence of all model entitlement. Never silently substitute an unapproved model; if no acceptable model is available, stop with this exact dependency and the useful filtered catalog.
- Launch a separate synthetic thread with no scientific input to observe the actual final profile and denied tool attempts. Keep known source proofs distinct from observed attempted denials; the model failing to attempt a tool is not an observed denial. A test that sees only broker calls is not a complete registry attestation.
- Only after admission and required synthetic boundary checks, use a fresh ephemeral scientific thread, fresh thread/turn bindings, allowed instruction origins, no resume/fork/memory/import/history, and the existing closed manifested evidence broker. Isolate the scientific context from the synthetic prompt as well as PI conversation. Prefer separate fresh process/state directories for synthetic and scientific sessions if runtime context-origin accounting is not adequate.
- Apply fixed per-run wall/output/call limits; recheck every frozen input before each science turn; preserve the reviewer's verdict directly and exclusively. Keep parent invocation and publication receipts distinct from the scientific verdict.
- Stop when an effective restriction conflicts with real managed requirements or a native/extension authority cannot be bounded. Do not override the policy or widen paths to manufacture passage.

Source-supported practical aim: evidence reads/hashes/fixed auditor plus exclusive verdict, with harmless bounded client output and unavailable Code Mode admitted honestly. This can be a finite attended review without demonstrating unattended continuation or a hosted ChatGPT quota meter. The received Codex quota is limited to its named provider window and remains unsuitable as a hosted-conversation allowance.

## Genuine remaining conditions

The successful report establishes metadata-stage observations, not a reviewer thread. Remaining implementation work is the actual controller and its exact enforced tool/context boundary, model identity/effort admission, preservation of existing policy/auth sources, and the finite synthetic observation tied to those actual sources. No scientific formal verdict exists yet.

The approved scope016 is expressly a metadata operation. The original programme authorizes scientific work and finite existing-subscription use, but any new reviewer operation that needs the native writable auth-file exception must be checked against the actual granted scope. It must not silently reuse a one-operation metadata exception as a general credential-write permission. Prepare the concrete finite reviewer scope first; ask only for a genuinely new required exception, not repeated sign-in or ordinary implementation permission.

This consultation does not choose a scientific disposition. After the separate reviewer interrogates the frozen novelty audit, the next research branch remains the open acquisition of useful descriptions, predicates or models through interaction, if the earlier candidate reductions survive review.

## Archive provenance

New fetches carry their GitHub-advertised blob IDs and are verified against exact full contents. Existing exact sources and LICENSE/NOTICE are copied from the previously manifested official-source archive with their original access date retained. The apply_patch transport initially appended one extra terminal LF to the new source copies. `TRANSFER_CORRECTION.json` records those initial local hashes; exactly one LF was removed only when that restored the advertised Git blob. No semantic source edits or native execution occurred. The archive manifest is the operative final byte record.
