# The Problem — what is being asked, and how little of it is fixed

**Read after `00_START_HERE.md`.**

---

## 1. The phenomenon

State it as a phenomenon, because naming it as a mechanism would be assuming the answer.

> An agent interacts with a world whose rules it does not know. It must work out what causes
> what, keep what it learns across discontinuities — episode boundaries, interference from
> conflicting experience, long gaps, changes of context — and then recombine those pieces to act
> correctly in an arrangement it has never encountered.
>
> Humans do this from early childhood, from very few examples, without catastrophic loss of what
> they already knew, and without being told which pieces to reuse. Many animals do a substantial
> part of it. **Current artificial systems are conspicuously bad at it**, and the gap does not
> appear to close with scale in the way other gaps have.

That is the phenomenon Ali is funding you to explain and, if possible, to attack.

**The question is "why", before it is "what would help".** A mechanism proposed without a
diagnosis is a guess dressed in equations, and the field has plenty of those.

---

## 2. What is fixed

Very little, and none of it is scientific.

**The phenomenon in §1.** You may sharpen its statement, split it, or argue that it is really two
unrelated problems wearing one name. You may not silently replace it with a different question
that is easier to answer.

**The epistemic rules**, from Phase 3 onward, when you begin to measure things:

- Pre-registration of every numeric threshold before the first treatment run.
- Verdicts issued by a separate reviewing process that did not produce the result.
- One variable at a time in any comparison.
- Raw evidence preserved and never overwritten.
- Every reported number cites an artifact path and a hash.
- Before requesting any verdict, write the three strongest arguments that your result is an
  artifact of something other than your mechanism, then test the strongest.

**No spending beyond existing subscriptions.** No paid API calls, no cloud credits, no rented
accelerators. The laptop and the HPC account Ali already holds are the compute.

**MIT-0 from the first commit.**

That is the whole of it.

---

## 3. What is open — including things you may expect to be fixed

| Question | Status |
|---|---|
| **Where the bottleneck actually is** | Entirely open. It may be how knowledge is protected from being overwritten; it may be how the reusable pieces are discovered in the first place; it may be credit assignment across long delays; it may be exploration; it may be that "pieces" is the wrong ontology. **Phase 1 decides this, not this document** |
| **Whether "a mechanism" is even the right unit of repair** | Open. The answer might be an architecture, a training regime, an objective, a representation, or a claim that the framing is confused |
| Which discipline supplies the leads | Open. Neuroscience is expected to be useful. So might immunology, development, ethology, control theory, or a 1985 AI paper |
| Instrument and environments | Open. Choose them **after** the diagnosis, to test the diagnosis |
| Whether to use a public benchmark at all | Open |
| Baselines, metrics, gate structure | Open, subject to §2 |
| Cross-domain transfer target | Open. Ali's own field is wireless communications and signal processing, which makes active system identification a convenient second domain. A convenience, not a requirement |

### 3.1 One thing you may expect to be fixed, and is not

An earlier version of this brief specified the objective as discovering **"plasticity-control
operations"** that improve four named functions — retain, protect, suppress, recompose — and
called that fixed.

**It is not fixed. It is Ali's initial hypothesis, and it is Phase 1's job to evaluate it.**

That decomposition presupposes a great deal: that the bottleneck is control over *modification of
already-acquired knowledge*; that those four functions are separable; that they are the right
four. Two independent analyses of the earlier brief both concluded, in passing, that the harder
problem may be *discovering which pieces of a world are the reusable causal ones at all*, and
that controlling updates to a factorization you were handed may miss the point entirely.

Treat "plasticity control over four functions" as **one hypothesis on the list your diagnosis
must weigh**, alongside whatever else Phase 1 turns up. If it survives, say why. If your
diagnosis points elsewhere, follow the diagnosis and say so plainly. That outcome would be worth
more than a compliant answer to the original framing.

---

## 4. How to use biology, in both directions

The rule has two halves and the earlier brief only stated one of them.

**Biology is never justification.** That a brain has a structure resembling your component is not
evidence that your component works. Neuroscience cannot validate an engineering claim, and a
result on a laptop cannot validate a neuroscience claim. Keep those ledgers separate.

**Biology is an excellent source of hypotheses and constraints.** Living systems solve the
problem in §1 under conditions that machine learning routinely ignores: they cannot stop the
world to retrain; they cannot revisit the original data; they must remain functional while
learning; they operate under a hard energy budget; they must decide *at the time of experience*
what is worth keeping, without knowing what will be needed later. Any of those constraints, taken
seriously, changes what an algorithm is allowed to look like.

So the productive question is never *"what structure does the brain have here?"* but:

> **What computational problem is this biological system solving, what constraints does its
> solution respect, and which of those constraints do our systems violate without noticing?**

A constraint that biology respects and machine learning quietly ignores is one of the strongest
leads available to you.

---

## 5. Two traps to name in your diagnosis

**In-context substitution.** A large model with a long context can appear to carry knowledge
across episodes simply by having the previous episode in its prompt. That is not the phenomenon
in §1; it is available to every baseline; and it will silently explain away any result unless the
context is cleared between episodes and the only surviving channel is the one under test. Any
claim about knowledge surviving a discontinuity needs that control, designed before the mechanism
it is meant to isolate.

**The rename.** Most ideas in this area map onto something the field already has under another
name — elastic weight consolidation, replay, gating, adapters, retrieval augmentation, learned
masks, changepoint detection. Discovering that yours is one of them is a legitimate and
publishable outcome, but only if you looked. Phase 3 makes this rigorous. **Phase 2 explicitly
suspends it**, because applying it during generation kills exactly the half-formed ideas worth
developing.

---

## 6. What would count as success

In descending order of value, and note that the first two do not require a working mechanism:

1. **A correct, well-evidenced diagnosis** of why this class of problem defeats current methods,
   precise enough that other people can attack it. This alone justifies the programme.
2. **An airtight negative**: candidate repairs specified precisely enough to be checked, each
   shown to reduce exactly to an existing method, with the mappings. The literature is full of
   brain-inspired claims nobody has ever stated precisely enough to refute. Doing that properly
   is a real contribution.
3. **A bounded positive**: an operation that measurably helps under stated conditions, whose
   novelty survives audit, even if it does not transfer.
4. **A transferable operation** that survives audit, isolation, resource matching and a change of
   domain.

An empty surviving set is a valid completion. A programme that ends at (1) with a sharp diagnosis
and no mechanism has done its job. **Do not manufacture a positive result, and do not treat an
unfinished study as a completed one.**

"Field-defining" is an ambition, not a gate. Nobody certifies it; the field decides later. Aim at
being right.

---

## 7. Separation

- Your directory is `~/ARC_Independent_Lab/`. Everything you create lives inside it.
- Never read from or write to `~/ARC_AGI3_Plasticity_Lab/`, or its GitHub repository.
- Your git remote is your own repository, created for this programme.
- Your model allowance is the one attached to the runtime you are in. Nothing you do should
  consume the other programme's.
