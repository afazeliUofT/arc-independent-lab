# Reviewer implementation decisions from the exact client interface

2026-09-07. PI engineering specification for the next step; no reviewer, model or Codex service has run. The source/interface discovery is complete. Do not ask the human to export the schema or repeat the passing command canary.

## Evidence and its boundary

The official release reconstructs the exact laptop executable in memory. Both published compressed export blobs occur uniquely inside those bytes. Their decoded `json_schema` maps therefore give the embedded interface data of the observed executable, rather than an assumed interface from the latest documentation. The exported maps and exact release source are in `artifacts/GATE0_CODEX_INTERFACE/20260907_001/`, whose `MANIFEST.json` SHA-256 is `61a99383e034ddd892586125664fd67390225f0bbd6410a0447e706926b96147`. Root separately rechecked the archive, complete in-memory binary, blob positions and every schema string: `evidence/GATE0_CODEX_INTERFACE_VERIFICATION_2026-09-07.json`, SHA-256 `7e9f3cde718ddce42643a8440b2c94c568e2955a1b8c118f6a0ee2d97db2a941`.

This is static evidence. It does not establish effective laptop settings, a subscription entitlement, the available model, fresh context or actual tool enforcement. The saved executable discrepancy and the superseded inference from its truncated bytes remain in `evidence/GATE0_CODEX_INTERFACE_EXTRACTION_OBSERVATIONS.json`; that copy was never executed. Source: [official release](https://github.com/openai/codex/releases/tag/rust-v0.151.0), [exact release source](https://github.com/openai/codex/tree/78c290807ce710180111df227df3b7a4fe845452), accessed 2026-09-07.

## Concrete interface choices

The following names are read from `schemas/experimental.json` in that manifested artifact. Each value is the original JSON-schema string keyed by its original export path. The release's separate `config-schema.json` supplies configuration syntax; recognized syntax does not prove that a setting is effective or permitted by managed requirements.

| Interface | What the embedded schema establishes | Implementation decision and remaining check |
|---|---|---|
| `v1/InitializeParams.json` | `capabilities.experimentalApi` is an explicit opt-in | Request it because the required profile and broker interfaces are experimental; reject an unsupported negotiation |
| `v2/ThreadStartParams.json` | `dynamicTools`, `permissions`, `ephemeral`, `environments` and `selectedCapabilityRoots` exist | Fresh ephemeral thread; explicit narrow broker tools; named permissions; no inherited capabilities. Inspect actual effective tool exposure before supplying science |
| `ThreadStartParams.environments` | An empty array disables environment access for turns that do not override it | Candidate way to withhold native filesystem/shell environments while retaining broker reads; verify actual behavior, not just the schema description |
| `ThreadStartParams.permissions` | Cannot be combined with legacy `sandbox` | Use the named profile consistently; reject requests that mix representations or relax it later |
| `ThreadStartParams.multiAgentMode` | Deprecated and explicitly ignored | Do not use it as a collaboration restriction. Check actual feature/tool controls instead; highest effort must not silently expose additional agents |
| `v2/ThreadStartResponse.json` | Returns `activePermissionProfile`, `instructionSources`, model/provider and reasoning effort, among other fields | Check the returned profile and model, plus allowed instruction origins. An empty instruction list alone is not proof that all context sources are absent |
| `DynamicToolCallParams.json` / `DynamicToolCallResponse.json` | Calls identify thread, turn, call, tool, namespace and arguments; results support text and image content | Match every call to the active session and a closed tool/argument allowlist; no arbitrary executable or destination path |
| `v2/ConfigReadResponse.json` / `v2/ConfigRequirementsReadResponse.json` | Effective config/origins/layers and managed requirements are separate response objects | Inspect in the parent, retain only allowlisted control fields and provenance, and never log raw configuration or authentication. Missing/unreadable requirements are not a clean default |
| `v2/ModelListResponse.json` | Model entries advertise `model`, `supportedReasoningEfforts` and `defaultReasoningEffort` | Establish the existing-subscription model and highest supported effort. Do not silently substitute a different model or paid provider |
| `v2/GetAccountRateLimitsResponse.json` | Returns named limits and a multi-bucket map; reset-credit information is a separate field | Read narrowly if available. Do not infer this hosted conversation's quota, reset limits, or enable automatic continuation |

`ServerRequest.json` also lists approval, permission, elicitation, authentication-refresh and other requests. A wrapper that only handles dynamic tools must not approve or silently ignore those other routes. It needs explicit refusal/stop behavior that preserves evidence without exposing credentials. The schema supplies message shapes; it does not make every listed request acceptable.

## Minimum broker to implement

The reviewer needs a way to inspect the originals, recompute hashes, execute the unchanged verifier and emit its verdict. A general shell is unnecessary if these operations are supplied by a small external broker:

- Read a manifested text file, or render/read a manifested physical paper page. Scanned formulas must remain inspectable as images; OCR is an aid.
- Compute SHA-256 from the selected actual file bytes. Never return the expected manifest value as though it were a measurement.
- Execute the pinned observer consistency checker on its declared original-inventory view, with its full frozen dependencies. Check later metadata separately and keep the existing limitation explicit. No rewriting the checker to accept extra files.
- Create the structured reviewer verdict in an exclusive, predetermined output location. The parent preserves it directly for the human; the PI cannot choose, edit or overwrite the result.

Every argument must resolve through the frozen packet inventory. Reject traversal, symlinks, unmanifested files, arbitrary commands, arbitrary output paths and any attempt to alter the active control state. The scientific packet and verifier remain immutable. The parent checks pinned inputs before each reviewer turn and stops on a mismatch. These are proposed broker behaviors that need adversarial verification; this document is not their implementation.

## Startup remains a separate requirement

Exact release source shows generic argument dispatch attempts dotenv loading and helper-directory work before reaching the schema-only subcommand. That is why the static extraction was preferable to an unconstrained client launch. For the actual review, protect the whole client startup and descendants before presenting scientific inputs. Preserve readable managed requirements; identify exact required runtime/service paths without a broad home-directory grant. Do not repurpose `HOME` or `CODEX_HOME`, copy authentication, or ignore managed rules to make startup appear clean.

The schema exposes configuration controls for apps/connectors, MCP, plugins, hooks, memory, goals, code execution and collaboration. Those controls must be effective under the actual installed managed policy, and every retained tool route must be exercised against synthetic allowed and forbidden operations. A default-disable flag does not settle a per-tool override. Empty native environments plus restricted broker tools is the candidate route to test, not an asserted complete boundary.

Prepare that bounded startup and broker preflight next, together with the complete method/execution packet. Only after it passes should one human-attended scientific review use the existing subscription. No unattended supervisor, new quota assumption, new scientific approval request or mechanism treatment is part of this preparation. If the boundary cannot be established, record the exact missing condition and stop reviewer invocation. Even a dependency verdict belongs to the required separate reviewer; the PI cannot issue one to compensate for an unavailable reviewer.
