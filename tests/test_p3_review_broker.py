"""Synthetic adversarial engineering checks, never independent science review."""
import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import p3_review_broker as broker

TEST_ROOT = ROOT / "delivery/p3_broker_tests"
TEST_ROOT.mkdir(parents=True, exist_ok=True)
PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=")


def sha(data):
    return hashlib.sha256(data).hexdigest()


class Fixture:
    def __init__(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="synthetic-", dir=TEST_ROOT)
        self.root = Path(self.temporary.name)
        self.packet = self.root / "packet"
        self.output = self.root / "output"
        self.packet.mkdir()
        self.output.mkdir()
        self.files = {}
        self.add("notes/evidence.txt", "αβγ\nactual evidence\n".encode(), "text")
        self.add("pages/page1.png", PNG, "image")
        self.add("papers/full.pdf", b"%PDF-1.4 synthetic bytes", "binary")
        for path in broker.REVIEW_MANIFESTS.values():
            self.add(path, b'{"scope":"synthetic engineering fixture only"}\n', "text")
        self.freeze()

    def add(self, path, data, kind):
        target = self.packet / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        self.files[path] = {"path": path, "sha256": sha(data), "kind": kind}

    def freeze(self):
        self.manifest = {"schema_version": 1, "files": list(self.files.values())}
        raw = json.dumps(self.manifest).encode()
        (self.packet / "BROKER_MANIFEST.json").write_bytes(raw)
        self.pin = sha(raw)

    def open(self):
        return broker.ReviewBroker(self.packet, manifest_sha256=self.pin, output_root=self.output)

    def verdict(self):
        return {
            "verdict": "SUSPEND_FOR_DEPENDENCY",
            "applies_to": {"scope": "SYNTHETIC TEST ONLY; no scientific review", **{
                field: self.files[path]["sha256"] for field, path in broker.REVIEW_MANIFESTS.items()}},
            "summary": "Synthetic transport test only.",
            "dispositions": [{"subject": subject, "disposition": "synthetic dependency",
                              "reason": "No scientific reviewer runs in this test.",
                              "evidence": [{"path": "notes/evidence.txt",
                                            "sha256": self.files["notes/evidence.txt"]["sha256"]}]}
                             for subject in broker.SUBJECTS],
            "strongest_objections": ["Synthetic transport is not independent review."],
            "missing_dependencies": ["This is a test fixture."], "required_corrections": []}

    def close(self):
        self.temporary.cleanup()


class BrokerBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.f = Fixture()

    def tearDown(self):
        self.f.close()

    def test_actual_text_offsets_hashes_and_page_image(self):
        with self.f.open() as instance:
            text = instance.dispatch("read_text", {"path": "notes/evidence.txt", "offset": 1, "length": 2})
            self.assertEqual(text["text"], "βγ")
            self.assertEqual(text["sha256"], sha((self.f.packet / "notes/evidence.txt").read_bytes()))
            image = instance.dispatch("read_page_image", {"path": "pages/page1.png"})
            self.assertEqual(base64.b64decode(image["data_base64"]), PNG)
            self.assertEqual(image["sha256"], sha(PNG))
            actual = instance.dispatch("hash_file", {"path": "papers/full.pdf"})
            self.assertEqual(actual["sha256"], sha(b"%PDF-1.4 synthetic bytes"))

    def test_traversal_absolute_unmanifested_and_noncanonical_paths(self):
        for value in ("../outside.txt", "/etc/passwd", "notes/../evidence.txt", "notes//evidence.txt",
                      "notes/./evidence.txt", "notes\\evidence.txt", "notes/missing.txt", "notes/evidence.txt\x00"):
            with self.subTest(value=value), self.f.open() as instance:
                with self.assertRaises(broker.BrokerError):
                    instance.dispatch("hash_file", {"path": value})

    def test_boolean_negative_float_and_overlarge_bounds(self):
        for field, value in (("offset", True), ("offset", -1), ("offset", 0.0),
                             ("length", False), ("length", 0), ("length", 100001)):
            with self.subTest(field=field, value=value), self.f.open() as instance:
                arguments = {"path": "notes/evidence.txt", "offset": 0, "length": 5}
                arguments[field] = value
                with self.assertRaises(broker.BrokerError):
                    instance.dispatch("read_text", arguments)

    def test_extra_sha_claim_and_arbitrary_command_destination_denied(self):
        calls = [("hash_file", {"path": "notes/evidence.txt", "sha256": "0" * 64}),
                 ("run_observer_audit", {"command": "touch /tmp/unauthorized"}),
                 ("run_observer_audit", {"receipt": "../arbitrary.json"}),
                 ("exec", {"command": "true"})]
        for tool, arguments in calls:
            with self.subTest(tool=tool, args=arguments), self.f.open() as instance:
                with mock.patch.object(broker.subprocess, "run") as runner:
                    with self.assertRaises(broker.BrokerError):
                        instance.dispatch(tool, arguments)
                    runner.assert_not_called()

    def test_forged_manifest_digest_rejected_before_read_return(self):
        with self.assertRaises(broker.BrokerError):
            broker.ReviewBroker(self.f.packet, manifest_sha256="0" * 64, output_root=self.f.output)

    def test_forged_manifest_file_hash_rejected(self):
        self.f.files["notes/evidence.txt"]["sha256"] = "0" * 64
        self.f.freeze()
        with self.assertRaises(broker.BrokerError):
            self.f.open()

    def test_any_changed_source_invalidates_unrelated_read_and_stops_broker(self):
        with self.f.open() as instance:
            (self.f.packet / "papers/full.pdf").write_bytes(b"changed")
            with self.assertRaises(broker.BrokerError):
                instance.dispatch("read_text", {"path": "notes/evidence.txt", "offset": 0, "length": 5})
            with self.assertRaises(broker.BrokerError):
                instance.dispatch("hash_file", {"path": "notes/evidence.txt"})

    def test_equal_bytes_replaced_identity_detected(self):
        with self.f.open() as instance:
            target = self.f.packet / "notes/evidence.txt"
            saved = target.read_bytes()
            target.unlink()
            target.write_bytes(saved)
            with self.assertRaises(broker.BrokerError):
                instance.dispatch("hash_file", {"path": "notes/evidence.txt"})

    def test_manifest_changed_after_setup_rejected(self):
        with self.f.open() as instance:
            path = self.f.packet / "BROKER_MANIFEST.json"
            path.write_bytes(path.read_bytes() + b" ")
            with self.assertRaises(broker.BrokerError):
                instance.verify_inputs()

    def test_symlink_file_and_directory_denied(self):
        outside = self.f.root / "outside.txt"
        outside.write_bytes((self.f.packet / "notes/evidence.txt").read_bytes())
        target = self.f.packet / "notes/evidence.txt"
        target.unlink()
        target.symlink_to(outside)
        with self.assertRaises(broker.BrokerError):
            self.f.open()
        target.unlink()
        target.write_bytes(outside.read_bytes())
        notes = self.f.packet / "notes"
        notes.rename(self.f.root / "moved-notes")
        notes.symlink_to(self.f.root / "moved-notes", target_is_directory=True)
        with self.assertRaises(broker.BrokerError):
            self.f.open()

    def test_hardlink_and_fifo_denied(self):
        target = self.f.packet / "notes/evidence.txt"
        alias = self.f.root / "alias"
        os.link(target, alias)
        with self.assertRaises(broker.BrokerError):
            self.f.open()
        alias.unlink()
        target.unlink()
        os.mkfifo(target)
        with self.assertRaises(broker.BrokerError):
            self.f.open()

    def test_wrong_resource_kind_and_out_of_range_text_denied(self):
        for tool, args in (("read_page_image", {"path": "notes/evidence.txt"}),
                           ("read_text", {"path": "papers/full.pdf", "offset": 0, "length": 10}),
                           ("read_text", {"path": "notes/evidence.txt", "offset": 500, "length": 10})):
            with self.subTest(tool=tool), self.f.open() as instance:
                with self.assertRaises(broker.BrokerError):
                    instance.dispatch(tool, args)

    def test_dependency_verdict_exact_payload_exclusive_output_and_double_submit_denied(self):
        payload = self.f.verdict()
        with self.f.open() as instance:
            result = instance.dispatch("submit_verdict", payload)
            data = (self.f.output / broker.VERDICT_NAME).read_bytes()
            self.assertEqual(result["sha256"], sha(data))
            self.assertEqual(json.loads(data)["reviewer_verdict"], payload)
            self.assertEqual((self.f.output / broker.VERDICT_NAME).stat().st_mode & 0o777, 0o400)
            with self.assertRaises(broker.BrokerError):
                instance.dispatch("submit_verdict", payload)
            self.assertEqual((self.f.output / broker.VERDICT_NAME).read_bytes(), data)

    def test_preexisting_or_symlink_output_never_overwritten(self):
        sentinel = self.f.root / "sentinel"
        sentinel.write_bytes(b"keep")
        out = self.f.output / broker.VERDICT_NAME
        for symlink in (False, True):
            with self.subTest(symlink=symlink):
                if symlink:
                    out.symlink_to(sentinel)
                else:
                    out.write_bytes(b"keep")
                with self.f.open() as instance:
                    with self.assertRaises(FileExistsError):
                        instance.dispatch("submit_verdict", self.f.verdict())
                self.assertEqual(out.read_bytes(), b"keep")
                self.assertEqual(sentinel.read_bytes(), b"keep")
                out.unlink()

    def test_stored_verdict_corruption_before_readback_is_not_reported_as_success(self):
        original_open = os.open
        corrupted = []
        def open_with_corruption(path, flags, *args, **kwargs):
            if path == broker.VERDICT_NAME and flags & os.O_ACCMODE == os.O_RDONLY:
                output = self.f.output / broker.VERDICT_NAME
                original = output.read_bytes()
                output.chmod(0o600)
                output.write_bytes(b"!" + original[1:])
                corrupted.append(True)
            return original_open(path, flags, *args, **kwargs)
        with self.f.open() as instance, mock.patch.object(broker.os, "open", side_effect=open_with_corruption):
            with self.assertRaisesRegex(broker.BrokerError, "stored-byte verification"):
                instance.dispatch("submit_verdict", self.f.verdict())
        self.assertEqual(corrupted, [True])
        self.assertTrue((self.f.output / broker.VERDICT_NAME).read_bytes().startswith(b"!"))

    def test_verdict_arbitrary_destination_forged_evidence_and_missing_subject_denied(self):
        for mutation in ("destination", "hash", "subject", "scope", "go"):
            with self.subTest(mutation=mutation), self.f.open() as instance:
                payload = self.f.verdict()
                if mutation == "destination":
                    payload["destination"] = str(self.f.root / "escape")
                elif mutation == "hash":
                    payload["dispositions"][0]["evidence"][0]["sha256"] = "0" * 64
                elif mutation == "subject":
                    payload["dispositions"][0]["subject"] = "C2"
                elif mutation == "scope":
                    payload["applies_to"]["original_manifest_sha256"] = "0" * 64
                else:
                    payload["verdict"] = "GO"
                with self.assertRaises(broker.BrokerError):
                    instance.dispatch("submit_verdict", payload)
                self.assertFalse((self.f.output / broker.VERDICT_NAME).exists())

    def test_all_substantive_verdicts_require_actual_auditor(self):
        for verdict in ("GO", "REVISE_ONCE", "KILL"):
            with self.subTest(verdict=verdict):
                payload = self.f.verdict()
                payload["verdict"] = verdict
                with self.f.open() as instance:
                    with self.assertRaises(broker.BrokerError):
                        instance.dispatch("submit_verdict", payload)

    def test_duplicate_manifest_json_keys_and_boolean_schema_rejected(self):
        path = self.f.packet / "BROKER_MANIFEST.json"
        for raw in (b'{"schema_version":1,"schema_version":1,"files":[]}',
                    json.dumps({"schema_version": True, "files": list(self.f.files.values())}).encode()):
            path.write_bytes(raw)
            with self.subTest(raw=raw[:50]), self.assertRaises(broker.BrokerError):
                broker.ReviewBroker(self.f.packet, manifest_sha256=sha(raw), output_root=self.f.output)

    def test_specs_are_independent_copies(self):
        specs = broker.dynamic_tool_specs()
        self.assertEqual({item["name"] for item in specs}, set(broker.TOOL_SCHEMAS))
        specs[0]["inputSchema"]["additionalProperties"] = True
        self.assertFalse(broker.dynamic_tool_specs()[0]["inputSchema"]["additionalProperties"])

    def test_specs_match_actual_embedded_dynamic_function_discriminator(self):
        path = ROOT / "artifacts/GATE0_CODEX_INTERFACE/20260907_001/schemas/experimental.json"
        embedded = json.loads(path.read_text())
        schema = json.loads(embedded["v2/ThreadStartParams.json"])
        function = next(item for item in schema["definitions"]["DynamicToolSpec"]["oneOf"]
                        if item["properties"]["type"]["enum"] == ["function"])
        for spec in broker.dynamic_tool_specs():
            self.assertTrue(set(function["required"]) <= set(spec))
            self.assertEqual(spec["type"], "function")
            for key in ("type", "name", "description"):
                self.assertEqual(function["properties"][key]["type"], "string")
                self.assertIs(type(spec[key]), str)
            self.assertIs(type(spec["inputSchema"]), dict)


