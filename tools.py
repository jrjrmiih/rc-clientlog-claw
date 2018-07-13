import json
import re

import time


def get_appid_from_filepath(filepath):
    filename = filepath[filepath.rfind('/') + 1:]
    return filename[filename.find('_') + 1:filename.rfind('_')]


def get_timestr(json_str):
    """
    获取文件 fileName 下的第一行日志的格式化时间。
    """
    try:
        json_obj = json.loads(json_str)
        timestamp = json_obj['time'] / 1000
        time_local = time.localtime(timestamp)
        timestr = time.strftime("%Y-%m-%d %H:%M:%S", time_local) + '.' + str(json_obj['time'] % 1000)
    except Exception:
        timestr = ''
    return timestr


def skip_logline_0x00(log):
    """
    Bug原因：日志整合的文件中，会出现 n 多的 '\x00'，导致 json.loads() 失败。
            初步怀疑是日志收集服务器收到日志到合并大文件中的 bug。(赵东的 bug)
    典型案例：log = '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00...'
    修复方案：忽略这一行。
    """
    if log.startswith('\x00'):
        return True
    return False


def skip_logline_unicode_encode_err(log):
    """
    问题描述：部分版本存在日志不是以 utf-8 形式写入的情况。
    处理方法：放弃这一行。
    复现版本：
    :return: 是否是该问题。
    """
    if not log.isprintable():
        return True
    return False


def skip_logline_breaking(log):
    """
    问题描述：部分版本存在日志没有完整写入的情况，通常出现在单个日志文件的最后一行。
    处理方法：放弃这一行。
    复现版本：
    :return: 是否是该问题。
    """
    match = re.search('}}$', log)
    if match is None:
        return True
    return False


def skip_logline_parallel_writing(log):
    """
    问题描述：部分版本存在日志并发写入的 bug。
    处理方法：放弃这一行。
    复现版本：
    :return: 是否是该问题。
    """
    if log.startswith('{{"time"') or \
            log.startswith('{"{"time"') or \
            log.startswith('{"t{"time"') or \
            log.startswith('{"ti{"time"') or \
            log.startswith('{"tim{"time"') or \
            log.startswith('{"time{"time"') or log.count('{"time"') == 2:
        return True
    return False


def fix_logline_invalid_return(log):
    """
    Bug原因：1. 日志在打印崩溃栈时，换行使用的是'\n'，导致 json.loads 出错。
            2. stacks 的最后不能出现换行符，否则 json.loads 会出错。
    典型案例：log = '{..."meta":{..."stacks":"...at java.net.PlainSocketImpl.socketConnect(Native Method)\n	..."}}'
    修复方案：1. 替换 '\n' 为 '\\n'。
             2. 删除 stacks 行末的 '\\n'。
    :param log: 可能有问题的 json 串。
    :return: 修复后的 json 串。
    """
    if '\\n"' in log or '\t' in log:
        log = log.replace('\\n"', '"')
        log = log.replace('\t', '    ')
    return log


def fix_logline_lack_brace(log):
    """
    Bug原因：当日志的 key 与 value 个数不匹配，需要拼接生成 json 时，最右边缺少一个'}'。
    典型案例：log = '{..."meta":{...}'
    修复方案：在最右边增加一个'}'。
    :param log: 可能有问题的 json 串。
    :return: 修复后的 json 串。
    """
    match = re.search('[^}]}$', log)
    if match is not None:
        log = log + '}'
    return log


def fix_logjson_kv_unpaired(json_obj):
    """
    Bug原因：当写日志的 key 与 value 个数不匹配时，生成 json['meta'] 中的键值没有分配。
    修复前提：log 必须是有效的 json 串。
    典型案例：log = '{..."meta":{"ptid":"19691-43738",
             "code|duration|data|url|ip|stacks":"-1|2|http://navsg01-glb.ronghub.com/navi.xml|null|"}'
    修复方案：根据已有案例，键混在一起的键值尽量匹配，重新组合。
             新的 log = '{..."meta":{"ptid":"19691-43738","code":-1,"duration":2,
             "url":"http://navsg01-glb.ronghub.com/navi.xml","ip":"null","stacks":""}}'
    :param json_obj: 可能有问题的 json 对象。
    :return: 修复后的 json 对象。
    """
    # value = '-1|2|http://navsg01-glb.ronghub.com/navi.xml|null|'
    key = 'code|duration|data|url|ip|stacks'
    if key in json_obj['meta']:
        vlist = json_obj['meta'][key].split('|')
        del json_obj['meta'][key]
        json_obj['meta']['code'] = int(vlist[0])
        json_obj['meta']['domain'] = vlist[2]
        json_obj['meta']['ip'] = vlist[3]
        json_obj['meta']['stacks'] = vlist[4]
    return json_obj
