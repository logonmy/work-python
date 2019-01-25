#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from pyquery import PyQuery as pq
from scrapy_test.my_mongodb import MyMongo

url = "http://www.dianping.com/citylist"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'}
resp = requests.get(url, headers=headers)
d = pq(resp.text)

db = MyMongo().get_db()
# url_pattern = "'https://www.dianping.com/%s/ch10', "
save_table = 'dianping_business_zone'
url_pattern = "https://www.dianping.com/%s/food"

tmp = """
克拉玛依市,kelamayi
乌鲁木齐市,wulumuqi
吐鲁番市,tulufandiqu
哈密市,hami
昌吉回族自治州,changjizhou
博尔塔拉蒙古自治州,boertala
巴音郭楞蒙古自治州,bayinguoleng
克孜勒苏柯尔克孜自治州,kezilesu
喀什地区,keshidiqu
和田地区,hetiandiqu
伊犁哈萨克自治州,yili
塔城地区,tachengdiqu
阿勒泰地区,aletaidiqu
"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
city_names = tmp.strip().split('\n')
for link in city_names:
    # href = link.get('href')
    # city_name = link.text
    city_name, pinyin = link.split(',')
    # if str(city_name) not in city_names:
    #     continue
    db[save_table].delete_many({'city_name': city_name})
    city_url = url_pattern % pinyin
    print city_url
    resp = requests.get(city_url, headers=headers)
    d = pq(resp.text)
    items = d('#J_nc_business .list_business ul>li>a')
    if items:
        for sub_link in items[0:10]:
            zone_name = sub_link.get('title')
            if zone_name:
                print '%s-%s' % (city_name, zone_name)
                db[save_table].save({'city_name': city_name, 'zone_name': zone_name})
    else:
        items = d('.term-list-item')
        if items:
            has_busi_zone = False
            for item in items.items():
                if item('strong').text() == u'热门商区:':
                    has_busi_zone = True
                    for sub_link in item('ul li a')[0:10]:
                        zone_name = sub_link.get('title')
                        if zone_name:
                            print '%s-%s' % (city_name, zone_name)
                            db[save_table].save({'city_name': city_name, 'zone_name': zone_name})
                    break
            if not has_busi_zone:
                # print 'no zone：%s' % city_name
                db[save_table].save({'city_name': city_name, 'zone_name': None})
        else:
            # print 'no zone：%s' % city_name
            db[save_table].save({'city_name': city_name, 'zone_name': None})
