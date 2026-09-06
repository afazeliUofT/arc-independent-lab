# Autonomy Specification — the operating contract

**This specifies a contract, not an implementation.** Section 8 is where you determine what your
own runtime can actually do, and implement the contract with it.

Where this document reports something as measured, it was measured by a previous autonomous
programme running on this same machine. That programme's *science* is deliberately withheld from
you (`00_START_HERE.md` §2); its *engineering* is not, because repeating those failures would
cost Ali money and buy you nothing.

---

## 0. How this contract applies across the three phases

`02_RESEARCH_PROCESS.md` defines three phases. This contract applies from your first action, but
not every clause bites in every phase.

- **Phases 1 and 2 produce no measurements**, so pre-registration, verifiers, pinned hashes and
  reviewer verdicts on results have nothing to act on yet. The state files, the ledger, the turn
  protocol, the escalation channel and the budget governor all apply from the start.
- **Phase 3 onward** brings the full anti-self-deception apparatus in §5 into force.
- A phase deliverable awaiting Ali's approval is a **human escalation**, reason 13, not a
  no-progress condition.

## 1. The premise everything else follows from

**You will lose your memory.** Context compaction, session restarts and machine reboots will all
happen over a multi-week run. Anything not written to disk did not happen.

The rule that follows: **write state before you think, not after.** The single most common cause
of long-run agent failure is a plan that lived only in the conversation.

Two corollaries:

- **The conversation is disposable.** Any turn must be resumable by a fresh instance of you,
  with no memory, reading only the state files.
- **A "memory" or "notes" feature in your runtime is not a substitute.** It is a convenience
  inside one session. This contract requires state that survives the process dying.

---

## 2. State on disk — four files

### `state/PROJECT_STATE.json` — the single source of truth

Read it first every turn. Write it last. Never let it disagree with reality.

```json
{
  "schema_version": 1,
  "updated_utc": "2026-09-06T14:03:11Z",
  "current_gate": "G3",
  "gate_status": "in_progress",
  "gate_entered_utc": "2026-09-05T09:12:00Z",
  "last_verified_gate": "G2",
  "last_verified_commit": "a1b2c3d",
  "active_task": {
    "id": "G3.4",
    "description": "Backtest verifier rejects injected wrong models",
    "attempt": 2,
    "escalation_level": 1,
    "started_utc": "2026-09-06T11:40:00Z"
  },
  "blocked_on": null,
  "next_action": "Concrete instruction a fresh session with no memory could execute",
  "open_questions": [],
  "mechanisms": {},
  "consecutive_no_progress_turns": 0,
  "route_history": ["G0", "G1", "G2", "G3"]
}
```

`gate_status` ∈ `not_started`, `in_progress`, `awaiting_verdict`, `passed`, `failed`, `blocked`,
`skipped`.

### `state/LEDGER.jsonl` — append-only, never edited, never truncated

One JSON object per line. This is your episodic memory and the thing that lets a future session
learn from a past failure instead of repeating it.

Required fields: `ts`, `gate`, `task`, `event`, `summary`. `event` ∈ `plan`, `attempt`,
`success`, `failure`, `decision`, `verdict`, `escalation`, `route_change`, `literature`,
`human_escalation`, `contamination`. Every `failure` carries `evidence` (artifact paths) and,
once known, a `hypothesis`. Every `success` carries the artifacts that prove it.

**Before starting any task, search the ledger for prior failures with the same kind or task
prefix. Repeating a documented failure is itself a failure.**

### `state/BUDGET.json` — the governor

Read every turn. Breaching a ceiling is an escalation, not a judgement call. Carries at minimum:
programme end date, maximum turns total and per gate, maximum attempts per task, default
experiment wall-clock, and the effort policy by task type.

### `state/ESCALATION.md` — empty unless you are blocked on a human

