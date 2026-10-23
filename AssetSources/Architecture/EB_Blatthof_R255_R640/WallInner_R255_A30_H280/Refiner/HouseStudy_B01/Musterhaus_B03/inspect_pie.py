from pathlib import Path
import json,unreal
ROOT=Path(__file__).resolve().parent
world=unreal.EditorLevelLibrary.get_game_world();player=unreal.GameplayStatics.get_player_character(world,0)
def xyz(v):return [v.x,v.y,v.z]
controller=player.get_controller();rot=controller.get_control_rotation()
doors=[a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Actor) if a.get_class().get_name()=='BP_EH_ReviewDoor_C']
data=dict(player_position=xyz(player.get_actor_location()),control_rotation=[rot.pitch,rot.yaw,rot.roll],
    actor_forward=xyz(player.get_actor_forward_vector()),doors=[dict(position=xyz(a.get_actor_location()),open=a.get_editor_property('bIsOpen')) for a in doors])
data['player_class']=player.get_class().get_name();data['controller_class']=controller.get_class().get_name()
data['components']=[c.get_class().get_name() for c in player.get_components_by_class(unreal.ActorComponent)]
for comp in player.get_components_by_class(unreal.ActorComponent):
    if comp.get_class().get_name()=='InteractionComponent':
        best=comp.find_best_target();data['interaction_target']=best.get_path_name() if best else None
data['ignore_move']=controller.is_move_input_ignored();data['ignore_look']=controller.is_look_input_ignored()
data['paused']=unreal.GameplayStatics.is_game_paused(world);data['world_seconds']=unreal.GameplayStatics.get_time_seconds(world)
movement=player.get_component_by_class(unreal.CharacterMovementComponent)
data['movement_tick_enabled']=movement.is_component_tick_enabled();data['movement_active']=movement.is_active();data['locally_controlled']=player.is_locally_controlled()
data['movement_pending']=xyz(player.get_pending_movement_input_vector());data['velocity']=xyz(movement.velocity)
data['global_time_dilation']=unreal.GameplayStatics.get_global_time_dilation(world)
data['world_class']=world.get_class().get_name();data['world_path']=world.get_path_name()
(ROOT/'Evidence/pie_inspect.json').write_text(json.dumps(data,indent=2)+'\n');unreal.log('B03_PIE_INSPECTED')
