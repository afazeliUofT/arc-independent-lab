# Reference encoding, accounting and interruption contract

**Implementation reconciliation:** This document is retained as design analysis. The adopted043 development ruler and explicit remaining admission limits are in `P3_REFERENCE_ACCOUNTING_043.md`. Binary codec, arena sharing and BIT_WORK_V1 alternatives below were not implemented.

Status: **bounded prospective draft for checkpoint043; no candidate, scheduler, prediction fit or profile executed**. This supplies implementable choices for the next reference adapter. It is not an immutable experimental ruler, a measured budget, an independent verdict or an amendment to the original035 file. The parent PI must reconcile it with the other043 analyses before pinning a final contract. Existing042 scientific panel, B_env285, controls, thresholds and non-admission remain intact.

## 1. What is fixed and what still needs a named choice

Frozen035 fixes the historical-predicate and recipe-update algorithms, but does not uniquely determine their executable serialization, logical storage layout, operation prices or all interruption points. At an unlimited budget many encodings agree. At a finite budget their cost and tie order can change which predicate is selected and which state is available. Therefore these are **prospective adapter choices**, not details to select after a result. They should have their own version and hash and appear in the final design review.

The scope here is only the042 interface: one observation field, five opaque observation indices, five opaque action indices, W2/S3/K4/L5/V2/q4, one physical block. Generalizing to additional field types, new block inheritance, stochastic resets or a different grammar would require another contract. There is no need to settle unused N2/N4/N5 parameters to implement this adapter.

The following distinguish legitimate completion from a scientific change:

| Choice | Classification and consequence |
|---|---|
| Equality leaf has Boolean size one; NOT adds one; AND/OR add one plus children | Already fixed by accepted042 completion; treating equality operands as extra Boolean nodes would change its grammar |
| Total order for equal-size literal trees and equality operands | Prospective completion affecting finite greedy ties; publish explicitly |
| Observed constants and their admission time | Information-sensitive completion; never use a later validation token in an earlier update |
| Validation assimilation after scoring, including completed prefixes | Already adopted in042; preserve chronological order and interruption evidence |
| Work prices, bytes, sharing, reservations and resume points | Resource-sensitive completion requiring a versioned ruler before measurements |
| Semantic deduplication, dropping self equalities, feature replacement, gate removal, block restart or target fitting | Changes to the stipulated candidate; not ordinary implementation |

No missing primary paper decides these local choices. They are inspectable research design decisions. A formal claim that035 had a unique executable realization would nevertheless be wrong.

## 2. Literal grammar and encounter inventory

### 2.1 Typed terms and values

Use logical term tuples `O(j,k)=(0,j,k)` and `A(k)=(1,0,k)`. In042, `j=0`, observation lags are0,1,2 and action lags are1,2. Type0 is observation and type1 is action. Missing terms produce a typed missing value, `MISSING_O` or `MISSING_A`; within a type it equals itself, differs from every ordinary token, and is never equal across types. MISSING is a term value, **not an extra admissible constant**.

Tokens use supplied integer indices. Terms are ordered by their tuples, preserving numeric field and lag order. Query action `a_t` is a separate prediction-key argument. It does not become action lag one; that lag is the already issued action which produced the current observation. A lag before the most recent RESET is missing. Raw histories retain the boundary and full observed prefix; using W terms does not erase older history bytes.

### 2.2 Exact candidate set

Admit ordered equality leaves:

1. `EQ(term_left, term_right)` for every ordered pair of terms of the same type, including self equality and the reverse ordering.
2. `EQ(term, constant)` for every term and currently encountered same-type constant. A reversed constant/term spelling is not an additional grammar production.

Do not sort or simplify the operands. The literal grammar admits both `EQ(t1,t2)` and `EQ(t2,t1)`, because035 deduplicates identical serialized trees, not all semantically equivalent expressions. Similarly retain NOT(NOT(p)), AND(p,p), both orders of AND/OR children, tautologies and other semantic duplicates. A later exact evaluation cache may share computations, but cannot delete candidates, change their canonical order or pretend cache construction is free.

