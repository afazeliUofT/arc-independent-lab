"""Exercise the real024 approval and receipt consumers with temporary files.

These engineering checks do not start a native client, call a model, inspect
credentials, or alter the lab's recorded escalation or historical approvals.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


LAB = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "p3_finite_review_024_tested", LAB / "scripts/p3_finite_review_024.py")
finite = importlib.util.module_from_spec(spec)
spec.loader.exec_module(finite)


class FiniteReview024ConsumerTests(unittest.TestCase):
    def setUp(self):
        fixture = tempfile.TemporaryDirectory(
            prefix="finite_review_024_approval_", dir=LAB)
        self.addCleanup(fixture.cleanup)
        self.root = Path(fixture.name)
        (self.root / "state").mkdir()
        patch_root = mock.patch.object(finite, "ROOT", self.root)
        patch_root.start()
        self.addCleanup(patch_root.stop)
        self.scope = {"approval_id": "APPROVE_P3_FINITE_REVIEW_024_CORRECTION"}
        self.answer = (
            "## ANSWER\n" + self.scope["approval_id"] +
            "\nscope_sha256: " + finite.SCOPE_SHA256 + "\n")

    def write_state(self, text, archive=False):
        relative = finite.APPROVAL_ARCHIVE if archive else "state/ESCALATION.md"
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = text.encode("utf-8")
        path.write_bytes(raw)
        return {"path": relative, "sha256": hashlib.sha256(raw).hexdigest()}

    def test_exact_actual_answer_returns_current_document_receipt(self):
        for text in (
                self.answer,
                "# Finite review request\n\n## QUESTION\nUnsigned request prose.\n\n" + self.answer,
                "## ANSWER\n\n" + self.scope["approval_id"] +
                "\n \nscope_sha256: " + finite.SCOPE_SHA256 + "\n\n\t\n"):
            # Whitespace-only lines are permitted; response lines stay exact.
            with self.subTest(text=text):
                receipt = self.write_state(text)
                self.assertEqual(finite.approval(self.scope), receipt)

    def test_wrong_approval_identity_or_scope_hash_is_rejected(self):
        wrong_hash = ("0" if finite.SCOPE_SHA256[0] != "0" else "1") + finite.SCOPE_SHA256[1:]
        cases = {
            "previous Sol approval": self.answer.replace(
                self.scope["approval_id"], "APPROVE_P3_FINITE_REVIEW_022_SOL"),
            "wrong024 approval": self.answer.replace(
                self.scope["approval_id"], "APPROVE_P3_FINITE_REVIEW_024"),
            "wrong hash": self.answer.replace(finite.SCOPE_SHA256, wrong_hash),
            "missing hash": "## ANSWER\n" + self.scope["approval_id"] + "\n",
            "hash key spacing": self.answer.replace("scope_sha256: ", "scope_sha256:"),
            "approval leading space": self.answer.replace(
                self.scope["approval_id"], " " + self.scope["approval_id"]),
        }
        for label, text in cases.items():
            with self.subTest(case=label):
                self.write_state(text)
                with self.assertRaises(finite.Stop):
                    finite.approval(self.scope)

    def test_duplicate_fenced_or_nonactual_answer_headings_are_rejected(self):
        cases = {
            "duplicate actual headings": self.answer + self.answer,
            "backtick fence": "```markdown\n" + self.answer + "```\n",
            "tilde fence": "~~~\n" + self.answer + "~~~\n",
            "indented fence": "   ```\n" + self.answer + "   ```\n",
            "unclosed fence": "```\n" + self.answer,
            "invalid fence close": "```\nquoted\n```still-fenced\n" + self.answer,
            "indented heading": self.answer.replace("## ANSWER", "    ## ANSWER"),
            "blockquote heading": self.answer.replace("## ANSWER", "> ## ANSWER"),
            "inline-only response": self.scope["approval_id"] +
                " scope_sha256: " + finite.SCOPE_SHA256 + "\n",
            "inline heading response": self.answer.replace("## ANSWER\n", "## ANSWER "),
        }
        for label, text in cases.items():
            with self.subTest(case=label):
                self.write_state(text)
                with self.assertRaises(finite.Stop):
                    finite.approval(self.scope)

    def test_html_comment_delimiters_anywhere_are_rejected(self):
        for text in (
                "<!--\n" + self.answer + "-->\n",
                "<!--\n" + self.answer,
                "-->\n" + self.answer,
                "<!-- request note -->\n" + self.answer,
                self.answer + "<!-- trailing note -->\n"):
            with self.subTest(text=text):
                self.write_state(text)
                with self.assertRaises(finite.Stop):
                    finite.approval(self.scope)

    def test_extra_response_prose_is_rejected(self):
        for text in (
                self.answer + "Proceed only if nothing changes.\n",
                self.answer + "## NOTES\nApproved.\n",
                self.answer.replace("## ANSWER\n", "## ANSWER\nI approve.\n"),
                self.answer.replace(self.scope["approval_id"],
                                    self.scope["approval_id"] + " approved")):
            with self.subTest(text=text):
                self.write_state(text)
                with self.assertRaises(finite.Stop):
                    finite.approval(self.scope)

    def test_archive_is_used_only_when_current_document_is_empty(self):
        receipt = self.write_state(self.answer, archive=True)
        for text in ("", "\n", " \t\n\n"):
            with self.subTest(current=text):
                self.write_state(text)
                self.assertEqual(finite.approval(self.scope), receipt)

    def test_nonempty_unsigned_current_document_prevents_archive_fallback(self):
        self.write_state(self.answer, archive=True)
        for text in (
                "## QUESTION\nA newer unanswered review request.\n",
                "## ANSWER\n\n",
                "The required response is " + self.scope["approval_id"] +
                " with scope_sha256: " + finite.SCOPE_SHA256 + ".\n",
                self.answer + "Only with an additional condition.\n"):
            with self.subTest(current=text):
                self.write_state(text)
                with self.assertRaises(finite.Stop):
                    finite.approval(self.scope)

    def test_valid_current_document_is_used_even_when_archive_is_unsigned(self):
        self.write_state("## QUESTION\nUnsigned archive fixture.\n", archive=True)
        receipt = self.write_state(self.answer)
        self.assertEqual(finite.approval(self.scope), receipt)

    def test_empty_current_document_with_missing_archive_is_rejected(self):
        self.write_state("")
        with self.assertRaises(finite.Stop):
            finite.approval(self.scope)

    def test_empty_current_document_with_unsigned_archive_is_rejected(self):
        self.write_state("")
        self.write_state("## QUESTION\nUnsigned archive fixture.\n", archive=True)
        with self.assertRaises(finite.Stop):
            finite.approval(self.scope)

    def test_existing_complete_receipt_is_reused_without_changes(self):
        run = self.root / "delivery" / finite.RUN_NAME
        run.mkdir(parents=True)
        pins = {"scope_sha256": finite.SCOPE_SHA256}
        report = {
            "kind": finite.REPORT_KIND,
            "pins": pins,
            "status": "STOPPED_WITHOUT_COMPLETED_REVIEW",
            "synthetic_fixture_only": True,
            "unattended_model_use_authorized": False,
            "parent_credential_contents_read": False,
            "reviewer_output": None,
            "preserved_session_receipts": [],
        }
        raw = (json.dumps(report) + "\n").encode("utf-8")
        (run / "REPORT.json").write_bytes(raw)
        checksum = (hashlib.sha256(raw).hexdigest() + "\n").encode("ascii")
        (run / "REPORT.sha256").write_bytes(checksum)
        before = {path.name: path.read_bytes() for path in run.iterdir()}
        self.assertEqual(finite.existing(run, pins), run / "REPORT.json")
        self.assertEqual({path.name: path.read_bytes() for path in run.iterdir()}, before)

    def test_nonterminal_missing_or_unknown_receipt_status_is_rejected_and_preserved(self):
        run = self.root / "delivery" / finite.RUN_NAME
        run.mkdir(parents=True)
        pins = {"scope_sha256": finite.SCOPE_SHA256}
        for status in ("STARTED", None, "SYNTHETIC_ENGINEERING_FIXTURE_ONLY"):
            with self.subTest(status=status):
                report = {
                    "kind": finite.REPORT_KIND,
                    "pins": pins,
                    "synthetic_fixture_only": True,
                    "unattended_model_use_authorized": False,
                    "parent_credential_contents_read": False,
                    "reviewer_output": None,
                    "preserved_session_receipts": [],
                }
                if status is not None:
                    report["status"] = status
                raw = (json.dumps(report) + "\n").encode("utf-8")
                (run / "REPORT.json").write_bytes(raw)
                checksum = (hashlib.sha256(raw).hexdigest() + "\n").encode("ascii")
                (run / "REPORT.sha256").write_bytes(checksum)
                before = {path.name: path.read_bytes() for path in run.iterdir()}
                with self.assertRaises(finite.Stop):
                    finite.existing(run, pins)
                self.assertEqual(
                    {path.name: path.read_bytes() for path in run.iterdir()}, before)

    def test_partial_existing_attempt_is_rejected_and_preserved(self):
        run = self.root / "delivery" / finite.RUN_NAME
        run.mkdir(parents=True)
        sentinel = run / "ATTEMPT.json"
        raw = b'{"synthetic_fixture_only":true}\n'
        sentinel.write_bytes(raw)
        with self.assertRaises((finite.Stop, OSError)):
            finite.existing(run, {"scope_sha256": finite.SCOPE_SHA256})
        self.assertEqual(sentinel.read_bytes(), raw)
        self.assertEqual([path.name for path in run.iterdir()], ["ATTEMPT.json"])

    def test_missing_attempt_has_no_receipt_and_creates_nothing(self):
        run = self.root / "delivery" / finite.RUN_NAME
        self.assertIsNone(finite.existing(run, {"scope_sha256": finite.SCOPE_SHA256}))
        self.assertFalse(run.exists())


if __name__ == "__main__":
    unittest.main()
