from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[6]
assert REPO==Path('E:/Business/fantasy-rpg-refiner')
out=ROOT/'Evidence';out.mkdir(exist_ok=True)
files={}
for folder in ['Content','AssetSources','docs','Config','Source','Tools']:
    for p in (REPO/folder).rglob('*'):
        if p.is_file() and not p.is_relative_to(ROOT) and '__pycache__' not in p.parts and not p.name.endswith('.blend1'):
            files[p.relative_to(REPO).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
(out/'baseline_files.json').write_text(json.dumps(files,indent=2)+'\n')
print('Baseline files',len(files))
