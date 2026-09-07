# Gate0 capability findings and next measured step

2026-09-07. Both requested JSON reports are now present and verified. This is an operational finding, not a scientific treatment or independent reviewer verdict.

The inputs are preserved unchanged under `artifacts/GATE0_CAPABILITY_INPUTS/20260907_001/`. The laptop report SHA-256 is `cc94e45fb4d4cef09a789c30b4b57db375a0e84a8772fbef6781968c58149c05`; the Narval report is `f53cee6616044ff947b239129a799ac618bd8a6b163169583ac6623f0d14f982`. Both match their earlier terminal receipts and the delivered inventory script hash. All 16 commands and 32 captured streams passed the exit-status, Base64, rendered-text, byte-length and digest checks. The complete receipt is `evidence/GATE0_CAPABILITY_INPUT_VERIFICATION_2026-09-07.json`, SHA-256 `6da38b2b47f6da6c5060f28bee745a4c85ab31538fac30566a776c208c51b559`.

## What is now observed

| Resource | Observation from the pinned report | What this permits us to decide |
|---|---|---|
| WSL CPU | 16 logical CPUs; affinity includes all 16 | Retain the agreed ceiling of 12 workers when the other programme runs; up to 16 otherwise, subject to actual workload profiling. Do not inspect that programme to decide contention. |
| WSL RAM | `MemTotal=32568972 kB`, about 31.06 GiB | Budget WSL processes against this exposed memory, not the Windows physical RAM total. Available memory is a timestamped snapshot, not reserved capacity. |
| Laptop runtime | Python 3.12.3, Git 2.43.0, Codex CLI 0.151.0 | A stdlib Python driver can test the installed command sandbox without installing packages or invoking a model. |
| Narval accounts | `def-rsadve_cpu`, `def-rsadve_gpu`; allowed QOS `normal` | Use the matching account when a CPU or GPU job is scientifically justified. The reported default-QOS field is blank. |
| Narval job bound | `MaxSubmitJobs=1000` for each displayed association | This is pending plus running jobs, not GPUs, concurrent training jobs, GPU-hours or remaining allocation. |
| Narval hardware metadata | Full A100 and MIG resource strings; CPU and GPU batch time bands extending to seven days | Plan beyond laptop VRAM where needed. Displayed resources and partition uptime do not establish idle capacity, job admission or throughput. |
| Narval storage at lab path | 19,343,605,760 free bytes, about 18.02 GiB | Do not assume this is personal quota or a safe budget for large weights. The final destination for large artifacts remains to be measured. |

The supplied setup document's earlier Windows GPU and physical-memory measurements remain useful historical observations; this new inventory did not rerun GPU checks or measure numerical package support. The WSL RAM observation agrees with the earlier documented WSL limit. No machine-wide memory or hibernate setting is changed.

The Narval field interpretation, resource hierarchy, source-access limits and future measurement concept are detailed in `evidence/GATE0_NARVAL_CAPABILITY_ANALYSIS_2026-09-07.md`. Blank caps are not unlimited access, partition node counts cannot be added across overlapping listings, and the login host's resources are not a compute allocation. See the primary [Slurm accounting field definitions](https://slurm.schedmd.com/sacctmgr.html) and [resource-limit hierarchy](https://slurm.schedmd.com/resource_limits.html), accessed 2026-09-07.

## Reviewer setup: measure the command boundary first

The actual CLI help exposes a named permission-profile selector for `codex sandbox`, including the option to retain managed requirements. It does not support blindly copying the older `codex sandbox linux` form. The selected test defines a new, uniquely named profile for that invocation only, then starts a fixed Python canary under it. Its policy grants minimal runtime reads and read access to one synthetic packet, with no network access and no writable roots. It changes no existing configuration file or managed control.

The driver first confirms that its synthetic files really are readable and writable without the proposed sandbox. It then tests allowed reads, denied sibling reads, a symlink to that sibling, several writes, subprocess inheritance and a loopback connection to its own verified listener. Its outside supervisor captures the command result and checks fixture bytes and directory entries. A failed launch cannot count as a successful denial. This is a falsifiable engineering check of a particular command boundary, not a prompt asking an agent to behave.

Official documentation describes permission profiles as controls for local commands; model service traffic, connectors and other tools have separate controls. Accordingly, a passing canary is necessary evidence for this proposed shell lane, and does not establish complete reviewer isolation. A later reviewer still needs a fresh context, restricted exposed tools, the frozen evidence and full methods, external hash verification, and an output channel the PI cannot fabricate. [Official permissions documentation](https://learn.chatgpt.com/docs/permissions), accessed 2026-09-07.

The new test is provided separately from any reviewer invocation. It contains no scientific inputs and never starts a model session. It makes no claim that Codex 0.151.0's sandbox has already been tested on this machine. The hosted runtime has no `codex` executable, so local validation must remain explicitly about the harness and its failure detection; the actual enforcement observation must come from the laptop.

Hosted harness validation found the expected violation when confinement was deliberately omitted, and did not treat a fabricated policy rejection or wrapper timeout as protection. Mocked cleanup retained partial output without an unbounded wait on detached pipes. The receipt is `evidence/GATE0_BOUNDARY_HARNESS_VALIDATION_2026-09-07.json`, SHA-256 `58f136c952bbcd636669d5f01777d0fa4c80427a0f9efda71d8d1ce036602b60`. All substituted-runner reports explicitly say `HARNESS_SIMULATION`; none measures the laptop's enforcement.

## Subscription metering remains a distinct question

The reports contain no authoritative allowance reading. Current official documentation advertises a rate-limit metadata method, but a pure read request is not a complete boundary around app-server startup: configured MCP processes can have their own startup activity. No app-server process or quota request has been launched by this programme. The bounded next command captures `codex doctor --help` to inspect any narrower advertised observation route, without running diagnostics or changing authentication. `evidence/GATE0_CODEX_METERING_SCOPE_2026-09-07.md` records the distinction. [Official app-server documentation](https://learn.chatgpt.com/docs/app-server), accessed 2026-09-07.

Even a later returned Codex quota bucket must be identified by its scope; it cannot silently stand for every hosted GPT-6 Astra use in this programme. There is no percentage estimate from time or local tokens. Unattended model use remains disabled.

## Resource and durability decision

No GPU treatment is selected merely because Narval is available. The present novelty questions are analytic and the remaining immediate dependency is reviewer enforcement. When measured design calls for hardware profiling, the first Narval bundle should fix a bounded device/software measurement, checkpoint protocol and output destination. It should use the observed GPU account and measure the allocated device before relying on its VRAM. The initial measurement ceiling is not a ceiling on the eventual scientific programme.

Small evidence packages already have a verified laptop-to-GitHub transfer path. That does not establish durable handling of large cluster outputs or resistance to a killed job. Before a large run, checkpoint data must leave job-local temporary storage at recoverable boundaries, receiving copies must be hash-verified, and the durable destination must be established. No claim about large-artifact durability is promoted by the small document transfers.

The two original inventory requests are complete. The next human action is one prepared publication-and-canary bundle under existing authorization. There is no repeated Phase 3 approval, new paper request, cluster submission, software installation or settings change in that bundle.
