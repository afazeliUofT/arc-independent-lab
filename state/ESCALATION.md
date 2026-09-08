# Native refresh access for the finite post-login check

The sign-in receipt is accepted. This request extends only the native credential-management permission required by the next concrete check. It does not approve a model run or a scientific verdict.

The previous approved scope, `configs/GATE0_SIGNIN_SCOPE_015.json`, authorized one human sign-in. It did not authorize a subsequent client's credential writes. The containment and credential rules in `00_START_HERE.md` §7 and `04_RESOURCES_AND_SETUP.md` §7 therefore require this extension. Routine read-only metadata preparation has already been done without asking again.

## Prepared action

Run `scripts/gate0_postlogin_metadata.py --run-metadata` through the installed pinned client. Before native access, the same invocation checks a dummy-file boundary and stops if it fails. The native client can then update only its existing `/home/afazeli2006/.codex/auth.json` during normal token refresh. The directory stays unwritable, and parent Python never opens, copies, hashes or exports the credential. Other writes stay within the fresh project run.

This finite process uses inherited host networking for native authentication and metadata; it is not an endpoint allowlist. It requests account status, policy projection, Codex limits and a model-catalog page. No login, model turn, scientific prompt, credit/reset consumption, purchase or paid API use is requested. A completed report is reused.

Why the write grant matters: exact native source refreshes tokens before saving them. Live networking with read-only credentials could allow a server refresh and then prevent saving the result. The chosen grant supports the client's normal in-place save. That native save can be interrupted; the wrapper does not make a credential backup.

Exact scope: `configs/GATE0_POSTLOGIN_SCOPE_016.json`, SHA-256 `fbd7ca325593c9c8de5573417faf1381dbf669b80218f85e4a31ae519beacc61`.
Wrapper: `scripts/gate0_postlogin_metadata.py`, SHA-256 `dd6d7950ed9f811a3a1325e7fec288142a1fd69fa84855dbe9ed2bac544d72a7`.
Validation: `artifacts/GATE0_POSTLOGIN_ENGINEERING/20260908_001/MANIFEST.json`, SHA-256 `63435cd1fa5239bfc9d3fa45f8af57c7d8aae87d99455fef871449c49beb9e1c`. Synthetic tests pass; the hosted environment cannot run the real namespace check, so it is required in the same WSL invocation before credential access.

## Answer protocol

Publish checkpoint016 first. To approve, append the following as an actual section at the end of this file, then commit and push it. This fenced example is not an answer and cannot authorize the wrapper.

```text
## ANSWER
APPROVE_G0_POSTLOGIN_016
scope_sha256: fbd7ca325593c9c8de5573417faf1381dbf669b80218f85e4a31ae519beacc61
```

After the answer is committed and pushed, run the canonical wrapper with `--run-metadata` and share only its `REPORT.json`. The handoff instructions provide exact commands, including folder-opening commands. If you decline, put that decision in an actual ANSWER section; no client will be launched.