Tree form is `EQ=0`, `NOT=1`, `AND=2`, `OR=3`, with these arities. Size is one for EQ, one plus child size for NOT, and one plus both sizes for AND/OR. Order candidates by `(Boolean_size, canonical_tree_serialization)`. A workable binary AST serialization is a one-byte operator tag followed by self-delimiting typed operands or child trees. Term operands carry their type, field and lag as unsigned fixed-width32-bit big-endian indices; constant operands have a distinct tag, type and fixed-width32-bit token index. The right operand has an explicit term-versus-constant tag. All042 indices fit this format. Numeric-order preservation, distinct types and arity make the encoding unambiguous. Pin the complete tag table and test byte-level examples before treating it as final.

With encountered observation count `c_O` and action count `c_A`, the equality-leaf count is

`E = 3*3 + 2*2 + 3*c_O + 2*c_A`.

For full encountered alphabets, E=38. At S3 the trees are E leaves, E NOT leaves, E double-NOT leaves, and two ordered E-by-E binary productions; the total is `3E+2E²=3002`. These are algebraic checks for this chosen literal grammar, not measured learner behavior. Enumeration must deliver each serialization once in the stated size/order and stop at the configured S, without importing evaluator role names.

### 2.3 Encounter timing matters

Maintain separate persistent inventories for observed ordinary observation tokens and actually issued primitive action tokens. Declared alphabet membership permits a token in the output distribution; it does not by itself make that token an encountered constant. An action enters its encounter inventory when the issued-action record is durably accepted, not when a proposal merely mentions it. A returned observation enters its encounter inventory when accepted as part of that chronological N1 event. RESET's observation is a real received observation and may supply an observation constant; RESET is not a primitive action constant or N1 transition.

For normal trial actions the chronological event order is issued action, accepted response, N1 transition insertion/update. Predictions, if requested beforehand, are sealed before accepting the response. Each transition update uses the inventory known through that event. A before-trial snapshot retains its own inventory even when later actions reveal more tokens.

Validation introduces a special staging boundary already selected in042. Its actual history is recorded immediately for the two frozen predictors, but live N1 assimilation is delayed until block scoring/finalization. **Replay the encounter events as well as the transitions chronologically when assimilating the batch.** Do not first union all validation tokens into the live inventory and then update the first queued transition: that would let an earlier update use a later observation. The observation-space size remains the complete declared size throughout, irrespective of encounter inventory. Frozen R_before/R_after inventories and predicates never expand during validation or target evaluation.

## 3. Canonical data and retained-memory model

Use a small explicit value model: booleans, bounded identifiers, arbitrary signed integers, reduced rational pairs, byte strings, typed tuples/lists and maps with fixed keys. No floating point, implicit NaN, Python hash order, locale-dependent string order or process-address identity enters scientific state.

A proposed object codec uses one-byte type tags and length-prefixed payloads. Unsigned integers have minimal unsigned magnitude bytes and a length; signed integers have a sign plus minimal magnitude, with one encoding for zero. Rationals are `(numerator,denominator)` with positive denominator and gcd1; zero is0/1. Sequences have element count and element encodings. Maps have unique fixed schema keys in UTF-8 byte order. AST and word ordering use their separately defined numeric-order-preserving encoding, not accidental lexical order of decimal integers. Pin tags, integer-length format, empty values and rejection behavior together; a schema-only promise of “canonical JSON” is insufficient for exact bytes.

Before profiles, the implementation must expose four different quantities:

- Logical live retained bytes, the scientific B_mem quantity defined below.
- Its high-water value, including reservations and simultaneous old/new objects.
- Observed resident memory of the actual implementation and descendants.
- Durable output/archive bytes, including additional observer copies.

They must not be substituted for one another.

### 3.1 Object identity and sharing

Represent logical storage as an object arena with explicit object IDs and charged root/reference records. Creating two independent payload objects with equal contents charges both. Sharing an already existing immutable payload is allowed only through an explicit reference to its ID. Charge that payload once while retained, plus every reference/root record and any lookup/index structures. Do not infer sharing merely because two JSON values compare equal. If content interning is implemented, charge the hash/read/lookup and retained intern table as well.

An append-only history store can be shared by views carrying a store ID and committed prefix endpoint. Earlier views cannot read later appended records. A snapshot can share existing immutable records and prefix views, but carries its own N1 root with the exact T/Phi/inventory/count/search/provenance versions. Mutating live state must create new versioned objects rather than alter an existing snapshot. A proposed `freeze_n1()` therefore returns a **complete logical N1 view**, not just T and Phi; omitted inventory, cursors, witnesses or logs do not become free nonexistent state.

