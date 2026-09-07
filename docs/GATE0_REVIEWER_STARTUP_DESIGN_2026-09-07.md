# Exact-version reviewer startup: decision and finite next step

2026-09-07 UTC. PI-side source investigation; no Codex client, model, service, login, API-key flow, configuration edit or outside-project write was executed. This is not an independent scientific review or an observed full-client boundary.

## Decision

The stock Codex 0.151.0 app-server cannot currently be advertised as runnable under a strict rule allowing writes only inside `~/ARC_Independent_Lab/`. Before it can accept the first JSON-RPC message, it unconditionally opens the real Codex installation identifier for writing. A read-only grant does not satisfy that open, even when the identifier is already valid. The ordinary `exec` command has the same dependency through its in-process app-server. This is an exact source-level incompatibility; another generic machine inventory or repeated passing command canary will not resolve it.

The recommended minimum exception, if the human elects to authorize one, is confined access to the **single existing nonsecret installation identifier file**, with its valid UUID and mode checked before launch, no parent-directory write grant, no authentication copy and no setting changes. Its exact canonical location must be measured from the existing runtime configuration, rather than assumed from a prompt. All bytes and metadata that could change must be checked afterwards. Such an exception still grants that file write capability; it must not be described as an enforced no-write boundary merely because the normal valid-UUID branch does not write its contents. If it is absent, invalid, a symlink, or not already mode 0644, this narrow existing-file exception does not authorize creating or repairing it.

This would resolve one known startup dependency only. It is not advance certification that no further dependency will be found or that a network-enabled scientific review is ready.

## Pinned source and observations

The investigated release commit is `78c290807ce710180111df227df3b7a4fe845452`, the source already matched to the actual 0.151.0 runtime in the interface extraction. New exact source copies, hashes and URLs are recorded in `artifacts/GATE0_CODEX_STARTUP/20260907_001/MANIFEST.json`. The Apache 2.0 LICENSE and NOTICE are retained with these source copies. Access date for every remote source below is 2026-09-07.

| Startup issue | Exact source finding | Consequence |
|---|---|---|
| Generic argument dispatch | Normal startup reads Codex's `.env`, then attempts helper directory creation and stale-directory cleanup beneath Codex home. Failure to prepare aliases explicitly prints a warning and continues with no alias guard; helper paths can fall back to the exact executable. | Deny helper-directory writes in the outer process boundary. No `HOME`/`CODEX_HOME` reassignment is needed to get past this particular attempt. Its actual warning must remain evidence. |
| Installed identity | `resolve_installation_id` calls `create_dir_all(codex_home)`, opens `installation_id` with read/write/create, locks it, normalizes its mode to 0644 if needed, and returns an existing valid UUID or writes a new one. The open requires write access even in the unchanged valid-file branch. App-server calls it unconditionally with error propagation before stdio initialization. | An exact read-only file grant is insufficient. No installation-identifier path override exists in the pinned config schema or this call. |
| Ordinary exec alternative | `exec` starts `InProcessAppServerClient`, which delegates to `app_server::in_process::start`; that startup also calls the same identifier resolver with error propagation. Its constructed thread parameters do not expose an external dynamic-tool broker or explicit empty environment list as CLI switches. | Switching to `exec --ephemeral` neither avoids the identifier dependency nor automatically implements the required broker boundary. |
| SQLite | App-server initializes the state database before JSON-RPC initialization. The exact config schema provides `sqlite_home`. | Supply a fresh lab-contained state directory using a CLI override; do not reuse the existing conversation database. |
| Other logs/history | Config schema provides `log_dir`, `history.persistence = "none"`, and memory controls. | Route supported runtime logging to a fresh lab-contained directory, disable history persistence/memory generation, and retain OS denial for unredirected writes. These overrides do not relocate the installation identifier, model cache, helper paths or authentication. |
| Invalid configuration | Without `--strict-config`, app-server can load defaults after an error. Its earlier cloud-loader preload catches many errors and warns even before the later strict load. | Require `app-server --strict-config`; reject preload/default-fallback warnings and missing managed-layer evidence. Strict parsing alone does not prove cloud requirements were loaded. |
| Hidden policy files | The loader treats `NotFound` as absence for config and requirements, whereas other read errors propagate. Root-deny mounts can hide an existing file as `ENOENT`. | Parent observation of the actual policy/config origins must establish existence/readability, and the confined process must see those same sources. A null `requirements` response alone cannot certify absence. |
| Plugin startup | The CLI selects runtime defaults that start plugin warmups. The manager's startup block is gated by effective `features.plugins`; remote-plugin handling has its own control. There is no CLI `PluginStartupTasks::Skip` flag. | Set restrictive overrides before process startup and inspect effective results, retaining managed requirements. Do not rely on a later thread-level empty environment list to prevent pre-thread plugins. |
| Background network | MessageProcessor unconditionally spawns a models refresh worker. Its first loop immediately calls `list_models(Online)`; the model manager fetches when a Codex backend or command authentication is active. | An initialize/config-only RPC script is not a promise of metadata-only network behavior. The first real preflight requires outer network denial before execution. |
| Remote control | The exact release contains an internal daemon marker `CODEX_INTERNAL_APP_SERVER_REMOTE_CONTROL_DISABLED=1`, consumed before worker threads, selecting `DisabledEphemeral`. | This is a version-pinned internal interface, not a documented public CLI flag. It restricts persisted remote control without changing settings; it is not a replacement for outer network denial. |

