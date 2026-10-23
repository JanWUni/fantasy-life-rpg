"""Explicit legacy reimport is not exposed by MCP import_file for existing assets."""
from pathlib import Path
import json,unreal
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[6]
assert Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).resolve()==REPO
assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name().startswith('/Game/Prototype/Maps/Lvl_AssetLab.')
assert unreal.SystemLibrary.get_console_variable_int_value('Interchange.FeatureFlags.Import.FBX')==0
d=json.loads((ROOT/'manifest.json').read_text());report={};sme=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
for name,i in d['assets'].items():
    path='/Game/Art/Architecture/WallCatalogue01/Meshes/'+name;mesh=unreal.load_asset(path);assert mesh
    before=dict(slots=[str(s.material_slot_name) for s in mesh.static_materials],materials=[s.material_interface.get_path_name() for s in mesh.static_materials],hulls=sme.get_convex_collision_count(mesh))
    options=unreal.FbxImportUI();options.automated_import_should_detect_type=False;options.import_mesh=True;options.import_as_skeletal=False
    options.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH;options.original_import_type=unreal.FBXImportType.FBXIT_STATIC_MESH
    options.import_materials=False;options.import_textures=False;options.import_animations=False
    for k,v in dict(combine_meshes=False,import_uniform_scale=1,convert_scene=True,convert_scene_unit=False,force_front_x_axis=False,
        transform_vertex_to_absolute=True,bake_pivot_in_vertex=False,auto_generate_collision=False,one_convex_hull_per_ucx=True,generate_lightmap_u_vs=True,
        normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS,normal_generation_method=unreal.FBXNormalGenerationMethod.MIKK_T_SPACE).items():options.static_mesh_import_data.set_editor_property(k,v)
    task=unreal.AssetImportTask();task.filename=str(ROOT/'Exports'/(name+'.fbx'));task.destination_path=path.rsplit('/',1)[0];task.destination_name=name
    task.replace_existing=True;task.replace_existing_settings=True;task.automated=True;task.save=False;task.factory=unreal.FbxFactory();task.options=options
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    after=dict(slots=[str(s.material_slot_name) for s in mesh.static_materials],materials=[s.material_interface.get_path_name() for s in mesh.static_materials],hulls=sme.get_convex_collision_count(mesh))
    assert before==after and after['hulls']==i['ucx_hulls'],(name,before,after)
    assert mesh.get_num_triangles(0)==i['triangles']
    assert mesh.get_editor_property('asset_import_data').get_class().get_name()=='FbxStaticMeshImportData'
    assert unreal.EditorAssetLibrary.save_loaded_asset(mesh,False)
    report[name]=dict(before=before,after=after,triangles=mesh.get_num_triangles(0),importer='FbxStaticMeshImportData')
(ROOT/'Evidence/reimport_windows.json').write_text(json.dumps(dict(status='passed',assets=report),indent=2)+'\n')
unreal.log('WC02_REIMPORT_PASSED')
