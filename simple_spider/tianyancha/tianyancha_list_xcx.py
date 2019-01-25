#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
# from bs4 import BeautifulSoup
from pymongo import MongoClient
import time, os, re, json, random
import traceback
import urllib
# from selenium import webdriver
# from selenium.webdriver.support.wait import WebDriverWait

headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_2 like Mac OS X) AppleWebKit/604.4.7 (KHTML, like Gecko) Mobile/15C114 MicroMessenger/6.7.4(0x1607042c) NetType/WIFI Language/zh_CN'
    , 'Accept': '*'
    , 'Accept-Language': 'zh-cn'
    , 'Accept-Encoding': 'gzip, deflate, br'
    , 'Host': 'api9.tianyancha.com'
    , 'Referer': 'https://servicewechat.com/wx9f2867fc22873452/16/page-frame.html'
    , 'version': 'TYC-XCX-WX'
}
db = None
table = None
succ_cnt = 0
succ_list = []
failed_list = []


def get_header(ref=None):
    # if ref:
    #     headers['Referer'] = ref
    return headers


def get_list(url, is_first_page=True, fail_cnt=0):
    log('get_list: ' + url)
    while 1:
        try:
            resp = requests.get(url, headers=get_header(), timeout=120)
            break
        except Exception, e:
            print e
            change_ip()
    if not resp.text or '"state":"ok"' not in resp.text:
        log('get_list fail:' + url)
        change_ip()
        if fail_cnt < 3:
            fail_cnt += 1
            get_list(url, is_first_page, fail_cnt)
        else:
            failed_list.append(url.strip(list_url_prefix))
    else:
        succ_list.append(url.strip(list_url_prefix))
        parse_list(url, resp.text)


def parse_list(url, content):
    try:
        soup = json.loads(content)
        result = []
        for item in soup['data']['companyList']:
            result.append(item['id'])
            item['timestamp'] = now_time()
            save_to_db(item)
        print 'insert %d urls' % len(result)
        insert_urls(task_sublink_key, result)
    except Exception, e:
        traceback.print_exc()
        log("parse_list fail: " + str(e))


def get_attr(tag, attr):
    return tag.attrs[attr] if tag else None


def now_time():
    return int(round(time.time() * 1000))


def save_to_db(item):
    while 1:
        try:
            db['tianyancha_level0_' + time.strftime("%Y%m%d%H", time.localtime())].save(item)
            break
        except Exception, e:
            traceback.print_exc()
            log("db error " + str(e))
            init_db()
            time.sleep(30)


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


def change_ip():
    os.system('D:\\node-changeip\\swip.bat')
    time.sleep(30)


log_file = open('tianyancha_list_xcx.log', 'a')


def log(msg):
    timestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print timestr + ": " + str(msg)
    log_file.write(timestr + ": " + str(msg) + "\n")


def flush_log():
    log_file.flush()
    log_file.close()


def insert_urls(key, urls):
    while True:
        try:
            data = {'new': urls}
            resp = requests.post('http://118.24.176.167:1234/%s' % key, json=data, timeout=60)
            return json.loads(resp.text)['msg'] == 'ok'
        except:
            time.sleep(3)


def get_urls(key):
    while True:
        try:
            resp = requests.get('http://118.24.176.167:1234/%s' % key, timeout=60)
            return json.loads(resp.content)
        except:
            time.sleep(3)


def back_urls(key, succ_list, failed_list):
    while True:
        try:
            data = {'success': succ_list, 'failed': failed_list}
            resp = requests.post('http://118.24.176.167:1234/%s' % key, json=data, timeout=60)
            return json.loads(resp.content)
        except:
            time.sleep(3)


if __name__ == '__main__':
    init_db()
    list_url_prefix = 'https://api9.tianyancha.com/services/v3/search/sNorV3/%s?pageNum=1&pageSize=10&sortType=0'
    task_key = 'task_1711_lv0'
    task_sublink_key = 'task_1711_lv1'
    try:
        while True:
            succ_list = []
            failed_list = []
            urls = get_urls(task_key)
            if urls:
                for line in urls:
                    link = line.encode('utf8')
                    if link:
                        get_list(list_url_prefix % urllib.quote(link))
                back_urls(task_key, succ_list, failed_list)
            else:
                time.sleep(5 * 60)
    except Exception, e:
        traceback.print_exc()
        log("program exception " + str(e))
        flush_log()
