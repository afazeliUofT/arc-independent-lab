# Preserved fallback interface probe — do not run

2026-09-07. `scripts/gate0_reviewer_interface_probe.py` and its validator were prepared while determining how to obtain the installed client's schema. Their evidence is `evidence/GATE0_INTERFACE_HARNESS_VALIDATION_2026-09-07.json`, SHA-256 `3d744978bd8b0757a9533b75abeeded6e925298c0662001e13cbde20515e8f7f`. Validation used substituted Codex responses and ordinary synthetic subprocesses. No actual Codex command, client session or model ran through this harness.

The subsequent static extraction made this proposed human machine request unnecessary. Both compressed source exports match bytes embedded in the exact laptop executable reconstructed from the official release. Read `docs/GATE0_REVIEWER_INTERFACE_DECISIONS_2026-09-07.md` and the manifested static data instead. The fallback source and its checks are retained to preserve the operational record; they are not the next instruction, a verified full-client boundary, or a reason to rerun an interface probe.

The next implementation is the finite reviewer broker and its actual startup/tool/context checks. Existing command canaries are complete. No new schema, general inventory or quota report is requested in checkpoint011.
