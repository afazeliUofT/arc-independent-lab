# Exact-client tool boundary for the separate reviewer

2026-09-07 UTC. Consultative PI-side engineering audit in the shared workspace. No Codex client, service, model, tool canary or scientific reviewer was executed. This is source evidence for implementation, not an independent verdict or a claim that the laptop's effective boundary has passed.

The source-supported route is an environmentless, fresh app-server thread with narrowly brokered dynamic tools. **Dynamic tools are additive, not an exclusive tool allowlist.** Empty environments remove the environment-backed native handlers, but several other tool sources need separate effective controls. Two precedence rules matter: a model may supply Code Mode despite disabled Code Mode feature flags; and enabled `multi_agent_v2` takes precedence over `agents.enabled=false`.

## Version and reproducible source evidence

All Rust sources cited below are pinned to the official release commit `78c290807ce710180111df227df3b7a4fe845452`, corresponding to the previously reconstructed Codex 0.151.0 executable. Sources were retrieved as data through the GitHub connection and checked against the exact tree's Git blob SHA-1, then independently recorded with SHA-256. No retrieved code was executed. The complete 24-file source selection, licensing, URLs, access dates, byte lengths and hashes are in `artifacts/GATE0_TOOL_BOUNDARY_SOURCE/20260907_001/MANIFEST.json`, SHA-256 `bfdc6e4bb2547df33490bec334d1ea1668f8615ce1f412387a9c25c6374c3873`. The source archive includes Apache 2.0 LICENSE and NOTICE. All URLs in this note were accessed 2026-09-07.

Key source SHA-256 values are:

| Source under `codex-rs/` | SHA-256 |
|---|---|
| `core/src/tools/spec_plan.rs` | `52f549a2ac0836aece71f159850a634e71d1fbe5cb3bb58b98cca9b5744d6f9d` |
| `core/src/tools/spec_plan_tests.rs` | `e3184eec67ee091e794c96dbae8c967dcb4e2bf926f041aead574bb279aade0e` |
| `core/src/tools/mod.rs` | `0c8ec9324f67053cf7c14dac5d53504c9e8c370b84cb2323fdb0239e674572d7` |
| `core/src/config/mod.rs` | `75544f344fef0ad40be9eb9e1d0dbbdafcd50929bfe32376118c9b56003d7d97` |
| `core/src/tools/registry.rs` | `72c1360168efa5a21cbf14aefadedb538ee2f23ec92ca6cab2f749bbf5d41ed7` |

