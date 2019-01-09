#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from pymongo.errors import BulkWriteError
import datetime
import time
from dateutil.relativedelta import relativedelta
import logging


class OuterMongo:
    def __init__(self):
        self.db = MongoClient('140.143.94.171', 27017).crawler
        self.db.authenticate('mongodbcrawler', 'Shantianci56')

    @property
    def d_b(self):
        return self.db


class InnerMongo:
    def __init__(self):
        self.db = MongoClient('10.82.244.18', 27018).crawler
        self.db.authenticate('spider', 'spider')

    @property
    def d_b(self):
        return self.db


class DataTransfer:

    def __init__(self, tables):
        self.src_db = OuterMongo().d_b
        self.target_db = InnerMongo().d_b
        self.tables = tables

    def transfer(self):
        if type(self.tables) != list:
            self.tables = [self.tables]
        batch = 100
        for table in self.tables:
            skip = 0
            logger.info('begin transfer table ' + table)
            if self.target_db[table].count() > 0:
                logger.warning('target table is exists, continue ...')
                continue
            count = self.src_db[table].count()
            logger.info('num count is ' + str(count))
            while skip < count:
                rows = list(self.src_db[table].find({}).sort("_id").skip(skip).limit(batch))
                try:
                    self.target_db[table].insert_many(rows)
                except BulkWriteError, e:
                    logger.error('now the skip is ' + str(skip))
                    logger.error(e.details)
                    self.target_db[table].drop()
                    break
                skip += batch
            logger.info('delete src table ' + table)
            self.src_db[table].drop()
            logger.info("finish table " + table)


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler('data_transfer.log', mode='a')
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    while True:
        begin = datetime.datetime.now()
        last_hour = begin - relativedelta(hours=1)
        last_hour = last_hour.strftime('%Y%m%d%H')
        for coll_name in OuterMongo().d_b.list_collection_names():
            if coll_name[-10:] == str(last_hour):
                try:
                    DataTransfer(coll_name).transfer()
                except Exception, e:
                    logger.error('exec failed ', exc_info=True)
        now = datetime.datetime.now()
        delta_second = (now - begin).seconds
        if delta_second < 3600:
            time.sleep(3600 - delta_second)


