# The Research Process — diagnose, invent, screen

**This is the core document of the pack.** It specifies three phases and the order is not
negotiable. Each phase ends in a written deliverable that Ali approves before the next begins.

The reason for the order is in `00_START_HERE.md` §2: a previous version of this brief asked for
mechanisms and their novelty defence in one step, and two capable models both concluded that
nothing they could think of was defensible. That is what happens when an idea must be born
already defended. **Generation and screening are separate activities and mixing them destroys
the generative one.**

---

# PHASE 1 — DIAGNOSIS

**Deliverable: `DIAGNOSIS.md`. Nothing else happens until Ali has read and approved it.**

This phase should take the largest share of the early programme. Ali has said explicitly that he
wants most of the initial time spent here. Do not compress it to reach the interesting part —
this *is* the interesting part, and everything downstream is only as good as it.

## 1.1 The prohibition, and what to do with ideas anyway

**You will not propose, rank, specify or defend any mechanism during Phase 1.**

Ideas will occur to you while you read. Suppressing them loses them; developing them biases the
diagnosis towards whatever you thought of first. So do neither:

> Keep `IDEAS_PARKED.md`. When an idea arrives, write it down in one or two sentences with the
> date and what prompted it. **Do not elaborate it, do not evaluate it, do not check its
> novelty.** Do not reread the file until Phase 2 begins.

That file becomes a Phase 2 input and also a record of how your thinking moved, which is worth
having.

Code in Phase 1 is permitted only for §1.4 — reproducing a failure. No architecture, no
mechanism, no harness for something you intend to test later.

## 1.2 Characterise the computational demand

Before cataloguing failures, be precise about what the problem in `01_THE_PROBLEM.md` §1 actually
demands. Useful questions, not a template to fill:

- What must be inferred that cannot be observed directly?
- What has to survive what, and for how long?
- What makes an arrangement "new" in a way that matters, as opposed to a resampling of the old?
- Which parts of the demand do current methods already handle well, and what distinguishes those
  from the parts they do not?

The last one is the most useful and the most often skipped. **A failure that is specific is
diagnosable; a failure that is general is just a complaint.**

## 1.3 Catalogue what is reported to fail, and why

Survey the recent AI literature for this class of problem. For each substantial finding, separate
three things that are routinely conflated:

| | |
|---|---|
| **A reported score** | "System X reached N% on benchmark Y." Almost no diagnostic content |
| **An observed failure mode** | "It never recovered the earlier rule after interference." Useful |
| **An identified mechanism of failure** | "Because the importance estimate is computed at task boundaries it cannot see mid-task conflict." Rare, and worth ten of the others |

Cite everything with a URL and an access date; mark preprints as preprints. Say explicitly what
appeared in the last six months. Where an author offers their own diagnosis, quote it and say
whether their evidence supports it — authors' diagnoses of their own failures are often the
weakest part of a paper.

**Where a claim you need to weigh sits behind a paywall, ask Ali for the paper.**
`04_RESOURCES_AND_SETUP.md` §5 has the format. Do not build an argument on an abstract when the
method section is what decides it, and do not treat an unreachable paper as absent evidence.

## 1.4 Reproduce at least one failure yourself

**Required.** Build the smallest system that exhibits the failure and watch it break.

This is cheap, local, needs no cluster and no frontier model in the loop. Its value is out of
proportion to its cost, for a reason worth stating: a failure you have read about comes with the
author's interpretation attached, and a failure you have instrumented does not.

Do not stop at reproducing that it fails. **Instrument it to find out where.** What is the last
point at which the system still had what it needed? What exactly is present in its state, and
what is absent, at the moment the failure becomes inevitable? A failure that is merely observed
gives you a symptom; a failure that is traced gives you a mechanism.

Be ready for the trace to disagree with the literature's account. If it does, that disagreement
is a finding and it goes in the diagnosis.

## 1.5 Interdisciplinary evidence, used generatively

Biology gets a section because it is where Ali most wants you to look, and because it is easy to
do badly.

**The wrong question:** what structure does the brain have that resembles a component I might
build? That produces anatomical decoration.

**The right question:**

> What computational problem is this system solving, under what constraints, and which of those
> constraints do artificial systems violate without noticing?

Go wider than the hippocampus. Candidate territories, offered as directions rather than a
reading list: systems and cellular neuroscience; developmental psychology and how children
acquire causal structure from tiny samples; animal cognition, including species that solve parts
of this with very little cortex; immunology, which maintains a discriminative memory over decades
under adversarial pressure and has an entirely different implementation; cell biology and how
structure persists through molecular turnover; ethology; control theory and system
identification.

