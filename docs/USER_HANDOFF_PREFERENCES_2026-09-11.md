# Standing delivery instruction — 2026-09-11

The user explicitly requires this workflow for every subsequent step:

1. Deliver **one ZIP containing the complete step**, including all required scripts and inputs that can lawfully be returned privately.
2. Give **one pasteable command block runnable from WSL home**. It must locate that ZIP in Windows Downloads, copy it into the correct project delivery location, extract it, execute the step and push all required results to the canonical GitHub repository.
3. The PI reads required reports and artifacts from GitHub. Do not require the user to attach output files or find an extraction directory manually.
4. Infer established paths and structure from repository evidence. If a necessary detail genuinely cannot be discovered, provide a bounded diagnostic command that produces it; do not ask the user to guess.

This supersedes the older delivery preference that a ZIP was needed only when a laptop execution or unavailable publication capability required one. Direct publication of original PI research outputs through the connected GitHub remains authorized; it does not substitute for the requested one-package handoff when delivering a step.

The current canonical laptop checkout is WSL `~/ARC_Independent_Lab`; observed account-specific evidence records `/home/afazeli2006/ARC_Independent_Lab`. Its remote is `afazeliUofT/arc-independent-lab`. `delivery/` is ignored and contains private handoff/execution material. `artifacts/` contains deliberately selected public results. The Windows user name must not be inferred from the WSL user name.

No concrete Windows Downloads path was found in the inspected records. Resolve the current Windows Downloads setting at execution time and translate it with `wslpath`. This supports a redirected folder without a guessed user name. The user-facing command should contain no path placeholders.

Repeated execution after a publication failure must preserve prior work and retry returning existing results where appropriate. A retry is not authorization to repeat model work or a completed finite experiment. Do not replace prior results, reset the checkout, publish private paper contents, or infer failed authentication solely from a stale askpass integration error.

## Authority and evidence

The user's instruction in this conversation begins: “You should always give me one .zip package that includes everything.” It explicitly specifies the Downloads-to-WSL-home execution and GitHub return path. The full current message is recorded in `state/PROJECT_STATE.json` alongside this preference.

Repository records inspected at `3ec4ed07a9ee66750228cea606ea37332aef84e9`, accessed 2026-09-11:

- [Earlier handoff preference](https://github.com/afazeliUofT/arc-independent-lab/blob/3ec4ed07a9ee66750228cea606ea37332aef84e9/docs/USER_HANDOFF_PREFERENCES_2026-09-07.md): rerun and publication separation.
- [Inventory run receipts](https://github.com/afazeliUofT/arc-independent-lab/blob/3ec4ed07a9ee66750228cea606ea37332aef84e9/evidence/GATE0_INVENTORY_RUN_RECEIPTS_2026-09-07.json): observed WSL project root.
- [Report retrieval instructions](https://github.com/afazeliUofT/arc-independent-lab/blob/3ec4ed07a9ee66750228cea606ea37332aef84e9/docs/GATE0_REPORT_RETRIEVAL_POWERSHELL.md): recorded WSL user.
- [Ignore rules](https://github.com/afazeliUofT/arc-independent-lab/blob/3ec4ed07a9ee66750228cea606ea37332aef84e9/.gitignore): private delivery location.

Previous-chat retrieval reported that personal context is disabled in this session. No unseen transcript was represented as retrieved. Repository evidence supplies the project layout, and the new command performs the remaining Windows path discovery.
