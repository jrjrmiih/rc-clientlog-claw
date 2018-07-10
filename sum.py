import pymysql

import ckey
from tools import Tools


class Sum:
    def __init__(self, claw):
        self.claw = claw
        self.db = pymysql.connect('172.31.32.6', 'developer', '1234%^&*', 'rym_db')
        self.cursor = self.db.cursor()
        self._check_table()
        self.sqlist = []

        self.navi = {ckey.REQ: 0, ckey.REP: 0, ckey.SUCCESS: 0, ckey.FAILED: 0, ckey.ERRCODE: {}}
        # handled platver.
        self.hpv = {}
        # unhandled platver.
        self.uhpv = {}

    def __del__(self):
        self.db.close()

    def summary(self):
        sql = """INSERT INTO 2018_07_10 (appid, userid, platver, userip, filepath, starttime, endtime, errdesc,
                 navireq, navirep, naviavedur, cmpreq, cmprep, cmpavedur)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s,
                 %s, %s, %s, %s, %s, %s)
              """
        self.cursor.executemany(sql, self.sqlist)
        self.db.commit()
        sumdict = {ckey.HPV: self.hpv, ckey.UHPV: self.uhpv, ckey.NAVI: self.navi}
        return sumdict.__str__()

    def flush(self, entity):
        # flush handled or unhandled platver.
        if entity.abs[ckey.SUPPORT]:
            self.hpv[entity.abs[ckey.PLATVER]] = \
                1 if entity.abs[ckey.PLATVER] not in self.hpv else self.hpv[entity.abs[ckey.PLATVER]] + 1
        else:
            self.uhpv[entity.abs[ckey.PLATVER]] = \
                1 if entity.abs[ckey.PLATVER] not in self.uhpv else self.uhpv[entity.abs[ckey.PLATVER]] + 1

        # flush navi.
        self.navi[ckey.REQ] = self.navi[ckey.REQ] + entity.navi[ckey.REQ]
        self.navi[ckey.REP] = self.navi[ckey.REP] + entity.navi[ckey.REP]
        self.navi[ckey.SUCCESS] = self.navi[ckey.SUCCESS] + entity.navi[ckey.SUCCESS]
        self.navi[ckey.FAILED] = self.navi[ckey.FAILED] + entity.navi[ckey.FAILED]
        for key, value in entity.navi[ckey.ERRCODE].items():
            self.navi[ckey.ERRCODE][key] = \
                value if key not in self.navi[ckey.ERRCODE] else self.navi[ckey.ERRCODE][key] + value

    def _check_table(self):
        tabname = 'summary'
        self.cursor.execute("SELECT table_name FROM information_schema.TABLES WHERE table_name = '{0}'".format(tabname))
        if self.cursor.rowcount == 0:
            self.cursor.execute("""
                CREATE TABLE {0} (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, starttime DATETIME, stoptime DATETIME,
                    platver TEXT, unplatver TEXT)
                """.format(tabname))

        tabname = '2018_07_10'
        self.cursor.execute("SELECT table_name FROM information_schema.TABLES WHERE table_name = '{0}'".format(tabname))
        if self.cursor.rowcount == 0:
            self.cursor.execute("""
                CREATE TABLE {0} (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    appid VARCHAR(8), userid VARCHAR(20), platver VARCHAR(15), userip VARCHAR(15),
                    filepath VARCHAR(127), starttime DATETIME, endtime DATETIME, errdesc TEXT,
                    navireq TINYINT UNSIGNED, navirep TINYINT UNSIGNED, naviavedur SMALLINT UNSIGNED,
                    cmpreq TINYINT UNSIGNED, cmprep TINYINT UNSIGNED, cmpavedur SMALLINT UNSIGNED)
                """.format(tabname))

    def insert_db(self, entity):
        tabname = '2018_07_10'
        value = (self.claw.appid, entity.abs[ckey.USERID], entity.abs[ckey.PLATVER],
                 entity.abs[ckey.USERIP], self.claw.filepath, Tools.get_timestrf(entity.abs[ckey.STARTTIME]),
                 Tools.get_timestrf(entity.abs[ckey.ENDTIME]), '', entity.navi[ckey.REQ], entity.navi[ckey.REP],
                 0, 0, 0, 0)
        self.sqlist.append(value)
