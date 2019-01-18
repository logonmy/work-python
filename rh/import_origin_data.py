#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uuid
import time
import csv
from util import MySqlUtil, Util

log = Util.log
config = None


column_map = {
    'gid': 'gid',
    'waybill_no': 'waybill_no',
    'city_code': 'city_code',
    'province': 'povince',
    'cityname': 'cityname',
    'norm_address': 'norm_address',
    'precision': 'precision_0',
    'zc_code': 'zc_code',
    'addr_total_freq': 'addr_total_freq',
    'addr_errcall_freq': 'addr_errcall_freq',
    'addr_first_order_time': 'addr_first_order_time',
    'addr_last_order_time': 'addr_last_order_time',
    'addr_first_errcall_time': 'addr_first_errcall_time',
    'addr_last_errcall_time': 'addr_last_errcall_time',
    'addr_err_freq': 'addr_err_freq',
    'addr_rece_differ_freq': 'addr_rece_differ_freq',
    'addr_first_differ_time': 'addr_first_differ_time',
    'addr_last_differ_time': 'addr_last_differ_time',
    'bq54_x': 'bq54_x',
    'bq54_y': 'bq54_y',
    'inc_day': 'inc_day',
    'normalized': 'normalized',
    'status': 'status_0',
    'time_stamp': 'time_stamp',
    'resp_time': 'resp_time',
    'MATCH_ADDR': 'MATCH_ADDR',
    'STANDARD': 'STANDARD',
    'SFLAG': 'SFLAG',
    'rh_x': 'rh_x',
    'rh_y': 'rh_y',
    'GL_LEVEL': 'GL_LEVEL',
    'SCORE': 'SCORE',
    'SPLITINFO': 'SPLITINFO',
    'MATCH_INFO': 'MATCH_INFO',
    'FILTER': 'FILTER',
    'MATCH_ID': 'MATCH_ID',
    'cell1': 'cell1',
    'cell3': 'cell3',
    'group_group': 'group_group',
    'key_index': 'key_index',
    'adcode': 'adcode',
    'poi_typecode': 'poi_typecode',
    'confidence': 'confidence',
    'rh_zc': 'rh_zc',
    'rh_tc': 'rh_tc',
    'rh_status': 'rh_status',
    'bq54_tc': 'bq54_tc',
    'src_log': 'src_log',
    'keyword': 'keyword'
}


def get_insert_sql(table, csv_columns, column_map):
    insert_sql = "insert into " + table
    print 'csv_column: ' + str(csv_columns)
    insert_columns_str = ''
    insert_columns_cnt = 0
    _columns = []
    for column in csv_columns:
        column = column.strip('"')
        if column in column_map:
            insert_columns_str += "`" + column_map[column] + "`, "
            insert_columns_cnt += 1
            _columns.append(column)
        else:
            print 'warn: 未定义的列名：%s' % column
    if 'gid' not in _columns:
        insert_columns_str += "`gid`, "
        insert_columns_cnt += 1
    insert_columns_str += "`input_day`, "
    insert_columns_cnt += 1
    value_str = '%s,' * insert_columns_cnt
    insert_sql += '(' + insert_columns_str[:-2] + ') values (' + value_str[:-1] + ')'
    print 'insert_sql: ' + insert_sql
    return insert_sql, _columns


def insert_records(records, columns, db, cursor, insert_sql):
    input_day = time.strftime('%Y%m%d', time.localtime())
    batch_insert_cnt = config.get_int('batch_insert_cnt', 10)
    batch_commit_cnt = config.get_int('batch_commit_cnt', 1000)
    items = []
    begin_time = time.clock()
    for i, fields in enumerate(records):
        values = [fields.get(k) for k in columns]
        if 'gid' not in columns:
            values.append(uuid.uuid4().get_hex())
        values.append(input_day)
        items.append(tuple(values))
        if (i + 1) % batch_insert_cnt == 0:
            try:
                cursor.executemany(insert_sql, items)
            except Exception, e:
                msg = e.message if e.message else str(e.args)
                log('insert error in rows from %d to %d, error: %s' % ((i + 1 - batch_insert_cnt), (i + 1), msg))
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


def remove_duplicate(db, cursor):
    log('执行排重...')
    cursor.execute("""
                delete from rh_err_origin where gid not in (select gid from (select min(gid) gid from
                rh_err_origin where is_task = 0 group by norm_address, STANDARD) t) and is_task = 0
            """)
    cursor.execute("""
                delete from rh_err_origin where gid in (
                   select ogid from (
                       select max(if(o.is_task = 0, o.gid, '0')) ogid, count(1) cnt
                       from rh_err_origin o group by norm_address, STANDARD
                    ) t where ogid <> '0' and cnt > 1
                 )
            """)
    db.commit()


def main(origin_file):
    Util.check_file_encoding(origin_file)
    global config
    config = Util.get_config()
    db = MySqlUtil(config)
    log('begin...')
    try:
        with open(origin_file, 'rb') as csvfile:
            csv_reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            insert_sql, _column = get_insert_sql('rh_err_origin', csv_reader.fieldnames, column_map)
            cursor = db.get_cursor()
            # 插入数据库
            insert_records(csv_reader, _column, db, cursor, insert_sql)
        # 去重
        remove_duplicate(db, cursor)
    except Exception, e:
        msg = e.message if e.message else str(e.args)
        log("error>>>" + msg)
        raise Exception(msg)
    finally:
        log('finish...')
        db.close_conn()
        Util.remove_file(origin_file)


if __name__ == '__main__':
    main(origin_file=r'E:\work\data\rh\source.csv')
