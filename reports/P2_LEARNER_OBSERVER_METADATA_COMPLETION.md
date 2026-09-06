# Post-run metadata completion for the learner-access diagnostic

Added 2026-09-06T19:19:15.766923+00:00. This supplement preserves every existing run, source, protocol, report and consistency-receipt byte. No experiment was rerun and no result or hypothesis was revised.

The original runner omitted the required filenames `resolved_config.yaml` and `hypotheses.jsonl` from `03_AUTONOMY_SPEC.md` §11. That was a repository-contract omission at run creation. The already frozen protocol contained the prospective hypotheses and the original `resolved_config.json` contained the resolved configuration. Adding filenames afterward does not retroactively establish compliant runtime emission.

The new `resolved_config.yaml` is an exact byte copy of the recorded JSON configuration, which is valid YAML. The new `hypotheses.jsonl` contains only verbatim hypothesis lines from the prospectively frozen protocol. Each record separates the original freeze time from this export time and explicitly disclaims being a runtime hypothesis trace or a newly preregistered hypothesis. The source protocol and freeze receipt are hashed in every record. No imagined per-step hypothesis history was added.

The separate `manifest_completion.json` supplies missing top-level metadata aliases from already recorded configuration, environment and source provenance, and binds the new metadata to the unchanged original manifest and inventory. These are post-run exports of existing information, not new measurements. `ADDITIONAL_SHA256SUMS` covers only these new metadata files; the original `SHA256SUMS` remains unchanged.

The original consistency script checks exact directory membership. Its preserved successful receipt applies to the original pre-export inventory. Rerunning that unchanged script against the expanded directory would reject the additional names. Current archive-integrity checking must therefore check the unchanged original inventory and the additional inventory separately, together with the completion manifest. We do not claim the unchanged original auditor accepts the expanded directory.

The scientific conclusions in `reports/P2_LEARNER_OBSERVER_001.md` remain unchanged. This supplement records an apparatus omission and its limited metadata repair; it does not strengthen the scientific evidence.

Local sources accessed 2026-09-06: `docs/governing/03_AUTONOMY_SPEC.md` §11, `artifacts/P2_LEARNER_OBSERVER/20260906_001/protocol.md`, `protocol_freeze.json`, `resolved_config.json`, and `manifest.json`. Repository contract: [03_AUTONOMY_SPEC.md](https://github.com/afazeliUofT/arc-independent-lab/blob/main/docs/governing/03_AUTONOMY_SPEC.md). Original manifest SHA-256 `b2f06a14433f546ea24d2f49990d38c13ec7b8e1ed945c9b8e09ac17927acac9`; original inventory SHA-256 `62c11df350f2b37f49d020431d8b50083ffd2a8bc2bb50259029f0387e6ff3d3`; original report SHA-256 `5503b185549fcce4daa841a9f4445f53d4f94dc3a43a73440bf877b2d38d1f11`.
