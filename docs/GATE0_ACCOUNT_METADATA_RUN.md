# One contained account observation

2026-09-07. Run on WSL, under the canonical `~/ARC_Independent_Lab`.

The checkpoint013 handoff installs and publishes the code separately from executing it. Do not repeat checkpoint012 startup.

Open the download destination, then copy the checkpoint013 ZIP, helper and Bash handoff into it:

```bash
explorer.exe "$(wslpath -w "$HOME/ARC_Independent_Lab/delivery")"
```

After applying checkpoint013, the direct observation command is:

```bash
python3 -I -B "$HOME/ARC_Independent_Lab/scripts/gate0_account_metadata.py" --run-account
```

The handoff's `observe` mode verifies the complete checkpoint before executing this command. It has a 60-second client deadline plus bounded cleanup. It requests cached account metadata with network access disabled and filters two configuration controls; it cannot invoke a model, log in, read quota, change credentials, or certify independent review.

The fixed report path makes a completed rerun return the same verified report without launching another client. An incomplete prior directory stops instead of overwriting it. Publication failures never launch the observation, and publication retries do not repeat it.

Open the exact report folder after the observation:

```bash
explorer.exe "$(wslpath -w "$HOME/ARC_Independent_Lab/delivery/GATE0_ACCOUNT_METADATA_013")"
```

Attach `REPORT.json` from that folder. If a STOP occurs and no report exists, paste only the printed fixed STOP message; do not send configuration, authentication, runtime logs or raw client responses.

For the already accepted checkpoint012 report, the exact previous folder is:

```bash
explorer.exe "$(wslpath -w "$HOME/ARC_Independent_Lab/delivery/GATE0_CLIENT_PREFLIGHT_20260907T183401.226510Z")"
```
