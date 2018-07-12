from abc import ABCMeta, abstractmethod


class Source(metaclass=ABCMeta):
    support_tag = [
        {
            'platver': ['Android-2.8.31', 'Android-2.8.32'],
            'tags': [
                'Log-Opened', 'A-init-O', 'L-network_changed-S', '2-bind_service-S',
                'L-get_navi-T', 'L-get_navi-R', 'L-get_navi-S', 'L-decode_navi-S',
                'A-connect-T', 'A-connect-R', 'P-connect-T', 'P-connect-R', 'P-connect-S',
                'A-disconnect-O'
            ]
        },
        {
            'platver': ['Android-2.9.0'],
            'tags': [
                'Log-Opened', 'A-init-O', 'L-network_changed-S', '2-bind_service-S',
                'G-upload_log-S', 'G-upload_log-E', 'G-upload_log-F', 'G-drop_log-E',
                'L-get_navi-T', 'L-get_navi-R', 'L-get_navi-S', 'L-decode_navi-S',
                'A-connect-T', 'A-connect-R', 'P-connect-T', 'P-connect-R', 'P-connect_entry-S',
                'A-disconnect-O'
            ]
        },
        {
            'platver': ['Android-2.9.1', 'Android-2.9.2'],
            'tags': [
                'Log-Opened', 'A-init-O', 'L-network_changed-S', '2-bind_service-S',
                'G-upload_log-S', 'G-upload_log-E', 'G-upload_log-F', 'G-drop_log-E',
                'L-get_navi-T', 'L-get_navi-R', 'L-get_navi-S', 'L-decode_navi-S',
                'A-connect-T', 'A-connect-R', 'P-connect-T', 'P-connect-R', 'P-connect_entry-S',
                'A-disconnect-O',
                'L-crash_main_trb-F', 'L-crash_main_ept-F', 'L-crash_ipc_ept-F',
                'L-crash_ipc_rmt-E', 'L-crash_ipc_rtm-F', 'L-crash_ipc_trb-F'
            ]
        }
    ]

    @property
    @abstractmethod
    def appid(self):
        pass

    @property
    @abstractmethod
    def userid(self):
        pass

    @property
    @abstractmethod
    def userip(self):
        pass

    @property
    @abstractmethod
    def platver(self):
        pass

    @abstractmethod
    def get_source_log(self, cb_parser, cb_error):
        pass

    def is_support_json(self, json_obj):
        for item in self.support_tag:
            if self.platver in item['platver'] and json_obj['tag'] in item['tags']:
                return True
        return False

    def tran_legal_json(self, json_obj):
        """
        transfer the json object form different platform & version to a uniform legal one.
        :param json_obj:
        :return: return the uniform json object.
        """
        del json_obj['level']
        del json_obj['type']
        ss = self.platver.lower().replace('-', '_').replace('.', '_')
        func = eval('self._tran_' + ss)
        json_obj = func(json_obj)
        return json_obj

    def _tran_android_2_8_28(self, json_obj):
        pass

    def _tran_android_2_8_29(self, json_obj):
        pass

    def _tran_android_2_8_30(self, json_obj):
        pass

    def _tran_android_2_8_31(self, json_obj):
        pass

    def _tran_android_2_8_32(self, json_obj):
        pass

    def _tran_android_2_9_0(self, json_obj):
        pass

    def _tran_android_2_9_1(self, json_obj):
        if json_obj['tag'].startswith('L-crash'):
            json_obj['tag'] = 'L-crash-F'
        print(json_obj)

    def _tran_android_2_9_2(self, json_obj):
        if json_obj['tag'].startswith('L-crash'):
            json_obj['tag'] = 'L-crash-F'
