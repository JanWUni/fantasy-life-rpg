from pathlib import Path
import json,unreal
ROOT=Path(__file__).resolve().parent
assert Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).resolve()==ROOT.parents[6]
items=[]
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if not a.get_components_by_class(unreal.StaticMeshComponent):continue
    c,e=a.get_actor_bounds(False);lo=[c.x-e.x,c.y-e.y,c.z-e.z];hi=[c.x+e.x,c.y+e.y,c.z+e.z]
    if hi[0]>=1400 and lo[0]<=2900 and hi[1]>=1000 and lo[1]<=2050:
        items.append(dict(label=a.get_actor_label(),lo=lo,hi=hi))
(ROOT/'Evidence/area.json').write_text(json.dumps(items,indent=2))

