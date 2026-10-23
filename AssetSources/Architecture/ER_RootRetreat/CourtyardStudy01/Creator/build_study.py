"""Local Blender architectural study. Writes only beside this script. No Unreal API.
Run Blender --background --factory-startup --python-exit-code 1 --python this.py -- --mode build|verify|render.
The matching library meshes stay at identity; visible scene objects instance their data.
"""
import argparse
import hashlib
import json
import math
import random
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

sys.dont_write_bytecode = True
STUDY = "B"
ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[4]
BASE = "e66d5beed7bb85313501659d646f25778515134b"
PREFIX = "EC" if STUDY == "A" else "ER"
KIT = "EC.HighCultureCity" if STUDY == "A" else "ER.RootRetreat"
MODULE = "StreetStudy01" if STUDY == "A" else "CourtyardStudy01"
BLEND = ROOT / (MODULE + ".blend")
PROFILE = REPO / "AssetSources/Calibration/BlenderUE01/unreal_import_profile.json"
REG = {}
PLACEMENTS = []
CHECKS = []
VIEWS = {}
MATS = {}
FACES = [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]


def dump(filename, obj):
    path = ROOT / filename
    assert path.resolve().is_relative_to(ROOT)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(obj, stream, indent=2, ensure_ascii=False)
        stream.write("\n")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def col(name):
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    return collection


class Geo:
    def __init__(self):
        self.v, self.f, self.smooth = [], [], []

    def add(self, vertices, faces, smooth=False):
        start = len(self.v)
        self.v.extend([tuple(v) for v in vertices])
        self.f.extend([tuple(start + i for i in face) for face in faces])
        self.smooth.extend([smooth] * len(faces))
        return self

    def box(self, lo, hi):
        x,y,z = lo
        a,b,c = hi
        assert a > x and b > y and c > z
        return self.add([(x,y,z),(a,y,z),(a,b,z),(x,b,z),(x,y,c),(a,y,c),(a,b,c),(x,b,c)],FACES)

    def tube(self, points, radii, sides=8):
        points = [Vector(p) for p in points]
        verts = []
        previous_u=None
        for i,p in enumerate(points):
            tangent = (points[min(i+1,len(points)-1)]-points[max(0,i-1)]).normalized()
            if previous_u is None:
                helper=min([Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1))],key=lambda a:abs(tangent.dot(a)))
                u=tangent.cross(helper).normalized()
            else:
                u=(previous_u-tangent*previous_u.dot(tangent)).normalized()
            previous_u=u
            v = tangent.cross(u)
            for j in range(sides):
                a = j*2*math.pi/sides
                verts.append(p + radii[i]*(math.cos(a)*u+math.sin(a)*v))
        faces = [tuple(reversed(range(sides))), tuple((len(points)-1)*sides+j for j in range(sides))]
        faces.extend([(i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j)
                      for i in range(len(points)-1) for j in range(sides)])
        return self.add(verts, faces, True)

    def ellipsoid(self, center, scale, rings=7, sides=12):
        # Closed latitude rings with distinct pole vertices.
        x,y,z = center
        a,b,c = scale
        verts = [(x,y,z-c)]
        for i in range(1,rings):
            t = -math.pi/2+math.pi*i/rings
            for j in range(sides):
                p = j*2*math.pi/sides
                verts.append((x+a*math.cos(t)*math.cos(p),y+b*math.cos(t)*math.sin(p),z+c*math.sin(t)))
        verts.append((x,y,z+c))
        faces = [(0,1+(j+1)%sides,1+j) for j in range(sides)]
        for i in range(rings-2):
            faces.extend([(1+i*sides+j,1+i*sides+(j+1)%sides,1+(i+1)*sides+(j+1)%sides,1+(i+1)*sides+j) for j in range(sides)])
        faces.extend([(1+(rings-2)*sides+j,1+(rings-2)*sides+(j+1)%sides,len(verts)-1) for j in range(sides)])
        return self.add(verts,faces,True)


def mesh_object(name, geo, material, collection):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(geo.v,[],geo.f)
    mesh.update()
    # Weld shared grid corners, remove no intended volume, then orient consistently.
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-7)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    for poly in mesh.polygons:
        poly.use_smooth = all(geo.smooth) if geo.smooth else False
    if material:
        mesh.materials.append(MATS[material])
    uv = mesh.uv_layers.new(name="UV0")
    for poly in mesh.polygons:
        axes = sorted(range(3),key=lambda k: abs(poly.normal[k]))[:2]
        for index in poly.loop_indices:
            p = mesh.vertices[mesh.loops[index].vertex_index].co
            uv.data[index].uv = (p[axes[0]]/2,p[axes[1]]/2)
    obj = bpy.data.objects.new(name,mesh)
    collection.objects.link(obj)
    return obj


def asset(label, geo, material, collisions=None, category="Structure"):
    name = "SM_"+PREFIX+"_"+label
    obj = mesh_object(name,geo,material,LIB)
    obj["study_asset"] = True
    obj["category"] = category
    obj["pivot_contract"] = "Local source origin; assembly placement in manifest; 1 m = 100 UE cm; no R255 interface"
    bodies = []
    for i,body in enumerate(collisions or []):
        hull = mesh_object("UCX_"+name+"_%02d"%i,body,None,COLL)
        hull.hide_render = True
        hull.display_type = "WIRE"
        bodies.append(hull)
    REG[label] = {"object":obj,"colliders":bodies,"category":category}
    return label


def box_asset(label, lo, hi, material, collision=False, category="Structure"):
    geo = Geo().box(lo,hi)
    return asset(label,geo,material,[geo] if collision else [],category)


def place(label, loc=(0,0,0), yaw=0, collection=None, tag=""):
    obj = REG[label]["object"].copy()
    obj.data = REG[label]["object"].data
    obj.name = PREFIX+"_"+(tag+"_" if tag else "")+label
    (collection or SCENE_COL).objects.link(obj)
    obj.location = loc
    obj.rotation_euler.z = math.radians(yaw)
    obj["library_asset"] = REG[label]["object"].name
    PLACEMENTS.append(obj)
    return obj


def transform(p, center, yaw):
    a=math.radians(yaw)
    return (center[0]+p[0]*math.cos(a)-p[1]*math.sin(a),center[1]+p[0]*math.sin(a)+p[1]*math.cos(a),center[2]+p[2])


