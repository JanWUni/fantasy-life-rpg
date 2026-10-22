"""Place both committed Blender assemblies in the isolated review map via MCP."""
import json

AS='editor_toolset.toolsets.asset.AssetTools'
OB='editor_toolset.toolsets.object.ObjectTools'
AC='editor_toolset.toolsets.actor.ActorTools'
SC='editor_toolset.toolsets.scene.SceneTools'
BASE='/Game/Art/Architecture/ElvenHouseB01'
MAP=BASE+'/Maps/Lvl_ElvenHouseB01_Review'
ROOT='E:/Business/fantasy-rpg-refiner/AssetSources/Architecture/EB_Blatthof_R255_R640/WallInner_R255_A30_H280/Refiner/HouseStudy_B01/Integration/'
MAT='/Game/Art/Materials/ElvenHouseB01'


def tool(group,operation,**args):
    result=execute_tool(group+'.'+operation,json.dumps(args))
    return result['returnValue'] if 'returnValue' in result else None


def ref(path):
    return {'refPath':path+'.'+path.rsplit('/',1)[-1]}


def vec(x,y,z):
    return {'x':x,'y':y,'z':z}


def xform(loc=(0,0,0),scale=(1,1,1),yaw=0,pitch=0):
    return dict(location=vec(*loc),rotation=dict(pitch=pitch,yaw=yaw,roll=0),scale=vec(*scale))


def props(obj,**values):
    tool(OB,'list_properties',instance=obj)
    assert tool(OB,'set_properties',instance=obj,values=json.dumps(values))


def components(actor,kind='StaticMeshComponent'):
    return tool(AC,'get_components',actor=actor,component_type={'refPath':'/Script/Engine.'+kind})


def run():
    assert tool(SC,'get_current_level')==MAP
    existing={tool(AC,'get_label',actor=a):a for a in tool(SC,'find_actors',name='',tag='',collision_channels=[])}
    placed={}
    def place(name,asset=None,kind=None,loc=(0,0,0),scale=(1,1,1),yaw=0,pitch=0,folder='Review'):
        transform=xform(loc,scale,yaw,pitch)
        if name in existing:
            actor=existing[name];tool(AC,'set_actor_transform',actor=actor,xform=transform)
        elif asset:
            actor=tool(SC,'add_to_scene_from_asset',asset_path=asset,name=name,xform=transform,snap_to_ground=False)
        else:
            actor=tool(SC,'add_to_scene_from_class',actor_type={'refPath':'/Script/Engine.'+kind},name=name,xform=transform,snap_to_ground=False)
        tool(SC,'set_actor_folder',actor=actor,folder_path=folder)
        placed[name]=actor
        return actor
    def box(name,loc,scale,material,folder='Review'):
        actor=place(name,asset='/Engine/BasicShapes/Cube',loc=loc,scale=scale,folder=folder)
        for comp in components(actor):
            props(comp,overrideMaterials=[ref(MAT+'/M_EH_'+material)])
        return actor
    with open(ROOT+'assembly.json','r',encoding='utf-8') as f:
        assemblies=json.load(f)
    for scene,offset_x,length in [('House_10x12',0,1200),('House_10x16_Variation',1800,1600)]:
        for index,item in enumerate(assemblies[scene]):
            label=scene+'_'+str(index)+'_'+(item['module'] or 'Step')
            if item['module']:
                loc=[item['location_cm'][0]+offset_x,item['location_cm'][1],item['location_cm'][2]+31]
                asset=(BASE+'/Blueprints/BP_EH_ReviewDoor' if item['module']=='SM_EH_DoorLeaf_132_Study'
                       else BASE+'/Meshes/'+item['module'])
                assert all(abs(s-1)<1e-6 for s in item['scale'])
                place(label,asset=asset,loc=loc,yaw=item['yaw_deg'],folder=scene)
            else:
                lower,upper=item['bounds_blender_m']
                number=int(item['label'].rsplit('_',1)[-1].split('.')[0])
                # Review-only steps end flush with the raised 31cm floor, rather than above it.
                height=[11,22,31][number]
                loc=[50*(lower[0]+upper[0])+offset_x,-50*(lower[1]+upper[1]),height/2]
                box(label,loc,[upper[0]-lower[0],upper[1]-lower[1],height/100],'Stone',scene)
        box(scene+'_Foundation',(offset_x+500,-length/2,5.5),(10,length/100,.11),'Stone',scene)
    box('Review_Ground',(1400,-650,-10),(50,35,.2),'ReviewGround')
    sun=place('Review_Sun',kind='DirectionalLight',loc=(0,0,1500),yaw=-55,pitch=-45)
    for comp in components(sun,'DirectionalLightComponent'):
        props(comp,intensity=50000,bAtmosphereSunLight=True,mobility='Movable')
    place('Review_Atmosphere',kind='SkyAtmosphere')
    sky=place('Review_SkyLight',kind='SkyLight',loc=(0,0,1000))
    for comp in components(sky,'SkyLightComponent'):
        props(comp,intensity=1,bRealTimeCapture=True,mobility='Movable')
    exposure=place('Review_Exposure',kind='PostProcessVolume')
    props(exposure,bUnbound=True,settings=dict(bOverride_AutoExposureMinBrightness=True,
          bOverride_AutoExposureMaxBrightness=True,autoExposureMinBrightness=13,
          autoExposureMaxBrightness=13))
    place('Review_PlayerStart',kind='PlayerStart',loc=(500,360,122),yaw=-90)
    worldsettings=existing['WorldSettings']
    props(worldsettings,defaultGameMode={'refPath':'/Game/Prototype/Blueprints/BP_PrototypeGameMode.BP_PrototypeGameMode_C'})
    assert tool(AS,'save_assets',asset_paths=[MAP])
    return dict(map=MAP,actors=placed,module_placement='Blender transforms mapped to UE cm; all module scales 1',
                steps='review-only Engine cube proxies, 11/22/31cm tops; source scene unchanged')
