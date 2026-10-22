"""Four reusable 30-degree Blatthof modules, centimetres, Unreal Z up.

Run from the project root. Writes only Saved/ElvenJoinSources.
The original style-study generator/assets are deliberately not rewritten.
Import and place through Unreal MCP. This is an asset-source exporter, not
a procedural building system. Join data is authoring metadata, not runtime PCG.
"""
import json
import math
from pathlib import Path

from generate_elven_blatthof import Mesh, polar


OUT = Path('Saved/ElvenJoinSources')
ANGLE = 30.0
REFERENCE_RADIUS = 255.0
SEGMENTS = 10
NAMES = {
    'Floor': 'SM_EB_Floor_R240_650_A30',
    'InnerWall': 'SM_EB_WallInner_R255_A30_H280',
    'OuterWall': 'SM_EB_WallOuter_R640_A30_H280',
    'Roof': 'SM_EB_LeafRoof_R215_695_A30',
}


def local(point):
    """Original radial frame -> tangent/inward frame at R255, angle zero."""
    x, y, z = point
    return (y, REFERENCE_RADIUS - x, z)


def unit(v):
    length = math.sqrt(sum(x*x for x in v))
    if length < 1e-12:
        raise ValueError('Degenerate face')
    return tuple(x/length for x in v)


def face_normal(points):
    a, b, c = points[:3]
    u = tuple(b[i]-a[i] for i in range(3))
    v = tuple(c[i]-a[i] for i in range(3))
    return unit((u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]))


def roof_z(radius):
    t = (radius-215.0)/480.0
    return 300.0 + 155.0*max(0.0, math.sin(math.pi*t))**0.85


def roof_normal(radius, angle, bottom=False):
    t = (radius-215.0)/480.0
    # The source profile has a vertical limiting tangent at both curled edges.
    if t <= 1e-10 or t >= 1-1e-10:
        slope = 1e12 if t < 0.5 else -1e12
    else:
        slope = 155*0.85*math.sin(math.pi*t)**(-0.15)*math.cos(math.pi*t)*math.pi/480
    a = math.radians(angle)
    normal = unit((-slope*math.cos(a), -slope*math.sin(a), 1))
    return tuple(-x for x in normal) if bottom else normal


class ModuleMesh(Mesh):
    """Reuse the study's arc geometry; add explicit normals at join boundaries."""
    def __init__(self):
        super().__init__()
        self.normals = []

    def face(self, points, material, normals=None):
        points = list(points)
        normal = face_normal(points)
        if normals is None:
            radii = [math.hypot(p[0], p[1]) for p in points]
            # Smooth cylindrical walls, but keep planar caps and slab tops hard.
            if max(radii)-min(radii) < 1e-6 and abs(normal[2]) < 1e-6:
                sign = 1 if normal[0]*points[0][0]+normal[1]*points[0][1] > 0 else -1
                normals = [(sign*p[0]/radii[i], sign*p[1]/radii[i], 0) for i,p in enumerate(points)]
            else:
                normals = [normal]*len(points)
        self.faces.append((points, material))
        self.normals.append(normals)

    def save_module(self, name):
        lines = ['# cm, Z up; local X tangent, Y inward; R255 start pivot',
                 'mtllib BlatthofJoin.mtl', 's off']
        offset = 0
        triangle_count = 0
        for (points, material), normals in zip(self.faces, self.normals):
            transformed = [local(p) for p in points]
            lines += ['v %.9f %.9f %.9f' % (x,-y,z) for x,y,z in transformed]
            lines += ['vt %.9f %.9f' % (x/200,(z+y)/200) for x,y,z in transformed]
            # Match the original OBJ import convention: reflect Y and reverse winding.
            lines += ['vn %.12f %.12f %.12f' % (ny,nx,nz) for nx,ny,nz in normals]
            lines.append('usemtl '+material)
            for i in range(1, len(points)-1):
                ids = [offset+i+2, offset+i+1, offset+1]
                lines.append('f '+' '.join('%d/%d/%d' % (j,j,j) for j in ids))
                triangle_count += 1
            offset += len(points)
        (OUT/(name+'.obj')).write_text('\n'.join(lines)+'\n', encoding='utf8')
        points = [local(p) for ps,_ in self.faces for p in ps]
        return {'name':name, 'triangles':triangle_count,
                'bounds':[[min(p[k] for p in points) for k in range(3)],
                          [max(p[k] for p in points) for k in range(3)]],
                'materials':sorted({mat for _,mat in self.faces})}


