"""Topology tests only; fake executables are never executed."""
import copy
import os
from pathlib import Path
import tempfile
import unittest
import importlib.util

spec = importlib.util.spec_from_file_location("gate0_client_mount_plan", Path(__file__).with_name("gate0_client_mount_plan.py"))
mount_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mount_module)
MountPlanError, build_mount_plan = mount_module.MountPlanError, mount_module.build_mount_plan


class MountPlanTests(unittest.TestCase):
    def setUp(self):
        base = Path(__file__).resolve().parents[1] / "delivery"
        base.mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(prefix="mount-plan-test-", dir=base)
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.home = root / "user"
        self.lab = self.home / "ARC_Independent_Lab"
        self.run = self.lab / "delivery" / "run"
        self.codex = self.home / "codex-state"
        for p in [self.run / "state", self.run / "logs", self.run / "packet", self.codex / "bin"]:
            p.mkdir(parents=True, exist_ok=True)
        self.runtime = self.codex / "bin" / "codex"
        self.bwrap = root / "bwrap"
        for p in [self.runtime, self.bwrap]:
            p.write_bytes(b"never execute this fixture\n")
            p.chmod(0o755)
        self.host_id = self.codex / "installation_id"
        self.copy_id = self.run / "identity_backing"
        for p in [self.host_id, self.copy_id]:
            p.write_text("4e015da3-9ca0-47ce-97a9-046919cedd09")
            p.chmod(0o644)
        self.config = self.codex / "config.toml"
        self.config.write_text("# synthetic fixture only\n")
        self.kw = dict(
            bwrap_path=self.bwrap, runtime_path=self.runtime, lab_root=self.lab,
            run_root=self.run, home_path=self.home, codex_home_path=self.codex,
            identity_copy_path=self.copy_id,
            readonly_paths=[self.config, self.run / "packet"],
            writable_paths=[self.run / "state", self.run / "logs"],
            command_argv=[str(self.runtime), "app-server", "--strict-config", "--stdio"],
        )

    def test_exact_same_identity_mapping_and_no_host_id_write(self):
        before = self.host_id.read_bytes(), self.host_id.stat().st_mtime_ns
        plan = build_mount_plan(**self.kw)
        maps = [m for m in plan["mounts"] if m["source"] != m["destination"]]
        self.assertEqual(maps, [{"source":str(self.copy_id), "destination":str(self.host_id), "access":"write", "kind":"same_identity_private_backing"}])
        self.assertFalse(any(m["access"] == "write" and m["source"] == str(self.host_id) for m in plan["mounts"]))
        self.assertEqual(before, (self.host_id.read_bytes(), self.host_id.stat().st_mtime_ns))
        self.assertFalse(plan["observed_boundary"])
        a = plan["argv"]
        self.assertIn("--unshare-all", a)
        self.assertIn("--unshare-user", a)
        self.assertEqual(a[a.index("--chdir")+1], str(self.run))
        self.assertEqual(a[-4:], self.kw["command_argv"])
        self.assertNotIn("--setenv", a)

    def test_readonly_run_baseline_before_private_write_carveouts(self):
        a=build_mount_plan(**self.kw)["argv"]
        ro=a.index(str(self.run))
        write=a.index(str(self.run / "state"))
        self.assertLess(ro, write)
        self.assertLess(a.index(str(self.copy_id)), a.index("--remount-ro"))

    def test_reject_broad_home_or_codex_home_or_lab(self):
        for p in [self.home, self.codex, self.lab, Path("/")]:
            with self.subTest(path=p), self.assertRaises(MountPlanError):
                build_mount_plan(**(self.kw | {"readonly_paths":[p]}))

    def test_reject_codex_directory_dependency(self):
        with self.assertRaises(MountPlanError):
            build_mount_plan(**(self.kw | {"readonly_paths":[self.codex / "bin"]}))

    def test_reject_symlink_id_and_read_origin(self):
        link=self.run / "linked"
        link.symlink_to(self.config)
        with self.assertRaises(MountPlanError):
            build_mount_plan(**(self.kw | {"readonly_paths":[link]}))
        self.copy_id.unlink(); self.copy_id.symlink_to(self.host_id)
        with self.assertRaises(MountPlanError):
            build_mount_plan(**self.kw)

    def test_reject_hardlink_backing(self):
        self.copy_id.unlink(); os.link(self.host_id,self.copy_id)
        with self.assertRaises(MountPlanError):
            build_mount_plan(**self.kw)

    def test_reject_outside_or_root_write(self):
        for p in [self.codex, self.run, self.lab]:
            with self.subTest(path=p),self.assertRaises(MountPlanError):
                build_mount_plan(**(self.kw | {"writable_paths":[p]}))

    def test_reject_write_overlap_with_packet(self):
        with self.assertRaises(MountPlanError):
            build_mount_plan(**(self.kw | {"writable_paths":[self.run / "packet"]}))

    def test_reject_write_parent_of_id(self):
        nested=self.run / "state" / "id"
        nested.write_bytes(self.copy_id.read_bytes()); nested.chmod(0o644)
        with self.assertRaises(MountPlanError):
            build_mount_plan(**(self.kw | {"identity_copy_path":nested}))

    def test_reject_missing_invalid_mode_or_nonexistent_id(self):
        self.host_id.chmod(0o600)
        with self.assertRaises(MountPlanError):build_mount_plan(**self.kw)
        self.host_id.unlink()
        with self.assertRaises(MountPlanError):build_mount_plan(**self.kw)

    def test_reject_unconfined_or_alternate_command(self):
        for cmd in [[str(self.bwrap),"app-server","--strict-config","--stdio"],
                    [str(self.runtime),"app-server","--stdio"],
                    self.kw["command_argv"] + ["--ignore-rules"],
                    self.kw["command_argv"] + ["--remote=unix://"]]:
            with self.subTest(cmd=cmd),self.assertRaises(MountPlanError):
                build_mount_plan(**(self.kw | {"command_argv":cmd}))

    def test_does_not_change_environment_or_input(self):
        environment=dict(os.environ)
        inputs=copy.deepcopy(self.kw)
        build_mount_plan(**self.kw)
        self.assertEqual(environment,dict(os.environ))
        self.assertEqual(inputs,self.kw)


if __name__ == "__main__":
    unittest.main()
