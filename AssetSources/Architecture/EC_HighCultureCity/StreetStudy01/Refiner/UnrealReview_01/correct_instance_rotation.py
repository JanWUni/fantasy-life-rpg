"""Correct the positional Rotator constructor error using explicit named axes."""
from pathlib import Path
import json,unreal
ROOT=Path(__file__).resolve().parent
assert Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).resolve()==ROOT.parents[5]
plan=json.loads((ROOT/'plan.json').read_text());created=json.loads((ROOT/'Evidence/create_assemblies.json').read_text())
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors();counts={}
for s in plan['studies']:
    actor=next(a for a in actors if a.get_actor_label()=='Lab_Study'+s['tag']+'_ClearGlass')
    live=actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent);count=0
    for e in s['mesh_manifest']['exports']:
        template=unreal.load_object(None,next(c['refPath'] for c in created['assemblies'][s['tag']]['components'] if 'Instances_'+e['asset_name'] in c['refPath']))
        actual=next(c for c in live if c.static_mesh.get_name()==e['asset_name'])
        instances=[i for i in s['mesh_manifest']['placement_instances'] if i['asset']==e['asset_name']]
        for comp in [template,actual]:
            assert comp.get_instance_count()==len(instances);comp.modify()
            for index,i in enumerate(instances):
                x,y,z=i['location_blender_m']
                t=unreal.Transform(location=unreal.Vector(100*x,-100*y,100*z),rotation=unreal.Rotator(pitch=0,yaw=-i['yaw_blender_degrees'],roll=0),scale=unreal.Vector(1,1,1))
                assert comp.update_instance_transform(index,t,world_space=False,mark_render_state_dirty=index==len(instances)-1,teleport=True)
        count+=len(instances)
    counts[s['tag']]=count
(ROOT/'Evidence/rotation_correction.json').write_text(json.dumps(dict(status='passed',instance_counts=counts,
    correction='Explicit Rotator(pitch=0,yaw=-BlenderYaw,roll=0) for saved templates and live actors; source transforms unchanged'),indent=2)+'\n')
unreal.log('STUDY_AB_ROTATIONS_CORRECTED')
