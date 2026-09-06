"""Build-time template for the self-contained, human-run first checkpoint handoff.

The distributed copy embeds a compressed file map. Default execution only inspects
it. --apply-and-push is the human's explicit instruction to install, record the
answer printed below, commit, and push to the exact programme repository.
No dependency installation, credential creation, overwrite, or force push.
"""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import zlib

PAYLOAD = "__ARC_PAYLOAD__"
REMOTE = "https://github.com/afazeliUofT/arc-independent-lab.git"
ANSWER = "\n## ANSWER\nHuman response supplied by running P1_CHECKPOINT_001.py --apply-and-push: Continue Phase 1 after independently verifying this checkpoint on GitHub. Paper retrieval is asynchronous; keep dependent claims unresolved until the papers are supplied. This answer does not approve the incomplete diagnosis or authorize Phase 2.\n"


def unpack(payload):
    raw = zlib.decompress(base64.b64decode(payload, validate=True))
    data = json.loads(raw)
    files = {}
    for name, entry in data['files'].items():
        path = PurePosixPath(name)
        if path.is_absolute() or path.as_posix() != name or any(p in ('..', '.', '.git') for p in path.parts):
            raise ValueError('Unsafe payload path: ' + name)
        body = base64.b64decode(entry['base64'], validate=True)
        if hashlib.sha256(body).hexdigest() != entry['sha256']:
            raise ValueError('Payload hash mismatch: ' + name)
        files[name] = body
    if sum(map(len, files.values())) > 50 * 1024 * 1024:
        raise ValueError('This first-checkpoint installer is limited to a small document package')
    return files


def install(target, files):
    if target.is_symlink():
        raise ValueError('Project root is a symlink; refusing to follow it')
    target.mkdir(parents=True, exist_ok=True)
    for name, body in files.items():
        p = target / name
        relative = Path(name)
        for prefix in (relative, *relative.parents):
            if (target / prefix).is_symlink():
                raise ValueError('Symlink in destination path: ' + name)
        if p.exists():
            if not p.is_file():
                raise ValueError('Destination is not a regular file: ' + name)
            existing = p.read_bytes()
            accepted_answer = name == 'state/ESCALATION.md' and existing == body + ANSWER.encode()
            if existing != body and not accepted_answer:
                raise ValueError('Existing file differs; nothing overwritten: ' + name)
    for name, body in files.items():
        p = target / name
        if not p.exists():
            p.parent.mkdir(parents=True, exist_ok=True)
            with p.open('xb') as out:
                out.write(body)
    for name, body in files.items():
        actual = (target / name).read_bytes()
        if actual != body and not (name == 'state/ESCALATION.md' and actual == body + ANSWER.encode()):
            raise ValueError('Post-install byte check failed: ' + name)


def git(target, *args, check=True):
    env = os.environ.copy()
    env['GIT_TERMINAL_PROMPT'] = '0'
    p = subprocess.run(['git', '-C', str(target), *args], text=True, capture_output=True, env=env)
    if p.returncode:
        folder = target / 'state'
        folder.mkdir(exist_ok=True)
        with (folder / 'handoff_errors.jsonl').open('a') as out:
            out.write(json.dumps({'command': ['git', *args], 'exit_code': p.returncode,
                                  'stdout': p.stdout, 'stderr': p.stderr,
                                  'required_success': check}) + '\n')
    if check and p.returncode:
        sys.stdout.write(p.stdout)
        sys.stderr.write(p.stderr)
        raise RuntimeError('Git step failed; local files are preserved. Resolve the reported cause, then rerun this same command. No history was rewritten.')
    return p


def publish(target, files):
    if (target / '.git').is_symlink():
        raise ValueError('Refusing a symlinked .git directory')
    if (target / '.git').exists():
        if not (target / '.git').is_dir():
            raise ValueError('Refusing a linked worktree; git state must be inside this project')
        top = git(target, 'rev-parse', '--show-toplevel').stdout.strip()
        if Path(top).resolve() != target.resolve():
            raise ValueError('Repository root differs from the programme directory')
        remotes = git(target, 'remote').stdout.split()
        if 'origin' in remotes and git(target, 'remote', 'get-url', 'origin').stdout.strip() != REMOTE:
            raise ValueError('Existing origin differs; not changing it')
        if 'origin' in remotes and git(target, 'remote', 'get-url', '--push', 'origin').stdout.strip() != REMOTE:
            raise ValueError('Existing push URL differs; not changing it')
        staged = git(target, 'diff', '--cached', '--name-only').stdout.splitlines()
        if set(staged) - set(files) - {'state/handoff_errors.jsonl'}:
            raise ValueError('Unrelated changes are staged; refusing to include them')
    install(target, files)
    if not (target / '.git').exists():
        git(target, 'init', '--initial-branch=main')
    if git(target, 'branch', '--show-current').stdout.strip() != 'main':
        raise ValueError('Current branch is not main; no branch was changed')
    if 'origin' not in git(target, 'remote').stdout.split():
        git(target, 'remote', 'add', 'origin', REMOTE)
    # Check remote history before committing. Fetch never checks out or merges.
    refs = git(target, 'ls-remote', '--heads', 'origin').stdout.splitlines()
    if refs:
        main = [r for r in refs if r.endswith('\trefs/heads/main')]
        if len(main) != 1:
            raise ValueError('Remote has unexpected branch state; reconcile before publishing')
        git(target, 'fetch', 'origin', 'main')
        head = git(target, 'rev-parse', '--verify', 'HEAD', check=False)
        if head.returncode or git(target, 'merge-base', '--is-ancestor', 'FETCH_HEAD', 'HEAD', check=False).returncode:
            raise ValueError('Remote main is not an ancestor of local HEAD; no merge or force push performed')
    escalation = target / 'state/ESCALATION.md'
    if not escalation.read_text().endswith(ANSWER):
        with escalation.open('a') as out:
            out.write(ANSWER)
    git(target, 'add', '--', *sorted(files))
    if (target / 'state/handoff_errors.jsonl').exists():
        git(target, 'add', '--', 'state/handoff_errors.jsonl')
    dirty = git(target, 'diff', '--cached', '--quiet', check=False)
    if dirty.returncode not in (0, 1):
        raise RuntimeError('Could not inspect staged changes')
    if dirty.returncode == 1:
        if (target / 'state/handoff_errors.jsonl').exists():
            git(target, 'add', '--', 'state/handoff_errors.jsonl')
        # Per-command programme identity; do not modify the user's git config.
        git(target, '-c', 'user.name=ARC Independent Lab', '-c', 'user.email=arc-independent-lab@localhost',
            'commit', '-m', 'P1.0: initial diagnostic evidence and operating checkpoint')
    git(target, 'push', '--set-upstream', 'origin', 'main')
    print('Push completed. Commit:', git(target, 'rev-parse', 'HEAD').stdout.strip())
    print('The agent must read back and verify GitHub before claiming durability.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply-and-push', action='store_true')
    args = parser.parse_args()
    files = unpack(PAYLOAD)
    target = Path.home() / 'ARC_Independent_Lab'
    print('Target:', target)
    print('Remote:', REMOTE)
    print('Payload files:')
    for name in sorted(files):
        print(' ', name, hashlib.sha256(files[name]).hexdigest())
    print('Human answer recorded only with --apply-and-push:')
    print(ANSWER.strip())
    if not args.apply_and_push:
        print('Inspection only. No files, commits or pushes were made.')
        return
    publish(target, files)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, RuntimeError, KeyError, zlib.error) as error:
        print('STOP:', error, file=sys.stderr)
        sys.exit(1)
