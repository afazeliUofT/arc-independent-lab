# Residual audit access and processing errors

2026-09-07. Verbatim consultation records follow. These are our operational notes, not paper contents. Sources were accessed through legitimate public copies; unused inaccessible sources are not evidence.

# Source access and local processing notes

2026-09-07. Private research provenance. No source-access control was bypassed. Original PDF downloads remain unchanged; OCR/extracted text is secondary working material.

## Access failures

The first Lovell download at `https://elischolar.library.yale.edu/cgi/viewcontent.cgi?article=1379&context=cowles-discussion-paper-series` returned:

```text
HTTP Error 403: Forbidden
```

The old Cowles URL `https://cowles.yale.edu/sites/default/files/files/pub/d01/d0151.pdf` redirected in web retrieval to a site search page. A search located the actual institutional migrated PDF, `https://cowles.yale.edu/sites/default/files/2022-08/d0151.pdf`; that download succeeded.

The web parser returned `Internal Error` for the first Yale PDF route and inaccessible publisher/SSRN attempts. It reported the following for the optional NIST Rao paper:

```text
Failed to fetch https://nvlpubs.nist.gov/nistpubs/jres/68B/jresv68Bn4p151_A1b.pdf: (400) Content length is too large: 24603884
```

Rao was not used by this consultation as a read primary source. The parent operator was informed.

The optional Cowles publication-page fetch at `https://cowles.yale.edu/node/142565` failed:

```text
Traceback (most recent call last):
  File "<stdin>", line 3, in <module>
  File "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/urllib/request.py", line 215, in urlopen
    return opener.open(url, data, timeout)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/urllib/request.py", line 521, in open
    response = meth(req, response)
               ^^^^^^^^^^^^^^^^^^^
  File "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/urllib/request.py", line 630, in http_response
    response = self.parent.error(
               ^^^^^^^^^^^^^^^^^^
  File "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/urllib/request.py", line 559, in error
    return self._call_chain(*args)
           ^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/urllib/request.py", line 492, in _call_chain
    result = func(*args)
             ^^^^^^^^^^^
  File "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/urllib/request.py", line 639, in http_error_default
    raise HTTPError(req.full_url, code, msg, hdrs, fp)
urllib.error.HTTPError: HTTP Error 403: Forbidden
```

The attempted final CVF Davari page returned:

```text
Failed to fetch https://openaccess.thecvf.com/content/CVPR2022/html/Davari_Probing_Representation_Forgetting_in_Supervised_and_Unsupervised_Continual_Learning_CVPR_2022_paper.html: (403) Forbidden
```

The separately obtained, version-pinned author preprint settles the information-access comparison; final publication text is not claimed read.

## OCR processing error and correction

The first four-worker OCR attempted 30-second per-page subprocess deadlines without limiting Tesseract's own thread count. It failed on one page; the first version did not save completed pages individually, so the combined output file did not exist. The failed read was:

```text
rg: private_sources/P3_OBSERVER/lovell1963_ocr.txt: IO error for operation on private_sources/P3_OBSERVER/lovell1963_ocr.txt: No such file or directory (os error 2)
```

The OCR process returned:

```text
Traceback (most recent call last):
  File "<stdin>", line 8, in <module>
  File "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/concurrent/futures/_base.py", line 619, in result_iterator
    yield _result_or_cancel(fs.pop())
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/concurrent/futures/_base.py", line 317, in _result_or_cancel
    return fut.result(timeout)
           ^^^^^^^^^^^^^^^^^^^
  File "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/concurrent/futures/_base.py", line 456, in result
    return self.__get_result()
           ^^^^^^^^^^^^^^^^^^^
  File "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/concurrent/futures/_base.py", line 401, in __get_result
    raise self._exception
  File "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/concurrent/futures/thread.py", line 59, in run
    result = self.fn(*self.args, **self.kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<stdin>", line 6, in read
  File "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/subprocess.py", line 550, in run
    stdout, stderr = process.communicate(input, timeout=timeout)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/subprocess.py", line 1209, in communicate
    stdout, stderr = self._communicate(input, endtime, timeout)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/subprocess.py", line 2116, in _communicate
    self._check_timeout(endtime, orig_timeout, stdout, stderr)
  File "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/subprocess.py", line 1253, in _check_timeout
    raise TimeoutExpired(
subprocess.TimeoutExpired: Command '['tesseract', 'private_sources/P3_OBSERVER/lovell1963_p21.png', 'stdout']' timed out after 30 seconds
```

Retry used the already rendered page PNGs, four workers with `OMP_THREAD_LIMIT=1`, a 60-second per-page deadline, and per-page output files. All 50 pages completed; combined OCR contains 69,104 characters including page headings. Mathematical theorem statement and proof were then inspected in rendered PDF pages 30 and 46 (printed pp. 28 and 44). No experimental run occurred.

## C4 follow-up edit parser error

2026-09-07: First follow-up edit call failed at JavaScript parsing before any command or mutation ran. Exact tool output:
Script error:
SyntaxError: Unexpected identifier 'evidence'
Cause: Markdown backticks inside a JavaScript template literal. Retried with explicit Python character construction; requested edits succeeded.