def wall_grid(label,width,height,openings,mat,depth=.35):
    xs=sorted({-width/2,width/2}|{v for x,z,w,h in openings for v in (x-w/2,x+w/2)})
    zs=sorted({0,height}|{v for x,z,w,h in openings for v in (z,z+h)})
    occupied=set()
    bodies=[]
    for i in range(len(xs)-1):
        for j in range(len(zs)-1):
            x,z=(xs[i]+xs[i+1])/2,(zs[j]+zs[j+1])/2
            if not any(abs(x-a)<w/2 and b<z<b+h for a,b,w,h in openings):
                occupied.add((i,j))
                bodies.append(Geo().box((xs[i],0,zs[j]),(xs[i+1],depth,zs[j+1])))
    geo=Geo()
    for i,j in occupied:
        x,a,z,c=xs[i],xs[i+1],zs[j],zs[j+1]
        vertices=[(x,0,z),(a,0,z),(a,depth,z),(x,depth,z),(x,0,c),(a,0,c),(a,depth,c),(x,depth,c)]
        faces=[FACES[2],FACES[4]]  # front/back always exposed
        for neighbor,face in [((i-1,j),FACES[5]),((i+1,j),FACES[3]),((i,j-1),FACES[0]),((i,j+1),FACES[1])]:
            if neighbor not in occupied:
                faces.append(face)
        geo.add(vertices,faces)
    return asset(label,geo,mat,bodies)


def hip_roof(label,w,d,z,rise):
    b=[(-w/2,-d/2,z),(w/2,-d/2,z),(w/2,d/2,z),(-w/2,d/2,z)]
    t=[(-w*.18,-d*.20,z+rise),(w*.18,-d*.20,z+rise),(w*.18,d*.20,z+rise),(-w*.18,d*.20,z+rise)]
    geo=Geo().add(b+t,FACES)
    return asset(label,geo,"Slate",[geo])


def arch_points(width,bottom,height,y=0,n=12):
    # Elliptic arch cap with upright jambs, not a gameplay door.
    return [(-width/2,y,bottom),(-width/2,y,height-.45)]+[(width/2*math.cos(math.pi-math.pi*i/n),y,height-.45+.45*math.sin(math.pi*i/n)) for i in range(1,n+1)]+[(width/2,y,bottom)]


def frame_and_window(prefix,wood="Wood"):
    g=Geo()
    g.box((-.4,-.10,-.06),(.4,.14,.06)).box((-.4,-.10,.78),(.4,.14,.9))
    g.box((-.4,-.10,0),(-.325,.14,.84)).box((.325,-.10,0),(.4,.14,.84))
    g.tube([(0,-.115,.02),(0,-.115,.35),(-.16,-.115,.65),(-.27,-.115,.77)],[.024]*4,6)
    g.tube([(0,-.115,.35),(.16,-.115,.65),(.27,-.115,.77)],[.024]*3,6)
    asset(prefix+"WindowFrame_65x80",g,wood,category="Windows_Doors")
    box_asset(prefix+"WindowGlass_65x80",(-.325,.10,0),(.325,.13,.8),"Glass",False,"Windows_Doors")
    box_asset(prefix+"Shutter_32x84",(-.32,-.045,0),(0,.045,.84),wood,False,"Windows_Doors")


def tree_assets(label,scale=1):
    rng=random.Random(13)
    g=Geo().tube([(0,0,0),(.12,0,2.2),(-.18,.05,4),(.1,.1,6.1)],[.22,.18,.13,.05],10)
    for i in range(7):
        a=i*2.4
        end=(math.cos(a)*1.9,math.sin(a)*1.8,5.3+(i%3)*.6)
        g.tube([(0,0,2.8+i*.22),(end[0]*.4,end[1]*.4,4.5),end],[.09,.055,.018],7)
    asset(label+"Trunk",g,"Wood",category="Nature")
    g=Geo()
    for i in range(15):
        a=i*2.4
        r=1.3 if i>2 else .3
        g.ellipsoid((math.cos(a)*r,math.sin(a)*r,5.6+(i%4)*.42),(1.1,.95,.68),5,10)
    asset(label+"Crown",g,"Leaves",category="Nature")


def mannequin():
    g=Geo().ellipsoid((0,0,1.67),(.12,.11,.13),6,10)
    g.tube([(0,0,.9),(0,0,1.46)],[.17,.23],10)
    for s in [-1,1]:
        g.tube([(s*.13,0,.92),(s*.14,0,.46),(s*.16,-.04,.09)],[.095,.075,.055],8)
        g.tube([(s*.23,0,1.42),(s*.30,0,1.13),(s*.34,-.04,.91)],[.07,.055,.04],8)
        g.box((s*.16-.07,-.14,0),(s*.16+.07,.1,.12))
    asset("ScaleFigure_H180",g,"Figure",category="Reference")


def city_house(center,yaw,tag,roof="HipRoof_790x890"):
    def p(label,loc=(0,0,0),rot=0,group=None):
        return place(label,transform(loc,center,yaw),yaw+rot,group,tag)
    p("Floor_700x800")
    p("Facade_700x390",(0,-4,0))
    p("SideWall_800x390",(-3.5,0,0),-90)
    p("SideWall_800x390",(3.5,0,0),90)
    p("RearWall_700x390",(0,4,0),180)
    p(roof)
    p("StoneDressings",group=DECOR)
    p("EntryWoodArch",(0,-4.02,0),group=DECOR)
    p("TreeRelief",(0,-4.025,2.65),group=DECOR)
    for x in [-2.2,2.2]:
        p("CityWindowFrame_65x80",(x,-4.02,1.25),group=DETAIL)
        p("CityWindowGlass_65x80",(x,-4,1.25),group=DETAIL)
        p("CityShutter_32x84",(x-.43,-4.18,1.23),-25,DETAIL)
        p("CityShutter_32x84",(x+.43,-4.18,1.23),205,DETAIL)
        p("CityWindowFrame_65x80",(-x,4.02,1.25),180,DETAIL)
        p("CityWindowGlass_65x80",(-x,4,1.25),180,DETAIL)
    for y in [-2,2]:
        for x,rot in [(-3.5,-90),(3.5,90)]:
            p("CityWindowFrame_65x80",(x,y,1.25),rot,DETAIL)
            p("CityWindowGlass_65x80",(x,y,1.25),rot,DETAIL)
    p("DoorLeaf_140x235",(-.70,-3.69,0),100,DETAIL)
    if tag=="House_C":
        p("PorchPosts_220x270",(0,-4.9,0))
        p("PorchRoof_240x150",(0,-4.65,2.7))
    CHECKS.append({"name":tag,"center":center,"yaw":yaw,"floor_samples":[[-2,0],[0,0],[2,1]],
                   "door_local_front":[0,-4,0],"clear_width_m":1.3,"clear_height_m":2.3,"inside_top_m":3.9})


