"""Supported MCP API, private new paths only, explicit legacy import session."""
import json
AS='editor_toolset.toolsets.asset.AssetTools';SM='editor_toolset.toolsets.static_mesh.StaticMeshTools'
TX='editor_toolset.toolsets.texture.TextureTools';MT='editor_toolset.toolsets.material.MaterialTools'
OB='editor_toolset.toolsets.object.ObjectTools';BP='editor_toolset.toolsets.blueprint.BlueprintTools';AC='editor_toolset.toolsets.actor.ActorTools'
ROOT='E:/Business/fantasy-rpg-refiner/AssetSources/Architecture/EC_HighCultureCity/StreetStudy01/Refiner/HighElfWallStudy_01/UnrealIntegration_01/'
MAT='/Game/Art/Materials/HighElfWallStudy01';TEX='/Game/Art/Textures/HighElfWallStudy01';ARCH='/Game/Art/Architecture/HighElfWallStudy01'
def tool(g,n,**a):return execute_tool(g+'.'+n,json.dumps(a)).get('returnValue')
def ref(p):return dict(refPath=p+'.'+p.rsplit('/',1)[-1])
def props(o,**v):
    tool(OB,'list_properties',instance=o);assert tool(OB,'set_properties',instance=o,values=json.dumps(v))
def node(m,k,x,y,**v):
    n=tool(MT,'add_expression',material_or_function=m,expression_class=dict(refPath='/Script/Engine.MaterialExpression'+k),x=x,y=y)
    if v:props(n,**v)
    return n
def output(n,p,pin=''):tool(MT,'connect_to_output',expression=n,output_name=pin,material_property='MP_'+p)
def run():
    assert tool('editor_toolset.toolsets.scene.SceneTools','get_current_level')=='/Game/Prototype/Maps/Lvl_AssetLab'
    assert not tool('EditorToolset.EditorAppToolset','IsPIERunning')
    with open(ROOT+'manifest.json','r') as f:data=json.load(f)
    saved=[];materials={};meshes={};blueprints={}
    for family in data['material_families']:
        path=MAT+'/M_HE01_'+family
        assert not tool(AS,'exists',path=path),path
        if family=='ClearGlass':
            assert tool(AS,'duplicate',path='/Game/Art/Materials/StudyAB_Review01/M_AB_Glass',new_path=path);m=ref(path)
        else:
            m=tool(MT,'create_material',folder_path=MAT,asset_name='M_HE01_'+family)
            for channel,sampler,y in [('BaseColor','Color',0),('Roughness','Masks',300),('Normal','Normal',600)]:
                name='T_HE01_'+family+'_'+channel;tp=TEX+'/'+name
                assert not tool(AS,'exists',path=tp)
                tool(TX,'import_file',folder_path=TEX,asset_name=name,source_file=ROOT+'Textures/'+name+'.png');t=ref(tp);saved.append(tp)
                if channel=='Normal':props(t,sRGB=False,compressionSettings='TC_Normalmap',bFlipGreenChannel=True)
                elif channel=='Roughness':props(t,sRGB=False,compressionSettings='TC_Masks')
                n=node(m,'TextureSample',-600,y,texture=t,samplerType='SAMPLERTYPE_'+sampler);output(n,channel,'R' if channel=='Roughness' else 'RGB')
            n=node(m,'Constant',-350,850,r=data['material_values'][family]['metal']);output(n,'Metallic')
            n=node(m,'Constant',-350,1000,r=.5);output(n,'Specular')
            tool(MT,'layout_expressions',material_or_function=m);tool(MT,'recompile',material_or_function=m)
        materials[family]=m;saved.append(path)
    for name,info in data['assets'].items():
        path=ARCH+'/Meshes/'+name;assert not tool(AS,'exists',path=path)
        r=tool(SM,'import_file',folder_path=ARCH+'/Meshes',asset_name=name,source_file=ROOT+'Exports/'+name+'.fbx',import_materials=False,import_textures=False,combine_meshes=False);assert len(r)==1
        mesh=ref(path);slots=tool(SM,'get_material_slots',mesh=mesh);assert slots==info['slots'],(name,slots)
        for slot in slots:tool(SM,'set_material',mesh=mesh,slot_name=slot,material=materials[slot.replace('HEWS01_','')])
        tool(SM,'set_nanite_enabled',mesh=mesh,enabled=False);meshes[name]=mesh;saved.append(path)
    for variant in ['A','B']:
        name='BP_HE01_WindowWall_'+variant;path=ARCH+'/Blueprints/'+name;assert not tool(AS,'exists',path=path)
        bp=tool(BP,'create',folder_path=ARCH+'/Blueprints',asset_name=name,asset_type=dict(refPath='/Script/Engine.Actor'))
        for part in ['WallCore','StoneCarving','GoldInlay','BlueInlay','WindowFrame','ClearGlass']:
            sourcevariant='A' if part in ['WallCore','WindowFrame','ClearGlass'] else variant
            meshname='SM_HE01_'+sourcevariant+'_'+part
            c=tool(AC,'add_component',owner=bp,component_type=dict(refPath='/Script/Engine.StaticMeshComponent'),name=part)
            coll=part in ['WallCore','ClearGlass']
            props(c,staticMesh=meshes[meshname],mobility='Static',castShadow=part!='ClearGlass',bodyInstance=dict(collisionProfileName='BlockAll' if coll else 'NoCollision',collisionEnabled='QueryAndPhysics' if coll else 'NoCollision'))
        tool(BP,'compile_blueprint',blueprint=bp,warnings_as_errors=True);blueprints[variant]=path;saved.append(path)
    assert tool(AS,'save_assets',asset_paths=saved)
    return dict(status='passed',saved=saved,materials=materials,meshes=meshes,blueprints=blueprints)
