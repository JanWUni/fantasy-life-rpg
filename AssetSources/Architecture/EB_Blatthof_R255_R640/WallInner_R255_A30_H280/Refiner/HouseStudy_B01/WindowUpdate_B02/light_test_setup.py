"""Temporary fixed-exposure control for a real clear-window vs opaque-plug sunlight comparison."""
import json
SC='editor_toolset.toolsets.scene.SceneTools'
AC='editor_toolset.toolsets.actor.ActorTools'
OB='editor_toolset.toolsets.object.ObjectTools'


def tool(group,operation,**args):
    r=execute_tool(group+'.'+operation,json.dumps(args))
    return r['returnValue'] if 'returnValue' in r else None


def props(obj,**values):
    tool(OB,'list_properties',instance=obj)
    assert tool(OB,'set_properties',instance=obj,values=json.dumps(values))


def run():
    assert tool(SC,'get_current_level')=='/Game/Prototype/Maps/Lvl_AssetLab'
    assert not tool(SC,'find_actors',name='Temporary_B02',tag='',collision_channels=[])
    plug=tool(SC,'add_to_scene_from_asset',asset_path='/Engine/BasicShapes/Cube',name='Temporary_B02_WindowPlug',
        xform=dict(location=dict(x=-2100,y=-1903,z=212.5),scale=dict(x=1,y=.08,z=1.73)),snap_to_ground=False)
    components=tool(AC,'get_components',actor=plug,component_type={'refPath':'/Script/Engine.StaticMeshComponent'})
    for comp in components:props(comp,bVisible=False,castShadow=True,bodyInstance=dict(collisionEnabled='NoCollision',collisionProfileName='NoCollision'))
    pp=tool(SC,'add_to_scene_from_class',actor_type={'refPath':'/Script/Engine.PostProcessVolume'},name='Temporary_B02_Exposure',xform={},snap_to_ground=False)
    props(pp,bUnbound=True,priority=100,settings=dict(bOverride_AutoExposureMinBrightness=True,
        bOverride_AutoExposureMaxBrightness=True,autoExposureMinBrightness=1,autoExposureMaxBrightness=1,
        bOverride_AutoExposureBias=True,autoExposureBias=0))
    return dict(plug=plug,plug_component=components[0],exposure=pp,fixed_exposure_ev=1,
                floor_sample_cm=[-1975,-2014,31],note='Not saved; remove both test actors after captures')
