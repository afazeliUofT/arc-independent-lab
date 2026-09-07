# Gate 0: scope of the available Codex metering interface

Date: 2026-09-07 UTC. Status: documentation and installed-help assessment;
**no live metadata measurement, model call, or independent review performed**.

## Decision

An automatic allowance reading remains unverified. The official app-server
interface contains a promising metadata route, but the evidence does not yet
establish a clean startup boundary for this installed client. Do not label an
app-server launch “pure read-only” merely because the client sends only read
methods. Do not infer a percentage from token counts or elapsed time. Unattended
model use remains paused under `03_AUTONOMY_SPEC.md` §7.

This finding does not require an extra human request now. Continue the already
prepared no-model sandbox capability probe and carry the metering dependency
into the subsequent measured client/reviewer setup. That batch can also
capture `codex doctor --help` to determine whether its advertised commands
offer a narrower metadata route; it must not invoke a doctor diagnostic.
Help output alone would not establish the behavior of an advertised command.
No metadata collector is delivered in this checkpoint.

## What the supplied inventory establishes

The attached laptop report has SHA-256
`cc94e45fb4d4cef09a789c30b4b57db375a0e84a8772fbef6781968c58149c05`.
It reports `codex-cli 0.151.0`; the version command exited 0. Its
`codex app-server --help` output, also exit 0, advertises `--stdio`, equivalent
to `--listen stdio://`, and separately advertises daemon and proxy commands.
The captured app-server help SHA-256 is
`95d290035d274e91e6f85b9af63e9a3fd2cf70a2295d9eedbfc23a2ee82d4383`.

That help does not advertise an option to ignore user configuration for
app-server. The separately captured `exec --help` does advertise
`--ignore-user-config`; that is not evidence the app-server accepts the flag.
Neither help output is an effective-configuration measurement or a trace of
startup file access and subprocesses. The inventory explicitly records that
client-internal file access was not traced.

## Documented metadata route

The current official guide specifies a stdio JSONL handshake, followed by
separate request methods for ChatGPT quota windows and the model catalog:

| Order | Message | Intended observation |
|---|---|---|
| 1 | `initialize` with client metadata | Protocol compatibility |
| 2 | `initialized` notification | Complete handshake |
| 3 | `account/rateLimits/read` | Returned quota buckets and windows |
| 4 | `model/list` | Returned model names and supported reasoning efforts |

Quota fields include `usedPercent`, `windowDurationMins`, and `resetsAt`;
`rateLimitsByLimitId` identifies multiple buckets when provided. The guide
also documents app-scoped MCP startup notifications, including a null
`threadId`. Its account reads therefore do not establish that startup is
free of integration activity. Source: [OpenAI, Codex App Server](https://learn.chatgpt.com/docs/app-server),
accessed 2026-09-07.

These are current documentation capabilities, not a successful observation
from the installed 0.151.0 process. A later measured result must preserve the
returned bucket identifiers and timestamps. A generic Codex bucket must not
be silently treated as the full allowance for this hosted GPT-6 Astra Ultra
conversation. A returned model name and effort option also do not prove a
successful invocation or establish which allowance bucket that invocation
would consume. The mapping remains a separate dependency.

## Why a four-message client is insufficient

Blocking outbound methods such as thread creation, turn start, login, credit
reset, or account history would constrain the collector's requests. Rejecting
unsolicited server requests would constrain what it authorizes in response.
Neither control prevents work that the server starts without asking the
collector first. This is a limitation of that proposed enforcement mechanism,
not evidence that this laptop actually ran a hook or MCP server.

Official hook documentation describes command and MCP hooks, lifecycle
events, and feature-level disabling. It also describes administrator-pinned
hooks that can remain enabled despite user choices. The configuration
reference documents per-server disabling and managed feature requirements.
Those mechanisms do not establish a complete startup-side-effect boundary
for an unmeasured configuration. Sources: [OpenAI, Hooks](https://learn.chatgpt.com/docs/hooks)
and [OpenAI, Configuration Reference](https://learn.chatgpt.com/docs/config-file/config-reference),
accessed 2026-09-07.

No user or credential files were inspected for this assessment. No
`HOME`/`CODEX_HOME` substitution, authentication copying, managed-control
override, login, or paid SDK/API route is proposed. The no-spending and
other-programme containment requirements continue to apply.

## Conditions for a later bounded measurement

First establish a client launch boundary that controls its startup behavior
and respects the installed managed requirements. Only then implement the
four-message metadata lane with a fixed request allowlist, finite timeout and
output bounds, fail-closed handling of unexpected server requests, and a
report schema that retains quota/model fields while excluding credentials,
identity and arbitrary server output. It must not create or resume a thread,
generate a model response, consume reset credits, or inspect usage history.

Record authentication errors, unsupported methods, null quota windows and
ambiguous bucket mappings as limitations. Successful fake-server protocol
tests would verify the collector's parsing and allowlist; they would not
verify real-client isolation, metering availability, subscription scope or
the user's model entitlement. The present assessment has run neither fake
protocol tests nor an actual app-server.
