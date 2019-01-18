#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient
import time


class MyMongo:
    def __init__(self, host="140.143.94.171", port=27017, db_name="crawler", user_name="mongodbcrawler",
                 password="Shantianci56"):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.user_name = user_name
        self.password = password
        self.db = None
        self._init_db()

    def _init_db(self):
        conn = MongoClient(self.host, self.port)
        self.db = conn[self.db_name]
        if self.user_name and self.password:
            self.db.authenticate(self.user_name, self.password)

    def get_db(self):
        return self.db

    def save(self, task_id, info):
        info['timestamp'] = int(round(time.time() * 1000))
        self.db[task_id + '_' + time.strftime("%Y%m%d%H", time.localtime())].save(info)

# if __name__ == '__main__':
#     print MyMongo().get_conn()
