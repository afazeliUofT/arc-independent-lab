#!/usr/bin/env python3
"""Build a compact public048 source package from exact committed Git blobs."""
from __future__ import annotations

import argparse
import ast
import importlib.util
import io
from pathlib import Path
import sys
import zipfile

sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location('_build048_safe', Path(__file__).with_name('launch048_home.py'))
safe = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = safe
_spec.loader.exec_module(safe)


def frozen_test_ids(sources):
    """Read the declared direct TestCase methods without importing or running tests."""
    ids = []
    for path in safe.SUITES:
        tree = ast.parse(sources[path], filename=path)
        found = []
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            direct = any((isinstance(b, ast.Attribute) and b.attr == 'TestCase') or
                         (isinstance(b, ast.Name) and b.id == 'TestCase') for b in node.bases)
            methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                       and n.name.startswith('test_')]
            safe.require(not methods or direct, 'test_inheritance_requires_explicit_manifest_revision')
            if direct:
                found.extend(Path(path).stem + '.' + node.name + '.' + name for name in methods)
        safe.require(found, 'empty_frozen_test_suite')
        ids.extend(sorted(found))
    safe.require(len(ids) == len(set(ids)), 'duplicate_frozen_test_id')
    return ids


def build(repo, output, *, commit=None):
    repo, output = Path(repo).absolute(), Path(output).absolute()
    commit = commit or safe.git(repo, 'rev-parse', 'refs/heads/main').decode().strip()
    safe.require(type(commit) is str and safe.re.fullmatch('[0-9a-f]{40}', commit), 'full_commit_pin_required')
    safe.require(not safe.git(repo, 'rev-list', '--max-count=1', safe.PARENT_COMMIT, '^' + commit).strip(),
                 'release_must_descend_from_accepted047')
    sources = {name: safe.git(repo, 'show', commit + ':' + name) for name in safe.SOURCE_PATHS}
    release = {'kind': 'P3_CHECKPOINT_048_RELEASE_v1', 'repository': safe.REPOSITORY,
               'release_commit': commit, 'parent_commit': safe.PARENT_COMMIT,
               'source_sha256': {name: safe.sha(raw) for name, raw in sources.items()},
               'suites': list(safe.SUITES), 'test_ids': frozen_test_ids(sources), 'max_seconds': 300,
               'accounting_correction_complete': False, 'target_admitted': False}
    files = {'source/' + name: raw for name, raw in sources.items()}
    files['package_release.json'] = safe.canonical(release)
    files['README_048.md'] = b'''# Checkpoint048: first accounting correction unit

Save ARC_Independent_Lab_048_HOME.zip in Windows Downloads and use the supplied
one-paste WSL-home command. This compact public package contains every source
needed to run exactly two frozen accounting kernel/static conformance suites.
The043 module supplies only the historical canonical-byte reference.

The launcher verifies the archive, manifest, exact release commit and canonical
GitHub repository. A clean main checkout advances only by fast-forward; local
edits and unrelated unpublished commits are preserved. Internet access and the
existing GitHub credentials are needed to fetch/push; no prior ZIP, paper, model,
profile, target world or cluster job is used by the test invocation.

One reserved invocation is limited to300 seconds and512KiB per private log.
Raw stdout/stderr and durable reservation state remain under .git/checkpoint048.
Only the exact REPORT.json and RECEIPT.json are committed and pushed. A repeat
reuses completed conformance and retries publication. An interrupted reserved
invocation does not run again automatically; its explicit incomplete status is
published for review. Failed tests are reported with IDs and sanitized types.

Passing establishes this limited kernel/static conformance only. The accounting
correction remains incomplete; scientific budget and target admission remain false.
'''
    files['SHA256SUMS'] = ''.join(safe.sha(raw) + '  ' + name + '\n'
                                 for name, raw in sorted(files.items())).encode('ascii')
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name, raw in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 9, 14, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, raw)
    raw = stream.getvalue()
    safe.archive_payloads(raw, safe.sha(raw))
    safe.same_or_new(output, raw)
    result = {'archive': str(output), 'archive_bytes': len(raw), 'archive_sha256': safe.sha(raw),
              'members': len(files), **release}
    print(safe.canonical(result).decode(), end='')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).absolute().parents[1])
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--commit')
    args = parser.parse_args()
    try:
        build(args.repo, args.output, commit=args.commit)
    except (safe.Stop, OSError, ValueError) as error:
        reason = str(error) if isinstance(error, safe.Stop) else type(error).__name__
        print('STOP: ' + reason, file=sys.stderr)
        raise SystemExit(1)
