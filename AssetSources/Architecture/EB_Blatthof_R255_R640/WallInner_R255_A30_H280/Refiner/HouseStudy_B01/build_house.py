"""Standalone Blender house study. No Unreal operations or existing asset writes.

New provisional kit EH.B01, separate from the preserved R255 arc interface.
Run build / verify / render in separate factory-startup Blender processes.
"""
import argparse, hashlib, json, math, sys
from pathlib import Path
sys.dont_write_bytecode=True
import bpy, bmesh
import numpy as np
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[5]
NAME='EH_HouseB01_Study'
W,H,L=10.,3.2,12.
PROFILE=json.loads((REPO/'AssetSources/Calibration/BlenderUE01/unreal_import_profile.json').read_text(encoding='utf-8'))
ASSETS={}
MATERIALS={}

def write(name,value):
    p=(ROOT/name).resolve(); assert p.is_relative_to(ROOT)
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

class Mesh:
    def __init__(self): self.v=[]; self.f=[]; self.m=[]; self.uv=[]; self.s=[]
    def part(self,verts,faces,material,smooth=False,uvscale=1.):
        assert all(math.isfinite(float(c)) for p in verts for c in p), 'Non-finite source coordinate'
        offset=len(self.v); self.v.extend([tuple(p) for p in verts])
        sizes=[max(p[k] for p in verts)-min(p[k] for p in verts) for k in range(3)]
        longest=max(range(3),key=lambda k:sizes[k])
        for face in faces:
            self.f.append(tuple(offset+i for i in face)); self.m.append(material); self.s.append(smooth)
            points=[Vector(verts[i]) for i in face]
            n=(points[1]-points[0]).cross(points[2]-points[0])
            normalaxis=max(range(3),key=lambda k:abs(n[k]))
            axes=[k for k in range(3) if k!=normalaxis]
            if material=='Timber' and longest in axes:
                axes=[k for k in axes if k!=longest]+[longest]
            self.uv.append([(p[axes[0]]/uvscale,p[axes[1]]/uvscale) for p in points])
    def box(self,center,size,mat,bevel=.0):
        bm=bmesh.new(); bmesh.ops.create_cube(bm,size=1)
        for v in bm.verts: v.co=Vector(tuple(v.co[k]*size[k] for k in range(3)))
        if bevel:
            bmesh.ops.bevel(bm,geom=list(bm.edges),offset=min(bevel,min(size)/5),segments=1,affect='EDGES')
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.verts.ensure_lookup_table()
        verts=[tuple(v.co+Vector(center)) for v in bm.verts]
        self.part(verts,[[v.index for v in f.verts] for f in bm.faces],mat)
        bm.free()
    def prism(self,outline,depth,mat):
        # outline is CCW in local X/Z; extrusion along positive Y.
        area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(outline,outline[1:]+outline[:1]))
        if area<0: outline=list(reversed(outline))
        n=len(outline); verts=[(x,y,z) for y in depth for x,z in outline]
        faces=[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]
        faces.extend(((i+1)%n,i,i+n,(i+1)%n+n) for i in range(n))
        self.part(verts,faces,mat)
    def tube(self,points,radius,mat,sides=6):
        points=[Vector(p) for p in points]; verts=[]
        closed=(points[0]-points[-1]).length<1e-8
        if closed:points.pop()
        for i,p in enumerate(points):
            tangent=(points[(i+1)%len(points)]-points[(i-1)%len(points)]).normalized() if closed else (points[min(i+1,len(points)-1)]-points[max(i-1,0)]).normalized()
            axis=Vector((0,1,0)) if abs(tangent.y)<.9 else Vector((1,0,0))
            u=tangent.cross(axis).normalized(); v=tangent.cross(u).normalized()
            verts.extend(tuple(p+radius*(math.cos(2*math.pi*j/sides)*u+math.sin(2*math.pi*j/sides)*v)) for j in range(sides))
        faces=[] if closed else [tuple(range(sides-1,-1,-1)),tuple((len(points)-1)*sides+j for j in range(sides))]
        for i in range(len(points) if closed else len(points)-1):
            k=(i+1)%len(points)
            for j in range(sides): faces.append((i*sides+j,i*sides+(j+1)%sides,k*sides+(j+1)%sides,k*sides+j))
        self.part(verts,faces,mat,True)
    def object(self,name,collection,slots):
        mesh=bpy.data.meshes.new(name); mesh.from_pydata(self.v,[],self.f); mesh.update()
        obj=bpy.data.objects.new(name,mesh); collection.objects.link(obj)
        for m in slots: mesh.materials.append(MATERIALS[m])
        uv=mesh.uv_layers.new(name='UV0')
        for p,mat,smooth,tex in zip(mesh.polygons,self.m,self.s,self.uv):
            p.material_index=slots.index(mat); p.use_smooth=smooth
            for i,t in zip(p.loop_indices,tex): uv.data[i].uv=t
        return obj

