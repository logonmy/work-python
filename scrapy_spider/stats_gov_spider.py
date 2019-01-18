#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy


class StatGovSpider(scrapy.Spider):
    name = 'stat_gov'
    start_urls = [
        "http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/index.html"
    ]
    charset = 'GBK'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'
    }

    def parse(self, response):
        for a in response.css(".provincetr a"):
            print a.xpath('text()').extract_first()

