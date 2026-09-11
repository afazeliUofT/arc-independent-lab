"""Verify filename selection, Windows path translation and checksum-before-code."""
import importlib.util
import io
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import zipfile

SPEC = importlib.util.spec_from_file_location('bootstrap038',
    Path(__file__).resolve().parents[1] / 'scripts/downloads_bootstrap038.py')
BOOT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BOOT)


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.downloads = self.base / 'One Drive' / 'Téléchargements'
        self.downloads.mkdir(parents=True)
        self.marker = self.base / 'executed.json'
        code = ("from pathlib import Path\nimport json\n"
                "Path(" + repr(str(self.marker)) + ").write_text(json.dumps({"
                "'archive': ARCHIVE_PATH, 'bytes': len(ARCHIVE_BYTES)}))\n")
        out = io.BytesIO()
        with zipfile.ZipFile(out, 'w') as archive:
            archive.writestr('launch038_home.py', code)
        self.raw = out.getvalue()
        self.sha = BOOT.hashlib.sha256(self.raw).hexdigest()
        self.commands = []

    def runner(self, command, **kwargs):
        self.commands.append(command)
        self.assertTrue(kwargs['check'])
        self.assertLessEqual(kwargs['timeout'], 20)
        if command[0] == 'wslpath':
            self.assertEqual(command, ['wslpath', '-u', 'D:\\One Drive\\Téléchargements'])
            return subprocess.CompletedProcess(command, 0, (str(self.downloads) + '\n').encode(), b'')
        return subprocess.CompletedProcess(command, 0,
            b'\xef\xbb\xbf' + 'D:\\One Drive\\Téléchargements\r\n'.encode(), b'')

    def invoke(self, runner=None):
        with patch.object(BOOT, 'ZIP_SHA256', self.sha), \
             patch.object(BOOT.subprocess, 'run', runner or self.runner), \
             patch.object(BOOT.shutil, 'which', return_value='/interop/powershell.exe'), \
             patch.object(BOOT.Path, 'home', return_value=self.base):
            BOOT.main()

    def test_redirected_unicode_downloads_and_verified_duplicate_filename(self):
        (self.downloads / BOOT.ZIP_NAME).write_bytes(b'wrong older download')
        name = BOOT.ZIP_NAME.removesuffix('.zip') + ' (1).zip'
        (self.downloads / name).write_bytes(self.raw)
        self.invoke()
        self.assertTrue(self.marker.exists())
        self.assertIn(name, self.marker.read_text())
        self.assertEqual(len(self.commands), 2)

    def test_wrong_archive_never_executes_embedded_code(self):
        (self.downloads / BOOT.ZIP_NAME).write_bytes(self.raw + b'changed')
        with self.assertRaisesRegex(SystemExit, 'failed the release checksum'):
            self.invoke()
        self.assertFalse(self.marker.exists())

    def test_missing_package_gives_actionable_diagnostic_without_writing(self):
        with self.assertRaisesRegex(SystemExit, 'package not found; Downloads discovery: Windows Downloads resolved'):
            self.invoke()
        self.assertFalse(self.marker.exists())

    def test_wsl_downloads_fallback_if_interop_is_unavailable(self):
        folder = self.base / 'Downloads'
        folder.mkdir()
        (folder / BOOT.ZIP_NAME).write_bytes(self.raw)
        def unavailable(*args, **kwargs):
            raise FileNotFoundError('no interop')
        self.invoke(unavailable)
        self.assertTrue(self.marker.exists())


if __name__ == '__main__':
    unittest.main()
