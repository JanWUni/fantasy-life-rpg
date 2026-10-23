"""Set only session import defaults for the verified legacy path."""
from pathlib import Path
import json,unreal
ROOT=Path(__file__).resolve().parent
assert Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).resolve()==Path('E:/Business/fantasy-rpg-refiner')
assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name().startswith('/Game/Prototype/Maps/Lvl_AssetLab.')
settings=dict(import_uniform_scale=1.,convert_scene=True,convert_scene_unit=False,force_front_x_axis=False,
    transform_vertex_to_absolute=True,bake_pivot_in_vertex=False,auto_generate_collision=False,one_convex_hull_per_ucx=True,
    generate_lightmap_u_vs=True,normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS,
    normal_generation_method=unreal.FBXNormalGenerationMethod.MIKK_T_SPACE)
defaults=unreal.get_default_object(unreal.FbxStaticMeshImportData)
for key,value in settings.items():defaults.set_editor_property(key,value)
prior=unreal.SystemLibrary.get_console_variable_int_value('Interchange.FeatureFlags.Import.FBX')
unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
(ROOT/'Evidence/import_session.json').write_text(json.dumps(dict(prior_interchange=prior),indent=2)+'\n')
unreal.log('B03_IMPORT_PREPARED')
