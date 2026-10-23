"""One 30-degree window-wall variant for the existing Blatthof kit.

Run with python -B from the project root. Writes only Saved/ElvenWindowSources.
Reuses the study's opaque glass palette and leaf tracery without changing it.
This exports source geometry and authoring metadata, not a building generator.
"""
import json
import math
from pathlib import Path

import generate_elven_join_sample as join
from generate_elven_blatthof import polar
from generate_elven_closed_house import box

OUT = Path('Saved/ElvenWindowSources')
NAME = 'SM_EB_WallOuter_Window_R640_A30_H280_LeafFrame'


class WindowMesh(join.ModuleMesh):
    def tube(self, points, radius, mat, sides=6):
        """Stable radial cross-sections even where the leaf becomes vertical.

        The study's generic tube helper changes its reference axis near a
        vertical tangent. Keep that source untouched and avoid ring twists here.
        """
        rings = []
        for i, p in enumerate(points):
            prev, nxt = points[max(0, i-1)], points[min(len(points)-1, i+1)]
            tangent = join.unit(tuple(nxt[k]-prev[k] for k in range(3)))
            radial = join.unit((p[0], p[1], 0))
            dot = sum(radial[k]*tangent[k] for k in range(3))
            u = join.unit(tuple(radial[k]-dot*tangent[k] for k in range(3)))
            v = (tangent[1]*u[2]-tangent[2]*u[1],
                 tangent[2]*u[0]-tangent[0]*u[2],
                 tangent[0]*u[1]-tangent[1]*u[0])
            rings.append([tuple(p[k]+radius*(u[k]*math.cos(j*2*math.pi/sides)
                                              +v[k]*math.sin(j*2*math.pi/sides))
                                for k in range(3)) for j in range(sides)])
        self.face(list(reversed(rings[0])), mat)
        self.face(rings[-1], mat)
        for i in range(len(rings)-1):
            for j in range(sides):
                self.face([rings[i][j], rings[i][(j+1)%sides],
                           rings[i+1][(j+1)%sides], rings[i+1][j]], mat)


def collision_band(a0, a1, z0, z1, r0=630, r1=650, step=6, name='Wall'):
    count = max(1, round((a1-a0)/step))
    width = (a1-a0)/count
    half = math.radians(width/2)
    radius = (r1+r0*math.cos(half))/2
    return [box(join.local(polar(radius, a0+width*(i+.5), (z0+z1)/2)),
                (2*r1*math.sin(half)+.1, r1-r0*math.cos(half), z1-z0),
                a0+width*(i+.5), name+'_%02d'%i) for i in range(count)]


def build():
    mesh = WindowMesh()
    # Match the solid module's ten 3-degree surface panels and end boundaries.
    for a, b, lo, hi in [(0, 6, 0, 280), (24, 30, 0, 280),
                         (6, 24, 0, 75), (6, 24, 240, 280)]:
        mesh.arc(630, 650, a, b, lo, hi, 'Ivory', round((b-a)/3))
    mesh.arc(637, 643, 6, 24, 75, 240, 'Glass', 6)
    # Continuous perimeter and upright, grouped rather than separate tiny assets.
    for z0, z1 in [(69, 81), (234, 246)]:
        mesh.arc(629, 655, 6, 24, z0, z1, 'Timber', 6)
    for a0, a1 in [(5.5, 6.5), (23.5, 24.5)]:
        mesh.arc(629, 655, a0, a1, 75, 240, 'Timber', 1)
    # Same motif as the original study, reduced segments for a small module.
    for sign in [-1, 1]:
        mesh.tube([polar(653, 15+sign*9*math.sin(math.pi*k/12), 75+165*k/12)
                   for k in range(13)], 5, 'Bronze', sides=6)
    mesh.tube([polar(654, 15, 75), polar(654, 15, 240)], 3, 'Timber', sides=6)
    for z in [95, 220]:
        mesh.tube([polar(653, 6+18*k/6, z) for k in range(7)], 3, 'Timber', sides=6)
    # Correct the arc helper's radial end winding only in this new source.
    # Tube polygons can also lie in a radial plane; only arc quads are changed.
    for i, (points, material) in enumerate(mesh.faces):
        angles = [math.degrees(math.atan2(p[1], p[0])) for p in points]
        if len(points) == 4 and max(angles)-min(angles) < 1e-7:
            points = list(reversed(points))
            mesh.faces[i] = (points, material)
            mesh.normals[i] = [join.face_normal(points)]*len(points)
    # Keep structural collision outside the opening; opaque fixed glass gets
    # its own thin blocking bodies. No collision on decorative leaf tracery.
    bodies = []
    for a, b, lo, hi, name in [(0, 6, 0, 280, 'SideA'), (24, 30, 0, 280, 'SideB'),
                                (6, 24, 0, 75, 'Sill'), (6, 24, 240, 280, 'Lintel')]:
        bodies += collision_band(a, b, lo, hi, name=name)
    bodies += collision_band(6, 24, 75, 240, 637, 643, name='FixedGlass')
    # Contract checks include normals and both ends against the unchanged solid wall.
    boundary = join.verify_boundaries(mesh)
    assert boundary == 4, boundary
    ivory = [(p, mat) for points, mat in mesh.faces for p in points if mat == 'Ivory']
    assert not any(6.01 < math.degrees(math.atan2(p[1], p[0])) < 23.99
                   and 75.01 < p[2] < 239.99 for p, _ in ivory)
    assert all(b['z'] > 0 and b['x'] > 0 and b['y'] > 0 for b in bodies)
    OUT.mkdir(parents=True, exist_ok=True)
    join.OUT = OUT
    materials = sorted({m for _, m in mesh.faces})
    (OUT/'BlatthofJoin.mtl').write_text(''.join('newmtl '+m+'\nKd 0.5 0.5 0.5\n'
                                               for m in materials), encoding='utf8')
    data = mesh.save_module(NAME)
    assert data['triangles'] <= 1000, data['triangles']
    manifest = dict(kit_id='EB.Blatthof.R255_R640', interface_version=1,
                    module_id='EB.Wall.Outer.Window.A30.v1', units='cm',
                    layer='OuterWall', angle_degrees=30, wall_radii_cm=[630, 650],
                    window=dict(angles_deg=[6, 24], sill_cm=75, top_cm=240,
                                glass_radii_cm=[637, 643], fixed=True, opaque=True),
                    pivot='R255 start; X tangent, Y inward, Z up',
                    joins=dict(Join_A=dict(location=[0, 0, 0], yaw=180),
                               Join_B=dict(location=[127.5, 34.16352203496813, 0], yaw=30)),
                    boundary_points_verified=boundary, mesh=data, collision_boxes=bodies,
                    collision_policy='UseSimpleAsComplex; 8 structure + 3 fixed glass boxes',
                    material_paths={m:'/Game/Art/Materials/ElvenBlatthof/MI_Blatthof_'+m
                                    for m in materials})
    (OUT/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf8')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    build()
