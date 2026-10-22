"""Read actual import metadata, geometry and source collision through MCP."""
import json

AS='editor_toolset.toolsets.asset.AssetTools'
OB='editor_toolset.toolsets.object.ObjectTools'
SM='editor_toolset.toolsets.static_mesh.StaticMeshTools'
SC='editor_toolset.toolsets.scene.SceneTools'
ROOT='E:/Business/fantasy-rpg-refiner/AssetSources/Architecture/EB_Blatthof_R255_R640/WallInner_R255_A30_H280/Refiner/HouseStudy_B01/'
BASE='/Game/Art/Architecture/ElvenHouseB01'


def tool(group,operation,**args):
    return execute_tool(group+'.'+operation,json.dumps(args))['returnValue']


def get(obj,fields):
    return json.loads(tool(OB,'get_properties',instance=obj,properties=fields))


def run():
    assert tool(SC,'get_current_level')==BASE+'/Maps/Lvl_ElvenHouseB01_Review'
    with open(ROOT+'manifest.json','r',encoding='utf-8') as f:
        manifest=json.load(f)
    results={}
    for item in manifest['assets']:
        path=BASE+'/Meshes/'+item['name']
        mesh={'refPath':path+'.'+item['name']}
        data=get(mesh,['AssetImportData','BodySetup'])
        import_data=data['AssetImportData']
        assert tool(OB,'get_class',instance=import_data)['refPath']=='/Script/UnrealEd.FbxStaticMeshImportData'
        collision=get(data['BodySetup'],['AggGeom','CollisionTraceFlag'])
        hulls=len(collision['AggGeom']['convexElems'])
        triangles=tool(SM,'get_triangle_count',mesh=mesh,lod_index=0)
        assert triangles==item['triangles'],(item['name'],triangles)
        assert hulls==item['ucx_hulls'],(item['name'],hulls,item['ucx_hulls'])
        results[item['name']]=dict(bounds=tool(SM,'get_bounds',mesh=mesh),triangles=triangles,
            hulls=hulls,collision_trace=collision['CollisionTraceFlag'],
            slots=tool(SM,'get_material_slots',mesh=mesh),
            import_options=get(import_data,['importUniformScale','importTranslation','importRotation',
                'bConvertScene','bConvertSceneUnit','bForceFrontXAxis','bTransformVertexToAbsolute',
                'bBakePivotInVertex','normalImportMethod','normalGenerationMethod','bCombineMeshes',
                'bOneConvexHullPerUCX','bAutoGenerateCollision','bGenerateLightmapUVs','bBuildNanite']))
    return dict(meshes=results,source_collision_counts_match=True,legacy_fbx_metadata=True,
                actors=tool(SC,'find_actors',name='',tag='',collision_channels=[]))
