#!/usr/bin/env python3
"""Human-run installation, evidence collection and explicit Git publication.

The fixed032 model operation is owned by review032_workflow, never by Git retry.
Only declared package files and exact collector outputs enter the commit.
"""
from pathlib import Path, PurePosixPath
import hashlib
import importlib.util
import json
import os
import stat
import subprocess
import sys

BASE = '39eae612ddb72a97979f001cd7f2385df8420bd1'
REMOTE = 'https://github.com/afazeliUofT/arc-independent-lab.git'
META = 'delivery/P3_032_PUBLICATION'
POINTER = 'state/LATEST_REVIEW_032_RETURN.json'
MAX_FILE = 32 * 1024 * 1024


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()


def safe_name(name):
    p = PurePosixPath(name)
    if (type(name) is not str or not name or p.is_absolute() or p.as_posix() != name
            or any(x in ('.', '..', '.git') for x in p.parts)
            or any(ord(c) < 32 for c in name) or '\\' in name or ':' in name):
        raise RuntimeError('Unsafe publication path')
    return name


def plain(path, directory=False):
    path = Path(path).absolute()
    cursor = Path(path.anchor)
    for part in path.parts[1:]:
        cursor /= part
        if cursor.is_symlink():
            raise RuntimeError('Symlink in publication path')
    s = path.stat()
    if directory:
        if not stat.S_ISDIR(s.st_mode):
            raise RuntimeError('Publication directory is not plain')
    elif not stat.S_ISREG(s.st_mode) or s.st_nlink != 1 or s.st_size > MAX_FILE:
        raise RuntimeError('Publication file is not a bounded single-link file')
    return s


def read(path):
    before = plain(path)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        opened = os.fstat(fd)
        if (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino):
            raise RuntimeError('Publication input changed while opening')
        body = bytearray()
        while len(body) <= MAX_FILE:
            part = os.read(fd, min(65536, MAX_FILE + 1 - len(body)))
            if not part:
                break
            body.extend(part)
        after = os.fstat(fd)
        if len(body) > MAX_FILE or (opened.st_size, opened.st_mtime_ns, opened.st_ctime_ns) != (
                after.st_size, after.st_mtime_ns, after.st_ctime_ns):
            raise RuntimeError('Publication input changed during reading')
        return bytes(body)
    finally:
        os.close(fd)


def write_new_or_equal(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    plain(path.parent, True)
    if os.path.lexists(path):
        if read(path) != raw:
            raise RuntimeError('Existing publication file differs; preserved')
        return
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    with os.fdopen(fd, 'wb') as f:
        f.write(raw)
        f.flush()
        os.fsync(f.fileno())


def git_env():
    env = os.environ.copy()
    for key in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_COMMON_DIR',
                'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'):
        env.pop(key, None)
    env['GIT_OPTIONAL_LOCKS'] = '0'
    return env


def git(root, *args, input=None):
    p = subprocess.run(['git', '--no-pager', '-C', str(root), *args], input=input,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=git_env(), timeout=60)
    if p.returncode:
        # Never propagate arbitrary credential-helper output into public evidence.
        raise RuntimeError('Local Git check failed: ' + args[0])
    return p.stdout


def names(raw):
    return {safe_name(x.decode()) for x in raw.split(b'\0') if x}


def repository_check(root):
    plain(root, True)
    if git(root, 'rev-parse', '--show-toplevel').decode().strip() != str(root):
        raise RuntimeError('Wrong repository root')
    if git(root, 'branch', '--show-current').decode().strip() != 'main':
        raise RuntimeError('Use the existing main branch; no branch was changed')
    for flag in ((), ('--push',)):
        remote = git(root, 'remote', 'get-url', *flag, 'origin').decode().strip().rstrip('/')
        if remote.removesuffix('.git') != REMOTE.removesuffix('.git'):
            raise RuntimeError('Origin differs from the authorized repository')
    git(root, 'merge-base', '--is-ancestor', BASE, 'HEAD')


def verify_declared(root, rows):
    for name, row in rows.items():
        safe_name(name)
        p = root / name
        if sha(read(p)) != row['sha256']:
            raise RuntimeError('Declared publication file changed: ' + name)


