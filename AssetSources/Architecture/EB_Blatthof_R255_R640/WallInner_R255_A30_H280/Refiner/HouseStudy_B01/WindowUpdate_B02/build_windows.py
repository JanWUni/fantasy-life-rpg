"""Split the immutable B01 window into wall opening, frame and glass in an own copy."""
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import sys
sys.dont_write_bytecode=True
import bpy
import bmesh
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent
NAMES=['SM_EH_Wall_WindowOpening_200x24x320','SM_EH_WindowFrame_Arch_100x173','SM_EH_WindowGlass_Arch_100x173']
MOUNT=Vector((1,-.055,.95))
spec=importlib.util.spec_from_file_location('b01mesh',SOURCE/'build_house.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,data):p.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')


def islands(mesh):
    links={v.index:set() for v in mesh.vertices}
    for e in mesh.edges:
        a,b=e.vertices;links[a].add(b);links[b].add(a)
    remaining=set(links);result=[]
    while remaining:
        todo=[min(remaining)];seen=set()
        while todo:
            i=todo.pop()
            if i in seen:continue
            seen.add(i);todo.extend(links[i]-seen)
        remaining-=seen;result.append(seen)
    return result


def subset(original,name,selected_faces,slots,offset):
    mesh=original.data
    indices=sorted({i for p in selected_faces for i in mesh.polygons[p].vertices})
    remap={index:i for i,index in enumerate(indices)}
    data=bpy.data.meshes.new(name)
    data.from_pydata([tuple(mesh.vertices[i].co-offset) for i in indices],[],
        [tuple(remap[i] for i in mesh.polygons[p].vertices) for p in selected_faces])
    data.update()
    for s in slots:data.materials.append(bpy.data.materials[s])
    uv=data.uv_layers.new(name='UV0')
    for out,index in zip(data.polygons,selected_faces):
        src=mesh.polygons[index]
        out.material_index=slots.index(mesh.materials[src.material_index].name)
        out.use_smooth=src.use_smooth
        for a,b in zip(out.loop_indices,src.loop_indices):uv.data[a].uv=mesh.uv_layers[0].data[b].uv
    obj=bpy.data.objects.new(name,data)
    obj['KitId']='EH.HouseB.Prototype01';obj['InterfaceVersion']='draft_1_window_2'
    bpy.data.scenes['Module_Library'].collection.objects.link(obj)
    return obj


def audit(obj):
    mesh=obj.data;mesh.calc_loop_triangles()
    bm=bmesh.new();bm.from_mesh(mesh)
    assert all(e.is_manifold and e.is_contiguous for e in bm.edges),obj.name
    volume=bm.calc_volume(signed=True);assert volume>0,(obj.name,volume)
    bm.free()
    assert all(t.area>1e-12 for t in mesh.loop_triangles)
    for t in mesh.loop_triangles:
        a,b,c=[mesh.uv_layers[0].data[i].uv for i in t.loops]
        assert abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))>1e-12
    assert all(abs(v)<1e-7 for v in obj.location) and all(abs(v)<1e-7 for v in obj.rotation_euler)
    assert all(abs(v-1)<1e-7 for v in obj.scale)
    return dict(vertices=len(mesh.vertices),triangles=len(mesh.loop_triangles),slots=[s.name for s in mesh.materials],
        bounds_m=[[min(v.co[k] for v in mesh.vertices) for k in range(3)],
                  [max(v.co[k] for v in mesh.vertices) for k in range(3)]],signed_volume_m3=volume,uv_channels=len(mesh.uv_layers))


