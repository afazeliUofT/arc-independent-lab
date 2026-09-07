#!/usr/bin/env python3
"""One bounded, network-disabled account observation in the canonical WSL lab.

No model, login, quota, keyring socket, credential copy or network grant. Default
inspects only. --run-account writes a single fixed step directory. Repeating a
completed command verifies and reopens its report; it never starts another client.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import os
import shlex

ROOT = Path(__file__).resolve().parents[1]
RUN_NAME = "GATE0_ACCOUNT_METADATA_013"
DRIVER_NAMES = (
    "scripts/gate0_client_preflight.py", "scripts/gate0_client_mount_plan.py",
    "scripts/gate0_account_metadata.py", "scripts/gate0_config_controls.py")
BACKENDS = ("file", "keyring", "auto", "ephemeral")
ACCOUNT_KINDS = ("apiKey", "chatgpt", "amazonBedrock")
PLAN_TYPES = (
    "free", "go", "plus", "pro", "prolite", "team", "self_serve_business_prolite",
    "self_serve_business_usage_based", "business", "ent26", "enterprise_cbp_automation",
    "enterprise_cbp_usage_based", "enterprise", "edu", "edu_plus", "edu_pro", "unknown")


def load_module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def safe_account_config(result):
    """Only enumerations/booleans; never output raw provider or credential config."""
    config = result.get("config") if type(result) is dict else None
    config = config if type(config) is dict else {}
    value = config.get("cli_auth_credentials_store")
    return {
        "configured_backend_field_present": "cli_auth_credentials_store" in config,
        "configured_backend": value if type(value) is str and value in BACKENDS else None,
        "configured_backend_recognized": type(value) is str and value in BACKENDS,
        "source_default_when_absent": "file",
        "default_is_source_inference_not_runtime_attestation": True,
        "projected_tool_controls": load_module("gate0_config_controls").observe_projected_tool_controls(result),
        "host_keyring_availability_measured": False,
        "managed_requirements_verified": False,
    }


def safe_account(result):
    """Report contained cached state only; email, ids and tokens never serialized."""
    result = result if type(result) is dict else {}
    account = result.get("account")
    kind = account.get("type") if type(account) is dict else None
    plan = account.get("planType") if type(account) is dict else None
    required = result.get("requiresOpenaiAuth")
    account_valid = account is None or (type(kind) is str and kind in ACCOUNT_KINDS)
    return {
        "response_shape_recognized": type(required) is bool and account_valid,
        "account_field_present": "account" in result,
        "account_present": account is not None,
        "account_kind": kind if type(kind) is str and kind in ACCOUNT_KINDS else None,
        "requires_openai_auth": required if type(required) is bool else None,
        "reported_plan_type": plan if kind == "chatgpt" and type(plan) is str and plan in PLAN_TYPES else None,
        "reported_plan_type_recognized": kind == "chatgpt" and type(plan) is str and plan in PLAN_TYPES,
        "scope": "cached_account_available_inside_this_network_disabled_namespace",
        "live_authentication_verified": False,
        "host_login_status_verified": False,
        "model_entitlement_verified": False,
        "authoritative_allowance_observed": False,
        "scientific_review_authorized_by_this_report": False,
    }


def existing_report(run, preflight):
    """Fail closed on partial run, edited receipt, changed source or foreign input."""
    if not run.exists():
        return None
    preflight.plain(run, True)
    path = preflight.plain(run / "REPORT.json")
    checksum = preflight.plain(run / "REPORT.sha256")
    preflight.require(path.stat().st_size <= 1024 * 1024 and checksum.stat().st_size == 65,
                      "Existing report exceeds its expected bounds")
    raw = path.read_bytes()
    preflight.require(checksum.read_text() == hashlib.sha256(raw).hexdigest() + "\n",
                      "Existing report digest mismatch; no new observation")
    result = preflight.parse_line(raw)
    expected = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in DRIVER_NAMES}
    preflight.require(result.get("driver_sources") == expected,
                      "Existing observation used different driver bytes; preserve it, do not rerun")
    preflight.require(result.get("model_called_by_protocol") is False and result.get("formal_verdict") is None,
                      "Existing report scope mismatch")
    return path


def print_folder_command(path):
    # This is a displayed WSL command; the Python runner does not launch Explorer.
    print('REPORT_FOLDER_COMMAND: explorer.exe "$(wslpath -w ' + shlex.quote(str(path.parent)) + ')"')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-account", action="store_true")
    args = parser.parse_args()
    preflight = load_module("gate0_client_preflight")
    try:
        preflight.require(ROOT == Path.home() / "ARC_Independent_Lab", "Run only in canonical ~/ARC_Independent_Lab")
        delivery = preflight.plain(ROOT / "delivery", True)
        prior = existing_report(delivery / RUN_NAME, preflight)
        if prior:
            print("Existing observation verified; client was not rerun.")
            print("REPORT: " + str(prior))
            print("REPORT_SHA256: " + hashlib.sha256(prior.read_bytes()).hexdigest())
            print_folder_command(prior)
            return
        facts = preflight.inventory()
        print("Exact runtime and original inputs inspected; credential contents were not read by the parent.")
        print("Next observation: contained cached account/read(refreshToken=false), network disabled, no model turn.")
        if not args.run_account:
            print("Inspection only. No client, network or filesystem change was made.")
            return
        path = preflight.run_preflight(facts, account_status=True)
        checksum = hashlib.sha256(path.read_bytes()).hexdigest() + "\n"
        with (path.parent / "REPORT.sha256").open("x") as stream:
            stream.write(checksum); stream.flush(); os.fsync(stream.fileno())
        preflight.require(existing_report(path.parent, preflight) == path, "Final account report verification failed")
        print_folder_command(path)
    except (preflight.Stop, OSError, ValueError) as error:
        # Config/credential/system exceptions can carry secrets. No raw repr.
        reason = str(error) if isinstance(error, preflight.Stop) else "Incomplete prior step or required input/report unavailable"
        print("STOP: " + reason + ". Preserve the fixed step directory; no automatic retry or repair.")
        raise SystemExit(2)


if __name__ == "__main__":
    main()
