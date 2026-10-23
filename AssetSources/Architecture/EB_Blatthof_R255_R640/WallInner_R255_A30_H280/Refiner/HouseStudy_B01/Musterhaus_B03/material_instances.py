"""Native fallback: material-instance creation/parameter setting is absent from current MCP toolset."""
from pathlib import Path
import json,unreal
ROOT=Path(__file__).resolve().parent
assert Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).resolve()==Path('E:/Business/fantasy-rpg-refiner')
base='/Game/Art/Materials/ElvenHouseB03'
variants={'Plaster_Warm':('Plaster',(1.04,.99,.91)), 'Plaster_Cool':('Plaster',(.94,.98,1.04)),
          'Timber_Dark':('Timber',(.76,.82,.86)), 'Timber_Honey':('Timber',(1.13,1.06,.94))}
result={}
for suffix,(family,color) in variants.items():
    name='MI_EH03_'+suffix;path=base+'/'+name
    instance=unreal.load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,base,unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
    unreal.MaterialEditingLibrary.set_material_instance_parent(instance,unreal.load_asset(base+'/M_EH03_'+family))
    unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(instance,'Tint',unreal.LinearColor(*color,1))
    actual=unreal.MaterialEditingLibrary.get_material_instance_vector_parameter_value(instance,'Tint')
    assert max(abs(a-b) for a,b in zip([actual.r,actual.g,actual.b],color))<1e-5,(suffix,actual,color)
    unreal.EditorAssetLibrary.save_loaded_asset(instance)
    result[suffix]=dict(path=path,tint=color)
(ROOT/'Evidence/material_instances.json').write_text(json.dumps(result,indent=2)+'\n')
unreal.log('B03_MATERIAL_INSTANCES_CREATED')
