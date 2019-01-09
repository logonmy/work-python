#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
import re
from my_mongodb import MyMongo


class GzccSpider(scrapy.Spider):
    name = "gzcc"
    start_urls = [
        'http://www.gzcc.gov.cn/data/laho/ProjectSearch.aspx',
    ]
    base_url = 'http://www.gzcc.gov.cn'
    next_page_prefix = 'http://www.gzcc.gov.cn/data/laho/%s'
    sell_form_url_pattern = re.compile('/data/laho/sellForm\.aspx\?pjID=\d+&presell=.*?&chnlname=fdcxmxx')
    db = MyMongo().get_db()

    def parse(self, response):
        for tr in response.css('.resultTableC tr')[1:]:
            info = {}
            href = tr.xpath('td[2]/a/@href').extract_first().strip()
            info['link'] = self.base_url + href
            info['projectName'] = tr.xpath('td[2]/a/text()').extract_first()
            info['projectAddress'] = tr.xpath('td[5]/a/text()').extract_first()
            yield response.follow(self.base_url + href, callback=self.parse_sell_form_url, meta={'info': info})
        next_page = response.xpath('//div[@class="pager"]/a/@href').extract()[-2]
        if next_page is not None:
            yield response.follow(self.next_page_prefix % next_page, self.parse)

    def parse_sell_form_url(self, response):
        sell_form_url = re.findall(self.sell_form_url_pattern, response.text)[0]
        yield response.follow(self.base_url + sell_form_url, callback=self.parse_project, meta=response.meta)

    def parse_project(self, response):
        meta_info = response.meta['info']
        for td in response.xpath('//input[@id="buildingID"]/..'):
            info = {}
            info.update(meta_info)
            info['buildingName'] = td.xpath('text()').extract()[1]
            bid = td.xpath('input/@value').extract_first()
            info['buildingId'] = int(bid)
            yield response.follow('http://www.gzcc.gov.cn/data/laho/sellFormForm.aspx',
                                  method='POST',
                                  headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                  body='houseStatusID=0&modeID=2&inAreaID=0&unitType=0&hfID=0&totalAreaID=0&buildingID='
                                       + bid,
                                  callback=self.parse_building,
                                  meta={'info': info},
                                  dont_filter=True)

    def parse_building(self, response):
        info = response.meta['info']
        rooms = response.xpath('//*[@class="content_tab"]/table/tr/td[1]/a/text()')
        if rooms:
            for room in rooms:
                room_no = room.extract()
                try:
                    info['roomNo'] = int(room_no)
                    info['floor'] = self.get_floor(info['roomNo'])
                except:
                    info['roomNo'] = room_no
                self.db['raw_result_gzcc'].save(info)
                del info['_id']
        else:
            self.db['raw_result_gzcc'].save(info)

    @staticmethod
    def get_floor(room_no):
        if room_no > 0:
            return room_no / 100
        else:
            if room_no < -10000:
                return -(room_no * -1 / 10000)
            elif room_no < -1000:
                return -(room_no * -1 / 1000)
            else:
                return -(room_no * -1 / 100)
