from pathlib import Path
import json,unreal
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[6]
assert Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).resolve()==REPO
d=json.loads((ROOT/'manifest.json').read_text());base=json.loads((ROOT/'Evidence/bootstrap.json').read_text());moved=json.loads((ROOT/'Evidence/move_inserts.json').read_text())
changes={e['label']:e['position_cm'] for e in moved['installed_inserts']}
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors();by={a.get_path_name():a for a in actors};labels={a.get_actor_label():a for a in actors}
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert world.get_path_name().startswith('/Game/Prototype/Maps/Lvl_AssetLab.')
def xyz(v):return [v.x,v.y,v.z]
for old in base['actors']:
    a=by[old['path']];r=a.get_actor_rotation();expected=changes.get(old['label'],old['location'])
    assert xyz(a.get_actor_location())==expected and [r.pitch,r.yaw,r.roll]==old['rotation'] and xyz(a.get_actor_scale3d())==old['scale'],old['label']
    assert str(a.get_folder_path())==old['folder']
    now=[dict(path=c.get_path_name(),mesh=c.static_mesh.get_path_name() if c.static_mesh else None,
        overrides=[m.get_path_name() if m else None for m in c.get_editor_property('override_materials')]) for c in a.get_components_by_class(unreal.StaticMeshComponent)]
    assert now==old['components'],old['label']
sme=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);meshes={}
for n,i in d['assets'].items():
    m=unreal.load_asset('/Game/Art/Architecture/WallCatalogue01/Meshes/'+n);b=m.get_bounding_box();lo,hi=i['bounds_m']
    expected=[[100*lo[0],-100*hi[1],100*lo[2]],[100*hi[0],-100*lo[1],100*hi[2]]]
    error=max(abs(x-y) for a,b in zip(expected,[xyz(b.min),xyz(b.max)]) for x,y in zip(a,b));assert error<.002
    assert m.get_num_triangles(0)==i['triangles'] and sme.get_convex_collision_count(m)==i['ucx_hulls']
    assert [str(s.material_slot_name) for s in m.static_materials]==['WC01_'+s for s in i['slots']]
    meshes[n]=dict(bounds_error_cm=error,triangles=m.get_num_triangles(0),ucx_hulls=sme.get_convex_collision_count(m))
def trace(x,z,ignore=[]):return unreal.SystemLibrary.line_trace_single(world,unreal.Vector(x,3120,z),unreal.Vector(x,2880,z),unreal.TraceTypeQuery.ECC_VISIBILITY,False,ignore,unreal.DrawDebugTrace.NONE,True)
checks=[]
for s,x in [('A',-2200),('B',-1200),('C',-200)]:
    glass=labels['Lab_WC01_'+s+'_WindowGlass_Clear_112x2x145'];wall=labels['Lab_WC01_'+s+'_Window']
    assert not glass.get_component_by_class(unreal.StaticMeshComponent).get_editor_property('cast_shadow')
    h=trace(x+165,180);assert h is not None,(s,'new glass missing')
    assert trace(x+165,180,[glass]) is None,(s,'new opening not clear')
    assert trace(x+195,180) is not None,(s,'new side infill missing')
    assert trace(x+195,180,[wall]) is None,(s,'old oversized glass collision remains')
    assert trace(x+150,120) is not None,(s,'raised sill not solid')
    assert trace(x+150,240) is not None,(s,'lowered header not solid')
    checks.append(dict(style=s,glass_blocks=True,real_opening_clear=True,new_side_sill_header_block=True,no_old_oversized_glass_collision=True))
(ROOT/'Evidence/unreal_verification.json').write_text(json.dumps(dict(status='passed',existing_actors_checked=len(base['actors']),only_six_insert_translations_changed=True,
    existing_house_changes=0,meshes=meshes,collision_checks=checks,colors_and_material_slots_preserved=True),indent=2)+'\n')
unreal.log('WC02_VERIFICATION_PASSED')
