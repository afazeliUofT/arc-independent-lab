import hashlib, importlib.util, json, os, subprocess, tempfile, zipfile
from pathlib import Path
ROOT = Path.cwd()
SPEC = importlib.util.spec_from_file_location('handoff003', ROOT/'scripts/checkpoint003_handoff.py')
H = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(H)
OUT = {'helper_sha256': H.sha((ROOT/'scripts/checkpoint003_handoff.py').read_bytes()), 'scope': 'Contained synthetic repositories only; no public network or real-project Git mutation.', 'cases': [], 'nonzero_git_commands': []}
TEMP = Path(tempfile.mkdtemp(prefix='checkpoint003_fixture_', dir=ROOT/'delivery'))

def git(repo,*args):
    p=subprocess.run(['git','-C',str(repo),*args],capture_output=True)
    if p.returncode:
        OUT['nonzero_git_commands'].append({'argv':list(args),'exit_code':p.returncode,'stdout':p.stdout.decode(errors='replace'),'stderr':p.stderr.decode(errors='replace')})
        raise RuntimeError(p.stderr)
    return p.stdout.decode().strip()

def fixture(name, crlf_doc=False):
    repo=TEMP/name; repo.mkdir()
    git(repo,'init','-q','-b','main');git(repo,'config','user.name','Contained Fixture');git(repo,'config','user.email','fixture@localhost')
    git(repo,'config','core.autocrlf','input');git(repo,'remote','add','origin',H.REMOTE)
    (repo/'.gitattributes').write_bytes(H.ATTRIBUTES)
    (repo/'delivery').mkdir();(repo/'.gitignore').write_text('delivery/\n')
    (repo/'old.txt').write_bytes(b'old\n');(repo/'unrelated.txt').write_bytes(b'untouched\n')
    (repo/'artifacts').mkdir();(repo/'artifacts/original.csv').write_bytes(b'a,b\r\n1,2\r\n')
    git(repo,'add','.');git(repo,'commit','-qm','fixture base')
    H.BASE=git(repo,'rev-parse','HEAD')
    files={'old.txt':{'old_sha256':H.sha(b'old\n'),'sha256':H.sha(b'new\r\n' if crlf_doc else b'new\n'),'mode':'100644','body':b'new\r\n' if crlf_doc else b'new\n'},'artifacts/new.csv':{'old_sha256':None,'sha256':H.sha(b'x,y\r\n3,4\r\n'),'mode':'100644','body':b'x,y\r\n3,4\r\n'}}
    return repo,files

def refusal(label, thunk):
    try: thunk()
    except (ValueError,RuntimeError) as e:
        OUT['cases'].append({'case':label,'result':'expected refusal','message':str(e)})
    else: raise AssertionError('Expected refusal: '+label)

repo,files=fixture('happy')
index_before=(repo/'.git/index').read_bytes()
H.inspect(repo,files)
assert (repo/'.git/index').read_bytes()==index_before
OUT['cases'].append({'case':'inspection','result':'index unchanged'})
# Real partial application: one delivered file already installed but not staged.
(repo/'old.txt').write_bytes(files['old.txt']['body'])
H.apply(repo,files);H.apply(repo,files)
for n,e in files.items():
    oid=git(repo,'rev-parse',':'+n)
    actual=subprocess.run(['git','-C',str(repo),'cat-file','blob',oid],capture_output=True,check=True).stdout
    assert H.sha(actual)==e['sha256']
assert git(repo,'rev-parse','HEAD')==H.BASE
OUT['cases'].append({'case':'partial application and repeat under core.autocrlf=input','result':'exact worktree/index CRLF artifact bytes; base HEAD unchanged'})
git(repo,'commit','-qm','fixture checkpoint');commit=git(repo,'rev-parse','HEAD')
H.inspect(repo,files,complete=True);H.apply(repo,files)
assert git(repo,'rev-parse','HEAD')==commit
OUT['cases'].append({'case':'completed direct-child retry','result':'exact expected tree accepted; no duplicate commit'})
git(repo,'rm','--cached','--','artifacts/new.csv')
before=(repo/'.git/index').read_bytes()
refusal('staged deletion after completed checkpoint',lambda:H.apply(repo,files))
assert (repo/'.git/index').read_bytes()==before

repo,files=fixture('dirty_worktree')
(repo/'unrelated.txt').write_text('human edit\n')
before=(repo/'.git/index').read_bytes()
refusal('unrelated working edit',lambda:H.apply(repo,files))
assert (repo/'old.txt').read_bytes()==b'old\n' and (repo/'.git/index').read_bytes()==before

repo,files=fixture('dirty_index')
(repo/'old.txt').write_bytes(b'human staged edit\n');git(repo,'add','old.txt');(repo/'old.txt').write_bytes(b'old\n')
before=(repo/'.git/index').read_bytes()
refusal('different hidden staged edit',lambda:H.apply(repo,files))
assert (repo/'.git/index').read_bytes()==before

repo,files=fixture('untracked_collision')
(repo/'artifacts/new.csv').write_bytes(b'human new file\n')
refusal('conflicting untracked destination',lambda:H.apply(repo,files))
assert (repo/'old.txt').read_bytes()==b'old\n' and (repo/'artifacts/new.csv').read_bytes()==b'human new file\n'

repo,files=fixture('normalizer',crlf_doc=True)
refusal('Git transforms a text payload despite exact worktree bytes',lambda:H.apply(repo,files))
assert git(repo,'rev-parse','HEAD')==H.BASE and (repo/'old.txt').read_bytes()==b'new\r\n'
assert list((repo/'delivery/checkpoint003_backups').glob('*/index.before'))
OUT['cases'].append({'case':'normalization refusal preservation','result':'no commit; exact worktree and pre-stage index backup retained; do not commit until corrected'})

repo,files=fixture('zip')
manifest={'checkpoint_id':'P1_CHECKPOINT_003','base_commit':H.BASE,'files':{n:{k:v for k,v in e.items() if k!='body'} for n,e in files.items()}}
package=TEMP/'package.zip'
with zipfile.ZipFile(package,'w') as z:
    z.writestr('HANDOFF.json',json.dumps(manifest))
    for n,e in files.items():z.writestr('files/'+n,e['body'])
assert H.load_package(package,H.sha(package.read_bytes()))==files
refusal('wrong published ZIP hash',lambda:H.load_package(package,'0'*64))
OUT['cases'].append({'case':'ZIP manifest','result':'full hashes and declared members accepted'})
OUT['fixture_root']=str(TEMP)
(ROOT/'evidence/CHECKPOINT_003_HANDOFF_VERIFICATION.json').write_text(json.dumps(OUT,indent=2)+'\n')
print(json.dumps(OUT,indent=2))