class HistoricalAuditTests(unittest.TestCase):
    def setUp(self):
        self.f = Fixture()
        closure = json.loads((ROOT / broker.CLOSURE).read_text())
        paths = {entry["path"] for entry in closure["view_input_files"]}
        paths |= {broker.RAW_DIR + "/" + name for name in closure["post_run_additional_inventory"]}
        paths.add(broker.CLOSURE)
        for path in paths:
            self.f.add(path, (ROOT / path).read_bytes(), "text")
        self.f.freeze()

    def tearDown(self):
        self.f.close()

    def test_actual_unchanged_auditor_and_original_metadata_partition(self):
        with self.f.open() as instance:
            result = instance.dispatch("run_observer_audit", {})
            receipt = (self.f.output / result["receipt_output_id"]).read_bytes()
            self.assertEqual(result["receipt_sha256"], sha(receipt))
            self.assertTrue(result["receipt"]["artifact_consistency_passed"])
            self.assertEqual(result["receipt"]["transitions_checked"], 6912)
            self.assertEqual(result["source_archive"], {"original_files": 13,
                "post_run_metadata_files": 4, "post_run_metadata_remains_post_run": True})
            self.assertIsNone(result["formal_verdict"])
            self.assertFalse(result["new_experiment"])
            self.assertFalse((self.f.output / broker.VERDICT_NAME).exists())
            with self.assertRaises(broker.BrokerError):
                instance.dispatch("run_observer_audit", {})

    def test_unlisted_expanded_archive_member_rejected_before_execution(self):
        (self.f.packet / broker.RAW_DIR / "unlisted.txt").write_bytes(b"not in either inventory")
        with self.f.open() as instance, mock.patch.object(broker.subprocess, "run") as runner:
            with self.assertRaises(broker.BrokerError):
                instance.dispatch("run_observer_audit", {})
            runner.assert_not_called()

    def test_changed_auditor_rejected_before_execution(self):
        with self.f.open() as instance, mock.patch.object(broker.subprocess, "run") as runner:
            (self.f.packet / broker.AUDITOR).write_bytes(b"raise RuntimeError('substituted')")
            with self.assertRaises(broker.BrokerError):
                instance.dispatch("run_observer_audit", {})
            runner.assert_not_called()

    def test_forged_receipt_rejected_and_actual_output_preserved(self):
        def fake_process(command, **kwargs):
            receipt = Path(command[command.index("--receipt") + 1])
            payload = json.loads((ROOT / broker.HISTORICAL_RECEIPT).read_text())
            payload["transitions_checked"] += 1
            receipt.write_text(json.dumps(payload))
            return subprocess.CompletedProcess(command, 0, b"synthetic forged receipt test", b"")
        with self.f.open() as instance, mock.patch.object(broker.subprocess, "run", side_effect=fake_process):
            with self.assertRaisesRegex(broker.BrokerError, "differs from historical"):
                instance.dispatch("run_observer_audit", {})
            self.assertEqual(len(list(self.f.output.glob("observer-audit-*/AUDITOR_STDOUT.bin"))), 1)
            self.assertFalse((self.f.output / broker.VERDICT_NAME).exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
