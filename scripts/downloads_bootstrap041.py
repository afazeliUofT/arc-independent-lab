"""Template for the one-paste WSL-home command; release tooling fills ZIP_SHA256."""
from pathlib import Path
import hashlib
import io
import shutil
import subprocess
import zipfile

ZIP_NAME = 'ARC_Independent_Lab_041.zip'
ZIP_SHA256 = '__ZIP_SHA256__'


def main():
    folders = [Path.home() / 'Downloads']
    ps = shutil.which('powershell.exe') or '/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe'
    query = r"""$ErrorActionPreference='Stop'; [Console]::OutputEncoding=[System.Text.Encoding]::UTF8; $k='HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders'; $p=(Get-ItemProperty -LiteralPath $k).'{374DE290-123F-4565-9164-39C4925E467B}'; if([string]::IsNullOrWhiteSpace($p)){throw 'Downloads path unavailable'}; [Environment]::ExpandEnvironmentVariables($p)"""
    discovery = 'not attempted'
    try:
        windows = subprocess.run([ps, '-NoProfile', '-NonInteractive', '-Command', query],
            capture_output=True, check=True, timeout=20).stdout.decode('utf-8-sig').strip()
        linux = subprocess.run(['wslpath', '-u', windows], capture_output=True,
            check=True, timeout=10).stdout.decode('utf-8').strip()
        if not linux or '\n' in linux:
            raise ValueError('invalid Downloads path')
        folders.insert(0, Path(linux))
        discovery = 'Windows Downloads resolved'
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        discovery = type(error).__name__
        folders += sorted(Path('/mnt/c/Users').glob('*/Downloads'))
    found = False
    for folder in dict.fromkeys(folders):
        for archive in sorted(folder.glob(ZIP_NAME.removesuffix('.zip') + '*.zip')):
            try:
                if archive.is_symlink() or not archive.is_file() or archive.stat().st_size > 64 * 1024 * 1024:
                    continue
                raw = archive.read_bytes()
            except OSError:
                continue
            found = True
            if hashlib.sha256(raw).hexdigest() != ZIP_SHA256:
                continue
            print('Using verified download:', archive, flush=True)
            with zipfile.ZipFile(io.BytesIO(raw)) as package:
                code = package.read('launch041_home.py')
            exec(compile(code, 'launch041_home.py', 'exec'),
                 {'__name__': '__main__', 'ARCHIVE_BYTES': raw, 'ARCHIVE_PATH': str(archive)})
            return
    reason = 'matching filenames failed the release checksum' if found else 'package not found'
    raise SystemExit('STOP: ' + reason + '; Downloads discovery: ' + discovery +
        '. Save ' + ZIP_NAME + ' in Windows Downloads and repeat. If it still stops, send only this STOP line.')


if __name__ == '__main__':
    main()
