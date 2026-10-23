"""Independent selectable wall samples and crafted props. Never opens a house source."""
from pathlib import Path
import sys,json,math,hashlib
sys.dont_write_bytecode=True
import bpy,bmesh,numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[5]
sys.path.insert(0,str(REPO/'AssetSources/Architecture/EB_Blatthof_R255_R640/WallInner_R255_A30_H280/Refiner/HouseStudy_B01'))
import build_house as lib
Mesh=lib.Mesh;ASSETS={};MATS={}
PROFILE=json.loads((REPO/'AssetSources/Calibration/BlenderUE01/unreal_import_profile.json').read_text())

def write(name,data):(ROOT/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def noise(n,f,rng):
    grid=rng.random((f,f),dtype=np.float32)
    a=np.arange(n,dtype=np.float32)*f/n;i=a.astype(int);t=a-i;t=t*t*(3-2*t)
    lo=grid[i[:,None]%f,i[None,:]%f]*(1-t[None,:])+grid[i[:,None]%f,(i[None,:]+1)%f]*t[None,:]
    hi=grid[(i[:,None]+1)%f,i[None,:]%f]*(1-t[None,:])+grid[(i[:,None]+1)%f,(i[None,:]+1)%f]*t[None,:]
    return (lo*(1-t[:,None])+hi*t[:,None])-.5

def textures():
    rng=np.random.default_rng(231001)
    for family in ['Timber','Plaster','Stone','Iron','Bronze']:
        n=2048 if family=='Timber' else 1024 if family in ['Plaster','Stone'] else 512
        u,v=np.meshgrid(np.arange(n,dtype=np.float32)/n,np.arange(n,dtype=np.float32)/n)
        coarse=noise(n,4,rng);med=noise(n,32,rng);fine=noise(n,256,rng)
        metal=0
        if family=='Timber':
            flow=u+.022*coarse+.007*np.sin(2*np.pi*v*3)
            knot=np.zeros_like(u)
            for cx,cy,rx,ry in [(.24,.28,.045,.115),(.72,.78,.032,.08)]:
                dx=(u-cx+.5)%1-.5;dy=(v-cy+.5)%1-.5;r=np.sqrt((dx/rx)**2+(dy/ry)**2)
                fall=np.exp(-r*r*.5);flow+=.027*fall*np.sin(np.arctan2(dy/ry,dx/rx));knot+=fall
            pores=np.maximum(0,np.sin(2*np.pi*flow*157)+.4*med-.82)
            grain=.34*np.sin(2*np.pi*flow*43)+.13*np.sin(2*np.pi*flow*113)+coarse*.5
            h=grain*.00022-pores*.00038-knot*.00022+fine*.00008
            color=np.array([.155,.076,.030])*(1+.37*grain[:,:,None]-.23*knot[:,:,None]-.24*pores[:,:,None])
            rough=.48+.15*med+.09*pores+.05*knot
        elif family=='Plaster':
            trowel=noise(n,9,rng)
            pits=np.maximum(0,-fine-.28)
            h=.00045*med+.00035*fine+.00020*trowel-pits*.001
            color=np.array([.62,.55,.43])*(1+.09*coarse[:,:,None]+.025*med[:,:,None])
            rough=.86+.09*fine+.05*trowel
        elif family=='Stone':
            vein=np.exp(-((np.sin(2*np.pi*(u*3+v*2+.7*coarse)))/.085)**2)
            h=.0015*med+.00055*fine-.0003*vein
            color=np.array([.30,.285,.245])*(1+.20*coarse[:,:,None]+.15*med[:,:,None]-.06*vein[:,:,None])
            rough=.78+.14*med+.07*fine
        else:
            metal=.85 if family=='Iron' else .78
            base=[.045,.052,.055] if family=='Iron' else [.32,.18,.065]
            h=.00013*med+.00008*fine
            color=np.array(base)*(1+.28*coarse[:,:,None]+.13*fine[:,:,None]);rough=.39+.13*med+.07*fine
        dx=(np.roll(h,-1,1)-np.roll(h,1,1))*n/2;dy=(np.roll(h,-1,0)-np.roll(h,1,0))*n/2
        nm=np.stack([-dx,-dy,np.ones_like(h)],-1);nm/=np.linalg.norm(nm,axis=-1)[:,:,None]
        mat=bpy.data.materials.new('WC01_'+family);mat.use_nodes=True;MATS[family]=mat
        bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Metallic'].default_value=metal
        for channel,pixels,space in [('BaseColor',color,'sRGB'),('Roughness',rough,'Non-Color'),('Normal',nm*.5+.5,'Non-Color')]:
            rgba=np.ones((n,n,4),np.float32);rgba[:,:,:3]=np.clip(pixels[:,:,None] if pixels.ndim==2 else pixels,0,1)
            im=bpy.data.images.new('T_WC01_'+family+'_'+channel,n,n,alpha=False);im.colorspace_settings.name=space
            im.pixels.foreach_set(rgba.ravel());im.file_format='PNG';im.filepath_raw=str(ROOT/'Textures'/(im.name+'.png'));im.save();im.filepath='//Textures/'+im.name+'.png'
            node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=im
            if channel=='Normal':
                normal=mat.node_tree.nodes.new('ShaderNodeNormalMap');mat.node_tree.links.new(node.outputs['Color'],normal.inputs['Color']);mat.node_tree.links.new(normal.outputs['Normal'],bs.inputs['Normal'])
            else:mat.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color' if channel=='BaseColor' else 'Roughness'])
    for family,color in [('Glass',(.98,.995,1,1)),('Glow',(1,.5,.14,1))]:
        mat=bpy.data.materials.new('WC01_'+family);mat.use_nodes=True;MATS[family]=mat
        bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=color
        if family=='Glass':bs.inputs['Transmission Weight'].default_value=1;bs.inputs['IOR'].default_value=1.45;bs.inputs['Roughness'].default_value=.025
        else:bs.inputs['Emission Color'].default_value=color;bs.inputs['Emission Strength'].default_value=4
    lib.MATERIALS.clear();lib.MATERIALS.update(MATS)

def box(c,s):m=Mesh();m.box(c,s,'Plaster');return m
def add(name,m,slots,ucx,description,kind='Wall'):
    name='SM_WC01_'+name;o=m.object(name,bpy.context.scene.collection,slots);bodies=[]
    # Curved tube quads can collapse under a single planar UV projection. Resolve
    # those faces on the final, explicit triangles rather than hiding a UV defect.
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
    uv=o.data.uv_layers.active
    for p in o.data.polygons:
        a,b,c=[uv.data[i].uv.copy() for i in p.loop_indices]
        if abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))<1e-12:
            axis=max(range(3),key=lambda k:abs(p.normal[k]));axes=[k for k in range(3) if k!=axis]
            for i in p.loop_indices:
                v=o.data.vertices[o.data.loops[i].vertex_index].co;uv.data[i].uv=(v[axes[0]],v[axes[1]])
    for i,c in enumerate(ucx):
        b=c.object('UCX_'+name+'_%02d'%i,bpy.context.scene.collection,['Plaster']);b.hide_render=True;b.hide_set(True);bodies.append(b)
    o['KitId']='EC.WallCatalogue01';o['Description']=description
    ASSETS[name]=dict(obj=o,ucx=bodies,description=description,kind=kind)
    return name

