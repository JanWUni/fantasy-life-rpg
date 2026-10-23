"""Resize only the catalogue windows and apertures in a separate Blender revision."""
from pathlib import Path
import sys,json,hashlib,math
sys.dont_write_bytecode=True
import bpy,numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parent;PARENT=ROOT.parent;REPO=ROOT.parents[6]
sys.path.insert(0,str(PARENT));import build_catalogue as g
NAMES=['SM_WC01_Wall_'+s+'_Window_300x24x320' for s in 'ABC']+['SM_WC01_WindowFrame_140x40x157','SM_WC01_WindowGlass_Clear_112x2x145']
SX=.65/1.20;SZ=.90/1.52
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):(ROOT/n).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

def copy_decor(old):
    """Keep every timber/stone face and UV exactly; only plaster is reconstructed."""
    m=g.Mesh();polys=[p for p in old.data.polygons if old.data.materials[p.material_index].name!='WC01_Plaster']
    ids=sorted({v for p in polys for v in p.vertices});lookup={v:i for i,v in enumerate(ids)}
    m.v=[tuple(old.data.vertices[v].co) for v in ids]
    for p in polys:
        m.f.append(tuple(lookup[v] for v in p.vertices));m.m.append(old.data.materials[p.material_index].name.removeprefix('WC01_'))
        m.s.append(p.use_smooth);m.uv.append([tuple(old.data.uv_layers.active.data[i].uv) for i in p.loop_indices])
    return m

def build():
    bpy.ops.wm.open_mainfile(filepath=str(PARENT/'WallCatalogue01.blend'))
    lib=bpy.data.scenes['Module_Library'];bpy.context.window.scene=lib
    old=json.loads((PARENT/'manifest.json').read_text());g.ASSETS.clear()
    g.lib.MATERIALS.clear();g.lib.MATERIALS.update({k:bpy.data.materials['WC01_'+k] for k in old['material_families']})
    before={};after={}
    for name in NAMES:
        o=lib.objects[name];before[name]=g.audit(o);previous=o.data;description=old['assets'][name]['description'];kind=old['assets'][name]['kind']
        if kind=='Wall':
            m=copy_decor(o);bodies=[]
            def fill(x0,x1,z0,z1):
                c=((x0+x1)/2,.12,(z0+z1)/2);s=(x1-x0,.24,z1-z0)
                m.box(c,s,'Plaster');bodies.append(g.box(c,s))
            fill(0,1.175,0,3.2);fill(1.825,3,0,3.2);fill(1.175,1.825,0,1.35)
            head=lambda x:2.10+.15*max(0,1-((x-1.5)/.325)**2)
            xs=np.linspace(1.175,1.825,13)
            for a,b in zip(xs,xs[1:]):
                outline=[(float(a),head(a)),(float(b),head(b)),(float(b),3.2),(float(a),3.2)]
                m.prism(outline,(0,.24),'Plaster');c=g.Mesh();c.prism(outline,(0,.24),'Plaster');bodies.append(c)
            old_ucx=[x for x in list(lib.objects) if x.name.startswith('UCX_'+name+'_')]
            for c in old_ucx:bpy.data.objects.remove(c,do_unlink=True)
            o.name='Previous_'+name
            newname=g.add(name.removeprefix('SM_WC01_'),m,old['assets'][name]['slots'],bodies,description+'; reduced 65 x 90 cm aperture',kind)
            new=g.ASSETS[newname]['obj'];newdata=new.data
            # Linked library instances keep transforms, materials and names.
            for inst in list(bpy.data.objects):
                if inst.data==previous:inst.data=newdata
            bpy.data.objects.remove(new,do_unlink=True);o.name=name;g.ASSETS[name]['obj']=o
        else:
            mesh=previous.copy()
            for v in mesh.vertices:v.co.x*=SX;v.co.z*=SZ
            mesh.update()
            for inst in list(bpy.data.objects):
                if inst.data==previous:inst.data=mesh
            bodies=[c for c in lib.objects if c.name.startswith('UCX_'+name+'_')]
            for c in bodies:
                c.data=c.data.copy()
                for v in c.data.vertices:v.co.x*=SX;v.co.z*=SZ
                c.data.update()
            g.ASSETS[name]=dict(obj=o,ucx=bodies,description=description+'; reduced insert, legacy asset ID retained',kind=kind)
    # Reposition only installed inserts; loose catalogue samples keep their display origin.
    for scene in bpy.data.scenes:
        if scene.name=='Module_Library':continue
        for o in scene.objects:
            if o.type=='MESH' and o.data in [g.ASSETS[n]['obj'].data for n in NAMES[-2:]] and abs(o.location.y-4.2)<.001:o.location.z+=.35
    settings=dict(g.PROFILE['export_settings']);settings['object_types']=set(settings['object_types'])
    bpy.ops.preferences.addon_enable(module='io_scene_fbx')
    for name,it in g.ASSETS.items():
        bpy.ops.object.select_all(action='DESELECT')
        for o in [it['obj']]+it['ucx']:o.hide_set(False);o.select_set(True)
        bpy.context.view_layer.objects.active=it['obj']
        bpy.ops.export_scene.fbx(filepath=str(ROOT/'Exports'/(name+'.fbx')),**settings)
        for c in it['ucx']:c.hide_set(True)
        after[name]=dict(**g.audit(it['obj']),ucx_hulls=len(it['ucx']),description=it['description'],kind=it['kind'],fbx_sha256=sha(ROOT/'Exports'/(name+'.fbx')))
    for im in bpy.data.images:
        if im.source=='FILE' and im.name.startswith('T_WC01_'):im.filepath='//../Textures/'+im.name+'.png'
    bpy.context.window.scene=bpy.data.scenes['Wall_Comparison'];bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'WindowResize02.blend'),relative_remap=False)
    write('manifest.json',dict(status='draft',accepted=False,revision=2,source='WindowResize02.blend',source_sha256=sha(ROOT/'WindowResize02.blend'),
        parent_source_sha256=sha(PARENT/'WallCatalogue01.blend'),kit_id='EC.WallCatalogue01',interface_version='draft_2_window',assets=after,
        before=before,opening_before_cm=[120,152],opening_after_cm=[65,90],sill_before_cm=100,sill_after_cm=135,insert_origin_cm=[150,0,135],
        unchanged='Wall X0..300 / core depth24 / Z0..320, outer seams, timber/stone decoration, slots, all materials/textures, all houses, solids and furniture',
        scope='Only three catalogue window walls plus frame and glass; colors temporarily retained and not accepted as elven style',
        reference=dict(studies='Existing A/B house studies',glass_cm=[65,80],frame_bounds_cm=[80,27.9,96]),export_profile=g.PROFILE,
        wall_window_interface='X117.5..182.5 cm; sill Z135; head Z210+15*(1-((X-150)/32.5)^2) cm',
        names='Existing nominal review asset IDs retained to preserve references; measured bounds are authoritative'))
    print('RESIZE_BUILD_OK',len(after))

