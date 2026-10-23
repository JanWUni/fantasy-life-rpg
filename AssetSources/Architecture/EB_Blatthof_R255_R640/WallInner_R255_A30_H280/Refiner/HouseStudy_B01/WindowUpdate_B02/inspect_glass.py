from pathlib import Path
import json,unreal
ROOT=Path(__file__).resolve().parent
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
a=next(a for a in actors if a.get_actor_label()=='Lab_EH_B02_House_10x12_1_Window')
out=[]
for c in a.get_components_by_class(unreal.StaticMeshComponent):
    out.append(dict(name=c.get_name(),mesh=c.static_mesh.get_path_name(),
        material=c.get_material(0).get_path_name(),overrides=[m.get_path_name() if m else None for m in c.get_editor_property('override_materials')],
        world=str(c.get_world_location()),scale=str(c.get_world_scale()),rotation=str(c.get_world_rotation())))
mat=unreal.load_asset('/Game/Art/Materials/ElvenHouseB01/M_EH_Glass_Clear')
data=dict(components=out,substrate=unreal.SystemLibrary.get_console_variable_int_value('r.Substrate'),
    blend=str(mat.get_editor_property('blend_mode')),model=str(mat.get_editor_property('shading_model')),
    front=str(unreal.MaterialEditingLibrary.get_material_property_input_node(mat,unreal.MaterialProperty.MP_FRONT_MATERIAL)))
(ROOT/'Evidence/inspect_glass.json').write_text(json.dumps(data,indent=2)+'\n')
unreal.log(str(data))
