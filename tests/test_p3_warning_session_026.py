#!/usr/bin/env python3
"""Offline transport regressions for synthetic-only warning diagnosis.

The child is a local Python pipe responder using fixed JSON fixtures only. The
unchanged real ReviewBroker enforces the canary read and traversal refusal.
No Codex binary, authentication, network, paid API or science packet is used.
These engineering fixtures are not an independent scientific review.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
import p3_reviewer_session_026 as session
import test_p3_deprecation_correction_024 as fixtures

CANARY = "PRIVATE_WARNING_TEST_MUST_NOT_BE_RETAINED_29a5ee47"
REPORTS = []

# Each group is written atomically when it fits PIPE_BUF. That lets the tests
# distinguish frames already readable from a hypothetical startup barrier.
# Deliberately large groups additionally exercise more than one parent read.
CHILD = r'''
import json, os, sys
fixture = json.load(open(sys.argv[1]))
def emit_group(values):
    data = b"".join(json.dumps(value).encode() + b"\n" for value in values)
    while data:
        count = os.write(sys.stdout.fileno(), data)
        data = data[count:]
for raw in sys.stdin:
    request = json.loads(raw)
    method = request.get("method")
    if method == "initialized":
        continue
    if method is None:
        emit_group(fixture.get("after_read", []))
        continue
    values = fixture.get("before", {}).get(method, [])
    values = values + [{"id": request["id"], "result": fixture["results"][method]}]
    values = values + fixture.get("after", {}).get(method, [])
    emit_group(values)
'''


def warning(message=None, **extra):
    if message is None:
        message = ("Code Mode is unavailable because " + CANARY
                   + ". Falling back to direct tools; enable `features.code_mode_host`"
                   + " and install `codex-code-mode-host`.")
    return {"method": "warning", "params": {"threadId": "thread-test",
                                               "message": message}, **extra}


class WarningSessionTests(unittest.TestCase):
    # Use only setup/cleanup methods: inheriting the prior TestCase would silently
    # rerun its entire suite, obscuring the concrete new risks addressed here.
    setUp = fixtures.SessionTests.setUp
    tearDown = fixtures.SessionTests.tearDown

    def run_fixture(self, *, mode="synthetic", expected_binding=None):
        source = self.root / "offline_responder_026.py"
        source.write_text(CHILD)
        fixture = self.root / "fixture_026.json"
        fixture.write_text(json.dumps(self.fixture))
        with session.broker_module.ReviewBroker(
                self.packet, manifest_sha256=self.manifest_sha,
                output_root=self.output) as broker:
            report = session.run_session(
                {"argv": [sys.executable, "-I", str(source), str(fixture)]},
                self.run, self.requested, broker, mode=mode,
                prompt="synthetic prompt", wall_seconds=10, max_calls=2,
                expected_binding=expected_binding)
        if report["client_started"]:
            self.assertTrue(report["native_process_reaped"])
        self.assertFalse(report["verdict_submitted"])
        self.assertEqual(list(self.output.iterdir()), [])
        serialized = json.dumps(report)
        self.assertNotIn(CANARY, serialized)
        self.assertNotIn(hashlib.sha256(CANARY.encode()).hexdigest(), serialized)
        self.assertFalse(report["startup_completion_barrier_claimed"])
        self.assertTrue(report["diagnostic_only"])
        REPORTS.append({"test": self.id(), "observation": report})
        return report

    def assert_warning_stop(self, report, *, turn_sent, turn_bound=False):
        self.assertEqual(report["status"], "STOPPED_WITHOUT_VERDICT")
        self.assertEqual(report["reason"],
                         "Generic warning stopped diagnostic; safe classification preserved")
        self.assertEqual(report["last_notification_type"], "warning")
        self.assertEqual(len(report["warning_diagnostics"]), 1)
        diagnostic = report["warning_diagnostics"][0]
        self.assertEqual(diagnostic["action"], "stop")
        self.assertFalse(diagnostic["warning_admitted"])
        self.assertFalse(diagnostic["producer_identity_established"])
        self.assertFalse(diagnostic["current_observation_identifies_historical024_warning"])
        self.assertEqual(report["model_turn_request_sent"], turn_sent)
        self.assertEqual("turn/start" in report["requests_sent"], turn_sent)
        self.assertEqual(report["last_notification_observation"]["turn_bound"], turn_bound)
        self.assertEqual(report["server_requests_dispatched"], 0)
        self.assertEqual(report["broker_receipts"], [])
        return diagnostic

    def test_warning_before_thread_response_stops_without_model_turn_or_untrusted_binding(self):
        self.fixture["before"] = {"thread/start": [warning()]}
        report = self.run_fixture()
        diagnostic = self.assert_warning_stop(report, turn_sent=False)
        self.assertFalse(report["model_turn_request_queued"])
        self.assertEqual(diagnostic["envelope"], "valid_text_thread_not_bound")
        self.assertEqual(diagnostic["thread_binding"], "no_expected_thread")
        self.assertEqual(diagnostic["family"], "tools.code_mode_unavailable")
        self.assertFalse(diagnostic["text_attribution_to_active_thread"])
        self.assertFalse(report["last_notification_observation"]["thread_bound"])

    def test_warning_in_same_write_after_thread_response_prevents_queuing_model_turn(self):
        self.fixture["before"] = {}
        self.fixture["after"] = {"thread/start": [warning()]}
        report = self.run_fixture()
        diagnostic = self.assert_warning_stop(report, turn_sent=False)
        self.assertFalse(report["model_turn_request_queued"])
        self.assertEqual(diagnostic["family"], "tools.code_mode_unavailable")
        self.assertEqual(diagnostic["details"]["behavior"], "fallback_to_direct_tools")
        self.assertEqual(diagnostic["envelope"], "valid_bound")

    def test_already_available_frames_across_parent_reads_prevent_model_turn(self):
        self.fixture["before"] = {}
        # Valid benign global frames total more than the 65536-byte read size.
        # A warning follows them while the child's write remains in progress.
        padding = [{"method": "remoteControl/status/changed", "params": {
            "status": "disabled", "unretained": CANARY * 750}} for _ in range(3)]
        self.fixture["after"] = {"thread/start": padding + [warning()]}
        report = self.run_fixture()
        self.assert_warning_stop(report, turn_sent=False)
        self.assertFalse(report["model_turn_request_queued"])
        self.assertGreater(report["streams"]["stdout"]["bytes_observed"], 65536)

    def test_warning_while_turn_response_pending_stops_and_counts_sent_turn(self):
        self.fixture["before"] = {"turn/start": [warning()]}
        self.fixture["after"] = {}
        report = self.run_fixture()
        diagnostic = self.assert_warning_stop(report, turn_sent=True)
        self.assertTrue(report["model_turn_request_queued"])
        self.assertEqual(diagnostic["family"], "tools.code_mode_unavailable")
        self.assertEqual(report["early_frames_buffered"], 0)

    def test_warning_after_bound_turn_and_activity_still_stops_without_admission(self):
        self.fixture["before"] = {}
        self.fixture["after"] = {"turn/start": [{"method": "item/started", "params": {
            "threadId": "thread-test", "turnId": "turn-test",
            "item": {"id": "item-test", "type": "reasoning"}}}, warning()]}
        report = self.run_fixture()
        self.assert_warning_stop(report, turn_sent=True, turn_bound=True)
        self.assertFalse(report["last_notification_observation"]["startup_window_open"])

    def test_malformed_warning_notification_envelope_has_safe_terminal_observation(self):
        base = copy.deepcopy(self.fixture)
        for extra in ({"emittedAtMs": True}, {CANARY: CANARY}, {"id": 1000}):
            with self.subTest(extra_kind=next(iter(extra)) != CANARY):
                self.fixture = copy.deepcopy(base)
                self.fixture["before"] = {}
                self.fixture["after"] = {"thread/start": [warning(**extra)]}
                report = self.run_fixture()
                diagnostic = self.assert_warning_stop(report, turn_sent=False)
                self.assertFalse(diagnostic["notification_envelope_valid"])

    def test_malformed_warning_parameters_have_safe_terminal_observation(self):
        base = copy.deepcopy(self.fixture)
        for params in (None, [], {"threadId": "thread-test", "message": 99},
                       {"threadId": "thread-test", "message": CANARY, CANARY: CANARY}):
            self.fixture = copy.deepcopy(base)
            self.fixture["before"] = {}
            self.fixture["after"] = {"thread/start": [{"method": "warning", "params": params}]}
            report = self.run_fixture()
            diagnostic = self.assert_warning_stop(report, turn_sent=False)
            self.assertEqual(diagnostic["family"], "unknown")
            self.assertNotEqual(diagnostic["envelope"], "valid_bound")

    def test_unknown_notification_name_is_fixed_category_and_stops_before_turn(self):
        self.fixture["before"] = {}
        self.fixture["after"] = {"thread/start": [{"method": CANARY, "params": {"secret": CANARY}}]}
        report = self.run_fixture()
        self.assertEqual(report["status"], "STOPPED_WITHOUT_VERDICT")
        self.assertEqual(report["reason"], "Unadvertised native notification effect")
        self.assertEqual(report["last_notification_type"], "unknown")
        self.assertEqual(report["last_notification_observation"]["method"], "unknown")
        self.assertFalse(report["model_turn_request_queued"])
        self.assertEqual(report["warning_diagnostics"], [])

    def test_science_mode_and_binding_are_refused_before_any_child_start(self):
        for mode, binding in (("science", None), ("science", {
                "model": "gpt-5.6-sol", "id": "gpt-5.6-sol", "effort": "max"}),
                ("synthetic", {"model": "gpt-5.6-sol", "id": "gpt-5.6-sol", "effort": "max"})):
            with mock.patch.object(session.subprocess, "Popen",
                                   side_effect=AssertionError("Popen must not be called")) as popen:
                report = self.run_fixture(mode=mode, expected_binding=binding)
            popen.assert_not_called()
            self.assertFalse(report["client_started"])
            self.assertEqual(report["requests_sent"], [])
            self.assertEqual(report["reason"], "Invalid finite session input")

    def test_eight_deprecations_and_clean_canary_reach_unchanged_real_broker_refusal(self):
        report = self.run_fixture()
        self.assertEqual(report["status"], "SYNTHETIC_REFUSAL_OBSERVED")
        self.assertEqual(len(report["deprecation_notices"]), 8)
        self.assertTrue(all(row["admitted"] for row in report["deprecation_notices"]))
        self.assertEqual(report["warning_diagnostics"], [])
        self.assertTrue(report["synthetic_allowed_read_observed"])
        self.assertTrue(report["observed_refusal"])
        self.assertEqual(report["server_requests_dispatched"], 1)
        self.assertEqual(report["requests_sent"].count("turn/start"), 1)
        self.assertEqual(report["selected_binding"], {
            "model": "gpt-5.6-sol", "id": "gpt-5.6-sol", "effort": "max"})


if __name__ == "__main__":
    unittest.main()
