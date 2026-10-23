"""B03 editable house copy, original furniture, partitions and physically scaled PBR maps."""
from pathlib import Path
import bpy,bmesh,numpy as np,sys,json,math,hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[6]
sys.path.insert(0,str(ROOT.parent));import build_house as old
Mesh=old.Mesh
MATS={};ASSETS={};PLACEMENTS=[]
PROFILE=json.loads((REPO/'AssetSources/Calibration/BlenderUE01/unreal_import_profile.json').read_text())

def write(name,value):
    p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def maps():
    """Tileable source maps, height-derived tangent normals; no photo or AI reference copying."""
    n=1024;u,v=np.meshgrid(np.arange(n,dtype=np.float32)/n,np.arange(n,dtype=np.float32)/n)
    rng=np.random.default_rng(2303)
    def noise(freqs):
        a=np.zeros_like(u)
        for f,w in freqs:
            for _ in range(4):
                k,l=rng.integers(1,f+1,2);a+=w/4*np.sin(2*np.pi*(k*u+l*v)+rng.random()*6.283)
        return a
    low=noise([(2,.5),(5,.3),(12,.2)]);fine=noise([(32,.5),(91,.3),(223,.2)])
    grain=np.sin(2*np.pi*(u*37+.20*np.sin(2*np.pi*v)+.07*np.sin(2*np.pi*v*7)))
    grain2=np.sin(2*np.pi*(u*133+.45*np.sin(2*np.pi*v*2)))
    for family in ['Plaster','Timber','Stone','Jade','Floor','Linen','Blanket','Iron','Bronze','Book','Flame']:
        metal=0;normalamp=.0004
        if family=='Plaster':
            pattern=.50*low+.20*fine;rgb=np.array([.57,.53,.455])*(1+pattern[:,:,None]*.19)
            h=.35*low+.65*fine;rough=.88+.06*fine;normalamp=.00045
        elif family in ('Timber','Floor'):
            p=.42*grain+.19*grain2+.42*low
            seam=np.exp(-(np.sin(np.pi*u*8)/.055)**2) if family=='Floor' else np.zeros_like(u)
            board=np.floor(u*8);tint=.07*np.sin(board*2.7)+.03*np.cos(board*5.2)
            base=[.20,.12,.065] if family=='Timber' else [.27,.185,.10]
            rgb=np.array(base)*(1+p[:,:,None]*.32+tint[:,:,None]-.5*seam[:,:,None]);h=p-.8*seam
            rough=.58+.10*low+.06*seam;normalamp=.00065
        elif family=='Stone':
            # Four staggered courses per 2 m tile; modest mortar recess, not a noisy cobble pattern.
            row=np.floor(v*4);xx=(u*3+(row%2)*.5)%1;yy=(v*4)%1
            joint=(np.minimum(xx,1-xx)<.015)|(np.minimum(yy,1-yy)<.018)
            tone=.13*np.sin(np.floor(u*3+(row%2)*.5)*3+row*1.7)+.09*low+.03*fine
            rgb=np.array([.32,.31,.275])*(1+tone[:,:,None]);rgb[joint]*=.66
            h=.23*low+.14*fine-joint*.55;rough=.82+.07*fine;normalamp=.0014
        elif family=='Jade':
            # Small staggered roof courses: a visible scale cue replaces smooth uniform roof paint.
            row=np.floor(v*8);xx=(u*6+(row%2)*.5)%1;yy=(v*8)%1
            seam=(yy<.027)|(xx<.023);tile=.07*np.sin(np.floor(u*6+(row%2)*.5)*2.3+row*4.1)
            rgb=np.array([.075,.16,.14])*(1+tile[:,:,None]+.10*low[:,:,None]);rgb[seam]*=.55
            h=.15*low+.13*yy-seam*.45;rough=.69+.08*low;normalamp=.0011
        elif family in ('Linen','Blanket'):
            weave=np.sin(2*np.pi*u*256)*np.sin(2*np.pi*v*256)
            base=[.73,.66,.50] if family=='Linen' else [.14,.255,.245]
            stripe=(np.sin(2*np.pi*u*8)>.85)*.07 if family=='Blanket' else 0
            rgb=np.array(base)*(1+.08*low[:,:,None]+.035*weave[:,:,None])+np.asarray(stripe)[...,None] if not np.isscalar(stripe) else np.array(base)*(1+.08*low[:,:,None]+.035*weave[:,:,None])
            h=.10*weave;rough=.92+.035*fine;normalamp=.00006
        else:
            base,metal,roughness={'Iron':([.045,.052,.05],.85,.43),'Bronze':([.31,.19,.075],.78,.35),
                'Book':([.22,.105,.055],0,.78),'Flame':([1,.32,.025],0,.6)}[family]
            rgb=np.array(base)*(1+.12*low[:,:,None]);h=.1*fine;rough=roughness+.045*fine;normalamp=.00008
        dx=(np.roll(h,-1,1)-np.roll(h,1,1))*n/2*normalamp
        dy=(np.roll(h,-1,0)-np.roll(h,1,0))*n/2*normalamp
        normal=np.stack([-dx,-dy,np.ones_like(h)],-1);normal/=np.linalg.norm(normal,axis=-1)[:,:,None]
        mat=bpy.data.materials.new('B03_'+family);mat.use_nodes=True;MATS[family]=mat
        bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Metallic'].default_value=metal
        bs.inputs['Specular IOR Level'].default_value=.32
        for channel,pixels,space in [('BaseColor',rgb,'sRGB'),('Roughness',rough,'Non-Color'),('Normal',normal*.5+.5,'Non-Color')]:
            if family in ('Iron','Bronze','Book','Flame') and channel=='Normal':continue
            rgba=np.ones((n,n,4),np.float32)
            rgba[:,:,:3]=np.clip(pixels[:,:,None] if pixels.ndim==2 else pixels,0,1)
            im=bpy.data.images.new('T_EH03_'+family+'_'+channel,n,n,alpha=False)
            im.colorspace_settings.name=space;im.pixels.foreach_set(rgba.ravel())
            im.file_format='PNG';im.filepath_raw=str(ROOT/'Textures'/(im.name+'.png'));im.save()
            im.filepath='//Textures/'+im.name+'.png'
            node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=im
            if channel=='Normal':
                nm=mat.node_tree.nodes.new('ShaderNodeNormalMap');mat.node_tree.links.new(node.outputs['Color'],nm.inputs['Color']);mat.node_tree.links.new(nm.outputs['Normal'],bs.inputs['Normal'])
            else:mat.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color' if channel=='BaseColor' else 'Roughness'])
        if family=='Flame':bs.inputs['Emission Color'].default_value=(1,.38,.035,1);bs.inputs['Emission Strength'].default_value=3
    old.MATERIALS.clear();old.MATERIALS.update(MATS)

