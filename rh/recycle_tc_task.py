#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uuid
import time
import csv
from util import MySqlUtil, Util

log = Util.log
config = None
ck_tag_dict = {'正确': 0, '不在范围': 1, '地址错误': 2, '地址已拆除': 4}


def update_task(records, db, cursor):
    if not records:
        return
    update_bm_task_sql = 'update rh_err_tc_task set ck_tag = %s, is_finish = %s, ck_tc = %s, ck_x = %s, ck_y = %s,' \
                         ' recycle_tm = %s where addr_groupid = %s and ztask_id = %s'
    log('update_tc_task ... ')
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
            task_update_items = []
            for r in records:
                # 任务状态
                is_finish = 'Y' if r['\xe4\xbb\xbb\xe5\x8a\xa1\xe7\x8a\xb6\xe6\x80\x81'] == '已提交' else 'N'
                if is_finish == 'N':
                    continue
                # 标准地址id
                addr_groupid = r['\xe6\xa0\x87\xe5\x87\x86\xe5\x9c\xb0\xe5\x9d\x80id']
                # 地址信息
                ck_tag = ck_tag_dict.get(r['\xe5\x9c\xb0\xe5\x9d\x80\xe4\xbf\xa1\xe6\x81\xaf'], '')
                # 核实后TC
                ck_tc = r['\xe6\xa0\xb8\xe5\xae\x9e\xe5\x90\x8eTC']
                # 经度
                ck_x = r['\xe7\xbb\x8f\xe5\xba\xa6']
                # 纬度
                ck_y = r['\xe7\xba\xac\xe5\xba\xa6']
                # 备注
                task_id = r['\xe5\xa4\x87\xe6\xb3\xa8']
                task_update_items.append((ck_tag, is_finish, ck_tc, ck_x, ck_y, recycle_tm, addr_groupid, task_id))

            cursor = db.get_cursor()
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
    main(origin_file=r'E:\work\data\rh\tc_recycle_test.csv')
