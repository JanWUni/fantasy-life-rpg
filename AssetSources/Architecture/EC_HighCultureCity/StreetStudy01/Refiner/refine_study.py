"""Targeted refinement of an immutable Creator study. No Unreal or shared-file writes."""
from pathlib import Path
import argparse,copy,hashlib,importlib.util,json,math,shutil,sys
sys.dont_write_bytecode=True
import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parent;CREATOR=ROOT.parent/'Creator';REPO=ROOT.parents[4]
INPUT_COMMIT='08e7d7eea4a161a5e5025d656ca5b199ed0130da'
MODULE='StreetStudy01';BLEND=ROOT/(MODULE+'_Refined.blend')
BEVELS={'StoneDressings':.004,'EntryWoodArch':.002,'DoorLeaf_140x235':.003,'CityWindowFrame_65x80':.002,'CityShutter_32x84':.003,'PorchPosts_220x270':.004,'PlanterRim':.004}
spec=importlib.util.spec_from_file_location('creator_study_read_only',CREATOR/'build_study.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
c.ROOT=ROOT;c.BLEND=BLEND;c.args=argparse.Namespace(view=None)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,data):
    p=ROOT/name;assert p.resolve().is_relative_to(ROOT.resolve());p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
def manifest():return json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
def fingerprint(mesh):
    data=dict(vertices=[list(v.co) for v in mesh.vertices],faces=[list(p.vertices) for p in mesh.polygons])
    return hashlib.sha256(json.dumps(data,separators=(',',':')).encode()).hexdigest()
def extra_stats(o):
    result=c.stats(o);me=o.data;me.calc_loop_triangles();uv=me.uv_layers.active;bad=0
    for t in me.loop_triangles:
        a,b,d=[uv.data[i].uv for i in t.loops]
        bad+=abs((b.x-a.x)*(d.y-a.y)-(b.y-a.y)*(d.x-a.x))<1e-12
    bm=bmesh.new();bm.from_mesh(me)
    volumes=[];todo=set(bm.verts)
    while todo:
        stack=[todo.pop()];verts=set(stack)
        while stack:
            for edge in stack.pop().link_edges:
                for v in edge.verts:
                    if v in todo:todo.remove(v);verts.add(v);stack.append(v)
        faces={f for v in verts for f in v.link_faces}
        # Signed tetrahedra from the actual triangulation per connected volume.
        face_ids={f.index for f in faces}
        volume=0.
        for t in me.loop_triangles:
            if t.polygon_index in face_ids:
                a,b,d=[me.vertices[i].co for i in t.vertices];volume+=a.dot(b.cross(d))/6
        volumes.append(volume)
    result.update(faces=len(me.polygons),edges=len(me.edges),smooth_faces=sum(p.use_smooth for p in me.polygons),has_custom_normals=me.has_custom_normals,
        degenerate_uv_triangles=bad,connected_components=len(volumes),component_signed_volumes_m3=volumes,
        sharp_edges=sum(bool(a.value) for a in me.attributes['sharp_edge'].data) if 'sharp_edge' in me.attributes else 0)
    bm.free();return result
def assert_clean(o):
    result=extra_stats(o)
    assert result['nonmanifold_edges']==result['degenerate_faces']==result['degenerate_uv_triangles']==0,(o.name,result)
    assert all(v>1e-10 for v in result['component_signed_volumes_m3']),(o.name,result['component_signed_volumes_m3'])
    return result
def project_uv(me):
    uv=me.uv_layers.active
    for p in me.polygons:
        axis=max(range(3),key=lambda k:abs(p.normal[k]));axes={0:(1,2),1:(0,2),2:(0,1)}[axis]
        for loop in p.loop_indices:
            v=me.vertices[me.loops[loop].vertex_index].co;uv.data[loop].uv=(v[axes[0]]/2,v[axes[1]]/2)
def bake_normals(obj,force_smooth=False):
    me=obj.data;users=[o for o in bpy.data.objects if o.type=='MESH' and o.data==me]
    if force_smooth:
        for p in me.polygons:p.use_smooth=True
    # Smooth curved sections while explicitly splitting caps and sharp box corners.
    me.set_sharp_from_angle(angle=math.radians(45))
    obj.data=me.copy()  # Applying a modifier requires a single-user working mesh.
    bpy.ops.object.select_all(action='DESELECT');obj.hide_set(False);obj.select_set(True);bpy.context.view_layer.objects.active=obj
    mod=obj.modifiers.new('Refiner_WeightedNormals','WEIGHTED_NORMAL');mod.keep_sharp=True;mod.weight=50
    bpy.ops.object.modifier_apply(modifier=mod.name)
    for other in users:other.data=obj.data
    if me.users==0:bpy.data.meshes.remove(me)
