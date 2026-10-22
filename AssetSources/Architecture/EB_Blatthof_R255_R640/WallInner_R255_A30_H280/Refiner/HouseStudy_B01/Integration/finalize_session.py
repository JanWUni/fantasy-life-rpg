"""Restore the temporary importer switch; audit only, no global config saving."""
from pathlib import Path
import json
import unreal
ROOT=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).resolve()
assert ROOT==Path('E:/Business/fantasy-rpg-refiner')
OUT=ROOT/'Saved/HouseB01Integration'
prior=json.loads((OUT/'bootstrap.json').read_text())['prior_interchange_cvar']
unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX '+str(prior))
actual=unreal.SystemLibrary.get_console_variable_int_value('Interchange.FeatureFlags.Import.FBX')
assert actual==prior
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name().startswith('/Game/Art/Architecture/ElvenHouseB01/Maps/Lvl_ElvenHouseB01_Review.')
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_set_game_view(True)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_set_viewport_realtime(False)
data=dict(status='passed',interchange_cvar_restored=actual,project=str(ROOT),
          editor_world=world.get_path_name(),realtime_viewport=False,
          dirty_content=[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()],
          dirty_maps=[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()])
(OUT/'session_final.json').write_text(json.dumps(data,indent=2)+'\n')
unreal.log('HOUSE_B01_SESSION_FINALIZED')
