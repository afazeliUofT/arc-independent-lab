# Phase 2 population clustering consultation

**Date: 2026-09-06.** Bounded convergence consultation after the complete raw population was frozen. Shared tools and filesystem; not independent review. No literature search, novelty audit, feasibility elimination or efficacy verdict was performed. Selection remains the PI's judgment.

I read all 24 entries in each of `P2_RAW_B1.md`, `P2_RAW_B2.md` and `P2_RAW_B3.md`, together with `P2_GENERATION_FREEZE.json`. All three raw-file hashes match that freeze. This note changes no raw entry.

## What the population count means

The population contains **72 proposals, not 72 independent mechanisms**. Several entries are inversions, limiting cases, different operating phases, or combinations of the same computational move. Source tags such as biology, history and inversion identify generation prompts; different tags do not establish computational independence.

The following **15 primary families** provide a complete indexing. Fifteen is also not an estimate of independent mechanisms. Some families contain distinguishable suboperations; others intersect through a common information dependency. An entry is assigned by its principal proposed operation, even when it also needs operations from another family. This makes the inventory reviewable without pretending that the conceptual boundaries are uniquely determined.

## Complete primary mapping

| Cluster | Underlying computational move | Raw IDs |
|---|---|---|
| C01 | Retain alternative interpretations | B1-01, B1-23, B3-09 |
| C02 | Construct the description language | B1-02, B1-14, B1-15, B1-20 |
| C03 | Bound and revise rule applicability | B1-03, B1-10, B1-12, B1-24, B3-16 |
| C04 | Preserve relations across description changes | B1-05, B1-11, B1-22 |
| C05 | Change what representation selection rewards | B1-04, B1-08, B1-18, B1-19 |
| C06 | Identify the observation process | B1-06, B1-16, B1-21, B2-03, B2-13, B2-15, B2-16, B2-22 |
| C07 | Preserve or restore opportunities for evidence | B1-07, B2-02, B2-04, B2-11, B2-12, B2-18 |
| C08 | Choose actions by the questions they distinguish | B1-13, B2-01, B2-05, B2-06, B2-10, B2-14, B2-23, B2-24 |
| C09 | Broaden interaction coverage | B2-07, B2-08, B2-09, B2-19, B2-21 |
| C10 | Learn whether inquiry obtained its promised evidence | B2-17, B2-20 |
| C11 | Separate or duplicate history-bearing states | B1-09, B1-17, B3-04, B3-14, B3-17 |
| C12 | Maintain compatibility between changing internal interfaces | B3-01, B3-06, B3-07, B3-08, B3-20 |
| C13 | Diagnose or reconstruct access to surviving state | B3-02, B3-03, B3-12, B3-13, B3-15, B3-19, B3-23, B3-24 |
| C14 | Make reading or updating undoable | B3-05, B3-21 |
| C15 | Use continuing interaction or external arrangements for later access | B3-10, B3-11, B3-18, B3-22 |

The companion `P2_POPULATION_CLUSTERS.json` contains the same primary mapping, an inverse index, raw-hash checks, and coverage validation: **72 assigned, 72 unique, no missing or unexpected IDs**. Secondary relationships below do not create additional primary assignments.

## Substantive overlap and distinctions worth preserving

1. **Keeping alternatives versus choosing among them.** B1-01 and B1-23 retain compatible executable explanations; the latter changes the breadth and construction process rather than the basic reason for keeping disagreement. B3-09 applies the same uncertainty-preservation move to readouts. B2-01 then uses such alternatives to choose an interaction. These are separable state and action operations, but they can be consecutive components of one explanation-maintenance process.

2. **Restoring evidence hidden by success.** B1-07, B2-02, B2-12 and B2-18 substantially overlap in preserving or recreating observation conditions. B2-04 acts before the opportunity is lost; B2-11 changes when inquiry ends. Those timing differences matter, but six entries should not be counted as six independent solutions to endogenous evidence loss. B1-16 and B1-21 instead record why observations have their current evidential meaning; they do not themselves restore access.

3. **Several action proposals share a disagreement criterion.** B2-01, B2-14 and B2-23 vary the relationship between a disputed prediction and current reward. B2-05 and B2-06 push allocation to extremes. B1-13 and B2-10 make a future-question family explicit. B2-24 moves the same concern into a stopping decision. These differences specify the demand and allocation rule; they do not by themselves add another operation for obtaining distinguishing observations. B2-17 and B2-20 add a different check: did an experiment obtain the separation it promised?

4. **Observation-channel identification appears in both representation and interaction language.** B1-06 retains explanations involving a changed observer; B2-03, B2-15 and B2-22 seek contrasts that could identify that change. B2-13 and B2-16 use time or reference conditions as part of a contrast. Keeping the alternatives and buying discriminating evidence remain different functions even when they address the same ambiguity.

5. **Rule boundaries and a richer language should not be collapsed.** B1-03 retains a known counterexample; B1-12 carries observed substitution limits; B1-24 refuses an unsupported bridge between evidence types. B1-14 proposes a predicate that changes what the learner can express. B1-10 makes contradiction-driven splitting the default. Retaining a boundary does not automatically discover the condition defining it. B3-16 adds a related expression distinction: a rule can be currently inapplicable without becoming false.

