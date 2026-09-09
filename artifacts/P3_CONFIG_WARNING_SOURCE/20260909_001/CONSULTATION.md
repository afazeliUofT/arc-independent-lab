# Config-warning source consultation, 2026-09-09

This is engineering consultation within the PI's shared workspace. It is not an independent scientific review, an observed native boundary test, or a scientific verdict. No Codex client, credential operation, model turn, or account operation was performed for this consultation.

## What the attached report proves

The report supplied as `REPORT(8).json` records one initialized synthetic-stage native process, then a `configWarning` notification. The controller stopped before its queued `config/read` was written; no thread request, model-turn request, dynamic tool call, synthetic read/refusal, or scientific review occurred. The native process was reaped. The report does not retain the warning summary, details, path, or range. Therefore its exact warning family cannot be recovered from this report. Stream byte counts do not identify the family reliably.

The source emits buffered startup warnings after initialization. Thus the observed order is a normal supported protocol sequence; the controller's generic stop reason describes an unhandled notification category, not evidence that the native process attempted an unadvertised tool effect. A fail-closed stop was appropriate while the warning was unclassified, but discarding all category information made the resulting report insufficient to diagnose the cause. Source: [initialize processor](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/app-server/src/request_processors/initialize_processor.rs), accessed 2026-09-09.

## Exact schema and known fixed advisory

The pinned `v2/ConfigWarningNotification.json` defines a `summary` string, optional `details` string/null, optional `path` string/null, and optional `range` null or `{start:{line,column},end:{line,column}}`. Only `summary` is required by the JSON schema. Positions are nonnegative integers in the schema, although the Rust field comments describe 1-based positions. The objects are not closed by the upstream JSON schema. A local classifier may impose smaller bounded sizes and reject unknown fields explicitly; those restrictions must be described as local output/admission restrictions, not upstream requirements.

Rust serialization retains `details:null` but omits `path` and `range` when their `Option` values are None. The outer notification is `{"method":"configWarning","params":...}`; the already pinned notification-envelope source governs optional JSON-RPC compatibility. Source: [configuration protocol](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/app-server-protocol/src/protocol/v2/config.rs), originally accessed 2026-09-07, reinspected 2026-09-09; [outgoing serializer test](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/app-server/src/outgoing_message.rs), originally accessed 2026-09-08, reinspected 2026-09-09. The extracted schema in `ConfigWarningNotification.json` is copied byte-for-byte from the existing pinned experimental-schema map, not regenerated.

The exact missing-system-bwrap advisory emitted by this source has these params:

```json
{
  "summary": "Codex could not find bubblewrap on PATH. Install bubblewrap with your OS package manager. See the sandbox prerequisites: https://developers.openai.com/codex/concepts/sandboxing#prerequisites. Codex will use the bundled bubblewrap in the meantime.",
  "details": null
}
```

The outer `bwrap` executable is not mounted into the inner empty-root reviewer namespace in the supplied mount plan. Therefore the fixed missing-system-bwrap warning is a strong source-based candidate if the native startup permission profile requires a platform sandbox. The actual startup profile was not read in this attempt, and the warning text was discarded. The classification remains an inference, not an observed explanation. This warning does not itself establish that the outer namespace is absent or ineffective. It describes native lookup of a nested sandbox helper. The source returns the missing-helper warning before trying a nested subprocess. Source: [Linux bwrap lookup and warning generation](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/sandboxing/src/bwrap.rs), accessed 2026-09-09.

Do not install a fake helper, bind in extra executable authority, disable the native sandbox, or suppress all `configWarning` notifications to remove this symptom. A correction may explicitly recognize and report only this exact fixed advisory while preserving the outer mount boundary and every later effective-configuration, requirements, model, thread, synthetic-refusal, and cleanup check. Such recognition must not imply that the native fallback helper was executed or successfully tested. Any changed details, unexpected path/range, different summary, malformed field, or warning received outside its accepted startup position must remain a stop unless separately investigated.

