"""Entrance and roof-matched end caps for the existing two-field Blatthof kit.

Run with python -B from the project root. Only writes Saved/ElvenClosedSources.
Existing study/join exporters and imported assets are not rewritten. The house
assembly remains an authored Blueprint, not a procedural building generator.
"""
import json
import math
from pathlib import Path

import generate_elven_join_sample as join
from generate_elven_blatthof import polar

OUT=Path('Saved/ElvenClosedSources')
NAMES={'Entry':'SM_EB_WallInner_Entry_A60_H280_Sealed',
       'EndStart':'SM_EB_EndCap_R245_650_A3_Start_Full',
       'EndEnd':'SM_EB_EndCap_R245_650_A3_End_Full'}


def portal(u,v,z):
    a=math.radians(30)
    return (v*math.cos(a)-u*math.sin(a),v*math.sin(a)+u*math.cos(a),z)


def prism(mesh, polygon, bottom, top):
    area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(polygon,polygon[1:]+polygon[:1]))
    if area < 0:polygon=list(reversed(polygon))
    mesh.face([(x,y,bottom) for x,y in reversed(polygon)],'Ivory')
    mesh.face([(x,y,top) for x,y in polygon],'Ivory')
    for a,b in zip(polygon,polygon[1:]+polygon[:1]):
        mesh.face([(a[0],a[1],bottom),(b[0],b[1],bottom),
                   (b[0],b[1],top),(a[0],a[1],top)],'Ivory')


def box(center,size,yaw,name):
    return {'center':dict(zip('xyz',center)),'rotation':dict(pitch=0,yaw=yaw,roll=0),
            'x':size[0],'y':size[1],'z':size[2],'name':name,
            'restOffset':0,'bIsGenerated':False,'bContributeToMass':True,
            'collisionEnabled':'QueryAndPhysics'}


def portal_box(u0,u1,v0,v1,z0,z1,name):
    return box(join.local(portal((u0+u1)/2,(v0+v1)/2,(z0+z1)/2)),
               (u1-u0,v1-v0,z1-z0),30,name)


def arc_boxes(a0,a1,r0=245,r1=265):
    count=max(1,round((a1-a0)/5))
    step=(a1-a0)/count
    half=math.radians(step/2)
    radius=(r1+r0*math.cos(half))/2
    return [box(join.local(polar(radius,a0+step*(i+.5),140)),
                (2*r1*math.sin(half)+.2,r1-r0*math.cos(half),280),
                a0+step*(i+.5),'EntryArc_%g_%d'%(a0,i)) for i in range(count)]


def entrance():
    mesh=join.ModuleMesh()
    mesh.arc(245,265,0,10,0,280,'Ivory',4)
    mesh.arc(245,265,50,60,0,280,'Ivory',4)
    # Correct the inherited arc helper's exposed end-cap winding locally; the
    # original exporter/assets remain untouched.
    for i,(points,material) in enumerate(mesh.faces):
        angles=[math.degrees(math.atan2(p[1],p[0])) for p in points]
        if max(angles)-min(angles)<1e-6 and (abs(angles[0])<1e-6 or abs(angles[0]-60)<1e-6):
            points=list(reversed(points))
            mesh.faces[i]=(points,material)
            mesh.normals[i]=[join.face_normal(points)]*len(points)
    collisions=arc_boxes(0,10)+arc_boxes(50,60)
    for sign in [-1,1]:
        angle=30+sign*20
        polygon=[polar(245,angle,0)[:2],polar(265,angle,0)[:2],
                 portal(sign*72,265,0)[:2],portal(sign*72,245,0)[:2]]
        prism(mesh,polygon,0,280)
        u0,u1=sorted([sign*72,sign*265*math.sin(math.radians(20))])
        collisions.append(portal_box(u0,u1,245*math.cos(math.radians(20)),265,
                                     0,280,'PortalShoulder_%d'%sign))
    polygon=[portal(u,v,0)[:2] for u,v in [(-72,245),(72,245),(72,265),(-72,265)]]
    prism(mesh,polygon,232,280)
    collisions.append(portal_box(-72,72,245,265,232,280,'PortalLintel'))
    # The frame spans u=-72..72, v=241..265; the leaf remains 120x12x220.
    door=join.local(portal(-60,259,0))
    assert all(b['center']['z']-b['z']/2 >= 232-1e-6 or
               abs((b['center']['x']-door[0])*math.cos(math.radians(30))+
                   (b['center']['y']-door[1])*math.sin(math.radians(30))-60)>60
               for b in collisions[-3:]),'Doorway must stay clear'
    return mesh,collisions,{'location':list(door),'yaw':30,'child_component_scale':[1,1,1]}


