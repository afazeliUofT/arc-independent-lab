#!/usr/bin/env python3
"""Bounded request refusal without widening the original evidence authority.

Invalid resource arguments never reach a filesystem read. Correctable feedback
requires a fresh whole-packet validation, and all corrections share the prior
eight-error ceiling. No old broker latch is reset and no original code changes.
"""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import sys


def _load_prior():
    name = 'p3_review_interface_028'
    path = Path(__file__).resolve().with_name(name + '.py')
    existing = sys.modules.get(name)
    if existing is not None:
        if Path(existing.__file__).resolve() != path:
            raise RuntimeError('Conflicting prior interface origin')
        return existing
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


prior = _load_prior()
original = prior.original
BrokerError = original.BrokerError
_path = original._path
REVIEW_MANIFESTS = original.REVIEW_MANIFESTS
SUBJECTS = original.SUBJECTS
VERDICT_NAME = original.VERDICT_NAME
MAX_RECOVERABLE_ERRORS = prior.MAX_RECOVERABLE_ERRORS

# Values are authored constants. No raw path, exception text, digest, or
# supplied field name is retained by a refusal receipt.
PATH_REFUSAL_CAUSES = {
    'resource_path_type': 'Invalid resource path',
    'resource_path_empty': 'Invalid resource path',
    'resource_path_too_long': 'Invalid resource path',
    'resource_path_backslash': 'Invalid resource path',
    'resource_path_control': 'Invalid resource path',
    'resource_path_absolute': 'Noncanonical resource path',
    'resource_path_traversal': 'Noncanonical resource path',
    'resource_path_noncanonical': 'Noncanonical resource path',
    'resource_not_manifested': 'Unmanifested resource denied',
}
PATH_INSTRUCTION = ('The requested resource was refused without opening it. '
    'Choose an exact manifested path from the supplied packet index. Do not '
    'guess, normalize or traverse paths. Correct the arguments and retry within '
    'the remaining shared correction and call limits.')
INPUT_INSTRUCTIONS = {**prior.INPUT_INSTRUCTIONS,
    **{key: PATH_INSTRUCTION for key in PATH_REFUSAL_CAUSES}}


def refusal_metadata(code):
    if code not in PATH_REFUSAL_CAUSES:
        raise BrokerError('Unknown interface input-error code')
    return {'category': code, 'original_guard_message': PATH_REFUSAL_CAUSES[code],
        'original_path_guard_executed': True,
        'manifest_membership_checked': code == 'resource_not_manifested',
        'denied_resource_opened': False, 'path_normalized_or_rewritten': False,
        'raw_path_or_exception_saved': False, 'full_packet_revalidated_before_feedback': True}


class ToolInputError(ValueError):
    """Only a finite, wholly revalidated argument refusal escapes dispatch."""
    def __init__(self, code):
        if code not in INPUT_INSTRUCTIONS:
            raise BrokerError('Unknown interface input-error code')
        self.code = code
        self.instruction = INPUT_INSTRUCTIONS[code]
        super().__init__(code)

    def as_dict(self):
        value = {'schema': 'arc.tool-input-error.v2', 'code': self.code,
            'instruction': self.instruction, 'retryable_with_corrected_arguments': True,
            'scientific_content_modified': False}
        if self.code in PATH_REFUSAL_CAUSES:
            value['resource_path_refusal'] = refusal_metadata(self.code)
        return value


def _path_category(value):
    if type(value) is not str:
        return 'resource_path_type'
    if not value:
        return 'resource_path_empty'
    if len(value) > 1024:
        return 'resource_path_too_long'
    if '\\' in value:
        return 'resource_path_backslash'
    if any(ord(char) < 32 for char in value):
        return 'resource_path_control'
    if value.startswith('/'):
        return 'resource_path_absolute'
    if '..' in value.split('/'):
        return 'resource_path_traversal'
    if any(part in ('', '.') for part in value.split('/')):
        return 'resource_path_noncanonical'
    return None


