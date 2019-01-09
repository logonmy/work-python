#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
import base64
import hashlib
import json
import re
from my_mongodb import MyMongo


class BeikeSpider(scrapy.Spider):
    name = "beike"
    start_urls = [
        'http://www.baidu.com/',
    ]
    download_delay = 1
    task_id = 'task_1692'
    db = MyMongo()
    secret = 'd5e343d453aecca8b14b2dc687c381ca'
    appid = '20180111_android:'
    districts_page = 'https://app.api.ke.com/newhouse/shellapp/config/filters?city_id=%s&data_version=201811576011001&request_ts=1542263217'
    # 源码中对queryString做了排序，这里直接把顺序写死
    list_page = 'https://app.api.ke.com/house/community/search?city_id=%s&limit_count=20&limit_offset=%d&region={"group":"district","id":"%s","key":"","name":""}'
    detail_page = 'https://app.api.ke.com/house/resblock/detailpart1?id=%s'
    headers = {
        "Lianjia-City-Id": "420100",
        "User-Agent": "Beike1.10.1;samsung SM-G955F; Android 4.4.2",
        "extension": "lj_android_id=8c164527b8b35295&lj_device_id_android=355757010140164&lj_imei=355757010140164&mac_id=08:00:27:5D:65:DF&lj_duid=DuRx0PGxy9YGXEpNNBtQ1MaTEGr3H5cbir+YpQuz8FQqDWLdD1N0AyWK+DOnN6/8usP7ix8ZNqYV7oKW/t37/n/Q",
        "Lianjia-Channel": "Android_ke_baidupinzhuan",
        "Lianjia-Device-Id": "355757010140164",
        "Lianjia-Version": "1.10.1",
        "Lianjia-Im-Version": "2.17.0-NEWPLUGIN",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip"}
    limit_offset_reg = re.compile(r'(limit_offset=)(\d+)')
    city_list = [
                 # '110000', '120000', '130100', '130200', '130300', '130400', '130500', '130600', '130700', '130800',
                 # '130900', '131000', '131100', '140100', '140200', '140300', '140400', '140500', '140600', '140700',
                 # '140800', '140900', '141000', '141100', '150100', '150200', '150300', '150400', '150500', '150600',
                 # '150700', '150800', '150900', '152200', '152500', '152900', '210100', '210200', '210300', '210400',
                 # '210500', '210600', '210700', '210800', '210900', '211000', '211100', '211200', '211300', '211400',
                 # '220100', '220200', '220300', '220400', '220500', '220600', '220700', '220800', '222400', '230100',
                 # '230200', '230300', '230400', '230500', '230600', '230700', '230800', '230900', '231000', '231100',
                 # '231200', '232700', '310000', '320100', '320200', '320300', '320400', '320500', '320600', '320700',
                 # '320800', '320900', '321000', '321100', '321200', '321300', '330100', '330200', '330300', '330400',
                 # '330500', '330600', '330700', '330800', '330900', '331000', '331100', '340100', '340200', '340300',
                 # '340400', '340500', '340600', '340700', '340800', '341000', '341100', '341200', '341300', '341500',
                 # '341600', '341700', '341800', '350100', '350200', '350300', '350400', '350500', '350600', '350700',
                 # '350800', '350900', '360100', '360200', '360300', '360400', '360500', '360600', '360700', '360800',
                 # '360900', '361000', '361100', '370100', '370200', '370300', '370400', '370500', '370600', '370700',
                 # '370800', '370900', '371000', '371100', '371200', '371300', '371400', '371500', '371600', '371700',
                 # '410100', '410200', '410300', '410400', '410500', '410600', '410700', '410800', '410900', '411000',
                 # '411100', '411200', '411300', '411400', '411500', '411600', '411700', '420100', '420200', '420300',
                 # '420500', '420600', '420700', '420800', '420900', '421000', '421100', '421200', '421300', '422800',
                 # '430100', '430200', '430300', '430400', '430500', '430600', '430700', '430800', '430900', '431000',
                 # '431100', '431200', '431300', '433100', '440100', '440200', '440300', '440400', '440500', '440600',
                 # '440700', '440800', '440900', '441200', '441300', '441400', '441500', '441600', '441700', '441800',
                 # '441900', '442000', '445100', '445200', '445300', '450100', '450200', '450300', '450400', '450500',
                 # '450600', '450700', '450800', '450900', '451000', '451100', '451200', '451300', '451400', '460100',
                 '460200', '460300', '460400', '500000', '510100', '510300', '510400', '510500', '510600', '510700',
                 # '510800', '510900', '511000', '511100', '511300', '511400', '511500', '511600', '511700', '511800',
                 # '511900', '512000', '513200', '513300', '513400', '520100', '520200', '520300', '520400', '520500',
                 # '520600', '522300', '522600', '522700', '530100', '530300', '530400', '530500', '530600', '530700',
                 # '530800', '530900', '532300', '532500', '532600', '532800', '532900', '533100', '533300', '533400',
                 # '540100', '540200', '540300', '540400', '540500', '542400', '542500', '610100', '610200', '610300',
                 # '610400', '610500', '610600', '610700', '610800', '610900', '611000', '620100', '620200', '620300',
                 # '620400', '620500', '620600', '620700', '620800', '620900', '621000', '621100', '621200', '622900',
                 # '623000', '630100', '630200', '632200', '632300', '632500', '632600', '632700', '632800', '640100',
                 # '640200', '640300', '640400', '640500', '650100', '650200', '650400', '650500', '652300', '652700',
                 # '652800', '652900', '653000', '653100', '653200', '654000', '654200', '654300'
                 ]

    def parse(self, response):
        for city in self.city_list:
            url = self.districts_page % city
            headers = {"Lianjia-City-Id": city}
            headers.update(self.headers)
            headers['Authorization'] = self.authorization(url)
            yield response.follow(url, self.parse_district, headers=headers, meta={'city': city})

    def parse_district(self, response):
        city = response.meta['city']
        res = json.loads(response.text)
        if res['errno'] == 0 and res['data']:
            districts = filter(lambda x: x['key'] == 'district_id',
                               filter(lambda x: x['key'] == 'region',
                                      res['data']['check_filter'])[0]['options'])[0]['options']
            for district in districts:
                if 'data' in district:
                    district_id = district['data']['district_id']
                    if district_id in self.city_list:
                        continue
                    headers = {"Page-Schema": "Community%2Flist", "Referer": "homepage", 'Lianjia-City-Id': city}
                    headers.update(self.headers)
                    url = self.list_page % (city, 0, district_id)
                    headers['Authorization'] = self.authorization(url)
                    yield response.follow(url, self.parse_list, headers=headers, meta={'orgi': url, 'city': city})
        else:
            'parse error ...' + response.url

    def parse_list(self, response):
        city = response.meta['city']
        res = json.loads(response.text)
        if res['errno'] == 0 and res['data']:
            for item in res['data']['list']:
                url = self.detail_page % item['community_id']
                headers = {"Page-Schema": "communitydetail", "Referer": "Community%2Flist", 'Lianjia-City-Id': city}
                headers.update(self.headers)
                headers['Authorization'] = self.authorization(url)
                yield response.follow(url, self.parse_detail, headers=headers)

            has_more = res['data']['has_more_data']
            if has_more == 1:
                next_url = re.sub(self.limit_offset_reg, lambda m: m.group(1) + str(int(m.group(2)) + 20),
                                  response.meta['orgi'])
                headers = response.request.headers
                headers['Authorization'] = [self.authorization(next_url)]
                yield response.follow(next_url, self.parse_list, headers=headers, meta={'orgi': next_url, 'city': city})
        else:
            print 'error .... ' + response.url

    def parse_detail(self, response):
        res = json.loads(response.text)
        if res['errno'] == 0 and res['data']:
            data = res['data']
            basic_info = data['basicInfo']
            info = dict()
            info['name'] = basic_info['name']
            info['address'] = basic_info['address']
            buildings = data['buildings']
            info['buildingCount'] = buildings['buildingCount']
            info['houseCount'] = buildings['houseCount']
            info['pageUrl'] = response.url
            result = []
            for build in buildings['list']:
                b = dict()
                b['building'] = build['name']
                b['lat'] = build['pointLat']
                b['lng'] = build['pointLng']
                result.append(b)
            info['result'] = result
            self.db.save(self.task_id, info)
        else:
            print 'error .... ' + response.url

    def authorization(self, url):
        query_str = url[url.find('?') + 1:].replace('&', '')
        local_str = hashlib.sha1(self.secret + query_str).hexdigest()
        return base64.encodestring(self.appid + local_str).strip()

if __name__ == '__main__':
    import requests
    headers = {
        "Lianjia-City-Id": "330100",
        "User-Agent": "Beike1.10.1;samsung SM-G955F; Android 4.4.2",
        "extension": "lj_android_id=8c164527b8b35295&lj_device_id_android=355757010140164&lj_imei=355757010140164&mac_id=08:00:27:5D:65:DF&lj_duid=DuRx0PGxy9YGXEpNNBtQ1MaTEGr3H5cbir+YpQuz8FQqDWLdD1N0AyWK+DOnN6/8usP7ix8ZNqYV7oKW/t37/n/Q",
        "Lianjia-Channel": "Android_ke_baidupinzhuan",
        "Lianjia-Device-Id": "355757010140164",
        "Lianjia-Version": "1.10.1",
        "Lianjia-Im-Version": "2.17.0-NEWPLUGIN",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "Authorization": "MjAxODAxMTFfYW5kcm9pZDpiZWY4ZDU1YzkyNTk5YjExOTUzMzNhNjNhOWY4NjA1NWJiZGE2NmYw"
        }
    url = "https://app.api.ke.com//house/community/search?city_id=330100&limit_count=20&limit_offset=0"
    resp = requests.get(url, headers=headers)
    print resp
# query_str_set = list()
# for i in range(0, 4):
#     a = s[i]
#     for j in range(0, 4):
#         if i == j:
#             continue
#         b = s[j]
#         for k in range(0, 4):
#             if k == j or k == i:
#                 continue
#             c = s[k]
#             for l in range(0, 4):
#                 if l == k or l == j or l == i:
#                     continue
#                 d = s[l]
#                 query_str_set.append(a+b+c+d)
# for qs in query_str_set:
#     secret = 'd5e343d453aecca8b14b2dc687c381ca'
#     appid = '20180111_android:'
#     local_str = hashlib.sha1(secret + qs).hexdigest()
#     print base64.encodestring(appid + local_str).strip() + '===' + qs