def build_city():
    openings=[(0,0,1.5,2.45),(-2.2,1.25,.65,.8),(2.2,1.25,.65,.8)]
    wall_grid("Facade_700x390",7,3.9,openings,"Stone")
    wall_grid("SideWall_800x390",8,3.9,[(-2,1.25,.65,.8),(2,1.25,.65,.8)],"Stone")
    wall_grid("RearWall_700x390",7,3.9,[(-2.2,1.25,.65,.8),(2.2,1.25,.65,.8)],"Stone")
    box_asset("Floor_700x800",(-3.5,-4,-.16),(3.5,4,0),"StoneFloor",True)
    hip_roof("HipRoof_790x890",7.9,8.9,3.9,1.5)
    hip_roof("HipRoof_LowVariant_790x890",7.9,8.9,3.9,1.1)
    g=Geo()
    bodies=[]
    for x in [-1.02,1.02]:
        body=Geo().box((x-.1,-.1,0),(x+.1,.1,2.7))
        g.box((x-.1,-.1,0),(x+.1,.1,2.7))
        bodies.append(body)
    asset("PorchPosts_220x270",g,"StoneLight",bodies)
    hip_roof("PorchRoof_240x150",2.4,1.5,0,.32)
    g=Geo()
    for x in [-3.45,3.45]:
        g.box((x-.10,-4.14,0),(x+.10,-3.90,3.9))
        g.box((x-.16,-4.18,3.66),(x+.16,-3.86,3.92))
    for x1,x2 in [(-3.5,-.85),(.85,3.5)]:
        g.box((x1,-4.1,.05),(x2,-3.9,.28))
    g.box((-3.6,-4.16,3.76),(3.6,-3.84,3.96))
    g.box((-.92,-4.15,0),(-.76,-3.75,2.5)).box((.76,-4.15,0),(.92,-3.75,2.5))
    g.tube(arch_points(1.7,2.0,2.8,-4.13),[.09]*16,8)
    asset("StoneDressings",g,"StoneLight",category="Decor")
    g=Geo().tube(arch_points(1.45,0,2.46,0),[.065]*16,8)
    asset("EntryWoodArch",g,"Wood",category="Decor")
    g=Geo().tube([(0,0,0),(0,0,.28),(-.04,0,.62),(0,0,1.02)],[.075,.055,.04,.018],8)
    for s in [-1,1]:
        for h in [.28,.55]:
            g.tube([(0,0,h),(s*.24,0,h+.18),(s*.48,0,h+.42),(s*.51,0,h+.65)],[.04,.035,.023,.009],7)
    asset("TreeRelief",g,"StoneLight",category="Decor")
    box_asset("DoorLeaf_140x235",(0,-.06,0),(1.4,.06,2.35),"Wood",True,"Windows_Doors")
    frame_and_window("City")
    box_asset("Paving_120x80",(-.594,-.394,-.10),(.594,.394,0),"StoneFloor",False,"Ground")
    box_asset("GroundBase_3200x3000",(-16,-10,-.35),(16,20,-.12),"Soil",True,"Ground")
    box_asset("Curb_100x20",(-.49,-.10,-.10),(.49,.10,0),"StoneLight",False,"Ground")
    box_asset("PlanterRim",(-.75,-.75,0),(.75,.75,.45),"Stone",False,"Ground")
    tree_assets("StreetTree")
    mannequin()
    city_house((-8.5,0,0),90,"House_A")
    city_house((-8.5,10,0),90,"House_B","HipRoof_LowVariant_790x890")
    city_house((8.5,5,0),-90,"House_C")
    place("GroundBase_3200x3000",collection=GROUND)
    for ix in range(-4,5):
        for iy in range(-11,24):
            place("Paving_120x80",(ix*1.2+(iy%2)*.12,iy*.8,-.03),collection=GROUND)
    for x in [-4.2,4.2]:
        for y in range(-9,19):
            place("Curb_100x20",(x,y,-.01),90,GROUND)
    for xy in [(-3.5,5),(3.5,11)]:
        place("PlanterRim",(*xy,-.03),collection=GROUND)
        place("StreetTreeTrunk",(*xy,.40),collection=NATURE)
        place("StreetTreeCrown",(*xy,.40),collection=NATURE)
    place("ScaleFigure_H180",(-.8,1.8,0),collection=REF)
    VIEWS.update({"01_eye_overview":((0,-10,1.8),(0,5,2.6),24),
                  "02_house":((1,-8,2.1),(-7,0,2.3),30),
                  "03_plan":((22,-20,26),(-1,5,0),40),
                  "04_interior":((-10.8,0,1.65),(-3.8,0,1.65),22)})


def strip_unit(label,width,depth,lower,upper,material,segments=12):
    geo=Geo()
    bodies=[]
    for i in range(segments):
        a=-width/2+width*i/segments
        b=-width/2+width*(i+1)/segments
        v=[(a,-depth/2,lower(a)),(b,-depth/2,lower(b)),(b,depth/2,lower(b)),(a,depth/2,lower(a)),
           (a,-depth/2,upper(a)),(b,-depth/2,upper(b)),(b,depth/2,upper(b)),(a,depth/2,upper(a))]
        faces=[FACES[k] for k in [0,1,2,4]]
        if i==0:
            faces.append(FACES[5])
        if i==segments-1:
            faces.append(FACES[3])
        geo.add(v,faces)
        bodies.append(Geo().add(v,FACES))
    return asset(label,geo,material,bodies)


def old_core():
    # Closed cylindrical wall with a real four-cell opening; no interior cap faces.
    count=40
    geo=Geo()
    bodies=[]
    # Main external aperture at 0deg; new internal links at -90/+90deg.
    occupied={(i,j) for i in range(count) for j in range(2)
              if not (j==0 and any(abs((-180+(i+.5)*9)-a)<18 for a in [0,-90,90]))}
    def vtx(r,t,z):
        return (r*math.sin(math.radians(t)),-r*math.cos(math.radians(t)),z)
    for i,j in occupied:
        a,b=-180+i*9,-180+(i+1)*9
        lo,hi=([0,2.45,4.3][j],[0,2.45,4.3][j+1])
        v=[vtx(2.2,a,lo),vtx(2.6,a,lo),vtx(2.6,b,lo),vtx(2.2,b,lo),
           vtx(2.2,a,hi),vtx(2.6,a,hi),vtx(2.6,b,hi),vtx(2.2,b,hi)]
        faces=[FACES[3],FACES[5]]
        for neighbor,idx in [(((i-1)%count,j),2),(((i+1)%count,j),4),((i,j-1),0),((i,j+1),1)]:
            if neighbor not in occupied:
                faces.append(FACES[idx])
        geo.add(v,faces)
        bodies.append(Geo().add(v,FACES))
    asset("OldCoreLinkedShell_R260_H430_v02",geo,"BarkOld",bodies)
    # A convex cylinder floor, not an ellipsoid pretending to be flat ground.
    verts=[(2.6*math.cos(i*2*math.pi/count),2.6*math.sin(i*2*math.pi/count),z) for z in [-.18,0] for i in range(count)]
    faces=[tuple(reversed(range(count))),tuple(count+i for i in range(count))]
    faces.extend([(i,(i+1)%count,count+(i+1)%count,count+i) for i in range(count)])
    floor=Geo().add(verts,faces)
    asset("OldCoreFloor_R260",floor,"Wood",[floor])
    dome=Geo().ellipsoid((0,0,4.6),(3.2,3.1,.9),8,24)
    asset("OldCoreCrown_640x620",dome,"BarkOld",[dome])


