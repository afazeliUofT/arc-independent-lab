# Scoped primary-source access recheck 037

Date: 2026-09-11 (UTC)

Scope: a bounded access recheck of the two unresolved primary sources named in `P3_SECOND_AUDIT_MANIFEST_036.json`. This is an access record, not an independent scientific review or formal novelty disposition. No candidate was executed and no third-party paper was copied into this repository.

## Result

Neither requested full text was obtained. The source-access dependencies remain open. An inaccessible route does not establish that a paper is unavailable elsewhere or that its method lacks relevant prior work.

| Source | Material actually accessed in this recheck | Consequence |
|---|---|---|
| David Pierce and Benjamin J. Kuipers (1997), *Map learning with uninterpreted sensors and effectors*, supplied DOI `10.1016/S0004-3702(96)00051-3` | No article body or methods; publisher request returned HTTP 403 and attempted author/university routes failed retrieval | The N4 acquisition-of-distinctions/procedures comparison cannot be completed from this recheck. No methods summary is asserted. |
| V. Chvátal (1979), *A Greedy Heuristic for the Set-Covering Problem*, DOI `10.1287/moor.4.3.233` | Publisher bibliographic record and abstract only; both PDF and enhanced-PDF routes redirected to the abstract page | The original greedy-step derivation and exact N1 pair-cover attribution were not checked against the full three-page paper. |

## Verified primary record

The [INFORMS publisher record](https://pubsonline.informs.org/doi/10.1287/moor.4.3.233) verifies Chvátal's paper in *Mathematics of Operations Research* 4(3), pages 233–235, published August 1, 1979. Its abstract concerns weighted binary set cover and reports a logarithmic performance bound in the largest matrix-column sum. It says the equal-cost case recovers earlier results of Johnson and Lovász. This supports the broad historical relevance of greedy set-cover analysis; it does not substitute for reading the algorithm, proof, or establishing a project-specific reduction.

## Route log

| Route | Observed result |
|---|---|
| [Pierce–Kuipers publisher article](https://www.sciencedirect.com/science/article/pii/S0004370296000513) | HTTP 403; no methods returned |
| [Pierce–Kuipers DOI](https://doi.org/10.1016/S0004-3702%2896%2900051-3) | Retrieval rejected by web fetcher; no content returned |
| [Michigan author publication-index candidate](https://web.eecs.umich.edu/~kuipers/research/pubs.html) | Retrieval failed; candidate URL was not validated as an existing page |
| [UT Austin author article-page candidate](https://www.cs.utexas.edu/~kuipers/papers/Pierce-aij-97.html) | Retrieval failed; candidate URL was not validated as an existing page |
| [Michigan author article-page candidate](https://web.eecs.umich.edu/~kuipers/papers/Pierce-aij-97.html) | Retrieval failed; candidate URL was not validated as an existing page |
| [UT Austin research-page candidate](https://www.cs.utexas.edu/~kuipers/research/bootstrap.html) | Retrieval failed; candidate URL was not validated as an existing page |
| [Michigan research-page candidate](https://web.eecs.umich.edu/~kuipers/research/bootstrap.html) | Retrieval failed; candidate URL was not validated as an existing page |
| [Chvátal publisher PDF link](https://pubsonline.informs.org/doi/pdf/10.1287/moor.4.3.233) | Redirected to publisher abstract; no PDF obtained |
| [Chvátal publisher enhanced-PDF route](https://pubsonline.informs.org/doi/epdf/10.1287/moor.4.3.233) | Redirected to publisher abstract; no PDF obtained |
| [Concordia author-publication candidate](https://users.encs.concordia.ca/~chvatal/publications.html) | Retrieval failed; candidate URL was not validated as an existing page |

Exact-title and author/university searches supplied no usable additional primary full text in this bounded attempt. Search-result snippets and unrelated sources were not used as substitutes for the requested methods.

## Review constraint carried forward

Retain the checkpoint 036 distinction: Pierce–Kuipers methods are required before an affirmative N4 whole-priority claim; Chvátal methods remain conditional on named-original attribution of the greedy step. Any focused review that proceeds while these gaps remain should mark those conclusions unresolved and should evaluate only claims supported by the primary methods already available.
