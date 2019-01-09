#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from pyquery import PyQuery as pq
from pymongo import MongoClient
import time


class Item:
    result = []

    def __init__(self, result, pageUrl, timestamp):
        self.result = result
        self.pageUrl = pageUrl
        self.timestamp = timestamp

    def to_dict(self):
        return {'result': self.result, 'pageUrl': self.pageUrl, 'timestamp': self.timestamp}


class Result:
    def __init__(self, name, link, code=None, code1=None):
        self.code = code
        self.link = link
        self.name = name
        self.code1 = code1

    def to_dict(self):
        ret = {}
        for k, v in self.__dict__.items():
            if v:
                ret[k] = v
        return ret


charset = 'GBK'
headers = {
    # Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
    # Accept-Encoding:gzip, deflate, sdch
    # Accept-Language:zh-CN,zh;q=0.8
    # Cache-Control:max-age=0
    # Connection:keep-alive
    # Cookie:td_cookie=3011926935; _trs_uv=jlbq2qvv_6_10iz; AD_RS_COOKIE=20081931
    # Host:www.stats.gov.cn
    # If-Modified-Since:Thu, 05 Jul 2018 00:43:11 GMT
    # If-None-Match:"17b5-57035d4e665c0-gzip"
    # Upgrade-Insecure-Requests:1
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'
}
start_url = "http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/index.html"
cnt_dict = {
    'province_cnt': 0,
    'city_cnt': 0,
    'county_cnt': 0,
    'town_cnt': 0,
    'village_cnt': 0
}
province_set = set()
city_set = set()
county_set = set()
town_set = set()
village_set = set()
db = None
nowTime = lambda: int(round(time.time() * 1000))
province_table = 'task_130_level0_2018082818'
city_table = 'task_130_level1_2018082818'
county_table = 'task_130_level2_2018082818'
town_table = 'task_130_level3_2018082818'
village_table = 'task_130_level4_2018082818'


def get_province(url):
    pageUrl = url
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print 'get_province fail:' + url
        get_province(url)
    else:
        soup = BeautifulSoup(resp.content, "html.parser")
        url_prifex = url[:url.rindex('/') + 1]
        result = []
        for tr in soup.find_all('tr', 'provincetr'):
            for a in tr.find_all('a'):
                name = a.text
                url = url_prifex + a.attrs['href']
                # print url
                province_set.add(url)
                result.append(Result(name, url).to_dict())
        # db[province_table].save(Item(result, pageUrl, nowTime()).to_dict())


def get_city(url):
    pageUrl = url
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print 'get_city fail:' + url
        get_city(url)
    else:
        d = pq(resp.content)
        url_prifex = url[:url.rindex('/') + 1]
        result = []
        for tr in d('.citytr').items():
            a1 = tr('td').eq(0).find('a')
            url = url_prifex + a1.attr('href')
            code = a1.text()
            name = tr('td').eq(1).find('a').text()
            # print url
            city_set.add(url)
            result.append(Result(name, url, code).to_dict())
        # db[city_table].save(Item(result, pageUrl, nowTime()).to_dict())


def get_county(url):
    pageUrl = url
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print 'get_county fail:' + url
        get_county(url)
    else:
        soup = BeautifulSoup(resp.content, "html.parser")
        url_prifex = url[:url.rindex('/') + 1]
        result = []
        trs = soup.find_all('tr', 'countytr')
        if len(trs) == 0:
            print 'get_county fail:' + url
        for tr in soup.find_all('tr', 'countytr'):
            tds = tr.find_all('td')
            a1 = tds[0].find('a')
            if a1:
                code = a1.text
                url = url_prifex + a1.attrs['href']
                name = tds[1].find('a').text
                county_set.add(url)
                result.append(Result(name, url, code).to_dict())
        # db[county_table].save(Item(result, pageUrl, nowTime()).to_dict())


def get_town(url):
    try:
        pageUrl = url
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            print 'get_town request fail:' + url
            get_town(url)
        else:
            soup = BeautifulSoup(resp.content.decode(charset, errors='ignore'), "html.parser")
            url_prifex = url[:url.rindex('/') + 1]
            result = []
            trs = soup.find_all('tr', 'towntr')
            if len(trs) == 0:
                print 'get_town parse fail:' + url
                return
            for tr in soup.find_all('tr', 'towntr'):
                tds = tr.find_all('td')
                a1 = tds[0].find('a')
                if a1:
                    code = a1.text
                    url = url_prifex + a1.attrs['href']
                    name = tds[1].find('a').text
                    town_set.add(url)
                    result.append(Result(name, url, code).to_dict())
            db[town_table].save(Item(result, pageUrl, nowTime()).to_dict())
    except Exception, e:
        print e
        print 'get_town fail:' + url


def get_village(url):
    pageUrl = url
    try:
        resp = requests.get(url, headers=headers, timeout=50)
        if resp.status_code != 200:
            print 'get_village request fail:' + url
            get_village(url)
        else:
            soup = BeautifulSoup(resp.content.decode(charset, errors='ignore'), "html.parser")
            result = []
            trs = soup.find_all('tr', 'villagetr')
            if len(trs) == 0:
                print 'get_village parse fail:' + url
                return
            for tr in soup.find_all('tr', 'villagetr'):
                tds = tr.find_all('td')
                if tds:
                    code = tds[0].text
                    code1 = tds[1].text
                    name = tds[2].text
                    village_set.add(url)
                    result.append(Result(name, url, code, code1).to_dict())
            db[village_table].save(Item(result, pageUrl, nowTime()).to_dict())
    except Exception, e:
        print e
        print 'get_village except fail:' + url


def init_db():
    conn = MongoClient('140.143.94.171', 27017)
    global db
    db = conn.crawler
    db.authenticate('mongodbcrawler', 'Shantianci56')


if __name__ == '__main__':
    init_db()
    # get_province(start_url)
    # print "省级" + str(len(province_set))
    # for url in province_set:
    #     get_city(url)
    # print "地级市" + str(len(city_set))
    # for url in city_set:
    #     get_county(url)
    # county_set = [
    #     'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/46/4604.html'
    # ]
    # print "县级市" + str(len(county_set))
    # for url in county_set:
    #     get_town(url)
    town_set.add('http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/46/04/460400106.html')
    print "乡镇" + str(len(town_set))
    for url in town_set:
        get_village(url)