def image(name,pixels,space='sRGB'):
    n=pixels.shape[0]; rgba=np.ones((n,n,4),dtype=np.float32)
    if pixels.ndim==2: rgba[:,:,:3]=pixels[:,:,None]
    else: rgba[:,:,:3]=pixels
    im=bpy.data.images.new(name,width=n,height=n,alpha=False)
    im.colorspace_settings.name=space; im.pixels.foreach_set(rgba.ravel())
    im.filepath_raw=str(ROOT/'Textures'/(name+'.png')); im.file_format='PNG'; im.save()
    return im

def textures():
    (ROOT/'Textures').mkdir(exist_ok=True)
    n=1024; u,v=np.meshgrid(np.arange(n,dtype=np.float32)/n,np.arange(n,dtype=np.float32)/n)
    rng=np.random.default_rng(1042)
    def noise():
        out=np.zeros((n,n),np.float32)
        for freq,amp in [(2,.42),(5,.25),(13,.15),(37,.09),(103,.05),(239,.025)]:
            for j in range(3):
                a,b=rng.integers(1,freq+1,2); phase=rng.random()*6.283
                out+=amp/3*np.sin(2*np.pi*(a*u+b*v)+phase)
        return out
    def material(key,base,pattern,height_amp,rough,metal=0):
        height=pattern*height_amp
        dx=(np.roll(height,-1,axis=1)-np.roll(height,1,axis=1))*n/2
        dy=(np.roll(height,-1,axis=0)-np.roll(height,1,axis=0))*n/2
        normal=np.stack((-dx,-dy,np.ones_like(dx)),axis=-1); normal/=np.linalg.norm(normal,axis=-1)[:,:,None]
        color=np.clip(np.array(base)[None,None,:]*(1+pattern[:,:,None]*(.06 if key=='Plaster' else .10)),0,1)
        maps={'BaseColor':image('T_EH_'+key+'_BaseColor',color),
              'Normal':image('T_EH_'+key+'_Normal',normal*.5+.5,'Non-Color'),
              'Roughness':image('T_EH_'+key+'_Roughness',np.clip(rough+pattern*.08,.05,1),'Non-Color')}
        mat=bpy.data.materials.new(key); mat.use_nodes=True
        nodes=mat.node_tree.nodes; links=mat.node_tree.links; bsdf=nodes.get('Principled BSDF')
        bsdf.inputs['Metallic'].default_value=metal
        for typ,im in maps.items():
            node=nodes.new('ShaderNodeTexImage'); node.image=im; node.extension='REPEAT'; node.label=typ
            if typ=='Normal':
                nm=nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value=.32 if key=='Timber' else .20
                links.new(node.outputs['Color'],nm.inputs['Color']); links.new(nm.outputs['Normal'],bsdf.inputs['Normal'])
            else: links.new(node.outputs['Color'],bsdf.inputs['Base Color' if typ=='BaseColor' else 'Roughness'])
        MATERIALS[key]=mat
    material('Plaster',(.88,.82,.70),noise(),.0003,.82)
    grain=.45*np.sin(2*np.pi*(u*36+.12*np.sin(2*np.pi*v*3)))+.22*np.sin(2*np.pi*(u*113+.18*np.sin(2*np.pi*v)))+noise()*.35
    material('Timber',(.42,.25,.12),grain,.00035,.57)
    material('Stone',(.68,.61,.48),noise(),.0007,.76)
    roofnoise=noise()
    material('Jade',(.16,.34,.31),roofnoise,.00035,.62,.08)
    for key,color,metal,rough in [('Glass',(.022,.095,.12,1),.45,.17),('Bronze',(.27,.15,.055,1),.75,.31)]:
        mat=bpy.data.materials.new(key); mat.use_nodes=True; bsdf=mat.node_tree.nodes.get('Principled BSDF')
        bsdf.inputs['Base Color'].default_value=color; bsdf.inputs['Metallic'].default_value=metal; bsdf.inputs['Roughness'].default_value=rough
        MATERIALS[key]=mat

def add_asset(name,mesh,slots,colliders,collection,description,joins=None):
    obj=mesh.object(name,collection,slots)
    obj['KitId']='EH.HouseB.Prototype01'; obj['InterfaceVersion']='draft_1'; obj['Description']=description
    ucx=[]
    for i,part in enumerate(colliders):
        collider=part.object('UCX_'+name+'_%02d'%i,collection,['Plaster'])
        collider.hide_render=True; collider.display_type='WIRE'; ucx.append(collider)
    ASSETS[name]={'object':obj,'ucx':ucx,'description':description,'joins':joins or []}
    return obj

def collider_box(c,s):
    m=Mesh(); m.box(c,s,'Plaster'); return m

