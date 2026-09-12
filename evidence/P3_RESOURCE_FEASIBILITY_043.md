# Resource feasibility of the exact calibration reference

Date and source-access date: **2026-09-12**. This is PI consultation and symbolic accounting analysis, not an independent verdict, implementation profile or experimental admission. It uses frozen035 and the accepted prospective042 design. No N1/N3 learner, scheduler, profile fixture or target panel was executed. A scalar arithmetic check evaluated the closed-form formulas below; it did not enumerate histories, candidate trees or treatment outcomes. The source documents are unchanged.

**Finding:** a finite, honest full-work envelope is possible, but a large snapshot or an apparently difficult learner run is not a certificate of the largest cumulative cost. Freeze the equality encoding, accounting units and interruption/resumption policy first. Then validate the optimized gain computation against a small explicit pair reference, and profile separately bounded components with proved full-run multiplicities. Do not write a direct candidate-by-pair implementation for the entire grid without confronting the billions of checks in its conservative envelope.

## 1. Contract and scope of the bounds

The design parameters are `W=2, S=3, K=4, L=5, V=2, q=4, B_env=285`, with one observation field and five primitive action and observation tokens.042 has not set `B_comp`, `B_mem` or numerical runtime admission. Its profile rule requires small, typical and largest work classes, three repetitions, the largest eligible complete-work measurement with a factor-two reserve, and a further 25% audit/rerun allowance for the planned grid. These are prospective design policies, not measured performance. [R1–R3]

The main envelope below is for one logical acquisition run with complete primitive warm-up and the prescribed validation block after each nonterminal trial. The terminal validation may be incomplete when a bound stops the run. A resource or infrastructure interruption stops the admitted run or resumes its recorded unfinished work under the **same** allowance; it does not grant another allowance or permit a completed pass to be repeated indefinitely. These are necessary execution conditions for a finite profile projection. If an implementation continues to schedule new trials after arbitrarily truncated validation blocks, the sharper trial/library bounds below do not apply. Section 5 gives a conservative fallback and identifies why that would require an explicit different completion contract.

The bounds deliberately allow combinations of component sizes that need not occur together in a reachable target trajectory. Such an over-approximation can support conservative resource planning if named accurately. It cannot be reported as a measured worst-case candidate trajectory.

## 2. Grammar inventory: freeze the encoding before counting it

There are three observation history terms, at lags zero through two, and two action history terms, at lags one and two. At maximum encountered inventory there are five constants of each type. A precise proposed serialization completion is:

- `EQ(term_i,term_j)` retains ordered operands; self-equalities are legal.
- `EQ(term_i,constant_c)` has exactly this term/constant orientation.
- Action and observation types are distinct. No constant/constant equality is generated.
- The dedicated typed MISSING value is a term-evaluation result, not an additional ordinary observed-token constant.
- Ordered Boolean children are retained. Only identical serialized trees are deduplicated; there is no semantic, commutative or tautology simplification.

This preserves the literal-tree reading of035, but the executable tags/order and term/constant orientation are still implementation dependencies in042. The accounting contract must state them rather than silently treating one convention as already fixed by its own code. [R1–R3]

Under this explicit completion, the number of equality leaves is

`E = 3^2 + 2^2 + 3*5 + 2*5 = 38`.

Equality tests are Boolean leaves. Size-one trees number `E`; size-two trees are `NOT(leaf)` and number `E`; size-three trees comprise `NOT(NOT(leaf))`, `AND(leaf,leaf)` and `OR(leaf,leaf)`, numbering `E+2E^2`. Thus

`P = 3E + 2E^2 = 3002`.

This includes expressions with repeated leaves and semantically equivalent different syntax. Deduplicating equality operand reversals or Boolean commutativity would change the reference enumeration/tie space unless explicitly justified as a different canonical grammar. Generating a second constant/term orientation would also change this inventory. Do not use 3002 as an unconditional source fact before the completion is frozen.

