from pathlib import Path
import json,unreal
ROOT=Path(__file__).resolve().parent
data=json.loads((ROOT/'Evidence/bootstrap.json').read_text())
actors={a.get_path_name():a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()}
out=[]
for p in data['actors']:
    a=actors[p['path']]
    if not a.get_components_by_class(unreal.StaticMeshComponent):continue
    o,e=a.get_actor_bounds(False)
    if o.y+e.y>1800 and o.y-e.y<3800 and o.z+e.z>50 and o.x-e.x<1500 and o.x+e.x>-2300:
        out.append(dict(label=a.get_actor_label(),min=[o.x-e.x,o.y-e.y,o.z-e.z],max=[o.x+e.x,o.y+e.y,o.z+e.z]))
(ROOT/'Evidence/existing_north_bounds.json').write_text(json.dumps(out,indent=2)+'\n')
