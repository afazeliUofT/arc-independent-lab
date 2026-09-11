#!/usr/bin/env python3
"""Install the verified039 outer ZIP under the existing WSL lab and run its finite review workflow.

The Downloads bootstrap supplies ARCHIVE_BYTES only after checking the published
outer SHA-256. This launcher checks the entire member inventory before writing.
It uses no network itself; the versioned workflow runs and publishes the review.
"""
from __future__ import annotations

import hashlib
import io
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import zipfile

REMOTE = 'https://github.com/afazeliUofT/arc-independent-lab'
STEM = 'delivery/P3_CHECKPOINT_039'
MAX_ARCHIVE, MAX_FILE, MAX_TOTAL, MAX_MEMBERS = 64 << 20, 32 << 20, 128 << 20, 512
ROOT_FILES = {'SHA256SUMS', 'RELEASE.json', 'launch039_home.py', 'README_039.md'}
BOOT_SCRIPTS = {'scripts/review039_workflow.py', 'scripts/publish_review039_evidence.py',
                'scripts/stage_source_packet038.py', 'scripts/review032_workflow.py'}



class LaunchStop(RuntimeError):
    pass


def require(value, reason):
    if not value:
        raise LaunchStop(reason)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def signature(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


def ordinary_directory(path, create=False):
    path = Path(path).absolute()
    require('..' not in path.parts, 'Parent-directory path refused')
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        if not os.path.lexists(current) and create:
            current.mkdir(mode=0o700)
        require(stat.S_ISDIR(current.lstat().st_mode), 'Linked or special directory refused')
    return path


def read_regular(path):
    ordinary_directory(path.parent)
    before = path.lstat()
    require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
            before.st_size <= MAX_ARCHIVE, 'Linked, special or oversized file refused')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        opened = os.fstat(fd)
        require(signature(opened) == signature(before), 'File changed while opening')
        with os.fdopen(fd, 'rb', closefd=False) as handle:
            raw = handle.read(MAX_ARCHIVE + 1)
        require(signature(os.fstat(fd)) == signature(opened) == signature(path.lstat()) and
                len(raw) == opened.st_size,
                'File changed while reading')
        return raw
    finally:
        os.close(fd)


def same_or_new(path, raw):
    ordinary_directory(path.parent, create=True)
    if os.path.lexists(path):
        require(read_regular(path) == raw, 'Changed existing file preserved: ' + path.name)
        return
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, 'wb', closefd=False) as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(fd)
    finally:
        os.close(fd)
    require(read_regular(path) == raw, 'Written file verification failed')


def safe_name(name):
    require(type(name) is str and name and len(name) <= 1024 and
            PurePosixPath(name).as_posix() == name and not name.startswith('/') and
            not any(ord(c) < 32 for c in name) and '\\' not in name and ':' not in name and
            all(part not in ('', '.', '..', '.git', '__MACOSX') and not part.startswith('._')
                for part in name.split('/')), 'Unsafe archive path')
    return name


def archive_payloads(raw):
    require(type(raw) is bytes and 0 < len(raw) <= MAX_ARCHIVE, 'Archive size or type refused')
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        entries = archive.infolist()
        names = [safe_name(entry.filename) for entry in entries]
        require(0 < len(names) <= MAX_MEMBERS and len(set(names)) == len(names),
                'Duplicate or excessive archive members')
        require(ROOT_FILES | BOOT_SCRIPTS <= set(names), 'Required package files missing')
        require(all(name in ROOT_FILES or
                    (name.startswith(('public/', 'scripts/', 'packet/')) and PurePosixPath(name).suffix in
                     ('.md', '.json', '.jsonl', '.py', '.txt', '.png', '.pdf')) for name in names),
                'Unexpected package member')
        require(not any(str(parent) in names for name in names
                        for parent in PurePosixPath(name).parents), 'Archive path collision')
        require(sum(entry.file_size for entry in entries) <= MAX_TOTAL,
                'Expanded archive byte limit')
        for entry in entries:
            require(not entry.is_dir() and not entry.flag_bits & 1 and
                    stat.S_IFMT(entry.external_attr >> 16) in (0, stat.S_IFREG) and
                    entry.compress_type in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED) and
                    0 <= entry.file_size <= MAX_FILE, 'Nonregular or oversized ZIP member')
        payloads = {entry.filename: archive.read(entry) for entry in entries}
    lines = payloads['SHA256SUMS'].decode('ascii').splitlines()
    rows = [re.fullmatch(r'([0-9a-f]{64})  (.+)', line) for line in lines]
    require(all(rows), 'Malformed SHA256SUMS')
    checks = {row[2]: row[1] for row in rows}
    require(len(checks) == len(rows) and set(checks) == set(payloads) - {'SHA256SUMS'},
            'SHA256SUMS must cover every other member exactly once')
    require(all(digest(payloads[name]) == expected for name, expected in checks.items()),
            'Package member digest mismatch')
    return payloads


