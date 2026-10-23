"""Read-only native evidence of saved assemblies, existing actors and simple collision."""
from pathlib import Path
import json,math,unreal
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[5]
assert Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).resolve()==REPO
plan=json.loads((ROOT/'plan.json').read_text());before=json.loads((ROOT/'Evidence/bootstrap_initial.json').read_text())
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert world.get_path_name().startswith(plan['map']+'.')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors();by_path={a.get_path_name():a for a in actors}
def xyz(v):return [v.x,v.y,v.z]
for old in before['actors']:
    a=by_path[old['path']];r=a.get_actor_rotation()
    assert xyz(a.get_actor_location())==old['location'] and [r.pitch,r.yaw,r.roll]==old['rotation'] and xyz(a.get_actor_scale3d())==old['scale'],old['label']
    assert str(a.get_folder_path())==old['folder']
    now=[dict(path=c.get_path_name(),mesh=c.static_mesh.get_path_name() if c.static_mesh else None,
        overrides=[m.get_path_name() if m else None for m in c.get_editor_property('override_materials')]) for c in a.get_components_by_class(unreal.StaticMeshComponent)]
    assert now==old['components'],old['label']
sme=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);results={};probes=[]
character=unreal.get_default_object(unreal.load_class(None,'/Game/Prototype/Blueprints/BP_PrototypeCharacter.BP_PrototypeCharacter_C'))
cap=character.get_component_by_class(unreal.CapsuleComponent);radius=cap.get_scaled_capsule_radius();half=cap.get_scaled_capsule_half_height()
def point(study,loc):return unreal.Vector(study['offset'][0]+100*loc[0],study['offset'][1]-100*loc[1],study['offset'][2]+100*loc[2])
def transform(loc,center,yaw):
    a=math.radians(yaw);x,y,z=loc
    return [center[0]+x*math.cos(a)-y*math.sin(a),center[1]+x*math.sin(a)+y*math.cos(a),center[2]+z]
def trace(study,start,end,capsule=False):
    common=(world,point(study,start),point(study,end));tail=(unreal.TraceTypeQuery.ECC_VISIBILITY,False,[],unreal.DrawDebugTrace.NONE,True)
    return unreal.SystemLibrary.capsule_trace_single(*common,radius,half,*tail) if capsule else unreal.SystemLibrary.line_trace_single(*common,*tail)
for s in plan['studies']:
    a=next(a for a in actors if a.get_actor_label()=='Lab_Study'+s['tag']+'_ClearGlass')
    assert xyz(a.get_actor_location())==s['offset'] and xyz(a.get_actor_scale3d())==[1,1,1]
    comps=a.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent);assert len(comps)==len(s['mesh_manifest']['exports'])
    measured={};count=0;glass_checks=0
    for e in s['mesh_manifest']['exports']:
        comp=next(c for c in comps if c.static_mesh.get_name()==e['asset_name']);mesh=comp.static_mesh
        instances=[i for i in s['mesh_manifest']['placement_instances'] if i['asset']==e['asset_name']]
        assert comp.get_instance_count()==len(instances),(e['asset_name'],comp.get_instance_count(),len(instances))
        count+=len(instances);maxerror=0
        for index,i in enumerate(instances):
            actual=comp.get_instance_transform(index,True);expected=point(s,i['location_blender_m'])
            error=(actual.translation-expected).length();assert error<.005,(i['object'],error)
            maxerror=max(maxerror,error);assert max(abs(v-1) for v in xyz(actual.scale3d))<1e-6
            yaw=actual.rotation.rotator().yaw;assert abs((yaw+i['yaw_blender_degrees']+180)%360-180)<.001,(i['object'],yaw,i['yaw_blender_degrees'],str(actual.rotation.rotator()))
            if 'Glass' in e['source_stats']['material_slots']:
                assert not comp.get_editor_property('cast_shadow')
                start=transform((.15,.515,.4),i['location_blender_m'],i['yaw_blender_degrees'])
                end=transform((.15,-.285,.4),i['location_blender_m'],i['yaw_blender_degrees'])
                hit=trace(s,start,end);assert hit is not None,(i['object'],'glass not blocking')
                expected_hit=point(s,transform((.15,.13,.4),i['location_blender_m'],i['yaw_blender_degrees']))
                assert (hit.to_dict()['impact_point']-expected_hit).length()<.1,(i['object'],hit.to_dict())
                glass_checks+=1
        assert mesh.get_num_triangles(0)==e['source_stats']['triangles']
        assert mesh.get_editor_property('asset_import_data').get_class().get_name()=='FbxStaticMeshImportData'
        assert [str(m.material_slot_name) for m in mesh.static_materials]==e['source_stats']['material_slots']
        assert all(m.material_interface.get_path_name().startswith(plan['materials']+'/') for m in mesh.static_materials)
        measured[e['asset_name']]=dict(instances=len(instances),max_instance_position_error_cm=maxerror,
            triangles=mesh.get_num_triangles(0),convex_ucx=sme.get_convex_collision_count(mesh),simple_primitives=sme.get_simple_collision_count(mesh))
    for check in s['mesh_manifest']['interior_test_contracts']:
        for x,y in check['floor_samples']:
            start=transform((x,y,2),check['center'],check['yaw']);end=transform((x,y,-.5),check['center'],check['yaw'])
            hit=trace(s,start,end);assert hit and abs(hit.to_dict()['impact_point'].z-s['offset'][2])<.05,(s['tag'],check['name'],'floor',hit)
        if check.get('access')=='internal_only':
            start=transform((check['direction']*2.5,0,.92),check['center'],check['yaw'])
            end=transform((check['direction']*5.6,0,.92),check['center'],check['yaw'])
        else:
            front=check['door_local_front'][1]
            start=transform((0,front-1,.92),check['center'],check['yaw']);end=transform((0,front+1.2,.92),check['center'],check['yaw'])
        hit=trace(s,start,end,True);assert hit is None,(s['tag'],check['name'],'capsule blocked',hit.to_dict() if hit else None)
        probes.append(dict(study=s['tag'],name=check['name'],capsule_clear=True,radius_cm=radius,half_height_cm=half,from_blender_m=start,to_blender_m=end))
    results[s['tag']]=dict(actor=a.get_path_name(),component_count=len(comps),instances=count,glass_panes_physically_checked=glass_checks,meshes=measured)
result=dict(status='passed',map=world.get_path_name(),existing_actors_preserved=len(before['actors']),new_assembly_actors=2,
    assemblies=results,capsule_probes=probes,scope='Editor world, actual source UCX and added primitive collision, not keyboard gameplay or production acceptance')
(ROOT/'Evidence/lab_verification.json').write_text(json.dumps(result,indent=2)+'\n')
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_set_game_view(True)
unreal.log('STUDY_AB_LAB_VERIFIED')
