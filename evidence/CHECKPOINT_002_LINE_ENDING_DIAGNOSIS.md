# Checkpoint 002: measured line-ending hypothesis

Date: 2026-09-06. This is a methods consultation using a contained synthetic repository, not an independent review and not a reading of the user's configuration. No shipped control surface or actual user repository was edited.

## Evidence and scope

The exact reproduction record is `evidence/CHECKPOINT_002_LINE_ENDING_DIAGNOSIS.json`, SHA-256 `7e3189a433fb4c4e9fd0ff8e1c68ecd40cee0d3ce7bf432feeb7a3781a360e52`. The attribute and append-only correction record is `evidence/CHECKPOINT_002_LINE_ENDING_ATTRIBUTES_AND_RECOVERY.json`, SHA-256 `e9b7cbd93c7026d01ae033722025ea7355bd7c872e26646e9f16736edf7bddb1`. These contain exact commands, stderr, file hashes, fixture commit identifiers, and results; no public remote was used.

The actual checkpoint CSV has CRLF line endings. With attributes absent, isolated `core.autocrlf=false` retained its raw bytes in worktree, index and commit. Both `true` and `input` retained raw worktree bytes but normalized index and committed bytes to LF; ordinary status was clean. Raw SHA-256 is `24b2dc318e048493d4f265291935ef02ce09c7221a96422cfc8c0405c02c434a`; LF-only SHA-256 is `f45b2c3d830f985629cb308a12ff11e94afbf7d4b2a436a5441d87595eafd34e`. The JSON records are the authority for these local results.

Explicit `text` also normalized this file with autocrlf disabled. Explicit `-text` preserved it with autocrlf enabled. An already normalized fixture commit was corrected by adding a path-specific `-text` attribute, staging the still-exact worktree file, and appending a commit. The old commit remained unchanged, new HEAD/index/worktree matched raw bytes, and status was clean. This establishes a possible recovery without rewriting history; it is not sufficient to authorize that mutation on the uninspected user repository. The shipped helper also rejects a grandchild of the pinned base, so retrying it after such a correction is not a recovery workflow.

Git's documentation states that the text attribute controls index line-ending normalization; an unset text attribute disables it, and unspecified text uses core.autocrlf. Attributes can come from repository, per-directory, per-user or system sources, with repository info attributes taking priority. A filter or working-tree encoding is a separate possible transformation. [Git gitattributes documentation](https://git-scm.com/docs/gitattributes), accessed 2026-09-06. The autocrlf setting supports true and input, with input omitting output conversion. [Git configuration documentation](https://git-scm.com/docs/git-config), accessed 2026-09-06.

## What the terminal sequence establishes

In the shipped helper, `Existing state` is printed before installation. `Existing HEAD` is printed at the end of the initial repository inspection, after its staged-byte check has passed. `publish` then installs files, stages them, commits locally with captured output, and calls repository inspection again before pushing.

Therefore the supplied terminal's old P1.0 state and printed pinned base HEAD are consistent with the first apply succeeding through local commit, then failing during the second staged-byte check. They do not show that the user remained at P1.0 or at the base commit after the STOP. In particular, this output does not support a claim that nothing was changed locally. The exact local HEAD and worktree now require inspection. Line-ending normalization reproduces a mechanism for this sequence, but the actual cause remains unverified until the user's bytes and effective configuration are read.

## Smallest useful read-only probe

Read helper SHA-256; exact target/root; HEAD and parents; branch; status with optional Git locks disabled; the expected remote's main reference; and worktree/index/HEAD SHA-256 for every payload file, with CRLF/LF counts for the CSV. Read only the configuration keys core.autocrlf, core.eol, core.safecrlf and core.attributesfile with origins, plus the effective text, eol, filter and working-tree-encoding attributes for the CSV. Do not dump full configuration or credential-bearing environment variables. A narrow config key can be absent without implying an error. Do not run the old applying helper again before this evidence is assessed.

Input provenance: supplied terminal SHA-256 `b4fb2b08f97b15265a20da209ca17582a1a641de380c6c9407dd67f91571094d`; inspected shipped helper SHA-256 `fa2053151ce56a21965ed3d83d99eaba2868680079162c00e8d33e3272251262`.
