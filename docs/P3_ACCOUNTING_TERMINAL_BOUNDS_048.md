# Static terminal multiplicities for the frozen acquisition call graph

Date: 2026-09-14. This is PI engineering analysis, not an independent verdict.
The accompanying module imports no learner, scheduler, profile, evaluator or
model. It enumerates finite integer counts. No target outcome is an input.
This document does not establish a closed schema, total memory/work bound,
corrected measurement, resource allowance or scientific admission.

## Source and assumptions

The source is the frozen043 acquisition and045 diagnostic graph. Exact source
identities are in `configs/P3_ACCOUNTING_COMPLETION_REQUIREMENTS_047.json`:

| File | SHA-256 |
|---|---|
| `scripts/reference_n3_043.py` | `4af1dbad200b3a4e5e0850a3def8b9710b70724a8a506df0c6a9a77f72385193` |
| `scripts/diagnostics045.py` | `d82855254880fe9d51242f98cea61b2813af7a5c62c36294a82786b86f2c0ed7` |
| `scripts/reference_n1_043.py` | `af4d6bb289591d1495af2d0d216c956c53be3201dc2fb6eb3b1a1340705029b5` |
| `scripts/fullwork046.py` | `e9dd696ac174864bfa8c17c21b3b4cd7af1a1d096e2d529f4065e5bd02f4348b` |

Frozen042 supplies A5/L5/V2/q4/K4/B_env285. Warm-up completes all five one-action
words and costs10 calls before any scored trial (`Acquisition.run`, lines541-558).
The scheduler excludes completed words (`Scheduler.select`, lines242-248).
Therefore scored words have length at least two and there are at most25 distinct
length-two words. A scored trial returning to the main loop has spent RESET,
its whole word, and V validation calls (`_scored_trial`, lines414-470,531-533).
No scientific refusal resumes this loop. The analysis deliberately permits any
unused word order; actual scheduler priorities can restrict this superset.

## Why a terminal record does not add a 51st replay boundary

For n scored trials with complete validation, the smallest total calls are
10 plus the costs of the n shortest unused words, each priced at length+3.
For n50 this is10+25*5+25*6=285. For n51 it is291.

The next trial record is allocated before the environmental reservation check
(`_scored_trial`, lines408-415). Thus50 completed trials can coexist with a
51st scored record and all five warm-up records. That51st record has no event.

Starting a terminal trial requires enough remaining allowance for its entire
RESET+word, even if interruption occurs immediately after RESET (`_trial`,
lines355-358). Only its two validation calls can be omitted from the lower
bound. A51st event-bearing boundary would therefore require at least291-2=289
calls, exceeding285. A partial event-bearing terminal boundary can replace the
50th complete boundary; it cannot augment50 complete boundaries.

Replay skips a terminal empty-event record (`replay_acquisition`, lines302-307).
For each other scored trial it captures pre/post states and emits one boundary
(lines311,329,368,385). Decomposition constructs at most three readers for each
boundary, even one with no validation rows (lines443-452), and requests three
forecasts per completed validation event (lines454-474). All those reader copies
remain live until session close. A refusal may leave a partial reader attempt;
it consumes one of these positions and does not authorize a new retry.

| Object or operation | Conservative042 bound |
|---|---:|
| Scored trials with complete validation |50|
| Allocated scored trial records, including terminal reservation |51|
| All trial records, including five warm-ups |56|
| Event-bearing scored replay boundaries, including terminal partial |50|
| Pre/post boundary records, each with its own T copy and Phi copy |100|
| Decomposition fitted-reader attempts, including a partial fit |150|
| Completed validation events |100|
| Decomposition forecasts/Brier requests |300|
| Acquisition before/after snapshot attempts |100|
| Scheduler selection attempts, including final attempt |51|
| Mutation assemblies in FULL/MACRO_OFF/FEEDBACK_NULL |39|
| Mutation assemblies in direct COVERAGE |0|
| Recipe records / macro records |55 /45|
| Raw mutation attempts in one conservative assembly |27,720|
| Raw insertion word length / retained nonempty-word vocabulary |10 /3,905|

