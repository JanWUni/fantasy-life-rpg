"""Supported MCP imports into this catalogue's private asset paths only."""
import json
AS='editor_toolset.toolsets.asset.AssetTools';SM='editor_toolset.toolsets.static_mesh.StaticMeshTools'
TX='editor_toolset.toolsets.texture.TextureTools';MT='editor_toolset.toolsets.material.MaterialTools'
OB='editor_toolset.toolsets.object.ObjectTools';BP='editor_toolset.toolsets.blueprint.BlueprintTools';AC='editor_toolset.toolsets.actor.ActorTools'
ROOT='E:/Business/fantasy-rpg-refiner/AssetSources/Architecture/EC_HighCultureCity/StreetStudy01/Refiner/WallCatalogue_01/'
MAT='/Game/Art/Materials/WallCatalogue01';TEX='/Game/Art/Textures/WallCatalogue01'
ARCH='/Game/Art/Architecture/WallCatalogue01';FURN='/Game/Art/Furniture/WallCatalogue01'
def tool(g,n,**a):return execute_tool(g+'.'+n,json.dumps(a)).get('returnValue')
def ref(p):return dict(refPath=p+'.'+p.rsplit('/',1)[-1])
def props(o,**v):
    tool(OB,'list_properties',instance=o);assert tool(OB,'set_properties',instance=o,values=json.dumps(v))
def node(m,k,x,y,**v):
    n=tool(MT,'add_expression',material_or_function=m,expression_class=dict(refPath='/Script/Engine.MaterialExpression'+k),x=x,y=y)
    if v:props(n,**v)
    return n
def output(n,p,pin=''):tool(MT,'connect_to_output',expression=n,output_name=pin,material_property='MP_'+p)
def path_for(n,kind):return (FURN if kind in ['Furniture','Lamp'] else ARCH)+'/Meshes/'+n
def run():
    assert tool('editor_toolset.toolsets.scene.SceneTools','get_current_level')=='/Game/Prototype/Maps/Lvl_AssetLab'
    assert not tool('EditorToolset.EditorAppToolset','IsPIERunning')
    with open(ROOT+'manifest.json','r') as f:data=json.load(f)
    saved=[];materials={};meshes={};measured={}
    for family in data['material_families']:
        path=MAT+'/M_WC01_'+family
        if tool(AS,'exists',path=path):materials[family]=ref(path);continue
        if family=='Glass':
            assert tool(AS,'duplicate',path='/Game/Art/Materials/StudyAB_Review01/M_AB_Glass',new_path=path)
            m=ref(path)
        else:
            m=tool(MT,'create_material',folder_path=MAT,asset_name='M_WC01_'+family)
            if family=='Glow':
                n=node(m,'Constant3Vector',-400,0,constant=dict(r=4,g=1.65,b=.4,a=1));output(n,'EmissiveColor')
                n=node(m,'Constant3Vector',-400,150,constant=dict(r=.8,g=.4,b=.1,a=1));output(n,'BaseColor')
            else:
                for channel,sampler,y in [('BaseColor','Color',0),('Roughness','Masks',300),('Normal','Normal',600)]:
                    name='T_WC01_'+family+'_'+channel;tp=TEX+'/'+name
                    if not tool(AS,'exists',path=tp):tool(TX,'import_file',folder_path=TEX,asset_name=name,source_file=ROOT+'Textures/'+name+'.png')
                    t=ref(tp);saved.append(tp)
                    if channel=='Normal':props(t,sRGB=False,compressionSettings='TC_Normalmap',bFlipGreenChannel=True)
                    elif channel=='Roughness':props(t,sRGB=False,compressionSettings='TC_Masks')
                    n=node(m,'TextureSample',-600,y,texture=t,samplerType='SAMPLERTYPE_'+sampler)
                    output(n,channel,'R' if channel=='Roughness' else 'RGB')
                n=node(m,'Constant',-350,850,r=.85 if family=='Iron' else .78 if family=='Bronze' else 0);output(n,'Metallic')
                n=node(m,'Constant',-350,1000,r=.35);output(n,'Specular')
            tool(MT,'layout_expressions',material_or_function=m);tool(MT,'recompile',material_or_function=m)
        materials[family]=m;saved.append(path)
    for name,info in data['assets'].items():
        path=path_for(name,info['kind'])
        if not tool(AS,'exists',path=path):
            r=tool(SM,'import_file',folder_path=path.rsplit('/',1)[0],asset_name=name,source_file=ROOT+'Exports/'+name+'.fbx',import_materials=False,import_textures=False,combine_meshes=False);assert len(r)==1
        mesh=ref(path);slots=tool(SM,'get_material_slots',mesh=mesh);assert slots==['WC01_'+s for s in info['slots']],(name,slots)
        for s in info['slots']:tool(SM,'set_material',mesh=mesh,slot_name='WC01_'+s,material=materials[s])
        tool(SM,'set_nanite_enabled',mesh=mesh,enabled=False)
        measured[name]=dict(bounds=tool(SM,'get_bounds',mesh=mesh),triangles=tool(SM,'get_triangle_count',mesh=mesh,lod_index=0),slots=slots)
        meshes[name]=mesh;saved.append(path)
    path=FURN+'/Blueprints/BP_WC01_WallLamp'
    if not tool(AS,'exists',path=path):
        bp=tool(BP,'create',folder_path=FURN+'/Blueprints',asset_name='BP_WC01_WallLamp',asset_type=dict(refPath='/Script/Engine.Actor'))
        c=tool(AC,'add_component',owner=bp,component_type=dict(refPath='/Script/Engine.StaticMeshComponent'),name='Fixture')
        props(c,staticMesh=meshes['SM_WC01_WallLamp_28x54x48'],mobility='Static',castShadow=False,bodyInstance=dict(collisionProfileName='NoCollision',collisionEnabled='NoCollision'))
        c=tool(AC,'add_component',owner=bp,component_type=dict(refPath='/Script/Engine.PointLightComponent'),name='Light')
        props(c,mobility='Movable',relativeLocation=dict(x=0,y=40,z=-23),intensityUnits='Lumens',intensity=32,
            attenuationRadius=240,bUseTemperature=True,temperature=3000,bUseInverseSquaredFalloff=True,sourceRadius=3,softSourceRadius=2,castShadows=True)
        tool(BP,'compile_blueprint',blueprint=bp,warnings_as_errors=True);saved.append(path)
    assert tool(AS,'save_assets',asset_paths=saved)
    return dict(status='passed',saved=saved,materials=materials,meshes=meshes,measurements=measured,
        lamp=path,lamp_policy='Visible source plus inverse-square point light; fixture self-shadow disabled, wall and furniture shadow enabled')
