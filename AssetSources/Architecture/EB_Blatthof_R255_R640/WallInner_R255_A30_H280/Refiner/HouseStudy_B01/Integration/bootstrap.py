"""Create only the new review world and session-local legacy import defaults.

Executed manually through the editor console; supported operations then use MCP.
No project configuration or existing content is saved here.
"""
from pathlib import Path
import json
import unreal

ROOT = Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).resolve()
assert ROOT == Path('E:/Business/fantasy-rpg-refiner')
OUT = ROOT/'Saved/HouseB01Integration'
OUT.mkdir(parents=True, exist_ok=True)
MAP = '/Game/Art/Architecture/ElvenHouseB01/Maps/Lvl_ElvenHouseB01_Review'
exists = unreal.EditorAssetLibrary.does_asset_exist(MAP)
if exists:
    current = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    assert current.get_path_name() == MAP+'.'+MAP.rsplit('/',1)[-1]
defaults = unreal.get_default_object(unreal.FbxStaticMeshImportData)
settings = dict(import_uniform_scale=1.0, convert_scene=True, convert_scene_unit=False,
                force_front_x_axis=False, transform_vertex_to_absolute=True,
                bake_pivot_in_vertex=False, auto_generate_collision=False,
                one_convex_hull_per_ucx=True, generate_lightmap_u_vs=True,
                normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS,
                normal_generation_method=unreal.FBXNormalGenerationMethod.MIKK_T_SPACE)
for key, val in settings.items():
    defaults.set_editor_property(key, val)
previous = unreal.SystemLibrary.get_console_variable_int_value('Interchange.FeatureFlags.Import.FBX')
unreal.SystemLibrary.execute_console_command(None, 'Interchange.FeatureFlags.Import.FBX 0')
if not exists:
    assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).new_level(MAP)
data = {'project':str(ROOT), 'map':MAP, 'prior_interchange_cvar':previous,
        'legacy_session_defaults':{k:str(v) for k,v in settings.items()}}
(OUT/'bootstrap.json').write_text(json.dumps(data,indent=2)+'\n')
unreal.log('HOUSE_B01_BOOTSTRAP_READY')
