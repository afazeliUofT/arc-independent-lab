#!/usr/bin/env python3
"""Verify and install the complete047 Git bundle; run offline return assessment only."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import zipfile

sys.dont_write_bytecode = True
REPOSITORY = 'afazeliUofT/arc-independent-lab'
REMOTE = 'https://github.com/' + REPOSITORY + '.git'
ZIP_NAME = 'ARC_Independent_Lab_047_HOME.zip'
ASSESSMENT = 'evidence/P3_CHECKPOINT_046_RETURN_VERIFICATION_047.json'
MEMBERS = {'SHA256SUMS', 'package_release.json', 'repo.bundle',
           'launch047_home.py', 'checkpoint047_workflow.py', 'README_047.md'}
MAX_FILE = 128 * 1024 * 1024
MAX_TOTAL = 160 * 1024 * 1024


class Stop(RuntimeError):
    pass


def require(ok, reason):
    if not ok:
        raise Stop(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True,
                       allow_nan=False) + '\n').encode('ascii')


def parse(raw):
    def unique(pairs):
        value = {}
        for key, item in pairs:
            require(key not in value, 'duplicate_json_key')
            value[key] = item
        return value
    return json.loads(raw, object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(Stop('nonfinite_json')))


def directory(path, create=False):
    path = Path(path).absolute()
    require('..' not in path.parts, 'parent_path_refused')
    cursor = Path(path.anchor)
    for part in path.parts[1:]:
        cursor /= part
        if not os.path.lexists(cursor) and create:
            try:
                cursor.mkdir(mode=0o700)
            except FileExistsError:
                pass
        require(stat.S_ISDIR(cursor.lstat().st_mode), 'linked_or_special_directory_refused')
    return path


def read_regular(path, limit=MAX_FILE):
    path = Path(path)
    directory(path.parent)
    before = path.lstat()
    require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
            before.st_size <= limit, 'linked_special_or_oversized_file_refused')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        opened = os.fstat(fd)
        require(before == opened, 'file_changed_while_opening')
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            raw = stream.read(limit + 1)
        after = os.fstat(fd)
        # atime may legitimately change on a read; content identity may not.
        fields = ('st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_size', 'st_mtime_ns', 'st_ctime_ns')
        require(all(getattr(opened, key) == getattr(after, key) == getattr(path.lstat(), key)
                    for key in fields) and len(raw) == opened.st_size,
                'file_changed_while_reading')
        return raw
    finally:
        os.close(fd)


def same_or_new(path, raw):
    path = Path(path)
    directory(path.parent, create=True)
    if os.path.lexists(path):
        require(read_regular(path) == raw, 'changed_existing_file_preserved:' + path.name)
        return
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, 'wb', closefd=False) as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(fd)
    finally:
        os.close(fd)
    require(read_regular(path) == raw, 'written_file_verification_failed')


def git(root, *args, allowed=(0,), input=None):
    env = os.environ.copy()
    for name in list(env):
        if name.startswith('GIT_') and name not in ('GIT_ASKPASS', 'GIT_TERMINAL_PROMPT',
                                                   'GIT_SSH', 'GIT_SSH_COMMAND'):
            env.pop(name)
    result = subprocess.run(['git', '--no-pager', '-c', 'core.hooksPath=/dev/null',
                             '-c', 'core.fsmonitor=false', '-C', str(root), *args],
                            input=input, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            env=env, timeout=120)
    require(result.returncode in allowed, 'git_' + args[0] + '_failed:' +
            result.stderr.decode('utf-8', errors='replace')[-1600:].strip())
    return result.stdout


def repository_check(lab):
    directory(lab)
    directory(lab / '.git')
    require(git(lab, 'rev-parse', '--show-toplevel').decode().strip() == str(lab),
            'wrong_project_root')
    require(git(lab, 'branch', '--show-current').decode().strip() == 'main', 'main_branch_required')
    for flags in (('--all',), ('--push', '--all')):
        values = git(lab, 'remote', 'get-url', *flags, 'origin').decode().splitlines()
        accepted = {REMOTE.rstrip('/').removesuffix('.git'),
                    'git@github.com:' + REPOSITORY,
                    'ssh://git@github.com/' + REPOSITORY}
        require(len(values) == 1 and values[0].rstrip('/').removesuffix('.git') in accepted,
                'wrong_authorized_origin')


def archive_payloads(raw, expected_sha):
    require(type(expected_sha) is str and re.fullmatch('[0-9a-f]{64}', expected_sha),
            'published_outer_sha256_required')
    require(type(raw) is bytes and 0 < len(raw) <= MAX_FILE and sha(raw) == expected_sha,
            'outer_archive_sha256_mismatch')
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        entries = archive.infolist()
        require(len(entries) == len(MEMBERS) and {item.filename for item in entries} == MEMBERS,
                'archive_inventory_differs')
        require(sum(item.file_size for item in entries) <= MAX_TOTAL, 'expanded_archive_too_large')
        for item in entries:
            require(not item.is_dir() and not item.flag_bits & 1 and
                    stat.S_IFMT(item.external_attr >> 16) in (0, stat.S_IFREG) and
                    item.compress_type in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED) and
                    0 <= item.file_size <= MAX_FILE, 'unsafe_archive_member')
        payloads = {item.filename: archive.read(item) for item in entries}
    rows = [re.fullmatch(r'([0-9a-f]{64})  (.+)', line)
            for line in payloads['SHA256SUMS'].decode('ascii').splitlines()]
    require(all(rows), 'malformed_sha256sums')
    checks = {row[2]: row[1] for row in rows}
    require(len(checks) == len(rows) and set(checks) == MEMBERS - {'SHA256SUMS'},
            'sha256sums_inventory_differs')
    require(all(sha(payloads[name]) == value for name, value in checks.items()),
            'package_member_sha256_mismatch')
    release = parse(payloads['package_release.json'])
    require(type(release) is dict and set(release) == {'kind', 'repository', 'release_commit',
            'bundle_sha256', 'assessment_path', 'assessment_sha256'} and
            release['kind'] == 'P3_CHECKPOINT_047_RELEASE_v1' and
            release['repository'] == REPOSITORY and release['assessment_path'] == ASSESSMENT,
            'wrong047_release_metadata')
    require(type(release['release_commit']) is str and
            re.fullmatch('[0-9a-f]{40}', release['release_commit']) and
            type(release['assessment_sha256']) is str and
            re.fullmatch('[0-9a-f]{64}', release['assessment_sha256']) and
            release['bundle_sha256'] == sha(payloads['repo.bundle']), 'invalid_release_pin')
    return payloads, release


def downloads_archive():
    ps = shutil.which('powershell.exe') or '/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe'
    query = r"""$ErrorActionPreference='Stop'; [Console]::OutputEncoding=[System.Text.Encoding]::UTF8; $k='HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders'; $p=(Get-ItemProperty -LiteralPath $k).'{374DE290-123F-4565-9164-39C4925E467B}'; if([string]::IsNullOrWhiteSpace($p)){throw 'Downloads path unavailable'}; [Environment]::ExpandEnvironmentVariables($p)"""
    windows = subprocess.run([ps, '-NoProfile', '-NonInteractive', '-Command', query],
                             capture_output=True, check=True, timeout=20).stdout.decode('utf-8-sig').strip()
    require(windows and '\n' not in windows, 'windows_downloads_resolution_failed')
    linux = subprocess.run(['wslpath', '-u', windows], capture_output=True,
                           check=True, timeout=10).stdout.decode('utf-8').strip()
    require(linux and '\n' not in linux and Path(linux).is_absolute(), 'wsl_downloads_resolution_failed')
    return Path(linux) / ZIP_NAME


def launch(raw, expected_sha, *, home=None, runner=None):
    payloads, release = archive_payloads(raw, expected_sha)
    lab = (Path.home() if home is None else Path(home)).absolute() / 'ARC_Independent_Lab'
    repository_check(lab)
    relative = 'delivery/P3_CHECKPOINT_047/' + expected_sha
    require(not git(lab, 'ls-files', '-z', '--', relative), 'delivery_is_tracked')
    require(git(lab, 'check-ignore', '--no-index', relative + '/package/repo.bundle',
                allowed=(0, 1)).strip(), 'delivery_must_be_ignored')
    destination = lab / relative
    package = destination / 'package'
    if os.path.lexists(package):
        directory(package)
        require({item.name for item in package.iterdir()} <= MEMBERS,
                'unexpected_existing_package_file_preserved')
    # Check every existing file before writing any new file.
    for name, body in payloads.items():
        path = package / name
        if os.path.lexists(path):
            require(read_regular(path) == body, 'changed_existing_package_preserved')
    same_or_new(destination / 'PACKAGE.zip', raw)
    for name, body in sorted(payloads.items()):
        same_or_new(package / name, body)
    print('Verified047 package. Checking the returned046 evidence offline; no profile, model, reviewer or target experiment is started.', flush=True)
    execute = subprocess.run if runner is None else runner
    result = execute([sys.executable, '-I', '-S', '-B', '-u', str(package / 'checkpoint047_workflow.py'),
                      '--lab', str(lab), '--package', str(package), '--archive-sha256', expected_sha],
                     cwd=lab)
    require(result.returncode == 0,
            '047_assessment_or_publication_stopped; repeat the same command to reuse saved assessment and retry publication')
    return destination


def main():
    if 'ARCHIVE_BYTES' in globals():
        launch(globals()['ARCHIVE_BYTES'], globals().get('EXPECTED_ARCHIVE_SHA256'))
    else:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument('--archive-sha256', required=True)
        parser.add_argument('--archive', type=Path)
        args = parser.parse_args()
        archive = args.archive if args.archive is not None else downloads_archive()
        require(archive.name == ZIP_NAME, 'exact047_archive_filename_required')
        launch(read_regular(archive), args.archive_sha256)
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (Stop, OSError, ValueError, UnicodeError, zipfile.BadZipFile, subprocess.SubprocessError) as error:
        print('STOP: ' + str(error) + '. Existing files are preserved.', file=sys.stderr)
        raise SystemExit(1)
