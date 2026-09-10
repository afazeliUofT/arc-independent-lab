# Second operation specifications: bounded semantic consultation

2026-09-10. Shared-workspace consultation on `docs/P2_SECOND_OPERATION_SPECIFICATIONS_035.md` as read before the PI's correction pass. This is not independent review, a novelty audit, an empirical evaluation, or a formal gate verdict. No literature lookup or candidate execution was performed. The findings concern whether the written procedures determine their actions, state updates and information boundaries. Explicit algorithm-family parameters are legitimate; they need values before a later implementation, not arbitrary values chosen during this consultation.

## 1. N4 cannot leave its stated warm-up

**Location:** N4, “State and acquired controls” and “Crossed experiment construction”; shared `Effect(w)` definition.

**Concrete problem:** The seed tries the empty word and each primitive action once. Shared `m >= 2` leaves every effect UNTESTED. An effective control requires a REPEATABLE effect, so no control exists, no contrast tuple enters the queue, and the queue scheduler cannot produce any second trial. This is a startup deadlock, independent of the scientific value of the idea.

**Minimal correction:** Complete `m` trials of the empty word and each primitive action before constructing control tuples. Also determine the next action when no effective acquired control exists. Either explicitly stop with `NO_EFFECTIVE_CONTROL_IN_ACQUIRED_LIBRARY`, or use a declared shortlex fallback that obtains `m` trials of the next untested word within `L` and adds its acquired fragments. The fallback better exposes delayed/composite effects, but whichever rule the PI chooses must be written rather than delegated to an unspecified explorer. A exhausted finite word set is a different condition from a temporary absence of controls.

## 2. Define how physical RESET enters N1's history and lag grammar

**Location:** shared “Shared execution and order”; N1 “State and inputs” and “Supplied grammar”; N3 “Construct, execute, then credit.”

**Ambiguity:** `Trial(w)` logs RESET, its observation and every primitive transition, while N1 receives all completed transitions. RESET is introduced separately from the primitive action alphabet. Lags may not cross episode markers, but it is not explicit whether physical RESET creates such a marker or a transition with a special action type. “Action at lag k” and “observation at lag k” also need an exact relative indexing convention.

**Minimal correction:** Choose one representation and use it consistently. A simple choice is: RESET costs and appears in the raw execution log, emits a boundary and initial observation, and is not an ordinary N1 transition. At a pre-transition history ending in `o_t`, observation lag 0 is `o_t`, observation lag k is `o_(t-k)`, and action lag 1 is the primitive action that produced `o_t`; unavailable terms since the most recent boundary return typed MISSING. Validation actions in N3 continue the same history after the chosen word, as already intended. If RESET instead belongs to the modeled alphabet, specify its type and lag behavior explicitly.

## 3. N1 needs a coherent state when search is interrupted or no feature can be added

**Location:** N1 “Update,” especially “unfinished cursor can be resumed” and “After every completed selection pass, rebuild a count table.”

**Concrete ambiguity:** A candidate's gain depends on the complete transition table, selected predicates and available observed constants. Appending a transition before resuming an unfinished pass changes all three possible inputs. Resuming old scores would mix different problems. Separately, a new transition may arrive when `K` is already reached or before a complete pass is possible; the stated count-rebuild trigger then leaves predictions using an old count table despite retaining the new transition.

**Minimal correction:** Bind each candidate pass and its partial scores to a version of `(T,Phi,constant_inventory)`. Either finish that immutable version before admitting a later transition into the pass or restart the pass when the version changes. Update/rebuild prediction counts for every admitted transition under the currently committed `Phi`, independently of whether another predicate is selected. If the computation/memory allowance cannot complete the bookkeeping, expose a pending state and refuse an ordinary prediction from inconsistent tables. Count rebuilds and reserved trace storage count against the declared bounds. A search interruption remains `SEARCH_INCOMPLETE`, never a proof that no separator exists.

## 4. N2 needs query validity and current evidence versions

