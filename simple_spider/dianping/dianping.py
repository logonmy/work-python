#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from pyquery import PyQuery as pq
from pymongo import MongoClient
import time, os, random
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'
    , 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    , 'Accept-Encoding': 'gzip, deflate, sdch'
    , 'Accept-Language': 'zh-CN,zh;q=0.8'
    , 'Cache-Control': 'max-age=0'
    , 'Proxy-Connection': 'keep-alive'
    , 'Upgrade-Insecure-Requests': '1'
}
region_list = set()
next_page_url = None
detail_set = set()
db = None
nowTime = lambda: int(round(time.time() * 1000))

city = None
table = None
driver = None
referer = None


def initdriver():
    global driver
    if not driver:
        cap = webdriver.DesiredCapabilities.PHANTOMJS
        cap["phantomjs.page.settings.userAgent"] = \
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36"
        cap["phantomjs.page.customHeaders.User-Agent"] = \
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'
        driver = webdriver.PhantomJS(
            executable_path=r"E:\java\trunk\src\YayCrawler-work\exec\phantomjs\window\phantomjs.exe",
            desired_capabilities=cap)
        # driver = webdriver.Chrome(executable_path=r"E:\work\exe\chromedriver.exe")
        driver.get("https://www.dianping.com/")


def verify(driver, url):
    getcookie()
    # driver.get(url)
    # title = driver.title
    # WebDriverWait(driver, 30).until(
    #     lambda the_driver: the_driver.find_element_by_xpath("//div[@id='yodaBoxWrapper']").is_displayed())
    # element = driver.find_element_by_xpath("//div[@id='yodaBox']")
    # ActionChains(driver).click_and_hold(on_element=element).perform()
    # time.sleep(0.15)
    # for i in range(0, 19):
    #     ActionChains(driver).move_by_offset(10, 1).perform()
    #     time.sleep(random.randint(10, 50) / 100)
    # ActionChains(driver).move_by_offset(6, 0).perform()
    # ActionChains(driver).release(on_element=element).perform()
    # if driver.title == title:
    #     verify(driver, url)
    # else:
    #     headers['Cookie'] = ";".join([cookie['name'] + "=" + cookie['value'] for cookie in driver.get_cookies()])


def getheader(ref):
    headers['Referer'] = ref
    return headers


def changeip():
    os.system('D:\\node-changeip\\swip.bat')
    time.sleep(20)


def getcookie(url=None):
    global city
    # changeip()
    if url:
        driver.get(url)
        print driver.title
    else:
        driver.get("http://www.dianping.com/")
        print driver.title
        driver.get("http://www.dianping.com/" + city)
        print driver.title
        driver.get("http://www.dianping.com/" + city + "/ch10")
        print driver.title
    headers['Cookie'] = ";".join([cookie['name'] + "=" + cookie['value'] for cookie in driver.get_cookies()])
    print headers['Cookie']


def getfromdriver(url):
    driver.get(url)
    return driver.page_source


def get_region(url):
    print 'get_region: ' + url
    resp = requests.get(url, headers=getheader(''))
    soup = BeautifulSoup(resp.text, "html.parser")
    if resp.url.find('verify.meituan.com') != -1:
        print 'get_region show virify:' + url
        global driver
        verify(driver, resp.url)
        get_region(url)
    elif not resp.text or not soup.find_all('div', {"id": 'bussi-nav'}):
        print 'get_region fail:' + url
        getcookie(url)
        get_region(url)
    else:
        for tr in soup.find_all('div', {"id": 'bussi-nav'}):
            for a in tr.find_all('a'):
                region_list.add(a.attrs['href'])


def get_detail_and_next(url, ref):
    # resp = requests.get(url, headers=getheader(ref))
    resp = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'})
    soup = BeautifulSoup(resp.content, "html.parser")
    if resp.url.find('verify.meituan.com') != -1:
        print 'get_detail_and_next show veriry :' + url
        global driver
        verify(driver, resp.url)
        get_detail_and_next(url, ref)
    elif not resp.text or not soup.find_all('div', 'tit'):
        print 'get_detail_and_next fail:' + url
        global driver
        getcookie(url)
        get_detail_and_next(url, ref)
    else:
        global referer
        referer = url

        # //div[@class='tit']/a[1]
        for tr in soup.find_all('div', 'tit'):
            for a in tr.find_all('a'):
                detail_set.add(a.attrs['href'])
                break
        next_page = soup.find('a', 'next')
        global next_page_url
        next_page_url = next_page.attrs['href'] if next_page else None


def parse_detail(url, ref):
    time.sleep(3)
    resp = requests.get(url, headers=getheader(ref))
    if resp.url.find('verify.meituan.com') != -1:
        print 'parse_detail show veriry :' + url
        global driver
        verify(driver, resp.url)
        parse_detail(url, ref)
    elif not resp.text or resp.text.find("window.shop_config") == -1:
        print 'get_detail fail:' + url
        getcookie(url)
        parse_detail(url, ref)
    else:
        d = pq(resp.text)
        avgpricestr = d("#avgPriceTitle").html()
        commentscorestr = d("#comment_score").html()
        telstr = d(".expand-info.tel").html()
        script = d('.footer-container+script').html()
        result = {
            'shop_config': script,
            'tel': telstr,
            'commentscore': commentscorestr,
            'avgprice': avgpricestr
        }
        item = {'pageUrl': url, 'timestamp': nowTime(), 'result': result}
        save_to_db(item)


def save_to_db(item):
    while 1:
        try:
            db[table].save(item)
            break
        except:
            print "db 异常"
            init_db()
            time.sleep(30)


def init_db():
    conn = MongoClient('140.143.94.171', 27017)
    global db
    db = conn.crawler
    db.authenticate('mongodbcrawler', 'Shantianci56')


if __name__ == '__main__':
    # init_db()
    # initdriver()
    city_list = [
        # 'beijing',
        # 'wuhan',
        # 'shanghai',
        # 'guangzhou',
        # 'shenzhen',
        'tianjin',
        'hangzhou',
        'nanjing',
        'suzhou',
        'chengdu',
        'chongqing',
        'xian'
    ]

    for cc in city_list:
        city = cc
        start_url = "https://www.dianping.com/" + city + "/ch10"
        print start_url
        # table = 'task_1132_list' + city
        # get_region(start_url)
        # print "rigion size " + str(len(region_list))
        # if not region_list:
        #     exit(0)
        # try:
        #     getcookie()
        #     for region in region_list:
        #         print 'request region: ' + region
        #         get_detail_and_next(region, start_url)
        #         referer = region
        #         while detail_set:
        #             print "detail size " + str(len(detail_set))
        #             for detail in detail_set:
        #                 if db[table].count({'pageUrl': detail}) > 0:
        #                     continue
        #                 parse_detail(detail, referer)
        #             detail_set.clear()
        #             if next_page_url:
        #                 print 'request next_page_url: ' + next_page_url
        #                 get_detail_and_next(next_page_url, referer)
        # except Exception, e:
        #     print e
        # finally:
        #     if driver:
        #         driver.close()
        #         driver = None
