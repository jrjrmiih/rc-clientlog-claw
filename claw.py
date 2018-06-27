import datetime
import json
import os
import re
import sys
import time
from json import JSONDecodeError

import errdef
from boot import Boot

KEY_REQ = 'req'
KEY_REP = 'rep'
KEY_SUCCESS = 'success'
KEY_FAILED = 'failed'
KEY_ERRCODE = 'errcode'
KEY_EXTRA = 'extra'
KEY_FILELINE = 'fileline'
KEY_LINENUM = 'linenum'
KEY_USERID = 'userid'
KEY_PLATVER = 'platver'
KEY_HANDLE_PLATVER = 'handle_platver'
KEY_UNHANDLE_PLATVER = 'unhandle_platver'
KEY_USERIP = 'userip'

EVERY_LINES = 100000


class Claw:
    support_list = ('Android-2.8.29', 'Android-2.8.30', 'Android-2.8.31', 'Android-2.8.32', 'Android-2.9.0',
                    'Android-2.9.1')

    def __init__(self):
        self.boot = Boot()

        # open log analysis result file.
        self.fw = open('summary.txt', 'a+')
        self._write_summary((' log summary ' + datetime.datetime.now().strftime('%m-%d %H:%M:%S')).center(60, '-'))

        # whole log summary.
        self.logsum = {}
        self.logsum_handle_platver = {}
        self.logsum_unhandle_platver = {}
        self.logsum_navi = {KEY_REQ: 0, KEY_REP: 0, KEY_SUCCESS: 0, KEY_FAILED: 0, KEY_ERRCODE: {}}
        # single log abstract.
        self._init_logabs()

        # debug info.
        self.filepath = ''
        self.n = 0
        self.log = ''

    def __del__(self):
        if hasattr(self, 'fw'):
            self.fw.close()

    def start(self):
        logfiles, startline = self.boot.get_logfiles_startline()
        for n, filepath in enumerate(logfiles):
            self.filepath = filepath
            if n == 0:
                self._parse_file(n + 1, len(logfiles), startline)
            else:
                self._parse_file(n + 1, len(logfiles), 1)

    def _parse_file(self, index, total, startline):
        if os.path.isfile(self.filepath):
            info = '\rinfo: parsing {0} of {1} file ... \'{2}\' ... {3} of {4} * 100k lines.'
            with open(self.filepath, 'r', encoding='utf-8', errors="ignore") as f:
                lines = f.readlines()
                print(info.format(index, total, self.filepath, int(startline / EVERY_LINES),
                                  int(len(lines) / EVERY_LINES)), end='', flush=True)
                self._parse_lines(lines, startline, lambda n: print(
                    info.format(index, total, self.filepath, int(n / EVERY_LINES),
                                int(len(lines) / EVERY_LINES)), end='', flush=True))
        else:
            print('\rwarning: file \'{0}\' is not exists.'.format(self.filepath))

    def _write_summary(self, str):
        self.fw.write(str + '\n')

    def _parse_lines(self, lines, startline, callback):
        skip_file = False
        while True:
            try:
                # '+ 1' for matching the line number start form 1 not 0.
                total = len(lines)
                for self.n in range(startline, total + 1):
                    if self.n % EVERY_LINES == 1:
                        callback(self.n)
                    self.log = lines[self.n - 1].strip()
                    if self.log.startswith('fileName'):
                        skip_file = self._prolog_filename()
                    elif skip_file:
                        continue
                    elif self.log != '':
                        json_obj = json.loads(self.log)
                        json_obj = self._fix_kv_unpaired(json_obj)
                        if self._prolog_navi(json_obj):
                            continue
                self._dump_sum_clean()
            except JSONDecodeError as err:
                if self._skip_file_zd_x00_x00() or \
                        self._skip_file_unicode_encode_err():
                    skip_file = True
                    startline = self.n + 1
                    continue
                elif self._skip_line_zd_last_breaking() or \
                        self._skip_line_parallel_writing():
                    startline = self.n + 1
                    continue
                elif self._fix_invalid_return() or \
                        self._fix_lack_brace():
                    startline = self.n
                    continue
                else:
                    self._raise_runtime_error('JSONDecodeError')
            except RuntimeError as err:
                sys.exit(-1)
            except Exception:
                self._raise_runtime_error('Exception')
                sys.exit(-1)
            break

    def _dump_sum_clean(self):
        """
        dump the abstract of a single log to database, sum data, and clean.
        """
        # dump
        self._fix_get_navi_no_r()
        # sum
        self.logsum_navi[KEY_REQ] = self.logsum_navi[KEY_REQ] + self.logabs_navi[KEY_REQ]
        self.logsum_navi[KEY_REP] = self.logsum_navi[KEY_REP] + self.logabs_navi[KEY_REP]
        self.logsum_navi[KEY_SUCCESS] = self.logsum_navi[KEY_SUCCESS] + self.logabs_navi[KEY_SUCCESS]
        self.logsum_navi[KEY_FAILED] = self.logsum_navi[KEY_FAILED] + self.logabs_navi[KEY_FAILED]
        for key, value in self.logabs_navi[KEY_ERRCODE].items():
            if key not in self.logsum_navi[KEY_ERRCODE]:
                self.logsum_navi[KEY_ERRCODE][key] = value
            else:
                self.logsum_navi[KEY_ERRCODE][key] = self.logsum_navi[KEY_ERRCODE][key] + value
        # clean
        self._init_logabs()

    def _fix_get_navi_no_r(self):
        """
        Bug原因：部分版本，取导航成功时没有打印 'L-get_navi-R'。
        修复方案：如果没有 'L-get_navi-R'，则默认取导航成功。
        """
        target_platver = ('Android-2.8.30', 'Android-2.8.31')
        if self.logabs[KEY_PLATVER] in target_platver:
            self.logabs_navi[KEY_REP] = self.logabs_navi[KEY_REQ]
            self.logabs_navi[KEY_SUCCESS] = self.logabs_navi[KEY_REQ] - self.logabs_navi[KEY_FAILED]

    def _init_logabs(self):
        self.logabs = {KEY_PLATVER: ''}
        self.logabs_navi = {KEY_REQ: 0, KEY_REP: 0, KEY_SUCCESS: 0, KEY_FAILED: 0, KEY_ERRCODE: {}, KEY_EXTRA: []}

    def _prolog_filename(self):
        """
        process log(prolog), which is the filename part.
        :param log: the single log line.
        :return: 'True' if the log is handled.
        """
        self._dump_sum_clean()
        items = self.log.split(';;;')
        platver = items[4] + '-' + items[3]
        self.logabs[KEY_LINENUM] = self.n
        self.logabs[KEY_USERID] = items[2]
        self.logabs[KEY_PLATVER] = platver
        self.logabs[KEY_USERIP] = items[5]
        # add platver into handle or unhandle list.
        if platver in self.support_list:
            if platver not in self.logsum_handle_platver:
                self.logsum_handle_platver[platver] = 1
            else:
                self.logsum_handle_platver[platver] = self.logsum_handle_platver[platver] + 1
        else:
            if platver not in self.logsum_unhandle_platver:
                self.logsum_unhandle_platver[platver] = 1
            else:
                self.logsum_unhandle_platver[platver] = self.logsum_unhandle_platver[platver] + 1
        return platver not in self.support_list

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
            if json_obj['meta']['code'] == 200:
                self.logabs_navi[KEY_SUCCESS] = self.logabs_navi[KEY_SUCCESS] + 1
            else:
                self.logabs_navi[KEY_FAILED] = self.logabs_navi[KEY_FAILED] + 1
                if json_obj['meta']['code'] == -1:
                    if json_obj['meta']['stacks'] == '':
                        self._err_nav_handler(errdef.ERR_NAV_STACKS_EMPTY)
                    elif json_obj['meta']['ip'] == 'null':
                        self._err_nav_handler(errdef.ERR_NAV_DNS_FAILED)
                    elif 'lang.NullPointerException' in json_obj['meta']['stacks']:
                        self._err_nav_handler(errdef.ERR_NAV_NULLPOINTER)
                    elif 'libcore.io.Streams.readAsciiLine' in json_obj['meta']['stacks']:
                        self._err_nav_handler(errdef.ERR_NAV_READASCIILINE)
                    elif 'java.io.BufferedInputStream.streamClosed' in json_obj['meta']['stacks']:
                        self._err_nav_handler(errdef.ERR_NAV_STREAMCLOSED)
                    elif 'Connection refused' in json_obj['meta']['stacks']:
                        self._err_nav_handler(errdef.ERR_NAV_CON_REFUSED)
                    elif 'connect timed out' in json_obj['meta']['stacks']:
                        self._err_nav_handler(errdef.ERR_NAV_CON_TIMEOUT)
                    elif 'failed to connect to' in json_obj['meta']['stacks']:
                        self._err_nav_handler(errdef.ERR_NAV_CON_FAILED)
                    elif 'Stream closed' in json_obj['meta']['stacks']:
                        self._err_nav_handler(errdef.ERR_NAV_STREAM_CLOSED)
                    elif 'SocketTimeoutException' in json_obj['meta']['stacks']:
                        self._err_nav_handler(errdef.ERR_NAV_SOCKET_TIMEOUT)
                    elif 'SocketException: Connection reset' in json_obj['meta']['stacks']:
                        self._err_nav_handler(errdef.ERR_NAV_CON_RESET)
                    elif 'unexpected end of stream on Connection' in json_obj['meta']['stacks']:
                        self._err_nav_handler(errdef.ERR_NAV_END_STREAM)
                    elif 'recvfrom failed: ECONNRESET' in json_obj['meta']['stacks']:
                        self._err_nav_handler(errdef.ERR_NAV_ECONNRESET)
                    elif 'SocketException: recvfrom failed: ETIMEDOUT' in json_obj['meta']['stacks']:
                        self._err_nav_handler(errdef.ERR_NAV_ETIMEDOUT)
                    elif 'SocketException: Software caused connection abort' in json_obj['meta']['stacks']:
                        self._err_nav_handler(errdef.ERR_NAV_SOFTWARE_ABORT)
                    elif 'ProtocolException: Too many follow-up requests' in json_obj['meta']['stacks']:
                        self._err_nav_handler(errdef.ERR_NAV_OKHTTP_TOOMANY_FOLLOWUP)
                    elif 'SocketException: Network is unreachable' in json_obj['meta']['stacks']:
                        self._err_nav_handler(errdef.ERR_NAV_SOCKET_NETWORK_UNREACHABLE)
                    elif 'ConnectException: Network is unreachable' in json_obj['meta']['stacks']:
                        self._err_nav_handler(errdef.ERR_NAV_CON_NETWORK_UNREACHABLE)
                    elif 'SocketException: Connection timed out' in json_obj['meta']['stacks']:
                        self._err_nav_handler(errdef.ERR_NAV_CON_NETWORK_UNREACHABLE)
                    elif 'SocketTimeoutException: failed to connect to' in json_obj['meta']['stacks']:
                        self._err_nav_handler(errdef.ERR_NAV_CON_NETWORK_UNREACHABLE)
                    elif 'java.lang.NumberFormatException' in json_obj['meta']['stacks']:
                        self._err_nav_handler(errdef.ERR_NAV_NUMBER_FORMAT_EXCEPTION)
                    elif 'com.android.okhttp' in json_obj['meta']['stacks']:
                        self._err_nav_handler(errdef.ERR_NAV_OKHTTP_CRASH)
                    elif 'java.net.ProtocolException: Too many redirects' in json_obj['meta']['stacks']:
                        self._err_nav_handler(errdef.ERR_NAV_PROTOCOL_TOO_MANY_REDIRECTS)
                    else:
                        self._raise_runtime_error('navi')
                else:
                    self._err_nav_handler(str(json_obj['meta']['code']))

    def _fix_lack_brace(self):
        """
        Bug原因：当日志的 key 与 value 个数不匹配，需要拼接生成 json 时，最右边缺少一个'}'。
        典型案例：log = '{..."meta":{...}'
        修复方案：在最右边增加一个'}'。
        :param log: 可能有问题的 json 串。
        :return: 修复后的有效 json 串。
        """
        match = re.search('[^}]}$', self.log)
        if match is not None:
            self._debug_err_info(sys._getframe().f_code.co_name, '')
            self.log = self.log + '}'
            return True
        return False

    def _fix_invalid_return(self):
        """
        Bug原因：1. 日志在打印崩溃栈时，换行使用的是'\n'，导致 json.loads 出错。
                2. stacks 的最后不能出现换行符，否则 json.loads 会出错。
        典型案例：log = '{..."meta":{..."stacks":"...at java.net.PlainSocketImpl.socketConnect(Native Method)\n	..."}}'
        修复方案：1. 替换 '\n' 为 '\\n'。
                 2. 删除 stacks 行末的 '\\n'。
        """
        if '\\n"' in self.log or '\t' in self.log:
            self._debug_err_info(sys._getframe().f_code.co_name, '')
            self.log = self.log.replace('\\n"', '"')
            self.log = self.log.replace('\t', '    ')
            return True
        return False

    def _fix_kv_unpaired(self, json_obj):
        """
        Bug原因：当写日志的 key 与 value 个数不匹配时，生成 json['meta'] 中的键值没有分配。
        修复前提：log 必须是有效的 json 串。
        典型案例：log = '{..."meta":{"ptid":"19691-43738",
                 "code|duration|data|url|ip|stacks":"-1|2|http://navsg01-glb.ronghub.com/navi.xml|null|"}'
        修复方案：根据已有案例，键混在一起的键值尽量匹配，重新组合。
                 新的 log = '{..."meta":{"ptid":"19691-43738","code":-1,"duration":2,
                 "url":"http://navsg01-glb.ronghub.com/navi.xml","ip":"null","stacks":""}}'
        :param json_obj: 可能有问题的 json 对象。
        :return: 修复后的有效 json 对象。
        """
        target_platvers = ('Android-2.8.29')
        if self.logabs[KEY_PLATVER] in target_platvers:
            # value = '-1|2|http://navsg01-glb.ronghub.com/navi.xml|null|'
            key = 'code|duration|data|url|ip|stacks'
            if key in json_obj['meta']:
                self._debug_err_info(sys._getframe().f_code.co_name, '')
                vlist = json_obj['meta'][key].split('|')
                del json_obj['meta'][key]
                json_obj['meta']['code'] = int(vlist[0])
                json_obj['meta']['domain'] = vlist[2]
                json_obj['meta']['ip'] = vlist[3]
                json_obj['meta']['stacks'] = vlist[4]
                self.log = json.dumps(json_obj)
        return json_obj

    def _err_nav_handler(self, errtype):
        self._debug_err_info(errtype, '')
        if errtype not in self.logabs_navi[KEY_ERRCODE]:
            self.logabs_navi[KEY_ERRCODE][errtype] = 1
        else:
            self.logabs_navi[KEY_ERRCODE][errtype] = \
                self.logabs_navi[KEY_ERRCODE][errtype] + 1

    def _skip_file_unicode_encode_err(self):
        target_platvers = ('Android-2.8.29', 'Android-2.8.30', 'Android-2.8.31', 'Android-2.8.32',
                           'Android-2.9.0', 'Android-2.9.1')
        if self.logabs[KEY_PLATVER] in target_platvers:
            if not self.log.isprintable():
                self._debug_err_info(sys._getframe().f_code.co_name, '')
                return True
        return False

    def _skip_file_zd_x00_x00(self):
        """
        Bug原因：日志整合的文件中，会出现 n 多的 '\x00'，导致 json.loads() 失败。
                初步怀疑是日志收集服务器收到日志到合并大文件中的 bug。(赵东的 bug)
        典型案例：log = '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00...'
        修复方案：忽略这一行。
        """
        if self.log.startswith('\x00'):
            self._debug_err_info(sys._getframe().f_code.co_name, '')
            return True
        return False

    def _skip_line_parallel_writing(self):
        """
        问题描述：部分版本存在日志并发写入的 bug。
        处理方法：放弃这一行。
        复现版本：${platver_list}
        """
        target_platvers = ('Android-2.8.29', 'Android-2.8.30', 'Android-2.8.31', 'Android-2.8.32',
                           'Android-2.9.0', 'Android-2.9.1')
        if self.log.startswith('{{"time"') or \
                self.log.startswith('{"{"time"') or \
                self.log.startswith('{"t{"time"') or \
                self.log.startswith('{"ti{"time"') or \
                self.log.startswith('{"tim{"time"') or \
                self.log.startswith('{"time{"time"') or self.log.count('{"time"') == 2:
            if self.logabs[KEY_PLATVER] not in target_platvers:
                self._raise_runtime_error()
            self._debug_err_info(sys._getframe().f_code.co_name, '')
            return True
        return False

    def _skip_line_zd_last_breaking(self):
        """
        问题描述：部分版本存在日志没有写全的情况，怀疑是日志收集服务器收到日志到合并大文件中的 bug。(赵东的 bug)
        处理方法：放弃这一行。
        复现版本：${platver_list}
        """
        target_platvers = ('Android-2.8.29', 'Android-2.8.30', 'Android-2.8.31', 'Android-2.8.32',
                           'Android-2.9.0', 'Android-2.9.1')
        match = re.search('}}$', self.log)
        if match is None:
            if self.logabs[KEY_PLATVER] not in target_platvers:
                self._raise_runtime_error()
            self._debug_err_info(sys._getframe().f_code.co_name, '')
            return True
        return False

    def _debug_err_info(self, errname, infodict):
        if self.boot.params['debug']:
            errdict = {KEY_FILELINE: self.filepath + ' +' + str(self.n), KEY_PLATVER: self.logabs[KEY_PLATVER],
                       KEY_EXTRA: infodict}
            self._write_summary('debug = {0}: {1}'.format(errname, errdict))

    def _raise_runtime_error(self, info=''):
        errdict = {KEY_FILELINE: self.filepath + ' +' + str(self.n), KEY_PLATVER: self.logabs[KEY_PLATVER],
                   KEY_EXTRA: self.log}
        self._write_summary('runtime error = {0}'.format(errdict))
        self.output()
        self.boot.stop_parsing(self.filepath, self.logabs[KEY_LINENUM])
        time.sleep(1)
        print('\nraise: ' + info)
        raise RuntimeError

    def output(self):
        self._write_summary('-'.center(60, '-'))
        self.logsum[KEY_HANDLE_PLATVER] = self.logsum_handle_platver
        self.logsum[KEY_UNHANDLE_PLATVER] = self.logsum_unhandle_platver
        self.logsum['navi'] = self.logsum_navi
        self._write_summary('logsum = {0}\n'.format(self.logsum))


claw = Claw()
claw.start()
claw.output()
