class StateNavi:
    def __init__(self):
        self.req = 0
        self.succ = 0
        self.fail = 0
        self.url = None
        self.ip = None
        self.ccode = None  # 导航请求的 http response code。
        self.dura = None
        self.crash = None
        self.dcode = None  # 导航解析的结果码。
        self.ddata = None  # 导航解析的内容，同时也是 http navi request 的 body。

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
        self.url = None
        self.ip = None
        self.ccode = None
        self.dura = None
        self.crash = None
        self.dcode = None
        self.ddata =None

    def on_get(self, url, ip):
        self.req = self.req + 1
        self.url = url
        self.ip = None if ip == 'null' else ip

    def on_got(self, source, network, linenum, code, dura):
        self.ccode = code
        self.dura = dura
        if self.ccode == 200:
            self.succ = self.succ + 1
        else:
            self.fail = self.fail + 1

    def on_decode(self, source, network, linenum, code, data):
        self.dcode = code
        self.ddata = data
        if self.ccode is not None:
            record = (source.appid, source.userid, source.starttime, network, linenum,
                      self.url, self.ip, self.ccode, self.dura, None, self.dcode, self.ddata)
            self._record_list.append(record)
            self._clear_get()

    def on_crash(self, source, network, linenum, stacks):
        self.ccode = -1
        self.dura = None
        self.crash = stacks
        self.fail = self.fail + 1
        self.dcode = None
        self.ddata = None

        record = (source.appid, source.userid, source.starttime, network, linenum,
                  self.url, self.ip, self.ccode, self.dura, self.crash, self.dcode, self.ddata)
        self._record_list.append(record)
        self._clear_get()