**This is the mechanism that makes the door two-way, and it must be exactly this explicit.** You
write the question into this file. **The human answers by appending a section beginning
`## ANSWER` to the same file.** Nothing else counts — not a chat message, not a verbal reply, not
an edit elsewhere. Your block check is literally *"does `state/ESCALATION.md` contain a line
beginning `## ANSWER`?"*

On yes: move the file to `state/escalations/<timestamp>.md`, clear `blocked_on`, append a
`decision` ledger entry recording the answer, resume.

**State this instruction inside the escalation text itself, every single time.** A human reading
an escalation three days later does not remember the protocol. On the previous programme,
several escalations were answered correctly only because the file said where to put the answer.

---

## 3. The turn protocol

Every turn, in this order, without exception.

1. **Orient.** Read `PROJECT_STATE.json`, the last 30 ledger lines, `BUDGET.json`. If
   `blocked_on` is non-null, do nothing but check whether the block cleared.
2. **Verify the world matches the state.** `git status --porcelain` plus your own state
   verifier. If the repository and the state file disagree, reconciling them is the entire turn.
   Never build on an inconsistent foundation.
3. **Recall.** Search the ledger for prior attempts at this task or failure kind. If a prior
   attempt failed, either apply what was learned or record why it does not apply. You may not
   silently retry.
4. **Act.** Exactly one advancing step — one thing that is independently verifiable. A module
   written and its tests passing. An experiment configured and run. Not "implement mechanism 1".
5. **Verify.** Run the checks the step warrants. Never mark something done on the basis of your
   own summary of it.
6. **Record.** Append to the ledger. Update `PROJECT_STATE.json`. Commit, with a message naming
   the gate and task.
7. **Decide the next action.** Write it into `next_action` as an instruction a fresh session with
   no memory could execute.

**No-progress counting.** A turn that ends without the ledger growing and without a commit made
no progress; increment the counter. At 3, escalate to L4. At 5, stop and escalate to the human.

Two counter rules that matter as much as the threshold, both learned expensively:

- **Any turn that lands a commit resets the counter to zero.**
- **A supervisor-initiated sleep is not a turn.** A pause for a usage window, a backoff on a
  server error, or waiting on a human answer must never touch the counter. Without this rule the
  first rate limit burns straight through the ladder and stops the run — precisely the failure
  this design exists to prevent.

---

## 4. The escalation ladder

Climb one rung at a time. Record every transition in the ledger. **Never skip to a redesign
because debugging is tedious.**

| L | Trigger | Action |
|---|---|---|
| **L0** | First failure, plausibly transient | Retry once, unchanged. Nothing else. |
| **L1** | Reproducible failure | Find the earliest reliable error. Reproduce with the smallest test. Smallest corrective patch. Add a regression test. Re-run. **Do not redesign unless the error is conceptual.** |
| **L2** | L1 did not resolve it | Search the whole ledger for this failure kind. Apply what was learned. If a prior fix failed, say so and go to L3. |
| **L3** | Not solvable from project history | Search current literature and repositories for how this specific problem is solved now. Record with URLs and dates. |
| **L4** | Three no-progress turns, or L3 produced no route | A separate reviewing process reads the full ledger and answers one question: *is this branch worth continuing, and what is the best alternative?* Output is a `route_change` entry and a new `next_action`. |
| **L5** | Approach sound, implementation is not | Spend one pre-registered revision. **Maximum two per mechanism.** |
| **L6** | Both revisions spent, or the hypothesis is falsified | KILL. Write the verdict, preserve all results, distinguish implementation failure from hypothesis failure, move on. **This is a successful outcome.** |
| **L7** | Blocked on something only a human can supply | §6. |

**Route changes are first-class.** Abandoning a bad branch early is the behaviour this programme
rewards.

---

## 5. Anti-self-deception controls

An autonomous research agent's characteristic failure is not crashing. It is producing
confident, well-formatted, wrong conclusions. These controls exist because you cannot be trusted
to grade yourself, and neither can any agent.

