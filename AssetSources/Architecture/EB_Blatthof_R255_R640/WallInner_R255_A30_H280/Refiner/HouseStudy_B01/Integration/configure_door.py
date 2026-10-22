"""Duplicate existing interaction into the study; never edit the original door."""
import json

AS='editor_toolset.toolsets.asset.AssetTools'
OB='editor_toolset.toolsets.object.ObjectTools'
BP='editor_toolset.toolsets.blueprint.BlueprintTools'
AC='editor_toolset.toolsets.actor.ActorTools'
SM='editor_toolset.toolsets.static_mesh.StaticMeshTools'
BASE='/Game/Art/Architecture/ElvenHouseB01'


def tool(group,operation,**args):
    result=execute_tool(group+'.'+operation,json.dumps(args))
    return result['returnValue'] if 'returnValue' in result else None


def ref(path):
    return {'refPath':path+'.'+path.rsplit('/',1)[-1]}


def vec(x,y,z):
    return {'x':x,'y':y,'z':z}


def props(obj,**values):
    tool(OB,'list_properties',instance=obj)
    assert tool(OB,'set_properties',instance=obj,values=json.dumps(values))


def run():
    target=BASE+'/Blueprints/BP_EH_ReviewDoor'
    assert not tool(AS,'exists',path=target)
    tool(AS,'duplicate',path='/Game/Prototype/Blueprints/BP_PrototypeDoor',new_path=target)
    blueprint=ref(target)
    cdo=tool(BP,'get_default_object',blueprint=blueprint)
    components=tool(AC,'get_components',actor=cdo,
                    component_type={'refPath':'/Script/Engine.SceneComponent'})
    leaf=ref(BASE+'/Meshes/SM_EH_DoorLeaf_132_Study')
    # The source intentionally has no UCX leaf; derive only this new mesh's simple collision.
    tool(SM,'generate_convex_collisions',mesh=leaf,hull_count=4,max_hull_verts=24,hull_precision=100000)
    updated=[]
    for component in components:
        path=component['refPath']
        if path.endswith(':Mesh'):
            props(component,staticMesh=leaf,relativeScale3D=vec(1,1,1),
                  overrideMaterials=[],mobility='Movable')
            updated.append('Mesh')
        elif path.endswith(':InteractionPoint'):
            props(component,relativeLocation=vec(66,10,100))
            updated.append('InteractionPoint')
        elif 'Handle' in path:
            props(component,bHiddenInGame=True,bVisible=False,
                  bodyInstance={'collisionEnabled':'NoCollision','collisionProfileName':'NoCollision'})
    assert 'Mesh' in updated and 'InteractionPoint' in updated,components
    tool(BP,'compile_blueprint',blueprint=blueprint,warnings_as_errors=True)
    assert tool(AS,'save_assets',asset_paths=[target,BASE+'/Meshes/SM_EH_DoorLeaf_132_Study'])
    return dict(blueprint=blueprint,cdo=cdo,components=components,updated=updated,
                collision='UE convex decomposition, requested 4 hulls/24 vertices; inspect actual count')
