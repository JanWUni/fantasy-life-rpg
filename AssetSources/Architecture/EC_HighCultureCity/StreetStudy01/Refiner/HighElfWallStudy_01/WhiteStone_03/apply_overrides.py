import json
def tool(g,n,**a):return execute_tool(g+'.'+n,json.dumps(a)).get('returnValue')
def ref(p):return dict(refPath=p+'.'+p.rsplit('/',1)[-1])
def run():
    root='E:/Business/fantasy-rpg-refiner/AssetSources/Architecture/EC_HighCultureCity/StreetStudy01/Refiner/HighElfWallStudy_01/WhiteStone_03/'
    with open(root+'Evidence/white_unreal.json','r') as f:d=json.load(f)
    ac='editor_toolset.toolsets.actor.ActorTools';ob='editor_toolset.toolsets.object.ObjectTools';proof={}
    for part in ['WallCore','StoneCarving','GoldInlay','BlueInlay','WindowFrame','ClearGlass']:
        cs=tool(ac,'get_components',actor=dict(refPath=d['updated_actor']),component_type=dict(refPath='/Script/Engine.StaticMeshComponent'))
        c=next(c for c in cs if c['refPath'].endswith('.'+part))
        tool(ob,'list_properties',instance=c);v=json.loads(tool(ob,'get_properties',instance=c,properties=['staticMesh']))
        slots=tool('editor_toolset.toolsets.static_mesh.StaticMeshTools','get_material_slots',mesh=v['staticMesh']);overrides=[]
        for slot in slots:
            family=slot.removeprefix('HEWS01_');version='03' if family in ['Ivory','CarvedStone','RecessStone'] else '02';overrides.append(ref('/Game/Art/Materials/HighElfWallStudy'+version+'/M_HE'+version+'_'+family))
        assert tool(ob,'set_properties',instance=c,values=json.dumps(dict(overrideMaterials=overrides)))
        proof[part]=overrides
    assert tool('editor_toolset.toolsets.asset.AssetTools','save_assets',asset_paths=['/Game/Prototype/Maps/Lvl_AssetLab'])
    return dict(status='passed',components=proof)
