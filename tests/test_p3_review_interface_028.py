"""Engineering contract checks with the real frozen broker; no model runs."""
import base64
import copy
import errno
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import p3_review_interface_028 as interface

original = interface.original
TEST_ROOT = ROOT / "delivery/interface028_work"
TEST_ROOT.mkdir(parents=True, exist_ok=True)
PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class Fixture:
    def __init__(self):
        self.temp = tempfile.TemporaryDirectory(dir=TEST_ROOT)
        self.root = Path(self.temp.name)
        self.packet, self.output = self.root / "packet", self.root / "output"
        self.packet.mkdir()
        self.output.mkdir()
        self.files = {}
        self.add("CANARY.txt", "αβγ\nfixture evidence\n".encode(), "text")
        self.add("pages/page.png", PNG, "image")
        self.add("papers/full.pdf", b"%PDF synthetic", "binary")
        for path in original.REVIEW_MANIFESTS.values():
            self.add(path, b'{"synthetic":true}\n', "text")
        self.freeze()

    def add(self, path, raw, kind):
        target = self.packet / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        self.files[path] = {"path": path, "sha256": sha(raw), "kind": kind}

    def freeze(self):
        raw = json.dumps({"schema_version": 1, "files": list(self.files.values())}).encode()
        (self.packet / "BROKER_MANIFEST.json").write_bytes(raw)
        self.pin = sha(raw)

    def open(self):
        return interface.ReviewBroker(self.packet, manifest_sha256=self.pin, output_root=self.output)

    def verdict(self):
        return {"verdict": "SUSPEND_FOR_DEPENDENCY",
                "applies_to": {"scope": "Synthetic engineering fixture, no scientific verdict", **{
                    field: self.files[path]["sha256"] for field, path in original.REVIEW_MANIFESTS.items()}},
                "summary": "Synthetic interface exercise only.",
                "dispositions": [{"subject": subject, "disposition": "Synthetic dependency",
                                  "reason": "No scientific model is running.", "evidence": [
                                      {"path": "CANARY.txt", "sha256": self.files["CANARY.txt"]["sha256"]}]}
                                 for subject in original.SUBJECTS],
                "strongest_objections": ["Engineering test only."],
                "missing_dependencies": [], "required_corrections": []}

    def close(self):
        self.temp.cleanup()