def prepare():
    for folder in ['Exports','Evidence','Previews']:(ROOT/folder).mkdir(exist_ok=True)
    incoming=json.loads((CREATOR/'manifest.json').read_text(encoding='utf-8'))
    assert sha(CREATOR/incoming['source_blend'])==incoming['source_blend_sha256']
    if BLEND.exists():
        if args.revise:
            prior=manifest();assert prior['input_commit']==INPUT_COMMIT and sha(BLEND)==prior['source_blend_sha256'], 'Refiner source has external changes'
            write('Evidence/previous_pass.json',dict(source_sha256=sha(BLEND),status=prior['status']))
            shutil.copy2(CREATOR/incoming['source_blend'],BLEND)
        else:assert sha(BLEND)==incoming['source_blend_sha256'] and (ROOT/'Evidence/copied_source.json').exists(), 'Existing edited Refiner work must not be overwritten'
    else:shutil.copy2(CREATOR/incoming['source_blend'],BLEND)
    write('Evidence/copied_source.json',dict(input_commit=INPUT_COMMIT,source_sha256=sha(BLEND),byte_identical_copy=True))
    bpy.ops.wm.open_mainfile(filepath=str(BLEND));before={};changes={}
    for entry in incoming['exports']:
        o=bpy.data.objects[entry['asset_name']];before[o.name]=assert_clean(o)
        assert list(o.location)==[0,0,0] and list(o.scale)==[1,1,1] and list(o.rotation_euler)==[0,0,0]
    collider_fingerprints={o.name:fingerprint(o.data) for o in bpy.data.collections['01_UCX_Source'].objects}
    instance_matrices={o['object']:list(sum((list(row) for row in bpy.data.objects[o['object']].matrix_world),[])) for o in incoming['placement_instances']}
    write('Evidence/before.json',dict(source_assets=before,collider_fingerprints=collider_fingerprints,instance_matrices=instance_matrices))
    for entry in incoming['exports']:
        obj=bpy.data.objects[entry['asset_name']];obj.hide_set(False);me=obj.data;old=me.copy();old_stats=before[obj.name]
        bm=bmesh.new();bm.from_mesh(me)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
        bmesh.ops.dissolve_limit(bm,angle_limit=1e-6,use_dissolve_boundaries=False,verts=list(bm.verts),edges=list(bm.edges),delimit={'MATERIAL','UV','SHARP'})
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
        width=BEVELS.get(entry['label'],0);bevel_applied=False
        if width:
            pre_bevel=me.copy();bm=bmesh.new();bm.from_mesh(me)
            edges=[e for e in bm.edges if e.is_manifold and e.calc_face_angle()>math.radians(45)]
            if edges:
                result=bmesh.ops.bevel(bm,geom=edges,offset=width,segments=2,affect='EDGES',clamp_overlap=True)
                for f in result['faces']:f.smooth=True
                bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);me.update()
                measured=c.stats(obj);error=max(abs(measured['bounds_blender_m'][i][k]-old_stats['bounds_blender_m'][i][k]) for i in range(2) for k in range(3))
                bevel_applied=error<1e-6 and measured['nonmanifold_edges']==measured['degenerate_faces']==0
                if not bevel_applied:
                    restore=bmesh.new();restore.from_mesh(pre_bevel);restore.to_mesh(me);restore.free();me.update()
            bm.free();bpy.data.meshes.remove(pre_bevel)
        curved=entry['label'] in ['StoneDressings','EntryWoodArch','TreeRelief','CityWindowFrame_65x80','StreetTreeTrunk','StreetTreeCrown']
        project_uv(me)
        foliage=entry['category']=='Nature' and any(s in old_stats['material_slots'] for s in ['Leaves','Herbs'])
        if foliage:
            for p in me.polygons:p.use_smooth=True
            me.set_sharp_from_angle(angle=math.pi)  # Keep soft foliage; area-weighted normals introduce visible bands here.
        else:bake_normals(obj,force_smooth=bool(curved or bevel_applied))
        now=assert_clean(obj)
        error=max(abs(now['bounds_blender_m'][i][k]-old_stats['bounds_blender_m'][i][k]) for i in range(2) for k in range(3));assert error<1e-6,(obj.name,error)
        old_bvh=BVHTree.FromPolygons([v.co.copy() for v in old.vertices],[list(p.vertices) for p in old.polygons])
        surface_error=max(old_bvh.find_nearest(v.co)[3] for v in obj.data.vertices)
        assert surface_error<max(width*2,1e-5),(obj.name,surface_error)
        changes[obj.name]=dict(before=old_stats,after=now,controlled_bevel_m=width if bevel_applied else 0,
            bevel_rejected_to_preserve_contract=bool(width and not bevel_applied),bounds_error_m=error,max_vertex_distance_to_input_surface_m=surface_error)
        bpy.data.meshes.remove(old)
    for name,digest in collider_fingerprints.items():assert fingerprint(bpy.data.objects[name].data)==digest,name
    for name,matrix in instance_matrices.items():assert list(sum((list(row) for row in bpy.data.objects[name].matrix_world),[]))==matrix,name
    settings=json.loads(c.PROFILE.read_text())['export_settings'];settings['object_types']=set(settings['object_types'])
    bpy.ops.preferences.addon_enable(module='io_scene_fbx');exports=[]
    for item in incoming['exports']:
        obj=bpy.data.objects[item['asset_name']];bpy.ops.object.select_all(action='DESELECT')
        for name in [obj.name]+item['collision_names']:
            member=bpy.data.objects[name];member.hide_set(False);member.select_set(True)
        bpy.context.view_layer.objects.active=obj;path=ROOT/item['path']
        bpy.ops.export_scene.fbx(filepath=str(path),**settings)
        entry=copy.deepcopy(item);entry['sha256']=sha(path);entry['source_stats']=extra_stats(obj);exports.append(entry)
    for collection in ['00_SourceMeshes','01_UCX_Source']:
        for obj in bpy.data.collections[collection].objects:obj.hide_set(True)
    bpy.context.scene['status']='refiner_source';bpy.context.scene['input_commit']=INPUT_COMMIT
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    result=copy.deepcopy(incoming)
    result.update(status='refiner_active',accepted=False,input_commit=INPUT_COMMIT,input_source_sha256=incoming['source_blend_sha256'],
        source_blend=BLEND.name,source_blend_sha256=sha(BLEND),exports=exports,refiner_directory=ROOT.relative_to(REPO).as_posix(),
        refiner_changes=changes,export_settings=settings|{'object_types':sorted(settings['object_types'])},unreal_import_performed=False)
    write('manifest.json',result);write('Evidence/refinement.json',dict(status='passed',changes=changes,colliders_unchanged=True,instances_unchanged=True))
    print('REFINEMENT_OK',MODULE,sum(v['after']['triangles'] for v in changes.values()),flush=True)