def beam(m,a,b,w,d,mat='Timber'):
    # Rectangular joinery, unlike inflated round tubes. Grain runs along each beam.
    a,b=Vector(a),Vector(b);z=(b-a).normalized();y=Vector((0,1,0));x=y.cross(z).normalized()
    verts=[tuple(p+sx*x*w/2+sy*y*d/2) for p in [a,b] for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    faces=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    m.part(verts,faces,mat)
    first=len(m.uv)-6
    for j,face in enumerate(faces):
        axes=(x,y) if j<2 else ((x,z) if j in [2,4] else (y,z))
        m.uv[first+j]=[(Vector(verts[k]).dot(axes[0]),Vector(verts[k]).dot(axes[1])) for k in face]

def peg(m,x,y,z,axis='Y',r=.014):
    if axis=='Y':p=[(x,y-.008,z),(x,y+.008,z)]
    else:p=[(x,y,z-.008),(x,y,z+.008)]
    m.tube(p,r,'Timber',8)

def wall(style,window):
    m=Mesh();coll=[]
    top=lambda x:2.24+.28*max(0,1-((x-1.5)/.60)**2)
    def fill(x0,x1,z0,z1):
        c=((x0+x1)/2,.12,(z0+z1)/2);s=(x1-x0,.24,z1-z0)
        m.box(c,s,'Plaster');coll.append(box(c,s))
    if not window:fill(0,3,0,3.2)
    else:
        fill(0,.90,0,3.2);fill(2.10,3,0,3.2);fill(.90,2.10,0,1.0)
        xs=np.linspace(.90,2.10,13)
        for a,b in zip(xs,xs[1:]):
            poly=[(float(a),top(a)),(float(b),top(b)),(float(b),3.2),(float(a),3.2)]
            m.prism(poly,(0,.24),'Plaster');c=Mesh();c.prism(poly,(0,.24),'Plaster');coll.append(c)
    # Start owns the upright; exact X0/X300 ends remain unchanged across all variants.
    for y in [-.035,.255]:
        m.box((.08,y,1.60),(.16,.075,3.2),'Timber',.003)
        m.box((1.5,y,3.115),(3,.075,.17),'Timber',.003)
        m.box((1.5,y,.21),(3,.075,.12),'Timber',.003)
    if style in ['B','C']:
        # Shallow tapered knee braces, readable from play distance, no ornamental lore motifs.
        for x,d in [(.18,1),(2.90,-1)]:
            points=[(x+d*.68*t,-.055,2.46+.56*t+.08*math.sin(math.pi*t)) for t in np.linspace(0,1,7)]
            for a,b in zip(points,points[1:]):beam(m,a,b,.065,.08)
            for z in [2.53,2.99]:peg(m,x,-.102,z)
        if not window:
            m.box((1.50,-.035,1.65),(.12,.075,2.87),'Timber',.003)
            for x in [.83,2.22]:m.box((x,-.036,.92),(1.22,.075,.085),'Timber',.002)
    if style=='C':
        # Real staggered masonry, each face subtly different. Backed by the solid wall core.
        rng=np.random.default_rng(44)
        for row in range(3):
            edges=sorted(set([0,3]+[x for x in np.arange(-.25+(.25 if row%2 else 0),3.5,.5) if 0<x<3]))
            for a,b in zip(edges,edges[1:]):
                m.box(((a+b)/2,-.035,.10+row*.19),(b-a-.012,.095,.178),'Stone',.009+float(rng.random())*.003)
        m.box((1.5,-.055,.60),(3,.12,.075),'Stone',.005)
    else:
        for i in range(6):m.box((.25+i*.5,-.016,.07),(.487,.08,.14),'Stone',.006)
    for x in [.08]:
        for z in [.39,2.86,3.11]:peg(m,x,-.082,z)
    return add('Wall_'+style+('_Window' if window else '_Solid')+'_300x24x320',m,['Plaster','Timber','Stone'],coll,
        {'A':'Restrained lime-plaster, clean timber joints','B':'Exposed timber framing and shaped knee braces','C':'Crafted staggered stone plinth and timber framing'}[style]+('; common real window opening' if window else '; closed panel'))

def window():
    m=Mesh();c=[]
    # Local origin at sill center. All window walls accept this exact independent assembly.
    left,right=-.60,.60;spring=1.24
    m.box((0,.04,-.015),(1.40,.40,.095),'Stone',.006)
    for x in [left,right]:m.box((x,.12,.61),(.085,.28,1.25),'Timber',.003)
    points=[(float(x),-.018,spring+.28*max(0,1-(x/.60)**2)) for x in np.linspace(left,right,17)]
    for a,b in zip(points,points[1:]):beam(m,a,b,.075,.085)
    m.box((0,-.018,.66),(.042,.07,1.32),'Timber',.002)
    for z in [.53,1.05]:m.box((0,-.018,z),(1.13,.06,.035),'Timber',.002)
    for x in [-.49,.49]:
        for z in [.08,1.14]:peg(m,x,-.08,z,r=.010)
    # Two interior wooden catches, visible on close inspection.
    for x in [-.055,.055]:m.box((x,.282,.78),(.025,.025,.12),'Bronze',.002)
    add('WindowFrame_140x40x157',m,['Timber','Stone','Bronze'],[], 'Independent sill, rebated jamb, curved head, glazing bars and two catches','Window')
    m=Mesh();outline=[(-.557,.04),(.557,.04)]+[(float(x),spring+.28*max(0,1-(x/.60)**2)-.035) for x in np.linspace(.557,-.557,17)]
    m.prism(outline,(.125,.145),'Glass');c=Mesh();c.prism(outline,(.125,.145),'Plaster')
    add('WindowGlass_Clear_112x2x145',m,['Glass'],[c],'Separate closed 2cm clear pane, no extra reflection plane','Glass')

def furniture():
    m=Mesh();coll=[]
    for i in range(5):
        y=-.40+i*.20;m.box((0,y,.755),(1.8,.196,.05),'Timber',.003)
        for x in [-.68,.68]:peg(m,x,y,.782,'Z',.008)
    for x in [-.71,.71]:
        for y in [-.31,.31]:
            m.box((x,y,.35),(.09,.09,.70),'Timber',.003);coll.append(box((x,y,.35),(.09,.09,.70)))
            m.box((x,y,.68),(.11,.11,.09),'Timber',.002)
    for y in [-.32,.32]:m.box((0,y,.64),(1.50,.055,.14),'Timber',.003)
    for x in [-.71,.71]:
        m.box((x,0,.25),(.055,.67,.07),'Timber',.002)
        for d in [-1,1]:beam(m,(x,d*.26,.49),(x-d*.22,d*.26,.66),.047,.047)
    m.box((0,0,.25),(1.43,.055,.065),'Timber',.002)
    coll.append(box((0,0,.755),(1.8,1,.05)))
    add('Table_180x100x78',m,['Timber'],coll,'Five real boards, pegged top, aprons, stretcher and braced legs','Furniture')
    m=Mesh();coll=[]
    for i in range(4):m.box((0,-.18+i*.12,.455),(.48,.116,.045),'Timber',.003)
    for x in [-.18,.18]:
        for y in [-.18,.18]:
            m.box((x,y,.21),(.055,.055,.42),'Timber',.002);coll.append(box((x,y,.21),(.055,.055,.42)))
        beam(m,(x,.18,.42),(x,.25,.98),.055,.055)
        m.box((x,0,.18),(.035,.36,.035),'Timber',.001)
    for z in [.68,.87]:m.box((0,.224+(z-.68)*.125,z),(.36,.045,.075),'Timber',.003)
    for x in [-.18,.18]:
        for z in [.68,.87]:peg(m,x,.20,z,r=.009)
    for y in [-.18,.18]:m.box((0,y,.37),(.36,.04,.08),'Timber',.002)
    coll.extend([box((0,0,.455),(.48,.48,.045)),box((0,.24,.74),(.42,.065,.50))])
    add('Chair_48x49x101',m,['Timber'],coll,'Board seat, angled back, slats and pegged joins; no sitting gameplay','Furniture')
    m=Mesh()
    # Mount pivot is the actual rear plate contact; light points away from the wall along -Y.
    m.box((0,-.018,0),(.12,.036,.34),'Iron',.005)
    for z in [-.12,.12]:m.tube([(0,-.035,z),(0,-.045,z)],.014,'Bronze',12)
    arm=[(0,-.04,.10),(0,-.14,.14),(0,-.29,.19),(0,-.40,.15),(0,-.40,.08)]
    m.tube(arm,.014,'Iron',10)
    for z in [-.33,-.055]:m.box((0,-.40,z),(.22,.22,.035),'Bronze',.004)
    for x in [-.086,.086]:
        for y in [-.486,-.314]:m.tube([(x,y,-.31),(x*.84,-.40+(y+.40)*.84,-.07)],.009,'Bronze',8)
    m.prism([(-.14,-.05),(.14,-.05),(.09,.025),(-.09,.025)],(-.54,-.26),'Bronze')
    for i in range(3):m.box((0,-.40,-.40-i*.025),(.14-i*.035,.14-i*.035,.018),'Bronze',.002)
    m.tube([(0,-.40,-.30),(0,-.40,-.16)],.030,'Glow',12)
    add('WallLamp_28x54x48',m,['Iron','Bronze','Glow'],[], 'Wall mount, curled support, vented hood, open cage and visible luminous core; no fuel canon','Lamp')

def audit(o):
    me=o.data;me.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(me)
    non=sum(not e.is_manifold for e in bm.edges);deg=sum(f.calc_area()<1e-10 for f in bm.faces)
    assert not non and not deg,(o.name,non,deg)
    assert bm.calc_volume(signed=True)>0,(o.name,'volume');bm.free()
    uv=me.uv_layers.active;assert uv
    for t in me.loop_triangles:
        a,b,c=[uv.data[i].uv.copy() for i in t.loops];assert abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))>1e-12,o.name
    return dict(triangles=len(me.loop_triangles),vertices=len(me.vertices),slots=[m.name.removeprefix('WC01_') for m in me.materials],
        bounds_m=[[min(v.co[k] for v in me.vertices) for k in range(3)],[max(v.co[k] for v in me.vertices) for k in range(3)]],
        nonmanifold_edges=non,degenerate_faces=deg,degenerate_uv_triangles=0)

