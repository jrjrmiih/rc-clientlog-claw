from abc import ABCMeta, abstractmethod

import config


class Source(metaclass=ABCMeta):
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

    @property
    @abstractmethod
    def starttime(self):
        pass

    @property
    @abstractmethod
    def endtime(self):
        pass

    @abstractmethod
    def get_source_log(self, cb_parser, cb_error):
        pass

    def is_support_json(self, json_obj):
        for item in config.support_tag:
            if self.platver in item['platver'] and json_obj['tag'] in item['tags']:
                return True
        return False

    def tran_legal_json(self, json_obj):
        """
        transfer the json object form different platform & version to a uniform legal one.
        :param json_obj:
        :return: return the uniform json object.
        """
        platver = self.platver.lower().replace('-', '_').replace('.', '_')
        func = eval('self._tran_' + platver)
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
        return json_obj

    def _tran_android_2_9_2(self, json_obj):
        if json_obj['tag'].startswith('L-crash'):
            json_obj['tag'] = 'L-crash-F'
        return json_obj