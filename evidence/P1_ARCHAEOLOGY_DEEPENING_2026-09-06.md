# Phase 1 archaeology: retrieval, rule discovery and hypothesis elimination

Date and source access date throughout: **2026-09-06**. Bounded primary-source pass by a collaborator sharing the investigator's tools and filesystem; **not an independent review**. This extends the initial archaeology and the supplied Drescher/Minton corrections. It proposes no repair, candidate, ranking or novelty judgment.

The important historical correction is that a lineage can replace a defective operation while keeping its original computational objective. Reasons for rejecting an early implementation must therefore be checked against a particular version. Conversely, continued publication does not establish that a method satisfies this programme's conjunction of acquisition, persistence and novel reuse.

## 1. Analogical retrieval: access can fail before an otherwise capable comparison

**MAC/FAC, 1995.** The input is an existing collection of structured descriptions and a probe. A first filter compares predicate-frequency vectors; a second performs structure-sensitive matching on the surviving descriptions. The vectors omit argument bindings. Thus storage, initial access and relational comparison are distinct operations. The authors rejected their earlier match-network-per-memory-item approach on computational and psychological timing grounds. They also identify vocabulary growth as unresolved in their implementation. These are documented design objections, **not evidence that analogy research was abandoned**. [Forbus, Gentner and Law, *MAC/FAC: A Model of Similarity-Based Retrieval*, published journal article, §§3.2–3.3, 7.1.3](https://groups.psych.northwestern.edu/gentner/papers/ForbusGentnerLaw94.2b.pdf), accessed 2026-09-06.

**2026 inference:** hardware changes feasible comparison costs, not distinctions absent from the first filter's input. An item excluded there cannot be recovered by improving only the later matcher. This pipeline consequence is not an attribution to current AI. Present full-memory matching cost was not measured.

## 2. Structure mapping: one old computational objection really is obsolete

**SME lineage, 1986–2017.** The developers report three historical restrictions: small comparisons, hand-coded descriptions and weak integration with other processing. They replaced exhaustive merging of partial mappings with greedy merging, trading guaranteed optimality for affordable search. In the later instrumented corpus, actual intermediate structures were often much smaller than worst-case bounds. The study times recorded comparisons outside their originating simulations; those measurements do not include the full cost of acquiring and encoding the knowledge. Input remains structured descriptions, with some task constraints supplied by surrounding models. [Forbus, Ferguson, Lovett and Gentner, *Extending SME to Handle Large-Scale Cognitive Modeling*, published journal article, §§1–2, 4.1, 4.5, 5](https://groups.psych.northwestern.edu/gentner/papers/ForbusFergusonLovett%26Gentner_2017.pdf), accessed 2026-09-06.

**2026 judgment:** “SME requires exhaustive enumeration” is obsolete for the later implementation, through algorithmic development. Bounded-search quality and representation construction remain distinct questions. Worst-case complexity alone does not identify the practical limiting cost. This is a continuing lineage.

The project currently makes source, example corpus and analysis materials available. That verifies inspectability and continued distribution, not present performance on the programme's demand. [Official SME v4 materials](https://www.qrg.northwestern.edu/software/sme4/index.html), accessed 2026-09-06.

## 3. Classifier systems: historical decline has participant testimony

**Historical evidence.** Holmes, Lanzi, Stolzmann and Wilson describe waning interest near the end of the 1980s, systems that seemed too complicated to study and few successful applications in the early 1990s, followed by revival through new models. They specifically connect simplification with making component roles easier to analyze. This is a contemporary account by participants in that revival, with an obvious advocacy interest; it is stronger than an invented fashion story but is not a bibliometric or causal study of the entire AI community. The same account distinguishes persistent uses of older systems from newer branches. [Holmes et al., *Learning Classifier Systems: New Models, Successful Applications*, author-hosted preprint/manuscript, §§1, 4–6](https://www.eskimo.com/~wilson/ps/ipl2000.ps.gz); [subsequently published 2002 journal record](https://doi.org/10.1016/S0020-0190(01)00283-6), accessed 2026-09-06. Publisher-version identity was not verified.

**2026 judgment:** the complaint that no analyzable alternative exists within the lineage had already lost force in that account. This establishes an expired objection to the entire family, not that the original complicated system has become easy to understand simply because computers improved.

**Primary method behind the revision.** Wilson explains why average payoff alone can give an accurate local rule and an inaccurate overgeneral rule the same reproductive value. XCS separates prediction, prediction error and fitness; its genetic search runs in local match sets. The experiments deliberately use supplied inputs with expressible regularities. The paper explicitly acknowledges that its comparison with ZCS also changes action selection, so the performance contrast does not isolate fitness alone. It learns payoff predictions, not a general next-observation model. [Wilson, 1995, *Classifier Fitness Based on Accuracy*, published journal article, §§2–4, 5.1–5.3](https://www.eskimo.com/~wilson/ps/xcs.pdf), accessed 2026-09-06.

**2026 inference:** multiplying computation without changing that earlier criterion does not itself make equally rewarded but differently reliable rules distinguishable to the criterion. This is a conditional objective mismatch, not a theorem that every strength-based system must fail. Evidence of improvement within the lineage counts against treating its early failures as a refutation of rule discovery.

The official GECCO 2026 track explicitly includes learning classifier systems and evolutionary rule-based systems. This establishes an active research venue, not a prevalence estimate or success claim. [GECCO 2026 EML track](https://gecco-2026.sigevo.org/Track?itemId=53), accessed 2026-09-06.

## 4. Version spaces: more data can eliminate the right answer under the wrong assumptions

**Hirsh, 1994.** Strict candidate elimination assumes a supplied hypothesis language containing a classifier consistent with all labels. Inconsistent data can empty that set. Hirsh's extension treats each observation as compatible with a specified neighborhood of possible instances and intersects the resulting hypothesis sets. Too narrow a neighborhood can still collapse the set; too broad a neighborhood can preserve excessive ambiguity and incur large costs. The method requires the language, generality operations and neighborhood assumptions; it does not discover all of them. The appendix separates per-update costs from growth of the boundary representation across examples. The paper expressly does not establish superiority to competing methods. [Hirsh, *Generalizing Version Spaces*, published journal article, §§2–3, 6.1–6.4, 9, Appendix A](https://link.springer.com/content/pdf/10.1023/A%3A1022600917598.pdf), accessed 2026-09-06.

**2026 judgment:** “version spaces cannot handle any inconsistent observations” was already too broad in 1994. Hardware can change feasible set sizes; it cannot make an empty feasible set nonempty under unchanged constraints. Relaxing consistency can exchange contradiction for unresolved alternatives. No defensible community-wide abandonment history was established for this line.

## 5. What this changes in the diagnosis

These histories motivate distinctions to test, not mechanisms to adopt:

| Conditional diagnosis | Observation that would undermine it in a particular system |
|---|---|
| The task-relevant representation survives, but an earlier access stage excludes it. | The representation reaches the decision process and failure still occurs under the same downstream conditions. |
| Learning selects knowledge using a statistic that cannot distinguish two kinds of rule that differ in future usefulness. | The implemented selection statistic already separates those kinds, and both receive comparable opportunities to affect learning. |
| An apparent loss is the consequence of maintaining an inconsistent or misspecified set of hypotheses. | A suitable hypothesis remains feasible and accessible under the declared language and evidence interpretation. |
| A historical computational objection applies to an operation no longer performed by the version being assessed. | The actual implementation still performs that operation, or its replacement has a separately measured limiting cost. |

These are falsifiable conditional attributions. None has yet been established as the dominant cause in current AI. In particular, source-provided features, predicates and expressive languages must not be counted as knowledge that an agent acquired through interaction. Neither attractive terminology nor the age of an idea supplies evidence for acquisition.

The supplied-source corrections remain binding: Drescher's mature specification includes predictive maintenance, and Minton's later utility validation remeasures matching cost and frequency while retaining an earlier savings estimate. This pass does not revive either superseded simplification. See `DRESCHER_SUPPLIED_METHODS_2026-09-06.md` and `MINTON_SUPPLIED_METHODS_2026-09-06.md`.

No measured case of a **hardware-only** historical obstacle becoming irrelevant in 2026 was established in this bounded pass. It would be misleading to manufacture one. What was established is narrower and useful: some objections were overcome within the historical lineages themselves, while other restrictions concern the information supplied or the criterion being optimized. Present typical-case cost remains a measurement question.

## 6. Reading coverage, version identity and unresolved access

All source access dates are 2026-09-06. The five core works above were accessed beyond their abstracts. Long papers were selectively read at the specified methods and limitations; **none is claimed read cover to cover except the short Holmes et al. manuscript**. No publisher PDF or source text is included in this public evidence note.

| Work and local private copy | Verified reading scope |
|---|---|
| MAC/FAC, `private_sources/archaeology_deepening/macfac1995.pdf` | PDF pp.1–7, 20–25, 51–54. Scan header says 1994; added author citation and publisher record say 1995. No independently verified human-effect size is adopted. |
| SME, `private_sources/archaeology_deepening/sme2017.pdf` | PDF pp.1–6, 25–28, 33–37; §4.3 browser text. No code audit, replication or full originating-encoder inspection. |
| XCS, `private_sources/archaeology_deepening/xcs1995.pdf` | §§2–3; multiplexer setup/state; Woods2 interface; §§5.1–5.3. No code audit or comparator rerun. |
| Hirsh, `private_sources/archaeology_deepening/hirsh1994.pdf` | §§1–3, 6.1–6.4, 9 and relevant Appendix A argument. The multi-domain empirical details and full prior theory are outside this pass. |
| Holmes et al., `private_sources/archaeology_deepening/lcs2002.ps` | Entire eight-page author manuscript, including references. Converted locally for reading; page 1 visually checked because extraction corrupted digits and split words. Its relationship to the final publisher wording remains unverified. Used as participant history, not as primary verification of every application it cites. |

The author-hosted Wilson 2011 interview could not be fetched through its journal or magazine links. It is not needed for the narrower historical conclusions now supported by the retrieved manuscript, so no human request is warranted for this pass. A claim about why these approaches lost wider AI influence, rather than why their authors changed particular implementations, remains unresolved and would require broader project histories or uptake evidence. No finding here depends on an inaccessible abstract.

Retrieval/conversion failures are retained in `P1_ARCHAEOLOGY_DEEPENING_ERRORS_2026-09-06.jsonl`. The source manifest records original private-copy hashes; these identify literature evidence, not newly generated experimental results.
