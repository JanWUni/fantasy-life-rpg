"""Run an own native inspection script via the observed MCP editor console.

Use for native API checks missing from the supported toolsets, not asset operations
that already have dedicated MCP tools.
"""
from pathlib import Path
import re
import sys
import ue_rpc as c

root=Path(__file__).resolve().parent
script=(root/sys.argv[1]).resolve()
assert script.parent==root and script.suffix=='.py' and script.is_file()
c.connect()
c.call('SlateInspectorToolset.SlateInspectorToolset','Observe',ref='w1',maxDepth=45)
snapshot=c.value(c.call('SlateInspectorToolset.SlateInspectorToolset','Snapshot',ref='w1',maxDepth=45))
start=snapshot.index('text "Cmd"')
match=re.search(r'textbox[^\n]*\[ref=(\w+)\]',snapshot[start:])
assert match,'No observed editor command box'
result=c.call('SlateInspectorToolset.SlateInspectorToolset','Type',ref=match.group(1),
              text='py '+script.as_posix(),submit=True)
print(c.value(result))
