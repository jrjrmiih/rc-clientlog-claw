import getopt
import os
import re
import sys

BOOT_FILE = 'load.ini'


class Boot:
    def __init__(self):
        # show help.
        if len(sys.argv) == 1:
            print('### Usage: python3 ./claw.py [--appid <app id>] [--start <start timestamp>]'
                  ' [--end <end timestamp>] <directory ...> ###')
            sys.exit(0)

        # init shell parameters.
        self.params = {'resume': False, 'appid': '', 'hour': '', 'start': '', 'end': '', 'dirs': []}
        opts, args = getopt.getopt(sys.argv[1:], '', ['resume', 'appid=', 'hour=', 'start=', 'end=', 'dirs='])
        for key, value in opts:
            if key == '--resume':
                self.params['resume'] = True
            if key == '--appid':
                self.params['appid'] = value
            if key == '--hour':
                self.params['hour'] = value
            if key == '--start':
                self.params['start'] = value
            if key == '--end':
                self.params['end'] = value
        self.params['dirs'] = args

        if not self.params['resume']:
            self._init_bootfile()
        self.startline = 1
        self.logfiles = []
        self._list_logfiles()

    def _init_bootfile(self):
        filter = self.params['appid'] + '_' + self.params['hour']
        with open(BOOT_FILE, 'w', encoding='utf-8') as f:
            for dir in self.params['dirs']:
                if os.path.isdir(dir):
                    filelist = []
                    for filepath in os.listdir(dir):
                        if re.search(filter, filepath) is not None:
                            filelist.append(filepath)
                    print('info: found {0} file(s) in directory \'{1}\''.format(len(filelist), dir))
                    for file in filelist:
                        f.write(dir + '/' + file + '\n')
                else:
                    print('warning: directory \'{0}\' is not exists'.format(dir))

    def _list_logfiles(self):
        with open(BOOT_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                if not line.startswith('* '):
                    line = line.strip()
                    pos = line.rfind('+')
                    if pos > 0:
                        self.startline = int(line[pos + 1:])
                        line = line[0:pos - 1]
                    self.logfiles.append(line)
