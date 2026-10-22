"""Explicit legacy reimport fallback: MCP import_file rejects existing assets."""
from pathlib import Path
import json
import unreal

ROOT=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).resolve()
assert ROOT==Path('E:/Business/fantasy-rpg-refiner')
SOURCE=ROOT/'AssetSources/Architecture/EB_Blatthof_R255_R640/WallInner_R255_A30_H280/Refiner/HouseStudy_B01'
BASE='/Game/Art/Architecture/ElvenHouseB01'
MAP=BASE+'/Maps/Lvl_ElvenHouseB01_Review'
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name()==MAP+'.'+MAP.rsplit('/',1)[-1]
assert unreal.SystemLibrary.get_console_variable_int_value('Interchange.FeatureFlags.Import.FBX')==0
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
smes=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)


def xyz(v):
    return [v.x,v.y,v.z]


def inspect(mesh):
    bounds=mesh.get_bounding_box()
    return dict(bounds=[xyz(bounds.min),xyz(bounds.max)],triangles=mesh.get_num_triangles(0),
        slots=[str(m.material_slot_name) for m in mesh.static_materials],
        materials=[m.material_interface.get_path_name() for m in mesh.static_materials],
        hulls=smes.get_convex_collision_count(mesh),
        importer=mesh.get_editor_property('asset_import_data').get_class().get_name())


report={}
for name in ('SM_EH_Wall_SolidA_200x24x320','SM_EH_Roof_Mid_W1000'):
    mesh=unreal.load_asset(BASE+'/Meshes/'+name)
    before=inspect(mesh)
    comps=[c for a in actors for c in a.get_components_by_class(unreal.StaticMeshComponent) if c.static_mesh==mesh]
    assert comps
    references=[(c,c.static_mesh.get_path_name(),list(c.get_editor_property('override_materials'))) for c in comps]
    options=unreal.FbxImportUI()
    options.automated_import_should_detect_type=False
    options.import_mesh=True;options.import_as_skeletal=False
    options.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
    options.original_import_type=unreal.FBXImportType.FBXIT_STATIC_MESH
    options.import_materials=False;options.import_textures=False;options.import_animations=False
    data=options.static_mesh_import_data
    settings=dict(combine_meshes=False,import_uniform_scale=1.0,convert_scene=True,
        convert_scene_unit=False,force_front_x_axis=False,transform_vertex_to_absolute=True,
        bake_pivot_in_vertex=False,auto_generate_collision=False,one_convex_hull_per_ucx=True,
        generate_lightmap_u_vs=True,normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS,
        normal_generation_method=unreal.FBXNormalGenerationMethod.MIKK_T_SPACE)
    for key,val in settings.items():data.set_editor_property(key,val)
    task=unreal.AssetImportTask()
    task.filename=str(SOURCE/'Exports'/(name+'.fbx'))
    task.destination_path=BASE+'/Meshes';task.destination_name=name
    task.replace_existing=True;task.replace_existing_settings=True
    task.automated=True;task.save=False;task.factory=unreal.FbxFactory();task.options=options
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    after=inspect(mesh)
    assert before==after,(name,before,after)
    assert all(c.static_mesh.get_path_name()==p and list(c.get_editor_property('override_materials'))==m for c,p,m in references)
    assert unreal.EditorAssetLibrary.save_loaded_asset(mesh,False)
    report[name]=dict(before=before,after=after,unchanged_actor_references=len(comps))
result=dict(status='passed',scope='Same-source legacy reimport; no changed geometry revision',assets=report,
            fallback_reason='Dedicated MCP import_file deliberately refuses existing assets')
(ROOT/'Saved/HouseB01Integration/reimport.json').write_text(json.dumps(result,indent=2)+'\n')
unreal.log('HOUSE_B01_LEGACY_REIMPORT_PASSED')