All raw learner observations, actions, histories, T, selected and enumerated syntax actually retained, pair/conflict representation, counts, F/M, utility records, parent provenance, queues, search cursors, temporary work buffers and the two snapshots count. Archived learner records remain charged retained storage; moving them to disk is not deletion from B_mem. The apparatus may keep additional inaccessible evidence copies, but must report their separate output bytes and physical cost; it cannot return them as a free learner memory channel.

An immutable payload may be released from the live arena only when it has no remaining live or archived reference and is not an original evidence record required for replay. Temporary scoring/work objects and superseded caches can be released if their contents are not stipulated retained evidence. Durable scientific logs preserve inputs, versions, selected decisions and reasons sufficient for replay; every primitive meter increment need not be copied into an unbounded scientific log. Specify that evidence schema before relying on deletion to meet a bound.

### 3.2 Reservations and failure atomicity

`reserve_bytes(n, purpose)` checks the **peak simultaneous allocation**, not just the final state size after an overwrite. A copy-on-write replacement holds old and new data concurrently until the commit; both count during that interval. A successful reservation creates charged capacity, and unused capacity can be released once the actual encoded size is known. The reservation itself is visible to the accounting log. A failed reservation has a status and cause, and makes no partial scientific mutation.

Before issuing an environment action, reserve the maximum response/event bytes under the finite alphabet, its durable action record, and a bounded failure/status footer. Also reserve endpoint/completed-word bookkeeping when issuing a last trial action. An unexpectedly interrupted action has its issued record but no invented response or transition. A received response is never silently discarded because a later predicate search or F update runs out of memory.

The footer/emergency channel must be finite and included in the admitted memory/output plan. Otherwise a full memory cap makes it impossible to report why it fired. Meter metadata and the trusted observer's inaccessible bookkeeping need a separate, explicitly bounded apparatus allowance to avoid a self-referential charge for recording each charge.

## 4. An implementable logical work kernel

Use a named abstract cost convention, for example `BIT_WORK_V1`, rather than equating a Python operation with one hardware instruction. A bit-priced logical counter is reproducible across machines; measured CPU and wall-clock remain necessary. The numerical prices below are prospective policy choices. They are not claims about a particular processor's instruction count.

Let `b(n)=max(1, bit_length(abs(n)))`. Each successful primitive operation consumes a dispatch unit plus its declared operand work. Define the following prices from input metadata, so they can be reserved **before** executing the operation or inspecting an outcome:

| Primitive | Proposed price in logical work units, excluding explicit storage reads/writes |
|---|---|
| Boolean NOT/AND/OR or one control branch | 1 |
| Integer compare, equality, add, subtract | `1+max(b(x),b(y))+1` |
| Integer multiplication | `1+b(x)*b(y)+b(x)+b(y)` |
| Nonzero-divisor integer quotient/remainder together | `1+b(x)*(b(y)+1)+b(x)+b(y)` |
| Integer absolute value or sign/zero test | `1+b(x)` |
| Byte copy/read/write of exactly n bytes | `1+8*n` |
| Lexicographic compare of two encoded values | One dispatch plus8 per byte position actually inspected; length comparison charged separately |
| Tuple/list/map construction | Charged element access, index/counter arithmetic, allocations and encoded writes; no unpriced bulk constructor |

The arithmetic prices deliberately include bit growth. They are a declared abstract pricing convention, not a proof of tight asymptotic complexity. Charge reads of integer encodings and writes/reserved output capacity separately under the memory primitives. Pre-reserve arithmetic output capacity using input-derived bounds—addition at most max input width plus one, multiplication at most the sum of widths, quotient no wider than the dividend. An output may use less capacity; do not refund the already executed arithmetic price based on a favorable result.

Euclidean gcd is a loop of charged quotient/remainder operations, comparisons and assignments. Rational construction rejects denominator0, normalizes sign and divides numerator/denominator by their charged gcd. Rational comparison charges both cross products and their comparison. Rational addition, subtraction, multiplication and division use their explicit integer formulas followed by normalization. Do not wrap `Fraction`, `gcd`, a dictionary or sort in one nominal unit while their substantive work goes uncounted.

