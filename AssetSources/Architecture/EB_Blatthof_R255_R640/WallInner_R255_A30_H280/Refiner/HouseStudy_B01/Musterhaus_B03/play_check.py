"""Actual E-key check at the furnished sample's door, then leave PIE for the movement fixture."""
from pathlib import Path
import sys,json,time,re
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT.parent/'Integration'));import ue_rpc as c
c.connect()
APP='EditorToolset.EditorAppToolset';SL='SlateInspectorToolset.SlateInspectorToolset';SC='editor_toolset.toolsets.scene.SceneTools';AC='editor_toolset.toolsets.actor.ActorTools';OB='editor_toolset.toolsets.object.ObjectTools'
def call(g,op,**kw):return c.value(c.call(g,op,**kw))
assert not call(APP,'IsPIERunning')
call(APP,'StartPIE',options=dict(bSimulate=False,playMode='PlayMode_InEditorFloating',warmupSeconds=3,startTransform=dict(location=dict(x=-1900,y=-1800,z=122),rotation=dict(pitch=0,yaw=-90,roll=0),scale=dict(x=1,y=1,z=1))))
snapshot=call(SL,'Snapshot',ref='',maxDepth=2)
(ROOT/'Evidence/pie_windows.txt').write_text(snapshot)
match=re.search(r'^window "[^"\n]*Vorschau[^"\n]*"[^\n]*\[ref=(w\d+)\]',snapshot,re.MULTILINE)
window=match.group(1) if match else 'w1'
doors=call(SC,'find_actors',name='',tag='',collision_channels=[],actor_type=dict(refPath='/Game/Art/Architecture/ElvenHouseB01/Blueprints/BP_EH_ReviewDoor.BP_EH_ReviewDoor_C'))
door=min(doors,key=lambda a:call(AC,'get_actor_transform',actor=a)['location']['x'])
def opened():return json.loads(call(OB,'get_properties',instance=door,properties=['bIsOpen']))['bIsOpen']
assert not opened()
call(SL,'Click',ref=window,button='left',doubleClick=False,modifiers=[])
states=[]
for expected in [True,False,True]:
    call(SL,'PressKey',key='E');time.sleep(.4);actual=opened();states.append(actual);assert actual==expected,(states,window,snapshot)
(ROOT/'Evidence/pie_door.json').write_text(json.dumps(dict(status='passed',actual_e_open_close_open=states,game_window=window),indent=2)+'\n')
print('PIE_DOOR_INPUT_PASSED',window)
