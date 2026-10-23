"""All supported imports, material graphs and reusable lamp BPs through editor MCP."""
import json
AS='editor_toolset.toolsets.asset.AssetTools';SM='editor_toolset.toolsets.static_mesh.StaticMeshTools'
TX='editor_toolset.toolsets.texture.TextureTools';MT='editor_toolset.toolsets.material.MaterialTools'
OB='editor_toolset.toolsets.object.ObjectTools';BP='editor_toolset.toolsets.blueprint.BlueprintTools';AC='editor_toolset.toolsets.actor.ActorTools'
SC='editor_toolset.toolsets.scene.SceneTools'
ROOT='E:/Business/fantasy-rpg-refiner/AssetSources/Architecture/EB_Blatthof_R255_R640/WallInner_R255_A30_H280/Refiner/HouseStudy_B01/Musterhaus_B03/'
MAT='/Game/Art/Materials/ElvenHouseB03';TEX='/Game/Art/Textures/ElvenHouseB03'
ARCH='/Game/Art/Architecture/ElvenHouseB03';FURN='/Game/Art/Furniture/ElvenHouseB03'
def tool(group,op,**args):
    r=execute_tool(group+'.'+op,json.dumps(args));return r.get('returnValue')
def ref(path):return dict(refPath=path+'.'+path.rsplit('/',1)[-1])
def props(o,**values):
    tool(OB,'list_properties',instance=o);assert tool(OB,'set_properties',instance=o,values=json.dumps(values))
def node(m,kind,x,y,**values):
    n=tool(MT,'add_expression',material_or_function=m,expression_class=dict(refPath='/Script/Engine.MaterialExpression'+kind),x=x,y=y)
    if values:props(n,**values)
    return n
def connect(a,b,pin,output=''):
    tool(MT,'connect_expressions',from_expression=a,from_output_name=output,to_expression=b,to_input_name=pin)
def out(n,p,pin=''):tool(MT,'connect_to_output',expression=n,output_name=pin,material_property='MP_'+p)
def path_for(name):return (ARCH if any(s in name for s in ['Interior','Ceiling']) else FURN)+'/Meshes/'+name
def run():
    assert tool(SC,'get_current_level')=='/Game/Prototype/Maps/Lvl_AssetLab'
    assert not tool('EditorToolset.EditorAppToolset','IsPIERunning')
    with open(ROOT+'manifest.json','r') as f:data=json.load(f)
    saved=[];materials={};meshes={};lamps={}
    for family in data['material_families']:
        path=MAT+'/M_EH03_'+family
        if tool(AS,'exists',path=path):
            mat=ref(path)
            for n in tool(MT,'get_expressions',material_or_function=mat):tool(MT,'delete_expression',material_or_function=mat,expression=n)
        else:mat=tool(MT,'create_material',folder_path=MAT,asset_name='M_EH03_'+family)
        materials[family]=mat;saved.append(path)
        samples={}
        for channel,sampler,y in [('BaseColor','Color',0),('Roughness','Masks',300),('Normal','Normal',600)]:
            if family in ['Iron','Bronze','Book','Flame'] and channel=='Normal':continue
            name='T_EH03_'+family+'_'+channel;tp=TEX+'/'+name
            if not tool(AS,'exists',path=tp):tool(TX,'import_file',folder_path=TEX,asset_name=name,source_file=ROOT+'Textures/'+name+'.png')
            t=ref(tp);saved.append(tp)
            if channel=='Normal':props(t,sRGB=False,compressionSettings='TC_Normalmap',bFlipGreenChannel=True)
            elif channel=='Roughness':props(t,sRGB=False,compressionSettings='TC_Masks')
            samples[channel]=node(mat,'TextureSample',-800,y,texture=t,samplerType='SAMPLERTYPE_'+sampler)
        tint=node(mat,'VectorParameter',-800,-250,parameterName='Tint',defaultValue=dict(r=1,g=1,b=1,a=1))
        mul=node(mat,'Multiply',-400,0);connect(samples['BaseColor'],mul,'A',output='RGB');connect(tint,mul,'B');out(mul,'BaseColor')
        out(samples['Roughness'],'Roughness','R')
        if 'Normal' in samples:out(samples['Normal'],'Normal','RGB')
        metal=node(mat,'Constant',-300,950,r=.85 if family=='Iron' else .78 if family=='Bronze' else 0);out(metal,'Metallic')
        spec=node(mat,'Constant',-300,1100,r=.32);out(spec,'Specular')
        if family=='Flame':
            e=node(mat,'Constant3Vector',-300,1350,constant=dict(r=3,g=.9,b=.08,a=1));out(e,'EmissiveColor')
        tool(MT,'layout_expressions',material_or_function=mat);tool(MT,'recompile',material_or_function=mat)
    for name,info in data['assets'].items():
        path=path_for(name);folder=path.rsplit('/',1)[0]
        if not tool(AS,'exists',path=path):
            result=tool(SM,'import_file',folder_path=folder,asset_name=name,source_file=ROOT+'Exports/'+name+'.fbx',import_materials=False,import_textures=False,combine_meshes=False);assert len(result)==1
        mesh=ref(path);meshes[name]=mesh;saved.append(path)
        for family in info['slots']:tool(SM,'set_material',mesh=mesh,slot_name='B03_'+family,material=materials[family])
    # Each lamp is separately placeable, including its matching light, with no Tick logic.
    for kind,lumens,radius,temp in [('Lantern',24,340,3000),('Pendant',90,470,3000),('WallLantern',40,380,3000)]:
        name='BP_EH03_'+kind;path=FURN+'/Blueprints/'+name
        if tool(AS,'exists',path=path):lamps[kind]=ref(path);continue
        bp=tool(BP,'create',folder_path=FURN+'/Blueprints',asset_name=name,asset_type=dict(refPath='/Script/Engine.Actor'))
        fixture=tool(AC,'add_component',owner=bp,component_type=dict(refPath='/Script/Engine.StaticMeshComponent'),name='Fixture')
        props(fixture,staticMesh=meshes['SM_EH03_'+kind+'_24'],mobility='Static',castShadow=False,
            bodyInstance=dict(collisionProfileName='BlockAll',collisionEnabled='QueryAndPhysics'))
        light=tool(AC,'add_component',owner=bp,component_type=dict(refPath='/Script/Engine.PointLightComponent'),name='Light')
        props(light,mobility='Movable',relativeLocation=dict(x=0,y=0,z=23),intensityUnits='Lumens',intensity=lumens,
            attenuationRadius=radius,bUseTemperature=True,temperature=temp,bUseInverseSquaredFalloff=True,
            sourceRadius=5,softSourceRadius=2,castShadows=True,indirectLightingIntensity=1.)
        tool(BP,'compile_blueprint',blueprint=bp,warnings_as_errors=True);lamps[kind]=bp;saved.append(path)
    assert tool(AS,'save_assets',asset_paths=saved)
    return dict(materials=materials,meshes=meshes,lamps=lamps,saved=saved,importer='Legacy FbxFactory',
        lamp_shadow_policy='Fixture component does not cast a shadow onto its internal point source; room geometry casts shadows normally')
