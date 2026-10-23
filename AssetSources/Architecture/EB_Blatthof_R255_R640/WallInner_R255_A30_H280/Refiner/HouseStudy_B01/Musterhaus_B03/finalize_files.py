"""Hash final deliverables and distinguish inherited changes from the B03 scope."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[6]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
baseline=json.loads((ROOT/'Evidence/baseline_files.json').read_text())
changed=[];missing=[]
for name,digest in baseline.items():
    p=REPO/name
    if not p.exists():missing.append(name)
    elif sha(p)!=digest:changed.append(name)
allowed={'Content/Prototype/Maps/Lvl_AssetLab.umap','docs/TECHNICAL_STATUS.md'}
assert not missing and set(changed)<=allowed,(missing,changed)
preservation=dict(status='passed',baseline_files=len(baseline),unchanged_files=len(baseline)-len(changed),changed_existing=changed,deleted_existing=missing,
    source_b01_b02_and_creator_unchanged=True,other_existing_unreal_assets_unchanged=True,config_source_tools_unchanged=True)
(ROOT/'Evidence/preservation.json').write_text(json.dumps(preservation,indent=2)+'\n')
manifest=json.loads((ROOT/'manifest.json').read_text())
manifest['status']='review_ready';manifest['accepted']=False
manifest['source_sha256']=sha(ROOT/manifest['source'])
manifest['source_hashes']={p.relative_to(ROOT).as_posix():sha(p) for folder in ['Exports','Textures'] for p in (ROOT/folder).glob('*') if p.is_file()}
manifest['unreal_hashes']={p.relative_to(REPO).as_posix():sha(p) for folder in ['Content/Art/Architecture/ElvenHouseB03','Content/Art/Furniture/ElvenHouseB03','Content/Art/Materials/ElvenHouseB03','Content/Art/Textures/ElvenHouseB03'] for p in (REPO/folder).rglob('*.uasset')}
manifest['lab_sha256']=sha(REPO/'Content/Prototype/Maps/Lvl_AssetLab.umap')
manifest['evidence']={p.name:json.loads(p.read_text()).get('status','recorded') for p in (ROOT/'Evidence').glob('*.json') if p.name!='baseline_files.json'}
manifest['spaces']=dict(living_dining_clear_m=[9.52,6.96],sleeping_clear_m=[4.88,4.44],storage_clear_m=[4.52,4.44],interior_doorway_clear_cm=[120,235])
(ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
files=[p for p in ROOT.rglob('*') if p.is_file() and p.name!='SHA256SUMS' and '__pycache__' not in p.parts and not p.name.endswith('.blend1')]
(ROOT/'SHA256SUMS').write_text(''.join(sha(p)+'  '+p.relative_to(ROOT).as_posix()+'\n' for p in sorted(files)))
print(json.dumps(dict(preservation=preservation,hashed_files=len(files),new_unreal_packages=len(manifest['unreal_hashes']))))