def connected_floor():
    """Union the three room floors; no overlapping render faces or transition step."""
    components=[]
    for label,center,yaw in [("WingFloor_640x550",(-5.5,3.70,0),-12),
                             ("WingFloor_640x550",(5.5,3.70,0),12),
                             ("OldCoreFloor_R260",(0,3,0),0)]:
        mesh=REG[label]["object"].data
        components.append(Geo().add([transform(v.co,center,yaw) for v in mesh.vertices],
                                    [list(p.vertices) for p in mesh.polygons]))
    primary=mesh_object("Temp_FloorUnion",components[0],None,LIB)
    bpy.context.view_layer.objects.active=primary
    primary.select_set(True)
    for i,geo in enumerate(components[1:]):
        operand=mesh_object("Temp_FloorOperand_"+str(i),geo,None,LIB)
        modifier=primary.modifiers.new("FloorUnion_"+str(i),"BOOLEAN")
        modifier.operation="UNION"
        modifier.solver="EXACT"
        modifier.object=operand
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        bpy.data.objects.remove(operand,do_unlink=True)
    merged=Geo().add([v.co[:] for v in primary.data.vertices],[list(p.vertices) for p in primary.data.polygons])
    bpy.data.objects.remove(primary,do_unlink=True)
    asset("ConnectedFloor_v02",merged,"Wood",components)
    place("ConnectedFloor_v02")
    for label in ["WingFloor_640x550","OldCoreFloor_R260"]:
        item=REG.pop(label)
        for obj in [item["object"]]+item["colliders"]:
            bpy.data.objects.remove(obj,do_unlink=True)


def retreat_wing(center,yaw,tag):
    def p(label,loc=(0,0,0),rot=0,collection=None):
        return place(label,transform(loc,center,yaw),yaw+rot,collection,tag)
    p("WingWindowFacade_640x280_v02",(0,-2.75,0))
    p("WingRear_640x280",(0,2.75,0),180)
    west=tag=="WestWing"
    p("WingSide_550x311" if west else "WingInternalLink_550x311_v02",(-3.2,0,0),-90)
    p("WingInternalLink_550x311_v02" if west else "WingSide_550x311",(3.2,0,0),90)
    p("WingCrownFill",(0,-2.575,0))
    p("WingCrownFill",(0,2.575,0))
    p("WingRootVault_720x620")
    p("WingRootRibs",collection=DECOR)
    p("WingClosedStoneSill_v02",collection=DECOR)
    p("RootDoorArch",(3.2 if west else -3.2,0,0),90 if west else -90,DECOR)
    p("RetreatWindowFrame_65x80",(0,-2.80,1.05),collection=DETAIL)
    p("RetreatWindowGlass_65x80",(0,-2.75,1.05),collection=DETAIL)
    p("Bench_210x56",(2.05 if tag=="WestWing" else -2.05,-3.35,0),collection=DECOR)
    for x in [-2.05,2.05]:
        p("RetreatWindowFrame_65x80",(x,-2.80,.95),collection=DETAIL)
        p("RetreatWindowGlass_65x80",(x,-2.75,.95),collection=DETAIL)
        p("RetreatWindowFrame_65x80",(-x,2.80,.95),180,DETAIL)
        p("RetreatWindowGlass_65x80",(-x,2.75,.95),180,DETAIL)
    for x,rot in [(-3.2,-90),(3.2,90)]:
        if (west and x>0) or (not west and x<0):
            continue
        for y in [-1.3,1.3]:
            p("RetreatWindowFrame_65x80",(x,y,.95),rot,DETAIL)
            p("RetreatWindowGlass_65x80",(x,y,.95),rot,DETAIL)
    CHECKS.append({"name":tag,"center":center,"yaw":yaw,"floor_samples":[[-1.8,0],[0,0],[1.8,1]],
                   "door_local_front":[3.2 if west else -3.2,0,0],"axis":"X","direction":1 if west else -1,
                   "access":"internal_only","clear_width_m":1.3,"clear_height_m":2.3,"inside_top_m":3.65})