For exact Brier scores, use the035 sparse-count expression, summing nonzero outcome-count squares in opaque outcome-index order. Fix arithmetic evaluation order: compute n, compute the ordered sum of count squares, add2n then D, square n+D, construct the resulting rational, subtract the rational `2*count(y)/(n+D)`, then add1. Sum before-minus-after Brier differences in validation order and divide by V. Each intermediate rational is normalized under the same convention. Proposal means and comparisons use these exact rationals; no floating tolerance or special negative-score clamp is permitted.

All collection algorithms must have a declared traversal and route through the kernel: word construction and flattening, generation of invalid candidates, deduplication, sort comparisons, predicate truth evaluation, hash/index reads if used, count rebuilding, pair grouping, snapshots and serialization. A source-to-counter map should identify which routine accounts for each required operation. Optimizations may reduce actual logical work, but must preserve the unlimited semantic result and prove that their skipped work is redundant. Never charge an optimized implementation as if a full naive computation ran; never declare the optimization free.

### 4.1 Minimum API and stop behavior

The minimum interface is:

- `charge(opcode, input_metadata)`: deterministic debit before performing the primitive; insufficient remaining budget returns WORK_LIMIT without performing it.
- `reserve_bytes(max_bytes, purpose)`, `commit_object(payload, reservation)`, `release_reference(id)`: explicit storage lifetime and peak checks.
- `record_boundary(kind, version_ids, meter_totals)`: bounded durable scientific boundary record.
- `checkpoint(cursor, expected_versions)` and `resume(cursor, expected_versions)`: resume only exact matching input versions, with all previously consumed work retained.

These are API descriptions, not implemented functions in this checkpoint. `charge` and storage accounting must be trusted, auditable routines; they are not permission for algorithm code to mutate counters or turn metering off. The meter's own increments cannot recursively meter themselves. Keep that apparatus overhead outside BIT_WORK_V1, record its bounded memory/output requirements, and include it in physical profiles. The final report must say that BIT_WORK_V1 is a logical workload measure, not a complete accounting of the host OS, interpreter or observer CPU.

If a long comparison, copy, tree evaluation or loop is resumable, charge completed primitive steps and store its exact next step. No result is published from an incomplete primitive or partial pass. A nonresumable primitive whose reservation succeeds but whose implementation errors is an apparatus failure, not successful work or a scientific zero. Such failures keep the debit/evidence rather than refunding spent work as if nothing happened.

## 5. N1 event and pass transactions

Each accepted normal primitive transition appends to T before its update is considered complete. Assign a monotone T version and chronological index. Update the encounter inventory only through that event. Maintain separate versions for Phi, inventory, count table and conflict representation. Every incomplete search cursor stores all three source versions plus its next candidate/record/operation, partial accumulated gain and completed best candidate. A new input event invalidates it; retain the spent-work record and explicitly retire the stale cursor. A partial best-so-far candidate is not a selection.

A deterministic initial reference schedule should be:

1. Durably accept the event and append its transition; record pending-update state.
2. Rebuild counts under the current Phi for all active T, committing the rebuilt table only when complete. Until then its source-version mismatch makes prediction nonnumeric.
3. Construct the current conflict representation. If it proves the pair set empty, record a complete zero-gain result; no candidate could have a positive gain. If there are conflicts and capacity remains, enumerate the complete legal unselected candidate set in canonical order, evaluating gains on that fixed table/Phi/inventory version.
4. After a complete pass, select the maximum positive gain with prescribed size/serialization ties, if any. Pre-reserve the selected syntax, feature log and new root. Commit the Phi append once. Record the full pass identity, winning gain and tie provenance. If no positive gain exists, record the completed no-selection result.
5. Rebuild counts after the pass as required, and recompute conflicts after a feature addition. Continue with a fresh pass until no positive gain remains, K is reached, or a bound interrupts required work.

A valid versioned count table can avoid a redundant rebuild only through an explicitly declared identity check proving T/Phi unchanged, charged as the actual check. A literal reference can rebuild instead; their cost comparison must use their actual implementations. The original035 phrase “after every completed selection pass” is not permission to use stale counts between updates.

