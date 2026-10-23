from pathlib import Path
import sys,json,time,re,base64
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT.parent/'Integration'));import ue_rpc as c
c.connect();SL='SlateInspectorToolset.SlateInspectorToolset';SC='editor_toolset.toolsets.scene.SceneTools';AC='editor_toolset.toolsets.actor.ActorTools';OB='editor_toolset.toolsets.object.ObjectTools'
def call(g,op,**kw):return c.value(c.call(g,op,**kw))
snapshot=call(SL,'Snapshot',ref='',maxDepth=5)
window=re.search(r'window "[^"\n]*Vorschau[^\n]*\[ref=(w\d+)\]',snapshot).group(1)
windows=json.loads(call(SL,'Windows',action='list',index=-1))
index=next(w['index'] for w in windows if 'Vorschau' in w['title'])
call(SL,'Windows',action='select',index=index)
call(SL,'Observe',ref=window,maxDepth=10);snapshot=call(SL,'Snapshot',ref=window,maxDepth=10)
print(snapshot[:2000]);images=re.findall(r'image[^\n]*\[ref=(\w+)\]',snapshot)
call(SL,'Click',ref=images[-1] if images else window,button='left',doubleClick=False,modifiers=[]);time.sleep(1)
doors=call(SC,'find_actors',name='',tag='',collision_channels=[],actor_type=dict(refPath='/Game/Art/Architecture/ElvenHouseB01/Blueprints/BP_EH_ReviewDoor.BP_EH_ReviewDoor_C'))
door=min(doors,key=lambda a:call(AC,'get_actor_transform',actor=a)['location']['x'])
states=[]
for expected in [True,False,True]:
    call(SL,'PressKey',key='E');time.sleep(.7)
    actual=json.loads(call(OB,'get_properties',instance=door,properties=['bIsOpen']))['bIsOpen'];states.append(actual)
    assert actual==expected,(states,snapshot)
(ROOT/'Evidence/pie_door.json').write_text(json.dumps(dict(status='passed',actual_e_open_close_open=states,game_window=window),indent=2)+'\n')
print('PIE_DOOR_PASSED')
