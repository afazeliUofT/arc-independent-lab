# START HERE

**For:** the autonomous researcher who will run this programme
**Funder and collaborator:** Ali Fazeli, postdoctoral researcher, Electrical and Computer
Engineering, University of Toronto
**Date:** 6 September 2026
**Read this file completely before opening anything else.**

---

## 1. What you are being asked to do

Not to test a list of mechanisms. To **work out why a whole category of problem defeats current
AI systems, and then think hard about what would fix it.**

The category, stated without prejudging its solution:

> An agent must build knowledge by interacting with a world it does not understand, keep that
> knowledge across discontinuities — new episodes, interference, long gaps — and recombine it to
> handle situations it has never seen. Humans and many animals do this so easily that it is hard
> to see as a problem. Current artificial systems are strikingly bad at it.

**Why?** That is the question. Not "which brain-inspired trick helps," but *what is actually
broken, mechanically, in how current systems approach this*, and does anything — in neuroscience,
in biology more broadly, in recent AI, or in the field's own abandoned past — suggest a repair.

Ali is looking for a mechanism that could matter to the field. He is explicitly **not** trying to
win a benchmark. He would rather have a correct diagnosis and no mechanism than a mechanism with
no diagnosis.

---

## 2. The shape of the work: diagnose, then invent, then screen

This is the single most important instruction in the pack, and it inverts how this kind of task
is normally posed to a model.

**You will not propose mechanisms for the first phase of this programme.** You will spend that
time understanding the failure. `02_RESEARCH_PROCESS.md` specifies three phases and you must
complete them in order:

| Phase | What it produces | Roughly |
|---|---|---|
| **1 — Diagnosis** | A ranked set of *bottlenecks*: falsifiable claims about **why** current methods fail at this class of problem, drawn from AI failure reports, from your own reproduction of at least one failure, from neuroscience and wider biology, and from the field's abandoned literature | The largest share of the early programme. Do not rush it |
| **2 — Ideation** | Many candidate ideas aimed at the top bottlenecks, generated with **novelty screening switched off**, then converged into a few specified operations | A bounded burst after Phase 1 is approved |
| **3 — Selection and design** | Novelty audit, experimental design, gates, budget — the conventional rigour, applied only to what survived Phase 2 | Then the programme proper |

**Why this order matters, stated plainly because a previous attempt got it wrong.** An earlier
version of this brief asked for ranked mechanisms *with their novelty defence* as the first
deliverable. Two capable models independently produced careful documents concluding that none of
their candidates could be defended as novel — which is what happens when you require an idea to
be born already defensible. Both of them then identified the real diagnostic problem in the
section reserved for self-criticism, because that was the only place the brief let diagnostic
thinking exist. Do not repeat that. **Nothing interesting is born defensible. Generation and
screening are separate phases and must stay separate.**

---

## 3. Breadth is the point

Phase 1 is not a literature review of continual learning. Four sources of evidence are all
required, and the last two are where the value is most likely to be:

**Recent AI.** What is actually reported to fail, and what do the authors themselves say the
cause is? Distinguish "scored badly" from "identified a mechanism of failure."

**Your own reproduction.** Build the smallest thing that exhibits the failure and watch it. A
failure you have seen is worth ten you have read about. This is cheap, it is local, and it is
where non-obvious findings usually come from.

**Neuroscience and biology, used generatively.** Not "the brain has a structure resembling my
module." Rather: *what computational problem is this biological system solving, and what
constraints does its solution satisfy that our systems violate?* Range wider than the
hippocampus — developmental psychology, animal cognition, immunology and its notion of memory,
cell biology, ethology, control theory. A constraint that biology respects and machine learning
ignores is a strong lead.

**The archaeology pass — required, not optional.** The field abandons ideas for reasons that
expire. Compute was scarce; data was scarce; differentiability was mandatory; something else was
fashionable. Go and look at what was set aside between roughly 1960 and 2010 that addressed
exactly this problem, and for each ask two questions: *why was it abandoned, and does that reason
still hold in 2026?* Grossberg's stability–plasticity dilemma is your objective, named in the
1970s. Drescher's schema mechanism learned causal structure from interaction. Explanation-based
learning, classifier systems, case-based reasoning, analogical structure mapping, qualitative
physics, version spaces, blackboard architectures, production-system architectures — these are
examples to start from, not a reading list to complete, and several of them were abandoned for
reasons that no longer apply. An idea that failed on 1990 hardware with 1990 data is not a
refuted idea.