def box(c,s):
    m=Mesh();m.box(c,s,'Plaster');return m
def add(name,m,slots,colliders,description):
    name='SM_EH03_'+name
    o=m.object(name,bpy.context.scene.collection,slots);bodies=[]
    for i,part in enumerate(colliders):
        body=part.object('UCX_'+name+'_%02d'%i,bpy.context.scene.collection,['Plaster']);body.hide_render=True;body.display_type='WIRE';bodies.append(body)
    o['KitId']='EH.HouseB.Musterhaus03';o['Description']=description
    ASSETS[name]=dict(obj=o,ucx=bodies,description=description)
    return name
def furniture():
    # Millimetre bevels on joinery, flat panel normals, no inflated all-over smoothing.
    m=Mesh()
    for i in range(5):m.box((0,-.4+i*.2,.735),(1.8,.196,.07),'Timber',.003)
    for x in [-.73,.73]:
        for y in [-.31,.31]:m.box((x,y,.35),(.085,.085,.70),'Timber',.003)
    for y in [-.32,.32]:m.box((0,y,.63),(1.48,.06,.13),'Timber',.002)
    add('Table_180x100x77',m,['Timber'],[box((0,0,.385),(1.8,1,.77))],'Five-board dining table, lower central pivot')
    m=Mesh();m.box((0,0,.445),(.47,.49,.055),'Timber',.003)
    for x in [-.18,.18]:
        for y in [-.18,.18]:m.box((x,y,.21),(.055,.055,.42),'Timber',.002)
        m.box((x,.21,.68),(.055,.055,.52),'Timber',.002)
    for z in [.64,.77,.90]:m.box((0,.21,z),(.36,.045,.065),'Timber',.002)
    add('Chair_47x49x94',m,['Timber'],[box((0,0,.24),(.47,.49,.48)),box((0,.21,.71),(.47,.06,.46))],'Open slatted chair, clear back space')
    m=Mesh()
    for x in [-.76,.76]:m.box((x,0,.33),(.08,2.15,.19),'Timber',.003)
    for y in [-1.025,1.025]:
        for x in [-.73,.73]:m.box((x,y,.25),(.10,.10,.50),'Timber',.003)
        m.box((0,y,.34),(1.5,.075,.19),'Timber',.003)
    m.box((0,.99,.73),(1.48,.08,.55),'Timber',.003)
    for i in range(7):m.box((0,-.9+i*.29,.42),(1.47,.065,.045),'Timber',.001)
    m.box((0,0,.54),(1.45,1.99,.20),'Linen',.025)
    m.box((0,-.28,.66),(1.47,1.35,.045),'Blanket',.012)
    for x in [-.37,.37]:m.box((x,.73,.68),(.60,.38,.12),'Linen',.035)
    add('Bed_160x215x101',m,['Timber','Linen','Blanket'],[box((0,0,.39),(1.6,2.15,.78)),box((0,.99,.89),(1.6,.10,.24))],'Framed double bed, woven linen mattress and separate blanket faces')
    for kind,w,d,h in [('Wardrobe',1.2,.55,2.10),('Sideboard',1.4,.45,.90),('Bookcase',.9,.35,1.90)]:
        m=Mesh();m.box((0,d/2-.018,h/2),(w,.035,h),'Timber',.002)
        for x in [-w/2+.035,w/2-.035]:m.box((x,0,h/2),(.07,d,h),'Timber',.002)
        for z in [.08,h-.035]:m.box((0,0,z),(w,d,.07),'Timber',.003)
        if kind!='Bookcase':
            for x in [-w/4,w/4]:
                m.box((x,-d/2+.015,h/2),(w/2-.07,.04,h-.22),'Timber',.002)
                m.tube([(x+.08,-d/2-.03,h*.50),(x+.08,-d/2-.03,h*.56)],.012,'Bronze',8)
            slots=['Timber','Bronze'];bodies=[box((0,0,h/2),(w,d,h))]
        else:
            for z in [.48,.90,1.32]:m.box((0,0,z),(w-.1,d-.03,.035),'Timber',.001)
            for row in range(3):
                for i in range(8):
                    bh=.20+.06*math.sin(i*2+row)**2
                    m.box((-.31+i*.084,-.015,.50+row*.42+bh/2),(.055,.20,bh),'Book',.001)
            slots=['Timber','Book'];bodies=[box((0,0,h/2),(w,d,h))]
        add(kind+'_'+str(int(w*100))+'x'+str(int(d*100))+'x'+str(int(h*100)),m,slots,bodies,kind+' with distinct boards and restrained edge bevels')
    m=Mesh()
    for i in range(3):m.box((0,-.15+i*.15,.43),(1.2,.145,.05),'Timber',.002)
    for x in [-.48,.48]:
        for y in [-.14,.14]:m.box((x,y,.20),(.07,.07,.40),'Timber',.002)
    add('Bench_120x45x46',m,['Timber'],[box((0,0,.23),(1.2,.45,.46))],'Low slatted bench')
    m=Mesh();m.box((0,0,.46),(.55,.45,.065),'Timber',.003)
    for x in [-.22,.22]:
        for y in [-.17,.17]:m.box((x,y,.22),(.055,.055,.44),'Timber',.002)
    m.box((0,0,.15),(.48,.38,.03),'Timber',.002)
    add('SideTable_55x45x49',m,['Timber'],[box((0,0,.245),(.55,.45,.49))],'Bedside or reading table')
    m=Mesh();m.box((0,0,.875),(1.4,.65,.07),'Timber',.003)
    for x in [-.58,.58]:
        for y in [-.23,.23]:m.box((x,y,.42),(.075,.075,.84),'Timber',.002)
    m.box((0,0,.20),(1.26,.50,.055),'Timber',.002)
    add('Workbench_140x65x91',m,['Timber'],[box((0,0,.455),(1.4,.65,.91))],'Plain work counter; no implied crafting functionality')
    m=Mesh();m.box((0,0,.235),(.9,.45,.47),'Timber',.004);m.box((0,0,.49),(.94,.49,.055),'Timber',.003)
    for x in [-.31,.31]:m.box((x,0,.501),(.035,.495,.04),'Iron',.001)
    m.box((0,-.255,.39),(.08,.02,.13),'Iron',.001)
    add('Chest_94x49x52',m,['Timber','Iron'],[box((0,0,.26),(.94,.49,.52))],'Storage chest with forged bands; static review prop')
    m=Mesh();m.box((0,0,.008),(2.4,1.8,.016),'Blanket',.002)
    add('Rug_240x180',m,['Blanket'],[],'Thin woven floor rug, nonblocking')
    # One self-contained lantern used on side tables and matching suspension variants.
    for kind in ['Lantern','Pendant','WallLantern']:
        m=Mesh();base=.0
        m.box((0,0,.025),(.24,.24,.05),'Bronze',.003)
        for x in [-.095,.095]:
            for y in [-.095,.095]:m.tube([(x,y,.06),(x,y,.36)],.012,'Bronze',8)
        m.box((0,0,.36),(.25,.25,.035),'Bronze',.003)
        # Small luminous chimney and wick, enclosed in the visible metal cage.
        m.box((0,0,.19),(.09,.09,.22),'Flame',.008)
        m.tube([(0,0,.38),(0,0,.45)],.018,'Bronze',8)
        if kind=='Pendant':
            suspension=old.roof_surface_z(3.,3.4,'Mid')-.12-2.45
            m.tube([(0,0,.45),(0,0,suspension)],.009,'Iron',8);m.box((0,0,suspension),(.16,.16,.025),'Iron',.002)
        elif kind=='WallLantern':
            m.box((0,.18,.40),(.10,.04,.34),'Iron',.003)
            m.tube([(0,.17,.53),(0,.08,.55),(0,0,.45)],.014,'Iron',8)
        add(kind+'_24',m,['Bronze','Flame']+(['Iron'] if kind!='Lantern' else []),[box((0,0,.23),(.25,.25,.46))],kind+'; luminous core is paired with a co-located Unreal light; fuel type not established')

