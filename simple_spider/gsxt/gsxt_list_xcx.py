#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from pymongo import MongoClient
import time, os, re, json, random
import traceback
import urllib
import threading

headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_2 like Mac OS X) AppleWebKit/604.4.7 (KHTML, like Gecko) Mobil'
                  'e/15C114 MicroMessenger/6.7.4(0x1607042c) NetType/WIFI Language/zh_CN'
    , 'Accept': 'application/json'
    , 'Accept-Language': 'zh-cn'
    , 'Accept-Encoding': 'br, gzip, deflate'
    , 'Host': 'app.gsxt.gov.cn'
    , 'Referer': 'https://servicewechat.com/wx5b0ed3b8c0499950/6/page-frame.html'
    , 'Content-Type': 'application/x-www-form-urlencoded'
    , 'Connection': 'keep-alive'
}
db = None
table = None
succ_cnt = 0


def get_header(ref=None):
    return headers


post_data = {
    'conditions': '{"excep_tab":"0","ill_tab":"0","area":"0","cStatus":"0","xzxk":"0","xzcf":"0","dydj":"0"}'
    , 'sourceType': 'W'
    , 'searchword': ''
}


def get_list(url, searchword, is_first_page=True, fail_cnt=0):
    log('get_list: %s %s' % (url, searchword))
    while 1:
        try:
            post_data['searchword'] = searchword
            resp = requests.post(url, headers=get_header(), data=post_data, timeout=120)
            break
        except Exception, e:
            print e
            change_ip()
    if not resp.text or '"status":200' not in resp.text:
        log('get_list fail:' + searchword)
        change_ip()
        if fail_cnt < 3:
            get_list(url, searchword, is_first_page, fail_cnt + 1)
        else:
            failed_list.add(searchword)
    else:
        succ_list.add(searchword)
        totalpage = parse_list(resp.text)
        if totalpage > 1 and is_first_page:
            for i in range(1, totalpage):
                get_list(re.sub('search-(\d+)', lambda g: 'search-' + str(int(g.group(1)) + i), url), searchword, False)


def parse_list(content):
    try:
        soup = json.loads(content)
        result = []
        data_result = soup['data']['result']
        for item in data_result['data']:
            result.append('%s&%s&%s' % (item['pripid'], item['nodeNum'], item['entType']))
            item['timestamp'] = now_time()
            save_to_db(item)
        print 'insert %d urls' % len(result)
        insert_urls(task_sublink_key, result)
        return data_result['totalPage']
    except Exception, e:
        traceback.print_exc()
        log("parse_list fail: " + str(e))
        return 0


def get_attr(tag, attr):
    return tag.attrs[attr] if tag else None


def now_time():
    return int(round(time.time() * 1000))


def save_to_db(item):
    while 1:
        try:
            db['gsxt_level0_' + time.strftime("%Y%m%d%H", time.localtime())].save(item)
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
    def do_change_ip():
        os.system('D:\\node-changeip\\swip.bat')

    t = threading.Thread(target=do_change_ip)
    t.setDaemon(True)
    t.start()
    t.join(60)
    time.sleep(30)


log_file = open('gsxt_list_xcx.log', 'a')


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
            resp = requests.post(url_server % key, json=data, timeout=60)
            return json.loads(resp.text)['msg'] == 'ok'
        except:
            time.sleep(3)


def get_urls(key):
    print 'get_urls...'
    while True:
        try:
            resp = requests.get(url_server % key, timeout=60)
            return json.loads(resp.content)
        except:
            time.sleep(3)


def back_urls(key, succ_list, failed_list):
    while True:
        try:
            data = {'success': list(succ_list), 'failed': list(failed_list)}
            resp = requests.post(url_server % key, json=data, timeout=60)
            return json.loads(resp.content)
        except:
            time.sleep(3)


if __name__ == '__main__':
    init_db()
    list_url_prefix = 'https://app.gsxt.gov.cn/gsxt/corp-query-app-search-1.html'
    # url_server = 'http://118.24.176.167:1234/%s'
    url_server = 'http://127.0.0.1:1234/%s'
    task_key = 'gsxt_lv0'
    task_sublink_key = 'gsxt_lv1'
    try:
        while True:
            succ_list = set()
            failed_list = set()
            urls = get_urls(task_key)
            if urls:
                for line in urls:
                    link = line.encode('utf8')
                    if link:
                        get_list(list_url_prefix, link)
                back_urls(task_key, succ_list, failed_list)
            else:
                time.sleep(5 * 60)
    except Exception, e:
        traceback.print_exc()
        log("program exception " + str(e))
        flush_log()
