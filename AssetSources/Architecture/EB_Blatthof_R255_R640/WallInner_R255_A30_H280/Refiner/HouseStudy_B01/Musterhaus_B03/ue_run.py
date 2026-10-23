"""Run supported editor MCP operations; console Python only for native verification gaps."""
from pathlib import Path
import json,re,sys,time
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'Integration'))
import ue_rpc as c
c.connect()
script=(ROOT/sys.argv[2]).resolve()
assert script.parent==ROOT and script.suffix=='.py'
if sys.argv[1]=='batch':
    data=c.value(c.call('editor_toolset.toolsets.programmatic.ProgrammaticToolset','execute_tool_script',script=script.read_text(encoding='utf-8')))
    if isinstance(data,str):data=json.loads(data)
    (ROOT/'Evidence').mkdir(exist_ok=True)
    (ROOT/'Evidence'/(script.stem+'.json')).write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(data))
else:
    assert sys.argv[1]=='native'
    c.call('SlateInspectorToolset.SlateInspectorToolset','Observe',ref='w1',maxDepth=45)
    snapshot=c.value(c.call('SlateInspectorToolset.SlateInspectorToolset','Snapshot',ref='w1',maxDepth=45))
    start=snapshot.index('text "Cmd"')
    match=re.search(r'textbox[^\n]*\[ref=(\w+)\]',snapshot[start:]);assert match
    print(c.value(c.call('SlateInspectorToolset.SlateInspectorToolset','Type',ref=match.group(1),text='py '+script.as_posix(),submit=True)))
