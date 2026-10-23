"""Build explicit Substrate clear glass instead of relying on legacy ThinTranslucent conversion."""
import json
AS='editor_toolset.toolsets.asset.AssetTools'
MT='editor_toolset.toolsets.material.MaterialTools'
OB='editor_toolset.toolsets.object.ObjectTools'
PATH='/Game/Art/Materials/ElvenHouseB01/M_EH_Glass_Clear'


def tool(group,operation,**args):
    r=execute_tool(group+'.'+operation,json.dumps(args))
    return r['returnValue'] if 'returnValue' in r else None


def props(obj,**values):
    tool(OB,'list_properties',instance=obj)
    assert tool(OB,'set_properties',instance=obj,values=json.dumps(values))


def run():
    mat={'refPath':PATH+'.M_EH_Glass_Clear'}
    for e in tool(MT,'get_expressions',material_or_function=mat):tool(MT,'delete_expression',material_or_function=mat,expression=e)
    props(mat,blendMode='BLEND_TranslucentColoredTransmittance',translucencyLightingMode='TLM_SurfacePerPixelLighting')
    def node(kind,x,y,**values):
        n=tool(MT,'add_expression',material_or_function=mat,expression_class={'refPath':'/Script/Engine.MaterialExpression'+kind},x=x,y=y)
        if values:props(n,**values)
        return n
    def connect(a,b,pin,output=''):
        names=tool(MT,'get_expression_input_names',expression=b)
        assert pin in names,(pin,names)
        tool(MT,'connect_expressions',from_expression=a,from_output_name=output,to_expression=b,to_input_name=pin)
    slab=node('SubstrateSlabBSDF',-180,0,subSurfaceType='MSS_SimpleVolume')
    inputs=tool(MT,'get_expression_input_names',expression=slab)
    for color,pin,y in [((0,0,0),'Diffuse Albedo',0),((.04,.04,.04),'F0',150)]:
        n=node('Constant3Vector',-650,y,constant=dict(r=color[0],g=color[1],b=color[2],a=1))
        connect(n,slab,pin)
    rough=node('Constant',-650,300,r=.06);connect(rough,slab,'Roughness')
    color=node('Constant3Vector',-1050,500,constant=dict(r=.97,g=.985,b=1,a=1))
    mfp=node('SubstrateTransmittanceToMFP',-650,500)
    mfp_inputs=tool(MT,'get_expression_input_names',expression=mfp)
    connect(color,mfp,mfp_inputs[0])
    mfp_outputs=tool(MT,'get_expression_output_names',expression=mfp)
    # Connector display names can differ from C++ member identifiers; inspect them explicitly.
    sss=next(n for n in inputs if 'MFP' in n and 'Scale' not in n)
    connect(mfp,slab,sss,mfp_outputs[0])
    tool(MT,'connect_to_output',expression=slab,output_name='',material_property='MP_FrontMaterial')
    tool(MT,'layout_expressions',material_or_function=mat)
    tool(MT,'recompile',material_or_function=mat)
    assert tool(AS,'save_assets',asset_paths=[PATH])
    return dict(status='passed',material=PATH,shader='Substrate Slab BSDF SimpleVolume + TransmittanceToMFP',
                normal_incidence_transmittance_rgb=[.97,.985,1],roughness=.06,refraction='Unconnected; no screen-space distortion',
                inputs=inputs,mfp_inputs=mfp_inputs,mfp_outputs=mfp_outputs)
