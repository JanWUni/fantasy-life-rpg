"""Leave the selected Refiner Lab saved, with no test objects or temporary importer settings."""
from pathlib import Path
import json,unreal
ROOT=Path(__file__).resolve().parent
assert Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).resolve()==Path('E:/Business/fantasy-rpg-refiner')
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name().startswith('/Game/Prototype/Maps/Lvl_AssetLab.')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
assert not any(a.get_actor_label().startswith('Temporary_B02') for a in actors)
prior=json.loads((ROOT/'Evidence/import_session.json').read_text())['prior_interchange']
unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX '+str(prior))
assert unreal.SystemLibrary.get_console_variable_int_value('Interchange.FeatureFlags.Import.FBX')==prior
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_set_game_view(True)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_set_viewport_realtime(False)
data=dict(status='passed',map=world.get_path_name(),temporary_test_actors=0,interchange_cvar_restored=prior,
    dirty_game_content=[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages() if p.get_path_name().startswith('/Game/')],
    dirty_maps=[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()])
(ROOT/'Evidence/final_state.json').write_text(json.dumps(data,indent=2)+'\n')
unreal.log('HOUSE_B02_LAB_FINALIZED')
