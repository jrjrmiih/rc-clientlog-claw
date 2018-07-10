import json
import os
import re
import sys
import time

import ckey
from boot import Boot
from entity import Entity
from sum import Sum
from writer import Writer

EVERY_LINES = 100000


class Claw:
    support_list = ('Android-2.8.29', 'Android-2.8.30', 'Android-2.8.31', 'Android-2.8.32', 'Android-2.9.0',
                    'Android-2.9.1', 'Android-2.9.2')

    def __init__(self):
        self.boot = Boot()
        self.sum = Sum()
        self.entity = Entity(self)
        self.writer = Writer()

        # debug info.
        self.filepath = ''
        self.n = 0
        self.log = ''

    def start(self):
        logfiles, startline = self.boot.get_logfiles_startline()
        for n, filepath in enumerate(logfiles):
            self.filepath = filepath
            self._parse_file(n + 1, len(logfiles), startline if n == 0 else 1)
        self.boot.finish_parsing()
        print()

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

    def _parse_lines(self, lines, startline, callback):
        while True:
            try:
                # '+ 1' for matching the line number start form 1 not 0.
                total = len(lines)
                for self.n in range(startline, total + 1):
                    if self.n % EVERY_LINES == 0:
                        callback(self.n)
                    self.log = lines[self.n - 1].strip()
                    if self.log.startswith('fileName'):
                        self.entity.start(self.n, self.log)
                    elif self.log == '':
                        self.entity.end()
                        self.sum.flush(self.entity)
                    elif not self.entity.abs[ckey.SUPPORT]:
                        continue
                    else:
                        json_obj = json.loads(self.log)
                        json_obj = self._fix_kv_unpaired(json_obj)
                        if self._prolog_navi(json_obj):
                            continue
                        elif self._prolog_netstate(json_obj):
                            continue
                self.sum.flush(self.entity)
            except ValueError:
                if self._skip_file_zd_x00_x00() or \
                        self._skip_file_unicode_encode_err():
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
                    self.raise_runtime_err()
            except Exception:
                self.raise_runtime_err()
                sys.exit(-1)
            break

    def _dump_sum_clean(self):
        """
        dump the abstract of a single log to database, sum data, and clean.
        """
        # dump
        self._fix_get_navi_no_rep()
        # clean
        self.entity.reset()

    def _fix_get_navi_no_rep(self):
        """
        Bug原因：部分版本，取导航成功时没有打印 'L-get_navi-R'。
        修复方案：如果没有 'L-get_navi-R'，则默认取导航成功。
        """
        target_platver = ('Android-2.8.30', 'Android-2.8.31')
        if self.entity.abs[ckey.PLATVER] in target_platver:
            self.entity.navi[ckey.REP] = self.entity.navi[ckey.REQ]
            self.entity.navi[ckey.SUCCESS] = self.entity.navi[ckey.REQ] - self.entity.navi[ckey.FAILED]

    def _prolog_navi(self, json_obj):
        """
        process log(prolog), which belongs to navi.
        :param json_obj: json object of the single log line.
        :return: 'True' if the log is handled.
        """
        if json_obj['tag'] == 'L-get_navi-T':
            self.entity.navi_get()
        elif json_obj['tag'] == 'L-get_navi-R':
            self.entity.navi_got(json_obj)

    def _prolog_netstate(self, json_obj):
        """
        process log(prolog), which belongs to net state.
        :param json_obj: json object of the single log line.
        :return: 'True' if the log is handled.
        """
        if json_obj['tag'] == 'L-network_changed-S':
            if not json_obj['meta']['available']:
                self.entity.abs[ckey.NETSTATE] = ckey.NET_NONE
            elif json_obj['meta']['network'] == 'WIFI':
                self.entity.abs[ckey.NETSTATE] = ckey.NET_WIFI
            elif json_obj['meta']['network'] == '4G':
                self.entity.abs[ckey.NETSTATE] = ckey.NET_4G
            elif json_obj['meta']['network'] == '3G':
                self.entity.abs[ckey.NETSTATE] = ckey.NET_3G
            elif json_obj['meta']['network'] == '2G':
                self.entity.abs[ckey.NETSTATE] = ckey.NET_2G
            else:
                self.entity.abs[ckey.NETSTATE] = ckey.NET_UNKNOWN

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
            self.write_debug_err(sys._getframe().f_code.co_name)
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
            self.write_debug_err(sys._getframe().f_code.co_name)
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
        if self.entity.abs[ckey.PLATVER] in target_platvers:
            # value = '-1|2|http://navsg01-glb.ronghub.com/navi.xml|null|'
            key = 'code|duration|data|url|ip|stacks'
            if key in json_obj['meta']:
                self.write_debug_err(sys._getframe().f_code.co_name)
                vlist = json_obj['meta'][key].split('|')
                del json_obj['meta'][key]
                json_obj['meta']['code'] = int(vlist[0])
                json_obj['meta']['domain'] = vlist[2]
                json_obj['meta']['ip'] = vlist[3]
                json_obj['meta']['stacks'] = vlist[4]
                self.log = json.dumps(json_obj)
        return json_obj

    def _skip_file_unicode_encode_err(self):
        target_platvers = ('Android-2.8.29', 'Android-2.8.30', 'Android-2.8.31', 'Android-2.8.32',
                           'Android-2.9.0', 'Android-2.9.1')
        if self.entity.abs[ckey.PLATVER] in target_platvers:
            if not self.log.isprintable():
                self.write_debug_err(sys._getframe().f_code.co_name)
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
            self.write_debug_err(sys._getframe().f_code.co_name)
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
            if self.entity.abs[ckey.PLATVER] not in target_platvers:
                self.raise_runtime_err()
            self.write_debug_err(sys._getframe().f_code.co_name)
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
            if self.entity.abs[ckey.PLATVER] not in target_platvers:
                self.raise_runtime_err()
            self.write_debug_err(sys._getframe().f_code.co_name)
            return True
        return False

    def write_debug_err(self, title):
        if self.boot.params['debug']:
            errdict = {ckey.FILELINE: self.filepath + ' +' + str(self.n), ckey.PLATVER: self.entity.abs[ckey.PLATVER]}
            self.writer.write('debug = {0}: {1}'.format(title, errdict))

    def raise_runtime_err(self):
        errdict = {ckey.FILELINE: self.filepath + ' +' + str(self.n), ckey.PLATVER: self.entity.abs[ckey.PLATVER],
                   ckey.EXTRA: self.log}
        self.writer.write('runtime error = {0}'.format(errdict))
        self.output()
        self.boot.stop_parsing(self.filepath, self.entity.abs[ckey.STARTLINE])
        time.sleep(1)
        raise RuntimeError

    def output(self):
        self.writer.write('-'.center(60, '-'))
        self.writer.write(self.sum.summary())


claw = Claw()
claw.start()
claw.output()
