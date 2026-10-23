"""Restore import defaults without closing the editor or discarding dirty work."""
from pathlib import Path
import json,unreal
ROOT=Path(__file__).resolve().parent
assert Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).resolve()==ROOT.parents[6]
old=json.loads((ROOT/'Evidence/bootstrap.json').read_text());d=unreal.get_default_object(unreal.FbxStaticMeshImportData)
for key,v in old['prior_fbx_defaults'].items():
    if isinstance(v,dict):v=getattr(getattr(unreal,v['enum_class']),v['enum_member'])
    d.set_editor_property(key,v);assert d.get_editor_property(key)==v
unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX '+str(old['prior_importer_cvar']))
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorLoadingSavingSettings'))
(ROOT/'Evidence/session_restored.json').write_text(json.dumps(dict(status='passed',importer_cvar=unreal.SystemLibrary.get_console_variable_int_value('Interchange.FeatureFlags.Import.FBX'),
    fbx_defaults_restored=True,save_config_called=False,editor_closed=False,dirty_packages_discarded=False,autosave_enabled=settings.get_editor_property('bAutoSaveEnable')),indent=2)+'\n')
unreal.log('WC01_IMPORT_DEFAULTS_RESTORED')