For the042 world, completed primitive warm-up encounters every observation role: the setters yield both cues, MASK yields neutral, and the two probes from the fixed reset register yield the two probe outcomes. All primitive actions have also been issued. Therefore the maximum ordinary constant inventory is already reached at completed warm-up; no later target observation is needed to build this grammar. Before that point the inventory can be smaller. [R1–R3; deduction]

## 3. Transition and update envelope

Primitive warm-up costs five RESET calls and five ordinary transitions. Each later started trial has at most five trial actions and two validation actions, so at most eight environment calls including its RESET.

Let `r` be the number of post-warm-up trials started, `c` the total issued calls and `n` the completed ordinary transitions. Then

`c <= min(285, 10+8r)` and `n = c-(5+r)`.

Maximizing this simple integer bound gives `n <= 245`: for `r<=34`, the expression is at most `5+7r <=243`; for `r>=35`, it is at most `280-r <=245`. This ignores restrictive coverage scheduling and may therefore overestimate reachability. It remains a safe envelope. Incomplete warm-up cannot exceed it because no scored run may start. [R1–R3]

Consequences at `n_max=245` are:

| Quantity | Conservative upper bound or formula |
|---|---|
| Ordinary transition rows | 245 |
| Unordered transition pairs | `C(245,2) = 29890` |
| Selected predicates | 4 |
| Populated N1 count keys | `min(n,5*5*2^4) <=245` |
| Outcome counts at each key | at most five categories |
| Successful selection passes across the entire run | at most four |

Every appended transition can require a final no-addition pass, and every selected predicate requires one successful pass. If completed passes are not gratuitously repeated and a resume continues its exact cursor, the number of complete candidate passes is at most `n+K <=249`. Reaching K stops further feature selection; this bound deliberately ignores that saving. A stopped partial pass must count its spent prefix, not a full pass and then a repeated free prefix. Version changes can discard work only when recorded; serial updates and the exact-cursor rule must keep total spent work within the declared execution graph.

For a direct reference that reevaluates every candidate on every current row and checks every unordered pair, a conservative cumulative envelope can be sharpened beyond multiplying all maxima:

`sum_rows = sum(i, i=1..245) + 4*245 = 31115`,

`sum_pair_passes = sum(C(i,2), i=1..245) + 4*C(245,2)`

`= C(246,3) + 4*C(245,2) = 2570540`.

The extra four full-size passes cover all possible successful selections. The ordinary per-transition passes use their own table sizes. With the conditional inventory `P=3002`, this yields

- at most `3002*249 = 747498` candidate visits;
- at most `3002*3*31115 = 280221690` Boolean-tree node evaluations when truth values are computed once per candidate/row/pass;
- at most `3002*2570540 = 7716761080` candidate/pair checks if gain uses the direct pair loop.

These are scalar-derived operation counts for the stated reference loop, not measured runtime or a claim that all these events can coexist in one target trajectory. A worse implementation that reevaluates both predicate outputs inside every pair adds that work; it cannot claim the truth-cache envelope while executing the uncached loop. A better indexed implementation must meter its actual different operations.

## 4. The exact algebraic escape from candidate-by-pair work

For each current N1 key, divide its transitions by candidate predicate output `b` in `{0,1}` and observed outcome `y`. Let `n_b` be the number on side b and `n_by` the per-outcome count. The candidate separates `n_0*n_1` cross-side pairs, of which `sum_y n_0y*n_1y` have equal outcomes and were not conflicts. Therefore the exact contribution to gain is

`n_0*n_1 - sum_y(n_0y*n_1y)`.

Sum this integer over current keys. Every counted pair is unordered because the false/true partition gives it one orientation. This is exactly035's pair gain, not a surrogate objective. It preserves the gain maximizer, then syntax-size and serialization tie rules, when all candidates are evaluated completely. [R1; direct deduction]

This removes pair enumeration from the inner candidate loop. A transparent implementation can evaluate candidate truth on rows, accumulate `(current_key,truth,outcome)` counts and finish the formula by key. The cost is row accumulation and fixed-outcome arithmetic per candidate/key. Any truth caches or bitset implementation must separately charge lookups, Boolean work, integer/popcount bit work, allocations and copies. A native `bit_count` call must not become one cost unit regardless of the number of bits processed if the accounting contract claims to count arithmetic bit work.

