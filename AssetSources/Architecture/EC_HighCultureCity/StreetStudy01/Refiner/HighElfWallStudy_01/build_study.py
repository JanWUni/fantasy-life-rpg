"""Two isolated Blender art studies; no Unreal or house writes."""
from pathlib import Path
import sys, json, math, hashlib, shutil
sys.dont_write_bytecode=True
import bpy, bmesh
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[5]
PARENT=ROOT.parent/'WallCatalogue_01'/'WindowResize_02'
sys.path.insert(0,str(ROOT.parent/'WallCatalogue_01'))
import build_catalogue as g
Mesh=g.Mesh
MATS={}; ASSETS=[]

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def write(name,data):
    p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def snapshot():
    return {p.relative_to(REPO).as_posix():sha(p) for d in ['AssetSources','Content','Config','Source','Tools','docs'] for p in (REPO/d).rglob('*') if p.is_file() and not p.is_relative_to(ROOT) and p.suffix not in ['.pyc','.blend1']}

def material(key,color,rough,metal=0,detail=False):
    m=bpy.data.materials.new('HEWS01_'+key);m.diffuse_color=(*color,1);m.use_nodes=True
    n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    if detail:
        tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=5;tex.inputs['Detail'].default_value=3
        coord=n.new('ShaderNodeTexCoord');l.new(coord.outputs['Object'],tex.inputs['Vector'])
        ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(*(v*.86 for v in color),1);ramp.color_ramp.elements[1].color=(*(min(v*1.045,1) for v in color),1)
        l.new(tex.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs['Color'],p.inputs['Base Color'])
        grain=n.new('ShaderNodeTexNoise');grain.inputs['Scale'].default_value=210;grain.inputs['Detail'].default_value=2;l.new(coord.outputs['Object'],grain.inputs['Vector'])
        bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.16;bump.inputs['Distance'].default_value=.00065 if not metal else .00015
        l.new(grain.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],p.inputs['Normal'])
        mr=n.new('ShaderNodeMapRange');mr.inputs['To Min'].default_value=rough-.07;mr.inputs['To Max'].default_value=rough+.06;l.new(tex.outputs['Fac'],mr.inputs['Value']);l.new(mr.outputs[0],p.inputs['Roughness'])
    MATS[key]=m;return m

def materials():
    material('Ivory',(.73,.70,.62),.57,detail=True)
    material('CarvedStone',(.84,.82,.74),.44,detail=True)
    material('RecessStone',(.49,.53,.53),.61,detail=True)
    material('Gold',(.63,.41,.14),.28,.83,True)
    material('Azure',(.055,.36,.49),.22,.25,True)
    m=material('ClearGlass',(.98,.995,1),.025)
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Transmission Weight'].default_value=1;bs.inputs['IOR'].default_value=1.45
    # Allow daylight through the pane in Cycles without pretending this is an Unreal material.
    n=m.node_tree.nodes;l=m.node_tree.links;lp=n.new('ShaderNodeLightPath');tr=n.new('ShaderNodeBsdfTransparent');mix=n.new('ShaderNodeMixShader')
    l.new(lp.outputs['Is Shadow Ray'],mix.inputs[0]);l.new(bs.outputs[0],mix.inputs[1]);l.new(tr.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],n.get('Material Output').inputs['Surface'])
    material('Stage',(.065,.084,.098),.8)
    material('Letter',(.68,.73,.74),.7)
    g.lib.MATERIALS.clear();g.lib.MATERIALS.update(MATS)

def add(m,name,coll,offset,kind='Decor'):
    slots=list(dict.fromkeys(m.m));o=m.object(name,coll,slots)
    # Deterministic face-normal correction and UV repair for non-planar curved ribbons.
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
    uv=o.data.uv_layers.active
    for p in o.data.polygons:
        a,b,c=[uv.data[i].uv.copy() for i in p.loop_indices]
        if abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))<1e-12:
            axis=max(range(3),key=lambda k:abs(p.normal[k]));axes=[k for k in range(3) if k!=axis]
            for i in p.loop_indices:
                v=o.data.vertices[o.data.loops[i].vertex_index].co;uv.data[i].uv=(v[axes[0]],v[axes[1]])
    o.location.x=offset;o['Study']='HighElfWallStudy01';o['Role']=kind;o['InterfaceVersion']='new_visual_draft_1';o['DisplayOffsetX_m']=offset
    ASSETS.append(o);return o

