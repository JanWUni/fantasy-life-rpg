"""Deterministic placeholder meshes for the neutral environment prototype.

Run from the project root. Outputs ignored import sources under Saved/EnvironmentSources.
No third-party assets or Python packages. Units: centimetres; OBJ coordinates: Z up.
"""
import json
import math
import pathlib
import random

OUT = pathlib.Path('Saved/EnvironmentSources')
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'Environment.mtl').write_text('\n'.join(
    'newmtl ' + name + '\nKd 0.5 0.5 0.5\n' for name in
    ['Grass','Path','Bark','Pine','PineLight','Stone','Wood','Roof','RoofLight','Glass']), encoding='utf-8')


def height(x, y):
    raw = (110 * math.sin(x / 1300) * math.cos(y / 1700)
           + 100 * math.sin((x + y) / 1900) + 90)
    d = math.hypot(x - 900, y - 1350)
    t = max(0, min(1, (d - 950) / 700))
    t = t * t * (3 - 2 * t)
    return 80 * (1 - t) + raw * t


def path_x(y):
    t = max(0, min(1, (y + 3300) / 4500))
    return -1700 + 2600 * t + 300 * math.sin(t * math.pi * 2)


class Mesh:
    def __init__(self):
        self.vertices = []
        self.faces = []

    def face(self, points, material='Grass'):
        indices = []
        for p in points:
            self.vertices.append(p)
            indices.append(len(self.vertices))
        for i in range(1, len(indices) - 1):
            self.faces.append((material, (indices[0], indices[i], indices[i + 1])))

    def box(self, center, size, material):
        x, y, z = center
        a, b, c = [v / 2 for v in size]
        v = [(x-a,y-b,z-c),(x+a,y-b,z-c),(x+a,y+b,z-c),(x-a,y+b,z-c),
             (x-a,y-b,z+c),(x+a,y-b,z+c),(x+a,y+b,z+c),(x-a,y+b,z+c)]
        for f in [(3,2,1,0),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]:
            self.face([v[i] for i in f], material)

    def cone(self, radius, bottom, top, material, segments=9, phase=0):
        ring = [(math.cos(i*2*math.pi/segments+phase)*radius,
                 math.sin(i*2*math.pi/segments+phase)*radius,bottom) for i in range(segments)]
        self.face(list(reversed(ring)), material)
        for i in range(segments):
            self.face([ring[i], ring[(i+1)%segments], (0,0,top)], material)

    def save(self, name):
        lines = ['# FantasyLifeRPG neutral prototype source, cm, Z-up', 'mtllib Environment.mtl', 's off']
        # OBJ/FBX import changes handedness by negating Y. Export that conversion
        # explicitly so the authored Unreal coordinates and winding survive import.
        lines += ['v %.4f %.4f %.4f' % (x,-y,z) for x,y,z in self.vertices]
        current = None
        for mat, f in self.faces:
            if mat != current:
                lines.append('usemtl ' + mat)
                current = mat
            lines.append('f ' + ' '.join(map(str, reversed(f))))
        (OUT / (name + '.obj')).write_text('\n'.join(lines), encoding='utf-8')
        print(name, len(self.faces), 'triangles')


terrain = Mesh()
for j in range(80):
    for i in range(80):
        x, y = -4000 + i * 100, -4000 + j * 100
        terrain.face([(a,b,height(a,b)) for a,b in [(x,y),(x+100,y),(x+100,y+100),(x,y+100)]])
terrain.save('SM_EnvironmentTerrain')

path = Mesh()
for i in range(100):
    y0, y1 = -3500+i*47, -3500+(i+1)*47
    w0, w1 = 120+15*math.sin(i*.3), 120+15*math.sin((i+1)*.3)
    path.face([(x,y,height(x,y)+2) for x,y in
               [(path_x(y0)-w0,y0),(path_x(y0)+w0,y0),(path_x(y1)+w1,y1),(path_x(y1)-w1,y1)]], 'Path')
path.save('SM_EnvironmentPath')

tree = Mesh()
tree.box((0,0,175),(35,35,350),'Bark')
tree.cone(185,180,570,'Pine',11)
tree.cone(152,330,680,'PineLight',10,.2)
tree.cone(105,480,800,'Pine',9,.5)
tree.save('SM_PrototypePine')

