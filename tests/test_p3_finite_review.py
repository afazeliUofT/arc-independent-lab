"""Synthetic finite-review orchestration checks; no native client or model use.

These are engineering checks of parent orchestration, not independent scientific
review or measured native isolation. All fixture files live inside the lab.
"""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest import mock


LAB = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("p3_finite_review_tested", LAB / "scripts/p3_finite_review.py")
finite = importlib.util.module_from_spec(spec)
spec.loader.exec_module(finite)


class FiniteReviewTests(unittest.TestCase):
    def setUp(self):
        fixture = tempfile.TemporaryDirectory(prefix="finite_review_fixture_", dir=LAB / "delivery")
        self.addCleanup(fixture.cleanup)
        self.root = Path(fixture.name) / "ARC_Independent_Lab"
        for name in ("delivery", "state", "configs", "scripts"):
            (self.root / name).mkdir(parents=True, exist_ok=True)
        self.patch_root = mock.patch.object(finite, "ROOT", self.root)
        self.patch_root.start()
        self.addCleanup(self.patch_root.stop)
        self.patch_scope = mock.patch.object(finite, "SCOPE_SHA256", "a" * 64)
        self.patch_scope.start()
        self.addCleanup(self.patch_scope.stop)
        self.scope = {"approval_id": "APPROVE_SYNTHETIC_FIXTURE",
                      "private_packet_manifest_sha256": "b" * 64,
                      "runtime_sha256": "runtime-fixture", "bwrap_sha256": "bwrap-fixture",
                      "synthetic_seconds_including_cleanup": 10,
                      "scientific_seconds_including_cleanup": 20,
                      "maximum_synthetic_broker_calls": 2,
                      "maximum_scientific_broker_calls": 5}
        self.pins = {"scope_sha256": finite.SCOPE_SHA256,
                     "packet_manifest_sha256": self.scope["private_packet_manifest_sha256"]}
        self.binding = {"model": "synthetic-model", "id": "synthetic-model", "effort": "xhigh"}
        self.run = self.root / "delivery" / finite.RUN_NAME
        self.packet = self.root / "private_packet"
        self.packet.mkdir()
        self.packet_info = {"packet_path": str(self.packet),
                            "manifest_sha256": self.scope["private_packet_manifest_sha256"]}
        self.answer = ("## ANSWER\n" + self.scope["approval_id"] +
                       "\nscope_sha256: " + finite.SCOPE_SHA256 + "\n")

    def write_answer(self, text):
        (self.root / "state/ESCALATION.md").write_text(text)

    def synthetic_stage(self, **changes):
        observation = {"status": "SYNTHETIC_REFUSAL_OBSERVED",
                       "synthetic_allowed_read_observed": True,
                       "observed_refusal": True, "native_process_reaped": True,
                       "selected_binding": dict(self.binding)}
        observation.update(changes)
        return {"stage": "synthetic", "host_checks": {"all_noncredential_checks_pass": True},
                "observation": observation}

    def science_stage(self, **changes):
        observation = {"status": "VERDICT_SUBMITTED", "verdict_submitted": True,
                       "native_process_reaped": True, "selected_binding": dict(self.binding)}
        observation.update(changes)
        return {"stage": "science", "host_checks": {"all_noncredential_checks_pass": True},
                "observation": observation}

    def write_verdict(self):
        output = self.run / "science_output"
        output.mkdir(exist_ok=True)
        raw = b'{"synthetic_fixture_only":true,"text":"preserve exact bytes"}\n'
        (output / "REVIEW_VERDICT.json").write_bytes(raw)
        return raw

    def execute(self, stage_callback, recheck=None):
        installer = types.SimpleNamespace(verify_packet=mock.Mock(return_value=self.packet_info))
        with mock.patch.object(finite, "run_stage", side_effect=stage_callback) as stages, \
             mock.patch.object(finite, "load_bundle", side_effect=recheck,
                               return_value=(self.scope, {}, self.pins)), \
             mock.patch.object(finite, "module", return_value=installer):
            path = finite.execute(self.scope, {}, self.pins, {"path": "synthetic approval"}, self.packet_info)
        raw = path.read_bytes()
        self.assertEqual((path.parent / "REPORT.sha256").read_text(), finite.sha(raw) + "\n")
        return json.loads(raw), stages

    def test_exact_answer_and_valid_archive(self):
        self.write_answer(self.answer)
        accepted = finite.approval(self.scope)
        self.assertEqual(accepted["path"], "state/ESCALATION.md")
        archive = self.root / finite.APPROVAL_ARCHIVE
        archive.parent.mkdir(parents=True)
        archive.write_text(self.answer)
        self.write_answer("\n")
        self.assertEqual(finite.approval(self.scope)["path"], finite.APPROVAL_ARCHIVE)

    def test_fenced_duplicate_conditional_or_malformed_answer_rejected(self):
        for wrong in ("```\n" + self.answer + "```\n", "~~~\n" + self.answer + "~~~\n",
                      "\n".join("    " + line for line in self.answer.splitlines()),
                      self.answer + self.answer, self.answer + "Only if nothing changes.\n",
                      self.answer.replace("scope_sha256: ", "scope_sha256:"),
                      "```\ninside fence\n```not-a-closing-fence\n" + self.answer):
            with self.subTest(wrong=wrong):
                self.write_answer(wrong)
                with self.assertRaises(finite.Stop):
                    finite.approval(self.scope)

    def test_current_nonempty_escalation_cannot_be_ignored_for_archive(self):
        archive = self.root / finite.APPROVAL_ARCHIVE
        archive.parent.mkdir(parents=True)
        archive.write_text(self.answer)
        self.write_answer("## QUESTION\nA newer unanswered request\n")
        with self.assertRaises(finite.Stop):
            finite.approval(self.scope)

    def test_comment_hidden_answer_never_authorizes(self):
        for text in ("<!--\n" + self.answer, "<!--\n" + self.answer + "-->\n"):
            with self.subTest(text=text):
                self.write_answer(text)
                with self.assertRaises(finite.Stop):
                    finite.approval(self.scope)

    def test_bundle_rejects_changed_source_and_frozen_input(self):
        source = self.root / "scripts/fixture_source.py"
        source.write_bytes(b"# Synthetic pin fixture; not executed.\n")
        evidence = self.root / "evidence"
        evidence.mkdir()
        member = evidence / "FROZEN.txt"
        member.write_bytes(b"synthetic frozen evidence\n")
        manifest = evidence / "FROZEN_MANIFEST.json"
        manifest.write_text(json.dumps({"files": [{"path": "evidence/FROZEN.txt",
                                                    "sha256": finite.sha(member.read_bytes())}]}))
        accepted = self.root / "accepted.json"
        accepted.write_text(json.dumps({"observation": {"status": "OBSERVED_POSTLOGIN_METADATA_ONLY"}}))
        prior = self.root / "prior.json"
        prior.write_text("{}")
        scope = dict(self.scope, maximum_native_processes=2, maximum_model_turns=2,
                     accepted_metadata_path="accepted.json", accepted_metadata_sha256=finite.sha(accepted.read_bytes()),
                     prior_native_scope_path="prior.json", prior_native_scope_sha256=finite.sha(prior.read_bytes()))
        scope_path = self.root / finite.SCOPE_PATH
        scope_path.write_text(json.dumps(scope))
        with mock.patch.object(finite, "SCOPE_SHA256", finite.sha(scope_path.read_bytes())), \
             mock.patch.object(finite, "SOURCE_PINS", {"scripts/fixture_source.py": finite.sha(source.read_bytes())}), \
             mock.patch.object(finite, "FROZEN", {"evidence/FROZEN_MANIFEST.json": finite.sha(manifest.read_bytes())}):
            self.assertEqual(finite.load_bundle()[0], scope)
            original = source.read_bytes()
            source.write_bytes(b"# Changed synthetic source\n")
            with self.assertRaisesRegex(finite.Stop, "Pinned reviewer dependency changed"):
                finite.load_bundle()
            source.write_bytes(original)
            member.write_bytes(b"changed synthetic evidence\n")
            with self.assertRaisesRegex(finite.Stop, "Frozen scientific input changed"):
                finite.load_bundle()

    def test_default_inspection_has_no_host_or_native_action(self):
        with mock.patch.object(finite, "load_bundle", return_value=(self.scope, {}, self.pins)), \
             mock.patch.object(finite, "canonical_host") as host, \
             mock.patch.object(finite, "approval") as approval, \
             mock.patch.object(finite, "module") as modules, \
             mock.patch.object(finite, "execute") as execute, \
             mock.patch.object(finite.sys, "argv", ["p3_finite_review.py"]), \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(finite.main(), 0)
        for function in (host, approval, modules, execute):
            function.assert_not_called()
        self.assertFalse(self.run.exists())

    def test_complete_receipt_reused_before_host_or_approval_checks(self):
        self.run.mkdir()
        report = {"kind": finite.REPORT_KIND, "pins": self.pins,
                  "unattended_model_use_authorized": False,
                  "parent_credential_contents_read": False, "reviewer_output": None}
        raw = finite.exclusive_json(self.run / "REPORT.json", report)
        (self.run / "REPORT.sha256").write_text(finite.sha(raw) + "\n")
        with mock.patch.object(finite, "load_bundle", return_value=(self.scope, {}, self.pins)), \
             mock.patch.object(finite, "canonical_host", side_effect=AssertionError("host queried")), \
             mock.patch.object(finite, "approval", side_effect=AssertionError("approval queried")), \
             mock.patch.object(finite, "execute", side_effect=AssertionError("native started")), \
             mock.patch.object(finite.sys, "argv", ["p3_finite_review.py", "--run-attended-review"]), \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(finite.main(), 0)
        self.assertEqual((self.run / "REPORT.json").read_bytes(), raw)

    def test_partial_attempt_preserved_and_never_retried(self):
        self.run.mkdir()
        sentinel = self.run / "ATTEMPT.json"
        sentinel.write_bytes(b"synthetic partial sentinel\n")
        with self.assertRaises((finite.Stop, OSError)):
            finite.existing(self.run, self.pins)
        with self.assertRaises(finite.Stop):
            finite.execute(self.scope, {}, self.pins, {}, self.packet_info)
        self.assertEqual(sentinel.read_bytes(), b"synthetic partial sentinel\n")
        self.assertEqual([p.name for p in self.run.iterdir()], ["ATTEMPT.json"])

    def test_synthetic_actual_session_fields_admit_distinct_science_binding(self):
        calls = []
        def stage(scope, prior, run, mode, packet, manifest, expected_binding=None):
            calls.append((mode, packet, expected_binding))
            if mode == "synthetic":
                return self.synthetic_stage()
            self.write_verdict()
            return self.science_stage()
        result, stages = self.execute(stage)
        self.assertEqual(stages.call_count, 2)
        self.assertEqual([item[0] for item in calls], ["synthetic", "science"])
        self.assertNotEqual(calls[0][1], calls[1][1])
        self.assertIsNone(calls[0][2])
        self.assertEqual(calls[1][2], self.binding)
        self.assertEqual(result["status"], "REVIEWER_OUTPUT_PRESERVED")
        self.assertFalse(result["reviewer_output"]["parent_edited"])

    def test_any_missing_synthetic_admission_evidence_prevents_science(self):
        for changes in ({"status": "STOPPED_WITHOUT_VERDICT"},
                        {"synthetic_allowed_read_observed": False}, {"observed_refusal": False},
                        {"native_process_reaped": False}):
            with self.subTest(changes=changes):
                # Each subcase is a genuinely distinct synthetic attempt folder.
                with mock.patch.object(finite, "RUN_NAME", "CASE_" + next(iter(changes))):
                    result, stages = self.execute(lambda *a, **k: self.synthetic_stage(**changes))
                self.assertEqual(stages.call_count, 1)
                self.assertEqual(len(result["stages"]), 1)
                self.assertIsNone(result["reviewer_output"])

    def test_frozen_input_recheck_failure_prevents_science(self):
        result, stages = self.execute(lambda *a, **k: self.synthetic_stage(),
                                      recheck=finite.Stop("Frozen scientific input changed"))
        self.assertEqual(stages.call_count, 1)
        self.assertEqual(result["status"], "STOPPED_WITHOUT_COMPLETED_REVIEW")
        self.assertEqual(result["reason"], "Frozen scientific input changed")

    def test_broker_verdict_preserved_when_later_host_check_fails(self):
        expected = []
        def stage(*args, **kwargs):
            if args[3] == "synthetic":
                return self.synthetic_stage()
            expected.append(self.write_verdict())
            value = self.science_stage()
            value["host_checks"]["all_noncredential_checks_pass"] = False
            return value
        result, _ = self.execute(stage)
        self.assertEqual(result["status"], "STOPPED_WITHOUT_COMPLETED_REVIEW")
        self.assertIsNotNone(result["reviewer_output"])
        self.assertEqual(result["reviewer_output"]["sha256"], finite.sha(expected[0]))
        self.assertEqual((self.run / result["reviewer_output"]["path"]).read_bytes(), expected[0])

    def test_broker_verdict_preserved_when_stage_raises_after_submission(self):
        expected = []
        def stage(*args, **kwargs):
            if args[3] == "synthetic":
                return self.synthetic_stage()
            expected.append(self.write_verdict())
            raise OSError("synthetic post-submission host failure")
        result, _ = self.execute(stage)
        self.assertIsNotNone(result["reviewer_output"])
        self.assertEqual(result["reviewer_output"]["sha256"], finite.sha(expected[0]))
        self.assertEqual(result["status"], "STOPPED_WITHOUT_COMPLETED_REVIEW")

    def test_missing_scientific_cleanup_never_claims_complete_review(self):
        def stage(*args, **kwargs):
            if args[3] == "synthetic":
                return self.synthetic_stage()
            self.write_verdict()
            return self.science_stage(native_process_reaped=False)
        result, _ = self.execute(stage)
        self.assertIsNotNone(result["reviewer_output"])
        self.assertNotEqual(result["status"], "REVIEWER_OUTPUT_PRESERVED")

    def test_changed_existing_verdict_stops_reuse_without_overwrite(self):
        self.run.mkdir()
        original = self.write_verdict()
        report = {"kind": finite.REPORT_KIND, "pins": self.pins,
                  "unattended_model_use_authorized": False, "parent_credential_contents_read": False,
                  "reviewer_output": {"path": "science_output/REVIEW_VERDICT.json",
                                      "sha256": finite.sha(original)}}
        raw = finite.exclusive_json(self.run / "REPORT.json", report)
        (self.run / "REPORT.sha256").write_text(finite.sha(raw) + "\n")
        output = self.run / report["reviewer_output"]["path"]
        changed = b"changed synthetic output\n"
        output.write_bytes(changed)
        with self.assertRaises(finite.Stop):
            finite.existing(self.run, self.pins)
        self.assertEqual(output.read_bytes(), changed)

    def test_reuse_checks_exact_session_receipts_and_unrecorded_verdict(self):
        for case in ("valid", "changed", "missing", "unrecorded", "duplicate",
                     "outside", "invalid_type", "verdict"):
            with self.subTest(case=case):
                run = self.root / "delivery" / ("reuse_case_" + case)
                run.mkdir()
                session_raw = b'{"synthetic_fixture_only":true}\n'
                session = run / "synthetic_SESSION.json"
                session.write_bytes(session_raw)
                entry = {"path": session.name, "sha256": finite.sha(session_raw)}
                report = {"kind": finite.REPORT_KIND, "pins": self.pins,
                          "unattended_model_use_authorized": False,
                          "parent_credential_contents_read": False, "reviewer_output": None,
                          "preserved_session_receipts": [entry]}
                if case == "changed":
                    session.write_bytes(b"modified synthetic session\n")
                elif case == "missing":
                    session.rename(run / "preserved_but_not_original_path.json")
                elif case == "unrecorded":
                    (run / "science_SESSION.json").write_bytes(session_raw)
                elif case == "duplicate":
                    report["preserved_session_receipts"].append(dict(entry))
                elif case == "outside":
                    report["preserved_session_receipts"][0] = {"path": "../OUTSIDE.json",
                                                              "sha256": finite.sha(session_raw)}
                elif case == "invalid_type":
                    report["preserved_session_receipts"] = {"path": "synthetic_SESSION.json"}
                elif case == "verdict":
                    output = run / "science_output"
                    output.mkdir()
                    (output / "REVIEW_VERDICT.json").write_bytes(b"unrecorded synthetic verdict\n")
                raw = finite.exclusive_json(run / "REPORT.json", report)
                (run / "REPORT.sha256").write_text(finite.sha(raw) + "\n")
                before = {str(path.relative_to(run)): path.read_bytes()
                          for path in run.rglob("*") if path.is_file()}
                if case == "valid":
                    self.assertEqual(finite.existing(run, self.pins), run / "REPORT.json")
                else:
                    with self.assertRaises((finite.Stop, OSError)):
                        finite.existing(run, self.pins)
                after = {str(path.relative_to(run)): path.read_bytes()
                         for path in run.rglob("*") if path.is_file()}
                self.assertEqual(after, before)

    def stage_fixtures(self):
        self.run.mkdir()
        schema = self.root / "artifacts/GATE0_CODEX_INTERFACE/20260907_001/config-schema.json"
        schema.parent.mkdir(parents=True)
        schema.write_text("{}")
        for prompt in finite.PROMPTS.values():
            (self.root / prompt).write_text("Synthetic engineering fixture prompt\n")
        facts = {"runtime_before": {"sha256": "runtime-fixture"},
                 "bwrap_before": {"sha256": "bwrap-fixture"},
                 "identifier_bytes": b"synthetic nonsecret identity\n",
                 "runtime": self.root / "not-a-native-runtime", "auth_before": {"present": True},
                 "origins": [], "cache_origins": []}
        brokers, sessions = [], []
        class Broker:
            _failed = False
            def __init__(self, packet, manifest_sha256, output_root):
                self.packet_root, self.output_root = Path(packet), Path(output_root)
                brokers.append(self)
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def verify_inputs(self):
                return {"synthetic_integrity_fixture": True}
        def session(plan, native, requested, broker, **kwargs):
            sessions.append((native, broker, kwargs))
            self.assertNotEqual(native, broker.output_root)
            self.assertFalse(native.is_relative_to(broker.packet_root))
            self.assertFalse(broker.packet_root.is_relative_to(native))
            return {"status": "SYNTHETIC_ENGINEERING_FIXTURE"}
        modules = {
            "gate0_postlogin_metadata": types.SimpleNamespace(
                inventory=lambda *_: facts, build_live_plan=lambda *args: {"argv": ["not-launched"]}),
            "gate0_client_preflight": types.SimpleNamespace(overrides=lambda _: []),
            "p3_reviewer_profile": types.SimpleNamespace(reviewer_overrides=lambda *_: [],
                                                         cli_override_arguments=lambda _: []),
            "gate0_client_mount_plan": object(),
            "p3_review_broker": types.SimpleNamespace(ReviewBroker=Broker),
            "p3_reviewer_session": types.SimpleNamespace(run_session=session)}
        return modules, brokers, sessions

    def test_run_stages_use_disjoint_native_and_broker_directories(self):
        modules, brokers, sessions = self.stage_fixtures()
        with mock.patch.object(finite, "module", side_effect=lambda name: modules[name]), \
             mock.patch.object(finite, "host_checks", return_value={"all_noncredential_checks_pass": True}):
            for mode in ("synthetic", "science"):
                finite.run_stage(self.scope, {}, self.run, mode, self.packet,
                                 self.scope["private_packet_manifest_sha256"],
                                 expected_binding=self.binding if mode == "science" else None)
        self.assertEqual([x[0].name for x in sessions], ["synthetic_native", "science_native"])
        self.assertEqual([b.output_root.name for b in brokers], ["synthetic_output", "science_output"])
        self.assertEqual(sessions[1][2]["expected_binding"], self.binding)
        for mode in ("synthetic", "science"):
            self.assertTrue((self.run / (mode + "_STAGE.json")).is_file())

    def test_safe_session_receipt_survives_later_host_check_exception(self):
        modules, brokers, sessions = self.stage_fixtures()
        with mock.patch.object(finite, "module", side_effect=lambda name: modules[name]), \
             mock.patch.object(finite, "host_checks", side_effect=OSError("synthetic host check failure")):
            with self.assertRaises(OSError):
                finite.run_stage(self.scope, {}, self.run, "science", self.packet,
                                 self.scope["private_packet_manifest_sha256"],
                                 expected_binding=self.binding)
        self.assertEqual(len(sessions), 1)
        receipt = self.run / "science_SESSION.json"
        self.assertEqual(json.loads(receipt.read_bytes()), {"status": "SYNTHETIC_ENGINEERING_FIXTURE"})
        self.assertFalse((self.run / "science_STAGE.json").exists())


if __name__ == "__main__":
    unittest.main()