def build():
    bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.name='Module_Library';s.unit_settings.system='METRIC'
    textures()
    for style in ['A','B','C']:
        for glazed in [False,True]:wall(style,glazed)
    window();furniture()
    settings=dict(PROFILE['export_settings']);settings['object_types']=set(settings['object_types'])
    bpy.ops.preferences.addon_enable(module='io_scene_fbx');assets={}
    for name,it in ASSETS.items():
        for o in s.objects:o.select_set(False)
        for o in [it['obj']]+it['ucx']:o.hide_set(False);o.select_set(True)
        bpy.context.view_layer.objects.active=it['obj']
        bpy.ops.export_scene.fbx(filepath=str(ROOT/'Exports'/(name+'.fbx')),**settings)
        for o in it['ucx']:o.hide_set(True)
        assets[name]=dict(**audit(it['obj']),ucx_hulls=len(it['ucx']),description=it['description'],kind=it['kind'],fbx_sha256=sha(ROOT/'Exports'/(name+'.fbx')))
        for c in it['ucx']:audit(c)
    # Separate preview scene: linked instances, sources and pivots remain at zero.
    show=bpy.data.scenes.new('Wall_Comparison');show.unit_settings.system='METRIC';bpy.context.window.scene=show
    places=[]
    def place(name,loc,yaw=0):
        o=ASSETS[name]['obj'].copy();o.data=ASSETS[name]['obj'].data;show.collection.objects.link(o);o.location=loc;o.rotation_euler.z=math.radians(yaw)
        places.append(dict(module=name,location_m=list(loc),yaw_blender=yaw));return o
    for col,style in enumerate(['A','B','C']):
        x=col*4.2
        place('SM_WC01_Wall_'+style+'_Solid_300x24x320',(x,0,0))
        place('SM_WC01_Wall_'+style+'_Window_300x24x320',(x,4.2,0))
        for n in ['WindowFrame_140x40x157','WindowGlass_Clear_112x2x145']:place('SM_WC01_'+n,(x+1.5,4.2,1.0))
    place('SM_WC01_Table_180x100x78',(5.7,2.0,0));place('SM_WC01_Chair_48x49x101',(5.7,1.0,0),180)
    place('SM_WC01_WallLamp_28x54x48',(4.7,0,1.95))
    # Explicit snap example: two panels touch at X=3, never attached to an existing house.
    place('SM_WC01_Wall_A_Solid_300x24x320',(0,8.2,0));place('SM_WC01_Wall_B_Solid_300x24x320',(3,8.2,0))
    for n,loc in [('Table_180x100x78',(10,7,0)),('Chair_48x49x101',(11.5,7,0)),('WindowFrame_140x40x157',(7,8.2,1)),('WindowGlass_Clear_112x2x145',(8.6,8.2,1))]:place('SM_WC01_'+n,loc)
    s.world=None;show.world=bpy.data.worlds.new('ReviewWorld');show.world.use_nodes=True;show.world.node_tree.nodes['Background'].inputs[0].default_value=(.22,.27,.34,1);show.world.node_tree.nodes['Background'].inputs[1].default_value=.35
    ground=Mesh();ground.box((5.7,4.5,-.08),(15,13,.16),'Stone');ground.object('Review_Ground',show.collection,['Stone'])
    for name,loc,energy,size in [('Key',(-1,-5,9),2400,7),('Fill',(12,2,7),1500,6)]:
        light=bpy.data.lights.new(name,'AREA');light.energy=energy;light.shape='DISK';light.size=size;o=bpy.data.objects.new(name,light);show.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((5,3,1.4))-o.location).to_track_quat('-Z','Y').to_euler()
    sun=bpy.data.lights.new('Sun','SUN');sun.energy=2;o=bpy.data.objects.new('Sun',sun);show.collection.objects.link(o);o.rotation_euler=(.5,-.4,-.4)
    cam=bpy.data.objects.new('ReviewCamera',bpy.data.cameras.new('ReviewCamera'));show.collection.objects.link(cam);show.camera=cam
    show.render.engine='CYCLES';show.cycles.samples=32;show.cycles.use_denoising=True;show.render.resolution_x=1500;show.render.resolution_y=1000;show.render.resolution_percentage=100
    show.view_settings.view_transform='AgX'
    for area in bpy.context.screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.clip_end=200;area.spaces.active.region_3d.view_distance=18;area.spaces.active.region_3d.view_location=(5.5,3,1.3)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'WallCatalogue01.blend'),relative_remap=False)
    write('manifest.json',dict(status='draft',accepted=False,kit_id='EC.WallCatalogue01',interface_version='draft_1',
        source='WallCatalogue01.blend',source_sha256=sha(ROOT/'WallCatalogue01.blend'),assets=assets,placements=places,
        material_families=list(MATS),export_profile=PROFILE,coordinates='UE_cm=(100*B.x,-100*B.y,100*B.z)',
        wall_contract=dict(width_cm=300,core_depth_cm=24,height_cm=320,pivot='lower start corner [0,0,0]',
            start=dict(position_cm=[0,0,0],outward_direction=[-1,0,0]),end=dict(position_cm=[300,0,0],outward_direction=[1,0,0]),
            seam_ownership='start owns timber upright; no end upright; closing post/corner module not yet supplied',
            window_insert_cm=[150,0,100],opening='X90..210, sill Z100; head Z224+28*(1-((X-150)/60)^2) cm',
            boundary='new provisional straight kit; not a drop-in replacement for study A/B or R255'),
        texture_uv='Intentional tile overlaps, 1 texture repeat per metre on planar components; beam grain aligned with longest/beam axis',
        scope='Independent comparison panels and props; no house source opened or modified; no culture canon'))
    print('CATALOGUE_BUILD_OK',len(assets))

