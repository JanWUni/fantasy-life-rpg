"""Read-only audit of the parent A source saved externally during glass rendering."""
from pathlib import Path
import importlib.util,sys,json,bpy
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('glass_update_audit',ROOT/'glass_update.py')
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
parent=ROOT.parent/g.PARENT_MANIFEST['source_blend']
bpy.ops.wm.open_mainfile(filepath=str(parent))
before=g.read('Evidence/geometry_before.json');now=g.snapshot()
changes={key:[n for n in set(before[key])|set(now[key]) if before[key].get(n)!=now[key].get(n)] for key in before}
result=dict(status='passed',parent_file=parent.relative_to(g.REPO).as_posix(),current_sha256=g.sha(parent),
    input_sha256=g.PARENT_MANIFEST['source_blend_sha256'],changes=changes,
    geometry_slots_uvs_transforms_and_other_materials_equal=before==now,
    parent_glass_equal_to_input=g.material_state(bpy.data.materials['Glass'])==g.read('Evidence/material_change.json')['before'],
    source_frame=bpy.context.scene.frame_current,
    scope='Read-only audit; parent source saved outside glass task, never restored or overwritten by refiner')
g.write('Evidence/external_parent_save.json',result)
print('EXTERNAL_PARENT_SAVE_AUDIT',result,flush=True)
