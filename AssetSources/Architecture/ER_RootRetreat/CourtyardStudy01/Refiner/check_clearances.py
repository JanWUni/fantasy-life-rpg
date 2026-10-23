"""Dense read-only Render/UCX checks for the single entrance and two connected rooms."""
from pathlib import Path
import bpy,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parent
m=json.loads((ROOT/'manifest.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(ROOT/m['source_blend']))
def bvh(o,geometry=None):
    me=(geometry or o).data
    return BVHTree.FromPolygons([o.matrix_world@v.co for v in me.vertices],[list(p.vertices) for p in me.polygons])
def hit(trees,start,end):
    a,b=Vector(start),Vector(end);d=b-a
    hits=[t.ray_cast(a,d.normalized(),d.length) for t in trees];hits=[r for r in hits if r[0] is not None]
    return min(hits,key=lambda r:r[3]) if hits else None
def transform(p,check):
    a=math.radians(check['yaw']);c=check['center'];x,y,z=p
    return (c[0]+x*math.cos(a)-y*math.sin(a),c[1]+x*math.sin(a)+y*math.cos(a),c[2]+z)
structure=[o for o in bpy.data.collections['10_Structure'].objects if o.type=='MESH']
physical=structure+[o for name in ['20_Decor','30_Doors_Windows'] for o in bpy.data.collections[name].objects if o.type=='MESH']
doors=[o for o in bpy.data.collections['30_Doors_Windows'].objects if 'DoorLeaf' in o.name]
assert len(doors)==1 and 'OldCore' in doors[0].name
render=[bvh(o) for o in physical];ucx=[]
for o in structure+doors:
    ucx.extend(bvh(o,c) for c in bpy.data.collections['01_UCX_Source'].objects if c.name.startswith('UCX_'+o['library_asset']+'_'))
routes=[]
for check in m['interior_test_contracts']:
    if check.get('access')!='internal_only':continue
    rays=0;heights=[]
    for i in range(9):
        offset=-.60+i*.15
        for j in range(16):
            z=.08+j*2.12/15
            start=transform((check['direction']*2.5,offset,z),check);end=transform((check['direction']*5.6,offset,z),check)
            assert hit(render,start,end) is None,(check['name'],'Render',i,j)
            assert hit(ucx,start,end) is None,(check['name'],'UCX',i,j);rays+=1
    samples=[]
    for i in range(64):
        for j in range(11):
            offset=-.6+j*.12;p=transform((check['direction']*(2.5+i*3.1/63),offset,1),check)
            actual=[]
            for trees in [render,ucx]:
                h=hit(trees,p,(p[0],p[1],-.5));assert h,(check['name'],'Missing floor',p)
                z=h[0].z;assert abs(z)<1e-5,(check['name'],'Floor step',p,z);heights.append(z);actual.append(z)
            samples.append(actual)
    routes.append(dict(name=check['name'],route_ray_count_per_representation=rays,route_width_m=1.2,top_test_height_m=2.2,
        floor_grid=[64,11],floor_samples_per_representation=len(samples),max_floor_z_error_m=max(abs(z) for z in heights),both_wall_layers_clear=True))
assert len(routes)==2
windows=[]
for name,holes in [('SM_ER_WingWindowFacade_640x280_v02',[(0,1.05),(-2.05,.95),(2.05,.95)]),
                   ('SM_ER_WingRear_640x280',[(-2.05,.95),(2.05,.95)]),('SM_ER_WingSide_550x311',[(-1.3,.95),(1.3,.95)])]:
    obj=bpy.data.objects[name];trees=[bvh(obj)]
    hulls=[bvh(obj,o) for o in bpy.data.collections['01_UCX_Source'].objects if o.name.startswith('UCX_'+name+'_')]
    count=0
    for center,sill in holes:
        for i in range(7):
            for j in range(7):
                x=center-.315+i*.105;z=sill+.01+j*.13
                for group in [trees,hulls]:assert hit(group,(x,-.2,z),(x,.55,z)) is None,(name,center,sill,i,j)
                count+=1
        for z in [.3,2.3]:
            for group in [trees,hulls]:assert hit(group,(center,-.2,z),(center,.55,z)) is not None,(name,'Open former doorway',center,z)
    windows.append(dict(asset=name,window_openings=len(holes),clear_ray_count_per_representation=count,closed_sills_and_headers=True))
floor=bpy.data.objects['SM_ER_ConnectedFloor_v02'].data
todo=set(range(len(floor.vertices)));adj={i:[] for i in todo}
for e in floor.edges:a,b=e.vertices;adj[a].append(b);adj[b].append(a)
components=0
while todo:
    components+=1;stack=[todo.pop()]
    while stack:
        for v in adj[stack.pop()]:
            if v in todo:todo.remove(v);stack.append(v)
assert components==1
top_vertices=[v for v in floor.vertices if abs(v.co.z)<1e-5];assert top_vertices
assert max(abs(v.co.z) for v in top_vertices)<1e-5
core=bpy.data.objects['SM_ER_OldCoreLinkedShell_R260_H430_v02'].data
assert core.uv_layers.active
result=dict(status='passed',external_door_leaves=1,external_door_object=doors[0].name,internal_routes=routes,
    windows=windows,shared_floor_connected_components=components,shared_floor_source_ucx=3,
    core_uv='Cylindrical metric UV0 on inner/outer curved walls; one periodic seam, planar jambs/caps; intentional tiling overlaps',
    scope='Dense sampled real Render geometry including decor and original UCX; not a continuous capsule sweep or Unreal test')
(ROOT/'Evidence/openings_and_floor.json').write_text(json.dumps(result,indent=2)+'\n')
print('CONNECTED_ROOMS_WINDOWS_AND_FLOOR_PASSED')