035 still requires unresolved pair records and their provenance. The grouped gain formula does not authorize deleting that evidence. Pair materialization can occur once per required partition/table version, outside the candidate loop, or use a prospectively defined canonical referenced representation that reconstructs the literal pairs with its reconstruction work charged. Retaining every candidate's full pair list is unnecessary; silently discarding required unresolved witnesses is not an optimization.

**Resolve this before substantial implementation:** define a simple explicit-pair reference on small development fixtures and an optimized grouped-gain implementation. Compare all candidate gains, selected order, complete-pass and incomplete-prefix behavior, count keys, witnesses and status transitions. This validates a meaningful semantic optimization; it is not a learner outcome test. No performance claim should be inferred from the algebra alone.

## 5. Trial, library and proposal envelope

After warm-up every primitive word has already completed and cannot be selected again. Every later completed trial has length at least two; there are only `5^2=25` distinct words of length two. Subsequent distinct words have length at least three.

If `j>=25` post-warm-up trials complete, their minimum total environment cost, allowing the terminal validation to omit both of its actions, is

`10 + 25*5 + (j-25)*6 - 2 = 6j-17`.

At `j=51` this exceeds285. Thus at most50 post-warm-up trials complete and `|F|<=55`, including the five warm-up words. The prefix of an incomplete trial does not add that word to F. An extra terminal reservation may be attempted and rejected without executing a trial; the runner must then stop, not retry the same unaffordable word in a loop.

Warm-up selects no predicates because each action occurs only once. Every later positive utility trial requires a newly selected predicate, so at most four trials can promote macros. A word of length five has at most `4+3+2+1=10` nonprimitive contiguous fragments. Primitive macros already exist. Consequently

`|M| <= 5 + 4*10 = 45`.

This is an upper bound; duplicate fragments, shorter credited words, negative credit or validation-selected predicates only reduce it. A parent word receives at most one numeric post-warm-up credit because completed words are excluded from both selection routes. [R1–R4]

For a parent of length `l`, the direct mutation enumeration generates at most

`(l+1)|M| + l|M| + l + (l-1)`

`= (2l+1)|M| + 2l-1`

raw insertion, replacement, deletion and adjacent-swap products. At `l<=5, |M|<=45`, this is at most504 per parent, or `55*504=27720` raw products per proposal assembly. An insertion can temporarily make a ten-action word before the length-five filter; token-copy and serialization costs must account for the intermediate word. The complete legal nonempty word universe contains `sum(5^k,k=1..5)=3905` words, bounding distinct valid serialized children but not duplicate generation or parent provenance.

Among the first50 post-warm-up indices,12 are coverage slots and38 can require proposal assembly. A possible terminal reservation at index51 adds at most one more assembly. Thus a simple stop-on-bound reference has at most39 such assemblies and at most `39*27720=1081080` raw products across the run. This deliberately allows every call to have maximum libraries, although early calls cannot.

The complete-validation premise matters. If a different wrapper were allowed to finalize arbitrarily many validation blocks early and then keep selecting new trials, a safe environment-only fallback ignores validation costs. It permits at most75 post-warm-up completed trials, since `10+25*3+(j-25)*4 <=285` gives `j<=75`, and hence `|F|<=80`. The sharper55/39 bounds are not valid for that policy. The accepted reference should close this loophole by stopping on an interrupted resource/infrastructure stage and resuming only documented unfinished work under the same allowance, rather than treating absent validation as a free scheduling advantage. This is an execution/accounting boundary, not permission to change the scientific validation contract.

## 6. Arithmetic and memory are finite, but bytes remain encoding-dependent

Within acquisition, each key count is at most245, fitting eight bits for its magnitude. The maximum unordered-pair count29890 fits15 bits. With `D=5`, each add-one count denominator is at most250. A Brier score has a denominator dividing `(n_key+5)^2`.

For two validation steps, a deliberately loose common denominator for the difference of before/after Brier scores and their mean is bounded by

