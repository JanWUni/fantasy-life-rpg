"""Compile populated study Blueprints, add only two assembly actors, save explicit assets."""
import json
AS='editor_toolset.toolsets.asset.AssetTools';BP='editor_toolset.toolsets.blueprint.BlueprintTools'
AC='editor_toolset.toolsets.actor.ActorTools';SC='editor_toolset.toolsets.scene.SceneTools'
ROOT='E:/Business/fantasy-rpg-refiner/AssetSources/Architecture/EC_HighCultureCity/StreetStudy01/Refiner/UnrealReview_01/'
def tool(g,n,**a):return execute_tool(g+'.'+n,json.dumps(a)).get('returnValue')
def ref(p):return dict(refPath=p+'.'+p.rsplit('/',1)[-1])
def run():
    with open(ROOT+'plan.json','r') as f:plan=json.load(f)
    assert tool(SC,'get_current_level')==plan['map'];saved=[];actors={}
    for s in plan['studies']:
        path=s['dest']+'/'+s['blueprint'];tool(BP,'compile_blueprint',blueprint=ref(path),warnings_as_errors=True)
        label='Lab_Study'+s['tag']+'_ClearGlass'
        existing=tool(SC,'find_actors',name=label,tag='',collision_channels=[]);assert not existing,'Do not duplicate an existing study'
        actor=tool(SC,'add_to_scene_from_asset',asset_path=path,name=label,
            xform=dict(location=dict(zip(['x','y','z'],s['offset'])),rotation=dict(pitch=0,yaw=0,roll=0),scale=dict(x=1,y=1,z=1)),snap_to_ground=False)
        tool(SC,'set_actor_folder',actor=actor,folder_path='Lab/Architecture/Study'+s['tag']+'_ClearGlass')
        actors[s['tag']]=actor;saved.append(path)
        saved.extend(s['dest']+'/Meshes/'+e['asset_name'] for e in s['mesh_manifest']['exports'])
    with open(ROOT+'Evidence/import_modules.json','r') as f:imported=json.load(f)
    saved.extend(p for p in imported['saved'] if '/Materials/' in p)
    saved.append(plan['map']);assert tool(AS,'save_assets',asset_paths=saved)
    return dict(status='passed',map=plan['map'],actors=actors,saved=saved)
