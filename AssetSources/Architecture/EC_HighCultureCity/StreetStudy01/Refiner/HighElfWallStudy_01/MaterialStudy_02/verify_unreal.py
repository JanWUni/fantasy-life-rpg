from pathlib import Path
import json,unreal
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[6]
assert Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).resolve()==REPO
base=json.loads((ROOT/'Evidence/baseline.json').read_text());world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert world.get_path_name().startswith('/Game/Prototype/Maps/Lvl_AssetLab.')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors();by={a.get_path_name():a for a in actors};labels={a.get_actor_label():a for a in actors}
def xyz(v):return [v.x,v.y,v.z]
for old in base['actors']:
    a=by[old['path']];r=a.get_actor_rotation();assert xyz(a.get_actor_location())==old['location'] and [r.pitch,r.yaw,r.roll]==old['rotation'] and xyz(a.get_actor_scale3d())==old['scale']
    assert str(a.get_folder_path())==old['folder']
    comps=[dict(path=c.get_path_name(),mesh=c.static_mesh.get_path_name() if c.static_mesh else None,overrides=[m.get_path_name() if m else None for m in c.get_editor_property('override_materials')]) for c in a.get_components_by_class(unreal.StaticMeshComponent)]
    assert comps==old['components'],old['label']
old=labels['Lab_HE02_Vorher'];new=labels['Lab_HE02_Materialstudie'];oc={c.get_name():c for c in old.get_components_by_class(unreal.StaticMeshComponent)};nc={c.get_name():c for c in new.get_components_by_class(unreal.StaticMeshComponent)}
assert set(oc)==set(nc) and len(nc)==6
components={}
for n,c in nc.items():
    assert c.static_mesh==oc[n].static_mesh
    assert xyz(c.get_relative_transform().translation)==xyz(oc[n].get_relative_transform().translation)
    assert xyz(c.get_world_scale())==[1,1,1]
    mats=[c.get_material(i).get_path_name() for i in range(c.get_num_materials())];assert all(m.startswith('/Game/Art/Materials/HighElfWallStudy02/') for m in mats),(n,mats)
    assert all(oc[n].get_material(i).get_path_name().startswith('/Game/Art/Materials/HighElfWallStudy01/') for i in range(oc[n].get_num_materials()))
    components[n]=dict(mesh=c.static_mesh.get_path_name(),materials=mats,collision=str(c.get_collision_profile_name()))
assert not nc['ClearGlass'].get_editor_property('cast_shadow') and nc['ClearGlass'].get_collision_profile_name()=='BlockAll'
def trace(a,b):return unreal.SystemLibrary.line_trace_single(world,unreal.Vector(*a),unreal.Vector(*b),unreal.TraceTypeQuery.ECC_VISIBILITY,False,[],unreal.DrawDebugTrace.NONE,True)
glass=[]
for direction in [-1,1]:
    h=trace([2360,1500+150*direction,172],[2360,1500-150*direction,172]);assert h and h.to_dict()['hit_component']==nc['ClearGlass'];glass.append(xyz(h.to_dict()['impact_point']))
for x,z in [(2290,172),(2350,112),(2350,262)]:
    h=trace([x,1650,z],[x,1350,z]);assert h and h.to_dict()['hit_component']==nc['WallCore']
textures={}
for family in ['Ivory','CarvedStone','RecessStone','Gold','Azure','ClearGlass']:
    for channel in ['BaseColor','Roughness','Normal']:
        if family=='ClearGlass' and channel=='BaseColor':continue
        p='/Game/Art/Textures/HighElfWallStudy02/T_HE02_'+family+'_'+channel;t=unreal.load_asset(p);assert t
        srgb=t.get_editor_property('srgb');assert srgb==(channel=='BaseColor')
        if channel=='Normal':assert t.get_editor_property('flip_green_channel')
        textures[p]=dict(srgb=srgb,compression=str(t.get_editor_property('compression_settings')))
proof=dict(status='passed',existing_actors_preserved=len(base['actors']),components=components,glass_hit_points_cm=glass,visible_window_geometry_present=True,geometry_and_collision_reused=True,independent_material_overrides=True,textures=textures)
(ROOT/'Evidence/unreal_verification.json').write_text(json.dumps(proof,indent=2)+'\n');unreal.log('HE02_VERIFY_PASSED')
