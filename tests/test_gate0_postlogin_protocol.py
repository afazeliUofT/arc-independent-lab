#!/usr/bin/env python3
"""Synthetic protocol tests only: no native client, network or credentials."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import signal
import sys
import tempfile
import time
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


protocol = load("gate0_postlogin_protocol")
preflight = load("gate0_client_preflight")
account = load("gate0_account_metadata")
CANARY = "SYNTHETIC_SECRET_CANARY_DO_NOT_PUBLISH_5ab71edc"

# The child is a synthetic stdio responder. It writes only the requests supplied
# by the test driver, inside TemporaryDirectory. Canary output never leaves the
# transient subprocess pipes, except inside unittest's in-memory assertions.
CHILD = r'''
import json, os, pathlib, sys, time
scenario, canary = sys.argv[1:]
def emit(x):
    print(json.dumps(x), flush=True)
for raw in sys.stdin:
    request = json.loads(raw)
    with pathlib.Path("requests.jsonl").open("a") as f:
        f.write(json.dumps(request) + "\n")
    method = request["method"]
    if method == "initialized":
        continue
    if scenario == "timeout" or (scenario == "rate_timeout" and method == "account/rateLimits/read"):
        time.sleep(20)
    if scenario == "stderr_flood":
        sys.stderr.write(canary * 100)
        sys.stderr.flush()
        time.sleep(20)
    if scenario == "stdout_flood":
        sys.stdout.write(canary * 100)
        sys.stdout.flush()
        time.sleep(20)
    if scenario in ("server_request", "server_request_timestamp"):
        notification = {"id": 99, "method": canary, "params": {"token": canary}}
        if scenario == "server_request_timestamp":
            notification["emittedAtMs"] = 1790000000000
        emit(notification)
        time.sleep(20)
    if scenario == "invalid_json":
        print('{"id":1,"result":{"secret":"' + canary + '"},"id":2}', flush=True)
        time.sleep(20)
    if scenario == "nonfinite_json":
        print('{"id":1,"result":{"secret":NaN}}', flush=True)
        time.sleep(20)
    if scenario == "deep_json":
        print('{"id":1,"result":' + '[' * 1500 + 'null' + ']' * 1500 + '}', flush=True)
        time.sleep(20)
    if scenario == "foreign_response":
        emit({"id": 99, "result": {"secret": canary}})
        time.sleep(20)
    if scenario == "ambiguous_envelope":
        emit({"id": request["id"], "result": {}, "error": {"message": canary}})
        time.sleep(20)
    if scenario == "early_exit":
        sys.stderr.write(canary)
        sys.exit(3)
    if ((scenario == "optional_errors" and method in ("account/rateLimits/read", "model/list"))
        or (scenario == "required_error" and method == "account/read")):
        emit({"id": request["id"], "error": {"code": -32001,
              "message": "auth refresh network " + canary, "data": {"token": canary}}})
        continue
    if method == "initialize":
        result = {"userAgent": canary,
                  "codexHome": os.environ.get("CODEX_HOME", str(pathlib.Path(os.environ["HOME"]) / ".codex")),
                  "platformFamily": "unix", "platformOs": "linux"}
        if scenario == "invalid_initialize":
            result["userAgent"] = 7
        if scenario == "wrong_codex_home":
            result["codexHome"] = "/synthetic/" + canary
        notification = {"method": canary, "params": {"secret": canary}}
        timestamps = {"notification_timestamp_null": None,
                      "notification_timestamp_zero": 0,
                      "notification_timestamp_native": 1790000000000,
                      "notification_timestamp_min": -(2 ** 63),
                      "notification_timestamp_max": 2 ** 63 - 1,
                      "notification_timestamp_bool": True,
                      "notification_timestamp_float": 1.5,
                      "notification_timestamp_string": canary,
                      "notification_timestamp_too_large": 2 ** 63,
                      "notification_timestamp_too_small": -(2 ** 63) - 1,
                      "notification_timestamp_array": [canary],
                      "notification_timestamp_object": {canary: canary}}
        if scenario in timestamps:
            notification["emittedAtMs"] = timestamps[scenario]
        if scenario == "notification_unknown_key":
            notification[canary] = canary
        if scenario == "notification_jsonrpc":
            notification["jsonrpc"] = "2.0"
        if scenario == "notification_invalid_method":
            notification["method"] = {canary: canary}
        emit(notification)
        print(canary, file=sys.stderr, flush=True)
    elif method == "config/read":
        result = {"config": {"approval_policy": "never", "cli_auth_credentials_store": "file",
                  "private_config": canary}, "origins": {canary: canary}, "layers": []}
        if scenario == "invalid_config":
            result["config"] = canary
    elif method == "configRequirements/read":
        result = {"requirements": {"additionalDeveloperInstructions": canary}}
    elif method == "account/read":
        result = {"account": {"type": "chatgpt", "planType": "pro", "email": canary,
                  "token": canary}, "requiresOpenaiAuth": True}
        if scenario == "invalid_account":
            result["requiresOpenaiAuth"] = canary
        if scenario == "api_key_account":
            result["account"] = {"type": "apiKey"}
        if scenario == "null_account":
            result["account"] = None
    elif method == "account/rateLimits/read":
        result = {"rateLimits": {"limitId": "codex", "limitName": canary,
                  "primary": {"usedPercent": 19, "windowDurationMins": 300,
                  "resetsAt": 1790000000}}, "rateLimitsByLimitId": {
                  "codex": {"limitId": "codex", "primary": {"usedPercent": 21},
                  "secondary": None}, canary: {"limitId": canary}},
                  "rateLimitResetCredits": {"credits": [{"id": canary}]}}
    elif method == "model/list":
        result = {"data": [{"id": "gpt-6-astra", "model": "gpt-6-astra",
                  "displayName": canary, "description": canary, "isDefault": True,
                  "hidden": False, "defaultReasoningEffort": "ultra",
                  "supportedReasoningEfforts": [{"reasoningEffort": "ultra", "description": canary},
                  {"reasoningEffort": canary, "description": canary}]},
                  {"id": canary, "model": canary}], "nextCursor": canary}
    else:
        raise RuntimeError("Forbidden or unrecognized synthetic request")
    emit({"id": request["id"], "result": result})
'''


class PrivacyAssertions:
    def assert_private(self, value):
        serialized = json.dumps(value)
        self.assertNotIn(CANARY, serialized)
        self.assertNotIn(hashlib.sha256(CANARY.encode()).hexdigest(), serialized)


class FilterTests(PrivacyAssertions, unittest.TestCase):
    def test_rate_limit_unknown_legacy_identity_is_not_called_codex(self):
        result = protocol.safe_rate_limits({"rateLimits": {"primary": {"usedPercent": 7}},
                   "rateLimitsByLimitId": {CANARY: {"limitId": CANARY}}})
        self.assertFalse(result["codex_bucket_observed"])
        self.assertFalse(result["legacy_bucket_identity_recognized"])
        self.assertEqual(result["unrecognized_bucket_count"], 1)
        self.assertFalse(result["hosted_chatgpt_allowance_verified"])
        self.assert_private(result)

    def test_rate_window_types_reject_booleans_and_secret_strings(self):
        result = protocol.safe_rate_limits({"rateLimits": {"limitId": "codex", "primary": {
                "usedPercent": True, "windowDurationMins": CANARY, "resetsAt": 2 ** 80}}})
        window = result["codex_snapshots"]["explicit_codex_legacy_entry"]["primary"]
        self.assertFalse(window["shape_recognized"])
        self.assertIsNone(window["usedPercent"])
        self.assertIsNone(window["windowDurationMins"])
        self.assertIsNone(window["resetsAt"])
        self.assert_private(result)

    def test_conflicting_codex_identity_stops(self):
        with self.assertRaises(protocol.Stop):
            protocol.safe_rate_limits({"rateLimits": {}, "rateLimitsByLimitId": {
                "codex": {"limitId": CANARY}}})

    def test_model_page_absence_with_cursor_is_not_entitlement_denial(self):
        result = protocol.safe_models({"data": [{"model": CANARY}], "nextCursor": CANARY})
        self.assertFalse(result["exact_requested_model_present_on_page"])
        self.assertTrue(result["additional_page_available"])
        self.assertFalse(result["model_entitlement_verified"])
        self.assert_private(result)

    def test_model_exact_field_match_is_distinct_from_id_match(self):
        row = {"id": "gpt-6-astra", "model": CANARY, "isDefault": False, "hidden": False,
               "defaultReasoningEffort": CANARY,
               "supportedReasoningEfforts": [{"reasoningEffort": "ultra"}, {"reasoningEffort": CANARY}]}
        result = protocol.safe_models({"data": [row]})
        self.assertFalse(result["exact_requested_model_present_on_page"])
        self.assertTrue(result["exact_requested_id_present_on_page"])
        self.assertEqual(result["matching_entries"][0]["unrecognized_effort_count"], 1)
        self.assertIsNone(result["matching_entries"][0]["default_effort"])
        self.assert_private(result)

    def test_requirements_presence_does_not_retain_policy_text(self):
        result = protocol.safe_requirements({"requirements": {"network": {CANARY: CANARY},
                                                               "additionalDeveloperInstructions": CANARY}})
        self.assertTrue(result["requirements_present"])
        self.assertFalse(result["cloud_policy_provenance_verified"])
        self.assert_private(result)


class TransportTests(PrivacyAssertions, unittest.TestCase):
    def run_case(self, scenario, *, stream_limit=None, wall_seconds=None, tree_size=None,
                 method_seconds=None, module=None):
        module = module or protocol
        with tempfile.TemporaryDirectory(prefix="arc_postlogin_test_", dir=ROOT / "delivery") as name:
            run = Path(name)
            with mock.patch.object(module, "STREAM_LIMIT", stream_limit or module.STREAM_LIMIT), \
                 mock.patch.object(module, "WALL_SECONDS", wall_seconds or module.WALL_SECONDS), \
                 mock.patch.object(module, "METHOD_SECONDS", method_seconds or module.METHOD_SECONDS), \
                 mock.patch.object(module, "CLEANUP_SECONDS", 0.2 if wall_seconds else module.CLEANUP_SECONDS), \
                 mock.patch.object(preflight, "tree_size", return_value=tree_size or 0):
                result = module.observe({"argv": [sys.executable, "-u", "-c", CHILD, scenario, CANARY]},
                                          run, {"approval_policy": "never"}, preflight, account)
            path = run / "requests.jsonl"
            requests = [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []
            self.assert_private(result)
            self.assertFalse(result["thread_or_model_request_sent"])
            self.assertFalse(result["login_config_write_or_credit_operation_sent"])
            self.assertFalse(result["unattended_model_use_authorized"])
            self.assertFalse(result["raw_config_auth_or_diagnostics_saved"])
            self.assertTrue(result["native_process_reaped"])
            self.assertTrue(all(set(item) == {"bytes_observed", "raw_saved", "hashed"}
                                and not item["hashed"] and not item["raw_saved"]
                                for item in result["streams"].values()))
            self.assertEqual({path.name for path in run.iterdir()} - {"requests.jsonl"}, set())
            return result, requests

    def test_complete_sanitized_protocol_and_only_fixed_requests(self):
        result, requests = self.run_case("complete")
        self.assertEqual(result["status"], "OBSERVED_POSTLOGIN_METADATA_ONLY")
        expected = ["initialize", "initialized", "config/read", "configRequirements/read",
                    "account/read", "account/rateLimits/read", "model/list"]
        self.assertEqual([item["method"] for item in requests], expected)
        self.assertEqual(requests[4]["params"], {"refreshToken": False})
        self.assertEqual(requests[6]["params"], {"limit": 100, "includeHidden": False})
        self.assertTrue(result["live_rate_limits_response_received"])
        self.assertFalse(result["authoritative_hosted_chatgpt_allowance_verified"])
        self.assertFalse(result["contained_account"]["live_authentication_verified"])
        self.assertIn("network_enabled", result["contained_account"]["scope"])
        self.assertTrue(result["model_catalog"]["exact_requested_model_present_on_page"])
        self.assertTrue(result["model_catalog"]["matching_entries"][0]["recognized_efforts"]["ultra"])
        self.assertEqual(result["notifications_received"], 1)
        self.assertTrue(result["initialization"]["codex_home_equals_original_environment"])
        shape = result["last_notification_envelope_shape"]
        self.assertEqual(shape["emitted_at_ms_type"], "absent")
        self.assertTrue(shape["envelope_valid"])

    def test_preserved_parser_rejects_native_source_shaped_timestamp(self):
        path = ROOT / ("artifacts/GATE0_NOTIFICATION_REPAIR_ENGINEERING/20260908_001/"
                       "protocol_validation/gate0_postlogin_protocol_before.py")
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),
                         "f26b0e7513f57fa521591c5991dcfd2f1f89cad9f5bd8861e3a3a2108a8a75fa")
        spec = importlib.util.spec_from_file_location("protocol_before_notification_repair", path)
        before = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(before)
        result, requests = self.run_case("notification_timestamp_native", module=before)
        self.assertEqual(result["status"], "STOPPED_WITHOUT_REVIEW")
        self.assertEqual(result["reason"], "Invalid notification envelope")
        self.assertEqual([item["method"] for item in requests], ["initialize"])

    def test_native_timestamp_null_and_signed_64_bit_integers_are_accepted(self):
        for suffix in ("null", "zero", "native", "min", "max"):
            with self.subTest(suffix=suffix):
                result, requests = self.run_case("notification_timestamp_" + suffix)
                self.assertEqual(result["status"], "OBSERVED_POSTLOGIN_METADATA_ONLY")
                self.assertEqual(len(requests), 7)
                shape = result["last_notification_envelope_shape"]
                self.assertTrue(shape["known_key_presence"]["emittedAtMs"])
                self.assertEqual(shape["emitted_at_ms_type"], "null" if suffix == "null" else "integer")
                self.assertTrue(shape["emitted_at_ms_type_and_range_valid"])
                self.assertTrue(shape["envelope_valid"])
                self.assertEqual(shape["unknown_key_count"], 0)

    def test_invalid_timestamp_types_and_ranges_stop_with_only_shape_diagnostics(self):
        expected_types = {"bool": "boolean", "float": "number", "string": "string",
                          "too_large": "integer", "too_small": "integer",
                          "array": "array", "object": "object"}
        for suffix, expected_type in expected_types.items():
            with self.subTest(suffix=suffix):
                result, requests = self.run_case("notification_timestamp_" + suffix)
                self.assertEqual(result["status"], "STOPPED_WITHOUT_REVIEW")
                self.assertEqual(result["reason"], "Invalid notification envelope")
                self.assertEqual(len(requests), 1)
                self.assertEqual(result["notifications_received"], 0)
                shape = result["last_notification_envelope_shape"]
                self.assertEqual(shape["emitted_at_ms_type"], expected_type)
                self.assertFalse(shape["emitted_at_ms_type_and_range_valid"])
                self.assertFalse(shape["envelope_valid"])

    def test_unknown_notification_keys_and_invalid_method_are_still_rejected(self):
        for scenario in ("notification_unknown_key", "notification_jsonrpc", "notification_invalid_method"):
            with self.subTest(scenario=scenario):
                result, requests = self.run_case(scenario)
                self.assertEqual(result["status"], "STOPPED_WITHOUT_REVIEW")
                self.assertEqual(result["reason"], "Invalid notification envelope")
                self.assertEqual(len(requests), 1)
                shape = result["last_notification_envelope_shape"]
                self.assertFalse(shape["envelope_valid"])
                self.assertEqual(shape["unknown_key_count"], 0 if scenario == "notification_invalid_method" else 1)
                self.assertEqual(shape["method_type_valid"], scenario != "notification_invalid_method")

    def test_optional_errors_do_not_repeat_or_abort_remaining_metadata(self):
        result, requests = self.run_case("optional_errors")
        self.assertEqual(result["status"], "OBSERVED_POSTLOGIN_METADATA_ONLY")
        self.assertEqual(len(result["responses"]), 6)
        self.assertEqual(len(requests), 7)
        self.assertFalse(result["live_rate_limits_response_received"])
        for response in result["responses"][-2:]:
            self.assertFalse(response["success"])
            self.assertEqual(response["error"]["code"], -32001)
            self.assertTrue(response["error"]["categories_observed"]["refresh"])

    def test_required_account_error_stops_before_rate_and_model_metadata(self):
        result, requests = self.run_case("required_error")
        self.assertEqual(result["status"], "STOPPED_WITHOUT_REVIEW")
        self.assertEqual(requests[-1]["method"], "account/read")
        self.assertNotIn("account/rateLimits/read", result["requests_sent"])

    def test_server_request_gets_no_response(self):
        for scenario in ("server_request", "server_request_timestamp"):
            with self.subTest(scenario=scenario):
                result, requests = self.run_case(scenario)
                self.assertEqual(result["status"], "STOPPED_WITHOUT_REVIEW")
                self.assertEqual(result["reason"], "Unexpected server request; no response dispatched")
                self.assertEqual(len(requests), 1)
                self.assertEqual(result["server_requests_dispatched"], 0)
                self.assertFalse(result["last_notification_envelope_shape"]["envelope_valid"])
                self.assertTrue(all("result" not in item and "error" not in item for item in requests))

    def test_duplicate_keys_nonfinite_foreign_and_ambiguous_envelopes_stop(self):
        for scenario in ("invalid_json", "nonfinite_json", "deep_json", "foreign_response", "ambiguous_envelope"):
            with self.subTest(scenario=scenario):
                result, requests = self.run_case(scenario)
                self.assertEqual(result["status"], "STOPPED_WITHOUT_REVIEW")
                self.assertEqual(len(requests), 1)

    def test_invalid_required_config_or_account_shape_stops(self):
        for scenario in ("invalid_initialize", "wrong_codex_home", "invalid_config", "invalid_account"):
            with self.subTest(scenario=scenario):
                result, requests = self.run_case(scenario)
                self.assertEqual(result["status"], "STOPPED_WITHOUT_REVIEW")
                self.assertNotIn("account/rateLimits/read", result["requests_sent"])

    def test_null_or_api_key_cached_account_stops_before_live_metadata(self):
        for scenario in ("null_account", "api_key_account"):
            with self.subTest(scenario=scenario):
                result, requests = self.run_case(scenario)
                self.assertEqual(result["status"], "STOPPED_WITHOUT_REVIEW")
                self.assertEqual(requests[-1]["method"], "account/read")
                self.assertEqual(result["responses"][-1], {
                    "method": "account/read", "received": True, "success": True})
                self.assertIn("contained_account", result)
                self.assertNotIn("account/rateLimits/read", result["requests_sent"])

    def test_stdout_and_stderr_stream_limits_stop_without_saved_data(self):
        for scenario in ("stdout_flood", "stderr_flood"):
            with self.subTest(scenario=scenario):
                result, _ = self.run_case(scenario, stream_limit=512)
                self.assertEqual(result["status"], "STOPPED_WITHOUT_REVIEW")
                self.assertEqual(result["reason"], "Protocol/diagnostic stream ceiling")

    def test_deadline_stops_and_reaps_synthetic_child(self):
        result, _ = self.run_case("timeout", wall_seconds=0.6)
        self.assertEqual(result["status"], "STOPPED_WITHOUT_REVIEW")
        self.assertEqual(result["reason"], "Metadata observation deadline")
        self.assertLess(result["elapsed_seconds"], 1.5)

    def test_optional_method_timeout_preserves_account_and_does_not_send_next(self):
        result, requests = self.run_case("rate_timeout", method_seconds=0.2)
        self.assertEqual(result["status"], "STOPPED_WITHOUT_REVIEW")
        self.assertEqual(result["timed_out_method"], "account/rateLimits/read")
        self.assertIn("contained_account", result)
        self.assertEqual(requests[-1]["method"], "account/rateLimits/read")
        self.assertNotIn("model/list", result["requests_sent"])

    def test_polled_runtime_tree_ceiling_stops(self):
        result, _ = self.run_case("complete", tree_size=protocol.TREE_LIMIT + 1)
        self.assertEqual(result["status"], "STOPPED_WITHOUT_REVIEW")
        self.assertEqual(result["reason"], "Runtime tree byte ceiling")

    def test_early_process_exit_records_failure_without_diagnostic_text(self):
        result, _ = self.run_case("early_exit")
        self.assertEqual(result["status"], "STOPPED_WITHOUT_REVIEW")
        self.assertEqual(result["client_exit_code"], 3)

    def test_launch_error_does_not_echo_native_error_or_paths(self):
        with mock.patch.object(protocol.subprocess, "Popen", side_effect=OSError(CANARY)):
            result = protocol.observe({"argv": ["synthetic-unused"]}, ROOT / "delivery", {}, preflight, account)
        self.assertFalse(result["client_started"])
        self.assertEqual(result["status"], "STOPPED_WITHOUT_REVIEW")
        self.assert_private(result)

    def test_cleanup_signals_group_after_direct_child_already_exited(self):
        process = mock.Mock(pid=123456)
        process.poll.return_value = 0
        process.wait.return_value = 0
        with mock.patch.object(protocol.os, "killpg") as kill:
            self.assertTrue(protocol._stop_process(process, time.monotonic() + 4))
        self.assertEqual(kill.call_args_list, [mock.call(123456, signal.SIGTERM),
                                               mock.call(123456, signal.SIGKILL)])


if __name__ == "__main__":
    unittest.main()