def stage_exact(root, rows):
    verify_declared(root, rows)
    staged = names(git(root, 'diff', '--cached', '--name-only', '-z'))
    if staged - set(rows):
        raise RuntimeError('Unrelated staged files preserved; publication stopped')
    for name in staged:
        if sha(git(root, 'show', ':' + name)) not in (
                rows[name]['sha256'], rows[name].get('old_sha256')):
            raise RuntimeError('Unexpected staged bytes preserved: ' + name)
    records = []
    for name, row in sorted(rows.items()):
        body = read(root / name)
        oid = git(root, 'hash-object', '-w', '--stdin', input=body).decode().strip()
        actual = hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest()
        if oid != actual:
            raise RuntimeError('Stored Git blob differs')
        records.append(('100644 ' + oid + '\t' + name + '\0').encode())
    git(root, 'update-index', '-z', '--index-info', input=b''.join(records))
    for name, row in rows.items():
        if sha(git(root, 'show', ':' + name)) != row['sha256']:
            raise RuntimeError('Staged bytes differ: ' + name)


def publish_pending(root, pending):
    rows = pending['files']
    verify_declared(root, rows)
    current = git(root, 'rev-parse', 'HEAD').decode().strip()
    if current != pending['parent']:
        parents = git(root, 'show', '-s', '--format=%P', 'HEAD').decode().split()
        if parents != [pending['parent']]:
            raise RuntimeError('Pending publication HEAD is not the prepared parent or exact child')
        changed = names(git(root, 'diff', '--name-only', '-z', pending['parent'], 'HEAD'))
        if changed - set(rows):
            raise RuntimeError('Existing child has unrelated changes; preserved')
        for name, row in rows.items():
            if sha(git(root, 'show', 'HEAD:' + name)) != row['sha256']:
                raise RuntimeError('Existing child bytes differ from pending publication')
    stage_exact(root, rows)
    if git(root, 'diff', '--cached', '--name-only').strip():
        if current != pending['parent']:
            raise RuntimeError('Unexpected staged changes after exact child verification')
        subprocess.run(['git', '-C', str(root), 'commit', '-m',
                        pending['commit_message']],
                       env=git_env(), check=True)
    current = git(root, 'rev-parse', 'HEAD').decode().strip()
    if current != pending['parent'] and git(root, 'show', '-s', '--format=%P', 'HEAD').decode().split() != [pending['parent']]:
        raise RuntimeError('Committed HEAD is not the exact prepared child; push stopped')
    changed = names(git(root, 'diff', '--name-only', '-z', pending['parent'], 'HEAD'))
    if changed - set(rows):
        raise RuntimeError('Commit includes unrelated changes; push stopped')
    for name, row in rows.items():
        if sha(git(root, 'show', 'HEAD:' + name)) != row['sha256']:
            raise RuntimeError('Committed publication bytes differ')
    print('PUSHING VERIFIED EVIDENCE: ' + current, flush=True)
    result = subprocess.run(['git', '-C', str(root), 'push', '--progress', 'origin',
                             current + ':refs/heads/main'], env=git_env())
    if result.returncode:
        print('PUSH FAILED: local commit and pending publication preserved. Repeat the same032 command; it will retry publication without invoking the reviewer.', flush=True)
        return result.returncode
    done = root / META / ('PUBLISHED_' + current + '.json')
    write_new_or_equal(done, encoded(pending))
    print('PUBLISHED: https://github.com/afazeliUofT/arc-independent-lab/commit/' + current, flush=True)
    if pending['phase'] == 'SETUP':
        write_new_or_equal(root / META / 'SETUP_PUBLISHED.json', encoded({'commit':current, 'files':rows, 'kind':'P3_032_SETUP_PUBLISHED_v1'}))
        print('SETUP PUBLISHED: exact source and standing authorization are durable. No reviewer has been launched by publication.', flush=True)
    else:
        print('RETURN INDEX: ' + pending['return_index'], flush=True)
        print('No attachments are needed. Tell the PI that GitHub is updated.', flush=True)
    (root / META / 'PENDING.json').unlink()
    return 0


