import datetime
import getopt
import json
import os
import sys

import pymysql as pymysql


class FileParser:
    app_id = None
    sdk_ver = None
    platform = None
    user_id = None
    start_time = None

    def __init__(self):
        self.db = pymysql.connect('172.31.32.6', 'developer', '1234%^&*', 'rym_db')
        cursor = self.db.cursor()
        cursor.execute('select * from client_log')
        results = cursor.fetchall()
        # for row in results:
        #     print('userid = %s', row[5])

    def __del__(self):
        self.db.close()

    def clear_data(self):
        self.sdk_ver = None
        self.platform = None
        self.user_id = None

    def parse_dir_files(self, dir_name, app_id):
        for file in os.listdir(dir_name):
            if app_id in file:
                with open(dir_name + '/' + file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines:
                        self.parse_line(line)

    def parse_line(self, line):
        if line.startswith('fileName'):
            items = line.split(';;;')
            self.sdk_ver = items[3]
            self.platform = items[4]
        elif line != '\n':
            json_str = json.loads(line)
            print(json_str['tag'])


class Claw:
    root_dir = None
    app_id = None
    start_time = None
    end_time = None
    current_datetime = None

    def __init__(self):
        self.para_init()
        self.file_parser = FileParser()
        self.file_parser.parse_dir_files(self.current_datetime.__str__(), self.app_id)

    def para_init(self):
        if len(sys.argv) == 1:
            print('### Usage: python3 ./claw.py <appId> <start_time> <end_time> ###')
            sys.exit(0)
        try:
            opts, args = getopt.getopt(sys.argv[3:], 'i:')
            self.root_dir = os.getcwd()
            self.app_id = sys.argv[1]
            self.start_time = sys.argv[2]
            self.end_time = sys.argv[3]
            self.current_datetime = datetime.date.fromtimestamp(int(self.start_time))
        except getopt.GetoptError as err:
            print('fatal:', err)
            sys.exit(1)


claw = Claw()

# for name, value in opts:
#     print(name, value)

# for new_dir in os.listdir(os.curdir):
#     print(new_dir)
