"""Offline boundary tests using synthetic texts/papers, never a scientific review."""
from pathlib import Path
import hashlib
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import p3_focused_review_broker_039 as broker
import p3_focused_review_protocol_039 as protocol


def sha(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, indent=2) + '\n').encode()


class Packet:
    def __init__(self, root):
        self.root = root / 'packet'
        self.output = root / 'output'
        self.root.mkdir()
        self.output.mkdir()
        self.files = {}
        self.paper_constants = {}
        public = list(broker.GOVERNING) + ['frozen_spec.md']
        inputs = [self.add(path, 'text', ('Synthetic input ' + path + '\n').encode()) for path in public]
        papers, private = [], []
        for pid, claim in [('CHV79', 'R1'), ('PK97', 'R6')]:
            pdf = self.add('private/' + pid + '.pdf', 'binary', ('Synthetic PDF fixture ' + pid).encode())
            private.append(pdf)
            full = self.add('reading/' + pid + '/full.txt', 'text', ('abcdefghijklmnopqrstuv\n' + pid).encode())
            pages = []
            for n in (1, 2):
                pages.append({'page': n,
                              'text': self.add('reading/' + pid + '/%s.txt' % n, 'text', ('page %s %s' % (pid, n)).encode()),
                              'image': self.add('reading/' + pid + '/%s.png' % n, 'image', b'\x89PNG\r\n\x1a\n' + pid.encode() + bytes([n]))})
            papers.append({'id': pid, 'pdf': pdf, 'full_text': full, 'pages': pages})
            self.paper_constants[pid] = {'sha256': pdf['sha256'], 'claim_id': claim, 'pages': 2, 'images': (2,)}
        science = {'claim_ids': list(broker.CLAIMS), 'inputs': inputs, 'private_sources': private}
        science_ref = self.add(broker.SCIENTIFIC_MANIFEST_PATH, 'text', json_bytes(science))
        self.science_sha = science_ref['sha256']
        self.scope = {'schema_version': 1, 'scope_id': broker.SCOPE_ID,
                      'scientific_manifest': science_ref, 'required_texts': public + [broker.SCIENTIFIC_MANIFEST_PATH], 'papers': papers}
        self.add(broker.SCOPE_PATH, 'text', json_bytes(self.scope))
        self.seal()

    def add(self, path, kind, data):
        target = self.root / path
        target.parent.mkdir(exist_ok=True, parents=True)
        target.write_bytes(data)
        self.files[path] = {'path': path, 'sha256': sha(data), 'kind': kind}
        return {'path': path, 'sha256': sha(data)}

    def seal(self):
        raw = json_bytes({'schema_version': 1, 'files': list(self.files.values())})
        (self.root / 'BROKER_MANIFEST.json').write_bytes(raw)
        self.manifest_sha = sha(raw)

    def open(self):
        return broker.ReviewBroker(self.root, manifest_sha256=self.manifest_sha, output_root=self.output)

    def evidence(self, path):
        return {'path': path, 'sha256': self.files[path]['sha256']}

    def verdict(self):
        common = {'proposition': 'Synthetic fixture proposition, not science.',
                  'assessment': 'SUPPORTED_WITH_SCOPE', 'analysis': 'Synthetic fixture analysis only.',
                  'evidence': [self.evidence('frozen_spec.md')]}
        rows = [{'claim_id': cid, 'premises': ['Synthetic fixture premise.'], **common} for cid in broker.CLAIMS]
        sources = [{'source_id': p['id'], 'claim_id': self.paper_constants[p['id']]['claim_id'],
                    **{**common, 'evidence': [p['pdf']]}} for p in self.scope['papers']]
        return {'verdict': 'GO', 'applies_to': {'scope_id': broker.SCOPE_ID, 'scientific_manifest_sha256': self.science_sha},
                'summary': 'Synthetic fixture review, never a scientific verdict.', 'claim_assessments': rows,
                'source_comparisons': sources,
                'recommendation': {'route': 'RETURN_TO_GENERATION', 'reason': 'Fixture route.',
                                   **{f: '' for f in ('future_decision', 'acquired_knowledge', 'matched_information_and_interactions', 'disconfirmation', 'unresolved_semantics')}},
                'strongest_objections': [], 'missing_dependencies': [], 'required_corrections': []}

    def deliver(self, b, *, images=True):
        for path in self.scope['required_texts']:
            b.dispatch('read_text', {'path': path, 'offset': 0, 'length': 100000})
        for paper in self.scope['papers']:
            b.dispatch('read_text', {'path': paper['full_text']['path'], 'offset': 0, 'length': 100000})
            if images:
                b.dispatch('read_page_image', {'path': paper['pages'][1]['image']['path']})


class FocusedBrokerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.packet = Packet(Path(self.tmp.name))
        self.mock_papers = patch.dict(broker.PAPERS, self.packet.paper_constants, clear=True)
        self.mock_papers.start()

    def tearDown(self):
        self.mock_papers.stop()
        self.tmp.cleanup()

    def test_complete_delivery_admits_one_scoped_fixture_output(self):
        with self.packet.open() as b:
            self.packet.deliver(b)
            receipt = b.source_access_receipt()
            self.assertTrue(receipt['all_required_delivery_complete'])
            result = b.dispatch('submit_verdict', self.packet.verdict())
            raw = (self.packet.output / broker.VERDICT_NAME).read_bytes()
            self.assertEqual(result['sha256'], sha(raw))
            body = json.loads(raw)
            self.assertEqual(body['reviewer_verdict'], self.packet.verdict())
            self.assertEqual(body['source_delivery_receipt']['papers'][0]['pdf_sha256'], self.packet.paper_constants['CHV79']['sha256'])
            self.assertNotIn('text', body['source_delivery_receipt']['delivery_events'][0])
            with self.assertRaises(broker.BrokerError):
                b.dispatch('submit_verdict', self.packet.verdict())

    def test_hashing_never_satisfies_reading(self):
        with self.packet.open() as b:
            for path in self.packet.files:
                b.dispatch('hash_file', {'path': path})
            self.assertFalse(b.source_access_receipt()['all_required_delivery_complete'])
            with self.assertRaises(broker.ToolInputError) as error:
                b.dispatch('submit_verdict', self.packet.verdict())
            self.assertEqual(error.exception.code, 'delivery_incomplete')
            self.assertFalse((self.packet.output / broker.VERDICT_NAME).exists())

    def test_text_gap_and_missing_images_do_not_count_as_complete(self):
        with self.packet.open() as b:
            self.packet.deliver(b, images=False)
            self.assertFalse(b.source_access_receipt()['all_required_delivery_complete'])
            path = self.packet.scope['papers'][0]['full_text']['path']
            b._delivered[path] = []  # Test-only reset of synthetic delivery state.
            b.dispatch('read_text', {'path': path, 'offset': 0, 'length': 5})
            b.dispatch('read_text', {'path': path, 'offset': 6, 'length': 100000})
            self.assertFalse(b.source_access_receipt()['papers'][0]['full_text_delivered'])
            b.dispatch('read_text', {'path': path, 'offset': 5, 'length': 1})
            self.assertTrue(b.source_access_receipt()['papers'][0]['full_text_delivered'])

    def test_governing_order_precedes_other_source_access(self):
        with self.packet.open() as b:
            with self.assertRaises(broker.ToolInputError) as error:
                b.dispatch('read_text', {'path': 'frozen_spec.md', 'offset': 0, 'length': 100000})
            self.assertEqual(error.exception.code, 'governing_read_order')
            self.packet.deliver(b)
            self.assertTrue(b.source_access_receipt()['all_required_delivery_complete'])

    def test_traversal_refusal_preserves_original_guard_cause_and_recovers(self):
        with self.packet.open() as b:
            with self.assertRaises(broker.ToolInputError) as error:
                b.dispatch('read_text', {'path': '../secret', 'offset': 0, 'length': 10})
            self.assertEqual(error.exception.code, 'resource_path_traversal')
            self.assertIsInstance(error.exception.__cause__, broker.BrokerError)
            tb = error.exception.__cause__.__traceback__
            codes = []
            while tb:
                codes.append(tb.tb_frame.f_code)
                tb = tb.tb_next
            self.assertIn(broker._path.__code__, codes)
            self.packet.deliver(b)

    def test_wrong_digest_is_terminal_even_alongside_bad_schema(self):
        with self.packet.open() as b:
            value = self.packet.verdict()
            value['summary'] = ''
            value['claim_assessments'][0]['evidence'][0]['sha256'] = '0' * 64
            with self.assertRaises(broker.BrokerError):
                b.dispatch('submit_verdict', value)
            with self.assertRaises(broker.BrokerError):
                b.dispatch('hash_file', {'path': 'frozen_spec.md'})

    def test_packet_mutation_is_terminal_and_never_ordinary_feedback(self):
        with self.packet.open() as b:
            (self.packet.root / 'frozen_spec.md').write_text('tampered')
            with self.assertRaises(broker.BrokerError):
                b.dispatch('read_text', {'path': '../bad', 'offset': 0, 'length': 100})
            self.assertEqual(b.recoverable_input_errors, 0)

    def test_linked_inputs_are_refused(self):
        path = self.packet.root / 'frozen_spec.md'
        data = path.read_bytes()
        other = self.packet.root.parent / 'outside.txt'
        other.write_bytes(data)
        path.unlink()
        path.symlink_to(other)
        with self.assertRaises(broker.BrokerError):
            self.packet.open()

    def test_duplicate_claim_or_foreign_source_claim_pair_is_refused(self):
        with self.packet.open() as b:
            self.packet.deliver(b)
            value = self.packet.verdict()
            value['claim_assessments'][1]['claim_id'] = 'R1'
            with self.assertRaises(broker.ToolInputError):
                b.dispatch('submit_verdict', value)
            value = self.packet.verdict()
            value['source_comparisons'][0]['claim_id'] = 'R6'
            with self.assertRaises(broker.ToolInputError):
                b.dispatch('submit_verdict', value)

    def test_no_observer_or_arbitrary_execution_tool(self):
        self.assertEqual(set(broker.TOOL_SCHEMAS), {'read_text', 'read_page_image', 'hash_file', 'source_access_receipt', 'submit_verdict'})
        with self.packet.open() as b:
            with self.assertRaises(broker.BrokerError):
                b.dispatch('run_observer_audit', {})

    def test_ninth_ordinary_error_stops_instance(self):
        with self.packet.open() as b:
            for _ in range(8):
                with self.assertRaises(broker.ToolInputError) as error:
                    b.dispatch('read_text', {'path': broker.GOVERNING[0], 'offset': 0, 'length': 0})
                self.assertEqual(error.exception.code, 'integer_bounds')
            with self.assertRaises(broker.BrokerError):
                b.dispatch('read_text', {'path': broker.GOVERNING[0], 'offset': 0, 'length': 0})

    def test_suspend_retains_unread_dependency_without_fabricating_receipt(self):
        with self.packet.open() as b:
            for path in self.packet.scope['required_texts']:
                b.dispatch('read_text', {'path': path, 'offset': 0, 'length': 100000})
            value = self.packet.verdict()
            value['verdict'] = 'SUSPEND_FOR_DEPENDENCY'
            value['missing_dependencies'] = ['Paper delivery is incomplete in this synthetic fixture.']
            value['recommendation']['route'] = 'RESOLVE_DEPENDENCY'
            for row in value['source_comparisons']:
                row['assessment'] = 'UNRESOLVED'
            b.dispatch('submit_verdict', value)
            output = json.loads((self.packet.output / broker.VERDICT_NAME).read_bytes())
            self.assertFalse(output['source_delivery_receipt']['all_required_delivery_complete'])

    def test_protocol_authentication_and_replay_stop_without_extra_dispatch(self):
        with self.packet.open() as b:
            boundary = protocol.DynamicToolBoundary(b, thread_id='t', turn_id='u')
            request = {'id': 1, 'method': 'item/tool/call', 'params': {'arguments': {'path': broker.GOVERNING[0], 'offset': 0, 'length': 100000}, 'callId': 'c', 'threadId': 't', 'turnId': 'u', 'tool': 'read_text'}}
            boundary.handle(json_bytes(request))
            with self.assertRaises(protocol.ProtocolStop):
                boundary.handle(json_bytes(request))
            self.assertEqual(len(b._delivery_events), 1)
            self.assertTrue(boundary.stopped)


class SyntheticBoundaryTests(unittest.TestCase):
    def test_synthetic_scope_has_no_science_or_verdict_authority(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            packet, output = root / 'packet', root / 'out'
            packet.mkdir(); output.mkdir()
            raw = b'Finite synthetic canary only.\n'
            (packet / 'CANARY.txt').write_bytes(raw)
            manifest = json_bytes({'schema_version': 1, 'files': [{'path': 'CANARY.txt', 'kind': 'text', 'sha256': sha(raw)}]})
            (packet / 'BROKER_MANIFEST.json').write_bytes(manifest)
            with broker.ReviewBroker(packet, manifest_sha256=sha(manifest), output_root=output, synthetic=True) as b:
                self.assertEqual(b.dispatch('read_text', {'path': 'CANARY.txt', 'offset': 0, 'length': 100})['text'], raw.decode())
                with self.assertRaises(broker.BrokerError):
                    b.dispatch('submit_verdict', {})
                self.assertFalse(list(output.iterdir()))


if __name__ == '__main__':
    unittest.main()
