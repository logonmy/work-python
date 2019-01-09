#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import urlparse
import requests
import time
from base_spider import BaseSpider


class TmsfSpider(BaseSpider):
    name = "tmsf"
    schema_host = 'http://www.tmsf.com'
    base_url = 'http://www.tmsf.com/hzweb/newhouse/'
    search_url = 'http://www.tmsf.com/newhouse/property_searchall.htm?searchkeyword=&keyword=&sid=&districtid=&areaid=&dealprice' \
                 '=&propertystate=&propertytype=&ordertype=&priceorder=&openorder=&view720data=&page=%d&bbs=&avanumorder=&comnumorder='
    next_page_url_postfix = '?isopen=1&presellid=&buildingid=&area=&allprice=&housestate=&housetype=&page=%d'
    next_page_pattern = re.compile('class="c" onclick=\"doPage\((\d+)\);return false;')
    total_page_pt = re.compile('\d+/(\d+)')
    task_id = 'task_1686'
    download_delay = 5

    def main(self):
        self.get_cookie([self.base_url], False)
        for page in range(1, 378):
            print self.search_url % page
            resp = self.request(self.search_url % page, self.base_url)
            self.parse_list(resp)

    def request(self, url, referer):
        time.sleep(self.download_delay)
        print 'request ' + url
        try:
            self.headers['Referer'] = referer
            resp = requests.get(url, headers=self.headers, timeout=60)
            if resp.status_code != 200 or resp.text.find('<title>') == -1:
                if resp.status_code != 200:
                    self.get_cookie([self.base_url, url], True)
                return self.request(url, referer)
            else:
                self.logger.info('success: ' + url)
                return resp
        except:
            self.get_cookie([self.base_url, url], True)
            return self.request(url, referer)

    def parse_list(self, response):
        for div in self.soup(response).select('div.build_txt'):
            build_name = self.get_text(div.select_one('div').select_one('a')).strip()
            other_name = self.get_text(div.select_one('.fl'))
            info = dict({'buildName': build_name, 'otherName': other_name, 'pageUrl': response.url})
            has_detail_page = False
            for a in div.select('.build_txt2 a'):
                if a.text == u'一房一价':
                    has_detail_page = True
                    detail_url = self.schema_host + a.get('href')
                    resp = self.request(detail_url, response.url)
                    self.parse_page(resp, meta={'info': info})

                    total_page = self.get_total_page(resp)
                    _, _, path, _, _, _ = urlparse.urlparse(resp.url)
                    for p in range(2, total_page + 1):
                        detail_url = self.schema_host + path + self.next_page_url_postfix % p
                        resp = self.request(detail_url, resp.url)
                        self.parse_page(resp, meta={'info': info})
            if not has_detail_page:
                self.save(self.task_id, info)

    def parse_page(self, response, meta):
        info = meta['info']
        info['pageUrl'] = response.url
        sp = self.soup(response)
        trs = sp.select('div.onbuildshow_contant > div.onbuildshow_contant table tr')
        result = []
        for tr in trs:
            loudong = self.get_text(tr.select('td')[0].select_one('a'))
            fanghao = self.get_text(tr.select('td')[1].select_one('a > div'))
            result.append({'loudong': loudong, 'fanghao': fanghao})
        info['result'] = result
        self.save(self.task_id, info)

    def get_total_page(self, response):
        total_num = int(re.findall(self.total_page_pt, self.soup(response).select_one('.spagenext').text)[0])
        if total_num % 6 == 0:
            return total_num / 6
        else:
            return total_num / 6 + 1


if __name__ == '__main__':
    TmsfSpider().main()
