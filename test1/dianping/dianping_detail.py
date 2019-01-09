#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from pyquery import PyQuery as pq
from pymongo import MongoClient
import time, os, random, socket
from selenium import webdriver

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
    , 'Cookie': 'td_cookie=2674000505; s_ViewType=10, cye=shanghai;cy=1'
}
db = None
save_table = None


def now_time():
    return int(round(time.time() * 1000))


def now_time_str():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def change_user_agent():
    headers['User-Agent'] = random.choice(user_agents)
    return headers['User-Agent']


def init_driver(ua):
    cap = webdriver.DesiredCapabilities.PHANTOMJS
    cap["phantomjs.page.settings.userAgent"] = ua
    cap["phantomjs.page.customHeaders.User-Agent"] = ua
    driver = webdriver.PhantomJS(
        executable_path=r"D:\exe\phantomjs.exe",
        desired_capabilities=cap)
    driver.implicitly_wait(30)
    return driver


def close_driver(driver):
    if driver:
        driver.close()
        driver.quit()


def get_header(ref):
    # headers['Referer'] = ref
    if 'Cookie' in headers:
        cookie = headers['Cookie']
        idx1 = cookie.find('%C7%C7')
        idx2 = cookie.find(";", idx1 + 1)
        headers['Cookie'] = cookie[0:idx1 + 6] + str(random.randint(1, 99)) + cookie[idx2:]
    return headers


def record_ip():
    f = open('used_ips.txt', 'a')
    f.write(now_time_str() + ": ")
    ip = socket.gethostbyname(socket.gethostname())
    f.write(ip)
    f.write('\n')
    f.close()
    return ip


def change_ip():
    os.system('D:\\node-changeip\\swip.bat')
    ip = record_ip()
    if ip and ip.startswith("192.168") or ip.startswith("172.16"):
        time.sleep(5)
        change_ip()
    time.sleep(20)
    global fail_cnt
    print 'has failed ' + str(fail_cnt) + 'times'


fail_cnt = 0
success_cnt = 0


def fail_cnt_incr():
    global fail_cnt
    fail_cnt += 1
    global success_cnt
    success_cnt = 0


def fail_cnt_desc():
    global fail_cnt
    if fail_cnt > 0:
        fail_cnt -= 1
    global success_cnt
    success_cnt += 1


def get_cookie(url, ref):
    ua = change_user_agent()
    change_ip()
    fail_cnt_incr()
    driver = init_driver(ua)
    try:
        driver.delete_all_cookies()
        driver.get(ref[0:ref.find("/ch10") + 5])
        print driver.title
        try:
            driver.find_element_by_xpath("//div[@class='navbar']/a[1]").click()
        except:
            pass
        driver.get(url)
        print driver.title
        # if driver.page_source.find('not-found-content') > -1:
        #     raise BaseException("not-found-content")
        headers['Cookie'] = ";".join([cookie['name'] + "=" + cookie['value'] for cookie in driver.get_cookies()])
        print headers['Cookie']
    except Exception, e:
        print e
    finally:
        close_driver(driver)


def parse_detail(url, ref, shop_info):
    time.sleep(random.randint(1, 4) * 0.9 + 0.2)
    try:
        global success_cnt
        if success_cnt > 120:
            print 'success_cnt has reach max, get_cookie again...'
            get_cookie(url, ref)
        resp = requests.get(url, headers=get_header(ref))
        if resp.status_code == 403:
            print 'parse_detail forbidden :' + url
            get_cookie(url, ref)
            parse_detail(url, ref, shop_info)
        elif resp.url.find('verify.meituan.com') != -1:
            print 'parse_detail show veriry :' + url
            get_cookie(url, ref)
            parse_detail(url, ref, shop_info)
        elif not resp.text:
            print 'parse_detail fail, no response:' + url
            get_cookie(url, ref)
            parse_detail(url, ref, shop_info)
        elif resp.text.find('not-found-content') > 0:
            print 'parse_detail:  url not found :' + url
        elif resp.text.find("window.shop_config") == -1:
            print 'parse_detail fail:' + url
            save_html(url[url.rfind('/') + 1:], resp.text)
            get_cookie(url, ref)
            parse_detail(url, ref, shop_info)
        else:
            d = pq(resp.text)
            # avgpricestr = d("#avgPriceTitle").html()
            # commentscorestr = d("#comment_score").html()
            telstr = d(".expand-info.tel").html()
            script = d('.footer-container+script').html()
            # result = {
            #     'shop_config': script,
            #     'tel': telstr,
            #     'commentscore': commentscorestr,
            #     'avgprice': avgpricestr
            # }
            shop_info['telstr'] = telstr
            shop_info['shop_config'] = script
            item = {'pageUrl': url, 'timestamp': now_time(), 'result': shop_info}
            save_to_db(item)
    except (Exception, BaseException) as e:
        print "parse detail: " + url + " , error: " + str(e)


def save_html(file_name, text):
    try:
        f = open(file_name, 'w')
        f.write(text)
        f.close()
    except:
        print 'save_html error'


def save_to_db(item):
    while 1:
        try:
            db[save_table].save(item)
            break
        except Exception, e:
            print "db error: " + str(e)
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


def log(message):
    print now_time_str() + ": " + message


if __name__ == '__main__':
    init_db()
    list_table = 'task_1132_list_nanjing'
    save_table = 'task_1132_nanjing_20180921'
    count = db[list_table].count()
    skip = 0
    while skip < count:
        rows = db[list_table].find({}, {"_id": 0}).sort("_id").skip(skip).limit(10)
        for row in rows:
            referer = row['pageUrl']
            for shop in row['result']:
                link = shop['link']
                if db[save_table].count({'pageUrl': link}) > 0:
                    continue
                log('request shop: ' + link)
                parse_detail(link, referer, shop)
                fail_cnt_desc()
        skip += 10
    print 'finish...'