def curve(points,n=24):
    a,b,c,d=[Vector(p) for p in points]
    return [tuple((1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d) for t in [i/n for i in range(n+1)]]

def rib(m,points,width,depth,mat):
    # Crisp chamfered rectangular moulding, with no round pipe-like section.
    pts=[Vector(p) for p in points];verts=[]
    section=[(-.5,-.3),(-.3,-.5),(.3,-.5),(.5,-.3),(.5,.3),(.3,.5),(-.3,.5),(-.5,.3)]
    for i,p in enumerate(pts):
        t=(pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)]).normalized();u=Vector((t.z,0,-t.x)).normalized();v=Vector((0,1,0))
        verts.extend(tuple(p+u*x*width+v*y*depth) for x,y in section)
    faces=[tuple(range(7,-1,-1)),tuple((len(pts)-1)*8+i for i in range(8))]
    for k in range(len(pts)-1):
        for j in range(8):faces.append((k*8+j,k*8+(j+1)%8,(k+1)*8+(j+1)%8,(k+1)*8+j))
    m.part(verts,faces,mat)

def lancet(m,cx,half,bottom,spring,top,y,w,d,mat):
    for sign in [-1,1]:
        pts=[(cx+sign*half,y,bottom),(cx+sign*half,y,spring)]
        pts+=curve([(cx+sign*half,y,spring),(cx+sign*half,y,spring+(top-spring)*.52),(cx+sign*half*.36,y,top-.12),(cx,y,top)],18)[1:]
        rib(m,pts,w,d,mat)

def jewel(m,x,y,z,w,h):
    # Small opaque blue stone inlay: an accent, not a magic/light source.
    m.prism([(x-(w+.025)/2,z),(x,z-(h+.035)/2),(x+(w+.025)/2,z),(x,z+(h+.035)/2)],(y-.006,.012),'Gold')
    verts=[(x,y-.032,z),(x-w/2,y,z),(x,y,z+h/2),(x+w/2,y,z),(x,y,z-h/2),(x,y+.018,z)]
    m.part(verts,[(0,1,2),(0,2,3),(0,3,4),(0,4,1),(5,2,1),(5,3,2),(5,4,3),(5,1,4)],'Azure')

def core_from_source():
    source=PARENT/'WindowResize02.blend'
    assert sha(source)==json.loads((PARENT/'manifest.json').read_text())['source_sha256']
    name='SM_WC01_Wall_A_Window_300x24x320'
    with bpy.data.libraries.load(str(source),link=False) as (a,b):b.objects=[name]
    o=b.objects[0];m=Mesh();polys=[p for p in o.data.polygons if o.data.materials[p.material_index].name=='WC01_Plaster']
    ids=sorted({i for p in polys for i in p.vertices});lookup={v:i for i,v in enumerate(ids)};m.v=[tuple(o.data.vertices[i].co) for i in ids]
    for p in polys:
        m.f.append(tuple(lookup[i] for i in p.vertices));m.m.append('Ivory');m.s.append(False);m.uv.append([tuple(o.data.uv_layers.active.data[i].uv) for i in p.loop_indices])
    bpy.data.objects.remove(o,do_unlink=True)
    return m

