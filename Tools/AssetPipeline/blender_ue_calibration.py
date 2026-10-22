"""Blender-only calibration source/export. Never imports or edits Unreal assets.

Run with Blender --background --factory-startup --python this_file -- --root DIR.
The 100 x 60 x 40 cm positive-axis specimen has three stable material slots,
one UV channel and three named convex collision boxes. No cultural styling.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import bpy

NAME = "SM_Calibration_Axes_100x60x40"
SLOTS = ["Cal_X", "Cal_Y", "Cal_Z"]
FACES = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
         (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]


def vertices(lo, hi):
    x, y, z = lo
    a, b, c = hi
    return [(x, y, z), (a, y, z), (a, b, z), (x, b, z),
            (x, y, c), (a, y, c), (a, b, c), (x, b, c)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--revision", type=int, choices=[1, 2], default=1)
    parser.add_argument("--forward", default="-Y")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    root = Path(args.root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.data.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = "METERS"
    width = 0.10 if args.revision == 1 else 0.12
    boxes = [((0, 0, 0), (1, width, 0.1)),
             ((0, 0.1, 0), (0.1, 0.6, 0.1)),
             ((0, 0, 0.1), (0.1, 0.1, 0.4))]
    verts, faces = [], []
    for lo, hi in boxes:
        offset = len(verts)
        # Blender RH -> Unreal LH: author -Y for the Unreal +Y/inward axis.
        verts.extend([(x, -y, z) for x, y, z in vertices(lo, hi)])
        faces.extend([tuple(offset + i for i in reversed(face)) for face in FACES])
    mesh = bpy.data.meshes.new(NAME)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(NAME, mesh)
    scene.collection.objects.link(obj)
    for name, color in zip(SLOTS, [(0.8, 0.03, 0.02, 1), (0.03, 0.7, 0.05, 1), (0.02, 0.08, 0.8, 1)]):
        mat = bpy.data.materials.new(name)
        mat.diffuse_color = color
        mesh.materials.append(mat)
    uv = mesh.uv_layers.new(name="UVMap")
    for index, poly in enumerate(mesh.polygons):
        poly.material_index = index // 6
        u, v = (index % 6) / 6, (index // 6) / 3
        for loop_index, corner in zip(poly.loop_indices, [(0, 0), (1, 0), (1, 1), (0, 1)]):
            uv.data[loop_index].uv = (u + (0.05 + 0.9 * corner[0]) / 6,
                                     v + (0.05 + 0.9 * corner[1]) / 3)
    for index, (lo, hi) in enumerate(boxes):
        cm = bpy.data.meshes.new("Collision_%02d" % index)
        cm.from_pydata([(x, -y, z) for x, y, z in vertices(lo, hi)], [],
                      [tuple(reversed(face)) for face in FACES])
        cm.update()
        co = bpy.data.objects.new("UCX_" + NAME + "_%02d" % index, cm)
        scene.collection.objects.link(co)
        co.display_type = "WIRE"
        co.hide_render = True
    bpy.context.view_layer.objects.active = obj
    for item in scene.objects:
        item.select_set(True)
        assert tuple(item.scale) == (1, 1, 1)
        assert tuple(item.location) == (0, 0, 0)
    bpy.ops.wm.save_as_mainfile(filepath=str(root / (NAME + ".blend")))
    if "io_scene_fbx" not in bpy.context.preferences.addons:
        bpy.ops.preferences.addon_enable(module="io_scene_fbx")
    settings = dict(use_selection=True, object_types={"MESH"}, global_scale=1.0,
                    apply_unit_scale=True, apply_scale_options="FBX_SCALE_NONE",
                    axis_forward=args.forward, axis_up="Z", use_space_transform=True,
                    bake_space_transform=False, use_mesh_modifiers=True,
                    mesh_smooth_type="FACE", use_triangles=True, use_tspace=True,
                    bake_anim=False, add_leaf_bones=False, path_mode="RELATIVE",
                    embed_textures=False)
    path = root / (NAME + ".fbx")
    bpy.ops.export_scene.fbx(filepath=str(path), **settings)
    settings["object_types"] = sorted(settings["object_types"])
    manifest = dict(name=NAME, revision=args.revision, blender=bpy.app.version_string,
                    blender_build=bpy.app.build_hash.decode(), units="meters",
                    bounds_cm=[[0, 0, 0], [100, 60, 40]], pivot_cm=[0, 0, 0],
                    scale=[1, 1, 1], material_slots=SLOTS, triangles=36, uv_channels=1,
                    logical_ue_axis_box_bounds_m=boxes,
                    blender_to_unreal_cm="(100*x, -100*y, 100*z)",
                    collision_hulls=3, export_settings=settings,
                    fbx_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("CALIBRATION_EXPORT_OK " + json.dumps(manifest))


if __name__ == "__main__":
    main()