def partitions():
    for width in [2.,1.52,.56]:
        for doorway in ([False,True] if width==2 else [False]):
            m=Mesh();bodies=[]
            pieces=[(0,width,0,3)] if not doorway else [(0,.4,0,3),(1.6,2,0,3),(.4,1.6,2.35,3)]
            for x0,x1,z0,z1 in pieces:
                c=((x0+x1)/2,.06,(z0+z1)/2);s=(x1-x0,.12,z1-z0)
                m.box(c,s,'Plaster');bodies.append(box(c,s))
            for y in [-.012,.132]:
                m.box((width/2,y,2.94),(width,.028,.12),'Timber',.002)
                for x0,x1,z0,z1 in pieces:
                    if z0==0:m.box(((x0+x1)/2,y,.065),(x1-x0,.03,.13),'Timber',.002)
                for x in ([.37,1.63] if doorway else [0.035,width-.035]):
                    m.box((x,y,1.18 if doorway else 1.5),(.07,.035,2.36 if doorway else 3),'Timber',.002)
                if doorway:m.box((1,y,2.39),(1.32,.035,.08),'Timber',.002)
            add(('InteriorDoorway' if doorway else 'InteriorWall')+'_'+str(round(width*100))+'x12x300',m,['Plaster','Timber'],bodies,'Interior wall; 120 x 235 cm clear doorway' if doorway else 'Interior partition, lower start pivot')
    m=Mesh();m.box((1.19,1.14,.08),(2.38,2.28,.16),'Plaster')
    for x in [.04,2.34]:m.box((x,1.14,-.025),(.08,2.28,.05),'Timber',.002)
    add('Ceiling_238x228x16',m,['Plaster','Timber'],[box((1.19,1.14,.08),(2.38,2.28,.16))],'Ceiling tile for closed rear rooms; explicit 238 x 228 cm layout')

