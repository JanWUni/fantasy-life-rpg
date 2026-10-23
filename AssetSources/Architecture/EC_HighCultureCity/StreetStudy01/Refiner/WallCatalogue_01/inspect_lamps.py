from pathlib import Path
import json,unreal
ROOT=Path(__file__).resolve().parent
lights=[]
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if a.get_actor_label().startswith('Lab_WC01_'):
        for c in a.get_components_by_class(unreal.PointLightComponent):lights.append(dict(actor=a.get_actor_label(),path=c.get_path_name(),intensity=c.intensity,temperature=c.temperature,radius=c.attenuation_radius))
bp=unreal.load_asset('/Game/Art/Furniture/WallCatalogue01/Blueprints/BP_WC01_WallLamp')
cdo=unreal.get_default_object(bp.generated_class())
for c in cdo.get_components_by_class(unreal.PointLightComponent):lights.append(dict(actor='CDO',path=c.get_path_name(),intensity=c.intensity,temperature=c.temperature,radius=c.attenuation_radius))
(ROOT/'Evidence/lamp_inspection.json').write_text(json.dumps(lights,indent=2)+'\n')
