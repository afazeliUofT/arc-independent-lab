#!/usr/bin/env python3
"""Closed R1-R7 analytical-review broker; no model, shell or scientific verdict.

Reuse the historical broker's descriptor-relative no-link I/O and whole-packet
integrity checks. The old observer operation and first-candidate verdict schema
are deliberately absent. The trusted parent, not this module, must isolate the
reviewer and pin this implementation, the packet manifest and output boundary.
A delivery receipt proves bytes were returned through tools, not human-like
reading, comprehension, or correctness of a reviewer's conclusions.
"""
from __future__ import annotations

import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys


def _load_original():
    name = 'p3_review_broker'
    path = Path(__file__).resolve().with_name(name + '.py')
    existing = sys.modules.get(name)
    if existing is not None:
        if Path(existing.__file__).resolve() != path:
            raise RuntimeError('Conflicting historical broker origin')
        return existing
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


original = _load_original()
BrokerError = original.BrokerError
_require, _keys, _path, _sha = original._require, original._keys, original._path, original._sha
VERDICT_NAME = 'REVIEW_VERDICT.json'
SCOPE_ID = 'P3_FOCUSED_ANALYTICAL_REVIEW_039'
SCOPE_PATH = 'FOCUSED_SCOPE.json'
SCIENTIFIC_MANIFEST_PATH = 'evidence/P3_FOCUSED_REVIEW_MANIFEST_038.json'
CLAIMS = tuple('R' + str(i) for i in range(1, 8))
SUBJECTS = CLAIMS
VERDICTS = original.VERDICTS
ASSESSMENTS = ('SUPPORTED_WITH_SCOPE', 'REFUTED_WITH_SCOPE', 'UNRESOLVED')
MAX_RECOVERABLE_ERRORS = 8
PAPERS = {
    'CHV79': {'sha256': '70e60317cc1e7815118aac54b00d3aadf5558f7bc219ca2d3b6e3396c2611086',
              'pages': 4, 'claim_id': 'R1', 'images': (2, 3, 4)},
    'PK97': {'sha256': '873998cb1f647756e12f061f5c9152c2bae9fa3b37b0efa45432aa4b7e9df570',
             'pages': 59, 'claim_id': 'R6', 'images': (1, 28, 39, 40, 45, 46, 47, 48)},
}
GOVERNING = tuple('docs/governing/' + name for name in (
    '00_START_HERE.md', '01_THE_PROBLEM.md', '02_RESEARCH_PROCESS.md',
    '03_AUTONOMY_SPEC.md', '04_RESOURCES_AND_SETUP.md', '05_OPERATIONAL_LESSONS.md'))


class ToolInputError(ValueError):
    """Only fixed argument/access-completion feedback is recoverable."""
    INSTRUCTIONS = {
        'invalid_arguments': 'Match the advertised tool schema exactly; correct the arguments and retry.',
        'resource_refused': 'Choose an exact manifested path. No denied resource was opened or normalized.',
        'resource_path_traversal': 'Use an exact manifested path with no parent traversal. The denied path was not opened.',
        'integer_bounds': 'Use the integer bounds in the advertised schema; correct the arguments and retry.',
        'governing_read_order': 'Read the six governing documents completely in the supplied order before other text or images.',
        'delivery_incomplete': 'Read the missing manifested text ranges and required paper images before a substantive verdict; source_access_receipt reports remaining delivery.',
        'verdict_contract': 'Supply exactly R1-R7 and CHV79/R1 plus PK97/R6, with evidence and a recommendation consistent with the scoped verdict.',
    }
    def __init__(self, code):
        _require(code in self.INSTRUCTIONS, 'Unknown input-error code')
        self.code = code
        super().__init__(code)
    def as_dict(self):
        return {'schema': 'arc.focused-tool-input-error.v1', 'code': self.code,
                'instruction': self.INSTRUCTIONS[self.code],
                'retryable_with_corrected_arguments': True,
                'scientific_content_modified': False}


def classify_broker_failure(error):
    if isinstance(error, ToolInputError):
        return 'input.' + error.code
    return 'focused_broker_integrity_or_boundary_failure'


