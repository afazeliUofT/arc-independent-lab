"""Local synthetic fixtures only; never creates a native client or reads credentials."""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import stat


ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT
ATTACHED_REPORT = ROOT / "artifacts/P3_FINITE_REVIEW_WARNING_OBSERVATIONS/20260909_025/REPORT.json"
EXPECTED_ATTACHED_SHA256 = "60f7a041d8415990a28362459e4ddd1b6029f10c1066d92ab85e0c6efee25c5f"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, indent=2, ensure_ascii=True) + "\n").encode()


def attached_report():
    # Archived exact current-conversation input, not historical host access.
    raw = ATTACHED_REPORT.read_bytes()
    if digest(raw) != EXPECTED_ATTACHED_SHA256:
        raise AssertionError("Attached engineering input differs")
    return json.loads(raw), raw


def snapshot(paths):
    result = {}
    for path in paths:
        path = Path(path)
        info = path.lstat()
        data = path.read_bytes() if stat.S_ISREG(info.st_mode) else None
        result[str(path)] = (data, info.st_mode, info.st_size, info.st_mtime_ns,
                             info.st_ctime_ns, info.st_ino, info.st_dev)
    return result


def fixture_report(project, *, config_bytes=b"[features]\nunder_development=false\n",
                   cache_bytes=b'{"models": []}\n'):
    """Create a synthetic byte-linked REPORT/SESSION plus two nonsecret inputs.

    Tests may patch the production digest constants in the imported module to
    exercise these fixtures. The production script is never rewritten.
    """
    report, _ = attached_report()
    report = copy.deepcopy(report)
    old_home = "/home/afazeli2006"
    report_path = project / "delivery/P3_FINITE_REVIEW_024/REPORT.json"
    session_path = report_path.with_name("synthetic_SESSION.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    native = report_path.parent / "synthetic_native"
    (native / "runtime_state").mkdir(parents=True)
    (native / "runtime_logs").mkdir()
    (project.parent / ".codex").mkdir(exist_ok=True)
    selected = {}
    for name, body in (("config.toml", config_bytes), ("models_cache.json", cache_bytes)):
        path = project.parent / ".codex" / name
        path.write_bytes(body)
        info = path.stat()
        meta = {"device": info.st_dev, "inode": info.st_ino, "bytes": info.st_size,
                "mode": stat.S_IMODE(info.st_mode), "mtime_ns": info.st_mtime_ns,
                "ctime_ns": info.st_ctime_ns}
        selected[name] = path
        for group in ("config_origins", "cache_origins"):
            for row in report["stages"][0][group]:
                if row.get("path") == old_home + "/.codex/" + name:
                    row.update({"path": str(path), "present": True, "metadata": meta})
    session_raw = json_bytes(report["stages"][0]["observation"])
    session_path.write_bytes(session_raw)
    report["preserved_session_receipts"][0]["sha256"] = digest(session_raw)
    raw = json_bytes(report)
    report_path.write_bytes(raw)
    return {"report": report, "report_path": report_path, "session_path": session_path,
            "report_raw": raw, "session_raw": session_raw, "native": native,
            "selected": selected, "project": project}