For each lead, record the constraint, the evidence class (human intervention, human recording,
animal, model, theory), and its limits. Recording evidence is not intervention evidence; a mouse
result is not a human result; a computational model of biology is a hypothesis about biology, not
a measurement of it.

## 1.6 The archaeology pass — required

The field discards ideas for reasons that expire: compute was scarce, data was scarce,
differentiability was mandatory, something else was fashionable, the authors moved on. Some of
those ideas addressed exactly the problem in `01_THE_PROBLEM.md` §1 and addressed it directly.

**Survey what was set aside, roughly 1960–2010, and for each ask two questions:**

1. Why was it abandoned?
2. **Does that reason still hold in 2026?**

Starting points, not a list to complete: Grossberg's stability–plasticity dilemma and adaptive
resonance, which named this objective in the 1970s; Drescher's schema mechanism, which learned
causal structure from interaction; explanation-based learning; Holland's classifier systems;
case-based reasoning; Gentner's structure mapping and the analogy literature; qualitative
physics; version spaces; blackboard architectures; production-system architectures such as SOAR
and ACT-R; the early predictive-coding tradition.

Judge each on its idea, not its era's results. **An idea that failed on 1990 hardware with 1990
data is not a refuted idea.** Equally, do not romanticise: some were abandoned because they were
wrong, and saying which is part of the work.

Ask Ali for anything you cannot reach. Much of this literature predates open access.

## 1.7 The deliverable

`DIAGNOSIS.md` contains, in this order:

1. **The computational demand**, stated precisely (§1.2), including which parts current methods
   already handle.
2. **The failure catalogue** (§1.3), with the three-way separation above maintained throughout.
3. **Your own reproduction** (§1.4): what you built, what you saw, where it broke, and whether
   the trace agreed with the literature.
4. **Interdisciplinary constraints** (§1.5): what other fields' solutions respect that ours do
   not, with evidence classes and limits.
5. **The archaeology** (§1.6): what was abandoned, why, and whether the reason still holds.
6. **Ranked bottlenecks.** The heart of it. Each one:
   - stated as a **falsifiable claim about why methods fail** — not a topic, a claim;
   - the evidence for it, and the evidence against;
   - **what observation would refute it**;
   - what else it predicts, that you have not yet checked;
   - your confidence, and what would raise it.
7. **The hypothesis you were handed.** `01_THE_PROBLEM.md` §3.1 gives Ali's initial framing —
   plasticity control over retain / protect / suppress / recompose. Where does it sit in your
   ranking, and why? Say plainly if your diagnosis points elsewhere.
8. **What you could not resolve**, and what it would take.

A bottleneck that cannot be stated as something that could be false is not a bottleneck. It is a
topic, and topics are not actionable.

---

# PHASE 2 — IDEATION

**Deliverable: `IDEAS.md`. Begins only after `DIAGNOSIS.md` is approved.**

Time-boxed and deliberately unlike Phase 1 in character. Phase 1 rewards caution. **Phase 2
punishes it.**

## 2.1 The suspension

**Novelty screening is switched off for the whole generative stage.** So is feasibility
screening, and so is your sense of what is respectable.

During generation, **no idea may be rejected** for being: probably a rename; obvious; already
tried; not differentiable; not scalable; symbolic; biologically implausible; implausibly simple;
or wrong. Those judgements come later and they come to a *population* of ideas, not to each idea
at birth.

This instruction exists because it is the exact failure of the previous brief. Two capable models
were asked to generate and defend simultaneously, and both produced nothing but well-defended
nothing. If you find yourself writing "but this is essentially EWC" during the generative stage,
**you are in the wrong phase.** Write the idea down and move on.

## 2.2 Generate

Work against the top two or three bottlenecks from `DIAGNOSIS.md`, one at a time.

**Aim for volume: at least twenty to thirty distinct ideas per bottleneck, and deliberately
include bad ones.** A generative pass with a 90% discard rate is working correctly. A pass that
produces four careful candidates has already been screening.

Draw deliberately from each of these, so the population is not all one kind of thing:

- `IDEAS_PARKED.md` — everything you noted during Phase 1, now reread for the first time
- The archaeology pass — old mechanisms, revived against the current diagnosis
- The biological constraints — what would an algorithm look like that actually respected one?
- Deliberate orthodoxy violations — non-differentiable, discrete, symbolic, non-stationary,
  no-gradient, no-replay, throw-away-the-data
- Inversions — if the diagnosis says the system lacks X, what if it needs *less* of the thing
  that makes X necessary?
