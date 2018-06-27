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
        self.params = {'debug': False, 'appid': '', 'hour': '', 'start': '', 'end': '', 'dirs': []}
        opts, args = getopt.getopt(sys.argv[1:], 'd', ['appid=', 'hour=', 'start=', 'end=', 'dirs='])
        for key, value in opts:
            if key == '-d':
                self.params['debug'] = True
            if key == '--appid':
                self.params['appid'] = value
            if key == '--hour':
                self.params['hour'] = value
            if key == '--start':
                self.params['start'] = value
            if key == '--end':
                self.params['end'] = value
        self.params['dirs'] = args
        self._init_bootfile()

    def _init_bootfile(self):
        if os.path.isfile(BOOT_FILE):
            with open(BOOT_FILE, 'r', encoding='utf-8') as f:
                params = f.readline().strip()
                if params == self.params.__str__():
                    branch = input('info: found unfinished job，continue? [y/n] ').lower()
                    if branch == 'y':
                        return
        filter = self.params['appid'] + '_' + self.params['hour']
        with open(BOOT_FILE, 'w', encoding='utf-8') as f:
            f.write(self.params.__str__() + '\n')
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

    def get_logfiles_startline(self):
        logfiles = []
        startline = 1
        with open(BOOT_FILE, 'r', encoding='utf-8') as f:
            f.readline()
            lines = f.readlines()
            for line in lines:
                if not line.startswith('* '):
                    line = line.strip()
                    pos = line.rfind('+')
                    if pos > 0:
                        startline = int(line[pos + 1:])
                        line = line[0:pos - 1]
                    logfiles.append(line)
        return logfiles, startline

    def stop_parsing(self, filepath, linenum):
        with open(BOOT_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        with open(BOOT_FILE, 'w', encoding='utf-8') as fw:
            found = False
            for line in lines:
                if line.startswith('{') or line.startswith('* '):
                    fw.write(line)
                elif not found:
                    if line.startswith(filepath):
                        fw.write(filepath + ' +' + str(linenum) + '\n')
                        found = True
                    else:
                        fw.write('* ' + line)
                else:
                    fw.write(line)