def wall_asset(typ,collection):
    m=Mesh(); coll=[]
    width=2.; depth=.24
    def body_box(x0,x1,z0,z1):
        if x1<=x0 or z1<=z0:return
        m.box(((x0+x1)/2,.12,(z0+z1)/2),(x1-x0,.24,z1-z0),'Plaster')
        coll.append(collider_box(((x0+x1)/2,.12,(z0+z1)/2),(x1-x0,.24,z1-z0)))
    if typ.startswith('Solid'):
        body_box(0,2,0,H)
    else:
        door=typ=='Entry'; half=.68 if door else .50; sill=0 if door else .95
        spring=2.22 if door else 2.02; rise=.63 if door else .66
        left,right=1-half,1+half
        body_box(0,left,0,H); body_box(right,2,0,H); body_box(left,right,0,sill)
        top=lambda x:spring+rise*max(0,1-abs((x-1)/half))**.72
        xs=np.linspace(left,right,17)
        for a,b in zip(xs,xs[1:]):
            outline=[(float(a),top(a)),(float(b),top(b)),(float(b),H),(float(a),H)]
            m.prism(outline,(0,.24),'Plaster')
            c=Mesh(); c.prism(outline,(0,.24),'Plaster'); coll.append(c)
        outline=[(left,sill),(right,sill)]+[(float(x),top(x)) for x in reversed(xs)]
        # Frame is a single continuous closed path around a genuine wall aperture.
        m.tube([(x,-.055,z) for x,z in outline+[outline[0]]],.058,'Timber',8)
        if not door:
            m.prism(outline,(.075,.095),'Glass')
            c=Mesh(); c.prism(outline,(.075,.095),'Plaster'); coll.append(c)
            m.box((1,-.07,1.65),(.035,.06,1.45),'Timber',.004)
            for sign in (-1,1):
                m.tube([(1,-.075,2.55),(1+sign*.24,-.075,2.15),(1+sign*.44,-.075,1.9)],.022,'Timber',6)
            m.box((1,-.10,sill-.04),(1.18,.38,.10),'Stone',.008)
    # No duplicated B post: a shared post belongs to the A end of each panel.
    m.box((.075,-.035,H/2),(.15,.16,H),'Timber',.008)
    m.box((1,-.035,3.10),(2,.17,.19),'Timber',.008)
    if typ!='Entry':
        m.box((1,-.035,.28),(2,.17,.12),'Timber',.006)
        for i in range(4):m.box((.25+.5*i,.0,.105),(.496,.31,.21),'Stone',.007)
    else:
        for x in (.16,1.84):m.box((x,-.02,.105),(.31,.32,.21),'Stone',.007)
    for mirrored in (False,True):
        x0=.08 if not mirrored else 2.
        direction=1 if not mirrored else -1
        points=[]
        for t in np.linspace(0,1,9):
            points.append((x0+direction*(.03+.54*t*t),-.075,2.38+.65*t))
        m.tube(points,.045 if typ!='SolidB' else .055,'Timber',6)
    if typ=='SolidB':
        m.tube([(.12,-.07,.42),(.27,-.07,.65),(.58,-.07,.77)],.034,'Timber',6)
    if typ=='Window':
        # This window is intentionally closed/glazed: one solid collision envelope suffices.
        coll=[collider_box((1,.12,H/2),(2,.24,H))]
    elif typ=='Entry':
        coll=[collider_box((.16,.12,H/2),(.32,.24,H)),collider_box((1.84,.12,H/2),(.32,.24,H))]
        for a,b in zip(np.linspace(.32,1.68,5),np.linspace(.32,1.68,5)[1:]):
            c=Mesh();c.prism([(float(a),top(a)),(float(b),top(b)),(float(b),H),(float(a),H)],(0,.24),'Plaster');coll.append(c)
    slots=['Plaster','Timber','Stone']+(['Glass'] if typ=='Window' else [])
    return add_asset('SM_EH_Wall_'+typ+'_200x24x320',m,slots,coll,collection,
        '2m panel; local X along wall, +Y interior, +Z up; A owns post; '+typ,
        [{'position_m':[0,0,0],'yaw_blender_deg':180},{'position_m':[2,0,0],'yaw_blender_deg':0}])

def roof_z(x,y,kind='Mid'):
    t=abs((x-5)/5.65)
    base=3.30+2.65*max(0,1-t**1.40)**1.20+.50*math.exp(-((t-1)/.105)**2)
    if kind=='End':
        s=max(0,min(1,(2.8-y)/2.8)); base+=.38*s*s*(3-2*s)
    return base

def roof_surface_z(x,y,kind='Mid'):
    gridx=np.linspace(-.65,10.65,49)
    base=float(np.interp(x,gridx,[roof_z(q,0,kind) for q in gridx]))
    if kind=='Mid':return base
    gridy=np.linspace(0,2.8,7)
    return base+float(np.interp(y,gridy,[roof_z(5,t,'End')-roof_z(5,0,'End') for t in gridy]))

