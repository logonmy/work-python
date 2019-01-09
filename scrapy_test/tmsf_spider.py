#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
import re
import urlparse
from my_mongodb import MyMongo


class TmsfSpider(scrapy.Spider):
    name = "tmsf"
    start_urls = [
        'http://www.tmsf.com/hzweb/newhouse/'
    ]
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'
    search_url = 'http://www.tmsf.com/newhouse/property_searchall.htm?searchkeyword=&keyword=&sid=&districtid=&areaid=&dealprice' \
                 '=&propertystate=&propertytype=&ordertype=&priceorder=&openorder=&view720data=&page=%d&bbs=&avanumorder=&comnumorder='
    next_page_url_postfix = '?isopen=1&presellid=&buildingid=&area=&allprice=&housestate=&housetype=&page=%d'
    next_page_pattern = re.compile('class="c" onclick=\"doPage\((\d+)\);return false;')
    url_base = 'http://www.tmsf.com'
    db = MyMongo()
    task_id = 'task_1686'
    download_delay = 5
    cookie = 'td_cookie=808556956; UM_distinctid=166ecf16d760-08a517c2b35d6f-414f0120-1fa400-166ecf16d77622; grwng_uid=97dee8ec-9ef1-4b1a-8bed-afdd9abc68dd; BSFIT_EXPIRATION=1541782146552; BSFIT_DEVICEID=iH-Fe6sWABvLJWdksEsELthRGtsMk7pBnpqqF3fQPShVJOEKezYEN8Ghh0vRYfzbzKl2Kkl0OycYB1SFmMikNlrTtZaaMFfEmMCEtMgWglM1tBJN9wY9unanS1kDG13nCWby53wmhwtrKzg_P-M_JLuQGbtL_lKa; JSESSIONID=5B59C953A6E2B28FF721D221AE4938DE; gr_user_id=ca9d657b-6a54-4e5c-b4f0-2fe108087745; b61f24991053b634_gr_session_id_f618c667-4506-4fd9-883c-0ef5010877df=true; b61f24991053b634_gr_session_id=f618c667-4506-4fd9-883c-0ef5010877df; Hm_lvt_bbb8b9db5fbc7576fd868d7931c80ee1=1541573537; Hm_lpvt_bbb8b9db5fbc7576fd868d7931c80ee1=1541735197; CNZZDATA1253675216=270082236-1541572800-%7C1541731020; BSFIT_8topm=DL40DLZzJLFwupP3DP,Dp8TJpDwDLvdD8'
    headers = {'Cookie': cookie,
               'Accept-Language': 'zh-CN,zh;q=0.8',
               'Cache-Control': 'no-cache',
               'Pragma': ' no-cache'}

    def parse(self, response):
        for page in range(1, 378):
            yield response.follow(self.search_url % page, self.parse_list, headers=self.headers,
                                  meta={'dont_merge_cookies': True})

    def parse_list(self, response):
        if response.text.find('<title>') == -1:
            yield response.follow(response.url, self.parse_list, dont_filter=True, headers=self.headers,
                                  meta={'dont_merge_cookies': True})
        else:
            for div in response.css('div.build_txt'):
                build_name = div.xpath('div[1]/a/text()').extract_first().strip()
                other_name = div.css('.fl').xpath('text()').extract_first()
                info = dict({'buildName': build_name, 'otherName': other_name, 'pageUrl': response.url})
                has_detail_page = False
                for a in div.xpath('div[@class="build_txt2"]/a'):
                    if a.xpath('text()').extract_first() == u'一房一价':
                        has_detail_page = True
                        yield response.follow(a.xpath('@href').extract_first(), callback=self.parse_page,
                                              meta={'info': info, 'dont_merge_cookies': True}, headers=self.headers)
                if not has_detail_page:
                    self.db.save(self.task_id, info)

    def parse_page(self, response):
        if response.text.find('<title>') == -1:
            yield response.follow(response.url, self.parse_list, dont_filter=True, headers=self.headers,
                                  meta={'dont_merge_cookies': True})
        else:
            info = response.meta['info']
            info['pageUrl'] = response.url
            trs = response.css('div.onbuildshow_contant > div.onbuildshow_contant table tr')
            for tr in trs:
                info['loudong'] = tr.xpath('td[1]/a/text()').extract_first()
                info['fanghao'] = tr.xpath('td[2]/a/div/text()').extract_first()
                self.db.save(self.task_id, info)
                del info['_id']

            next_page = re.findall(self.next_page_pattern, ''.join(response.css('.spagenext').extract()))
            if next_page:
                scheme, netloc, path, _, _, _ = urlparse.urlparse(response.url)
                next_page_url = self.url_base + path + self.next_page_url_postfix % next_page[0]
                yield response.follow(next_page_url, self.parse_page)
