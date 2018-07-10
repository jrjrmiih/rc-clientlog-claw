from datetime import datetime


class Writer:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Writer, cls).__new__(cls)
            cls.instance.fw = open('summary.txt', 'a+')
            cls.instance.write((' log summary ' + datetime.now().strftime('%m-%d %H:%M:%S')).center(60, '-'))
        return cls.instance

    def __del__(self):
        self.fw.close()

    def write(self, string):
        self.fw.write(string + '\n')