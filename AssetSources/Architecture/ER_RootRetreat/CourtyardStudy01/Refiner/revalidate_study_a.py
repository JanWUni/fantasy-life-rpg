"""Read-only repeat of A source and all FBX checks; report only into B/Evidence."""
from pathlib import Path
import importlib.util,json,hashlib,sys,bpy
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[4]
A=REPO/'AssetSources/Architecture/EC_HighCultureCity/StreetStudy01/Refiner'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
sealed={}
for line in (A/'SHA256SUMS').read_text().splitlines():
    digest,name=line.split(maxsplit=1);assert sha(A/name)==digest,name;sealed[name]=digest
seal_sha=sha(A/'SHA256SUMS')
spec=importlib.util.spec_from_file_location('refiner_a',A/'refine_study.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
m=r.manifest();assert m['status']=='review_ready' and sha(A/m['source_blend'])==m['source_blend_sha256']
bpy.ops.wm.open_mainfile(filepath=str(A/m['source_blend']))
baseline=json.loads((A/'Evidence/before.json').read_text())
for name,digest in baseline['collider_fingerprints'].items():assert r.fingerprint(bpy.data.objects[name].data)==digest
for name,matrix in baseline['instance_matrices'].items():assert list(sum((list(row) for row in bpy.data.objects[name].matrix_world),[]))==matrix
source={e['asset_name']:r.assert_clean(bpy.data.objects[e['asset_name']]) for e in m['exports']}
roundtrips={}
for e in m['exports']:
    assert sha(A/e['path'])==e['sha256']
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.preferences.addon_enable(module='io_scene_fbx')
    bpy.ops.import_scene.fbx(filepath=str(A/e['path']),use_anim=False,use_image_search=False,use_custom_normals=True)
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(meshes)==1+len(e['collision_names'])
    obj=bpy.data.objects[e['asset_name']];stats=r.assert_clean(obj);expected=source[obj.name]
    assert stats['triangles']==expected['triangles'] and stats['material_slots']==expected['material_slots']
    error=max(abs(stats['bounds_blender_m'][i][k]-expected['bounds_blender_m'][i][k]) for i in range(2) for k in range(3));assert error<1e-4
    assert max(abs(v) for v in obj.location)<1e-6 and max(abs(s-1) for s in obj.scale)<1e-6
    for name in e['collision_names']:
        co=bpy.data.objects[name];assert r.c.stats(co)['nonmanifold_edges']==0
        for poly in co.data.polygons:
            origin=co.data.vertices[poly.vertices[0]].co
            assert max(poly.normal.dot(v.co-origin) for v in co.data.vertices)<1e-4
    roundtrips[obj.name]=dict(status='passed',stats=stats,bounds_error_m=error,ucx=len(e['collision_names']))
for name,digest in sealed.items():assert sha(A/name)==digest
assert sha(A/'SHA256SUMS')==seal_sha
(ROOT/'Evidence/study_a_revalidation.json').write_text(json.dumps(dict(status='passed',source_reopened=True,
    source_assets=source,fbx_roundtrips=roundtrips,all_fbx_reimported=True,study_a_files_unchanged=len(sealed),
    study_a_checksum_file_unchanged=True,scope='Fresh Blender source and all 21 FBX/UCX checks; no writes to A or Unreal'),indent=2)+'\n',encoding='utf-8',newline='\n')
print('STUDY_A_READ_ONLY_REVALIDATION_PASSED',len(roundtrips))
