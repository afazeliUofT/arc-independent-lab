# Resource request policy 032

The published 030 science run completed 90 successful broker calls and stopped
on a denied image-resource path. The saved `boundary.resource_path` category
combines an unknown page name with malformed paths; the exact failed path is
unavailable. The controller then skipped final packet verification because
the same operational broker was already stopped. Neither final corruption nor
final equality was measured. This historical failure remains a failure, and
the new policy does not retroactively admit it.

`p3_review_interface_032.py` separates refusal of a resource request from
termination of the whole review. A denied resource is still never opened. A
correctable response requires successful whole-packet verification and consumes
one of the existing eight total input corrections. The ninth error is terminal;
successful calls, compaction and tool changes cannot reset that counter.

The policy is the same in synthetic and scientific sessions. The synthetic
controller may terminate its fixed challenge after it observes the real
traversal refusal; the broker itself does not grant a synthetic-only exception.

## Original authority remains in force

The new interface imports the original broker and prior interface without
editing either. The unchanged original `_path` function executes for every
supplied resource reference. Only a path it accepts and that belongs to the
fixed manifest may reach the unchanged descriptor-relative reader. The latter
retains no-follow component traversal, single-link regular-file checks,
original identity comparison, byte bounds and measured digest checks. No path
is normalized, guessed, rewritten, redirected or opened outside the manifest.

The finite refusal categories distinguish wrong type, empty, overlength,
backslash, control character, absolute, traversal, other noncanonical syntax,
and canonical unmanifested names. Their receipts contain authored category and
original-guard constants. They contain neither the rejected path nor its hash.
The tool's existing path schemas are unchanged. Broader ordinary shape, kind,
integer, evidence and verdict validation remains inherited from interface028.

Malformed requests do not suppress verifiable integrity claims. Every supplied
valid resource reference is still read and checked. False well-formed digests
for known evidence or the scope manifests remain fatal even when another
reference in the same request is invalid. Before returning any correctable
error, the complete manifested packet is verified again. A changed identity,
missing known file, symlink, hardlink, wrong digest or manifest mutation takes
priority over argument feedback. A malformed known PNG remains a terminal
format failure.

Correctable path failure never reaches the original broker's terminal dispatch.
No failed latch is cleared. A broker stopped for actual integrity, unknown
operation, correction ceiling or original-dispatch failure remains stopped.
Valid operations still execute through the original dispatch with its before
and after whole-input verification. The original auditor and verdict output
semantics, authority and exclusivity are unchanged.

## Evidence for the actual synthetic guard

For traversal syntax, the emitted `ToolInputError` retains the actual original
`BrokerError` as its immediate `__cause__`. That cause retains the traceback
frame of the unchanged `_path` function. The session can therefore bind its
synthetic result to the exact fixed `../OUTSIDE.txt` challenge, original guard
execution, and completed packet revalidation. It must not infer a witnessed
refusal from a model statement or a category string alone.

For an unmanifested but canonical path, the original `_read` method supplies
the actual manifest-membership rejection before any raw read. The interface
exposes `resource_path_refusal_receipt()` with total refusals, fixed counts by
category, the latest validated refusal, and the shared correction count. The
transport reconstructs its response through the same finite `ToolInputError`
catalog. It must import interface032 to recognize the added categories.

## Tests and limits

The 22 local tests exercise each path category, zero access to every refused
resource, normal corrected image and hash calls, unchanged successful verdict
content, exclusive output, original path cause identity, mixed corrections and
ninth-error termination, unchanged Unicode path acceptance, the historical
packet-poisoning counterexamples, mutation between denial and feedback,
same-byte replacement, missing files, symlinks, hardlinks, malformed images,
false evidence and scope digests in mixed valid/invalid requests, fixed receipt
contents and unchanged tool schemas. No native client or model is involved.

An initial local test exposed a mistaken helper name (`tool_specs` instead of
the original `dynamic_tool_specs`). That implementation and test were
corrected; the subsequent 22-test run passed. The separate historical forensic
reproduction remains unchanged.

The strongest concern is that accepting corrections after traversal might
permit repeated probing. It grants no filesystem access: every such request
is rejected before opening, with no arbitrary path echoed and with the shared
eight-error/call/time bounds still in force. The complete manifest is already
an authorized evidence index, so saying to select a manifested path reveals no
new filesystem inventory. Actual integrity failures remain terminal.

This change cannot establish what exact path caused 030 or guarantee that a
future reviewer will deliver a verdict. It also does not repair historical
missing final measurements. Final packet observation must use a separate,
parent-held verifier with its original baseline, rather than depending on the
operational broker's continued availability; that is a separate controller
responsibility.

Source basis: the unchanged [original broker](https://github.com/afazeliUofT/arc-independent-lab/blob/4ed9c95b4200daf2dcc455d1f14c9a93757054a6/scripts/p3_review_broker.py),
[interface028](https://github.com/afazeliUofT/arc-independent-lab/blob/4ed9c95b4200daf2dcc455d1f14c9a93757054a6/scripts/p3_review_interface_028.py),
and [controller030](https://github.com/afazeliUofT/arc-independent-lab/blob/4ed9c95b4200daf2dcc455d1f14c9a93757054a6/scripts/p3_finite_review_030.py),
all accessed 2026-09-10. This is shared-workspace engineering validation, not an
independent scientific review.