def place(module,loc,yaw=0,zone='Furniture',light=None):
    o=ASSETS[module]['obj'].copy();o.data=ASSETS[module]['obj'].data;house=bpy.data.scenes['House_10x12'];house.collection.objects.link(o)
    o.location=loc;o.rotation_euler.z=math.radians(yaw);o['SourceModule']=module
    PLACEMENTS.append(dict(module=module,location_m=list(loc),yaw_blender=yaw,zone=zone,light=light))
def layout():
    prefix='SM_EH03_'
    def p(n,loc,yaw=0,zone='Furniture',light=None):place(prefix+n,loc,yaw,zone,light)
    for x,n in [(.24,'InteriorWall_200x12x300'),(2.24,'InteriorDoorway_200x12x300'),(4.24,'InteriorWall_200x12x300'),(6.24,'InteriorDoorway_200x12x300'),(8.24,'InteriorWall_152x12x300')]:p(n,(x,7.2,0),zone='Partitions')
    # Longitudinal wall along +Y, one owner at each junction.
    for y,n in [(7.32,'InteriorWall_200x12x300'),(9.32,'InteriorWall_200x12x300'),(11.32,'InteriorWall_56x12x300')]:p(n,(5.24,y,0),90,'Partitions')
    for i in range(4):
        for j in range(2):p('Ceiling_238x228x16',(.24+i*2.38,7.2+j*2.28,3.),zone='Partitions')
    p('Table_180x100x77',(3.0,3.4,0));p('Rug_240x180',(3,3.4,.005))
    for x,y,yaw in [(3,2.42,0),(3,4.38,180),(1.66,3.4,-90),(4.34,3.4,90)]:p('Chair_47x49x94',(x,y,0),yaw)
    p('Sideboard_140x45x90',(1.4,.53,0),180)
    p('Bookcase_90x35x190',(8.5,.49,0),180)
    p('Workbench_140x65x91',(9.35,4.8,0),90)
    p('Bench_120x45x46',(1.0,5.9,0),90)
    p('Bed_160x215x101',(1.65,10.4,0))
    p('SideTable_55x45x49',(2.95,10.5,0))
    p('Wardrobe_120x55x210',(4.8,9.5,0),-90)
    p('Chest_94x49x52',(7,10.8,0));p('Chest_94x49x52',(8.6,10.8,0))
    p('Bookcase_90x35x190',(9.55,8.7,0),-90)
    p('Sideboard_140x45x90',(7.6,11.45,0))
    p('Pendant_24',(3,3.4,2.45),light=dict(lumens=90,radius_cm=470,temperature=3000))
    p('Lantern_24',(2.95,10.5,.493),light=dict(lumens=24,radius_cm=340,temperature=3000))
    p('WallLantern_24',(8.8,7.02,1.65),0,light=dict(lumens=40,radius_cm=380,temperature=3000))
    p('Lantern_24',(7.6,11.45,.90),light=dict(lumens=24,radius_cm=300,temperature=3000))

