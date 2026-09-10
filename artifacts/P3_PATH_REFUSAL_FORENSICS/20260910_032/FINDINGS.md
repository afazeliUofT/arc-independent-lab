# Broker stop forensic finding, 2026-09-10

The 030 science run stopped because a `read_page_image` request supplied a
denied resource-path string. The saved classification does not distinguish an
ordinary unknown page name from traversal or another malformed path. It does
not report a file-content or identity failure. The later packet postcheck was
prevented by the already-stopped broker; it did not independently establish
that the packet had changed.

This is an engineering source audit and synthetic reproduction, not an
independent scientific review. No model or native client was started. No
credential contents or actual private packet contents were accessed.

## Historical evidence

The returned `science_SESSION.json` has SHA-256
`1059b733db491fc9e5aee64113784cb95620bab487f76346f91ec243000f0da9`.
The separate `science_STAGE.json` has SHA-256
`0911d75d736e9286d6b7600588051fa471c4f610ed24236253539155bc3490b7`.

- 90 successful broker receipts: 51 whole-file hashes, 35 text reads, three
  page-image reads and one fixed observer audit.
- The next image request failed with `boundary.resource_path`. There were
  zero recoverable input errors and exactly one failed broker call.
- One context compaction completed, and no native event failure was recorded.
- The session lasted 649.667418 seconds, approximately 10 minutes 50 seconds.
  The native child was reaped. No verdict was submitted.
- All recorded noncredential host checks passed. The initial packet receipt
  verified 722 files. The final packet receipt is null, with
  `packet_after_check_failed`.

Those facts come from the exact returned files; their paths and hashes are
retained in `REPORT.json`. The actual failed path was not retained and cannot
be recovered from this report. No attempted reconstruction of model text or
private paths was performed.

## Complete source route

1. The 028 interface checks every supplied string-valued resource path before
   ordinary argument validation. For `read_page_image`, a non-string path is
   instead a recoverable `resource_path_type` error after whole-packet
   validation. Thus the historical path was a string under these unchanged
   controls. `ReviewBroker._check_paths`, lines 150–167, and `_resource` are in
   the [published interface source](https://github.com/afazeliUofT/arc-independent-lab/blob/4ed9c95b4200daf2dcc455d1f14c9a93757054a6/scripts/p3_review_interface_028.py),
   accessed 2026-09-10.
2. The original `_path` rejects strings of length zero or over 1024,
   backslashes, characters with code point below 32, and empty, `.` or `..`
   slash-delimited components. An explicit absolute-path rejection follows;
   ordinary POSIX absolute paths already fail the empty-component check.
   Canonical strings absent from the manifest are also rejected. None of
   these requests reaches `_read_raw`, so no denied resource is opened.
   `_path` and `_read`, lines 63–69 and 233–242, are in the
   [published original broker](https://github.com/afazeliUofT/arc-independent-lab/blob/4ed9c95b4200daf2dcc455d1f14c9a93757054a6/scripts/p3_review_broker.py),
   accessed 2026-09-10.
3. The interface groups all four authored messages—invalid, noncanonical,
   absolute and unmanifested—under `boundary.resource_path`. Its outer
   dispatch handler sets the original broker's `_failed` latch. The protocol
   then marks the boundary stopped and saves the group code, tool and layer,
   without the path or raw exception. See the interface above, lines 267–298,
   and [published protocol](https://github.com/afazeliUofT/arc-independent-lab/blob/4ed9c95b4200daf2dcc455d1f14c9a93757054a6/scripts/p3_review_protocol_028.py),
   accessed 2026-09-10.
4. The 030 controller's science `packet_after` function requires that this
   same broker is not failed before calling `verify_inputs`. This predicate
   now fails deterministically. The stage recorder catches it and records
   `packet_after_check_failed`, without performing the final packet rehash.
   See [controller lines 341–349](https://github.com/afazeliUofT/arc-independent-lab/blob/4ed9c95b4200daf2dcc455d1f14c9a93757054a6/scripts/p3_finite_review_030.py)
   and [stage recorder](https://github.com/afazeliUofT/arc-independent-lab/blob/4ed9c95b4200daf2dcc455d1f14c9a93757054a6/scripts/p3_stage_evidence_030.py),
   both accessed 2026-09-10.

Every successful original-broker dispatch rehashes all manifested inputs
before and after its operation. Consequently the 90th successful call
contains an earlier successful full-input check. That is not a final-time
measurement. A packet mutation after that check could coexist with the later
denied path. The historical report therefore establishes neither final-byte
equality nor final-byte corruption.

## Synthetic reproduction

`reproduce_broker_stop.py` exercises the unchanged original broker, 028
interface and protocol, and 030 stage recorder. Its 16 cases all passed.
`REPORT.json` records measured outcomes and source hashes; `SHA256SUMS`
identifies the exact runner and report bytes. Temporary fixtures were removed.

| Synthetic input or condition | Saved class | Later original packet check | Separate verifier |
|---|---|---|---|
| Valid known image | success | Rehash attempted | Pass |
| Canonical missing page or page-number typo | `boundary.resource_path` | Blocked by failed latch | Pass when bytes unchanged |
| Traversal, absolute, empty, long, backslash, control, double slash | `boundary.resource_path` | Blocked by failed latch | Pass when bytes unchanged |
| Non-string path or known wrong resource kind | Recoverable input error | Rehash attempted | Pass |
| Known file removed or manifested bytes changed | `integrity.resource` | Blocked by failed latch | Detects failure |
| Unknown path plus concurrent manifested-byte mutation | `boundary.resource_path` | Blocked by failed latch | Detects failure |
| Manifested image whose bytes are not PNG | `integrity.packet_format` | Blocked by failed latch | Hash/identity pass; format failure remains terminal |

The separate verifier in the experiment is another original broker opened
before the synthetic action. It receives no tool requests and retains its own
original identities and descriptors. It is used only to show the difference
between request failure, content integrity, and format validation. No stop
latch is reset, and the historical broker is not resumed.

## Correction options

The most conservative durable correction separates three decisions:

1. Whether the request is authorized to access a resource. Keep exact manifest
   membership, descriptor-relative no-follow access, kind, bounds and digest
   checks. Never normalize a denied path into an accepted path, guess a page
   filename, open an unlisted resource, or echo arbitrary input text.
2. Whether an ordinary invalid argument needs to kill the session. A canonical
   but unmanifested string can be refused without any file opening, then
   receive fixed feedback to select an exact entry from the already supplied
   index. This is a changed session policy, not expanded file authority. It
   must be explicitly implemented, bounded by the existing correction/call
   limits, tested and recorded; it must never retroactively admit 030. Keep
   traversal, absolute and other malformed authority attempts terminal unless
   a separate, reasoned policy change is made. Whole-packet validation must
   succeed before any recoverable feedback, including for otherwise invalid
   requests, so an input mistake cannot mask a simultaneous integrity failure.
3. Whether final packet measurements can still be collected after a stop.
   Use a separately held, read-only verifier initialized before the model
   starts, or a narrowly specified diagnostic-only verifier that retains the
   original identity baseline and never resets the dispatch stop state.
   Always retain both the operational failure and any final integrity result.

Store fixed subcategories such as `path.syntax`, `path.not_manifested`,
`integrity.identity`, `integrity.digest`, and `packet_check.not_attempted`
without saving arbitrary path contents. Do not report a skipped measurement
as measured corruption. The current collapsed classification cannot tell
which request-policy change would have saved this historical run; implementing
only canonical-unknown feedback therefore cannot guarantee a verdict in a
future run. The retained access boundary and more precise evidence, rather
than a promise of success, justify a correction.
