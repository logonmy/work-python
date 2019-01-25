#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import time, os, re, json, random
import traceback
import urllib
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'
    , 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    , 'Accept-Encoding': 'gzip, deflate, br'
    , 'Host': 'www.tianyancha.com'
}
db = None
table = None
succ_cnt = 0
succ_list = []
failed_list = []


def get_header(ref=None):
    if ref:
        headers['Referer'] = ref
    return headers


def get_list(url, is_first_page=True, fail_cnt=0):
    log('get_list: ' + url)
    while 1:
        try:
            resp = requests.get(url, headers=get_header(), timeout=120)
            break
        except Exception, e:
            print e
            get_cookie()
    if resp.url.find('login') != -1 or not resp.text:
        log('get_list fail:' + url)
        get_cookie()
        if fail_cnt < 3:
            fail_cnt += 1
            get_list(url, is_first_page, fail_cnt)
        else:
            failed_list.append(url.strip(list_url_prefix))
    else:
        succ_list.append(url.strip(list_url_prefix))
        soup = BeautifulSoup(resp.text, 'lxml')
        parse_list(url, soup)
        if is_first_page:
            next_page_urls = soup.select('a.num', limit=5)
            if next_page_urls and len(next_page_urls) > 1:
                for next_page in next_page_urls[1:]:
                    next_page_url = next_page.attrs['href']
                    get_list(next_page_url, False, 0)


def parse_list(url, soup):
    try:
        # save_item = {'pageUrl': url, 'timestamp': now_time()}
        result = []
        for item in soup.select("div.search-result-single"):
            # info = dict()
            # info['GongSiLianJie'] = get_attr(item.select_one(".content > .header > a"), 'href')
            result.append(get_attr(item.select_one(".content > .header > a"), 'href'))
        # save_item['result'] = result
        # save_to_db(save_item)
        # result = filter(lambda x: x[x.rfind('/') + 1:] not in has_crawlered_ids, result)
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
            db[table].save(item)
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


def init_driver(ua):
    cap = webdriver.DesiredCapabilities.PHANTOMJS
    cap["phantomjs.page.settings.userAgent"] = ua
    cap["phantomjs.page.customHeaders.User-Agent"] = ua
    driver = webdriver.PhantomJS(
        executable_path=r"D:\worker\phantomjs.exe",
        desired_capabilities=cap)
    driver.implicitly_wait(30)
    return driver


def get_cookie(chang_ip=True):
    if chang_ip:
        change_ip()
    driver = init_driver('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',)
    try:
        driver.delete_all_cookies()
        driver.get('https://www.tianyancha.com')
        print driver.title
        wdw = WebDriverWait(driver, 60, 0.5)
        element = wdw.until(lambda driver: driver.find_elements_by_css_selector(".key"))
        random.choice(element[0:15]).click()
        print driver.title
        headers['Cookie'] = ";".join([cookie['name'] + "=" + cookie['value'] for cookie in driver.get_cookies()])
        print headers['Cookie']
    except Exception, e:
        print e
    finally:
        close_driver(driver)


def close_driver(driver):
    if driver:
        driver.close()
        driver.quit()


def change_ip():
    os.system('D:\\node-changeip\\swip.bat')
    #requests.get("http://127.0.0.1:4500", timeout=60)
    time.sleep(30)


log_file = open('tianyancha_list.log', 'a')


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
    list_url_prefix = 'https://bj.tianyancha.com/search?key='
    table = 'tianyancha_beijing_list'
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
                        get_list(list_url_prefix + urllib.quote(link))
                back_urls(task_key, succ_list, failed_list)
            else:
                time.sleep(5 * 60)
    except Exception, e:
        traceback.print_exc()
        log("program exception " + str(e))
        flush_log()