Sources: [argument dispatcher](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/arg0/src/lib.rs), [identifier resolver](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/core/src/installation_id.rs), [app-server startup](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/app-server/src/lib.rs), [exec implementation](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/exec/src/lib.rs), [in-process startup](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/app-server/src/in_process.rs), [config loader](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/config/src/loader/mod.rs), [plugin manager](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/core-plugins/src/manager.rs), [message processor](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/app-server/src/message_processor.rs), [models refresh worker](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/app-server/src/models_refresh_worker.rs), [models manager](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/models-manager/src/manager.rs), [remote-control transport](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/app-server-transport/src/transport/remote_control/mod.rs), all accessed 2026-09-07.

## Candidate no-model invocation and protocol

This is an implementation specification, **not a command to run before resolving the dependency above**. The controlling parent starts the pinned executable only after an OS boundary covers its entire startup and descendants. Reusing the successful command canary's underlying launcher must account for the launcher's own generic pre-dispatch actions; putting only the eventual child under `sandbox -P` does not retroactively confine its parent's earlier startup.

The source supports the inner argument vector:

```text
<exact-runtime> -c sqlite_home="<fresh-lab-state>" -c log_dir="<fresh-lab-log>"
  -c history.persistence="none"
  -c features.plugins=false -c features.remote_plugin=false
  -c features.apps=false -c features.memories=false
  -c memories.generate_memories=false -c memories.use_memories=false
  -c web_search="disabled"
  app-server --strict-config --stdio
```

Here each `-c` value is one argument containing TOML syntax; this multiline display is deliberately not a copy-and-paste shell command. The parent's implementation must add the complete source-verified tool/context disable set, including the exact orchestrator controls identified in the parallel tool-boundary trace, and validate all override values against the embedded schema. The short vector above documents supported startup choices; it does not claim to disable every tool route.

The parent preserves the existing `HOME` and `CODEX_HOME` values. It neither clones authentication nor substitutes policy files. Supported `sqlite_home` and `log_dir` overrides point to separate fresh project directories. Outer root denial permits only minimal runtime files, the pinned executable, the specifically observed policy/config/service dependencies, the read-only synthetic packet, and the stated runtime write locations. No full-home, entire release-directory, protected evidence or other-programme grant is acceptable. Network is disabled. A missing required dependency stops the attempt; permission expansion is not an automatic retry.

Only these messages are sent in the first stage, sequentially with bounded output and time:

```json
{"id":1,"method":"initialize","params":{"clientInfo":{"name":"arc_reviewer_preflight","version":"1"},"capabilities":{"experimentalApi":true,"extensions":{}}}}
{"method":"initialized","params":{}}
{"id":2,"method":"config/read","params":{"cwd":"<fresh-lab-synthetic-packet>","includeLayers":true}}
{"id":3,"method":"configRequirements/read","params":{}}
```

The parent waits for each response, checks identifiers and method shapes, and rejects unexpected server requests. It sends no thread creation, prompt, login, configuration mutation, quota-reset, model turn, resume/fork or account request. It records only allowlisted effective controls and their origins; raw configuration and authentication material are not transcript output. A final network-enabled model/allowance read and scientific thread remain separate steps.

The embedded schemas establish these message shapes. Current official documentation independently describes initialization, configuration reads and managed requirements, but does not prove the actual laptop's effective policy or isolation. [App-server documentation](https://learn.chatgpt.com/docs/app-server), [managed configuration](https://learn.chatgpt.com/docs/enterprise/managed-configuration), accessed 2026-09-07.

