#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from pymongo import MongoClient
import time
import os
import random

db = None
save_table = None
user_agents = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1',
]
headers = {
    'User-Agent': ''
    , 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    , 'Accept-Encoding': 'gzip, deflate, sdch'
    , 'Accept-Language': 'zh-CN,zh;q=0.8'
    , 'Cache-Control': 'max-age=0'
    , 'Proxy-Connection': 'keep-alive'
    , 'Upgrade-Insecure-Requests': '1'
    , 'Pragma': 'no-cache',
}


def get_header():
    headers['User-Agent'] = random.choice(user_agents)
    return headers


def now_time():
    return int(round(time.time() * 1000))


def now_time_str():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def change_ip():
    os.system('D:\\node-changeip\\swip.bat')
    time.sleep(10)


def save_to_db(item):
    while 1:
        try:
            db[save_table].save(item)
            break
        except Exception, e:
            print "db error: " + str(e)
            init_db()
            time.sleep(10)


def init_db():
    while 1:
        try:
            conn = MongoClient('140.143.94.171', 27017)
            global db
            db = conn.crawler
            db.authenticate('mongodbcrawler', 'Shantianci56')
            break
        except:
            change_ip()


def log(message):
    print now_time_str() + ": " + str(message)


def download(url):
    try:
        log('download url ' + line)
        resp = requests.get(url, headers=get_header()).json()
        return resp['entregistry']['list'][0]
    except Exception, e:
        log(e)
        return ''


if __name__ == '__main__':
    init_db()
    save_table = 'tele_changsha_1'
    url_source = 'changsha_link20181012_1000_url_1.txt'
    sleep_time = 1
    fail_cnt = 0
    with open(url_source) as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            while 1:
                time.sleep(sleep_time)
                result = download(line)
                if result:
                    fail_cnt = 0
                    save_to_db({'result': result, 'pageUrl': line, 'timestamp': now_time()})
                    break
                else:
                    fail_cnt += 1
                    if fail_cnt > 5:
                        change_ip()
                        fail_cnt = 0
                        break
