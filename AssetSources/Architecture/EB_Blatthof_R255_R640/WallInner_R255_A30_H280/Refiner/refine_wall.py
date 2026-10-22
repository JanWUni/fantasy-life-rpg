"""Blender-only UV refinement and independent contract checks. Writes beside this script.

Run --mode refine, verify or previews in separate Blender background processes.
No creator generator is executed and no Unreal API is used.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / 'Evidence'
INPUT = EVIDENCE / 'Input'
NAME = 'SM_EB_WallInner_R255_A30_H280'
BLEND = ROOT / (NAME + '.blend')
FBX = ROOT / 'Exports' / (NAME + '.fbx')
CONTRACT = json.loads((INPUT / 'manifest.json').read_text(encoding='utf-8'))
COMMIT = 'e66d5beed7bb85313501659d646f25778515134b'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_json(path, value):
    path = path.resolve()
    assert path.is_relative_to(ROOT)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')

def ue(p):
    return Vector((100 * p.x, -100 * p.y, 100 * p.z))

def expected_point(r, a, z):
    return Vector((r * math.sin(math.radians(a)) / 100,
                   (r * math.cos(math.radians(a)) - 255) / 100, z / 100))

def kind(poly, mesh):
    points = [mesh.vertices[i].co for i in poly.vertices]
    if max(p.z for p in points) - min(p.z for p in points) < 1e-5:
        return 'top' if points[0].z > 1 else 'bottom'
    radii = [math.hypot(p.x, p.y + 2.55) for p in points]
    if max(radii) - min(radii) < 1e-5:
        return 'inner' if sum(radii) / len(radii) < 2.55 else 'outer'
    angles = [math.atan2(p.x, p.y + 2.55) for p in points]
    assert max(angles) - min(angles) < 1e-5
    return 'start' if abs(angles[0]) < 1e-5 else 'end'

def topology(obj):
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    assert all(e.is_manifold and e.is_contiguous for e in bm.edges), obj.name
    assert all(f.calc_area() > 1e-10 for f in bm.faces), obj.name
    assert len(bm.verts) - len(bm.edges) + len(bm.faces) == 2
    volume = bm.calc_volume(signed=True)
    assert volume > 0
    bm.free()
    points = [v.co.copy() for v in mesh.vertices]
    minimum_separation = min((a - b).length for i, a in enumerate(points) for b in points[i+1:])
    assert minimum_separation > 1e-7, 'Coincident vertices'
    mesh.calc_loop_triangles()
    return {'vertices': len(mesh.vertices), 'edges': len(mesh.edges), 'faces': len(mesh.polygons),
            'triangles': len(mesh.loop_triangles), 'volume_m3': volume,
            'minimum_vertex_separation_m': minimum_separation,
            'closed_consistent_outward_manifold': True, 'duplicate_vertices': 0}

def cross2(a, b):
    return a[0] * b[1] - a[1] * b[0]

def sub2(a, b):
    return (a[0] - b[0], a[1] - b[1])

def polygon_area(poly):
    return abs(sum(cross2(poly[i], poly[(i+1) % len(poly)]) for i in range(len(poly)))) / 2 if len(poly) > 2 else 0

def overlap_area(tri_a, tri_b):
    clip = list(tri_b)
    if cross2(sub2(clip[1], clip[0]), sub2(clip[2], clip[0])) < 0:
        clip.reverse()
    out = list(tri_a)
    for a, b in zip(clip, clip[1:] + clip[:1]):
        src, out = out, []
        if not src:
            return 0
        edge = sub2(b, a)
        p = src[-1]
        dp = cross2(edge, sub2(p, a))
        for q in src:
            dq = cross2(edge, sub2(q, a))
            if (dp >= 0) != (dq >= 0):
                t = dp / (dp - dq)
                out.append((p[0] + t*(q[0]-p[0]), p[1] + t*(q[1]-p[1])))
            if dq >= 0:
                out.append(q)
            p, dp = q, dq
    return polygon_area(out)

def uv_metrics(mesh):
    assert len(mesh.uv_layers) == 1 and mesh.uv_layers[0].name == 'UV0'
    uv = mesh.uv_layers[0].data
    mesh.calc_loop_triangles()
    triangles, densities, anisotropies = [], [], []
    for tri in mesh.loop_triangles:
        p, q, r = [mesh.vertices[i].co for i in tri.vertices]
        tex = [tuple(uv[i].uv) for i in tri.loops]
        assert all(math.isfinite(x) and -1e-6 <= x <= 1+1e-6 for t in tex for x in t)
        area_uv = polygon_area(tex)
        area_world = (q-p).cross(r-p).length / 2
        assert area_uv > 1e-10 and area_world > 1e-10
        densities.append(math.sqrt(area_uv / area_world))
        # Singular values of the per-triangle physical-meters -> UV Jacobian.
        e1, e2 = q-p, r-p
        x1 = e1.length
        x2 = e1.dot(e2) / x1
        y2 = math.sqrt(max(0, e2.length_squared - x2*x2))
        t1, t2 = sub2(tex[1], tex[0]), sub2(tex[2], tex[0])
        j1 = (t1[0]/x1, t1[1]/x1)
        j2 = ((t2[0]-t1[0]*x2/x1)/y2, (t2[1]-t1[1]*x2/x1)/y2)
        a, b, c = sum(v*v for v in j1), sum(v*v for v in j2), sum(v*w for v, w in zip(j1, j2))
        d = math.sqrt((a-b)**2 + 4*c*c)
        anisotropies.append(math.sqrt((a+b+d)/(a+b-d)))
        triangles.append(tex)
    overlaps = [(i, j, overlap_area(a, b)) for i, a in enumerate(triangles) for j, b in enumerate(triangles[i+1:], i+1)
                if overlap_area(a, b) > 1e-9]
    assert not overlaps, overlaps[:3]
    # Connected face charts based on UV continuity along shared mesh edges.
    adjacency = {p.index: set() for p in mesh.polygons}
    edges = {}
    for poly in mesh.polygons:
        ids = list(poly.loop_indices)
        for i, lid in enumerate(ids):
            nxt = ids[(i+1) % len(ids)]
            entry = {mesh.loops[lid].vertex_index: tuple(uv[lid].uv), mesh.loops[nxt].vertex_index: tuple(uv[nxt].uv)}
            key = tuple(sorted(entry))
            for other, coords in edges.get(key, []):
                if all(sum((x-y)**2 for x, y in zip(entry[v], coords[v])) < 1e-12 for v in key):
                    adjacency[poly.index].add(other)
                    adjacency[other].add(poly.index)
            edges.setdefault(key, []).append((poly.index, entry))
    todo, charts = set(adjacency), []
    while todo:
        group, pending = set(), [next(iter(todo))]
        while pending:
            i = pending.pop()
            if i in group:
                continue
            group.add(i)
            pending.extend(adjacency[i] - group)
        todo -= group
        coords = [tuple(uv[lid].uv) for i in group for lid in mesh.polygons[i].loop_indices]
        charts.append({'faces': len(group), 'min': [min(t[k] for t in coords) for k in (0,1)],
                       'max': [max(t[k] for t in coords) for k in (0,1)]})
    assert len(charts) == 6, len(charts)
    box_gap = min(math.hypot(max(a['min'][0]-b['max'][0], b['min'][0]-a['max'][0], 0),
                              max(a['min'][1]-b['max'][1], b['min'][1]-a['max'][1], 0))
                  for i, a in enumerate(charts) for b in charts[i+1:])
    return {'channels': 1, 'islands': 6, 'overlap_pairs_above_1e_9_uv_area': len(overlaps),
            'density_uv_per_meter_min': min(densities), 'density_uv_per_meter_max': max(densities),
            'density_max_min_ratio': max(densities)/min(densities), 'max_triangle_anisotropy': max(anisotropies),
            'occupied_uv_area': sum(polygon_area(t) for t in triangles),
            'minimum_chart_bbox_gap_uv': box_gap, 'charts': charts}

def inspect_scene(roundtrip=False):
    meshes = sorted([o for o in bpy.context.scene.objects if o.type == 'MESH'], key=lambda o: o.name)
    assert len(meshes) == 11 and len(bpy.context.scene.objects) == 11
    wall = bpy.data.objects[NAME]
    for obj in meshes:
        assert max(abs(x) for x in obj.location) < 1e-6
        assert max(abs(x) for x in obj.rotation_euler) < 1e-6
        assert max(abs(x-1) for x in obj.scale) < 1e-6
        assert obj.matrix_world.determinant() > 0
    result = topology(wall)
    assert result['vertices'] == 44 and result['triangles'] == 84
    assert [s.material.name for s in wall.material_slots] == ['Ivory']
    assert all(p.material_index == 0 for p in wall.data.polygons)
    assert not bpy.data.libraries
    assert not any(i.source == 'FILE' for i in bpy.data.images)
    expected = [expected_point(r, i*3, z) for i in range(11) for r in (245,265) for z in (0,280)]
    actual = [v.co.copy() for v in wall.data.vertices]
    error = max(max(min((p-q).length for q in expected) for p in actual), max(min((p-q).length for p in actual) for q in expected))*100
    assert error < 0.001
    points_ue = [ue(p) for p in actual]
    result['bounds_ue_cm'] = [[min(p[k] for p in points_ue) for k in range(3)], [max(p[k] for p in points_ue) for k in range(3)]]
    starts = [p for p in points_ue if abs(p.x) < .001]
    ends = [p for p in points_ue if abs(math.degrees(math.atan2(p.x,255-p.y))-30) < .0001]
    assert len(starts) == len(ends) == 4
    jb = CONTRACT['joins_ue_cm_degrees']['Join_B']
    a = math.radians(jb['yaw'])
    c, s = math.cos(a), math.sin(a)
    joined = [Vector((jb['position'][0]+c*p.x-s*p.y, jb['position'][1]+s*p.x+c*p.y,p.z)) for p in starts]
    seam = max(min((p-q).length for q in ends) for p in joined)
    assert seam < CONTRACT['tolerances']['join_position_cm']
    result['analytic_profile_max_error_cm'] = error
    result['two_instance_seam_error_cm'] = seam
    # Verify every radial corner and every planar cap normal, not only smoothing flags.
    norm_error, cap_error, ns, ne = 0, 0, [], []
    for poly in wall.data.polygons:
        typ = kind(poly, wall.data)
        for lid in poly.loop_indices:
            p = wall.data.vertices[wall.data.loops[lid].vertex_index].co
            n = wall.data.corner_normals[lid].vector.copy()
            if typ in ('inner','outer'):
                sign = 1 if typ == 'outer' else -1
                radial = Vector((p.x, p.y+2.55, 0)).normalized() * sign
                norm_error = max(norm_error,(n-radial).length)
                n_ue = Vector((n.x,-n.y,n.z))
                if abs(p.x) < 1e-5:
                    ns.append(Vector((c*n_ue.x-s*n_ue.y,s*n_ue.x+c*n_ue.y,n_ue.z)))
                if abs(math.degrees(math.atan2(p.x,p.y+2.55))-30) < .0001:
                    ne.append(n_ue)
            else:
                cap_error = max(cap_error,(n-poly.normal).length)
    seam_normal = max(min((p-q).length for q in ne) for p in ns)
    assert max(norm_error, cap_error, seam_normal) < .001
    result.update({'radial_normal_error': norm_error, 'planar_cap_normal_error': cap_error, 'seam_normal_error': seam_normal})
    result['uv'] = uv_metrics(wall.data)
    colliders = []
    for i in range(10):
        obj = bpy.data.objects['UCX_' + NAME + '_%02d' % i]
        item = topology(obj)
        assert item['vertices'] == 8 and item['triangles'] == 12
        expected = [expected_point(r,t,z) for t in (i*3,(i+1)*3) for r in (245,265) for z in (0,280)]
        err = max(min((p-v.co).length for v in obj.data.vertices) for p in expected)
        assert err < 1e-6
        convex_error = max(poly.normal.dot(v.co-obj.data.vertices[poly.vertices[0]].co) for poly in obj.data.polygons for v in obj.data.vertices)
        assert convex_error < 1e-6
        colliders.append({'name': obj.name, **item, 'expected_segment_error_m': err, 'convex_error_m': convex_error})
    volume_error = abs(sum(x['volume_m3'] for x in colliders)-result['volume_m3'])
    assert volume_error < 1e-6
    result.update({'collision_hulls': 10, 'collision_triangles': 120, 'collision': colliders,
                   'collision_volume_sum_error_m3': volume_error, 'identity_transforms': True,
                   'slots': ['Ivory'], 'roundtrip': roundtrip})
    if not roundtrip:
        assert bpy.context.scene.unit_settings.system == 'METRIC'
        assert bpy.context.scene.unit_settings.scale_length == 1
        assert len(wall.modifiers) == 1 and wall.modifiers[0].type == 'TRIANGULATE'
        metadata_error = max(abs(float(x)-y) for x,y in zip(wall['Join_B_UE_cm_yaw_deg'], jb['position']+[jb['yaw']]))
        assert metadata_error < 1e-5
        result['join_metadata_max_numeric_error'] = metadata_error
        ev = wall.evaluated_get(bpy.context.evaluated_depsgraph_get())
        mesh = ev.to_mesh()
        mesh.calc_loop_triangles()
        assert len(mesh.loop_triangles) == 84 and all(len(p.vertices)==3 for p in mesh.polygons)
        ev.to_mesh_clear()
    return result

def signature(obj):
    m = obj.data
    return {'vertices': [list(v.co) for v in m.vertices], 'polygons': [list(p.vertices) for p in m.polygons],
            'normals': [list(n.vector) for n in m.corner_normals], 'smooth': [p.use_smooth for p in m.polygons],
            'transform': [list(row) for row in obj.matrix_world]}

def remap_uv(wall):
    mesh = wall.data
    groups = {t: [] for t in ('inner','outer','start','end','top','bottom')}
    for poly in mesh.polygons:
        groups[kind(poly,mesh)].append(poly)
    raw = {}
    for typ, polys in groups.items():
        ids = set(v for p in polys for v in p.vertices)
        coords = {i: mesh.vertices[i].co.copy() for i in ids}
        if typ in ('inner','outer'):
            levels = sorted({i for i in ids if abs(coords[i].z) < 1e-6}, key=lambda i: math.atan2(coords[i].x,coords[i].y+2.55))
            cumulative, length = {}, 0
            for index, i in enumerate(levels):
                if index:
                    length += (coords[i]-coords[levels[index-1]]).length
                cumulative[round(math.atan2(coords[i].x,coords[i].y+2.55),5)] = length
            raw[typ] = {i: (cumulative[round(math.atan2(p.x,p.y+2.55),5)],p.z) for i,p in coords.items()}
        elif typ in ('top','bottom'):
            # These surfaces are exactly planar; XY projection is an isometry.
            raw[typ] = {i: (p.x,p.y) for i,p in coords.items()}
        else:
            bottom = [p for p in coords.values() if abs(p.z) < 1e-6]
            origin = min(bottom,key=lambda p: math.hypot(p.x,p.y+2.55))
            axis = (max(bottom,key=lambda p: math.hypot(p.x,p.y+2.55))-origin).normalized()
            raw[typ] = {i: ((p-origin).dot(axis),p.z) for i,p in coords.items()}
    mins = {t: [min(p[k] for p in d.values()) for k in (0,1)] for t,d in raw.items()}
    sizes = {t: [max(p[k] for p in d.values())-mins[t][k] for k in (0,1)] for t,d in raw.items()}
    gap, margin = .04, .04
    offsets, cursor = {}, margin
    for typ in ('inner','outer','start','end'):
        offsets[typ] = (cursor,margin)
        cursor += sizes[typ][0] + gap
    top_y = margin + 2.8 + gap
    offsets['top'] = (margin,top_y)
    offsets['bottom'] = (margin+sizes['top'][0]+gap,top_y)
    side = max(cursor-gap+margin, offsets['bottom'][0]+sizes['bottom'][0]+margin,
               top_y+max(sizes['top'][1],sizes['bottom'][1])+margin)
    uv = mesh.uv_layers[0].data
    for typ, polys in groups.items():
        for poly in polys:
            for lid in poly.loop_indices:
                value = raw[typ][mesh.loops[lid].vertex_index]
                uv[lid].uv = tuple((value[k]-mins[typ][k]+offsets[typ][k])/side for k in (0,1))
    # Mark existing six chart boundaries for predictable later manual editing.
    edge_types = {}
    for poly in mesh.polygons:
        for lid in poly.loop_indices:
            edge_types.setdefault(mesh.loops[lid].edge_index,set()).add(kind(poly,mesh))
    for edge in mesh.edges:
        edge.use_seam = len(edge_types[edge.index]) > 1
    return {'layout': 'Six physical-metric charts: chord-length side strips, planar XY caps, radial end strips',
            'uniform_pack_side_m': side, 'padding_physical_m': gap, 'padding_uv': gap/side,
            'source_uv_layer': 'UV0', 'seam_edges_marked': sum(e.use_seam for e in mesh.edges)}

def refine():
    assert sha(BLEND) == CONTRACT['sha256'][BLEND.name], 'Expected a pristine copied Creator input'
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    before = inspect_scene()
    geometry_before = {o.name: signature(o) for o in bpy.context.scene.objects}
    wall = bpy.data.objects[NAME]
    packing = remap_uv(wall)
    after = inspect_scene()
    geometry_after = {o.name: signature(o) for o in bpy.context.scene.objects}
    assert geometry_before == geometry_after, 'Refinement must not alter geometry, normals or transforms'
    assert after['uv']['density_max_min_ratio'] < 1.0001 and after['uv']['max_triangle_anisotropy'] < 1.0001
    wall['RefinerInputCommit'] = COMMIT
    wall['RefinerRevision'] = 1
    wall['RefinerChange'] = 'UV0: uniform physical density; six islands; seam flags. Geometry/normals/UCX unchanged.'
    bpy.context.preferences.filepaths.save_version = 0
    assert bpy.ops.wm.save_as_mainfile(filepath=str(BLEND)) == {'FINISHED'}
    if 'io_scene_fbx' not in bpy.context.preferences.addons:
        bpy.ops.preferences.addon_enable(module='io_scene_fbx')
    for obj in bpy.context.scene.objects:
        obj.select_set(obj.type == 'MESH')
    bpy.context.view_layer.objects.active = wall
    settings = dict(CONTRACT['export']['settings'])
    assert settings['apply_scale_options'] == 'FBX_SCALE_NONE'
    settings['object_types'] = set(settings['object_types'])
    FBX.parent.mkdir(exist_ok=True)
    assert bpy.ops.export_scene.fbx(filepath=str(FBX), **settings) == {'FINISHED'}
    write_json(EVIDENCE / 'refinement.json', {'input_commit': COMMIT, 'blender': bpy.app.version_string,
        'build': bpy.app.build_hash.decode(), 'before': before, 'after': after,
        'geometry_normals_transforms_bitwise_unchanged': True, 'packing': packing,
        'output_sha256': {BLEND.name:sha(BLEND),'Exports/'+FBX.name:sha(FBX)}})
    print('REFINE_OK', json.dumps({'before_uv': before['uv'], 'after_uv': after['uv']}))

def verify():
    refinement = json.loads((EVIDENCE/'refinement.json').read_text(encoding='utf-8'))
    for name,digest in refinement['output_sha256'].items():
        assert sha(ROOT/name) == digest
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    source = inspect_scene()
    assert source == refinement['after']
    source_mesh = bpy.data.objects[NAME].data
    source_corners = [(source_mesh.vertices[loop.vertex_index].co.copy(), source_mesh.uv_layers[0].data[loop.index].uv.copy())
                      for loop in source_mesh.loops]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if 'io_scene_fbx' not in bpy.context.preferences.addons:
        bpy.ops.preferences.addon_enable(module='io_scene_fbx')
    assert bpy.ops.import_scene.fbx(filepath=str(FBX),use_custom_normals=True,use_anim=False,use_image_search=False)=={'FINISHED'}
    roundtrip = inspect_scene(roundtrip=True)
    assert roundtrip['uv']['density_max_min_ratio'] < 1.0001
    assert roundtrip['uv']['max_triangle_anisotropy'] < 1.0001
    # Match UVs by position, not by FBX loop order; retain every authored corner mapping.
    imported = bpy.data.objects[NAME].data
    assert len(imported.uv_layers)==1
    uv_error = 0
    for loop in imported.loops:
        p = imported.vertices[loop.vertex_index].co
        tex = imported.uv_layers[0].data[loop.index].uv
        matches = [v for q,v in source_corners if (p-q).length < 1e-6]
        assert matches
        uv_error = max(uv_error, min((tex-v).length for v in matches))
    assert uv_error < 1e-6
    assert FBX.read_bytes()[:23] == b'Kaydara FBX Binary  \x00\x1a\x00'
    result = {'status':'passed','scope':'Saved Refiner source reopened and Refiner FBX imported into empty Blender scene in a separate process; no Unreal validation',
        'blender':bpy.app.version_string,'build':bpy.app.build_hash.decode(),'source':source,'fbx_roundtrip':roundtrip,
        'output_sha256':refinement['output_sha256'],'fbx_binary_version':int.from_bytes(FBX.read_bytes()[23:27],'little'),
        'roundtrip_max_corner_uv_error':uv_error,'unreal_import_performed':False}
    write_json(ROOT/'verification.json',result)
    print('VERIFY_OK',json.dumps({'source_seam_cm':source['two_instance_seam_error_cm'],
        'fbx_seam_cm':roundtrip['two_instance_seam_error_cm'],'fbx_uv':roundtrip['uv']}))

def setup_camera(scene, location, target, scale):
    camera = bpy.data.objects.new('ReviewCamera',bpy.data.cameras.new('ReviewCamera'))
    scene.collection.objects.link(camera)
    scene.camera=camera
    camera.data.type='ORTHO'
    camera.data.ortho_scale=scale
    camera.location=location
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()

def render(path):
    scene=bpy.context.scene
    scene.render.engine='BLENDER_WORKBENCH'
    scene.display.shading.light='STUDIO'
    scene.display.shading.color_type='OBJECT'
    scene.display.shading.show_shadows=True
    scene.display.shading.show_cavity=True
    scene.display.shading.background_type='WORLD'
    if not scene.world:
        scene.world=bpy.data.worlds.new('PreviewWorld')
    scene.world.color=(.045,.055,.075)
    scene.render.resolution_x=1200
    scene.render.resolution_y=1000
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)

def previews():
    dest=ROOT/'Previews'
    dest.mkdir(exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    wall=bpy.data.objects[NAME]
    wall.color=(.82,.78,.65,1)
    second=wall.copy()
    bpy.context.scene.collection.objects.link(second)
    jb=CONTRACT['joins_blender_m_degrees']['Join_B']
    second.location=jb['position']
    second.rotation_euler.z=math.radians(jb['yaw'])
    second.color=(.47,.64,.63,1)
    setup_camera(bpy.context.scene,(5,6,4.5),(1.1,-.35,1.35),5.5)
    render(dest/'two_modules.png')
    # Reverse view exposes outside, cap and the same exact join from the other side.
    bpy.context.scene.camera.location=(4,-6,4.4)
    bpy.context.scene.camera.rotation_euler=(Vector((1.1,-.35,1.35))-bpy.context.scene.camera.location).to_track_quat('-Z','Y').to_euler()
    render(dest/'two_modules_outer.png')
    # UV before/after as actual triangulated Blender mesh charts under identical scale.
    for label, source in [('before',INPUT/BLEND.name),('after',BLEND)]:
        bpy.ops.wm.open_mainfile(filepath=str(source))
        mesh=bpy.data.objects[NAME].data
        mesh.calc_loop_triangles()
        uv=mesh.uv_layers[0].data
        coords=[(v.uv.x,v.uv.y,0) for v in uv]
        faces=[tuple(t.loops) for t in mesh.loop_triangles]
        bpy.ops.wm.read_factory_settings(use_empty=True)
        chart=bpy.data.meshes.new('UV0_Charts')
        chart.from_pydata(coords,[],faces)
        obj=bpy.data.objects.new('UV0_Charts',chart)
        bpy.context.scene.collection.objects.link(obj)
        obj.color=(.38,.72,.75,1)
        obj.show_wire=True
        obj.show_all_edges=True
        setup_camera(bpy.context.scene,(.5,.5,3),(.5,.5,0),1.35)
        render(dest/('uv_'+label+'.png'))
    print('PREVIEWS_OK; no preview objects saved into source')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--mode',choices=['refine','verify','previews'],required=True)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    {'refine':refine,'verify':verify,'previews':previews}[args.mode]()
