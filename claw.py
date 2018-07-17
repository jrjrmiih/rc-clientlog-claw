from transitions import MachineError

from sdkstate import SdkState
from sink_mysql import SinkMySql
from source_folder import SourceFolder


class Claw:
    def __init__(self):
        self.source = SourceFolder()
        self.sink = SinkMySql()
        self.sdkstate = SdkState()

    def start(self):
        self.source.get_source_log(self.log_parse, self.log_parse_error, self.flush_db)

    def log_parse(self, json_obj_list):
        self.sdkstate.start()
        linenum = 0
        json_obj = None
        startindex = 0
        while True:
            try:
                for index in range(startindex, len(json_obj_list)):
                    linenum = json_obj_list[index][0]
                    json_obj = json_obj_list[index][1]
                    if json_obj['tag'] == 'Log-Opened':
                        self.sdkstate.start()
                    elif json_obj['tag'] == 'A-init-O':
                        self.sdkstate.init()
                    elif json_obj['tag'] == 'L-get_navi-T':
                        self.sdkstate.navi_get(json_obj)
                    elif json_obj['tag'] == 'L-get_navi-R':
                        self.sdkstate.navi_got(json_obj, self.source, linenum)
                    elif json_obj['tag'] == 'L-decode_navi-S':
                        self.sdkstate.navi_decode(json_obj, self.source, linenum)
                    elif json_obj['tag'] == 'A-connect-T':
                        self.sdkstate.cmp_aget(json_obj, self.source, linenum)
                    elif json_obj['tag'] == 'A-connect-R':
                        self.sdkstate.cmp_agot(json_obj, self.source, linenum)
                    elif json_obj['tag'] == 'P-connect-T':
                        self.sdkstate.cmp_pget(json_obj, self.source, linenum)
                    elif json_obj['tag'] == 'P-connect-R':
                        self.sdkstate.cmp_pgot(json_obj, self.source, linenum)
                    elif json_obj['tag'] == 'L-network_changed-S':
                        self.sdkstate.on_network_changed(json_obj)
                    elif json_obj['tag'] == 'L-crash-F':
                        self.sdkstate.crash(json_obj, self.source, linenum)
                self.sdkstate.end(json_obj, self.source, linenum)
            except KeyError as err:
                self.sdkstate.append_crash(self.source, linenum, 'KeyError', 'no key named ' + str(err))
                startindex = index + 1
                continue
            except MachineError as err:
                self.sdkstate.append_crash(self.source, linenum, 'StateError', json_obj['meta']['stacks'])
                startindex = index + 1
                continue
            break

    def log_parse_error(self, linenum, type, info):
        print('\nlog parse error: {0} +{1}, {2}: {3}'.format(self.source.filepath, linenum, type, info))
        self.sdkstate.append_crash(self.source, linenum, type, info)

    def flush_db(self):
        self.sink.flush(self.sdkstate)

claw = Claw()
claw.start()