## Other warning families that must remain stops

The startup source also emits the following families. These must not inherit the benign-advisory classification.

| Family | Source behavior | Consequence for reviewer admission |
| --- | --- | --- |
| Invalid configuration with defaults | On load failure without strict mode, stores a fixed summary and detailed error, then loads defaults | Stop. The observed argv includes `--strict-config`, which returns the error before initialization instead; this specific branch is excluded for the observed successful initialize, conditional on the pinned source/runtime correspondence |
| Execution-policy parse failure | Fixed summary `Error parsing rules; custom rules not applied.`, potentially free-text details and path/range | Stop; intended policies were not applied |
| Disabled project configuration | Constructs a summary including folder paths and disabled reasons; details/path/range null | Stop; do not expose the raw summary or trust the project to silence it |
| Configuration startup warnings | Forwards arbitrary source-generated summaries; these include requirements-constrained fallback and other load warnings | Stop; a requested value may have been replaced by a managed requirement |
| SQLite recovery | Fixed summary `Codex rebuilt its local database.`, details from recovery notice | Stop; establish state provenance before a fresh-review claim |
| Missing system bwrap | Exact fixed advisory above | Record only the specifically reviewed advisory; all separate isolation/admission checks remain required |
| User-namespace support warning | Fixed warning that native Linux sandbox needs access to create user namespaces | Stop; not equivalent to an absent helper |
| WSL1 warning | Fixed warning that WSL1 cannot create the required namespaces and advises WSL2 | Stop; not equivalent to an absent helper |

Sources: [app-server startup](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/app-server/src/lib.rs), originally accessed 2026-09-07, reinspected 2026-09-09; [core configuration constraints](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/core/src/config/mod.rs), originally accessed 2026-09-07, reinspected 2026-09-09; [bwrap warnings](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/sandboxing/src/bwrap.rs), accessed 2026-09-09. This table is a startup call-site classification, not a claim that every transitive warning string was enumerated.

## Minimal safe observability

Keep raw summary, details, paths, unknown keys, and native diagnostics in memory only, bounded by the existing frame bound and a tighter local warning bound. Persist a locally chosen category, validity booleans, presence/null booleans, and character/byte lengths. For a known constant, a fixed local summary label is safe; never forward a matched prefix's remainder. Do not hash native diagnostic text as a substitute for redaction. Preserve exact source pins and state whether a classification is observed or merely inferred. A malformed warning must still produce safe shape metadata and stop rather than copying the offending value into an exception.

For the narrow advisory, match the entire source constant and native null/omitted fields, not a substring or prefix. A category such as `native_system_bwrap_absent_bundled_fallback_advisory` is an observation label, not native verification or a model capability claim. Unknown categories and all consequential known categories stop before model use. Fake-child tests should cover exact advisory, extra details, altered summary, path/range additions, managed fallback, policy parse, malformed/oversized values, and a later warning after model admission.

An offline bounded classifier over an already existing run-local log might recover the family without a new native launch. App-server writes the warnings at error level after installing its optional SQLite log layer. Persistence is not established: the process was terminated after 0.412 seconds and the report did not preserve stderr. Absence in an existing log would not establish absence of a warning. No such log has been requested or read in this consultation. Any subsequent native correction run must preserve the failed attempt and remain within the already approved exact operation scope and remaining finite model-call budget.

## Source provenance

New source files were fetched from the official OpenAI Codex repository at exact commit `78c290807ce710180111df227df3b7a4fe845452`. Their Git blob hashes were checked against the nontruncated exact release tree. `FETCH_ERRORS.json` retains the one unsuccessful exploratory path request before the actual initialize-processor path was retrieved. `LICENSE` and `NOTICE` are unchanged copies from the existing exact-release source archive. Existing source artifacts and pinned controller/profile files were not edited.
