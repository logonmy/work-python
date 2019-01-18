#!/usr/bin/env python
# -*- coding: utf-8 -*-
import MySQLdb
import time
import chardet
import os


class MySqlUtil:
    def __init__(self, config):
        self.host = config.get('mysql.host')
        self.user = config.get('mysql.user')
        self.passwd = config.get('mysql.passwd')
        self.db = config.get('mysql.db')
        self.port = config.get('mysql.port')
        self.conn = None

    def _connect(self):
        self.conn = MySQLdb.connect(host=self.host, port=self.port, user=self.user,
                                    passwd=self.passwd, db=self.db, charset='utf8')
        self.conn.autocommit(False)

    def _get_conn(self):
        if self.conn is None:
            self._connect()
        return self.conn

    def close_conn(self):
        self._get_conn().close()

    def get_cursor(self, batch_query=False):
        return self._get_conn().cursor(None if not batch_query else MySQLdb.cursors.DictCursor)

    def commit(self):
        self._get_conn().commit()


class Util:
    def __init__(self):
        pass

    @staticmethod
    def remove_file(filepath):
        os.remove(filepath)

    @staticmethod
    def log(msg):
        print "%s: %s" % (time.strftime('%Y%m%d %H:%M:%S', time.localtime()), msg.decode('utf-8'))

    @staticmethod
    def check_file_encoding(file_path):
        with open(file_path, 'r') as f:
            result = chardet.detect(f.read(1000))
            if result['encoding'] != 'utf-8':
                raise Exception("文件的编码格式必须是utf-8!!!，当前文件编码为%s" % result['encoding'])

    @staticmethod
    def is_blank(x):
        return x is None or x == ''

    @staticmethod
    def first_non_blank(*args):
        for arg in args:
            if not Util.is_blank(arg):
                return arg
        return ''

    @staticmethod
    def get_config():

        class Config:
            def __init__(self, item_dict):
                self.item_dict = item_dict

            def get(self, k, d=None):
                return self.item_dict.get(k, d)

            def get_int(self, k, d=None):
                return int(self.get(k, d))

        config_items = {}
        with open('./config.ini') as f:
            for line in f.readlines():
                if line.strip() == '' or line[0:1] in (';', '#'):
                    continue
                key, value = line.strip().split('=')
                config_items[key.strip()] = value.strip()
        return Config(config_items)


if __name__ == '__main__':
    print Util.first_non_blank('', '3', '', 1)