def underside(radius):
    j=min(31,max(0,int((radius-215)/15)))
    r=215+15*j
    return join.roof_z(r)+(join.roof_z(r+15)-join.roof_z(r))*(radius-r)/15-12


def cap(a0,a1):
    mesh=join.ModuleMesh()
    radii=sorted({245,650}|{215+15*j for j in range(33) if 245<215+15*j<650})
    # Each cap occupies one existing 3-degree roof panel, including its exact profile.
    for i,(r,s) in enumerate(zip(radii,radii[1:])):
        zr,zs=underside(r),underside(s)
        mesh.face([polar(r,a0,0),polar(r,a1,0),polar(s,a1,0),polar(s,a0,0)],'Ivory')
        mesh.face([polar(s,a0,zs),polar(s,a1,zs),polar(r,a1,zr),polar(r,a0,zr)],'Ivory')
        for a,reverse in [(a0,False),(a1,True)]:
            p=[polar(r,a,0),polar(s,a,0),polar(s,a,zs),polar(r,a,zr)]
            mesh.face(list(reversed(p)) if reverse else p,'Ivory')
    for r,reverse in [(245,True),(650,False)]:
        z=underside(r)
        p=[polar(r,a0,0),polar(r,a1,0),polar(r,a1,z),polar(r,a0,z)]
        mesh.face(list(reversed(p)) if reverse else p,'Ivory')
    # Lower collision remains solid; the narrow upper profile is approximated by
    # radial bands. No invisible collision across the entrance opening is created.
    collisions=[]
    mid=(a0+a1)/2
    half=math.radians((a1-a0)/2)
    for i in range(10):
        r,s=245+405*i/10,245+405*(i+1)/10
        center=(s+r*math.cos(half))/2
        height=max(underside(r),underside(s),underside((r+s)/2))
        collisions.append(box(join.local(polar(center,mid,height/2)),
                              (2*s*math.sin(half)+.1,s-r*math.cos(half),height),mid,'EndBand_%02d'%i))
    return mesh,collisions


def check_entry_boundary(mesh):
    for angle in [0,60]:
        found={tuple(round(v,6) for v in p) for points,_ in mesh.faces for p in points
               if abs(math.degrees(math.atan2(p[1],p[0]))-angle)<1e-6}
        assert all(tuple(round(v,6) for v in polar(r,angle,z)) in found
                   for r in [245,265] for z in [0,280]),'Entry boundary mismatch'


def check_end_normals(mesh,a0,a1):
    for points,_ in mesh.faces:
        angles=[math.degrees(math.atan2(p[1],p[0])) for p in points]
        if max(angles)-min(angles)>1e-6:continue
        for angle,sign in [(a0,-1),(a1,1)]:
            if abs(angles[0]-angle)>1e-6:continue
            normal=join.face_normal(points)
            a=math.radians(angle)
            assert sign*(-math.sin(a)*normal[0]+math.cos(a)*normal[1])>.99,'Inward-facing end wall'


def build():
    OUT.mkdir(parents=True,exist_ok=True)
    join.OUT=OUT
    (OUT/'BlatthofJoin.mtl').write_text('newmtl Ivory\nKd 0.5 0.5 0.5\n',encoding='utf8')
    entry,collision,door=entrance()
    check_entry_boundary(entry)
    result={'kit_id':'EB.Blatthof.R255_R640','interface_version':1,
            'units':'cm','entry_opening_cm':[144,232],'door_leaf_cm':[120,12,220],
            'door_transform':door,'modules':{}}
    for key,mesh,boxes in [('Entry',entry,collision),('EndStart',*cap(-.01,3)),('EndEnd',*cap(-3,.01))]:
        check_end_normals(mesh,*(dict(Entry=(0,60),EndStart=(-.01,3),EndEnd=(-3,.01))[key]))
        result['modules'][key]=mesh.save_module(NAMES[key])
        result['modules'][key]['collision_boxes']=boxes
    result['end_transform']={'location':[255*math.sin(math.radians(60)),255*(1-math.cos(math.radians(60))),0],'yaw':60}
    (OUT/'manifest.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':build()
