# Existing review030 workflow

`review030_workflow.run_workflow(project_root)` returns a dictionary with
`workflow_report`, `collection`, `controller_invoked`, `status`,
`controller_outcome`, and `inspection_outcome`. `collection` is the evidence
collector's result containing explicit repository paths for the human-operated
publisher. This module never commits, pushes, accesses credentials, or changes
an approved030 source, scope, or approval.

An existing030 main directory, kernel-prerequisite directory, or exclusive
wrapper launch marker prohibits another model operation. Existing partial
paths also prohibit it. The wrapper may run the pinned030 Python controller
without its manual launch flag to obtain safe read-only inspection diagnostics;
the unchanged main function performs no native/model operation on that route.
Unsafe existing path shapes or changed pins skip inspection but still collect.

Only when both030 paths and the marker are absent can an explicit human call
invoke the unchanged controller with `--run-attended-review`. Its controller,
scope and exact already-published answer hashes are checked first. An exclusive,
fsynced launch marker is written before process creation, and the030 paths are
checked again. Even a failed Python spawn leaves the marker and forbids retry.
This marker does not establish that a native process started or a model turn was
sent. The approved030 controller remains responsible for those controls.

The fixed local folder is `delivery/P3_030_RETURN_WORKFLOW`. A
`WORKFLOW_REPORT.json` is produced independently of the030 controller's report,
including guarded import failures and interruptions. The first reserved
operation's `LAUNCH_OUTCOME.json` is immutable across publication or collection
retries. `LAUNCH_RESERVED.json` is never removed or reset. The final workflow
report is written before calling `publish_review030_evidence.collect(root)`.

Raw controller streams are bounded to 1 MiB each in memory, then discarded.
Only fixed-prefix stdout status/STOP lines and stderr exception class plus
module basename/line number are included in the JSON. Arbitrary stderr messages,
source-code lines and raw native streams are not saved or hashed. The direct
child's output is drained continuously, with terminal delivery also capped.

The attended controller has a 4310-second outer guard, beyond its 600-second
synthetic and 3600-second scientific stage ceilings plus the 10-second synthetic
kernel prerequisite. Read-only inspection has a 60-second guard. Interruption
first forwards SIGINT and gives the controller 60 seconds for its own cleanup;
emergency TERM has 10 seconds, then KILL 5 seconds. Forced cleanup is explicit and
does not prove native-child cleanup or scientific admission. No branch retries.

`runner`, `inspector`, `collector`, `pins` and `emit` injection arguments exist
for local fixture testing. Production calls use the fixed defaults. Fixture
tests start ordinary synthetic Python children only, with no native client,
model, Git mutation, network or credential operations.

Evidence cannot be created if its destination is unsafe or unwritable, and
power loss or uncatchable process termination can leave a partial marker.
Such a marker is still a stop condition. Collection cannot establish an atomic
snapshot of evidence concurrently being written by a separately launched030
controller. A missing report or verdict never proves that no model ran.
