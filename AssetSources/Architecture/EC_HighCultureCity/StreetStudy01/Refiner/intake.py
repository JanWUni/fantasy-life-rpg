"""Read-only provenance checks and preservation baseline for the assigned Creator handoff."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parent;CREATOR=ROOT.parent/'Creator';REPO=ROOT.parents[4]
COMMIT='08e7d7eea4a161a5e5025d656ca5b199ed0130da'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO).decode('utf-8').strip()
def write(name,data):
    p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,indent=2)+'\n')
def baseline():
    assert REPO==Path('E:/Business/fantasy-rpg-refiner')
    assert git('branch','--show-current')=='assets/refiner'
    assert not git('diff','--cached','--name-only'),'Existing staged changes: stop before cherry-pick'
    files={}
    for folder in ['Content','AssetSources','Config','Source','Tools','docs']:
        for p in (REPO/folder).rglob('*'):
            if p.is_file() and not p.is_relative_to(ROOT) and '__pycache__' not in p.parts and not p.name.endswith('.blend1'):
                files[p.relative_to(REPO).as_posix()]=sha(p)
    for p in [REPO/'AGENTS.md',REPO/'.gitattributes',REPO/'.gitignore',REPO/'FantasyLifeRPG.uproject']:
        files[p.relative_to(REPO).as_posix()]=sha(p)
    write('Evidence/preservation_before.json',dict(head=git('rev-parse','HEAD'),files=files,git_status=git('status','--short')))
    print('PRESERVATION_BASELINE',len(files))
def verify():
    sums={}
    for line in (CREATOR/'SHA256SUMS').read_text().splitlines():
        digest,name=line.split(maxsplit=1);name=name.lstrip('* ');p=(CREATOR/name).resolve()
        assert p.is_relative_to(CREATOR.resolve()) and p.is_file(),name
        actual=sha(p);assert actual==digest,(name,digest,actual);sums[name]=digest
    lfs={};tree=git('ls-tree','-r','--name-only',COMMIT,'--',CREATOR.relative_to(REPO).as_posix()).splitlines()
    for relative in tree:
        blob=subprocess.check_output(['git','show',COMMIT+':'+relative],cwd=REPO)
        if blob.startswith(b'version https://git-lfs.github.com/spec/v1\n'):
            text=blob.decode();oid=next(s[11:] for s in text.splitlines() if s.startswith('oid sha256:'))
            size=int(next(s[5:] for s in text.splitlines() if s.startswith('size ')))
            p=REPO/relative;assert p.stat().st_size==size and sha(p)==oid,(relative,'LFS pointer or incomplete object')
            lfs[relative]=dict(oid=oid,size=size)
        else:
            assert (REPO/relative).read_bytes()==blob,('Creator text differs from input commit',relative)
    header=(CREATOR/'StreetStudy01.blend').read_bytes()[:12]
    assert not header.startswith(b'version http'),'Unhydrated Blender LFS pointer'
    write('Evidence/intake_verification.json',dict(status='passed',input_commit=COMMIT,checked_sha256_files=sums,
        lfs_objects=lfs,blend_header_hex=header.hex(),creator_matches_input_commit=True,branch=git('branch','--show-current'),head_after_intake=git('rev-parse','HEAD')))
    print('INTAKE_PASSED',len(sums),'hashes',len(lfs),'LFS objects')
if __name__=='__main__':{'baseline':baseline,'verify':verify}[sys.argv[-1]]()