`2 * 250^8 = 30517578125000000000`,

which fits65 bits. The mean score lies between minus two and two, so its reduced numerator magnitude fits at most66 bits under this bound. Comparing two such utilities by cross multiplication therefore has a finite bound of131 magnitude bits. These limits support a bit-cost contract; they do not prescribe a particular gcd, multiplication or serialization implementation. There is no growing repeated-sample utility denominator for one completed recipe in this single block. [R1–R3; direct deductions]

A finite memory envelope must cover more than T and F:

- all ordinary and RESET histories, with explicitly bounded record encodings;
- selected syntax and the full grammar inventory;
- truth caches and all their versions or invalidation records;
- counts, unresolved pair witnesses and feature-selection evidence;
- proposal products or their deduplicated representation with parent provenance;
- utilities, mutation cursors, completed-word exclusions and validation queues;
- the live N1 state and the before/after snapshots needed simultaneously;
- serialized outputs, diagnostic reconstruction state and retained audit history.

Snapshot policy is material. Retaining full copies for every trial and retaining two temporary copies while referencing immutable T prefixes are different memory/work implementations. Either must retain the provenance needed to reconstruct `T0,T1,Phi0,Phi1` for the mandated diagnostics. Shared immutable records count once while physically shared, and creating an actual copy counts both its bytes and copying work. A short digest is not a substitute for the referenced evidence's storage.

Before a largest memory fixture exists, freeze record tags, integer encodings, history references, sorting/provenance encodings, the immutable-sharing policy, and whether all candidate gains or only a specified sufficient certificate are retained for each pass. A finite token alphabet does not by itself bound arbitrarily verbose logs, repeated snapshots or unrestricted error strings. Use a declared bounded evidence format and explicit overflow status; do not silently discard an action response to fit it. Report canonical retained bytes, serialized output bytes and measured process memory separately. No numerical `B_mem` can honestly be derived from object counts alone before those choices.

## 7. How to obtain an honest largest complete-work profile

One danger is circularity: creating a large conflict-heavy state can make N1 fill K immediately, after which it stops exhaustive candidate passes. Such a fixture may be large in memory and cheap over its remaining trajectory. Conversely, a no-positive-gain table can force repeated complete passes without ever adding a feature. The maxima of n, available slots, positive additions, macro growth and provenance size need not coexist in an actual target run.

Use the permitted042 route of **profiled components with a proved full-run projection**, explicitly describing the projection as an over-approximation:

1. Freeze synthetic small, typical and maximum component inputs and hashes before timing. They contain permitted token/term/record structures, never target instance roles, the target transition simulator, acquisition goals or target candidate scores.
2. Include a fabricated equal-window/unequal-outcome conflict case with no possible positive predicate gain, forcing a complete pass. It is an N1 component stress fixture, not a claim of a reachable deterministic042 world trajectory. Its record count is bounded by the acquisition envelope even if its fabricated record combination could not be produced within the target's environmental allowance.
3. Separately profile successful selection plus key/count rebuild and witness update, full grammar/truth-cache construction, maximum proposal mutation/deduplication/sorting with complete provenance, exact rational scoring, snapshot copy/reference operations, serialization and interruption finalization. Include the direct coverage implementation's materially different work.
4. Validate component correctness first. Repeating a corrupted or incomplete largest fixture three times does not make it eligible for a complete-work projection. Preserve failed and interrupted profiles separately.
5. Cover the entire acquisition graph using proven multiplicities, such as at most245 transition additions, at most249 complete selection passes, at most four successful additions and at most39 proposal assemblies for the declared reference. A direct max-size-per-call projection is conservative; the cumulative-size formulas in section3 may be used only when validated implementation work is bounded by those formulas. Include constructor, finalization and serialized evidence costs that do not occur inside the timed update.
6. Profile the same-trace readers, N1 replay, `P00/P10/P11` reconstructions, predicate-deletion interventions and per-decision evaluation separately under their common diagnostic allowance. A bound for online acquisition does not pay for these operations. Their complete multiplicities must be fixed before the grid projection.
7. Apply the predeclared factor-two and25% reserves to the appropriate complete-work and panel projection. Preserve the identity of the fixture/repeat setting each maximum. Such a timing estimate is conservative planning, not a mathematical hardware-runtime guarantee.