**Location:** N2 “Trials and panel,” “Role update,” “Reading and recombination,” and “Reset and cost.”

**Ambiguity:** The role semantics correctly require full panel signatures and expressly decline to claim a congruence. The query rule nevertheless lacks a first check for whether `f` and `g` are acquired nonempty fragments and whether both queried compositions fit `L`. It could otherwise issue a conjecture for an invalid reference word. Historical role signatures also survive across blocks while empirical effect tables are block-specific; the rule does not say whether a historical signature can justify a current-block conjecture. A later VARIABLE effect must invalidate an earlier role for current use even when the panel membership itself has not changed.

**Minimal correction:** Type-check the query and composition length before interpreting it. Key usable role signatures by `(block, panel_version, effect_table_version)`, and rebuild or revoke them when any supporting effect changes. Use current-block signatures in the reference rule; return older relations only as explicitly historical proposals if cross-block transfer is intended. Keep all previous signatures in provenance. State explicitly that scheduler combinations range over all acquired `C × F` satisfying `L`, if that is the intended reading, rather than leaving panel-only versus full-context exploration implicit.

**Already appropriate:** Missing/VARIABLE cells do not match, partial overlaps do not become transitive equivalence, and equal endpoints do not imply hidden-state equality or universal substitutability. No strengthening of those claims is warranted.

## 5. N3 needs an exact experiment clock and pending-update behavior

**Location:** N3 “State” and “Construct, execute, then credit.”

**Ambiguity:** `t` is introduced but not initialized or advanced, so the first coverage trial and the validation action starting index are not determined. Warm-up, completed experiments, incomplete trials and completed validation blocks could all produce different plausible clocks. It is also unclear whether a pending N1 update can be frozen as `R_after` and count toward “predicates newly selected during this trial.”

**Minimal correction:** Define the clock explicitly, for example `t` counts post-warm-up experiments started, incremented immediately before choosing the word; apply the coverage condition and validation offset to that fixed value. Other choices are valid if equally explicit. Define a freeze boundary for `R_before` and `R_after` using coherent committed N1 state. If an update cannot reach that boundary, preserve the trace and return a pending/incomplete experiment without utility credit until the specified completion rule is met. Do not credit later unrelated feature updates to an earlier recipe.

**Already appropriate:** New experiments are actually constructed by mutation and macro insertion; flattened words are executed and charged. The local credit depends on subsequent permitted observations and does not claim causal attribution to a predicate. The macro library contains acquired fragments, not an oracle list of complete informative experiments. A negative or unhelpful credit signal is a scientific possibility, not an implementation error to suppress.

## 6. N4 catalogue reads need current support and deterministic mixed statuses

**Location:** N4 “Update” and “Reading and use”; shared revocation of repeatability.

**Ambiguity:** A positive pattern is stored with its six endpoint effects. A later differing observation revokes repeatability, but catalogue retrieval does not explicitly revoke the earlier record's current support. Queries may also have a mixture of positive, negative, untested and VARIABLE restoring candidates; “as appropriate” leaves precedence unspecified. Finally, matching the action word `p c` is insufficient to authorize use of a record from an earlier block if the catalogue survives.

**Minimal correction:** Store historical positive records permanently but calculate current support from the same-block current effect records. Query output should include the ordered supported restorers plus literal per-candidate statuses, or an explicitly defined aggregate precedence. Scope `NO_MATCHING_PATTERN` to the tested candidate set and preserve whether untested candidates remain. Require a matching current block as well as the exact since-RESET action history before executing a catalogued restorer.

**Already appropriate:** The selected pattern establishes only lost and restored observable contrast. It neither identifies a measurement-only change nor proves restoration of the original cause, policy utility or a later useful distinction. The stated weak bridge is scientifically honest and should remain.

## 7. N5 needs a scalar output contract and a finite source-query input

**Location:** N5 “Supplied learning-state interface,” “Lessons and state,” and “Program grammar and search.”

