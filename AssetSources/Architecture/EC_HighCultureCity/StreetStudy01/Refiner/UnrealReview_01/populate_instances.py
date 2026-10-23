"""Native fallback only for HISM instance editing and primitive collision creation.

Public MCP has no AddInstances or add-simple-box operation. Mesh/BP creation,
material editing, compilation, placement and saving are separate MCP batches.
"""
from pathlib import Path
import json,math,unreal
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[5]
assert Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).resolve()==REPO
plan=json.loads((ROOT/'plan.json').read_text());created=json.loads((ROOT/'Evidence/create_assemblies.json').read_text())
sme=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
result={};measurements={}
for study in plan['studies']:
    total=0;components=created['assemblies'][study['tag']]['components']
    for e in study['mesh_manifest']['exports']:
        mesh=unreal.load_asset(study['dest']+'/Meshes/'+e['asset_name']);assert mesh
        imported=mesh.get_editor_property('asset_import_data');assert imported.get_class().get_name()=='FbxStaticMeshImportData'
        box=mesh.get_bounding_box();lo=e['source_stats']['bounds_blender_m'][0];hi=e['source_stats']['bounds_blender_m'][1]
        expectedlo=[100*lo[0],-100*hi[1],100*lo[2]];expectedhi=[100*hi[0],-100*lo[1],100*hi[2]]
        actual=[box.min.x,box.min.y,box.min.z,box.max.x,box.max.y,box.max.z]
        error=max(abs(a-b) for a,b in zip(actual,expectedlo+expectedhi));assert error<.002,(e['asset_name'],error)
        prior_hulls=sme.get_simple_collision_count(mesh)+sme.get_convex_collision_count(mesh)
        assert prior_hulls==len(e['collision_names']),(e['asset_name'],prior_hulls,len(e['collision_names']))
        supplement=not e['collision_names'] and ('Glass' in e['source_stats']['material_slots'] or 'Paving' in e['label'] or 'CourtStone' in e['label'])
        if supplement:
            index=sme.add_simple_collisions(mesh,unreal.ScriptingCollisionShapeType.BOX);assert index>=0
            assert sme.get_simple_collision_count(mesh)+sme.get_convex_collision_count(mesh)==1
        comp_ref=next(c['refPath'] for c in components if 'Instances_'+e['asset_name'] in c['refPath'])
        component=unreal.load_object(None,comp_ref);assert isinstance(component,unreal.HierarchicalInstancedStaticMeshComponent),comp_ref
        assert component.get_instance_count()==0,'Never overwrite populated assembly data'
        instances=[i for i in study['mesh_manifest']['placement_instances'] if i['asset']==e['asset_name']]
        transforms=[]
        for i in instances:
            assert max(abs(v-1) for v in i['scale'])<1e-6
            x,y,z=i['location_blender_m']
            transforms.append(unreal.Transform(location=unreal.Vector(100*x,-100*y,100*z),rotation=unreal.Rotator(pitch=0,yaw=-i['yaw_blender_degrees'],roll=0),scale=unreal.Vector(1,1,1)))
        component.modify();component.add_instances(transforms,False,False,False)
        assert component.get_instance_count()==len(instances),(e['asset_name'],component.get_instance_count(),len(instances))
        total+=len(instances)
        measurements[e['asset_name']]=dict(importer=imported.get_class().get_name(),bounds_error_cm=error,original_ucx=prior_hulls,
            added_simple_box=bool(supplement),simple_collision_count=sme.get_simple_collision_count(mesh),convex_collision_count=sme.get_convex_collision_count(mesh),instances=len(instances),template=comp_ref)
    exported={e['asset_name'] for e in study['mesh_manifest']['exports']}
    excluded=[i for i in study['mesh_manifest']['placement_instances'] if i['asset'] not in exported]
    assert all('ScaleFigure' in i['asset'] for i in excluded)
    assert total==len(study['mesh_manifest']['placement_instances'])-len(excluded)
    result[study['tag']]=dict(instances=total,unique_components=len(components),nonexported_blender_reference_figures=excluded)
(ROOT/'Evidence/populate_instances.json').write_text(json.dumps(dict(status='passed',assemblies=result,meshes=measurements,
    source_mapping='UE_cm=(100*Bx,-100*By,100*Bz), yaw=-BlenderYaw; source placements unrounded',
    collision_addition='One simple box only on new glass and paving meshes; original imported UCX preserved'),indent=2)+'\n')
unreal.log('STUDY_AB_INSTANCE_DATA_READY')