The separately manifested embedded schemas remain authoritative for wire spelling and accepted structure: `artifacts/GATE0_CODEX_INTERFACE/20260907_001/schemas/experimental.json` and the adjacent configuration schema. [Official app-server documentation](https://learn.chatgpt.com/docs/app-server) confirms the client-handled dynamic-tool protocol and distinguishes MCP status from the overall tool surface; current documentation does not replace the exact release source.

## What empty environments establish

`thread_start` converts the explicit environment vector and `thread_start_task` applies the default only when that option is absent. An explicit empty vector reaches `StartThreadOptions.environments` as `Some(empty)`. `TurnProcessor::build_environment_override` likewise preserves explicit selections; a later cwd-only or workspace-roots-only override can reconstruct default environments. Therefore the wrapper must keep `environments: []` on the fresh thread and subsequent turn, and refuse unrestricted turn/settings/cwd/environment updates. [Thread processor](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/app-server/src/request_processors/thread_processor.rs), [turn processor](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/app-server/src/request_processors/turn_processor.rs).

`tool_environment_mode` counts selected turn environments. `add_shell_tools` returns immediately if that count is zero. `add_core_utility_tools` separately requires an environment before registering apply-patch, view-image or permission-request handlers. This is registration absence, not only omission from the model's displayed tool descriptions. The exact upstream test `environment_count_controls_environment_backed_tools` asserts both visible and registered absence of `exec_command`, `write_stdin`, `apply_patch`, `view_image`, and `request_permissions`, and absence of terminal controls. The test was read, not rerun here. [Tool-plan implementation](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/core/src/tools/spec_plan.rs), [upstream test](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/core/src/tools/spec_plan_tests.rs).

This does not constrain process startup, native file/config reads by the client itself, authentication, metadata workers, or the external broker. Those require the whole-process boundary and broker validation developed separately.

## Minimum effective controls and residual cases

These are constraints to assert on the actual merged configuration and resolved runtime. They are not a ready-to-run launch profile. Apply restrictive controls at process startup and again at the thread, preserve managed requirements, and stop when a required value is unreadable or policy prevents it. Never rewrite policy or metadata to manufacture a passing result.

| Surface | Effective condition | Why it is needed |
|---|---|---|
| Native environment tools | `environments=[]`; no later cwd/root/environment replacement | Exact registration gate above |
| Collaboration at highest supported effort | `agents.enabled=false` **and** `features.multi_agent_v2=false`; also disable legacy `features.multi_agent` | `Config::multi_agent_version_override` prioritizes V2, then disabled agents, before model metadata. With both first conditions satisfied it returns Disabled. Ultra changes proactive instructions only after V2 is selected |
| Hosted web and standalone web extension | `web_search="disabled"` | Both hosted model specs and the `web.run` extension consult web-search mode; native command-network policy alone is unrelated |
| Apps | `features.apps=false` | Hosted Apps MCP contribution becomes removal. App-specific default toggles alone can have overrides |
| MCP | `orchestrator.mcp.enabled=false`; no selected executor roots and no effective external/client MCP contributions | An empty `mcp_servers` override is not evidence that layered or extension contributions are absent. Inspect effective catalog/status without starting new external servers |
| Plugins | `features.plugins=false`, `features.remote_plugin=false`; no selected capability roots | Avoid plugin discovery and contributed MCP/context surfaces; startup timing remains separately audited |
| Skills tools | `orchestrator.skills.enabled=false` and `selectedCapabilityRoots=[]`, with no resolved executor roots | `skill_tools` returns an empty vector when orchestrator skills are unavailable and the executor query is absent. Host skill discovery and injected context are separate |
| Memory and history-note tools/context | `features.memory_tool=false`, `memories.use_memories=false`, `features.token_budget=false`; disable memory-generation background features too | Dedicated memory extension checks MemoryTool/use_memories. TokenBudget disabled yields no token-budget config, so HistoryNotes backend/thread-hint tools cannot initialize through that config |
| Request input and planning utility | `tools.experimental_request_user_input.enabled=false`; `tools.update_plan.enabled=false` | Their resolved defaults are true. `features.default_mode_request_user_input=false` only changes allowed modes; it is insufficient to unregister input requests |
| Environment waiting, time, context-window control | `features.deferred_executor=false`, `features.current_time_reminder=false`, `features.token_budget=false` | These utility registrations are independent of having an environment |
| Image generation | Effective ImageGeneration disabled | Extension filtering uses this resolved feature along with model/provider availability |
| Browser, computer, hooks, goals, remote control | Effective corresponding features disabled; no host/client contributions | These require startup and extension enforcement; an environmentless thread alone does not prove absence |
| Code Mode | Resolved effective tool mode must be established; feature booleans alone do not establish Direct | `requested_tool_mode` uses model-declared `tool_mode` first, falling back to feature flags only when model metadata omits it |

Collaboration precedence comes from [configuration resolution](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/core/src/config/mod.rs) and [Ultra mode instructions](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/core/src/session/multi_agents.rs). `ThreadStartParams.multiAgentMode` is ignored and its response is a compatibility constant; neither proves collaboration is disabled.

Code Mode precedence is explicit in [tools/mod.rs](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/core/src/tools/mod.rs). A Code Mode worker may remain even with no nested tool entries. Do not silently lower the requested model or effort to avoid this. Either establish Direct mode for the actual selected model, or treat the Code Mode worker as a retained surface requiring its own complete containment proof. The public `model/list` schema includes multi-agent metadata but does **not** expose `tool_mode` or the full experimental supported-tool list.

Two additional model-declared tools are registered directly in `add_core_utility_tools`: `send_user_message_async` for a root session and `test_sync_tool` when advertised by the model. Their registration in this function does not consult their similarly named feature toggles. Refuse to assert a broker-only catalog merely because those toggles were set. The source also allows model-supported tool search when deferred entries exist; an unused search feature flag is not an all-tools kill switch. [Tool-plan implementation](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/core/src/tools/spec_plan.rs).

Extension-specific checks are in [Apps MCP contribution](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/ext/mcp/src/lib.rs), [skill tool creation](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/ext/skills/src/tools/mod.rs), [skills thread state](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/ext/skills/src/state.rs), [memory extension](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/ext/memories/src/extension.rs), and [history-notes extension](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/ext/history-notes/src/extension.rs).

## What the protocol can and cannot attest

The exact `ClientRequest` schema has no general `tools/list`, tool-plan preview or resolved-tool-catalog RPC. `mcpServerStatus/list` covers MCP only. `experimentalFeature/list` reports feature enablement; `config/read` and `configRequirements/read` report configuration and requirements. None reports the complete resolved registry, hosted tool set, Code Mode nested inventory and model metadata together. `server/diagnostics` exposes process/gauge data, not a tool catalog.

`features.tool_registry.turn_metadata_includes_tool_info` causes `finalize_tool_router` to construct tool namespace information only for Responses-Lite models. `ToolRouter::tool_namespaces_info` is an internal per-request inventory, not a public app-server response. Thus it cannot be treated as a no-model preflight attestation obtained through ordinary stdio RPC. Likewise `attestation/generate` asks the host for an opaque client token; it supplies no tool inventory. [Tool-plan finalization](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/core/src/tools/spec_plan.rs), [router](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/core/src/tools/router.rs), embedded `AttestationGenerateParams`/`Response` schemas.

The raw model catalog exists internally and is cached at the actual Codex home's `models_cache.json`. That file can contain `tool_mode`, but a separately read cache is not by itself evidence that the active turn uses identical in-memory metadata: refreshes and provider-specific catalog selection exist. It can inform a later bounded verifier, not replace binding the model metadata to the actual turn. Do not inject a fabricated catalog or modify model metadata to hide a tool. [Model manager](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/models-manager/src/manager.rs), [cache implementation](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/models-manager/src/cache.rs).

`ToolRegistry::dispatch_any_with_terminal_outcome` looks up the registered runtime and returns an unsupported-call error if absent. A hidden tool, however, is not necessarily unregistered: model-visible specs and executable registry are separate. The wrapper must distinguish advertisement, registration, execution and external effects. Seeing only broker calls in one ordinary model response is not an exhaustive denial test. [Registry dispatch](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/core/src/tools/registry.rs).

## Closed external protocol for the broker

The external driver must own a finite state machine, not forward arbitrary JSON-RPC supplied by the model. Before any scientific turn it may send only its pinned initialization/configuration/requirements/model/allowance operations. Later it may create exactly the authorized fresh thread and turn, deliver bounded broker results, and interrupt on failure. No resume/fork/history import, settings mutation, environment addition, shell/file/process RPC, account login/reset-credit operation, plugin installation, MCP direct call or tool-triggered nested thread creation is forwarded.

For incoming server requests the exact schema supports the following finite decisions. Refusal is followed by an interrupt/stop and a sanitized evidence record; it is not permission to try another route.

| Incoming method | Driver action |
|---|---|
| `item/tool/call` | Handle only exact broker namespace/name, current thread/turn, unused call ID, exact argument shape and bounded output. Unknown namespace/tool/extra property or replay stops the session |
| `item/commandExecution/requestApproval`, `item/fileChange/requestApproval` | Return `{"decision":"cancel"}`; never accept or amend a policy |
| `item/permissions/requestApproval` | Return `{"permissions":{},"scope":"turn"}` and stop; never supply additional permissions |
| `mcpServer/elicitation/request` | Return `{"action":"cancel"}` and stop |
| `execCommandApproval`, `applyPatchApproval` | Return `{"decision":"abort"}` and stop |
| `item/tool/requestUserInput` | Do not invent a human answer; reject and stop |
| `account/chatgptAuthTokens/refresh`, `attestation/generate` | No token handling/copying or fabricated attestation in this driver; reject and stop if unexpectedly requested |
| `currentTime/read` | Either explicitly implement the fixed host-clock-only response shape or reject; the minimal driver rejects it |
| Any unknown method or malformed frame | Protocol error, bounded stop and preserved evidence |

Dynamic-tool results are `{"contentItems":[...],"success":true|false}`. The tool handler parses arguments, emits a DynamicToolCall item and waits for the client response; it does not perform the broker operation. This makes the broker's own path validation, actual byte hashing, frozen verifier subprocess and exclusive verdict creation necessary enforcement components. The success field is not scientific approval. [Dynamic-tool runtime](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/core/src/tools/handlers/dynamic.rs).

## Implementation consequence

The concrete next build can safely implement the broker, closed protocol parser and offline adversarial validation using the pinned schema. It must retain separate states for `BROKER_VALIDATED`, `CLIENT_STARTUP_BOUNDARY_OBSERVED`, and `RESOLVED_TOOL_BOUNDARY_OBSERVED`. Completing the first state must never enable inference or science on its own. The remaining full-client launch dependency cannot be settled by fabricating a nonexistent tool-catalog RPC or calling the passing shell canary a full reviewer boundary. These source findings are useful constraints for the finite reviewer driver, not justification for another unbounded platform-building phase.

Three initial guessed source paths returned GitHub 404; tree discovery then resolved the real paths. Exact error for each: `GitHub API error 404: {"message":"Not Found","documentation_url":"https://docs.github.com/rest/repos/contents#get-repository-content","status":"404"}`. Paths were `codex-rs/core/src/tools/spec.rs`, `codex-rs/app-server/src/codex_message_processor.rs`, and `codex-rs/ext/skills/src/tools.rs`. No claim depends on those failed fetches.