def roof_shell(mesh):
    cross_segments = 32
    for i in range(SEGMENTS):
        a, b = ANGLE*i/SEGMENTS, ANGLE*(i+1)/SEGMENTS
        for j in range(cross_segments):
            r, s = 215+480*j/cross_segments, 215+480*(j+1)/cross_segments
            coords = [(s,a),(s,b),(r,b),(r,a)]
            mesh.face([polar(rad, ang, roof_z(rad)) for rad,ang in coords],
                      'JadeLight' if j >= cross_segments//2 else 'Jade',
                      [roof_normal(rad,ang) for rad,ang in coords])
            coords.reverse()
            mesh.face([polar(rad,ang,roof_z(rad)-12) for rad,ang in coords], 'Timber',
                      [roof_normal(rad,ang,True) for rad,ang in coords])
        for rad, reverse in [(215,True),(695,False)]:
            p=[polar(rad,a,roof_z(rad)-12),polar(rad,b,roof_z(rad)-12),
               polar(rad,b,roof_z(rad)),polar(rad,a,roof_z(rad))]
            mesh.face(list(reversed(p)) if reverse else p,'Jade')
    for a, reverse in [(0,False),(ANGLE,True)]:
        for j in range(cross_segments):
            r,s=215+480*j/cross_segments,215+480*(j+1)/cross_segments
            p=[polar(r,a,roof_z(r)-12),polar(s,a,roof_z(s)-12),
               polar(s,a,roof_z(s)),polar(r,a,roof_z(r))]
            mesh.face(list(reversed(p)) if reverse else p,'Timber')


def wall_roof_fill(mesh, r, s):
    """Close the two wall crowns to the exact sampled roof underside.

    Use the roof's piecewise-linear radial profile, including wall boundaries,
    so fill surfaces cannot poke through or leave a gap beneath the roof.
    """
    def underside(rad):
        t=(rad-215)/15
        j=min(31,max(0,int(t)))
        p=215+15*j
        return roof_z(p)+(roof_z(p+15)-roof_z(p))*(rad-p)/15-12

    radii=sorted({r,s} | {215+15*j for j in range(33) if r < 215+15*j < s})
    for r0,r1 in zip(radii,radii[1:]):
        z0,z1=underside(r0),underside(r1)
        for i in range(SEGMENTS):
            a,b=ANGLE*i/SEGMENTS,ANGLE*(i+1)/SEGMENTS
            mesh.face([polar(r0,a,280),polar(r0,b,280),polar(r1,b,280),polar(r1,a,280)],'Ivory')
            mesh.face([polar(r1,a,z1),polar(r1,b,z1),polar(r0,b,z0),polar(r0,a,z0)],'Ivory')
            mesh.face([polar(r1,a,280),polar(r1,b,280),polar(r1,b,z1),polar(r1,a,z1)],'Ivory')
            mesh.face([polar(r0,b,280),polar(r0,a,280),polar(r0,a,z0),polar(r0,b,z0)],'Ivory')
        for a,reverse in [(0,True),(ANGLE,False)]:
            p=[polar(r0,a,280),polar(r1,a,280),polar(r1,a,z1),polar(r0,a,z0)]
            mesh.face(list(reversed(p)) if reverse else p,'Ivory')


def verify_boundaries(mesh):
    """A second identical module must match both positions and visible normals."""
    a, b = {}, {}
    normals_a, normals_b = {}, {}
    angle=math.radians(ANGLE)
    ca,sa=math.cos(angle),math.sin(angle)
    dx,dy=255*sa,255*(1-ca)
    for (points,_), normals in zip(mesh.faces,mesh.normals):
        for p,n in zip(points,normals):
            theta=math.degrees(math.atan2(p[1],p[0]))
            if abs(theta) < 1e-7:
                x,y,z=local(p)
                key=tuple(round(v,6) for v in (dx+ca*x-sa*y,dy+sa*x+ca*y,z))
                a[key]=True
                if abs(n[1]) < 1e-6:  # Exclude the intentionally hard end cap.
                    nx,ny,nz=n[1],-n[0],n[2]
                    normal=tuple(round(v,6) for v in (ca*nx-sa*ny,sa*nx+ca*ny,nz))
                    normals_a.setdefault(key,set()).add(normal)
            if abs(theta-ANGLE) < 1e-7:
                key=tuple(round(v,6) for v in local(p))
                b[key]=True
                if abs(-sa*n[0]+ca*n[1]) < 1e-6:
                    normal=tuple(round(v,6) for v in (n[1],-n[0],n[2]))
                    normals_b.setdefault(key,set()).add(normal)
    assert a.keys()==b.keys(), (set(a)-set(b),set(b)-set(a))
    assert normals_a==normals_b, 'Visible normals must match across the joint'
    return len(a)