## Exact unresolved conditions

1. The single installation-identifier write-capability dependency requires a narrowly scoped human exception under the original containment contract, unless a later supported client release changes the startup path. No request to change the whole laptop configuration, copy credentials, patch the Codex binary, or remap Codex home is justified.
2. The full-client outer launch boundary must cover pre-argument-dispatch work. The direct helper dispatch below supplies a source-supported candidate without generic startup; its exact generated profile, launcher dependencies, and temporary bookkeeping still require bounded validation. A standalone sandbox subcommand that runs its own unconstrained generic startup is not that proof.
3. Exact existing policy/config/auth runtime reads must be mounted without converting hidden managed sources into apparent absence. Enforced requirements and effective tool controls must be observed before any scientific context is sent.
4. A later network-enabled client will perform background service activity in addition to explicit RPCs. Restrict and verify that lane before describing an existing-subscription review as bounded.

The useful next implementation is the broker/protocol preparation and its synthetic enforcement checks, followed by one concrete human-executable bundle once the above dependency is resolved. Do not repeat broad inventories or the already passing v2 command canary.

## Retrieval correction record

Five initial guessed source paths returned GitHub API 404 responses: `codex-rs/core/src/features.rs`, `codex-rs/app-server/src/config_api.rs`, `codex-rs/app-server/src/request_processors/plugin.rs`, `codex-rs/app-server/src/request_processors/config.rs`, and `codex-rs/environments/src/manager.rs`. The exact release tree was then queried and the matching actual source locations used. These failures establish only incorrect guessed paths, not missing capabilities. The exact error strings are preserved in the source manifest.

A provisional message listed Codex-home `managed_config.toml` among WSL default origins. Exact `layer_io.rs` corrects this: on Unix the default legacy managed path is `/etc/codex/managed_config.toml`. The document above uses that corrected source behavior. Sources of configuration selected by the actual installation still require observation.

## Source-supported outer helper route

The exact argument dispatcher recognizes an executable argument-zero basename of `codex-linux-sandbox` **before** dotenv loading or alias creation and enters the Linux helper, which never returns to generic startup. Python's `subprocess.Popen(executable=exact_runtime, args=["codex-linux-sandbox", ...])` can select this branch without changing the binary, creating a home-directory alias or rebuilding Codex. The helper's actual argument shape is:

```text
argv[0] = codex-linux-sandbox
--sandbox-policy-cwd <canonical-synthetic-packet>
--command-cwd <canonical-synthetic-packet>
--permission-profile <serialized-canonical-PermissionProfile-JSON>
-- <exact-runtime> <inner-app-server-arguments>
```

This is the exact release's hidden internal helper interface, not a public `-P` profile name. It does not itself load named profiles or managed configuration. The parent must build a restrictive canonical profile and preserve the actual app-server managed configuration inside it. It must not substitute an unchecked hand-authored broad profile for managed rules.

The helper uses the separate system `bwrap` executable found on PATH after probing its capabilities, or an adjacent bundled `bwrap` resource with its configured digest check. Setting argv[0] to `bwrap` does **not** dispatch an embedded bubblewrap implementation. The actually selected executable and its capabilities must be observed. A bwrap supporting `--argv0` re-enters the exact Codex binary as the inner helper. A legacy bwrap falls back to executing the helper's current argv[0] string, so a bare synthetic name can fail there; do not silently fall back to an unconfined client. A real lab-contained alias would be a separate concrete implementation choice only if required and correctly pinned.

The helper directly execs bwrap without synthetic-mount registry bookkeeping when both its synthetic-mount and protected-create target arrays are empty. Otherwise it creates and locks `std::env::temp_dir()/codex-bwrap-synthetic-mount-targets-<uid>` and manages target markers. A candidate must therefore either prove the chosen existing-root profile yields empty arrays or provide explicitly justified lab-contained temporary routing; it cannot claim “no outside writes” while silently using a host `/tmp` registry. The source does not require granting writes to `~/.codex/tmp` for this direct-helper route.

This closes the particular generic-arg0 architectural issue at the source-design level. It does not remove the real app-server `installation_id` dependency or establish an actual runtime boundary. Sources: [Linux helper parsing and dispatch](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/linux-sandbox/src/linux_run_main.rs), [bwrap launcher](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/linux-sandbox/src/launcher.rs), [bundled resource verification](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/linux-sandbox/src/bundled_bwrap.rs), [filesystem mount construction](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/linux-sandbox/src/bwrap.rs), accessed 2026-09-07.

