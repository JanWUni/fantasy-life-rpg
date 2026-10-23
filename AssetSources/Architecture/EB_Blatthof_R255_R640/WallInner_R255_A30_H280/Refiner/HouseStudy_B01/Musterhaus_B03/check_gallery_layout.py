"""Offline size check before filling the existing Lab's free western area."""
from pathlib import Path
import bpy,json
ROOT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'EH_Musterhaus_B03.blend'))
names=set(json.loads((ROOT/'manifest.json').read_text())['assets'])
for o in bpy.data.scenes['Module_Library'].objects:
    if o.type=='MESH' and not o.name.startswith('UCX_'):names.add(o.name)
names.discard('SM_EH_Wall_Window_200x24x320')
items=[]
for n in names:
    o=bpy.data.objects[n];dims=[100*(max(v.co[k] for v in o.data.vertices)-min(v.co[k] for v in o.data.vertices)) for k in range(3)]
    items.append(dict(module=n,width=dims[0],depth=dims[1]))
items.sort(key=lambda e:-e['width']);x=-5800;y=-850;row_depth=0;placements=[]
for e in items:
    width=max(e['width'],140)+100;depth=max(e['depth'],130)+130
    if x+width>-2860:x=-5800;y-=row_depth;row_depth=0
    assert y-depth>-3950,(e['module'],y,depth)
    placements.append(dict(module=e['module'],bay_cm=[x,y,width,depth]));x+=width;row_depth=max(row_depth,depth)
(ROOT/'Evidence/gallery_space_check.json').write_text(json.dumps(dict(status='passed',count=len(items),south_edge=y-row_depth,placements=placements),indent=2)+'\n')
print('GALLERY_FITS',len(items),y-row_depth)
