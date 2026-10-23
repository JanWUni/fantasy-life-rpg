"""Calibrated legacy imports and study-private review materials via supported MCP."""
import json
AS='editor_toolset.toolsets.asset.AssetTools';SM='editor_toolset.toolsets.static_mesh.StaticMeshTools'
MT='editor_toolset.toolsets.material.MaterialTools';OB='editor_toolset.toolsets.object.ObjectTools'
ROOT='E:/Business/fantasy-rpg-refiner/AssetSources/Architecture/EC_HighCultureCity/StreetStudy01/Refiner/UnrealReview_01/'
def tool(group,name,**args):return execute_tool(group+'.'+name,json.dumps(args)).get('returnValue')
def ref(p):return dict(refPath=p+'.'+p.rsplit('/',1)[-1])
def props(obj,**values):
    tool(OB,'list_properties',instance=obj);assert tool(OB,'set_properties',instance=obj,values=json.dumps(values))
def node(mat,kind,x,y,**values):
    obj=tool(MT,'add_expression',material_or_function=mat,expression_class=dict(refPath='/Script/Engine.MaterialExpression'+kind),x=x,y=y)
    if values:props(obj,**values)
    return obj
def run():
    assert tool('editor_toolset.toolsets.scene.SceneTools','get_current_level')=='/Game/Prototype/Maps/Lvl_AssetLab'
    assert not tool('EditorToolset.EditorAppToolset','IsPIERunning')
    with open(ROOT+'plan.json','r') as f:plan=json.load(f)
    saved=[];materials={};meshes={};measurements={}
    used={slot for s in plan['studies'] for e in s['mesh_manifest']['exports'] for slot in e['source_stats']['material_slots']}
    definitions={m['name']:m for m in plan['studies'][0]['mesh_manifest']['materials']}
    for family in sorted(used):
        path=plan['materials']+'/M_AB_'+family
        if tool(AS,'exists',path=path):materials[family]=ref(path);continue
        if family=='Glass':
            original='/Game/Art/Materials/ElvenHouseB01/M_EH_Glass_Clear'
            assert tool(AS,'exists',path=original)
            tool(AS,'duplicate',path=original,new_path=path);mat=ref(path)
            # The validated graph is copied privately; existing shared glass stays untouched.
            rough=[]
            for e in tool(MT,'get_expressions',material_or_function=mat):
                if tool(OB,'get_class',instance=e)['refPath']=='/Script/Engine.MaterialExpressionConstant':
                    tool(OB,'list_properties',instance=e);values=tool(OB,'get_properties',instance=e,properties=['r'])
                    if isinstance(values,str):values=json.loads(values)
                    if abs(values['r']-.06)<1e-5:props(e,r=.025);rough.append(e)
            assert len(rough)==1,rough
        else:
            mat=tool(MT,'create_material',folder_path=plan['materials'],asset_name='M_AB_'+family)
            d=definitions[family];color=node(mat,'Constant3Vector',-250,0,constant=dict(zip(['r','g','b','a'],d['base_color'])))
            tool(MT,'connect_to_output',expression=color,output_name='',material_property='MP_BaseColor')
            for prop,value,y in [('Roughness',d['roughness'],170),('Metallic',0,320),('Specular',.35,470)]:
                n=node(mat,'Constant',-250,y,r=value);tool(MT,'connect_to_output',expression=n,output_name='',material_property='MP_'+prop)
        tool(MT,'layout_expressions',material_or_function=mat);tool(MT,'recompile',material_or_function=mat)
        materials[family]=mat;saved.append(path)
    for study in plan['studies']:
        for e in study['mesh_manifest']['exports']:
            path=study['dest']+'/Meshes/'+e['asset_name']
            if not tool(AS,'exists',path=path):
                created=tool(SM,'import_file',folder_path=study['dest']+'/Meshes',asset_name=e['asset_name'],
                    source_file=study['parent']+'/'+e['path'],import_materials=False,import_textures=False,combine_meshes=False)
                assert len(created)==1,(path,created)
            mesh=ref(path);slots=tool(SM,'get_material_slots',mesh=mesh);assert slots==e['source_stats']['material_slots'],(path,slots)
            for slot in slots:tool(SM,'set_material',mesh=mesh,slot_name=slot,material=materials[slot])
            tool(SM,'set_nanite_enabled',mesh=mesh,enabled=False)
            measurements[path]=dict(bounds=tool(SM,'get_bounds',mesh=mesh),triangles=tool(SM,'get_triangle_count',mesh=mesh,lod_index=0),slots=slots)
            meshes[e['asset_name']]=mesh;saved.append(path)
    assert tool(AS,'save_assets',asset_paths=saved)
    return dict(status='passed',materials=materials,meshes=meshes,measurements=measurements,saved=saved,
        importer='Explicit calibrated Legacy FbxFactory, session CVar disabled during import',
        solids='Source colors/roughness; Blender procedural bump is not transferred',glass='Private duplicate of validated Substrate SimpleVolume graph; roughness .025')
