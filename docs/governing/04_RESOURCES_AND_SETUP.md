# Resources and Setup

What you have, what you cannot reach directly, and how to ask for the rest.

---

## 1. The laptop

Measured with a read-only probe on 5 September 2026.

```
OS             Windows 11 Pro 25H2 (build 26200.9168), 64-bit
CPU            Intel Core Ultra 7 265H — 16 physical cores, 16 logical (no SMT), 2.2 GHz base
RAM            63.4 GB DDR5-6400
Disk           Samsung NVMe SSD — 1350 GB free of 1906 GB
GPU discrete   NVIDIA RTX PRO 1000 Blackwell Laptop — 8151 MiB VRAM, compute capability 12.0,
               driver 596.58, CUDA 13.2
GPU integrated Intel Arc Pro 140T

WSL2           Ubuntu 24.04.4 LTS, kernel 6.18.33.2, systemd enabled, user afazeli2006
               sees 16 cores, 31 GiB RAM, 8 GiB swap
               root filesystem 1007 GB, 895 GB available
               Python 3.12.3, pip 24.0, git 2.43.0, gcc 13.3.0, GNU Make 4.3
               nvidia-smi works inside WSL; CUDA driver libs at /usr/lib/wsl/lib
               MISSING in WSL: uv, node, npm, nvcc, torch
               apt available; DNS resolves; pypi.org and github.com reachable; no proxy

Power          Ultimate Performance; sleep disabled on AC and battery;
               hibernate after ~12.9 hours on AC
Security       Windows Defender real-time on; Controlled Folder Access off
```

**Your directory is `~/ARC_Independent_Lab/`.** Everything you create lives inside it.

You may use all of this — every core, the GPU, RAM, disk, overnight — subject to §2.

### 1.1 Four constraints that will shape your design

**`sudo` requires a password.** Verified. No unattended `apt install` is possible. Anything you
need must install into userspace — a project-local virtual environment, `pip --user`, or a
standalone binary. If a step needs a system package, that is a human escalation every time, which
breaks unattended operation. Design around it.

**Hibernate fires after about 12.9 hours on AC.** Sleep is disabled; hibernate is not. Any
unattended run longer than that dies mid-flight, and short jobs do not solve it because a new job
can start just before the machine-level timer expires. Disabling hibernation is a machine-wide
change outside your directory: propose the exact command with its effect and let Ali decide. Do
not assume a timeout of zero is sufficient — Windows documents adaptive behaviour at that setting.

**WSL sees 31 GiB, not 63 GB.** The default half-of-host cap. Raising it needs a `.wslconfig`
change, again outside your directory.

**The machine is shared.** Another programme runs long CPU-bound jobs on it — one to two hours of
wall-clock each, sometimes back to back overnight. Its work is CPU and model-call bound, so the
discrete GPU should be uncontended; the sixteen cores are not. Profile in a quiet window that Ali
confirms, measure a contention profile separately, and never substitute one for the other.

**The GPU is an accelerator to validate, not an assumption.** Compute capability 12.0 is new
enough that wheel support must be checked; there is no `nvcc` and no torch installed. If the
wheel route fails, the CPU programme continues and any claim that specifically needed the GPU
is narrowed, not quietly dropped.

---

## 2. The HPC cluster — available and encouraged

Ali holds a **Digital Research Alliance of Canada** account with GPU nodes (Narval, Rorqual,
Nibi; H100 and A100 class). This is real compute, free at point of use, and **you should use it
where it genuinely helps.** Do not silently design a laptop-sized programme because the cluster
is inconvenient to reach.

**You cannot reach it directly.** Access is SSH with multi-factor authentication into a SLURM
batch queue. No hosted assistant can hold that session. The loop is:

1. You write the code and the SLURM submission script, and commit them to the repository.
2. Ali pulls on the cluster, submits, and the job runs.
3. Results are pushed back to the repository, and **you read them yourself** — see §3.

**Constraints to design for, and to verify with Ali before depending on:**

- **Compute nodes typically have no internet.** Dependencies must be installed on a login node
  or shipped as a pre-built environment. A job that tries to `pip install` at runtime will fail.
- Jobs are queued, not immediate. Wall-clock limits are per-partition and a job exceeding its
  request is killed. Ask for what you need and checkpoint.
