"""Refresh exactly the two corrected FBXs from the saved Refiner source."""
from pathlib import Path
import importlib.util,sys,bpy
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('refiner',ROOT/'refine_study.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
m=r.manifest();assert m['interior_root_cleanup'] and r.sha(ROOT/m['source_blend'])==m['source_blend_sha256']
bpy.ops.wm.open_mainfile(filepath=str(ROOT/m['source_blend']))
bpy.ops.preferences.addon_enable(module='io_scene_fbx')
settings=m['export_settings'].copy();settings['object_types']=set(settings['object_types'])
for entry in m['exports']:
    if entry['asset_name'] not in m['interior_root_cleanup']['changed_decor_assets']:continue
    obj=bpy.data.objects[entry['asset_name']];bpy.ops.object.select_all(action='DESELECT');obj.hide_set(False);obj.select_set(True);bpy.context.view_layer.objects.active=obj
    bpy.ops.export_scene.fbx(filepath=str(ROOT/entry['path']),**settings)
    entry['sha256']=r.sha(ROOT/entry['path']);entry['source_stats']=r.assert_clean(obj)
r.write('manifest.json',m)
print('CORRECTED_ROOT_EXPORTS_REFRESHED')
