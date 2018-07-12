import getopt
import json
import os
import re
import sys

import config
import tools
from source import Source

BOOT_FILE = '.loadfile'
LINE_UNIT = 100000


class SourceFolder(Source):
    def __init__(self):
        self._appid = None
        self._userid = None
        self._userip = None
        self._platver = None
        self._init_boot()

        self._file = None
        self._startline = 1
        self._index = 1
        self._support = False
        self._logfiles = []
        self._read_loadfile()

    @property
    def appid(self):
        return self._appid

    @property
    def userid(self):
        return self._userid

    @property
    def userip(self):
        return self._userip

    @property
    def platver(self):
        return self._platver

    def _init_boot(self):
        # init params.
        self._params = {'debug': False, 'appid': '', 'hour': '', 'dirs': []}
        opts, args = getopt.getopt(sys.argv[1:], 'd', ['appid=', 'hour=', 'dirs='])
        for key, value in opts:
            if key == '-d':
                self._params['debug'] = True
            if key == '--appid':
                self._params['appid'] = value
            if key == '--hour':
                self._params['hour'] = value
        self._params['dirs'] = args

        # if continue task.
        if os.path.isfile(BOOT_FILE):
            with open(BOOT_FILE, 'r', encoding='utf-8') as f:
                if f.readline().strip() == self._params.__str__():
                    if input('info: found unfinished job，continue? [y/n] ').lower() == 'y':
                        return
        # start new task.
        if self._params['hour'] == '':
            filter = self._params['appid'] + '_\d{4}.log'
        else:
            filter = self._params['appid'] + '_' + self._params['hour'] + '.log'
        with open(BOOT_FILE, 'w', encoding='utf-8') as f:
            f.write(self._params.__str__() + '\n')
            for dir in self._params['dirs']:
                if dir.endswith('/'):
                    dir = dir[:-1]
                if os.path.isdir(dir):
                    num = 0
                    for filename in os.listdir(dir):
                        if re.search(filter, filename) is not None:
                            num = num + 1
                            f.write(dir + '/' + filename + '\n')
                    print('info: found {0} file(s) in directory \'{1}\''.format(num, dir))
                else:
                    print('warning: directory \'{0}\' is not exists'.format(dir))

    def _read_loadfile(self):
        with open(BOOT_FILE, 'r', encoding='utf-8') as f:
            f.readline()
            lines = f.readlines()
            for line in lines:
                if not line.startswith('* '):
                    line = line.strip()
                    pos = line.rfind('+')
                    if pos > 0:
                        self._startline = int(line[pos + 1:])
                        line = line[0:pos - 1]
                    self._logfiles.append(line)

    def _write_loadfile(self):
        with open(BOOT_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        with open(BOOT_FILE, 'w', encoding='utf-8') as fw:
            found = False
            for line in lines:
                if line.startswith('{') or line.startswith('* '):
                    fw.write(line)
                elif not found:
                    if line.startswith(self._file):
                        fw.write(self._file + ' +' + str(self._startline) + '\n')
                        found = True
                    else:
                        fw.write('* ' + line)
                else:
                    fw.write(line)

    def get_source_log(self, cb_parser, cb_error):
        """
        get an unparsed json object list which from the first line of 'fileName' file,
        end with the last line of the 'fileName' file.
        :return: a json object list.
        """

        def __print_log(fileindex, filetotal, file, lineindex, linetotal):
            info = '\rinfo: parsing {0} of {1} file ... \'{2}\' ... {3} of {4} * 100k lines.'
            print(info.format(fileindex, filetotal, file, lineindex, linetotal), end='', flush=True)

        for n, self._file in enumerate(self._logfiles):
            if os.path.isfile(self._file):
                self._appid = tools.get_appid_from_filepath(self._file)
                with open(self._file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    __print_log(n, len(self._logfiles), self._file,
                                int(self._startline / LINE_UNIT), int(len(lines) / LINE_UNIT))
                    self._get_source_lines(lines, cb_parser,
                                           lambda: __print_log(n, len(self._logfiles), self._file,
                                                               int(self._index / LINE_UNIT),
                                                               int(len(lines) / LINE_UNIT)), cb_error)
            else:
                # TODO: file doesn't exist, output warning.
                pass
        os.remove(BOOT_FILE)

    def _get_source_lines(self, loglines, cb_parser, cb_info, cb_error):
        startline = self._startline
        json_obj_list = []
        while True:
            try:
                for self._index in range(startline, len(loglines) + 1):
                    if self._index % LINE_UNIT == 0:
                        cb_info()
                    log = loglines[self._index - 1].strip()
                    if log.startswith('fileName'):
                        self._parse_filename(log)
                        self._startline = self._index
                    elif log == '' and len(json_obj_list) > 0:
                        cb_parser(json_obj_list)
                        json_obj_list = []
                    elif not self._support:
                        pass
                    else:
                        json_obj = json.loads(log)
                        if self.is_support_json(json_obj):
                            json_obj = tools.fix_logjson_kv_unpaired(json_obj)
                            json_obj_list.append(self.tran_legal_json(json_obj))
            except ValueError:
                if tools.skip_logline_0x00(log) or \
                        tools.skip_logline_unicode_encode_err(log) or \
                        tools.skip_logline_breaking(log) or \
                        tools.skip_logline_parallel_writing(log):
                    startline = self._index + 1
                    continue
                log = tools.fix_logline_invalid_return(log)
                log = tools.fix_logline_lack_brace(log)
                try:
                    json.loads(log)
                except ValueError:
                    cb_error(self._file, self._startline, self._index, log)
                    startline = self._index + 1
                    continue
            except Exception as err:
                cb_error(self._file, self._startline, self._index, err)
                self._write_loadfile()
            break

    def _parse_filename(self, log):
        items = log.split(';;;')
        self._userid = items[2]
        self._platver = items[4] + '-' + items[3]
        self._userip = items[5]
        self._support = self._platver in config.support_list
