import getopt
import json
import os
import sys
# json keys.
import time
from json import JSONDecodeError

KEY_REQ = 'req'
KEY_REP = 'rep'
KEY_ERRCODE = 'errcode'
KEY_EXTRA = 'extra'

# error types.
ERR_NAV_DNS_FAILED = 'NAV-DNS-FAILED'
ERR_NAV_CON_REFUSED = 'NAV-CON-REFUSED'
ERR_NAV_STACKS_EMPTY = 'NAV-STACKS-EMPTY'
ERR_NAV_CON_TIMEOUT = 'NAV-CON-TIMEOUT'
ERR_NAV_CON_FAILED = 'NAV-CON-FAILED'
ERR_NAV_STREAM_CLOSED = 'NAV-STREAM-CLOSED'


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

        # whole log summary.
        self.logsum = {}
        self.logsum_platver = {}
        self.logsum_navi = {KEY_REQ: 0, KEY_REP: 0, KEY_ERRCODE: {}}
        # append every log abstract which enconter error, to show them all at then end.
        self.logerr_list = []
        # single log abstract.
        self.logabs = {}
        self.logabs_navi = {KEY_REQ: 0, KEY_REP: 0, KEY_ERRCODE: {}, KEY_EXTRA: []}
        # wheather encounter error when pasring single log to abstract.
        self.logabs_encounter_err = False
        # debug info.
        self.debug = {}
        self.n = 0
        self.log = ''

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
        sys.stdout.write('\rinfo: in directory \'{0}\' ... parsed 0 of {1} files.'.format(dirpath, len(logfiles)))
        sys.stdout.flush()
        for n, file in enumerate(logfiles):
            filepath = dirpath + '/' + file
            with open(filepath, 'r', encoding='utf-8') as f:
                self._parse_lines(filepath, f.readlines())
            sys.stdout.write('\rinfo: in directory \'{0}\' ... parsed {1} of {2} files.'
                             .format(dirpath, n + 1, len(logfiles)))
            sys.stdout.flush()
        print()

    def _parse_lines(self, filepath, lines):
        not_support = False
        start = 1
        while True:
            try:
                # '+ 1' for matching the line number start form 1 not 0.
                for self.n in range(start, len(lines) + 1):
                    # 'self.n == start and start != 1' means just recovered from exception, and 'log' has been fixed.
                    if self.n > start or start == 1:
                        # remove '\n' character at the end of log.
                        self.log = lines[self.n - 1][:-1]
                    if self.log.startswith('fileName'):
                        not_support = self._prolog_filename(filepath)
                    elif not_support:
                        continue
                    elif self.log != '':
                        json_obj = json.loads(self.log)
                        json_obj = self._fix_kv_unpaired(json_obj)
                        if self._prolog_start(json_obj):
                            continue
                        if self._prolog_navi(json_obj):
                            continue
                self._dump_sum_clean()
            except JSONDecodeError as err:
                self._fix_invalid_return()
                self._fix_lack_brace()
                start = self.n
                continue
            except RuntimeError:
                sys.exit(-1)
            except Exception:
                self._debug_ouput()
                sys.exit(-1)
            break

    def _dump_sum_clean(self):
        """
        dump the abstract of a single log to database, sum data, and clean.
        """
        # dump
        self.logabs['navi'] = self.logabs_navi
        if self.logabs_encounter_err:
            self.logerr_list.append(self.logabs)
        # sum
        self.logsum_navi[KEY_REQ] = self.logsum_navi[KEY_REQ] + self.logabs_navi[KEY_REQ]
        self.logsum_navi[KEY_REP] = self.logsum_navi[KEY_REP] + self.logabs_navi[KEY_REP]
        for key, value in self.logabs_navi[KEY_ERRCODE].items():
            if key not in self.logsum_navi[KEY_ERRCODE]:
                self.logsum_navi[KEY_ERRCODE][key] = value
            else:
                self.logsum_navi[KEY_ERRCODE][key] = self.logsum_navi[KEY_ERRCODE][key] + value
        # clean
        self.logabs = {}
        self.logabs_navi = {KEY_REQ: 0, KEY_REP: 0, KEY_ERRCODE: {}, KEY_EXTRA: []}
        self.logabs_encounter_err = False

    def _prolog_filename(self, filepath):
        """
        process log(prolog), which is the filename part.
        :param log: the single log line.
        :return: 'True' if the log is handled.
        """
        self._dump_sum_clean()
        items = self.log.split(';;;')
        platver = items[4] + '-' + items[3]
        self.logabs['file'] = filepath + ' +' + str(self.n)
        self.logabs['userid'] = items[2]
        self.logabs['platver'] = platver
        self.logabs['userip'] = items[5]
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
            self._dump_sum_clean()
            return True
        return False

    def _prolog_navi(self, json_obj):
        """
        process log(prolog), which belongs navi log.
        :param json_obj: json object of the single log line.
        :return: 'True' if the log is handled.
        """
        if json_obj['tag'] == 'L-get_navi-T':
            self.logabs_navi[KEY_REQ] = self.logabs_navi[KEY_REQ] + 1
        elif json_obj['tag'] == 'L-get_navi-R':
            self.logabs_navi[KEY_REP] = self.logabs_navi[KEY_REP] + 1
            if json_obj['meta']['code'] != 200:
                if json_obj['meta']['code'] == -1 and json_obj['meta']['ip'] == 'null':
                    self._err_nav_dns_failed(json_obj)
                elif json_obj['meta']['code'] == -1 and 'Connection refused' in json_obj['meta']['stacks']:
                    self._err_nav_con_refused(json_obj)
                elif json_obj['meta']['code'] == -1 and 'connect timed out' in json_obj['meta']['stacks']:
                    self._err_nav_con_timeout(json_obj)
                elif json_obj['meta']['code'] == -1 and 'failed to connect to' in json_obj['meta']['stacks']:
                    self._err_nav_con_failed(json_obj)
                elif json_obj['meta']['code'] == -1 and 'Stream closed' in json_obj['meta']['stacks']:
                    self._err_nav_stream_closed(json_obj)
                elif json_obj['meta']['code'] == -1 and json_obj['meta']['stacks'] == '':
                    self._err_nav_stacks_empty(json_obj)
                else:
                    self._debug_ouput()

    def _fix_lack_brace(self):
        """
        Bug原因：当日志的 key 与 value 个数不匹配，需要拼接生成 json 时，最右边缺少一个'}'。
        典型案例：log = '{..."meta":{...}'
        修复方案：在最右边增加一个'}'。
        :param log: 可能有问题的 json 串。
        :return: 修复后的有效 json 串。
        """
        if self.log[-2:] != '}}':
            self.log = self.log + '}'

    def _fix_invalid_return(self):
        """
        Bug原因：1. 日志在打印崩溃栈时，换行使用的是'\n'，导致 json.loads 出错。
                2. stacks 的最后不能出现换行符，否则 json.loads 会出错。
        典型案例：log = '{..."meta":{..."stacks":"...at java.net.PlainSocketImpl.socketConnect(Native Method)\n	..."}}'
        修复方案：1. 替换 '\n' 为 '\\n'。
                 2. 删除 stacks 行末的 '\\n'。
        """
        self.log = self.log.replace('\\n"', '"')
        self.log = self.log.replace('\t', '    ')

    def _fix_kv_unpaired(self, json_obj):
        """
        Bug原因：当写日志的 key 与 value 个数不匹配时，生成 json['meta'] 中的键值没有分配。
        修复前提：log 必须是有效的 json 串。
        典型案例：log = '{..."meta":{"ptid":"19691-43738","code|duration|data|url|ip|stacks":"-1|2|http://navsg01-glb.ronghub.com/navi.xml|null|"}'
        修复方案：根据已有案例，键混在一起的键值尽量匹配，重新组合。
                 新的 log = '{..."meta":{"ptid":"19691-43738","code":-1,"duration":2,:"url":"http://navsg01-glb.ronghub.com/navi.xml","ip":"null","stacks":""}}'
        :param json_obj: 可能有问题的 json 对象。
        :return: 修复后的有效 json 对象。
        """
        # Android-2.8.29
        # value = '-1|2|http://navsg01-glb.ronghub.com/navi.xml|null|'
        key = 'code|duration|data|url|ip|stacks'
        if key in json_obj['meta']:
            vlist = json_obj['meta'][key].split('|')
            del json_obj['meta'][key]
            json_obj['meta']['code'] = int(vlist[0])
            json_obj['meta']['domain'] = vlist[2]
            json_obj['meta']['ip'] = vlist[3]
            json_obj['meta']['stacks'] = vlist[4]
            self.log = json.dumps(json_obj)
        return json_obj

    def _err_nav_dns_failed(self, json_obj):
        """
        错误代码：'NAV-DNS-FAILED'
        错误描述：导航地址 DNS 解析失败。
        认定条件："tag":"L-get_navi-R", "meta":{"ip":"null"}
        复现版本：Android-2.8.29
        """
        self.logabs_encounter_err = True
        if ERR_NAV_DNS_FAILED not in self.logabs_navi[KEY_ERRCODE]:
            self.logabs_navi[KEY_ERRCODE][ERR_NAV_DNS_FAILED] = 1
        else:
            self.logabs_navi[KEY_ERRCODE][ERR_NAV_DNS_FAILED] = \
                self.logabs_navi[KEY_ERRCODE][ERR_NAV_DNS_FAILED] + 1
        err = ERR_NAV_DNS_FAILED + ':' + json_obj['meta']['domain']
        if err not in self.logabs_navi[KEY_EXTRA]:
            self.logabs_navi[KEY_EXTRA].append(err)

    def _err_nav_con_refused(self, json_obj):
        """
        错误代码：'NAV-CON-REFUSED'
        错误描述：导航连接失败，原因未知。
        认定条件："tag":"L-get_navi-R", "meta":{"stacks":"...Connection refused..."}
        复现版本：Android-2.8.29
        """
        self.logabs_encounter_err = True
        if ERR_NAV_CON_REFUSED not in self.logabs_navi[KEY_ERRCODE]:
            self.logabs_navi[KEY_ERRCODE][ERR_NAV_CON_REFUSED] = 1
        else:
            self.logabs_navi[KEY_ERRCODE][ERR_NAV_CON_REFUSED] = \
                self.logabs_navi[KEY_ERRCODE][ERR_NAV_CON_REFUSED] + 1
        err = ERR_NAV_CON_REFUSED + ':' + json_obj['meta']['domain'] + ';;;' + json_obj['meta']['ip']
        if err not in self.logabs_navi[KEY_EXTRA]:
            self.logabs_navi[KEY_EXTRA].append(err)

    def _err_nav_con_timeout(self, json_obj):
        """
        错误代码：'NAV-CON-TIMEOUT'
        错误描述：导航连接失败，连接超时。
        认定条件："tag":"L-get_navi-R", "meta":{"stacks":"...connect timed out..."}
        复现版本：Android-2.8.29
        """
        self.logabs_encounter_err = True
        if ERR_NAV_CON_TIMEOUT not in self.logabs_navi[KEY_ERRCODE]:
            self.logabs_navi[KEY_ERRCODE][ERR_NAV_CON_TIMEOUT] = 1
        else:
            self.logabs_navi[KEY_ERRCODE][ERR_NAV_CON_TIMEOUT] = \
                self.logabs_navi[KEY_ERRCODE][ERR_NAV_CON_TIMEOUT] + 1
        err = ERR_NAV_CON_TIMEOUT + ':' + json_obj['meta']['domain'] + ';;;' + json_obj['meta']['ip']
        if err not in self.logabs_navi[KEY_EXTRA]:
            self.logabs_navi[KEY_EXTRA].append(err)

    def _err_nav_con_failed(self, json_obj):
        """
        错误代码：'NAV-CON-FAILED'
        错误描述：导航连接失败，原因未知。
        认定条件："tag":"L-get_navi-R", "meta":{"stacks":"...failed to connect to..."}
        复现版本：Android-2.8.29
        """
        self.logabs_encounter_err = True
        if ERR_NAV_CON_FAILED not in self.logabs_navi[KEY_ERRCODE]:
            self.logabs_navi[KEY_ERRCODE][ERR_NAV_CON_FAILED] = 1
        else:
            self.logabs_navi[KEY_ERRCODE][ERR_NAV_CON_FAILED] = \
                self.logabs_navi[KEY_ERRCODE][ERR_NAV_CON_FAILED] + 1
        err = ERR_NAV_CON_FAILED + ':' + json_obj['meta']['domain'] + ';;;' + json_obj['meta']['ip']
        if err not in self.logabs_navi[KEY_EXTRA]:
            self.logabs_navi[KEY_EXTRA].append(err)

    def _err_nav_stream_closed(self, json_obj):
        """
        错误代码：'NAV-CON-FAILED'
        错误描述：导航连接失败，原因未知。
        认定条件："tag":"L-get_navi-R", "meta":{"stacks":"...failed to connect to..."}
        复现版本：Android-2.8.29
        """
        self.logabs_encounter_err = True
        if ERR_NAV_STREAM_CLOSED not in self.logabs_navi[KEY_ERRCODE]:
            self.logabs_navi[KEY_ERRCODE][ERR_NAV_STREAM_CLOSED] = 1
        else:
            self.logabs_navi[KEY_ERRCODE][ERR_NAV_STREAM_CLOSED] = \
                self.logabs_navi[KEY_ERRCODE][ERR_NAV_STREAM_CLOSED] + 1
        err = ERR_NAV_STREAM_CLOSED + ':' + json_obj['meta']['domain'] + ';;;' + json_obj['meta']['ip']
        if err not in self.logabs_navi[KEY_EXTRA]:
            self.logabs_navi[KEY_EXTRA].append(err)

    def _err_nav_stacks_empty(self, json_obj):
        """
        错误代码：'NAV-STACKS-EMPTY'
        错误描述：导航连接失败，打印不出崩溃栈，原因未知。
        认定条件："tag":"L-get_navi-R", "meta":{"stacks":""}
        复现版本：Android-2.8.29
        """
        self.logabs_encounter_err = True
        if ERR_NAV_STACKS_EMPTY not in self.logabs_navi[KEY_ERRCODE]:
            self.logabs_navi[KEY_ERRCODE][ERR_NAV_STACKS_EMPTY] = 1
        else:
            self.logabs_navi[KEY_ERRCODE][ERR_NAV_STACKS_EMPTY] = \
                self.logabs_navi[KEY_ERRCODE][ERR_NAV_STACKS_EMPTY] + 1
        err = ERR_NAV_CON_REFUSED + ':' + json_obj['meta']['domain'] + ';;;' + json_obj['meta']['ip']
        if err not in self.logabs_navi[KEY_EXTRA]:
            self.logabs_navi[KEY_EXTRA].append(err)

    def _debug_ouput(self):
        self.logsum['platver'] = self.logsum_platver
        print('logsum = {0}'.format(self.logsum))
        self.logabs['navi'] = self.logabs_navi
        print('logabs = {0}'.format(self.logabs))
        self.debug['n'] = self.n
        self.debug['log'] = self.log
        print('debug = {0}'.format(self.debug))
        time.sleep(1)
        raise RuntimeError

    def output(self):
        print('-'.center(60, '-'))
        for err_exp in self.logerr_list:
            print(err_exp)
        self.logsum['platver'] = self.logsum_platver
        self.logsum['navi'] = self.logsum_navi
        print('logsum = {0}'.format(self.logsum))


claw = Claw()
claw.start()
claw.output()