def _check_schema(value, schema):
    kind = schema.get('type')
    valid = {'object': type(value) is dict, 'array': type(value) is list,
             'string': type(value) is str, 'integer': type(value) is int}.get(kind, False)
    if not valid:
        raise ToolInputError('invalid_arguments')
    if 'enum' in schema and value not in schema['enum']:
        raise ToolInputError('invalid_arguments')
    if kind == 'object':
        if set(value) != set(schema['properties']):
            raise ToolInputError('invalid_arguments')
        for key, child in schema['properties'].items():
            _check_schema(value[key], child)
    elif kind == 'array':
        if not schema.get('minItems', 0) <= len(value) <= schema.get('maxItems', 10000):
            raise ToolInputError('invalid_arguments')
        for item in value:
            _check_schema(item, schema['items'])
    elif kind == 'string':
        if not schema.get('minLength', 0) <= len(value) <= schema.get('maxLength', 30000):
            raise ToolInputError('invalid_arguments')
        if schema.get('pattern') and not original.SHA_RE.fullmatch(value):
            raise ToolInputError('invalid_arguments')
        if schema.get('minLength', 0) and not value.strip():
            raise ToolInputError('invalid_arguments')
    elif not schema.get('minimum', 0) <= value <= schema.get('maximum', original.MAX_FILE_BYTES):
        raise ToolInputError('integer_bounds')


def _merge(ranges, start, end):
    values = sorted([*ranges, (start, end)])
    result = []
    for a, b in values:
        if result and a <= result[-1][1]:
            result[-1] = (result[-1][0], max(b, result[-1][1]))
        else:
            result.append((a, b))
    return result


