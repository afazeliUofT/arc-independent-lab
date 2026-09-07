# Narval capability analysis — 2026-09-07

Status: bounded operational analysis of supplied evidence. This is shared-context consultation, not an independently enforced review. No job, model task, installation, settings change, or quota modification was performed. Hardware availability does not authorize a scientific treatment that has not passed the research gates.

## Evidence and integrity

The complete user-supplied `GATE0_CAPABILITY_SLURM_20260907T015414.435418Z.json` was read. Its SHA-256 is `f53cee6616044ff947b239129a799ac618bd8a6b163169583ac6623f0d14f982`, matching the earlier terminal receipt. Report creation: `2026-09-07T01:54:14.435459+00:00`; inventory script SHA-256: `e2ce2da1ff8a52b86264b9a237c03bfccc396642dcd901d9c1e23b9acde79145`.

All eight commands returned status `ok`, exit code `0`, and empty stderr. The base64, UTF-8, byte count, and SHA-256 of every captured stdout/stderr field were independently checked and agree. Association and QOS records were parsed using their actual requested field order and retain all empty fields. This establishes the supplied report's internal consistency, not independent observation of the cluster.

The report observes Python 3.11.4, Git 2.41.0, and Slurm command clients 25.11.8. It does not test any Python numerical package, CUDA execution, GPU driver, or compute-node software environment.

## Exact associations and limits

| Field | CPU association | GPU association |
| --- | --- | --- |
| Cluster | `narval` | `narval` |
| Account | `def-rsadve_cpu` | `def-rsadve_gpu` |
| User | `rsadve1` | `rsadve1` |
| Association partition | empty | empty |
| `DefaultQOS` | empty | empty |
| Allowed `QOS` | `normal` | `normal` |
| `MaxSubmitJobs` | `1000` | `1000` |
| `MaxJobs` | empty | empty |
| `GrpTRES`, `GrpTRESMins`, `GrpTRESRunMins` | all empty | all empty |
| `MaxTRES`, `MaxTRESMins`, `MaxWall` | all empty | all empty |

