#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
from pymongo.errors import PyMongoError
from my_mongodb import MyMongo
import time


class DianpingListSpider(scrapy.Spider):
    name = "dianping_list"
    start_urls = ['https://www.dianping.com/shenzhen/ch10']
    download_delay = 2
    user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"
    db = MyMongo().get_db()
    exec_cnt = 0

    def incr_cnt(self):
        self.exec_cnt += 1
        if self.exec_cnt >= 500:
            time.sleep(1)
            self.exec_cnt = 0

    def parse(self, response):
        self.incr_cnt()
        if not response.text:
            print "页面" + response.url + "请求失败"
            yield response.follow(response.url, self.parse, dont_filter=True)
        else:
            region_path = "//div[@id='bussi-nav']/a | //div[@id='region-nav']/a"
            if response.xpath(region_path):
                for region in response.xpath(region_path):
                    yield response.follow(region.xpath('@href').extract_first(), self.parse_list)
            else:
                print '\''+ response.url + '\','
                # 迭代器
                _gen = self.parse_list(response)
                try:
                    while 1:
                        yield next(_gen)
                except StopIteration:
                    pass

    def parse_list(self, response):
        self.incr_cnt()
        try:
            if not response.xpath("//div[@class='tit']/a[1]"):
                yield response.follow(response.url, self.parse_list, dont_filter=True)
            else:
                pageUrl = response.url
                # start_idx = 25 if pageUrl.find('https') > -1 else 24
                # city = pageUrl[start_idx:pageUrl.find('/', start_idx)]
                item = {'pageUrl': pageUrl, 'timestamp': int(round(time.time() * 1000))}
                result = []
                for shop in response.xpath("//div[@class='txt']"):
                    shop_info = {}
                    shop_info['name'] = shop.xpath('div/a/h4/text()').extract_first()
                    shop_info['address'] = shop.css('.tag-addr').xpath("span[@class='addr']/text()").extract_first()
                    shop_info['region'] = shop.css('.tag-addr').xpath("a[2]/span[@class='tag']/text()").extract_first()
                    shop_info['shop_id'] = shop.xpath('div[1]/a[1]/@data-shopid').extract_first()
                    shop_info['link'] = shop.xpath('div[1]/a[1]/@href').extract_first()
                    shop_info['mean_price'] = shop.css(".mean-price").xpath("b/text()").extract_first()
                    shop_info['kouwei'] = shop.xpath("span[@class='comment-list']/span[1]/b/text()").extract_first()
                    shop_info['huanjing'] = shop.xpath("span[@class='comment-list']/span[2]/b/text()").extract_first()
                    shop_info['fuwu'] = shop.xpath("span[@class='comment-list']/span[3]/b/text()").extract_first()
                    result.append(shop_info)
                item['result'] = result
                # self.db['task_1132_list_' + str(time.strftime("%Y%m%d", time.localtime()))].save(item)
                self.db['task_1132_list_shenzhen_20180925'].save(item)
                next_page = response.css('a.next')
                if next_page:
                    yield response.follow(next_page.xpath('@href').extract_first(), self.parse_list)
        except PyMongoError:
            print 'db error, reconnect..'
            self.db = MyMongo.get_db()
        except Exception, e:
            print e


