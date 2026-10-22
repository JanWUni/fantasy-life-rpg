"""Read the committed Blender scene; write assembly evidence without saving it."""
from pathlib import Path
import json
import bpy

ROOT = Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT.parent/'EH_HouseB01_Study.blend'))
scenes = {}
for name in ('House_10x12', 'House_10x16_Variation'):
    scene = bpy.data.scenes[name]
    items = []
    for obj in scene.objects:
        if obj.type != 'MESH':
            continue
        item = {'label': obj.name, 'module': obj.get('SourceModule'),
                'location_cm': [100*obj.location.x, -100*obj.location.y, 100*obj.location.z],
                'yaw_deg': -obj.rotation_euler.z*180/3.141592653589793,
                'scale': list(obj.scale)}
        if not item['module']:
            # Presentation steps are boxes; retain their true world bounds as test props.
            points = [obj.matrix_world@v.co for v in obj.data.vertices]
            item['bounds_blender_m'] = [[min(v[k] for v in points) for k in range(3)],
                                        [max(v[k] for v in points) for k in range(3)]]
            item['material'] = obj.data.materials[0].name
        items.append(item)
    scenes[name] = items
(ROOT/'assembly.json').write_text(json.dumps(scenes, indent=2)+'\n', encoding='utf-8')
print('ASSEMBLY_EXTRACTED', {k:len(v) for k,v in scenes.items()})
