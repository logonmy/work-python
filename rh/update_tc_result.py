#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from util import MySqlUtil, Util

log = Util.log
config = None


def update_origin_data(records, db, cursor):
    if not records:
        return
    update_origin_sql = 'update rh_err_origin set ck_tag = %s, ck_result = %s, recycle_tm = %s where gid = %s'
    log('update_origin_data ... ')
    cursor.executemany(update_origin_sql, records)
    db.commit()


def update_task(records, db, cursor):
    if not records:
        return
    update_bm_task_sql = 'update rh_err_tc_task set ck_result = %s where delivery_type = %s'
    log('update_tc_task ... ')
    cursor.executemany(update_bm_task_sql, records)
    db.commit()


query_sql = """
    select delivery_type as gid, ck_tag, if(min(ck_tc) = max(ck_tc), '1', '2') as ck_result 
    from rh_err_tc_task where ztask_id like '%task_day' and is_finish = 'Y' 
    group by delivery_type having count(1) = 2
"""


def main(task_day):
    global config
    config = Util.get_config()
    db = MySqlUtil(config)
    log('begin...')
    recycle_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    try:
        cursor = db.get_cursor(True)
        sql = query_sql.replace('task_day', task_day)
        log(sql)
        cursor.execute(sql)
        rows = cursor.fetchall()
        if rows:
            update_task_items = []
            update_origin_items = []
            for r in rows:
                update_task_items.append((r['ck_result'], r['gid']))
                update_origin_items.append((r['ck_tag'], r['ck_result'], recycle_tm, r['gid']))

            update_task(update_task_items, db, cursor)
            update_origin_data(update_origin_items, db, cursor)
        else:
            log("没有查询到可以更新的数据!!!")
            raise Exception("没有查询到可以更新的数据!!!")
    except Exception, e:
        msg = e.message if e.message else str(e.args)
        log("error>>>" + msg)
        raise Exception(msg)
    finally:
        log('finish...')
        db.close_conn()


if __name__ == '__main__':
    main('20190108')
