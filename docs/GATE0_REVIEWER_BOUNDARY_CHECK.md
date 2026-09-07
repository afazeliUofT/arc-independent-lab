# Gate0: observe the command sandbox on this laptop

Prepared 2026-09-07, before the laptop observation. This is an operational canary, not a scientific treatment, a reviewer invocation or a formal verdict. The new helper is `scripts/gate0_reviewer_boundary_probe.py`; its exact bytes are pinned by the publication package and checkpoint manifest before the human runs it.

## Question and limits

Can the installed Codex 0.151.0 command sandbox execute a fixed reader while denying the same process and its descendants the tested reads and writes outside the requested allowance? Can that process complete a nonce exchange with a known live host-loopback listener while the requested profile has networking disabled?

Only synthetic files and a synthetic local listener are used. The test does not open scientific artifacts, credentials, user configuration files or the other programme. The driver supplies a new uniquely named permissions profile as an invocation override, retains managed requirements, and changes no existing settings. Client-internal configuration/file access is not traced; the claim that the driver itself avoids those files does not apply to every internal client operation.

The actual inventory advertises `codex sandbox -P`, `--include-managed-config`, `-C`, and configuration overrides. The profile grants minimal runtime reads and reads of one synthetic packet, with no write grants and networking disabled. It uses neither a guessed sandbox-state JSON schema nor the older `sandbox linux` command form. The [official profile schema](https://learn.chatgpt.com/docs/permissions) and [configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference), accessed 2026-09-07, supply the configuration syntax. Actual enforcement remains the subject of this test.

## Controls fixed before the observation

- A separate unconfined synthetic fixture runs the same child. Its reads, writes, shell redirection, subprocess actions and loopback exchange must succeed. This checks that a malformed payload, missing file or broken endpoint cannot impersonate sandbox denial.
- The protected fixture uses ordinary owner-writable files. The parent confirms access before invoking Codex. It does not manufacture success with `chmod` read-only files.
- The child must emit the expected start/completion events with the fresh run nonce and successfully read the allowed canary. Absence of execution is an unavailable or inconclusive observation, not successful protection.
- Direct and symlink-mediated sibling reads, protected writes, new-file creation, atomic replacement, unlinking, shell redirection and nested subprocess operations are observed separately. The shell redirection is performed inside the child, not by the parent before sandbox entry.
- The external parent compares the protected directory's inventory, file bytes, modes and symlink targets after execution. An unchanged hash alone cannot prove that an operation ran or was denied; the child event and external comparison are both required.
- A live nonce server is checked outside the proposed sandbox. The confined connection is assessed only for that exact IPv4 loopback route. The report does not certify all outbound destinations, Unix sockets, connectors or model-service traffic.

There is no automatic fallback to a broader profile if the client rejects the policy or cannot start Python. Errors and partial output remain evidence. A version mismatch also stops the substantive probe, preserving the fact rather than silently testing a different runtime.

## Execution and outputs

After the checkpoint installs the script, run in WSL:

```bash
python3 -u "$HOME/ARC_Independent_Lab/scripts/gate0_reviewer_boundary_probe.py"
```

All driver-created files stay inside a fresh `delivery/gate0_boundary/<run-id>/` directory. Earlier runs are preserved. The driver prints each stage, then `REPORT:` and `REPORT_SHA256:`. Return the JSON report itself as an attachment, including when the reported status is a failure or inconclusive. No credential or authentication setup is requested to make this canary pass.

The driver calls only Codex version, `doctor --help`, and the synthetic `sandbox` command. Doctor help is a separate metadata observation and does not run a doctor diagnostic. No app-server, model session, review, job, package install, login or quota-consuming action is invoked. The helper uses Python's standard library. External command deadlines are bounded; process cleanup targets only the group the driver created. Unusual detached descendants and file-I/O timing are not claimed universally contained.

## Interpretation before proceeding

Any unexpected successful forbidden operation or changed protected fixture is adverse evidence. A launch error, timeout, incomplete child protocol or failed allowed read is not a pass. Keep filesystem and loopback outcomes distinct; do not call an untested network route protected.

Even an entirely favorable observation is **not independent-review readiness**. The eventual reviewer still needs a fresh model context, an enforced restriction on every exposed tool and connector, externally checked evidence hashes and the human-controlled verdict channel. If its tool lane is offline, its private read-only evidence packet must already contain the cited full methods. The published first review packet and residual supplement remain the scientific task; this canary does not issue their verdict.

Local validation in the hosted workspace can inspect and exercise the harness with substituted runners. Such results must remain labelled simulations or harness checks. A deliberately unconfined runner should be rejected, not advertised as a real Codex sandbox success. The installed laptop runtime is the only target of the next actual observation.

The delivered probe SHA-256 is `839d67de25280777bdd588cd4baf3e0112f7e946b78beecc34a7c23e069642c4`. Hosted validation exercised an intentionally unconfined child, a fabricated policy rejection, a fabricated wrapper timeout, and mocked detached-pipe cleanup. Each produced its required adverse or bounded-cleanup outcome. The exact receipt is `evidence/GATE0_BOUNDARY_HARNESS_VALIDATION_2026-09-07.json`, SHA-256 `58f136c952bbcd636669d5f01777d0fa4c80427a0f9efda71d8d1ce036602b60`; it maps the archived raw simulation reports and reproducible validator source. These checks establish harness behavior only.
