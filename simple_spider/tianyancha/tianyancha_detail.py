#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
# from bs4 import BeautifulSoup
from pymongo import MongoClient
import time, os, re, random, zlib, json
import traceback
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
import bson.binary
import threading

user_agents = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
    # 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
    # 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
    # 'Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0',
    # 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41',
    # 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1',
]
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'
    , 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
    , 'Accept-Encoding': 'gzip, deflate, br'
    , 'Accept-Language': 'zh-CN,zh;q=0.9'
    , 'Host': 'www.tianyancha.com'
}
db = None
succ_cnt = 0
font_url_pattern = re.compile('https://static.tianyancha.com/fonts-styles/css/\w+/?\w+/font.css')


def close_driver(driver):
    if driver:
        driver.close()
        driver.quit()


def change_user_agent():
    headers['User-Agent'] = random.choice(user_agents)
    return headers['User-Agent']


def get_header(ref=None):
    if ref:
        headers['Referer'] = ref
    return headers


def get_cookie(chang_ip=True):
    ua = change_user_agent()
    if chang_ip:
        change_ip()
    driver = init_driver(ua)
    try:
        driver.delete_all_cookies()
        driver.get('https://www.tianyancha.com')
        print driver.title
        wdw = WebDriverWait(driver, 60, 0.5)
        element = wdw.until(lambda driver: driver.find_elements_by_css_selector(".key"))
        random.choice(element[0:15]).click()
        print driver.title
        # element = wdw.until(lambda driver:  driver.find_element_by_css_selector('.select-none'))
        # print element.get_attribute('href')
        # element.click()
        # print driver.title
        headers['Cookie'] = ";".join([cookie['name'] + "=" + cookie['value'] for cookie in driver.get_cookies()])
        print headers['Cookie']
    except Exception, e:
        print e
    finally:
        close_driver(driver)


def get_detail(url, fail_cnt=0):
    time.sleep(0.5)
    log('get_detail: ' + url)
    while 1:
        try:
            resp = requests.get(url, headers=get_header(), timeout=120)
            break
        except Exception, e:
            print e
            get_cookie()
    try:
        if resp.url.find('login') != -1 or not resp.text or resp.text.find('sorryPage') > 0:
            log('get_detail forbid:' + url)
            get_cookie()
            if fail_cnt < 3:
                fail_cnt += 1
                get_detail(url, fail_cnt)
            else:
                failed_list.append(url)
        else:
            succ_list.append(url)
            save_item = {'pageUrl': url, 'timestamp': now_time()}
            save_item['source'] = bson.binary.Binary(zlib.compress(resp.content))
            save_to_db(save_item)
    except:
        traceback.print_exc()
        log('get_detail fail:' + url)


def now_time():
    return int(round(time.time() * 1000))


def save_to_db(item):
    while 1:
        try:
            db['tianyancha_wuhan_detail_' + time.strftime("%Y%m%d-%H", time.localtime())].save(item)
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


log_file = open('tianyancha_detail.log', 'a')


def log(msg):
    timestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print timestr + ": " + str(msg)
    log_file.write(timestr + ": " + str(msg) + "\n")


def flush_log():
    log_file.flush()
    log_file.close()


def init_driver(ua):
    cap = webdriver.DesiredCapabilities.PHANTOMJS
    cap["phantomjs.page.settings.userAgent"] = ua
    cap["phantomjs.page.customHeaders.User-Agent"] = ua
    driver = webdriver.PhantomJS(
        executable_path=r"D:\worker\phantomjs.exe",
        desired_capabilities=cap)
    driver.implicitly_wait(30)
    return driver


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
    get_cookie(False)
    task_key = 'task_1711_lv1'
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
                                get_detail(link)
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
