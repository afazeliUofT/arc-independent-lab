# One supported human sign-in for reviewer preparation

2026-09-07. Prepared action, not an executed sign-in or an independent review.

The scientific purpose is to let a separate, restricted, fresh-context process scrutinize the frozen novelty audit. Diagnosis and ideation are approved. Final selection and PROGRAMME.md remain incomplete. Recent account and publication checks add no evidence about learning. The account observation already established that the authorized namespace had no cached account; repeating it before an access change cannot resolve that dependency.

## Exact permission and why it is needed

The authoritative scope is `configs/GATE0_SIGNIN_SCOPE_015.json`, SHA-256 `6020d46ae6818f6c15341a7074ea4f7306b3764d8c64a92d0dcce745ed1c7ccd`. This is one native browser sign-in, operated by Ali. The programme will not see or copy credentials. It requires the explicit exception in `04_RESOURCES_AND_SETUP.md` section 6 and `03_AUTONOMY_SPEC.md` section 6, reasons 1 and 5: the observed native file backend stores credentials outside the project, in `~/.codex/auth.json`.

Ordinary native login can also write private login logs and support files under the existing Codex installation. The wrapper refuses a configured log directory outside that installation or the project. Browser cookies/session state and the localhost callback are part of the sign-in. No backend, home directory, account-security setting or managed policy is changed by the wrapper.

The exact native command, reached only after the wrapper's checks and the recorded approval, is:

```bash
"$HOME/.codex/packages/standalone/releases/0.151.0-x86_64-unknown-linux-musl/bin/codex" login
```

Use the existing ChatGPT subscription. Do not choose an API-key login or buy credits. A successful sign-in is not proof of access to GPT-6 Astra Ultra, an authoritative allowance, or a complete reviewer boundary. Those remain separate measurements. Unattended model use remains disabled.

## Native effects that must not be hidden

The pinned CLI loads authentication policy, opens its native login log and calls authentication cleanup/revocation before initiating browser login. The wrapper refuses an existing or symlinked `auth.json` without opening it, and checks the recorded configuration provenance. This avoids knowingly replacing an existing file-backed account; it does not assert that the whole host is logged out.

The browser flow contacts the authentication service and persists native credentials. It also attempts an optional API-key-style token exchange and may store that token with ChatGPT authentication mode. That is native authentication, not a model usage request; this approval authorizes no API model use or spending. No terminal/browser transcript, native log, token, credential contents or credential hash belongs in the programme's report or repository.

The source can cancel an existing login listener on its default callback port. The wrapper therefore checks that port before launching and refuses an occupied port. Do not start a parallel login. The preliminary bind check cannot provide atomic exclusion against another process starting afterward.

This is a finite attended action, capped at the scope's timeout. Its result is a nonsecret receipt: native exit status, whether the credential file is present afterward, source identities and completion flags. It does not inspect the credential or call `login status`. A verified completed receipt is reused; an incomplete prior attempt stops. If sign-in fails, preserve it and report the receipt rather than repeatedly replacing account state.

## Human sequence

1. Publish checkpoint015 with its supplied publication command. This publishes the request and code; it does not authorize or run sign-in.
2. To approve, append the following to `state/ESCALATION.md` on GitHub, commit and push that edit. The exact scope hash fixes what you are approving:

```text
## ANSWER
APPROVE_G0_SIGNIN_015
scope_sha256: 6020d46ae6818f6c15341a7074ea4f7306b3764d8c64a92d0dcce745ed1c7ccd
```

3. Pull that answer in WSL and launch the guarded human action:

```bash
git -C "$HOME/ARC_Independent_Lab" pull --ff-only &&
python3 -I -B "$HOME/ARC_Independent_Lab/scripts/gate0_human_signin.py" --sign-in
```

Complete the browser flow privately. If WSL does not open a browser, use the native client's displayed login link in your Windows browser yourself. Do not paste that link or any login output into this conversation.

4. Open the result folder and attach only `REPORT.json`:

```bash
explorer.exe "$(wslpath -w "$HOME/ARC_Independent_Lab/delivery/GATE0_HUMAN_SIGNIN_015")"
```

If you decline, append `## ANSWER` and `DECLINE_G0_SIGNIN_015` instead. The existing evidence remains intact; this reviewer-access route is suspended. No alternate credential route or weakening of independence is silently substituted.

## Source evidence and rejected alternatives

Official documentation identifies browser ChatGPT sign-in as the subscription route, explains cached credentials and private native login logs, and describes device-code sign-in as an alternative that can require an account setting. It distinguishes authentication from workspace access and policy. [Authentication documentation](https://learn.chatgpt.com/docs/auth), accessed 2026-09-07. Version-specific effects above are source analysis, not claims that sign-in was executed.

Pinned source commit: `78c290807ce710180111df227df3b7a4fe845452`. [CLI dispatch](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/cli/src/main.rs), [CLI login](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/cli/src/login.rs), [browser callback and token persistence](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/login/src/server.rs), and [credential storage](https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/login/src/auth/storage.rs), all accessed 2026-09-07. New source archive manifest: `artifacts/GATE0_LOGIN_SOURCE/20260907_001/MANIFEST.json`, SHA-256 `f67702c332474b345fa7579ccd4947ffbd7081ac01641dcbe6843447f91baf8d`. Existing source archive manifest: `artifacts/GATE0_SUBSCRIPTION_SOURCE/20260907_001/MANIFEST.json`, SHA-256 `fb8be6505d401ad77e83ebe61b9e9888d9fb2de0f281aa245fc77e3652928270`.

An app-server login avoids the CLI's preliminary cleanup but still needs native credential storage and adds a custom login transport and completion lifecycle. It does not remove this permission dependency. Ephemeral authentication would change the observed backend and lose cross-process persistence. Device-code login is a supported fallback, but changing an account security setting is not included here. Ordinary browser login is the smaller current route.

After a receipt establishes completion, the next preparation is a new filtered post-login account/policy/entitlement observation using the supported native session. Do not rerun report013 or invoke a scientific reviewer before the applicable access, policy and full fresh-context/tool boundary are established. The next scientific decision remains independent scrutiny of the candidate reductions and joint/observer corrections; a confirmed negative would justify an explicitly separate return to description-discovery ideation with screening off.

## Prepared-action validation

The final wrapper passed its targeted synthetic refusal, approval and retry checks; native login, TTY and callback operations were stubbed. This is engineering validation only. Final wrapper SHA-256 `6afaa0d36ee3162a5043b3252757b49acfb669944951ac1ccdeb200ba0a75f63`. Controlling harness manifest: `artifacts/GATE0_HUMAN_SIGNIN_HARNESS/20260907_001/MANIFEST.json`, SHA-256 `b4ea6f4e8021e28a6677986abc7f67c0f64fed3fd14460433ae77888dc4cfff8`. Native wait is capped by the permission scope; termination cleanup may take up to eight additional seconds. No actual sign-in or scientific reviewer has run.
