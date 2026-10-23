"""Instantiate each reusable lamp, inspect real instance values and remove the test instance."""
import json
AS='editor_toolset.toolsets.asset.AssetTools';SC='editor_toolset.toolsets.scene.SceneTools';AC='editor_toolset.toolsets.actor.ActorTools';OB='editor_toolset.toolsets.object.ObjectTools'
def tool(g,op,**kw):return execute_tool(g+'.'+op,json.dumps(kw)).get('returnValue')
def run():
    result={}
    for kind,power in [('Lantern',24),('Pendant',90),('WallLantern',40)]:
        path='/Game/Art/Furniture/ElvenHouseB03/Blueprints/BP_EH03_'+kind
        actor=tool(SC,'add_to_scene_from_asset',asset_path=path,name='Temporary_B03_Prefab_'+kind,
            xform=dict(location=dict(x=-5600,y=-3600,z=0),scale=dict(x=1,y=1,z=1)),snap_to_ground=False)
        try:
            light=tool(AC,'get_components',actor=actor,component_type=dict(refPath='/Script/Engine.PointLightComponent'))[0]
            actual=json.loads(tool(OB,'get_properties',instance=light,properties=['intensity','temperature','intensityUnits','bUseTemperature']))
            assert actual['intensity']==power and actual['temperature']==3000,actual
            result[kind]=actual
        finally:tool(SC,'remove_from_scene',actor=actor)
    assert tool(AS,'save_assets',asset_paths=['/Game/Prototype/Maps/Lvl_AssetLab'])
    return dict(status='passed',reusable_lamp_instances=result,temporary_actors_removed=True)
