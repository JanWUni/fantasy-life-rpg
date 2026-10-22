"""Blender-only Creator source/export and verification; no Unreal operations.

Run with Blender --background --factory-startup --python-exit-code 1
--python <this file> -- --mode build|verify|preview. Writes only beside this file.
Build is deliberately refused if a delivered .blend or FBX already exists.
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[4]
NAME = "SM_EB_WallInner_R255_A30_H280"
KIT = "EB.Blatthof.R255_R640"
MODULE = "WallInner_R255_A30_H280"
BASE = "b1b2f051a2ead8d95c72e1253131eb9934d59b49"
BLEND = ROOT / (NAME + ".blend")
FBX = ROOT / "Exports" / (NAME + ".fbx")
PROFILE = REPO / "AssetSources/Calibration/BlenderUE01/unreal_import_profile.json"
ANGLE = math.radians(30)
JOIN_B = [255 * math.sin(ANGLE), 255 * (1 - math.cos(ANGLE)), 0]


def write_json(name, data):
    path = (ROOT / name).resolve()
    assert path.is_relative_to(ROOT)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ue(point):
    return Vector((point[0] * 100, -point[1] * 100, point[2] * 100))


def point(radius, angle_degrees, z):
    a = math.radians(angle_degrees)
    return (radius * math.sin(a) / 100, (radius * math.cos(a) - 255) / 100, z / 100)


def geometry(start=0, end=30, segments=10):
    """Welded ring-sector prism: no internal faces, no duplicated surface vertices."""
    vertices = [point(r, start + (end - start) * i / segments, z)
                for i in range(segments + 1) for r, z in ((245, 0), (265, 0), (245, 280), (265, 280))]
    faces, kinds = [], []
    for i in range(segments):
        a, b = 4 * i, 4 * (i + 1)
        # Outward Blender winding; Y reflection is in vertex coordinates already.
        faces.extend([(a, a + 1, b + 1, b), (a + 2, b + 2, b + 3, a + 3),
                      (a + 1, a + 3, b + 3, b + 1), (a, b, b + 2, a + 2)])
        kinds.extend(["bottom", "top", "outer", "inner"])
    faces.extend([(0, 2, 3, 1), (4 * segments, 4 * segments + 1, 4 * segments + 3, 4 * segments + 2)])
    kinds.extend(["start", "end"])
    return vertices, faces, kinds


def make_object(name, collection, start=0, end=30, segments=10):
    verts, faces, kinds = geometry(start, end, segments)
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj, kinds


def setup_render_mesh(obj, kinds):
    mesh = obj.data
    material = bpy.data.materials.new("Ivory")
    material.diffuse_color = (0.82, 0.78, 0.65, 1)
    material.use_nodes = True
    material.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value = material.diffuse_color
    material.node_tree.nodes.get("Principled BSDF").inputs["Roughness"].default_value = 0.8
    mesh.materials.append(material)
    layer = mesh.uv_layers.new(name="UV0")
    normals = []
    tile = {"inner": (0, 0), "outer": (1, 0), "top": (2, 0),
            "bottom": (0, 1), "start": (1, 1), "end": (2, 1)}
    for poly, kind in zip(mesh.polygons, kinds):
        poly.use_smooth = kind in ("inner", "outer")
        for loop_id in poly.loop_indices:
            p = mesh.vertices[mesh.loops[loop_id].vertex_index].co
            x, y, z = ue(p)
            radius = math.hypot(x, 255 - y)
            angle = math.atan2(x, 255 - y)
            if kind in ("inner", "outer"):
                sign = 1 if kind == "outer" else -1
                normal = (sign * math.sin(angle), sign * math.cos(angle), 0)
                u, v = angle / ANGLE, z / 280
            elif kind in ("top", "bottom"):
                normal = tuple(poly.normal)
                u, v = angle / ANGLE, (radius - 245) / 20
            else:
                normal = tuple(poly.normal)
                u, v = (radius - 245) / 20, z / 280
            normals.append(normal)
            col, row = tile[kind]
            layer.data[loop_id].uv = ((col + 0.05 + 0.9 * u) / 3, (row + 0.05 + 0.9 * v) / 2)
    mesh.normals_split_custom_set(normals)
    triangulate = obj.modifiers.new("Export_Triangulation", "TRIANGULATE")
    triangulate.quad_method = "FIXED"
    triangulate.ngon_method = "CLIP"
    if hasattr(triangulate, "keep_custom_normals"):
        triangulate.keep_custom_normals = True
    obj["KitId"] = KIT
    obj["ModuleId"] = MODULE
    obj["InterfaceVersion"] = 1
    obj["Join_A_UE_cm_yaw_deg"] = [0, 0, 0, 180]
    obj["Join_B_UE_cm_yaw_deg"] = JOIN_B + [30]
    obj["BlenderToUnrealCm"] = "(100*x,-100*y,100*z)"
    obj["UnrealMaterial_Slot0"] = "/Game/Art/Materials/ElvenBlatthof/MI_Blatthof_Ivory"


def build():
    assert not BLEND.exists() and not FBX.exists(), "Delivered sources are frozen; use a new explicit handoff to regenerate."
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.data.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1
    scene.unit_settings.length_unit = "METERS"
    bpy.context.preferences.filepaths.save_version = 0
    render_collection = bpy.data.collections.new("Render")
    collision_collection = bpy.data.collections.new("Collision_UCX")
    scene.collection.children.link(render_collection)
    scene.collection.children.link(collision_collection)
    wall, kinds = make_object(NAME, render_collection)
    setup_render_mesh(wall, kinds)
    for i in range(10):
        collider, _ = make_object("UCX_" + NAME + "_%02d" % i, collision_collection, 3 * i, 3 * (i + 1), 1)
        collider.display_type = "WIRE"
        collider.hide_render = True
    for obj in scene.objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = wall
    # Useful initial solid viewport, with all source objects at identity transforms.
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.spaces.active.region_3d.view_location = Vector((0.65, -0.08, 1.4))
                area.spaces.active.region_3d.view_distance = 5
    assert bpy.ops.wm.save_as_mainfile(filepath=str(BLEND)) == {"FINISHED"}
    if "io_scene_fbx" not in bpy.context.preferences.addons:
        bpy.ops.preferences.addon_enable(module="io_scene_fbx")
    settings = json.loads(PROFILE.read_text(encoding="utf-8"))["export_settings"]
    settings["object_types"] = set(settings["object_types"])
    FBX.parent.mkdir(exist_ok=True)
    assert bpy.ops.export_scene.fbx(filepath=str(FBX), **settings) == {"FINISHED"}
    settings["object_types"] = sorted(settings["object_types"])
    manifest = {
        "asset_name": NAME, "kit_id": KIT, "kit_directory": "EB_Blatthof_R255_R640",
        "module_id": MODULE, "interface_version": 1, "revision": 1, "status": "draft",
        "role": "Asset Creator", "base_commit": BASE,
        "allowed_write_directory": ROOT.relative_to(REPO).as_posix(),
        "sources": {"blend": BLEND.name, "fbx": FBX.relative_to(ROOT).as_posix(), "generator": "create_wall.py"},
        "reference": {"generator": "Tools/Prototype/generate_elven_join_sample.py", "commit": BASE,
                      "contract": "docs/technical/ELVEN_JOIN_SAMPLE_01.md", "visual": "docs/technical/ELVEN_BLATTHOF_STUDY.md"},
        "blender": {"version": bpy.app.version_string, "build": bpy.app.build_hash.decode(),
                    "addons": ["io_scene_fbx"], "external_dependencies": [], "modifier": "TRIANGULATE/FIXED"},
        "units": {"blender": "meters", "unreal": "centimeters", "unit_scale": 1,
                  "blender_to_unreal_cm": "(100*x,-100*y,100*z)"},
        "profile": {"layer": "InnerWall", "radius_reference_cm": 255, "radii_cm": [245, 265],
                    "angle_degrees": 30, "height_cm": 280, "floor_top_z_cm": 0, "segments": 10,
                    "thickness_radial_cm": 20, "openings": [], "decor": "none"},
        "pivot": {"location_cm": [0, 0, 0], "description": "Start on R255 at floor Z0; X tangent, UE Y inward, Z up",
                  "circle_center_ue_cm": [0, 255, 0], "circle_center_blender_m": [0, -2.55, 0]},
        "object_transform_blender": {"location_m": [0, 0, 0], "rotation_degrees": [0, 0, 0], "scale": [1, 1, 1]},
        "joins_ue_cm_degrees": {"Join_A": {"position": [0, 0, 0], "yaw": 180}, "Join_B": {"position": JOIN_B, "yaw": 30}},
        "joins_blender_m_degrees": {"Join_A": {"position": [0, 0, 0], "yaw": -180},
                                    "Join_B": {"position": [JOIN_B[0] / 100, -JOIN_B[1] / 100, 0], "yaw": -30}},
        "tolerances": {"join_position_cm": 0.1, "join_angle_degrees": 0.1},
        "material_slots": [{"index": 0, "name": "Ivory", "unreal_material": "/Game/Art/Materials/ElvenBlatthof/MI_Blatthof_Ivory"}],
        "uv": {"channels_source": 1, "name": "UV0", "layout": "Six separate padded islands; cylindrical sides continuous over ten segments",
               "overlap": "none", "lightmap_channel": "not authored; calibrated importer generates UV1; production quality untested"},
        "normal_policy": "Explicit radial split normals on curved sides; hard top/bottom/end caps; controlled export triangulation",
        "collision": {"mode_intended_unreal": "UseSimpleAsComplex", "hulls": 10, "triangles_total": 120,
                      "description": "Ten closed convex 3-degree prisms exactly matching render segments; shared cap planes, no volume overlap",
                      "difference_from_reference": "Source-owned convex prisms replace the five approximate editor boxes; same structural interface",
                      "unreal_validation": "not performed"},
        "render": {"vertices_source": 44, "quads_source": 42, "triangles_evaluated": 84, "material_slots": 1,
                   "textures": [], "texture_sizes": [], "lods_delivered": 1, "nanite_intended": False,
                   "lod_plan": "Keep simple 84-triangle LOD0; any further LODs require a separate assignment"},
        "export": {"settings": settings, "calibration_profile_id": "Blender522_UE58_LegacyFBX_Calibration01",
                   "profile_path": PROFILE.relative_to(REPO).as_posix(), "validation": "pending Blender-only roundtrip; no Unreal import"},
        "unreal": {"import_performed": False, "intended_importer": "FbxFactory / FbxStaticMeshImportData (legacy)",
                   "import_settings_reference": PROFILE.relative_to(REPO).as_posix(),
                   "calibration_observed_options": json.loads(PROFILE.read_text(encoding="utf-8"))["unreal_import_options_observed"],
                   "warning": "Observed calibration settings are reference values, not measured settings for this module. Interchange is not validated.",
                   "integration": "Separate assignment; no replacement of the existing same-named JoinSample01 asset is authorized"},
        "not_tested": ["Unreal import/reimport", "Unreal render vertices/UV generation/material assignment",
                       "Kapsel/PIE/camera/gameplay", "Performance/packaging/multiplayer", "Combined floor/roof assembly"],
        "sha256": {BLEND.name: sha(BLEND), FBX.relative_to(ROOT).as_posix(): sha(FBX), "create_wall.py": sha(Path(__file__))},
    }
    write_json("manifest.json", manifest)
    print("CREATOR_BUILD_OK", NAME)


def topology(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    assert all(e.is_manifold and e.is_contiguous for e in bm.edges), obj.name + ": nonmanifold/inconsistent winding"
    assert all(f.calc_area() > 1e-10 for f in bm.faces), obj.name + ": degenerate face"
    volume = bm.calc_volume(signed=True)
    assert volume > 0, (obj.name, volume)
    result = {"vertices": len(bm.verts), "edges": len(bm.edges), "faces": len(bm.faces), "volume_m3": volume}
    assert len(bm.verts) - len(bm.edges) + len(bm.faces) == 2
    bm.free()
    obj.data.calc_loop_triangles()
    result["triangles"] = len(obj.data.loop_triangles)
    return result


def check_geometry(obj):
    # Read existing generator functions without running build() or writing its outputs.
    sys.path.insert(0, str(REPO / "Tools/Prototype"))
    from generate_elven_join_sample import ModuleMesh, local
    reference = ModuleMesh()
    reference.arc(245, 265, 0, 30, 0, 280, "Ivory", 10)
    expected = {tuple(local(p)) for points, _ in reference.faces for p in points}
    actual = [ue(obj.matrix_world @ v.co) for v in obj.data.vertices]
    error = max(min((p - Vector(q)).length for p in actual) for q in expected)
    error = max(error, max(min((p - Vector(q)).length for q in expected) for p in actual))
    assert error < 0.001, error
    bounds = [[min(p[k] for p in actual) for k in range(3)], [max(p[k] for p in actual) for k in range(3)]]
    endpoint = lambda p: math.degrees(math.atan2(p.x, 255 - p.y))
    start = [p for p in actual if abs(endpoint(p)) < 0.0001]
    end = [p for p in actual if abs(endpoint(p) - 30) < 0.0001]
    assert len(start) == len(end) == 4
    c, s = math.cos(ANGLE), math.sin(ANGLE)
    joined = [Vector((JOIN_B[0] + c * p.x - s * p.y, JOIN_B[1] + s * p.x + c * p.y, p.z)) for p in start]
    seam = max(min((p - q).length for q in end) for p in joined)
    assert seam < 0.001, seam
    # Validate each actual corner normal independently against the reference field.
    normal_error = 0
    normals_start, normals_end = [], []
    for poly in obj.data.polygons:
        points = [ue(obj.data.vertices[obj.data.loops[i].vertex_index].co) for i in poly.loop_indices]
        radii = [math.hypot(p.x, 255 - p.y) for p in points]
        if max(radii) - min(radii) < 0.001 and max(p.z for p in points) - min(p.z for p in points) > 1:
            sign = 1 if abs(radii[0] - 265) < 0.01 else -1
            for loop_id, p in zip(poly.loop_indices, points):
                a = math.atan2(p.x, 255 - p.y)
                expected_n = Vector((sign * math.sin(a), sign * math.cos(a), 0))
                n = obj.data.corner_normals[loop_id].vector.copy()
                normal_error = max(normal_error, (n - expected_n).length)
                n_ue = Vector((n.x, -n.y, n.z))
                if abs(endpoint(p)) < 0.0001:
                    normals_start.append(Vector((c * n_ue.x - s * n_ue.y, s * n_ue.x + c * n_ue.y, n_ue.z)))
                if abs(endpoint(p) - 30) < 0.0001:
                    normals_end.append(n_ue)
    assert normals_start and normals_end
    seam_normal = max(min((n - m).length for m in normals_end) for n in normals_start)
    assert normal_error < 0.001 and seam_normal < 0.001, (normal_error, seam_normal)
    return {"bounds_ue_cm": bounds, "reference_generator_max_error_cm": error,
            "two_instance_seam_error_cm": seam, "radial_normal_max_vector_error": normal_error,
            "seam_normal_max_vector_error": seam_normal}


def inspect_scene(roundtrip=False):
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    assert len(meshes) == 11
    wall = bpy.data.objects[NAME]
    colliders = [bpy.data.objects["UCX_" + NAME + "_%02d" % i] for i in range(10)]
    for obj in meshes:
        assert max(abs(v) for v in obj.location) < 1e-6
        assert max(abs(v) for v in obj.rotation_euler) < 1e-6
        assert max(abs(v - 1) for v in obj.scale) < 1e-6
    data = topology(wall)
    assert data["triangles"] == 84
    assert [s.material.name for s in wall.material_slots] == ["Ivory"]
    assert len(wall.data.uv_layers) == 1
    uv = wall.data.uv_layers.active
    for tri in wall.data.loop_triangles:
        a, b, c = [uv.data[i].uv for i in tri.loops]
        area2 = abs((b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x))
        assert area2 > 1e-9
        assert all(-1e-6 <= x <= 1 + 1e-6 for p in (a, b, c) for x in p)
    data.update(check_geometry(wall))
    collision = []
    for i, obj in enumerate(colliders):
        item = topology(obj)
        assert item["triangles"] == 12 and item["vertices"] == 8
        expected, _, _ = geometry(3 * i, 3 * (i + 1), 1)
        for p in expected:
            assert min((v.co - Vector(p)).length for v in obj.data.vertices) < 1e-6
        for poly in obj.data.polygons:
            origin = obj.data.vertices[poly.vertices[0]].co
            assert max(poly.normal.dot(v.co - origin) for v in obj.data.vertices) < 1e-6, "UCX must be convex"
        collision.append({"name": obj.name, **item})
    volume_error = abs(sum(c["volume_m3"] for c in collision) - data["volume_m3"])
    assert volume_error < 1e-6
    data["collision"] = collision
    data["collision_volume_sum_error_m3"] = volume_error
    data["uv_triangles_finite_nondegenerate_in_unit_square"] = True
    data["closed_consistent_outward_manifold"] = True
    data["roundtrip"] = roundtrip
    return data


def verify():
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    for name, digest in manifest["sha256"].items():
        assert sha(ROOT / name) == digest, "Handoff input changed: " + name
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    assert bpy.context.scene.unit_settings.system == "METRIC"
    assert bpy.context.scene.unit_settings.scale_length == 1
    assert not bpy.data.libraries
    assert not any(i.filepath for i in bpy.data.images if i.source == "FILE")
    source = inspect_scene()
    assert source["vertices"] == 44 and source["faces"] == 42
    obj = bpy.data.objects[NAME]
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
    evaluated.calc_loop_triangles()
    assert len(evaluated.loop_triangles) == 84
    assert all(len(p.vertices) == 3 for p in evaluated.polygons)
    obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh_clear()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if "io_scene_fbx" not in bpy.context.preferences.addons:
        bpy.ops.preferences.addon_enable(module="io_scene_fbx")
    assert bpy.ops.import_scene.fbx(filepath=str(FBX), use_custom_normals=True,
                                    use_anim=False, use_image_search=False) == {"FINISHED"}
    roundtrip = inspect_scene(roundtrip=True)
    result = {"status": "passed", "scope": "Blender source reopen and FBX Blender roundtrip only; not Unreal validation",
              "blender": bpy.app.version_string, "source": source, "fbx_roundtrip": roundtrip,
              "hashes_verified": manifest["sha256"], "unreal_import_performed": False}
    write_json("verification.json", result)
    manifest["status"] = "creator_ready"
    manifest["bounds_ue_cm"] = source["bounds_ue_cm"]
    manifest["bounds_blender_m"] = [[source["bounds_ue_cm"][0][0] / 100, -source["bounds_ue_cm"][1][1] / 100, 0],
                                    [source["bounds_ue_cm"][1][0] / 100, -source["bounds_ue_cm"][0][1] / 100, 2.8]]
    manifest["export"]["validation"] = "passed Blender roundtrip; Unreal import/reimport not performed"
    manifest["verification"] = {"file": "verification.json", "sha256": sha(ROOT / "verification.json")}
    write_json("manifest.json", manifest)
    print("CREATOR_VERIFY_OK", json.dumps({"source": {k: v for k, v in source.items() if k != "collision"},
                                            "fbx_roundtrip": {k: v for k, v in roundtrip.items() if k != "collision"}}))


def preview():
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    wall = bpy.data.objects[NAME]
    scene = bpy.context.scene
    second = wall.copy()
    second.data = wall.data
    scene.collection.objects.link(second)
    second.location = (JOIN_B[0] / 100, -JOIN_B[1] / 100, 0)
    second.rotation_euler.z = -ANGLE
    for obj, color in ((wall, (0.82, 0.78, 0.65, 1)), (second, (0.48, 0.65, 0.62, 1))):
        obj.color = color
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "OBJECT"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.background_type = "WORLD"
    scene.world.color = (0.055, 0.065, 0.08)
    camera_data = bpy.data.cameras.new("Preview_Camera")
    camera = bpy.data.objects.new("Preview_Camera", camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = 4.6
    camera.location = (5, 5, 4.1)
    camera.rotation_euler = (Vector((1.1, -0.35, 1.35)) - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.resolution_x = 1100
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    out = ROOT / "Previews"
    out.mkdir(exist_ok=True)
    scene.render.filepath = str(out / "two_modules.png")
    bpy.ops.render.render(write_still=True)
    # Preview-only duplication/camera are never saved into the delivered .blend.
    print("CREATOR_PREVIEW_OK")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["build", "verify", "preview"], required=True)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    {"build": build, "verify": verify, "preview": preview}[args.mode]()