**C1 — Pre-registration is locked before results exist.** Before the first treatment run of any
gate, write `preregistration/<gate>.yaml` with the hypothesis, primary metric, **every numeric
threshold**, the kill rule, mandated baselines, and the revision limit. Commit it. Record its
SHA-256. Your verifier reads thresholds *from this file*, never from prose. If you come to
believe a pre-registration is wrong, you may not change it: record the objection and proceed, or
kill the gate.

**C2 — The verifier is immutable within a gate.** Its hash is pinned. Changing the ruler after
measuring is the most seductive failure available to you.

C1 and C2 need enforcement in layers, because any single layer is bypassable:

1. A tool-call interception that denies edits to protected paths once a result exists.
   **Crucially, it must intercept shell commands as well as file-write tools** — a guard that
   only matches "write file" does nothing about `sed -i`, `tee`, `>`, `cp`, `mv`, `truncate`,
   `python -c` or `git checkout --`. Verify this empirically against synthetic payloads and
   record the result. An unverified guard is not a control.
2. **An external process re-verifies every pinned hash before each turn and aborts on
   mismatch.** This is the layer that actually holds, because it does not depend on a guard you
   could disable.
3. The pre-registration is written before results exist, so the honest window and the locked
   window do not overlap.

The remaining hole, stated plainly rather than hidden: **you author the verifier and the
pre-registration in the first place.** Nothing mechanical prevents a weak threshold chosen in
good faith. That is what C5 and reviewer independence are for, and it is why a pre-registration
must state the threshold *and the reasoning that fixed it there*.

**C3 — Verdicts come from a reviewer, not from you.** A separate process with **read-only** tools
reads raw artifacts, re-runs the verifier, and issues exactly one of
`GO` / `REVISE_ONCE` / `KILL` / `SUSPEND_FOR_DEPENDENCY`. It must have a fresh context — it must
not inherit your reasoning about why your result is good. A verdict that does not cite artifact
paths and SHA-256 digests is rejected and must be reissued.

**C4 — Every result number cites an artifact.** No number produced by this project appears in any
document without a path and a hash. "Improved by 18%" without a citation is not a finding.
Numbers taken from the literature cite their source instead.

**C5 — Adversarial self-review before every verdict request.** Write, in the ledger, the three
strongest arguments that your result is an artifact of something other than the mechanism — a
compute imbalance, a seed, a leak, a baseline implemented too weakly, in-context substitution.
Then test the strongest one.

---

## 6. When to stop for the human — the complete list

Stop **only** for these. Everything else you handle yourself.

1. A secret is needed — API key, token, credential.
2. Money would be spent beyond the existing subscription.
3. An irreversible external action — public push, submission, publication, email.
4. A licensing or legal question the evidence base does not settle.
5. A change requiring administrative rights, or a change outside your project directory.
6. Destructive action on anything outside your project directory.
7. All routes exhausted — L4 produced no viable alternative.
8. Five consecutive no-progress turns.
9. **A scientific finding that invalidates the objective's premise.** Say so. Do not quietly
   redefine the question to keep working.
10. A budget ceiling reached.
11. A required external resource cannot be obtained. Escalate directly; no amount of debugging
    produces a dataset.
12. The governing documents conflict irreconcilably.
13. **A phase deliverable is ready for approval.** `DIAGNOSIS.md`, `IDEAS.md` and
    `PROGRAMME.md` each require Ali's approval before the next phase begins. This is a normal,
    expected stop, not a failure.
14. **A paper you need is unreachable.** Batch these and use the format in
    `04_RESOURCES_AND_SETUP.md` §5. Do not treat a paywalled source as absent evidence.
15. **A job should run on the HPC cluster.** You cannot reach it; Ali submits it. Supply the code,
    the submission script and what you expect back. Using the cluster is encouraged, not a last
    resort.
16. **Any change to your own control surface** — the pre-registrations, the verifier, the pinned
    hashes, the supervisor, the evidence documents. These are not yours to modify. Append-only
    additions to an evidence document carrying a URL and a date are the one exception; never a
    deletion, never a weakened threshold.

