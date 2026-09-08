#!/usr/bin/env python3
"""One explicit correction of the approved metadata check; no new access grant.

Default inspection does not launch a client or write files. A completed report is
reused without another native process. Credentials are never opened by this parent.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat

ROOT = Path(__file__).resolve().parents[1]
SCOPE_PATH = "configs/GATE0_POSTLOGIN_SCOPE_016.json"
SCOPE_SHA256 = "fbd7ca325593c9c8de5573417faf1381dbf669b80218f85e4a31ae519beacc61"
DRIVER_PINS = {
    "scripts/gate0_client_preflight.py": "a4d0c4be8d6ade00f82285381dfa68e0310146fca300752bac3fac74d6bd3038",
    "scripts/gate0_client_mount_plan.py": "4500a10227a5209a525e5ab7534a1bd2e55e3574c91381c584e5a99c7095a107",
    "scripts/gate0_config_controls.py": "9dc478ba6c68e32be69079e154dde1f3debd4d8dbd998f7648577b5df2c4bf8d",
    "scripts/gate0_account_metadata.py": "13f4e87a7da463b6915f49df4f97b2cea271a7e8de9f16b21281db50842dac76",
    "scripts/gate0_postlogin_protocol.py": "222ed3eb698b947b0d7286991101308485f44554c823abb7723c9882d213877a",
    "scripts/gate0_postlogin_boundary.py": "aab4cb14a30bb1ee9f7b1e0d983f54fe509977bdc9d8aad7a4d8e54fbec6d20f"
}
PRIOR_RUN_NAME = "GATE0_POSTLOGIN_METADATA_016"
PRIOR_REPORT_PATH = "artifacts/GATE0_POSTLOGIN_OBSERVATIONS/20260908_001/REPORT.json"
PRIOR_REPORT_SHA256 = "4aa0757da0d56a4db65ca7a33cf15d7454129c21fab7283457261d3a8ebcbba7"
APPROVAL_ARCHIVE = "state/escalations/2026-09-08_POSTLOGIN_REFRESH_APPROVED.md"
APPROVAL_SHA256 = "73d96a954fa9f13d5d286f2153b46326577904412450996857c6e175af24214a"
RUN_NAME = "GATE0_POSTLOGIN_METADATA_016_REPAIR_001"
AUTH_RELATIVE = ".codex/auth.json"
SECRET_ENV = ("OPENAI_API_KEY", "CODEX_API_KEY", "CODEX_ACCESS_TOKEN")
REPORT_KIND = "GATE0_POSTLOGIN_METADATA_016_REPAIR_001_v1"
REPORT_KEYS = {
    "kind", "created_utc", "pins", "scope", "model_requested", "formal_verdict",
    "unattended_model_use_authorized", "mount_plan", "observation", "origin_inventory",
    "cache_origins", "network_inputs", "auth_metadata_before", "auth_metadata_after",
    "credential_contents_opened_hashed_or_copied_by_parent", "native_credential_refresh_may_have_occurred",
    "host_config_metadata_unchanged", "host_cache_metadata_unchanged", "host_runtime_unchanged",
    "host_bwrap_unchanged", "host_installation_id_unchanged", "private_installation_id_matches",
    "hosted_chatgpt_allowance_verified", "model_entitlement_verified", "full_reviewer_boundary_verified",
    "managed_policy_closure_verified", "raw_native_logs_or_protocol_in_report", "synthetic_boundary",
}


class Stop(RuntimeError):
    pass


def require(ok, message):
    if not ok:
        raise Stop(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def plain(path, directory=False):
    path = Path(path).absolute()
    require(".." not in path.parts, "Noncanonical path")
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        require(not current.is_symlink(), "Symlink in protected path")
    info = path.stat()
    require(stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode),
            "Required path has wrong type")
    require(directory or info.st_nlink == 1, "Hardlinked protected file rejected")
    return path


def bounded(path, maximum=2 * 1024 * 1024):
    path = plain(path)
    require(path.stat().st_size <= maximum, "Oversized public input")
    return path.read_bytes()


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / (name + ".py"))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def load_bundle():
    raw = bounded(ROOT / SCOPE_PATH)
    require(sha(raw) == SCOPE_SHA256, "Post-login scope differs from published bytes")
    require(bool(DRIVER_PINS), "Unfinished source pinning; no execution")
    for name, expected in DRIVER_PINS.items():
        require(sha(bounded(ROOT / name)) == expected, "Dependent source differs from published bytes")
    scope = json.loads(raw)
    receipt = bounded(ROOT / scope["signin_receipt_path"])
    require(sha(receipt) == scope["signin_receipt_sha256"], "Accepted sign-in receipt differs")
    require(sha(bounded(ROOT / PRIOR_REPORT_PATH)) == PRIOR_REPORT_SHA256,
            "Accepted failed attempt differs; preserve it")
    return scope, {
        "scope_sha256": sha(raw),
        "wrapper_sha256": sha(bounded(ROOT / "scripts/gate0_postlogin_metadata.py")),
        "driver_sources": DRIVER_PINS,
        "signin_receipt_sha256": sha(receipt),
        "prior_failed_report_sha256": PRIOR_REPORT_SHA256,
        "repair_id": "notification_envelope_001",
    }


def approval(scope):
    # Existing permission persists. A nonempty new escalation is never ignored.
    text = bounded(ROOT / "state/ESCALATION.md").decode("utf-8")
    if not text.strip():
        raw = bounded(ROOT / APPROVAL_ARCHIVE)
        require(sha(raw) == APPROVAL_SHA256, "Archived approval differs from the published human answer")
        text = raw.decode("utf-8")
    lines, headings, fence = text.splitlines(), [], None
    for i, line in enumerate(lines):
        stripped = line.lstrip(" ")
        if len(line) - len(stripped) <= 3 and stripped.startswith(("```", "~~~")):
            char = stripped[0]
            length = len(stripped) - len(stripped.lstrip(char))
            if fence is None:
                fence = (char, length)
            elif char == fence[0] and length >= fence[1]:
                fence = None
            continue
        if fence is None and line == "## ANSWER":
            headings.append(i)
    require(len(headings) == 1, "One recorded ANSWER is required before native refresh access")
    answer = [line for line in lines[headings[0] + 1:] if line.strip()]
    require(answer == [scope["approval_id"], "scope_sha256: " + SCOPE_SHA256],
            "ANSWER differs from the exact approved scope; no client launched")


def prior_observation():
    """Read only the already-shared receipt; never native logs or credentials."""
    path = ROOT / "delivery" / PRIOR_RUN_NAME / "REPORT.json"
    raw = bounded(path)
    require(sha(raw) == PRIOR_REPORT_SHA256, "Original local failed report differs; preserve it")
    require(bounded(path.parent / "REPORT.sha256", 65) == (PRIOR_REPORT_SHA256 + "\n").encode(),
            "Original receipt checksum differs; preserve it")
    prior = json.loads(raw)
    require(prior["pins"]["scope_sha256"] == SCOPE_SHA256
            and prior["synthetic_boundary"]["passed"] is True,
            "Accepted prerequisite observation is unavailable")
    return path, prior


def reuse_boundary(facts, prior):
    """Reuse the passed prerequisite, explicitly not a fresh kernel attestation."""
    require(prior["pins"]["driver_sources"]["scripts/gate0_postlogin_boundary.py"] ==
            DRIVER_PINS["scripts/gate0_postlogin_boundary.py"], "Boundary implementation changed")
    require(prior["pins"]["driver_sources"]["scripts/gate0_client_mount_plan.py"] ==
            DRIVER_PINS["scripts/gate0_client_mount_plan.py"], "Mount planner changed")
    # Actual executable checks were made by inventory against the unchanged scope.
    require(facts["bwrap_before"]["sha256"] == "52231e1caf55bcbc667b269f49c63599a6f7db4767ae6a039580d0ff853db712",
            "Namespace executable changed since the passing prerequisite")
    return {"kind": "GATE0_POSTLOGIN_SYNTHETIC_BIND_REUSED_v1", "passed": True,
            "executed_this_attempt": False, "prior_report_path": PRIOR_REPORT_PATH,
            "prior_report_sha256": PRIOR_REPORT_SHA256,
            "same_boundary_implementation_and_bwrap_verified": True,
            "fresh_kernel_or_full_reviewer_attestation": False}


def exact_network_inputs():
    """Only fixed resolver/CA paths, with exact symlink targets; no directory grants."""
    result = []
    for name in ("/etc/resolv.conf", "/etc/hosts", "/etc/nsswitch.conf",
                 "/etc/ssl/certs/ca-certificates.crt"):
        path = Path(name)
        if not os.path.lexists(path):
            require(name not in ("/etc/resolv.conf", "/etc/ssl/certs/ca-certificates.crt"),
                    "Required resolver or CA file is absent")
            continue
        target = path.resolve(strict=True)
        require(target.is_file() and target.stat().st_nlink == 1, "Network dependency is not one ordinary file")
        require(not target.is_relative_to(Path.home()) and "ARC_AGI3_Plasticity_Lab" not in target.parts,
                "Network dependency resolves into a user programme")
        info = target.stat()
        require(info.st_size <= 2 * 1024 * 1024, "Network dependency exceeds bounds")
        result.append({"source": str(target), "destination": name, "access": "read",
                       "metadata": metadata(target)})
    return result


def metadata(path):
    # In particular, no credential content or content-derived hash is read.
    info = path.stat()
    return {"device": info.st_dev, "inode": info.st_ino, "bytes": info.st_size,
            "mode": stat.S_IMODE(info.st_mode), "mtime_ns": info.st_mtime_ns,
            "ctime_ns": info.st_ctime_ns}


def inventory(scope, preflight):
    require(Path.home() == Path(scope["canonical_home"]) and ROOT == Path(scope["canonical_project"]),
            "Use the existing canonical WSL project and home")
    require(os.environ.get("HOME") == scope["canonical_home"], "HOME provenance differs")
    codex_home = Path.home() / ".codex"
    require("CODEX_HOME" not in os.environ or os.environ["CODEX_HOME"] == str(codex_home),
            "CODEX_HOME provenance differs; do not change it")
    require(not any(name in os.environ for name in SECRET_ENV), "Credential environment variable present; no value read")
    facts = preflight.inventory()
    require(facts["bwrap_before"]["sha256"] == scope["bwrap_sha256"], "Bubblewrap differs from observed binary")
    require(facts["runtime_before"]["sha256"] == scope["runtime_sha256"], "Native runtime differs")
    auth = plain(Path.home() / AUTH_RELATIVE)
    auth_info = auth.stat()
    require(stat.S_IMODE(auth_info.st_mode) == 0o600 and auth_info.st_uid == os.getuid(),
            "Credential file must already be owned by this user and mode0600")
    prelogin_raw = bounded(ROOT / scope["prelogin_report_path"])
    require(sha(prelogin_raw) == scope["prelogin_report_sha256"], "Accepted pre-login evidence differs")
    before = json.loads(prelogin_raw)
    old = {item["path"]: item for item in before["origin_inventory"]}
    current = {item["path"]: item for item in facts["origins"]}
    require(set(old) == set(current), "Configuration origin inventory changed")
    for name in old:
        if name == str(auth):
            require(current[name]["present"], "Native credential path missing")
        else:
            require(current[name] == old[name], "Configuration provenance changed since the accepted observation")
    cache_origins = []
    for basename in ("cloud-config-bundle-cache.json", "models_cache.json"):
        path = codex_home / basename
        require(not path.is_symlink(), "Metadata cache is a symlink")
        item = {"path": str(path), "present": path.exists()}
        if item["present"]:
            plain(path)
            item["metadata"] = metadata(path)
            facts["readonly_paths"].append(path)
        cache_origins.append(item)
    facts.update({"auth": auth, "auth_before": metadata(auth),
                  "cache_origins": cache_origins, "network_inputs": exact_network_inputs()})
    return facts


def build_live_plan(facts, run, command, helper):
    """One exact native credential-file write grant, no parent/home directory grant."""
    auth = facts["auth"]
    plan = helper.build_mount_plan(
        bwrap_path=facts["bwrap"], runtime_path=facts["runtime"], lab_root=ROOT,
        run_root=run, home_path=facts["home"], codex_home_path=facts["codex_home"],
        identity_copy_path=run / "installation_id_copy",
        readonly_paths=[p for p in facts["readonly_paths"] if p != auth],
        writable_paths=[run / "runtime_state", run / "runtime_logs"], command_argv=command)
    # --share-net explicitly overrides the preceding --unshare-all network bit.
    # This is inherited host networking, NOT an endpoint allowlist or model boundary.
    argv = plan["argv"]
    position = argv.index("--unshare-all") + 1
    argv[position:position] = ["--share-net"]
    position = argv.index("--remount-ro")
    additions = []
    for item in facts["network_inputs"]:
        additions += ["--ro-bind", item["source"], item["destination"]]
        plan["mounts"].append({k: item[k] for k in ("source", "destination", "access")})
    additions += ["--bind", str(auth), str(auth)]
    argv[position:position] = additions
    plan["mounts"].append({"source": str(auth), "destination": str(auth), "access": "write",
                           "kind": "approved_native_existing_credential_refresh_only"})
    plan.update({"kind": "GATE0_POSTLOGIN_MOUNT_PLAN_016_v1", "network": "inherited_host_network",
                 "network_endpoint_allowlist_enforced": False,
                 "native_existing_credential_writable": True, "full_reviewer_boundary_verified": False})
    return plan


def existing(run, pins):
    if not os.path.lexists(run):
        return None
    plain(run, True)
    raw = bounded(run / "REPORT.json")
    require(bounded(run / "REPORT.sha256", 65) == (sha(raw) + "\n").encode(),
            "Prior report checksum differs; preserve it")
    value = json.loads(raw)
    require(type(value) is dict and set(value) == REPORT_KEYS, "Prior report schema differs; preserve it")
    require(value.get("kind") == REPORT_KIND and value.get("pins") == pins,
            "Prior report has different source provenance; preserve it")
    require(value.get("model_requested") is False and value.get("formal_verdict") is None
            and value.get("unattended_model_use_authorized") is False,
            "Prior report overstates its scope")
    return run / "REPORT.json"


def exclusive(path, value):
    raw = (json.dumps(value, indent=2) + "\n").encode()
    with path.open("xb") as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    return raw


def run_once(scope, pins, facts, preflight, boundary):
    require(type(boundary) is dict and boundary.get("passed") is True,
            "Verified prior boundary is required before a correction attempt")
    run = plain(ROOT / "delivery", True) / RUN_NAME
    run.mkdir(mode=0o700)
    exclusive(run / "ATTEMPT.json", {"created_utc": datetime.now(timezone.utc).isoformat(), "pins": pins})
    for name in ("runtime_state", "runtime_logs"):
        (run / name).mkdir(mode=0o700)
    copy = run / "installation_id_copy"
    with copy.open("xb") as stream:
        stream.write(facts["identifier_bytes"])
    copy.chmod(0o644)
    requested = preflight.overrides(run)
    command = [str(facts["runtime"])]
    for key, value in requested.items():
        command += ["-c", key + "=" + json.dumps(value)]
    command += ["app-server", "--strict-config", "--stdio"]
    plan = build_live_plan(facts, run, command, module("gate0_client_mount_plan"))
    if boundary.get("passed") is True:
        observation = module("gate0_postlogin_protocol").observe(
            plan, run, requested, preflight, module("gate0_account_metadata"))
    else:
        observation = {"status": "STOPPED_WITHOUT_NATIVE_CREDENTIAL_ACCESS",
                       "reason": "Synthetic file-bind prerequisite did not pass",
                       "client_started": False, "thread_or_model_request_sent": False,
                       "requests_sent": [], "responses": []}
    origins_unchanged = all(metadata(Path(i["path"])) == i["metadata"]
                            if i["present"] else not os.path.lexists(i["path"])
                            for i in facts["origins"] if i["path"] != str(facts["auth"]))
    caches_unchanged = all(metadata(Path(i["path"])) == i["metadata"]
                           if i["present"] else not os.path.lexists(i["path"])
                           for i in facts["cache_origins"])
    report = {
        "kind": REPORT_KIND, "created_utc": datetime.now(timezone.utc).isoformat(), "pins": pins,
        "scope": "Finite native metadata observation; no model or scientific review",
        "model_requested": False, "formal_verdict": None, "unattended_model_use_authorized": False,
        "mount_plan": plan, "observation": observation, "synthetic_boundary": boundary,
        "origin_inventory": facts["origins"], "cache_origins": facts["cache_origins"],
        "network_inputs": facts["network_inputs"], "auth_metadata_before": facts["auth_before"],
        "auth_metadata_after": metadata(facts["auth"]),
        "credential_contents_opened_hashed_or_copied_by_parent": False,
        "native_credential_refresh_may_have_occurred": observation.get("client_started") is True,
        "host_config_metadata_unchanged": origins_unchanged,
        "host_cache_metadata_unchanged": caches_unchanged,
        "host_runtime_unchanged": preflight.signature(facts["runtime"]) == facts["runtime_before"],
        "host_bwrap_unchanged": preflight.signature(facts["bwrap"]) == facts["bwrap_before"],
        "host_installation_id_unchanged": preflight.signature(facts["identifier"]) == facts["identifier_before"],
        "private_installation_id_matches": copy.read_bytes() == facts["identifier_bytes"],
        "hosted_chatgpt_allowance_verified": False, "model_entitlement_verified": False,
        "full_reviewer_boundary_verified": False, "managed_policy_closure_verified": False,
        "raw_native_logs_or_protocol_in_report": False,
    }
    raw = exclusive(run / "REPORT.json", report)
    with (run / "REPORT.sha256").open("x") as stream:
        stream.write(sha(raw) + "\n"); stream.flush(); os.fsync(stream.fileno())
    require(existing(run, pins) is not None, "Final receipt verification failed")
    return run / "REPORT.json"


def show(path):
    print("REPORT: " + str(path))
    print("REPORT_SHA256: " + sha(bounded(path)))
    print('REPORT_FOLDER_COMMAND: explorer.exe "$(wslpath -w "$HOME/ARC_Independent_Lab/delivery/' + path.parent.name + '")"')
    print("Share only REPORT.json. Keep native runtime files private. No model or verdict was requested.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--run-metadata", action="store_true",
                      help="Show the original completed attempt only; never rerun it")
    mode.add_argument("--run-repaired-metadata", action="store_true",
                      help="Explicit human launch of the corrected protocol under the existing approval")
    args = parser.parse_args()
    preflight = None
    try:
        scope, pins = load_bundle()
        if args.run_metadata:
            path, _ = prior_observation()
            print("Original attempt preserved; legacy command cannot start a correction.")
            show(path)
            return
        prior = existing(ROOT / "delivery" / RUN_NAME, pins)
        if prior:
            print("Verified completed report; native client was not rerun.")
            show(prior)
            return
        _, prior_report = prior_observation()
        preflight = module("gate0_client_preflight")
        facts = inventory(scope, preflight)
        boundary = reuse_boundary(facts, prior_report)
        print("Pinned runtime and original configuration inspected; credential contents were not read.")
        print("Correction only: supported notification timestamp; existing permissions and passed prerequisite reused.")
        if not args.run_repaired_metadata:
            print("Inspection only. No native process, network call or filesystem change was made.")
            return
        approval(scope)
        show(run_once(scope, pins, facts, preflight, boundary))
    except Exception as error:
        # Native/config/credential errors can carry secrets; only our fixed Stop text is public.
        known = isinstance(error, Stop) or (preflight is not None and isinstance(error, preflight.Stop))
        reason = str(error) if known else "Required input or completed receipt unavailable; raw exception withheld"
        print("STOP: " + reason + ". Preserve the fixed run directory; no automatic retry or repair.")
        raise SystemExit(2) from None


if __name__ == "__main__":
    main()