def audit(o):
    me=o.data;me.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(me)
    nonmanifold=sum(not e.is_manifold for e in bm.edges);zero=sum(f.calc_area()<1e-10 for f in bm.faces)
    assert nonmanifold==zero==0,(o.name,nonmanifold,zero)
    assert me.uv_layers.active
    uvbad=0
    for t in me.loop_triangles:
        a,b,c=[Vector(me.uv_layers.active.data[i].uv) for i in t.loops]
        uvbad+=abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))<1e-12
    assert not uvbad,(o.name,uvbad)
    lo=[min(v.co[k] for v in me.vertices) for k in range(3)];hi=[max(v.co[k] for v in me.vertices) for k in range(3)]
    vol=bm.calc_volume(signed=True);assert vol>0;bm.free()
    return dict(triangles=len(me.loop_triangles),vertices=len(me.vertices),slots=[m.name.replace('B03_','') for m in me.materials],bounds_m=[lo,hi],nonmanifold_edges=nonmanifold,degenerate_faces=zero,degenerate_uv_triangles=uvbad,volume_m3=vol)

def build():
    for p in ['Textures','Exports','Evidence','Previews']:(ROOT/p).mkdir(exist_ok=True)
    source=ROOT.parent/'WindowUpdate_B02/EH_HouseB02_Windows.blend'
    bpy.ops.wm.open_mainfile(filepath=str(source))
    maps()
    # Refine material roles on the own small-house copy; keep the comparison source scene unchanged.
    house=bpy.data.scenes['House_10x12']
    for o in house.objects:
        if o.type!='MESH' or o.name.startswith('UCX_'):continue
        o.data=o.data.copy()
        for i,mat in enumerate(o.data.materials):
            role=mat.name.split('.')[0]
            if role in MATS:o.data.materials[i]=MATS['Floor' if role=='Stone' and 'Floor' in o.get('SourceModule','') else role]
    library=bpy.data.scenes.new('B03_Asset_Library');library.unit_settings.system='METRIC';library.unit_settings.scale_length=1
    bpy.context.window.scene=library
    furniture();partitions();layout()
    settings=dict(PROFILE['export_settings']);settings['object_types']=set(settings['object_types'])
    if 'io_scene_fbx' not in bpy.context.preferences.addons:bpy.ops.preferences.addon_enable(module='io_scene_fbx')
    info={}
    for name,item in ASSETS.items():
        bpy.ops.object.select_all(action='DESELECT')
        for o in [item['obj']]+item['ucx']:o.select_set(True)
        bpy.context.view_layer.objects.active=item['obj']
        bpy.ops.export_scene.fbx(filepath=str(ROOT/'Exports'/(name+'.fbx')),**settings)
        info[name]=dict(**audit(item['obj']),ucx_hulls=len(item['ucx']),description=item['description'])
        for body in item['ucx']:
            audit(body)
            assert max(p.normal.dot(v.co-body.data.vertices[p.vertices[0]].co) for p in body.data.polygons for v in body.data.vertices)<1e-5
    bpy.context.window.scene=house
    for im in bpy.data.images:
        if im.source=='FILE' and not im.name.startswith('T_EH03_'):im.filepath='//../Textures/'+im.filepath.replace('\\','/').rsplit('/',1)[-1]
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'EH_Musterhaus_B03.blend'),relative_remap=False)
    write('manifest.json',dict(status='draft',accepted=False,kit_id='EH.HouseB.Musterhaus03',parent_source_sha256=sha(source),
        source='EH_Musterhaus_B03.blend',base_commit='21a7ef17dd5cfd6f058b4c0f7440d2727b98c18d',
        assets=info,placements=PLACEMENTS,export_profile=PROFILE,
        coordinate_mapping='UE_cm=(100*B.x,-100*B.y,100*B.z)',house_origin_ue_cm=[-2400,-1900,31],
        spaces=dict(living_dining=[9.52,6.96],sleeping=[5.0,4.44],storage=[4.40,4.44]),
        material_families=list(MATS),provisional_design='One furnished test layout, not culture or household canon',
        lamps='Visible lantern bodies with matching static emissive cores and movable point lights; no fuel/gameplay system'))
    print('B03_BUILD_OK',len(info),len(PLACEMENTS))

