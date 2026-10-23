"""Material-only quality comparison on identical existing wall geometry."""
from pathlib import Path
import sys,json,math,hashlib
sys.dont_write_bytecode=True
import bpy,numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parent;PARENT=ROOT.parent;REPO=ROOT.parents[6]
sys.path.insert(0,str(PARENT));import build_study as s
g=s.g
def write(n,d):(ROOT/n).write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def sha(p):return s.sha(p)
def noise(n,f,rng):return g.noise(n,f,rng)
def texture(name,pixels,space):
    n=pixels.shape[0];rgba=np.ones((n,n,4),np.float32);rgba[:,:,:3]=np.clip(pixels[:,:,None] if pixels.ndim==2 else pixels,0,1)
    im=bpy.data.images.new(name,n,n,alpha=False);im.colorspace_settings.name=space;im.pixels.foreach_set(rgba.ravel());im.file_format='PNG';im.filepath_raw=str(ROOT/'Textures'/(name+'.png'));im.save();im.filepath='//Textures/'+name+'.png';return im
def build():
    input_manifest=json.loads((PARENT/'manifest.json').read_text());assert sha(PARENT/input_manifest['source'])==input_manifest['source_sha256']
    if not (ROOT/'Evidence/files_before.json').exists():
        write('Evidence/files_before.json',{p.relative_to(REPO).as_posix():sha(p) for f in ['AssetSources','Content','Config','Source','Tools','docs'] for p in (REPO/f).rglob('*') if p.is_file() and not p.is_relative_to(ROOT) and p.suffix not in ['.blend1','.pyc']})
    bpy.ops.wm.open_mainfile(filepath=str(PARENT/input_manifest['source']))
    rng=np.random.default_rng(63027);materials={};stats={};definitions={}
    for family in ['Ivory','CarvedStone','RecessStone','Gold','Azure','ClearGlass']:
        n=2048 if family in ['Ivory','CarvedStone','RecessStone'] else 1024
        span=3.0 if family=='Ivory' else 1.0
        u,v=np.meshgrid(np.arange(n,dtype=np.float32)/n,np.arange(n,dtype=np.float32)/n)
        coarse=noise(n,4,rng);medium=noise(n,34,rng);fine=noise(n,256,rng);grit=noise(n,768 if n==2048 else 384,rng)
        if family in ['Ivory','CarvedStone','RecessStone']:
            veins=np.exp(-((np.sin(2*np.pi*(u*3+v*2+coarse*.5+medium*.08)))/.11)**2)
            pores=np.maximum(0,-grit-.22)
            base=np.array({'Ivory':[.55,.515,.44],'CarvedStone':[.64,.605,.535],'RecessStone':[.39,.405,.38]}[family])
            tone=1+.20*coarse+.10*medium+.035*fine-.06*veins
            h=.00055*medium+.0002*fine+.00030*grit-pores*.0012
            rough=.63+.18*medium+.10*fine+.08*pores
            if family=='Ivory':
                # 75 x 50 cm fitted stones; 3 mm joints. The pattern repeats every three metres.
                rows=np.floor(v*6).astype(int);xx=(u*4+(rows%2)*.5)%1;zz=(v*6)%1
                dx=np.minimum(xx,1-xx)*.75;dz=np.minimum(zz,1-zz)*.50
                dist=np.minimum(dx,dz)
                joint=np.clip(1-dist/.0020,0,1);shoulder=np.clip(1-dist/.007,0,1)
                blocks=rng.uniform(-.065,.065,(6,4));ix=np.floor(u*4+(rows%2)*.5).astype(int)%4
                tone+=blocks[rows,ix];tone*=1-.22*joint-.035*shoulder
                h-=.0016*joint+.00045*shoulder;rough+=.12*joint
            else:
                # Faint dressed stone tool marks, no fake masonry through carved profiles.
                strokes=np.sin(2*np.pi*(u*180+coarse*.18))
                h+=.00007*strokes;rough+=.015*strokes
            color=base[None,None,:]*tone[:,:,None];metal=0
        elif family=='Gold':
            scratches=np.maximum(0,np.sin(2*np.pi*(u*280+coarse*.2))-.92)
            h=.000035*medium+.000012*fine-.000035*scratches
            color=np.array([.59,.365,.105])[None,None,:]*(1+.12*coarse[:,:,None]+.06*medium[:,:,None])
            rough=.29+.14*medium+.07*fine+.05*scratches;metal=.92
        elif family=='Azure':
            h=.000025*medium;rough=.19+.08*medium
            color=np.array([.045,.30,.41])[None,None,:]*(1+.15*coarse[:,:,None]);metal=.15
        else:
            # Nearly flat rolled glass: small waviness affects reflections, not the aperture geometry.
            h=.00011*noise(n,12,rng)+.000008*fine;rough=.055+.05*medium+.025*np.maximum(0,coarse)
            color=np.zeros((n,n,3),np.float32)+np.array([.91,.96,.975]);metal=0
        ddx=(np.roll(h,-1,1)-np.roll(h,1,1))*n/(2*span);ddy=(np.roll(h,-1,0)-np.roll(h,1,0))*n/(2*span)
        normal=np.stack([-ddx,-ddy,np.ones_like(h)],-1);normal/=np.linalg.norm(normal,axis=-1)[:,:,None]
        images={c:texture('T_HE02_'+family+'_'+c,p,space) for c,p,space in [('BaseColor',color,'sRGB'),('Roughness',np.clip(rough,.02,.95),'Non-Color'),('Normal',normal*.5+.5,'Non-Color')]}
        mat=bpy.data.materials.new('HE02_'+family);mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Metallic'].default_value=metal
        nodes=mat.node_tree.nodes;links=mat.node_tree.links;uv=nodes.new('ShaderNodeTexCoord');scale=nodes.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs['Scale'].default_value=1/span;links.new(uv.outputs['UV'],scale.inputs[0])
        for channel,im in images.items():
            t=nodes.new('ShaderNodeTexImage');t.image=im;links.new(scale.outputs['Vector'],t.inputs['Vector'])
            if channel=='Normal':
                nm=nodes.new('ShaderNodeNormalMap');links.new(t.outputs['Color'],nm.inputs['Color']);links.new(nm.outputs['Normal'],bs.inputs['Normal'])
            elif family!='ClearGlass' or channel=='Roughness':links.new(t.outputs['Color'],bs.inputs['Base Color' if channel=='BaseColor' else 'Roughness'])
        if family=='ClearGlass':
            bs.inputs['Base Color'].default_value=(.91,.96,.975,1);bs.inputs['Transmission Weight'].default_value=1;bs.inputs['IOR'].default_value=1.52
            lp=nodes.new('ShaderNodeLightPath');tr=nodes.new('ShaderNodeBsdfTransparent');mix=nodes.new('ShaderNodeMixShader');links.new(lp.outputs['Is Shadow Ray'],mix.inputs[0]);links.new(bs.outputs[0],mix.inputs[1]);links.new(tr.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],nodes.get('Material Output').inputs['Surface'])
        materials[family]=mat
        stats[family]=dict(size=n,tile_span_m=span,base_color_min=color.min(axis=(0,1)).tolist(),base_color_max=color.max(axis=(0,1)).tolist(),roughness_min=float(rough.min()),roughness_max=float(rough.max()),normal_xy_rms=float(np.sqrt(np.mean(normal[:,:,:2]**2))))
        definitions[family]=dict(metal=metal,tile_scale=1/span)
    # Existing left A remains the reference. Replace the display B in this own source with a copy of A.
    col=bpy.data.collections['B_Prachtvoll'];col.name='A_Material_Detail'
    for o in list(col.objects):bpy.data.objects.remove(o,do_unlink=True)
    changed={}
    for old in list(bpy.data.collections['A_Schlicht'].objects):
        o=old.copy();o.data=old.data.copy();col.objects.link(o);o.name=old.name.replace('HE01_A_','HE02_A_');o.location.x=4.2
        for i,m in enumerate(o.data.materials):o.data.materials[i]=materials[m.name.replace('HEWS01_','')]
        changed[o.name]=g.audit(o)
    for o in bpy.data.objects:
        if o.type=='FONT':
            if o.data.body.startswith('A  /'):o.data.body='VORHER'
            elif o.data.body.startswith('B  /'):o.data.body='MATERIALSTUDIE'
            elif 'Spitzboegen' in o.data.body:o.data.body='Werkstein / Gold / klares Glas'
    # Pack prior procedural source has no file dependencies. New textures are relative beside the file.
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'HighElf_MaterialComparison_02.blend'),relative_remap=False)
    write('manifest.json',dict(status='draft',accepted=False,source='HighElf_MaterialComparison_02.blend',source_sha256=sha(ROOT/'HighElf_MaterialComparison_02.blend'),input_sha256=input_manifest['source_sha256'],assets=changed,material_values=definitions,texture_statistics=stats,scope='Material-only A-wall quality comparison. All existing mesh assets unchanged. New material overrides on one new Blueprint.',glass=dict(F0=.045,transmittance=[.91,.96,.975],roughness='texture .03-.08',normal='subtle reflection waviness',shadow='disabled so daylight enters; no opaque filler'),pending=['Unreal material and glass visual review','Production performance and clean reload']))
    print('MATERIAL_STUDY_READY')