def install(root, bundle, manifest):
    rows = manifest['files']
    working = names(git(root, 'diff', '--name-only', '-z'))
    staged = names(git(root, 'diff', '--cached', '--name-only', '-z'))
    if (working | staged) - set(rows):
        raise RuntimeError('Unrelated tracked edits or staged files preserved; installation stopped')
    payload = {}
    for name, row in rows.items():
        safe_name(name)
        body = (manifest['_approved_escalation_bytes'] if name == 'state/ESCALATION.md' and '_approved_escalation_bytes' in manifest else read(bundle / 'payload' / name))
        if sha(body) != row['sha256']:
            raise RuntimeError('Package bytes differ: ' + name)
        if name in staged and sha(git(root, 'show', ':' + name)) not in (
                row['sha256'], row.get('old_sha256')):
            raise RuntimeError('Unexpected staged bytes preserved: ' + name)
        p = root / name
        present = os.path.lexists(p)
        if present and sha(read(p)) not in (row['sha256'], row.get('old_sha256')):
            raise RuntimeError('Existing file differs from the declared transition: ' + name)
        if not present and row.get('old_sha256') is not None:
            raise RuntimeError('Expected existing file is absent: ' + name)
        payload[name] = body
    for name, body in payload.items():
        p = root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        plain(p.parent, True)
        if os.path.lexists(p) and read(p) == body:
            continue
        # Only an already verified declared old file is replaced.
        tmp = p.with_name(p.name + '.032-install')
        write_new_or_equal(tmp, body)
        os.replace(tmp, p)
    return rows


def failed_collection(root):
    # A collector refusal must not turn into an unreported Python traceback.
    # Publish only a fixed diagnostic. Never invent a native execution report.
    workflow_path = 'delivery/P3_032_RETURN_WORKFLOW/WORKFLOW_REPORT.json'
    body = encoded({'kind':'P3_032_COLLECTION_FAILURE_v1',
        'status':'COLLECTION_FAILED_LOCAL_EVIDENCE_PRESERVED',
        'execution_receipts_published':False, 'native_or_model_retry_authorized':False,
        'scientific_admission_claimed':False,
        'local_workflow_report':workflow_path,
        'refused_source_contents_read_or_hashed_by_fallback':False})
    digest = sha(body)
    archive = 'evidence/P3_REVIEW_032_RETURN_FAILURES/' + digest
    path = archive + '/INDEX.json'
    write_new_or_equal(root / path, body)
    return {'archive_relative_path':archive, 'evidence_digest':digest,
            'tracked_paths':[path], 'status_summary':{'collection_failed':True}}


def approved_manifest(bundle, manifest):
    """Select the exact standing-authorized variant only in the human command.

    The distributed payload remains unsigned. Both variants are fully hashed;
    the answer is scope-specific and no authority is fabricated in scratch.
    """
    value = json.loads(json.dumps(manifest))
    approval = value['standing_authorization']
    scope = read(bundle / 'payload' / 'configs/P3_FINITE_REVIEW_SCOPE_032.json')
    if sha(scope) != approval['scope_sha256']:
        raise RuntimeError('Standing authorization scope differs')
    unsigned = read(bundle / 'payload' / 'state/ESCALATION.md')
    if sha(unsigned) != approval['unsigned_sha256']:
        raise RuntimeError('Unsigned correction request differs')
    if any(line == '## ANSWER' for line in unsigned.decode('utf-8').splitlines()):
        raise RuntimeError('Unsigned package already contains an answer')
    answer = unsigned.rstrip() + ('\n\n## ANSWER\n\nAPPROVE_P3_FINITE_REVIEW_032_CORRECTION\nscope_sha256: ' +
        approval['scope_sha256'] + '\n').encode()
    if sha(answer) != approval['approved_sha256']:
        raise RuntimeError('Exact standing authorization bytes differ')
    value['files']['state/ESCALATION.md']['sha256'] = sha(answer)
    value['_approved_escalation_bytes'] = answer
    return value


def prepare_setup(root, bundle, manifest):
    selected = approved_manifest(bundle, manifest)
    rows = install(root, bundle, selected)
    return {'kind':'P3_032_PENDING_PUBLICATION_v1', 'phase':'SETUP',
        'parent':git(root, 'rev-parse', 'HEAD').decode().strip(), 'files':rows,
        'return_index':None,
        'commit_message':'Phase 3: publish exact032 correction and standing authorization before execution',
        'reviewer_launch_forbidden_during_publication_retry':True}