---

## 4. Working with Ali

He is an active collaborator here, not a distant approver.

**Ask him for papers.** If a source is paywalled or otherwise unreachable and a claim depends on
it, **ask**. He has university access. Batch your requests and use the format in
`04_RESOURCES_AND_SETUP.md` §5. Do not treat an inaccessible paper as absent evidence, and do not
build a novelty argument on an abstract when the method section is what matters.

**Ask him for compute.** He has a Digital Research Alliance of Canada HPC account with GPU nodes
in addition to the laptop. You cannot reach it directly, but he can run what you write.
`04_RESOURCES_AND_SETUP.md` §3 explains the loop. **Using it is encouraged where it genuinely
helps** — do not silently design around a laptop because the cluster is inconvenient.

**Ask him to publish results you need to read.** He will give you read access to the programme's
GitHub repository so you can inspect artifacts directly rather than having them pasted.

**Never hand him a blind instruction.** If you need to know something about his machine, give him
a command that produces the answer.

**Guess-free scripts.** Anything he runs should be pasteable, idempotent, and handle its own
failure modes. He has had automation fail badly before; reliability beats cleverness.

**Honest over reassuring.** If a lead is weak, say so. If you were wrong earlier, correct it
explicitly rather than quietly.

**Do not ask what you can decide.** State a safe default, record it, continue. Save his attention
for what only he can settle.

---

## 5. Reading order

| # | File | What it is |
|---|---|---|
| 1 | `00_START_HERE.md` | this file |
| 2 | `01_THE_PROBLEM.md` | what is being asked, what is fixed, and how little of it is |
| 3 | `02_RESEARCH_PROCESS.md` | the three phases in detail. **The core document** |
| 4 | `03_AUTONOMY_SPEC.md` | the operating contract, written to be runtime-agnostic |
| 5 | `04_RESOURCES_AND_SETUP.md` | machine, cluster, repository, papers, secrets |
| 6 | `05_OPERATIONAL_LESSONS.md` | engineering traps already paid for. Read before you debug anything |

A seventh document, a verified fact sheet on the ARC-AGI-3 benchmark, exists and is **deliberately
withheld until Phase 3.** It contains a detailed account of one convergent architecture, and
giving it to you now would anchor your diagnosis on someone else's answer. Ask Ali for it when
you reach instrument selection.

---

## 6. Another programme exists and you are not being shown it

Ali runs a second autonomous programme against a related question. It occupies
`~/ARC_AGI3_Plasticity_Lab/` on his machine and has a public GitHub repository.

**Do not read either.** Not the directory, not the repository, not by asking Ali what it
concluded. You are being kept clear of it deliberately, so that your diagnosis is yours. If two
programmes that never communicated reach the same place, that convergence is evidence; if you
read its answer first, any agreement is worth nothing.

If you learn something about it accidentally, **record it in your ledger as a contamination
event** with what you learned and when. Honesty about contamination preserves most of its value.
Concealment destroys all of it.

What you *have* been given from it is apparatus knowledge only — machine setup, engineering
traps, the operating contract. None of that is scientific.

---

## 7. Ground rules that do not move

1. **You never grade yourself.** A separate reviewing process with read-only access and a fresh
   context issues every verdict.
2. **Thresholds are written and frozen before results exist.** This applies from Phase 3 onward;
   Phases 1 and 2 have no thresholds because they produce no measurements.
3. **Every number you report cites the file it came from and that file's hash.**
4. **Biology is a source of hypotheses and constraints, never a justification.** "The brain does
   something like this" is a reason to investigate and never a reason to believe. Both halves of
   that sentence matter.
5. **A negative result is a result.** A correct diagnosis with no surviving mechanism is a
   successful programme. Do not manufacture a positive one.
6. **Never write a credential into a file, a log, a commit, or a message.**

Your directory is **`~/ARC_Independent_Lab/`**. Nothing you create lives outside it.

---

## 8. Your first output

Not a proposal. Not code. Not a repository.

**Read all six documents completely, then ask Ali every question whose answer would change what
you do — all at once, in one message.** Then begin Phase 1 as specified in
`02_RESEARCH_PROCESS.md`, whose first deliverable is `DIAGNOSIS.md`.

Take the time Phase 1 deserves. Ali would rather wait a week for a diagnosis he can act on than
receive a mechanism list tomorrow.
