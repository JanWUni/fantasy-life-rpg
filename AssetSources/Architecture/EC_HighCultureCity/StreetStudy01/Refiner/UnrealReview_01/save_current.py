"""Save only the two study assemblies, private materials/meshes and the authorized lab."""
import json
ROOT='E:/Business/fantasy-rpg-refiner/AssetSources/Architecture/EC_HighCultureCity/StreetStudy01/Refiner/UnrealReview_01/'
def tool(g,n,**a):return execute_tool(g+'.'+n,json.dumps(a)).get('returnValue')
def run():
    with open(ROOT+'plan.json','r') as f:plan=json.load(f)
    with open(ROOT+'Evidence/place_in_lab.json','r') as f:placed=json.load(f)
    for s in plan['studies']:
        p=s['dest']+'/'+s['blueprint'];tool('editor_toolset.toolsets.blueprint.BlueprintTools','compile_blueprint',blueprint=dict(refPath=p+'.'+s['blueprint']),warnings_as_errors=True)
    assert tool('editor_toolset.toolsets.asset.AssetTools','save_assets',asset_paths=placed['saved'])
    return dict(status='passed',saved=placed['saved'])
