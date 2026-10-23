"""Read-only native geometry/collision checks unavailable in the public tool surface."""
from pathlib import Path
import json,unreal
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[6]
assert Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).resolve()==REPO
data=json.loads((ROOT/'manifest.json').read_text());base=json.loads((ROOT/'Evidence/bootstrap.json').read_text());placed=json.loads((ROOT/'Evidence/place_walls.json').read_text())
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert world.get_path_name().startswith('/Game/Prototype/Maps/Lvl_AssetLab.')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors();by={a.get_path_name():a for a in actors};labels={a.get_actor_label():a for a in actors}
def xyz(v):return [v.x,v.y,v.z]
for old in base['actors']:
    a=by[old['path']];r=a.get_actor_rotation()
    assert xyz(a.get_actor_location())==old['location'] and [r.pitch,r.yaw,r.roll]==old['rotation'] and xyz(a.get_actor_scale3d())==old['scale'],old['label']
    assert str(a.get_folder_path())==old['folder']
    comps=[dict(path=c.get_path_name(),mesh=c.static_mesh.get_path_name() if c.static_mesh else None,overrides=[m.get_path_name() if m else None for m in c.get_editor_property('override_materials')]) for c in a.get_components_by_class(unreal.StaticMeshComponent)]
    assert comps==old['components'],old['label']
sme=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);meshes={}
for n,i in data['assets'].items():
    m=unreal.load_asset('/Game/Art/Architecture/HighElfWallStudy01/Meshes/'+n);assert m and m.get_num_triangles(0)==i['triangles']
    assert m.get_editor_property('asset_import_data').get_class().get_name()=='FbxStaticMeshImportData'
    assert [str(s.material_slot_name) for s in m.static_materials]==i['slots']
    assert all(s.material_interface.get_path_name().startswith('/Game/Art/Materials/HighElfWallStudy01/') for s in m.static_materials)
    b=m.get_bounding_box();lo,hi=i['bounds_m'];expected=[[100*lo[0],-100*hi[1],100*lo[2]],[100*hi[0],-100*lo[1],100*hi[2]]]
    err=max(abs(a-b) for row,actual in zip(expected,[xyz(b.min),xyz(b.max)]) for a,b in zip(row,actual));assert err<.002,(n,err)
    assert sme.get_convex_collision_count(m)==i['ucx_hulls'],(n,sme.get_convex_collision_count(m),i['ucx_hulls'])
    meshes[n]=dict(triangles=m.get_num_triangles(0),bounds_error_cm=err,hulls=sme.get_convex_collision_count(m),slots=i['slots'])
checks=[]
def trace(a,b):return unreal.SystemLibrary.line_trace_single(world,unreal.Vector(*a),unreal.Vector(*b),unreal.TraceTypeQuery.ECC_VISIBILITY,False,[],unreal.DrawDebugTrace.NONE,True)
for p in placed['placed']:
    a=labels[p['label']];assert xyz(a.get_actor_location())==p['location_cm'] and xyz(a.get_actor_scale3d())==[1,1,1]
    comps=a.get_components_by_class(unreal.StaticMeshComponent);assert len(comps)==6
    core=next(c for c in comps if c.static_mesh.get_name().endswith('WallCore'));glass=next(c for c in comps if c.static_mesh.get_name().endswith('ClearGlass'))
    assert not glass.get_editor_property('cast_shadow');assert glass.get_collision_profile_name()=='BlockAll'
    for c in comps:
        assert c.static_mesh.get_path_name().startswith('/Game/Art/Architecture/HighElfWallStudy01/')
        if c not in [core,glass]:assert c.get_collision_profile_name()=='NoCollision'
    x,y,z=p['location_cm'];pane=trace([x+160,y+150,z+170],[x+160,y-150,z+170]);assert pane
    # A trace from each side must hit the pane first. A hull across the aperture would hit the core first.
    pane_hits=[]
    for direction in [-1,1]:
        hit=trace([x+160,y+150*direction,z+170],[x+160,y-150*direction,z+170]);assert hit
        component=hit.to_dict()['hit_component'];assert component==glass,(p['label'],str(component))
        pane_hits.append(component.get_path_name())
    for label,px,pz in [('side',x+90,z+170),('sill',x+150,z+110),('header',x+150,z+260)]:
        hit=trace([px,y+150,pz],[px,y-150,pz]);assert hit
        assert hit.to_dict()['hit_component']==core,(p['label'],label,str(hit))
    checks.append(dict(actor=p['label'],pane_blocks=True,core_aperture_free=True,wall_blocks=True))
seams=[]
for x in [1899.8,1900.2]:
    h=trace([x,2450,160],[x,2250,160]);assert h;seams.append(xyz(h.to_dict()['impact_point']))
capsules=[]
for x,blocked in [(1750,True),(2350,True),(2050,False)]:
    for direction in [-1,1]:
        h=unreal.SystemLibrary.capsule_trace_single(world,unreal.Vector(x,3100+180*direction,93),unreal.Vector(x,3100-180*direction,93),35,90,unreal.TraceTypeQuery.ECC_VISIBILITY,False,[],unreal.DrawDebugTrace.NONE,True)
        assert (h is not None)==blocked,(x,direction,str(h))
        capsules.append(dict(x=x,direction=direction,blocked=blocked,radius_cm=35,half_height_cm=90))
write=dict(status='passed',existing_actors_preserved=len(base['actors']),meshes=meshes,wall_checks=checks,seam_simple_collision=seams,scope='Editor mesh/material/placement/simple-collision checks; no clean editor reload, no performance certification')
write['capsule_checks']=capsules
(ROOT/'Evidence/unreal_verification.json').write_text(json.dumps(write,indent=2)+'\n');unreal.log('HE01_VERIFY_PASSED')
