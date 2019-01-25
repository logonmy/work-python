#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import time
from pymongo import MongoClient


class ParseProcess:
    transform_table = {}

    def __init__(self):
        self.dict_file = 'transfer_dict.txt'
        self.db = MongoClient('140.143.94.171', 27017).crawler
        self.db.authenticate('mongodbcrawler', 'Shantianci56')
        self.tel_pattern = re.compile(r'<span class=\"(.*?)\".*?/?>|</span>')
        self.load()

    def load(self):
        with open(self.dict_file) as f:
            for l in f.readlines():
                if l.strip():
                    (k, v) = l.strip("\n").split("=")
                    ParseProcess.transform_table[k] = v

    @staticmethod
    def transform(m):
        m1 = m.group(1)
        return ParseProcess.transform_table.get(m1) if m1 and m1[0:2] == 'fn' else ''

    def process(self, table):
        skip = 0
        batch = 200
        print 'begin process ... ' + table
        count = self.db[table].count()
        print 'count is %d' % count
        while skip < count:
            rows = self.db[table].find().sort("_id").skip(skip).limit(batch)
            for row in rows:
                result = row['result']
                item = {'timestamp': row['timestamp'], 'pageUrl': row['pageUrl']}
                try:
                    if result:
                        shop_config = result['shop_config']
                        shop_config = shop_config.replace('window.shop_config={', '').replace('}', '')
                        for t in [x.split(':', 1) for x in shop_config.split(',')]:
                            if len(t) < 2: continue
                            item[t[0].strip()] = t[1].strip(' \"')
                        item['tel'] = re.sub(self.tel_pattern, self.transform, result['telstr']).encode('utf-8').split('\xef\xbc\x9a')[1].strip()
                        item['kouwei'] = result['kouwei']
                        item['huanjing'] = result['huanjing']
                        item['fuwu'] = result['fuwu']
                        item['avgprice'] = result['mean_price'].encode('utf-8').replace('\xef\xbf\xa5', '') + ' 元' if result['mean_price'] else None
                    self.db['task_1132_' + time.strftime("%Y%m%d%H", time.localtime())].save(item)
                except Exception, e:
                    print item['pageUrl']
            skip += batch
        print 'finish ...'


def main():
    parse = ParseProcess()
    # for table in ['task_1132_shenzhen']:
    for table in ['task_1132_chongqing_20180919', 'task_1132_detail_20180922_0_5', 'task_1132_guangzhou_20180919',
                  'task_1132_nanjing_20180921', 'task_1132_shanghai_20180921', 'task_1132_xian_20180920']:
        parse.process(table)


if __name__ == '__main__':
    main()