def wall_collision_boxes(r0, r1):
    """Five tangent boxes; avoid voxel shrinkage on the 20 cm thin walls."""
    half_angle=math.radians(3)
    center_radius=(r1+r0*math.cos(half_angle))/2
    boxes=[]
    for i in range(5):
        angle=3+6*i
        x,y,z=local(polar(center_radius,angle,140))
        boxes.append({'center':dict(x=x,y=y,z=z),
                      'rotation':dict(pitch=0,yaw=angle,roll=0),
                      'x':2*r1*math.sin(half_angle)+0.2,
                      'y':r1-r0*math.cos(half_angle),'z':280,
                      'restOffset':0,'bIsGenerated':False,'name':'WallArc_%02d'%i,
                      'bContributeToMass':True,'collisionEnabled':'QueryAndPhysics'})
    return boxes


def floor_collision_boxes():
    """Flat slab collision, ten tangent boxes; small end-corner overcoverage."""
    half_angle=math.radians(1.5)
    center_radius=(650+240*math.cos(half_angle))/2
    boxes=[]
    for i in range(10):
        angle=1.5+3*i
        x,y,z=local(polar(center_radius,angle,-6))
        boxes.append({'center':dict(x=x,y=y,z=z),
                      'rotation':dict(pitch=0,yaw=angle,roll=0),
                      'x':2*650*math.sin(half_angle)+0.1,
                      'y':650-240*math.cos(half_angle),'z':12,
                      'restOffset':0,'bIsGenerated':False,'name':'FloorArc_%02d'%i,
                      'bContributeToMass':True,'collisionEnabled':'QueryAndPhysics'})
    return boxes


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    meshes={key:ModuleMesh() for key in NAMES}
    meshes['Floor'].arc(240,650,0,ANGLE,-12,0,'Stone',SEGMENTS)
    meshes['InnerWall'].arc(245,265,0,ANGLE,0,280,'Ivory',SEGMENTS)
    meshes['OuterWall'].arc(630,650,0,ANGLE,0,280,'Ivory',SEGMENTS)
    roof_shell(meshes['Roof'])
    wall_roof_fill(meshes['Roof'],245,265)
    wall_roof_fill(meshes['Roof'],630,650)
    materials=sorted({mat for mesh in meshes.values() for _,mat in mesh.faces})
    (OUT/'BlatthofJoin.mtl').write_text(''.join('newmtl '+m+'\nKd 0.5 0.5 0.5\n' for m in materials),encoding='utf8')
    angle=math.radians(ANGLE)
    manifest={'kit_id':'EB.Blatthof.R255_R640','interface_version':1,
              'angle_degrees':ANGLE,'units':'cm','scale':[1,1,1],
              'pivot':'Start on R255 at floor Z0; X tangent, Y inward, Z up',
              'joins':{'Join_A':{'location':[0,0,0],'yaw':180},
                       'Join_B':{'location':[255*math.sin(angle),255*(1-math.cos(angle)),0],'yaw':ANGLE}},
              'modules':{},'boundary_points_verified':{}}
    for key,mesh in meshes.items():
        manifest['boundary_points_verified'][key]=verify_boundaries(mesh)
        manifest['modules'][key]=mesh.save_module(NAMES[key])
    manifest['modules']['InnerWall']['collision_boxes']=wall_collision_boxes(245,265)
    manifest['modules']['OuterWall']['collision_boxes']=wall_collision_boxes(630,650)
    manifest['modules']['Floor']['collision_boxes']=floor_collision_boxes()
    manifest['collision_policy']='UseSimpleAsComplex; floor: ten flat boxes; walls: five tangent boxes each; roof: convex hulls'
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
    print(json.dumps(manifest,indent=2))


if __name__=='__main__':
    build()
