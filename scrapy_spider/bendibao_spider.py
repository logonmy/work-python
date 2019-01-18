#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
import re
from utils import geo_util
from my_mongodb import MyMongo


class BendibaoSpider(scrapy.Spider):
    name = "bendibao"
    start_urls = [
        'http://wh.bendibao.com/cyfw/wangdian/455.shtm',
    ]
    db = MyMongo()
    lat_lon_pt = re.compile('"com_jd":"(\d+\.\d+)","com_wd":"(\d+\.\d+)"')

    def parse(self, response):
        for ul in response.xpath('//div[@id="listContent"]/ul'):
            info = dict({'name': ul.xpath('li[1]/a/text()').extract_first(),
                         'address': ul.xpath('li[2]/a/text()').extract_first()})
            yield response.follow(ul.xpath('li[1]/a/@href').extract_first(), self.parse_detail, meta={'info': info})

    def parse_detail(self, response):
        info = response.meta['info']
        # lon = response.xpath('//input[@name="jd"]/@value').extract_first()
        # lat = response.xpath('//input[@name="wd"]/@value').extract_first()
        lon, lat = re.findall(self.lat_lon_pt, response.text)[0]
        lon, lat = geo_util.bd09togcj02(float(lon), float(lat))
        info['lon'] = lon
        info['lat'] = lat
        self.db.save('bendibao', info)
