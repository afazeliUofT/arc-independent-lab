"""Evidence boundary checks; these do not execute a native/model client."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('publisher040_fixture', ROOT / 'scripts/publish_review040_evidence.py')
p = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(p)


class PublisherTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.folder = self.root / p.MAIN
        self.folder.mkdir(parents=True)

    def test_fixed_allowlist_excludes_private_and_raw_streams(self):
        (self.folder / 'REPORT.json').write_text('{"status":"fixture"}\n')
        (self.folder / 'raw_native_stream.json').write_text('{"secret":"fixture"}\n')
        (self.folder / 'paper.pdf').write_bytes(b'%PDF-private fixture')
        result = p.collect(self.root)
        self.assertFalse(any('raw_native_stream' in path or '.pdf' in path for path in result['tracked_paths']))
        self.assertEqual(p.collect(self.root), result)
        self.assertTrue(result['status_summary']['missing_files_do_not_establish_no_execution'])

    def test_symlink_and_malformed_json_refused_without_copy(self):
        outside = self.root / 'private.txt'
        outside.write_text('PRIVATE SOURCE')
        (self.folder / 'REPORT.json').symlink_to(outside)
        (self.folder / 'ATTEMPT.json').write_text('not JSON private content')
        result = p.collect(self.root)
        index = json.loads((self.root / result['archive_relative_path'] / 'INDEX.json').read_text())
        rows = {row['source_path']: row for row in index['sources']}
        self.assertEqual(rows[p.MAIN + 'REPORT.json']['status'], 'REFUSED')
        self.assertEqual(rows[p.MAIN + 'ATTEMPT.json']['status'], 'REFUSED')
        self.assertFalse(any(path.endswith('/REPORT.json') or path.endswith('/ATTEMPT.json') for path in result['tracked_paths']))

    def test_bulk_private_passage_refused_with_verdict_kept_private(self):
        text = ' '.join('word' + str(i) for i in range(250))
        for source_id in ('CHV79', 'PK97'):
            path = self.root / 'delivery/P3_FOCUSED_REVIEW_PACKET_040/reading' / source_id / 'full_text.txt'
            path.parent.mkdir(parents=True)
            path.write_text(text)
        path = self.folder / 'science_output/REVIEW_VERDICT.json'
        path.parent.mkdir()
        path.write_text(json.dumps({'summary': text}))
        original = path.read_bytes()
        result = p.collect(self.root)
        self.assertEqual(path.read_bytes(), original)
        self.assertFalse(any(name.endswith('/REVIEW_VERDICT.json') for name in result['tracked_paths']))
        index = json.loads((self.root / result['archive_relative_path'] / 'INDEX.json').read_text())
        row = next(row for row in index['sources'] if row['source_path'].endswith('/REVIEW_VERDICT.json'))
        self.assertEqual(row['status'], 'REFUSED')
        self.assertTrue(row['private_source_bulk_copy_guard']['detected'])

    def test_missing_controller_report_preserves_partial_attempt(self):
        (self.folder / 'ATTEMPT.json').write_text('{"reserved":true}\n')
        result = p.collect(self.root)
        self.assertEqual(result['status_summary']['collection_status'], 'PARTIAL_EVIDENCE_WITHOUT_MAIN_REPORT')
        self.assertIn('NEVER_INFER_ZERO', result['status_summary']['actual_usage'])
        self.assertTrue(any(path.endswith('/ATTEMPT.json') for path in result['tracked_paths']))


if __name__ == '__main__':
    unittest.main()
