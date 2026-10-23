"""Session-only autosave guard while editing templates; never SaveConfig."""
from pathlib import Path
import json,unreal
ROOT=Path(__file__).resolve().parent
assert Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).resolve()==ROOT.parents[5]
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorLoadingSavingSettings'))
prior=settings.get_editor_property('bAutoSaveEnable')
settings.set_editor_property('bAutoSaveEnable',False)
(ROOT/'Evidence/autosave_session.json').write_text(json.dumps(dict(prior=prior,current=False,save_config_called=False,
    reason='Engine MeshDescription access violation during automatic saving of Engine helper meshes; restore before final clean restart'),indent=2)+'\n')
exec(compile((ROOT/'bootstrap.py').read_text(),str(ROOT/'bootstrap.py'),'exec'))
