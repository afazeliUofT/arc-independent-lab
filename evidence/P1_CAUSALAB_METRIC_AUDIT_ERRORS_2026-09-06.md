# CausaLab metric audit tool errors, 2026-09-06

1. GitHub connector GET `https://api.github.com/repos/DylanZSZ/CausaLab` returned `isError: true` with the following text:

```text
GitHub API error 404: {"message":"Not Found","documentation_url":"https://docs.github.com/rest/repos/repos#get-a-repository","status":"404"}
```

2. Web open `https://github.com/DylanZSZ/CausaLab` returned:

```text
Internal Error ()
```

No shell exit code exists for these tool results. Subsequent retrieval used the different repository URL explicitly linked on the authors' companion page, `https://github.com/DylanZSZ/CausaLab-Benchmark`, successfully; no guessed file paths or credentials were used.
