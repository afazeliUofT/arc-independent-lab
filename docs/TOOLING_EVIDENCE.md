# Tooling evidence — Gate 0 within Phase 1

Access/observation date: 2026-09-06. Status labels are deliberately distinct: **documented**, **observed in this hosted session**, **user-reported on the laptop**, **unverified**. No scientific verdict is issued here.

| Question | Evidence and practical conclusion |
|---|---|
| Persistent filesystem | Local write/read works in this session. The hosted scratch workspace is ephemeral by its runtime description. Persistence across reset/reboot is **unverified**; never count it as durable storage. |
| Durable bridge | Exact-repository GitHub metadata read succeeded. `evidence/github_access.json` records the response subset. A checkpoint is durable only after Ali pushes it and the agent fetches its manifest and constituent evidence from GitHub. First round trip remains **pending**. |
| Session resume after death | **Unverified**. A tool process/session identifier is not proof that a model conversation or sandbox survives death. No restart was induced. |
| Unattended multi-session continuation | **Unverified and disabled**. No supervisor or scheduled model loop was started. An active interactive turn and its bounded scouts are not a demonstrated multi-day autonomous runtime. |
| Scheduled/background execution | Automation tools are exposed; capability to create a scheduled task is not evidence of reliable research continuation. No automation was created because unattended model use is paused. |
| Isolated sub-agents | Delegation works. Delegates share filesystem and tool availability. They are scouts, not independent reviewers. Fresh context alone does not meet the tool-isolation requirement. |
| Per-tool protection, including shell | This host enforces a workspace boundary, but no project-specific immutable-preregistration guard or independently enforced reviewer role has been established. C1/C2/C3 **not verified**. |
| Noninteractive invocation/exit codes | Python and git run through the shell. This is not a verified headless model invocation. No paid API or new model client was invoked. |
| Environment propagation | A nonsecret variable constructed in the shell process was visible in its Python subprocess (`evidence/runtime_probe.json`). This does not test desktop-client-to-shell propagation, laptop filtering or secrets. |
| Context exhaustion behaviour | **Unverified**. No destructive or artificial exhaustion test was run. Disk/remote state is required regardless. |
| Usage-limit signature and resets | **Unverified**. Do not exhaust the subscription deliberately to collect a signature. Record a real occurrence verbatim if encountered. |
| Authoritative subscription meter | No callable account-usage/remaining-quota endpoint appeared in the available tool registry. This is a scoped negative observation about exposed tools, not proof that the provider has no usage information. Current authoritative reading is null. |
| Cache accounting | No authoritative cache-use or billing counters were exposed. No savings estimate is made from task duration or token guesses. |

Official documentation says current limits/reset information are available in the usage dashboard and describes `/status` for an active Codex CLI session. Neither statement supplies this hosted agent with a reading of Ali's account. The page cautions that superficially similar tasks can consume different allowance. **No plan table was converted into a project allowance.** [OpenAI pricing documentation](https://learn.chatgpt.com/docs/pricing), accessed 2026-09-06. The first model-specific search returned off-domain search results; those were not used as authority.

The GitHub connection reports privileges beyond the user-authorized read role. The agent is following the narrower role, but this is an instruction boundary, not enforced read-only isolation. Ali executes the prepared publication steps.

The supplied laptop observations remain user-reported for this session. This agent has not reached WSL, inspected its processes, measured its GPU, changed hibernation or contacted a cluster. The hosted environment must not be mistaken for the laptop.

## Durability acceptance and remaining Gate 0 work

The first handoff carries exact files and content hashes. Its installer refuses conflicting files and repository identity mismatches, and never force-pushes. Local reconstruction checks can establish byte integrity but cannot establish remote persistence. The next session must fetch `state/CHECKPOINT_001.json` from the exact repository, then independently fetch/hash the listed files before marking the checkpoint durable.

For small Phase 1 traces, use this same manifest/commit bridge. Before larger experiments, output volume must be measured and a complete raw-artifact transfer/retrieval tested through a reset or fresh working copy. An output that cannot be durably transferred blocks the proposed run. GitHub metadata, a successful push message, a checksum file alone, and an untested large-asset plan do not close this requirement. The general large-output route is **not yet verified**, so Gate 0 is not declared complete.

