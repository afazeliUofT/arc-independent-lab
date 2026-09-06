# Ryan et al. (2015): supplied article and recovered supplement

Date accessed/read: **2026-09-06**. Phase 1 source analysis, not an independent reviewer verdict. No mechanism proposal.

## Source identity and completeness

Tomás J. Ryan, Dheeraj S. Roy, Michele Pignatelli, Autumn Arons and Susumu Tonegawa (2015), *Engram cells retain memory under retrograde amnesia*, Science 348(6238), 1007–1013. **Published journal article, not a preprint.** [DOI](https://doi.org/10.1126/science.aaa5542), accessed 2026-09-06.

The supplied `science.aaa5542.pdf` contains eight PDF pages. PDF pages 1–7 contain the complete published article, journal pages 1007–1013. Page 1 also contains the preceding materials-science article's ending, and page 7 begins the next article; neither is Ryan evidence. PDF page 8 is a publisher summary and rights page. The supplementary-materials notice on journal p.1013 identifies Materials and Methods, Figs. S1–S13 and reference 41, but those materials are **not in the supplied PDF**.

Main-PDF SHA-256, checked against `SUPPLIED_PAPERS_001_MANIFEST.json`:

`b306ff140f37d1aa02bf0e1d20869219bbdb260c85a3baa671bc3eef5926b308`

The missing supplement was subsequently retrieved from the EMBL-EBI BioStudies deposit linked to PMC5583719. **No repeat human fetch is needed to obtain readable methods.** [BioStudies record](https://www.ebi.ac.uk/biostudies/studies/S-EPMC5583719) and [deposited supplement DOCX](https://www.ebi.ac.uk/biostudies/files/S-EPMC5583719/NIHMS900165-supplement-Supplemental_Information.docx), accessed 2026-09-06. The downloaded DOCX identifies the same title/authors and contains Materials and Methods, all S1–S13 captions and images, and references. Its complete text was read; S4 and S8–S13 images were also inspected.

Retrieved file: `private_sources/request_batch_001/ryan_supplement_retrieved.docx`, 11,735,205 bytes. SHA-256:

`1845941476a8942e58f3a617aff27e33c7b94607d47fec62b3fd20900ab2ea8f`

The supplied PDF, retrieved DOCX, full extractions and rendered images remain in ignored `private_sources/`, not in the public repository. This note contains the provenance and analysis needed to find and recheck the source.

Retrieval record: the publisher supplementary URL and PMC binary URL failed through the browsing tool; the BioStudies record was indexed, and direct HTTPS retrieval of its deposited DOCX succeeded with status 200 and the correct DOCX media type. The successful retrieval was a public download, with no credentials.

## Version and locator correction

The supplied published article has **five** main figures. The [PMC author manuscript](https://pmc.ncbi.nlm.nih.gov/articles/PMC5583719/), accessed 2026-09-06, and recovered supplement use an earlier four-figure arrangement in several references:

| Subject | Supplied published article | PMC manuscript/supplement reference |
|---|---|---|
| Reconsolidation | Fig.4A, p.1011 | Fig.3D |
| Context-specific fear inception | Fig.4B, p.1011 | Fig.3E |
| Downstream amygdala activation and engram overlap | Fig.5, pp.1011–1012 | Fig.4 |

Do not silently transfer figure numbers between versions. The recovered supplement's reconsolidation prose also gives a shorter sequence than the published Fig.4A schedule; exact reconstruction of that particular experiment remains version-dependent. No inference here depends on reconciling that sequence. The identity of this deposited supplement is established; byte-for-byte concordance with the publisher's current supplement is not established.

## What the supplied published article actually supports

The strongest observation is a within-paradigm dissociation. After contextual fear conditioning, anisomycin-treated mice froze less than saline controls when returned to the training context on day 1. On day 2, stimulation of dentate-gyrus cells tagged around training elicited freezing in a distinct context in both groups. On day 3, the anisomycin group's deficit under natural contextual cues remained. The main behavioral groups are saline n=10 and anisomycin n=8; no-shock groups are n=4 each. These schedules, controls and reported significance tests are in published Fig.2A–E, p.1009, which was visually inspected. [Main article](https://doi.org/10.1126/science.aaa5542), accessed 2026-09-06.

The no-shock controls matter: stimulating a similarly tagged neutral-context ensemble did not simply cause freezing. Published Fig.3A additionally reports place avoidance, and Fig.4B tests context specificity through later fear association. These constrain a nonspecific motor explanation; they do not reveal the full content of a remembered episode. The behavioral observations therefore support survival of some experience-specific information accessible through artificial stimulation, while leaving its completeness unknown. [Main article, pp.1009–1011](https://doi.org/10.1126/science.aaa5542), accessed 2026-09-06.

Published Fig.1G measures whether labeled CA3 cells respond to stimulation of labeled DG terminals. Fig.5 measures downstream activation and overlap of activity markers. Neither reads out an entire synaptic wiring pattern or establishes that a particular connection pattern is the unique storage substrate. The authors' connectivity-based account on p.1013 is an interpretation of these observations, not a separately demonstrated identity between connectivity and memory content. [Main article, pp.1008–1013](https://doi.org/10.1126/science.aaa5542), accessed 2026-09-06.

## Decisive supplement findings

The following concise record is based on the [deposited supplementary methods and figures](https://www.ebi.ac.uk/biostudies/files/S-EPMC5583719/NIHMS900165-supplement-Supplemental_Information.docx), accessed 2026-09-06:

- S12: after CA1 encoding disruption, CNO mice still showed significant light-induced freezing (p<0.05), but less than saline: 9.3±1.6% versus 18.2±1.3%, p<0.0005; n=13 versus 11.
- Spine analysis: four cells per group, ten dendritic fragments per cell. Fig.1F's N=40 is fragments, not mice.
- S4: anisomycin-group tagged cells had increased input resistance and 31% greater excitability than untagged cells.
- S9: cycloheximide replication, n=9/group; contextual freezing decreased, while stimulation elicited freezing.
- S10: reduced Arc-positive cell fraction one hour after treatment; not a direct measurement of all protein synthesis.
- S11: delayed anisomycin, n=11/group; no reported contextual-freezing deficit.
- S13: stimulation response at day 8, saline n=7, anisomycin n=8; natural-cue deficit measured on day 1.
- Methods: behavioral scoring, ex vivo experiments and cell counting used blinding; manual video scoring followed randomization. Behavioral animals were male. Spine-image order was randomized. OptoPA excludes extreme zone occupancy. Granule cells selected as engram cells for analysis had to respond to stimulation with an action potential.

## Consequences for our diagnosis

**Correct the categorical encoding-control language.** The main article says the encoding intervention prevented later light-evoked retrieval. The recovered S12 data describe a reduced response with residual light-associated freezing. A binary narrative in which artificial stimulation rescues access failure but never encoding failure is too strong for these data. An incomplete disruption of encoding is compatible with the residual response; the experiment does not establish which portion of that response reflects retained information. This is why reading the requested methods changes our interpretation.

**Retain the access/storage distinction without claiming clean isolation.** Artificial stimulation can be substantially stronger or otherwise different from natural cue input. Preserved performance under it does not establish that every component needed for ordinary recall remained intact. A mixed account involving both degraded representations and an elevated retrieval threshold remains compatible with the reported dissociation. The observed excitability difference reinforces the need to avoid treating anisomycin as a single-variable manipulation of storage.

**Do not equate a nonsignificant group difference with full restoration.** The paper repeatedly describes similar light-induced responses; its reported tests are not equivalence tests with prespecified margins. The justified statement is that both groups respond and the reported comparison does not detect a difference. Full recovery of the underlying information is a stronger, unmeasured proposition.

**Respect units of replication.** A fragment-level N=40 cannot be reported as 40 independent animals. The methods do not specify mouse-level independence for that spine analysis sufficiently to resolve clustering here. This limits the precision we can assign to the morphological evidence; it does not by itself invalidate the separate behavioral experiment.

**Keep the temporal claim exact.** Day-8 stimulation demonstrates a response at day 8. Without a contemporaneous natural-cue test in that experiment, it does not itself show that natural-cue amnesia was still present on day 8.

**Limit transfer to AI.** The admissible diagnostic lesson is methodological: poor task performance alone underdetermines acquisition, retention and access failures. Recoverable information must be tested under a changed access condition, with costs and intervention strength made explicit. This experiment does not establish that AI and mouse failures share a biological mechanism, nor that a proposed AI memory repair follows from it.

## Remaining bounded uncertainties

No unavailable full-text claim is needed for the qualified access-versus-storage distinction above. Publisher/deposit version concordance, animal-level clustering for some cellular analyses, quantitative completeness of protein-synthesis inhibition, and reconstruction of full remembered content remain unresolved. If a later argument depends on a clean encoding-failure negative control or exact reconsolidation schedule, first obtain the current publisher supplement and compare it with the deposited file; if the discrepancy persists, request clarification rather than inventing a reconciliation. No additional paper request is necessary for the present bounded Phase 1 use.
