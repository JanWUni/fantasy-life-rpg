import json
def tool(g,n,**a):return execute_tool(g+'.'+n,json.dumps(a)).get('returnValue')
def run():
    root='E:/Business/fantasy-rpg-refiner/AssetSources/Architecture/EC_HighCultureCity/StreetStudy01/Refiner/HighElfWallStudy_01/WhiteStone_03/'
    with open(root+'manifest.json','r') as f:d=json.load(f)
    mt='editor_toolset.toolsets.material.MaterialTools';ob='editor_toolset.toolsets.object.ObjectTools';saved=[]
    for family,v in d['colors'].items():
        p='/Game/Art/Materials/HighElfWallStudy03/M_HE03_'+family;m=dict(refPath=p+'.M_HE03_'+family)
        n=next(n for n in tool(mt,'get_expressions',material_or_function=m) if 'MaterialExpressionConstant3Vector' in n['refPath'])
        r=v['ratio'];tool(ob,'list_properties',instance=n);assert tool(ob,'set_properties',instance=n,values=json.dumps(dict(constant=dict(r=r[0],g=r[1],b=r[2],a=1))))
        tool(mt,'recompile',material_or_function=m);saved.append(p)
    assert tool('editor_toolset.toolsets.asset.AssetTools','save_assets',asset_paths=saved)
    return dict(status='passed',colors=d['colors'])
