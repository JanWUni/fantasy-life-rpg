import json
OB='editor_toolset.toolsets.object.ObjectTools';AC='editor_toolset.toolsets.actor.ActorTools';BP='editor_toolset.toolsets.blueprint.BlueprintTools';AS='editor_toolset.toolsets.asset.AssetTools'
def tool(g,n,**a):return execute_tool(g+'.'+n,json.dumps(a)).get('returnValue')
def props(o,**v):
    tool(OB,'list_properties',instance=o);assert tool(OB,'set_properties',instance=o,values=json.dumps(v))
def run():
    p='/Game/Art/Furniture/WallCatalogue01/Blueprints/BP_WC01_WallLamp';bp=dict(refPath=p+'.BP_WC01_WallLamp')
    values=[('intensity',32),('temperature',3000),('attenuationRadius',240)]
    for field,value in values:
        lights=tool(AC,'get_components',actor=tool(BP,'get_default_object',blueprint=bp),component_type=dict(refPath='/Script/Engine.PointLightComponent'));assert len(lights)==1
        props(lights[0],**{field:value})
    tool(BP,'compile_blueprint',blueprint=bp,warnings_as_errors=True)
    result=[]
    with open('E:/Business/fantasy-rpg-refiner/AssetSources/Architecture/EC_HighCultureCity/StreetStudy01/Refiner/WallCatalogue_01/Evidence/place_catalogue.json','r') as f:placed=json.load(f)
    for entry in placed['placed']:
        if entry['kind']=='Lamp':
            for field,value in values:
                c=tool(AC,'get_components',actor=entry['actor'],component_type=dict(refPath='/Script/Engine.PointLightComponent'))[0]
                props(c,**{field:value})
            result.append(entry['label'])
    assert len(result)==3
    assert tool(AS,'save_assets',asset_paths=[p,'/Game/Prototype/Maps/Lvl_AssetLab'])
    return dict(status='passed',labels=result,lumens=32,temperature=3000,radius_cm=240,reason='Visual correction of overly strong day-lit hotspot')