def build_retreat():
    wall_grid("WingWindowFacade_640x280_v02",6.4,2.8,[(0,1.05,.65,.8),(-2.05,.95,.65,.8),(2.05,.95,.65,.8)],"BarkYoung")
    wall_grid("WingRear_640x280",6.4,2.8,[(-2.05,.95,.65,.8),(2.05,.95,.65,.8)],"BarkYoung")
    wall_grid("WingSide_550x311",5.5,3.11,[(-1.3,.95,.65,.8),(1.3,.95,.65,.8)],"BarkYoung")
    wall_grid("WingInternalLink_550x311_v02",5.5,3.11,[(0,0,1.6,2.4)],"BarkYoung")
    box_asset("WingFloor_640x550",(-3.2,-2.75,-.18),(3.2,2.75,0),"Wood",True)
    profile=lambda x: 2.95+.75*(1-(x/3.6)**2)
    strip_unit("WingRootVault_720x620",7.2,6.2,profile,lambda x:profile(x)+.20,"BarkYoung")
    strip_unit("WingCrownFill",6.4,.35,lambda x:2.8,profile,"BarkYoung")
    box_asset("DoorLeaf_140x230",(0,-.07,0),(1.4,.07,2.3),"Wood",True,"Windows_Doors")
    g=Geo().tube(arch_points(1.63,0,2.52,-.03),[.12]*16,10)
    asset("RootDoorArch",g,"BarkOld",category="Decor")
    frame_and_window("Retreat","Wood")
    g=Geo()
    for x in [-2.8,2.8]:
        s=1 if x>0 else -1
        g.tube([(x+s*.55,-2.95,0),(x+s*.12,-3.03,.65),(x,-3.04,1.8),(x-s*.35,-3.0,2.75),(x-s*1.0,-2.92,3.40)], [.14,.21,.20,.16,.07],10)
    for y in [-2.93,0,2.93]:
        pts=[(-3.52+7.04*i/14,y,profile(-3.52+7.04*i/14)+.19) for i in range(15)]
        g.tube(pts,[.10]*15,8)
    asset("WingRootRibs",g,"BarkOld",category="Decor")
    g=Geo()
    g.box((-3.2,-2.84,0),(3.2,-2.55,.25))
    asset("WingClosedStoneSill_v02",g,"StoneFloor",category="Decor")
    old_core()
    # Visible living tree starts above the inhabited shell, preserving its room.
    g=Geo().tube([(-.4,.5,4.75),(-.65,.55,6.4),(-.35,.45,8.4),(-1.0,.3,10.8)], [1.05,.85,.65,.30],14)
    for i,(end,startz) in enumerate([((3.5,.2,10.2),6.5),((-4.0,.8,10.5),7.3),((1.4,3.8,11.2),7.0),((-1.2,-2.8,10.6),8.0)]):
        g.tube([(-.55,.5,startz),(end[0]*.5,end[1]*.5,9),end],[.43,.26,.09],10)
    asset("LivingOldTrunk",g,"BarkOld",category="Nature")
    g=Geo()
    for s in [-1,1]:
        g.tube([(s*3.8,-2.2,.0),(s*2.5,-2.8,.45),(s*1.95,-2.2,1.7),(s*1.6,-2.1,3.6),(s*.65,.4,5.4)], [.22,.34,.40,.48,.37],12)
        g.tube([(s*3.8,2.2,0),(s*2.8,1.85,.6),(s*2.05,1.6,2.0),(s*1.5,1,4.2),(s*.7,.55,5.3)], [.18,.28,.36,.39,.26],10)
        g.tube([(s*1.05,-2.72,.08),(s*1.08,-2.77,1.5),(s*.90,-2.7,2.55),(0,-2.6,3.10)], [.13,.15,.13,.07],10)
    asset("OldButtressRoots",g,"BarkOld",category="Decor")
    g=Geo()
    rng=random.Random(22)
    for i in range(26):
        a=i*2.39996
        r=2.8 if i>4 else .5
        g.ellipsoid((r*math.cos(a),r*.8*math.sin(a),9.8+(i%4)*.55),(1.8,1.5,.85),5,10)
    asset("OldTreeCanopy",g,"Leaves",category="Nature")
    g=Geo().tube([(.9,1.7,3.45),(1.1,1.75,4.7),(.85,1.9,6.5)],[.35,.24,.10],10)
    g.tube([(1.06,1.77,4.8),(1.6,1.6,5.7),(2.0,1.5,6.1)],[.16,.10,.035],8)
    g.tube([(.98,1.8,5.3),(.2,1.85,5.8),(-.7,1.9,6.2)],[.13,.08,.035],8)
    asset("YoungLivingTrunk",g,"BarkYoung",category="Nature")
    g=Geo()
    for p in [(.8,1.9,6.65),(2,1.5,6.3),(-.7,1.9,6.5),(.7,2.8,6.35),(.4,.8,6.6)]:
        g.ellipsoid(p,(1.1,1,.65),5,10)
    asset("YoungTreeCrown",g,"Leaves",category="Nature")
    # Curved outward connections link the three masses without closing the courtyard.
    g=Geo()
    for s in [-1,1]:
        g.tube([(s*2.0,2.5,2.6),(s*3.2,2.0,3.25),(s*4.2,1.4,3.35),(s*5.0,.8,3.25)], [.28,.32,.25,.14],10)
    asset("LinkingRootArches",g,"BarkOld",category="Decor")
    box_asset("Ground_2600x2300",(-13,-10,-.3),(13,13,-.12),"Soil",True,"Ground")
    box_asset("CourtStone_100x70",(-.485,-.335,-.10),(.485,.335,0),"StoneFloor",False,"Ground")
    g=Geo()
    for x in [-.85,.85]:
        g.box((x-.09,-.22,0),(x+.09,.22,.42))
    g.box((-1.05,-.28,.42),(1.05,.28,.53))
    asset("Bench_210x56",g,"Wood",category="Decor")
    g=Geo()
    verts=[(x,y,z) for z in [0,.34] for x,y in [(-1.25,-.70),(1.25,-.70),(1.25,.70),(-1.25,.70),(-1.07,-.52),(1.07,-.52),(1.07,.52),(-1.07,.52)]]
    faces=[]
    for i in range(4):
        j=(i+1)%4
        faces.extend([(i,j,8+j,8+i),(4+j,4+i,12+i,12+j),(i,4+i,4+j,j),(8+i,8+j,12+j,12+i)])
    g.add(verts,faces)
    asset("HerbBed_250x140",g,"StoneFloor",category="Decor")
    g=Geo()
    for i in range(12):
        x=-.9+(i%4)*.6
        y=-.33+(i//4)*.33
        g.ellipsoid((x,y,.35),(.22,.18,.23),4,8)
    asset("HerbClusters",g,"Herbs",category="Nature")
    mannequin()
    retreat_wing((-5.5,3.70,0),-12,"WestWing")
    retreat_wing((5.5,3.70,0),12,"EastWing")
    connected_floor()
    for label in ["OldCoreLinkedShell_R260_H430_v02","OldCoreCrown_640x620"]:
        place(label,(0,3,0),tag="OldCore")
    place("DoorLeaf_140x230",(-.70,.65,0),100,DETAIL,"OldCore")
    place("RootDoorArch",(0,.35,0),collection=DECOR,tag="OldCore")
    place("OldButtressRoots",(0,3,0),collection=DECOR)
    place("LivingOldTrunk",(0,3,0),collection=NATURE)
    place("OldTreeCanopy",(0,3,0),collection=NATURE)
    for center,yaw in [((-5.5,3.70,0),-12),((5.5,3.70,0),12)]:
        place("YoungLivingTrunk",center,yaw,NATURE)
        place("YoungTreeCrown",center,yaw,NATURE)
    place("LinkingRootArches",collection=DECOR)
    CHECKS.append({"name":"OldCore","center":[0,3,0],"yaw":0,"floor_samples":[[-1,0],[0,0],[1,.5]],
                   "door_local_front":[0,-2.6,0],"clear_width_m":1.3,"clear_height_m":2.3,"inside_top_m":3.7})
    place("Ground_2600x2300",collection=GROUND)
    rng=random.Random(8)
    for ix in range(-8,9):
        for iy in range(-8,8):
            if (ix/9)**2+((iy+1)/10)**2<1:
                place("CourtStone_100x70",(ix*1.0,iy*.70,-.03),rng.uniform(-3,3),GROUND)
    for x in [-3.1,3.1]:
        place("HerbBed_250x140",(x,-4.7,0),collection=DECOR)
        place("HerbClusters",(x,-4.7,0),collection=NATURE)
    place("ScaleFigure_H180",(.7,-2.2,0),collection=REF)
    VIEWS.update({"01_eye_overview":((0,-17,1.8),(0,1.3,4.1),22),
                  "02_house":((-11,-9,2.0),(-4.5,.7,1.9),27),
                  "03_plan":((20,-21,25),(0,1.5,1),36),
                  "04_interior":((.55,3.15,1.65),(-5.5,3.65,1.5),20),
                  "05_connected_plan":((0,-1,23),(0,3,0),35)})


def materials():
    specs={"Stone":((.68,.61,.46),.82),"StoneLight":((.84,.76,.58),.75),"StoneFloor":((.42,.43,.39),.88),
           "Slate":((.075,.12,.15),.72),"Wood":((.15,.075,.032),.58),"BarkOld":((.22,.18,.115),.94),
           "BarkYoung":((.34,.23,.115),.88),"Leaves":((.16,.24,.065),.9),"Herbs":((.22,.31,.12),.9),
           "Soil":((.18,.17,.12),1),"Glass":((.12,.20,.22),.22),"Figure":((.35,.40,.43),.65)}
    for name,(color,roughness) in specs.items():
        mat=bpy.data.materials.new(name)
        mat.use_nodes=True
        mat.diffuse_color=(*color,1)
        bsdf=mat.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value=(*color,1)
        bsdf.inputs["Roughness"].default_value=roughness
        if name=="Glass":
            bsdf.inputs["Transmission Weight"].default_value=.35
        if name in ("Stone","StoneFloor","Slate","Wood","BarkOld","BarkYoung"):
            nodes=mat.node_tree.nodes
            noise=nodes.new("ShaderNodeTexNoise")
            noise.inputs["Scale"].default_value=16 if "Bark" not in name else 6
            noise.inputs["Detail"].default_value=2
            bump=nodes.new("ShaderNodeBump")
            bump.inputs["Strength"].default_value=.18
            bump.inputs["Distance"].default_value=.025 if "Bark" in name else .012
            mat.node_tree.links.new(noise.outputs["Fac"],bump.inputs["Height"])
            mat.node_tree.links.new(bump.outputs["Normal"],bsdf.inputs["Normal"])
        MATS[name]=mat


def lighting():
    scene=bpy.context.scene
    scene.render.engine="CYCLES"
    scene.cycles.samples=24
    scene.cycles.use_denoising=True
    if scene.world is None:
        scene.world=bpy.data.worlds.new("NeutralDaylight")
    scene.world.color=(.6,.65,.72)
    world=scene.world
    world.use_nodes=True
    world.node_tree.nodes.get("Background").inputs["Color"].default_value=(.65,.75,1,1)
    world.node_tree.nodes.get("Background").inputs["Strength"].default_value=.45
    data=bpy.data.lights.new("Daylight_5600K","SUN")
    data.energy=2.7
    data.angle=math.radians(12)
    obj=bpy.data.objects.new("Daylight_5600K",data)
    LIGHTS.objects.link(obj)
    obj.rotation_euler=(math.radians(28),math.radians(-25),math.radians(-30))
    data=bpy.data.lights.new("SkyFill","AREA")
    data.energy=1800
    data.shape="DISK"
    data.size=12
    obj=bpy.data.objects.new("SkyFill",data)
    LIGHTS.objects.link(obj)
    obj.location=(0,-5,11)
    data=bpy.data.cameras.new("Review_Camera")
    obj=bpy.data.objects.new("Review_Camera",data)
    LIGHTS.objects.link(obj)
    scene.camera=obj
    scene.render.resolution_x=1280
    scene.render.resolution_y=960
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    scene.view_settings.view_transform="AgX"


def stats(obj):
    deps=bpy.context.evaluated_depsgraph_get()
    ev=obj.evaluated_get(deps)
    mesh=ev.to_mesh()
    mesh.calc_loop_triangles()
    bm=bmesh.new()
    bm.from_mesh(mesh)
    result={"vertices":len(mesh.vertices),"triangles":len(mesh.loop_triangles),
            "material_slots":[m.name for m in mesh.materials],"uv_channels":len(mesh.uv_layers),
            "nonmanifold_edges":sum(not e.is_manifold for e in bm.edges),
            "degenerate_faces":sum(f.calc_area()<1e-10 for f in bm.faces),
            "bounds_blender_m":[[min(v.co[k] for v in mesh.vertices) for k in range(3)],[max(v.co[k] for v in mesh.vertices) for k in range(3)]]}
    bm.free()
    ev.to_mesh_clear()
    return result


def export_assets():
    bpy.ops.preferences.addon_enable(module="io_scene_fbx")
    settings=json.loads(PROFILE.read_text(encoding="utf-8"))["export_settings"]
    settings["object_types"]=set(settings["object_types"])
    exports=ROOT/"Exports"
    exports.mkdir(exist_ok=True)
    result=[]
    for label,item in REG.items():
        if item["category"]=="Reference":
            continue
        bpy.ops.object.select_all(action="DESELECT")
        obj=item["object"]
        for member in [obj]+item["colliders"]:
            member.select_set(True)
        bpy.context.view_layer.objects.active=obj
        path=exports/(obj.name+".fbx")
        bpy.ops.export_scene.fbx(filepath=str(path),**settings)
        result.append({"label":label,"asset_name":obj.name,"category":item["category"],"path":path.relative_to(ROOT).as_posix(),
                       "sha256":sha(path),"pivot_blender_m":[0,0,0],"rotation":[0,0,0],"scale":[1,1,1],
                       "collision_names":[o.name for o in item["colliders"]],"source_stats":stats(obj)})
    return result


def build(revise=False):
    global LIB,COLL,SCENE_COL,DECOR,DETAIL,GROUND,NATURE,REF,LIGHTS
    if revise:
        previous=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
        assert previous["base_commit"]==BASE and previous["module_id"]==MODULE
    else:
        assert not BLEND.exists(),"Do not overwrite a delivered study"
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version=0
    scene=bpy.context.scene
    scene.unit_settings.system="METRIC"
    scene.unit_settings.scale_length=1
    scene.unit_settings.length_unit="METERS"
    LIB=col("00_SourceMeshes")
    COLL=col("01_UCX_Source")
    SCENE_COL=col("10_Structure")
    DECOR=col("20_Decor")
    DETAIL=col("30_Doors_Windows")
    GROUND=col("40_Ground")
    NATURE=col("50_Nature")
    REF=col("60_Scale_180cm")
    LIGHTS=col("90_Review_Cameras_Lights")
    materials()
    build_city() if STUDY=="A" else build_retreat()
    LIB.hide_render=True
    COLL.hide_render=True
    lighting()
    bpy.context.view_layer.update()
    scene["study_id"]=KIT+"/"+MODULE
    scene["checks_json"]=json.dumps(CHECKS)
    scene["views_json"]=json.dumps(VIEWS)
    scene["status"]="draft"
    exports=export_assets()
    if revise:
        current={e["path"] for e in exports}
        for old in previous.get("exports",[]):
            obsolete=(ROOT/old["path"]).resolve()
            if old["path"] not in current and obsolete.is_relative_to((ROOT/"Exports").resolve()) and obsolete.suffix==".fbx":
                obsolete.unlink(missing_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in LIB.objects:
        obj.hide_set(True)
    for obj in COLL.objects:
        obj.hide_set(True)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    reference=("195a27381b9088b2f095ddfc4ab4d6c29add66e7626060700fe29c94c1af678f" if STUDY=="A" else "28dd234d36960c91154452c84d3eb225701985067dd9e93b28e40a06176f6afe")
    manifest={"kit_id":KIT,"module_id":MODULE,"interface_version":"0.2","revision":2,"status":"draft","base_commit":BASE,
              "creator_directory":ROOT.relative_to(REPO).as_posix(),"blender":bpy.app.version_string,
              "reference_image_sha256":reference,"source_blend":BLEND.name,"source_blend_sha256":sha(BLEND),
              "units":{"blender":"meters","unit_scale":1,"ue":"centimeters","mapping":"(100*x,-100*y,100*z)"},
              "export_profile":"Blender522_UE58_LegacyFBX_Calibration01","importer_intended":"FbxFactory / FbxStaticMeshImportData; Interchange not validated",
              "unreal_import_performed":False,"exports":exports,"interior_test_contracts":CHECKS,"review_views":VIEWS,
              "placement_instances":[{"object":o.name,"asset":o["library_asset"],"location_blender_m":list(o.location),
                                      "yaw_blender_degrees":math.degrees(o.rotation_euler.z),"scale":list(o.scale)} for o in PLACEMENTS],
              "materials":[{"name":m.name,"roughness":m.node_tree.nodes.get("Principled BSDF").inputs["Roughness"].default_value,
                            "base_color":list(m.diffuse_color)} for m in MATS.values()],
              "uv_policy":"UV0 per-face metric planar projections; overlaps intentionally allowed for prototype tile surfaces; no production atlas or lightmap UVs",
              "collision_policy":"Source-owned convex UCX on structural units; no enclosing whole-house hull. Decorative meshes have no collision.",
              "prototype_assumptions":(["Three 7x8m one-storey houses; 3.9m wall crown; 5.0/5.4m roof tops; 9m facade-to-facade street", "1.5x2.45m structural door apertures, 1.3x2.3m tested central clearance", "65x80cm small windows; source wall thickness35cm"] if STUDY=="A" else ["Three connected masses within approx20m width; living-tree association remains provisional"]),
              "interface":"0.2 connected-room study; changed facades/internal wall/core interfaces have new asset names. No R255 compatibility or Unreal reimport.",
              "approved_change":"User selected one main entrance on the old core, window-only wing fronts, and internally connected rooms. Scene decision only, no culture/lore rule.",
              "connectivity":{"external_entrances":1,"wing_centers_blender_m":[[-5.5,3.70,0],[5.5,3.70,0]],
                              "wing_yaws_blender_degrees":[-12,12],"core_center_blender_m":[0,3,0],
                              "internal_link_apertures":"Wing inner wall centered at local y0, width1.6m, height2.4m; core angular apertures +/-90deg with36deg sweep, height2.45m",
                              "floor":"One Boolean-unioned render floor at Z0 with three source-owned convex UCX; overlapping proxy volumes intentional at shared level"},
              "lods":1,"nanite_intended":False,"textures":[],"not_validated":["Unreal import/reimport","PIE/player capsule/camera","performance","packaging","production materials/lightmaps"]}
    dump("manifest.json",manifest)
    print("STUDY_BUILD_OK",MODULE,len(exports),"FBX units",flush=True)


def instance_bvh(obj,source=None):
    mesh=(source or obj).data
    return BVHTree.FromPolygons([obj.matrix_world@v.co for v in mesh.vertices],[list(p.vertices) for p in mesh.polygons],all_triangles=False)


def verify():
    manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    assert bpy.context.scene.unit_settings.scale_length==1
    assert not bpy.data.libraries
    assert sha(BLEND)==manifest["source_blend_sha256"]
    src=[]
    for entry in manifest["exports"]:
        obj=bpy.data.objects[entry["asset_name"]]
        measured=stats(obj)
        assert measured["degenerate_faces"]==0,(obj.name,measured)
        assert measured["nonmanifold_edges"]==0,(obj.name,measured)
        assert len(measured["material_slots"])<=4
        assert measured["uv_channels"]==1
        src.append({"asset":obj.name,"source_reopen":measured})
    structure=[o for o in bpy.data.collections["10_Structure"].objects if o.type=="MESH"]
    doors=[o for o in bpy.data.collections["30_Doors_Windows"].objects if "DoorLeaf" in o.name]
    assert len(doors)==1,"Only the core may have an external door leaf"
    floor=bpy.data.objects["SM_ER_ConnectedFloor_v02"].data
    adjacency={i:set() for i in range(len(floor.vertices))}
    for edge in floor.edges:
        a,b=edge.vertices
        adjacency[a].add(b)
        adjacency[b].add(a)
    visited=set()
    todo=[0]
    while todo:
        i=todo.pop()
        if i not in visited:
            visited.add(i)
            todo.extend(adjacency[i]-visited)
    assert len(visited)==len(floor.vertices),"Shared floor must be one connected component"
    physical=structure+[o for name in ["20_Decor","30_Doors_Windows"] for o in bpy.data.collections[name].objects if o.type=="MESH"]
    bvhs=[instance_bvh(o) for o in physical]
    collision_bvhs=[]
    for obj in structure+doors:
        prefix="UCX_"+obj["library_asset"]+"_"
        collision_bvhs.extend(instance_bvh(obj,co) for co in bpy.data.collections["01_UCX_Source"].objects if co.name.startswith(prefix))
    def blocked(origin,end,trees=None):
        origin,end=Vector(origin),Vector(end)
        return any(tree.ray_cast(origin,(end-origin).normalized(),(end-origin).length)[0] is not None for tree in (bvhs if trees is None else trees))
    probes=[]
    for check in manifest["interior_test_contracts"]:
        center,yaw=check["center"],check["yaw"]
        door=check["door_local_front"]
        for x in [-.60,0,.60]:
            for z in [.1,1.1,2.2]:
                if check.get("axis")=="X":
                    sign=check["direction"]
                    start=transform((sign*2.5,x,z),center,yaw)
                    end=transform((sign*5.6,x,z),center,yaw)
                else:
                    start=transform((door[0]+x,door[1]-.6,z),center,yaw)
                    end=transform((door[0]+x,door[1]+.7,z),center,yaw)
                hits=[(obj.name,tuple(hit)) for obj,tree in zip(physical,bvhs)
                      if (hit:=tree.ray_cast(Vector(start),(Vector(end)-Vector(start)).normalized(),(Vector(end)-Vector(start)).length)[0]) is not None]
                assert not blocked(start,end),(check["name"],"door obstructed",x,z,hits)
                assert not blocked(start,end,collision_bvhs),(check["name"],"UCX door obstructed",x,z)
        for x,y in check["floor_samples"]:
            p=transform((x,y,1),center,yaw)
            assert blocked(p,(p[0],p[1],-.5)),(check["name"],"floor missing")
            assert blocked(p,(p[0],p[1],8)),(check["name"],"roof missing")
            assert blocked(p,(p[0],p[1],-.5),collision_bvhs),(check["name"],"UCX floor missing")
            assert blocked(p,(p[0],p[1],8),collision_bvhs),(check["name"],"UCX roof missing")
        if check["name"] in ("WestWing","EastWing"):
            for z in [.1,.6,2.2]:
                p=transform((0,-3.35,z),center,yaw)
                q=transform((0,-2.1,z),center,yaw)
                assert blocked(p,q),(check["name"],"Former external door is still open")
                assert blocked(p,q,collision_bvhs),(check["name"],"Former door UCX is still open")
            link_levels=[]
            for t in range(32):
                for offset in [-.6,0,.6]:
                    p=transform((check["direction"]*(2.5+t*.1),offset,1),center,yaw)
                    for trees in [bvhs,collision_bvhs]:
                        hits=[tree.ray_cast(Vector(p),Vector((0,0,-1)),1.5)[0] for tree in trees]
                        heights=[v.z for v in hits if v is not None]
                        assert heights and abs(max(heights))<1e-5,(check["name"],"Floor transition",p,heights)
                        link_levels.append(max(heights))
            for x in [-3.1,-2.95,-1.8,0,1.8,2.95,3.1]:
                for z in [2.75,2.9,3.05]:
                    p=transform((x,-3.4,z),center,yaw)
                    q=transform((x,-2.2,z),center,yaw)
                    assert blocked(p,q),(check["name"],"upper facade gap",x,z)
                    assert blocked(p,q,collision_bvhs),(check["name"],"upper facade UCX gap",x,z)
        probes.append({"interior":check["name"],"door_grid_9_rays":"clear","floor_and_roof_samples":"hit","scope":"render and source UCX BVH, not capsule/Unreal"})
        if check["name"] in ("WestWing","EastWing"):
            probes[-1]["upper_facade_grid_21_rays"]="render and UCX hit"
            probes[-1]["former_external_door"]="closed at floor/head heights; new65x80cm window above solid sill"
            probes[-1]["internal_route_width_120_height_220"]="nine unobstructed render/UCX rays across both room walls"
            probes[-1]["route_floor_samples_per_representation"]=96
            probes[-1]["max_floor_level_error_m"]=max(abs(v) for v in link_levels)
    enclosure_count=0
    for i in range(720):
        angle=-179.75+i*.5
        if abs(angle)<19:
            continue  # The single intended external entrance remains open.
        a=math.radians(angle)
        for z in [1.0,2.2]:
            p=(0,3,z)
            q=(25*math.sin(a),3-25*math.cos(a),z)
            assert blocked(p,q),("Unintended opening from central room",angle,z)
            enclosure_count+=1
    roundtrips=[]
    bpy.ops.preferences.addon_enable(module="io_scene_fbx")
    for entry in manifest["exports"]:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        path=ROOT/entry["path"]
        assert sha(path)==entry["sha256"]
        bpy.ops.import_scene.fbx(filepath=str(path),use_anim=False,use_image_search=False,use_custom_normals=True)
        meshes=[o for o in bpy.context.scene.objects if o.type=="MESH"]
        assert len(meshes)==1+len(entry["collision_names"])
        obj=bpy.data.objects[entry["asset_name"]]
        actual=stats(obj)
        expected=entry["source_stats"]
        assert actual["triangles"]==expected["triangles"]
        assert actual["material_slots"]==expected["material_slots"]
        bounds_error=max(abs(actual["bounds_blender_m"][i][k]-expected["bounds_blender_m"][i][k]) for i in range(2) for k in range(3))
        assert bounds_error<1e-4,(entry["asset_name"],bounds_error)
        for name in entry["collision_names"]:
            co=bpy.data.objects[name]
            assert stats(co)["nonmanifold_edges"]==0
            for poly in co.data.polygons:
                origin=co.data.vertices[poly.vertices[0]].co
                assert max(poly.normal.dot(v.co-origin) for v in co.data.vertices)<1e-4,(name,"not convex")
        roundtrips.append({"asset":entry["asset_name"],"triangles":actual["triangles"],"bounds_error_m":bounds_error,"collision_hulls":len(entry["collision_names"]),"passed":True})
    result={"status":"passed","revision":2,"external_door_leaves":1,"shared_floor_connected_components":1,
            "central_room_enclosure":{"rays":enclosure_count,"heights_m":[1.0,2.2],"excluded":"intended front entrance +/-19deg","all_hit_render_geometry":True},
            "scope":"Source reopen, all FBX roundtrips; single exterior entrance, internal connections, closed former doors, continuous shared floor; sampled render/UCX tests",
            "source_assets":src,"interior_probes":probes,"roundtrips":roundtrips,"unreal_import":False}
    dump("verification.json",result)
    manifest["status"]="creator_ready"
    manifest["verification"]={"file":"verification.json","sha256":sha(ROOT/"verification.json")}
    dump("manifest.json",manifest)
    print("STUDY_VERIFY_OK",MODULE,len(roundtrips),flush=True)


def render():
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    views=json.loads(bpy.context.scene["views_json"])
    out=ROOT/"Previews"
    out.mkdir(exist_ok=True)
    for name,(pos,target,lens) in views.items():
        if args.view and name!=args.view:
            continue
        scene=bpy.context.scene
        cam=scene.camera
        cam.location=pos
        cam.rotation_euler=(Vector(target)-cam.location).to_track_quat("-Z","Y").to_euler()
        cam.data.lens=lens
        if name=="05_connected_plan":
            cam.data.type="ORTHO"
            cam.data.ortho_scale=21.5
            for obj in bpy.data.collections["10_Structure"].objects:
                if any(part in obj.name for part in ["Vault","Crown","Roof"]):
                    obj.hide_render=True
            bpy.data.collections["20_Decor"].hide_render=True
            bpy.data.collections["50_Nature"].hide_render=True
            section=mesh_object("ReviewOnly_SectionVolume",Geo().box((-20,-15,-1),(20,20,1.8)),None,scene.collection)
            section.hide_render=True
            for collection_name in ["10_Structure","30_Doors_Windows"]:
                for obj in bpy.data.collections[collection_name].objects:
                    if obj.type=="MESH" and not obj.hide_render:
                        modifier=obj.modifiers.new("ReviewOnly_CutAt180cm","BOOLEAN")
                        modifier.operation="INTERSECT"
                        modifier.solver="EXACT"
                        modifier.object=section
        if name=="04_interior":
            data=bpy.data.lights.new("ReviewOnly_InteriorBounce","AREA")
            data.energy=450
            data.size=2.5
            light=bpy.data.objects.new("ReviewOnly_InteriorBounce",data)
            scene.collection.objects.link(light)
            light.location=Vector(pos)+Vector((0,0,.9))
            light.rotation_euler=(Vector(target)-light.location).to_track_quat("-Z","Y").to_euler()
        scene.render.filepath=str(out/(name+".png"))
        bpy.ops.render.render(write_still=True)
        if name=="04_interior":
            bpy.data.objects.remove(light,do_unlink=True)
        print("STUDY_RENDER_OK",name,flush=True)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--mode",choices=["build","revise","verify","render"],required=True)
    parser.add_argument("--view",default=None)
    args=parser.parse_args(sys.argv[sys.argv.index("--")+1:])
    {"build":build,"revise":lambda: build(True),"verify":verify,"render":render}[args.mode]()
