from pathlib import Path
import bpy,json,hashlib,sys,numpy as np
R=Path(__file__).resolve().parent;d=json.loads((R/'manifest.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if sys.argv[-1]=='build':
    assert sha(Path(d['input_source']))==d['input_sha256'];bpy.ops.wm.open_mainfile(filepath=d['input_source'])
    mats={}
    for family,v in d['colors'].items():
        m=bpy.data.materials['HE02_'+family].copy();m.name='HE03_'+family
        nodes=m.node_tree.nodes;links=m.node_tree.links;bs=nodes.get('Principled BSDF');old=bs.inputs['Base Color'].links[0].from_socket
        im=old.node.image;px=np.empty(len(im.pixels),dtype=np.float32);im.pixels.foreach_get(px);mean=px.reshape(-1,4)[:,:3].mean(axis=0);ratio=[float(t*.96/s) for t,s in zip(v['white'],mean)]
        d['colors'][family]['measured_linear_mean']=mean.tolist();d['colors'][family]['ratio']=ratio
        mul=nodes.new('ShaderNodeVectorMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=ratio;links.new(old,mul.inputs[0]);links.new(mul.outputs['Vector'],bs.inputs['Base Color']);mats[family]=m
    for o in bpy.data.collections['A_Schlicht'].objects:
        if o.type!='MESH':continue
        for i,m in enumerate(o.data.materials):
            family=m.name.removeprefix('HEWS01_');o.data.materials[i]=mats.get(family) or bpy.data.materials['HE02_'+family]
    for o in bpy.data.objects:
        if o.type=='FONT' and o.data.body=='VORHER':o.data.body='WEISS / MIT DETAILS'
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(R/d['source']))
    d['source_sha256']=sha(R/d['source']);(R/'manifest.json').write_text(json.dumps(d,indent=2))
else:
    bpy.ops.wm.open_mainfile(filepath=str(R/d['source']))
    proofs=[]
    for o in bpy.data.collections['A_Schlicht'].objects:
        if o.type!='MESH':continue
        other=bpy.data.objects[o.name.replace('HE01_','HE02_')]
        assert [tuple(v.co) for v in o.data.vertices]==[tuple(v.co) for v in other.data.vertices]
        assert [tuple(p.vertices) for p in o.data.polygons]==[tuple(p.vertices) for p in other.data.polygons]
        assert [tuple(u.uv) for u in o.data.uv_layers.active.data]==[tuple(u.uv) for u in other.data.uv_layers.active.data]
        proofs.append(o.name)
    assert len(proofs)==6
    used={n.image for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
    assert all(Path(bpy.path.abspath(i.filepath)).exists() for i in used)
    (R/'Evidence/blender_verification.json').write_text(json.dumps(dict(status='passed',source_reopened=True,geometry_uv_unchanged=proofs,relative_textures_resolved=True)))
    sc=bpy.context.scene;sc.camera=bpy.data.objects['01_Aussen_Vergleich'];sc.cycles.samples=32;sc.render.filepath=str(R/'Previews/Blender_Weissvergleich.png');bpy.ops.render.render(write_still=True)
