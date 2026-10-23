"""Trim two decorative root groups behind the existing core's interior wall.

Run after refine_study.py prepare, before verify/render/finalize. Source, pivots,
instances, collision and exterior geometry are explicitly checked. No Unreal API.
"""
from pathlib import Path
import hashlib, importlib.util, json, math, sys
sys.dont_write_bytecode = True
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('refiner', ROOT/'refine_study.py')
r = importlib.util.module_from_spec(spec); spec.loader.exec_module(r)
m = r.manifest()
assert m['status'] in ['review_ready', 'refiner_active']
assert r.sha(ROOT/m['source_blend']) == m['source_blend_sha256']
assert not m.get('interior_root_cleanup'), 'Cleanup already applied'
bpy.ops.wm.open_mainfile(filepath=str(ROOT/m['source_blend']))
prior_sha = m['source_blend_sha256']
proof = {}

for label, center in [('OldButtressRoots', (0,0,0)), ('LinkingRootArches', (0,3,0))]:
    obj = bpy.data.objects['SM_ER_'+label]
    assert not next(e for e in m['exports'] if e['asset_name']==obj.name)['collision_names']
    old = obj.data
    users = [o for o in bpy.data.objects if o.type=='MESH' and o.data==old]
    before = r.assert_clean(obj)
    radius, count = 2.24, 40  # Existing inner radius 2.20, outer radius 2.60 m.
    points = [Vector((center[0]+radius*math.sin(math.radians(-180+i*9)),
                      center[1]-radius*math.cos(math.radians(-180+i*9)), z))
              for z in [-.1,4.3] for i in range(count)]
    faces = [tuple(reversed(range(count))), tuple(count+i for i in range(count))]
    faces += [(i,(i+1)%count,count+(i+1)%count,count+i) for i in range(count)]
    mesh = bpy.data.meshes.new('ReviewTrimOperand'); mesh.from_pydata(points,[],faces); mesh.update()
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
    operand=bpy.data.objects.new('ReviewTrimOperand',mesh);bpy.context.scene.collection.objects.link(operand)
    # Process disconnected tubes separately, preserving their intentional overlaps.
    pending=set(range(len(old.vertices)));adj={i:[] for i in pending}
    for e in old.edges:
        a,b=e.vertices;adj[a].append(b);adj[b].append(a)
    vertices=[];polygons=[]
    while pending:
        component={pending.pop()};stack=list(component)
        while stack:
            for v in adj[stack.pop()]:
                if v in pending:pending.remove(v);component.add(v);stack.append(v)
        ids=sorted(component);remap={v:i for i,v in enumerate(ids)}
        part=bpy.data.meshes.new('RootComponent')
        # Keep Blender's existing triangulation of non-planar tube quads exactly.
        old.calc_loop_triangles()
        part.from_pydata([old.vertices[i].co for i in ids],[],
            [tuple(remap[i] for i in t.vertices) for t in old.loop_triangles if t.vertices[0] in component])
        part.update();work=bpy.data.objects.new('RootComponent',part);bpy.context.scene.collection.objects.link(work)
        bpy.ops.object.select_all(action='DESELECT');work.select_set(True);bpy.context.view_layer.objects.active=work
        mod=work.modifiers.new('Refiner_CoreInteriorClearance','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=operand
        bpy.ops.object.modifier_apply(modifier=mod.name)
        offset=len(vertices);vertices.extend(v.co.copy() for v in work.data.vertices)
        polygons.extend(tuple(offset+i for i in p.vertices) for p in work.data.polygons)
        result_mesh=work.data;bpy.data.objects.remove(work,do_unlink=True);bpy.data.meshes.remove(result_mesh)
    bpy.data.objects.remove(operand,do_unlink=True);bpy.data.meshes.remove(mesh)
    me=bpy.data.meshes.new(old.name+'_InteriorClear');me.from_pydata(vertices,[],polygons);me.update();me.uv_layers.new(name='UVMap')
    # The temporary operand has no shader; retain the one original slot exactly.
    me.materials.clear()
    for material in old.materials:me.materials.append(material)
    for face in me.polygons:face.material_index=0
    bm=bmesh.new();bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bmesh.ops.triangulate(bm,faces=list(bm.faces))
    bm.to_mesh(me);bm.free();me.update()
    r.project_uv(me)
    for p in me.polygons:p.use_smooth=True
    me.set_sharp_from_angle(angle=math.radians(45))
    for user in users:user.data=me
    after=r.assert_clean(obj)
    error=max(abs(after['bounds_blender_m'][i][k]-before['bounds_blender_m'][i][k]) for i in range(2) for k in range(3))
    deltas=[[after['bounds_blender_m'][i][k]-before['bounds_blender_m'][i][k] for k in range(3)] for i in range(2)]
    # Removing the interior-only root tip may raise Z min and reduce Y max;
    # it has no collider or connector. All other bounds and all structural bounds stay exact.
    if label=='LinkingRootArches':
        assert 0<=deltas[0][2]<.05 and -.05<deltas[1][1]<=0 and max(abs(deltas[i][k]) for i in range(2) for k in range(3) if (i,k) not in [(0,2),(1,1)])<1e-6,(label,deltas)
    else:assert error<1e-6,(label,'bounds',error)
    newtree=BVHTree.FromPolygons([v.co for v in me.vertices],[list(p.vertices) for p in me.polygons])
    oldtree=BVHTree.FromPolygons([v.co for v in old.vertices],[list(p.vertices) for p in old.polygons])
    # Outside the wall (r>=2.6), all old surface samples must remain unchanged.
    old.calc_loop_triangles();samples=[]
    for t in old.loop_triangles:
        a,b,c=[old.vertices[i].co for i in t.vertices]
        for p in [a,b,c,(a+b+c)/3,(a+b)/2,(b+c)/2,(c+a)/2]:
            if math.hypot(p.x-center[0],p.y-center[1])>=2.6:samples.append(p)
    exterior_error=max(newtree.find_nearest(p)[3] for p in samples)
    assert exterior_error<1e-5,(label,'exterior changed',exterior_error)
    # No remaining part of these decorations may intrude into the inner cavity.
    # The 40-sided cutter inradius is 2.233 m, safely behind the 2.20-m wall.
    intrusive=[v for v in me.vertices if -.099<v.co.z<4.299 and math.hypot(v.co.x-center[0],v.co.y-center[1])<2.22]
    assert not intrusive,(label,'interior intrusion',len(intrusive))
    proof[obj.name]=dict(before=before,after=after,bounds_error_m=error,bounds_delta_m=deltas,
        exterior_surface_samples=len(samples),max_exterior_surface_error_m=exterior_error,
        cutter_center_m=list(center),cutter_radius_m=radius,cutter_sides=count,cutter_z_range_m=[-.1,4.3],
        interior_intruding_vertices_after=len(intrusive),material_slots_preserved=before['material_slots']==after['material_slots'])
    m['refiner_changes'][obj.name]['after']=after
    m['refiner_changes'][obj.name]['bounds_error_m']=error
    m['refiner_changes'][obj.name]['interior_root_trim']=proof[obj.name]
    # New cap vertices are inside the existing solid wall; exterior is unchanged.
    m['refiner_changes'][obj.name]['max_vertex_distance_to_input_surface_m']=max(oldtree.find_nearest(v.co)[3] for v in me.vertices)
    if old.users==0:bpy.data.meshes.remove(old)

baseline=json.loads((ROOT/'Evidence/before.json').read_text())
for name,digest in baseline['collider_fingerprints'].items():assert r.fingerprint(bpy.data.objects[name].data)==digest
for name,matrix in baseline['instance_matrices'].items():assert list(sum((list(row) for row in bpy.data.objects[name].matrix_world),[]))==matrix
settings=m['export_settings'].copy();settings['object_types']=set(settings['object_types'])
bpy.ops.preferences.addon_enable(module='io_scene_fbx')
for entry in m['exports']:
    if entry['asset_name'] not in proof:continue
    obj=bpy.data.objects[entry['asset_name']];bpy.ops.object.select_all(action='DESELECT');obj.hide_set(False);obj.select_set(True);bpy.context.view_layer.objects.active=obj
    bpy.ops.export_scene.fbx(filepath=str(ROOT/entry['path']),**settings)
    entry['sha256']=r.sha(ROOT/entry['path']);entry['source_stats']=r.extra_stats(obj)
for collection in ['00_SourceMeshes','01_UCX_Source']:
    for obj in bpy.data.collections[collection].objects:obj.hide_set(True)
bpy.context.scene['refiner_revision']=2
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/m['source_blend']))
m.update(status='refiner_active',refiner_revision=2,source_blend_sha256=r.sha(ROOT/m['source_blend']),
    interior_root_cleanup=dict(file='Evidence/interior_root_cleanup.json',script=Path(__file__).name,
        prior_source_sha256=prior_sha,changed_decor_assets=list(proof),structural_geometry_unchanged=True))
r.write('manifest.json',m)
r.write('Evidence/interior_root_cleanup.json',dict(status='passed',previous_source_sha256=prior_sha,
    changes=proof,colliders_unchanged=True,instance_matrices_unchanged=True,
    intent='Remove interior-only protrusions of existing decorative roots; caps buried behind existing inner wall. No new geometry added to cover defects.'))
r.write('Evidence/refinement.json',dict(status='passed',changes=m['refiner_changes'],colliders_unchanged=True,instances_unchanged=True))
print('INTERIOR_ROOT_CLEANUP_OK', list(proof),flush=True)
