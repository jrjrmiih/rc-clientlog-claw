from transitions.extensions import HierarchicalMachine as Machine

import ckey
import errdef


class Entity:
    states = [
         'start', {'name': 'navi', 'children': ['get', 'got', 'decode']}, 'end'
    ]
    transitions = [
        {'trigger': 'start', 'source': '*', 'dest': 'start', 'before': '_before_start'},
        {'trigger': 'navi_get', 'source': '*', 'dest': 'navi_get', 'before': '_before_navi_get'},
        {'trigger': 'navi_got', 'source': '*', 'dest': 'navi_got', 'before': '_before_navi_got'},
        ['navi_decode', '*', 'navi_decode'],
        ['crash', 'navi', 'navi_got'],
        ['end', '*', 'end']
    ]

    def __init__(self, claw):
        self.claw = claw
        self.machine = Machine(model=self, states=Entity.states, transitions=Entity.transitions, send_event=True)
        # abstract info.
        self.abs = {}
        self._init_navi()

    def _init_navi(self):
        self.navi = {ckey.REQ: 0, ckey.REP: 0, ckey.SUCCESS: 0, ckey.FAILED: 0, ckey.ERRCODE: {}}

    def _before_start(self, event):
        items = event.args[1].split(';;;')
        self.abs[ckey.STARTLINE] = event.args[0]
        self.abs[ckey.USERID] = items[2]
        self.abs[ckey.PLATVER] = items[4] + '-' + items[3]
        self.abs[ckey.USERIP] = items[5]
        self.abs[ckey.SUPPORT] = self.abs[ckey.PLATVER] in self.claw.support_list
        self.abs[ckey.NETSTATE] = ckey.NET_UNKNOWN
        self._init_navi()

    def _before_navi_get(self, event):
        self.navi[ckey.REQ] = self.navi[ckey.REQ] + 1

    def _before_navi_got(self, event):
        self.navi[ckey.REP] = self.navi[ckey.REP] + 1
        json_obj = event.args[0]
        if json_obj['meta']['code'] == 200:
            self.navi[ckey.SUCCESS] = self.navi[ckey.SUCCESS] + 1
        else:
            self.navi[ckey.FAILED] = self.navi[ckey.FAILED] + 1
            if json_obj['meta']['code'] == -1:
                if json_obj['meta']['stacks'] == '':
                    self._err_nav_handler(errdef.ERR_NAV_STACKS_EMPTY)
                elif json_obj['meta']['ip'] == 'null':
                    self._err_nav_handler(errdef.ERR_NAV_DNS_FAILED)
                elif 'lang.NullPointerException' in json_obj['meta']['stacks']:
                    self._err_nav_handler(errdef.ERR_NAV_NULLPOINTER)
                elif 'libcore.io.Streams.readAsciiLine' in json_obj['meta']['stacks']:
                    self._err_nav_handler(errdef.ERR_NAV_READASCIILINE)
                elif 'java.io.BufferedInputStream.streamClosed' in json_obj['meta']['stacks']:
                    self._err_nav_handler(errdef.ERR_NAV_STREAMCLOSED)
                elif 'Connection refused' in json_obj['meta']['stacks']:
                    self._err_nav_handler(errdef.ERR_NAV_CON_REFUSED)
                elif 'connect timed out' in json_obj['meta']['stacks']:
                    self._err_nav_handler(errdef.ERR_NAV_CON_TIMEOUT)
                elif 'failed to connect to' in json_obj['meta']['stacks']:
                    self._err_nav_handler(errdef.ERR_NAV_CON_FAILED)
                elif 'Stream closed' in json_obj['meta']['stacks']:
                    self._err_nav_handler(errdef.ERR_NAV_STREAM_CLOSED)
                elif 'SocketTimeoutException' in json_obj['meta']['stacks']:
                    self._err_nav_handler(errdef.ERR_NAV_SOCKET_TIMEOUT)
                elif 'SocketException: Connection reset' in json_obj['meta']['stacks']:
                    self._err_nav_handler(errdef.ERR_NAV_CON_RESET)
                elif 'unexpected end of stream on Connection' in json_obj['meta']['stacks']:
                    self._err_nav_handler(errdef.ERR_NAV_END_STREAM)
                elif 'recvfrom failed: ECONNRESET' in json_obj['meta']['stacks']:
                    self._err_nav_handler(errdef.ERR_NAV_ECONNRESET)
                elif 'SocketException: recvfrom failed: ETIMEDOUT' in json_obj['meta']['stacks']:
                    self._err_nav_handler(errdef.ERR_NAV_ETIMEDOUT)
                elif 'SocketException: Software caused connection abort' in json_obj['meta']['stacks']:
                    self._err_nav_handler(errdef.ERR_NAV_SOFTWARE_ABORT)
                elif 'ProtocolException: Too many follow-up requests' in json_obj['meta']['stacks']:
                    self._err_nav_handler(errdef.ERR_NAV_OKHTTP_TOOMANY_FOLLOWUP)
                elif 'SocketException: Network is unreachable' in json_obj['meta']['stacks']:
                    self._err_nav_handler(errdef.ERR_NAV_SOCKET_NETWORK_UNREACHABLE)
                elif 'ConnectException: Network is unreachable' in json_obj['meta']['stacks']:
                    self._err_nav_handler(errdef.ERR_NAV_CON_NETWORK_UNREACHABLE)
                elif 'SocketException: Connection timed out' in json_obj['meta']['stacks']:
                    self._err_nav_handler(errdef.ERR_NAV_CON_NETWORK_UNREACHABLE)
                elif 'SocketTimeoutException: failed to connect to' in json_obj['meta']['stacks']:
                    self._err_nav_handler(errdef.ERR_NAV_CON_NETWORK_UNREACHABLE)
                elif 'java.lang.NumberFormatException' in json_obj['meta']['stacks']:
                    self._err_nav_handler(errdef.ERR_NAV_NUMBER_FORMAT_EXCEPTION)
                elif 'com.android.okhttp' in json_obj['meta']['stacks']:
                    self._err_nav_handler(errdef.ERR_NAV_OKHTTP_CRASH)
                elif 'java.net.ProtocolException: Too many redirects' in json_obj['meta']['stacks']:
                    self._err_nav_handler(errdef.ERR_NAV_PROTOCOL_TOO_MANY_REDIRECTS)
                else:
                    self._raise_runtime_error()
            else:
                self._err_nav_handler(str(json_obj['meta']['code']))

    def _err_nav_handler(self, errtype):
        self.navi[ckey.ERRCODE][errtype] = \
            1 if errtype not in self.navi[ckey.ERRCODE] else self.navi[ckey.ERRCODE][errtype] + 1
        self.claw.write_debug_err(errtype)

    def _raise_runtime_error(self):
        self.claw.raise_runtime_err()
