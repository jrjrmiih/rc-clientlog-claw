import pymysql

import config
from sink import Sink


class SinkMySql(Sink):
    def __init__(self):
        self.db = pymysql.connect('172.31.32.6', 'developer', '1234%^&*', 'rym_db')
        self.cursor = self.db.cursor()
        self._tablename = '2018_07_12'
        self._init_table()

    def __del__(self):
        self.db.close()

    def _init_table(self):
        create_template_list = (config.db_create_table, config.db_create_table_navi,
                                config.db_create_table_cmp, config.db_create_table_crash)
        self.cursor.execute("SELECT table_name FROM information_schema.TABLES"
                            " WHERE table_name = '{0}'".format(self._tablename))
        if self.cursor.rowcount == 0:
            for template in create_template_list:
                self.cursor.execute(template.format(self._tablename))

    def flush(self, sdkstate):
        record_list = sdkstate.record_list
        if len(record_list) > 0:
            self.cursor.executemany(config.db_insert_main_template.format(self._tablename), record_list)
            self.db.commit()

        record_list = sdkstate.state_navi.record_list
        if len(record_list) > 0:
            self.cursor.executemany(config.db_insert_navi_template.format(self._tablename), record_list)
            self.db.commit()

        record_list = sdkstate.state_cmp.record_list
        if len(record_list) > 0:
            self.cursor.executemany(config.db_insert_cmp_template.format(self._tablename), record_list)
            self.db.commit()

        record_list = sdkstate.crash_list
        if len(record_list) > 0:
            self.cursor.executemany(config.db_insert_crash_template.format(self._tablename), record_list)
            self.db.commit()

        sdkstate.clear_all_lists()
