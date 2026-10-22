"""Review-only fill lights and eye adaptation; no production fixture/design decision."""
import json
SC='editor_toolset.toolsets.scene.SceneTools'
AC='editor_toolset.toolsets.actor.ActorTools'
OB='editor_toolset.toolsets.object.ObjectTools'
AS='editor_toolset.toolsets.asset.AssetTools'
MAP='/Game/Art/Architecture/ElvenHouseB01/Maps/Lvl_ElvenHouseB01_Review'


def tool(group,operation,**args):
    result=execute_tool(group+'.'+operation,json.dumps(args))
    return result['returnValue'] if 'returnValue' in result else None


def props(obj,**values):
    tool(OB,'list_properties',instance=obj)
    assert tool(OB,'set_properties',instance=obj,values=json.dumps(values))


def run():
    assert tool(SC,'get_current_level')==MAP
    exposure=tool(SC,'find_actors',name='Review_Exposure',tag='',collision_channels=[])[0]
    props(exposure,settings=dict(bOverride_AutoExposureMinBrightness=True,
        bOverride_AutoExposureMaxBrightness=True,autoExposureMinBrightness=6,autoExposureMaxBrightness=13,
        bOverride_AutoExposureBias=True,autoExposureBias=-1.25))
    lights=[]
    for x,length in ((500,1200),(2300,1600)):
        for y in (-length*.3,-length*.7):
            label='Review_InteriorFill_'+str(x)+'_'+str(int(-y))
            found=tool(SC,'find_actors',name=label,tag='',collision_channels=[])
            actor=(found[0] if found else tool(SC,'add_to_scene_from_class',
                actor_type={'refPath':'/Script/Engine.PointLight'},name=label,
                xform={'location':dict(x=x,y=y,z=280)},snap_to_ground=False))
            tool(SC,'set_actor_folder',actor=actor,folder_path='Review/TemporaryInteriorLighting')
            for component in tool(AC,'get_components',actor=actor,
                                  component_type={'refPath':'/Script/Engine.PointLightComponent'}):
                props(component,intensity=3500,intensityUnits='Lumens',attenuationRadius=1100,mobility='Movable')
            lights.append(actor)
    assert tool(AS,'save_assets',asset_paths=[MAP])
    return dict(review_only_lights=lights,eye_adaptation_ev=[6,13],exposure_bias=-1.25,production_lighting=False)
