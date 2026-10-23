import json
def tool(g,n,**a):return execute_tool(g+'.'+n,json.dumps(a)).get('returnValue')
def run():
    p='/Game/Art/Materials/HighElfWallStudy02/M_HE02_ClearGlass';m=dict(refPath=p+'.M_HE02_ClearGlass')
    mt='editor_toolset.toolsets.material.MaterialTools';ob='editor_toolset.toolsets.object.ObjectTools'
    for name,values in [('MaterialExpressionConstant3Vector_2',dict(constant=dict(r=.78,g=.89,b=.94,a=1))),('MaterialExpressionConstant_1',dict(r=1.06))]:
        n=dict(refPath=m['refPath']+':'+name);tool(ob,'list_properties',instance=n);assert tool(ob,'set_properties',instance=n,values=json.dumps(values))
    tool(mt,'recompile',material_or_function=m)
    assert tool('editor_toolset.toolsets.asset.AssetTools','save_assets',asset_paths=[p])
    return dict(status='passed',transmittance=[.78,.89,.94],refraction='PixelNormalOffset',amount=1.06,SSR=True)
