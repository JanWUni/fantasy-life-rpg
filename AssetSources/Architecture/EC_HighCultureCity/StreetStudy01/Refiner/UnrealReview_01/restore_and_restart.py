"""Restore session settings, then exit cleanly after explicit saves for a fresh reopen."""
from pathlib import Path
import json,unreal
ROOT=Path(__file__).resolve().parent
assert Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).resolve()==ROOT.parents[5]
dirty_content=[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()]
dirty_maps=[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()]
assert not dirty_maps,dirty_maps
assert not any(p.startswith('/Game/') for p in dirty_content),dirty_content
original=json.loads((ROOT/'Evidence/bootstrap_initial.json').read_text())
defaults=unreal.get_default_object(unreal.FbxStaticMeshImportData)
for key,v in original['prior_fbx_defaults'].items():
    if isinstance(v,dict):v=getattr(getattr(unreal,v['enum_class']),v['enum_member'])
    defaults.set_editor_property(key,v);assert defaults.get_editor_property(key)==v
unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX '+str(original['prior_importer_cvar']))
auto=json.loads((ROOT/'Evidence/autosave_session.json').read_text())
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorLoadingSavingSettings'))
settings.set_editor_property('bAutoSaveEnable',auto['prior'])
perf=json.loads((ROOT/'Evidence/background_tick_session.json').read_text())
p=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'))
p.set_editor_property('bThrottleCPUWhenNotForeground',perf['prior_background_throttle'])
unreal.SystemLibrary.execute_console_command(None,'Slate.bAllowThrottling '+str(perf['prior_slate_throttle']))
data=dict(status='passed',importer_cvar=unreal.SystemLibrary.get_console_variable_int_value('Interchange.FeatureFlags.Import.FBX'),
    autosave_enabled=settings.get_editor_property('bAutoSaveEnable'),background_throttle=p.get_editor_property('bThrottleCPUWhenNotForeground'),
    slate_throttle=unreal.SystemLibrary.get_console_variable_int_value('Slate.bAllowThrottling'),
    fbx_defaults_restored=True,save_config_called=False,unsaved_project_packages=[],dirty_nonproject_packages=dirty_content,
    clean_restart_reason='Reopen saved assemblies and discard only generated unsaved Engine helper state from editor introspection')
(ROOT/'Evidence/session_restored.json').write_text(json.dumps(data,indent=2)+'\n')
unreal.log('STUDY_AB_SESSION_RESTORED_CLEAN_RESTART')
unreal.SystemLibrary.quit_editor()
