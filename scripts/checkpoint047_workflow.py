#!/usr/bin/env python3
"""Assess the accepted046 return offline from a complete pinned Git bundle and publish047."""
from __future__ import annotations

import argparse
import fcntl
import importlib.util
import os
from pathlib import Path
import resource
import stat
import subprocess
import sys

sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location('_checkpoint047_safe',
                                             Path(__file__).absolute().with_name('launch047_home.py'))
safe = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = safe
_spec.loader.exec_module(safe)
ASSESSOR = 'scripts/assess_return046.py'
MAX_REPORT = 2 * 1024 * 1024
COMMIT_MESSAGE = 'Checkpoint047: verify returned046 evidence offline and record assessment receipt'


def names(raw):
    return set(raw.decode('utf-8').split('\0')) - {''}


def ancestor(lab, first, second):
    return not safe.git(lab, 'rev-list', '--max-count=1', first, '^' + second).strip()


def expected_outputs(release, assessment):
    base = 'artifacts/CHECKPOINT_047_RETURN/' + release['release_commit']
    report = {'kind': 'P3_CHECKPOINT_047_OFFLINE_RETURN_ASSESSMENT_v1',
              'status': 'MATCHED_PUBLISHED_ASSESSMENT', 'release_commit': release['release_commit'],
              'assessment_path': release['assessment_path'],
              'assessment_sha256': release['assessment_sha256'], 'assessment': assessment,
              'prior_measurements_reexecuted': False, 'reviewer_started': False,
              'model_started': False, 'target_experiment_started': False,
              'future_experiment_admission_asserted': False}
    report_raw = safe.canonical(report)
    safe.require(len(report_raw) <= MAX_REPORT, '047_report_size_limit')
    receipt = {'kind': 'P3_CHECKPOINT_047_OFFLINE_RECEIPT_v1',
               'status': 'ASSESSMENT_COMPLETED', 'release_commit': release['release_commit'],
               'input_identity': release['release_commit'], 'repository': safe.REPOSITORY,
               'report_path': base + '/REPORT.json', 'report_sha256': safe.sha(report_raw),
               'assessment_sha256': release['assessment_sha256'],
               'execution_scope': 'OFFLINE_EXISTING_RETURN_VERIFICATION_ONLY',
               'scientific_execution_admitted': False}
    return {base + '/REPORT.json': report_raw, base + '/RECEIPT.json': safe.canonical(receipt)}


def check_checkout(lab, expected):
    safe.repository_check(lab)
    for args in (('diff', '--name-only', '-z'), ('diff', '--cached', '--name-only', '-z'),
                 ('ls-files', '--others', '--exclude-standard', '-z')):
        changed = names(safe.git(lab, *args))
        safe.require(changed <= set(expected), 'dirty_canonical_checkout_preserved')
        for name in changed:
            safe.require(safe.read_regular(lab / name, MAX_REPORT) == expected[name],
                         'changed047_output_preserved')
            if '--cached' in args:
                safe.require(safe.git(lab, 'show', ':' + name) == expected[name],
                             'changed047_index_preserved')
    # Even a committed older result must not be silently replaced.
    for name, body in expected.items():
        if os.path.lexists(lab / name):
            safe.require(safe.read_regular(lab / name, MAX_REPORT) == body,
                         'changed_existing047_result_preserved')


def validate_snapshot(snapshot, commit):
    safe.directory(snapshot)
    safe.directory(snapshot / '.git')
    safe.require(safe.git(snapshot, 'rev-parse', 'HEAD').decode().strip() == commit,
                 'snapshot_commit_differs')
    safe.require(not safe.git(snapshot, 'status', '--porcelain=v1', '--untracked-files=all'),
                 'snapshot_is_not_immutable')
    rows = safe.git(snapshot, 'ls-tree', '-r', '-z', commit).split(b'\0')
    tracked = set()
    for row in rows:
        if not row:
            continue
        metadata, encoded = row.split(b'\t', 1)
        mode, kind, oid = metadata.decode().split()
        name = encoded.decode('utf-8')
        safe.require(mode in ('100644', '100755') and kind == 'blob',
                     'snapshot_special_tracked_file_refused')
        raw = safe.read_regular(snapshot / name)
        safe.require(safe.git(snapshot, 'hash-object', '--stdin', input=raw).decode().strip() == oid,
                     'snapshot_tracked_bytes_differ')
        tracked.add(name)
    # Includes ignored additions which git status omits.
    actual = set()
    for parent, dirs, files in os.walk(snapshot, followlinks=False):
        if Path(parent) == snapshot:
            dirs.remove('.git')
        for name in dirs:
            safe.directory(Path(parent) / name)
        actual.update((Path(parent) / name).relative_to(snapshot).as_posix() for name in files)
    safe.require(actual == tracked, 'snapshot_extra_or_missing_files')
    safe.require(ASSESSOR in tracked and safe.ASSESSMENT in tracked,
                 'snapshot_assessor_or_assessment_missing')


