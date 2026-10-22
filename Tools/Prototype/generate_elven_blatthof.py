"""Reproducible style-study geometry, centimetres, Unreal Z up.

Run from the project root. Writes OBJ/MTL under Saved/ElvenBlatthofSources.
Import through Unreal MCP; no engine, plugin or gameplay changes required.
This is a visual prototype, not a definition of elven social ranks or lore.
"""
import json
import math
from pathlib import Path

OUT = Path('Saved/ElvenBlatthofSources')
MATERIALS = ['Ivory', 'Jade', 'JadeLight', 'Timber', 'Bronze', 'Glass', 'Stone', 'Garden', 'Water']


def polar(radius, angle, z):
    a = math.radians(angle)
    return (radius * math.cos(a), radius * math.sin(a), z)


class Mesh:
    def __init__(self):
        self.faces = []

    def face(self, points, material):
        self.faces.append((list(points), material))

    def box(self, center, size, mat):
        x,y,z = center
        a,b,c = (s/2 for s in size)
        v = [(x-a,y-b,z-c),(x+a,y-b,z-c),(x+a,y+b,z-c),(x-a,y+b,z-c),
             (x-a,y-b,z+c),(x+a,y-b,z+c),(x+a,y+b,z+c),(x-a,y+b,z+c)]
        for f in [(3,2,1,0),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]:
            self.face([v[i] for i in f],mat)

    def arc(self, r0, r1, a0, a1, z0, z1, mat, segments=None):
        segments = segments or max(1, round(abs(a1-a0)/3))
        for i in range(segments):
            a = a0+(a1-a0)*i/segments
            b = a0+(a1-a0)*(i+1)/segments
            self.face([polar(r0,a,z0),polar(r0,b,z0),polar(r1,b,z0),polar(r1,a,z0)],mat)
            self.face([polar(r1,a,z1),polar(r1,b,z1),polar(r0,b,z1),polar(r0,a,z1)],mat)
            self.face([polar(r1,a,z0),polar(r1,b,z0),polar(r1,b,z1),polar(r1,a,z1)],mat)
            self.face([polar(r0,b,z0),polar(r0,a,z0),polar(r0,a,z1),polar(r0,b,z1)],mat)
        for a,reverse in [(a0,True),(a1,False)]:
            p=[polar(r0,a,z0),polar(r1,a,z0),polar(r1,a,z1),polar(r0,a,z1)]
            self.face(list(reversed(p)) if reverse else p,mat)

    def tube(self, points, radius, mat, sides=7):
        rings=[]
        for i,p in enumerate(points):
            prev, nxt=points[max(0,i-1)],points[min(len(points)-1,i+1)]
            t=[nxt[j]-prev[j] for j in range(3)]
            length=math.sqrt(sum(v*v for v in t)); t=[v/length for v in t]
            helper=(0,0,1) if abs(t[2])<.9 else (0,1,0)
            u=(t[1]*helper[2]-t[2]*helper[1],t[2]*helper[0]-t[0]*helper[2],t[0]*helper[1]-t[1]*helper[0])
            length=math.sqrt(sum(v*v for v in u));u=[v/length for v in u]
            v=(t[1]*u[2]-t[2]*u[1],t[2]*u[0]-t[0]*u[2],t[0]*u[1]-t[1]*u[0])
            rings.append([tuple(p[k]+radius*(u[k]*math.cos(j*2*math.pi/sides)+v[k]*math.sin(j*2*math.pi/sides)) for k in range(3)) for j in range(sides)])
        self.face(list(reversed(rings[0])),mat);self.face(rings[-1],mat)
        for i in range(len(rings)-1):
            for j in range(sides):
                self.face([rings[i][j],rings[i][(j+1)%sides],rings[i+1][(j+1)%sides],rings[i+1][j]],mat)

    def save(self,name,smooth=False):
        lines=['# Elven Blatthof style prototype, cm, Z-up','mtllib Blatthof.mtl','s off']
        normals={}
        if smooth:
            for points,mat in self.faces:
                a,b,c=points[:3]
                u=[b[k]-a[k] for k in range(3)];v=[c[k]-a[k] for k in range(3)]
                n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
                for p in points:
                    key=(tuple(round(x,3) for x in p),mat)
                    old=normals.get(key,(0,0,0));normals[key]=tuple(old[k]+n[k] for k in range(3))
        n=0;triangles=0
        for points,mat in self.faces:
            # OBJ importer reflects Y; explicit reflection + winding preserves Unreal coordinates.
            lines+=['v %.5f %.5f %.5f'%(x,-y,z) for x,y,z in points]
            lines+=['vt %.5f %.5f'%(x/200,z/200+y/200) for x,y,z in points]
            if smooth:
                for p in points:
                    nx,ny,nz=normals[(tuple(round(x,3) for x in p),mat)]
                    length=math.sqrt(nx*nx+ny*ny+nz*nz) or 1
                    lines.append('vn %.6f %.6f %.6f'%(nx/length,-ny/length,nz/length))
            lines.append('usemtl '+mat)
            for i in range(1,len(points)-1):
                ids=[n+i+2,n+i+1,n+1]
                lines.append('f '+' '.join(('%d/%d/%d'%(j,j,j) if smooth else '%d/%d'%(j,j)) for j in ids));triangles+=1
            n+=len(points)
        (OUT/(name+'.obj')).write_text('\n'.join(lines),encoding='utf8')
        return {'name':name,'triangles':triangles,'bounds':[[min(p[k] for ps,_ in self.faces for p in ps) for k in range(3)], [max(p[k] for ps,_ in self.faces for p in ps) for k in range(3)]]}


