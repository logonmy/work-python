#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uuid
import time
import csv
from rh.util import MySqlUtil, Util

log = Util.log
config = None


def update_origin_data(records, db, cursor):
    update_origin_sql = 'update rh_err_origin set ck_tag = %s, ck_result = %s, recycle_tm = %s where gid = %s'
    log('update_origin_data ... ')
    cursor.executemany(update_origin_sql, records)
    db.commit()


def update_task(records, db, cursor):
    update_bm_task_sql = 'update rh_err_bm_task set keyword = %s, ck_tag = %s, is_finish = %s,' \
                         ' ck_result = %s, recycle_tm = %s where gid = %s and task_id = %s '
    log('update_bm_task ... ')
    cursor.executemany(update_bm_task_sql, records)
    db.commit()


def main(origin_file):
    Util.check_file_encoding(origin_file)
    global config
    config = Util.get_config()
    db = MySqlUtil(config)
    recycle_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    log('begin...')
    try:
        with open(origin_file, 'rb') as csvfile:
            records = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            origin_update_items = []
            task_update_items = []
            for r in records:
                gid = r['gid']
                keyword = r['keyword']
                ck_tag = r['tag']
                is_finish = r['is_finish']
                ck_result = r['\xe5\x88\xab\xe5\x90\x8d\xe7\xb1\xbb\xe5\x9e\x8b']
                task_id = r['task_id']
                if r['parent_id']:
                    # 如未原始地址 则要修改原始数据
                    origin_update_items.append((ck_tag, ck_result, recycle_tm, gid))
                task_update_items.append((keyword, ck_tag, is_finish, ck_result, recycle_tm, gid, task_id))

            cursor = db.get_cursor()
            update_origin_data(origin_update_items, db, cursor)
            update_task(task_update_items, db, cursor)
    except Exception, e:
        msg = e.message if e.message else str(e.args)
        log("error>>>" + msg)
        raise Exception(msg)
    finally:
        log('finish...')
        db.close_conn()
        Util.remove_file(origin_file)


if __name__ == '__main__':
    main(origin_file=r'E:\work\data\rh\bm_recycle_test.csv')
