#!/usr/bin/env python3
"""Offline engineering fixtures; no native client, authentication or model use.

The pipe responder is a local Python test double with fixed JSON fixtures. The
session transport, full022 admission, unchanged protocol boundary and unchanged
real ReviewBroker run in the integration tests. No scientific verdict is made.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import p3_reviewer_session_024 as session
import p3_deprecation_notice as notice

SOURCE = ROOT / "artifacts/P3_DEPRECATION_SOURCE/20260909_REBUILD024"
SOURCE_NOTICES = json.loads((SOURCE / "EXPECTED_NOTICES.json").read_text())["notices"]
PAIRS = [{key: row[key] for key in ("summary", "details")} for row in SOURCE_NOTICES]
CANARY = "PRIVATE_NATIVE_NOTICE_MUST_NOT_APPEAR_24c4fe32"


def notification(params, **extra):
    return {"method": "deprecationNotice", "params": params, **extra}


def restrictive_profile(run=Path("/synthetic/reviewer")):
    schema = (ROOT / "artifacts/GATE0_CODEX_INTERFACE/20260907_001/config-schema.json").read_bytes()
    return session.profile.reviewer_overrides(session.preflight.overrides(run), schema)


def source_profile():
    result = {}
    for row in SOURCE_NOTICES:
        result[row["override_key"]] = False
        result["features." + row["canonical"]] = False
    result["web_search"] = "disabled"
    return result


class ClassifierTests(unittest.TestCase):
    def classify(self, params=None, **changes):
        context = {"requested": source_profile(), "profile_admitted": True,
                   "thread_requested": True, "startup_window_open": True,
                   "accepted_categories": set()}
        context.update(changes)
        return notice.classify(PAIRS[0] if params is None else params, **context)

    def test_exact_eight_pairs_equal_independently_saved_upstream_fixture(self):
        self.assertEqual(set(notice.EXACT_PAIRS),
                         {(row["summary"], row["details"]) for row in SOURCE_NOTICES})
        self.assertEqual(len(notice.EXACT_PAIRS), 8)
        accepted = set()
        for pair in PAIRS:
            result = self.classify(pair, accepted_categories=accepted)
            self.assertTrue(result["admitted"])
            accepted.add(result["category"])
            self.assertFalse(result["raw_content_saved_or_hashed"])
            self.assertNotIn(pair["summary"], json.dumps(result))
            self.assertNotIn(pair["details"], json.dumps(result))
        self.assertEqual(len(accepted), 8)

    def test_full_exact_pair_required_no_prefix_trim_case_or_cross_pair_matches(self):
        alterations = []
        for key in ("summary", "details"):
            for changed in (PAIRS[0][key] + " ", " " + PAIRS[0][key],
                            PAIRS[0][key].upper(), PAIRS[0][key] + CANARY,
                            PAIRS[0][key][:-1], CANARY):
                alterations.append({**PAIRS[0], key: changed})
        alterations.append({"summary": PAIRS[0]["summary"], "details": PAIRS[1]["details"]})
        alterations.append({key: value.replace("experimental_use_unified_exec_tool",
            "use_experimental_unified_exec_tool") for key, value in PAIRS[3].items()})
        for value in alterations:
            with self.subTest(value_type=type(value).__name__):
                result = self.classify(value)
                self.assertFalse(result["admitted"])
                self.assertNotIn(CANARY, json.dumps(result))
                for native_value in value.values():
                    self.assertNotIn(hashlib.sha256(native_value.encode()).hexdigest(),
                                     json.dumps(result))

    def test_malformed_and_extended_parameter_shapes_refused(self):
        for value in ([], "bad", 0, True, {"summary": PAIRS[0]["summary"]},
                      {"details": PAIRS[0]["details"]}, {**PAIRS[0], "details": None},
                      {**PAIRS[0], "summary": 0}, {**PAIRS[0], "details": []},
                      {**PAIRS[0], "threadId": CANARY}, {**PAIRS[0], CANARY: CANARY}):
            result = self.classify(value)
            self.assertFalse(result["admitted"])
            self.assertEqual(result["decision"], "unsupported_notice_shape")
            self.assertNotIn(CANARY, json.dumps(result))

    def test_all_related_controls_require_present_literal_false(self):
        for key in source_profile():
            for value in (None, True, 0, "false", {"enabled": False}):
                changed = source_profile()
                changed[key] = value
                with self.subTest(key=key, value_type=type(value).__name__):
                    self.assertFalse(self.classify(requested=changed)["admitted"])
            missing = source_profile()
            del missing[key]
            self.assertFalse(self.classify(requested=missing)["admitted"])

    def test_web_live_cached_or_indexed_is_never_admitted(self):
        for value in ("live", "cached", "indexed", "Disabled", "disabled "):
            self.assertFalse(self.classify(requested={**source_profile(),
                "web_search": value})["admitted"])

    def test_exact_context_booleans_and_valid_history_required(self):
        for field in ("profile_admitted", "thread_requested", "startup_window_open"):
            for value in (False, None, 1, "true"):
                self.assertFalse(self.classify(**{field: value})["admitted"])
        for value in (None, [], {}, {CANARY}, {False}):
            result = self.classify(accepted_categories=value)
            self.assertFalse(result["admitted"])
            self.assertNotIn(CANARY, json.dumps(result))

    def test_duplicates_including_ninth_notice_are_terminal(self):
        first = self.classify()
        self.assertEqual(self.classify(accepted_categories={first["category"]})["decision"],
                         "repeated_notice")
        self.assertFalse(self.classify(accepted_categories=set(notice.CATEGORIES))["admitted"])


class EventTests(unittest.TestCase):
    def events(self):
        value = session._Events("synthetic prompt")
        value.initialized = value.thread_requested = True
        value.admit_notice_profile(restrictive_profile())
        value.thread_id, value.turn_id = "thread-test", "turn-test"
        return value

    def test_empty_turn_response_preserves_startup_notice_window(self):
        value = self.events()
        self.assertEqual(value.turn({"id": "turn-test", "items": [],
            "status": "inProgress"}), "turn-test")
        value.accept(notification(PAIRS[0]))
        self.assertTrue(value.startup_window_open)

    def test_nonempty_turn_response_closes_startup_notice_window(self):
        value = self.events()
        value.turn({"id": "turn-test", "items": [{"id": "item-test",
                    "type": "reasoning"}], "status": "inProgress"})
        with self.assertRaises(session.Stop):
            value.accept(notification(PAIRS[0]))
        self.assertEqual(value.deprecation_notices[-1]["decision"], "startup_window_closed")

    def test_activity_notifications_close_window_even_without_response_items(self):
        fixtures = [
            {"method": "item/started", "params": {"threadId": "thread-test",
                "turnId": "turn-test", "item": {"id": "item-test", "type": "reasoning"}}},
            {"method": "turn/started", "params": {"threadId": "thread-test",
                "turn": {"id": "turn-test", "items": [], "status": "inProgress"}}},
            {"method": "thread/tokenUsage/updated", "params": {"threadId": "thread-test",
                "turnId": "turn-test", "tokenUsage": {}}},
            {"method": "model/verification", "params": {"threadId": "thread-test",
                "turnId": "turn-test"}},
            {"method": "thread/status/changed", "params": {"threadId": "thread-test",
                "status": {"type": "idle"}}},
        ]
        for fixture in fixtures:
            value = self.events()
            value.accept(fixture)
            with self.assertRaises(session.Stop):
                value.accept(notification(PAIRS[0]))
            self.assertEqual(value.deprecation_notices[-1]["decision"], "startup_window_closed")

    def test_thread_started_only_does_not_close_window(self):
        value = self.events()
        value.accept({"method": "thread/started", "params": {"thread": {
            "id": "thread-test", "ephemeral": True, "turns": []}}})
        value.accept(notification(PAIRS[0], emittedAtMs=1790000000000))
        self.assertTrue(value.startup_window_open)

    def test_invalid_envelope_cannot_reach_notice_classifier(self):
        for extra in ({"emittedAtMs": True}, {"emittedAtMs": 2**63}, {CANARY: CANARY}):
            value = self.events()
            with self.assertRaises(session.Stop) as error:
                value.accept(notification(PAIRS[0], **extra))
            self.assertEqual(value.deprecation_notices, [])
            self.assertNotIn(CANARY, str(error.exception))


# This child interprets fixed fixtures only. It does not import Codex, use a
# network library, read authentication, invoke tools, or write any file.
CHILD = r'''
import json, sys
fixture = json.load(open(sys.argv[1]))
def emit(value):
    print(json.dumps(value), flush=True)
for raw in sys.stdin:
    request = json.loads(raw)
    method = request.get("method")
    if method == "initialized":
        continue
    if method is None:
        for value in fixture.get("after_read", []):
            emit(value)
        continue
    for value in fixture.get("before", {}).get(method, []):
        emit(value)
    result = fixture["results"][method]
    emit({"id": request["id"], "result": result})
    for value in fixture.get("after", {}).get(method, []):
        emit(value)
'''


def effective_config(requested):
    config = {"cli_auth_credentials_store": "file"}
    origins = {}
    origin = {"name": {"type": "sessionFlags"}, "version": "fixture-version"}
    for dotted, expected in requested.items():
        target = config
        keys = dotted.split(".")
        for key in keys[:-1]:
            target = target.setdefault(key, {})
        target[keys[-1]] = copy.deepcopy(expected)
        for leaf, _ in session.admission._leaves(dotted, expected):
            origins[leaf] = copy.deepcopy(origin)
    return {"config": config, "origins": origins, "layers": [{
        **origin, "config": copy.deepcopy(config)}]}


def tool_call(rid, arguments):
    return {"id": rid, "method": "item/tool/call", "params": {
        "callId": "call-" + str(rid), "threadId": "thread-test", "turnId": "turn-test",
        "tool": "read_text", "arguments": arguments}}


class SessionTests(unittest.TestCase):
    def setUp(self):
        temp_root = ROOT / "delivery/p3_deprecation_tests_024"
        temp_root.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix="offline-", dir=temp_root)
        self.root = Path(self.temporary.name)
        self.run = self.root / "run"
        self.run.mkdir()
        self.packet = self.root / "packet"
        self.packet.mkdir()
        self.output = self.root / "output"
        self.output.mkdir()
        data = b"SYNTHETIC ENGINEERING CANARY ONLY\n"
        (self.packet / "CANARY.txt").write_bytes(data)
        manifest = json.dumps({"schema_version": 1, "files": [{"path": "CANARY.txt",
            "sha256": hashlib.sha256(data).hexdigest(), "kind": "text"}]}).encode()
        (self.packet / "BROKER_MANIFEST.json").write_bytes(manifest)
        self.manifest_sha = hashlib.sha256(manifest).hexdigest()
        self.requested = restrictive_profile(self.run)
        import os
        expected_home = os.environ.get("CODEX_HOME", str(Path(os.environ["HOME"]) / ".codex"))
        thread = {"id": "thread-test", "sessionId": "session-test", "ephemeral": True,
            "cwd": str(self.run), "modelProvider": "openai", "cliVersion": "0.151.0",
            "turns": [], "preview": "", "status": {"type": "idle"}}
        self.fixture = {"results": {
            "initialize": {"userAgent": "offline-fixture", "codexHome": expected_home,
                "platformFamily": "unix", "platformOs": "linux"},
            "config/read": effective_config(self.requested),
            "configRequirements/read": {"requirements": None},
            "account/read": {"account": {"type": "chatgpt", "planType": "pro"},
                "requiresOpenaiAuth": True},
            "account/rateLimits/read": {"rateLimits": {"limitId": "codex",
                "primary": {"usedPercent": 1}}},
            "model/list": {"data": [{"id": "gpt-5.6-sol", "model": "gpt-5.6-sol",
                "isDefault": False, "hidden": False, "defaultReasoningEffort": "max",
                "supportedReasoningEfforts": [{"reasoningEffort": "max"},
                                              {"reasoningEffort": "ultra"}]}], "nextCursor": None},
            "thread/start": {"thread": thread, "model": "gpt-5.6-sol", "modelProvider": "openai",
                "reasoningEffort": "max", "approvalPolicy": "never", "approvalsReviewer": "user",
                "activePermissionProfile": {"id": ":read-only"}, "sandbox": {"type": "readOnly"},
                "cwd": str(self.run), "runtimeWorkspaceRoots": [], "instructionSources": []},
            "turn/start": {"turn": {"id": "turn-test", "items": [], "status": "inProgress"}},
        }, "before": {"turn/start": [{"method": "thread/started", "params": {"thread": thread}}]
                    + [notification(pair) for pair in PAIRS]},
           "after": {"turn/start": [tool_call(101, session.SYNTHETIC_READ)]},
           "after_read": [tool_call(102, session.SYNTHETIC_FORBIDDEN)]}

    def tearDown(self):
        self.temporary.cleanup()

    def run_fixture(self):
        source = self.root / "offline_responder.py"
        source.write_text(CHILD)
        data = self.root / "fixture.json"
        data.write_text(json.dumps(self.fixture))
        with session.broker_module.ReviewBroker(self.packet, manifest_sha256=self.manifest_sha,
                output_root=self.output) as broker:
            report = session.run_session({"argv": [sys.executable, "-I", str(source), str(data)]},
                self.run, self.requested, broker, mode="synthetic", prompt="synthetic prompt",
                wall_seconds=10, max_calls=2)
        self.assertTrue(report["native_process_reaped"])
        self.assertFalse(report["verdict_submitted"])
        self.assertEqual(list(self.output.iterdir()), [])
        self.assertNotIn(CANARY, json.dumps(report))
        self.assertNotIn(hashlib.sha256(CANARY.encode()).hexdigest(), json.dumps(report))
        for pair in PAIRS:
            self.assertNotIn(pair["summary"], json.dumps(report))
            self.assertNotIn(pair["details"], json.dumps(report))
        return report

    def test_nine_buffered_frames_before_empty_turn_response_reach_real_broker_refusal(self):
        report = self.run_fixture()
        self.assertEqual(report["status"], "SYNTHETIC_REFUSAL_OBSERVED")
        self.assertEqual(report["early_frames_buffered"], 9)
        self.assertEqual(len(report["deprecation_notices"]), 8)
        self.assertTrue(all(row["admitted"] for row in report["deprecation_notices"]))
        self.assertTrue(report["synthetic_allowed_read_observed"])
        self.assertTrue(report["observed_refusal"])
        self.assertEqual(report["server_requests_dispatched"], 1)
        self.assertEqual(report["selected_binding"], {"model": "gpt-5.6-sol",
                         "id": "gpt-5.6-sol", "effort": "max"})
        self.assertEqual(report["deprecation_notice_policy"]["startup_window_closed_by"],
                         "broker_request")

    def test_duplicate_unknown_and_malformed_stop_before_any_broker_dispatch(self):
        base = copy.deepcopy(self.fixture)
        for bad in (PAIRS[0], {**PAIRS[0], "details": CANARY},
                    {**PAIRS[0], "details": None}, {**PAIRS[0], CANARY: CANARY}):
            self.fixture = copy.deepcopy(base)
            self.fixture["before"]["turn/start"] = self.fixture["before"]["turn/start"][:2]
            self.fixture["before"]["turn/start"].append(notification(bad))
            report = self.run_fixture()
            self.assertEqual(report["status"], "STOPPED_WITHOUT_VERDICT")
            self.assertEqual(report["reason"], "Deprecation notice admission refused")
            self.assertEqual(report["server_requests_dispatched"], 0)
            self.assertEqual(report["broker_receipts"], [])

    def test_notice_before_profile_or_thread_request_is_terminal(self):
        base = copy.deepcopy(self.fixture)
        for method in ("initialize", "model/list"):
            self.fixture = copy.deepcopy(base)
            self.fixture["before"] = {method: [notification(PAIRS[0])]}
            report = self.run_fixture()
            self.assertEqual(report["status"], "STOPPED_WITHOUT_VERDICT")
            self.assertEqual(report["server_requests_dispatched"], 0)
            self.assertFalse(report["thread_request_sent"])

    def test_late_buffered_notice_after_turn_activity_is_terminal(self):
        self.fixture["before"]["turn/start"].insert(1, {"method": "turn/started", "params": {
            "threadId": "thread-test", "turn": {"id": "turn-test", "items": [],
                                                   "status": "inProgress"}}})
        report = self.run_fixture()
        self.assertEqual(report["deprecation_notices"][0]["decision"], "startup_window_closed")
        self.assertEqual(report["server_requests_dispatched"], 0)

    def test_nonempty_rpc_response_closes_window_before_draining_buffered_notices(self):
        self.fixture["results"]["turn/start"]["turn"]["items"] = [
            {"id": "item-test", "type": "reasoning"}]
        report = self.run_fixture()
        self.assertEqual(report["early_frames_buffered"], 9)
        self.assertEqual(report["deprecation_notices"][0]["decision"], "startup_window_closed")
        self.assertEqual(report["deprecation_notice_policy"]["startup_window_closed_by"],
                         "activity_item")
        self.assertEqual(report["server_requests_dispatched"], 0)

    def test_notice_after_real_broker_read_is_terminal(self):
        self.fixture["before"]["turn/start"] = self.fixture["before"]["turn/start"][:1]
        self.fixture["after_read"] = [notification(PAIRS[0])]
        report = self.run_fixture()
        self.assertEqual(report["deprecation_notices"][0]["decision"], "startup_window_closed")
        self.assertEqual(report["server_requests_dispatched"], 1)
        self.assertTrue(report["synthetic_allowed_read_observed"])
        self.assertFalse(report["observed_refusal"])

    def test_effective_config_failure_cannot_mark_profile_admitted_or_request_thread(self):
        config = self.fixture["results"]["config/read"]
        config["config"]["features"]["hooks"] = True
        report = self.run_fixture()
        self.assertFalse(report["deprecation_notice_policy"]["profile_admitted"])
        self.assertFalse(report["thread_request_sent"])
        self.assertFalse(report["model_turn_request_sent"])

    def test_admitted_but_enabled_alias_profile_cannot_accept_notice(self):
        self.requested["features.codex_hooks"] = True
        self.fixture["results"]["config/read"] = effective_config(self.requested)
        report = self.run_fixture()
        self.assertEqual(report["deprecation_notices"][0]["decision"],
                         "restrictive_profile_not_admitted")
        self.assertEqual(report["server_requests_dispatched"], 0)

    def test_existing_config_warning_rule_is_preserved(self):
        self.fixture["after"]["initialize"] = [{"method": "configWarning", "params": {
            "summary": session.config_warning.MISSING_BWRAP_SUMMARY, "details": None}}]
        report = self.run_fixture()
        self.assertEqual(report["status"], "SYNTHETIC_REFUSAL_OBSERVED")
        self.assertEqual(len(report["config_warnings"]), 1)
        self.assertTrue(report["config_warnings"][0]["admitted"])


if __name__ == "__main__":
    unittest.main()
