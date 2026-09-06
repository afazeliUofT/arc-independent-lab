# CausaLab metric and verification audit

Status: bounded Phase 1 methods consultation, 2026-09-06. Shared tools/filesystem; no claim of isolated review. Read-only source inspection; no model calls, benchmark execution, or public writes.

## Sources and provenance

Paper: Yang, Zhang et al., *CausaLab: A Scalable Environment for Interactive Causal Discovery Toward AI Scientists*, arXiv:2605.26029v2, 28 May 2026, **preprint**. [Primary HTML](https://arxiv.org/html/2605.26029v2) and [PDF](https://arxiv.org/pdf/2605.26029v2), accessed 2026-09-06. Inspected evaluation, DSL, RQ4, Table 7, and Appendix A.11; the PDF confirms the relevant table and figure values.

The paper's repository URL did not resolve. The [authors' companion page](https://dylanzsz.github.io/causalab/), accessed 2026-09-06, links the live [CausaLab-Benchmark repository](https://github.com/DylanZSZ/CausaLab-Benchmark). GitHub connector reads pinned its default branch to commit **42ba47fb88e60dc1eca17bd29c47ace4e8e9960e**. The recursive tree was not truncated. All code citations below refer to that commit, accessed 2026-09-06. The release postdates paper v2; correspondence to the paper's exact execution version remains unverified.

## What the released metrics compute

In [metrics.py](https://github.com/DylanZSZ/CausaLab-Benchmark/blob/42ba47fb88e60dc1eca17bd29c47ace4e8e9960e/causalab_reeval/metrics.py), `compute_edge_metrics` normalizes aliases, deduplicates directed edges, and scores set intersection. For predicted set P, truth T and C=P∩T, precision is |C|/|P|, recall |C|/|T|, and F1 their harmonic mean. If both sets are empty, each score is one; if exactly one is empty, F1 is zero. Ground-truth roots are specifically parentless ancestors of `resonanceFreq`, not every parentless node in the episode. Root F1 compares this set with the supplied predicted root list. Git blob: `82a59184a4a9e318254a683657a532f181998175`.

The [summary runner](https://github.com/DylanZSZ/CausaLab-Benchmark/blob/42ba47fb88e60dc1eca17bd29c47ace4e8e9960e/causalab_reeval/run_lightweight_reeval.py) averages per-row precision, recall and F1 separately, using numeric entries. Thus its aggregate F1 need not be the harmonic mean of its displayed aggregate precision and recall. Git blob: `4ab8df679973f63c4071dfbfb87fbea2a454785a`.

## Why perfect edges need not imply a perfect reported root score

Table 7 reports GPT-5.2-high, three nodes: all-edge precision/recall/F1=1.000, SHD=0.000, but root F1=0.740. The paper describes scoring the structured hypothesis; its basic DSL has no explicit root field.

The released [reeval_core.py](https://github.com/DylanZSZ/CausaLab-Benchmark/blob/42ba47fb88e60dc1eca17bd29c47ace4e8e9960e/causalab_reeval/reeval_core.py) implements two materially different paths:

- `summarize_seed_for_stage1` derives predicted roots directly from the logged final graph and scores that graph without a model call.
- `summarize_seed_for_reeval` makes a new model call requesting roots and a root-based frequency formula from replayed exploration context. A separate model call receives the final hypothesis and returns its graph, equation and coefficients. Root and edge metrics then score those separate outputs. Both calls can retry at larger output budgets if truncated. Git blob: `e1bfe8694f34a4ed686cee436c85f73b2e391fe2`.

**Our inference:** the second path permits correct graph reporting alongside incorrect root extraction. The apparent discrepancy therefore does not establish a scoring bug. It also need not establish that the acquired graph itself lacks the roots: it may measure failure to answer a different post-run question. The first path would have matching inferred roots for identical complete edge sets. I did not locate the table-linked per-case re-evaluation outputs or manifest identifying which path produced Table 7. Exact reconciliation remains open; do not report the second-path explanation as verified provenance for that table.

## Does 48% to 60% establish equal compute?

RQ4 and Figure 14 attribute this four-node improvement to verification against existing evidence. They do not provide an equal-token, equal-call or equal-runtime control in the inspected methods.

The released [validation prompt](https://github.com/DylanZSZ/CausaLab-Benchmark/blob/42ba47fb88e60dc1eca17bd29c47ace4e8e9960e/agents/recoma/prompts/react_simple_memory_prompt_dsl_validate.txt) instructs consistency checks against all accumulated data at every step, plus explicit acknowledgment and revision when inconsistent. It also differs from the ordinary prompt in observation-management wording. Git blob: `ad5e2f347ee06d872400e9e24f15a1896fced33b`. The inspected [default configuration](https://github.com/DylanZSZ/CausaLab-Benchmark/blob/42ba47fb88e60dc1eca17bd29c47ace4e8e9960e/agents/recoma/configs/react-simple-memory.jsonnet) does not select this validation file. I did not identify a table-linked run manifest establishing that it generated Figure 14.

**Our judgment:** retain 48% to 60% as a reported procedural intervention, with implementation and compute matching unresolved. It supports further scrutiny of evidence checking; it does not uniquely identify overconfidence, establish equal compute, or quantify how much of the gain comes from extra reasoning, revised instructions, or changed action allocation. A cap on allowed interventions alone would not establish equal computational effort.

Needed to settle both issues: exact code commit and command/configuration for Table 7 and Figure 14; per-case original and re-evaluation outputs with generation status; complete baseline/verification prompts; calls, token usage and intervention counts in both arms. The supplied paper PDF is accessible, so this is a missing execution-provenance request, not a request for another paywalled article.

Tool failures are preserved separately in `P1_CAUSALAB_METRIC_AUDIT_ERRORS_2026-09-06.md`.
