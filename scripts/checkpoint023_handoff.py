"""Local P3 checkpoint-023 ZIP handoff. No commit, push, fetch, or authentication.

Supply the ZIP and its published SHA-256. Default: inspect. --apply: install and
stage known transitions, then verify actual index blobs. --verify: require the
complete installed and staged payload, or its exact checkpoint commit.
Accepts base021 and the precisely pinned previously delivered022 transitions.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import tempfile
import zipfile

BASE = "bb5dbae9d5cfc3b591d8080548bdc72eab4a7f44"
REMOTE = "https://github.com/afazeliUofT/arc-independent-lab.git"
ATTRIBUTES = b"# Preserve the exact bytes of scientific run artifacts.\n/artifacts/** -text\n"
MAX_BYTES = 64 * 1024 * 1024
PREVIOUS_ZIP_SHA256 = "2678ebb907f0e58fd9bf4be3945f40d29a197172dab9e4e841de649abb886795"
# Generated solely from the immutable delivered022 ZIP, including its manifest.
PREVIOUS_FILES = {'artifacts/P3_FINITE_REVIEW_MODEL_OBSERVATIONS/20260909_001/REPORT.json': {'git_oid': '90775d1750bbc5ce3b5ea9e3caf40fa4cf8dfcfd',
                                                                            'mode': '100644',
                                                                            'old_sha256': None,
                                                                            'sha256': 'd024d5b1ec85cce7ec61f36e7f5594efe0b37d7e2eb6db7ca6d4b2094115631c'},
 'artifacts/P3_FINITE_REVIEW_MODEL_OBSERVATIONS/20260909_001/SHA256SUMS': {'git_oid': '9bb80b28e80c347379bc427213c0aed3b3059ab6',
                                                                           'mode': '100644',
                                                                           'old_sha256': None,
                                                                           'sha256': '9d9d97d7143710b455d580e1869204bf3077fdbe111211f5e954c2fece6b09d6'},
 'artifacts/P3_MODEL_CATALOG_SOURCE/20260909_001/CONSULTATION.md': {'git_oid': '3f18755236e400b03dd2b5b8dc6f57e4867b6389',
                                                                    'mode': '100644',
                                                                    'old_sha256': None,
                                                                    'sha256': '09fd45a3862c68a6cb441676b6e6e8ba768bed982fb76ddc457c11e9369ab01b'},
 'artifacts/P3_MODEL_CATALOG_SOURCE/20260909_001/LICENSE': {'git_oid': '4606e72e042564097e8780d66c1d4dcb611869bd',
                                                            'mode': '100644',
                                                            'old_sha256': None,
                                                            'sha256': 'd17f227e4df5da1600391338865ce0f3055211760a36688f816941d58232d8dc'},
 'artifacts/P3_MODEL_CATALOG_SOURCE/20260909_001/MANIFEST.json': {'git_oid': 'b39c3db45204e48d464007b2833360bacae536cb',
                                                                  'mode': '100644',
                                                                  'old_sha256': None,
                                                                  'sha256': '45a8991fafa7937eeaab275d08bba172101b85c7a9b5396e54953a1f2176c068'},
 'artifacts/P3_MODEL_CATALOG_SOURCE/20260909_001/ModelListParams.json': {'git_oid': '11a3476240ca9dc59a3478a2a87530764d903878',
                                                                         'mode': '100644',
                                                                         'old_sha256': None,
                                                                         'sha256': 'de29a536c00a5b8f46f34dba417dabd93365305571a8ed200e33bea85db68b5a'},
 'artifacts/P3_MODEL_CATALOG_SOURCE/20260909_001/ModelListResponse.json': {'git_oid': '657a433f88ae548aa81fb1c2ee44ba4fc5a781f8',
                                                                           'mode': '100644',
                                                                           'old_sha256': None,
                                                                           'sha256': 'c7b58b332f6cf18fd64235409a6daf27bb9e6c09d12dcd0daa2f3dc628b55f6f'},
 'artifacts/P3_MODEL_CATALOG_SOURCE/20260909_001/NOTICE': {'git_oid': '2805899d56d0332d175cfc613c67d45d6f006db7',
                                                           'mode': '100644',
                                                           'old_sha256': None,
                                                           'sha256': '9d71575ecfd9a843fc1677b0efb08053c6ba9fd686a0de1a6f5382fd3c220915'},
 'artifacts/P3_MODEL_CATALOG_SOURCE/20260909_001/SHA256SUMS': {'git_oid': '91d694a7ed4ada856b9f7a3df0bf508643f45d0e',
                                                               'mode': '100644',
                                                               'old_sha256': None,
                                                               'sha256': 'cda1c2e605d1966facb9415816d01184b0dcf0e890895555845b7bbd304a6dfb'},
 'artifacts/P3_MODEL_CATALOG_SOURCE/20260909_001/SOURCE_RECHECK.json': {'git_oid': '26b51aff6620b3f22cf13b75ef74a71a2446bac7',
                                                                        'mode': '100644',
                                                                        'old_sha256': None,
                                                                        'sha256': '7862631b0004526a91904d64fdcea90de194a49c8c9dfd7b5271c45d95c1628a'},
 'artifacts/P3_MODEL_CATALOG_SOURCE/20260909_001/SOURCE_REFERENCES.json': {'git_oid': '75c1eea82d1331662b000ec92087b3a92fb3ed41',
                                                                           'mode': '100644',
                                                                           'old_sha256': None,
                                                                           'sha256': '7d503fcf0d957899864e2636a64c2b6eaf603b499b442a0ffd4b744aeaa08c73'},
 'artifacts/P3_MODEL_CATALOG_SOURCE/20260909_001/SOURCE_TREE_SELECTION.json': {'git_oid': 'f9f61cac66a1113997443a7eb3a5b7aefa2263d2',
                                                                               'mode': '100644',
                                                                               'old_sha256': None,
                                                                               'sha256': '777d22266bd9bc02694c610d003f0c3a54a2c6001b05f766a0cb3f3c0d95f8da'},
 'artifacts/P3_MODEL_CATALOG_SOURCE/20260909_001/TOOL_ERRORS.jsonl': {'git_oid': 'cb26c57bf1b2cda61604bd79984fcc9d9341c899',
                                                                      'mode': '100644',
                                                                      'old_sha256': None,
                                                                      'sha256': 'ae80503a3adc28ae20ff78ae4090d5e04fff9b5451a3917f113d77ea898b12d3'},
 'artifacts/P3_MODEL_CATALOG_SOURCE/20260909_001/codex-rs/models-manager/models.json': {'git_oid': '0c4137ad9560e1ac7b9baf1adc95dbc7051e2b6c',
                                                                                        'mode': '100644',
                                                                                        'old_sha256': None,
                                                                                        'sha256': 'eb0d7b9a5dcaf103895c5f8a14c16b269df46e039b375a55ba97f6238542d2ed'},
 'artifacts/P3_MODEL_CATALOG_SOURCE/20260909_001/codex-rs/models-manager/src/lib.rs': {'git_oid': 'cd7b59a0530b6ead4c3852d0a3217aa7115a4d81',
                                                                                       'mode': '100644',
                                                                                       'old_sha256': None,
                                                                                       'sha256': 'b31b6e8fdaebedbbf07999b27c02201020e8d876ae293ac05a8fe4bf051244d3'},
 'artifacts/P3_MODEL_CATALOG_SOURCE/20260909_001/codex-rs/protocol/src/openai_models.rs': {'git_oid': '25d34b250199f0185a9381a4f0a382a4182a0ff6',
                                                                                           'mode': '100644',
                                                                                           'old_sha256': None,
                                                                                           'sha256': '8ec03e1382ef5bc4350c93262d1eb8833c7462057e2e995887c6e147deb63758'},
 'artifacts/P3_MODEL_OPTION_VALIDATION/20260909_001/REPORT.json': {'git_oid': '3c9cbb5db4c27264ca87137a5cf547fb90bea5c3',
                                                                   'mode': '100644',
                                                                   'old_sha256': None,
                                                                   'sha256': '027a2519b50ef4c15956541ef978a689b1487b28d99e79d16809dd0ead1c06cf'},
 'artifacts/P3_MODEL_OPTION_VALIDATION/20260909_001/SHA256SUMS': {'git_oid': 'e4c38e66243dbad3cc31382065a3fe7266423cb6',
                                                                  'mode': '100644',
                                                                  'old_sha256': None,
                                                                  'sha256': '010eb006309e57addaceee1fe833d7d19238e3f1fa8af2f6024d9fe4095ca915'},
 'artifacts/P3_MODEL_OPTION_VALIDATION/20260909_001/inspection.stderr.txt': {'git_oid': 'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391',
                                                                             'mode': '100644',
                                                                             'old_sha256': None,
                                                                             'sha256': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'},
 'artifacts/P3_MODEL_OPTION_VALIDATION/20260909_001/inspection.stdout.txt': {'git_oid': '32716b81e48feb7ec9dbbb7f098d546bf82278c0',
                                                                             'mode': '100644',
                                                                             'old_sha256': None,
                                                                             'sha256': '618740cadb99edf510b3ac69ae0826443253fd968907e6255e402e5d92375f40'},
 'artifacts/P3_MODEL_OPTION_VALIDATION/dev_022/attempt_001.json': {'git_oid': '04c9afc97fdf6546e404d950e885e032b7cfe0e6',
                                                                   'mode': '100644',
                                                                   'old_sha256': None,
                                                                   'sha256': '18d3ac51386d85f90b2e8ae8fc033c52c18e53989e309882d6fc9bf7e4d6bb48'},
 'artifacts/P3_MODEL_OPTION_VALIDATION/dev_022/attempt_001.stderr.txt': {'git_oid': '528fbb6f238f1ef871ed428dac3f5c451441e12c',
                                                                         'mode': '100644',
                                                                         'old_sha256': None,
                                                                         'sha256': '552e27b6fefec049cb887655d4f478d04f5ea4a24326ecb7df0093b9d252878a'},
 'artifacts/P3_MODEL_OPTION_VALIDATION/dev_022/attempt_001.stdout.txt': {'git_oid': 'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391',
                                                                         'mode': '100644',
                                                                         'old_sha256': None,
                                                                         'sha256': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'},
 'configs/P3_FINITE_REVIEW_SCOPE_022.json': {'git_oid': '8a148d39ce67798129865c2b259252d3cb97b912',
                                             'mode': '100644',
                                             'old_sha256': None,
                                             'sha256': '46301a69ae7a2d0cdac537eb2127415e8d4ac3c4ab5d7e8ea00ff1a1894a9f0f'},
 'evidence/P3_FINITE_REVIEW_021_OBSERVATION_REVIEW.json': {'git_oid': 'd185a32dba159bdfecd83cc58b5776e3dfc9a3ba',
                                                           'mode': '100644',
                                                           'old_sha256': None,
                                                           'sha256': 'ac84e3c6b53f8e199962062b70a9ba519bc89535f59c2ba084d881bb852002d4'},
 'evidence/P3_MODEL_CATALOG_SOURCE_ROOT_VERIFICATION.json': {'git_oid': '64ce132982411c87802c25bb22e640a093bda158',
                                                             'mode': '100644',
                                                             'old_sha256': None,
                                                             'sha256': '2bc97cc3b7ae823614dfbdb7cf46116d88d10b7626688dad1b3aceddd5edac7d'},
 'evidence/REMOTE_CHECKPOINT_021_VERIFICATION.json': {'git_oid': 'd11bf349cbf05decd3e416ed01106fb4a527c7ba',
                                                      'mode': '100644',
                                                      'old_sha256': None,
                                                      'sha256': '8f0ece5b4b234383f1ad7a52891d8359e34e54283e76810afbfaaacf82fa58fc'},
 'reports/DIGEST_2026-09-09.md': {'git_oid': '64ea20e4a74216772aff168da704eff0f175f694',
                                  'mode': '100644',
                                  'old_sha256': '6dd9391f43bc6f17c488e1683933caff6095042125dcb8381ca52432f7782936',
                                  'sha256': 'dbd883849a63dcf5be34897b644eae3ccd52343b530c1008a7954d333b1fdbe4'},
 'reports/P3_CHECKPOINT_022_STATUS.md': {'git_oid': '3e3c40e44e18609913b50ff47e5c1834a9239415',
                                         'mode': '100644',
                                         'old_sha256': None,
                                         'sha256': 'fd9f9aeba9e798ba036d8f688e421aea6d358c6a05c80b2f4ba10b80ada1e366'},
 'scripts/checkpoint022_handoff.py': {'git_oid': '5b207f3b0f366df3c6a408b7e00b712043ac01c6',
                                      'mode': '100644',
                                      'old_sha256': None,
                                      'sha256': '9762772dcbbde8e4d1060f9963eb21ff28fb0efb1421e1ca3e9d79fb2e718a58'},
 'scripts/p3_finite_review_022.py': {'git_oid': '5f5240dbb37975e8fc1577dffc96d957a254282b',
                                     'mode': '100644',
                                     'old_sha256': None,
                                     'sha256': 'ef9b1bb0b19e3d8687aac88d70f268183f00c435c789420e47996211ea09e116'},
 'scripts/p3_reviewer_admission_022.py': {'git_oid': 'a732c30666bed9d93baece536c658cfd1bcc1dba',
                                          'mode': '100644',
                                          'old_sha256': None,
                                          'sha256': '329bccdfba14c93bb345841e6764b00f911b1ab8e3067636879a8a58194a783e'},
 'scripts/p3_reviewer_profile_022.py': {'git_oid': '21e32221173c3c081b69dcbab5f766c8baeb2fb7',
                                        'mode': '100644',
                                        'old_sha256': None,
                                        'sha256': '3c1d66ace2c3441d3c1ce1da98f2ec9bd253d3fe470b03d5ff54ec7ee7eeaa4d'},
 'scripts/p3_reviewer_session_022.py': {'git_oid': 'a4f56cf6e5aae6c0ef8981d09dd8ff90f430e4f2',
                                        'mode': '100644',
                                        'old_sha256': None,
                                        'sha256': 'fce5d0707ed16a0155cf0852e4e7d5e37d715ef14c33400c244a5f183b5c1730'},
 'state/BUDGET.json': {'git_oid': 'cd520e84e4b6881e3d8a16f1fe56122caf833b23',
                       'mode': '100644',
                       'old_sha256': 'ee983c02955d7f192a0acf05492fd320393e97fea70cf0c178671ec2240469ab',
                       'sha256': '8328afe274f4aed7a6824c29baf5fbd6128817ac3c384a0933245116837f83ea'},
 'state/CHECKPOINT_022.json': {'git_oid': '0b8ee5c788715e67ad8fbb615a8abbdc6bd9caa6',
                               'mode': '100644',
                               'old_sha256': None,
                               'sha256': 'cee766ec4fb3e48feb920b9aaf39b0f686bcc9c440cb253748832c3089e94248'},
 'state/ESCALATION.md': {'git_oid': '71edb8714b30d7b5df12c6e2e64d198136c7da87',
                         'mode': '100644',
                         'old_sha256': '482cca0d8f73483047c8658579b106b7b96fb8378d59d8806126e32ab0ba4700',
                         'sha256': '956cd6ec5a5bf48d741e64c165b005889fd722b31413e39ef191c3891fbbd60d'},
 'state/LEDGER.jsonl': {'git_oid': '123d89ad86bcbe769ba7c5b1b4855fadf4bb2ccb',
                        'mode': '100644',
                        'old_sha256': '19a91bfaf1165d8eab49181ccc93a7d368a13326ce05274e6567ba4d5e3f1da0',
                        'sha256': 'eee3457302e039f616f339f222d1fe409a03e8c3e6009b68180cc44ae43803cd'},
 'state/PROJECT_STATE.json': {'git_oid': '46442a236030c107d6d8368aed4a6226e89234eb',
                              'mode': '100644',
                              'old_sha256': 'c8670230a4a7eae974303e6f2f2b3b778881db10b746a3bbcb31e915d9444177',
                              'sha256': '8972261e27f8ba1abdd10f8a4b85242a7b67a3be582be0fbd6ff278fdb19be7b'},
 'state/escalations/2026-09-08_FINITE_REVIEW_019_APPROVED.md': {'git_oid': '3915745d5a4f76fec23e3bb1b87d29f1d0086859',
                                                                'mode': '100644',
                                                                'old_sha256': None,
                                                                'sha256': '482cca0d8f73483047c8658579b106b7b96fb8378d59d8806126e32ab0ba4700'},
 'state/tool_errors.jsonl': {'git_oid': 'abfaa927e1c3e9cadac5957d55e88c7d0a601c1e',
                             'mode': '100644',
                             'old_sha256': '00ecf0bb002efa1753cdfd534a624954d6337e05614ca4c338450b93272528f9',
                             'sha256': 'dfd9b0da4d555866804ed11b9e7f5eca6ea2b76e9ea5694e4cde8ae091510dd3'},
 'tests/test_p3_model_option_022.py': {'git_oid': '891450abd7cae30eb8a4c552d8b6e6baafd5f9da',
                                       'mode': '100644',
                                       'old_sha256': None,
                                       'sha256': '140ca5be10f446907341960c230a3e0a8bcb9604aa5df4c0fdbe8f9b3d87e733'}}


def sha(body):
    return hashlib.sha256(body).hexdigest()


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key: " + key)
        result[key] = value
    return result


def safe_name(name):
    if not isinstance(name, str) or not name or any(ord(c) < 32 for c in name):
        raise ValueError("Invalid package path")
    path = PurePosixPath(name)
    if (path.is_absolute() or path.as_posix() != name or "\\" in name or ":" in name
            or any(p.lower() in (".", "..", ".git") for p in path.parts)
            or path.parts[0] in ("delivery", "private_sources")
            or path.name == "IDEAS_PARKED.md" or path.suffix.lower() == ".pdf"):
        raise ValueError("Disallowed package path: " + name)
    return name


def load_package(path, expected_hash):
    if not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
        raise ValueError("Expected ZIP SHA-256 must have 64 lowercase hex characters")
    if path.stat().st_size > MAX_BYTES or sha(path.read_bytes()) != expected_hash:
        raise ValueError("ZIP size or SHA-256 differs from the supplied checkpoint")
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        names = [e.filename for e in entries]
        if len(names) != len(set(names)) or sum(e.file_size for e in entries) > MAX_BYTES:
            raise ValueError("Duplicate ZIP members or oversized uncompressed payload")
        manifest = json.loads(archive.read("HANDOFF.json"), object_pairs_hook=unique)
        if (set(manifest) != {"checkpoint_id", "base_commit", "files"}
                or manifest["checkpoint_id"] != "P3_CHECKPOINT_023"
                or manifest["base_commit"] != BASE
                or not isinstance(manifest["files"], dict) or not manifest["files"]):
            raise ValueError("Unexpected handoff manifest")
        files = manifest["files"]
        if set(names) != {"HANDOFF.json"} | {"files/" + n for n in files}:
            raise ValueError("ZIP must contain exactly the declared files and HANDOFF.json")
        for name, entry in files.items():
            safe_name(name)
            if set(entry) != {"old_sha256", "sha256", "mode"} or entry["mode"] not in ("100644", "100755"):
                raise ValueError("Unexpected entry: " + name)
            for key in ("old_sha256", "sha256"):
                if key == "old_sha256" and entry[key] is None:
                    continue
                if not isinstance(entry[key], str) or not re.fullmatch(r"[0-9a-f]{64}", entry[key]):
                    raise ValueError("Invalid content hash: " + name)
            entry["body"] = archive.read("files/" + name)
            if sha(entry["body"]) != entry["sha256"]:
                raise ValueError("Payload byte mismatch: " + name)
            if any(p.as_posix() in files for p in PurePosixPath(name).parents):
                raise ValueError("File/parent collision: " + name)
    if ".gitattributes" in files and files[".gitattributes"]["body"] != ATTRIBUTES:
        raise ValueError("Artifact byte-preservation rule must remain unchanged")
    if set(PREVIOUS_FILES) - set(files):
        raise ValueError("Checkpoint023 must carry every previously delivered022 transition")
    return files


def ordinary(root, name, directory=False):
    path = root
    parts = PurePosixPath(name).parts
    for i, part in enumerate(parts):
        path = path / part
        if path.is_symlink():
            raise ValueError("Symlink refused: " + name)
        if not path.exists():
            return root / name
        want_dir = i < len(parts) - 1 or directory
        if not (path.is_dir() if want_dir else path.is_file()):
            raise ValueError("Unexpected filesystem object: " + name)
    return path


class Git:
    def __init__(self, root):
        self.root = root

    def run(self, *args):
        env = os.environ.copy()
        for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
                    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"):
            env.pop(key, None)
        env["GIT_OPTIONAL_LOCKS"] = "0"
        argv = ["git", "-C", str(self.root), *args]
        result = subprocess.run(argv, capture_output=True, env=env)
        if result.returncode:
            record = {"command": argv, "exit_code": result.returncode,
                      "stdout": result.stdout.decode("utf-8", "replace"),
                      "stderr": result.stderr.decode("utf-8", "replace")}
            # Exact output is printed even in inspection mode; no error-log write.
            print(json.dumps(record, ensure_ascii=True), file=sys.stderr)
            raise RuntimeError("Git failed; save the printed record. No commit was attempted.")
        return result.stdout

    def text(self, *args):
        return self.run(*args).decode().strip()

    def tree(self, revision):
        result = {}
        for record in self.run("ls-tree", "-r", "-z", revision).split(b"\0"):
            if record:
                metadata, name = record.split(b"\t", 1)
                mode, kind, oid = metadata.decode().split()
                result[name.decode()] = (mode, oid)
        return result

    def index(self):
        result = {}
        for record in self.run("ls-files", "--stage", "-z").split(b"\0"):
            if record:
                metadata, name = record.split(b"\t", 1)
                mode, oid, stage = metadata.decode().split()
                if stage != "0":
                    raise ValueError("Unmerged index entries exist")
                result[name.decode()] = (mode, oid)
        return result


def known_trees(git, files):
    base = git.tree(BASE)
    previous, expected = dict(base), dict(base)
    for name, entry in PREVIOUS_FILES.items():
        old = git.run("cat-file", "blob", base[name][1]) if name in base else None
        if (sha(old) if old is not None else None) != entry["old_sha256"]:
            raise ValueError("Pinned previous old hash differs from base: " + name)
        previous[name] = (entry["mode"], entry["git_oid"])
    for name, entry in files.items():
        old = git.run("cat-file", "blob", base[name][1]) if name in base else None
        if (sha(old) if old is not None else None) != entry["old_sha256"]:
            raise ValueError("Declared old hash differs from pinned base: " + name)
        oid = hashlib.sha1(b"blob " + str(len(entry["body"])).encode() + b"\0" + entry["body"]).hexdigest()
        expected[name] = (entry["mode"], oid)
    return base, previous, expected


def classify_head(git, head, previous, expected):
    if head == BASE:
        return "base021"
    parents = git.text("rev-list", "--parents", "-n", "1", head).split()
    tree = git.tree(head)
    if parents == [head, BASE] and tree == previous:
        return "checkpoint022"
    if tree == expected and len(parents) == 2:
        parent = parents[1]
        if parent == BASE:
            return "checkpoint023"
        if (git.text("rev-list", "--parents", "-n", "1", parent).split() == [parent, BASE]
                and git.tree(parent) == previous):
            return "checkpoint023"
    raise ValueError("HEAD is neither base021, exact022 child, nor exact023 child of those")


def inspect(root, files, complete=False):
    if root.is_symlink() or root.resolve() != root.absolute() or not root.is_dir():
        raise ValueError("Target must be the existing ordinary ~/ARC_Independent_Lab directory")
    if not ordinary(root, ".git", directory=True).is_dir():
        raise ValueError("Expected a contained ordinary .git directory")
    git = Git(root)
    if (Path(git.text("rev-parse", "--show-toplevel")) != root
            or Path(git.text("rev-parse", "--absolute-git-dir")) != root / ".git"
            or (root / git.text("rev-parse", "--git-common-dir")).resolve() != root / ".git"
            or git.text("branch", "--show-current") != "main"):
        raise ValueError("Repository root, Git directory, or main branch differs")
    for options in (("--all",), ("--push", "--all")):
        if git.text("remote", "get-url", *options, "origin").splitlines() != [REMOTE]:
            raise ValueError("Origin differs from the fixed project URL; no URL changed")
    if ordinary(root, ".gitattributes").read_bytes() != ATTRIBUTES:
        raise ValueError("Expected exact artifact byte-preservation rule")
    base, previous, expected = known_trees(git, files)
    head = git.text("rev-parse", "HEAD")
    disposition = classify_head(git, head, previous, expected)
    if disposition == "checkpoint023":
        complete = True
    index = git.index()
    if complete:
        if index != expected:
            raise ValueError("Actual index differs from the complete expected tree")
        for name, entry in files.items():
            if sha(git.run("cat-file", "blob", index[name][1])) != entry["sha256"]:
                raise ValueError("Actual staged blob SHA-256 differs: " + name)
    else:
        if set(index) - set(expected) or set(base) - set(index):
            raise ValueError("Unexpected index additions or staged deletions")
        for name, value in index.items():
            if value not in (base.get(name), previous.get(name), expected.get(name)):
                raise ValueError("Unrecognized staged content or mode: " + name)
    dirty = {n.decode() for n in git.run("diff", "--name-only", "--no-renames", "-z").split(b"\0") if n}
    if dirty - set(files):
        raise ValueError("Unrelated tracked working changes: " + ", ".join(sorted(dirty - set(files))))
    snapshot = {}
    for name, entry in files.items():
        path = ordinary(root, name)
        body = path.read_bytes() if path.exists() else None
        actual = sha(body) if body is not None else None
        accepted = {entry["sha256"]} if complete else {
            entry["old_sha256"], entry["sha256"],
            PREVIOUS_FILES.get(name, {}).get("sha256", entry["old_sha256"])}
        if actual not in accepted:
            raise ValueError("Unrecognized working bytes; preserved: " + name)
        if path.exists():
            mode = "100755" if path.stat().st_mode & stat.S_IXUSR else "100644"
            accepted_modes = {entry["mode"]} if actual == entry["sha256"] else set()
            if not complete and actual == entry["old_sha256"] and name in base:
                accepted_modes.add(base[name][0])
            if not complete and name in PREVIOUS_FILES and actual == PREVIOUS_FILES[name]["sha256"]:
                accepted_modes.add(PREVIOUS_FILES[name]["mode"])
            if mode not in accepted_modes:
                raise ValueError("Unexpected working executable mode: " + name)
        snapshot[name] = body
    print("Verified local HEAD:", head)
    print("Recognized checkpoint state:", disposition)
    print("Verified complete staged checkpoint." if complete else "Verified known base021/022/023 transitions.")
    return git, head, snapshot, disposition


def apply(root, files):
    git, head, snapshot, disposition = inspect(root, files)
    if disposition == "checkpoint023":
        print("Checkpoint commit already exists; no files or index changed.")
        return
    backup_parent = ordinary(root, "delivery/checkpoint023_backups", directory=True)
    backup_parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ-")
    backup = Path(tempfile.mkdtemp(prefix=stamp, dir=backup_parent))
    # Preserve the pre-stage index and every replaced file, including control files.
    index_path = ordinary(root, ".git/index")
    (backup / "index.before").write_bytes(index_path.read_bytes())
    for name, body in snapshot.items():
        if body is not None and body != files[name]["body"]:
            dest = backup / "files" / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(body)
    print("Backup:", backup)
    for name, entry in sorted(files.items()):
        path = ordinary(root, name)
        current = path.read_bytes() if path.exists() else None
        if current != snapshot[name]:
            raise ValueError("Working file changed during application: " + name)
        current_mode = "100755" if path.exists() and path.stat().st_mode & stat.S_IXUSR else "100644"
        if current == entry["body"] and current_mode == entry["mode"]:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix="replacement-", dir=backup)
        with os.fdopen(fd, "wb") as handle:
            os.fchmod(handle.fileno(), int(entry["mode"][-3:], 8))
            handle.write(entry["body"])
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    git.run("add", "--", *sorted(files))
    inspect(root, files, complete=True)
    print("READY: installed bytes and actual staged blobs match. No commit or push was attempted.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zip_path", type=Path)
    parser.add_argument("--sha256", required=True)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    files = load_package(args.zip_path, args.sha256)
    root = Path.home() / "ARC_Independent_Lab"
    print("Target:", root)
    print("Pinned base:", BASE)
    for name, entry in sorted(files.items()):
        print(name, entry["old_sha256"] or "absent", "->", entry["sha256"])
    if args.apply:
        apply(root, files)
    else:
        inspect(root, files, complete=args.verify)
        print("Inspection only. No changes or network calls were made.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, OSError, KeyError, TypeError, zipfile.BadZipFile) as error:
        print("STOP:", error, file=sys.stderr)
        sys.exit(1)
