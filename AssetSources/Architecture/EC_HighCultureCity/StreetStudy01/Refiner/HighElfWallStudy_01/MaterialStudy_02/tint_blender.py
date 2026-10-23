from pathlib import Path
import bpy,json,hashlib
root=Path(__file__).resolve().parent;p=root/'HighElf_MaterialComparison_02.blend'
bpy.ops.wm.open_mainfile(filepath=str(p))
bpy.data.materials['HE02_ClearGlass'].node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.78,.89,.94,1)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(p))
m=json.loads((root/'manifest.json').read_text());m['source_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();m['glass'].update(transmittance=[.78,.89,.94],unreal_refraction='PixelNormalOffset 1.06',unreal_screen_space_reflections=True,blender_IOR=1.52)
(root/'manifest.json').write_text(json.dumps(m,indent=2)+'\n',encoding='utf8')