The startup source archive contains 26 source files plus LICENSE and NOTICE, with every newly fetched source file's Git blob SHA-1 checked against the exact release tree and its SHA-256 measured. Its manifest SHA-256 is `cb07a7b4417254f1768c6995a8839c941b0bfbe86eaf076d7513b7f893a42913`.

One targeted search also used an incorrect local script path and returned `rg: scripts/gate0_reviewer_command_boundary.py: IO error for operation on scripts/gate0_reviewer_command_boundary.py: No such file or directory (os error 2)`. No inference depended on that search and no script was run.

## CORRECTION: a host-write exception is not established as necessary

The earlier recommendation that a human exception was necessary for the existing installation identifier was too strong. That conclusion assumed a permission profile with identical source and destination paths. **I withdraw the necessity claim.** A separate direct bubblewrap namespace can bind a private lab-backed copy of the **same existing identifier bytes** onto the client's original identifier pathname. The client can then perform its required read/write open against the private backing file while the real host file remains outside all writable mounts. This changes neither `HOME` nor `CODEX_HOME`, copies no authentication, and must preserve the exact original configuration and managed-policy sources.

This is ordinary filesystem containment using the vendored bubblewrap manual's supported `--bind SRC DEST`. Codex's canonical profile builder emits same-path binds and has no backing-map setting; the alternative therefore uses an explicit outer bubblewrap plan, not an invented Codex configuration field. The existing identifier must be regular, nonsymlink, valid, and already mode 0644. The private copy must be a distinct inode, never a hard link, and must have the same bytes. No host creation or repair is authorized if those preconditions fail. The parent must keep the copied identifier out of public artifacts and scientific prompts.

The source uses this identifier in Responses metadata and in remote-control enrollment and refresh requests. Those requests receive authentication separately. This supports treating the file as installation metadata rather than an authentication credential, but does **not** establish that a changed identifier would have no backend security, rate-limit or device-identity consequences. For that reason this route preserves the same existing identifier. A fresh UUID is not the recommended default, and no identity rotation is used to obtain service access. [Responses metadata](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/core/src/responses_metadata.rs), [remote-control request construction](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/app-server-transport/src/transport/remote_control/server_api.rs), [vendored bubblewrap manual](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/vendor/bubblewrap/bwrap.xml), accessed 2026-09-07.

The implemented **planning helper only**, `scripts/gate0_client_mount_plan.py`, accepts the pinned runtime, actual existing home/config locations, a fresh lab run root, exact read-only dependencies, separate runtime write directories, and the already verified private identity copy. It emits a direct bubblewrap argument vector starting from an empty filesystem namespace, with network isolation, exact read-only mounts, the fresh run mounted read-only, explicit runtime write carveouts, and the single source-to-different-destination identity bind. Fresh `/proc`, `/dev` and namespace-only `/tmp` are created; the namespace root is remounted read-only. It never binds the host root or home directory and never executes a process, reads file contents, sets environment variables, clones auth, or edits configuration. It rejects symlinked sensitive origins, host-ID hard links, broad home/config directory grants and writable overlap with protected inputs. Standard explicitly selected system aliases such as `/lib -> /usr/lib` may be mounted read-only at their original spelling.

Twelve topology tests in `scripts/test_gate0_client_mount_plan.py` passed using synthetic directories and fake executable files that were never executed. These establish the planner's validation behavior and emitted topology, **not** actual bubblewrap enforcement. The parent implementation still owns original UUID validation, private-copy creation, exact runtime and bubblewrap identity, actual config-source preservation, environment scrubbing, bounded protocol messages, and before/after host-file checks. No identifier was copied from a real user installation during this source investigation or test run. No client, model, account request, service or configuration mutation was invoked.

The additional exact-release metadata and bubblewrap sources are in `artifacts/GATE0_CODEX_STARTUP/20260907_002/MANIFEST.json`, SHA-256 `0a8cb9c8a652a78c2f0a9eec13e3b5279019a8a1daf48af7b4db1d43527e07c1`. The source's vendor `LICENSE` is a seven-byte symlink blob; a content fetch returned its referent and failed the blob match with `Blob mismatch codex-rs/vendor/bubblewrap/LICENSE`. The verified regular `COPYING` file is retained instead, and the manifest records that correction. Current-branch code search was used only to discover source filenames; every cited source was fetched and blob-verified at the exact release commit.
