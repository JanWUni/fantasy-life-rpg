import json
AC='editor_toolset.toolsets.actor.ActorTools';AS='editor_toolset.toolsets.asset.AssetTools'
ROOT='E:/Business/fantasy-rpg-refiner/AssetSources/Architecture/EC_HighCultureCity/StreetStudy01/Refiner/WallCatalogue_01/WindowResize_02/'
def tool(g,n,**a):return execute_tool(g+'.'+n,json.dumps(a)).get('returnValue')
def run():
    with open(ROOT+'../Evidence/place_catalogue.json','r') as f:d=json.load(f)
    result=[]
    for e in d['placed']:
        if any(e['label'].startswith('Lab_WC01_'+s+'_Window') for s in 'ABC') and ('WindowFrame_' in e['label'] or 'WindowGlass_' in e['label']):
            p=list(e['location_cm']);assert p[2]==102;p[2]=137
            assert tool(AC,'set_actor_transform',actor=e['actor'],xform=dict(location=dict(zip('xyz',p)),rotation=dict(pitch=0,yaw=0,roll=0),scale=dict(x=1,y=1,z=1)),worldspace=True)
            result.append(dict(label=e['label'],position_cm=p))
    assert len(result)==6
    assert tool(AS,'save_assets',asset_paths=['/Game/Prototype/Maps/Lvl_AssetLab'])
    return dict(status='passed',installed_inserts=result,house_changes=0)
