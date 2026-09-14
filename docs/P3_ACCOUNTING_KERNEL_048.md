# 048 bounded kernel prerequisite

Status: implementation candidate, with a finite source-frozen conformance matrix.
This document alone reports no execution result. The new files are
`scripts/accounting048.py` and `tests/test_accounting048.py`; historical043–047
files are not changed. The unit is **not the completed047 accounting correction**.

Only a global ownership/work kernel and a closed-schema canonical codec exist in
this unit. N1/N3 construction, acquisition, snapshots, diagnostics, evaluation,
transport and whole-program projection remain unguarded in their frozen modules.
**None of the eleven047 coverage rows can be marked fully complete.** In
particular, passing the codec fixtures does not establish all eventual scientific
schemas or an independent whole-program projector. No B_comp/B_mem, physical
feasibility, target authorization or independent review verdict is supplied.

## Closed domain and setup boundary

`Schema` is an immutable finite tree. `compile_schema` reads only its declarations,
never a scientific value. Limits are depth20,512 visited schema declarations,
65536 entries per list/tuple/set/map,1024-bit integer/fraction operands,4096 Unicode
code points per string, and at most8 disjoint alternatives per union. The width
ceiling accommodates245 retained transitions,3002 literal predicates and27720
raw derivations without asserting schemas or multiplicities for them. Repeated
value elements use the same child declaration. Record keys are fixed and unique;
record values must contain exactly those keys. Unions must have disjoint exact
Python runtime types. Cyclic schema declarations exceed the depth limit and are
rejected. Schema numerical products must fit the finite63-bit metadata domain
with1024-fold headroom.

Supported values are exact builtins `None`, `bool`, `int`, `str`, `list`, `tuple`,
`set`, `frozenset`, `dict`, and exact `fractions.Fraction`. Floats, custom classes,
subclasses and ambiguous unions are unsupported. A bounded schema need not admit
every value accepted by043. Admitted values must emit **byte-identical043**
canonical JSON, including tagged fractions, sets and non-string-key maps. Empty
maps follow043's ordinary-object representation. Unicode escaping includes DEL,
non-BMP characters and lone surrogates.

Immutable declarations, route tables and the prepared `Codec` are bounded setup
apparatus. They are constructed before scientific codec traversal and are not
claimed as a measured scientific value-construction trace. Their stated finite
caps are an explicit setup boundary; a complete047 apparatus/source map must
incorporate their actual retained multiplicities. The kernel's fixed ledger
counter/owner/terminal metadata has its own counted envelope. These two statements
must not be conflated with complete-work apparatus coverage.

## Structural recurrence

Let B be maximum canonical output bytes, N source traversal nodes, K simultaneously
reserved canonical ordering-key text, and D structural workspace depth. A string
of c code points has B=12c+2; a b-bit signed integer has B=b+1, a deliberately loose
decimal upper bound. Scalar `None`/bool uses B=5. A fraction uses B=17+2(b+1), N=3.
The remaining scalar cases have N=1 and K=0.

For width n and child (B,N,K,D):

| Schema | Output B | Source nodes N | Ordering keys K |
|---|---:|---:|---:|
| list / tuple | 2+nB+max(0,n−1) | 1+nN | nK |
| set / frozenset | 11+nB+max(0,n−1) | 1+nN | nK+nB |
| map, child key/value subscripts k/v | 11+n(3+Bk+Bv)+max(0,n−1) | 1+n(Nk+Nv) | n(Kk+Kv+Bk) |
| fixed record | 2+sum(JSON-key-length+1+Bv)+max(0,n−1) | 1+sum(1+Nv) | sum(Kv) |
| disjoint union | maximum alternative B | maximum alternative N | maximum alternative K |

The tagged map expression dominates the string-key object form. D increases by
one for list/tuple/record, two for set, and three for map; a union adds a dispatch
level. The literal recurrence is tested against independent043 canonical lengths
and043 node counts for declared finite fixtures. This is a generic schema check,
not the separate eventual whole-program algebraic projector/reference proof.

All six codec owners are admitted together before validation or normalization:

| Disjoint owner | Reserved logical envelope | Lifetime |
|---|---:|---|
| source | max(existing reservation,B) | Survives success/refusal while caller holds input |
| validation | 256(D+21) | Preallocated bounded reference stack through codec call |
| normalized | B | Complete normalized containers through byte creation |
| ordering | K+4B+64(N+D+1) | Key strings, pair/reference slots, scalar scratch and JSON chunk workspace |
| json_text | B | Final ASCII-compatible JSON text through byte creation |
| encoded | B | Returned handle until caller drops output and closes handle |