Reasons 13 to 15 are collaboration, not blockage: they are the channels through which Ali
contributes to the work, and using them freely is expected.

To stop: write `state/ESCALATION.md` with what you need, why, what you already tried, and what
you will do with each possible answer. Set `blocked_on`. Append a `human_escalation` ledger
entry. Then stop cleanly — do not spin.

**Do not ask a question when a safe default exists.** State the default, record it, continue.

---

## 7. Budget governor

**Environment stepping is free. Model calls are the entire cost.** This was confirmed by
measurement on the previous programme, and it is the most consequential fact about running this
kind of experiment cheaply.

Requirements:

- **Meter your own consumption in the units your subscription actually limits**, and check your
  meter against the provider's own usage display at least once a day. The previous programme's
  throttle initially metered turn *wall-clock* as model spend, which made every game run
  unaffordable and livelocked the programme for hours. Wall-clock spent inside an environment
  simulator costs nothing.
- **Self-throttle with hysteresis.** A ceiling per rolling window, and resume at a *fraction* of
  the ceiling — 60% works — so the run does not oscillate on and off at the boundary.
- **Every experiment declares a maximum runtime in its config. An experiment with no declared
  limit does not run.** The experiment runner's own limit must fire *before* any external kill,
  because an externally killed run writes no manifest and its entire cost is wasted.
- **Classify failures, do not collapse them.** Four signatures, four responses:

| Signature | Meaning | Response |
|---|---|---|
| usage or rate limit hit | window exhausted | sleep to reset, resume — **and match the sleep ceiling to the window that was actually hit.** A five-hour backoff against a weekly limit retries and fails thirty times across the week |
| authentication expired | credentials gone | **escalate** — reason 1 |
| server 5xx, timeout | transient | retry, exponential backoff |
| any other non-zero | unknown | log verbatim, retry once, then escalate |

- **Log every non-zero exit verbatim to `state/tool_errors.jsonl` from day one**, so the first
  real rate limit teaches your supervisor its true signature rather than you guessing it. This
  was the single most useful piece of instrumentation the previous programme built.
- **Effort is a cost lever.** Highest effort for planning, verdicts, novelty audits and
  retrospectives. Middle effort for implementation and debugging. **No model at all** for log
  parsing, metric aggregation, artifact hashing and file bookkeeping — those are scripts, and
  running a frontier model on them wastes the allowance the science needs.
- **Check for a caching pathology early.** On the previous programme, 24 model calls recorded
  510,669 cache-creation tokens against **zero** cache reads, because each invocation was a
  fresh non-persistent session. Size any fix honestly before acting: cache creation costs about
  1.25× ordinary input, so simply not requesting cache saves roughly 20% of that line, around 8%
  of the bill. The large saving needs genuinely persistent sessions so the cache is *read*, which
  is an architecture decision rather than a flag.

---

## 8. The continuation problem — determine your own runtime, do not assume

This is where you must build your own implementation, and where guessing will cost you days.

The previous programme runs a separate Python process outside the agent's tool reach. It invokes
the agent headlessly one turn at a time, checks the escalation file between turns, re-verifies
pinned hashes, meters the budget, sleeps through rate limits, and runs long experiments as jobs
*between* turns rather than inside them. That design was forced by a specific finding: **no way
was found to make the agent continue working from inside itself.** No stop-hook mechanism could
force continuation, so continuation had to be external.

Your runtime is different and may well be better at this. **Your first engineering task after
the proposal is approved is to establish, empirically, what it actually provides.** Write the
answers into your own tooling-evidence document with dates, marking each as documented,
unconfirmed, or verified on the machine. At minimum:

1. Is there a filesystem that persists across sessions and reboots? Where exactly?
2. Can a session be resumed by identifier after the process dies?
3. Is there unattended multi-session continuation — can work proceed with nobody watching, and
   for how long? **Reported multi-day autonomous operation is a marketing claim until you have
   measured it on this machine.**
