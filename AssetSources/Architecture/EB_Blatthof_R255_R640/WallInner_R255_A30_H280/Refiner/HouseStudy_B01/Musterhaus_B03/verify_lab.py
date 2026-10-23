"""Actual saved-world geometry, collision, lamp placement and preservation audit."""
from pathlib import Path
import json,unreal,math
ROOT=Path(__file__).resolve().parent
assert Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).resolve()==Path('E:/Business/fantasy-rpg-refiner')
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert world.get_path_name().startswith('/Game/Prototype/Maps/Lvl_AssetLab.')
manifest=json.loads((ROOT/'manifest.json').read_text());before=json.loads((ROOT/'Evidence/lab_before.json').read_text())
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors();by_path={a.get_path_name():a for a in actors}
def xyz(v):return [v.x,v.y,v.z]
preserved=[];refined=[]
for old in before['actors']:
    a=by_path[old['path']];r=a.get_actor_rotation()
    assert xyz(a.get_actor_location())==old['position'] and [r.pitch,r.yaw,r.roll]==old['rotation'] and xyz(a.get_actor_scale3d())==old['scale'],old['label']
    assert str(a.get_folder_path())==old['folder']
    current=[dict(path=c.get_path_name(),mesh=c.static_mesh.get_path_name() if c.static_mesh else None,
        overrides=[m.get_path_name() if m else None for m in c.get_editor_property('override_materials')]) for c in a.get_components_by_class(unreal.StaticMeshComponent)]
    if old['label'].startswith('Lab_EH_B02_House_10x12_'):
        assert [c['mesh'] for c in current]==[c['mesh'] for c in old['meshes']]
        refined.append(old['label'])
    else:assert current==old['meshes'],old['label'];preserved.append(old['label'])
smes=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);meshresults={}
for name,info in manifest['assets'].items():
    folder=('/Game/Art/Architecture/ElvenHouseB03' if any(s in name for s in ['Interior','Ceiling']) else '/Game/Art/Furniture/ElvenHouseB03')+'/Meshes'
    mesh=unreal.load_asset(folder+'/'+name);box=mesh.get_bounding_box();actual=[xyz(box.min),xyz(box.max)]
    lo,hi=info['bounds_m'];expected=[[100*lo[0],-100*hi[1],100*lo[2]],[100*hi[0],-100*lo[1],100*hi[2]]]
    error=max(abs(actual[i][j]-expected[i][j]) for i in range(2) for j in range(3));assert error<.002,(name,error)
    assert mesh.get_num_triangles(0)==info['triangles'];assert smes.get_convex_collision_count(mesh)==info['ucx_hulls']
    slots=[str(m.material_slot_name) for m in mesh.static_materials];assert slots==['B03_'+s for s in info['slots']],(name,slots)
    assert mesh.get_editor_property('asset_import_data').get_class().get_name()=='FbxStaticMeshImportData'
    assert all(m.material_interface.get_path_name().startswith('/Game/Art/Materials/ElvenHouseB03/') for m in mesh.static_materials)
    meshresults[name]=dict(bounds_cm=actual,bounds_error_cm=error,triangles=mesh.get_num_triangles(0),hulls=smes.get_convex_collision_count(mesh),slots=slots,uv_channels=smes.get_num_uv_channels(mesh,0))
new=[a for a in actors if a.get_actor_label().startswith('Lab_EH_B03_')]
catalogue=[a for a in new if a.get_actor_label().startswith('Lab_EH_B03_Catalogue_') and 'Title' not in a.get_actor_label()]
assert len(catalogue)==34,len(catalogue)
interior=[a for a in new if a.get_actor_label().startswith('Lab_EH_B03_Interior_')];assert len(interior)==37
lamps=[]
for a in interior:
    assert xyz(a.get_actor_scale3d())==[1,1,1]
    for light in a.get_components_by_class(unreal.PointLightComponent):
        origin=light.get_world_location();fixture=a.get_component_by_class(unreal.StaticMeshComponent)
        assert fixture and (origin-a.get_actor_location()).length()<30
        assert light.get_editor_property('use_inverse_squared_falloff') and light.get_editor_property('cast_shadows')
        lamps.append(dict(label=a.get_actor_label(),position_cm=xyz(origin),lumens=light.get_editor_property('intensity'),
            units=str(light.get_editor_property('intensity_units')),radius_cm=light.get_editor_property('attenuation_radius'),
            temperature=light.get_editor_property('temperature'),visible_fixture=True,actor_tick_enabled=a.is_actor_tick_enabled()))
assert len(lamps)==4
all_points=[c for a in actors for c in a.get_components_by_class(unreal.PointLightComponent)];assert len(all_points)==4
# Capsule sweeps through both new doorways and the main approach, plus blocked wall samples.
def point(x,y,z=92):return unreal.Vector(-2400+100*x,-1900-100*y,31+z)
routes=[[(5,.5),(5,5.9)],[(5,6.3),(3.24,6.3)],[(3.24,6.3),(3.24,8.8)],[(5,6.3),(7.24,6.3)],[(7.24,6.3),(7.24,9.6)]]
checks=[]
for start,end in routes:
    hit=unreal.SystemLibrary.capsule_trace_single(world,point(*start),point(*end),35,90,unreal.TraceTypeQuery.ECC_VISIBILITY,False,[],unreal.DrawDebugTrace.NONE,True)
    assert hit is None,(start,end,hit.to_dict() if hit else None)
    checks.append(dict(from_blender_m=start,to_blender_m=end,clear_capsule_radius_cm=35,half_height_cm=90))
for x in [1.2,5.,8.9]:
    hit=unreal.SystemLibrary.line_trace_single(world,point(x,6.9,150),point(x,7.5,150),unreal.TraceTypeQuery.ECC_VISIBILITY,False,[],unreal.DrawDebugTrace.NONE,True)
    assert hit is not None,('Partition missing',x)
ceilings=[]
for x,y in [(2,9),(7,9)]:
    hit=unreal.SystemLibrary.line_trace_single(world,point(x,y,200),point(x,y,350),unreal.TraceTypeQuery.ECC_VISIBILITY,False,[],unreal.DrawDebugTrace.NONE,True)
    assert hit is not None
    z=hit.to_dict()['location'].z;assert abs(z-331)<.02,z;ceilings.append(z)
sun=next(a for a in actors if isinstance(a,unreal.DirectionalLight))
assert sun.get_component_by_class(unreal.DirectionalLightComponent).get_editor_property('intensity')==6
result=dict(status='passed',map=world.get_path_name(),existing_actors_fully_preserved=len(preserved),small_house_overrides_only=len(refined),
    new_actors=len(new),catalogue_meshes=len(catalogue),interior_instances=len(interior),meshes=meshresults,lamps=lamps,capsule_sweeps=checks,
    rear_room_ceiling_heights_cm=ceilings,hidden_fill_lights=0,existing_daylight_unchanged=True)
(ROOT/'Evidence/lab_verification.json').write_text(json.dumps(result,indent=2)+'\n')
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_set_game_view(True)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_set_viewport_realtime(True)
unreal.log('B03_LAB_VERIFIED')
