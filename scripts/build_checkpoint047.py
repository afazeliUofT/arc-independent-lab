#!/usr/bin/env python3
"""Build the complete public-history047 offline-assessment handoff."""
from pathlib import Path
import argparse
import hashlib
import io
import json
import subprocess
import tempfile
import zipfile


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def build(repo, output):
    repo = repo.resolve()
    commit = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'refs/heads/main'], text=True).strip()
    assessment_path = 'evidence/P3_CHECKPOINT_046_RETURN_VERIFICATION_047.json'
    def blob(path):
        return subprocess.check_output(['git', '-C', str(repo), 'show', commit + ':' + path])
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='bundle047-', dir=output.parent) as folder:
        bundle_path = Path(folder) / 'repo.bundle'
        subprocess.run(['git', '-C', str(repo), 'bundle', 'create', str(bundle_path.resolve()), 'refs/heads/main'], check=True)
        bundle = bundle_path.read_bytes()
    release = {'kind': 'P3_CHECKPOINT_047_RELEASE_v1',
               'repository': 'afazeliUofT/arc-independent-lab',
               'release_commit': commit, 'bundle_sha256': digest(bundle),
               'assessment_path': assessment_path, 'assessment_sha256': digest(blob(assessment_path))}
    files = {'repo.bundle': bundle,
             'package_release.json': (json.dumps(release, sort_keys=True, indent=2) + '\n').encode(),
             'launch047_home.py': blob('scripts/launch047_home.py'),
             'checkpoint047_workflow.py': blob('scripts/checkpoint047_workflow.py'),
             'README_047.md': b'''# Checkpoint047 complete offline assessment

Save ARC_Independent_Lab_047_HOME.zip in Windows Downloads and use the supplied
one-paste WSL-home command. It verifies this archive and its pinned Git bundle,
checks the existing046 return, and publishes047 REPORT.json and RECEIPT.json.

The complete public history supplies every needed source and original result.
No private paper input is required for this step. No learner, profile, reviewer,
model, target or cluster job starts. The accounting correction is specified, not
implemented or admitted. Do not repeat Development046.

Existing completed047 evidence is reused for publication retries. Unrelated
checkout changes and changed saved evidence are preserved. The next accounting
implementation does not depend on waiting for this synchronization receipt.

Main report: reports/P3_RETURN_046_AND_RESOURCE_DECISION_047.md
Next correction: docs/P3_ACCOUNTING_CORRECTION_PLAN_047.md
'''}
    files['SHA256SUMS'] = ''.join(digest(raw) + '  ' + name + '\n'
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
    if output.exists() and output.read_bytes() != raw:
        raise RuntimeError('Existing different archive preserved: choose a fresh output path')
    output.write_bytes(raw)
    result = {'archive': str(output.resolve()), 'archive_bytes': len(raw),
              'archive_sha256': digest(raw), 'members': len(files), **release}
    print(json.dumps(result, sort_keys=True, indent=2))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    build(args.repo, args.output)
