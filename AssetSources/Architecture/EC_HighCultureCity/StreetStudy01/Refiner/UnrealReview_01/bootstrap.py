"""Native verification/session settings absent from the current MCP public API."""
from pathlib import Path
import json,re,unreal
ROOT=Path(__file__).resolve().parent
assert Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).resolve()==ROOT.parents[5]==Path('E:/Business/fantasy-rpg-refiner')
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name().startswith('/Game/Prototype/Maps/Lvl_AssetLab.')
settings=dict(import_uniform_scale=1.,convert_scene=True,convert_scene_unit=False,force_front_x_axis=False,
    transform_vertex_to_absolute=True,bake_pivot_in_vertex=False,auto_generate_collision=False,one_convex_hull_per_ucx=True,
    generate_lightmap_u_vs=True,normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS,
    normal_generation_method=unreal.FBXNormalGenerationMethod.MIKK_T_SPACE)
defaults=unreal.get_default_object(unreal.FbxStaticMeshImportData);before={}
for key,value in settings.items():
    old=defaults.get_editor_property(key)
    if isinstance(old,(bool,int,float,str)):before[key]=old
    else:
        match=re.match(r'<(\w+)\.(\w+):',str(old));assert match,str(old)
        before[key]=dict(enum_class=match[1],enum_member=match[2])
    defaults.set_editor_property(key,value)
prior=unreal.SystemLibrary.get_console_variable_int_value('Interchange.FeatureFlags.Import.FBX')
unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
def vec(v):return [v.x,v.y,v.z]
actors=[]
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    t=a.get_actor_transform();r=a.get_actor_rotation()
    actors.append(dict(path=a.get_path_name(),label=a.get_actor_label(),location=vec(a.get_actor_location()),rotation=[r.pitch,r.yaw,r.roll],
        scale=vec(a.get_actor_scale3d()),folder=str(a.get_folder_path()),components=[dict(path=c.get_path_name(),mesh=c.static_mesh.get_path_name() if c.static_mesh else None,
        overrides=[m.get_path_name() if m else None for m in c.get_editor_property('override_materials')]) for c in a.get_components_by_class(unreal.StaticMeshComponent)]))
data=dict(project=unreal.Paths.project_dir(),world=world.get_path_name(),actors=actors,prior_importer_cvar=prior,prior_fbx_defaults=before)
(ROOT/'Evidence/bootstrap.json').write_text(json.dumps(data,indent=2)+'\n')
unreal.log('STUDY_AB_BOOTSTRAP_READY '+str(len(actors)))