6. **Interface maintenance has several directions.** B3-01, B3-07, B3-08 and B3-20 preserve compatibility while changing which side of the interface moves or which contract is explicit. B3-06 retains changes to responses as the transport object. They are close variants of maintaining a meaning-preserving correspondence, with different state inventories and evidence requirements. B3-02 and B3-23 could help infer such a correspondence, but neither supplies an automatic invariant merely by naming it.

7. **Probe-based access work contains an important information difference.** B3-03 keeps structural relations among probe responses; B3-13 also keeps old responses. Both can diagnose interface drift, but the latter preserves an additional answer-bearing channel. Their overlap should not erase that distinction. B3-12 and B3-24 alter how aggressively a readout is reconstructed; B3-15 and B3-19 restrict the search through structural matching or a history of failed queries.

8. **State separation is a family, not one homogeneous mechanism.** B1-17 separates contexts; B3-04 freezes used states; B3-17 splits after detected conflict. B1-09 withholds generalization by retaining individual encounters. B3-14 duplicates a relation across different encodings instead of merely assigning different contexts to different states. All avoid depending on one shared evolving expression, but the circumstances that trigger separation and the later selection problem differ.

9. **Reacquisition and external persistence change the surviving channels.** B3-10 and B3-22 obtain information again through the world; B3-18 creates another access route through new use; B3-11 leaves a physical cue. Their common reliance on continued environmental opportunities motivates one indexing family, but an external stored cue is not the same operation as reacquiring an absent distinction. B3-05 and B3-21 instead revisit or transform internal state through inversion or a disposable copy.

## Assessment against the PI's developed specifications

After making the raw primary map, I read all of `docs/P2_OPERATION_SPECIFICATIONS.md`. The distinctions below apply to those explicit operations. In particular, the final C4 is narrower than the initial combination of raw B1-03/14/24: it **constructs scope within a supplied finite atom library**. A request for an upstream distinguishing predicate is an output; predicate creation and within-instance library expansion are not implemented parts of C4. The raw map retains B1-14 in description-language construction because the raw entry itself has not changed.

These are assessments of distinctness, not a selection or efficacy verdict.

| Developed operation | Object changed | What makes the move distinct | Remaining dependency or overlap |
|---|---|---|---|
| PI C1 — retain executable alternatives | Live explanation/state pairs within a supplied finite transducer family | Keeps compatible predictions available under identical evidence and an unchanged acquisition policy; does not enlarge the family | Can supply alternatives to inquiry, but its survival filter is separately specified. Enumeration in B1-23 is a raw variant, not evidence of a second independent move. |
| PI C2 — choose an experiment by future decision loss | The next bounded experiment policy and its resulting observations | Uses a fixed externally supplied predictive substrate, future-problem prior and downstream rule; compares evidence value after accounting for resulting world state and cost | Needs predictions about how observations and world state change. The biology-inspired restoration case is one possible experiment within this rule, not a separate implemented restoration learner. |
| PI C3 — align current features with an old interface | A fitted linear map into the reference representation | Leaves encoder training and the old reader fixed while fitting the map from declared anchors and reference activations | The activations preserve historical information; their role must remain distinct from evidence that current features still carry the old distinction. Alternatives or probes can assist access without making C3 the same operation as C1. |
| PI C4 — construct the scope of a proposed rule | A conjunction over supplied atoms bounding the proposed F | Holds F, actions, provenance rule and atom library fixed; retains positive and negative witnesses and selects a boundary within that language | Related to retaining compatible hypotheses, but changes the applicability of a local prediction and returns one chosen conjunction, rather than maintaining C1's full alternative transducer population. It does not implement B1-14's predicate discovery. |

**Judgment on diversity:** these specifications denote distinct operations because they change different objects and state what remains fixed. They do not establish four causally independent theories of the entire problem. C1 and C2 are complementary functions but are separable here because C1's comparison fixes acquisition and C2 can receive an unchanged external inference substrate. C3 concerns a different conditional failure location: access after representational change.

C1 and C4 are mathematically related at a broad level: both use evidence to restrict permissible statements within supplied languages. That commonality should remain visible. Their specified update and output are nevertheless different. C1 preserves the full set of compatible explanatory states and exposes disagreement; C4 selects a scope for a supplied local prediction using a seed, contradictory witnesses and a coverage/length tie rule. C4's chosen scope can still be an incorrect generalization outside the observations, a limit acknowledged in the specification. It would be misleading either to count their shared consistency principle twice as independent explanatory support or to merge the two interventions merely because both reject contradiction.

**Correction to the preliminary consultation:** I initially described the fourth tentative move as a composite including predicate construction. That description applied to the raw anchors as a group. It does not apply to the developed C4, which makes predicate construction an explicit upstream dependency. Witness retention plus boundary enumeration is now one defined scope operation. The historical connection to B1-14 remains a generation link, not an implemented capability.

For subsequent comparison, retain the specifications' distinction between a component's result and a package's result. Combining all four might change several failure locations simultaneously; successful joint performance would not allocate credit among them. Conversely, a shared prerequisite does not make one component unnecessary. No novelty or feasibility conclusion follows from this structural assessment.

## Families outside the tentative four

Coverage-directed interaction, observation-process identification, changes to representation-selection criteria, description invariance, inquiry self-checks, state compartmentalization, reversible access, and declared external persistence remain represented in the frozen population. Their absence from the tentative four is a scope decision, not evidence that they are invalid, already known, or impractical. No such screening was undertaken here.
