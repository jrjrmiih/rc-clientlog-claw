class StateNavi:
    def __init__(self):
        self.req = 0
        self.succ = 0
        self.fail = 0
        self.url = ''
        self.ip = ''
        self.code = 0
        self.dura = 0

    def reset(self):
        self.req = 0
        self.succ = 0
        self.fail = 0
        self.url = ''
        self.ip = ''
        self.code = 0
        self.dura = 0

    def on_get(self, url, ip):
        self.req = self.req + 1
        self.url = url
        self.ip = ip

    def on_got(self, code, dura):
        self.code = code
        self.dura = dura
        if self.code == 200:
            self.succ = self.succ + 1
        else:
            self.fail = self.fail + 1

    def on_crash(self, stacks):
        self.fail = self.fail + 1
        
