# Operational Lessons

Every item here cost real time on a previous autonomous programme running on this same machine.
**None of it is scientific — this is all apparatus.** Read it before you debug anything, and read
it again the first time something behaves impossibly.

The meta-lesson first, because it generated most of the rest:

> **That programme's throughput was limited by engineering defects, not by model capability, for
> its entire first three days.** Its first positive result came from changing two integer
> constants that had been chosen before any data existed. No larger model and no bigger budget
> would have found them. Budget your attention accordingly: the substrate is where the failures
> are, and reaching for a stronger model when the apparatus is the limiter is how you spend a
> large budget confirming the same zero.

---

## 1. Budget metering — the one that livelocked the programme

**Symptom.** The supervisor did a handful of tiny turns, then slept for hours, then repeated,
never running an experiment.

**Cause.** The throttle metered each turn's **wall-clock** as model spend. A game run takes two
hours of wall-clock and perhaps twenty minutes of model time, because almost all of it is the
environment simulator, which costs nothing. Under wall-clock metering no game run was ever
affordable, so the supervisor kept choosing cheap no-op turns and throttling itself anyway.

**Fix.** Meter only the model time each run *reports*. Environment time is free; charging for it
starves the science.

**Second-order bug from the same fix.** The code that located the reported figure did a loose key
search and matched `max_model_wallclock_seconds` — the *cap* — instead of
`model_wallclock_seconds_total` — the *value*. It therefore charged the ceiling on every run by
a new route.

**Fix.** Match the exact key first. Only fall back to a loose search, and when you do, exclude
keys containing `max`, `limit`, `cap`, `budget`, `quota`, `allow`, `remaining`, `threshold`,
`ceiling`, `per_call`, `timeout`.

**Generalisation:** any heuristic that searches a nested structure for "the number that looks
right" will eventually find a limit instead of a measurement.

---

## 2. Kill ordering — whoever kills first decides whether you keep the data

**Symptom.** A long run was terminated by the supervisor's hard wall-clock kill and produced no
manifest, so hours of model spend were unrecoverable.

**Fix.** The experiment runner's own `wallclock_limit_seconds` must fire **strictly before** any
external kill — 10,500 s against a 10,800 s supervisor kill, for example. The runner then exits
cleanly and writes its artifacts; the external kill exists only as a backstop for a hung process.

---

## 3. Buffering — why `tail -f` shows nothing

**Symptom.** A supervisor running under `nohup ... > log 2>&1 &` produced an empty log for twenty
minutes while clearly working.

**Cause.** Python block-buffers stdout when it is not a terminal.

**Fix.** `PYTHONUNBUFFERED=1`, or `python3 -u`. Do both; it costs nothing.

---

## 4. `pgrep -f` matches your own command line

**Symptom.** A script that ran `pkill -f 'scripts/supervisor.py'` killed *itself*, repeatedly,
because the pattern appeared in its own shell's argv.

**Fix.** The bracket trick: `pgrep -f 'scripts/supervisor[.]py'`. The regex matches the literal
string, but the pattern text itself no longer matches. When even that is not enough — because the
target string appears elsewhere in the invoking command — scan `/proc/*/cmdline` and skip your
own PID.

---

## 5. `set -o pipefail` plus `head` equals SIGPIPE

**Symptom.** A script died silently partway through, having done half its work, with no error
message.

**Cause.** `find ... | head -12` under `set -Eeuo pipefail`. `head` exits after twelve lines,
`find` gets SIGPIPE, `pipefail` propagates the failure, `-e` exits the script.

**Fix.** Do not pipe an unbounded producer into `head` in a `pipefail` script. Use
`awk 'NR<=12'`, or append `|| true`, or capture into a variable first.

**Generalisation:** a strict-mode script that stops halfway is worse than one that never ran,
because it leaves inconsistent state. Make every mutating script **idempotent** and have it
**detect an already-applied state** and exit cleanly.

---

## 6. `git rm` aborts wholesale on a single non-matching pathspec

**Symptom.** A cleanup script printed "index cleaned" and had cleaned nothing.

**Cause.** `git rm --cached -r a b c` fails entirely if `b` matches nothing. All three paths were
left untouched, and the script's success message was printed unconditionally.

**Fix.** Remove each path in its own command. Then **re-count and report the actual state** rather
than asserting success. The rule adopted after this: *a mutating script verifies by re-measuring,
never by assuming its own command worked.*

Related: staged deletions were left uncommitted in one branch of the same script, so the
repository looked clean on the next inspection and was not.

---

## 7. Counting files: AppleDouble sidecars and non-recursive globs

Two separate miscounts on the same dataset, in opposite directions.

