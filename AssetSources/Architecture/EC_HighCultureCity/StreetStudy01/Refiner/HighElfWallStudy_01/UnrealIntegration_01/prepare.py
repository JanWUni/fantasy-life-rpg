"""Own export/bake copy of the approved wall study. Never saves the input source."""
from pathlib import Path
import sys,json,hashlib,shutil
sys.dont_write_bytecode=True
import bpy,bmesh
ROOT=Path(__file__).resolve().parent;PARENT=ROOT.parent;REPO=ROOT.parents[6]
sys.path.insert(0,str(PARENT));import build_study as s
g=s.g
def sha(p):return s.sha(p)
def write(p,d):(ROOT/p).write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def build():
    manifest=json.loads((PARENT/'manifest.json').read_text());assert sha(PARENT/manifest['source'])==manifest['source_sha256']
    if not (ROOT/'Evidence/files_before.json').exists():
        before={p.relative_to(REPO).as_posix():sha(p) for f in ['AssetSources','Content','Config','Source','Tools','docs'] for p in (REPO/f).rglob('*') if p.is_file() and not p.is_relative_to(ROOT) and p.suffix not in ['.pyc','.blend1']}
        write('Evidence/files_before.json',before)
        backup=REPO/'Saved/HighElfWallStudy01/Before/Lvl_AssetLab.umap';backup.parent.mkdir(parents=True,exist_ok=True)
        assert not backup.exists();shutil.copy2(REPO/'Content/Prototype/Maps/Lvl_AssetLab.umap',backup)
    bpy.ops.wm.open_mainfile(filepath=str(PARENT/manifest['source']))
    chosen=['HE01_A_WallCore','HE01_A_WindowFrame','HE01_A_ClearGlass']+['HE01_'+v+'_'+part for v in ['A','B'] for part in ['StoneCarving','GoldInlay','BlueInlay']]
    keep={bpy.data.objects[n] for n in chosen}
    for o in list(bpy.data.objects):
        if o not in keep:bpy.data.objects.remove(o,do_unlink=True)
    bpy.context.scene.name='Export_Library';bpy.context.scene.unit_settings.system='METRIC'
    data={};mapping={}
    for old in chosen:
        o=bpy.data.objects[old];o.location=(0,0,0);name='SM_'+old;o.name=name;mapping[old]=name
        collisions=[]
        kind='Core' if old.endswith('WallCore') else 'Glass' if old.endswith('ClearGlass') else 'Frame' if old.endswith('WindowFrame') else 'Decor'
        if kind in ['Core','Glass']:
            # Every disconnected piece of this known convex core is a separate hull.
            adjacent={v.index:set() for v in o.data.vertices}
            for e in o.data.edges:a,b=e.vertices;adjacent[a].add(b);adjacent[b].add(a)
            remaining=set(adjacent)
            while remaining:
                todo=[remaining.pop()];ids=set(todo)
                while todo:
                    v=todo.pop()
                    for w in adjacent[v]&remaining:remaining.remove(w);ids.add(w);todo.append(w)
                ids=sorted(ids);lookup={v:i for i,v in enumerate(ids)}
                mesh=bpy.data.meshes.new('Hull');mesh.from_pydata([o.data.vertices[i].co for i in ids],[],[[lookup[i] for i in p.vertices] for p in o.data.polygons if p.vertices[0] in lookup]);mesh.update()
                c=bpy.data.objects.new('UCX_'+name+'_%02d'%len(collisions),mesh);bpy.context.scene.collection.objects.link(c);c.hide_render=True;collisions.append(c)
        bpy.ops.object.select_all(action='DESELECT')
        for x in [o]+collisions:x.hide_set(False);x.select_set(True)
        bpy.context.view_layer.objects.active=o
        options=dict(g.PROFILE['export_settings']);options['object_types']=set(options['object_types'])
        bpy.ops.export_scene.fbx(filepath=str(ROOT/'Exports'/(name+'.fbx')),**options)
        for x in collisions:x.hide_set(True)
        data[name]=dict(**g.audit(o),kind=kind,ucx_hulls=len(collisions),fbx_sha256=sha(ROOT/'Exports'/(name+'.fbx')))
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'HighElf_Export_01.blend'))
    write('manifest.json',dict(status='export_prepared',accepted=False,source_sha256=manifest['source_sha256'],export_source='HighElf_Export_01.blend',assets=data,mapping=mapping,profile=g.PROFILE,
        material_families=['Ivory','CarvedStone','RecessStone','Gold','Azure','ClearGlass'],material_values={
        'Ivory':dict(color=[.73,.70,.62],rough=.57,metal=0),'CarvedStone':dict(color=[.84,.82,.74],rough=.44,metal=0),'RecessStone':dict(color=[.49,.53,.53],rough=.61,metal=0),
        'Gold':dict(color=[.63,.41,.14],rough=.28,metal=.83),'Azure':dict(color=[.055,.36,.49],rough=.22,metal=.25)},
        scope='Own Unreal comparison assets; unchanged approved source geometry',texture_policy='1 metre procedural material swatches baked to reusable 1024px UV0 tiles; exact palette and roughness ranges, approximate 2D representation of 3D procedural noise'))
    print('EXPORT_READY',len(data))
