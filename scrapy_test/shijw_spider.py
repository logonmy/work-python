#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
from my_mongodb import MyMongo
import json


class ShijwSpider(scrapy.Spider):
    name = "shijw"
    start_urls = [
        'http://www.shjjw.gov.cn',
    ]
    list_url = 'http://www.shjjw.gov.cn/fg/zzjs/jfxk/s?pn=%d&ps=10'
    detail_url = 'http://www.shjjw.gov.cn/fg/zzjs/xkxx?id=%s'
    db = MyMongo().get_db()

    def parse(self, response):
        for i in range(1, 1689 + 1):
            yield response.follow(self.list_url % i, self.parse_list)

    def parse_list(self, response):
        result = json.loads(response.body)
        for item in result['data']['list']:
            yield response.follow(self.detail_url % item['info_id'], callback=self.parse_detail)

    def parse_detail(self, response):
        result = json.loads(response.body)
        data = result['data']
        info = dict()
        info['projectAddress'] = data['dz']
        info['projectName'] = data['xmmc']
        info['infoId'] = data['info_id']
        info['building'] = data['zh']
        info['link'] = response.url
        self.db['raw_result_shijw'].save(info)