def roof_asset(kind,collection):
    m=Mesh(); coll=[]; length=2.8 if kind=='End' else 2.
    xs=np.linspace(-.65,10.65,49); ys=np.linspace(0,length,7 if kind=='End' else 2)
    # Shared vertices across the closed two-sided roof shell.
    verts=[(float(x),float(y),roof_z(x,y,kind)-d) for d in (0,.12) for y in ys for x in xs]
    nx,ny=len(xs),len(ys); layer=nx*ny; faces=[]
    for j in range(ny-1):
        for i in range(nx-1):
            a=j*nx+i; faces.append((a,a+1,a+nx+1,a+nx)); faces.append((layer+a+nx,layer+a+nx+1,layer+a+1,layer+a))
    for j in range(ny-1):
        a=j*nx; b=a+nx; faces.append((a,b,b+layer,a+layer))
        a=j*nx+nx-1;b=a+nx;faces.append((a+layer,b+layer,b,a))
    for i in range(nx-1):
        faces.append((i+layer,i+layer+1,i+1,i))
        a=(ny-1)*nx+i;faces.append((a,a+1,a+1+layer,a+layer))
    m.part(verts,faces,'Jade',True,2.)
    # A-owned rib and continuous ridge/eave trims, so repeated middle fields have no doubled ribs.
    for y in [0]:
        m.tube([(float(x),y,roof_z(x,y,kind)+.025) for x in xs],.052,'Timber',6)
    for x in (-.65,5.,10.65):
        m.tube([(x,float(y),roof_z(x,y,kind)+.025) for y in ys],.058,'Timber',6)
    for x in (1.1,2.7,7.3,8.9):
        m.tube([(x,float(y),roof_z(x,y,kind)+.009) for y in ys],.012,'Timber',4)
    # Conservative convex roof strips; this is source collision, not UE/Kapsel validation.
    for a,b in zip(np.linspace(-.65,10.65,17),np.linspace(-.65,10.65,17)[1:]):
        for ya,yb in [(0,length)]:
            points=[(float(x),float(y),roof_z(x,y,kind)-d) for d in (0,.12) for y in (ya,yb) for x in (a,b)]
            bm=bmesh.new()
            for p in points:bm.verts.new(p)
            bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False)
            bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.verts.ensure_lookup_table()
            c=Mesh();c.part([tuple(v.co) for v in bm.verts],[[v.index for v in f.verts] for f in bm.faces],'Plaster');bm.free();coll.append(c)
    return add_asset('SM_EH_Roof_'+kind+'_W1000',m,['Jade','Timber'],coll,collection,
        'Draft 10m wall span with 65cm side eaves; '+kind+' length '+str(length)+'m',
        [{'position_m':[0,0,0],'yaw_blender_deg':180},{'position_m':[0,length,0],'yaw_blender_deg':0}])