The user-amended operating policy is interactive work only while authoritative usage is unavailable. Scientific work can advance in explicitly requested attended turns; autonomous continuation remains paused. No arbitrary allowance, usage percentage or elapsed-time proxy is substituted.

## Appended verification record, 2026-09-06

`evidence/checkpoint_transfer_verification.json` records the completed local byte-reconstruction, conflict, symlink, tampering, traversal and bare-repository round-trip checks against its pinned transfer-source hash. See `evidence/checkpoint_transfer_test_method.md` for the method. These checks succeeded locally; the real remote round trip and execution on the laptop remain pending. Source URL for the intended remote: https://github.com/afazeliUofT/arc-independent-lab , accessed by its connector metadata on 2026-09-06.

## Appended real-remote and raw-trace checkpoint, 2026-09-06

The first real GitHub round trip is now **verified** at commit `189f424e5cc9588d9774fd58850c44c9b182f813`. Actual constituent file bytes were fetched at that pinned commit, independently hashed and compared with the original checkpoint manifest; the scoped human answer was also read and archived. Receipt: `evidence/REMOTE_CHECKPOINT_001_VERIFICATION.json`, SHA-256 `e5340a450abc52ee7bc8c0fb39dfd09a1218d5bb7d8865496f1f8d7164e54e8f`. Source: [exact GitHub commit](https://github.com/afazeliUofT/arc-independent-lab/commit/189f424e5cc9588d9774fd58850c44c9b182f813), accessed 2026-09-06. This supersedes earlier pending status for the first small checkpoint only.

Hosted standard-library execution produced the first complete raw artifact set. Its consistency receipt is `evidence/P1_REPRODUCTION_AUDIT_20260906_001.json`, SHA-256 `0fec7f01bcec518ad0f14ae26fd4591744e25dd7475e043fbf5512670b67bab4`. Its code/config/trace enter the next human-published checkpoint; until remote readback, they remain locally verified but not GitHub-verified. The new handoff updates expected old bytes and preserves a backup; the original first-checkpoint transfer source is unchanged.

No authoritative usage reading, unattended continuation, enforced independent reviewer, laptop reboot persistence or large-output transfer has been established. HPC allocation remains unmeasured. The small run did not require a GPU or cluster; no conclusion about the later programme's compute scale follows.

### Appended incremental-transfer check, 2026-09-06

A candidate package containing the complete raw trace was published to a local bare fixture and read back byte for byte; retry retained the same commit. The final transfer-source revision passed this check. Receipt: `evidence/CHECKPOINT_002_RELEASE_ROUNDTRIP.json`, SHA-256 `2f5c32697b1a4fb1a9cd42057372d9b21d53e3c9aa4b9f3bb6ce8ae6e28287c1`. Endpoint for eventual independent real verification: [authorized GitHub repository](https://github.com/afazeliUofT/arc-independent-lab), accessed 2026-09-06. This local test does not establish actual checkpoint-002 publication or laptop execution.

A targeted pre-delivery regression exposed acceptance of a staged deletion on retry for a newly added payload file. The new helper now rejects staged deletions before index changes; the original first-checkpoint helper was untouched. Before/after evidence: `evidence/CHECKPOINT_UPDATE_INDEX_REGRESSION_2026-09-06.json`, SHA-256 `0883f3c442b9b162ed1604b4b74d2d3406c42c8481fcf80adde40bd05bb9a577`. The root initially described the defect too broadly after reading a pre-freeze source snapshot; the pinned version already guarded files present at the base. That scope correction is preserved in the methods note. This transfer-code revision did not change experimental source, configuration, evidence thresholds or raw results.

## Appended confirmed Git conversion and tested correction, 2026-09-06

Ali's read-only laptop report confirms that Git normalized only the CSV's committed bytes under `core.autocrlf=input`, while every declared working file retained its expected bytes. A clean tracked status did not establish byte preservation. Source: `evidence/CHECKPOINT_002_LAPTOP_DIAGNOSTIC_2026-09-06.json`, SHA-256 `f168ac553d2ac11d1b900ef7da7cc60a5c535bf0ec046f92b858506dcd8ee73c`. The first transfer tests had not covered this setting.

A new repair helper preserves the original commit and working CSV, stages it under an artifact-specific -text rule, verifies every declared hash, and adds a correction commit. It passed bounded real-Git local checks including a rejected push and repeat execution. Receipt: `evidence/CHECKPOINT_002_REPAIR_VERIFICATION.json`, SHA-256 `5d1ba6955e0b7dbf33a05c81678a6baab08c7f951d1833a4f126e57a6756bc71`. The actual user-run repair and GitHub readback remain pending. Source for the documented attribute behavior: [Git attributes, version 2.43.0](https://git-scm.com/docs/gitattributes/2.43.0), accessed 2026-09-06. The local test interpreter used the Git version recorded in the receipt, not the laptop executable.

## 2026-09-06: repair timeout and missing operation identity

The actual laptop repair encountered a generic Git timeout. The old helper enforced per-command and total caps but did not retain the timed-out command or partial output, and captured successful mutation output silently. That is an observability defect. It leaves post-timeout local commit status unknown even though GitHub main still points to the initial checkpoint. Evidence: `evidence/CHECKPOINT_002_REPAIR_TIMEOUT_2026-09-06.json`, SHA-256 `80f145ddc5279ccc33387db0fc5bbf66df398e71cace30bb09be62b7dc59d020`. No claim that authentication, network transport or signing was the cause. The new read-only diagnosis and its boundaries are in `docs/CHECKPOINT_002_TIMEOUT_HANDOFF.md`. Shipped repair bytes are preserved.

## Verified local correction and direct publication handoff, 2026-09-06

The timeout probe now verifies corrected local HEAD `6c69eca83cadd0346d85110af470a61f3f075d5d`, all original inspection guards and a successful remote read. GitHub main still points to checkpoint001. Receipt: `evidence/CHECKPOINT_002_CORRECTION_PRESENT_2026-09-06.json`, SHA-256 `5bfcac6b6ea14c87d875dc217de18dc854d91a21d7e22e8a002c8345639654cd`; [remote ref](https://api.github.com/repos/afazeliUofT/arc-independent-lab/git/ref/heads/main), accessed 2026-09-06. This resolves present local correction state, not the exact earlier timeout cause.

Current human action is the guarded foreground push in `docs/CHECKPOINT_002_PUSH_EXISTING_COMMIT.md`. It reuses the original local inspection, checks the measured SHA and publishes that existing commit with visible Git progress and normal local authentication. No new repair helper, staging or commit is needed. Keep credentials local. Publication/readback still gates scientific continuation; the already recorded human answer is not requested again.

## Confirmed VS Code credential IPC failure, 2026-09-06

The foreground operation now reports `ECONNREFUSED` connecting to `/run/user/1000/vscode-git-0c56237c84.sock`, followed by GitHub refusing an anonymous write and a reported status128. The local exact-byte correction passed the preceding inspection; GitHub main remains checkpoint001 in the independent GitHub-plugin read. Receipt: `evidence/CHECKPOINT_002_VSCODE_AUTH_FAILURE_2026-09-06.json`, SHA-256 `cbd43b9c3eb6a7afd980c1a14ab7b16de9a18e1a76480ec5e5e40f4235bef21d`.

The immediate failure is the local VS Code credential-request bridge. Current official [askpass entry point](https://github.com/microsoft/vscode/blob/main/extensions/git/src/askpass-main.ts) routes IPC exceptions through its generic credential-error message; the [IPC client](https://github.com/microsoft/vscode/blob/main/extensions/git/src/ipc/ipcClient.ts) uses `VSCODE_GIT_IPC_HANDLE` as its local socket path. [Terminal credential integration](https://github.com/microsoft/vscode/blob/main/extensions/git/src/askpass.ts) supplies the askpass environment. All accessed 2026-09-06 through the selected GitHub plugin. Installed VS Code version is unmeasured. These sources support the observed failure path, not a claim about why its listener stopped.

Credential validity/expiry and GitHub account permissions have not been established. A stale terminal environment following a closed/restarted/disconnected VS Code session is a plausible explanation, not a measurement. This signature explains the current push failure; the earlier generic timeout may have a different cause.

The three reported publication attempts remain in history and will not be repeated unchanged. Repository repair is complete; the next human operation is to restore the newly diagnosed authentication path: create a new WSL integrated terminal from a currently running VS Code window for this lab and complete normal GitHub sign-in locally when requested. Do not shut down WSL, reload unrelated programme windows, reset this repository, weaken authentication, change global Git configuration or disclose tokens. A fresh terminal is a targeted first recovery step, not a guarantee that credentials already exist or are valid.

The pasted command also omits the continuation backslash between push and its SHA refspec. If entered literally, those are two commands; the reported status and omitted shell error do not establish that literal execution. This formatting issue cannot explain the observed credential IPC failure. Future push commands will keep the complete refspec on one physical line. After authentication recovery, the already authorized fixed-SHA publication command is:

```bash
git -C ~/ARC_Independent_Lab push --progress origin 6c69eca83cadd0346d85110af470a61f3f075d5d:refs/heads/main
```

This is human-observed execution with normal authentication and manual cancellation, not an automatic retry. Use the original inspection if repository contents changed since the successful check. Return only nonsecret completion/error output. Any claimed success still requires independent remote blob/history verification and preservation of the hosted recovery overlay before scientific continuation. The existing human phase-continuation answer need not be repeated.

## Checkpoint002 closure and checkpoint003 transfer boundary, 2026-09-06

The actual public correction was verified from repository bytes and history, then adopted without resetting hosted working files. Recovery evidence and the human answer remain preserved. The new checkpoint003 helper makes no network calls or commits; it checks staged bytes before the human commit. Its contained regression evidence covers the previous CRLF conversion and staged-deletion failures. This is a tested transfer procedure, not evidence of enforced reviewer isolation, subscription metering or unattended continuation. Large-output durability still needs Gate0 resolution before relevant runs.

## Phase3 first audit checkpoint and capability inventory — 2026-09-06

Checkpoint006 and the published Phase2 approval were verified byte-for-byte and adopted locally without overwriting the hosted worktree. Receipt: `evidence/PHASE2_APPROVAL_AND_CHECKPOINT006_VERIFICATION.json`, SHA-256 `2eedb9d6ac2a6c63ee99d333e2ec334f1f7d474e6343933a30364645781d139c`. [Verified approval commit](https://github.com/afazeliUofT/arc-independent-lab/commit/d9200bd6061a63cf82037c2fc31f361fa0109cb3), accessed 2026-09-06. This confirms the small-artifact bridge, not a large-output transfer plan.

The first Phase3 audit has no treatment run or formal verdict. Its source consultations share the PI filesystem and tools. The current exposed tool registry supplies no authoritative allowance reading or enforceable per-sub-agent read-only role. This is a scoped observation, not a claim about every provider product. Unattended model use remains disabled.

A bounded capability inventory is prepared for human execution on WSL and Alliance. It calls version/help and read-only resource metadata commands and saves fresh reports within the lab. It does not invoke a model, install software, change settings, submit jobs or inspect another programme. Source and limits: `docs/P3_GATE0_CAPABILITY_INVENTORY.md`; contained checks `evidence/P3_GATE0_CAPABILITY_INVENTORY_VERIFICATION.json`, SHA-256 `3480b6cd430d188c742a5118f7efa44f20389c9ed582c71039f38737b687d85c`. Advertised controls, actual enforcement, configured limits and remaining allocation remain distinct. No laptop/cluster execution is claimed by the contained checks.

Publication of checkpoint007 uses the existing human commit/push authorization; it does not require a new scientific approval. Capability reports are factual observations, and can be supplied asynchronously while the remaining bounded audit proceeds. `state/ESCALATION.md` remains empty because no new human decision or formal verdict is currently requested. A later actual phase/reviewer dependency will use the prescribed answered-file protocol.