def verify():
    d=json.loads((ROOT/'manifest.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(ROOT/d['source']))
    result={}
    for n,a in d['assets'].items():
        o=bpy.data.objects[n];old=bpy.data.objects[n.replace('HE02_','HE01_')]
        assert [tuple(v.co) for v in o.data.vertices]==[tuple(v.co) for v in old.data.vertices]
        assert [tuple(p.vertices) for p in o.data.polygons]==[tuple(p.vertices) for p in old.data.polygons]
        assert [tuple(u.uv) for u in o.data.uv_layers.active.data]==[tuple(u.uv) for u in old.data.uv_layers.active.data]
        assert g.audit(o)==a;result[n]=dict(geometry_and_uv_unchanged=True,triangles=a['triangles'])
    used={n.image for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
    assert all(Path(bpy.path.abspath(i.filepath)).exists() for i in used)
    write('Evidence/blender_verification.json',dict(status='passed',source_reopened=True,all_textures_resolved=True,assets=result));print('MATERIAL_VERIFY_PASSED')
def render():
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'HighElf_MaterialComparison_02.blend'));sc=bpy.context.scene
    sc.camera=bpy.data.objects['01_Aussen_Vergleich'];sc.cycles.samples=48;sc.render.filepath=str(ROOT/'Previews/Blender_Materialvergleich.png');bpy.ops.render.render(write_still=True)
if __name__=='__main__':{'build':build,'verify':verify,'render':render}[sys.argv[-1]]()
