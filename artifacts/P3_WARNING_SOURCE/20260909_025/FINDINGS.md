# Pinned Codex startup warning source audit

Read-only primary-source engineering audit. Access date: 2026-09-09. This is not an independent scientific review and supplies no model-runtime evidence.

## Result and evidential limit

REPORT(20260909-213441).json (reported SHA256 60f7a041d8415990a28362459e4ddd1b6029f10c1066d92ab85e0c6efee25c5f) establishes rejection of generic method `warning` after eight accepted deprecations. The exact discarded warning body is not recoverable from that report. This audit does not identify its actual message.

There are at least three materially different source-compatible next-warning causes: an inherited explicit under-development feature notice, a configuration/requirements diagnostic queued at thread startup, and a first-turn model-metadata/Code Mode dependency warning. All can precede the first turn-start/item notification visible to the controller. Therefore the observed order does not justify admitting a warning prefix or assuming the next warning is harmless.

Captured primary source: openai/codex commit `78c290807ce710180111df227df3b7a4fe845452`, package version 0.151.0. MANIFEST.json records all 58 exact files, source URLs, access date, Git blob SHA and independently computed SHA256. Every selected blob was verified using SHA1("blob " + byte_length + NUL + contents). Eight files reused from 024 were reverified against the pinned remote tree. GitHub default-branch searches were used only to locate a few source paths; every evidentiary file was fetched/reverified at the pinned commit's blob SHA. No claim relies on default-branch source contents.

## Bounded call graph and order

1. Config construction creates `config.startup_warnings` from config-layer warnings, then managed/exact requirement handling, hook trust bypass, managed feature requirement aliases/unknown keys, Windows sandbox constraints, named permission profile selection/compilation, agent role loading, SQLite path requirements, approval/reviewer/permission/web-search constraints, and OTel sanitization. See core/src/config/mod.rs:3166–4110 and the called config helpers captured in this source bundle.
2. Codex startup appends `LoadedUserInstructions.warnings` to that same vector (core/src/session/mod.rs:549–556). The ordinary Codex-home provider can produce a global AGENTS.md read-failure diagnostic; arbitrary instruction provider warning strings are an open interface.
3. Session::new builds its post-configured queue: all legacy feature deprecations first (session/session.rs:1006–1016), all config.startup_warnings next (1017–1024), optional under-development warning next (1025–1037), then hook discovery warnings (1296–1304).
4. Session::new sends SessionConfigured then that queue in order (session/session.rs:1477–1507). This is producer queue order, not a promise that thread/start's reply or thread/started proves the app-server listener drained it.
5. After Session::new returns, Codex startup can additionally send unsupported service-tier warning (session/mod.rs:794–801, formatter960–975). Resume history can produce a previous/current model mismatch warning; a new ephemeral thread excludes that resume branch.
6. At input admission, model warnings are awaited BEFORE spawn_task/start_task (session/turn_input.rs:302–303 and410–411). These are, in source order: fallback model metadata, Code Mode unavailable, Code Mode configured for a model without support (session/turn_context.rs:1042–1077).
7. Only afterward does tasks/mod.rs:start_task emit turn-start lifecycle (329), start the task and eventually model sampling. Thus the controller may already have sent an accepted turn/start yet receive a model/dependency warning before turn/started or item messages. A no-model thread-start probe cannot exercise this prelude.
8. Downstream warnings after task/sampling/operations are separately catalogued for fail-closed recognition: host skill/provider warnings, async hook output, transport fallback, cyber model reroute, compaction accuracy, task transcript persistence failure, rollback persistence failure, execpolicy and network amendment failures. They are not startup informational allowances.

The app-server can also emit extension warnings directly, separate from core WarningEvent. The parallel notification-contract audit covers that extension route and its bounded truncation/asynchronous listener behavior. Arbitrary extension/provider text prevents a finite whole-program semantic warning allowlist. This bundle's claim is the bounded ordinary thread-start/config/first-turn prelude and explicit critical exclusions, not every possible third-party extension string.

## Wire contract

Source app-server-protocol/src/protocol/v2/notification.rs:18–27 defines `WarningNotification { thread_id: Option<String>, message: String }` with camelCase serialization. The wire method is `warning` (protocol/common.rs:1918).

Pinned JSON schema requires only `message` (string). `threadId` may be omitted, string or null. It has no turnId, no detail/severity/code discriminator, no closed extra-property restriction and no string-length bounds. These source permissions do not require a controller to accept all values. The core WarningEvent translator always constructs `threadId: Some(current_thread_id)` and transfers message unchanged (app-server/src/bespoke_event_handling.rs:255–263). It supplies no WarningEvent id/turn id on this wire.

A strict controller may require exactly its supported fields, the current known thread id, a bounded UTF-8 body and a tightly recognized diagnostic family. Schema-validity alone is not authorization. Source-family classification and admission must remain separate.

## Under-development features

features/src/lib.rs:1642–1688 checks the FULL effective config table. It requires suppression false, a canonical feature key explicitly true (boolean or table.enabled=true), the effective feature enabled and Stage::UnderDevelopment. It sorts keys lexically and formats the one fixed message. Default-enabled features without an explicit true table entry do not trigger it; aliases not matching a canonical FEATURES key do not enter the list.

UNDER_DEVELOPMENT_FEATURES.json is a complete extraction of all 48 canonical UnderDevelopment entries and their enum identifiers/source lines. Each has default_enabled=false. Extraction count was cross-checked against every Stage::UnderDevelopment block in the pinned FEATURES array.

The approved 024 preflight/reviewer override functions add restrictive false values and no true feature keys. They do not overwrite every one of these 48 keys. An inherited explicit true key can therefore remain in the full effective table. The override subset alone cannot predict a mandatory warning or its key list.

