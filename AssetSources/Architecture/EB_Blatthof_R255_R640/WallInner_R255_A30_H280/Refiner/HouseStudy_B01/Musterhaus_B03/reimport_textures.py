"""Explicit reimport of only the own generated B03 base-color revisions."""
from pathlib import Path
import json,unreal
ROOT=Path(__file__).resolve().parent
assert Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).resolve()==Path('E:/Business/fantasy-rpg-refiner')
result={}
for family in ['Plaster','Timber','Stone','Jade','Floor']:
    name='T_EH03_'+family+'_BaseColor';path='/Game/Art/Textures/ElvenHouseB03/'+name
    task=unreal.AssetImportTask();task.filename=str(ROOT/'Textures'/(name+'.png'));task.destination_path='/Game/Art/Textures/ElvenHouseB03'
    task.destination_name=name;task.replace_existing=True;task.replace_existing_settings=False;task.automated=True;task.save=True;task.factory=unreal.TextureFactory()
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task]);texture=unreal.load_asset(path)
    assert texture.get_editor_property('srgb')
    result[name]=dict(srgb=True,source=str(ROOT/'Textures'/(name+'.png')))
(ROOT/'Evidence/reimport_textures.json').write_text(json.dumps(dict(status='passed',textures=result),indent=2)+'\n')
unreal.log('B03_TEXTURES_REIMPORTED')
