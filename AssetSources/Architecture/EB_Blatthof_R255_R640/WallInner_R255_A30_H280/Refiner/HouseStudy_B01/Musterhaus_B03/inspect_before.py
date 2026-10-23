"""Native read-only snapshot, including fixtures and exact instance assignments."""
from pathlib import Path
import json,unreal
ROOT=Path(__file__).resolve().parent
assert Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).resolve()==Path('E:/Business/fantasy-rpg-refiner')
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name().startswith('/Game/Prototype/Maps/Lvl_AssetLab.')
def v(x):return [x.x,x.y,x.z]
def snap(a):
    r=a.get_actor_rotation()
    meshes=[]
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        meshes.append(dict(path=c.get_path_name(),mesh=c.static_mesh.get_path_name() if c.static_mesh else None,
            overrides=[m.get_path_name() if m else None for m in c.get_editor_property('override_materials')]))
    return dict(path=a.get_path_name(),label=a.get_actor_label(),class_name=a.get_class().get_name(),position=v(a.get_actor_location()),
        rotation=[r.pitch,r.yaw,r.roll],scale=v(a.get_actor_scale3d()),folder=str(a.get_folder_path()),meshes=meshes)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
data=dict(map=world.get_path_name(),actors=[snap(a) for a in actors],lights=[])
for a in actors:
    for c in a.get_components_by_class(unreal.LightComponent):
        data['lights'].append(dict(actor=a.get_actor_label(),component=c.get_class().get_name(),intensity=c.get_editor_property('intensity')))
(ROOT/'Evidence/lab_before.json').write_text(json.dumps(data,indent=2)+'\n')
unreal.log('B03_BASELINE_SAVED '+str(len(actors)))