rock = Mesh()
rng = random.Random(64)
rings = []
for z, radius in [(0,80),(65,115),(145,62)]:
    rings.append([(math.cos(i*math.pi/4)*radius*rng.uniform(.85,1.15),
                   math.sin(i*math.pi/4)*radius*rng.uniform(.85,1.15),z+rng.uniform(-10,10)) for i in range(8)])
for k in range(2):
    for i in range(8): rock.face([rings[k][i],rings[k][(i+1)%8],rings[k+1][(i+1)%8],rings[k+1][i]],'Stone')
rock.face(rings[-1],'Stone')
rock.face(list(reversed(rings[0])),'Stone')
rock.save('SM_PrototypeRock')

house = Mesh()
# Front aperture is 144cm wide, matching the existing door frame's outer width.
house.box((0,350,-12),(830,730,24),'Stone')
for x, width in [(-236,328),(236,328)]:
    house.box((x,10,150),(width,20,300),'Wood')
house.box((0,10,266),(144,20,68),'Wood')
house.box((0,690,150),(800,20,300),'Wood')
for x in [-390,390]: house.box((x,350,150),(20,700,300),'Wood')
# Horizontal plank seams, corner posts and structural bands.
for z in range(30,300,30):
    for x,w in [(-236,328),(236,328)]: house.box((x,-2,z),(w,5,3),'Bark')
    for x in [-402,402]: house.box((x,350,z),(5,700,3),'Bark')
for x in [-400,400]:
    for y in [0,700]: house.box((x,y,150),(24,24,310),'Bark')
for z in [12,300]:
    house.box((0,-5,z),(850,22,24),'Bark') if z==300 else None
    for x in [-405,405]: house.box((x,350,z),(25,730,24),'Bark')
# Front and rear gables.
for y in [10,690]:
    tri=[(-400,y,300),(400,y,300),(0,y,555)]
    house.face(list(reversed(tri)) if y==10 else tri,'Wood')
# Thick roof slopes. Individual strips make restrained shingle rows.
for side in [-1,1]:
    for row in range(8):
        a,b=row/8,(row+1)/8
        x0,x1=side*a*455,side*b*455
        z0,z1=555-a*290,555-b*290
        p=[(x0,-65,z0+8),(x1,-65,z1+8),(x1,765,z1+8),(x0,765,z0+8)]
        house.face(list(reversed(p)) if side<0 else p,'Roof' if row%2 else 'RoofLight')
        # Back face and raised row edge also visible from inside.
        house.face(list(reversed(p)) if side>0 else p,'Roof')
        house.box((x1,350,z1+7),(8,830,12),'Bark')
house.box((0,350,563),(24,850,20),'Bark')
# Small front windows and shutters. Dark panes remain solid placeholder surfaces.
for x in [-250,250]:
    house.box((x,-4,178),(90,12,100),'Bark')
    house.box((x,-12,178),(72,4,82),'Glass')
    house.box((x,-17,178),(7,8,90),'Wood')
    house.box((x,-18,178),(80,8,7),'Wood')
    house.box((x,-24,126),(110,40,12),'Bark')
house.save('SM_PrototypeTimberHouse')

# Deterministic scatter; reserve the house clearing, spawn and entire path corridor.
placements = []
rng = random.Random(812)
for i in range(64):
    for attempt in range(200):
        x,y=rng.uniform(-3700,3700),rng.uniform(-3700,3700)
        if math.hypot(x-900,y-1350)<1300 or abs(x-path_x(y))<380: continue
        if any(math.hypot(x-p['x'],y-p['y'])<360 for p in placements if p['kind']=='Tree'): continue
        placements.append(dict(kind='Tree',x=x,y=y,z=height(x,y)-5,yaw=rng.uniform(0,360),scale=rng.uniform(.7,1.25)))
        break
for i in range(32):
    x,y=rng.uniform(-3600,3600),rng.uniform(-3600,3600)
    if math.hypot(x-900,y-1350)<1050 or abs(x-path_x(y))<270: continue
    placements.append(dict(kind='Rock',x=x,y=y,z=height(x,y)-15,yaw=rng.uniform(0,360),scale=rng.uniform(.5,1.6)))
(OUT/'placements.json').write_text(json.dumps(placements,indent=2),encoding='utf-8')
print(len(placements),'placements')