The snapshot bound is an attempt bound, not an assertion that each snapshot
has an issued event: a before-snapshot attempt may fail before RESET. The
whole-trial environmental check nevertheless precedes that attempt, so it
occupies one of at most50 admitted scored-trial positions. Each such position
attempts no more than one before and one after snapshot.

The100 boundary records contain100 T copies and100 Phi copies; they are not a
bound of100 individual list objects. Their separately exported record views,
source copies and codec owners are additional owner classes still to be priced.
These are bounds for named categories, not simultaneously attainable maxima.
There are at most51 selections; indices divisible by q4 skip mutations, giving
51-floor(51/4)=39. A terminal selection can construct proposals before failing
the later trial reservation (`run`, lines558-568). K4 permits at most four
fresh positive-credit trials. Each length-five word supplies at most ten
nonprimitive contiguous fragments, in addition to the five already stored
primitive macros: M<=5+4*10=45. At most55 recipes participate. Literal mutation
loops yield F*((L+1)*M+L+L*M+(L-1))=27,720 attempts; insertion can transiently
produce ten tokens before the length filter. Parent and derivation counts must
still account for all actual occurrences; these formulas do not measure them.

The transition-table bound also survives a terminal partial trial. Complete
warm-up contributes five primitive transitions and ten calls. With b later
event-bearing trials, at most7b further primitive responses fit their
length-five words and two validation slots. Their b paid RESETs leave at most
275-b further primitive calls. Consequently
`n <= 5 + min(7*b, 275-b)`. The two lines cross at b=275/8; over integers their
maximum is245 at b35 (b34 gives243). A structural allocation attaining these
counts is34 full length-five scored words followed by RESET and two terminal
primitive responses:10+34*8+3=285 calls and5+34*7+2=245 transitions. This is an
overapproximation witness, not a claim the actual scheduler reaches that order.
An incomplete warm-up cannot exceed floor(B_env/2) retained primitive responses.

The module's transition bound uses the two integers around the crossing; its
independent reference enumerates every integer later RESET count. The generic
bound deliberately permits more length-L trials than may be available after
word-vocabulary exhaustion, so it remains an upper bound rather than a claim
of tightness. Each acquisition source table and each chronological replay
boundary table is bounded by245 in042. Independent table copies still require
their own owners and do not share this single table's byte allocation.

## Finite reference and limitations

`scripts/accounting_bounds048.py` implements two different derivations. The
reference recursively enumerates every feasible vector of completed-word counts
by length under the environment allowance, then visits each possible unused
terminal word length at the record, whole-trial reservation and validation
stages. The algebra minimizes cost by filling shortest lengths, then computes
the maximum complete and event-bearing counts. Both use the frozen reservation
semantics and finite distinct-word vocabulary; neither runs the mechanism.

The frozen test matrix in `FROZEN_CASE_MATRIX` compares the two on small action,
word-length, validation and environment domains, tests stage boundaries and
vocabulary exhaustion, and compares the actual042 domain. It additionally
compares closed and enumerated transition bounds on every such domain. The test result is
recorded separately; this source document by itself claims no test pass.

The credit helper reproduces D<=250, denominator<=2*250^8 (65 bits), and absolute
numerator<=twice that (66 bits). It also supplies unreduced cross-product caps
from input numerator/denominator bounds. This is not a blanket66-bit temporary
bound and does not yet price gcd, comparison, repeated accumulation, encoding,
or all intermediate integer owners.

In particular, these finite counts do not fix the current first allocation gap:
`N1.__init__` allocates containers and calls `_seal` (`reference_n1_043.py`,
lines125-160); `_seal` constructs `state()` before retaining it (lines174-178);
`Meter.encode` traverses `_nodes` and normalizes before output reservation
(`accounting043.py`, lines99-125). The047 schema, global owner lifetime,
pre-expansion guarded adapters, terminal commit rules, complete work ruler and
independent admission requirements remain pending. No existing source file is
changed and no old execution is reclassified as corrected accounting.
