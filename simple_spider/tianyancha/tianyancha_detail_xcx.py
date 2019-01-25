#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from pymongo import MongoClient
import time, os, re, json
import traceback
import threading
import uuid

headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_2 like Mac OS X) AppleWebKit/604.4.7 (KHTML, like Gecko) Mobil'
                  'e/15C114 MicroMessenger/6.7.4(0x1607042c) NetType/WIFI Language/zh_CN'
    , 'Accept': '*/*'
    , 'Accept-Language': 'zh-cn'
    , 'Accept-Encoding': 'gzip, deflate, br'
    , 'Host': 'api9.tianyancha.com'
    , 'Referer': 'https://servicewechat.com/wx9f2867fc22873452/16/page-frame.html'
    , 'version': 'TYC-XCX-WX'
    , 'Content-Type': 'application/json'
}
db = None
succ_cnt = 0
font_url_pattern = re.compile('https://static.tianyancha.com/fonts-styles/css/\w+/?\w+/font.css')


def get_header(ref=None):
    if ref:
        headers['Referer'] = ref
    #headers['Authorization'] = '0###oo34J0Zf1RURy1GlsO8UbYihbmak###%s###%s' % get_random_strs()
    return headers


def get_random_strs():
    return str(int(time.time() * 1000)), uuid.uuid4().get_hex()


def get_detail(url, fail_cnt=0):
    log('get_detail: ' + url)
    while 1:
        try:
            resp = requests.get(url, headers=get_header(), timeout=120)
            break
        except Exception, e:
            print e
            change_ip()
    try:
        if not resp.text or '"state":"ok"' not in resp.text:
            log('get_detail forbid:' + url)
            change_ip()
            if fail_cnt < 3:
                fail_cnt += 1
                get_detail(url, fail_cnt)
            else:
                failed_list.append(url)
        else:
            succ_list.append(url)
            save_item = {'pageUrl': url, 'timestamp': now_time()}
            data = json.loads(resp.text)
            save_item['data'] = data['data'] if 'data' in data else None
            save_to_db(save_item)
    except:
        traceback.print_exc()
        log('get_detail fail:' + url)


def now_time():
    return int(round(time.time() * 1000))


def save_to_db(item):
    while 1:
        try:
            db['tianyancha_level1_' + time.strftime("%Y%m%d%H", time.localtime())].save(item)
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


log_file = open('tianyancha_detail_xcx.log', 'a')


def log(msg):
    timestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print timestr + ": " + str(msg)
    log_file.write(timestr + ": " + str(msg) + "\n")


def flush_log():
    log_file.flush()
    log_file.close()


def change_ip():
    def do_change_ip():
        os.system('D:\\node-changeip\\swip.bat')

    t = threading.Thread(target=do_change_ip)
    t.setDaemon(True)
    t.start()
    t.join(60)
    time.sleep(30)


def get_urls(key):
    while True:
        try:
            print 'get urls'
            resp = requests.get('http://118.24.176.167:1234/%s' % key)
            return json.loads(resp.content)
        except:
            time.sleep(3)


def back_urls(key, succ_list, failed_list):
    while True:
        try:
            data = {'success': succ_list, 'failed': failed_list}
            resp = requests.post('http://118.24.176.167:1234/%s' % key, json=data)
            return json.loads(resp.content)
        except:
            time.sleep(3)


if __name__ == '__main__':
    init_db()
    task_key = 'task_1711_lv1'
    url_prefix = 'https://api9.tianyancha.com/services/v3/t/common/baseinfoV5/%s'
    try:
        while True:
            urls = get_urls(task_key)
            if urls:
                succ_list = []
                failed_list = []
                for link in urls:
                    while 1:
                        try:
                            if link:
                                get_detail(url_prefix % link)
                            break
                        except:
                            init_db()
                back_urls(task_key, succ_list, failed_list)
            else:
                time.sleep(5 * 60)
    except Exception, e:
        traceback.print_exc()
        log("program exception " + str(e))
        flush_log()
