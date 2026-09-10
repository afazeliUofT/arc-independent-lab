#!/usr/bin/env python3
"""Run the existing approved030 operation at most once, then collect its evidence.

This wrapper adds no model permission, changes no030 dependency and never retries
a controller whose run directories or exclusive wrapper marker already exist.
Raw controller streams are bounded in memory and discarded after safe extraction.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import selectors
import signal
import stat
import subprocess
import sys
import time
from datetime import datetime, timezone

WORKFLOW = 'delivery/P3_030_RETURN_WORKFLOW'
MAIN = 'delivery/P3_FINITE_REVIEW_030'
KERNEL = 'delivery/P3_FINITE_REVIEW_030_KERNEL_PREFLIGHT'
CONTROLLER = 'scripts/p3_finite_review_030.py'
PINS = {
    CONTROLLER: '1f8a61e9fb98dc15d0478a067950f46aa512d0ae3e900d649f6bb5eb71a3948a',
    'configs/P3_FINITE_REVIEW_SCOPE_030.json': '5abc5794f3adadeebc0e3df3e1ffd5bc4416806d2d1212f0a6b73db96d177060',
    'state/ESCALATION.md': '58e0dc94a91bc05109b68edfed9285154047d3f511102326c2f25475914cbbe1',
}
OUTER_SECONDS = 4310
CAPTURE_BYTES = 1024 * 1024
SAFE_PREFIXES = ('STOP: ', 'STATUS: ', 'REPORT: ', 'REPORT_SHA256: ',
                 'REVIEW_VERDICT: ', 'VERIFIED TERMINAL RECEIPT;',
                 'No scientific verdict was submitted.')


class WorkflowStop(Exception):
    """A fixed categorical failure, safe to include in the public report."""


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def checked_directory(path, *, create=False):
    """Refuse symlink components before any workflow-controlled write."""
    path = Path(path).absolute()
    current = Path(path.anchor)
    for component in path.parts[1:]:
        current /= component
        try:
            mode = current.lstat().st_mode
        except FileNotFoundError:
            if not create:
                raise WorkflowStop('required_directory_absent')
            try:
                current.mkdir(mode=0o700)
            except FileExistsError:
                pass
            mode = current.lstat().st_mode
        if not stat.S_ISDIR(mode):
            raise WorkflowStop('directory_symlink_or_special_file_refused')
    return path


def read_fixed(root, relative, maximum=4 * 1024 * 1024):
    path = root / relative
    checked_directory(path.parent)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or before.st_size > maximum:
            raise WorkflowStop('fixed_input_file_shape_refused')
        raw = os.read(fd, maximum + 1)
        after = os.fstat(fd)
        if len(raw) > maximum or len(raw) != before.st_size or (
                before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (
                after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns):
            raise WorkflowStop('fixed_input_changed_or_oversized')
        return raw
    finally:
        os.close(fd)


def write_json(path, value, *, exclusive=False):
    checked_directory(path.parent)
    raw = (json.dumps(value, indent=2, sort_keys=True) + '\n').encode('utf-8')
    if exclusive:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        try:
            with os.fdopen(fd, 'wb') as handle:
                handle.write(raw)
                handle.flush()
                os.fsync(handle.fileno())
        finally:
            # fdopen owns the descriptor even when its write raises.
            pass
    else:
        if os.path.lexists(path):
            info = path.lstat()
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                raise WorkflowStop('workflow_report_target_refused')
        temporary = path.with_name(path.name + '.pending-' + str(os.getpid()))
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        try:
            with os.fdopen(fd, 'wb') as handle:
                handle.write(raw)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
        finally:
            if os.path.lexists(temporary):
                temporary.unlink()
    directory_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)
    return sha(raw)


def safe_diagnostics(stdout, stderr):
    """Keep approved controller status text, never arbitrary stderr messages."""
    safe = []
    for line in stdout.decode('utf-8', 'replace').splitlines():
        if line.startswith(SAFE_PREFIXES):
            safe.append(''.join(c for c in line[:2048] if c.isprintable()))
    classes, frames = [], []
    for line in stderr.decode('utf-8', 'replace').splitlines():
        match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*(?:Error|Exception|Interrupt))(?::|$)', line)
        if match:
            classes.append(match.group(1))
        match = re.match(r'^\s*File "([^"]+)", line ([0-9]+)', line)
        if match:
            name = Path(match.group(1)).name
            if re.fullmatch(r'[A-Za-z0-9_.-]{1,128}', name):
                frames.append({'module_basename': name, 'line': int(match.group(2))})
    return {'controller_status_lines': safe[-32:],
            'stderr_exception_classes': classes[-16:], 'stderr_frames': frames[-32:],
            'raw_stderr_saved_or_hashed': False, 'raw_streams_saved_or_hashed': False}


def run_controller(root, emit=print, *, command=None, wall_seconds=OUTER_SECONDS):
    """Run one pinned controller; overrides exist solely for local fixture tests.

    SIGINT is sent to the controller first, allowing its existing finally cleanup.
    A 60-second grace precedes emergency TERM (10s), then KILL (5s). Forced
    wrapper cleanup is reported; it never establishes native-child admission.
    """
    argv = command or [sys.executable, '-I', '-B', '-u', str(root / CONTROLLER), '--run-attended-review']
    started = time.monotonic()
    result = {'controller_started': False, 'controller_reaped': False,
              'interrupted': False, 'outer_guard_reached': False,
              'forced_controller_cleanup': False, 'native_cleanup_inferred': False,
              'exit_code': None, 'outer_guard_seconds': wall_seconds}
    streams = {'stdout': bytearray(), 'stderr': bytearray()}
    observed = {'stdout': 0, 'stderr': 0}
    process, selector = None, selectors.DefaultSelector()
    phase, deadline = 'running', started + wall_seconds
    try:
        process = subprocess.Popen(argv, cwd=root, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        result['controller_started'] = True
        for name in streams:
            stream = getattr(process, name)
            os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_READ, name)
        while True:
            try:
                now = time.monotonic()
                if process.poll() is not None and not selector.get_map():
                    break
                if now >= deadline:
                    if phase == 'running':
                        result['outer_guard_reached'] = True
                        phase, deadline = 'interrupt', now + 60
                        if process.poll() is None:
                            process.send_signal(signal.SIGINT)
                        emit('WORKFLOW: outer guard reached; allowing controller cleanup.')
                    elif phase == 'interrupt':
                        result['forced_controller_cleanup'] = True
                        phase, deadline = 'terminate', now + 10
                        if process.poll() is None:
                            os.killpg(process.pid, signal.SIGTERM)
                    elif phase == 'terminate':
                        phase, deadline = 'kill', now + 5
                        if process.poll() is None:
                            os.killpg(process.pid, signal.SIGKILL)
                    else:
                        break
                for key, _ in selector.select(timeout=0.2):
                    try:
                        chunk = os.read(key.fileobj.fileno(), 65536)
                    except BlockingIOError:
                        continue
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    name = key.data
                    observed[name] += len(chunk)
                    remaining = CAPTURE_BYTES - len(streams[name])
                    if remaining > 0:
                        streams[name].extend(chunk[:remaining])
                    # This is the parent controller's console, not native logs.
                    # Terminal delivery is bounded as well as memory retention.
                    if remaining > 0:
                        emit(chunk[:remaining].decode('utf-8', 'replace').rstrip('\n'))
            except KeyboardInterrupt:
                result['interrupted'] = True
                if phase == 'running':
                    phase, deadline = 'interrupt', time.monotonic() + 60
                    if process.poll() is None:
                        process.send_signal(signal.SIGINT)
                    emit('WORKFLOW: interruption received; preserving controller cleanup and evidence.')
                # Repeated Ctrl-C cannot skip the controller's cleanup grace.
    except BaseException as error:
        result['transport_failure_class'] = type(error).__name__
        result['interrupted'] = result['interrupted'] or isinstance(error, KeyboardInterrupt)
    finally:
        if process is not None:
            if process.poll() is None:
                # Unexpected parent I/O/terminal failures take the same bounded
                # cleanup route. They cannot leave an unobserved child running.
                for sig, grace in ((signal.SIGINT, 60), (signal.SIGTERM, 10), (signal.SIGKILL, 5)):
                    try:
                        if process.poll() is not None:
                            break
                        if sig == signal.SIGINT:
                            process.send_signal(sig)
                        else:
                            result['forced_controller_cleanup'] = True
                            os.killpg(process.pid, sig)
                        process.wait(timeout=grace)
                    except (ProcessLookupError, subprocess.TimeoutExpired):
                        continue
                    except KeyboardInterrupt:
                        result['interrupted'] = True
                        continue
            result['exit_code'] = process.poll()
            result['controller_reaped'] = process.returncode is not None
            for stream in (process.stdout, process.stderr):
                if stream is not None:
                    stream.close()
        selector.close()
        result.update(safe_diagnostics(bytes(streams['stdout']), bytes(streams['stderr'])))
        result['stream_bytes_observed'] = observed
        result['stream_capture_truncated'] = {k: observed[k] > CAPTURE_BYTES for k in observed}
        result['elapsed_seconds'] = round(time.monotonic() - started, 6)
    return result


def default_collector(root):
    path = Path(__file__).with_name('publish_review030_evidence.py')
    spec = importlib.util.spec_from_file_location('collect_review030_evidence_031', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.collect(root)


def run_inspection(root, emit=print):
    """The approved030 no-argument main only verifies/prints; no native launch."""
    outcome = run_controller(root, emit, command=[sys.executable, '-I', '-B', '-u',
        str(root / CONTROLLER)], wall_seconds=60)
    outcome['invocation_kind'] = 'PINNED030_READ_ONLY_INSPECTION_NO_MANUAL_LAUNCH_FLAG'
    outcome['native_start_or_model_turn_requested'] = False
    return outcome


def verify_pins(root, pins):
    for relative, expected in pins.items():
        if sha(read_fixed(root, relative)) != expected:
            raise WorkflowStop('approved030_pinned_input_mismatch')


def run_workflow(root, *, runner=run_controller, inspector=run_inspection,
                 collector=None, pins=None, emit=print):
    """Return {'collection': explicit publisher inventory, 'status': category}.

    Call only from an explicit human operation. No Git write or network occurs
    here. Injected dependencies let fixture tests execute without native models.
    """
    root = checked_directory(Path(root))
    folder = checked_directory(root / WORKFLOW, create=True)
    report_path, marker = folder / 'WORKFLOW_REPORT.json', folder / 'LAUNCH_RESERVED.json'
    report = {'kind': 'P3_030_RETURN_WORKFLOW_v1', 'started_utc': utc(),
        'status': 'STARTED', 'controller_invoked': False, 'reason_code': None,
        'existing_paths': {}, 'controller_outcome': None, 'inspection_outcome': None,
        'automatic_retry': False, 'model_allowance_added': False,
        'scientific_admission_asserted': False, 'credential_contents_read': False,
        'publication_performed_by_workflow': False}
    collection = None
    reserved = False
    try:
        write_json(report_path, report)
        existing = {name: os.path.lexists(root / name) for name in (MAIN, KERNEL, WORKFLOW + '/LAUNCH_RESERVED.json')}
        report['existing_paths'] = existing
        if any(existing.values()):
            report['status'] = 'COLLECT_ONLY_EXISTING_ATTEMPT_OR_MARKER'
            emit('WORKFLOW: existing attempt or launch marker; no native retry. Inspecting and collecting evidence.')
            try:
                for relative in (MAIN, KERNEL):
                    path = root / relative
                    if os.path.lexists(path) and not stat.S_ISDIR(path.lstat().st_mode):
                        raise WorkflowStop('existing_attempt_path_is_not_a_regular_directory')
                verify_pins(root, PINS if pins is None else pins)
            except Exception as error:
                report['inspection_outcome'] = {'status': 'SKIPPED_INSPECTION_PRECONDITION_FAILED',
                    'reason_code': str(error) if type(error) is WorkflowStop else 'fixed_input_validation_failed',
                    'error_class': type(error).__name__, 'native_start_or_model_turn_requested': False}
            else:
                report['inspection_outcome'] = inspector(root, emit)
        else:
            verify_pins(root, PINS if pins is None else pins)
            # Exclusive durable reservation happens before the child. Any later
            # failure, including failure to spawn, prevents automatic re-entry.
            try:
                write_json(marker, {'kind': 'P3_030_WRAPPER_EXCLUSIVE_RESERVATION_v1',
                    'reserved_utc': utc(), 'controller_relative_path': CONTROLLER,
                    'controller_sha256': (PINS if pins is None else pins)[CONTROLLER],
                    'automatic_retry': False, 'native_start_or_model_turn_proven': False}, exclusive=True)
            except FileExistsError:
                report['status'] = 'COLLECT_ONLY_CONCURRENT_RESERVATION'
            else:
                reserved = True
                # A direct030 invocation could have reserved its own directory
                # while this wrapper verified its inputs. Do not invoke it then.
                if os.path.lexists(root / MAIN) or os.path.lexists(root / KERNEL):
                    report['status'] = 'COLLECT_ONLY_ATTEMPT_APPEARED_BEFORE_LAUNCH'
                else:
                    report['controller_invoked'] = True
                    emit('WORKFLOW: invoking the unchanged approved030 controller once.')
                    report['controller_outcome'] = runner(root, emit)
                    report['status'] = 'CONTROLLER_RETURNED_EVIDENCE_COLLECTION_REQUIRED'
    except KeyboardInterrupt:
        report['status'] = 'WORKFLOW_INTERRUPTED_EVIDENCE_PRESERVED'
        report['reason_code'] = 'human_interrupt_outside_controller_transport'
    except BaseException as error:
        if isinstance(error, (SystemExit, GeneratorExit)):
            report['status'] = 'WORKFLOW_EARLY_EXIT_EVIDENCE_PRESERVED'
        else:
            report['status'] = 'WORKFLOW_STOPPED_EVIDENCE_PRESERVED'
        report['reason_code'] = str(error) if type(error) is WorkflowStop else 'guarded_workflow_or_controller_dependency_failure'
        report['error_class'] = type(error).__name__
    finally:
        report['finished_utc'] = utc()
        report['observed_at_return'] = {name: os.path.lexists(root / name)
            for name in (MAIN + '/REPORT.json', KERNEL + '/REPORT.json', MAIN + '/science_output/REVIEW_VERDICT.json')}
        # A first launch's outcome is immutable across later collect-only calls.
        if reserved:
            try:
                write_json(folder / 'LAUNCH_OUTCOME.json', report, exclusive=True)
            except Exception as error:
                report['outcome_write_failure_class'] = type(error).__name__
        write_json(report_path, report)
        emit('WORKFLOW_REPORT: ' + str(report_path))
        try:
            collection = (collector or default_collector)(root)
        except Exception as error:
            report['collection_failure_class'] = type(error).__name__
            report['collection_failure_code'] = 'evidence_collector_stopped_preserve_existing_files'
            write_json(report_path, report)
            emit('WORKFLOW: evidence collector stopped; preserve the workflow report and all existing files.')
    return {'workflow_report': str(report_path.relative_to(root)), 'collection': collection,
            'controller_invoked': report['controller_invoked'], 'status': report['status'],
            'controller_outcome': report['controller_outcome'], 'inspection_outcome': report['inspection_outcome']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-or-collect', action='store_true', required=True)
    args = parser.parse_args()
    result = run_workflow(Path.home() / 'ARC_Independent_Lab')
    print('WORKFLOW_STATUS: ' + result['status'])
    return 0 if result['collection'] is not None else 1


if __name__ == '__main__':
    raise SystemExit(main())
