# Phase 2 prerequisite: immune learning changes its own selection evidence

**Status:** focused biology consultation before candidate generation. Shared tools and filesystem; not independent review. All external sources and deposits below were accessed **2026-09-06**. The two sources used for the finding and artificial comparison are published papers, not preprints. No candidate artificial mechanism is proposed or novelty screened.

The useful additional constraint concerns acquisition, not the survival of a memory carrier: **a learning system's successful products can change the evidence on which its subsequent variants are selected.** An assessment that holds the incoming examples independent of the learner's outputs removes this coupling. That is a legitimate simplification for some experiments; it becomes an unsupported assumption when their conclusions are extended to systems whose actions change what they can subsequently distinguish.

## Primary biological evidence and its limits

Zhang et al. (2013), *Germinal center B cells govern their own fate via antibody feedback*, J. Exp. Med. 210:457–464. [Published paper](https://doi.org/10.1084/jem.20120150); [main article](https://pmc.ncbi.nlm.nih.gov/articles/PMC3600904/); [deposited full XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC3600904/fullTextXML). Accessed 2026-09-06.

**Evidence class: mouse intervention plus a separate mathematical model.** In primed mice, investigators injected NP-specific IgM variants of different binding strengths after NP-CGG immunization, varying injection timing. Allotype staining distinguished injected from endogenous antibody. Stronger variants entered established germinal centres, increased apoptosis and reduced their size and plasmablast output. Intermediate antibody had less effect later in the response. Early high-affinity antibody accelerated the measured endogenous-IgG affinity increase. Antibody-deficient mice provided complementary interventions. These observations support response-dependent competition over antigen access.

**What the methods decide:** binding rank used multivalent IgM and surface plasmon resonance; serum affinity used an NP2/NP15 binding ratio, not a complete clone-level inventory. T-cell interaction was inferred from germline transcription rather than directly tracked contacts. The model combines antigen masking and uptake restrictions; reproducing outcomes does not establish unique in-vivo sufficiency. One-sided nonparametric tests were used. Effects on antigen localization, retention and downstream signalling remain coupled; the intervention is not a pure change to information alone. Infection protection, unknown-antigen transfer and optimal evolutionary speed were not demonstrated.

The preceding evidence account is deliberately bounded. It does not adopt the paper's stronger optimality or evolutionary-necessity language.

## Operational constraint — our inference

Consider a learner with current state `s`, an external condition `w`, and accumulated products `a` of its earlier activity. Its next evidence may follow a distribution `Q(e | s, w, a)`. Changing `s` changes later `a`; changing `a` can change what is observable even with the original external condition held fixed. The scientific problem therefore includes a changing measurement process, not just fitting a better response to a fixed stream.

This creates three distinctions relevant to the funded problem:

1. The learner may encounter less of a signal because it has successfully acted on the world, because its own activity masks the signal, or because the world ceased producing it. These possibilities need not warrant the same later response.
2. A variant's performance under yesterday's observation conditions need not predict its performance under conditions produced by today's more successful population. Ranking variants without specifying that environment leaves the comparison incomplete.
3. An output can simultaneously be useful action and part of the process that determines future learning evidence. Counting it only as a stored answer omits a causal route by which earlier learning changes later acquisition.

These are deductions about systems with such coupling. The biological intervention supplies a concrete instance of the premise; it does not show that every learning problem has it, or that the organism explicitly represents any of these distinctions. The chosen experiments also do not establish a requirement to preserve current protection while learning: that would need a functional challenge and a joint performance measurement.

## A precise artificial setup that removes the constraint

Dohare et al. (2024), *Loss of plasticity in deep continual learning*, Nature 632:768–774. [Published paper](https://doi.org/10.1038/s41586-024-07711-7); [deposited primary methods](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11338828/fullTextXML). Accessed 2026-09-06. This pass reread the complete **Class-incremental CIFAR-100** Methods subsection, including its extended-data discussion; prior audit: `P1_RETENTION_METHODS_2026-09-06.md`.

The CIFAR experiment adds five classes per increment and retains all currently available training images. Training uses 200 epochs per increment with supplied random image transformations. The model's predictions do not determine which physical scenes are subsequently photographed or which image distinctions remain accessible. Class arrival and augmentation are imposed by the protocol.

**Our mapping:** this arrangement removes output-dependent changes to the source of evidence. It can isolate consequences of previous fitting under a supplied data stream. Its persistent trainability failure remains a real finding under those conditions; this comparison does not explain it away. But the experiment cannot decide whether an interactive learner's later failure comes from impaired fitting or from its own success having altered the observations that would distinguish future cases. Extending that result to the latter setting without restoring this distinction quietly assumes the coupling is irrelevant. The paper itself need not be making that extension.

The claim is confined to this named setup. Reinforcement learning and active control can already include action-dependent observation distributions. No general claim that current AI lacks feedback follows, and novelty screening has not been performed.

## Question carried into generation

**When earlier competence changes which distinctions are observable, what must a learner know about that change to avoid treating self-produced absence of evidence as evidence that no further distinction matters?**

This question constrains a future account: it must say what the agent can observe about its own effects, which alternatives remain identifiable, and whether resolving them is worth the permitted interaction cost. It does not prescribe an immune-inspired component, a selection algorithm, or an unlimited obligation to keep exploring. The biological case makes the coupled problem concrete; whether it is a consequential bottleneck in our eventual artificial setting remains unmeasured.

## Reading coverage and stop rule

- Read approved `DIAGNOSIS.md` §4, `P1_BIOLOGICAL_CONSTRAINTS_2026-09-06.md`, and the immune persistence account in `SCOUT_BIOLOGY_2026-09-06.md`. This pass adds an acquisition constraint beyond their carrier/accounting conclusions.
- Zhang: complete deposited main text, Results/Discussion, Materials and Methods, all main figure legends and model specification read. The image panels were not independently digitized or visually audited; no new numerical estimate is inferred from them. Upstream mouse-line/protocol papers, raw data and model code were not audited. No separate supplementary-material element appears in the retrieved XML.
- Weisel et al.'s 2016 temporal-output study was considered during source discovery, but the [PMC page](https://pmc.ncbi.nlm.nih.gov/articles/PMC4724390/) returned a browser challenge and the [ordinary full-text XML endpoint](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4724390/fullTextXML) failed. Accessed 2026-09-06. Its methods were not read and it supports no claim here. No argument about keeping low-affinity memory for unknown future antigens is adopted from it.
- The focused question is answered by the accessible primary intervention and a concrete artificial comparator. No additional paper request or unbounded survey is needed. The immune pass supplies no new evidence of arbitrary recombination, anticipation of unseen pathogens, superiority over AI, or a demonstrated general repair.
- Local reading copies are under `tmp/p2_immune/` and excluded from scientific publication. The analytical note and `P2_BIOLOGY_IMMUNE_ERRORS_2026-09-06.jsonl` are the durable evidence artifacts. No project state, approved diagnosis or other programme was edited.