def misc_assets(collection):
    g=Mesh()
    xs=sorted({0.,10.}|{float(x) for x in np.linspace(-.65,10.65,49) if 0<x<10})
    for a,b in zip(xs,xs[1:]):
        verts=[(float(x),y,z) for y in (0,.24) for x in (a,b) for z in (H,roof_surface_z(x,y+.8,'End')-.12)]
        g.part(verts,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],'Plaster')
    for x in (0,2,4,6,8,10):
        top=roof_z(x,.8,'End')-.12
        g.box((x,-.035,(H+top)/2),(.14,.16,max(.01,top-H)),'Timber',.005)
    g.tube([(float(x),-.035,roof_z(x,.8,'End')-.17) for x in xs],.058,'Timber',6)
    add_asset('SM_EH_Gable_W1000',g,['Plaster','Timber'],[],collection,'Full-width closed gable infill; front/back reuse at positive-scale 180 degree rotation; collision not supplied yet')
    # Sidewall crown -> exact sampled underside. Separate pieces preserve repeatable middles.
    for typ in ('Mid','EndA','EndB'):
        fill=Mesh()
        endx=sorted({0.,2.}|{float(y-.8) for y in np.linspace(0,2.8,7) if 1e-6<y-.8<2-1e-6})
        xx=[0.,2.] if typ=='Mid' else (endx if typ=='EndA' else sorted(2-x for x in endx))
        yy=sorted({0.,.24}|{float(x) for x in np.linspace(-.65,10.65,49) if 0<x<.24})
        def top(x,y):
            return roof_surface_z(y,0,'Mid')-.12 if typ=='Mid' else roof_surface_z(y,.8+(x if typ=='EndA' else 2-x),'End')-.12
        for a,b in zip(xx,xx[1:]):
            for c,d in zip(yy,yy[1:]):
                verts=[(x,y,z) for y in (c,d) for x in (a,b) for z in (H,top(x,y))]
                fill.part(verts,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],'Plaster')
        fill.tube([(x,-.035,top(x,0)-.035) for x in xx],.04,'Timber',6)
        add_asset('SM_EH_EaveFill_'+typ+'_200',fill,['Plaster','Timber'],[],collection,'Closed sidewall crown infill matched to the sampled roof underside; '+typ+'; upper collision pending')
    floor=Mesh();floor.box((1,1,-.10),(2,2,.20),'Stone',.004)
    add_asset('SM_EH_Floor_200x200x20',floor,['Stone'],[collider_box((1,1,-.1),(2,2,.2))],collection,'2m floor tile, upper surface Z0')
    door=Mesh();half=.66
    top=lambda x:2.20+.61*max(0,1-abs((x-half)/half))**.72
    xs=np.linspace(0,2*half,17)
    outline=[(0,.035),(2*half,.035)]+[(float(x),top(x)) for x in reversed(xs)]
    door.prism(outline,(-.055,.035),'Timber')
    for x in np.linspace(.04,1.28,9):
        door.tube([(float(x),-.061,.08),(float(x),-.061,top(x)-.035)],.005,'Timber',4)
    for z in (.38,1.05):door.box((.29,-.075,z),(.54,.04,.055),'Bronze',.005)
    door.tube([(.13,-.095,.45),(.13,-.095,2.15)],.018,'Bronze',6)
    door.box((1.07,-.095,1.15),(.06,.06,.12),'Bronze',.008)
    add_asset('SM_EH_DoorLeaf_132_Study',door,['Timber','Bronze'],[],collection,'Static visual door leaf with hinge at local X0/Z0. No gameplay or validated door collision')
    canopy=Mesh();xs=np.linspace(-1.12,1.12,33);verts=[]
    for d in (0,.10):
        for y in (-.95,.05):
            for x in xs:verts.append((float(x),y,2.78+.42*max(0,1-(x/1.12)**2)+.04*abs(y)-d))
    nx=len(xs);layer=2*nx;faces=[]
    for i in range(nx-1):
        faces.extend([(i,i+1,nx+i+1,nx+i),(layer+nx+i,layer+nx+i+1,layer+i+1,layer+i),
                      (i+layer,i+layer+1,i+1,i),(nx+i,nx+i+1,layer+nx+i+1,layer+nx+i)])
    faces.extend([(0,nx,layer+nx,layer),(nx-1,layer+nx-1,layer+2*nx-1,2*nx-1)])
    canopy.part(verts,faces,'Jade',True,2.)
    for y in (-.95,.05):canopy.tube([(float(x),y,2.8+.42*max(0,1-(x/1.12)**2)+.04*abs(y)) for x in xs],.044,'Timber',6)
    add_asset('SM_EH_EntryCanopy_224',canopy,['Jade','Timber'],[],collection,'Optional entrance canopy; visual decoration, no collision')

def instance(scene,name,location,rotation=0,label=None):
    src=ASSETS[name]['object']; obj=src.copy();obj.data=src.data;scene.collection.objects.link(obj)
    obj.name=label or name+'_Instance';obj.location=location;obj.rotation_euler.z=math.radians(rotation)
    obj['SourceModule']=name
    return obj

def assembly(scene,length,offset=0):
    count=0
    rows=[(5,(offset,0,0),0),(int(length/2),(offset+10,0,0),90),(5,(offset+10,length,0),180),(int(length/2),(offset,length,0),270)]
    for row,(n,origin,angle) in enumerate(rows):
        a=math.radians(angle)
        for i in range(n):
            typ='Entry' if row==0 and i==2 else ('Window' if (i%2==1 or row==0 and i in (1,3)) else ('SolidA' if i%4==0 else 'SolidB'))
            instance(scene,'SM_EH_Wall_'+typ+'_200x24x320',(origin[0]+2*i*math.cos(a),origin[1]+2*i*math.sin(a),0),angle)
            if row in (1,3):
                fill='EndA' if i==0 else ('EndB' if i==n-1 else 'Mid')
                instance(scene,'SM_EH_EaveFill_'+fill+'_200',(origin[0]+2*i*math.cos(a),origin[1]+2*i*math.sin(a),0),angle)
            count+=1
    for x in range(5):
        for y in range(int(length/2)):instance(scene,'SM_EH_Floor_200x200x20',(offset+2*x,2*y,0))
    instance(scene,'SM_EH_Gable_W1000',(offset,0,0))
    instance(scene,'SM_EH_Gable_W1000',(offset+10,length,0),180)
    instance(scene,'SM_EH_Roof_End_W1000',(offset,-.8,0))
    for y in range(2,int(length-2),2):instance(scene,'SM_EH_Roof_Mid_W1000',(offset,y,0))
    instance(scene,'SM_EH_Roof_End_W1000',(offset+10,length+.8,0),180)
    instance(scene,'SM_EH_DoorLeaf_132_Study',(offset+4.34,-.005,0),label='FrontDoor_Only')
    instance(scene,'SM_EH_EntryCanopy_224',(offset+5,0,0))
    # Foundation steps: visual assembly props, not additional architectural modules.
    for i in range(3):
        m=Mesh();m.box((offset+5,-1.35+.34*i,-.20+.055*i),(2.15-.08*i,.72,.22+.11*i),'Stone',.012)
        m.object('Study_EntranceStep_%d'%i,scene.collection,['Stone'])
    return count

