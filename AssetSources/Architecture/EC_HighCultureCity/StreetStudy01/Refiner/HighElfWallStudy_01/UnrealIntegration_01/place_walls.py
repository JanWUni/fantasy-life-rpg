import json
AS='editor_toolset.toolsets.asset.AssetTools';SC='editor_toolset.toolsets.scene.SceneTools';AC='editor_toolset.toolsets.actor.ActorTools';OB='editor_toolset.toolsets.object.ObjectTools'
ROOT='E:/Business/fantasy-rpg-refiner/AssetSources/Architecture/EC_HighCultureCity/StreetStudy01/Refiner/HighElfWallStudy_01/UnrealIntegration_01/'
ARCH='/Game/Art/Architecture/HighElfWallStudy01';PREFIX='Lab_HE01_'
def tool(g,n,**a):return execute_tool(g+'.'+n,json.dumps(a)).get('returnValue')
def props(o,**v):
    tool(OB,'list_properties',instance=o);assert tool(OB,'set_properties',instance=o,values=json.dumps(v))
def vec(x,y,z):return dict(x=x,y=y,z=z)
def xf(p,yaw=0):return dict(location=vec(*p),rotation=dict(pitch=0,yaw=yaw,roll=0),scale=vec(1,1,1))
def run():
    MAP='/Game/Prototype/Maps/Lvl_AssetLab';assert tool(SC,'get_current_level')==MAP and not tool('EditorToolset.EditorAppToolset','IsPIERunning')
    assert not any(tool(AC,'get_label',actor=a).startswith(PREFIX) for a in tool(SC,'find_actors',name='',tag='',collision_channels=[]))
    placed=[]
    for label,v,p in [('A_Schlicht','A',[1600,3100,2]),('B_Prachtvoll','B',[2200,3100,2]),('Snap_A','A',[1600,2350,2]),('Snap_B','B',[1900,2350,2])]:
        path=ARCH+'/Blueprints/BP_HE01_WindowWall_'+v
        a=tool(SC,'add_to_scene_from_asset',asset_path=path,name=PREFIX+label,xform=xf(p),snap_to_ground=False)
        tool(SC,'set_actor_folder',actor=a,folder_path='Lab/Architecture/HighElfWallStudy01/Walls')
        placed.append(dict(label=PREFIX+label,variant=v,location_cm=p,actor=a))
    for label,message,p,size in [('Label_A','A / SCHLICHT',[1750,3220,25],22),('Label_B','B / PRACHTVOLL',[2350,3220,25],22),('Label_Join','ANSCHLUSSPROBE / 2 x 300 cm',[1900,2450,25],20)]:
        a=tool(SC,'add_to_scene_from_class',actor_type=dict(refPath='/Script/Engine.TextRenderActor'),name=PREFIX+label,xform=xf(p,90),snap_to_ground=False)
        tool(SC,'set_actor_folder',actor=a,folder_path='Lab/Architecture/HighElfWallStudy01/Labels')
        c=tool(AC,'get_components',actor=a,component_type=dict(refPath='/Script/Engine.TextRenderComponent'))[0]
        props(c,text=message,worldSize=size,horizontalAlignment='EHTA_Center',textRenderColor=dict(r=240,g=235,b=215,a=255))
    assert tool(AS,'save_assets',asset_paths=[MAP])
    return dict(status='passed',map=MAP,placed=placed,new_actors=7)
