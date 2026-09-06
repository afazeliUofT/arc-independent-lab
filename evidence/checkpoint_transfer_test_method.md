# Transfer verification method

Observed on 2026-09-06; exact outcomes and tested-source hash are in `checkpoint_transfer_verification.json`. This is an integrity check on the handoff, not a scientific gate verdict and not proof of GitHub persistence.

The test imported `scripts/checkpoint_transfer.py` and constructed a document fixture containing a licence, JSON state and an unanswered escalation. It encoded this using the same compressed JSON/base64 scheme as the distributed installer, then verified unpacked bytes and repeated installation.

Separate fresh destinations checked an existing conflicting licence (must be preserved and prevent other payload writes), a symlinked state directory (must not be followed), a changed payload digest (must be rejected), and a parent-traversal payload path (must be rejected).

For the round trip, an empty bare git repository was created under the project's ignored `delivery/transfer_test/` directory. The imported module's remote constant was changed **only within that test process** to the local fixture. Publishing installed the files, appended the declared human-answer fixture, committed and pushed. Every payload file was then read from the bare repository at the resulting commit, with exact byte comparisons. Repeating publishing had to preserve the same commit and leave a clean working tree. The distributed source retains only the real authorized GitHub URL.

No actual GitHub write, laptop execution, credential handling, independent reviewer isolation or scratch-reset persistence was exercised by these tests. The actual first remote readback remains a human-dependent next action.
