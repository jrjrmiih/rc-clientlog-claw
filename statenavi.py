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

        self.record_list = []

    def reset(self):
        self.req = 0
        self.succ = 0
        self.fail = 0
        self.reset_once()

    def reset_once(self):
        self.url = ''
        self.ip = ''
        self.code = 0
        self.dura = 0
        self.crash = ''

    def on_get(self, url, ip):
        self.req = self.req + 1
        self.url = url
        self.ip = ip

    def on_got(self, source, linenum, code, dura):
        self.code = code
        self.dura = dura
        if self.code == 200:
            self.succ = self.succ + 1
        else:
            self.fail = self.fail + 1

        record = (source.appid, source.userid, source.starttime, linenum,
                  self.url, self.ip, self.code, self.dura, '')
        self.record_list.append(record)
        self.reset_once()

    def on_crash(self, source, linenum, stacks):
        self.code = -1
        self.dura = 0
        self.crash = stacks
        self.fail = self.fail + 1

        record = (source.appid, source.userid, source.starttime, linenum,
                  self.url, self.ip, self.code, self.dura, self.crash)
        self.record_list.append(record)
        self.reset_once()
