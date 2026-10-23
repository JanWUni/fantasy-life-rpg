"""Actual live editor checks, read-only except for writing this delivery's evidence."""
from pathlib import Path
import json,unreal
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[5]
assert Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).resolve()==REPO
data=json.loads((ROOT/'manifest.json').read_text());base=json.loads((ROOT/'Evidence/bootstrap.json').read_text())
placed=json.loads((ROOT/'Evidence/place_catalogue.json').read_text())
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert world.get_path_name().startswith('/Game/Prototype/Maps/Lvl_AssetLab.')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors();by={a.get_path_name():a for a in actors};labels={a.get_actor_label():a for a in actors}
def xyz(v):return [v.x,v.y,v.z]
for old in base['actors']:
    a=by[old['path']];r=a.get_actor_rotation()
    assert xyz(a.get_actor_location())==old['location'] and [r.pitch,r.yaw,r.roll]==old['rotation'] and xyz(a.get_actor_scale3d())==old['scale'],old['label']
    assert str(a.get_folder_path())==old['folder']
    comps=[dict(path=c.get_path_name(),mesh=c.static_mesh.get_path_name() if c.static_mesh else None,
        overrides=[m.get_path_name() if m else None for m in c.get_editor_property('override_materials')]) for c in a.get_components_by_class(unreal.StaticMeshComponent)]
    assert comps==old['components'],old['label']
sme=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);meshes={}
for n,i in data['assets'].items():
    folder='Furniture' if i['kind'] in ['Furniture','Lamp'] else 'Architecture'
    mesh=unreal.load_asset('/Game/Art/'+folder+'/WallCatalogue01/Meshes/'+n)
    assert mesh and mesh.get_num_triangles(0)==i['triangles']
    assert mesh.get_editor_property('asset_import_data').get_class().get_name()=='FbxStaticMeshImportData'
    assert [str(m.material_slot_name) for m in mesh.static_materials]==['WC01_'+s for s in i['slots']]
    assert all(m.material_interface.get_path_name().startswith('/Game/Art/Materials/WallCatalogue01/') for m in mesh.static_materials)
    b=mesh.get_bounding_box();lo=i['bounds_m'][0];hi=i['bounds_m'][1]
    expected=[[100*lo[0],-100*hi[1],100*lo[2]],[100*hi[0],-100*lo[1],100*hi[2]]]
    err=max(abs(a-b) for row,actual in zip(expected,[xyz(b.min),xyz(b.max)]) for a,b in zip(row,actual));assert err<.002,(n,err)
    assert sme.get_convex_collision_count(mesh)==i['ucx_hulls'],(n,sme.get_convex_collision_count(mesh),i['ucx_hulls'])
    meshes[n]=dict(triangles=mesh.get_num_triangles(0),bounds_error_cm=err,ucx_hulls=sme.get_convex_collision_count(mesh),slots=i['slots'])
new=[];lamps=[]
for p in placed['placed']:
    a=labels[p['label']];assert xyz(a.get_actor_location())==p['location_cm'] and xyz(a.get_actor_scale3d())==[1,1,1]
    assert str(a.get_folder_path()).startswith('Lab/Architecture/WallCatalogue01/')
    if p['kind']=='Lamp':
        c=a.get_component_by_class(unreal.PointLightComponent);assert c
        assert c.intensity==32 and c.temperature==3000 and c.attenuation_radius==240
        assert c.get_editor_property('use_inverse_squared_falloff') and c.get_editor_property('cast_shadows')
        assert xyz(c.get_editor_property('relative_location'))==[0,40,-23]
        lamps.append(dict(actor=a.get_actor_label(),lumens=c.intensity,temperature=c.temperature,radius_cm=c.attenuation_radius,source_cm=xyz(c.get_world_location())))
    new.append(a.get_actor_label())
def trace(a,b,ignore=[]):
    return unreal.SystemLibrary.line_trace_single(world,unreal.Vector(*a),unreal.Vector(*b),unreal.TraceTypeQuery.ECC_VISIBILITY,False,ignore,unreal.DrawDebugTrace.NONE,True)
window_checks=[]
for style,x in [('A',-2200),('B',-1200),('C',-200)]:
    glass=labels['Lab_WC01_'+style+'_WindowGlass_Clear_112x2x145'];comp=glass.get_component_by_class(unreal.StaticMeshComponent);assert not comp.get_editor_property('cast_shadow')
    a=[x+175,3120,137];b=[x+175,2880,137]
    hit=trace(a,b);assert hit is not None,(style,'pane missing')
    assert trace(a,b,[glass]) is None,(style,'opening filled')
    assert trace([x+50,3120,180],[x+50,2880,180]) is not None,(style,'wall collision missing')
    window_checks.append(dict(style=style,pane_blocks=True,actual_aperture_clear_when_only_pane_ignored=True,wall_blocks=True))
seam=[]
for x in [999.8,1000.2]:
    h=trace([x,3600,152],[x,3400,152]);assert h is not None
    seam.append(dict(x_cm=x,hit_cm=xyz(h.to_dict()['impact_point'])))
write=dict(status='passed',existing_actors_preserved=len(base['actors']),existing_house_actors_modified=0,new_actors=len(new),meshes=meshes,
    window_checks=window_checks,seam_checks=seam,lamps=lamps,scope='Actual editor geometry/collision/placement/material/lighting properties, not manual traversal or production acceptance')
(ROOT/'Evidence/unreal_verification.json').write_text(json.dumps(write,indent=2)+'\n')
unreal.log('WC01_VERIFICATION_PASSED')
