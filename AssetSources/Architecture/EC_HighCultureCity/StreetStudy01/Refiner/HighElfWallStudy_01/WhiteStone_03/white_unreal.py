import json
R='E:/Business/fantasy-rpg-refiner/AssetSources/Architecture/EC_HighCultureCity/StreetStudy01/Refiner/HighElfWallStudy_01/WhiteStone_03/'
AS='editor_toolset.toolsets.asset.AssetTools';MT='editor_toolset.toolsets.material.MaterialTools';OB='editor_toolset.toolsets.object.ObjectTools';AC='editor_toolset.toolsets.actor.ActorTools'
def tool(g,n,**a):return execute_tool(g+'.'+n,json.dumps(a)).get('returnValue')
def ref(p):return dict(refPath=p+'.'+p.rsplit('/',1)[-1])
def props(o,**v):
    tool(OB,'list_properties',instance=o);assert tool(OB,'set_properties',instance=o,values=json.dumps(v))
def run():
    assert tool('editor_toolset.toolsets.scene.SceneTools','get_current_level')=='/Game/Prototype/Maps/Lvl_AssetLab'
    assert not tool('EditorToolset.EditorAppToolset','IsPIERunning')
    with open(R+'manifest.json','r') as f:d=json.load(f)
    with open(R+'Evidence/baseline.json','r') as f:base=json.load(f)
    saved=[];mats={}
    for family,v in d['colors'].items():
        path='/Game/Art/Materials/HighElfWallStudy03/M_HE03_'+family;assert not tool(AS,'exists',path=path)
        assert tool(AS,'duplicate',path='/Game/Art/Materials/HighElfWallStudy02/M_HE02_'+family,new_path=path)
        m=ref(path);old=tool(MT,'get_property_input',material=m,material_property='MP_BaseColor')
        factor=tool(MT,'add_expression',material_or_function=m,expression_class=dict(refPath='/Script/Engine.MaterialExpressionConstant3Vector'),x=-400,y=0)
        ratio=[t/s for t,s in zip(v['white'],v['old'])];props(factor,constant=dict(r=ratio[0],g=ratio[1],b=ratio[2],a=1),desc='Original pale stone base colour; detailed normal and roughness preserved.')
        mul=tool(MT,'add_expression',material_or_function=m,expression_class=dict(refPath='/Script/Engine.MaterialExpressionMultiply'),x=-200,y=0)
        for n,out,pin in [(old['expression'],old['output_name'],'A'),(factor,'','B')]:tool(MT,'connect_expressions',from_expression=n,from_output_name=out,to_expression=mul,to_input_name=pin)
        tool(MT,'connect_to_output',expression=mul,output_name='',material_property='MP_BaseColor');tool(MT,'layout_expressions',material_or_function=m);tool(MT,'recompile',material_or_function=m);mats[family]=m;saved.append(path)
    wall=next(a for a in base['actors'] if a['label']=='Lab_HE02_Vorher');a=dict(refPath=wall['path'])
    components=tool(AC,'get_components',actor=a,component_type=dict(refPath='/Script/Engine.StaticMeshComponent'))
    for c in components:
        tool(OB,'list_properties',instance=c);values=json.loads(tool(OB,'get_properties',instance=c,properties=['staticMesh']))
        slots=tool('editor_toolset.toolsets.static_mesh.StaticMeshTools','get_material_slots',mesh=values['staticMesh'])
        overrides=[]
        for slot in slots:
            family=slot.removeprefix('HEWS01_');overrides.append(mats[family] if family in mats else ref('/Game/Art/Materials/HighElfWallStudy02/M_HE02_'+family))
        props(c,overrideMaterials=overrides)
    label=next(a for a in base['actors'] if a['label']=='Lab_HE02_Label_Vorher')
    c=tool(AC,'get_components',actor=dict(refPath=label['path']),component_type=dict(refPath='/Script/Engine.TextRenderComponent'))[0]
    props(c,text='WEISS / MIT DETAILS')
    assert tool(AS,'save_assets',asset_paths=saved+['/Game/Prototype/Maps/Lvl_AssetLab'])
    return dict(status='passed',new_materials=saved,updated_actor=wall['path'],updated_label=label['path'],new_textures=0,new_meshes=0)

