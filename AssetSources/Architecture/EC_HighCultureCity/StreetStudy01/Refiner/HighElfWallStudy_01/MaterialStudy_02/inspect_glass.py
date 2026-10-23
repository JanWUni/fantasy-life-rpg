import json
def tool(g,n,**a):return execute_tool(g+'.'+n,json.dumps(a)).get('returnValue')
def run():
    m=dict(refPath='/Game/Art/Materials/HighElfWallStudy02/M_HE02_ClearGlass.M_HE02_ClearGlass')
    mt='editor_toolset.toolsets.material.MaterialTools';ob='editor_toolset.toolsets.object.ObjectTools'
    tool(ob,'list_properties',instance=m)
    nodes=[]
    for n in tool(mt,'get_expressions',material_or_function=m):
        keys=json.loads(tool(ob,'list_properties',instance=n)); wanted=[k for k in keys if k in ['r','constant','subSurfaceType','texture','samplerType']]
        nodes.append(dict(ref=n,values=tool(ob,'get_properties',instance=n,properties=wanted),inputs=tool(mt,'get_expression_inputs',material_or_function=m,expression=n)))
    return dict(values=tool(ob,'get_properties',instance=m,properties=['blendMode','translucencyLightingMode','bScreenSpaceReflections','refractionMethod']),nodes=nodes,front=tool(mt,'get_property_input',material=m,material_property='MP_FrontMaterial'))


