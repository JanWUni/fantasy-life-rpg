"""Import three new meshes, one clear-glass material, and a reusable window Blueprint via MCP."""
import json
AS='editor_toolset.toolsets.asset.AssetTools'
SM='editor_toolset.toolsets.static_mesh.StaticMeshTools'
MT='editor_toolset.toolsets.material.MaterialTools'
OB='editor_toolset.toolsets.object.ObjectTools'
BP='editor_toolset.toolsets.blueprint.BlueprintTools'
AC='editor_toolset.toolsets.actor.ActorTools'
SC='editor_toolset.toolsets.scene.SceneTools'
BASE='/Game/Art/Architecture/ElvenHouseB01/Windows'
MAT='/Game/Art/Materials/ElvenHouseB01'
ROOT='E:/Business/fantasy-rpg-refiner/AssetSources/Architecture/EB_Blatthof_R255_R640/WallInner_R255_A30_H280/Refiner/HouseStudy_B01/WindowUpdate_B02/'


def tool(group,operation,**args):
    result=execute_tool(group+'.'+operation,json.dumps(args))
    return result['returnValue'] if 'returnValue' in result else None


def ref(path):return {'refPath':path+'.'+path.rsplit('/',1)[-1]}
def props(obj,**values):
    tool(OB,'list_properties',instance=obj)
    assert tool(OB,'set_properties',instance=obj,values=json.dumps(values))


def node(mat,kind,x,y,**values):
    expression=tool(MT,'add_expression',material_or_function=mat,
        expression_class={'refPath':'/Script/Engine.MaterialExpression'+kind},x=x,y=y)
    if values:props(expression,**values)
    return expression


def output(expression,prop):
    tool(MT,'connect_to_output',expression=expression,output_name='',material_property='MP_'+prop)


def run():
    assert tool(SC,'get_current_level')=='/Game/Prototype/Maps/Lvl_AssetLab'
    with open(ROOT+'manifest.json','r',encoding='utf-8') as f:manifest=json.load(f)
    meshes={}
    for name,info in manifest['assets'].items():
        assert not tool(AS,'exists',path=BASE+'/Meshes/'+name)
        imported=tool(SM,'import_file',folder_path=BASE+'/Meshes',asset_name=name,
            source_file=ROOT+'Exports/'+name+'.fbx',import_materials=False,import_textures=False,combine_meshes=False)
        assert len(imported)==1;meshes[name]=imported[0]
    material_path=MAT+'/M_EH_Glass_Clear'
    assert not tool(AS,'exists',path=material_path)
    mat=tool(MT,'create_material',folder_path=MAT,asset_name='M_EH_Glass_Clear')
    props(mat,blendMode='BLEND_Translucent',shadingModel='MSM_ThinTranslucent',
          translucencyLightingMode='TLM_SurfacePerPixelLighting',twoSided=False)
    color=node(mat,'Constant3Vector',-500,300,constant=dict(r=.97,g=.985,b=1,a=1))
    thin=node(mat,'ThinTranslucentMaterialOutput',-200,300)
    inputs=tool(MT,'get_expression_input_names',expression=thin)
    assert 'TransmittanceColor' in inputs,inputs
    tool(MT,'connect_expressions',from_expression=color,from_output_name='',to_expression=thin,to_input_name='TransmittanceColor')
    for prop,value,y in [('Metallic',0,0),('Roughness',.08,100),('Specular',.5,200),('Opacity',1,400)]:
        expression=node(mat,'Constant',-200,y,r=value);output(expression,prop)
    tool(MT,'layout_expressions',material_or_function=mat)
    tool(MT,'recompile',material_or_function=mat)
    for name,info in manifest['assets'].items():
        for slot in info['slots']:
            tool(SM,'set_material',mesh=meshes[name],slot_name=slot,
                 material=mat if slot=='Glass' else ref(MAT+'/M_EH_'+slot))
    blueprint_path=BASE+'/BP_EH_Window_Arch_100x173'
    assert not tool(AS,'exists',path=blueprint_path)
    blueprint=tool(BP,'create',folder_path=BASE,asset_name='BP_EH_Window_Arch_100x173',asset_type={'refPath':'/Script/Engine.Actor'})
    components={}
    for component_name,mesh_name in [('Frame','SM_EH_WindowFrame_Arch_100x173'),('Glazing','SM_EH_WindowGlass_Arch_100x173')]:
        comp=tool(AC,'add_component',owner=blueprint,component_type={'refPath':'/Script/Engine.StaticMeshComponent'},name=component_name)
        values=dict(staticMesh=meshes[mesh_name],relativeScale3D=dict(x=1,y=1,z=1),mobility='Static',
                    castShadow=component_name=='Frame')
        if component_name=='Glazing':
            values['bAffectDistanceFieldLighting']=False
            values['bodyInstance']=dict(collisionProfileName='BlockAll',collisionEnabled='QueryAndPhysics')
        else:values['bodyInstance']=dict(collisionProfileName='NoCollision',collisionEnabled='NoCollision')
        props(comp,**values);components[component_name]=comp
    tool(BP,'compile_blueprint',blueprint=blueprint,warnings_as_errors=True)
    paths=[BASE+'/Meshes/'+name for name in meshes]+[material_path,blueprint_path]
    assert tool(AS,'save_assets',asset_paths=paths)
    return dict(meshes=meshes,material=mat,blueprint=blueprint,components=components,
        glazing_shadow_policy='Frame casts shadows; clear glazing does not cast opaque shadows or affect distance-field lighting',
        source_materials_unchanged=True)
