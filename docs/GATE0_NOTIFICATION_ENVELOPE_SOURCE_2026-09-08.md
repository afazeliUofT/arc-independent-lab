# Native notification envelope correction

Date: 2026-09-08. This is an engineering source diagnosis, not an independent scientific review or a live account observation.

The published post-login parser rejects a notification shape emitted by the exact installed Codex release. It allows only `method` and `params` at the top level. Codex app-server 0.151.0 at commit `78c290807ce710180111df227df3b7a4fe845452` wraps outgoing server notifications with the additional `emittedAtMs` field. The source proves this compatibility defect. Because the failed native notification was deliberately not retained, the source does **not** prove which field was present in the user's particular rejected message.

## Exact source chain

1. `ServerNotificationEnvelope` flattens the typed notification into the envelope and declares `emitted_at_ms: Option<i64>` with camel-case serialization. Its comments say current server versions populate this field, while absence supports older servers. `default` and `skip_serializing_if = Option::is_none` mean absent and null values can decode as no timestamp; the sender omits a `None` value. [Protocol envelope, lines 1958–1974](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/app-server-protocol/src/protocol/common.rs#L1958-L1974), accessed 2026-09-08.
2. Both ordinary notification send paths call `timestamped_server_notification`. That helper supplies `Some(...)`, converting the current Unix milliseconds into signed 64-bit form with zero as the conversion-error fallback. The adjacent source test explicitly serializes `method`, `params`, and `emittedAtMs` together. [Sender, lines 585–640 and 725–738; serialization test, lines 774–803](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/app-server/src/outgoing_message.rs), accessed 2026-09-08.
3. The transport's untagged `OutgoingMessage` enum serializes app-server notifications using that envelope. Successful responses contain `id` and `result`; errors contain `error` and `id`. There is no corresponding response timestamp field. [Outgoing transport types](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/app-server-transport/src/outgoing_message.rs), accessed 2026-09-08.
4. The shared transport serializer calls `serde_json::to_string` on the typed outgoing message; stdio appends a newline and writes those bytes. There is no second generic JSON-RPC wrapper inserted by stdio. [Transport serializer, lines 260 onward](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/app-server-transport/src/transport/mod.rs#L260), [stdio writer, lines 82 onward](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/app-server-transport/src/transport/stdio.rs#L82), accessed 2026-09-08.
5. The general RPC source explicitly says this protocol neither sends nor expects a `jsonrpc` version field. Its optional W3C `trace` field belongs to a **request**, not a response or this outgoing notification envelope. The generic `JSONRPCNotification` type contains only `method` and optional `params`; reading that type alone therefore misses the app-server's actual outgoing wrapper. [General RPC types, lines 1–2 and 44–79](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/app-server-protocol/src/rpc.rs), accessed 2026-09-08.

## Minimal supported change

Permit only the additional notification key `emittedAtMs`. If present and non-null, require Python `type(value) is int` and the signed 64-bit range `-(2**63) <= value < 2**63`. This rejects booleans, floats, strings, and integers outside the source type. Accept absent or null timestamps, matching the optional field. The native current sender supplies a nonnegative integer, but negativity alone is not invalid under the declared wire type.

Keep the existing notification method-string requirement, unknown-key rejection, refusal of all server requests, exact response-ID binding, duplicate-key rejection, result/error exclusivity, stream limits, deadlines, and process cleanup. Do not add a generic `jsonrpc` or `trace` exception and do not broaden response envelopes. Notifications remain counted and discarded without dispatching their methods or retaining their payload, method value, timestamp value, raw bytes, or hashes. A future failure may report only locally defined envelope-shape categories, never arbitrary key names or values.

The change corrects framing within the same finite metadata request sequence. It does not request another sign-in, expand credential or network permissions, authorize any model operation, or establish model entitlement, allowance, policy provenance, or independent reviewer readiness.

## Synthetic evidence and its limit

`evidence/GATE0_NOTIFICATION_ENVELOPE_SYNTHETIC_REPRO_2026-09-08.json` records a contained synthetic responder test. The original protocol was obtained from `git show HEAD:scripts/gate0_postlogin_protocol.py`, with SHA-256 `f26b0e7513f57fa521591c5991dcfd2f1f89cad9f5bd8861e3a3a2108a8a75fa`. No native Codex binary, network request, credential operation, or model turn was used. The existing synthetic fixture was changed only in memory to emit a notification carrying a signed 64-bit timestamp when `config/read` arrived.

The published parser stopped with `Invalid notification envelope` after sending `initialize` and `config/read`, with only the initialization response accepted. The in-memory candidate parser accepting the typed optional timestamp completed the same six metadata requests. Synthetic secret canaries stayed absent from each returned observation. Both synthetic subprocesses were reaped; neither raw stream was saved. This shows the source-derived shape is sufficient to cause and repair the framing stop in a controlled test. It is not a recovered trace of the user's failed message, and it does not establish that subsequent live requests will succeed.

Synthetic observation SHA-256: `069bb3e6484f54ca10dfc93137507cba279ac6b7419bdd9aaed94fc3446fa69b`.

## Preserved source evidence

`artifacts/GATE0_NOTIFICATION_ENVELOPE_SOURCE/20260908_001/MANIFEST.json` lists all six exact source files, source URLs and access dates, byte lengths, SHA-256 hashes, and upstream Git blob identifiers. Each source file was checked against its upstream blob identity. The Apache-2.0 `LICENSE` and `NOTICE` are included from the already verified archive. Source materialization removed a transport-added final newline only when the resulting bytes matched the pinned Git blob. No scientific packet or frozen review manifest was changed by this diagnosis.

Source manifest SHA-256: `68502be129cdc106299adfe01e14f34d66c38934ddb4f034e9a1ea3e64b1facf`.
