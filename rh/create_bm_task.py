#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from util import MySqlUtil, Util

log = Util.log
config = None


def insert_records(records, db, cursor):
    insert_sql = """
        insert rh_err_bm_task(gid, address, zno_code, type, city_code, team_code, right_tc, x, y, keyword, parent_id, 
        task_id, task_name, init_id, init_id_source) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    batch_insert_cnt = config.get_int('batch_insert_cnt', 10)
    batch_commit_cnt = config.get_int('batch_commit_cnt', 1000)
    items = []
    begin_time = time.clock()
    for i, fields in enumerate(records):
        items.append(fields)
        if (i + 1) % batch_insert_cnt == 0:
            cursor.executemany(insert_sql, items)
            items = []
            if (i + 1) % batch_commit_cnt == 0:
                db.commit()
                now_time = time.clock()
                log('insert %d rows elapse %d s' % (batch_commit_cnt, now_time - begin_time))
                begin_time = now_time
    else:
        if items:
            cursor.executemany(insert_sql, items)
            db.commit()


def update_origin(gids, db, cursor):
    log("update origin table...")
    update_sql = 'update rh_err_origin set is_task = 1 where gid = %s'
    cursor.executemany(update_sql, gids)
    db.commit()


query_sql = """
    SELECT 
    gid, norm_address, rh_zc, zc_code, city_code, rh_tc, rh_x, ts_x, bq54_x, rh_y, ts_y ,bq54_y, keyword, group_group, STANDARD
    FROM
        rh_err_origin
    WHERE
    is_task = '0'
    AND group_group IS NOT NULL
    AND group_group <> ''
    AND rh_tc IS NOT NULL
    AND rh_tc <> ''
    AND zc_code LIKE CONCAT('%', city_code, '%')
    AND input_day >= 'begin_day'
    AND input_day <= 'end_day'
    GROUP BY group_group
"""


def main(begin_day, end_day):
    global config
    config = Util.get_config()
    db = MySqlUtil(config)
    log('begin...')
    curdate = time.strftime('%Y%m%d', time.localtime())
    try:
        cursor = db.get_cursor(True)
        sql = query_sql.replace('begin_day', begin_day).replace('end_day', end_day)
        log(sql)
        cursor.execute(sql)
        rows = cursor.fetchall()
        if rows:
            items = []
            gids = []
            for r in rows:
                gids.append((r['gid'], ))
                task_id = 'rh_BM_' + r['city_code'] + '_task1_' + curdate
                x = Util.first_non_blank(r['rh_x'], r['ts_x'], r['bq54_x'])
                y = Util.first_non_blank(r['rh_y'], r['ts_y'], r['bq54_y'])

                items.append((r['gid'], r['norm_address'], r['zc_code'], '3', r['city_code'], r['rh_tc'], '', x, y,
                             r['keyword'], r['group_group'], task_id, task_id, '', '原始地址'))
                items.append((r['group_group'], r['STANDARD'], r['zc_code'], '1', r['city_code'], r['rh_tc'], '', x, y,
                              r['keyword'], '', task_id, task_id, r['group_group'], '标准地址'))
            insert_records(items, db, cursor)
            update_origin(gids, db, cursor)
        else:
            log("没有查询到任务数据!!!")
            raise Exception("没有查询到任务数据!!!")
    except Exception, e:
        msg = e.message if e.message else str(e.args)
        log("error>>>" + msg)
        raise Exception(msg)
    finally:
        log('finish...')
        db.close_conn()


if __name__ == '__main__':
    main('20190108', '20190108')