def verify():
    data=json.loads((ROOT/'manifest.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(ROOT/data['source']))
    s=bpy.data.scenes['Module_Library'];result={}
    assert not [i.filepath for i in bpy.data.images if i.source=='FILE' and not Path(bpy.path.abspath(i.filepath)).is_file()]
    original={n:audit(s.objects[n]) for n in data['assets']}
    for name,info in data['assets'].items():
        bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.preferences.addon_enable(module='io_scene_fbx')
        bpy.ops.import_scene.fbx(filepath=str(ROOT/'Exports'/(name+'.fbx')),use_anim=False,use_image_search=False)
        o=next(o for o in bpy.context.scene.objects if o.type=='MESH' and not o.name.startswith('UCX_'));v=audit(o)
        assert v['triangles']==original[name]['triangles'] and v['slots']==original[name]['slots']
        err=max(abs(v['bounds_m'][i][k]-original[name]['bounds_m'][i][k]) for i in range(2) for k in range(3));assert err<1e-5
        assert sum(o.name.startswith('UCX_') for o in bpy.context.scene.objects)==info['ucx_hulls']
        result[name]=dict(bounds_error_m=err,**v)
    write('Evidence/blender_verification.json',dict(status='passed',source_reopened=True,all_textures_resolved=True,blender=bpy.app.version_string,assets=result))
    print('CATALOGUE_VERIFY_OK',len(result))

def render():
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'WallCatalogue01.blend'));s=bpy.data.scenes['Wall_Comparison'];bpy.context.window.scene=s
    views=dict(overview=((15,-14,11),(5.6,3,1.3)),walls=((9,-9,5.2),(5.6,0,1.6)),windows=((10,1,4.0),(5.8,4.2,1.7)),joinery=((6.9,-1.5,2.8),(4.9,0,2.7)),furniture=((7.6,3.3,2.6),(5.7,1.8,.60)),lamp=((5.5,-1,2.0),(4.7,-.26,1.8)),lamp_night=((5.5,-1,2.0),(4.7,-.26,1.8)))
    views['comparison']=((5.7,-12,4.1),(5.7,0,1.5))
    name=sys.argv[-1];pos,target=views[name];s.camera.location=pos;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=43 if name=='overview' else 52
    if name=='comparison':
        s.camera.data.type='ORTHO';s.camera.data.ortho_scale=12.8;s.render.resolution_y=700
        for o in s.objects:
            if o.type=='MESH' and o.name!='Review_Ground':
                o.hide_render=not (o.name.startswith('SM_WC01_Wall_') and '_Solid_' in o.name and abs(o.location.y)<1e-6)
    if name=='lamp_night':
        for o in s.objects:
            if o.type=='LIGHT':o.data.energy=0
            if o.type=='MESH' and o.get('Description','').startswith('Wall mount'):o.visible_shadow=False
        s.world.node_tree.nodes['Background'].inputs[1].default_value=.015
        light=bpy.data.lights.new('FixtureLight','POINT');light.energy=12;light.color=(1,.60,.30);light.shadow_soft_size=.03
        o=bpy.data.objects.new('FixtureLight',light);s.collection.objects.link(o);o.location=(4.7,-.40,1.72)
    s.render.filepath=str(ROOT/'Previews'/('Blender_'+name+'.png'));bpy.ops.render.render(write_still=True)

if __name__=='__main__':
    mode=sys.argv[sys.argv.index('--')+1]
    {'build':build,'verify':verify,'render':render}[mode]()
