import json
SC='editor_toolset.toolsets.scene.SceneTools';AC='editor_toolset.toolsets.actor.ActorTools';OB='editor_toolset.toolsets.object.ObjectTools'
def tool(g,n,**a):return execute_tool(g+'.'+n,json.dumps(a)).get('returnValue')
def run():
    a=tool(SC,'add_to_scene_from_asset',asset_path='/Game/Art/Furniture/WallCatalogue01/Blueprints/BP_WC01_WallLamp',name='WC01_Temporary_Lamp_Default_Check',
        xform=dict(location=dict(x=-5000,y=3000,z=200),rotation=dict(pitch=0,yaw=0,roll=0),scale=dict(x=1,y=1,z=1)),snap_to_ground=False)
    try:
        c=tool(AC,'get_components',actor=a,component_type=dict(refPath='/Script/Engine.PointLightComponent'))[0]
        d=tool(OB,'get_properties',instance=c,properties=['intensity','temperature','attenuationRadius','intensityUnits','bUseTemperature','bUseInverseSquaredFalloff','castShadows'])
        if isinstance(d,str):d=json.loads(d)
        assert d['intensity']==32 and d['temperature']==3000 and d['attenuationRadius']==240,d
        return dict(status='passed',fresh_blueprint_instance=d,temporary_actor_removed=True)
    finally:
        assert tool(SC,'remove_from_scene',actor=a)
        assert tool('editor_toolset.toolsets.asset.AssetTools','save_assets',asset_paths=['/Game/Prototype/Maps/Lvl_AssetLab'])