def build(revise=False):
    assert revise or not (ROOT/(NAME+'.blend')).exists(),'Use explicit revise mode for the own study'
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for d in ('Textures','Exports','Previews','Evidence'): (ROOT/d).mkdir(exist_ok=True)
    textures()
    modules=bpy.data.scenes.new('Module_Library')
    modules.unit_settings.system='METRIC';modules.unit_settings.scale_length=1
    for typ in ('SolidA','SolidB','Window','Entry'):wall_asset(typ,modules.collection)
    for typ in ('Mid','End'):roof_asset(typ,modules.collection)
    misc_assets(modules.collection)
    main=bpy.context.scene;main.name='House_10x12'
    main.unit_settings.system='METRIC';main.unit_settings.scale_length=1
    assembly(main,12)
    variant=bpy.data.scenes.new('House_10x16_Variation')
    variant.unit_settings.system='METRIC';variant.unit_settings.scale_length=1
    assembly(variant,16)
    bpy.context.preferences.filepaths.save_version=0
    bpy.context.window.scene=modules
    if 'io_scene_fbx' not in bpy.context.preferences.addons:bpy.ops.preferences.addon_enable(module='io_scene_fbx')
    settings=dict(PROFILE['export_settings']);settings['object_types']=set(settings['object_types'])
    info=[]
    for name,data in ASSETS.items():
        bpy.ops.object.select_all(action='DESELECT')
        for obj in [data['object']]+data['ucx']:obj.select_set(True)
        bpy.context.view_layer.objects.active=data['object']
        assert bpy.ops.export_scene.fbx(filepath=str(ROOT/'Exports'/(name+'.fbx')),**settings)=={'FINISHED'}
        obj=data['object'];obj.data.calc_loop_triangles()
        info.append({'name':name,'vertices':len(obj.data.vertices),'triangles':len(obj.data.loop_triangles),
            'slots':[s.name for s in obj.data.materials],'uv_channels':len(obj.data.uv_layers),'ucx_hulls':len(data['ucx']),
            'description':data['description'],'joins_draft':data['joins'],'fbx':'Exports/'+name+'.fbx'})
    bpy.context.window.scene=main
    # Portable image paths; no packed textures required, no machine-specific dependency.
    for im in bpy.data.images:
        if im.source=='FILE' and im.filepath:im.filepath='//Textures/'+Path(im.filepath).name
    assert bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/(NAME+'.blend')))=={'FINISHED'}
    write('manifest.json',{'status':'draft','kit_id':'EH.HouseB.Prototype01','interface_version':'draft_1',
        'source':NAME+'.blend','source_revision':'4702ccf44e88d06e97d8e3975ec34b3982673a7f',
        'units':'Blender meters; UE_cm=(100*x,-100*y,100*z)','primary_footprint_m':[10,12],'comparison_footprint_m':[10,16],
        'wall_height_m':H,'dimensions_status':'Provisional study dimensions, not a canonical building standard',
        'blender':bpy.app.version_string,'build':bpy.app.build_hash.decode(),'export_profile':PROFILE,
        'assets':info,'textures':{m:[n.name for n in MATERIALS[m].node_tree.nodes if n.type=='TEX_IMAGE'] for m in ('Plaster','Timber','Stone','Jade')},
        'unreal_import_performed':False,'not_validated':['Unreal materials/import/reimport','gameplay door','Kapsel/PIE/camera','performance/LOD budgets','production interface acceptance'],
        'collision_caveats':['Gable, eave infills, static door and entry canopy have no supplied UCX yet','Roof convex approximation must be measured and reviewed in Unreal','Window glazing blocks intentionally using a single full-panel hull; no breakability gameplay','Entry arch collision has four upper strips: conservatively approximated, rectangular minimum clearance 136x222 cm'],
        'variation':'Separate 10x16 assembly reuses exactly the same mesh datablocks; two solid wall detail variants',
        'sha256':{NAME+'.blend':sha(ROOT/(NAME+'.blend')),**{'Exports/'+p.name:sha(p) for p in (ROOT/'Exports').glob('*.fbx')}}})
    print('HOUSE_BUILD_OK',len(info),'exported modules')

