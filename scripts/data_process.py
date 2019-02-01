#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient
import re, os


class DuplicateData:
    def __init__(self, src_table, ):
        self.db = OuterMongo().db
        self.src_table = src_table

    def process(self):
        count = self.db[self.src_table].count()
        skip = 0
        limit = 100
        urls = set()
        while skip < count:
            rows = self.db[self.src_table].find({}).sort("_id").skip(skip).limit(limit)
            for row in rows:
                result = row['result']
                for r in result:
                    if r['link'] not in urls:
                        urls.add(r['link'])
            skip += limit
        print 'finish...' + str(len(urls))


class OuterMongo:
    def __init__(self):
        self.db = MongoClient('140.143.94.171', 27017).crawler
        self.db.authenticate('mongodbcrawler', 'Shantianci56')

    @property
    def db(self):
        return self.db


class InnerMongo:
    def __init__(self):
        self.db = MongoClient('10.82.244.18', 27018).crawler
        self.db.authenticate('spider', 'spider')

    @property
    def db(self):
        return self.db


class DataTransfer:

    def __init__(self, tables):
        self.src_db = OuterMongo().db
        self.target_db = InnerMongo().db
        self.tables = tables

    def transfer(self):
        if type(self.tables) == str:
            self.tables = [self.tables]
        batch = 200
        for table in self.tables:
            skip = 0
            print 'begin transfer table ' + table
            if self.target_db[table].count() > 0:
                print 'target table is exists, ignore ...'
                # self.target_db[table].drop()
                # continue
            count = self.src_db[table].count()
            while skip < count:
                rows = self.src_db[table].find({}).sort("_id").skip(skip).limit(batch)
                self.target_db[table].insert_many(rows)
                skip += batch
            print 'delete src table '
            self.src_db[table].drop()
        print "finish ..."

    def drop(self):
        for table in self.tables:
            self.src_db[table].drop()


class UrlFetch:
    def __init__(self, tables):
        self.db = OuterMongo().db
        self.tables = tables

    def fetch(self):
        if type(self.tables) == str:
            self.tables = [self.tables]
        batch = 200
        for table in self.tables:
            skip = 0
            print 'begin fetch table ' + table
            count = self.db[table].count()
            if count == 0:
                continue
            with open(r'E:\work\data\tyc\\detail\\' + table + '.txt', 'w') as url_file:
                while skip < count:
                    rows = self.db[table].find({}, {'result': 1}).sort("_id").skip(skip).limit(batch)
                    for row in rows:
                        company = row['result']
                        if company:
                            if type(company) == dict:
                                url_file.write(company['GongSiLianJie'] + '\n')
                            elif type(company) == list:
                                url_file.writelines([c['GongSiLianJie'] + '\n' for c in
                                                     list(filter(lambda _c: _c['GongSiLianJie'] is not None, company))])
                            else:
                                print 'invalid type : '
                                print company
                    skip += batch
        print "finish ..."


class DianpingTelProcess:
    def __init__(self, table):
        self.dict_file = 'dianping_tel_transform_table.txt'
        self.db = OuterMongo().db
        self.table = table
        self.tel_pattern = re.compile(r'fn-\w+')
        self.tel_transform_table = dict()
        self.load()

    def load(self):
        with open(self.dict_file) as f:
            for l in f.readlines():
                if l.strip():
                    (k, v) = l.strip("\n").split("=")
                    self.tel_transform_table[k] = v

    def process(self):
        skip = 0
        batch = 200
        print 'begin process ... '
        count = self.db[self.table].count()
        while skip < count:
            rows = self.db[self.table].find({}, {'pageUrl': 1, 'result.tel': 1}).sort("_id").skip(skip).limit(batch)
            for row in rows:
                if row['result']:
                    matchs = re.findall(self.tel_pattern, row['result']['tel'])
                    if matchs:
                        for m in matchs:
                            if m not in self.tel_transform_table.keys():
                                print row['pageUrl'] + ' not found : ' + str(matchs)
                    else:
                        print 'not match ' + str(row)
            skip += batch
        print self.tel_transform_table
        with open('dianping_tel_transform_table.txt', 'w') as f:
            f.writelines([k + "=" + v + "\n" for k, v in self.tel_transform_table.items()])
        print 'finish ...'