The four extra B envelopes conservatively separate bounded integer operands and
results, JSON fragments and concatenation workspace. The64-byte node/frame slots
are a **declared logical apparatus convention**, not Python `sizeof` measurements.
No Python heap/RSS bound or exact interpreter-instruction trace is claimed. The
output bound plus bounded node/frame slots describes this codec convention; a
physical runtime validation and complete source audit remain separate gates.

Caller-created input must already have an independently justified ownership
envelope. Codec admission cannot retroactively guard its construction or certify
the size of an arbitrary malformed caller object. A prior larger source
reservation is preserved. Validation checks lengths/types/bit widths before
recursive normalization and makes no recursive copy of the input. Invalid input
refuses without normalization and keeps its caller-owned source reservation.
The explicit too-small validation-workspace option refuses before traversal.

## Ledger and work

`Ledger(work_limit, memory_limit, owners, terminal_slots)` requires fixed owner
names (ASCII,80 characters maximum), at most4096 owner slots and16 terminal slots.
The only channels are acquisition, diagnostic and apparatus. The operation-price
vocabulary is a fixed tuple; counters, reservations, escrows and terminal slots
are allocated once. Initialization checks its finite apparatus prepayment before
allocating those arrays. Owner registration and refusal histories cannot grow.
Owner metadata uses256 logical bytes plus identifier length; fixed counters use64
bytes per channel/category; terminal slots use128 bytes. An additional512-byte
header includes the first-cause fields. All numerical fields are bounded to63 bits.
An overflow demand recorded as MAX_UNITS is explicitly a saturated lower bound.

`reserve_bundle` checks the **global simultaneous sum**, across all channels, and
commits sizes atomically only if it fits. Each attempted owner guard costs one
work unit even when the bundle later refuses. `reserve_work` reserves capacity,
not executed work. `spend(..., escrow_owner=...)` transfers actual work from that
owner's escrow into the spent channel; it never charges an unused reservation.
Ordinary unescrowed spending must fit alongside every existing escrow. No branch
receives work imputed from an unexecuted more expensive algorithm.

Each reached validation, normalization, measurement, JSON-node visit, slot or
move costs one unit. Examined characters and emitted ASCII bytes cost eight.
Integer decimal-length divisions are charged from the actual current operand bit
width before each executed division. JSON output length is measured without
serializing first. Before each actual `json.dumps`, the codec prepays its reached
node/output convention and the explicit043 ordering rule
`max(1,L.bit_length()) * max(1,8*L)` for actual output length L. This is a declared
abstract rule, not a claimed CPython comparison trace. The separate stable
builtin ordering of set/map rows uses `cmp_to_key` and charges each character
comparison actually reached, plus its bounded key-wrapper slots. Internal pointer
moves remain part of the declared apparatus convention, not an invented exact
move trace. This avoids introducing a quadratic insertion-sort algorithm into
the future full domain. Final ASCII encoding receives its own emitted-byte charge.

## Terminal and ownership discipline

The first work, memory, schema or workspace refusal is authoritative. Every later
scientific spend/reservation refuses with the same cause, including requests for
zero work. Only fixed terminal commits and prepaid cleanup continue. Terminal
codes come from a closed vocabulary; a slot may be repeated identically but not
overwritten. Cleanup is idempotent and retires its owner permanently, releasing
its reservation and unused escrow. Spent work never decreases. Initialization
prepays three units per owner cleanup and per terminal slot plus one setup unit.

On an expected codec `Limit`, retained traceback frames could otherwise keep
normalized data alive. The codec detaches the old traceback/context/cause, exits
the handler, drops temporary references, performs prepaid cleanup, then raises a
fresh bounded cause-only exception. Source ownership remains live. Unexpected
Python exceptions preserve the temporary reservations because their traceback
may still own intermediates. This does not claim recovery from process/OOM failure.

`Encoded.close()` clears that handle's byte reference before owner cleanup and is
idempotent. Clients must not retain an unregistered alias to those bytes and then
release its last owner. Source cleanup belongs to the caller after it drops input.
These cooperative ownership rules are not a Python reference-ownership type
system; arbitrary client mutation or retained aliases are outside this unit.

## Frozen conformance cases

`CASE_MATRIX` in the test source enumerates15 direct `unittest.TestCase` methods:
global simultaneous ownership, disjoint copies, escrow/spent separation, latched
first cause and cleanup, finite terminal slots, closed metadata vocabulary,
byte-identical043 edges, structural length/node reference, fail-before-normalize,
insufficient validation workspace, malformed/out-of-schema input, live overlap and
output lifetime, mid-codec work refusal, finite schema definition limits, and
actual set-ordering branch charges. The conformance runner must select only this
frozen file and the separately declared048 bounds suite; it must not discover
historical learner tests. AST syntax parsing is preparation, not conformance.

Source hashes, actual runner output and any first failure/correction history must
be reported by the048 handoff. A successful result establishes only these bounded
prerequisites. It supplies no independent-review GO and admits no treatment run.
