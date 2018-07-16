from enum import Enum

from transitions.extensions import HierarchicalMachine as Machine

import config
from statecmp import StateCmp
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
        self.network = config.NET_UNKNOWN
        self._record_list = []
        self._crash_list = []
        self.state_navi = StateNavi()
        self.state_cmp = StateCmp()

    @property
    def record_list(self):
        return self._record_list

    @property
    def crash_list(self):
        return self._crash_list

    def on_network_changed(self, json_obj):
        if not json_obj['meta']['available']:
            self.network = config.NET_NONE
        else:
            self.network = json_obj['meta']['network'] if json_obj['meta']['network'] != '' else config.NET_UNKNOWN

    def on_enter_start(self, event):
        self._has_init = False
        self.network = config.NET_UNKNOWN
        self.state_navi.clear_all()
        self.state_cmp.clear_all()

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
        self.state_navi.on_got(source, self.network, linenum, code, dura)

    def on_enter_navi_crash(self, event):
        json_obj = event.args[0]
        source = event.args[1]
        linenum = event.args[2]
        stacks = json_obj['meta']['stacks']
        self.state_navi.on_crash(source, self.network, linenum, stacks)

    def on_enter_cmp_aget(self, event):
        self.state_cmp.on_aget()

    def on_enter_cmp_agot(self, event):
        json_obj = event.args[0]
        code = json_obj['meta']['code']
        self.state_cmp.on_agot(code)

    def on_enter_cmp_pget(self, event):
        json_obj = event.args[0]
        conntype = 1 if json_obj['meta']['strategy'] == 'serial' else 2
        cmpurls = json_obj['meta']['cached']
        useurl = json_obj['meta']['use']
        self.state_cmp.on_pget(conntype, cmpurls, useurl)

    def on_enter_cmp_pgot(self, event):
        json_obj = event.args[0]
        source = event.args[1]
        linenum = event.args[2]
        scode = json_obj['meta']['status_code']
        ncode = json_obj['meta']['native_code']
        dura = json_obj['meta']['duration']
        network = json_obj['meta']['network'] if json_obj['meta']['network'] != '' else config.NET_UNKNOWN
        self.state_cmp.on_pgot(source, network, linenum, scode, ncode, dura)

    def on_enter_end(self, event):
        source = event.args[1]
        record = (source.appid, source.userid, source.platver, source.userip,
                  source.filepath, source.starttime, source.endtime,
                  self.state_navi.req, self.state_navi.succ, self.state_navi.fail,
                  self.state_cmp.req, self.state_cmp.succ, self.state_cmp.fail)
        self._record_list.append(record)

    def append_crash(self, source, linenum, type, info):
        args = (source.appid, source.userid, source.starttime, self.network, linenum, type, info)
        self._crash_list.append(args)

    def clear_all_lists(self):
        self.state_navi.clear_all()
        self.state_cmp.clear_all()
        self._record_list.clear()
        self._crash_list.clear()