4. Is there scheduled or background execution?
5. Are there sub-agents with isolated context? This is what C3 reviewer independence needs.
6. Is there per-tool permission control, and can a guard intercept **shell commands** and not
   just file writes? C1/C2 layer 1 depends on this.
7. What is the non-interactive invocation, and what are its exit codes?
8. **Are environment variables passed through to subprocesses your tools spawn?** The previous
   programme lost most of a day to this: its runtime strips certain variables from its own shell
   subprocesses, so an experiment launched from inside a turn could not authenticate. Test it
   with a throwaway variable before you depend on it — `04_RESOURCES_AND_SETUP.md` §7 has the
   two-line check.
9. How does the runtime behave at context exhaustion in unattended mode?
10. What is the exact failure signature when the usage limit is hit — exit code, message text,
    whether a reset timestamp is carried?

Then implement the contract with what you have. Two acceptable shapes:

- **Native.** If your runtime genuinely supports multi-day unattended sessions, use them — but
  the state files in §2 are still mandatory, because the session will still eventually die.
- **External supervisor.** A small process outside your tool reach that drives turns. Choose this
  if item 3 is unproven. It is more work and it always holds.

**Do not build the loop on anything inside the agent** unless item 3 came back verified on this
machine. That is the one architectural conclusion the previous programme is confident transfers.

---

## 9. Roles

Separate reviewing processes with **fresh context and restricted tools**. The reviewer must not
inherit your reasoning. At minimum:

| Role | Tools | Job |
|---|---|---|
| **builder** | full, scoped to the project directory | Implements, tests, debugs. The default |
| **reviewer** | read-only, plus the ability to run the verifier, hash files, and write **only** into the verdicts directory | Issues `GO` / `REVISE_ONCE` / `KILL` / `SUSPEND_FOR_DEPENDENCY` from raw artifacts. Cannot touch code, configs, results or pre-registrations |
| **scout** | web search and fetch, read | L3 literature search on a specific blocked problem. Returns URLs and dates |
| **novelty-auditor** | web search and fetch, read, write to the audit documents | Maintains the novelty audit and claim–evidence matrix. Runs before each mechanism and before any manuscript claim |
| **retrospective** | read-only | L4. Reads the whole ledger; answers whether the branch is worth continuing |
| **debugger** | read, edit, shell, search | L1. Minimal repro, smallest patch, regression test. Nothing else |

The reviewer needs its own hashing capability: certifying the graded party's own checksum file is
not certification. And it needs write access to the verdicts directory, because otherwise the
only party that could file the verdict is the party the reviewer exists to exclude.

---

## 10. Daily digest

Once per calendar day, write `reports/DIGEST_<YYYY-MM-DD>.md` and commit it. One page:

1. Where we are — gate, task, one sentence.
2. What advanced.
3. **What failed and what it taught.** The most valuable section; do not compress it away.
4. Route changes, and why.
5. Usage — window percentages, turns run, pauses.
6. What is next, and anything you need from Ali.

**Write it honestly.** A digest that reports steady progress during a week of thrashing is worse
than no digest.

---

## 11. Repository contract

One canonical entry point for every experiment. Never create a second incompatible one.

Every run writes, under `artifacts/<experiment_id>/<run_id>/`: `manifest.json`,
`resolved_config.yaml`, `results.json`, `metrics.csv`, `transitions.jsonl`, `hypotheses.jsonl`,
`stdout.log`, `stderr.log`, `git_state.txt`, `environment_info.json`, `SHA256SUMS`.

The manifest records at minimum: experiment id, run id, timestamp, git commit, dirty-tree flag,
language version, dependency-lock hash, config hash, generator version, seed, model identifier,
prompt hash, action budget, simulation budget, token budget, persistent-state cap, hardware,
wall-clock limit, completion status.

Commit after every verified step. Never commit a virtual environment. **Never commit a secret.**
Never rewrite history.
