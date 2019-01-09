#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uuid
import time
import csv
from util import MySqlUtil, Util

log = Util.log
config = None


column_map = {
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
    '_STANDARD': 'STANDARD',
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
    'src_log': 'src_log'
}


def get_insert_sql(table, csv_column_str, column_map, extra_columns):
    insert_sql = "insert into " + table
    print 'csv_column_str: ' + csv_column_str
    insert_columns_str = ''
    insert_columns_cnt = 0
    for column in csv_column_str.split(','):
        if column in column_map:
            insert_columns_str += "`" + column_map[column] + "`, "
            insert_columns_cnt += 1
        else:
            print '未定义的列名：%s' % column
    for column in extra_columns:
        insert_columns_str += "`" + column + "`, "
        insert_columns_cnt += 1
    value_str = '%s,' * insert_columns_cnt
    insert_sql += '(' + insert_columns_str[:-2] + ') values (' + value_str[:-1] + ')'
    print 'insert_sql: ' + insert_sql
    return insert_sql


def get_column_values(line_str, extra_values):
    col_values = []
    for col_value in line_str.split(','):
        col_values.append(col_value if col_value else None)
    for ev in extra_values:
        col_values.append(ev)
    return col_values


def insert_records(records, field_limit_size, db, cursor, insert_sql):
    input_day = time.strftime('%Y%m%d', time.localtime())
    batch_insert_cnt = config.get_int('batch_insert_cnt', 10)
    batch_commit_cnt = config.get_int('batch_commit_cnt', 1000)
    items = []
    begin_time = time.clock()
    for i, fields in enumerate(records):
        if len(fields) > field_limit_size:
            log('第%d行数据列数不对，停止插入' % (i + 1))
            exit()
        fields.append(uuid.uuid4().get_hex())
        fields.append(input_day)
        items.append(tuple(fields))
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
    db = MySqlUtil(config.get('mysql.host'), config.get('mysql.user'),
                   config.get('mysql.passwd'), config.get('mysql.db'))
    log('begin...')
    try:
        with open(origin_file, 'rb') as csvfile:
            column_str = csvfile.readline()
            insert_sql = get_insert_sql('rh_err_origin', column_str.strip(), column_map, ['gid', 'input_day'])
            records = csv.reader(csvfile, delimiter=',', quotechar='"')
            cursor = db.get_cursor()
            # 插入数据库
            insert_records(records, len(column_map), db, cursor, insert_sql)
        # 去重
        remove_duplicate(db, cursor)
    except Exception, e:
        log("error>>>" + e.message)
    finally:
        log('finish...')
        db.close_conn()


if __name__ == '__main__':
    main(origin_file=r'E:\work\data\rh\source_test.csv')
