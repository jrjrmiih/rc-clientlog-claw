import json

import time


class Tools:
    @staticmethod
    def get_timestr(json_str):
        try:
            json_obj = json.loads(json_str)
            time = json_obj['time']
        except Exception:
            time = ''
        return time

    @staticmethod
    def get_timestrf(timestr):
        try:
            timestamp = timestr / 1000
            time_local = time.localtime(timestamp)
            timestr = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
        except Exception:
            timestr = ''
        return timestr
