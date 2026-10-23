"""Two reusable Blueprints with one HISM per unique mesh, no per-stone actors."""
import json
AS='editor_toolset.toolsets.asset.AssetTools';OB='editor_toolset.toolsets.object.ObjectTools'
BP='editor_toolset.toolsets.blueprint.BlueprintTools';AC='editor_toolset.toolsets.actor.ActorTools'
ROOT='E:/Business/fantasy-rpg-refiner/AssetSources/Architecture/EC_HighCultureCity/StreetStudy01/Refiner/UnrealReview_01/'
def tool(g,n,**a):return execute_tool(g+'.'+n,json.dumps(a)).get('returnValue')
def ref(p):return dict(refPath=p+'.'+p.rsplit('/',1)[-1])
def props(o,**v):
    tool(OB,'list_properties',instance=o);assert tool(OB,'set_properties',instance=o,values=json.dumps(v))
def run():
    with open(ROOT+'plan.json','r') as f:plan=json.load(f)
    result={}
    for study in plan['studies']:
        path=study['dest']+'/'+study['blueprint']
        if tool(AS,'exists',path=path):bp=ref(path)
        else:bp=tool(BP,'create',folder_path=study['dest'],asset_name=study['blueprint'],asset_type=dict(refPath='/Script/Engine.Actor'))
        existing=tool(AC,'get_components',actor=tool(BP,'get_default_object',blueprint=bp),component_type=dict(refPath='/Script/Engine.HierarchicalInstancedStaticMeshComponent'))
        assert not existing,'Existing partially built assembly must be inspected, not overwritten'
        for e in study['mesh_manifest']['exports']:
            comp=tool(AC,'add_component',owner=bp,component_type=dict(refPath='/Script/Engine.HierarchicalInstancedStaticMeshComponent'),name='Instances_'+e['asset_name'])
            cdo=tool(BP,'get_default_object',blueprint=bp)
            root=tool(AC,'get_root_component',actor=cdo);props(root,mobility='Static')
            comps=tool(AC,'get_components',actor=tool(BP,'get_default_object',blueprint=bp),component_type=dict(refPath='/Script/Engine.HierarchicalInstancedStaticMeshComponent'))
            comp=next(c for c in comps if ('Instances_'+e['asset_name']) in c['refPath'])
            props(comp,staticMesh=ref(study['dest']+'/Meshes/'+e['asset_name']))
            # Reacquire after every BP property edit/reinstancing.
            cdo=tool(BP,'get_default_object',blueprint=bp)
            comps=tool(AC,'get_components',actor=cdo,component_type=dict(refPath='/Script/Engine.HierarchicalInstancedStaticMeshComponent'))
            comp=next(c for c in comps if ('Instances_'+e['asset_name']) in c['refPath'])
            props(comp,mobility='Static')
            cdo=tool(BP,'get_default_object',blueprint=bp);comps=tool(AC,'get_components',actor=cdo,component_type=dict(refPath='/Script/Engine.HierarchicalInstancedStaticMeshComponent'))
            comp=next(c for c in comps if ('Instances_'+e['asset_name']) in c['refPath'])
            props(comp,castShadow='Glass' not in e['source_stats']['material_slots'])
            cdo=tool(BP,'get_default_object',blueprint=bp);comps=tool(AC,'get_components',actor=cdo,component_type=dict(refPath='/Script/Engine.HierarchicalInstancedStaticMeshComponent'))
            comp=next(c for c in comps if ('Instances_'+e['asset_name']) in c['refPath'])
            collision=bool(e['collision_names'] or 'Glass' in e['source_stats']['material_slots'] or 'Paving' in e['label'] or 'CourtStone' in e['label'])
            props(comp,bodyInstance=dict(collisionProfileName='BlockAll' if collision else 'NoCollision',collisionEnabled='QueryAndPhysics' if collision else 'NoCollision'))
        tool(BP,'compile_blueprint',blueprint=bp,warnings_as_errors=True)
        cdo=tool(BP,'get_default_object',blueprint=bp)
        comps=tool(AC,'get_components',actor=cdo,component_type=dict(refPath='/Script/Engine.HierarchicalInstancedStaticMeshComponent'))
        assert len(comps)==len(study['mesh_manifest']['exports'])
        assert tool(AS,'save_assets',asset_paths=[path]);result[study['tag']]=dict(blueprint=path,components=comps)
    return dict(status='passed',assemblies=result,instances_not_yet_populated=True)
