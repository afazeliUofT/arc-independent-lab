# Existing-subscription route: exact Codex 0.151 source analysis

Date: 2026-09-07. This is an engineering consultation in the PI's shared workspace, not an independent scientific review. No client, login, network-enabled client, model turn, or account request was executed for this analysis.

## Decision

Use one bounded follow-up of the existing network-disabled, same-installation-ID startup observation. After `initialize` and the existing configuration requests, send exactly `account/read` with `{"refreshToken":false}`. Preserve only validated account-kind, recognized plan enum, and the boolean `requiresOpenaiAuth`; discard email and any unknown raw fields. Read the configured credential-store enum through the existing configuration response, without changing it.

This answers a precise question: **what account metadata is available to this contained client under the presently authorized mounts and environment?** It does not answer whether the host is logged in elsewhere, whether a hidden keyring credential exists, whether a subscription covers a particular model, whether a model's complete tool surface is confined, or how much allowance remains. Do not repeat the passing startup-only observation separately. Do not add a model thread, enable networking, expose the host session bus, copy credentials, change the credential backend, or initiate login as part of this follow-up.

This is the smallest supported next observation selected with the PI. Its value is to distinguish the contained client's actual account response from inference based on the absent `auth.json`. It is not a complete solution to authentication or reviewer isolation.

## Exact request and filtered response

The release's embedded experimental schema contains `v2/GetAccountParams.json` and `v2/GetAccountResponse.json`. The request field is `refreshToken`, a boolean; send it explicitly as false. The response requires `requiresOpenaiAuth`, a boolean. `account` may be absent or null. Recognized account types are `apiKey`, `chatgpt`, and `amazonBedrock`. A ChatGPT account also has `email` and `planType`; email must not enter a report.

The recognized plan strings in this exact release are:

`free`, `go`, `plus`, `pro`, `prolite`, `team`, `self_serve_business_prolite`, `self_serve_business_usage_based`, `business`, `ent26`, `enterprise_cbp_automation`, `enterprise_cbp_usage_based`, `enterprise`, `edu`, `edu_plus`, `edu_pro`, and `unknown`.

There is no `ultra` plan string in this schema. Do not map a returned enum to the funder's stated ChatGPT Ultra subscription by name similarity. Record observed account metadata, preserve the declared resource separately, and leave any entitlement discrepancy unresolved. An absent account member, null account, malformed account, and unrecognized enum are separate outcomes.

Schema provenance: the exact 0.151 exports already archived under `artifacts/GATE0_CODEX_INTERFACE/20260907_001/schemas/experimental.json`, whose containing manifest is SHA-256 `61a99383e034ddd892586125664fd67390225f0bbd6410a0447e706926b96147`. The upstream schema-export mechanism is [the pinned precomputed export source](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/app-server-protocol/src/precomputed_exports.rs), access date 2026-09-07; the local extracted schemas, rather than a current documentation example, control the exact field and enum assertions above.

## What refreshToken=false does and does not mean

The account handler calls `refresh_token_if_requested(false)`, which skips that explicit refresh, then loads the latest configuration and constructs a provider. For the ordinary OpenAI-compatible provider, `account_state()` reads `auth_cached()` synchronously; it does not itself make an account-metadata network request. A cached permanent refresh failure suppresses the reported account. Missing required ChatGPT account details can produce an error. Thus even a well-formed null account is a statement about this client's available cached account state, not a definitive statement about host login.

Configuration loading and the client lifecycle remain separate. Startup installs a cloud-config loader with a background refresh task; the models worker requests online model refresh. `AuthManager.auth()`, used by other paths, can proactively refresh stale credentials and persist the result. The absence of a model request does not make the complete app-server process network-inert or write-inert. The outer namespace and read-only mounts enforce the existing restriction; this follow-up must not relax them to make a request succeed.

Sources: [account handler](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/app-server/src/request_processors/account_processor.rs), [provider account state](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/model-provider/src/provider.rs), [auth manager](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/login/src/auth/manager.rs), [cloud loader](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/cloud-config/src/bundle_loader.rs), and [model refresh worker](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/app-server/src/models_refresh_worker.rs), all accessed 2026-09-07.

## Credential-store interpretation and access boundary

The implementation's `AuthCredentialsStoreMode` enum defaults to `File`. Its supported values are `file`, `keyring`, `auto`, and `ephemeral`. File storage uses `CODEX_HOME/auth.json`; keyring storage fails if unavailable; auto attempts keyring and falls back to file; ephemeral storage belongs to the current process. External in-memory credentials are checked before persistent storage. Configured login and workspace restrictions are retained by the bootstrap authentication configuration.