def setup_presentation(scene,length):
    scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
    scene.cycles.device='CPU'
    scene.render.resolution_x=1280;scene.render.resolution_y=960;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.view_settings.view_transform='AgX'
    world=bpy.data.worlds.new('PresentationWorld_'+scene.name);world.use_nodes=True
    world.node_tree.nodes['Background'].inputs['Color'].default_value=(.55,.65,.75,1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35;scene.world=world
    ground=bpy.data.meshes.new('PresentationGround')
    ground.from_pydata([(-200,-200,-.28),(200,-200,-.28),(200,200,-.28),(-200,200,-.28)],[],[(0,1,2,3)])
    obj=bpy.data.objects.new('PresentationGround',ground);scene.collection.objects.link(obj)
    mat=bpy.data.materials.new('PresentationGround');mat.use_nodes=True
    bsdf=mat.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(.18,.17,.15,1);bsdf.inputs['Roughness'].default_value=.85
    ground.materials.append(mat)
    for name,loc,power,size,color in [('Key',(-6,-7,15),2400,9,(1,.88,.72)),('Fill',(15,2,12),1500,8,(.75,.85,1)),('Rim',(1,length+6,13),2000,7,(1,.94,.82))]:
        lamp=bpy.data.lights.new('Presentation_'+name,'AREA');lamp.energy=power;lamp.shape='DISK';lamp.size=size;lamp.color=color
        light=bpy.data.objects.new(lamp.name,lamp);scene.collection.objects.link(light);light.location=loc
        light.rotation_euler=(Vector((5,length/2,2))-light.location).to_track_quat('-Z','Y').to_euler()
    sun=bpy.data.lights.new('Presentation_Sun','SUN');sun.energy=1.5;sun.angle=math.radians(10)
    obj=bpy.data.objects.new(sun.name,sun);scene.collection.objects.link(obj);obj.rotation_euler=(math.radians(28),math.radians(-20),math.radians(-30))
    for name,loc,target in [('Front',(21,-22,13.5),(5,4.7,2.6)),('Rear',(-15,length+22,12),(5,length*.58,2.6))]:
        data=bpy.data.cameras.new('Camera_'+name);camera=bpy.data.objects.new(data.name,data);scene.collection.objects.link(camera)
        camera.location=loc;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=23 if length==12 else 27
        camera['PresentationView']=name
        if name=='Front':scene.camera=camera

def render_study():
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/(NAME+'.blend')))
    for scene,length in [(bpy.data.scenes['House_10x12'],12),(bpy.data.scenes['House_10x16_Variation'],16)]:
        if not scene.camera:setup_presentation(scene,length)
    bpy.context.window.scene=bpy.data.scenes['House_10x12']
    # Presentation cameras/lights stay transient; the validated source is never re-saved here.
    for scene_name,view,out in [('House_10x12','Front','house_front.png'),('House_10x12','Rear','house_rear.png'),('House_10x16_Variation','Front','house_long_variant.png')]:
        scene=bpy.data.scenes[scene_name];bpy.context.window.scene=scene
        scene.camera=next(o for o in scene.objects if o.type=='CAMERA' and o.get('PresentationView')==view)
        scene.render.filepath=str(ROOT/'Previews'/out)
        bpy.ops.render.render(write_still=True)
        print('RENDER_OK',out,flush=True)

def audit(obj):
    m=obj.data;m.calc_loop_triangles()
    assert all(math.isfinite(c) for v in m.vertices for c in v.co)
    assert all(math.isfinite(c) for uv in m.uv_layers[0].data for c in uv.uv)
    assert all(t.area>1e-12 for t in m.loop_triangles),obj.name+': degenerate triangle'
    for t in m.loop_triangles:
        a,b,c=[m.uv_layers[0].data[i].uv for i in t.loops]
        assert abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))>1e-12,obj.name+': degenerate UV triangle'
    bm=bmesh.new();bm.from_mesh(m)
    bad_edges=sum(not(e.is_manifold and e.is_contiguous) for e in bm.edges)
    volume=bm.calc_volume(signed=True);bm.free()
    assert bad_edges==0,(obj.name,bad_edges)
    assert volume>0,(obj.name,volume)
    assert all(abs(x)<1e-6 for x in obj.location) and all(abs(x)<1e-6 for x in obj.rotation_euler)
    assert all(abs(x-1)<1e-6 for x in obj.scale)
    return {'vertices':len(m.vertices),'triangles':len(m.loop_triangles),'slots':[x.name for x in m.materials],
        'closed_components_consistent_winding':True,'signed_volume_m3':volume,'uv_channels':len(m.uv_layers),
        'bounds_m':[[min(v.co[k] for v in m.vertices) for k in range(3)],[max(v.co[k] for v in m.vertices) for k in range(3)]]}

