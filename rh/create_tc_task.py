#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from util import MySqlUtil, Util

log = Util.log
config = None
jingpin_citys = ['755', '020', '751', '763', '021', '010', '571', '025', '852', '853']


def insert_records(records, db, cursor):
    insert_sql = """
        insert rh_err_tc_task(addrabb, addr_src, addr_groupid, addr_dept, addr_team_code, longitude, latitude,
        priority, scount, ztask_id, delivery_type) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
    update_sql = 'update rh_err_origin set is_task = 2 where gid = %s'
    cursor.executemany(update_sql, gids)
    db.commit()


query_sql = """
    SELECT 
    norm_address, group_group, zc_code, rh_tc, rh_x, ts_x, bq54_x, rh_y, ts_y ,bq54_y, addr_total_freq, city_code, gid
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
    db = MySqlUtil(config.get('mysql.host'), config.get('mysql.user'),
                   config.get('mysql.passwd'), config.get('mysql.db'))
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
                task_id = 'rh_' + r['city_code'] + '_task1_' + curdate
                is_jingpin_city = r['city_code'] in jingpin_citys
                x = Util.first_non_blank(r['rh_x'], r['ts_x'], r['bq54_x'])
                y = Util.first_non_blank(r['rh_y'], r['ts_y'], r['bq54_y'])
                priority_level = '1' if r['addr_total_freq'] > 1 else '2'

                # 原始地址
                items.append((r['norm_address'], 'DDS_AUTO' if is_jingpin_city else 'NM_Addr', r['group_group'],
                              r['zc_code'], r['rh_tc'], x, y, priority_level, r['addr_total_freq'], task_id, r['gid']))
                # 标准地址
                items.append((r['norm_address'], 'yizhi' if is_jingpin_city else 'MC_Addr',
                              r['group_group'] + '_' + r['city_code'], r['zc_code'], r['rh_tc'], x, y, priority_level,
                              r['addr_total_freq'], task_id, r['gid']))

            insert_records(items, db, cursor)
            update_origin(gids, db, cursor)
        else:
            log("没有查询到任务数据!!!")
            raise Exception("没有查询到任务数据!!!")
    except Exception, e:
        log("error>>>" + e.message)
        raise Exception(e.message)
    finally:
        log('finish...')
        db.close_conn()


if __name__ == '__main__':
    main('20190108', '20190108')