class ReviewBroker(prior.ReviewBroker):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._path_refusal_counts = {code: 0 for code in PATH_REFUSAL_CAUSES}
        self._last_path_refusal = None

    def resource_path_refusal_receipt(self):
        return {'kind': 'P3_RESOURCE_PATH_REFUSALS_032_v1',
            'calls_refused': sum(self._path_refusal_counts.values()),
            'calls_by_category': dict(self._path_refusal_counts),
            'last_refusal': copy.deepcopy(self._last_path_refusal),
            'shared_recoverable_error_count': self.recoverable_input_errors,
            'shared_recoverable_error_ceiling': MAX_RECOVERABLE_ERRORS,
            'raw_paths_saved_or_hashed': False, 'denied_resource_access_granted': False}

    def _validate_resource_reference(self, value):
        """Execute the unchanged syntax guard before membership or any read."""
        category = _path_category(value)
        try:
            original._path(value)
        except BrokerError as error:
            # Unexpected future original-guard behaviour stays terminal. The
            # category is explanatory; it is never an alternative path parser.
            if category is None or str(error) != PATH_REFUSAL_CAUSES[category]:
                raise
            raise ToolInputError(category) from error
        original._require(category is None, 'Path classifier differs from original guard')
        if value not in self._original._files:
            try:
                # This unchanged original guard performs no read for an absent
                # manifest entry, and provides an actual refusal cause.
                self._original._read(value)
            except BrokerError as error:
                if str(error) != PATH_REFUSAL_CAUSES['resource_not_manifested']:
                    raise
                raise ToolInputError('resource_not_manifested') from error
            raise BrokerError('Unmanifested original read unexpectedly succeeded')

    def _check_paths(self, tool, args):
        paths = []
        if type(args) is dict:
            if tool in ('read_text', 'read_page_image', 'hash_file') and 'path' in args:
                paths.append(args['path'])
            if tool == 'submit_verdict' and type(args.get('dispositions')) is list:
                for item in args['dispositions']:
                    if type(item) is dict and type(item.get('evidence')) is list:
                        for reference in item['evidence']:
                            if type(reference) is dict and 'path' in reference:
                                paths.append(reference['path'])
        denial = None
        allowed = set()
        for path in paths:
            try:
                self._validate_resource_reference(path)
            except ToolInputError as error:
                if denial is None:
                    denial = error
                continue
            allowed.add(path)
            self._checked_read(path, keep_text=tool == 'read_text')
        # A denied reference cannot hide a false digest for a different known
        # reference or for a scope manifest. All verifiable integrity claims
        # are checked before returning the first fixed argument refusal.
        if tool == 'submit_verdict' and type(args) is dict:
            claims = args.get('applies_to')
            if type(claims) is dict:
                for field, path in REVIEW_MANIFESTS.items():
                    claim = claims.get(field)
                    if type(claim) is str and original.SHA_RE.fullmatch(claim):
                        _, measured = self._checked_read(path)
                        original._require(measured == claim, 'Review scope manifest mismatch')
            if type(args.get('dispositions')) is list:
                for item in args['dispositions']:
                    if type(item) is dict and type(item.get('evidence')) is list:
                        for reference in item['evidence']:
                            if type(reference) is dict:
                                path, claim = reference.get('path'), reference.get('sha256')
                                if (type(path) is str and path in allowed and type(claim) is str
                                        and original.SHA_RE.fullmatch(claim)):
                                    _, measured = self._checked_read(path)
                                    original._require(measured == claim, 'Verdict evidence digest mismatch')
        if denial is not None:
            raise denial

    def dispatch(self, tool, arguments):
        with self._interface_lock:
            self._request_reads = {}
            try:
                original._require(not self._failed and not self._original._verdict_written,
                    'Broker already stopped/completed')
                original._require(type(tool) is str and tool in original.TOOL_SCHEMAS,
                    'Unknown operation')
                try:
                    self._check_paths(tool, arguments)
                    self._prevalidate(tool, arguments)
                except (ToolInputError, prior.ToolInputError) as error:
                    # This runs before the error counter or feedback is exposed.
                    # A real mutation or unavailable manifested file is fatal.
                    self.verify_inputs()
                    self.recoverable_input_errors += 1
                    original._require(self.recoverable_input_errors <= MAX_RECOVERABLE_ERRORS,
                        'Recoverable input-error ceiling reached')
                    if error.code in PATH_REFUSAL_CAUSES:
                        self._path_refusal_counts[error.code] += 1
                        self._last_path_refusal = refusal_metadata(error.code)
                    cause = error.__cause__ if isinstance(error.__cause__, BrokerError) else None
                    raise ToolInputError(error.code) from cause
                return self._original.dispatch(tool, arguments)
            except ToolInputError:
                raise
            except BaseException:
                self._original._failed = True
                raise
            finally:
                self._request_reads.clear()


def classify_broker_failure(error):
    if isinstance(error, ToolInputError):
        return 'input.' + error.code
    return prior.classify_broker_failure(error)


def dynamic_tool_specs():
    specs = prior.dynamic_tool_specs()
    old = ('Ordinary argument mistakes may receive fixed feedback, with eight total '
           'corrections allowed; authority, integrity and protocol failures remain terminal.')
    new = ('Invalid resource arguments are refused without opening the requested resource '
           'and may receive fixed corrective feedback only after whole-packet verification. '
           'They share the same eight total argument corrections. Integrity failures, '
           'unknown operations and protocol violations remain terminal. No denied path '
           'is normalized, rewritten or granted access.')
    for spec in specs:
        original._require(old in spec['description'], 'Prior tool feedback description differs')
        spec['description'] = spec['description'].replace(old, new)
    return specs
