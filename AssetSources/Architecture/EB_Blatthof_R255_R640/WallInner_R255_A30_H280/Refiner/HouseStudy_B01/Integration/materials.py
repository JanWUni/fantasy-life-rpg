"""Create the study's own PBR materials through Unreal MCP."""
import json

AS = 'editor_toolset.toolsets.asset.AssetTools'
MT = 'editor_toolset.toolsets.material.MaterialTools'
OB = 'editor_toolset.toolsets.object.ObjectTools'
SM = 'editor_toolset.toolsets.static_mesh.StaticMeshTools'
ROOT = 'E:/Business/fantasy-rpg-refiner/AssetSources/Architecture/EB_Blatthof_R255_R640/WallInner_R255_A30_H280/Refiner/HouseStudy_B01/'
BASE = '/Game/Art/Architecture/ElvenHouseB01'
MAT = '/Game/Art/Materials/ElvenHouseB01'
TEX = '/Game/Art/Textures/ElvenHouseB01'


def tool(group, name, **args):
    result = execute_tool(group+'.'+name, json.dumps(args))
    return result['returnValue'] if 'returnValue' in result else None


def ref(path):
    return {'refPath':path+'.'+path.rsplit('/',1)[-1]}


def props(obj, **values):
    tool(OB, 'list_properties', instance=obj)
    assert tool(OB, 'set_properties', instance=obj, values=json.dumps(values))


def node(mat, kind, x, y, **values):
    obj = tool(MT, 'add_expression', material_or_function=mat,
               expression_class={'refPath':'/Script/Engine.MaterialExpression'+kind},x=x,y=y)
    if values:
        props(obj, **values)
    return obj


def output(obj, prop, pin=''):
    tool(MT, 'connect_to_output', expression=obj, output_name=pin, material_property='MP_'+prop)


def connect(a, b, pin):
    tool(MT, 'connect_expressions', from_expression=a, from_output_name='',
         to_expression=b, to_input_name=pin)


def scalar(mat, prop, val, y):
    obj = node(mat, 'Constant',-200,y,r=val)
    output(obj,prop)


def run():
    materials = {}
    for family in ('Plaster','Timber','Stone','Jade','Glass','Bronze','ReviewGround'):
        path = MAT+'/M_EH_'+family
        if tool(AS,'exists',path=path):
            # Only this integration's own material graphs may be rebuilt after a failed pass.
            mat = ref(path)
            for expr in tool(MT,'get_expressions',material_or_function=mat):
                tool(MT,'delete_expression',material_or_function=mat,expression=expr)
        else:
            mat = tool(MT,'create_material',folder_path=MAT,asset_name='M_EH_'+family)
        materials[family] = mat
        if family in ('Plaster','Timber','Stone','Jade'):
            for channel, prop, sampler, y in [('BaseColor','BaseColor','Color',0),
                                               ('Roughness','Roughness','Masks',250),
                                               ('Normal','Normal','Normal',500)]:
                texture = ref(TEX+'/T_EH_'+family+'_'+channel)
                if channel == 'Normal':
                    props(texture,sRGB=False,compressionSettings='TC_Normalmap',bFlipGreenChannel=True)
                elif channel == 'Roughness':
                    props(texture,sRGB=False,compressionSettings='TC_Masks')
                sample = node(mat,'TextureSample',-700,y,texture=texture,
                              samplerType='SAMPLERTYPE_'+sampler)
                if channel == 'Normal':
                    strength = .32 if family == 'Timber' else .20
                    scale = node(mat,'Constant3Vector',-700,800,
                                 constant={'r':strength,'g':strength,'b':1,'a':1})
                    mult = node(mat,'Multiply',-380,500)
                    connect(sample,mult,'A'); connect(scale,mult,'B')
                    norm = node(mat,'Normalize',-180,500)
                    connect(mult,norm,'VectorInput')
                    output(norm,prop)
                else:
                    output(sample,prop,'R' if channel=='Roughness' else 'RGB')
            scalar(mat,'Metallic',.08 if family=='Jade' else 0,1000)
        else:
            color,metal,rough = {'Glass':((.022,.095,.12),.45,.17),
                                'Bronze':((.27,.15,.055),.75,.31),
                                'ReviewGround':((.18,.20,.16),0,.9)}[family]
            obj=node(mat,'Constant3Vector',-200,0,
                     constant={'r':color[0],'g':color[1],'b':color[2],'a':1})
            output(obj,'BaseColor');scalar(mat,'Metallic',metal,150);scalar(mat,'Roughness',rough,300)
        tool(MT,'layout_expressions',material_or_function=mat)
        tool(MT,'recompile',material_or_function=mat)
    with open(ROOT+'manifest.json','r',encoding='utf-8') as f:
        manifest=json.load(f)
    for item in manifest['assets']:
        mesh=ref(BASE+'/Meshes/'+item['name'])
        for family in item['slots']:
            tool(SM,'set_material',mesh=mesh,slot_name=family,material=materials[family])
    paths = [MAT+'/M_EH_'+key for key in materials]
    paths += [TEX+'/T_EH_'+family+'_'+channel for family in ('Plaster','Timber','Stone','Jade')
              for channel in ('BaseColor','Normal','Roughness')]
    paths += [BASE+'/Meshes/'+item['name'] for item in manifest['assets']]
    assert tool(AS,'save_assets',asset_paths=paths)
    return dict(materials=materials,normal_green_flipped=True,
                normal_xy_strength={'Timber':.32,'others':.20})