def verify():
    m=manifest();c.verify()  # The supplied checker is rebound to the Refiner directory only.
    bpy.ops.wm.open_mainfile(filepath=str(BLEND));before=json.loads((ROOT/'Evidence/before.json').read_text());src={}
    for item in m['exports']:src[item['asset_name']]=assert_clean(bpy.data.objects[item['asset_name']])
    for name,digest in before['collider_fingerprints'].items():assert fingerprint(bpy.data.objects[name].data)==digest
    for name,matrix in before['instance_matrices'].items():assert list(sum((list(row) for row in bpy.data.objects[name].matrix_world),[]))==matrix,name
    roundtrip={}
    for item in m['exports']:
        bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.preferences.addon_enable(module='io_scene_fbx')
        bpy.ops.import_scene.fbx(filepath=str(ROOT/item['path']),use_anim=False,use_image_search=False,use_custom_normals=True)
        obj=bpy.data.objects[item['asset_name']];actual=assert_clean(obj)
        assert list(obj.location)==[0,0,0] and max(abs(s-1) for s in obj.scale)<1e-6
        assert actual['material_slots']==src[obj.name]['material_slots']
        roundtrip[obj.name]=actual
    write('Evidence/independent_verification.json',dict(status='passed',source_reopened=True,source_assets=src,all_fbx_reimported=True,
        roundtrips=roundtrip,instance_matrices_exactly_preserved=True,collider_geometry_exactly_preserved=True,unreal_import=False))
    m=manifest();m['status']='refiner_verified';m['accepted']=False;write('manifest.json',m)
    print('INDEPENDENT_VERIFY_OK',MODULE,flush=True)
def render():
    c.args.view=args.view;c.render()
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=['prepare','verify','render'],required=True);parser.add_argument('--view');parser.add_argument('--revise',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);{'prepare':prepare,'verify':verify,'render':render}[args.mode]()