- A ZIP produced on macOS contained a `__MACOSX/` tree of `._` AppleDouble sidecars. Counting
  them gave **680 recordings where there were 340**, and produced a confident, wrong instruction
  to go and extract 340 more.
- An inspection snippet used non-recursive `glob` on a nested directory tree and reported **zero**
  files where there were hundreds.

**Fix.** Filter `__MACOSX` and `._*` explicitly. Use `rglob`, not `glob`, unless you know the tree
is flat. And when a count is surprising in either direction, verify it a second way before acting
on it.

---

## 8. Patching a file by computed offsets

**Symptom.** A patch script corrupted the supervisor into unparseable text —
`env[        model_s, source = ...`.

**Cause.** The script computed slice indices, then inserted a helper function *before* applying
them, so every index was stale.

**Fix, and this is a standing rule:** patch by **exact string replacement**, never by computed
offsets. Then `compile()` the result and **only write the file if it compiles**. A patch script
that can leave a file syntactically broken will eventually do it, at the worst possible moment, to
the one file that runs everything.

```python
new = old.replace(ANCHOR, REPLACEMENT, 1)
try:
    compile(new, "target.py", "exec")
except SyntaxError as e:
    sys.exit(f"ABORT: would not compile ({e}); nothing written.")
path.write_text(new)
```

Also: take a timestamped backup before touching any control-surface file.

---

## 9. An outcome kind with no branch halts everything

**Symptom.** The supervisor stopped dead with a HALT and no useful message.

**Cause.** A turn returned an outcome classified as `unknown`, and the dispatch had no branch for
`unknown`. The first guard written to fix it tested `outcome.kind == "ok"`, which would have
missed the case again.

**Fix.** Every classifier needs a default branch that is *conservative and logged*, not one that
stops the programme. And when you write the fix, test it against the *actual* recorded failure,
not against your reconstruction of it.

**A related human failure, worth naming because it is the most dangerous kind.** The bug was
diagnosed from memory as "exit code 0, `is_error` false". The machine's own `tool_errors.jsonl`
showed exit code 1 and `is_error` true. The diagnosis was confidently wrong and would have
produced a fix for a bug that did not exist. **Read the log. Do not reconstruct it from what you
expect.**

---

## 10. Control-surface guards must intercept the shell

A guard that matches only file-writing tools does nothing about `sed -i`, `tee`, `>`, `cp`, `mv`,
`truncate`, `python -c` or `git checkout --`. The previous programme's guard matches shell
invocations too, and this was verified empirically against five synthetic payloads — three
denied, two allowed — before the supervisor was allowed to start.

**Do the same, and record the result. An unverified guard is not a control.**

---

## 11. Prompt caching in non-persistent sessions

Across 24 model calls the previous programme recorded **510,669 cache-creation tokens and zero
cache reads**. Every call re-paid cache creation on the whole history, because each invocation was
a fresh session in a fresh directory with nothing to resume.

Check the same on your runtime early. But size the fix honestly before acting on it: cache
creation costs about 1.25× ordinary input, so *not* requesting cache saves roughly 20% of that
line — around 8% of the bill. The large saving needs sessions that genuinely persist so the cache
is *read*, which is an architecture decision, not a flag. The first estimate given was "43%,
recoverable", and it had to be corrected.

---

## 12. Write gate thresholds as minimums, and evaluate them at the right commit

A gate predicate that counted items in an evidence document was written as an equality. The
document later, correctly, gained an item, and the gate began failing for a good reason.

**Rule:** a threshold that counts items is a **minimum**, never an equality. And gate verification
is evaluated at the **graded commit**, not at `HEAD` — otherwise ordinary progress after a run
invalidates a verdict that was correct when it was issued.

---

## 13. The escalation answer channel must be stated inside the escalation

The contract specifies that a human answers by appending a `## ANSWER` section to
`state/ESCALATION.md`, and that nothing else counts. This works only because every escalation
message repeats that instruction. A human reading an escalation three days later does not
remember the protocol.

**Say where the answer goes, in every escalation, every time.**

---

## 14. General rules adopted after all of the above

1. **Test destructive or patching scripts against a throwaway copy of the tree first.** Keep a
   mock lab under `/tmp/` for exactly this. It caught several of the bugs above before they
   touched the real repository.
2. **Re-measure to verify; never assert success.** Print the observed state after a mutation.
3. **Make every script idempotent** and able to detect that it has already run.
4. **Log every non-zero exit verbatim from day one.** The first real rate limit then teaches you
   its true signature instead of you guessing it. This was the single most useful piece of
   instrumentation in the programme.
5. **Back up any control-surface file before patching it**, with a timestamp in the name.
6. **When a number is surprising, verify it a second way before acting on it.** Every wrong
   instruction given to that programme by its human came from a number he believed on first
   sight.
