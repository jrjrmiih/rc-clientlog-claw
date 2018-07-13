from transitions.extensions import HierarchicalMachine as Machine

from statenavi import StateNavi


class SdkState:
    states = [
        'start',
        'init',
        {'name': 'navi', 'children': ['get', 'got', 'decode', 'crash']},
        {'name': 'cmp', 'children': ['aget', 'pget', 'state', 'pgot', 'agot']},
        'end'
    ]

    transitions = [
        ['start', '*', 'start'],
        ['init', '*', 'init'],
        ['navi_get', '*', 'navi_get'],
        ['navi_got', '*', 'navi_got'],
        ['crash', 'navi', 'navi_crash'],
        ['navi_decode', '*', 'navi_decode'],
        ['cmp_aget', '*', 'cmp_aget'],
        ['cmp_pget', '*', 'cmp_pget'],
        ['cmp_state', '*', 'cmp_state'],
        ['cmp_pgot', '*', 'cmp_pgot'],
        ['cmp_agot', '*', 'cmp_agot'],
        ['end', '*', 'end']
    ]

    def __init__(self):
        self.machine = Machine(model=self, states=SdkState.states, transitions=SdkState.transitions, send_event=True)
        self._has_init = False
        self.state_navi = StateNavi()

    def on_enter_start(self, event):
        self._has_init = False
        self.state_navi.reset()

    def on_enter_init(self, event):
        self._has_init = True

    def on_enter_navi_get(self, event):
        json_obj = event.args[0]
        url = json_obj['meta']['url']
        ip = json_obj['meta']['ip']
        self.state_navi.on_get(url, ip)

    def on_enter_navi_got(self, event):
        json_obj = event.args[0]
        source = event.args[1]
        linenum = event.args[2]
        code = json_obj['meta']['code']
        dura = json_obj['meta']['duration']
        self.state_navi.on_got(source, linenum, code, dura)

    def on_enter_navi_crash(self, event):
        json_obj = event.args[0]
        source = event.args[1]
        linenum = event.args[2]
        stacks = json_obj['meta']['stacks']
        self.state_navi.on_crash(source, linenum, stacks)

