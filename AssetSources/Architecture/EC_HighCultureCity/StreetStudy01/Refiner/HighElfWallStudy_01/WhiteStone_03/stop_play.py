import json
def run():
    def call(n):return execute_tool('EditorToolset.EditorAppToolset.'+n,'{}').get('returnValue')
    was=call('IsPIERunning')
    if was:call('StopPIE')
    return dict(was_running=was)
