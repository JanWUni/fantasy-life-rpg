"""Restore import/tick defaults while preserving the live editor and all dirty packages.

Autosave remains paused in memory because of the observed engine-helper crash.
No SaveConfig, package discard, editor shutdown or package reload is performed.
"""
from pathlib import Path
import json,unreal
ROOT=Path(__file__).resolve().parent
assert Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).resolve()==ROOT.parents[5]
original=json.loads((ROOT/'Evidence/bootstrap_initial.json').read_text())
defaults=unreal.get_default_object(unreal.FbxStaticMeshImportData)
for key,v in original['prior_fbx_defaults'].items():
    if isinstance(v,dict):v=getattr(getattr(unreal,v['enum_class']),v['enum_member'])
    defaults.set_editor_property(key,v);assert defaults.get_editor_property(key)==v
unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX '+str(original['prior_importer_cvar']))
perf=json.loads((ROOT/'Evidence/background_tick_session.json').read_text())
p=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'))
p.set_editor_property('bThrottleCPUWhenNotForeground',perf['prior_background_throttle'])
unreal.SystemLibrary.execute_console_command(None,'Slate.bAllowThrottling '+str(perf['prior_slate_throttle']))
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorLoadingSavingSettings'))
data=dict(status='passed',editor_left_open=True,packages_discarded=False,save_config_called=False,
    importer_cvar=unreal.SystemLibrary.get_console_variable_int_value('Interchange.FeatureFlags.Import.FBX'),fbx_defaults_restored=True,
    background_throttle=p.get_editor_property('bThrottleCPUWhenNotForeground'),slate_throttle=unreal.SystemLibrary.get_console_variable_int_value('Slate.bAllowThrottling'),
    autosave_enabled=settings.get_editor_property('bAutoSaveEnable'),autosave_session_paused_due_to_observed_crash=True,
    dirty_packages_preserved=[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()],
    clean_restart_not_performed='Automatic approval rejected possible loss of unsaved packages; no workaround used')
(ROOT/'Evidence/session_preserved.json').write_text(json.dumps(data,indent=2)+'\n')
unreal.log('STUDY_AB_IMPORT_DEFAULTS_RESTORED_LIVE_EDITOR_PRESERVED')