- The module system, not `apt`, supplies system software.
- Home, scratch and project filesystems have different quotas and retention. Scratch is purged.

**When to reach for it.** A grid that does not fit the laptop; anything needing real GPU memory;
embarrassingly parallel sweeps. **When not to.** Anything interactive, anything you need to
iterate on quickly, and anything small enough to run locally — the round trip through Ali costs
hours, so batch your cluster work rather than trickling it.

Raise the cluster at whatever phase it becomes useful. There is no gate you must pass first.

---

## 3. The repository, and how you read your own results

Ali will create a GitHub repository for this programme and give you read access, so that you can
inspect artifacts directly instead of having output pasted to you.

- Push after every verified step, as `03_AUTONOMY_SPEC.md` §11 requires.
- To read results — your own, or a cluster run's — **fetch the repository with your browsing
  tools** rather than asking Ali to paste them. Ask him to confirm the URL and access route at
  Gate 0.
- Never commit a credential, a virtual environment, or raw data you cannot license. Never rewrite
  history.
- **MIT-0 from the first commit.**

This channel is also how a cluster job's output reaches you: Ali pushes, you read.

---

## 4. Reading the other programme is forbidden

`~/ARC_AGI3_Plasticity_Lab/` and its public GitHub repository are off limits — see
`00_START_HERE.md` §6. This includes not searching GitHub for it, and not asking Ali what it
found. If you learn something accidentally, log a contamination event.

---

## 5. Asking for papers

**A standing channel, and Ali wants you to use it.** He has University of Toronto library access.
Do not build an argument on an abstract when the method section decides it, and do not treat a
paywalled paper as absent evidence.

**Batch your requests** — one message with several, not a trickle. Format:

```
PAPER REQUEST
1. Authors, year, title
   DOI or stable URL:
   Why I need it:            (one line)
   What depends on it:       (which bottleneck, candidate or novelty claim)
   What I need from it:      (whole paper / methods / a specific figure or equation)
   If unavailable:           (what I will do instead, and what that costs)
```

That last line matters: it tells Ali which requests are worth his time. Rank them if there are
many. Much of the archaeology literature in `02_RESEARCH_PROCESS.md` §1.6 predates open access,
so expect this channel to matter most during Phase 1.

---

## 6. Secrets

**Never in a message, never in shell history, never in a file you create, never in a commit.**

The earlier version of this pack contained a bootstrap that wrote a credential file into the home
directory. **That instruction is withdrawn** — it contradicted the stronger rule above and it sat
outside your directory. Use the runtime's supported credential management, without the agent
seeing or copying the secret. If the only available route requires a credential file or a change
outside your directory, **escalate the conflict rather than creating one.**

If you ever need Ali to confirm a credential is set, ask for its **length**, never its value:

```bash
echo "${#SOME_VARIABLE} characters"
```

If he had to log in somewhere to obtain a string, that string does not belong in a message.

---

## 7. Bootstrap, after approval

Idempotent, detects existing state, prints what it is doing. Python 3.12.3 and git are already
present and sufficient; `uv` is missing but not required, since a project-local virtual
environment works. Node and npm are absent and should not be assumed.

```bash
set -Eeuo pipefail
mkdir -p ~/ARC_Independent_Lab && cd ~/ARC_Independent_Lab
python3 -m venv .venv && . .venv/bin/activate
python3 -c "import sys; print('python', sys.version.split()[0])"
git init -q
mkdir -p state preregistration docs configs src tests scripts artifacts reports
```

Write the MIT-0 licence, a `.gitignore` excluding `.venv/` and any state file that could hold a
secret, and commit. Pin dependencies in a lockfile. No unattended `sudo`.

---

## 8. Measure before you commit

The most expensive mistake available to a programme like this is committing to a large grid on an
unmeasured per-unit cost.

Before any full experimental set: profile a **small, a typical and the largest permitted** case,
several repeats, on every materially different implementation. Record CPU time across
descendants — not just the immediate process — wall-clock, peak memory, output bytes, and GPU
utilisation where relevant. Then project the remaining grid from **the largest observed case
multiplied by a safety factor**, not from the median, and add the audit and rerun reserve.

If the projection exceeds the allowance: remove already-killed branches, apply measured
parallelism, or move the grid to the cluster. Do not quietly cut seeds, drop the nearest
comparator, or weaken a threshold.