The fixed scientific panel has240 worlds, four acquisition arms and20 decisions per world/reader; these are design counts, not executed measurements. Do not multiply only the FULL acquisition timing by the world count and omit the other arms and diagnostics. Do not present a maximum single-update measurement as a maximum full-run measurement. If the component projection is too expensive even before treatment, choose an exact validated optimization or an appropriate measured computing route; preserve the scientific design instead of trimming its panel or thresholds to fit a preferred machine. [R2, R3, R5]

The profile driver should mechanically lack target evaluator imports, target manifest access and target-score output fields. A synthetic component may instantiate a data structure or update routine solely to measure its declared work, but it must not secretly become a target acquisition run under the name “profile.” No such component execution occurred in this consultation.

## 8. Concrete next decision

The main obstacle is now accounting precision, not a missing paper or an unbounded mathematical state space. Resolve the equality serialization, exact gain/caching implementation, evidence-retention representation, and the stop/resume graph before constructing a large profiling package. These choices change both costs and what a maximum fixture must contain.

A small explicit-pair conformance reference plus the grouped-gain reference offers a justified route to exact implementation. The bounds above make the needed full-run projection inspectable without target outcomes. They do not provide measured numerical admission, settle laptop versus Alliance HPC, or establish that the calibration can produce a scientific positive result.

**Further papers:** none for these local combinatorial and accounting deductions. No historical-priority or external-method claim is introduced.

## 9. Exact sources

Repository source URLs use returned commit `c66f764955c6cfe17d78ae593c290b4ae949e4d3`, accessed **2026-09-12**. Source hashes were recomputed from the available exact snapshot. The root return-verification task independently checks the GitHub return. The043 publication manifest supplies this new analysis's hash.

| ID | Source | SHA-256 |
|---|---|---|
| R1 | [docs/P2_SECOND_OPERATION_SPECIFICATIONS_035.md](https://github.com/afazeliUofT/arc-independent-lab/blob/c66f764955c6cfe17d78ae593c290b4ae949e4d3/docs/P2_SECOND_OPERATION_SPECIFICATIONS_035.md) | `25f3148827d22abbe587a6c2ff0c5a3ff2db1883f70e678f640f16d0f07a7c69` |
| R2 | [docs/P3_COMPARISON_DESIGN_042.md](https://github.com/afazeliUofT/arc-independent-lab/blob/c66f764955c6cfe17d78ae593c290b4ae949e4d3/docs/P3_COMPARISON_DESIGN_042.md) | `597ad1981a90682eea3e8e0118bbea0c9268d2f2edb82a20bce8c1c018d593fb` |
| R3 | [configs/P3_CALIBRATION_DESIGN_042.json](https://github.com/afazeliUofT/arc-independent-lab/blob/c66f764955c6cfe17d78ae593c290b4ae949e4d3/configs/P3_CALIBRATION_DESIGN_042.json) | `bd892bf72027ddb3d3ebdee979e4304cad5e36766a87d240acd32d11d783ee5f` |
| R4 | [evidence/P3_COMPARISON_FEASIBILITY_042.md](https://github.com/afazeliUofT/arc-independent-lab/blob/c66f764955c6cfe17d78ae593c290b4ae949e4d3/evidence/P3_COMPARISON_FEASIBILITY_042.md) | `4e8fdaa35d82f874f141540d91b307088567969d04780454d656afd03ff0d57a` |
| R5 | [docs/governing/04_RESOURCES_AND_SETUP.md](https://github.com/afazeliUofT/arc-independent-lab/blob/c66f764955c6cfe17d78ae593c290b4ae949e4d3/docs/governing/04_RESOURCES_AND_SETUP.md) | `00e2e878fbfc1a11d56ada0ed512bd53443250326a0275ad082f842013c25cd5` |
