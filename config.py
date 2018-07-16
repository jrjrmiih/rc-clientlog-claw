NET_UNKNOWN = 'UNKNOWN'
NET_NONE = 'NONE'
NET_WIFI = 'WIFI'
NET_2G = '2G'
NET_3G = '3G'
NET_4G = '4G'

support_list = ('Android-2.8.29', 'Android-2.8.30', 'Android-2.8.31', 'Android-2.8.32', 'Android-2.9.0',
                'Android-2.9.1', 'Android-2.9.2')

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

db_create_table = \
    """ CREATE TABLE {0} (appid VARCHAR(8), userid VARCHAR(20), platver VARCHAR(15), userip VARCHAR(15),
        filepath VARCHAR(127), starttime DATETIME(3), endtime DATETIME(3),
        navireq TINYINT UNSIGNED, navisucc TINYINT UNSIGNED, navifail TINYINT UNSIGNED,
        cmpreq TINYINT UNSIGNED, cmpsucc TINYINT UNSIGNED, cmpfail TINYINT UNSIGNED,
        PRIMARY KEY(appid, userid, starttime))
    """

db_create_table_navi = \
    """ CREATE TABLE {0}_navi (uid INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        appid VARCHAR(8), userid VARCHAR(20), starttime DATETIME(3), network VARCHAR(10),
        pos VARCHAR(50), naviurl VARCHAR(50), naviip VARCHAR(15),
        code SMALLINT, dura INT UNSIGNED, crash TEXT)
    """

db_create_table_cmp = \
    """ CREATE TABLE {0}_cmp (uid INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        appid VARCHAR(8), userid VARCHAR(20), starttime DATETIME(3), network VARCHAR(10),
        pos VARCHAR(50), conntype TINYINT, cmpurls VARCHAR(200), useurl VARCHAR(50),
        scode SMALLINT, ncode SMALLINT, dura INT UNSIGNED)
    """

db_create_table_crash = \
    """ CREATE TABLE {0}_crash (uid INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        appid VARCHAR(8), userid VARCHAR(20), starttime DATETIME(3), network VARCHAR(10),
        pos VARCHAR(50), type VARCHAR(20), info TEXT)
    """

db_insert_main_template = \
    """ INSERT INTO {0} (appid, userid, platver, userip, filepath, starttime, endtime,
        navireq, navisucc, navifail, cmpreq, cmpsucc, cmpfail)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

db_insert_navi_template = \
    """ INSERT INTO {0}_navi (appid, userid, starttime, network, pos, naviurl, naviip, CODE, dura, crash)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

db_insert_cmp_template = \
    """ INSERT INTO {0}_cmp (appid, userid, starttime, network, pos, conntype, cmpurls, useurl, scode, ncode, dura)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

db_insert_crash_template = \
    """ INSERT INTO {0}_crash (appid, userid, starttime, network, pos, type, info)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
