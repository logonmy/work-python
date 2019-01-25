#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import time, os

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'
    , 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    , 'Accept-Encoding': 'gzip, deflate, sdch'
}
next_page_url = None
db = None
city = None
table = None
succ_cnt = 0


def get_header(ref=None):
    if ref:
        headers['Referer'] = ref
    return headers


def get_region(url):
    log('get_region: ' + url)
    resp = requests.get(url, headers=get_header())
    soup = BeautifulSoup(resp.text, 'lxml')
    if resp.url.find('verify') != -1 or not resp.text or soup.select_one('.not-found-right>.back-to-home'):
        log('get_region fail:' + url)
        change_ip()
        return get_region(url)
    else:
        # 按行政区
        region_set = set()
        tr = soup.find('div', {"id": 'region-nav'})
        for a in tr.find_all('a'):
            region_set.add(a.attrs['href'])
        log(url + " get " + str(len(region_set)) + " region")
        return region_set


def get_sub_region(url):
    print 'get_sub_region: ' + url
    resp = requests.get(url, headers=get_header())
    soup = BeautifulSoup(resp.text, 'lxml')
    if resp.url.find('verify') != -1 or not resp.text or soup.select_one('.not-found-right>.back-to-home'):
        log('get_sub_region fail:' + url)
        change_ip()
        return get_sub_region(url)
    else:
        # 子行政区
        sub_region_set = set()
        tr = soup.find('div', {"id": 'region-nav-sub'})
        tags = tr.find_all('a')
        if len(tags) > 1:
            for a in tags[1:]:
                sub_region_set.add(a.attrs['href'])
        else:
            sub_region_set.add(url)
        log(url + " get " + str(len(sub_region_set)) + " sub region")
        return sub_region_set


def get_classfy(url):
    print 'get_classfy: ' + url
    resp = requests.get(url, headers=get_header())
    soup = BeautifulSoup(resp.text, 'lxml')
    if resp.url.find('verify') != -1 or not resp.text or soup.select_one('.not-found-right>.back-to-home'):
        log('get_classfy fail:' + url)
        change_ip()
        return get_classfy(url)
    else:
        # 先判断是否是50页 //a[@data-ga-page="50"]
        urls = []
        if soup.find("a", {"data-ga-page": "50"}):
            for classfy in soup.select("div#classfy a"):
                urls.append(classfy.attrs['href'])
            log(url + " get " + str(len(urls)) + " classfy")
        if urls:
            return urls
        else:
            parse_list(url, soup)
            return None


def get_sub_classfy(url):
    print 'get_sub_classfy: ' + url
    resp = requests.get(url, headers=get_header())
    soup = BeautifulSoup(resp.text, 'lxml')
    if resp.url.find('verify') != -1 or not resp.text or soup.select_one('.not-found-right>.back-to-home'):
        log('get_sub_classfy fail:' + url)
        change_ip()
        return get_sub_classfy(url)
    else:
        # 先判断是否是50页 //a[@data-ga-page="50"]
        urls = []
        if soup.find("a", {"data-ga-page": "50"}):
            css_select = "div#classfy-sub a"
            if soup.select(css_select):
                for classfy in soup.select(css_select)[1:]:
                    urls.append(classfy.attrs['href'])
            log(url + " get " + str(len(urls)) + " classfy")
        if urls:
            return urls
        else:
            parse_list(url, soup)
            return None


def get_list(url):
    global succ_cnt
    succ_cnt += 1
    if succ_cnt > 5000:
        change_ip()
        succ_cnt = 0
    print 'get_list: ' + url
    resp = requests.get(url, headers=get_header())
    soup = BeautifulSoup(resp.text, 'lxml')
    if resp.url.find('verify') != -1 or not resp.text or soup.select_one('.not-found-right>.back-to-home'):
        log('get_list fail:' + url)
        change_ip()
        get_list(url)
    else:
        parse_list(url, soup)


def parse_list(url, soup):
    try:
        item = {'pageUrl': url, 'timestamp': now_time()}
        result = []
        for shop in soup.select("div.txt"):
            shop_info = dict()
            shop_info['name'] = shop.select_one("div.tit a h4").text
            addr = shop.select(".tag-addr span")
            shop_info['address'] = addr[1].text
            shop_info['region'] = addr[2].text
            shop_info['shop_id'] = shop.select_one('div.tit a').attrs['data-shopid']
            shop_info['link'] = shop.select_one('div.tit a').attrs['href']
            shop_info['mean_price'] = get_text(shop.select_one(".mean-price b"))
            comment = shop.select('.comment-list span')
            shop_info['kouwei'] = get_text(comment[0].select_one('b')) if comment else None
            shop_info['huanjing'] = get_text(comment[1].select_one('b')) if comment else None
            shop_info['fuwu'] = get_text(comment[2].select_one('b')) if comment else None
            result.append(shop_info)
        item['result'] = result
        save_to_db(item)
        next_page = soup.select_one('a.next')
        global next_page_url
        next_page_url = next_page.attrs['href'] if next_page else None
    except Exception,e:
        log("parse_list fail: " + str(e))


def get_text(tag):
    return tag.text if tag else None


def now_time():
    return int(round(time.time() * 1000))


def save_to_db(item):
    while 1:
        try:
            db[table].save(item)
            break
        except Exception, e:
            log("db error " + str(e))
            init_db()
            time.sleep(30)


def init_db():
    conn = MongoClient('140.143.94.171', 27017)
    global db
    db = conn.crawler
    db.authenticate('mongodbcrawler', 'Shantianci56')


def change_ip():
    os.system('D:\\node-changeip\\swip.bat')
    time.sleep(20)


log_file = open('dianping_list.log', 'a')
def log(msg):
    timestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print timestr + ": " + msg
    log_file.write(timestr + ": " + msg + "\n")


def flush_log():
    log_file.flush()
    log_file.close()


if __name__ == '__main__':
    init_db()
    city_list = [
        # 'beijing',
        # 'wuhan',
        # 'shanghai',
        #  'guangzhou',
         'shenzhen',
        #  'tianjin',
        #  'hangzhou',
        #  'nanjing',
        #  'suzhou',
        #  'chengdu',
        #  'chongqing',
        #  'xian'
    ]
    got_regions = [
        'http://www.dianping.com/shenzhen/ch10/r34',
        'http://www.dianping.com/shenzhen/ch10/r32',
        'http://www.dianping.com/shenzhen/ch10/r30',
        'http://www.dianping.com/shenzhen/ch10/r33',
    ]
    try:
        for cc in city_list:
            city = cc
            start_url = "https://www.dianping.com/" + city + "/ch10"
            table = 'task_1132_list_l2_' + city

            for region in get_region(start_url):
                if region in got_regions:
                    continue
                for sub_region in get_sub_region(region):
                    classfy_links = get_classfy(sub_region)
                    if classfy_links:
                        for link in classfy_links:
                            sub_classfy_links = get_sub_classfy(link)
                            if sub_classfy_links:
                                for sub_link in sub_classfy_links:
                                    next_page_url = sub_link
                                    while next_page_url:
                                        get_list(next_page_url)
                            else:
                                while next_page_url:
                                    get_list(next_page_url)
                    else:
                        while next_page_url:
                            get_list(next_page_url)
    except Exception, e:
        log("program exception " + str(e))
        flush_log()