class TianyanchaFontProcess:
    def __init__(self, tables):
        self.db = InnerMongo().db
        self.tables = tables
        # self.font_path_pattern = re.compile(r'https://static.tianyancha.com/fonts-styles/css/(\w+/?\w+)/font.css')
        self.font_path_set = set()
        self.count = 0

    def process(self):
        for table in self.tables:
            skip = 0
            batch = 200
            count = self.db[table].count()
            self.count += count
            print 'begin process ... ' + table + ' count ' + str(count)
            while skip < count:
                rows = self.db[table].find({}, {'fontUrl': 1}).sort("_id").skip(skip).limit(batch)
                for row in rows:
                    ft = row['fontUrl']
                    if ft and ft not in self.font_path_set:
                        self.font_path_set.add(ft)

                skip += batch
        print self.font_path_set
        print 'total ' + str(len(self.font_path_set))
        print 'record total ' + str(self.count)
        print 'finish ...'


class TeleCompany:
    def __init__(self, url_file, write_file):
        self.url_file = url_file
        self.write_file = write_file
        self.url_pattern = 'http://xn--%s.xn--vhquv.xn--vuq861b/v2/companyInfo/companyBasicInfoAll'

    def process(self):
        with open(self.url_file) as r:
            with open(self.write_file, 'w') as w:
                for line in r.readlines():
                    line = line.strip("\n\"").split(".")[0]
                    if line:
                        url = self.url_pattern % (line.decode('utf-8').encode('punycode'))
                        w.write(url + "\n")
                        # print url


class DataExport:
    def __init__(self, table, header, columns):
        import sys
        reload(sys)
        sys.setdefaultencoding('utf-8')
        self.header = header
        self.db = OuterMongo().db
        self.table = table
        if not columns or type(columns) != list:
            raise Exception("必须指定列(以数组的方式)")
        self.columns = columns

    def process(self):
        skip = 0
        batch = 200
        count = self.db[self.table].count()
        print 'begin process ... ' + self.table + ' count ' + str(count)
        with open('./data/' + self.table + '.csv', 'w') as f:
            f.write(self.header + '\n')
            while skip < count:
                print 'skip %d ......' % skip
                rows = self.db[self.table].find({}, self.columns).sort("_id").skip(skip).limit(batch)
                for row in rows:
                    for i, col in enumerate(self.columns):
                        if i > 0:
                            f.write(',')
                        try:
                            f.write('"%s"' % str(row[col]).replace('\n', '') if col in row and row[col] else '')
                        except Exception, e:
                            print e.message
                            print row
                    f.write('\n')
                skip += batch


class FetchId:
    def __init__(self, table_prefix, save_file):
        self.db = InnerMongo().db
        self.save_file = save_file
        self.table_prefix = table_prefix

    def process(self):
        with open(self.save_file, 'w') as sf:
            all_id = set()
            for coll_name in self.db.list_collection_names():
                if coll_name.find(self.table_prefix) == 0:
                    # skip = 0
                    # batch = 200
                    # count = self.db[coll_name].count()
                    # while skip < count:
                    #     # rows = self.db[coll_name].find({}, ['result.building_id']).sort("_id").skip(skip).limit(batch)
                    #     rows = self.db[coll_name].find({'result.point_lng': None}, ['pageUrl']).sort("_id").skip(skip).limit(batch)
                    #     for row in rows:
                    #         page_url = row['pageUrl']
                    #         all_id.add(page_url[page_url.rfind('=') + 1:])
                    #         # [all_id.add(x+"\n") for x in row['result']['building_id']]
                    #     skip += batch

                    rows = self.db[coll_name].find({}, ['result.JobId'])
                    for row in rows:
                        jobid = row['result']['JobId']
                        if not jobid:
                            print coll_name
                            continue
                        # all_id.add(page_url[page_url.rfind('=') + 1:]+"\n")
                        all_id.add(jobid + "\n")
            sf.writelines(all_id)
            print len(all_id)


