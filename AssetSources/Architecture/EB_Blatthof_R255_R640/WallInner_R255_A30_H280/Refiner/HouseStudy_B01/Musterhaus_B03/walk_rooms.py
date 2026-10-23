"""Temporary PIE fixture: real CharacterMovement input along room routes; no teleport or NoClip."""
from pathlib import Path
import json,time,math,unreal
ROOT=Path(__file__).resolve().parent
assert Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).resolve()==Path('E:/Business/fantasy-rpg-refiner')
world=unreal.EditorLevelLibrary.get_game_world();assert world and world.get_path_name().startswith('/Game/Prototype/Maps/UEDPIE_')
player=unreal.GameplayStatics.get_player_character(world,0);controller=player.get_controller()
capsule=player.get_component_by_class(unreal.CapsuleComponent)
radius=capsule.get_scaled_capsule_radius();half=capsule.get_scaled_capsule_half_height()
assert radius==35 and half==90
movement=player.get_component_by_class(unreal.CharacterMovementComponent)
interaction=next(c for c in player.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name()=='InteractionComponent')
door=interaction.find_best_target();assert door and door.get_class().get_name()=='BP_EH_ReviewDoor_C'
states=[]
for expected in [True,False,True]:
    assert interaction.try_interact();states.append(door.get_editor_property('bIsOpen'));assert states[-1]==expected
(ROOT/'Evidence/pie_interaction.json').write_text(json.dumps(dict(status='passed',open_close_open=states,
    method='Existing UInteractionComponent.TryInteract, including range, visibility and authority checks',
    actual_e_input='Synthetic Slate E did not reach gameplay reliably; physical keyboard check remains manual'),indent=2)+'\n')
targets=[(-1900,-2000),(-1900,-2480),(-2076,-2530),(-2076,-2760),(-2076,-2530),(-1676,-2530),(-1676,-2840),(-1676,-2530),(-1900,-2480),(-1900,-2000),(-1900,-1780)]
state=dict(index=0,started=time.monotonic(),leg_started=time.monotonic(),visited=[],samples=[],status='running')
def xyz(v):return [v.x,v.y,v.z]
def finish(status,reason=None):
    unreal.unregister_slate_post_tick_callback(handle)
    movement.stop_movement_immediately();state['status']=status;state['reason']=reason
    state['duration_seconds']=time.monotonic()-state['started'];state['capsule_cm']=[radius,half]
    state['method']='Character.add_movement_input into existing CharacterMovement, collision enabled; no in-route teleport'
    state['after']=xyz(player.get_actor_location());state['movement_mode']=str(movement.get_editor_property('movement_mode'))
    (ROOT/'Evidence/pie_room_walk.json').write_text(json.dumps(state,indent=2)+'\n')
    unreal.log('B03_ROOM_WALK_'+status.upper())
def tick(dt):
    if not unreal.SystemLibrary.is_valid(player):finish('failed','Player destroyed');return
    current=player.get_actor_location();x,y=targets[state['index']];delta=unreal.Vector(x-current.x,y-current.y,0);dist=delta.length()
    if len(state['samples'])==0 or time.monotonic()-state['samples'][-1]['time']>.4:
        state['samples'].append(dict(time=time.monotonic(),position=xyz(current)))
    if current.z<80 or current.z>155:finish('failed','Unexpected floor height');return
    if dist<28:
        state['visited'].append(dict(target=[x,y],actual=xyz(current)));state['index']+=1;state['leg_started']=time.monotonic()
        if state['index']==len(targets):finish('passed');return
    else:
        if time.monotonic()-state['leg_started']>14:finish('failed','Waypoint timeout '+str(state['index']));return
        direction=delta/dist
        controller.set_control_rotation(unreal.Rotator(0,math.degrees(math.atan2(direction.y,direction.x)),0))
        player.add_movement_input(direction,min(.65,dist/110))
handle=unreal.register_slate_post_tick_callback(tick)
unreal.log('B03_ROOM_WALK_STARTED')
