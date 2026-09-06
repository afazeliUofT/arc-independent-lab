# Jones et al. (2012): supplied main-article audit; supporting methods still missing

Date accessed/read: 2026-09-06. Programme: ARC Independent Lab, Phase 1. Role: bounded research consultation, not an independent review. This note audits one biological source and access coverage; it does not propose a mechanism, experiment, or novelty claim.

## Source identity, version, and coverage

Joshua L. Jones, Guillem R. Esber, Michael A. McDannald, Aaron J. Gruber, Alex Hernandez, Aaron Mirenzi, and Geoffrey Schoenbaum. **Orbitofrontal Cortex Supports Behavior and Learning Using Inferred But Not Cached Values.** *Science* 338(6109), 953–956, 16 November 2012. Submitted 16 July 2012; accepted 27 September 2012. DOI: [10.1126/science.1227489](https://doi.org/10.1126/science.1227489). Publisher: [article landing page](https://www.science.org/doi/10.1126/science.1227489). Primary deposit identifier: [PMC3592380](https://pmc.ncbi.nlm.nih.gov/articles/PMC3592380/); manuscript identifier NIHMS446679. All access dates in this note are 2026-09-06.

The user-supplied `/workspace/scratch/d2a3782c2235/upload/science.1227489.pdf` is a five-PDF-page publisher reading copy, with Jones article matter across printed pages 953–956, adjacent-article material at its boundaries, and a publisher article-information page. It is the final published article, not the Supporting Online Material. Main article prose, reported statistics, both main figures and captions, references, and the supplement pointer were read. Existing private renders of printed pages 954–955 were visually inspected. The adjacent articles are not evidence for this note.

| Reading copy | SHA-256 | Coverage |
|---|---|---|
| User-supplied `science.1227489.pdf` | `636e76a71b2ea3b15e167bc6cb7d7364f92e6f4ed61494b152b465012a499444` | Main article and main figures read; no SOM present |
| Private extraction `private_sources/request_batch_002/jones2012_main.txt` | `55a8f8aa7528b9f0d2cd5abc793d7bfbfffbf8bdf9b01b622a1145711df72b70` | Text extraction checked against rendered figures/pages |
| Supporting Online Material / PMC `NIHMS446679-supplement-Supplementary_Data.docx` | Unavailable; no source bytes recovered, therefore no hash | **Unread**; filename and 1.4 MB size identified only from primary-deposit search indexing |

The supplied main article explicitly lists the missing supplement as **Materials and Methods; Supplementary Text; Figures S1 and S2; References 31–36** at its printed page 956. Its original publisher pointer is [338/6109/953/DC1](https://www.sciencemag.org/cgi/content/full/338/6109/953/DC1). Supplement-file identity is not a verification of its contents or version equivalence to the publisher SOM. No abstract-only or search-snippet method claim is used below; substantive findings derive from the supplied main article.

## What was actually manipulated and measured

The behavioral measure was time spent in the food cup during cue presentation. Main figures report cue responding above baseline and show SEM. This is anticipatory Pavlovian approach, not a direct report of an internal representation or an explicit choice between plans.

| Stage | Main-article procedure | Timing and interpretive consequence |
|---|---|---|
| Sensory preconditioning | Bilateral OFC cannulae; 19 control and 16 OFC-inactivation rats. Two days of neutral auditory pairings A→B and C→D; physical cues counterbalanced. | Main Figure 1 places no drug intervention during initial neutral pair learning. Food-cup responding near baseline does not independently verify that both cue-pair memories were acquired. |
| Direct conditioning | Six days of B→sucrose and D→no reward. Both groups acquired the B/D discrimination. | Direct reward learning preceded the critical inactivation. Similar acquisition performance limits a pre-existing gross reward-learning deficit. |
| Sensory-preconditioning probe | Saline or baclofen–muscimol before the probe; three presentations of each directly conditioned cue B/D, with reinforcement as in training, followed by six unrewarded presentations of each A/C cue, counterbalanced. | Inactivation occurred after initial pair learning and reward conditioning. However, the probe session includes reinforced B reminders before the critical A/C measurements; it is not a session devoid of additional reward experience. |
| Inferred-value blocking | A subset of the preceding animals received two days of reinforced AX and CY compounds; X/Y were novel visual cues, counterbalanced, and both compounds delivered the same sucrose reward previously paired with B. Saline or baclofen–muscimol was infused before each blocking session. | Here the intervention overlaps new compound learning, rather than only the final response test. A has an indirect reward history through B; C has a nonreward history through D. |
| Blocking probe | The next day: AX/CY reminder trials followed by unreinforced X/Y presentations. | Main Figure 2 places the inactivation box under blocking, not the later probe. The exact reminder schedule, drug washout, and whether any infusion occurred at probe require the missing methods. The main text does not establish these details independently. |

The direct B/D control is particularly useful: both groups responded strongly to B and weakly to D under the probe infusion. The authors also report an analysis restricted to the first presentation of each direct cue, described as before any reward delivery. That comparison protects the direct-cue result against an explanation requiring repeated within-probe reward exposure. It does not remove the fact that the subsequent A/C probe follows B/D reminder trials.

Controls responded more to A than C; inactivated rats did not discriminate A from C. In the later blocking test, controls responded more to Y than X, whereas the inactivated group did not show that difference. The combined pattern supports a late OFC contribution to behavior using an indirect association and an OFC contribution during subsequent learning affected by that association.

## Reported statistics and their limits

These are the main article's tests, not a reanalysis of raw data.

| Comparison | Main article report |
|---|---|
| Neutral cue responding during preconditioning | Cue × treatment ANOVA: all reported F < 1.27 and P > .29 |
| B/D conditioning | Cue F(1,33)=170.5, P<.0001; session F(5,165)=54.75, P<.0001; cue × session F(5,165)=64.6, P<.0001; treatment main effect/interactions F<1.49, P>.19 |
| First presentation of direct B/D cues at probe | Cue F(1,33)=53.21, P<.0001; treatment main effect/interaction F<1.9, P>.17 |
| Preconditioned A/C response contrast | Cue F(1,33)=14.7, P<.001; cue × treatment F(1,33)=7.33, P<.01; Bonferroni post hoc comparisons reported |
| Responding during blocking | Session F(1,19)=16.53, P<.001; treatment main effect/interactions F<1.44, P>.24 |
| Later X/Y blocking probe | Cue × treatment F(1,19)=7.70, P=.012; controls Y>X after Bonferroni correction, P<.05; OFCi X/Y contrast P>.05 |

The treatment-by-cue interactions matter more than contrasting a significant within-group test with a nonsignificant one. Conversely, nonsignificant treatment effects or X/Y equality tests are not demonstrations of numerical equivalence or identical underlying processes. The figure bars alone do not establish every possible cross-group simple effect. The main article's blocking degrees of freedom suggest a total of 21 analyzed rats, but this is an inference from the report; exact blocking group counts and the subset-selection rule are not verified here. Its baseline comparison for the blocked cue is printed as `t(1,11)=0.67, P=.52`; no sample-allocation claim is based on that unusual notation.

The supplied main article does not give enough information to audit randomization, blinding, initial enrollment versus analyzed sample, exclusions, misplaced cannula decisions, loss of animals between experiments, power planning, assumption checks, exact baseline windows, or the full family of statistical comparisons. Main figures show cannula positions, but do not replace histological inclusion criteria or an infusion-spread assessment. The missing methods must be read before asserting those controls were present or absent in the complete study.

## Inferred versus cached value: warranted reading and alternatives

**What the manipulation isolates reasonably well.** Because initial neutral-pair learning and B/reward conditioning preceded the sensory-preconditioning probe infusion, the selective A/C deficit cannot be attributed simply to the absence of OFC activity during those original acquisition stages. Preserved directly rewarded B responding under the same intervention argues against complete suppression of food-cup approach, gross inability to detect every cue, or complete loss of reward responsiveness. No reward devaluation manipulation was required. This is useful evidence that prior learning can fail to guide later behavior when a required region is disrupted.

**What it does not uniquely identify.** The main article does not separately demonstrate that A→B and B→reward component memories remain intact under inactivation while only their combination fails. Its late manipulation is compatible with disruption of retrieval/access, relational integration, cue-specific attention, or another operation needed more by indirect responding than by the robust direct B response. A and B were also trained differently and elicited different response strengths. Preserving B performance therefore does not, on its own, isolate a single computation for A.

The authors interpret A's response as inferred value rather than a value cached through direct reward pairing. The main text explicitly directs the reader to supplementary discussion for why sensory preconditioning requires that interpretation. The unobserved alternative most relevant to that boundary is **mediated learning**: B might reactivate its associated A representation during B/reward training, allowing reward-related information to become associated with A before the final A test. The main article alone is insufficient to establish whether, and how, its Supplementary Text or Figures S1–S2 excludes that account. This note does not assert that mediated learning explains the results; it states that the unique-online-inference claim is not fully method-audited without those materials.

The blocking result strengthens the behavioral scope: the indirect cue history affects later learning as well as approach at its own test. But the actual blocker cue A is paired directly with reward during the two AX blocking days. Its informational basis can therefore change within blocking, and aggregated learning-stage responses cannot identify a purely inferred signal on every trial. The re-use of a subset of previously tested animals also makes selection and prior probe/drug history relevant. The missing methods are needed to establish group reassignment, carry-over controls, retraining, and timing before calling this an independent replication or a history-free test of inferred-value blocking.

The paper's statement that ordinary cached-value blocking does not require OFC relies on cited earlier studies (main references 17 and 21), not a newly described matched standard-blocking arm in this article. That contextual comparison is a cited literature claim, not a within-paper control verified in this consultation.

Finally, the authors themselves allow that the associative structure may be stored elsewhere and that their results do not require value to be calculated in OFC. The defensible use here is **selective dependence of indirect-association-guided behavior and subsequent learning on OFC at later stages**. The stronger claim that intact component memories were stored elsewhere and uniquely recombined online by OFC is not directly demonstrated by the supplied main article. This is a regional perturbation result in a small appetitive cue task, not direct evidence for a general-purpose reusable causal-model architecture.

## Retrieval result and remaining source boundary

The pre-existing access log was read before retrieval. Previously failed Europe PMC fullTextXML and modern publisher `jones.sm.pdf` routes were not reissued unchanged. Targeted primary/author discovery located the PMC supplement filename but no accessible author-hosted full SOM. One follow-up from a newly returned, currently indexed PMC article result was used to try to resolve its real attachment link; it still returned the same challenge and was stopped.

New routes and outcomes:

- [Original publisher SOM landing page](https://www.sciencemag.org/cgi/content/full/338/6109/953/DC1): web tool reported a non-retryable safe-open failure.
- [PMC filename path under PMC3592380](https://pmc.ncbi.nlm.nih.gov/articles/PMC3592380/bin/NIHMS446679-supplement-Supplementary_Data.docx): web safe-open failure; ordinary HTTP request returned 404. This may be a path-form failure and is not evidence that the supplement does not exist.
- [PMC instance attachment route](https://pmc.ncbi.nlm.nih.gov/articles/instance/3592380/bin/NIHMS446679-supplement-Supplementary_Data.docx): returned HTML headed “Preparing to download ...” with a JavaScript challenge asset, not DOCX bytes. No challenge was solved.
- [Europe PMC supplementary-files API](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC3592380/supplementaryFiles): returned XML stating `Article with id PMC3592380 is not open access one`. This is an API availability restriction, not a conclusion about every legitimate reader-access route.
- Parent-supplied final candidate: [BioStudies S-EPMC3592380](https://www.ebi.ac.uk/biostudies/studies/S-EPMC3592380) returned a web safe-open failure, and one ordinary request to the [candidate deposited DOCX](https://www.ebi.ac.uk/biostudies/files/S-EPMC3592380/NIHMS446679-supplement-Supplementary_Data.docx) returned `HTTP Error 404: `. No file signature or internal title could be verified. This remains an unsuccessful candidate path, not an established BioStudies file identity.

**Still needed:** the complete Jones 2012 Supporting Online Material associated with DOI 10.1126/science.1227489, specifically Materials and Methods, Supplementary Text, Figures S1–S2 and their captions, and references 31–36; the indexed PMC deposited file is `NIHMS446679-supplement-Supplementary_Data.docx`.

Until that source is available, leave exact infusion dose/volume/site coordinates/delay/duration, histological and subject exclusions, blocking-subset assignment/history, probe/reminder details, and the supplementary case against cached or mediated interpretations explicitly unverified. This does not invalidate the main-article perturbation result; it limits how specifically that result can resolve the programme's distinction between acquiring/storing knowledge and successfully using it later.

Resource priority: **optional, lower-priority strengthening of this source audit**. It is not a blocker for a current diagnosis that stays within the main-article-supported boundary above. Root owns that scoped diagnostic decision; this consultation makes no phase/state recommendation.

Verbatim access-error messages from this consultation are appended in `evidence/JONES_SUPPLIED_METHODS_ACCESS_ERRORS_2026-09-06.jsonl`. Copyrighted reading copies, text, and page images remain under ignored `private_sources/request_batch_002/` or the user-supplied upload location. No full supplement bytes were recovered. This note does not change previous evidence, the diagnosis, ledger, programme state, or parked ideas.

## PI reading qualification, 2026-09-06

The main article says “six unrewarded presentations of A and C.” Its wording alone does not establish the allocation per cue. The table's “of each A/C cue” is therefore too specific without the SOM and should be read as the quoted main-text description with per-cue counts unverified. This changes no contrast adopted in DIAGNOSIS.md. [Published article](https://doi.org/10.1126/science.1227489), supplied copy read 2026-09-06.
