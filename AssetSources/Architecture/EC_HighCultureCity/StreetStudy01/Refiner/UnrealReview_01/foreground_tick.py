"""Session-only background ticking for MCP operations and later PIE checks."""
from pathlib import Path
import json,unreal
ROOT=Path(__file__).resolve().parent
assert Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).resolve()==ROOT.parents[5]
p=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'))
data=dict(prior_background_throttle=p.get_editor_property('bThrottleCPUWhenNotForeground'),
    prior_slate_throttle=unreal.SystemLibrary.get_console_variable_int_value('Slate.bAllowThrottling'),save_config_called=False)
p.set_editor_property('bThrottleCPUWhenNotForeground',False)
unreal.SystemLibrary.execute_console_command(None,'Slate.bAllowThrottling 0')
(ROOT/'Evidence/background_tick_session.json').write_text(json.dumps(data,indent=2)+'\n')
unreal.log('STUDY_AB_BACKGROUND_TICK_ENABLED')