def wall(style,offset,core):
    col=bpy.data.collections.new(style);bpy.context.scene.collection.children.link(col)
    prefix='HE01_'+style.split('_')[0];add(core,prefix+'_WallCore',col,offset,'Structure')
    stone=Mesh();gold=Mesh();blue=Mesh();frame=Mesh();glass=Mesh()
    ornate=style.startswith('B')
    # Base and crown run exactly to the end planes; end-face decoration does not overlap adjacent modules.
    for y in [-.035,.255]:
        stone.box((1.5,y,.12),(3,.16,.24),'RecessStone',.006)
        stone.box((1.5,y,.26),(3,.20,.055),'CarvedStone',.004)
        stone.box((1.5,y,3.13),(3,.15,.14),'CarvedStone',.004)
        stone.box((1.5,y,3.015),(3,.11,.055),'CarvedStone',.003)
        gold.box((1.5,y-.077 if y<0 else y+.077,3.095),(2.98,.012,.012),'Gold',.001)
    # Small scale stone courses, restrained lower-wall relief.
    for i in range(6):
        stone.box((.25+i*.5,-.006,.105),(.496,.08,.19),'CarvedStone',.003)
    # Pilasters sit fully inside the module, so neither endpoint owns a duplicate shared post.
    for x in [.20,2.80]:
        stone.box((x,-.08,.43),(.28,.23,.29),'CarvedStone',.005)
        stone.box((x,-.09,2.77),(.25,.22,.12),'CarvedStone',.004)
        stone.box((x,-.075,1.64),(.16 if not ornate else .19,.17,2.12),'CarvedStone',.004)
        for dx in ([-.043,.043] if ornate else [0]):
            rib(gold,[(x+dx,-.166,.59),(x+dx,-.166,2.69)],.009,.008,'Gold')
        stone.box((x,-.08,.60),(.22,.22,.055),'CarvedStone',.004)
        if ornate:
            # Tapered tips below the shared crown, not taller-than-module spires.
            stone.prism([(x-.11,2.83),(x+.11,2.83),(x,3.045)],(-.15,-.04),'CarvedStone')
            jewel(blue,x,-.16,2.84,.055,.13)
    # Sill and real aperture surround; the 65 x 90 cm source opening is unchanged.
    for y in [-.043,.26]:
        frame.box((1.5,y,1.325),(.87,.34,.075),'CarvedStone',.006)
        for x in [1.158,1.842]:frame.box((x,y,1.73),(.065,.13,.79),'CarvedStone',.003)
        pts=[(1.175+i*.65/24,y,2.10+.15*(1-((1.175+i*.65/24-1.5)/.325)**2)) for i in range(25)]
        rib(frame,pts,.060,.115,'CarvedStone')
    # Fine metal glazing bars, a clear independently selectable pane.
    frame.box((1.5,.09,1.77),(.018,.035,.83),'Gold',.001)
    frame.box((1.5,.09,1.79),(.625,.035,.016),'Gold',.001)
    outline=[(1.183,1.358),(1.817,1.358)]+[(1.817-i*.634/24,2.10+.15*(1-((1.817-i*.634/24-1.5)/.325)**2)-.008) for i in range(25)]
    glass.prism(outline,(.115,.125),'ClearGlass')
    # Lancet-shaped stone hood above a small window; window shape/contract remains untouched.
    lancet(stone,1.5,.46,1.29,2.14,2.81,-.075,.083,.13,'CarvedStone')
    lancet(gold,1.5,.465,1.40,2.14,2.81,-.145,.012,.014,'Gold')
    jewel(blue,1.5,-.045,2.49,.075 if not ornate else .11,.16 if not ornate else .24)
    # Two quiet recessed foot panels anchor the opening.
    for x in [.79,2.21]:
        stone.box((x,-.012,.77),(.73,.03,.70),'CarvedStone',.006)
    if ornate:
        lancet(stone,1.5,.56,1.27,2.15,2.97,-.057,.052,.085,'CarvedStone')
        # Slender blind side bays and paired upward-sweeping ribs echo the tower reference.
        for cx in [.70,2.30]:
            lancet(stone,cx,.25,.50,1.87,2.51,-.053,.047,.075,'CarvedStone')
            lancet(gold,cx,.25,.65,1.87,2.51,-.095,.010,.009,'Gold')
            jewel(blue,cx,-.045,1.57,.09,.25)
        for sign in [-1,1]:
            pts=curve([(1.5+sign*1.27,-.09,1.70),(1.5+sign*1.08,-.09,2.19),(1.5+sign*.62,-.09,2.47),(1.5+sign*.10,-.09,2.97)],28)
            rib(stone,pts,.062,.10,'CarvedStone')
            rib(gold,[(x,y-.054,z) for x,y,z in pts],.010,.010,'Gold')
        # Carved petal-shaped relief below the sill, no independent lore motif.
        for s in [-1,1]:
            pts=curve([(1.5,-.06,.42),(1.5+s*.36,-.06,.67),(1.5+s*.25,-.06,.99),(1.5,-.06,1.18)],20)
            rib(stone,pts,.040,.055,'CarvedStone')
        jewel(blue,1.5,-.076,.82,.075,.19)
        for x in [.20,2.80]:
            # Additional bevelled ribs on the pilaster shafts create readable highlights.
            for dx in [-.068,.068]:rib(stone,[(x+dx,-.17,.64),(x+dx,-.17,2.68)],.022,.025,'CarvedStone')
    add(stone,prefix+'_StoneCarving',col,offset)
    add(gold,prefix+'_GoldInlay',col,offset)
    add(blue,prefix+'_BlueInlay',col,offset)
    add(frame,prefix+'_WindowFrame',col,offset,'WindowFrame')
    add(glass,prefix+'_ClearGlass',col,offset,'Glass')
    return col