def verify():
    d=json.loads((ROOT/'manifest.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(ROOT/d['source']))
    lib=bpy.data.scenes['Module_Library'];source={n:g.audit(lib.objects[n]) for n in NAMES}
    used={n.image for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
    assert all(Path(bpy.path.abspath(i.filepath)).is_file() for i in used if i.source=='FILE'),[(i.name,i.filepath) for i in used if i.source=='FILE' and not Path(bpy.path.abspath(i.filepath)).is_file()]
    old=json.loads((PARENT/'manifest.json').read_text());unchanged={}
    for n,i in old['assets'].items():
        if n not in NAMES:
            actual=g.audit(lib.objects[n]);assert all(actual[k]==i[k] for k in ['triangles','vertices','slots','bounds_m']);unchanged[n]=True
    result={}
    for n in NAMES:
        bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.preferences.addon_enable(module='io_scene_fbx')
        bpy.ops.import_scene.fbx(filepath=str(ROOT/'Exports'/(n+'.fbx')),use_anim=False,use_image_search=False)
        o=next(o for o in bpy.context.scene.objects if o.type=='MESH' and not o.name.startswith('UCX_'));actual=g.audit(o)
        assert actual['triangles']==source[n]['triangles'] and actual['slots']==source[n]['slots']
        error=max(abs(actual['bounds_m'][i][k]-source[n]['bounds_m'][i][k]) for i in range(2) for k in range(3));assert error<1e-5
        assert sum(o.name.startswith('UCX_') for o in bpy.context.scene.objects)==d['assets'][n]['ucx_hulls']
        result[n]=dict(bounds_error_m=error,**actual)
    write('Evidence/blender_verification.json',dict(status='passed',source_reopened=True,textures_resolved=True,unchanged_other_modules=unchanged,assets=result))
    print('RESIZE_VERIFY_OK',len(result))

def render():
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'WindowResize02.blend'));s=bpy.data.scenes['Wall_Comparison'];bpy.context.window.scene=s
    # Hide other samples only for the explanatory render; do not save this scene state.
    for o in s.objects:
        if o.type=='MESH' and o.name!='Review_Ground':o.hide_render=abs(o.location.y-4.2)>.001
    cam=s.camera;cam.data.type='ORTHO';cam.data.ortho_scale=12.8;cam.location=(5.7,-8,4.2)
    cam.rotation_euler=(Vector((5.7,4.2,1.5))-cam.location).to_track_quat('-Z','Y').to_euler()
    s.render.resolution_x=1500;s.render.resolution_y=700;s.render.filepath=str(ROOT/'Previews/Blender_smaller_windows.png')
    bpy.ops.render.render(write_still=True)

if __name__=='__main__':{'build':build,'verify':verify,'render':render}[sys.argv[-1]]()