- Combinations of two ideas that do not obviously belong together

Record each in a few sentences: what it does, which bottleneck it attacks, and why it might work.
Nothing longer at this stage.

## 2.3 Converge

Only when generation is finished:

1. **Cluster** the population. Most ideas will collapse into a handful of underlying moves; the
   clustering itself is informative and belongs in the deliverable.
2. **Pick three to five** to develop, choosing for *diversity of underlying move* as much as for
   individual promise. Two variants of the same idea are one candidate.
3. **Develop each into a specified operation** — state, inputs, update rule, what it explicitly
   leaves unchanged, cost. Precise enough that someone else could implement it and get the same
   thing.
4. **Only now** note, for each, the nearest existing method you are aware of — as a one-line
   flag, not an audit. The audit is Phase 3.

## 2.4 The deliverable

`IDEAS.md` contains: the full generated population, unedited and including the bad ones; the
clustering and what it revealed; the three to five developed candidates with their
specifications; the nearest-method flags; and **which bottleneck each candidate attacks and how
you would know if it had addressed it.**

Keep the discarded ideas visible. A later phase may need to come back through them, and the shape
of what you rejected is evidence about how you were thinking.

---

# PHASE 3 — SELECTION, AUDIT AND DESIGN

**Deliverable: `PROGRAMME.md`. Begins only after `IDEAS.md` is approved.**

Now the conventional rigour applies, to candidates that were generated to fix a diagnosed
failure rather than sampled from a literature review.

This is also where you request `06_BENCHMARK_FACTS.md` from Ali if you are considering an
interactive benchmark. It was withheld until now on purpose — it describes one convergent
architecture in detail and would have anchored your diagnosis.

`PROGRAMME.md` contains:

1. **The novelty audit.** For each candidate: nearest existing method, checked against its
   primary method description rather than its abstract; a variable-by-variable mapping of state,
   inputs, update, allocation, reset behaviour and resource cost; a concrete history on which the
   two behave differently; and an argument that the difference is not merely a tunable special
   case of the comparator. An exact reduction is a kill, and a clean kill with the mapping
   written out is a publishable result — see `01_THE_PROBLEM.md` §6.
2. **Experimental design.** Instrument and why. Environments and how generated. The context
   clearing control, designed *before* the mechanism it isolates. Baseline ladder, including the
   nearest existing method for each candidate. Metrics. Compute matching, stated in what is
   actually counted.
3. **Gate structure** with machine-checkable exits and kill rules.
4. **Budget**, measured before committed. Profile a small, typical and largest case; project from
   the largest observed rather than the median; and if the projection exceeds the allowance, do
   not start — either reduce scope by a preregistered rule or escalate.
5. **Compute plan.** Say explicitly what runs on the laptop and what should go to the HPC
   cluster. See `04_RESOURCES_AND_SETUP.md` §3; using the cluster is encouraged where it helps.
6. **The three strongest arguments that the whole approach is wrong**, with what would defeat
   each and what would confirm it.

---

# Across all phases

**The ledger starts now.** From your first action, `03_AUTONOMY_SPEC.md` §2 applies: state on
disk, append-only ledger, one advancing step per turn. Phases 1 and 2 are research, not
measurement, but they are still work that must survive you losing your memory.

**Approval between phases is a human gate**, handled through `state/ESCALATION.md` once the lab
exists and through conversation before it does.

**You may go back.** If Phase 2 generation reveals that the diagnosis was wrong, say so and
return to Phase 1. If Phase 3's audit kills everything, the right move may be another Phase 2
pass against the second-ranked bottleneck rather than closing the programme. Record the loop in
the ledger with the reason.

## Ways this goes wrong

- **Phase 1 becomes a literature review.** Symptom: lots of citations, no falsifiable bottleneck.
  The test is §1.7 item 6 — if nothing you wrote could be false, you have surveyed, not diagnosed.
- **Phase 1 is rushed to reach Phase 2.** Symptom: bottlenecks that restate the problem instead
  of explaining it. "Systems forget" is not a diagnosis.
- **Phase 2 screens while generating.** Symptom: four careful candidates instead of sixty rough
  ones. See §2.1.
- **The diagnosis is written to justify an idea you already had.** This is why `IDEAS_PARKED.md`
  stays closed. If you catch yourself doing it, say so in the deliverable.
- **The archaeology becomes nostalgia.** Symptom: old ideas praised without saying what killed
  them or why that has changed.
- **Biology becomes decoration.** Symptom: a mechanism named after a brain structure whose
  behaviour does not depend on anything biological. `01_THE_PROBLEM.md` §4.
