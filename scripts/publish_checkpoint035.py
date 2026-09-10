#!/usr/bin/env python3
"""Human-run publication only of declared checkpoint035 documents and evidence.

Only explicitly declared documents and evidence are installed and published.
No reviewer, workflow, probe or model is imported or started by this program.
All commits and pushes occur only when the human runs this file.
"""
from pathlib import Path, PurePosixPath
import hashlib
import json
import os
import stat
import subprocess
import sys

BASE = '53768f9fc6b867834e1ab03b86248b487a19b617'
REMOTE = 'https://github.com/afazeliUofT/arc-independent-lab.git'
META = 'delivery/P2_035_PUBLICATION'
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


def read(path, limit=None):
    limit = MAX_FILE if limit is None else min(limit, MAX_FILE)
    before = plain(path)
    if before.st_size > limit:
        raise RuntimeError('Publication input exceeds its read bound')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        opened = os.fstat(fd)
        if (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino):
            raise RuntimeError('Publication input changed while opening')
        body = bytearray()
        while len(body) <= limit:
            part = os.read(fd, min(65536, limit + 1 - len(body)))
            if not part:
                break
            body.extend(part)
        after = os.fstat(fd)
        if len(body) > limit or (opened.st_size, opened.st_mtime_ns, opened.st_ctime_ns) != (
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


def verify_exact_child(root, pending):
    current = git(root, 'rev-parse', 'HEAD').decode().strip()
    if current != pending['parent']:
        if git(root, 'show', '-s', '--format=%P', 'HEAD').decode().split() != [pending['parent']]:
            raise RuntimeError('HEAD is not the prepared parent or exact child; preserved')
    changed = names(git(root, 'diff', '--name-only', '-z', pending['parent'], 'HEAD'))
    if changed - set(pending['files']):
        raise RuntimeError('Commit includes unrelated changes; preserved')
    if current != pending['parent']:
        for name, row in pending['files'].items():
            if sha(git(root, 'show', 'HEAD:' + name)) != row['sha256']:
                raise RuntimeError('Committed publication bytes differ: ' + name)
    return current


def publish_pending(root, pending):
    rows = pending['files']
    verify_declared(root, rows)
    current = verify_exact_child(root, pending)
    stage_exact(root, rows)
    if git(root, 'diff', '--cached', '--name-only').strip():
        if current != pending['parent']:
            raise RuntimeError('Unexpected staged changes after exact child verification')
        subprocess.run(['git', '-C', str(root), 'commit', '-m',
                        pending['commit_message']], env=git_env(), check=True)
    current = verify_exact_child(root, pending)
    if current == pending['parent']:
        raise RuntimeError('Checkpoint has no prepared child; push stopped')
    verify_declared(root, rows)
    print('PUSHING VERIFIED CHECKPOINT: ' + current, flush=True)
    result = subprocess.run(['git', '-C', str(root), 'push', '--progress', 'origin',
                             current + ':refs/heads/main'], env=git_env())
    if result.returncode:
        print('PUSH FAILED: local commit and pending publication preserved. Repeat the same 035 command; it retries publication only.', flush=True)
        return result.returncode
    receipt = {'kind':'P2_035_PUBLISHED_v1', 'commit':current,
               'package_manifest_sha256':pending['package_manifest_sha256'],
               'files':rows, 'execution_started':False}
    write_new_or_equal(root / META / 'PUBLISHED.json', encoded(receipt))
    (root / META / 'PENDING.json').unlink()
    print('PUBLISHED: https://github.com/afazeliUofT/arc-independent-lab/commit/' + current, flush=True)
    print('PUBLICATION COMPLETE. No reviewer or model was started. Tell the PI that GitHub is updated; no attachments are needed.', flush=True)
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
        body = read(bundle / 'payload' / name)
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
        tmp = p.with_name(p.name + '.035-install')
        write_new_or_equal(tmp, body)
        os.replace(tmp, p)
    return rows


def package(root, bundle):
    raw = read(bundle / 'PACKAGE_MANIFEST.json')
    manifest = json.loads(raw)
    if (manifest.get('kind') != 'P2_CHECKPOINT_035_PACKAGE_v1'
            or manifest.get('base_commit') != BASE
            or manifest.get('publication_only') is not True
            or manifest.get('execution_started') is not False
            or not isinstance(manifest.get('files'), dict) or not manifest['files']):
        raise RuntimeError('Wrong publication package')
    for name, row in manifest['files'].items():
        safe_name(name)
        if not isinstance(row, dict) or set(row) != {'sha256', 'old_sha256'}:
            raise RuntimeError('Wrong publication row')
        for value in (row['sha256'], row['old_sha256']):
            if value is not None and (type(value) is not str or len(value) != 64
                    or any(c not in '0123456789abcdef' for c in value)):
                raise RuntimeError('Invalid publication digest')
        if row['sha256'] is None or sha(read(bundle / 'payload' / name)) != row['sha256']:
            raise RuntimeError('Package bytes differ: ' + name)
    return manifest, sha(raw)



def drive(root, bundle):
    repository_check(root)
    manifest, manifest_sha = package(root, bundle)
    rows = manifest['files']
    pending_path = root / META / 'PENDING.json'
    done_path = root / META / 'PUBLISHED.json'
    if os.path.lexists(pending_path):
        pending = json.loads(read(pending_path))
        expected_rows = rows
        if (pending.get('kind') != 'P2_035_PENDING_PUBLICATION_v1'
                or pending.get('parent') != BASE or pending.get('files') != expected_rows
                or pending.get('package_manifest_sha256') != manifest_sha
                or pending.get('commit_message') != COMMIT_MESSAGE
                or pending.get('execution_started') is not False):
            raise RuntimeError('Pending publication differs from this package; preserved')
        return publish_pending(root, pending)
    if os.path.lexists(done_path):
        done = json.loads(read(done_path))
        expected_rows = rows
        if (done.get('kind') != 'P2_035_PUBLISHED_v1' or done.get('files') != expected_rows
                or done.get('package_manifest_sha256') != manifest_sha
                or done.get('execution_started') is not False
                or done.get('commit') != git(root, 'rev-parse', 'HEAD').decode().strip()):
            raise RuntimeError('Completed publication receipt differs; preserved')
        verify_declared(root, expected_rows)
        if git(root, 'diff', '--name-only', '-z') or git(root, 'diff', '--cached', '--name-only', '-z'):
            raise RuntimeError('Uncommitted tracked edits preserved after publication')
        verify_exact_child(root, {'parent':BASE, 'files':expected_rows})
        print('ALREADY PUBLISHED: no commit, push, reviewer or model was repeated.', flush=True)
        return 0
    if git(root, 'rev-parse', 'HEAD').decode().strip() != BASE:
        raise RuntimeError('Fresh publication requires the exact pinned base; current work is preserved')
    # Old-byte transitions are tied to the pinned Git base, not merely local files.
    base_names = names(git(root, 'ls-tree', '-r', '--name-only', '-z', BASE))
    for name, row in rows.items():
        old_sha = sha(git(root, 'show', BASE + ':' + name)) if name in base_names else None
        if old_sha != row['old_sha256']:
            raise RuntimeError('Declared old version differs from pinned base: ' + name)
    install(root, bundle, manifest)
    pending = {'kind':'P2_035_PENDING_PUBLICATION_v1', 'parent':BASE,
        'package_manifest_sha256':manifest_sha, 'files':rows,
        'commit_message':COMMIT_MESSAGE, 'execution_started':False}
    write_new_or_equal(pending_path, encoded(pending))
    return publish_pending(root, pending)


COMMIT_MESSAGE = 'Phase 2: specify second-pass candidates and record checkpoint034 verification'


def main():
    if sys.argv[1:] != ['--publish']:
        raise SystemExit('Use --publish for checkpoint035 document publication only.')
    return drive(Path.home() / 'ARC_Independent_Lab', Path(__file__).resolve().parent)


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print('Publication interrupted. Existing files are preserved; repeat the same 035 command.', file=sys.stderr)
        raise SystemExit(130)
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, subprocess.SubprocessError) as error:
        print('STOP: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