def bake():
    bpy.ops.wm.open_mainfile(filepath=str(PARENT/'HighElf_WallVariants_01.blend'))
    for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=4
    bpy.ops.mesh.primitive_plane_add(size=1);plane=bpy.context.object;plane.name='MaterialSwatch'
    evidence={}
    for family in ['Ivory','CarvedStone','RecessStone','Gold','Azure']:
        mat=bpy.data.materials['HEWS01_'+family];plane.data.materials.clear();plane.data.materials.append(mat)
        nodes=mat.node_tree.nodes;links=mat.node_tree.links;bs=nodes.get('Principled BSDF');out=nodes.get('Material Output')
        emission=nodes.new('ShaderNodeEmission');emission.inputs['Strength'].default_value=1
        target=nodes.new('ShaderNodeTexImage');nodes.active=target
        values={}
        for channel in ['BaseColor','Roughness','Normal']:
            name='T_HE01_'+family+'_'+channel;im=bpy.data.images.new(name,width=1024,height=1024,alpha=False)
            im.colorspace_settings.name='sRGB' if channel=='BaseColor' else 'Non-Color';target.image=im
            if channel=='Normal':links.new(bs.outputs['BSDF'],out.inputs['Surface']);typ='NORMAL'
            else:
                inp=bs.inputs['Base Color' if channel=='BaseColor' else 'Roughness'];assert inp.is_linked
                links.new(inp.links[0].from_socket,emission.inputs['Color']);links.new(emission.outputs[0],out.inputs['Surface']);typ='EMIT'
            bpy.ops.object.bake(type=typ,margin=4,use_clear=True)
            im.filepath_raw=str(ROOT/'Textures'/(name+'.png'));im.file_format='PNG';im.save();values[channel]=dict(sha256=sha(ROOT/'Textures'/(name+'.png')),width=1024,height=1024)
        links.new(bs.outputs[0],out.inputs['Surface']);evidence[family]=values
    write('Evidence/material_bakes.json',dict(status='passed',bakes=evidence,method='Cycles EMIT for BaseColor/Roughness; NORMAL for procedural micro-bump; XY-plane 1m tile'))
    print('MATERIAL_BAKES_READY')
def verify():
    d=json.loads((ROOT/'manifest.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(ROOT/d['export_source']))
    for n,a in d['assets'].items():assert g.audit(bpy.data.objects[n])=={k:a[k] for k in g.audit(bpy.data.objects[n])}
    results={}
    for n,a in d['assets'].items():
        bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(ROOT/'Exports'/(n+'.fbx')),use_anim=False,use_image_search=False)
        o=next(o for o in bpy.context.scene.objects if o.type=='MESH' and not o.name.startswith('UCX_'));v=g.audit(o)
        assert v['triangles']==a['triangles'] and v['slots']==a['slots'];assert v['degenerate_faces']==0 and v['nonmanifold_edges']==0
        err=max(abs(v['bounds_m'][i][j]-a['bounds_m'][i][j]) for i in range(2) for j in range(3));assert err<1e-5
        count=sum(o.name.startswith('UCX_') for o in bpy.context.scene.objects);assert count==a['ucx_hulls'];results[n]=dict(bounds_error_m=err,ucx_hulls=count,triangles=v['triangles'])
    write('Evidence/blender_verification.json',dict(status='passed',source_reopened=True,roundtrips=results));print('ROUNDTRIP_PASSED')
if __name__=='__main__':{'build':build,'bake':bake,'verify':verify}[sys.argv[-1]]()
