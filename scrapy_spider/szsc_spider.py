#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
from my_mongodb import MyMongo
import urlparse
import re


class SzscSpider(scrapy.Spider):
    name = "szsc"
    start_urls = [
        'http://www.sz.gov.cn/school/ssxx/',
        # 'http://www.sz.gov.cn/school/ba/baqxx/xazx_01_1_1/ywxx/'
    ]
    db = MyMongo()
    sub_ptn = re.compile('<style[\s\S]*?</style>|</?.*?>')
    cnt = 0

    def parse(self, response):
        yield response.follow(response.url, callback=self.parse_list, dont_filter=True)
        for sc in response.xpath('//li[@class="sliderNav"]/ul/li/a/@href'):
            yield response.follow(sc, callback=self.parse_list)


    def parse_list(self, response):
        c = len(response.css('li.list_name > div'))
        self.cnt += c
        for sc in response.css('li.list_name > div'):
            jgkk = sc.xpath('p[1]/a/@href').extract_first()
            ywxx = sc.xpath('p[2]/a/@href').extract_first()
            yield response.follow(jgkk, callback=self.parse_jggk, meta={'ywxx': urlparse.urljoin(response.url, ywxx)})
            # break  # only test one

    def parse_jggk(self, response):
        info = dict()
        info['name'] = response.xpath('//div[@class="zx_ml_list"]/div[2]/span/text()').extract_first()
        table = response.xpath('//div[@class="tabCon"]')[0].xpath('table')
        if table:
            # info['name'] = table.xpath('tr[1]/th/text()').extract_first()
            # if info['name'] == u'机构名称':
            #     print 'xxxx'
            info['type'] = table.xpath('tr[2]/td[2]/text()').extract_first()
            info['attr'] = table.xpath('tr[3]/td[2]/text()').extract_first()
            info['address'] = table.xpath('tr[5]/td[2]/text()').extract_first()
        yield response.follow(response.meta['ywxx'], callback=self.parse_ywxx, meta={'info': info})

    def parse_ywxx(self, response):
        info = response.meta['info']
        table = response.xpath('//div[@class="tabCon"]')[0].xpath('table')
        if table:
            source_range = ' '.join([self.get_text(item) for item in table.xpath('tr[1]/td[2]').extract()])
            info['source_range'] = source_range
        info['link'] = response.url
        self.db.save('task_1672', info)

    def get_text(self, item):
        return self.sub_ptn.sub('', item)

    def closed(self, reason):
        print '总共==='+str(self.cnt)