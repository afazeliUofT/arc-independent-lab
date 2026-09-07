# Bounded client startup observation

2026-09-07. This is the next operational step toward a separate review of the Phase 3 novelty audit. It does not start a scientific review, approve an idea, train a mechanism, or use a model. The original research objective remains diagnosing and addressing knowledge acquisition, retention across discontinuities, and novel recombination; the next scientific decision is whether the component reductions and joint-specification criticism survive independent review.

## Run once after checkpoint012 is installed and published

Use WSL on the laptop, in a fresh terminal. Narval and PowerShell are not involved in this check.

```bash
python3 -I -B "$HOME/ARC_Independent_Lab/scripts/gate0_client_preflight.py" --run-preflight
```

The script first checks the exact installed binary, existing system bubblewrap, canonical project paths and the existing nonsecret installation identifier. It creates a fresh directory inside this project's `delivery/`. It then starts the existing app-server under direct bubblewrap confinement and sends only initialization, effective-configuration read, and requirements read requests. Network access is unshared before Codex starts. No thread or model-turn request, login, config-write request, scientific input, API key or quota operation is in the driver.

The child observation has a 60-second deadline plus bounded termination cleanup. Hashing before/after is additional local work. Individual child files have an 8 MiB limit and a polled aggregate runtime-tree limit is 64 MiB; polling is not an atomic disk quota. Runtime state/log writes are restricted to fresh project subdirectories. Namespace-only temporary files do not write to the host's temporary directory.

A valid, already mode0644 installation identifier is copied to a distinct project file and mounted at the same pathname inside the confined process. Its value is unchanged. The host original is outside every writable mount. Credentials are neither read by the parent nor copied; the existing runtime may read its explicitly mounted credential source. The parent preserves HOME and CODEX_HOME at launch. An existing runtime dotenv file can change non-CODEX variables inside the child, so post-dotenv environment identity is not certified. There is no outside-project setting change and no permission exception is requested.

The report prints its absolute path and SHA-256. Return **only that `REPORT.json`**. Runtime directories and the identifier backing file stay on the laptop. The report contains filtered control comparisons and path metadata, not raw configuration, credential values or raw client diagnostics. If the script stops before producing a report, return its printed STOP message. Do not install, repair, broaden permissions, or retry a different client version to force a pass.

## How the observation will be interpreted

`OBSERVED_STARTUP_AND_CONFIG_RESPONSES_ONLY` means the confined process answered the selected requests. It is expressly not certification of all tool routes, managed requirements, clean scientific context, subscription entitlement, model allowance or reviewer independence. A present or absent requirements object cannot establish that cloud requirements were verified while network access was disabled. Background metadata attempts can occur even though the driver sends no model request. No full reviewer or formal verdict is automatically started after the observation.

A missing system bubblewrap, changed runtime, noncanonical path, invalid identifier, denied startup dependency, unexpected server request, protocol error or ceiling stops the observation without a review. The original positive command canary remains valid for its own scope; this new check does not repeat it. The next engineering decision uses this exact report, not another general inventory.

Implementation validation: `artifacts/P3_REVIEW_BROKER_VALIDATION/20260907_003_aad8feb3/REPORT.json`, SHA-256 `f694367f848a1d58adcf0347152ed9f58e78d8a5f9123e9de990d26a15d68a45`. Final launcher source/fixture checks: `artifacts/GATE0_CLIENT_PREFLIGHT_HARNESS/20260907_001/REPORT.json`, SHA-256 `99ca15258e3fec7ccedfba254409358ae3a79f314bf61a3c815a3020aebf7a53`. These are synthetic local checks and a fixed historical arithmetic-auditor reexecution, not execution of the actual laptop client.

Exact source and the correction to the initial outside-write inference are in `docs/GATE0_REVIEWER_STARTUP_DESIGN_2026-09-07.md`. The source-supported private backing-file mount removes the previously supposed need for a host-write exception. The exact tool-registration limitations are in `docs/GATE0_REVIEWER_TOOL_BOUNDARY_SOURCE_2026-09-07.md`. Official source: [Codex installation identifier](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/core/src/installation_id.rs), [bubblewrap mount documentation](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/vendor/bubblewrap/bwrap.xml), and [app-server protocol](https://learn.chatgpt.com/docs/app-server), accessed 2026-09-07. Source is not substituted for the pending machine observation.