The association limit query requests exactly twelve fields. The trailing `1000` is the twelfth, **`MaxSubmitJobs`**, meaning the configured bound on pending plus running jobs in that association. It is not 1,000 concurrent running jobs, GPUs, GPU-hours, or credits. The `normal` QOS record has eleven fields: its name followed by ten empty requested flag/limit fields. An empty `DefaultQOS` is not a measured default of `normal`. [`sacctmgr` manual, accessed 2026-09-07](https://slurm.schedmd.com/sacctmgr.html).

Empty displayed caps are not a usable unlimited allocation. Job QOS, partition QOS, association hierarchy, group limits, and partition policy can affect scheduling. Ordinary `sacctmgr` association output can propagate parent limits—the query did not use `WOPLimits`—so it would also be incorrect to describe every displayed value as necessarily configured directly on the user. This inventory is not a full policy hierarchy or fair-share measurement. [`sacctmgr` manual, accessed 2026-09-07](https://slurm.schedmd.com/sacctmgr.html); [Slurm resource-limit hierarchy, accessed 2026-09-07](https://slurm.schedmd.com/resource_limits.html).

Decision: use the observed CPU and GPU association names for future CPU and GPU requests, respectively. Continue planning as default-tier access, without an assumed large award, remaining allowance, concurrency entitlement, or predicted queue delay. The report's account names are operational inputs; no other users' associations or job histories were examined.

## Displayed resource families

The `sinfo` format was `%P|%a|%l|%D|%c|%m|%G` with `--exact`. The memory field `%m` is configured memory in **MiB**, CPU count is per node, `%D` is a grouped node count, and `%G` describes configured generic resources. `%a=up` is partition state; it does not mean its nodes or GPUs are idle. No node-state, allocated/idle count, or used-GRES field was requested. [Slurm `sinfo` manual, accessed 2026-09-07](https://slurm.schedmd.com/sinfo.html).

| Displayed family | CPUs per node | Configured memory per node, MiB | GPU resource strings |
| --- | ---: | --- | --- |
| Base CPU | 64 | 256000 or 512000 | none |
| Large-memory CPU | 64 | 2057500 or 4115000 | none |
| Full A100 GPU, first host family | 48 | 510000 | `gpu:a100:4` |
| Full A100 GPU, second host family | 64 | 1024000 | `gpu:a100:4` |
| Partitioned A100 GPU | 48 | 510000 | `a100_1g.5gb`, `a100_2g.10gb`, `a100_3g.20gb`, `a100_4g.20gb` in several mixtures |

Both `bycore`/`bynode` CPU and `bygpu`/`bynode` GPU partition families display batch bands of 3 hours, 12 hours, 1 day, 3 days, and 7 days. Interactive partitions display 8 hours. CPU and GPU backfill partitions display 1 day. A further named CPU partition appears in the inventory, but its visibility is not evidence of a relevant account entitlement; it is not selected for this programme.

No node counts were summed across partitions. A physical resource can be exposed through several duration/access partitions; the inventory has no node names with which to deduplicate. Likewise, the multiple MIG instances are subdivisions and must not be counted as full physical GPUs.

The inventory itself gives the model label `a100`, not the full GPU memory capacity. Alliance's indexed GPU documentation identifies Narval's full A100 as 40 GB and its MIG profiles as smaller slices. Treat 40 GB as documentation-supported planning information; the allocated device's actual capacity still needs a compute-node measurement. Direct page retrieval was denied, as recorded below. [Alliance GPU documentation, indexed content accessed 2026-09-07](https://docs.alliancecan.ca/wiki/Using_GPUs_with_Slurm); [Alliance MIG documentation, indexed content accessed 2026-09-07](https://docs.alliancecan.ca/wiki/Multi-Instance_GPU).

The report's host-level 64 logical CPUs, approximately 251 GiB `MemTotal`, and approximately 143 GiB `MemAvailable` concern the current login host. They are not an allocation to this programme and must not set a training process's resource budget.

## Small next hardware measurement, when needed

A justified initial GPU capability measurement can request one full A100 on `def-rsadve_gpu`, one node, one task, 4 CPUs, 16 GiB host memory, and a 10-minute wall limit. This is a proposed request ceiling for a bounded device/software check, not a claim that the workload requires or can use that budget. It is also not a laptop-sized ceiling on the eventual scientific programme. Full treatment scale should follow observed per-case time, memory and storage, including the largest required case.

The intended Slurm resource directives are `--account=def-rsadve_gpu`, `--nodes=1`, `--ntasks=1`, `--cpus-per-task=4`, `--mem=16G`, `--gres=gpu:a100:1`, and `--time=00:10:00`. Leave the internal partition unspecified. The GPU syntax and omission of an explicit partition are supported by the available indexed Alliance guidance; no scheduler acceptance test has yet been performed. [Alliance GPU jobs, indexed content accessed 2026-09-07](https://docs.alliancecan.ca/wiki/Using_GPUs_with_Slurm); [Alliance job submission, indexed content accessed 2026-09-07](https://docs.alliancecan.ca/wiki/Running_jobs).

Do not submit an empty generic benchmark solely because a GPU is available. The eventual prepared bundle should first fix exactly which device/package/kernel measurements resolve a live planning uncertainty, how long they may run, what evidence they emit, and where the evidence survives. It must use the cluster software environment actually available, rather than guessing a CUDA or PyTorch installation. CPU-only checks can use the CPU association without reserving a GPU. No executable job was produced or submitted by this analysis.

PowerShell is the user's local SSH/SCP interface. After SSH login, commands and batch scripts execute under Linux on Narval. WSL is not required for submitting or retrieving Narval work. Batch submission should produce a recorded job ID; laptop sleep or a later SSH disconnect need not become an experiment's process supervisor. The job's own time limit, output handling, and failure states remain explicit.

## Durability before experimental runs

`lab_filesystem_bytes.free` is **19,343,605,760 bytes**, about **18.02 GiB** or **19.34 decimal GB**, measured at the laboratory path. Its `total` of 51,200,000,000 bytes is not identified by this probe as a user's storage quota. Do not describe these values as a measured 50 GB personal allowance or 20 GB that can safely be filled. No project/scratch capacity, quota, inode limit, or I/O performance was measured.

Alliance's indexed storage documentation says the job-local `$SLURM_TMPDIR` directory is deleted when a job ends. Its indexed scratch policy says files older than 60 days are periodically purged. The full policy details were not retrievable; do not infer precise age calculations, exemptions, warnings, or backup guarantees from these excerpts. [Alliance storage guidance, indexed content accessed 2026-09-07](https://docs.alliancecan.ca/wiki/Storage_and_file_management/en); [Alliance scratch purge policy, indexed content accessed 2026-09-07](https://docs.alliancecan.ca/wiki/Scratch_purging_policy).

The programme therefore needs two distinct operations: checkpoints must leave job-local temporary storage while a job is running, and finalized evidence must reach the user's canonical working copy and GitHub. A successful scratch copy alone does not meet the programme's durability rule. The job should write a bounded manifest with exact input/code hashes, parameters, timings, environment, output hashes, and explicit completion/failure status. Checkpoints must be written at recoverable boundaries; an exit trap cannot protect against every hard kill or node failure. Never delete the cluster copy before the receiving copy and repository publication are verified.

Small reports, state, traces and provenance belong in the existing GitHub checkpoint workflow. If a future experiment produces large weights or datasets, choose and verify their durable destination and retrieval receipts before launching it; do not assume ordinary Git is an appropriate bulk artifact store. Storage quotas and permissible project destination remain measured setup tasks, not excuses to cap the science at the laptop. This note does not provision or alter a destination.

## Remaining unknowns and source-access record

The report establishes readable scheduling metadata and two own associations. It does not establish successful job admission, actual allocated hardware, sustained throughput, memory requirements of a scientific workload, queue wait, fair-share position, effective group caps, storage quotas, durable artifact transfer, reviewer isolation, or any model subscription allowance. Those claims remain unset.

Direct web opens of the Alliance Narval, storage, allocations/scheduling, and GPU pages returned the following verbatim denial on 2026-09-07:

> Access Denied: error code b3728715388cb593.

The pages identified their protection as BotStopper. No access control was bypassed. Official indexed excerpts were usable only for the narrow facts explicitly labeled above. Full Slurm manual pages were readable and supplied the field and limit semantics. This access limitation is not a scientific paper request and does not require another human round trip for the conclusions made here.