class InterfaceTests(unittest.TestCase):
    def setUp(self):
        self.f = Fixture()

    def tearDown(self):
        self.f.close()

    def assertRecoverable(self, tool, args, code):
        with self.f.open() as broker:
            with self.assertRaises(interface.ToolInputError) as result:
                broker.dispatch(tool, args)
            self.assertEqual(result.exception.code, code)
            self.assertFalse(broker._failed)
            self.assertEqual(broker.dispatch("hash_file", {"path": "CANARY.txt"})["sha256"],
                             self.f.files["CANARY.txt"]["sha256"])
            self.assertFalse((self.f.output / original.VERDICT_NAME).exists())

    def test_real_text_unicode_eof_hash_and_image_success(self):
        with self.f.open() as broker:
            value = broker.dispatch("read_text", {"path": "CANARY.txt", "offset": 1, "length": 2})
            self.assertEqual(value["text"], "βγ")
            end = broker.dispatch("read_text", {"path": "CANARY.txt", "offset": value["total_characters"], "length": 100000})
            self.assertEqual(end["text"], "")
            self.assertTrue(end["complete"])
            self.assertEqual(base64.b64decode(broker.dispatch("read_page_image", {"path": "pages/page.png"})["data_base64"]), PNG)
            self.assertEqual(broker.dispatch("hash_file", {"path": "papers/full.pdf"})["bytes"], 14)

    def test_lost_integer_constraints_recover_and_no_float_coercion(self):
        for key, values in (("offset", (True, -1, 0.0, 134217729, None, "0", float("inf"))),
                            ("length", (False, 0, 100001, 1.0, None, "10", float("nan")))):
            for value in values:
                args = {"path": "CANARY.txt", "offset": 0, "length": 10}
                args[key] = value
                with self.subTest(key=key, value=value):
                    self.assertRecoverable("read_text", args, "integer_bounds")

    def test_exact_fields_all_five_tools(self):
        examples = {"read_text": {"path": "CANARY.txt", "offset": 0, "length": 10},
                    "read_page_image": {"path": "pages/page.png"}, "hash_file": {"path": "CANARY.txt"},
                    "run_observer_audit": {}, "submit_verdict": self.f.verdict()}
        for tool, args in examples.items():
            with self.subTest(tool=tool):
                extra = copy.deepcopy(args)
                extra["undeclared_field"] = "not executed or reflected"
                self.assertRecoverable(tool, extra, "argument_fields")
                self.assertRecoverable(tool, [], "argument_fields")
                if args:
                    missing = copy.deepcopy(args)
                    missing.pop(next(iter(missing)))
                    self.assertRecoverable(tool, missing, "argument_fields")

    def test_known_wrong_kinds_and_past_eof_are_correctable(self):
        for tool, args, code in (
                ("read_text", {"path": "papers/full.pdf", "offset": 0, "length": 10}, "resource_kind"),
                ("read_page_image", {"path": "CANARY.txt"}, "resource_kind"),
                ("read_text", {"path": "CANARY.txt", "offset": 1000, "length": 10}, "text_offset_past_end"),
                ("hash_file", {"path": 3}, "resource_path_type")):
            with self.subTest(tool=tool, code=code):
                self.assertRecoverable(tool, args, code)

    def test_path_denials_are_fatal_original_path_frames_survive(self):
        for path in ("../outside", "/etc/passwd", "./CANARY.txt", "folder/../CANARY.txt", "folder//CANARY.txt", "CANARY.txt\\x", "CANARY.txt\x00", "", "x" * 1025, "unknown.txt"):
            with self.subTest(path=path), self.f.open() as broker:
                try:
                    broker.dispatch("read_text", {"path": path, "offset": 0, "length": 10})
                except original.BrokerError as error:
                    frames = []
                    traceback = error.__traceback__
                    while traceback:
                        frames.append(traceback.tb_frame.f_code)
                        traceback = traceback.tb_next
                    self.assertIn(original.ReviewBroker._read.__code__, frames)
                    if path != "unknown.txt":
                        self.assertIn(original._path.__code__, frames)
                else:
                    self.fail("Forbidden path accepted")
                self.assertTrue(broker._failed)
                with self.assertRaises(original.BrokerError):
                    broker.dispatch("hash_file", {"path": "CANARY.txt"})

    def test_forbidden_path_cannot_hide_behind_extra_keys_or_bad_bounds(self):
        with self.f.open() as broker:
            with self.assertRaises(original.BrokerError):
                broker.dispatch("read_text", {"path": "../outside", "offset": -1, "length": 0, "extra": True})
            self.assertTrue(broker._failed)

    def test_unknown_operation_is_fatal_no_process(self):
        with self.f.open() as broker, mock.patch.object(original.subprocess, "run") as runner:
            with self.assertRaises(original.BrokerError):
                broker.dispatch("exec", {"command": "anything"})
            self.assertTrue(broker._failed)
            runner.assert_not_called()

    def test_arbitrary_auditor_arguments_never_execute(self):
        with mock.patch.object(original.subprocess, "run") as runner:
            self.assertRecoverable("run_observer_audit", {"command": "not executed", "destination": "../not written"}, "argument_fields")
            runner.assert_not_called()

    def test_eight_errors_total_ninth_fatal_success_does_not_reset(self):
        with self.f.open() as broker:
            for _ in range(8):
                with self.assertRaises(interface.ToolInputError):
                    broker.dispatch("read_text", {"path": "CANARY.txt", "offset": 0, "length": 0})
                broker.dispatch("hash_file", {"path": "CANARY.txt"})
            self.assertEqual(broker.recoverable_input_errors, 8)
            with self.assertRaisesRegex(original.BrokerError, "ceiling"):
                broker.dispatch("run_observer_audit", {"extra": True})
            self.assertTrue(broker._failed)
            with self.assertRaises(AttributeError):
                broker._failed = False

    def test_corrupted_unrelated_input_never_hidden_by_bad_argument(self):
        with self.f.open() as broker:
            (self.f.packet / "papers/full.pdf").write_bytes(b"mutation")
            with self.assertRaises(original.BrokerError):
                broker.dispatch("read_text", {"path": "CANARY.txt", "offset": 0, "length": 0})
            self.assertTrue(broker._failed)
            self.assertEqual(broker.recoverable_input_errors, 0)

    def test_mutation_between_input_check_and_error_response_is_fatal(self):
        with self.f.open() as broker:
            actual = broker._prevalidate
            def mutate_then_error(tool, args):
                (self.f.packet / "papers/full.pdf").write_bytes(b"mutation")
                return actual(tool, args)
            with mock.patch.object(broker, "_prevalidate", side_effect=mutate_then_error):
                with self.assertRaises(original.BrokerError):
                    broker.dispatch("read_text", {"path": "CANARY.txt", "offset": 0, "length": 0})
            self.assertTrue(broker._failed)
            self.assertEqual(broker.recoverable_input_errors, 0)

    def test_valid_calls_keep_original_two_corpus_passes_errors_verify_before_feedback(self):
        with self.f.open() as broker:
            with mock.patch.object(broker._original, "verify_inputs", wraps=broker._original.verify_inputs) as verify:
                broker.dispatch("hash_file", {"path": "CANARY.txt"})
                self.assertEqual(verify.call_count, 2)
                verify.reset_mock()
                with self.assertRaises(interface.ToolInputError):
                    broker.dispatch("read_text", {"path": "CANARY.txt", "offset": 0, "length": 0})
                self.assertEqual(verify.call_count, 1)
            self.assertEqual(broker._request_reads, {})

    def test_mutation_after_successful_prevalidation_caught_by_original_dispatch(self):
        with self.f.open() as broker:
            actual = broker._prevalidate
            def mutate_after_validate(tool, args):
                result = actual(tool, args)
                (self.f.packet / "papers/full.pdf").write_bytes(b"mutation")
                return result
            with mock.patch.object(broker, "_prevalidate", side_effect=mutate_after_validate):
                with self.assertRaises(original.BrokerError):
                    broker.dispatch("hash_file", {"path": "CANARY.txt"})
            self.assertTrue(broker._failed)
            self.assertEqual(broker._request_reads, {})

    def test_same_bytes_replaced_identity_symlink_hardlink_fatal(self):
        for mode in ("replacement", "symlink", "hardlink"):
            fixture = Fixture()
            try:
                with fixture.open() as broker:
                    target = fixture.packet / "CANARY.txt"
                    saved = target.read_bytes()
                    if mode == "replacement":
                        target.unlink()
                        target.write_bytes(saved)
                    elif mode == "symlink":
                        target.unlink()
                        other = fixture.root / "outside"
                        other.write_bytes(saved)
                        target.symlink_to(other)
                    else:
                        os.link(target, fixture.root / "alias")
                    with self.assertRaises(original.BrokerError):
                        broker.dispatch("hash_file", {"path": "CANARY.txt"})
                    self.assertTrue(broker._failed)
            finally:
                fixture.close()

    def test_invalid_utf8_and_oversize_or_nonpng_are_packet_failures(self):
        for path, raw, kind, tool in (("bad.txt", b"\xff", "text", "read_text"),
                                      ("bad.png", b"not png", "image", "read_page_image"),
                                      ("large.png", PNG + b"x" * original.MAX_IMAGE_BYTES, "image", "read_page_image")):
            self.f.add(path, raw, kind)
            self.f.freeze()
            with self.subTest(path=path), self.f.open() as broker:
                args = {"path": path, **({"offset": 0, "length": 10} if tool == "read_text" else {})}
                with self.assertRaises(original.BrokerError):
                    broker.dispatch(tool, args)
                self.assertTrue(broker._failed)

    def test_verdict_nested_shapes_and_unique_subjects_correctable(self):
        mutations = [
            (lambda p: p.update(verdict="APPROVED"), "verdict_vocabulary"),
            (lambda p: p.update(summary=" \n\t"), "bounded_text"),
            (lambda p: p.update(summary="x" * 30001), "bounded_text"),
            (lambda p: p["applies_to"].update(scope=""), "bounded_text"),
            (lambda p: p["applies_to"].update(extra="x"), "argument_fields"),
            (lambda p: p["applies_to"].update(original_manifest_sha256="A" * 64), "sha256_format"),
            (lambda p: p["dispositions"].pop(), "subject_dispositions"),
            (lambda p: p["dispositions"][0].update(subject="C2"), "subject_dispositions"),
            (lambda p: p["dispositions"][0].update(subject="other"), "subject_dispositions"),
            (lambda p: p["dispositions"][0].update(disposition=""), "bounded_text"),
            (lambda p: p["dispositions"][0].update(reason=""), "bounded_text"),
            (lambda p: p["dispositions"][0].update(evidence=[]), "evidence_list"),
            (lambda p: p["dispositions"][0]["evidence"][0].update(sha256="0" * 63), "sha256_format"),
            (lambda p: p["dispositions"][0]["evidence"][0].update(extra="x"), "argument_fields"),
            (lambda p: p.update(strongest_objections="not list"), "text_list"),
            (lambda p: p.update(missing_dependencies=["x"] * 101), "text_list"),
            (lambda p: p.update(required_corrections=[""]), "bounded_text"),
        ]
        for mutation, code in mutations:
            payload = self.f.verdict()
            mutation(payload)
            with self.subTest(code=code, mutation=mutation):
                self.assertRecoverable("submit_verdict", payload, code)

    def test_evidence_max_list_bound_correctable(self):
        payload = self.f.verdict()
        payload["dispositions"][0]["evidence"] *= 201
        self.assertRecoverable("submit_verdict", payload, "evidence_list")

    def test_large_encoded_verdict_is_feedback_without_partial_output(self):
        payload = self.f.verdict()
        payload["strongest_objections"] = ["α" * 30000] * 30
        self.assertRecoverable("submit_verdict", payload, "verdict_size")

    def test_claimed_sha_mismatch_fatal_even_when_other_field_malformed(self):
        for field in ("scope", "evidence"):
            payload = self.f.verdict()
            payload["summary"] = ""
            if field == "scope":
                payload["applies_to"]["original_manifest_sha256"] = "0" * 64
            else:
                payload["dispositions"][0]["evidence"][0]["sha256"] = "0" * 64
            with self.subTest(field=field), self.f.open() as broker:
                with self.assertRaises(original.BrokerError) as error:
                    broker.dispatch("submit_verdict", payload)
                self.assertEqual(interface.classify_broker_failure(error.exception), "integrity.claimed_sha256")
                self.assertTrue(broker._failed)

    def test_forbidden_evidence_fatal_even_when_verdict_wrong_shape(self):
        payload = self.f.verdict()
        payload["dispositions"][0]["evidence"][0]["path"] = "../outside"
        payload["extra"] = "ordinary error must not hide denial"
        with self.f.open() as broker:
            with self.assertRaises(original.BrokerError):
                broker.dispatch("submit_verdict", payload)
            self.assertTrue(broker._failed)

    def test_all_substantive_verdicts_require_real_audit(self):
        for verdict in ("GO", "REVISE_ONCE", "KILL"):
            payload = self.f.verdict()
            payload["verdict"] = verdict
            with self.subTest(verdict=verdict):
                self.assertRecoverable("submit_verdict", payload, "audit_required")

    def test_dependency_payload_order_and_text_unchanged_exclusive_output(self):
        payload = self.f.verdict()
        payload["dispositions"].reverse()
        with self.f.open() as broker:
            result = broker.dispatch("submit_verdict", payload)
            stored = (self.f.output / original.VERDICT_NAME).read_bytes()
            self.assertEqual(json.loads(stored)["reviewer_verdict"], payload)
            self.assertEqual(result["sha256"], sha(stored))
            with self.assertRaises(original.BrokerError):
                broker.dispatch("submit_verdict", payload)
            self.assertEqual((self.f.output / original.VERDICT_NAME).read_bytes(), stored)

    def test_preexisting_output_not_overwritten_classified_without_raw_os_text(self):
        out = self.f.output / original.VERDICT_NAME
        out.write_bytes(b"preserve")
        with self.f.open() as broker:
            with self.assertRaises(FileExistsError) as error:
                broker.dispatch("submit_verdict", self.f.verdict())
            self.assertEqual(interface.classify_broker_failure(error.exception), "os.output_already_exists")
            self.assertTrue(broker._failed)
        self.assertEqual(out.read_bytes(), b"preserve")

    def test_error_feedback_and_failure_labels_never_echo_unknown_values(self):
        marker = "DO_NOT_EXPOSE_PRIVATE_INPUT"
        with self.f.open() as broker:
            with self.assertRaises(interface.ToolInputError) as error:
                broker.dispatch("hash_file", {"path": "CANARY.txt", marker: marker})
            value = error.exception.as_dict()
            self.assertNotIn(marker, json.dumps(value))
            self.assertEqual(value["code"], "argument_fields")
        for error, expected in ((original.BrokerError(marker), "broker.unclassified_failure"),
                                (OSError(errno.EACCES, marker, marker), "os.permission_denied"),
                                (ValueError(marker), "broker.unclassified_failure")):
            self.assertEqual(interface.classify_broker_failure(error), expected)

    def test_specs_original_grammar_unchanged_and_fresh(self):
        def strip(value):
            if type(value) is dict:
                return {key: strip(item) for key, item in value.items() if key != "description"}
            return [strip(item) for item in value] if type(value) is list else value
        before = original.dynamic_tool_specs()
        after = interface.dynamic_tool_specs()
        for old, new in zip(before, after):
            self.assertEqual(strip(old), strip(new))
        after[0]["inputSchema"]["properties"]["length"]["description"] = "corrupted caller copy"
        self.assertNotIn("corrupted", json.dumps(interface.dynamic_tool_specs()))
        self.assertEqual(original.dynamic_tool_specs(), before)

    def test_constraints_survive_description_preserving_schema_projection(self):
        # Source-based projection, not an executed native serializer. This is
        # exact for this simple typed/no-ref/no-composition schema subset: Rust
        # sanitizer makes no changes, then JsonSchema serde drops unknown keys.
        # Primary source accessed 2026-09-10:
        # https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/tools/src/json_schema.rs
        source = ROOT / "artifacts/P3_INTERFACE_CONTRACT_SOURCE/20260910_028/source/codex-rs/tools/src/json_schema.rs"
        self.assertEqual(sha(source.read_bytes()), "ccfc96787883f2c1c3d51a61c36db34ec2d371fc1e029bef4c42683d5069748d")
        kept = {"type", "properties", "items", "required", "additionalProperties", "description", "enum"}
        def project(schema):
            result = {key: copy.deepcopy(value) for key, value in schema.items() if key in kept}
            if "properties" in result:
                result["properties"] = {key: project(value) for key, value in result["properties"].items()}
            if "items" in result:
                result["items"] = project(result["items"])
            return result
        for spec in interface.dynamic_tool_specs():
            schema = spec["inputSchema"]
            projected = project(schema)
            # Rust first measures the projected compact normalized length;
            # exceeding 5000 invokes the pass that strips all descriptions.
            self.assertLessEqual(len(json.dumps(projected, ensure_ascii=False, separators=(",", ":")).encode()), 5000)
            def compare(old, new):
                description = new.get("description", "")
                self.assertTrue(description)
                for key in ("minimum", "maximum", "minLength", "maxLength", "minItems", "maxItems"):
                    if key in old:
                        self.assertIn(str(old[key]), description)
                if "pattern" in old:
                    self.assertIn("64 lowercase hexadecimal", description)
                for key, child in old.get("properties", {}).items():
                    compare(child, new["properties"][key])
                if "items" in old:
                    compare(old["items"], new["items"])
            compare(schema, projected)
        verdict = next(s for s in interface.dynamic_tool_specs() if s["name"] == "submit_verdict")
        self.assertIn("once each in any order", verdict["description"])
        self.assertIn("1048576", verdict["description"])
        self.assertIn("524288", verdict["description"])


