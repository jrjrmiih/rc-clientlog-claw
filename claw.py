import getopt
import json
import os
import sys


class Claw:
    support_list = ('Android-2.8.29', 'Android-2.8.30', 'Android-2.8.31', 'Android-2.8.32')

    def __init__(self):
        if len(sys.argv) == 1:
            print('### Usage: python3 ./claw.py [--appid <app id>] [--start <start timestamp>]'
                  ' [--end <end timestamp>] <directory ...> ###')
            sys.exit(0)
        # init shell parameters.
        opts, args = getopt.getopt(sys.argv[1:], '', ['help', 'appid=', 'start=', 'end=', 'dirs='])
        self.shell_paras = {}
        for key, value in opts:
            if key == '--appid':
                self.shell_paras['appid'] = value
            if key == '--start':
                self.shell_paras['start'] = value
            if key == '--end':
                self.shell_paras['end'] = value
        self.shell_paras['dirs'] = args
        # init members.
        self.file = ''
        self.logsum = {}
        self.logsum_platver = {}
        self.logabs = {}
        self.logabs_navi = {}

    def start(self):
        for dirpath in self.shell_paras['dirs']:
            if os.path.isdir(dirpath):
                self._parse_files(dirpath, os.listdir(dirpath))
            else:
                print('warning: directory \'{0}\' is not exists'.format(dirpath))

    def _parse_files(self, dirpath, files):
        logfiles = []
        for file in files:
            if self.shell_paras['appid'] in file:
                logfiles.append(file)
        if len(logfiles) == 0:
            sys.stdout.write('\rinfo: parsing directory \'{0}\' ... 0 of {1} files.'.format(dirpath, len(logfiles)))
        else:
            sys.stdout.write('\rinfo: parsing directory \'{0}\' ... 1 of {1} files.'.format(dirpath, len(logfiles)))
        sys.stdout.flush()
        for n, file in enumerate(logfiles):
            with open(dirpath + '/' + file, 'r', encoding='utf-8') as f:
                self.file = file
                self._parse_lines(file, f.readlines())
            sys.stdout.write('\rinfo: parsing directory \'{0}\' ... {1} of {2} files.'
                             .format(dirpath, n + 1, len(logfiles)))
            sys.stdout.flush()
        print()

    def _parse_lines(self, file, lines):
        not_support = False
        line = None
        log = None
        try:
            for line, log in enumerate(lines):
                # remove '\n' character at the end of log.
                log = log[:-1]
                if log.startswith('fileName'):
                    not_support = self._prolog_filename(log)
                elif not_support:
                    continue
                elif log != '':
                    json_obj = json.loads(log)
                    if self._prolog_start(json_obj):
                        continue
                    if self._prolog_navi(json_obj):
                        continue
        except Exception as err:
            self._debug_ouput(err, file, line, log)
            sys.exit(-1)

    def _dump_and_clean(self):
        """
        dump the abstract data of a log part to database, and clean the data.
        """
        # dump
        pass
        # clean
        self.logabs = {}
        self.logabs_navi = {'req': 0, 'rep': 0, 'code': {}}

    def _prolog_filename(self, line):
        """
        process log(prolog), which is the filename part.
        :param line: the single log line.
        :return: 'True' if the log is handled.
        """
        self._dump_and_clean()
        items = line.split(';;;')
        self.logabs['userid'] = items[2]
        self.logabs['sdkver'] = items[3]
        self.logabs['platform'] = items[4]
        platver = self.logabs['platform'] + '-' + self.logabs['sdkver']
        if platver not in self.logsum_platver:
            self.logsum_platver[platver] = 1
        else:
            self.logsum_platver[platver] = self.logsum_platver[platver] + 1
        return platver not in self.support_list

    def _prolog_start(self, json_obj):
        """
        process log(prolog), which is the first log after app start.
        :param json_obj: json object of the single log line.
        :return: 'True' if the log is handled.
        """
        if json_obj['tag'] == 'Log_Opened':
            self._dump_and_clean()
            return True
        return False

    def _prolog_navi(self, json_obj):
        """
        process log(prolog), which belongs navi log.
        :param json_obj: json object of the single log line.
        :return: 'True' if the log is handled.
        """
        if json_obj['tag'] == 'L-get_navi-T':
            self.logabs_navi['req'] = self.logabs_navi['req'] + 1
        elif json_obj['tag'] == 'L-get_navi-R':
            self.logabs_navi['rep'] = self.logabs_navi['rep'] + 1
            if str(json_obj['meta']['code']) not in self.logabs_navi['code']:
                self.logabs_navi['code'][str(json_obj['meta']['code'])] = 1
            else:
                self.logabs_navi['code'][str(json_obj['meta']['code'])] = \
                    self.logabs_navi['code'][str(json_obj['meta']['code'])] + 1

    def _debug_ouput(self, err, file='', line=0, log=''):
        if file != '':
            print('file = \'{0}\', line = {1}, log = \'{2}\''.format(file, line, log))
        self.logsum['platver'] = self.logsum_platver
        print('logsum = {0}'.format(self.logsum))
        self.logabs['navi'] = self.logabs_navi
        print('logabs = {0}'.format(self.logabs))
        raise err

    def output(self):
        print('-'.center(60, '-'))
        self.logsum['platver'] = self.logsum_platver
        print('logsum = {0}'.format(self.logsum))


claw = Claw()
claw.start()
claw.output()