When a complete pass chooses a predicate but its subsequent count rebuild cannot finish, retain the committed Phi and dirty count status. Do not roll back the predicate to gain capacity or use the old counts as if they matched. If memory cannot commit the selection itself, it has not been selected. These distinctions control N3's newly-selected list and must survive interruption.

Conflict preservation can use an exact grouped representation rather than materializing every pair. Group records by current key and then next outcome. The cross-outcome pairs within a key are the literal unresolved set. Store enough ordered record IDs and version metadata to enumerate any requested pair exactly. This preserves all conflicts; a mere total count without their support would not.

For a candidate p, split each current-key group by its Boolean value. Its gain is

`n_0*n_1 - sum_y n_(0,y)*n_(1,y)`,

summed over groups. This exactly counts separated pairs with unequal outcomes and avoids reevaluating every candidate/pair combination. Charge truth evaluation, group reads/writes, multiplications and sums. A bounded conformance fixture must compare this result and selected order with direct pair enumeration. It is an exact implementation alternative, not a different greedy objective.

A global acquisition computation cap is not replenished on a process restart, resumed cursor, next action or checkpoint. If an exhausted update cannot progress, stop acquisition with that literal status. Do not loop retrying it with zero progress, skip it to admit a cheaper action, or add a per-call allowance that evades the total. An external scheduling interruption may resume under the original remaining allowance and unchanged versions. Target evaluation may finish a count rebuild under its separately admitted allowance, as042 permits; it may not resume feature search or assimilate pending training observations.

## 6. N3 state-machine completion

Warm-up executes every single-action word in opaque action order once, with ordinary N1 updates and no scored validation block. Insert those primitive words into F/M in that order. Represent their zero initial proposal utility as an explicit warm-up status with sum0 and available-credit count0; an uncredited mean has proposal value0. This fixes bookkeeping without inventing scored warm-up trials. Every completed word remains excluded from later proposals/coverage even if its credit was unavailable.

At an idle post-warm-up boundary compute `next_t=t+1` for deciding the coverage slot and validation start. Generate/choose the word under next_t. Persist `t=next_t` immediately before the actual trial-reservation attempt; retain it if that reservation or later execution fails. A failure during proposal construction before any reservation attempt does not claim a reserved experiment. This completion resolves the original dependence of selection on the counter that is said to increment immediately before reservation.

For proposal construction, enumerate F by acquisition index, mutation operators in the listed INSERT/DELETE/REPLACE/SWAP order, primitive positions ascending, and M by acquisition index. INSERT includes every boundary from0 through word length; DELETE/REPLACE act at each primitive index; SWAP exchanges each adjacent pair. Construct and charge the literal result before invalid-length/empty filtering where applicable. Deduplicate by exact word bytes and aggregate all parent provenance; do not retain only the first parent. The operative score is the maximum of parent mean utilities, including zero for uncredited parents but preserving negative credited values. Child choice is descending score, ascending length, opaque-index word order, then parent acquisition index. No child is selected until the required proposal traversal/score determination completes.

The coverage slot chooses the first incomplete primitive word in length/lexicographic order without constructing the mutation queue. Noncoverage slots use coverage only when the completed proposal set has no eligible child. A proposal-generation interruption is not evidence of an empty queue and cannot trigger coverage fallback. Direct COVERAGE intentionally skips mutation work; the feedback controls do not receive an unregistered shortcut.

Trial reservation is for RESET plus the whole chosen word, as042 retains. Freeze the before N1 view before Trial, issue/log RESET, then the word's ordinary actions in order, with serialized N1 updates. Preserve partial traces and stop if a required update cannot continue. After the final physical action response, record completed-word status even if later bookkeeping/search fails; any pending F insertion is explicit and must complete before a future selection. Freeze R_after only at the actual permitted after-trial state and record its completeness, without privately finishing its feature search under a fresh allowance.

Validation uses the two frozen views and actual evolving history. For action j in the V block, choose opaque index `(t+j) mod |A|`, ask both predictors before accepting that response, preserve their numeric or nonnumeric statuses, and queue actual events. No live N1 fitting occurs before block finalization. An environment limit can end a partial block; it supplies completed observations and no credit. If a declared computation/memory bound prevents a required prediction or response reservation, stop without an unregistered extra action.

Credit precedence is:

