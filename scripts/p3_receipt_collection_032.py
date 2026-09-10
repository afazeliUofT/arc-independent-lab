#!/usr/bin/env python3
"""Read fixed original receipts and preserve failures without launching or writing.

The caller supplies the exact emitter source hash and expected schema kind.
This module never repairs a historical SESSION or manufactures a main REPORT.
Its integrity flag is only eligibility for later controller admission checks.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import stat


SESSION_KIND = 'P3_FINITE_REVIEWER_SESSION_032_v1'
RECEIPT_LIMIT_BYTES = 16 * 1024 * 1024
SOURCE_LIMIT_BYTES = 2 * 1024 * 1024
MODES = ('synthetic', 'science')


class ReceiptFailure(Exception):
    """Fixed public error code; never a raw exception or file excerpt."""


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value, indent=2, ensure_ascii=True, allow_nan=False) + '\n').encode()


def _signature(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_nlink,
            info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def _read(path, maximum):
    """Descriptor-relative traversal, with no symlinks or special-file opens."""
    path = Path(path).absolute()
    directory = None
    fd = None
    try:
        directory = os.open(path.anchor, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        for part in path.parts[1:-1]:
            next_directory = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                     dir_fd=directory)
            os.close(directory)
            directory = next_directory
        before_path = os.stat(path.name, dir_fd=directory, follow_symlinks=False)
        if not stat.S_ISREG(before_path.st_mode):
            raise ReceiptFailure('not_regular_file')
        if before_path.st_nlink != 1:
            raise ReceiptFailure('multiple_hardlinks_refused')
        if before_path.st_mode & 0o022:
            raise ReceiptFailure('group_or_world_writable_file')
        if before_path.st_size > maximum:
            raise ReceiptFailure('file_byte_limit_exceeded')
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
        before = os.fstat(fd)
        if _signature(before) != _signature(before_path):
            raise ReceiptFailure('file_changed_during_open')
        chunks = []
        total = 0
        while True:
            chunk = os.read(fd, min(65536, maximum + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > maximum:
                raise ReceiptFailure('file_byte_limit_exceeded')
        after = os.fstat(fd)
        after_path = os.stat(path.name, dir_fd=directory, follow_symlinks=False)
        if (_signature(before) != _signature(after) or _signature(before) != _signature(after_path)
                or total != before.st_size):
            raise ReceiptFailure('file_changed_during_read')
        return b''.join(chunks)
    except ReceiptFailure:
        raise
    except FileNotFoundError:
        raise ReceiptFailure('missing_file') from None
    except OSError:
        raise ReceiptFailure('protected_path_read_failed') from None
    finally:
        if fd is not None:
            os.close(fd)
        if directory is not None:
            os.close(directory)


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ReceiptFailure('duplicate_json_key')
        result[key] = value
    return result


def _parse(raw):
    try:
        value = json.loads(raw, object_pairs_hook=_object,
                           parse_constant=lambda value: (_ for _ in ()).throw(ReceiptFailure('nonfinite_json')))
    except ReceiptFailure:
        raise
    except (ValueError, UnicodeError, RecursionError):
        raise ReceiptFailure('invalid_json') from None
    if type(value) is not dict:
        raise ReceiptFailure('json_object_required')
    return value


def collect(run, *, emitter_path, emitter_sha256, expected_kind, expected_modes=MODES):
    """Collect independent original receipts, including partial failed runs.

    ``emitter_path`` must name a versioned session source under ``scripts``.
    Its exact hash and schema kind come from the caller's frozen source binding;
    accepting a historical kind is never inferred from an untrusted receipt.
    No kind is rewritten. Errors contain only categorical codes and original
    file references. Valid observations retain exactly the supplied JSON data.
    """
    result = {'kind': 'P3_SOURCE_BOUND_RECEIPT_COLLECTION_032_v1',
              'observations': {}, 'stages': {}, 'files': [], 'errors': [],
              'expected_modes': list(expected_modes) if type(expected_modes) in (tuple, list) else [],
              'source_binding_verified': False, 'complete': False,
              'eligible_for_controller_admission_checks': False,
              'execution_admission_evaluated': False,
              'original_receipts_changed': False, 'missing_receipts_reconstructed': False,
              'native_clients_started': 0, 'model_turns_sent': 0}
    def error(phase, code, file=None):
        result['errors'].append({'phase': phase, 'code': code, 'file': file})
    if expected_modes not in ((), ('synthetic',), MODES, [], ['synthetic'], list(MODES)):
        error('input', 'expected_mode_order_invalid')
        return result
    modes = tuple(expected_modes)
    if (type(expected_kind) is not str or not re.fullmatch(r'P3_FINITE_REVIEWER_SESSION_[A-Z0-9_]+_v1', expected_kind)
            or type(emitter_sha256) is not str or not re.fullmatch(r'[0-9a-f]{64}', emitter_sha256)):
        error('source_binding', 'binding_shape_invalid')
    else:
        try:
            source = Path(emitter_path)
            if source.parent.name != 'scripts' or not re.fullmatch(r'p3_reviewer_session_[0-9]{3}\.py', source.name):
                raise ReceiptFailure('emitter_source_name_refused')
            raw = _read(source, SOURCE_LIMIT_BYTES)
            result['emitter_source'] = {'path': 'scripts/' + source.name, 'sha256': sha(raw),
                                        'bytes': len(raw), 'expected_kind': expected_kind}
            if sha(raw) != emitter_sha256:
                raise ReceiptFailure('emitter_source_hash_differs')
            result['source_binding_verified'] = True
        except ReceiptFailure as exc:
            error('source_binding', str(exc))
        except (TypeError, ValueError):
            error('source_binding', 'emitter_source_path_invalid')
    saved = {}
    for mode in MODES:
        for suffix in ('SESSION', 'STAGE'):
            filename = mode + '_' + suffix + '.json'
            record = {'path': filename, 'status': 'UNREAD', 'sha256': None, 'bytes': None}
            result['files'].append(record)
            try:
                raw = _read(Path(run) / filename, RECEIPT_LIMIT_BYTES)
                record.update(status='PRESENT', sha256=sha(raw), bytes=len(raw))
                if mode not in modes:
                    raise ReceiptFailure('unrequested_stage_receipt_present')
                saved[filename] = (raw, _parse(raw))
            except ReceiptFailure as exc:
                if str(exc) == 'missing_file':
                    record['status'] = 'MISSING'
                    if mode not in modes:
                        continue
                elif record['status'] == 'UNREAD':
                    record['status'] = 'REFUSED'
                error('read_or_parse', str(exc), record.copy())
            except (TypeError, ValueError):
                record['status'] = 'REFUSED'
                error('read_or_parse', 'receipt_path_invalid', record.copy())
    for mode in modes:
        filename = mode + '_SESSION.json'
        if filename not in saved:
            continue
        raw, observation = saved[filename]
        reference = {'path': filename, 'sha256': sha(raw), 'bytes': len(raw)}
        try:
            if not result['source_binding_verified']:
                raise ReceiptFailure('source_binding_not_verified')
            if observation.get('kind') != expected_kind:
                raise ReceiptFailure('session_kind_differs_from_bound_emitter')
            if observation.get('mode') != mode:
                raise ReceiptFailure('session_mode_differs')
            if any(type(observation.get(k)) is not bool for k in ('client_started', 'model_turn_request_sent')):
                raise ReceiptFailure('actual_execution_counters_not_boolean')
            if observation['model_turn_request_sent'] and not observation['client_started']:
                raise ReceiptFailure('sent_turn_without_client_start')
            if mode == 'synthetic' and observation.get('verdict_submitted') is not False:
                raise ReceiptFailure('synthetic_verdict_claim_refused')
            result['observations'][mode] = observation
        except ReceiptFailure as exc:
            error('session_integrity', str(exc), reference)
    for mode in modes:
        filename = mode + '_STAGE.json'
        if filename not in saved:
            continue
        raw, stage = saved[filename]
        reference = {'path': filename, 'sha256': sha(raw), 'bytes': len(raw)}
        try:
            if mode not in result['observations']:
                raise ReceiptFailure('separate_session_not_validated')
            if stage.get('stage') != mode:
                raise ReceiptFailure('stage_mode_differs')
            if canonical(stage.get('observation')) != saved[mode + '_SESSION.json'][0]:
                raise ReceiptFailure('stage_observation_differs_from_original_session_bytes')
            if canonical(stage) != raw:
                raise ReceiptFailure('stage_encoding_differs_from_emitter_canonical_bytes')
            result['stages'][mode] = stage
        except ReceiptFailure as exc:
            error('stage_integrity', str(exc), reference)
        except (ValueError, UnicodeError, RecursionError):
            error('stage_integrity', 'stage_canonical_encoding_refused', reference)
    result['complete'] = (len(result['observations']) == len(modes) and len(result['stages']) == len(modes)
                          and not result['errors'])
    result['eligible_for_controller_admission_checks'] = result['complete'] and result['source_binding_verified']
    return result
