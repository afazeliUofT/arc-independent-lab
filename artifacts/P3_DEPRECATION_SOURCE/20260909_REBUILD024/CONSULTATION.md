# P3 startup deprecation source consultation — rebuild 024

Access date: 2026-09-09. Repository: openai/codex. Pinned commit: 78c290807ce710180111df227df3b7a4fe845452. The saved Cargo.toml identifies workspace version 0.151.0 at line 144.

This is an engineering source audit of startup-notice handling. It is not an independent scientific review, and it makes no scientific verdict. No native Codex client, authentication flow, model request, or reviewer run was started.

## Source recovery and integrity

The original failed notice's exact summary/details payload is unavailable in the supplied rebuild materials. EXPECTED_NOTICES.json therefore contains eight source-derived pairs conditional on the admitted reviewer profile's literal-false overrides; it does not reconstruct an observed failed payload or assert that all eight were received.

Each source file was fetched through the GitHub connector twice where the original requested contents URL was available: once at the exact commit's contents URL, and once at its Git blob SHA. Additional protocol-enum and version files were fetched by the Git blob SHA obtained from a commit-pinned directory listing. The saved UTF-8 bytes were checked using Git's SHA1(`blob ` + decimal byte length + NUL + bytes) against the listed blob SHA. All eight match. SHA256, byte counts, exact URLs, and Git blob identifiers are in MANIFEST.json. SOURCE_METADATA.json preserves the selected pinned-directory metadata used for those checks. These are content-identity checks, not a signature or runtime-attestation claim.

| Saved upstream path | Source role | Relevant lines |
| --- | --- | --- |
| [codex-rs/features/src/legacy.rs](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/features/src/legacy.rs) | Alias mapping, including the actual experimental_use_unified_exec_tool spelling | 11–51, 58–66 |
| [codex-rs/features/src/lib.rs](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/features/src/lib.rs) | Usage retention, bool-independent detection, exact notice strings, canonical keys | 407–419, 491–509, 531–603, 647–698, 880–884, 988–998, 1030–1034, 1090–1094, 1166–1170, 1190–1194 |
| [codex-rs/core/src/session/session.rs](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/core/src/session/session.rs) | Startup notice queue and SessionConfigured-first event dispatch | 1006–1016, 1472–1507 |
| [codex-rs/app-server/src/bespoke_event_handling.rs](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/app-server/src/bespoke_event_handling.rs) | Copy core event summary/details into server notification | 947–954 |
| [codex-rs/app-server-protocol/src/protocol/v2/notification.rs](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/app-server-protocol/src/protocol/v2/notification.rs) | DeprecationNoticeNotification payload definition | 8–16 |
| [codex-rs/app-server-protocol/src/protocol/common.rs](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/app-server-protocol/src/protocol/common.rs) | Wire method maps to deprecationNotice | 1920 |
| [codex-rs/core/tests/suite/deprecation_notice.rs](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/core/tests/suite/deprecation_notice.rs) | Upstream test asserts exact web-search pair for both true and false | 55–95 |
| [codex-rs/Cargo.toml](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/Cargo.toml) | Workspace version | 144 |

All links in this table were consulted at the pinned commit via their contents or blob API forms on the access date above; the exact consulted API URLs are in MANIFEST.json.

## Causal flow

1. The supplied 022 preparation helper copies its supplied base overrides, adds restrictive false feature controls, disables orchestrator MCP, and makes Code Mode false in its structured form (scripts/p3_reviewer_profile_022.py, lines 53–93). That helper does not itself prove the eight legacy keys are present; the new admission/session code must check the supplied profile. The source consultation did not alter that helper or the supplied controls.
2. Features::apply_map records web_search_request and web_search_cached usage without testing their boolean value. For aliases, it resolves the canonical Feature, records usage when the alias differs from the canonical key, then applies the true/false enable/disable branch. Therefore a literal false legacy spelling remains notice-producing. False remains a disable request; the notice is not evidence that the feature is enabled.
3. legacy_usage_notice emits generic migration pairs for five aliases and the web-search-specific pair for three names. The web-search notice's generic advice says web search is enabled by default; that static wording does not establish the effective web_search configuration of the current process.
4. Core session initialization copies each retained usage's exact summary/details into DeprecationNoticeEvent. It sends SessionConfigured first and then the queued startup events. This explains how deprecationNotice can precede a client adapter's expected next response without a model turn.
5. The app-server handler preserves both strings in DeprecationNoticeNotification. The payload fields are summary: String and details: Option<String>, with no threadId. common.rs:1920 provides the exact wire method deprecationNotice. Therefore recognition must rest on the bounded startup phase plus the admitted profile and exact payload pair, rather than a claimed per-notice thread identifier.

## Finite source-derived set

| Legacy or deprecated feature key | Canonical Feature key | Notice family |
| --- | --- | --- |
| features.codex_hooks | hooks | migration |
| features.collab | multi_agent | migration |
| features.connectors | apps | migration |
| features.experimental_use_unified_exec_tool | unified_exec | migration |
| features.memory_tool | memories | migration |
| features.web_search | web_search_request | web search |
| features.web_search_cached | web_search_cached | web search |
| features.web_search_request | web_search_request | web search |

EXPECTED_NOTICES.json retains the exact summary/details strings, including punctuation, literal backticks, quoted mode values, and the current pinned guidance URL. The eight entries are a finite source-derived recognition set, not a native-client output log. The JSON's canonical values for web-search keys describe internal Feature keys, not proposed replacement overrides.

The upstream first test deliberately calls record_legacy_usage_force with use_experimental_unified_exec_tool. That synthetic spelling is different from the actual alias experimental_use_unified_exec_tool in legacy.rs. It does not expand the permitted set. Likewise the source includes other deprecated settings; their notices are outside these eight profile-derived pairs.

## Implementation limits

The new adapter should accept only its supported, exact payload form, check the literal-false profile conditions, bound the number of notices, and restrict acceptance to the authorized startup phase. Unknown, altered, duplicate, oversized, or late notices must remain stop conditions under the new local contract. These strict local rules are an engineering policy for this adapter; the upstream protocol's optional details field alone does not guarantee them.

No notice acceptance establishes effective model identity, effort support, authentication, entitlement, absence of tools, a successful reviewer run, or scientific independence. No override should be removed, enabled, or migrated merely to suppress the notices. The original 022 reviewer abort remains evidence of an abort, not a completed review. This consultation does not supply missing runtime receipts or change scientific verdicts.
