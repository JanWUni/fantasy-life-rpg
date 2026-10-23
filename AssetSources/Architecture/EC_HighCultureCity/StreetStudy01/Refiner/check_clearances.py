"""Additional actual wall-opening and level-floor probes, no source writes."""
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
    results=[t.ray_cast(a,d.normalized(),d.length) for t in trees]
    results=[r for r in results if r[0] is not None]
    return min(results,key=lambda r:r[3]) if results else None
windows=[]
for name,centers in [('SM_EC_Facade_700x390',[-2.2,2.2]),('SM_EC_RearWall_700x390',[-2.2,2.2]),('SM_EC_SideWall_800x390',[-2,2])]:
    obj=bpy.data.objects[name];render=[bvh(obj)]
    ucx=[bvh(obj,o) for o in bpy.data.collections['01_UCX_Source'].objects if o.name.startswith('UCX_'+name+'_')]
    count=0
    for center in centers:
        for i in range(7):
            for j in range(7):
                x=center-.315+i*.63/6;z=1.26+j*.78/6
                assert hit(render,(x,-.2,z),(x,.55,z)) is None,(name,x,z,'render')
                assert hit(ucx,(x,-.2,z),(x,.55,z)) is None,(name,x,z,'UCX');count+=1
        assert hit(render,(center,-.2,1.0),(center,.55,1.0)) is not None
        assert hit(render,(center,-.2,2.2),(center,.55,2.2)) is not None
    windows.append(dict(asset=name,openings=2,clear_rays_each_representation=count,below_and_above_solid=True))
structure=[o for o in bpy.data.collections['10_Structure'].objects if o.type=='MESH']
render=[bvh(o) for o in structure];ucx=[]
for o in structure:
    ucx.extend(bvh(o,c) for c in bpy.data.collections['01_UCX_Source'].objects if c.name.startswith('UCX_'+o['library_asset']+'_'))
floors=[]
for check in m['interior_test_contracts']:
    yaw=math.radians(check['yaw']);cx,cy,cz=check['center'];samples=[]
    for x,y in [(-3,-3),(3,-3),(-3,3),(3,3),(0,0)]:
        wx=cx+x*math.cos(yaw)-y*math.sin(yaw);wy=cy+x*math.sin(yaw)+y*math.cos(yaw)
        actual=[]
        for trees in [render,ucx]:
            result=hit(trees,(wx,wy,1),(wx,wy,-.5));assert result
            assert abs(result[0].z)<1e-5,(check['name'],result[0].z);actual.append(result[0].z)
        samples.append(dict(local_xy=[x,y],render_and_ucx_z_m=actual))
    floors.append(dict(house=check['name'],samples=samples))
(ROOT/'Evidence/openings_and_floor.json').write_text(json.dumps(dict(status='passed',windows=windows,floors=floors,
    scope='Actual structural Render/UCX samples. Frame/glass are separate visual parts; no capsule or Unreal test.'),indent=2)+'\n')
print('WINDOWS_AND_FLOOR_PASSED')