The notice emission itself performs no capability invocation. Nevertheless, a notice naming a control required false contradicts the approved configuration; a notice naming another key does not establish that key is safe. Do not suppress the warning or broaden admission merely to remove the symptom. It can safely support a diagnostic consisting only of the source family id and recognized canonical enum keys, after complete fixed-message validation and bounds; do not publish its runtime config path, arbitrary body or body hash. Such a diagnostic still stops unless the exact feature state has already been approved.

## Model and Code Mode distinctions

Fallback metadata is not itself a different model identifier. models-manager/src/model_info.rs:142 preserves the requested slug and constructs a minimal descriptor with used_fallback_model_metadata=true. That can change tool/feature assumptions and is a dependency failure for this review contract. Actual model reroute is separately signalled by ModelReroute, followed by its warning (session/mod.rs:3485–3507); it must stop.

Tool mode has a particularly relevant precedence rule: core/src/tools/mod.rs:78–90 uses model_info.tool_mode before CodeMode/CodeModeOnly feature values. Consequently features.code_mode=false does not guarantee metadata cannot request Code Mode. With runtime unavailable, tool_mode=CodeMode and allowed in-process fallback, effective_tool_mode becomes Direct; CodeModeOnly or disabled fallback stays in the code-mode route. The warning text exposes either "Falling back to direct tools" or "Code mode will fail closed" (tools/code_mode/mod.rs:102–118). This is a route/dependency condition, not an innocuous warning.

The public model/list fields admitted by profile024 omit internal ModelInfo.tool_mode and used_fallback_model_metadata. Reading that same public catalog cannot prove these internal branches absent. The exact Code Mode warning formatter has no tracing statement. The already archived pinned protocol/src/openai_models.rs also marks used_fallback_model_metadata as skip_serializing and skip_deserializing; a models_cache.json key cannot recover that runtime marker and is ignored if present. The cache can expose selected model tool_mode as direct/code_mode/code_mode_only; absence or an unknown value is omitted by the native optional-selector deserializer. Cache content extraction alone does not prove actual-run cache selection or freshness.

## Critical family catalogue

WARNING_FAMILIES.json records 35 source families with phase, fixed source text/placeholder description, condition, conservative classification and logging reachability. It is a source catalogue, not executable regex policy. In particular:

- Permission fallback, unsupported filesystem rules, unrecognized requirement keys, hook trust bypass and provider/residency change are security/configuration stops.
- Metadata fallback, unsupported service tier, Code Mode availability, missing instructions, malformed roles and skill/provider failures are dependency/configuration stops.
- Under-development and malformed optional OTel diagnostics have informational emission semantics, but require validation against approved state before admission.
- Model reroute, runtime hook/tool/policy effects and other unexpected operations remain stops regardless of warning wording.
- Hook discovery warnings disappear when CodexHooks is effectively false because engine::new returns an empty warning vector before discovery. The configured false controls should not be weakened to inspect their output.

## Can the body be recovered without another native run?

There is one source-backed read-only candidate: the existing run's configured SQLite runtime-state directory.

- state/src/sqlite.rs:29 fixes the log filename as `logs_2.sqlite`; sqlite_home determines its directory. The approved override points at that run's native/runtime_state. log_dir/runtime_logs is not the SQLite log location.
- app-server/src/lib.rs:671–680 installs a separate local log database layer. state/src/log_db.rs:57–82 defaults this layer to TRACE for general targets. RUST_LOG=off controls the stderr formatting layer, and does not globally disable this independent SQLite layer.
- Current log schema is in state/logs_migrations/0002_logs_feedback_log_body.sql: `logs.feedback_log_body` contains the formatted message/spans; useful fixed metadata fields are target/file/line/thread_id/process_uuid/timestamp. The older message column was removed. A main database with WAL must not be treated as a complete standalone snapshot; a private consistent copy can preserve existing companions without mutating source files.
- Logging is bounded and asynchronous (queue2048, batch512, flush interval10s). Abrupt reaping can lose unflushed records. Existence of the file does not imply that the warning was persisted.
- Several config producers separately trace their diagnostic body or structured conflict fields. A matching retained producer trace could establish a specific family with no native model work.
- models-manager/src/model_info.rs:143 separately warns when fallback metadata is created. This is useful source-family evidence even though its text differs from the wire WarningNotification.
- Neither the under-development formatter nor the Code Mode unavailable formatter logs its body. Generic core send_event_raw (session/mod.rs:2272–2293) does not log event payloads. Outgoing app-server trace uses ServerNotification's strum Display, which is the wire method label; `app-server event: warning` does not contain the warning text.
- Ordinary rollout policy explicitly excludes Warning as transient (rollout/src/policy.rs:138–150). The optional rollout-trace mechanism requires CODEX_ROLLOUT_TRACE_ROOT, which approved restricted_env does not forward. It is not an expected recovery path here.
- Therefore a bounded offline SQLite classifier is the best next information-gathering action if actual024's runtime state is still available. Select only known producer metadata/family candidates, classify in memory, output finite labels/enum keys and bounded counts; never dump arbitrary feedback_log_body. Do not infer under-development or benignity from no match.

A thread-only no-model probe can cover thread-start config notices but cannot settle turn-only metadata/Code Mode causes. Another blind model turn is not justified by this source audit. If the offline evidence remains absent or inconclusive, the exact warning identity remains unknown.

## Verification and scope

All 58 source file Git blob SHAs verified. Under-development inventory cross-check:48/48. No native Codex process, authentication, model run, policy/controller mutation, external repository write or other programme access was performed. Only new source-audit artifacts under delivery/rebuild025/source_work were written. The root task will integrate selected artifacts and decide any authorized diagnostic workflow.