def git(lab, *args, input=None):
    env = os.environ.copy()
    for key in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_COMMON_DIR',
                'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'):
        env.pop(key, None)
    result = subprocess.run(['git', '--no-pager', '-C', str(lab), *args], input=input,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, timeout=60)
    require(result.returncode == 0, 'Repository check failed: git ' + args[0])
    return result.stdout


def repository_check(lab):
    ordinary_directory(lab)
    ordinary_directory(lab / '.git')
    require(git(lab, 'rev-parse', '--show-toplevel').decode().strip() == str(lab),
            'Wrong project root')
    require(git(lab, 'branch', '--show-current').decode().strip() == 'main',
            'Existing main branch required')
    for flags in (('--all',), ('--push', '--all')):
        values = git(lab, 'remote', 'get-url', *flags, 'origin').decode().splitlines()
        require(len(values) == 1 and values[0].rstrip('/').removesuffix('.git') == REMOTE,
                'Origin differs from the authorized repository')
    # The pinned workflow checks tracked/index contents before repository writes.
    # It permits only its exact return artifacts, including a staged commit retry.


def private_destination_check(lab, relative, files):
    require(not git(lab, 'ls-files', '-z', '--', relative), 'Delivery destination is tracked')
    expected = {(PurePosixPath(relative) / name).as_posix() for name in files}
    raw = b''.join(name.encode() + b'\0' for name in sorted(expected))
    ignored = git(lab, 'check-ignore', '--no-index', '-z', '--stdin', input=raw)
    require(set(ignored.decode().split('\0')) - {''} == expected,
            'Delivery destination is not completely ignored')


def verify_existing(destination, files):
    if not os.path.lexists(destination):
        return
    ordinary_directory(destination)
    directories = {str(parent) for name in files for parent in PurePosixPath(name).parents
                   if str(parent) != '.'}
    for parent, dirs, names in os.walk(destination, followlinks=False):
        for name in dirs:
            path = Path(parent) / name
            require(path.relative_to(destination).as_posix() in directories,
                    'Unexpected existing directory preserved')
            ordinary_directory(path)
        for name in names:
            path = Path(parent) / name
            relative = path.relative_to(destination).as_posix()
            require(relative in files and read_regular(path) == files[relative],
                    'Unexpected or changed existing file preserved')


def launch(raw, archive_path='', *, home=None, runner=None):
    payloads = archive_payloads(raw)
    lab = (Path.home() if home is None else Path(home)) / 'ARC_Independent_Lab'
    repository_check(lab)
    relative = STEM + '/' + digest(raw)
    destination = lab / relative
    files = {'PACKAGE.zip': raw, **{'bundle/' + name: body for name, body in payloads.items()}}
    private_destination_check(lab, relative, files)
    verify_existing(destination, files)
    for name, body in sorted(files.items()):
        same_or_new(destination / name, body)
    verify_existing(destination, files)
    private_destination_check(lab, relative, files)
    bundle = destination / 'bundle'
    print('Verified package copied and extracted to: ' + str(bundle), flush=True)
    print('Running finite focused review or collecting its existing attempt; returning results to GitHub.', flush=True)
    execute = subprocess.run if runner is None else runner
    result = execute([sys.executable, '-B', '-u', str(bundle / 'scripts/review039_workflow.py'),
                      '--lab', str(lab), '--bundle', str(bundle)], cwd=lab)
    require(result.returncode == 0, 'Review workflow stopped; rerun only collects an existing reserved attempt and retries publication')
    return bundle


if __name__ == '__main__':
    try:
        require('ARCHIVE_BYTES' in globals(), 'Run the provided WSL-home Downloads command')
        launch(ARCHIVE_BYTES, globals().get('ARCHIVE_PATH', ''))
    except (LaunchStop, OSError, ValueError, UnicodeError, zipfile.BadZipFile,
            subprocess.SubprocessError) as error:
        print('STOP: ' + str(error) + '. Existing files are preserved.', file=sys.stderr)
        raise SystemExit(1)
