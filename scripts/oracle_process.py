#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cx_Oracle
from pymongo import MongoClient
import traceback
import os
import bson
import time, datetime




os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'

# mon_db = MongoClient('140.143.94.171', 27017).crawler
# mon_db.authenticate('mongodbcrawler', 'Shantianci56')
mon_db = MongoClient('10.82.244.18', 27018).crawler
mon_db.authenticate('spider', 'spider')

conn = cx_Oracle.connect('crawler/crawler1357@10.82.244.18/oradev')
cur = conn.cursor()

# insert into RAW_RESULT_ZTO ("ID", "ACTION_ID","LINK","NAME","ADDRESS","DISPATCH_RANGE","ADCODE","CREATE_TIME","UPDATE_TIME","X_COORD","Y_COORD","SOURCE_ID")
# values (:ID, 1, :LINK, :NAME, :ADDRESS, :DISPATCH_RANGE, 0, sysdate, sysdate, :X_COORD, :Y_COORD, :SOURCE_ID)  BUILDING
# sql = """
# insert into RAW_RESULT_GZCC ("ID", "ACTION_ID","LINK","NAME","ADDRESS","ADCODE","CREATE_TIME","UPDATE_TIME","SOURCE_ID", "BUILDING_NAME", "FLOOR", "ROOM_NO")
# values (:ID, 1, :LINK, :NAME, :ADDRESS, 0, sysdate, sysdate, :SOURCE_ID, :BUILDING_NAME, :FLOOR, :ROOM_NO)
# """
# sql = """
# insert into RAW_RESULT_SHIJW ("ID", "ACTION_ID","LINK","NAME","ADDRESS","ADCODE","CREATE_TIME","UPDATE_TIME","SOURCE_ID", "BUILDING")
# values (:ID, 1, :LINK, :NAME, :ADDRESS, 0, sysdate, sysdate, :SOURCE_ID, :BUILDING)
# """
sql = """
insert into RAW_RESULT_BEIKE_BUILDING ("ID", "CREATE_TIME","UPDATE_TIME","SOURCE_ID", "COMMUNITY_ID")
values (:ID, to_timestamp(:CREATE_TIME, 'yyyy-mm-dd hh24:mi:ss'), to_timestamp(:CREATE_TIME, 'yyyy-mm-dd hh24:mi:ss'), :SOURCE_ID, :COMMUNITY_ID)
"""
try:
    i = 0
    for coll_name in mon_db.list_collection_names():
        if coll_name.find('task_1712_level0_') == 0:
            cnt = mon_db[coll_name].count()
            print 'begin %s total %d' % (coll_name, cnt)
            cur.prepare(sql)
            limit = 50
            skip = 0
            while skip < cnt:
                rows = mon_db[coll_name].find().sort("_id").skip(skip).limit(limit)
                results = []
                for r in rows:
                    skip += 1
                    community_id = r['pageUrl'][27:].split('/')[0]
                    create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(r['timestamp']/1000))
                    for b in r['result']['building_id']:
                        i += 1
                        item = {}
                        item['ID'] = i
                        item['SOURCE_ID'] = b
                        item['CREATE_TIME'] = create_time
                        item['COMMUNITY_ID'] = community_id
                        # i += 1
                        results.append(item)
                print 'skip %d  result %d ' % (skip , len(results))
                cur.executemany(None, results)
                conn.commit()
except Exception, e:
    traceback.print_exc()
    print e
finally:
    conn.commit()
    conn.close()
