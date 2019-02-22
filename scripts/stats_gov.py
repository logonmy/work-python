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
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'
}
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
province_table = 'task_1872_level0'
city_table = 'task_1872_level1'
county_table = 'task_1872_level2'
town_table = 'task_1872_level3'
village_table = 'task_1872_level4'


def get_province(url):
    pageUrl = url
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print 'get_province fail:' + url
        get_province(url)
    else:
        soup = BeautifulSoup(resp.content.decode(charset, errors='ignore'), "html.parser")
        url_prifex = url[:url.rindex('/') + 1]
        result = []
        for tr in soup.find_all('tr', 'provincetr'):
            for a in tr.find_all('a'):
                name = a.text
                url = url_prifex + a.attrs['href']
                # print url
                province_set.add(url)
                result.append(Result(name, url).to_dict())
        db[province_table].save(Item(result, pageUrl, nowTime()).to_dict())


def get_city(url):
    pageUrl = url
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print 'get_city fail:' + url
        get_city(url)
    else:
        d = pq(resp.content.decode(charset, errors='ignore'))
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
        db[city_table].save(Item(result, pageUrl, nowTime()).to_dict())


def get_county(url):
    pageUrl = url
    try:
        resp = requests.get(url, headers=headers)
    except:
        print 'get_county request fail:' + url
        return
    if resp.status_code != 200:
        print 'get_county request fail:' + url
        get_county(url)
    else:
        soup = BeautifulSoup(resp.content.decode(charset, errors='ignore'), "html.parser")
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
            else:
                code = tds[0].text
                name = tds[1].text
                result.append(Result(name, None, code).to_dict())
        db[county_table].save(Item(result, pageUrl, nowTime()).to_dict())


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
                else:
                    code = tds[0].text
                    name = tds[1].text
                    result.append(Result(name, None, code).to_dict())
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
    start_url = "http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/index.html"
    init_db()
    # get_province(start_url)
    # print "省级" + str(len(province_set))
    # for url in province_set:
    #     get_city(url)
    # print "地级市" + str(len(city_set))
    # for url in city_set:
    #     get_county(url)
    # print "县级市" + str(len(county_set))
    # for url in county_set:
    #     get_town(url)
    town_set = [
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/35/08/24/350824108.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/44/53/03/445303106.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/41/13/22/411322101.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/33/06/83/330683002.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/36/07/81/360781104.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/23/06/22/230622588.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/32/01/13/320113406.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/23/09/21/230921200.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/12/01/02/120102011.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/50/02/42/500242105.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/52/03/25/520325108.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/41/05/27/410527100.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/14/11/29/141129201.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/23/01/84/230184202.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/13/02/07/130207105.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/44/08/83/440883003.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/63/28/21/632821500.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/35/07/83/350783103.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/23/06/24/230624205.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/44/05/07/440507008.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/52/05/22/520522216.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/45/02/05/450205005.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/21/07/82/210782209.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/41/01/08/410108003.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/36/04/81/360481100.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/42/90/04/429004100.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/32/09/22/320922403.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/33/04/24/330424105.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/62/11/02/621102108.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/23/01/04/230104111.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/36/09/24/360924102.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/45/12/21/451221204.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/41/04/82/410482110.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/32/10/23/321023109.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/21/09/21/210921125.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/51/14/02/511402106.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/42/90/04/429004003.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/13/07/06/130706002.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/34/04/03/340403101.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/42/01/16/420116402.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/62/05/02/620502108.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/11/01/16/110116001.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/53/25/02/532502203.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/37/02/11/370211100.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/45/03/27/450327104.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/36/09/21/360921104.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/14/09/81/140981102.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/23/06/06/230606205.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/45/10/27/451027102.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/50/01/05/500105007.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/45/09/21/450921104.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/51/13/02/511302007.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/44/12/23/441223110.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/13/06/07/130607104.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/34/16/23/341623119.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/53/05/81/530581111.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/35/01/25/350125207.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/51/34/26/513426200.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/15/08/23/150823107.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/37/08/31/370831103.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/37/09/23/370923001.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/13/01/08/130108101.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/21/01/23/210123101.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/42/03/22/420322204.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/34/04/04/340404100.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/41/04/21/410421100.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/51/17/81/511781103.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/52/26/30/522630104.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/62/11/25/621125105.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/34/11/72/341172001.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/36/01/21/360121100.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/51/34/29/513429212.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/45/02/05/450205008.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/51/13/24/511324209.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/63/28/01/632801401.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/44/12/84/441284003.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/33/08/03/330803100.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/15/29/23/152923201.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/21/09/21/210921105.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/61/08/30/610830107.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/36/07/23/360723107.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/64/05/22/640522400.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/22/24/03/222403104.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/42/06/06/420606400.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/51/19/21/511921202.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/53/29/24/532924101.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/44/09/81/440981119.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/52/27/01/522701001.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/41/16/23/411623108.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/35/06/03/350603103.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/36/08/30/360830108.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/32/09/81/320981100.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/36/03/21/360321207.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/32/07/06/320706006.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/41/04/25/410425001.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/37/08/83/370883103.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/65/40/04/654004003.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/51/13/22/511322210.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/41/05/23/410523103.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/37/15/23/371523103.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/41/04/81/410481003.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/35/07/83/350783109.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/32/05/07/320507004.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/22/07/81/220781103.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/54/02/27/540227209.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/54/02/27/540227209.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/35/04/24/350424103.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/35/04/24/350424103.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/51/05/24/510524105.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/63/26/21/632621201.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/52/23/02/522302109.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/23/27/62/232762102.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/54/02/25/540225200.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/14/09/31/140931201.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/23/11/82/231182483.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/62/30/22/623022209.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/51/01/83/510183110.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/51/13/22/511322103.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/13/03/03/130303004.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/37/03/21/370321104.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/42/03/25/420325206.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/51/01/21/510121110.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/42/01/04/420104009.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/63/25/21/632521402.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/33/06/24/330624102.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/42/01/11/420111081.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/34/12/22/341222119.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/37/14/03/371403102.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/36/07/02/360702104.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/61/09/02/610902102.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/51/13/22/511322213.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/65/28/27/652827104.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/53/28/23/532823403.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/65/01/02/650102014.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/37/01/03/370103021.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/34/01/23/340123108.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/33/06/02/330602006.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/22/02/71/220271001.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/51/18/22/511822203.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/43/12/22/431222238.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/62/04/23/620423400.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/22/08/81/220881102.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/43/01/82/430182002.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/22/06/21/220621201.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/62/06/02/620602110.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/23/02/23/230223202.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/45/10/26/451026100.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/52/05/26/520526117.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/65/31/25/653125002.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/62/11/23/621123105.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/15/09/81/150981109.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/51/06/04/510604106.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/44/03/10/440310002.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/53/06/25/530625203.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/15/07/25/150725503.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/11/01/07/110107004.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/13/09/22/130922104.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/36/07/25/360725101.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/44/07/83/440783111.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/23/03/21/230321102.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/13/10/03/131003005.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/43/11/03/431103002.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/23/07/03/230703409.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/36/06/03/360603408.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/52/01/81/520181203.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/13/07/08/130708202.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/51/17/25/511725125.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/61/01/13/610113009.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/36/09/23/360923107.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/43/02/25/430225203.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/51/11/24/511124107.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/45/07/02/450702101.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/21/01/03/210103006.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/43/11/24/431124005.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/43/01/12/430112007.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/43/01/82/430182101.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/44/12/04/441204106.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/44/14/81/441481136.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/33/05/23/330523001.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/34/11/82/341182100.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/34/01/72/340172005.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/36/09/25/360925100.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/63/02/22/630222209.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/37/11/03/371103001.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/32/02/14/320214453.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/52/03/02/520302009.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/13/04/25/130425106.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/42/12/21/421221106.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/65/40/25/654025204.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/21/07/26/210726108.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/23/04/07/230407002.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/15/08/23/150823106.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/22/08/02/220802200.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/53/07/22/530722201.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/52/26/26/522626108.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/52/06/21/520621204.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/23/12/82/231282205.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/42/10/23/421023102.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/15/29/21/152921405.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/23/10/83/231083103.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/52/03/30/520330107.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/13/05/28/130528104.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/13/04/26/130426103.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/62/11/24/621124111.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/23/01/10/230110013.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/41/13/28/411328105.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/34/01/04/340104003.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/61/04/04/610404003.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/44/15/02/441502103.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/21/06/81/210681105.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/41/17/21/411721500.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/13/08/27/130827103.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/61/01/22/610122105.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/23/08/22/230822103.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/42/12/22/421222106.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/34/15/22/341522206.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/23/01/83/230183206.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/14/07/24/140724204.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/37/11/22/371122109.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/45/10/81/451081104.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/14/08/25/140825106.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/21/10/21/211021101.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/62/11/22/621122110.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/41/17/22/411722107.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/52/23/02/522302003.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/41/13/24/411324303.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/13/04/31/130431202.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/23/09/21/230921101.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/14/10/21/141021101.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/51/33/32/513332206.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/62/07/02/620702105.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/37/17/21/371721106.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/65/29/28/652928102.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/21/05/02/210502011.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/15/07/22/150722400.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/13/04/26/130426104.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/36/08/28/360828202.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/61/04/25/610425109.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/46/90/05/469005115.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/51/17/81/511781223.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/61/05/27/610527109.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/35/09/81/350981112.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/14/02/13/140213004.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/42/05/06/420506401.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/64/03/81/640381104.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/45/08/81/450881101.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/13/07/30/130730102.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/13/07/05/130705200.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/53/29/26/532926102.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/14/11/82/141182102.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/13/07/08/130708101.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/43/06/23/430623102.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/35/09/82/350982201.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/53/29/27/532927102.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/51/01/21/510121109.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/15/08/26/150826107.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/21/02/24/210224104.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/35/08/81/350881205.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/21/01/81/210181206.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/43/11/21/431121111.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/14/08/29/140829202.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/51/07/27/510727201.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/34/08/26/340826212.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/41/16/23/411623109.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/42/05/05/420505003.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/14/08/81/140881100.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/34/16/22/341622112.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/44/01/06/440106007.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/12/01/19/120119108.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/23/01/02/230102006.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/21/03/23/210323005.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/22/07/02/220702405.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/51/19/22/511922103.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/37/06/84/370684103.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/13/02/09/130209406.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/13/11/26/131126103.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/14/07/28/140728102.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/32/02/82/320282100.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/51/33/25/513325206.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/23/10/04/231004003.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/13/01/32/130132105.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/15/22/01/152201103.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/23/01/04/230104009.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/65/31/27/653127506.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/41/04/22/410422108.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/13/10/22/131022100.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/43/07/25/430725002.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/23/01/08/230108101.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/63/01/21/630121100.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/36/06/03/360603507.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/43/08/22/430822228.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/42/28/26/422826400.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/44/53/22/445322400.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/36/11/28/361128213.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/14/08/22/140822204.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/44/09/83/440983117.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/34/13/02/341302009.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/52/27/25/522725108.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/14/11/21/141121105.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/35/08/23/350823103.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/45/08/21/450821104.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/62/08/02/620802105.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/13/11/24/131124104.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/51/13/03/511303106.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/43/31/30/433130237.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/41/16/22/411622106.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/43/10/81/431081220.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/37/05/23/370523109.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/14/02/25/140225100.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/44/16/22/441622123.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/51/18/26/511826201.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/32/09/22/320922109.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/62/01/02/620102004.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/51/01/17/510117108.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/33/04/24/330424005.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/41/15/21/411521002.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/43/11/22/431122109.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/14/01/07/140107009.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/15/08/23/150823104.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/43/02/25/430225200.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/23/01/03/230103010.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/51/16/23/511623206.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/23/12/25/231225585.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/41/14/71/411471001.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/32/06/84/320684409.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/42/10/81/421081103.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/44/07/81/440781106.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/34/17/02/341702105.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/51/11/24/511124215.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/37/11/22/371122400.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/42/09/23/420923101.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/43/06/21/430621112.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/36/11/28/361128106.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/65/40/02/654002008.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/15/06/23/150623101.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/41/13/22/411322401.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/65/23/28/652328205.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/23/11/81/231181200.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/42/13/81/421381107.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/52/27/25/522725104.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/13/07/05/130705004.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/54/25/26/542526202.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/52/26/28/522628102.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/32/12/02/321202401.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/44/02/32/440232113.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/51/17/81/511781230.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/52/06/24/520624002.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/64/03/24/640324104.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/41/01/06/410106004.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/53/06/29/530629104.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/33/10/24/331024107.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/35/05/05/350505001.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/41/15/03/411503102.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/22/07/23/220723200.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/62/04/22/620422120.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/41/16/21/411621107.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/50/02/37/500237222.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/41/04/23/410423106.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/37/02/83/370283005.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/14/06/81/140681101.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/53/26/23/532623102.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/34/15/22/341522400.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/15/25/30/152530200.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/15/07/81/150781012.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/15/07/83/150783007.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/51/08/12/510812213.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/41/16/27/411627112.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/13/08/26/130826105.html',
        'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/52/26/32/522632104.html'
    ]
    print "乡镇" + str(len(town_set))
    for url in town_set:
        get_village(url)