**Ambiguity:** State and query vectors are specified, but `Base(s,x)` has no output type. The grammar constructs a scalar numeric expression, while a generic base predictor can return a vector. “Queries the learner can construct from its permitted encounters” also leaves the source-query generation/selection operation unspecified and potentially imports semantic or target information through a helper. Exact output depends on which source queries become lessons.

**Minimal correction:** Restrict the reference to rational scalar base outputs, or explicitly add a fixed output dimension and tuple-valued program semantics. Treat each source episode as supplying a finite ordered query list with provenance, generated by a named deterministic rule from permitted source encounters. If the list itself is an interface input, declare that this operation learns a reader for that supplied query interface and does not discover query semantics. State the rule for whether available queries mean queries from this source episode or accumulated source episodes.

## 8. N5 macro enumeration and source/target closure should be explicit

**Location:** N5 “Program grammar and search,” “Reference output and target invocation,” and “Later diagnostic contrast.”

**Ambiguity:** The text prescribes size/serialization enumeration, then says cached macros are tried first “only when scores tie.” A score tie is not known before evaluation, so that is not an executable enumeration rule. The final expanded-tree optimum is fortunately unambiguous. Separately, holding target instances out of source lessons is currently emphasized as a later contrast rather than fully defining the reference's source/target data closure.

**Minimal correction:** Preserve size/expanded-serialization enumeration and use macros only for memoized evaluation, or define a deterministic cache-first enumeration independently of scores and retain the existing expanded-tree final tie-break. An incomplete enumeration still cannot claim the exhaustive optimum. Freeze source lessons, source query selection, grammar parameters and the selected program before exposing target-specific state, queries or old answers to the synthesis process. Put the target-instance exclusion rule directly in the operation's data contract; an evaluator can enforce the split without revealing target labels to the learner. Preserve the odd/even source-episode split and the prohibition on using checking errors to choose another program in this pass.

**Already appropriate:** Old source answers, copies, stored lessons, reader constants and learned expressions are charged as channels. Runtime target inference takes only current state and query, and emits a conjecture without an old-answer validation oracle. Target-world interaction is a separate reacquisition variant. The proposed matched-carrier contrast is needed to distinguish a history-bearing target carrier from an answer stored in source material.

## Scope of this consultation

The specifications now identify five different learned objects and concrete generative operations, rather than merely selecting among supplied complete world models. Their strong supplied interfaces remain visible. The finite grammar, resettable blocks and source-change lessons narrow the scientific scope; they do not by themselves invalidate the proposals. The corrections above concern execution semantics and information accounting, not novelty, expected efficacy or practical compute feasibility.

No raw ideas, specifications, state or ledger were edited by this consultation. The PI should apply the selected corrections, freeze the resulting specification, and only then add nearest-method flags as required by the governing Phase 2 order.

## Revision readback during the same consultation

After these findings were drafted, the PI revised the specification. A subsequent read of the relevant sections confirmed the following changes; the original findings above remain a record of the earlier draft, not a claim that each still applies:

- Finding 1: corrected. N4 now completes `m` seed trials and uses an explicit finite-word coverage fallback when its tuple queue is empty, with exhaustion distinguished from no effective acquired control.
- Finding 2: RESET representation corrected. It is now a logged, charged boundary rather than an N1 primitive transition, and its observation begins the new history. An explicit lag-index sentence remains recommended.
- Finding 3: corrected. Cursors carry table, predicate and constant-inventory versions; stale cursors restart with spent computation retained; counts cover completed active-block transitions; unavailable bookkeeping returns `COMPUTATION_INCOMPLETE`.
- Finding 5: corrected for the identified clock and numeric-credit ambiguity. The post-warm-up counter now has an initialization and increment point. Nonnumeric frozen predictions make credit `UNAVAILABLE`, with coherent count snapshots required. The PI also changed the local scoring rule to an exact rational Brier-score difference; this consultation makes no efficacy claim for either scoring choice.
- Findings 4, 6, 7 and 8 were sent to the PI as remaining corrections at this readback. Their eventual disposition must be established from the final specification, not inferred from this draft record.
