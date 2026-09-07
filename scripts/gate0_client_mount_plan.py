"""Build a finite no-model app-server mount plan; never launch a process.

The parent owns UUID-content checks, runtime identity, config provenance, protocol
validation, and environment scrubbing. This module validates filesystem topology
and emits a direct bubblewrap argv. An emitted plan is not an observed boundary.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Sequence


class MountPlanError(ValueError):
    pass


_SYSTEM_READ_ALIASES = {"/bin", "/sbin", "/lib", "/lib64"}
_FORBIDDEN_COMMAND_FLAGS = {
    "--ignore-rules", "--ignore-user-config", "--dangerously-bypass-approvals-and-sandbox",
    "--yolo", "--remote-control", "--remote", "--remote-auth-token-env",
}


def _inside(path: Path, parent: Path) -> bool:
    return path == parent or parent in path.parents


def _path(value: str | os.PathLike[str], *, allow_system_read_alias: bool = False) -> Path:
    raw = os.fspath(value)
    if not isinstance(raw, str) or not raw or "\0" in raw:
        raise MountPlanError("Path must be a nonempty string without NUL")
    path = Path(raw)
    if not path.is_absolute() or ".." in path.parts or str(path) != raw:
        raise MountPlanError("Path must use normalized absolute syntax")
    if "ARC_AGI3_Plasticity_Lab" in path.parts:
        raise MountPlanError("Other programme paths are forbidden")
    try:
        resolved = path.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise MountPlanError("Path must already exist and resolve") from exc
    if resolved != path:
        alias_ok = (
            allow_system_read_alias and raw in _SYSTEM_READ_ALIASES
            and path.is_symlink() and _inside(resolved, Path("/usr"))
            and resolved.is_dir()
        )
        if not alias_ok:
            raise MountPlanError("Symlinks and symlinked ancestors are forbidden")
    return path


def _directory(path: Path, label: str) -> None:
    if not path.is_dir():
        raise MountPlanError(label + " must be an existing directory")


def _regular(path: Path, label: str) -> None:
    if not path.is_file() or path.is_symlink():
        raise MountPlanError(label + " must be an existing regular nonsymlink file")


def build_mount_plan(
    *,
    bwrap_path: str | os.PathLike[str],
    runtime_path: str | os.PathLike[str],
    lab_root: str | os.PathLike[str],
    run_root: str | os.PathLike[str],
    home_path: str | os.PathLike[str],
    codex_home_path: str | os.PathLike[str],
    identity_copy_path: str | os.PathLike[str],
    readonly_paths: Sequence[str | os.PathLike[str]],
    writable_paths: Sequence[str | os.PathLike[str]],
    command_argv: Sequence[str],
) -> dict:
    """Return validated argv/mount metadata without reading contents or executing.

    No environment values are set. The run root is read-only except for explicit
    separate runtime directories. Only the installation-ID backing file may have
    differing source/destination pathnames. Standard /bin,/lib aliases are allowed
    as explicitly selected same-spelling readonly binds if they resolve into /usr.
    """
    bwrap = _path(bwrap_path)
    runtime = _path(runtime_path)
    lab = _path(lab_root)
    run = _path(run_root)
    home = _path(home_path)
    codex_home = _path(codex_home_path)
    identity_copy = _path(identity_copy_path)
    for p, label in [(bwrap, "bubblewrap"), (runtime, "Codex runtime"), (identity_copy, "ID copy")]:
        _regular(p, label)
    for p, label in [(lab, "Lab"), (run, "Run"), (home, "Home"), (codex_home, "Codex home")]:
        _directory(p, label)
    if not os.access(bwrap, os.X_OK) or not os.access(runtime, os.X_OK):
        raise MountPlanError("Both executables must have execute access")
    if run == lab or not _inside(run, lab):
        raise MountPlanError("Run root must be a strict descendant of the lab")
    if _inside(lab, codex_home) or _inside(codex_home, lab):
        raise MountPlanError("Lab and existing Codex home must not overlap")
    if not _inside(lab, home) or not _inside(codex_home, home):
        raise MountPlanError("Lab and Codex home must belong to the supplied actual home")
    if not _inside(identity_copy, run) or identity_copy == run:
        raise MountPlanError("ID backing file must be inside the fresh run")
    identity_target = _path(codex_home / "installation_id")
    _regular(identity_target, "Existing installation ID")
    if identity_copy.stat().st_ino == identity_target.stat().st_ino and identity_copy.stat().st_dev == identity_target.stat().st_dev:
        raise MountPlanError("ID backing file must not hard-link the host ID")
    if identity_copy.stat().st_mode & 0o777 != 0o644:
        raise MountPlanError("ID backing file must already have mode 0644")
    if identity_target.stat().st_mode & 0o777 != 0o644:
        raise MountPlanError("Host ID must already have mode 0644")

    ro = {_path(p, allow_system_read_alias=True) for p in readonly_paths}
    ro.add(runtime)
    ro.add(run)
    forbidden_broad = {Path("/"), Path("/home"), Path("/root"), Path("/etc"), home, codex_home, lab}
    for p in ro:
        if p in forbidden_broad or _inside(home, p):
            raise MountPlanError("Broad root, home, Codex home, lab, or /etc read grant forbidden")
        if _inside(p, codex_home) and p.is_dir():
            raise MountPlanError("Codex-home dependencies must be exact file grants")
        if p.is_dir() and _inside(p, home) and not _inside(p, run):
            raise MountPlanError("Home-directory reads outside this run require exact file grants")
        if p in {Path("/proc"), Path("/sys"), Path("/dev"), Path("/tmp")}:
            raise MountPlanError("Host proc/sys/dev/tmp mounts are forbidden")
        if not p.is_file() and not p.is_dir():
            raise MountPlanError("Read mounts must be files or directories")

    rw = {_path(p) for p in writable_paths}
    if not rw:
        raise MountPlanError("Explicit runtime write directories are required")
    for p in rw:
        _directory(p, "Runtime write target")
        if p == run or not _inside(p, run):
            raise MountPlanError("Runtime writes must be strict fresh-run descendants")
        if _inside(identity_copy, p):
            raise MountPlanError("Runtime directory cannot contain the ID backing file")
        for other in ro - {run}:
            if _inside(p, other) or _inside(other, p):
                raise MountPlanError("Runtime write directory overlaps a readonly input")
        for other in rw - {p}:
            if _inside(p, other) or _inside(other, p):
                raise MountPlanError("Runtime write directories must not overlap")

    cmd = list(command_argv)
    if not cmd or cmd[0] != str(runtime):
        raise MountPlanError("Only the pinned exact runtime may be the command")
    if any(not isinstance(x, str) or not x or "\0" in x for x in cmd):
        raise MountPlanError("Command arguments must be nonempty strings without NUL")
    if any(x in _FORBIDDEN_COMMAND_FLAGS or any(x.startswith(f + "=") for f in _FORBIDDEN_COMMAND_FLAGS) for x in cmd):
        raise MountPlanError("Bypass, remote, and ignore-config command flags are forbidden")
    if not all(flag in cmd for flag in ["app-server", "--strict-config", "--stdio"]):
        raise MountPlanError("Only strict stdio app-server startup is allowed")

    # Start with an empty mount namespace. No host-root or host-home bind exists.
    argv = [str(bwrap), "--unshare-all", "--unshare-user", "--die-with-parent", "--new-session", "--tmpfs", "/"]
    mounts = []
    for p in sorted(ro, key=lambda x: (len(x.parts), str(x))):
        argv.extend(["--ro-bind", str(p), str(p)])
        mounts.append({"source": str(p), "destination": str(p), "access": "read"})
    for p in sorted(rw):
        argv.extend(["--bind", str(p), str(p)])
        mounts.append({"source": str(p), "destination": str(p), "access": "write"})
    argv.extend(["--bind", str(identity_copy), str(identity_target)])
    mounts.append({"source": str(identity_copy), "destination": str(identity_target), "access": "write", "kind": "same_identity_private_backing"})
    argv.extend(["--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp", "--remount-ro", "/", "--cap-drop", "ALL", "--chdir", str(run), "--"])
    argv.extend(cmd)
    return {
        "kind": "GATE0_CLIENT_MOUNT_PLAN_v1", "observed_boundary": False,
        "argv": argv, "mounts": mounts, "command_cwd": str(run),
        "network": "new_unshared_namespace", "host_root_bound": False,
        "home_environment_modified": False, "codex_home_environment_modified": False,
        "authentication_copied": False, "host_installation_id_writable_bind": False,
        "temporary_files": "namespace-only /tmp", "identity_copy_content_verification": "parent_required",
        "policy_config_provenance_verification": "parent_required",
    }