class RealHistoricalAuditTests(unittest.TestCase):
    def setUp(self):
        self.f = Fixture()
        closure = json.loads((ROOT / original.CLOSURE).read_text())
        paths = {entry["path"] for entry in closure["view_input_files"]}
        paths |= {original.RAW_DIR + "/" + name for name in closure["post_run_additional_inventory"]}
        paths.add(original.CLOSURE)
        for path in paths:
            self.f.add(path, (ROOT / path).read_bytes(), "text")
        self.f.freeze()

    def tearDown(self):
        self.f.close()

    def test_real_fixed_audit_repeat_feedback_then_substantive_transport(self):
        payload = self.f.verdict()
        payload["verdict"] = "REVISE_ONCE"
        with self.f.open() as broker:
            self.assertFalse(broker.audit_completed)
            with self.assertRaises(AttributeError):
                broker.audit_completed = True
            with self.assertRaises(interface.ToolInputError) as error:
                broker.dispatch("submit_verdict", payload)
            self.assertEqual(error.exception.code, "audit_required")
            receipt = broker.dispatch("run_observer_audit", {})
            self.assertTrue(broker.audit_completed)
            with self.assertRaises(AttributeError):
                broker.audit_completed = False
            self.assertTrue(receipt["receipt"]["artifact_consistency_passed"])
            self.assertEqual(receipt["receipt"]["transitions_checked"], 6912)
            with self.assertRaises(interface.ToolInputError) as error:
                broker.dispatch("run_observer_audit", {})
            self.assertEqual(error.exception.code, "audit_already_run")
            self.assertEqual(len(list(self.f.output.glob("observer-audit-*"))), 1)
            broker.dispatch("submit_verdict", payload)
            self.assertEqual(json.loads((self.f.output / original.VERDICT_NAME).read_bytes())["reviewer_verdict"], payload)
            self.assertIsNone(receipt["formal_verdict"])

    def test_unlisted_archive_member_still_fatal_before_execution(self):
        (self.f.packet / original.RAW_DIR / "unlisted.txt").write_bytes(b"unknown")
        with self.f.open() as broker, mock.patch.object(original.subprocess, "run") as run:
            with self.assertRaises(original.BrokerError) as error:
                broker.dispatch("run_observer_audit", {})
            self.assertEqual(interface.classify_broker_failure(error.exception), "integrity.audit")
            self.assertTrue(broker._failed)
            run.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
