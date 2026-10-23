"""Read live game state; do not claim manual input or walk tests."""
from pathlib import Path
import json,unreal
ROOT=Path(__file__).resolve().parent
assert Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).resolve()==ROOT.parents[5]
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();assert world
pawn=unreal.GameplayStatics.get_player_pawn(world,0);assert pawn
actors=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Actor)
counts={}
for tag in ['A','B']:
    a=next(a for a in actors if a.get_actor_label()=='Lab_Study'+tag+'_ClearGlass')
    counts[tag]=sum(c.get_instance_count() for c in a.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent))
assert counts==dict(A=470,B=318),counts
v=pawn.get_actor_location();cap=pawn.get_component_by_class(unreal.CapsuleComponent)
data=dict(status='passed',world=world.get_path_name(),player_class=pawn.get_class().get_name(),player_position_cm=[v.x,v.y,v.z],
    capsule_radius_cm=cap.get_scaled_capsule_radius(),capsule_half_height_cm=cap.get_scaled_capsule_half_height(),
    game_world_time_seconds=unreal.GameplayStatics.get_time_seconds(world),studies_present=counts,
    scope='Actual existing player and both assemblies present in PIE; no physical keyboard walk claimed')
(ROOT/'Evidence/pie_live.json').write_text(json.dumps(data,indent=2)+'\n')
unreal.log('STUDY_AB_LIVE_PIE_READY')