def camera(name,loc,target,scale):
    d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);bpy.context.scene.collection.objects.link(o)
    o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=scale;d.lens=45
    return o
def text(label,loc,size,col):
    d=bpy.data.curves.new(label,'FONT');d.body=label;d.size=size;d.align_x='CENTER';d.extrude=0
    o=bpy.data.objects.new(label,d);col.objects.link(o);o.location=loc;o.rotation_euler=(math.pi/2,0,0);d.materials.append(MATS['Letter'])

def build():
    ROOT.mkdir(exist_ok=True);(ROOT/'Previews').mkdir(exist_ok=True);(ROOT/'Evidence').mkdir(exist_ok=True)
    if not (ROOT/'Evidence/files_before.json').exists():write('Evidence/files_before.json',snapshot())
    bpy.ops.wm.read_factory_settings(use_empty=True)
    core=core_from_source();materials()
    s=bpy.context.scene;s.name='01_Wandvergleich';s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
    wall('A_Schlicht',0,core);wall('B_Prachtvoll',4.2,core)
    stage=bpy.data.collections.new('Praesentation');s.collection.children.link(stage)
    m=Mesh();m.box((3.6,.2,-.055),(200,200,.1),'Stage');o=m.object('StudioFloor',stage,['Stage'])
    for x,label,sub in [(1.5,'A  /  SCHLICHT','Stein  /  feine Goldlinien'),(5.7,'B  /  PRACHTVOLL','Spitzboegen  /  plastische Reliefs')]:
        m=Mesh();m.box((x,-.13,-.25),(3.22,.90,.50),'Stage');m.object('Display_Base_'+label[0],stage,['Stage'])
        text(label,(x,-.585,-.23),.16,stage)
        # Labels sit on a separate low front plaque, below the wall footprint.
        text(sub,(x,-.585,-.38),.072,stage)
    # Raise presentation floor below plaques; module base still Z0.
    o.location.z=-.48
    cam=camera('01_Aussen_Vergleich',(8,-19,7),(3.6,0,1.42),9.2);s.camera=cam
    camera('02_Innen_Vergleich',(-.4,17,6),(3.6,.12,1.45),9.2)
    camera('03_Detail_Prachtvoll',(7.2,-7,3.7),(5.7,-.05,1.85),3.85)
    camera('04_Front_Orthogonal',(3.6,-16,1.6),(3.6,0,1.6),8.65)
    world=bpy.data.worlds.new('Neutral_Studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.38,.44,.50,1);world.node_tree.nodes['Background'].inputs[1].default_value=.35;s.world=world
    for name,loc,power,size,color in [('Key',(-3,-6,8),1700,7,(1,.92,.80)),('Fill',(8,-1,6),1050,5,(.78,.88,1)),('Daylight',(3,5,6),2100,4,(.90,.96,1))]:
        d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color
        o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((3.6,0,1.5))-o.location).to_track_quat('-Z','Y').to_euler()
    s.render.engine='CYCLES';s.cycles.samples=48;s.cycles.use_denoising=True;s.cycles.max_bounces=8;s.cycles.transmission_bounces=6
    s.render.resolution_x=1600;s.render.resolution_y=1000;s.render.resolution_percentage=100
    s.view_settings.view_transform='AgX';s.render.image_settings.file_format='PNG'
    # Store useful orbit view and material preview. No UI automation or preference changes needed.
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                sp=area.spaces.active;sp.region_3d.view_rotation=cam.rotation_euler.to_quaternion();sp.region_3d.view_location=(3.6,0,1.45);sp.region_3d.view_distance=10;sp.region_3d.view_perspective='PERSP'
                sp.shading.type='MATERIAL';sp.shading.studiolight_rotate_z=.7;sp.overlay.show_overlays=False;sp.lens=48;sp.clip_end=500
    bpy.ops.object.select_all(action='DESELECT')
    for o in ASSETS:o.select_set(True)
    bpy.context.view_layer.objects.active=ASSETS[0]
    # Remove unused source datablocks/images to keep this file self-contained.
    bpy.ops.outliner.orphans_purge(do_recursive=True)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'HighElf_WallVariants_01.blend'))
    assets={o.name:g.audit(o) for o in ASSETS}
    write('manifest.json',dict(status='draft',accepted=False,scope='Blender-only new style study; existing houses, Unreal and prior wall sources unchanged',source='HighElf_WallVariants_01.blend',source_sha256=sha(ROOT/'HighElf_WallVariants_01.blend'),input_source=str(PARENT.relative_to(REPO)/'WindowResize02.blend'),input_sha256=sha(PARENT/'WindowResize02.blend'),reference='User-supplied ivory/gold/ice-blue tower image; visual direction only; no lore or building use assigned',kit_id='HE.WallStudy01',interface_version='new_visual_draft_1',core_cm=[300,24,320],opening_cm=[65,90],sill_cm=135,opening_profile='Same source parabolic head Z210+15*(1-((X-150)/32.5)^2) cm; pointed hood is decorative',join_A_cm=[0,0,0],join_B_cm=[300,0,0],axes='Blender X along wall, Y interior, Z up; UE eventual (100*x,-100*y,100*z)',display_offsets_m={'A':[0,0,0],'B':[4.2,0,0]},assets=assets,materials='Own Blender procedural stone/gold materials, no external image textures. Clear glass shader passes shadow rays; blue accents are opaque inlays, not lights.',collision='Inherited opening dimensions only; no collision bodies or Unreal import in this visual-only study',lods=1,nanite='not applicable; not imported',exports='Not generated in this Blender-only task',pending=['User style choice','Bake/translate Blender procedural materials for Unreal','Optimise decoration and material slots before serial production','Prepare collision and FBX roundtrip only after style selection','Validate in Unreal in a separately authorised integration']))
    print('STUDY_BUILD_OK')

