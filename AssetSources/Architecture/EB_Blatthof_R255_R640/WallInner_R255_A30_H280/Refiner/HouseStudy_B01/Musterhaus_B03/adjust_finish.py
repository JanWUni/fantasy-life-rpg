"""Supported MCP correction after actual rendered review: floor and balanced visible lamps."""
import json
AS='editor_toolset.toolsets.asset.AssetTools';SC='editor_toolset.toolsets.scene.SceneTools';AC='editor_toolset.toolsets.actor.ActorTools'
OB='editor_toolset.toolsets.object.ObjectTools';BP='editor_toolset.toolsets.blueprint.BlueprintTools'
ROOT='E:/Business/fantasy-rpg-refiner/AssetSources/Architecture/EB_Blatthof_R255_R640/WallInner_R255_A30_H280/Refiner/HouseStudy_B01/Musterhaus_B03/'
FURN='/Game/Art/Furniture/ElvenHouseB03';MAT='/Game/Art/Materials/ElvenHouseB03'
def tool(g,op,**args):return execute_tool(g+'.'+op,json.dumps(args)).get('returnValue')
def ref(p):return dict(refPath=p+'.'+p.rsplit('/',1)[-1])
def props(o,**v):
    tool(OB,'list_properties',instance=o);assert tool(OB,'set_properties',instance=o,values=json.dumps(v))
def run():
    with open(ROOT+'manifest.json','r') as f:manifest=json.load(f)
    with open(ROOT+'Evidence/assemble_lab.json','r') as f:assembly=json.load(f)
    with open(ROOT+'Evidence/lab_before.json','r') as f:before=json.load(f)
    saved=[];defaults={}
    for kind,power in [('Lantern',24),('Pendant',90),('WallLantern',40)]:
        path=FURN+'/Blueprints/BP_EH03_'+kind;bp=ref(path)
        cdo=tool(BP,'get_default_object',blueprint=bp)
        for field,value in [('intensity',power),('temperature',3000)]:
            light=tool(AC,'get_components',actor=cdo,component_type=dict(refPath='/Script/Engine.PointLightComponent'))[0]
            props(light,**{field:value})
        tool(BP,'compile_blueprint',blueprint=bp,warnings_as_errors=True);saved.append(path);defaults[kind]=power
    for i,item in enumerate(manifest['placements']):
        if not item['light']:continue
        actor=assembly['new_actors']['Lab_EH_B03_Interior_%02d_'%i+item['module']]
        for field,value in [('intensity',item['light']['lumens']),('temperature',item['light']['temperature']),('attenuationRadius',item['light']['radius_cm'])]:
            light=tool(AC,'get_components',actor=actor,component_type=dict(refPath='/Script/Engine.PointLightComponent'))[0]
            props(light,**{field:value})
    floors=[]
    for old in before['actors']:
        if old['label'].startswith('Lab_EH_B02_House_10x12_') and any('SM_EH_Floor_' in (c['mesh'] or '') for c in old['meshes']):floors.append(dict(refPath=old['path']))
    floors.extend(e['actor'] for e in assembly['catalogue'] if 'SM_EH_Floor_' in e['module'])
    for actor in floors:
        comp=tool(AC,'get_components',actor=actor,component_type=dict(refPath='/Script/Engine.StaticMeshComponent'))[0]
        props(comp,overrideMaterials=[ref(MAT+'/M_EH03_Floor')])
    saved.append('/Game/Prototype/Maps/Lvl_AssetLab');assert tool(AS,'save_assets',asset_paths=saved)
    return dict(status='passed',floor_instances_corrected=len(floors),lamp_default_lumens=defaults,temperature_K=3000,
        reason='Actual first render exposed excessive lamp dominance and the old Stone slot on the floor; corrected before review')
