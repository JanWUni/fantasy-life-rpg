"""Run through MCP ProgrammaticToolset, with a new-world guard."""
import json

AS = 'editor_toolset.toolsets.asset.AssetTools'
SM = 'editor_toolset.toolsets.static_mesh.StaticMeshTools'
SC = 'editor_toolset.toolsets.scene.SceneTools'
TX = 'editor_toolset.toolsets.texture.TextureTools'
ROOT = 'E:/Business/fantasy-rpg-refiner/AssetSources/Architecture/EB_Blatthof_R255_R640/WallInner_R255_A30_H280/Refiner/HouseStudy_B01/'
BASE = '/Game/Art/Architecture/ElvenHouseB01'


def tool(group, name, **args):
    return execute_tool(group+'.'+name, json.dumps(args))['returnValue']


def run():
    assert tool(SC, 'get_current_level') == BASE+'/Maps/Lvl_ElvenHouseB01_Review'
    with open(ROOT+'manifest.json', 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    meshes = {}
    for item in manifest['assets']:
        path = BASE+'/Meshes/'+item['name']
        assert not tool(AS, 'exists', path=path), path
        meshes[item['name']] = tool(SM, 'import_file', folder_path=BASE+'/Meshes',
            asset_name=item['name'], source_file=ROOT+item['fbx'],
            import_materials=False, import_textures=False, combine_meshes=False)
        assert len(meshes[item['name']]) == 1
    textures = {}
    for family, maps in manifest['textures'].items():
        for channel in ('base_color', 'normal', 'roughness'):
            name = maps[channel].rsplit('/',1)[-1].split('.')[0]
            textures[name] = tool(TX, 'import_file', folder_path='/Game/Art/Textures/ElvenHouseB01',
                                 asset_name=name, source_file=ROOT+maps[channel])
    return dict(meshes=meshes, textures=textures)
