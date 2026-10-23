from pathlib import Path
import json,unreal
ROOT=Path(__file__).resolve().parent
assert Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).resolve()==ROOT.parents[6]
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert world.get_path_name().startswith('/Game/Prototype/Maps/Lvl_AssetLab.')
assert not (ROOT/'Evidence/baseline.json').exists()
def xyz(v):return [v.x,v.y,v.z]
actors=[]
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    r=a.get_actor_rotation();actors.append(dict(path=a.get_path_name(),label=a.get_actor_label(),location=xyz(a.get_actor_location()),rotation=[r.pitch,r.yaw,r.roll],scale=xyz(a.get_actor_scale3d()),folder=str(a.get_folder_path()),components=[dict(path=c.get_path_name(),mesh=c.static_mesh.get_path_name() if c.static_mesh else None,overrides=[m.get_path_name() if m else None for m in c.get_editor_property('override_materials')]) for c in a.get_components_by_class(unreal.StaticMeshComponent)]))
(ROOT/'Evidence/baseline.json').write_text(json.dumps(dict(project=unreal.Paths.project_dir(),world=world.get_path_name(),actors=actors),indent=2))
unreal.log('HE02_BASELINE_READY')
