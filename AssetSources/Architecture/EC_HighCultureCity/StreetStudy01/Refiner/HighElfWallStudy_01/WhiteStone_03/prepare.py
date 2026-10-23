from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parent;repo=R.parents[6];src=R.parent/'MaterialStudy_02'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not (R/'Evidence/files_before.json').exists()
baseline={p.relative_to(repo).as_posix():sha(p) for f in ['Content','AssetSources','Config','Source','Tools','docs'] for p in (repo/f).rglob('*') if p.is_file() and not p.is_relative_to(R) and p.suffix not in ['.blend1','.pyc']}
(R/'Evidence/files_before.json').write_text(json.dumps(baseline,indent=2))
shutil.copy2(repo/'Content/Prototype/Maps/Lvl_AssetLab.umap',R/'Evidence/Lab_before.umap')
data=dict(source='HighElf_WhiteStoneComparison_03.blend',input_source=str(src/'HighElf_MaterialComparison_02.blend'),input_sha256=sha(src/'HighElf_MaterialComparison_02.blend'),colors={'Ivory':dict(old=[.55,.515,.44],white=[.73,.70,.62]),'CarvedStone':dict(old=[.64,.605,.535],white=[.84,.82,.74]),'RecessStone':dict(old=[.39,.405,.38],white=[.49,.53,.53])})
(R/'manifest.json').write_text(json.dumps(data,indent=2))
print('BASELINE_READY',len(baseline))