def load_snapshot(package, release):
    parent = package.parent
    snapshot = parent / 'snapshot'
    bundle = package / 'repo.bundle'
    safe.require(safe.sha(safe.read_regular(bundle)) == release['bundle_sha256'],
                 'bundle_sha256_mismatch')
    heads = safe.git(parent, 'bundle', 'list-heads', str(bundle)).decode().splitlines()
    safe.require(heads == [release['release_commit'] + ' refs/heads/main'],
                 'bundle_release_head_differs')
    if not os.path.lexists(snapshot):
        safe.git(parent, 'clone', '--no-local', '--no-checkout', '--', str(bundle), str(snapshot))
        safe.git(snapshot, 'checkout', '--detach', release['release_commit'])
    validate_snapshot(snapshot, release['release_commit'])
    safe.git(snapshot, 'bundle', 'verify', str(bundle))
    for name in ('checkpoint047_workflow.py', 'launch047_home.py'):
        safe.require(safe.read_regular(package / name) ==
                     safe.read_regular(snapshot / 'scripts' / name),
                     'executing_wrapper_differs_from_release')
    raw = safe.read_regular(snapshot / release['assessment_path'], MAX_REPORT)
    safe.require(safe.sha(raw) == release['assessment_sha256'], 'published_assessment_sha256_differs')
    assessment = safe.parse(raw)
    safe.require(type(assessment) is dict, 'assessment_must_be_object')
    return snapshot, assessment


def run_assessor(snapshot, output):
    def limits():
        resource.setrlimit(resource.RLIMIT_AS, (2 * 1024 ** 3,) * 2)
        resource.setrlimit(resource.RLIMIT_CPU, (240, 240))
        resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_REPORT,) * 2)
    result = subprocess.run([sys.executable, '-I', '-S', '-B', str(snapshot / ASSESSOR),
                             '--repo', str(snapshot), '--output', str(output)],
                            cwd=snapshot, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=300, preexec_fn=limits)
    safe.require(result.returncode == 0, 'offline_assessor_failed:' +
                 result.stderr.decode('utf-8', errors='replace')[-1200:])


def assessment_once(state, snapshot, release, assessment, outputs, assessor):
    safe.directory(state, create=True)
    completed = state / 'COMPLETE.json'
    marker = {'kind': 'P3_CHECKPOINT_047_SAVED_ASSESSMENT_v1',
              'release_commit': release['release_commit'],
              'assessment_sha256': release['assessment_sha256'],
              'outputs': {name: safe.sha(raw) for name, raw in sorted(outputs.items())}}
    reservation = safe.canonical({'release_commit': release['release_commit'],
                                  'assessment_sha256': release['assessment_sha256'],
                                  'execution_scope': 'OFFLINE_EXISTING_RETURN_VERIFICATION_ONLY',
                                  'scientific_work_reexecution': False})
    result_file = state / 'ASSESSMENT.json'
    saved = {Path(name).name: raw for name, raw in outputs.items()}
    if os.path.lexists(completed):
        safe.require(safe.read_regular(completed, MAX_REPORT) == safe.canonical(marker),
                     'changed_saved_completion_preserved')
        safe.require(safe.read_regular(state / 'RESERVED.json') == reservation,
                     'changed_saved_reservation_preserved')
        safe.require(safe.canonical(safe.parse(safe.read_regular(result_file, MAX_REPORT))) ==
                     safe.canonical(assessment), 'changed_saved_assessment_preserved')
        for name, raw in saved.items():
            safe.require(safe.read_regular(state / name, MAX_REPORT) == raw,
                         'changed_saved_result_preserved')
        return
    safe.same_or_new(state / 'RESERVED.json', reservation)
    if not os.path.lexists(result_file):
        # Retrying an interrupted read-only parser is safe when it left no result.
        # Existing results, including malformed or mismatched data, are preserved.
        assessor(snapshot, result_file)
    safe.require(safe.canonical(safe.parse(safe.read_regular(result_file, MAX_REPORT))) ==
                 safe.canonical(assessment), 'offline_result_differs_from_published_assessment')
    validate_snapshot(snapshot, release['release_commit'])
    for name, raw in saved.items():
        safe.same_or_new(state / name, raw)
    safe.same_or_new(completed, safe.canonical(marker))


