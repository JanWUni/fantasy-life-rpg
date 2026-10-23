"""Actual Lab viewport captures after temporal visibility and exposure warmup."""
from pathlib import Path
import base64,json,math,sys,time
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'Integration'))
import ue_rpc as c
views={'lab_overview':((-4100,-650,1400),(-800,-2550,280)),
       'window_outside':((-2125,-1740,215),(-2125,-2250,215)),
       'window_inside':((-2125,-2200,215),(-2125,-1750,215)),
       'sunlit_floor':((-1800,-2450,320),(-1975,-2014,31))}
name=sys.argv[1];pos,target=views[name]
delta=[target[i]-pos[i] for i in range(3)]
pose=dict(location=dict(zip('xyz',pos)),rotation=dict(
    pitch=math.degrees(math.atan2(delta[2],math.hypot(*delta[:2]))),yaw=math.degrees(math.atan2(delta[1],delta[0])),roll=0))
c.connect();c.call('EditorToolset.EditorAppToolset','SetCameraTransform',transform=pose)
args=dict(captureTransform=pose,bShowUI=False,annotations=dict(gridSpacing=0,gridExtent=0,gridHeight=0,
    maxLabelDistance=0,maxLabels=0,classFilter={'refPath':'/Script/Engine.Actor'}))
c.call('EditorToolset.EditorAppToolset','CaptureViewport',**args);time.sleep(3)
data=c.value(c.call('EditorToolset.EditorAppToolset','CaptureViewport',**args))
image=data.pop('image');out=ROOT/'Previews';out.mkdir(exist_ok=True)
suffix=sys.argv[2] if len(sys.argv)>2 else ''
(out/(name+suffix+'.png')).write_bytes(base64.b64decode(image['data']))
(out/(name+suffix+'.json')).write_text(json.dumps(data,indent=2)+'\n')
print(str(out/(name+suffix+'.png')))
