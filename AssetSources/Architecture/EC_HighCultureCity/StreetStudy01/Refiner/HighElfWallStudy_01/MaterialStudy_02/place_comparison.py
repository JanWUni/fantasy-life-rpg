import json
AS='editor_toolset.toolsets.asset.AssetTools';SC='editor_toolset.toolsets.scene.SceneTools';AC='editor_toolset.toolsets.actor.ActorTools';OB='editor_toolset.toolsets.object.ObjectTools'
ROOT='E:/Business/fantasy-rpg-refiner/AssetSources/Architecture/EC_HighCultureCity/StreetStudy01/Refiner/HighElfWallStudy_01/MaterialStudy_02/'
def tool(g,n,**a):return execute_tool(g+'.'+n,json.dumps(a)).get('returnValue')
def props(o,**v):
    tool(OB,'list_properties',instance=o);assert tool(OB,'set_properties',instance=o,values=json.dumps(v))
def xf(x,y,z,yaw=0):return dict(location=dict(x=x,y=y,z=z),rotation=dict(pitch=0,yaw=yaw,roll=0),scale=dict(x=1,y=1,z=1))
def run():
    assert tool(SC,'get_current_level')=='/Game/Prototype/Maps/Lvl_AssetLab' and not tool('EditorToolset.EditorAppToolset','IsPIERunning')
    with open(ROOT+'Evidence/baseline.json','r') as f:base=json.load(f)
    assert not any(a['label'].startswith('Lab_HE02_') for a in base['actors'])
    placed=[]
    for label,path,x in [('Vorher','/Game/Art/Architecture/HighElfWallStudy01/Blueprints/BP_HE01_WindowWall_A',1600),('Materialstudie','/Game/Art/Architecture/HighElfWallStudy02/Blueprints/BP_HE02_WindowWall_A',2200)]:
        a=tool(SC,'add_to_scene_from_asset',asset_path=path,name='Lab_HE02_'+label,xform=xf(x,1500,2),snap_to_ground=False)
        tool(SC,'set_actor_folder',actor=a,folder_path='Lab/Architecture/HighElfMaterialStudy02')
        placed.append(dict(label='Lab_HE02_'+label,actor=a,location_cm=[x,1500,2],path=path))
        a=tool(SC,'add_to_scene_from_class',actor_type=dict(refPath='/Script/Engine.TextRenderActor'),name='Lab_HE02_Label_'+label,xform=xf(x+150,1620,25,90),snap_to_ground=False)
        tool(SC,'set_actor_folder',actor=a,folder_path='Lab/Architecture/HighElfMaterialStudy02/Labels')
        c=tool(AC,'get_components',actor=a,component_type=dict(refPath='/Script/Engine.TextRenderComponent'))[0]
        props(c,text='VORHER' if label=='Vorher' else 'STEIN / GOLD / GLAS',worldSize=22,horizontalAlignment='EHTA_Center',textRenderColor=dict(r=240,g=235,b=215,a=255))
    assert tool(AS,'save_assets',asset_paths=['/Game/Prototype/Maps/Lvl_AssetLab'])
    return dict(status='passed',placed=placed,new_actors=4)