class Search:
    def __init__(self, table_prefix, query):
        self.table_prefix = table_prefix
        if query == {}:
            raise Exception("query must not empty")
        self.query = query
        self.db = InnerMongo().db

    def search(self):
        for coll_name in self.db.list_collection_names():
            if coll_name.find(self.table_prefix) == 0:
                for row in self.db[coll_name].find(self.query).limit(1):
                    print 'find in ' + coll_name
                    print row
                    break


class Counter:
    def __init__(self, table_prefix, query):
        self.db = InnerMongo().db
        self.query = query
        self.table_prefix = table_prefix

    def process(self):
        count = 0
        for coll_name in self.db.list_collection_names():
            if coll_name.find(self.table_prefix) == 0:
                cnt = self.db[coll_name].count(self.query)
                # cnt = len(self.db[coll_name].distinct("pageUrl"))
                print '%s cnt is %d' % (coll_name, cnt)
                count += cnt
        print 'total cnt is %d ' % count


import datetime


class Rename:
    def __init__(self, table_prefix, new_table_prefix):
        self.db = InnerMongo().db
        self.new_table_prefix = new_table_prefix
        self.table_prefix = table_prefix

    def process(self):
        start_date = datetime.datetime.strptime('2019012518', '%Y%m%d%H')
        for coll_name in self.db.list_collection_names():
            if coll_name.find(self.table_prefix) == 0:
                # new_table_name = coll_name.replace(self.table_prefix, self.new_table_prefix)
                new_table_name = self.new_table_prefix + '_' + start_date.strftime('%Y%m%d%H')
                print 'from %s to %s' % (coll_name, new_table_name)
                self.db[coll_name].rename(new_table_name)
                start_date += datetime.timedelta(hours=1)


if __name__ == '__main__':
    # DataExport('task_1673_2018110611', '区域,名称,地址,等级,规模', ['zone', 'name', 'address', 'level', 'size']).process()
    # DataExport('task_1672_2019013017', '学校名称,所属区,学校地址,学校类别,学校性质,网站,联系电话,招生范围',
    #            ['name', 'area', 'address', 'type', 'attr', 'website', 'phone', 'source_range']).process()
    # DataExport('bendibao_2018110915', '名称,地址,经度,纬度', ['name', 'address', 'lon', 'lat']).process()
    # TeleCompany(r'E:\work\data\tele\sx_link.txt', r'E:\work\data\tele\sx_url.txt').process()
    # TeleCompany(r'E:\work\data\tele\42_1_2.txt', r'E:\work\data\tele\42_1_2_keyword.txt').process()
    # UrlFetch(['tianyancha_shenzhen_list_07']).fetch()
    # Search('tianyancha_level1_', {'pageUrl': 'https://api9.tianyancha.com/services/v3/t/common/baseinfoV5/26910314'}).search()
    # FetchId('task_1805_level0', r'E:\work\data\jobs\1805_leipin.txt').process()
    FetchId('task_1812_level1', r'E:\work\data\jobs\task_1812_level1.txt').process()
    # Counter('task_1812_level1', {}).process()
    # DataTransfer(['tianyancha_level0_2019012418']).transfer()
    # Rename('task_1812_level0_level1', 'task_1812_level1').process()
    # Search('task_1822_level1', {'data.id': 3169068818}).search()
    # Search('task_1822_level1', {'pageUrl': 'https://api9.tianyancha.com/services/v3/t/common/baseinfoV5/3169068818'}).search()