def publish(lab, package, release, outputs):
    check_checkout(lab, outputs)
    commit = release['release_commit']
    # This only imports complete Git objects; it never moves a branch or worktree.
    safe.git(lab, 'fetch', '--no-tags', str(package / 'repo.bundle'), 'refs/heads/main')
    head = safe.git(lab, 'rev-parse', 'HEAD').decode().strip()
    if not ancestor(lab, commit, head):
        safe.require(ancestor(lab, head, commit), 'canonical_and_release_diverged')
        safe.git(lab, 'merge', '--ff-only', '--no-overwrite-ignore', commit)
    # Incorporate remote descendants only through a normal fast-forward. A diverged
    # human branch is preserved for explicit resolution; no reset/rebase is used.
    safe.git(lab, 'fetch', '--no-tags', 'origin', 'refs/heads/main')
    remote_head = safe.git(lab, 'rev-parse', 'FETCH_HEAD').decode().strip()
    head = safe.git(lab, 'rev-parse', 'HEAD').decode().strip()
    # Never publish a clean but unrelated local commit as a side effect. The only
    # authorized unpublished commits are release ancestry and our exact receipt.
    for ahead in safe.git(lab, 'rev-list', remote_head + '..' + head).decode().splitlines():
        if ancestor(lab, ahead, commit):
            continue
        parents = safe.git(lab, 'rev-list', '--parents', '-n', '1', ahead).decode().split()
        changed = names(safe.git(lab, 'diff-tree', '--no-commit-id', '--name-only', '-r', '-z', ahead))
        safe.require(len(parents) == 2 and changed == set(outputs) and
                     safe.git(lab, 'show', '-s', '--format=%s', ahead).decode().strip() == COMMIT_MESSAGE and
                     all(safe.git(lab, 'show', ahead + ':' + name) == body for name, body in outputs.items()),
                     'unrelated_unpublished_local_commit_preserved')
    for name in names(safe.git(lab, 'ls-tree', '-r', '--name-only', '-z', remote_head,
                               '--', *sorted(outputs))):
        safe.require(name in outputs and safe.git(lab, 'show', remote_head + ':' + name) == outputs[name],
                     'changed_remote047_result_preserved')
    if ancestor(lab, head, remote_head):
        safe.git(lab, 'merge', '--ff-only', '--no-overwrite-ignore', remote_head)
    else:
        safe.require(ancestor(lab, remote_head, head),
                     'canonical_and_remote_diverged; saved assessment needs no reexecution')
    check_checkout(lab, outputs)
    for name, raw in outputs.items():
        safe.same_or_new(lab / name, raw)
    paths = sorted(outputs)
    safe.git(lab, 'add', '--', *paths)
    staged = names(safe.git(lab, 'diff', '--cached', '--name-only', '-z'))
    safe.require(staged <= set(outputs), 'unrelated_staged_files_preserved')
    if staged:
        safe.git(lab, 'commit', '-m', COMMIT_MESSAGE, '--', *paths)
    for name, raw in outputs.items():
        safe.require(safe.git(lab, 'show', 'HEAD:' + name) == raw, 'committed047_result_differs')
    # Non-force push preserves remote changes. A push failure keeps the exact local commit for retry.
    safe.git(lab, 'push', 'origin', 'HEAD:refs/heads/main')
    remote = safe.git(lab, 'ls-remote', '--exit-code', 'origin', 'refs/heads/main').decode().split()
    head = safe.git(lab, 'rev-parse', 'HEAD').decode().strip()
    safe.require(len(remote) == 2 and remote == [head, 'refs/heads/main'],
                 'remote_publication_not_confirmed; saved output is preserved')
    return head


def workflow(lab, package, archive_sha256, *, assessor=None):
    lab, package = Path(lab).absolute(), Path(package).absolute()
    safe.require(package == lab / 'delivery/P3_CHECKPOINT_047' / archive_sha256 / 'package',
                 'package_not_at_expected_delivery_location')
    safe.directory(package)
    raw = safe.read_regular(package.parent / 'PACKAGE.zip')
    payloads, release = safe.archive_payloads(raw, archive_sha256)
    safe.require({item.name for item in package.iterdir()} == safe.MEMBERS,
                 'existing_package_inventory_differs')
    for name, body in payloads.items():
        safe.require(safe.read_regular(package / name) == body, 'extracted_package_differs')
    safe.repository_check(lab)
    state = package.parent / 'state'
    safe.directory(state, create=True)
    lock = state / 'WORKFLOW.lock'
    if os.path.lexists(lock):
        safe.read_regular(lock)
    fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        safe.require(stat.S_ISREG(os.fstat(fd).st_mode) and os.fstat(fd).st_nlink == 1,
                     'unsafe_workflow_lock')
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise safe.Stop('047_workflow_already_running')
        snapshot, assessment = load_snapshot(package, release)
        outputs = expected_outputs(release, assessment)
        check_checkout(lab, outputs)
        assessment_once(state, snapshot, release, assessment, outputs,
                        run_assessor if assessor is None else assessor)
        commit = publish(lab, package, release, outputs)
        return {'status': 'ASSESSMENT_COMPLETED', 'commit': commit,
                'report_path': next(name for name in outputs if name.endswith('/REPORT.json')),
                'receipt_path': next(name for name in outputs if name.endswith('/RECEIPT.json'))}
    finally:
        os.close(fd)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lab', type=Path, default=Path.home() / 'ARC_Independent_Lab')
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--archive-sha256', required=True)
    args = parser.parse_args()
    result = workflow(args.lab, args.package, args.archive_sha256)
    print('Checkpoint047 offline assessment: ' + result['status'])
    print('GitHub receipt: https://github.com/' + safe.REPOSITORY + '/blob/' +
          result['commit'] + '/' + result['receipt_path'])
    print('Returned046 evidence matches the published assessment. No profile, reviewer, model or target experiment was started. Future experiment admission is not asserted.')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (safe.Stop, OSError, ValueError, UnicodeError, subprocess.SubprocessError) as error:
        print('STOP: ' + str(error) + '. Existing files and saved assessment are preserved.', file=sys.stderr)
        raise SystemExit(1)
