#!/usr/bin/env python3
"""Install one exact private reviewer packet locally. No Git, client, network or model.

The CLI has fixed source/destination paths under ~/ARC_Independent_Lab. Its two
functions accept a project root for the controller and contained synthetic tests;
callers must enforce their own canonical project root before invoking native work.
Existing complete bytes are reused. Any partial or unexpected tree is preserved.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import zipfile

PACKET_NAME = 'P3_REVIEW_PACKET_019'
ARCHIVE_NAME = 'P3_REVIEW_PACKET_019_PRIVATE.zip'
MANIFEST_SHA256 = '437700c8850b7194b052d159b1eaf6a22b366c4a464e63148bb9b6b3084bdd98'
ARCHIVE_SHA256 = '5b7afe3b742e14dffacfe0640e5b1d9210b449bbb9c5fd7a08b5083484859759'
ARCHIVE_BYTES = 233079345
MANIFEST_FILE = 'BROKER_MANIFEST.json'
MANIFEST_ENTRIES = 722
MAX_FILE_BYTES = 128 * 1024 * 1024
MAX_TOTAL_BYTES = 300 * 1024 * 1024

class Stop(RuntimeError):
    pass

def require(value, reason):
    if not value:
        raise Stop(reason)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def safe_path(value):
    require(type(value) is str and 0 < len(value) <= 1024, 'Invalid member path type/length')
    p = PurePosixPath(value)
    require(not p.is_absolute() and p.as_posix() == value and '\\' not in value and
            '\x00' not in value and all(x not in ('', '.', '..') for x in value.split('/')),
            'Unsafe member path')
    return p.parts

def directory(path):
    path = Path(path)
    require(path.is_absolute() and '..' not in path.parts, 'Project path must be absolute/canonical')
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current = current / part
        info = current.lstat()
        require(stat.S_ISDIR(info.st_mode), 'Directory missing, linked, or non-directory')
    return path

def identity(info):
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns, info.st_mode, info.st_nlink)

def read_regular(path, limit):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        before = os.fstat(fd)
        require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size <= limit,
                'Expected bounded regular file without links')
        chunks = []
        remaining = limit + 1
        while remaining:
            b = os.read(fd, min(1024 * 1024, remaining))
            if not b:
                break
            chunks.append(b)
            remaining -= len(b)
        data = b''.join(chunks)
        require(len(data) == before.st_size and len(data) <= limit and identity(before) == identity(os.fstat(fd)),
                'File changed during read or exceeded limit')
        return data
    finally:
        os.close(fd)

def _pairs(items):
    result = {}
    for key, value in items:
        require(key not in result, 'Duplicate JSON key')
        result[key] = value
    return result

def manifest_entries(raw):
    require(digest(raw) == MANIFEST_SHA256, 'Packet manifest hash mismatch')
    try:
        m = json.loads(raw, object_pairs_hook=_pairs)
    except (ValueError, UnicodeError) as error:
        raise Stop('Invalid packet manifest JSON') from error
    require(type(m) is dict and set(m) == {'schema_version', 'files'} and
            type(m['schema_version']) is int and m['schema_version'] == 1,
            'Invalid packet manifest schema')
    require(type(m['files']) is list and len(m['files']) == MANIFEST_ENTRIES,
            'Unexpected packet inventory length')
    entries = {}
    for e in m['files']:
        require(type(e) is dict and set(e) == {'path', 'sha256', 'kind'}, 'Invalid packet inventory entry')
        safe_path(e['path'])
        require(e['path'] not in entries and e['path'] != MANIFEST_FILE, 'Duplicate/self manifest member')
        require(type(e['sha256']) is str and re.fullmatch('[0-9a-f]{64}', e['sha256']) and
                e['kind'] in ('text', 'binary', 'image'), 'Invalid member hash or kind')
        entries[e['path']] = e['sha256']
    entries[MANIFEST_FILE] = MANIFEST_SHA256
    return entries

def _expected_directories(entries):
    return {str(p) for name in entries for p in PurePosixPath(name).parents if str(p) != '.'}

def verify_packet(root: Path) -> dict:
    """Read-only complete exact-tree and byte verification; no archive required."""
    root = directory(root)
    delivery = directory(root / 'delivery')
    packet = directory(delivery / PACKET_NAME)
    entries = manifest_entries(read_regular(packet / MANIFEST_FILE, 1024 * 1024))
    actual_files, actual_directories = set(), set()
    total = 0
    for parent, dirs, files in os.walk(packet, followlinks=False):
        parent = Path(parent)
        for name in dirs:
            path = parent / name
            require(stat.S_ISDIR(path.lstat().st_mode), 'Linked/non-directory packet entry')
            actual_directories.add(path.relative_to(packet).as_posix())
        for name in files:
            path = parent / name
            relative = path.relative_to(packet).as_posix()
            require(relative in entries, 'Unlisted packet file; preserved')
            raw = read_regular(path, MAX_FILE_BYTES)
            require(digest(raw) == entries[relative], 'Packet byte mismatch; preserved')
            actual_files.add(relative)
            total += len(raw)
            require(total <= MAX_TOTAL_BYTES, 'Packet total byte limit')
    require(actual_files == set(entries) and actual_directories == _expected_directories(entries),
            'Partial packet or unexpected directory; preserved')
    return {'packet_path': str(packet), 'manifest_sha256': MANIFEST_SHA256,
            'files_verified': len(entries), 'bytes_verified': total,
            'status': 'VERIFIED_EXACT_PRIVATE_PACKET', 'model_called': False,
            'git_changed': False, 'public_redistribution_authorized': False}

def _checked_archive(root, archive):
    delivery = directory(Path(root) / 'delivery')
    expected = delivery / ARCHIVE_NAME
    require(Path(archive) == expected, 'Only the fixed project archive is accepted')
    raw = read_regular(expected, ARCHIVE_BYTES)
    require(len(raw) == ARCHIVE_BYTES and digest(raw) == ARCHIVE_SHA256, 'Private archive byte/hash mismatch')
    z = zipfile.ZipFile(io.BytesIO(raw))
    try:
        infos = z.infolist()
        require(len(infos) == MANIFEST_ENTRIES + 1, 'Archive file count mismatch')
        names = set()
        total = 0
        for info in infos:
            safe_path(info.filename)
            require(info.filename not in names, 'Duplicate archive member')
            names.add(info.filename)
            mode = info.external_attr >> 16
            require(info.create_system == 3 and stat.S_ISREG(mode) and not info.is_dir() and
                    not info.flag_bits & 1 and info.compress_type in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED),
                    'Linked, encrypted, directory, or unsupported archive member')
            require(0 <= info.file_size <= MAX_FILE_BYTES, 'Archive member size bound')
            total += info.file_size
            require(total <= MAX_TOTAL_BYTES, 'Archive expanded byte limit')
        require(MANIFEST_FILE in names, 'Missing archive manifest')
        require(z.getinfo(MANIFEST_FILE).file_size <= 1024 * 1024, 'Archive manifest size bound')
        entries = manifest_entries(z.read(MANIFEST_FILE))
        require(names == set(entries), 'Unlisted or missing archive members')
        # Validate every actual decompressed byte BEFORE making a destination.
        for name, expected_sha in entries.items():
            require(digest(z.read(name)) == expected_sha, 'Archive member hash mismatch')
        return z, entries
    except BaseException:
        z.close()
        raise

def inspect_packet(root: Path) -> dict:
    root = directory(root)
    delivery = directory(root / 'delivery')
    destination = delivery / PACKET_NAME
    if destination.exists() or destination.is_symlink():
        result = verify_packet(root)
        result['action'] = 'REUSE_COMPLETE_PACKET'
        return result
    z, entries = _checked_archive(root, delivery / ARCHIVE_NAME)
    z.close()
    return {'status': 'VERIFIED_ARCHIVE_NOT_INSTALLED', 'action': 'INSTALL_ONLY_WITH_EXPLICIT_FLAG',
            'packet_path': str(destination), 'archive_sha256': ARCHIVE_SHA256,
            'manifest_sha256': MANIFEST_SHA256, 'files_verified': len(entries),
            'writes_performed': False, 'model_called': False, 'git_changed': False}

def _write_relative(root_fd, relative, raw):
    parts = safe_path(relative)
    current = os.dup(root_fd)
    try:
        for part in parts[:-1]:
            try:
                os.mkdir(part, mode=0o700, dir_fd=current)
            except FileExistsError:
                pass
            next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=current)
            os.close(current)
            current = next_fd
        fd = os.open(parts[-1], os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                     0o600, dir_fd=current)
        try:
            with os.fdopen(fd, 'wb', closefd=False) as f:
                f.write(raw)
                f.flush()
                os.fsync(f.fileno())
        finally:
            os.close(fd)
    finally:
        os.close(current)

def install_packet(root: Path, archive: Path) -> dict:
    """Install only the fixed packet under root/delivery; preserve/reuse existing."""
    root = directory(root)
    delivery = directory(root / 'delivery')
    require(Path(archive) == delivery / ARCHIVE_NAME, 'Only the fixed project archive is accepted')
    destination = delivery / PACKET_NAME
    if destination.exists() or destination.is_symlink():
        result = verify_packet(root)
        result.update({'action': 'REUSED_COMPLETE_PACKET', 'writes_performed': False})
        return result
    z, entries = _checked_archive(root, archive)
    delivery_fd = os.open(delivery, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    packet_fd = None
    try:
        os.mkdir(PACKET_NAME, mode=0o700, dir_fd=delivery_fd)
        packet_fd = os.open(PACKET_NAME, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                            dir_fd=delivery_fd)
        for name in sorted(entries):
            _write_relative(packet_fd, name, z.read(name))
        os.fsync(packet_fd)
        os.fsync(delivery_fd)
    finally:
        z.close()
        if packet_fd is not None:
            os.close(packet_fd)
        os.close(delivery_fd)
    result = verify_packet(root)
    result.update({'action': 'INSTALLED_EXACT_PRIVATE_PACKET', 'archive_sha256': ARCHIVE_SHA256,
                   'writes_performed': True})
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install', action='store_true', help='Install the fixed verified archive; completed exact packet is reused')
    args = parser.parse_args()
    root = Path(__file__).absolute().parents[1]
    require(root == Path.home() / 'ARC_Independent_Lab', 'CLI must run from ~/ARC_Independent_Lab/scripts')
    result = install_packet(root, root / 'delivery' / ARCHIVE_NAME) if args.install else inspect_packet(root)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    try:
        main()
    except (Stop, OSError, ValueError, zipfile.BadZipFile) as error:
        raise SystemExit('STOP: ' + str(error) + '. Existing/partial files are preserved.')