def roof_point(a,t,offset=0):
    # Broad leaf cross section: edge curl and tall central vein; raised tips.
    radius=215+480*t
    tip=85*abs((a-90)/125)**3
    z=300+155*math.sin(math.pi*t)**.85+tip+offset
    return polar(radius,a,z)


def build():
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'Blatthof.mtl').write_text('\n'.join('newmtl '+m+'\nKd 0.5 0.5 0.5\n' for m in MATERIALS))
    shell,roof,detail,court=Mesh(),Mesh(),Mesh(),Mesh()
    # Ground-supported crescent, ~71m2 interior, courtyard facing -Y.
    shell.arc(240,650,-35,215,-12,0,'Stone')
    # Inner wall has a genuine 144cm-wide doorway at rear centre, 232cm high.
    opening=math.degrees(math.asin(72/260))
    shell.arc(245,265,-35,90-opening,0,280,'Ivory')
    shell.arc(245,265,90+opening,215,0,280,'Ivory')
    shell.arc(245,265,90-opening,90+opening,232,280,'Ivory')
    # Outer wall with four large glazed apertures, no opaque wall behind windows.
    window_intervals=[(-9,9),(36,54),(126,144),(171,189)]
    cuts=sorted(set([-35,215]+[v for pair in window_intervals for v in pair]))
    for a,b in zip(cuts,cuts[1:]):
        window=any(abs(a-x)<.01 and abs(b-y)<.01 for x,y in window_intervals)
        if window:
            shell.arc(630,650,a,b,0,75,'Ivory')
            shell.arc(630,650,a,b,240,280,'Ivory')
            # Opaque dark-teal glass prototype deliberately closes the collision opening.
            shell.arc(637,643,a,b,75,240,'Glass')
        else: shell.arc(630,650,a,b,0,280,'Ivory')
    # End walls close both tips, but keep a full connected interior corridor.
    for a in [-35,215]: shell.arc(265,630,a-.9,a+.9,0,280,'Ivory',1)
    # Close the gap between the level wall crown and curved roof underside.
    for r in [245,265,630,650]:
        for i in range(84):
            a=-35+250*i/84;b=-35+250*(i+1)/84
            za=roof_point(a,(r-215)/480,-12)[2]
            zb=roof_point(b,(r-215)/480,-12)[2]
            points=[polar(r,a,280),polar(r,b,280),polar(r,b,zb),polar(r,a,za)]
            shell.face(points,'Ivory');shell.face(list(reversed(points)),'Ivory')
    # Base and crown bands; below ceiling clearance, roof is sealed to wall crown.
    for r0,r1 in [(241,269),(626,654)]:
        detail.arc(r0,r1,-35,215,4,19,'Stone')
        detail.arc(r0,r1,-35,215,266,282,'Timber')
    # Three overlapping broad roof leaves, visible central and branching veins.
    for a0,a1 in [(-41,45),(39,141),(135,221)]:
        nu,nv=32,16
        for i in range(nu):
            a=a0+(a1-a0)*i/nu;b=a0+(a1-a0)*(i+1)/nu
            for j in range(nv):
                t=j/nv;u=(j+1)/nv
                mat='JadeLight' if j>nv/2 else 'Jade'
                roof.face([roof_point(a,u),roof_point(b,u),roof_point(b,t),roof_point(a,t)],mat)
                roof.face([roof_point(a,t,-12),roof_point(b,t,-12),roof_point(b,u,-12),roof_point(a,u,-12)],'Timber')
        for t in [0,1]:
            pts=[roof_point(a0+(a1-a0)*i/nu,t) for i in range(nu+1)]
            detail.tube(pts,5,'Bronze')
            for p,q in zip(pts,pts[1:]): roof.face([p,q,(q[0],q[1],q[2]-12),(p[0],p[1],p[2]-12)],'Jade')
        detail.tube([roof_point(a0+(a1-a0)*i/40,.5,4) for i in range(41)],8,'Bronze')
        for a in range(round(a0)+10,round(a1)-5,13):
            for sign in [-1,1]:
                pts=[roof_point(a+sign*6*k/12,.5+sign*.48*k/12,3) for k in range(13)]
                detail.tube(pts,2.5,'JadeLight')
        for a in [a0,a1]:
            detail.tube([roof_point(a,k/24,1) for k in range(25)],6,'Timber')
    # Sculptural branching buttresses (not rectangular timber framing).
    for a in [-34,22,68,112,158,214]:
        for r,sign in [(247,-1),(644,1)]:
            pts=[polar(r+sign*18*math.sin(math.pi*k/18),a,8+285*k/18) for k in range(19)]
            detail.tube(pts,10,'Timber')
            for turn in [-1,1]:
                detail.tube([polar(r+sign*5,a+turn*9*k/12,180+105*k/12) for k in range(13)],6,'Timber')
    # Decorative leaf tracery over each window, with structural upright mullion.
    for a,b in window_intervals:
        mid=(a+b)/2
        for sign in [-1,1]:
            detail.tube([polar(653,mid+sign*(b-a)/2*math.sin(math.pi*k/24),75+165*k/24) for k in range(25)],5,'Bronze')
        detail.tube([polar(654,mid,75),polar(654,mid,240)],3,'Timber')
        for z in [95,220]:detail.tube([polar(653,a+(b-a)*k/12,z) for k in range(13)],3,'Timber')
    # Raised portal leaf arch, existing door fits its 144x232 opening separately.
    detail.tube([(-77,246,0),(-77,246,210),(-60,246,246),(0,246,270),(60,246,246),(77,246,210),(77,246,0)],8,'Timber')
    # Accessible courtyard path and bridge are flush with level floor; no raised trip hazards.
    court.box((0,-240,-4),(150,970,8),'Stone')
    # Water is a decorative flat strip; collision remains on existing lab ground below.
    court.box((0,-385,1),(810,95,2),'Water')
    court.box((0,-385,4),(170,140,8),'Stone')
    for x in [-88,88]:
        detail.tube([(x,-462,8),(x,-440,60),(x,-385,76),(x,-330,60),(x,-308,8)],4,'Bronze')
    # Two low leaf-shaped planted beds in courtyard, leaving >=150cm central path.
    for cx in [-155,155]:
        ring=[]
        for i in range(40):
            a=i*2*math.pi/40
            ring.append((cx+62*math.cos(a),-70+150*math.sin(a),10))
        court.face(list(reversed(ring)),'Garden')
        court.face(ring,'Garden')
        detail.tube(ring+[ring[0]],7,'Stone')
        for y in [-135,-65,10]:
            # Stylized broad foliage blades, no costly alpha or Niagara.
            for sign in [-1,1]:
                court.face([(cx,y,10),(cx+sign*38,y+24,38),(cx+sign*24,y+62,58),(cx,y+38,18)],'Garden')
    results=[m.save('SM_ElvenBlatthof_'+n,smooth=n in ['LeafRoof','Ribs']) for m,n in [(shell,'Shell'),(roof,'LeafRoof'),(detail,'Ribs'),(court,'Courtyard')]]
    (OUT/'manifest.json').write_text(json.dumps(results,indent=2))
    print(json.dumps(results,indent=2))


if __name__=='__main__': build()