def verify():
    data=json.loads((ROOT/'manifest.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(ROOT/data['source']))
    result={}
    for name,expected in data['assets'].items():
        o=bpy.data.objects[name];actual=g.audit(o)
        assert actual==expected,(name,actual,expected)
        assert actual['nonmanifold_edges']==0 and actual['degenerate_faces']==0 and actual['degenerate_uv_triangles']==0,name
        assert all(abs(v-1)<1e-6 for v in o.scale);assert sum(abs(v) for v in o.rotation_euler)<1e-6
        assert actual['bounds_m'][0][0]>=-1e-5 and actual['bounds_m'][1][0]<=3.00001,name
        assert actual['bounds_m'][0][2]>=-1e-5 and actual['bounds_m'][1][2]<=3.20001,name
        result[name]=actual
    # Ray tests in local module coordinates verify an actual empty aperture and a separately removable pane.
    rays={}
    for p in ['HE01_A','HE01_B']:
        core=bpy.data.objects[p+'_WallCore'];glass=bpy.data.objects[p+'_ClearGlass']
        tests={}
        for label,x,z,blocked in [('opening',1.5,1.6,False),('left_infill',1.0,1.6,True),('sill',1.5,1.2,True),('head',1.5,2.4,True)]:
            hit=core.ray_cast(Vector((x,-1,z)),Vector((0,1,0)))[0];assert hit==blocked,(p,label);tests[label]=hit
        assert glass.ray_cast(Vector((1.6,-1,1.7)),Vector((0,1,0)))[0];rays[p]=tests
    assert not [i for i in bpy.data.images if i.source=='FILE' and i.users], 'External image dependency'
    original=core_from_source()
    signature=lambda verts,faces:sorted(tuple(sorted(tuple(round(float(v),7) for v in verts[i]) for i in f)) for f in faces)
    expected=signature(original.v,original.f)
    for p in ['HE01_A','HE01_B']:
        me=bpy.data.objects[p+'_WallCore'].data
        assert signature([v.co for v in me.vertices],[p.vertices[:] for p in me.polygons])==expected
    glassmat=bpy.data.materials['HEWS01_ClearGlass'];bs=glassmat.node_tree.nodes.get('Principled BSDF')
    assert bs.inputs['Transmission Weight'].default_value==1
    write('Evidence/verification.json',dict(status='passed',blender=bpy.app.version_string,source_reopened=True,source_core_triangle_geometry_unchanged=True,all_components_closed=True,degenerate_geometry_or_UVs=0,unity_scale=True,core_ray_tests=rays,glass_transmission=1,assets=result))
    data['status']='review_ready';write('manifest.json',data);print('STUDY_VERIFY_OK')

def render():
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'HighElf_WallVariants_01.blend'));s=bpy.context.scene
    names=sys.argv[sys.argv.index('--')+2:]
    for name in names:
        s.camera=bpy.data.objects[name];s.render.filepath=str(ROOT/'Previews'/(name+'.png'));bpy.ops.render.render(write_still=True)

if __name__=='__main__':{'build':build,'verify':verify,'render':render}[sys.argv[sys.argv.index('--')+1]]()
