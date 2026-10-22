"""Capture a real Unreal viewport through MCP and store only small metadata as JSON."""
from pathlib import Path
import base64
import json
import math
import sys
import time
import ue_rpc as c

views={'front':((-1000,1600,950),(500,-350,300)),
       'comparison':((3800,2200,1600),(1400,-700,250)),
       'rear':((1600,-2500,1100),(500,-650,300)),
       'inside':((750,-850,190),(500,-30,160))}
name=sys.argv[1];position,target=views[name]
delta=[target[i]-position[i] for i in range(3)]
rotation={'pitch':math.degrees(math.atan2(delta[2],math.hypot(delta[0],delta[1]))),
          'yaw':math.degrees(math.atan2(delta[1],delta[0])),'roll':0}
pose={'location':dict(zip('xyz',position)),'rotation':rotation}
c.connect()
c.call('EditorToolset.EditorAppToolset','SetCameraTransform',transform=pose)
options=dict(captureTransform=pose,bShowUI=False,
    annotations={'gridSpacing':0,'gridExtent':0,'gridHeight':0,'maxLabelDistance':0,
                 'classFilter':{'refPath':'/Script/Engine.Actor'},'maxLabels':0})
# Let temporal visibility and exposure settle after moving from outside to inside.
c.call('EditorToolset.EditorAppToolset','CaptureViewport',**options)
time.sleep(2)
data=c.value(c.call('EditorToolset.EditorAppToolset','CaptureViewport',**options))
picture=data.pop('image')
root=Path(__file__).resolve().parent/'Previews';root.mkdir(exist_ok=True)
(root/(name+'.png')).write_bytes(base64.b64decode(picture['data']))
(root/(name+'.json')).write_text(json.dumps(data,indent=2)+'\n')
print(str(root/(name+'.png')))