def verify():
    manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
    for p,h in manifest['sha256'].items():assert sha(ROOT/p)==h,p
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/(NAME+'.blend')))
    modules=bpy.data.scenes['Module_Library'];bpy.context.window.scene=modules
    assert len([o for o in modules.objects if not o.name.startswith('UCX_')])==len(manifest['assets'])
    source={}
    for item in manifest['assets']:
        obj=modules.objects[item['name']];source[item['name']]=audit(obj)
        assert source[item['name']]['triangles']==item['triangles']
        for c in [o for o in modules.objects if o.name.startswith('UCX_'+item['name']+'_')]:
            audit(c)
            error=max(p.normal.dot(v.co-c.data.vertices[p.vertices[0]].co) for p in c.data.polygons for v in c.data.vertices)
            assert error<1e-5,(c.name,error)
        if item['name'].startswith('SM_EH_EaveFill_') or item['name']=='SM_EH_Gable_W1000':
            top_ids={i for p in obj.data.polygons if p.material_index==0 for i in p.vertices if obj.data.vertices[i].co.z>H+1e-5}
            assert top_ids
            errors=[]
            for i in top_ids:
                p=obj.data.vertices[i].co
                if item['name']=='SM_EH_Gable_W1000':expected=roof_surface_z(p.x,p.y+.8,'End')-.12
                elif '_Mid_' in item['name']:expected=roof_surface_z(p.y,0,'Mid')-.12
                else:expected=roof_surface_z(p.y,.8+(p.x if '_EndA_' in item['name'] else 2-p.x),'End')-.12
                errors.append(abs(p.z-expected))
            source[item['name']]['roof_underside_fit_max_error_m']=max(errors)
            assert max(errors)<1e-5,(item['name'],max(errors))
    for im in bpy.data.images:
        if im.source=='FILE':assert Path(bpy.path.abspath(im.filepath)).is_file(),im.filepath
    # Reused meshes, one entrance, positive transforms, and repeatable roof spans in both houses.
    assemblies={}
    for sn,length in [('House_10x12',12),('House_10x16_Variation',16)]:
        scene=bpy.data.scenes[sn];bpy.context.window.scene=scene;bpy.context.view_layer.update()
        inst=[o for o in scene.objects if o.get('SourceModule')]
        entries=[o for o in inst if o['SourceModule']=='SM_EH_Wall_Entry_200x24x320'];assert len(entries)==1
        assert all(all(abs(x-1)<1e-6 for x in o.scale) for o in inst)
        assert all(o.data==modules.objects[o['SourceModule']].data for o in inst)
        roof=[o for o in inst if o['SourceModule'].startswith('SM_EH_Roof_')]
        # At each end/middle boundary check actual cap vertices in world space.
        seams=[]
        for y in range(2,length,2):
            sets=[]
            for obj in roof:
                pts=[obj.matrix_world@v.co for v in obj.data.vertices if abs((obj.matrix_world@v.co).y-y)<1e-5]
                if pts:sets.append(pts)
            assert len(sets)==2,(sn,y,len(sets))
            # Main roof shell vertices are first; decorative ribs may intentionally overlap the wood joints.
            a,b=sets
            shell_a=[p for p in a if min(abs(p.z-roof_z(p.x,0,'Mid')),abs(p.z-(roof_z(p.x,0,'Mid')-.12)))<1e-4]
            shell_b=[p for p in b if min(abs(p.z-roof_z(p.x,0,'Mid')),abs(p.z-(roof_z(p.x,0,'Mid')-.12)))<1e-4]
            error=max(min((p-q).length for q in shell_b) for p in shell_a);assert error<1e-5
            seams.append({'y_m':y,'max_shell_position_error_m':error})
        assemblies[sn]={'footprint_m':[10,length],'entry_fields':1,'mesh_instances':len(inst),'shared_module_data':True,'roof_seams':seams}
    if 'io_scene_fbx' not in bpy.context.preferences.addons:bpy.ops.preferences.addon_enable(module='io_scene_fbx')
    roundtrip={}
    for item in manifest['assets']:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        if 'io_scene_fbx' not in bpy.context.preferences.addons:bpy.ops.preferences.addon_enable(module='io_scene_fbx')
        assert bpy.ops.import_scene.fbx(filepath=str(ROOT/item['fbx']),use_custom_normals=True,use_anim=False,use_image_search=False)=={'FINISHED'}
        meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
        render=[o for o in meshes if not o.name.startswith('UCX_')];assert len(render)==1
        observed=audit(render[0]);expected=source[item['name']]
        assert observed['triangles']==expected['triangles']
        assert observed['slots']==expected['slots']
        assert len(meshes)-1==item['ucx_hulls']
        err=max(abs(observed['bounds_m'][i][j]-expected['bounds_m'][i][j]) for i in (0,1) for j in (0,1,2));assert err<1e-4
        observed['bounds_roundtrip_max_error_m']=err;roundtrip[item['name']]=observed
    write('verification.json',{'status':'passed','scope':'Blender source reopen, geometry and per-module FBX Blender roundtrip; not Unreal validation',
        'source':source,'roundtrip':roundtrip,'assemblies':assemblies,'blender':bpy.app.version_string,'unreal_import_performed':False})
    print('HOUSE_VERIFY_OK',len(source),'modules, both house assemblies, FBX roundtrips')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=['build','revise','verify','render'],required=True)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    {'build':build,'revise':lambda:build(revise=True),'verify':verify,'render':render_study}[args.mode]()
