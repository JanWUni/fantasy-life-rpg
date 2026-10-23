"""Read native window data, test aperture/glazing collision, and preserve original Lab actors."""
from pathlib import Path
import json
import unreal
ROOT=Path(__file__).resolve().parent
REPO=Path('E:/Business/fantasy-rpg-refiner')
assert Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).resolve()==REPO
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name().startswith('/Game/Prototype/Maps/Lvl_AssetLab.')
manifest=json.loads((ROOT/'manifest.json').read_text())
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
by_path={a.get_path_name():a for a in actors}
before=json.loads((REPO/'Saved/HouseB02/lab_before.json').read_text())['actors']
def xyz(v):return [v.x,v.y,v.z]
unchanged=[]
for original in before:
    a=by_path[original['path']]
    assert xyz(a.get_actor_location())==original['position'],original['label']
    r=a.get_actor_rotation();assert [r.pitch,r.yaw,r.roll]==original['rotation']
    assert xyz(a.get_actor_scale3d())==original['scale']
    assert str(a.get_folder_path())==original['folder']
    meshes=[dict(path=c.get_path_name(),mesh=c.static_mesh.get_path_name() if c.static_mesh else None,
        overrides=[m.get_path_name() if m else None for m in c.get_editor_property('override_materials')])
        for c in a.get_components_by_class(unreal.StaticMeshComponent)]
    assert meshes==original['meshes'],original['label']
    unchanged.append(original['label'])
smes=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);meshes={}
for name,info in manifest['assets'].items():
    mesh=unreal.load_asset('/Game/Art/Architecture/ElvenHouseB01/Windows/Meshes/'+name)
    box=mesh.get_bounding_box();actual=[xyz(box.min),xyz(box.max)]
    lo,hi=info['bounds_m'];expected=[[lo[0]*100,-hi[1]*100,lo[2]*100],[hi[0]*100,-lo[1]*100,hi[2]*100]]
    error=max(abs(actual[i][j]-expected[i][j]) for i in range(2) for j in range(3));assert error<.001
    assert smes.get_convex_collision_count(mesh)==info['ucx_hulls']
    assert mesh.get_num_triangles(0)==info['triangles']
    assert mesh.get_editor_property('asset_import_data').get_class().get_name()=='FbxStaticMeshImportData'
    slots=[str(m.material_slot_name) for m in mesh.static_materials];assert slots==info['slots']
    meshes[name]=dict(bounds_cm=actual,bounds_error_cm=error,hulls=smes.get_convex_collision_count(mesh),
        triangles=mesh.get_num_triangles(0),slots=slots,uv_channels=smes.get_num_uv_channels(mesh,0))
    data=mesh.get_editor_property('asset_import_data')
    meshes[name]['import_options']={key:str(data.get_editor_property(key)) for key in (
        'import_uniform_scale','convert_scene','convert_scene_unit','force_front_x_axis',
        'auto_generate_collision','one_convex_hull_per_ucx','generate_lightmap_u_vs',
        'normal_import_method','normal_generation_method')}
windows=[a for a in actors if a.get_class().get_name()=='BP_EH_Window_Arch_100x173_C']
assert len(windows)==22,len(windows)
window_checks=[]
for a in windows:
    assert xyz(a.get_actor_scale3d())==[1,1,1]
    components=a.get_components_by_class(unreal.StaticMeshComponent);assert len(components)==2
    for c in components:
        assert xyz(c.get_editor_property('relative_scale3d'))==[1,1,1]
        is_glass='WindowGlass' in c.static_mesh.get_name()
        assert c.get_editor_property('cast_shadow')==(not is_glass)
        assert c.is_visible()
        if is_glass:assert c.static_mesh.static_materials[0].material_interface.get_name()=='M_EH_Glass_Clear'
    # Local X/Y basis maps the same physical aperture in all four wall orientations.
    origin=a.get_actor_location();x=a.get_actor_forward_vector();y=a.get_actor_right_vector()
    start=origin+x*-25+y*120+unreal.Vector(0,0,90)
    end=origin+x*-25+y*-200+unreal.Vector(0,0,90)
    args=(unreal.TraceTypeQuery.ECC_VISIBILITY,False)
    pane=unreal.SystemLibrary.line_trace_single(world,start,end,*args,[],unreal.DrawDebugTrace.NONE,True)
    hole=unreal.SystemLibrary.line_trace_single(world,start,end,*args,[a],unreal.DrawDebugTrace.NONE,True)
    assert pane is not None,a.get_actor_label()
    assert hole is None,(a.get_actor_label(),'Wall ring obstructs aperture')
    window_checks.append(dict(label=a.get_actor_label(),window_blocks_player_rays=True,wall_opening_clear_when_window_ignored=True))
new_actors=[a for a in actors if a.get_actor_label().startswith('Lab_EH_B02_')]
assert len(new_actors)==198,len(new_actors)
sun=next(a for a in actors if isinstance(a,unreal.DirectionalLight))
result=dict(status='passed',original_actors_preserved=len(unchanged),new_house_actors=len(new_actors),
    windows=len(windows),meshes=meshes,aperture_tests=window_checks,
    lab_sun_direction=xyz(sun.get_actor_forward_vector()),
    lab_sun_intensity=sun.get_component_by_class(unreal.DirectionalLightComponent).get_editor_property('intensity'),
    material=dict(blend=str(unreal.load_asset('/Game/Art/Materials/ElvenHouseB01/M_EH_Glass_Clear').get_editor_property('blend_mode'))))
(ROOT/'Evidence/lab_verification.json').write_text(json.dumps(result,indent=2)+'\n')
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_set_game_view(True)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_set_viewport_realtime(True)
unreal.log('HOUSE_B02_LAB_VERIFICATION_PASSED')