def verify_setup(root, bundle, manifest):
    marker = json.loads(read(root / META / 'SETUP_PUBLISHED.json'))
    selected = approved_manifest(bundle, manifest)
    if marker.get('kind') != 'P3_032_SETUP_PUBLISHED_v1' or marker.get('files') != selected['files']:
        raise RuntimeError('Published setup receipt differs from this package')
    git(root, 'merge-base', '--is-ancestor', marker['commit'], 'HEAD')
    verify_declared(root, selected['files'])
    for name, row in selected['files'].items():
        if sha(git(root, 'show', marker['commit'] + ':' + name)) != row['sha256']:
            raise RuntimeError('Published setup commit bytes differ')
    if git(root, 'diff', '--name-only', '-z') or git(root, 'diff', '--cached', '--name-only', '-z'):
        raise RuntimeError('Uncommitted tracked edits preserved before reviewer operation')
    return marker


def execute_workflow(root):
    try:
        workflow_path = root / 'scripts/review032_workflow.py'
        spec = importlib.util.spec_from_file_location('review032_workflow', workflow_path)
        workflow = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(workflow)
        return workflow.run_workflow(root)
    except Exception:
        return {'collection':None, 'status':'WORKFLOW_COLLECTION_COULD_NOT_COMPLETE'}


def prepare_return(root, outcome):
    rows = {}
    collection = outcome.get('collection')
    if not isinstance(collection, dict):
        collection = failed_collection(root)
    for name in collection['tracked_paths']:
        safe_name(name)
        if not name.startswith(('artifacts/P3_REVIEW_032_RETURN/', 'evidence/P3_REVIEW_032_RETURN_FAILURES/')):
            raise RuntimeError('Collector requested an unexpected publication path')
        rows[name] = {'sha256': sha(read(root / name))}
    pointer_body = encoded({'kind':'P3_REVIEW_032_LATEST_RETURN_v1',
        'archive':collection['archive_relative_path'], 'index':collection['archive_relative_path'] + '/INDEX.json',
        'evidence_digest':collection['evidence_digest'], 'workflow_status':outcome['status'],
        'scientific_admission_claimed_by_publisher':False})
    pointer = root / POINTER
    pointer.parent.mkdir(exist_ok=True)
    old_sha = None
    if os.path.lexists(pointer):
        old = read(pointer)
        if old != pointer_body and old != git(root, 'show', 'HEAD:' + POINTER):
            raise RuntimeError('Previous return pointer was edited; preserved')
        old_sha = sha(old)
    tmp = pointer.with_name(pointer.name + '.032-install')
    write_new_or_equal(tmp, pointer_body)
    os.replace(tmp, pointer)
    rows[POINTER] = {'sha256':sha(pointer_body), 'old_sha256':old_sha}
    return {'kind':'P3_032_PENDING_PUBLICATION_v1', 'phase':'RETURN',
        'parent':git(root, 'rev-parse', 'HEAD').decode().strip(), 'files':rows,
        'return_index':collection['archive_relative_path'] + '/INDEX.json',
        'commit_message':'Phase 3: preserve032 actual reviewer receipts and missing-output status',
        'reviewer_launch_forbidden_during_publication_retry':True}


def drive(root, bundle):
    repository_check(root)
    pending_path = root / META / 'PENDING.json'
    if os.path.lexists(pending_path):
        pending = json.loads(read(pending_path))
        result = publish_pending(root, pending)
        if result == 0 and pending['phase'] == 'SETUP':
            print('SETUP RETRY COMPLETE: run the same032 command once more for the remaining conditional operation. This retry did not launch a reviewer.', flush=True)
        return result
    manifest = json.loads(read(bundle / 'PACKAGE_MANIFEST.json'))
    if manifest['base_commit'] != BASE:
        raise RuntimeError('Wrong publication package base')
    setup_path = root / META / 'SETUP_PUBLISHED.json'
    if not os.path.lexists(setup_path):
        pending = prepare_setup(root, bundle, manifest)
        write_new_or_equal(pending_path, encoded(pending))
        result = publish_pending(root, pending)
        if result != 0:
            return result
    verify_setup(root, bundle, manifest)
    outcome = execute_workflow(root)
    pending = prepare_return(root, outcome)
    write_new_or_equal(pending_path, encoded(pending))
    return publish_pending(root, pending)


def main():
    if sys.argv[1:] != ['--run-and-publish']:
        raise SystemExit('Use --run-and-publish for the exact standing-approved032 publication and conditional operation.')
    return drive(Path.home() / 'ARC_Independent_Lab', Path(__file__).resolve().parent)


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print('Publication interrupted. Existing evidence is preserved; repeat the same032 command.', file=sys.stderr)
        raise SystemExit(130)
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, subprocess.SubprocessError) as error:
        print('STOP: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