The user report says `auth.json` was absent and the configuration file existed. Its contents were not exposed. This does not establish the effective credential-store setting. The public config-response schema permits additional properties but does not explicitly declare `cli_auth_credentials_store`. The next filtered report must record whether that field is present and is one of the four recognized strings. If omitted, the source-level default remains a default, not a measured effective setting. Likewise, a `keyring` or `auto` result does not prove that a keyring is present, reachable, unlocked, or populated.

The keyring wrapper provides load, save, and delete methods against an OS credential service. Exposing an entire session-bus socket would grant an IPC endpoint; a read-only filesystem mount of a socket does not restrict the service's operations to read-only credential access. This analysis has not established an enforced per-secret, read-only keyring transport. Therefore do not mount the session bus or a broader runtime directory into the reviewer simply to recover authentication. Do not extract a credential into a file or change backend settings as a substitute.

Sources: [credential-store enum](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/config/src/types.rs), [authentication storage](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/login/src/auth/storage.rs), [bootstrap authentication settings](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/core/src/config/auth_keyring.rs), and [keyring interface](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/keyring-store/src/lib.rs), all accessed 2026-09-07. The socket-boundary conclusion is engineering inference from the exposed IPC capability, not an observed attack or a claim that this host uses that backend.

## Cloud requirements, model listing, and allowance are later observations

The exact cloud service first calls `auth_manager.auth()`. No available auth returns no bundle. Otherwise it fetches cloud configuration only for an auth route using the Codex backend and an eligible business-like, education-like, or Enterprise plan. Eligible accounts use an identity-matched cache when valid, with backend fetch and background refresh paths. Therefore a null requirements result in an unauthenticated or restricted namespace does not show that the host's applicable managed policy is absent. Keep managed-requirement verification false until the actual account route and applicable policy are established.

`model/list` uses `OnlineIfUncached`, so it can request metadata from the network; startup also launches an online refresh independently. The returned catalog can reflect bundled or cached model data and is not a measured model invocation or a complete tool-registry disclosure. It does not establish that the stated subscription can run the selected model at the desired effort under the required boundary.

`account/rateLimits/read` calls `AuthManager.auth()`, requires an auth route using the Codex backend, and fetches rate-limit snapshots plus reset-credit details. Its call path can refresh credentials. Merely fetching reset-credit details does not consume a reset; the implementation has a separate consume operation, which is outside the authorized no-spending programme. No allowance percentage can be filled in from these source facts. An eventual authenticated service response must be interpreted by its stated limit identifier, window, timestamp, and scope; a Codex-specific meter must not be represented as an authoritative meter for the hosted ChatGPT conversation without evidence.

Sources: [cloud service](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/cloud-config/src/service.rs), [cloud backend](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/cloud-config/src/backend.rs), [model-list conversion](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/app-server/src/models.rs), [account rate-limit handler](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/app-server/src/request_processors/account_processor.rs), and [separate reset-credit operations](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/app-server/src/request_processors/account_processor/rate_limit_resets.rs), all accessed 2026-09-07.

## Do not use a blind login instruction to repair an unknown state

The supported CLI has `login status`, browser login, and device-code login. However, a raw status command can print a formatted API-key fragment for an API-key account, and ordinary ChatGPT login clears existing authentication with a revoke attempt before starting the new login flow. These are material reasons not to instruct the funder to paste raw status output or to run login speculatively. No login, logout, account replacement, or backend migration is needed for the selected contained metadata observation.

If that observation later establishes that the authorized namespace lacks a usable subscription route, the next account setup must use a supported human sign-in procedure with its concrete side effects explained. That would be an account setup decision, not permission to copy credentials or loosen the reviewer's boundary.

Source: [exact CLI login implementation](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/cli/src/login.rs), accessed 2026-09-07.

## Archived evidence and limits

New licensed source archive: `artifacts/GATE0_SUBSCRIPTION_SOURCE/20260907_001/`. Its `MANIFEST.json` has SHA-256 `fb8be6505d401ad77e83ebe61b9e9888d9fb2de0f281aa245fc77e3652928270`. All 21 source/license files, totaling 397,875 bytes, match the exact upstream Git blob identifiers in commit `78c290807ce710180111df227df3b7a4fe845452`; LICENSE and NOTICE are included. Two initially materialized source files had one transport-added final LF, removed only after the resulting bytes matched the pinned upstream Git blob. Two guessed obsolete source paths returned 404; the complete exact tree then located the current login crate. A local source-table text patch failed because serialized object-key order differed; no patch was applied, and the complete source table was saved separately. These are recorded acquisition observations, not client-execution results.

The next report may establish contained account availability and typed configuration observations. It cannot independently authorize a scientific verdict, certify the model tool boundary, establish a subscription allowance, or lift the existing pause on unattended model use.