class ReviewBroker(original.ReviewBroker):
    def __init__(self, *args, synthetic=False, **kwargs):
        _require(type(synthetic) is bool, "Invalid trusted synthetic selector")
        super().__init__(*args, **kwargs)
        self.synthetic = synthetic
        self.recoverable_input_errors = 0
        self._refusals = 0
        self._delivered = {}
        self._images_delivered = set()
        self._delivery_events = []
        if synthetic:
            try:
                _require(set(self._files) == {'CANARY.txt'} and self._files['CANARY.txt']['kind'] == 'text', 'Synthetic packet must contain only CANARY.txt')
            except BaseException:
                self.close()
                raise
            return
        try:
            raw, self.scope_descriptor_sha256 = self._read(SCOPE_PATH, 'text')
            scope = original._json(raw)
            _keys(scope, ('schema_version', 'scope_id', 'scientific_manifest', 'required_texts', 'papers'))
            _require(type(scope['schema_version']) is int and scope['schema_version'] == 1 and scope['scope_id'] == SCOPE_ID, 'Wrong focused scope')
            self._reference(scope['scientific_manifest'], 'text')
            _require(scope['scientific_manifest']['path'] == SCIENTIFIC_MANIFEST_PATH, 'Wrong scientific manifest')
            self.scientific_manifest_sha256 = scope['scientific_manifest']['sha256']
            science = original._json(self._read(SCIENTIFIC_MANIFEST_PATH, 'text')[0])
            _require(science.get('claim_ids') == list(CLAIMS), 'Wrong scientific claim set')
            required = scope['required_texts']
            expected = [entry['path'] for entry in science['inputs']] + [SCIENTIFIC_MANIFEST_PATH]
            _require(type(required) is list and len(required) == len(set(required)) and set(required) == set(expected),
                     'Required text inventory must match complete scientific manifest')
            _require(required[:6] == list(GOVERNING), 'Wrong governing reading order')
            self.required_texts = list(required)
            for entry in science['inputs']:
                self._reference(entry, 'text')
            _require(type(scope['papers']) is list and len(scope['papers']) == 2, 'Wrong paper inventory')
            self.papers = {}
            for paper in scope['papers']:
                _keys(paper, ('id', 'pdf', 'full_text', 'pages'))
                pid = paper['id']
                _require(pid in PAPERS and pid not in self.papers, 'Unknown or duplicate paper')
                self._reference(paper['pdf'], 'binary')
                self._reference(paper['full_text'], 'text')
                _require(paper['pdf']['sha256'] == PAPERS[pid]['sha256'], 'Wrong supplied PDF bytes')
                _require(type(paper['pages']) is list and len(paper['pages']) == PAPERS[pid]['pages'], 'Paper page count differs')
                _require(paper['pdf'] in science['private_sources'], 'PDF absent from scientific manifest')
                derivative_paths = {paper['full_text']['path']}
                for number, page in enumerate(paper['pages'], 1):
                    _keys(page, ('page', 'text', 'image'))
                    _require(type(page['page']) is int and page['page'] == number, 'Page inventory not complete/in order')
                    self._reference(page['text'], 'text')
                    self._reference(page['image'], 'image')
                    for field in ('text', 'image'):
                        path = page[field]['path']
                        _require(path not in derivative_paths, 'Duplicate derivative path')
                        derivative_paths.add(path)
                self.papers[pid] = copy.deepcopy(paper)
            self.scope = scope
        except BaseException:
            self.close()
            raise

    def _reference(self, reference, kind=None):
        _keys(reference, ('path', 'sha256'))
        _, actual = self._read(reference['path'], kind)
        _require(actual == _sha(reference['sha256']), 'Scope reference hash mismatch')
        return actual

    def _complete(self, path):
        raw, _ = self._read(path, 'text')
        total = len(raw.decode('utf-8'))
        return self._delivered.get(path, []) == [(0, total)]

    def _next_governing(self):
        return next((path for path in GOVERNING if not self._complete(path)), None)

    def _validate_arguments(self, tool, args):
        # Check any well-formed claimed known hashes before ordinary feedback.
        if type(args) is dict and tool == 'submit_verdict':
            applies = args.get('applies_to')
            if type(applies) is dict:
                sha = applies.get('scientific_manifest_sha256')
                if type(sha) is str and original.SHA_RE.fullmatch(sha):
                    _require(sha == self.scientific_manifest_sha256, 'Verdict scientific scope digest differs')
            for field in ('claim_assessments', 'source_comparisons'):
                rows = args.get(field)
                if type(rows) is list:
                    for row in rows:
                        if type(row) is dict and type(row.get('evidence')) is list:
                            for ref in row['evidence']:
                                if type(ref) is dict and type(ref.get('path')) is str and ref['path'] in self._files:
                                    sha = ref.get('sha256')
                                    if type(sha) is str and original.SHA_RE.fullmatch(sha):
                                        _require(self._read(ref['path'])[1] == sha, 'Verdict evidence digest differs')
        _check_schema(args, TOOL_SCHEMAS[tool])
        paths = []
        if tool in ('read_text', 'read_page_image', 'hash_file'):
            paths = [args['path']]
        elif tool == 'submit_verdict':
            paths = [r['path'] for f in ('claim_assessments', 'source_comparisons') for row in args[f] for r in row['evidence']]
        for path in paths:
            try:
                _path(path)
            except BrokerError as error:
                code = 'resource_path_traversal' if type(path) is str and '..' in path.split('/') else 'resource_refused'
                raise ToolInputError(code) from error
            if path not in self._files:
                raise ToolInputError('resource_refused')
        if tool in ('read_text', 'read_page_image'):
            next_doc = None if self.synthetic else self._next_governing()
            if next_doc is not None and args['path'] != next_doc:
                raise ToolInputError('governing_read_order')
            expected_kind = 'text' if tool == 'read_text' else 'image'
            if self._files[args['path']]['kind'] != expected_kind:
                raise ToolInputError('invalid_arguments')
            if tool == 'read_text':
                total = len(self._read(args['path'], 'text')[0].decode('utf-8'))
                if args['offset'] > total:
                    raise ToolInputError('invalid_arguments')
        if tool == 'submit_verdict':
            self._validate_verdict(args)

    def dispatch(self, tool, arguments):
        with self._lock:
            _require(not self._failed and not self._verdict_written, 'Broker already stopped/completed')
            try:
                _require(type(tool) is str and tool in TOOL_SCHEMAS, 'Unknown operation')
                _require(not self.synthetic or tool == 'read_text', 'Synthetic scope admits only read_text')
                self.verify_inputs()
                try:
                    self._validate_arguments(tool, arguments)
                except ToolInputError as error:
                    self.verify_inputs()
                    self.recoverable_input_errors += 1
                    _require(self.recoverable_input_errors <= MAX_RECOVERABLE_ERRORS, 'Recoverable input-error ceiling reached')
                    if error.code in ('resource_refused', 'resource_path_traversal'):
                        self._refusals += 1
                    raise
                result = getattr(self, '_' + tool)(arguments)
                self.verify_inputs()
                return result
            except ToolInputError:
                raise
            except BaseException:
                self._failed = True
                raise

    def _read_text(self, args):
        value = super()._read_text(args)
        self._delivered[args['path']] = _merge(self._delivered.get(args['path'], []), value['offset'], value['next_offset'])
        self._delivery_events.append({'tool': 'read_text', 'path': value['path'], 'sha256': value['sha256'],
                                      'offset': value['offset'], 'next_offset': value['next_offset']})
        return value

    def _read_page_image(self, args):
        value = super()._read_page_image(args)
        self._images_delivered.add(args['path'])
        self._delivery_events.append({'tool': 'read_page_image', 'path': value['path'], 'sha256': value['sha256']})
        return value

    def source_access_receipt(self):
        self.verify_inputs()
        if self.synthetic:
            return {'kind': 'P3_FOCUSED_SYNTHETIC_DELIVERY_039_v1', 'synthetic': True, 'scientific_delivery': False, 'delivery_events': copy.deepcopy(self._delivery_events)}
        papers = []
        for pid, paper in self.papers.items():
            full = self._complete(paper['full_text']['path'])
            pages = [p['page'] for p in paper['pages'] if self._complete(p['text']['path'])]
            images = [p['page'] for p in paper['pages'] if p['image']['path'] in self._images_delivered]
            complete = (full or len(pages) == len(paper['pages'])) and set(PAPERS[pid]['images']).issubset(images)
            papers.append({'source_id': pid, 'pdf_sha256': paper['pdf']['sha256'],
                           'full_text_delivered': full, 'page_texts_delivered': pages,
                           'page_images_delivered': images, 'required_page_images': list(PAPERS[pid]['images']),
                           'required_source_delivery_complete': complete})
        missing = [p for p in self.required_texts if not self._complete(p)]
        return {'kind': 'P3_FOCUSED_SOURCE_DELIVERY_039_v1',
                'scientific_manifest_sha256': self.scientific_manifest_sha256,
                'packet_manifest_sha256': self.manifest_sha256,
                'descriptor_sha256': self.scope_descriptor_sha256,
                'missing_required_texts': missing, 'papers': papers,
                'all_required_delivery_complete': not missing and all(p['required_source_delivery_complete'] for p in papers),
                'text_ranges_delivered': {p: [list(pair) for pair in rs] for p, rs in sorted(self._delivered.items())},
                'delivery_events': copy.deepcopy(self._delivery_events),
                'meaning': 'Measured complete-file hashes and tool-returned content coverage; not proof of comprehension or scientific correctness.'}

    def _source_access_receipt(self, args):
        return self.source_access_receipt()

    def resource_path_refusal_receipt(self):
        return {'kind': 'P3_RESOURCE_PATH_REFUSALS_039_v1', 'calls_refused': self._refusals,
                'shared_recoverable_error_count': self.recoverable_input_errors,
                'shared_recoverable_error_ceiling': MAX_RECOVERABLE_ERRORS,
                'denied_path_logged_or_individually_hashed': False,
                'whole_request_digests_include_arguments': True, 'denied_resource_access_granted': False}

    def _validate_verdict(self, args):
        if args['applies_to']['scope_id'] != SCOPE_ID:
            raise ToolInputError('verdict_contract')
        _require(args['applies_to']['scientific_manifest_sha256'] == self.scientific_manifest_sha256,
                 'Wrong verdict scientific manifest')
        ids = [row['claim_id'] for row in args['claim_assessments']]
        pairs = [(row['source_id'], row['claim_id']) for row in args['source_comparisons']]
        if sorted(ids) != list(CLAIMS) or sorted(pairs) != [('CHV79', 'R1'), ('PK97', 'R6')]:
            raise ToolInputError('verdict_contract')
        receipt = self.source_access_receipt()
        access = {p['source_id']: p['required_source_delivery_complete'] for p in receipt['papers']}
        for row in args['source_comparisons']:
            if row['assessment'] != 'UNRESOLVED' and not access[row['source_id']]:
                raise ToolInputError('delivery_incomplete')
            if row['assessment'] != 'UNRESOLVED':
                pdf = self.papers[row['source_id']]['pdf']
                if pdf not in row['evidence']:
                    raise ToolInputError('verdict_contract')
        if args['verdict'] != 'SUSPEND_FOR_DEPENDENCY' and not receipt['all_required_delivery_complete']:
            raise ToolInputError('delivery_incomplete')
        if args['verdict'] == 'GO' and (any(row['assessment'] == 'UNRESOLVED' for field in ('claim_assessments', 'source_comparisons') for row in args[field]) or args['missing_dependencies'] or args['required_corrections']):
            raise ToolInputError('verdict_contract')
        if args['verdict'] == 'SUSPEND_FOR_DEPENDENCY' and not args['missing_dependencies']:
            raise ToolInputError('verdict_contract')
        if args['verdict'] == 'REVISE_ONCE' and not args['required_corrections']:
            raise ToolInputError('verdict_contract')
        recommendation = args['recommendation']
        if recommendation['route'] == 'SPECIFY_SUCCESSOR_COMPARISON':
            if not all(recommendation[f] for f in ('future_decision', 'acquired_knowledge', 'matched_information_and_interactions', 'disconfirmation', 'unresolved_semantics')):
                raise ToolInputError('verdict_contract')
        if args['verdict'] == 'SUSPEND_FOR_DEPENDENCY' and recommendation['route'] != 'RESOLVE_DEPENDENCY':
            raise ToolInputError('verdict_contract')
        for field in ('claim_assessments', 'source_comparisons'):
            for row in args[field]:
                for ref in row['evidence']:
                    self._reference(ref)
                    if self._files[ref['path']]['kind'] == 'text' and not self._complete(ref['path']):
                        raise ToolInputError('delivery_incomplete')

    def _submit_verdict(self, args):
        evidence = {ref['path']: self._reference(ref) for field in ('claim_assessments', 'source_comparisons') for row in args[field] for ref in row['evidence']}
        body = {'schema_version': 1, 'kind': 'P3_FOCUSED_REVIEW_VERDICT_039_v1',
                'received_utc': datetime.now(timezone.utc).isoformat(),
                'packet_manifest_sha256': self.manifest_sha256,
                'actual_evidence_sha256': evidence, 'source_delivery_receipt': self.source_access_receipt(),
                'reviewer_verdict': copy.deepcopy(args),
                'broker_role': 'transport, schema and integrity only; no scientific verdict generated',
                'excluded_inferences': ['candidate efficacy', 'global novelty clearance', 'PROGRAMME approval', 'integrated N1-N5 guarantee']}
        encoded = (json.dumps(body, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')
        _require(len(encoded) <= 1024 * 1024, 'Verdict exceeds output bound')
        self.verify_inputs()
        fd = os.open(VERDICT_NAME, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                     0o400, dir_fd=self._output_fd)
        try:
            with os.fdopen(fd, 'wb', closefd=False) as stream:
                stream.write(encoded)
                stream.flush()
                os.fsync(fd)
        finally:
            os.close(fd)
        os.fsync(self._output_fd)
        fd = os.open(VERDICT_NAME, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=self._output_fd)
        try:
            before = os.fstat(fd)
            _require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size == len(encoded), 'Verdict output identity/size differs')
            stored = b''
            while len(stored) <= len(encoded):
                piece = os.read(fd, 65536)
                if not piece:
                    break
                stored += piece
            _require(original._identity(before) == original._identity(os.fstat(fd)) and stored == encoded, 'Stored verdict bytes differ')
        finally:
            os.close(fd)
        self._verdict_written = True
        return {'accepted': True, 'output_id': VERDICT_NAME, 'sha256': hashlib.sha256(stored).hexdigest(), 'bytes': len(stored)}


_object = original._object
_STRING = {'type': 'string', 'minLength': 1, 'maxLength': 30000}
_OPTIONAL_TEXT = {'type': 'string', 'minLength': 0, 'maxLength': 30000}
_PATH = {'type': 'string', 'minLength': 1, 'maxLength': 1024}
_SHA = {'type': 'string', 'pattern': '^[0-9a-f]{64}$'}
_EVIDENCE = _object({'path': _PATH, 'sha256': _SHA})
_TEXT_LIST = {'type': 'array', 'items': _STRING, 'maxItems': 100}
_COMMON_ASSESSMENT = {'proposition': _STRING, 'assessment': {'type': 'string', 'enum': list(ASSESSMENTS)},
                      'analysis': _STRING, 'evidence': {'type': 'array', 'items': _EVIDENCE, 'minItems': 1, 'maxItems': 100}}
TOOL_SCHEMAS = {
    'read_text': _object({'path': _PATH, 'offset': {'type': 'integer', 'minimum': 0, 'maximum': original.MAX_FILE_BYTES},
                          'length': {'type': 'integer', 'minimum': 1, 'maximum': 100000}}),
    'read_page_image': _object({'path': _PATH}),
    'hash_file': _object({'path': _PATH}),
    'source_access_receipt': _object({}),
    'submit_verdict': _object({
        'verdict': {'type': 'string', 'enum': list(VERDICTS)},
        'applies_to': _object({'scope_id': {'type': 'string', 'enum': [SCOPE_ID]}, 'scientific_manifest_sha256': _SHA}),
        'summary': _STRING,
        'claim_assessments': {'type': 'array', 'minItems': 7, 'maxItems': 7,
                             'items': _object({'claim_id': {'type': 'string', 'enum': list(CLAIMS)}, 'premises': {**_TEXT_LIST, 'minItems': 1}, **_COMMON_ASSESSMENT})},
        'source_comparisons': {'type': 'array', 'minItems': 2, 'maxItems': 2,
                              'items': _object({'source_id': {'type': 'string', 'enum': list(PAPERS)},
                                                'claim_id': {'type': 'string', 'enum': ['R1', 'R6']}, **_COMMON_ASSESSMENT})},
        'recommendation': _object({'route': {'type': 'string', 'enum': ['SPECIFY_SUCCESSOR_COMPARISON', 'RETURN_TO_GENERATION', 'RESOLVE_DEPENDENCY']},
                                    'reason': _STRING, **{field: _OPTIONAL_TEXT for field in ('future_decision', 'acquired_knowledge', 'matched_information_and_interactions', 'disconfirmation', 'unresolved_semantics')}}),
        'strongest_objections': _TEXT_LIST, 'missing_dependencies': _TEXT_LIST, 'required_corrections': _TEXT_LIST})}


def dynamic_tool_specs():
    descriptions = {
        'read_text': 'Read exact manifested UTF-8 text by character offset and return measured whole-file SHA-256. Read governing files in order. Full source text delivery is tracked.',
        'read_page_image': 'Deliver one manifested PNG page from a supplied paper; measured SHA-256 and actual image bytes are returned.',
        'hash_file': 'Compute SHA-256 of complete manifested bytes. Hashing alone is not a reading receipt.',
        'source_access_receipt': 'Report actual text-range and paper-image delivery and missing required input; this does not certify comprehension.',
        'submit_verdict': 'Submit one R1-R7 analytical review with two supplied-method comparisons; never candidate efficacy or programme approval. Substantive verdicts require complete source delivery.'}
    suffix = ' At most eight ordinary argument corrections are permitted after whole-packet revalidation; integrity and authority failures stop this instance.'
    return [{'type': 'function', 'name': name, 'description': descriptions[name] + suffix, 'inputSchema': copy.deepcopy(schema)} for name, schema in TOOL_SCHEMAS.items()]
