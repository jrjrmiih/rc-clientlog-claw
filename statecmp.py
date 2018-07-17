class StateCmp:
    def __init__(self):
        self.req = 0
        self.succ = 0
        self.fail = 0

        self.conntype = 0  # 0: unknown, 1: serial, 2: parallel
        self.cmpurls = ''
        self.useurl = ''
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
        self.conntype = 0
        self.cmpurls = ''
        self.useurl = ''

    def on_aget(self):
        self.req = self.req + 1

    def on_agot(self, code):
        if code == 0:
            self.succ = self.succ + 1
        else:
            self.fail = self.fail + 1

    def on_pget(self, conntype, cmpurls, useurl):
        self.conntype = conntype
        self.cmpurls = cmpurls
        self.useurl = useurl

    def on_pgot(self, source, network, linenum, scode, ncode, dura):
        record = (source.appid, source.userid, source.starttime, network, linenum,
                  self.conntype, self.cmpurls, self.useurl, scode, ncode, dura)
        self._record_list.append(record)