1. Trial or validation physically incomplete: INCOMPLETE, no available utility count and no macros.
2. Complete block with any nonnumeric frozen prediction: UNAVAILABLE, no available utility count and no macros, even if no new predicate was selected.
3. Complete fully numeric block with no predicate selected during the trial: available utility0.
4. Complete fully numeric block with a new trial predicate: the exact rational mean pre/post Brier difference; positive values alone promote macros.

The second rule must precede the no-new-predicate zero gate;035 explicitly refuses to turn a nonnumeric prediction into zero credit. Unavailable credit does not prevent a physically completed trial entering F. A finite scalar credit increments that recipe's available count and sum exactly once. Idempotent recovery cannot award it again.

For positive utility, take all nonempty contiguous fragments of the completed word, deduplicate exact literal words and insert previously absent macros in length/lexicographic order. Preserve every occurrence/credit provenance in acquisition/index order. This gives an unambiguous order to a promotion event that adds several fragments at once. Then finalize credit state and assimilate completed validation events chronologically under042. Any predicate selected during this delayed assimilation belongs to validation provenance and does not retrospectively open the preceding trial's credit gate.

The MACRO_OFF/FEEDBACK_NULL shadow diagnostics must use the same validation and arithmetic logic. MACRO_OFF suppresses only the promotion operation. FEEDBACK_NULL additionally sets operative proposal priorities to zero; it must label measured utility as shadow data, not use it through another queue or stopping decision. Their real savings or extra records are charged according to what is actually stored and computed.

## 7. Mandatory conformance cases before a profile

The next package can test these properties on hand-authored, outcome-isolated fixtures. It need not fit or score the042 worlds to do so:

- Exact grammar membership,38/3002 full-inventory counts, numeric token ordering, self/reversed leaves, typed MISSING and reset lags.
- Chronological encountered constants, including a validation batch where a late token would otherwise leak into an earlier update.
- Gain equivalence for direct pair enumeration versus grouped counts, full-pass selection ties, and no selection from a partial pass.
- Dirty counts after an appended transition or committed predicate; numeric predictions only after a matching count rebuild.
- Snapshot immutability, prefix views, explicit shared versus copied storage, peak allocation and response reservation before action issue.
- Exact rational price/accounting trace including gcd normalization, unavailable-credit precedence, negative parent means, duplicate parents and simultaneous fragment promotion.
- Interrupt/resume at each scientific commit boundary, stale-cursor rejection, preserved spent counters, no duplicated trial/credit and no zero-progress retry loop.
- Each prescribed control's single operative change and the completed-schedule identity between FEEDBACK_NULL and direct coverage when neither hits a resource boundary.

These are meaningful conformance gates because the finite-budget scientific comparison depends on their behavior. They are not observations of candidate efficacy. A later profile must cover cumulative complete-work costs and retained evidence, not just one favorable update. B_comp/B_mem and machine/grid admission remain unset until the final contract, validated code and isolated profiles support them.

## 8. Sources and remaining reconciliation

Inputs read completely for the relevant N1/N3/shared sections and the accepted042 design/config, accessed2026-09-12:

- `docs/P2_SECOND_OPERATION_SPECIFICATIONS_035.md`, SHA-256 `25f3148827d22abbe587a6c2ff0c5a3ff2db1883f70e678f640f16d0f07a7c69`.
- `docs/P3_COMPARISON_DESIGN_042.md`, SHA-256 `597ad1981a90682eea3e8e0118bbea0c9268d2f2edb82a20bce8c1c018d593fb`.
- `configs/P3_CALIBRATION_DESIGN_042.json`, SHA-256 `bd892bf72027ddb3d3ebdee979e4304cad5e36766a87d240acd32d11d783ee5f`.

Canonical repository: [arc-independent-lab](https://github.com/afazeliUofT/arc-independent-lab). The root043 publication record must attach the exact inspected Git commit and this draft's hash; this consultant has not independently fetched or verified the new GitHub receipt.

Before adoption, reconcile the proposed byte tags and work prices with the concrete kernel, classify any differing phase/counter ordering explicitly, and confirm that the evidence schema fits its planned storage allowance. Do not silently mix one draft's grammar, another implementation's cost model and a third state machine while labeling the combination the frozen035 reference. No further paper is needed for this reconciliation. No current result or experimental admission follows from writing this draft.
