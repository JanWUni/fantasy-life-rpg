"""Exercise actual E input and movement in the isolated PIE scene through MCP."""
from pathlib import Path
import base64
import json
import re
import time
import ue_rpc as c

ROOT=Path(__file__).resolve().parent
OUT=ROOT.parents[6]/'Saved/HouseB01Integration'
AS='editor_toolset.toolsets.actor.ActorTools'
SC='editor_toolset.toolsets.scene.SceneTools'
OB='editor_toolset.toolsets.object.ObjectTools'
SL='SlateInspectorToolset.SlateInspectorToolset'
c.connect()
snapshot=c.value(c.call(SL,'Snapshot',ref='',maxDepth=2))
match=re.search(r'^window "[^"\n]*Vorschau[^"\n]*"[^\n]*\[ref=(w\d+)\]',snapshot,re.MULTILINE)
WINDOW=match.group(1) if match else 'w1'


def call(group,operation,**args):
    return c.value(c.call(group,operation,**args))


def actors(kind):
    return call(SC,'find_actors',name='',tag='',collision_channels=[],actor_type={'refPath':kind})


def state(door):
    return json.loads(call(OB,'get_properties',instance=door,properties=['bIsOpen']))['bIsOpen']


def pose(actor):
    return call(AS,'get_actor_transform',actor=actor)


def screenshot(name):
    result=c.call(SL,'Screenshot',ref=WINDOW)
    block=next((x for x in result['content'] if x['type']=='image'),None)
    if block:
        raw=block['data']
    else:
        data=c.value(result)
        raw=data['data'] if 'data' in data else data['image']['data']
    path=ROOT/'Previews'/name
    path.write_bytes(base64.b64decode(raw))


assert call('EditorToolset.EditorAppToolset','IsPIERunning')
player=actors('/Script/Engine.Character')[0]
doors=actors('/Game/Art/Architecture/ElvenHouseB01/Blueprints/BP_EH_ReviewDoor.BP_EH_ReviewDoor_C')
assert len(doors)==2
door=min(doors,key=lambda d:pose(d)['location']['x'])
call(AS,'set_actor_transform',actor=player,xform=dict(location=dict(x=500,y=100,z=122),
     rotation=dict(pitch=0,yaw=-90,roll=0)))
time.sleep(.5)
assert state(door) is False
before=pose(player)
# The observed central splitter covers the game viewport; give it keyboard focus.
call(SL,'Click',ref=WINDOW if WINDOW!='w1' else 'sp4',button='left',doubleClick=False,modifiers=[])
call(SL,'PressKey',key='E');time.sleep(.5)
assert state(door) is True,'Actual E input did not open the copied door'
opened=pose(door)
call(SL,'PressKey',key='E');time.sleep(.5)
assert state(door) is False,'Actual E input did not close the copied door'
call(SL,'PressKey',key='E');time.sleep(.5)
assert state(door) is True
screenshot('pie_door_open.png')
for count in range(50):
    call(SL,'PressKey',key='W')
    time.sleep(.025)
    if count%4==3 and pose(player)['location']['y']<-250:
        break
after=pose(player)
assert after['location']['y']<0,after
assert abs(after['location']['z']-121)<5,after
screenshot('pie_inside.png')
data=dict(status='passed',actual_e_open_close_open=True,walked_inside=True,
          before=before,after=after,open_door_pose=opened,movement_inputs=count+1,
          limit='One front approach and entry route; full camera/walk review remains manual')
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'pie_result.json').write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps(data))
