class StateNavi:
    def __init__(self):
        self.req = 0
        self.succ = 0
        self.fail = 0
        self.url = ''
        self.ip = ''
        self.code = 0
        self.dura = 0
        self.crash = ''

        self._record_list = []

    @property
    def record_list(self):
        return self._record_list

    def clear_all(self):
        self.clear_count()
        self._record_list.clear()

    def clear_count(self):
        self.req = 0
        self.succ = 0
        self.fail = 0

    def _clear_get(self):
        self.url = ''
        self.ip = ''
        self.code = 0
        self.dura = 0
        self.crash = ''

    def on_get(self, url, ip):
        self.req = self.req + 1
        self.url = url
        self.ip = ip

    def on_got(self, source, network, linenum, code, dura):
        self.code = code
        self.dura = dura
        if self.code == 200:
            self.succ = self.succ + 1
        else:
            self.fail = self.fail + 1

        record = (source.appid, source.userid, source.starttime, network, linenum,
                  self.url, self.ip, self.code, self.dura, '')
        self._record_list.append(record)
        self._clear_get()

    def on_crash(self, source, network, linenum, stacks):
        self.code = -1
        self.dura = 0
        self.crash = stacks
        self.fail = self.fail + 1

        record = (source.appid, source.userid, source.starttime, network, linenum,
                  self.url, self.ip, self.code, self.dura, self.crash)
        self._record_list.append(record)
        self._clear_get()
