#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
import re
from my_mongodb import MyMongo
import time
import os

telnum_map = {
    'fn-urRy': '0',
    'fn-FJy9': '2',
    'fn-huhQ': '3',
    'fn-3Ywa': '4',
    'fn-Ws1o': '5',
    'fn-xfkY': '6',
    'fn-zpQd': '7',
    'fn-0lrK': '8',
    'fn-04ho': '8',
}
p_tel = re.compile('fn-\w{4}')
p_shop = re.compile(
    'shopId:\s?"(.*?)".*?shopName:\s?"(.*?)".*?address:\s?"(.*?)".*?shopGlat:\s?"(.*?)".*?shopGlng:\s?"(.*?)"')
db = MyMongo().get_db()
nowTime = lambda: int(round(time.time() * 1000))


class DianpingSpider(scrapy.Spider):
    name = "dianping"
    start_urls = [
        'https://www.dianping.com/wuhan/ch10',
        # 'http://localhost:8888',
    ]
    user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"
    download_delay = 10
    current_city = 'wuhan'
    cookie = None

    def parse(self, response):
        if not response.text:
            print "页面" + response.url + "请求失败"
            yield response.follow(response.url, self.parse)
        else:
            self.cookie = getcookie(self.current_city)
            headers = {'referer': response.url,
                       'cookie': self.cookie}
            for region in response.css("#bussi-nav a"):
                yield response.follow(region.xpath('@href').extract_first(), self.parse_list, headers=headers)

    def parse_list(self, response):
        if not response.xpath("//div[@class='tit']/a[1]"):
            changeip()
            self.cookie = getcookie()
            yield response.follow(response.url, self.parse_list, headers={'cookie': self.cookie})
        else:
            headers = {'referer': response.url,
                       'cookie': self.cookie}
            for shop in response.xpath("//div[@class='tit']/a[1]"):
                yield response.follow(shop.xpath('@href').extract_first(), self.parse_detail, headers=headers, priority=3)
            next_page = response.css('a.next')
            if next_page:
                yield response.follow(next_page.xpath('@href').extract_first(), self.parse_list, headers=headers)

    def parse_detail(self, response):
        result = None
        try:
            avgpricestr = response.xpath("//span[@id='avgPriceTitle']").extract_first()
            commentscorestr = response.xpath("//span[@id='comment_score']").extract_first()
            telstr = response.xpath("//p[@class='expand-info tel']").extract_first()
            script = response.css('.footer-container+script').xpath('text()').extract_first()
            match = p_shop.search(script)
            result = {
                'shopId': match.group(1),
                'shopName': match.group(2),
                'address': match.group(3),
                'shopGlat': match.group(4),
                'shopGlng': match.group(5),
                'tel': telstr,
                'commentscore': commentscorestr,
                'avgprice': avgpricestr
            }
        except Exception, e:
            print e
            pass
        if result:
            item = {'pageUrl': response.url, 'timestamp': nowTime(), 'result': result}
            db['task_1132_20180910'].save(item)
        else:
            time.sleep(5)
            changeip()
            self.cookie = getcookie(self.current_city)
            yield response.follow(response.url, self.parse_list, headers={'cookie': self.cookie}, priority=2)


def changeip():
    os.system('D:\\deploy\\node-changeip\\swip.bat')

from selenium import webdriver
def getcookie(city):
    driver = webdriver.PhantomJS()
    driver.get("http://www.dianping.com/")
    print driver.title
    driver.get("http://www.dianping.com/" + city)
    print driver.title
    driver.get("http://www.dianping.com/" + city + "/ch10")
    print driver.title
    return ";".join([cookie['name'] + "=" + cookie['value'] for cookie in driver.get_cookies()])


def process_tel(telstr):
    telnum = ""
    try:
        numtext = telstr.split('</span>')[1:]
        for line in numtext:
            line = line.strip()
            if not line:
                continue
            idx = line.find('<span')
            if idx > 0:
                telnum += line[0:idx]
                line = line[idx:]
            telnum += telnum_map[p_tel.findall(line)[0]]
    except:
        pass
    return telnum
