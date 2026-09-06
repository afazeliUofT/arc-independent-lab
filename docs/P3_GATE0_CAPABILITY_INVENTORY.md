# Gate0: one bounded capability inventory

Run the inventory on the laptop and on an Alliance login host. Its purpose is to choose an implementable reviewer boundary and compute plan from observed capabilities. It requests no model response or new scientific approval. The resulting reports do not establish reviewer isolation, available allocation or subscription allowance.

The script is `scripts/gate0_capability_inventory.py`, SHA-256 `e2ce2da1ff8a52b86264b9a237c03bfccc396642dcd901d9c1e23b9acde79145`. It uses Python's standard library. Its only writes are new reports and temporary report files under `~/ARC_Independent_Lab/delivery/gate0_inventory/`. Prior reports are preserved. It does not install software, authenticate, edit settings, submit work or change Git. It reads no credential or configuration file itself. The internal file access of installed commands is not traced, so version/help execution is not claimed as an enforced isolation test.

## Laptop

After checkpoint007 installs the script, run in your WSL terminal:

```bash
python3 -u "$HOME/ARC_Independent_Lab/scripts/gate0_capability_inventory.py" --mode laptop
```

This records Python and Git versions; installed `codex` availability, version and help for the base command, `exec`, `review`, `sandbox` and `app-server`; and logical CPU count, CPU affinity, selected kernel memory counters and filesystem space at the lab path. It never starts a model session. Missing commands and counters are explicit unknowns. The CPU and memory observations describe WSL, which may differ from the Windows machine's physical resources. GPU execution and hibernate behavior remain unmeasured.

## Alliance

Use your existing SSH/MFA login to an Alliance cluster; no hostname or credential is requested here. In that login terminal, create only the project directory if needed:

```bash
mkdir -p "$HOME/ARC_Independent_Lab/scripts"
```

Using your normal file-transfer client, copy the same `gate0_capability_inventory.py` into that `scripts` directory. Then run on the login host:

```bash
python3 -u "$HOME/ARC_Independent_Lab/scripts/gate0_capability_inventory.py" --mode slurm
```

This records Slurm versions, visible partition metadata, associations filtered to the current Unix user, and limits for QOS names returned by that user's associations. It performs no job listing or job-history query. It does not inspect any other programme directory. The login host's CPU and memory are labelled separately from compute-node resources.

The partition columns are partition, availability, maximum job time, node count, CPUs per node, memory per node in MiB and configured generic resources. `--exact` avoids merging nodes with different reported configurations. These are reported capacities, not idle resources or an allocation promise. Field definitions were checked in the [official SchedMD sinfo manual source](https://github.com/SchedMD/slurm/blob/master/doc/man/man1/sinfo.1), accessed 2026-09-06.

Association and QOS queries report group resource caps, resource-minute caps, per-job and per-user caps, wall-time limits and job-count limits. QOS lookup is skipped if returned identifiers cannot be parsed safely; no broader query substitutes for it. The [official sacctmgr manual source](https://github.com/SchedMD/slurm/blob/master/doc/man/man1/sacctmgr.1), accessed 2026-09-06, defines these display fields. That source is labelled Slurm 26.11 development; the script records your installed version and preserves any unsupported-field error.

A blank limit is not a remaining balance or permission to assume unlimited use. Hierarchical account limits, QOS precedence and partition limits interact, and runtime resource availability is a separate matter. We retain default-tier assumptions until these observations and any required follow-up resolve the relevant bound. See [Slurm resource-limit hierarchy](https://slurm.schedmd.com/resource_limits.html), accessed 2026-09-06.

## Return both reports together

Each run prints `REPORT:` with its exact JSON path and `REPORT_SHA256:`. Download the cluster report through your normal file-transfer client and attach both JSON reports in one message. They remain outside ordinary committed content until their relevant metadata has been reviewed for public inclusion. Do not paste configuration files or credentials. A failed or unsupported query is useful evidence; do not install, authenticate or change settings to make this inventory pass.

Every subprocess has a timeout: local version/help calls allow at most 12 seconds, Slurm queries at most 30 seconds, with a 150-second shared command budget and bounded cleanup. The script names each probe before it runs. It saves exact stdout/stderr bytes as Base64, a readable rendering and hashes after each result, including nonzero exit codes and partial timeout output. It terminates only the process group it created. Detached descendants are not claimed to be contained. File I/O is not claimed to have a hard real-time deadline.

## How the observations will be used

Official current CLI documentation exposes read-only sandbox options and separate approval controls. Help output can show whether the installed client advertises them; it cannot prove they enforce the reviewer boundary. `--ephemeral` concerns persisted rollout files, not access to prior material. We will still need a separate contained enforcement test for permitted reads, forbidden reads/writes, shell access and connector access before calling any review independent. See [OpenAI developer commands](https://learn.chatgpt.com/docs/developer-commands?surface=cli) and [OpenAI sandbox documentation](https://learn.chatgpt.com/docs/sandboxing), both accessed 2026-09-06.

This inventory does not launch `/status`, `/usage`, a login flow or an API query. No authoritative subscription reading is produced. Unattended model use stays paused; elapsed time and local token counts will not be converted into a guessed allowance percentage. A displayed token counter or context-capacity figure would not alone supply the required allowance.

Contained checks cover the command lists and user/QOS filtering using fake clients, exact nonzero-byte capture, an owned-process timeout, symlink rejection and missing kernel counters. They establish the helper's limited behavior in those checks, not behavior on your laptop or cluster. Receipt: `evidence/P3_GATE0_CAPABILITY_INVENTORY_VERIFICATION.json`. One initial fixture failed because this hosted sandbox lacks `/proc/meminfo`; the corrected script records unavailable optional counters and continues independent probes. The original failure is preserved in `evidence/P3_GATE0_CAPABILITY_INVENTORY_ERRORS.jsonl`.