def build():
    assert not (ROOT/'EH_HouseB02_Windows.blend').exists()
    for folder in ('Exports','Evidence','Previews'):(ROOT/folder).mkdir(exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE/'EH_HouseB01_Study.blend'))
    old.MATERIALS.update({m.name:m for m in bpy.data.materials})
    library=bpy.data.scenes['Module_Library'];bpy.context.window.scene=library
    original=library.objects['SM_EH_Wall_Window_200x24x320']
    src_mesh=original.data;groups=[[],[],[]];parts=[]
    for component in islands(src_mesh):
        faces=[p.index for p in src_mesh.polygons if p.vertices[0] in component]
        mats={src_mesh.materials[src_mesh.polygons[p].material_index].name for p in faces}
        assert len(mats)==1,mats
        material=next(iter(mats))
        points=[src_mesh.vertices[i].co for i in component]
        lo=[min(v[k] for v in points) for k in range(3)];hi=[max(v[k] for v in points) for k in range(3)]
        target=2 if material=='Glass' else (1 if material in ('Timber','Stone') and lo[0]>.35 and hi[0]<1.65 and lo[2]>.5 and hi[2]<2.85 else 0)
        groups[target].extend(faces);parts.append(dict(material=material,target=target,bounds=[lo,hi]))
    assert sum(p['target']==1 for p in parts)==5,parts
    assert sum(p['target']==2 for p in parts)==1
    objs=[subset(original,NAMES[i],sorted(groups[i]),slots,Vector((0,0,0)) if i==0 else MOUNT)
          for i,slots in enumerate([['Plaster','Timber','Stone'],['Timber','Stone'],['Glass']])]
    assert sum(audit(o)['triangles'] for o in objs)==1272
    # Wall ring: 2 side boxes, sill box and 4 convex strips above the arch. Opening remains free.
    colliders={name:[] for name in NAMES}
    bodies=[old.collider_box((.25,.12,1.6),(.5,.24,3.2)),
            old.collider_box((1.75,.12,1.6),(.5,.24,3.2)),old.collider_box((1,.12,.475),(1,.24,.95))]
    top=lambda x:2.02+.66*max(0,1-abs((x-1)/.5))**.72
    for a,b in zip((.5,.75,1,1.25),(.75,1,1.25,1.5)):
        body=old.Mesh();body.prism([(a,top(a)),(b,top(b)),(b,3.2),(a,3.2)],(0,.24),'Plaster');bodies.append(body)
    for i,body in enumerate(bodies):
        o=body.object('UCX_'+NAMES[0]+'_%02d'%i,library.collection,['Plaster']);o.hide_render=True;o.display_type='WIRE'
        colliders[NAMES[0]].append(o)
    glass=objs[2].copy();glass.data=objs[2].data.copy();glass.name='UCX_'+NAMES[2]+'_00'
    library.collection.objects.link(glass);glass.hide_render=True;glass.display_type='WIRE';colliders[NAMES[2]].append(glass)
    replacements={}
    for scene_name in ('House_10x12','House_10x16_Variation'):
        scene=bpy.data.scenes[scene_name];count=0
        for inst in list(scene.objects):
            if inst.get('SourceModule')!='SM_EH_Wall_Window_200x24x320':continue
            transform=inst.matrix_world.copy();inst.data=objs[0].data;inst['SourceModule']=NAMES[0]
            for obj in objs[1:]:
                part=obj.copy();part.data=obj.data;scene.collection.objects.link(part)
                part.location=transform@MOUNT;part.rotation_euler=inst.rotation_euler.copy();part['SourceModule']=obj.name
            count+=1
        replacements[scene_name]=count
    bpy.data.objects.remove(original,do_unlink=True)
    for obj in list(library.objects):
        if obj.name.startswith('UCX_SM_EH_Wall_Window_200x24x320_'):bpy.data.objects.remove(obj,do_unlink=True)
    glassmat=bpy.data.materials['Glass'];bsdf=glassmat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value=(.95,.98,1,1)
    bsdf.inputs['Metallic'].default_value=0;bsdf.inputs['Roughness'].default_value=.08
    bsdf.inputs['Transmission Weight'].default_value=1;bsdf.inputs['IOR'].default_value=1.45
    for image in bpy.data.images:
        if image.source=='FILE':image.filepath='//../Textures/'+image.filepath.replace('\\','/').rsplit('/',1)[-1]
    settings=dict(old.PROFILE['export_settings']);settings['object_types']=set(settings['object_types'])
    if 'io_scene_fbx' not in bpy.context.preferences.addons:bpy.ops.preferences.addon_enable(module='io_scene_fbx')
    info={}
    for obj in objs:
        bpy.ops.object.select_all(action='DESELECT')
        for selected in [obj]+colliders[obj.name]:selected.select_set(True)
        bpy.context.view_layer.objects.active=obj
        assert bpy.ops.export_scene.fbx(filepath=str(ROOT/'Exports'/(obj.name+'.fbx')),**settings)=={'FINISHED'}
        info[obj.name]=audit(obj)
        for body in colliders[obj.name]:
            audit(body)
            error=max(p.normal.dot(v.co-body.data.vertices[p.vertices[0]].co) for p in body.data.polygons for v in body.data.vertices)
            assert error<1e-5,(body.name,error)
        info[obj.name]['ucx_hulls']=len(colliders[obj.name])
    bpy.context.window.scene=bpy.data.scenes['House_10x12']
    bpy.context.preferences.filepaths.save_version=0
    assert bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'EH_HouseB02_Windows.blend'),relative_remap=False)=={'FINISHED'}
    manifest=dict(status='draft',source_revision='21a7ef17dd5cfd6f058b4c0f7440d2727b98c18d',
        parent_blend_sha256=sha(SOURCE/'EH_HouseB01_Study.blend'),source='EH_HouseB02_Windows.blend',
        kit_id='EH.HouseB.Prototype01',interface_version='draft_1_window_2',assets=info,
        window_mount_blender_m=list(MOUNT),window_mount_ue_cm=[100,-100*MOUNT.y,95],
        opening_nominal_cm=[100,173],wall_contract_cm=[200,24,320],
        wall_joins_blender_m=[[0,0,0],[2,0,0]],glass_thickness_cm=2,
        slot_contract={'wall':['Plaster','Timber','Stone'],'frame':['Timber','Stone'],'glass':['Glass']},
        replacement_counts=replacements,export_profile=old.PROFILE,
        preserved_all_original_render_triangles=1272,partitioned_components=parts)
    write(ROOT/'manifest.json',manifest)
    print('WINDOWS_BUILD_OK',replacements,info)


