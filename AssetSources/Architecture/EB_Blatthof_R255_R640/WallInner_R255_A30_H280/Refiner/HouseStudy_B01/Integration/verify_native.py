"""Read native UE data and probe simple line/capsule collision in the own review world.

The test temporarily opens only a study door and restores its transform in finally.
It does not pretend this editor-world probe is a gameplay/input test.
"""
from pathlib import Path
import hashlib
import json
import unreal

ROOT=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).resolve()
assert ROOT==Path('E:/Business/fantasy-rpg-refiner')
SOURCE=ROOT/'AssetSources/Architecture/EB_Blatthof_R255_R640/WallInner_R255_A30_H280/Refiner/HouseStudy_B01'
OUT=ROOT/'Saved/HouseB01Integration'
BASE='/Game/Art/Architecture/ElvenHouseB01'
MAP=BASE+'/Maps/Lvl_ElvenHouseB01_Review'
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name()==MAP+'.'+MAP.rsplit('/',1)[-1]
manifest=json.loads((SOURCE/'manifest.json').read_text())
source=json.loads((SOURCE/'verification.json').read_text())['source']
def xyz(v):
    return [v.x,v.y,v.z]
meshes={}
smes=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
for item in manifest['assets']:
    name=item['name'];mesh=unreal.load_asset(BASE+'/Meshes/'+name)
    box=mesh.get_bounding_box()
    actual=[xyz(box.min),xyz(box.max)]
    lo,hi=source[name]['bounds_m']
    expected=[[100*lo[0],-100*hi[1],100*lo[2]],[100*hi[0],-100*lo[1],100*hi[2]]]
    error=max(abs(actual[i][j]-expected[i][j]) for i in (0,1) for j in range(3))
    assert error<.001,(name,error)
    slots=[str(x.material_slot_name) for x in mesh.static_materials]
    assert slots==item['slots'],(name,slots)
    assert [x.material_interface.get_path_name() for x in mesh.static_materials]==[
        '/Game/Art/Materials/ElvenHouseB01/M_EH_'+s+'.M_EH_'+s for s in slots]
    assert mesh.get_editor_property('asset_import_data').get_class().get_name()=='FbxStaticMeshImportData'
    meshes[name]={'bounds_cm':actual,'source_bounds_max_error_cm':error,
                  'triangles':mesh.get_num_triangles(0),'uv_channels':smes.get_num_uv_channels(mesh,0),
                  'slots':slots,'simple_collision_count':smes.get_simple_collision_count(mesh),
                  'convex_collision_count':smes.get_convex_collision_count(mesh)}
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
doors=[a for a in actors if a.get_class().get_name()=='BP_EH_ReviewDoor_C']
assert len(doors)==2
module_actors=[]
for a in actors:
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        mesh=c.static_mesh
        if mesh and mesh.get_path_name().startswith(BASE+'/Meshes/'):
            scale=a.get_actor_scale3d()
            assert max(abs(t-1) for t in xyz(scale))<1e-6,a.get_actor_label()
            assert max(abs(t-1) for t in xyz(c.get_editor_property('relative_scale3d')))<1e-6
            module_actors.append(a.get_actor_label())
assert len(module_actors)==168,len(module_actors)
character=unreal.get_default_object(unreal.load_class(None,'/Game/Prototype/Blueprints/BP_PrototypeCharacter.BP_PrototypeCharacter_C'))
capsule=character.get_component_by_class(unreal.CapsuleComponent)
radius=capsule.get_scaled_capsule_radius();half_height=capsule.get_scaled_capsule_half_height()


def trace(start,end,capsule=False):
    common=(world,unreal.Vector(*start),unreal.Vector(*end))
    tail=(unreal.TraceTypeQuery.ECC_VISIBILITY,False,[],unreal.DrawDebugTrace.NONE,True)
    hit=(unreal.SystemLibrary.capsule_trace_single(*common,radius,half_height,*tail) if capsule
         else unreal.SystemLibrary.line_trace_single(*common,*tail))
    if not hit:
        return None
    return {k:xyz(hit.to_dict()[k]) for k in ('location','impact_point','normal')}


tests={}
for offset,length in [(0,1200),(1800,1600)]:
    prefix=str(length)+'_'
    for name,x,y in [('floor_A',199.99,-100),('floor_B',200.01,-100),('floor_center',500,-length/2)]:
        hit=trace((offset+x,y,200),(offset+x,y,-20))
        assert hit and abs(hit['location'][2]-31)<.05,(name,hit)
        tests[prefix+name]=hit
    tests[prefix+'closed_door']=trace((offset+500,180,122),(offset+500,-220,122),True)
    assert tests[prefix+'closed_door'] is not None
    door=min(doors,key=lambda a:abs(a.get_actor_location().x-(offset+434)))
    closed=door.get_actor_rotation()
    try:
        door.set_actor_rotation(unreal.Rotator(0,closed.yaw-90,0),False)
        tests[prefix+'open_door']=trace((offset+500,180,122),(offset+500,-220,122),True)
        assert tests[prefix+'open_door'] is None,tests[prefix+'open_door']
    finally:
        door.set_actor_rotation(closed,False)
    for name,start,end in [
        ('front_wall',(offset+100,100,181),(offset+100,-100,181)),
        ('rear_wall',(offset+500,-length+100,181),(offset+500,-length-100,181)),
        ('roof_A',(offset+300,-199.99,1000),(offset+300,-199.99,250)),
        ('roof_B',(offset+300,-200.01,1000),(offset+300,-200.01,250))]:
        tests[prefix+name]=trace(start,end)
        assert tests[prefix+name] is not None,(name,offset)
    assert abs(tests[prefix+'roof_A']['location'][2]-tests[prefix+'roof_B']['location'][2])<.1
normal_maps={}
for family in ('Plaster','Timber','Stone','Jade'):
    texture=unreal.load_asset('/Game/Art/Textures/ElvenHouseB01/T_EH_'+family+'_Normal')
    normal_maps[family]={'flip_green':texture.get_editor_property('flip_green_channel'),
                         'srgb':texture.get_editor_property('srgb'),
                         'compression':str(texture.get_editor_property('compression_settings'))}
    assert normal_maps[family]['flip_green'] and not normal_maps[family]['srgb']
result={'status':'passed','project':str(ROOT),'map':MAP,'meshes':meshes,
        'module_instances':len(module_actors),'functional_door_instances':2,
        'capsule_cm':{'radius':radius,'half_height':half_height},
        'trace_complex':False,'collision_tests':tests,'normal_maps':normal_maps,
        'source_sha256':hashlib.sha256((SOURCE/'EH_HouseB01_Study.blend').read_bytes()).hexdigest(),
        'scope':'Editor world probes; actual PIE interaction and movement are separate checks'}
(OUT/'native_verification.json').write_text(json.dumps(result,indent=2)+'\n')
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_set_game_view(True)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_set_viewport_realtime(True)
unreal.log('HOUSE_B01_NATIVE_VERIFICATION_PASSED')
