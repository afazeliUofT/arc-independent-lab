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
