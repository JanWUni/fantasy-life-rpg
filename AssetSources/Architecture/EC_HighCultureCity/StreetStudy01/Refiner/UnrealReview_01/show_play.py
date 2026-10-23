"""Begin an ordinary playable session in front of study B using the existing player."""
import json
def tool(g,n,**a):return execute_tool(g+'.'+n,json.dumps(a)).get('returnValue')
def run():
    assert tool('editor_toolset.toolsets.scene.SceneTools','get_current_level')=='/Game/Prototype/Maps/Lvl_AssetLab'
    assert not tool('EditorToolset.EditorAppToolset','IsPIERunning')
    tool('EditorToolset.EditorAppToolset','StartPIE',options=dict(bSimulate=False,playMode='PlayMode_InViewPort',warmupSeconds=1,
        startTransform=dict(location=dict(x=4300,y=3400,z=140),rotation=dict(pitch=0,yaw=-90,roll=0),scale=dict(x=1,y=1,z=1))))
    return dict(status='passed',pie_running=tool('EditorToolset.EditorAppToolset','IsPIERunning'),
        spawn_override_cm=[4300,3400,140],facing_yaw=-90,existing_player_and_game_mode=True)
