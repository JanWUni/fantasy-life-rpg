"""Dedicated port-8001 MCP runner for the two authorized Refiner lab studies."""
from pathlib import Path
import argparse,base64,hashlib,json,re,shutil,sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[5]
sys.path.insert(0,str(REPO/'AssetSources/Architecture/EB_Blatthof_R255_R640/WallInner_R255_A30_H280/Refiner/HouseStudy_B01/Integration'))
import ue_rpc as c
def write(name,data):
    p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def init():
    assert REPO==Path('E:/Business/fantasy-rpg-refiner')
    sources=['EC_HighCultureCity/StreetStudy01','ER_RootRetreat/CourtyardStudy01'];studies=[]
    for tag,src,offset,dest,bp in zip(['A','B'],sources,[[4000,-800,31],[4000,2500,31]],['StudyA_Street01','StudyB_Root01'],['BP_EC_StreetStudy01','BP_ER_CourtyardStudy01']):
        parent=REPO/'AssetSources/Architecture'/src/'Refiner';glass=parent/'GlassUpdate_01'
        m=json.loads((parent/'manifest.json').read_text());g=json.loads((glass/'manifest.json').read_text());assert g['status']=='review_ready'
        for line in (glass/'SHA256SUMS').read_text().splitlines():
            h,n=line.split(maxsplit=1);assert sha(glass/n)==h,n
        for e in m['exports']:assert sha(parent/e['path'])==e['sha256']
        studies.append(dict(tag=tag,parent=parent.as_posix(),glass_source=(glass/g['source_blend']).as_posix(),glass_source_sha256=g['source_blend_sha256'],
            mesh_manifest=m,glass_manifest=g,offset=offset,dest='/Game/Art/Architecture/'+dest,blueprint=bp))
    write('plan.json',dict(map='/Game/Prototype/Maps/Lvl_AssetLab',materials='/Game/Art/Materials/StudyAB_Review01',studies=studies))
    existing={}
    for folder in ['Content','AssetSources','Config','Source','Tools','docs']:
        for p in (REPO/folder).rglob('*'):
            if p.is_file() and not p.is_relative_to(ROOT) and '__pycache__' not in p.parts and not p.name.endswith('.blend1'):
                existing[p.relative_to(REPO).as_posix()]=sha(p)
    write('Evidence/files_before.json',existing)
    backup=REPO/'Saved/StudyABIntegration/Before/Lvl_AssetLab.umap';backup.parent.mkdir(parents=True,exist_ok=True)
    assert not backup.exists();shutil.copy2(REPO/'Content/Prototype/Maps/Lvl_AssetLab.umap',backup)
    assert sha(backup)==existing['Content/Prototype/Maps/Lvl_AssetLab.umap']
    print('INPUTS_VERIFIED_AND_LAB_BACKED_UP',len(existing))
def main():
    mode=sys.argv[1]
    if mode=='init':return init()
    c.connect()
    if mode=='schema':
        for group in sys.argv[2:]:
            r=c.rpc('tools/call',dict(name='describe_toolset',arguments=dict(toolset_name=group)))
            data=json.loads(r['content'][0]['text']);write('Evidence/schema_'+group.rsplit('.',1)[-1]+'.json',data)
            print(group,len(data.get('tools',[])))
    elif mode=='batch':
        p=ROOT/sys.argv[2];assert p.parent==ROOT
        data=c.value(c.call('editor_toolset.toolsets.programmatic.ProgrammaticToolset','execute_tool_script',script=p.read_text(encoding='utf-8')))
        if isinstance(data,str):data=json.loads(data)
        write('Evidence/'+p.stem+'.json',data);print(json.dumps(data,ensure_ascii=True)[:14000])
    elif mode=='native':
        p=(ROOT/sys.argv[2]).resolve();assert p.parent==ROOT
        c.call('SlateInspectorToolset.SlateInspectorToolset','Observe',ref='',maxDepth=45)
        snap=c.value(c.call('SlateInspectorToolset.SlateInspectorToolset','Snapshot',ref='',maxDepth=45))
        write('Evidence/console_before_'+p.stem+'.json',snap)
        start=snap.index('text "Cmd"');match=re.search(r'textbox[^\n]*\[ref=(\w+)\]',snap[start:]);assert match
        assert c.value(c.call('SlateInspectorToolset.SlateInspectorToolset','Click',ref=match.group(1)))
        print(c.value(c.call('SlateInspectorToolset.SlateInspectorToolset','Type',ref=match.group(1),text='py '+p.as_posix(),submit=True)))
    elif mode=='capture':
        view=json.loads((ROOT/'views.json').read_text())[sys.argv[2]]
        c.call('EditorToolset.EditorAppToolset','SetCameraTransform',transform=view)
        result=c.call('EditorToolset.EditorAppToolset','CaptureViewport',captureTransform=view,bShowUI=False,
            annotations=dict(gridSpacing=0,gridExtent=0,gridHeight=0,maxLabelDistance=0,classFilter=dict(refPath='/Script/Engine.Actor'),maxLabels=0))
        pixels=next((x for x in result['content'] if x['type']=='image'),None)
        if pixels is None:
            data=c.value(result);pixels=data.pop('image');write('Evidence/camera_'+sys.argv[2]+'.json',data)
        out=ROOT/'Previews'/(sys.argv[2]+'.png');out.parent.mkdir(exist_ok=True)
        out.write_bytes(base64.b64decode(pixels['data']));print('CAPTURED',out)
if __name__=='__main__':main()
