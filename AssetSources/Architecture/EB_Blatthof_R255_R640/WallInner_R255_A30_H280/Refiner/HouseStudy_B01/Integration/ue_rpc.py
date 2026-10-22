"""Local MCP client for this study's separate editor (port 8001)."""
import argparse
import base64
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parent
SESSION = None
COUNTER = 0


def rpc(method, params=None, notification=False):
    global SESSION, COUNTER
    COUNTER += 1
    body = dict(jsonrpc='2.0', method=method, params=params or {})
    if not notification:
        body['id'] = COUNTER
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream'}
    if SESSION:
        headers['Mcp-Session-Id'] = SESSION
    request = urllib.request.Request('http://127.0.0.1:8001/mcp', json.dumps(body).encode(), headers)
    with urllib.request.urlopen(request, timeout=600) as response:
        SESSION = response.headers.get('Mcp-Session-Id', SESSION)
        raw = response.read()
    if not raw:
        return None
    result = json.loads(raw)
    if 'error' in result:
        raise RuntimeError(result['error'])
    return result['result']


def connect():
    rpc('initialize', dict(protocolVersion='2024-11-05', capabilities={},
                           clientInfo=dict(name='HouseB01Integration', version='1')))
    rpc('notifications/initialized', notification=True)


def call(group, operation, **arguments):
    result = rpc('tools/call', dict(name='call_tool', arguments=dict(
        toolset_name=group, tool_name=operation, arguments=arguments)))
    if result.get('isError'):
        raise RuntimeError(result)
    return result


def value(result):
    texts = [json.loads(item['text']) for item in result['content'] if item['type'] == 'text']
    return texts[0].get('returnValue', texts[0]) if len(texts) == 1 else texts


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', choices=['describe', 'call', 'batch'])
    parser.add_argument('target')
    parser.add_argument('method', nargs='?')
    parser.add_argument('--args', default='{}')
    parser.add_argument('--out')
    args = parser.parse_args()
    connect()
    if args.operation == 'describe':
        result = rpc('tools/call', dict(name='describe_toolset', arguments=dict(toolset_name=args.target)))
        data = json.loads(result['content'][0]['text'])
    elif args.operation == 'batch':
        result = call('editor_toolset.toolsets.programmatic.ProgrammaticToolset',
                      'execute_tool_script', script=Path(args.target).read_text(encoding='utf-8'))
        data = value(result)
        if isinstance(data, str):
            data = json.loads(data)
    else:
        result = call(args.target, args.method, **json.loads(args.args))
        if args.out and any(item['type'] == 'image' for item in result['content']):
            item = next(item for item in result['content'] if item['type'] == 'image')
            Path(args.out).write_bytes(base64.b64decode(item['data']))
            data = {'image': args.out}
        else:
            data = value(result)
    if args.out and not (isinstance(data, dict) and 'image' in data):
        Path(args.out).write_text(json.dumps(data, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(json.dumps(data, ensure_ascii=True))
