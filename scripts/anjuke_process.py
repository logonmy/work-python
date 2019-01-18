#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient

# 列表页
# conn = MongoClient('140.143.94.171', 27017)
# db = conn.crawler
# db.authenticate('mongodbcrawler', 'Shantianci56')
# table_anjuke = db['t_anjuke_1']
#
# urls = set()
# shenghui = ['北京', '上海', '天津', '重庆', '哈尔滨', '长春', '沈阳', '呼和浩特', '石家庄', '乌鲁木齐', '兰州', '西宁',
#             '西安', '银川', '郑州', '济南', '太原', '合肥', '长沙', '武汉', '南京', '成都', '贵阳', '昆明', '南宁',
#             '拉萨', '杭州', '南昌', '广州', '福州', '台北', '海口', '香港']
# zuf = open("anjuke_zu_urls.text", 'w+')
# salef = open("anjuke_sale_urls.text", 'w+')
# for result in table_anjuke.find({'name': {'$ne': '武汉'}}, {'name': 1, 'zu.link': 1, 'sales.link': 1}):
#     ran = 50 if result['name'] in shenghui else 20
#     for sale in result['sales']:
#         url = sale['link']
#         # print url
#         if url not in urls:
#             urls.add(url)
#             for i in range(1, ran + 1):
#                 print url + "p" + str(i)
#                 salef.write(url + "p" + str(i) + "\n")
#     for zu in result['zu']:
#         url = zu['link']
#         # print url
#         if url not in urls:
#             urls.add(url)
#             for i in range(1, ran + 1):
#                 print url + 'p' + str(i)
#                 zuf.write(url + "p" + str(i)  + "\n")
#
# conn.close()


# 详情页
conn = MongoClient('10.82.244.18', 27018)
db = conn.crawler
db.authenticate('spider', 'spider')
tables = [
    'task_1019_level0_2018090420'
    , 'task_1019_level0_2018090421'
    , 'task_1019_level0_2018090422'
    , 'task_1019_level0_2018090423'
    , 'task_1019_level0_2018090424'
    , 'task_1019_level0_2018090514'
    , 'task_1019_level0_2018090515'
    , 'task_1019_level0_2018090516'
    , 'task_1019_level0_2018090520'
    , 'task_1028_level0_2018090519'
    , 'task_1028_level0_2018090520'
    , 'task_1028_level0_2018090521'
    , 'task_1028_level0_2018090522'
    , 'task_1028_level0_2018090610'
]
zu_detail_urls_file = open("anjuke_zu_detail_urls.txt", 'w+')
sale_detail_urls_file = open("anjuke_sale_detail_urls.txt", 'w+')


def write_to_file(link):
    if link.find('.zu.') != -1:
        zu_detail_urls_file.write(link + "\n")
    else:
        sale_detail_urls_file.write(link + "\n")


for table in tables:
    table_anjuke = db[table]
    print table
    for row in table_anjuke.find({'result': {"$ne": []}}, {'result.link': 1}):
        try:
            if 'result' in row:
                if type(row['result']) == dict:
                    link = row['result']['link']
                    write_to_file(link)
                else:
                    for links in row['result']:
                        link = links['link']
                        write_to_file(link)
        except Exception, e:
            print table + " error :"
            print e
conn.close()
