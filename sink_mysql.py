import pymysql

import config
from sink import Sink


class SinkMySql(Sink):
    def __init__(self):
        self.db = pymysql.connect('172.31.32.6', 'developer', '1234%^&*', 'rym_db')
        self.cursor = self.db.cursor()
        self._init_table()

    def __del__(self):
        self.db.close()

    def _init_table(self):
        create_template_list = (config.db_create_table, config.db_create_table_navi,
                                config.db_create_table_cmp, config.db_create_table_crash)
        self.cursor.execute("SELECT table_name FROM information_schema.TABLES"
                            " WHERE table_name = 'clientlog_main'")
        if self.cursor.rowcount == 0:
            for template in create_template_list:
                self.cursor.execute(template)

    def flush(self, sdkstate):
        record_list_bundle = ((config.db_insert_main_template, sdkstate.record_list),
                              (config.db_insert_navi_template, sdkstate.state_navi.record_list),
                              (config.db_insert_cmp_template, sdkstate.state_cmp.record_list),
                              (config.db_insert_crash_template, sdkstate.crash_list))
        for insert_template, record_list in record_list_bundle:
            if len(record_list) > 0:
                self.cursor.executemany(insert_template, record_list)
        self.db.commit()
        sdkstate.clear_all_lists()
