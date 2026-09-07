# Next reviewer boundary after the successful laptop command test

2026-09-07 UTC. Shared-workspace technical consultation, not independent review. No client, model, app-server, or doctor diagnostic was invoked. No configuration or programme state was changed.

The supplied v2 report is the required successful command-boundary observation. Its runtime is Codex CLI 0.151.0, executable SHA-256 `9739cbc928b9c573be83256acd46668f5dd4f119d2d09e05246895ca2aaf0c9a`. It does not establish a complete reviewer launch. The useful next step is to **assemble the complete offline review input and design one bounded full-client preflight**, rather than repeat the passing shell test or start a review prematurely.

## Work the PI can complete now

Build a fresh, separately manifested review directory from the union of `evidence/P3_AUDIT_REVIEW_MANIFEST.json` and `evidence/P3_RESIDUAL_REVIEW_MANIFEST.json`. Include both review instructions unchanged. Inventory the exact full-method source versions required by every reduction and provide legitimate already-accessible full texts in a private part of that directory. Keep copyrighted sources out of GitHub. List genuinely missing method dependencies in one batch; do not make the reviewer rediscover which source versions were actually read. This is substantive preparation that requires no further capability request.

Specify the externally owned launcher and output channel before asking the human to run anything: immutable input hashes checked before invocation; a fresh thread without PI conversation history; packet-only command reads; output captured by the parent process outside reviewer file-write reach; no continuation loop. A successful technical preflight must precede the scientific prompt. The exact invocation is not established by the evidence currently available, so this note deliberately supplies no guessed launch command.

## Narrow technical preflight to develop

Prefer the app-server protocol as the **candidate** next route because it exposes the required metadata and named permission-profile selection explicitly. Its documented `thread/start` can select a named `permissions` profile when experimental API support is enabled, and returns loaded `instructionSources`. It must not be mixed with legacy `sandbox` in the same request. The installed `exec --help` contains no `-P` option; copying the successful standalone `sandbox -P` flags into `exec` would therefore be unsupported. Source: [Codex App Server](https://learn.chatgpt.com/docs/app-server), accessed 2026-09-07; installed help in the archived laptop inventory.

Develop a finite two-stage preflight, with no model generation in either stage:

1. **Establish startup containment before connecting to account services.** Constrain the entire app-server process and its descendants, rather than only future shell tools, while keeping effective managed requirements in force. Inspect only allowlisted effective control fields and their origins through `config/read` and `configRequirements/read`; do not export raw configuration, identity, authentication, or arbitrary server output. Resolve exact startup dependencies from the installed version before supplying any path grants. An absent or unreadable managed layer is a failed preflight, not a clean default. A network-off launch can validate startup containment and configuration parsing, but cannot produce live quota information.
2. **Only once the startup boundary is established**, permit the narrow existing-subscription metadata lane: `initialize`, `initialized`, `account/rateLimits/read`, and `model/list`, with bounded time/output and rejection of unexpected requests. Retain returned bucket identifiers, windows, timestamps, available model identifiers and supported efforts. Do not create/resume a thread, start a turn, refresh/reset credits, run login, inspect account history, or fall back to a paid API. If account metadata is unavailable, retain the limitation and keep unattended use paused.

The preceding paragraph is an engineering acceptance specification, not a claim that a ready-to-run safe app-server wrapper exists. Complete and locally validate the wrapper's static checks and protocol handling before requesting one human run. In particular, the successful Python child test does not yet prove that a full Codex client can run inside that same outer profile with its own configuration and service dependencies.

## Why metering is still separate

The official interface returns named quota buckets, including a backward-compatible single-bucket view and a multi-bucket map. A generic `codex` bucket is not proof of the allowance remaining for this hosted GPT-6 Astra Ultra conversation. The actual model identifier, highest supported effort, subscription authentication, and consumption-bucket mapping remain to be observed. Source: [Codex App Server](https://learn.chatgpt.com/docs/app-server), accessed 2026-09-07.

The current report's `codex doctor --help` describes an installation/configuration/authentication/runtime diagnostic with `--json`; it offers no selective quota subcommand. Running the entire doctor now would not be a justified substitute. The previous app-server startup concern also remains: official documentation permits app-scoped MCP startup before any thread is created. Sending only read RPCs does not constrain that startup activity.

## Complete reviewer acceptance conditions

A future observed launch must additionally establish:

- Effective tool exposure: no enabled app/connector, MCP, browser/computer, plugin-provided, file-write, or collaborative escape route with effects outside the approved boundary. Disabled defaults alone are insufficient if specific overrides remain.
- Fresh input context: no resumed/forked PI conversation, unexpected instruction files, or memory injection. `instructionSources` is useful evidence, not proof about every possible context source.
- Actual enforcement for every retained tool route, including direct file operations and nested shell commands, plus externally checked input hashes.
- Full methods available within the allowed source boundary; otherwise the review may issue `SUSPEND_FOR_DEPENDENCY` rather than reason from abstracts.
- Model and subscription evidence sufficient for the requested reviewer mode; no automatic extension or unattended retry while allowance remains unknown.

Permission profiles restrict local command execution; they do not themselves restrict apps/MCP or other hosted tool traffic. Source: [Permissions](https://learn.chatgpt.com/docs/permissions), accessed 2026-09-07. The configuration reference separately exposes app integration, hook, memory and collaboration controls, per-server MCP enabling, and managed feature requirements. These controls must be checked as effective values, not assumed from a default. Source: [Configuration Reference](https://learn.chatgpt.com/docs/config-file/config-reference), accessed 2026-09-07.

Proceed with packet preparation and launcher development now. A further human machine run will ultimately be necessary because this hosted environment has no matching Codex executable or authenticated laptop session. It should be requested only after the complete next preflight is reviewable, and batched with the next natural publication checkpoint. No additional scientific approval is needed for that already-authorized preparation.
