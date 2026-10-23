import json
def tool(g,n,**a):return execute_tool(g+'.'+n,json.dumps(a)).get('returnValue')
def run():
    p='/Game/Art/Materials/HighElfWallStudy02/M_HE02_ClearGlass';m=dict(refPath=p+'.M_HE02_ClearGlass')
    mt='editor_toolset.toolsets.material.MaterialTools';ob='editor_toolset.toolsets.object.ObjectTools'
    tool(ob,'list_properties',instance=m)
    assert tool(ob,'set_properties',instance=m,values=json.dumps(dict(bScreenSpaceReflections=True,refractionMethod='RM_PixelNormalOffset')))
    n=tool(mt,'add_expression',material_or_function=m,expression_class=dict(refPath='/Script/Engine.MaterialExpressionConstant'),x=-400,y=1200)
    tool(ob,'list_properties',instance=n);assert tool(ob,'set_properties',instance=n,values=json.dumps(dict(r=1.15,desc='Small pixel normal offset from pane waviness; no opaque fake glass.')))
    tool(mt,'connect_to_output',expression=n,output_name='',material_property='MP_Refraction')
    tool(mt,'layout_expressions',material_or_function=m);tool(mt,'recompile',material_or_function=m)
    assert tool('editor_toolset.toolsets.asset.AssetTools','save_assets',asset_paths=[p])
    return dict(status='passed',SSR=True,refraction='PixelNormalOffset',amount=1.15)
