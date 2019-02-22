# /usr/bin/env python
# -*- coding: UTF-8 -*-

import requests
import time
import re
from pymongo import MongoClient
from selenium import webdriver

headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Cookie': 'JSESSIONID=ABAAABAABEEAAJA57ACC6152DA09BD5CF9FC7D26D3E7C2C;Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1550215945;Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1550215945;user_trace_token=20190215153225-d6ef68db-30f3-11e9-81f7-5254005c3644;_ga=GA1.2.927570450.1550215945;_gat=1;LGSID=20190215153225-d6ef6a12-30f3-11e9-81f7-5254005c3644;PRE_SITE=;PRE_HOST=;PRE_UTM=;PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F;LGRID=20190215153225-d6ef6b2d-30f3-11e9-81f7-5254005c3644;LGUID=20190215153225-d6ef6b8e-30f3-11e9-81f7-5254005c3644;_gid=GA1.2.347360680.1550215945;index_location_city=%E5%85%A8%E5%9B%BD',
    'Host': 'www.lagou.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
}


def init_driver():
    global driver
    ua = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'
    cap = webdriver.DesiredCapabilities.PHANTOMJS
    cap["phantomjs.page.settings.userAgent"] = ua
    cap["phantomjs.page.customHeaders.User-Agent"] = ua
    driver = webdriver.PhantomJS(
        executable_path=r"D:\exe\phantomjs.exe",
        desired_capabilities=cap)
    # driver = webdriver.Chrome(r'E:\work\exe\chromedriver.exe')
    driver.implicitly_wait(30)
    driver.set_page_load_timeout(30)


def close_driver():
    global driver
    if driver:
        driver.close()
        driver.quit()


def now_time():
    return int(round(time.time() * 1000))


def init_db():
    while 1:
        try:
            conn = MongoClient('140.143.94.171', 27017)
            global db
            db = conn.crawler
            db.authenticate('mongodbcrawler', 'Shantianci56')
            break
        except:
            time.sleep(5)


def save_to_db(item):
    while 1:
        try:
            db['task_1875_level1_' + time.strftime("%Y%m%d%H", time.localtime())].save(item)
            break
        except Exception, e:
            init_db()


def request(url):
    try:
        global driver
        while True:
            # resp = requests.get(url, headers=headers, timeout=10)
            driver.get(url)
            print ";".join([cookie['name'] + "=" + cookie['value'] for cookie in driver.get_cookies()])
            content = driver.page_source
            if 'positionAddress' in content:
                result = addr_pattern.findall(content)
                break
            else:
                close_driver()
                time.sleep(3)
                init_driver()
        item = {'timestamp': now_time()}
        result = {'QiYeDiZhi': result[0]}
        item['result'] = result
        item['pageUrl'] = url
        save_to_db(item)
    except Exception, e:
        print e
        close_driver()
        time.sleep(3)
        init_driver()


driver = None
if __name__ == '__main__':
    start_time = now_time()
    try:
        init_db()
        init_driver()
        addr_pattern = re.compile('name="positionAddress" value="(.*?)"')
        with open('lagou_jobs') as f:
            for line in f.readlines():
                line = line.strip()
                print time.strftime('%Y-%m-%d %H:%M:%S'), ':', line
                request(line)
    finally:
        close_driver()
        print 'total elapse %d ms' % (now_time() - start_time)
