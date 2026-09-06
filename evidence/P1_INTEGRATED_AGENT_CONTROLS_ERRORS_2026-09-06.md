# Access failures in the CLIN / Voyager methods consultation

Date: 2026-09-06. These are retrieval outcomes, not experiment failures. No process exit status was supplied for web-tool failures. Python caught the one HTTP exception; its containing shell process exited 0.

1. `https://openreview.net/forum?id=ehfRiF0R3a` and `https://openreview.net/forum?id=d5DGVHMdsC` returned a browser verification page: `Verifying your browser` / `Complete the check below to continue to OpenReview`. No verification was bypassed.
2. `https://arxiv.org/html/2310.10134v2`: `Failed to fetch https://arxiv.org/html/2310.10134v2: DisabledError`. Read the author's COLM PDF instead.
3. `https://openreview.net/pdf?id=ehfRiF0R3a` returned the same browser verification page. Author arXiv v2 methods were read; final-publication status was verified on the journal's own list, without assuming identical versions.
4. `https://api2.openreview.net/notes?id=ehfRiF0R3a`: `URL https://api2.openreview.net/notes?id=ehfRiF0R3a is not safe to open (non-retryable error)`. No retry of that URL.
5. Journal-list PDF-link click: `Unable to resolve click call: click({"ref_id":"turn19view1","id":13486}) due to invalid arguments`. The supplied tool reference differed from the displayed internal error reference. Neither is a scientific citation.
6. Retrieval of `https://openreview.net/pdf/625b7da181479e7642abce270739da66290f0fa3.pdf` by Python: `HTTPError HTTP Error 403: Forbidden`. No PDF bytes were saved under the attempted filename.

All scientific claims are supported by accessible primary paper versions or explicitly pinned code. No library-access request is required for the present claims; equality with the uninspected final Voyager PDF remains unverified.
