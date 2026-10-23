"""Capture actual Unreal views; warm up temporal visibility, keep original Lab exposure."""
from pathlib import Path
import base64,json,sys,time,math
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT.parent/'Integration'));import ue_rpc as c
views=dict(exterior=((-3400,-1250,510),(-1900,-2350,240)),
    overview=((-5300,-300,2250),(-3500,-2250,120)),
    living=((-1830,-2080,206),(-2120,-2490,160)),
    rooms=((-1880,-2430,202),(-1875,-2750,175)),
    bedroom=((-2050,-2730,202),(-2230,-2960,115)),
    storage=((-1676,-2700,202),(-1620,-2980,145)),
    materials=((-2350,-1700,220),(-2350,-1950,200)),
    gallery=((-6000,-500,650),(-4500,-2100,110)))
name=sys.argv[1];pos,target=views[name];d=[target[i]-pos[i] for i in range(3)]
pose=dict(location=dict(zip('xyz',pos)),rotation=dict(pitch=math.degrees(math.atan2(d[2],math.hypot(*d[:2]))),yaw=math.degrees(math.atan2(d[1],d[0])),roll=0))
c.connect();c.call('EditorToolset.EditorAppToolset','SetCameraTransform',transform=pose)
args=dict(captureTransform=pose,bShowUI=False,annotations=dict(gridSpacing=0,gridExtent=0,gridHeight=0,maxLabelDistance=0,maxLabels=0,classFilter=dict(refPath='/Script/Engine.Actor')))
c.call('EditorToolset.EditorAppToolset','CaptureViewport',**args);time.sleep(3)
data=c.value(c.call('EditorToolset.EditorAppToolset','CaptureViewport',**args));im=data.pop('image')
(ROOT/'Previews'/(name+'.png')).write_bytes(base64.b64decode(im['data']));(ROOT/'Previews'/(name+'.json')).write_text(json.dumps(data,indent=2)+'\n')
print(name)
