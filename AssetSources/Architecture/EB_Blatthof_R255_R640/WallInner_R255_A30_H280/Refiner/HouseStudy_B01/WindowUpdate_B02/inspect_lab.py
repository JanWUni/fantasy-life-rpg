"""Read the actual Refiner Lab before placing anything."""
from pathlib import Path
import json
import unreal
ROOT=Path('E:/Business/fantasy-rpg-refiner')
assert Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).resolve()==ROOT
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name().startswith('/Game/Prototype/Maps/Lvl_AssetLab.')
out=[]
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    center,extent=a.get_actor_bounds(False)
    out.append(dict(path=a.get_path_name(),label=a.get_actor_label(),kind=a.get_class().get_name(),
        position=[a.get_actor_location().x,a.get_actor_location().y,a.get_actor_location().z],
        rotation=[a.get_actor_rotation().pitch,a.get_actor_rotation().yaw,a.get_actor_rotation().roll],
        scale=[a.get_actor_scale3d().x,a.get_actor_scale3d().y,a.get_actor_scale3d().z],
        meshes=[dict(path=c.get_path_name(),mesh=c.static_mesh.get_path_name() if c.static_mesh else None,
            overrides=[m.get_path_name() if m else None for m in c.get_editor_property('override_materials')])
            for c in a.get_components_by_class(unreal.StaticMeshComponent)],
        bounds_center=[center.x,center.y,center.z],bounds_extent=[extent.x,extent.y,extent.z],
        folder=str(a.get_folder_path())))
path=ROOT/'Saved/HouseB02/lab_before.json'
path.write_text(json.dumps(dict(world=world.get_path_name(),actors=out),indent=2)+'\n')
unreal.log('HOUSE_B02_LAB_INSPECTED')
