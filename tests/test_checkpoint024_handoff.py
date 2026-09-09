"""Engineering tests only: local fixture clones; no commits, pushes, or model calls."""
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile

SOURCE = Path(__file__).resolve().parents[1]
HERE = SOURCE / 'delivery'
HERE.mkdir(exist_ok=True)
spec = importlib.util.spec_from_file_location('handoff024_engineering', SOURCE / 'scripts/checkpoint024_handoff.py')
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)


def git(root, *args, body=None):
    result = subprocess.run(['git', '-C', str(root), *args], input=body, capture_output=True)
    if result.returncode:
        raise AssertionError('Fixture Git operation failed: ' + args[0])
    return result.stdout


def digest_tree(root):
    return {str(p.relative_to(root)): (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mode & 0o777)
            for p in root.rglob('*') if p.is_file()}


def silent(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


def refusal(fn):
    try:
        silent(fn)
    except (ValueError, RuntimeError):
        return
    raise AssertionError('Expected refusal')


def run():
    checks = []
    with tempfile.TemporaryDirectory(prefix='handoff024-engineering-', dir=HERE) as temporary:
        top = Path(temporary)
        baseline = top / 'baseline'
        result = subprocess.run(['git', 'clone', '--local', '--no-hardlinks', '--quiet', str(SOURCE), str(baseline)], capture_output=True)
        assert result.returncode == 0, 'Local clone failed'
        git(baseline, 'remote', 'set-url', 'origin', h.REMOTE)
        assert git(baseline, 'rev-parse', 'HEAD').decode().strip() == h.BASE
        g = h.Git(baseline)
        base = g.tree(h.BASE)
        base_bodies = g.blobs(oid for mode, oid in base.values())
        raw_scope = b'{"scope_id":"engineering_only_scope024"}\n'
        raw_request = b'# Engineering fixture only\n\nAn unsigned exact-byte request.\n'
        h.SCOPE_SHA256 = h.sha(raw_scope)
        h.UNSIGNED_ESCALATION_SHA256 = h.sha(raw_request)
        payload = {
            h.SCOPE_PATH: (raw_scope, '100644'),
            h.ESCALATION_PATH: (raw_request, '100644'),
            'artifacts/CHECKPOINT024_ENGINEERING/bytes.bin': (b'line1\r\nline2\r\n\x00', '100644'),
            'scripts/checkpoint024_engineering_fixture.sh': (b'#!/bin/sh\nexit 0\n', '100755'),
        }
        rows = {name: {'path': name, 'sha256': h.sha(base_bodies[oid]), 'mode': mode}
                for name, (mode, oid) in base.items()}
        for name, (body, mode) in payload.items():
            rows[name] = {'path': name, 'sha256': h.sha(body), 'mode': mode}
        checkpoint = {'schema_version': 1, 'checkpoint_id': h.CHECKPOINT_ID, 'base_commit': h.BASE,
                      'correction_approval': h.approval_metadata(),
                      'exclusions': {h.CHECKPOINT_PATH: 'Self hash is pinned by containing commit and ZIP.'},
                      'files': [rows[name] for name in sorted(rows)]}
        payload[h.CHECKPOINT_PATH] = (h.json_bytes(checkpoint), '100644')
        files = {name: {'old_sha256': h.sha(base_bodies[base[name][1]]) if name in base else None,
                        'sha256': h.sha(body), 'mode': mode, 'body': body}
                 for name, (body, mode) in payload.items()}
        archive = top / 'unsigned.zip'
        manifest = {'checkpoint_id': h.CHECKPOINT_ID, 'base_commit': h.BASE,
                    'files': {name: {key: value for key, value in row.items() if key != 'body'} for name, row in files.items()}}
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
            z.writestr('HANDOFF.json', h.json_bytes(manifest))
            for name, entry in files.items():
                z.writestr('files/' + name, entry['body'])
        loaded = h.load_package(archive, h.sha(archive.read_bytes()))
        assert loaded == files
        checks.append('verified_unsigned_zip_and_full_manifest')
        approved = h.select_variant(loaded, True)
        assert approved == h.select_variant(loaded, True)
        changed = {name for name in loaded if approved[name]['body'] != loaded[name]['body']}
        assert changed == {h.ESCALATION_PATH, h.CHECKPOINT_PATH}
        answer = approved[h.ESCALATION_PATH]['body'].decode().split('## ANSWER\n')[1]
        assert answer.splitlines() == [h.APPROVAL_ID, 'scope_sha256: ' + h.SCOPE_SHA256]
        assert h.CHECKPOINT_PATH not in {r['path'] for r in json.loads(approved[h.CHECKPOINT_PATH]['body'])['files']}
        checks.append('deterministic_two_file_approval_exact_answer_no_self_hash')

        def fixture(label):
            root = top / label
            shutil.copytree(baseline, root)
            return root

        root = fixture('inspection')
        before = digest_tree(root)
        silent(h.inspect, root, loaded)
        assert before == digest_tree(root)
        checks.append('default_inspection_preserves_every_fixture_byte_and_mode')

        root = fixture('unsigned_and_approved')
        silent(h.apply, root, loaded)
        silent(h.inspect, root, loaded, complete=True)
        before = digest_tree(root)
        silent(h.apply, root, loaded)
        assert before == digest_tree(root)
        silent(h.apply, root, approved, unsigned_files=loaded)
        silent(h.inspect, root, approved, complete=True, unsigned_files=loaded)
        before = digest_tree(root)
        silent(h.apply, root, approved, unsigned_files=loaded)
        assert before == digest_tree(root)
        refusal(lambda: h.inspect(root, loaded))
        assert before == digest_tree(root)
        checks.append('unsigned_apply_approval_transition_and_retry_are_idempotent')
        checks.append('approved_state_requires_matching_explicit_variant')

        root = fixture('filters_and_modes')
        git(root, 'config', 'core.autocrlf', 'input')
        git(root, 'config', 'core.fileMode', 'false')
        git(root, 'config', 'credential.helper', 'engineering_nonsecret_sentinel')
        git(root, 'config', 'filter.engineering_fail.clean', 'false')
        git(root, 'config', 'filter.engineering_fail.required', 'true')
        (root / '.git/info/attributes').write_bytes(b'* filter=engineering_fail\n')
        config_before = (root / '.git/config').read_bytes()
        silent(h.apply, root, loaded)
        index = h.Git(root).index()
        name = 'artifacts/CHECKPOINT024_ENGINEERING/bytes.bin'
        assert h.Git(root).blobs([index[name][1]])[index[name][1]] == payload[name][0]
        assert index['scripts/checkpoint024_engineering_fixture.sh'][0] == '100755'
        assert (root / '.git/config').read_bytes() == config_before
        checks.append('direct_staging_preserves_crlf_nul_executable_mode_and_git_credential_configuration')

        base_target = 'state/BUDGET.json'
        scenarios = [
            ('unknown_staged_addition', lambda r: ((r / 'engineering-unrelated.txt').write_bytes(b'preserve\n'), git(r, 'add', '--', 'engineering-unrelated.txt'))),
            ('staged_tracked_deletion', lambda r: git(r, 'rm', '--', base_target)),
            ('unknown_tracked_work_edit', lambda r: (r / base_target).write_bytes(b'preserve foreign edit\n')),
            ('unknown_payload_work_edit', lambda r: (r / h.ESCALATION_PATH).write_bytes(b'preserve altered request\n')),
            ('unknown_staged_mode', lambda r: git(r, 'update-index', '--chmod=+x', '--', base_target)),
            ('assume_unchanged_cannot_hide_edit', lambda r: (git(r, 'update-index', '--assume-unchanged', '--', base_target), (r / base_target).write_bytes(b'preserve hidden edit\n'))),
        ]
        for label, mutate in scenarios:
            root = fixture(label)
            mutate(root)
            before = digest_tree(root)
            refusal(lambda: h.apply(root, approved, unsigned_files=loaded))
            assert before == digest_tree(root), label
            checks.append(label + '_refused_without_mutation')

        root = fixture('partial_apply')
        subset = [h.SCOPE_PATH, h.ESCALATION_PATH]
        for name in subset:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(approved[name]['body'])
        silent(h.apply, root, approved, unsigned_files=loaded)
        silent(h.inspect, root, approved, complete=True, unsigned_files=loaded)
        checks.append('partial_file_apply_retry_completes_known_transitions')

        altered = copy.deepcopy(loaded)
        altered[h.ESCALATION_PATH]['body'] += b'Changed allowance\n'
        altered[h.ESCALATION_PATH]['sha256'] = h.sha(altered[h.ESCALATION_PATH]['body'])
        refusal(lambda: h.select_variant(altered, True))
        checks.append('altered_unsigned_approval_request_refused')

        expected = dict(base)
        expected.update({name: (entry['mode'], h.blob_oid(entry['body'])) for name, entry in approved.items()})
        child = 'c' * 40
        class ReadOnlyChildFixture:
            def __init__(self, parents, tree): self.parents, self.entries = parents, tree
            def text(self, *args): return ' '.join(self.parents)
            def tree(self, revision): return self.entries
        assert h.classify_head(ReadOnlyChildFixture([child, h.BASE], expected), child, expected) == 'checkpoint024'
        refusal(lambda: h.classify_head(ReadOnlyChildFixture([child, 'd' * 40], expected), child, expected))
        refusal(lambda: h.classify_head(ReadOnlyChildFixture([child, h.BASE, 'd' * 40], expected), child, expected))
        checks.append('exact_child_parent_and_tree_rule_without_creating_commits')
    return {'test_type': 'engineering_only', 'passed': len(checks), 'checks': checks,
            'actual_commits_pushes_network_or_native_operations': 0,
            'controller_approval_parser': 'Root separately validates actual controller against delivered payload.'}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
