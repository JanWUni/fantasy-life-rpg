import json
AS='editor_toolset.toolsets.asset.AssetTools';MT='editor_toolset.toolsets.material.MaterialTools';TX='editor_toolset.toolsets.texture.TextureTools'
OB='editor_toolset.toolsets.object.ObjectTools';BP='editor_toolset.toolsets.blueprint.BlueprintTools';AC='editor_toolset.toolsets.actor.ActorTools'
ROOT='E:/Business/fantasy-rpg-refiner/AssetSources/Architecture/EC_HighCultureCity/StreetStudy01/Refiner/HighElfWallStudy_01/MaterialStudy_02/'
MAT='/Game/Art/Materials/HighElfWallStudy02';TEX='/Game/Art/Textures/HighElfWallStudy02';ARCH='/Game/Art/Architecture/HighElfWallStudy02'
def tool(g,n,**a):return execute_tool(g+'.'+n,json.dumps(a)).get('returnValue')
def ref(p):return dict(refPath=p+'.'+p.rsplit('/',1)[-1])
def props(o,**v):
    tool(OB,'list_properties',instance=o);assert tool(OB,'set_properties',instance=o,values=json.dumps(v))
def node(m,k,x,y,**v):
    n=tool(MT,'add_expression',material_or_function=m,expression_class=dict(refPath='/Script/Engine.MaterialExpression'+k),x=x,y=y)
    if v:props(n,**v)
    return n
def connect(a,b,pin,out=''):
    assert pin in tool(MT,'get_expression_input_names',expression=b),pin
    tool(MT,'connect_expressions',from_expression=a,from_output_name=out,to_expression=b,to_input_name=pin)
def output(n,p,out=''):tool(MT,'connect_to_output',expression=n,output_name=out,material_property='MP_'+p)
def run():
    assert tool('editor_toolset.toolsets.scene.SceneTools','get_current_level')=='/Game/Prototype/Maps/Lvl_AssetLab'
    assert not tool('EditorToolset.EditorAppToolset','IsPIERunning')
    with open(ROOT+'manifest.json','r') as f:data=json.load(f)
    saved=[];materials={};glassproof={}
    for family,values in data['material_values'].items():
        path=MAT+'/M_HE02_'+family;assert not tool(AS,'exists',path=path)
        mat=tool(MT,'create_material',folder_path=MAT,asset_name='M_HE02_'+family)
        uv=node(mat,'TextureCoordinate',-1200,-300);scale=node(mat,'Constant',-1200,-200,r=values['tile_scale']);mul=node(mat,'Multiply',-1000,-300);connect(uv,mul,'A');connect(scale,mul,'B')
        sampled={}
        for channel,sampler,y in [('BaseColor','Color',0),('Roughness','Masks',300),('Normal','Normal',600)]:
            if family=='ClearGlass' and channel=='BaseColor':continue
            name='T_HE02_'+family+'_'+channel;tp=TEX+'/'+name;assert not tool(AS,'exists',path=tp)
            tool(TX,'import_file',folder_path=TEX,asset_name=name,source_file=ROOT+'Textures/'+name+'.png');t=ref(tp);saved.append(tp)
            if channel=='Normal':props(t,sRGB=False,compressionSettings='TC_Normalmap',bFlipGreenChannel=True)
            elif channel=='Roughness':props(t,sRGB=False,compressionSettings='TC_Masks')
            n=node(mat,'TextureSample',-800,y,texture=t,samplerType='SAMPLERTYPE_'+sampler);connect(mul,n,'UVs');sampled[channel]=n
            if family!='ClearGlass':output(n,channel,'R' if channel=='Roughness' else 'RGB')
        if family=='ClearGlass':
            props(mat,blendMode='BLEND_TranslucentColoredTransmittance',translucencyLightingMode='TLM_SurfacePerPixelLighting')
            slab=node(mat,'SubstrateSlabBSDF',-200,0,subSurfaceType='MSS_SimpleVolume');pins=tool(MT,'get_expression_input_names',expression=slab)
            black=node(mat,'Constant3Vector',-600,-100,constant=dict(r=0,g=0,b=0,a=1));connect(black,slab,'Diffuse Albedo')
            f0=node(mat,'Constant3Vector',-600,0,constant=dict(r=.045,g=.045,b=.045,a=1));connect(f0,slab,'F0')
            connect(sampled['Roughness'],slab,'Roughness','R');normalpin=next(p for p in pins if p=='Normal');connect(sampled['Normal'],slab,normalpin,'RGB')
            tint=node(mat,'Constant3Vector',-1000,900,constant=dict(r=.91,g=.96,b=.975,a=1));mfp=node(mat,'SubstrateTransmittanceToMFP',-600,900)
            inp=tool(MT,'get_expression_input_names',expression=mfp);outs=tool(MT,'get_expression_output_names',expression=mfp);connect(tint,mfp,inp[0]);connect(mfp,slab,next(p for p in pins if 'MFP' in p and 'Scale' not in p),outs[0]);output(slab,'FrontMaterial')
            glassproof=dict(pins=pins,F0=.045,transmittance=[.91,.96,.975],roughness_texture=True,normal_texture=True,shader='Substrate SimpleVolume')
        else:
            n=node(mat,'Constant',-400,900,r=values['metal']);output(n,'Metallic')
            n=node(mat,'Constant',-400,1050,r=.5);output(n,'Specular')
        tool(MT,'layout_expressions',material_or_function=mat);tool(MT,'recompile',material_or_function=mat);materials[family]=mat;saved.append(path)
    name='BP_HE02_WindowWall_A';path=ARCH+'/Blueprints/'+name;assert not tool(AS,'exists',path=path)
    bp=tool(BP,'create',folder_path=ARCH+'/Blueprints',asset_name=name,asset_type=dict(refPath='/Script/Engine.Actor'))
    for part in ['WallCore','StoneCarving','GoldInlay','BlueInlay','WindowFrame','ClearGlass']:
        meshpath='/Game/Art/Architecture/HighElfWallStudy01/Meshes/SM_HE01_A_'+part
        c=tool(AC,'add_component',owner=bp,component_type=dict(refPath='/Script/Engine.StaticMeshComponent'),name=part)
        slots=tool('editor_toolset.toolsets.static_mesh.StaticMeshTools','get_material_slots',mesh=ref(meshpath));coll=part in ['WallCore','ClearGlass']
        props(c,staticMesh=ref(meshpath),overrideMaterials=[materials[s.replace('HEWS01_','')] for s in slots],mobility='Static',castShadow=part!='ClearGlass',bodyInstance=dict(collisionProfileName='BlockAll' if coll else 'NoCollision',collisionEnabled='QueryAndPhysics' if coll else 'NoCollision'))
    tool(BP,'compile_blueprint',blueprint=bp,warnings_as_errors=True);saved.append(path)
    assert tool(AS,'save_assets',asset_paths=saved)
    return dict(status='passed',saved=saved,materials=materials,blueprint=path,glass=glassproof)
