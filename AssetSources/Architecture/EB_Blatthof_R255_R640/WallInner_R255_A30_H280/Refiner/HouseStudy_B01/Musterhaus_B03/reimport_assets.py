"""Native fallback for existing-asset legacy import, unsupported by current MCP import_file."""
from pathlib import Path
import json,unreal
ROOT=Path(__file__).resolve().parent
assert Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).resolve()==Path('E:/Business/fantasy-rpg-refiner')
assert unreal.SystemLibrary.get_console_variable_int_value('Interchange.FeatureFlags.Import.FBX')==0
manifest=json.loads((ROOT/'manifest.json').read_text());smes=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
def inspect(mesh):return dict(triangles=mesh.get_num_triangles(0),hulls=smes.get_convex_collision_count(mesh),
    slots=[str(s.material_slot_name) for s in mesh.static_materials],materials=[s.material_interface.get_path_name() for s in mesh.static_materials],
    importer=mesh.get_editor_property('asset_import_data').get_class().get_name())
report={}
for name,info in manifest['assets'].items():
    folder=('/Game/Art/Architecture/ElvenHouseB03' if any(s in name for s in ['Interior','Ceiling']) else '/Game/Art/Furniture/ElvenHouseB03')+'/Meshes'
    mesh=unreal.load_asset(folder+'/'+name);before=inspect(mesh)
    options=unreal.FbxImportUI();options.automated_import_should_detect_type=False;options.import_mesh=True
    options.import_as_skeletal=False;options.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
    options.original_import_type=unreal.FBXImportType.FBXIT_STATIC_MESH
    options.import_materials=False;options.import_textures=False;options.import_animations=False
    data=options.static_mesh_import_data
    for key,value in dict(combine_meshes=False,import_uniform_scale=1,convert_scene=True,convert_scene_unit=False,
        force_front_x_axis=False,transform_vertex_to_absolute=True,bake_pivot_in_vertex=False,
        auto_generate_collision=False,one_convex_hull_per_ucx=True,generate_lightmap_u_vs=True,
        normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS,
        normal_generation_method=unreal.FBXNormalGenerationMethod.MIKK_T_SPACE).items():data.set_editor_property(key,value)
    task=unreal.AssetImportTask();task.filename=str(ROOT/'Exports'/(name+'.fbx'))
    task.destination_path=folder;task.destination_name=name;task.replace_existing=True;task.replace_existing_settings=True
    task.automated=True;task.save=False;task.factory=unreal.FbxFactory();task.options=options
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    after=inspect(mesh);assert before==after,(name,before,after)
    assert after['triangles']==info['triangles'] and after['hulls']==info['ucx_hulls']
    assert unreal.EditorAssetLibrary.save_loaded_asset(mesh,False)
    report[name]=dict(before=before,after=after)
(ROOT/'Evidence/reimport_assets.json').write_text(json.dumps(dict(status='passed',assets=report),indent=2)+'\n')
unreal.log('HOUSE_B03_REIMPORT_PASSED')