def verify():
    manifest=json.loads((ROOT/'manifest.json').read_text())
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'EH_HouseB02_Windows.blend'))
    library=bpy.data.scenes['Module_Library'];source={}
    for name in NAMES:
        source[name]=audit(library.objects[name]);assert source[name]['triangles']==manifest['assets'][name]['triangles']
    for im in bpy.data.images:
        if im.source=='FILE':assert Path(bpy.path.abspath(im.filepath)).is_file(),im.filepath
    results={}
    for name in NAMES:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        if 'io_scene_fbx' not in bpy.context.preferences.addons:bpy.ops.preferences.addon_enable(module='io_scene_fbx')
        bpy.ops.import_scene.fbx(filepath=str(ROOT/'Exports'/(name+'.fbx')),use_anim=False,use_image_search=False)
        render=[o for o in bpy.context.scene.objects if o.type=='MESH' and not o.name.startswith('UCX_')];assert len(render)==1
        observed=audit(render[0]);assert observed['slots']==source[name]['slots'] and observed['triangles']==source[name]['triangles']
        error=max(abs(observed['bounds_m'][i][j]-source[name]['bounds_m'][i][j]) for i in range(2) for j in range(3));assert error<1e-5
        assert len([o for o in bpy.context.scene.objects if o.name.startswith('UCX_')])==manifest['assets'][name]['ucx_hulls']
        results[name]=dict(bounds_roundtrip_error_m=error,**observed)
    write(ROOT/'Evidence/blender_verification.json',dict(status='passed',source_reopened=True,source=source,roundtrip=results,blender=bpy.app.version_string))
    print('WINDOWS_VERIFY_PASSED')


if __name__=='__main__':
    {'build':build,'verify':verify}[sys.argv[-1]]()