def verify():
    manifest=json.loads((ROOT/'manifest.json').read_text())
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'EH_Musterhaus_B03.blend'))
    lib=bpy.data.scenes['B03_Asset_Library'];source={n:audit(lib.objects[n]) for n in manifest['assets']}
    missing=[im.filepath for im in bpy.data.images if im.source=='FILE' and not Path(bpy.path.abspath(im.filepath)).is_file()];assert not missing,missing
    results={}
    for name,original in source.items():
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.preferences.addon_enable(module='io_scene_fbx')
        bpy.ops.import_scene.fbx(filepath=str(ROOT/'Exports'/(name+'.fbx')),use_anim=False,use_image_search=False)
        objects=[o for o in bpy.context.scene.objects if o.type=='MESH' and not o.name.startswith('UCX_')];assert len(objects)==1
        actual=audit(objects[0]);assert actual['triangles']==original['triangles']
        assert actual['slots']==original['slots'],(actual['slots'],original['slots'])
        err=max(abs(actual['bounds_m'][i][j]-original['bounds_m'][i][j]) for i in range(2) for j in range(3));assert err<1e-5
        ucx=[o for o in bpy.context.scene.objects if o.name.startswith('UCX_')];assert len(ucx)==manifest['assets'][name]['ucx_hulls']
        results[name]=dict(bounds_error_m=err,ucx_hulls=len(ucx),**actual)
    write('Evidence/blender_verification.json',dict(status='passed',blender=bpy.app.version_string,source_reopened=True,all_textures_resolved=True,assets=results))
    print('B03_VERIFY_OK',len(results))

if __name__=='__main__':{'build':build,'verify':verify}[sys.argv[-1]]()
