#!/usr/bin/env python3
"""Synthetic filesystem checks; no Git, native client, auth or network use."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock


HERE = Path(__file__).absolute().parent
SPEC = importlib.util.spec_from_file_location("collector031", HERE.parent / "scripts" / "publish_review030_evidence.py")
c = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(c)


class EvidenceCollectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="collector031_", dir=HERE)
        self.root = Path(self.temp.name) / "project"
        self.root.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def write(self, relative, raw=b"{}\n"):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        return path

    def run_collection(self):
        result = c.collect(self.root)
        archive = self.root / result["archive_relative_path"]
        index = json.loads((archive / "INDEX.json").read_bytes())
        manifest = json.loads((archive / "MANIFEST.json").read_bytes())
        self.assertEqual(result["evidence_digest"], c.sha256((archive / "INDEX.json").read_bytes()))
        for row in manifest["files"]:
            raw = (archive / row["path"]).read_bytes()
            self.assertEqual(c.sha256(raw), row["sha256"])
            self.assertEqual(len(raw), row["bytes"])
        self.assertEqual(sorted(str(path.relative_to(self.root)) for path in archive.rglob("*")
                                if path.is_file()), result["tracked_paths"])
        return result, archive, index

    def entry(self, index, path):
        return next(row for row in index["sources"] if row["source_path"] == path)

    def test_genuinely_missing_report_creates_index_and_manifest(self):
        result, archive, index = self.run_collection()
        self.assertEqual(result["status_summary"]["collection_status"], "NO_ALLOWED_SOURCE_FILES_PRESENT")
        self.assertEqual(len(result["tracked_paths"]), 2)
        self.assertTrue(all(row["status"] == "MISSING" for row in index["sources"]))
        self.assertFalse((archive / "files").exists())

    def test_partial_kernel_report_has_no_fabricated_main_report(self):
        raw = b'{ "status": "FAILED", "no_native_start": true }\r\n'
        self.write(c.KERNEL + "REPORT.json", raw)
        result, archive, index = self.run_collection()
        self.assertEqual(result["status_summary"]["main_report"], "MISSING")
        self.assertEqual(result["status_summary"]["kernel_report"], "PRESENT")
        self.assertEqual((archive / "files" / (c.KERNEL + "REPORT.json")).read_bytes(), raw)
        self.assertFalse((archive / "files" / (c.MAIN + "REPORT.json")).exists())

    def test_verdict_preserved_even_when_run_failed_without_admission(self):
        self.write(c.MAIN + "REPORT.json", b'{"status":"STOPPED_WITHOUT_COMPLETED_REVIEW"}\n')
        raw = b'{"candidate":"reject","reason":"fixture"}\n'
        self.write(c.MAIN + "science_output/REVIEW_VERDICT.json", raw)
        result, archive, index = self.run_collection()
        self.assertEqual(result["status_summary"]["verdict"], "PRESENT")
        self.assertEqual(result["status_summary"]["verdict_execution_admission"], "NOT_EVALUATED_BY_COLLECTOR")
        self.assertEqual((archive / "files" / (c.MAIN + "science_output/REVIEW_VERDICT.json")).read_bytes(), raw)

    def test_fixed_workflow_files_allow_missing030_to_be_explained(self):
        for name in ("WORKFLOW_REPORT.json", "LAUNCH_RESERVED.json", "LAUNCH_OUTCOME.json"):
            self.write(c.WORKFLOW + name)
        result, archive, index = self.run_collection()
        self.assertEqual(result["status_summary"]["collection_status"], "WORKFLOW_EVIDENCE_ONLY_NO_030_RECEIPTS")
        self.assertEqual(result["status_summary"]["original030_file_count"], 0)
        self.assertEqual(result["status_summary"]["present_file_count"], 3)

    def test_repeat_is_identical_and_does_not_write_sources(self):
        source = self.write(c.MAIN + "REPORT.json", b'{"fixture":true}\n')
        before = source.stat()
        first, archive, index = self.run_collection()
        archive_mtimes = {path: (self.root / path).stat().st_mtime_ns for path in first["tracked_paths"]}
        second, _, _ = self.run_collection()
        self.assertEqual(first, second)
        self.assertEqual(archive_mtimes, {path: (self.root / path).stat().st_mtime_ns for path in second["tracked_paths"]})
        self.assertEqual(before.st_mtime_ns, source.stat().st_mtime_ns)

    def test_later_real_report_makes_new_archive_keeps_old(self):
        first, first_archive, _ = self.run_collection()
        self.write(c.MAIN + "REPORT.json")
        second, second_archive, _ = self.run_collection()
        self.assertNotEqual(first["evidence_digest"], second["evidence_digest"])
        self.assertTrue(first_archive.exists())
        self.assertTrue(second_archive.exists())

    def test_only_named_files_read_and_no_recursive_discovery(self):
        self.write(c.MAIN + "REPORT.json")
        blocked = [c.MAIN + "science_native/auth.json", c.MAIN + "science_output/SECRET.txt",
                   c.MAIN + "science_native/trace.jsonl", c.WORKFLOW + "CONSOLE.txt",
                   "delivery/private_paper.pdf", "delivery/REPORT.json"]
        for name in blocked:
            self.write(name, b"SYNTHETIC_DO_NOT_COLLECT")
        original_open = os.open
        seen = []
        def record_open(path, *args, **kwargs):
            seen.append(str(path))
            return original_open(path, *args, **kwargs)
        with mock.patch.object(c.os, "open", side_effect=record_open):
            result, archive, index = self.run_collection()
        self.assertNotIn("auth.json", seen)
        self.assertNotIn("CONSOLE.txt", seen)
        self.assertNotIn("private_paper.pdf", seen)
        self.assertFalse(any(b"SYNTHETIC_DO_NOT_COLLECT" in (self.root / path).read_bytes()
                             for path in result["tracked_paths"]))

    def test_final_file_symlink_refused_without_read(self):
        outside = Path(self.temp.name) / "outside"
        outside.write_bytes(b"SYNTHETIC_PRIVATE")
        source = self.root / (c.MAIN + "REPORT.json")
        source.parent.mkdir(parents=True)
        source.symlink_to(outside)
        result, archive, index = self.run_collection()
        self.assertEqual(self.entry(index, c.MAIN + "REPORT.json")["reason_code"], "symlink_refused")
        self.assertEqual(result["status_summary"]["main_report"], "REFUSED")

    def test_ancestor_symlink_refused_without_read(self):
        outside = Path(self.temp.name) / "outside"
        outside.mkdir()
        (outside / "REPORT.json").write_bytes(b"SYNTHETIC_PRIVATE")
        (self.root / "delivery").mkdir()
        (self.root / c.MAIN.rstrip("/")).symlink_to(outside, target_is_directory=True)
        result, archive, index = self.run_collection()
        self.assertEqual(result["status_summary"]["main_report"], "REFUSED")

    def test_hardlinked_alias_refused(self):
        source = self.write(c.MAIN + "REPORT.json", b"SYNTHETIC_PRIVATE")
        os.link(source, Path(self.temp.name) / "alias")
        _, _, index = self.run_collection()
        self.assertEqual(self.entry(index, c.MAIN + "REPORT.json")["reason_code"], "multiple_hardlinks_refused")

    def test_fifo_refused_before_open(self):
        source = self.root / (c.MAIN + "REPORT.json")
        source.parent.mkdir(parents=True)
        os.mkfifo(source)
        _, _, index = self.run_collection()
        self.assertEqual(self.entry(index, c.MAIN + "REPORT.json")["reason_code"], "not_regular_file")

    def test_group_writable_source_refused(self):
        source = self.write(c.MAIN + "REPORT.json")
        source.chmod(0o664)
        _, _, index = self.run_collection()
        self.assertEqual(self.entry(index, c.MAIN + "REPORT.json")["reason_code"], "group_or_world_writable_file")

    def test_size_limit_refused_without_copy(self):
        self.write(c.MAIN + "REPORT.sha256", b"A" * 66)
        _, archive, index = self.run_collection()
        self.assertEqual(self.entry(index, c.MAIN + "REPORT.sha256")["reason_code"], "file_byte_limit_exceeded")
        self.assertFalse((archive / "files" / (c.MAIN + "REPORT.sha256")).exists())

    def test_source_mutation_during_read_discards_bytes(self):
        source = self.write(c.MAIN + "REPORT.json", b"A" * 20)
        original = os.read
        mutated = False
        def mutate(fd, size):
            nonlocal mutated
            raw = original(fd, size)
            if not mutated:
                source.write_bytes(b"B" * 21)
                mutated = True
            return raw
        with mock.patch.object(c.os, "read", side_effect=mutate):
            _, archive, index = self.run_collection()
        self.assertEqual(self.entry(index, c.MAIN + "REPORT.json")["reason_code"], "source_changed_during_collection")
        self.assertFalse((archive / "files" / (c.MAIN + "REPORT.json")).exists())

    def test_source_replacement_before_final_check_discards_bytes(self):
        source = self.write(c.MAIN + "REPORT.json", b"{}\n")
        original = c._stat_fixed
        def replace(root_fd, relative):
            if relative == c.MAIN + "REPORT.json":
                source.unlink()
                source.write_bytes(b"{\"replacement\":true}\n")
            return original(root_fd, relative)
        with mock.patch.object(c, "_stat_fixed", side_effect=replace):
            _, _, index = self.run_collection()
        self.assertEqual(self.entry(index, c.MAIN + "REPORT.json")["reason_code"], "source_changed_during_collection")

    def test_existing_archive_changed_file_is_preserved_and_refused(self):
        result, archive, index = self.run_collection()
        target = archive / "INDEX.json"
        target.write_bytes(b"CHANGED")
        with self.assertRaises(c.CollectionError):
            c.collect(self.root)
        self.assertEqual(target.read_bytes(), b"CHANGED")

    def test_archive_symlink_refused_without_outside_write(self):
        outside = Path(self.temp.name) / "outside"
        outside.mkdir()
        (self.root / "artifacts").symlink_to(outside, target_is_directory=True)
        with self.assertRaises((c.CollectionError, OSError)):
            c.collect(self.root)
        self.assertEqual(list(outside.iterdir()), [])

    def test_relative_or_parent_step_root_refused(self):
        with self.assertRaises(c.CollectionError):
            c.collect(Path("relative-project"))
        with self.assertRaises(c.CollectionError):
            c.collect(self.root / ".." / "project")

    def test_project_root_symlink_refused(self):
        alias = Path(self.temp.name) / "alias"
        alias.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(OSError):
            c.collect(alias)


if __name__ == "__main__":
    unittest.main(verbosity=2)
