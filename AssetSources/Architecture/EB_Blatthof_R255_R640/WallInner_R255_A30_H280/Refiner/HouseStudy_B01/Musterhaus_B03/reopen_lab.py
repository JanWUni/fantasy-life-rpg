"""Explicit saved-map reopen without saving any unrelated package."""
import json
SC='editor_toolset.toolsets.scene.SceneTools';AS='editor_toolset.toolsets.asset.AssetTools'
def tool(g,op,**kw):return execute_tool(g+'.'+op,json.dumps(kw)).get('returnValue')
def run():
    assert not tool('EditorToolset.EditorAppToolset','IsPIERunning')
    assert tool(AS,'save_assets',asset_paths=['/Game/Prototype/Maps/Lvl_AssetLab'])
    tool(SC,'load_level',level_path='/Game/Art/Architecture/ElvenHouseB01/Maps/Lvl_ElvenHouseB01_Review')
    tool(SC,'load_level',level_path='/Game/Prototype/Maps/Lvl_AssetLab')
    assert tool(SC,'get_current_level')=='/Game/Prototype/Maps/Lvl_AssetLab'
    return dict(status='passed',lab_reopened=True)
