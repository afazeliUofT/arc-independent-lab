# Smallest defensible route to the first independent review

2026-09-07 UTC. PI-side technical consultation in the shared workspace; not an independent review or an observed full-client launch. No client, model, login, doctor diagnostic, or service was started. This note leaves the frozen science and controls unchanged.

The objective is one independent scientific audit of the existing Phase 3 claims. The successful v2 command canary is sufficient to stop repeating that canary. The remaining work should produce a finite human-attended reviewer session, not an unattended research platform. Missing authoritative allowance telemetry continues to prohibit unattended model use; it does not require a hosted-conversation quota map before an already-authorized attended review.

## The next executable step

Prepare one bounded **installed-version schema export**. This is the missing interface fact needed to implement the reviewer without guessing settings or protocol fields.

The archived laptop inventory actually observed Codex CLI 0.151.0 and lists `app-server generate-json-schema`. The official documentation explicitly supplies `codex app-server generate-json-schema --out ./schemas` and identifies its output as version-specific. It separately describes starting the service with bare `codex app-server`. This supports choosing the schema subcommand as an offline interface probe; it is not proof about every internal startup action. [Codex App Server](https://learn.chatgpt.com/docs/app-server), accessed 2026-09-07.

The human-run wrapper should:

1. Reuse the successful exact-runtime identity checks, root-deny/minimal/exact-runtime profile and `--include-managed-config`. Keep network disabled. Add write permission only for a newly created project-contained schema output directory; no home, credential, release-directory, or other-programme grant. Keep captured report files outside the child-writable directory.
2. Run the exact pinned binary with `app-server generate-json-schema --help` inside that boundary. Require the observed help to advertise `--out` before invoking it. Record the help and its digest. If the help offers an experimental-schema inclusion option, use only its actually observed syntax; do not invent an option or presume the default schema includes experimental fields.
3. Invoke the documented schema subcommand with `--out` naming that fresh directory. Set finite process, output-byte and file-count limits. Supply no RPC messages, thread, prompt, login, account request, model request or service-start command. Reject nonregular files and paths escaping the directory; stop on timeout or missing dependencies without broadening access.
4. Preserve the exact exported JSON files, stdout/stderr and their hashes, exact command arguments, runtime identity before/after and the applied profile. An empty/invalid schema export is not success. A permission-related failure is useful dependency evidence, not permission to retry with a broader profile.

This step is supported now and can be bundled with the already prepared checkpoint evidence. It is not another general inventory. The hosted environment does not have the matching installed binary, so generating the authoritative local schema is a necessary human machine action.

Read the resulting schemas for actual `ThreadStartParams`, tool-call requests/results, named permissions, configuration/requirements responses, model selection and fresh-thread evidence. Presence in a schema establishes interface shape only. Effective settings, startup containment and retained tool enforcement still need observation before science is submitted.

## Why a tool-free paper review is insufficient

The original `03_AUTONOMY_SPEC.md` §5 C3 requires a separate process to inspect raw artifacts and rerun the verifier. Section 9 additionally requires its own hashing capability and an exclusive verdict-output path. A new conversation containing full text and PI-authored checksum receipts can provide a useful critique, but it cannot independently compute the hashes or rerun the verifier. Calling that the required reviewer would weaken the contract.

A minimal broker can satisfy these requirements without giving the reviewer a general write-capable shell. The reviewer would have narrow operations to read a manifested file/page, compute SHA-256 from its actual bytes, invoke the pinned verifier, and create its verdict in a predetermined verdict-only destination. The hash operation must recompute from bytes, not repeat a manifest entry. The verifier operation must run the frozen verifier rather than return a PI-produced result. The verdict operation must preserve the reviewer's output automatically, without PI selection or rewriting. This is a design proposal, not an implemented or measured boundary.

## Preferred finite review shape after schema inspection

Use one fresh app-server thread, driven by an external human-started wrapper with a strict request allowlist and finite duration. Prefer narrow broker tools over new general shell privileges. Keep the full source packet offline. Permit only existing-subscription inference traffic after startup and tool restrictions are established; never fall back to a paid API. The wrapper receives no PI conversation history, never resumes/forks a thread, and does not automatically start another review.

The documented app-server interface supports client-handled dynamic tool calls and returns loaded instruction paths. Named permission profiles and dynamic tools are experimental, making the installed schema important. These are useful building blocks; neither automatically disables the other built-in tools. [Codex App Server](https://learn.chatgpt.com/docs/app-server), accessed 2026-09-07.

The full launch must enforce, before a scientific prompt:

- Packet-only reads and verifier execution; the verifier's required temporary output, if any, is outside protected evidence and separately constrained.
- No active apps/connectors, MCP servers, plugins, browser/computer tools, collaboration, hooks, memory or automatic goals that create another context or effect route. A default setting is insufficient if a specific override can enable the capability.
- Readable, enforced managed requirements. Do not use `--ignore-rules`, repurpose `HOME`/`CODEX_HOME`, copy authentication into the packet, or remove a managed layer to obtain a clean-looking configuration.
- An external per-turn check of pinned inputs and controls, and an output path outside reviewer authority except for its narrow verdict operation.
- A fresh context with only the selected scientific instructions and manifested evidence. Instruction-file reporting is evidence about those files, not proof that every other source of context is absent.

Official configuration documents distinguish app/MCP controls from command-network permissions; command isolation therefore cannot certify connector isolation. They also expose hooks, memory, goals and collaboration settings. Inspect effective controls on the actual client, including restrictive managed sources, rather than rely on the existence of documented keys. [Configuration Reference](https://learn.chatgpt.com/docs/config-file/config-reference), accessed 2026-09-07; [Managed Configuration](https://learn.chatgpt.com/docs/enterprise/managed-configuration), accessed 2026-09-07.

The archived `exec --help` advertises `--ephemeral`, `--strict-config`, `--ignore-user-config` and legacy `--sandbox`, but does not advertise standalone `sandbox -P`. These flags do not establish all-tool containment. Merely adding `-P` to `exec`, or treating ephemeral operation as context isolation, is not a defensible shortcut.

## Remaining minimal machine facts

The schema probe should settle the installed protocol shapes and supported experimental export options in one run. Before the later attended launch, only these additional classes of fact remain essential: exact startup dependencies without broad grants; effective policy/tool/context controls; the existing subscription's available requested model and highest supported effort; and actual enforcement of the retained broker/output routes. Rate-limit telemetry may be collected narrowly when available, but unknown allowance must remain unknown and no automatic continuation may be enabled.

Full-method coverage is an independent scientific dependency and can advance in parallel. If a required method cannot be obtained, the reviewer must be able to issue `SUSPEND_FOR_DEPENDENCY`. No further scientific approval is required merely to prepare this authorized review. No formal verdict exists until the separate reviewer actually completes the required process.

## Local evidence consulted

- `artifacts/GATE0_CAPABILITY_INPUTS/20260907_001/GATE0_CAPABILITY_LAPTOP_20260907T014042.751426Z.json`, SHA-256 `cc94e45fb4d4cef09a789c30b4b57db375a0e84a8772fbef6781968c58149c05`.
- `artifacts/GATE0_BOUNDARY_OBSERVATIONS/20260907_002/REPORT.json`, SHA-256 `386d912567deb1e953faa851c8eaded5ca32e2edc516aad99aadae35bd162cfd`.
- `docs/GATE0_FULL_REVIEWER_PREFLIGHT_SCOPE.md`, `docs/P3_AUDIT_REVIEW_PACKET.md`, `docs/P3_RESIDUAL_REVIEW_SUPPLEMENT.md`, the supplied original autonomy contract and the recorded prior boundary failures.

The initial attempt to read the original contract from a guessed repository-root path failed with `cat: 03_AUTONOMY_SPEC.md: No such file or directory`. The supplied attachment path was then read. No boundary or schema probe was retried or executed in this consultation.

## Superseding implementation finding: no human schema run is needed

The recommendation above to request a laptop schema export was premature. We subsequently obtained the official release TAR, verified its published asset hash, reconstructed its binary in memory, and matched the exact laptop binary's size and SHA-256. The release-tag schema generator copies JSON strings from two embedded compressed data blobs. Both exact-tag blobs occur once in the complete matching binary. Decoding them as data establishes the version-matched interface without executing Codex. This removes the proposed human terminal action. It does not establish the eventual reviewer's effective permissions or fresh context.

The reproducible extractor is `scripts/extract_codex_interface.py`. Its public outputs are in `artifacts/GATE0_CODEX_INTERFACE/20260907_001/`: exact stable and experimental schema string maps, the compressed source blobs, the official configuration schema, exact-tag source files, release metadata, Apache 2.0 license and NOTICE, and a manifest recording every file plus every individual schema hash. The large release archive and an uncertified truncated intermediate binary remain outside Git.

An unconstrained executable shortcut was rejected for a concrete reason: generic `arg0` startup reads Codex's `.env` and creates/cleans helper directories before the CLI dispatch reaches the schema-only branch. The static data route invokes none of that code. [Exact release CLI dispatch](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/cli/src/main.rs), [exact release argument dispatcher](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/arg0/src/lib.rs), [exact release export implementation](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/app-server-protocol/src/precomputed_exports.rs), accessed 2026-09-07.

One saved intermediate binary was later shorter than the originally reported extraction stream. The cause is unestablished. Its negative embedded-blob search was invalid evidence about the full release binary; that inference is explicitly withdrawn. The certified extraction instead verifies the unchanged full archive and reconstructs the binary entirely in memory before matching the blobs. `evidence/GATE0_CODEX_INTERFACE_EXTRACTION_OBSERVATIONS.json` preserves the discrepancy and a separate missing-output-parent implementation error. Neither is a laptop boundary failure, and neither is evidence that the hosted storage problem has been diagnosed.
