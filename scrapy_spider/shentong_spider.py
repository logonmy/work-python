#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
import json
from my_mongodb import MyMongo
import math


class ShentongSpider(scrapy.Spider):
    name = "shentong"
    start_urls = [
        'http://www.zto.com/express/expressWebsite.html',
    ]
    post_url = 'https://hdgateway.zto.com/siteListService'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
        'Content-Type': 'application/json'
    }
    db = MyMongo().get_db()

    def parse(self, response):
        for city in get_all_city():
            yield response.follow(self.post_url, self.parse_detail, 'post', headers=self.headers, body=json.dumps(city),
                                  dont_filter=True)

    def parse_detail(self, response):
        data = json.loads(response.text)
        if data['result']['errorMsg'] != "SUCCESS":
            print 'error: ' + response.url
        else:
            for data_list in data['result']['data']:
                for district in data_list['list']:
                    lng, lat = bd09togcj02(district['longitude'], district['latitude'])
                    self.db['raw_result_zto'].save({
                        'LINK': response.url,
                        'ADDRESS': district['address'],
                        'X_COORD': lng,
                        'Y_COORD': lat,
                        # 'districtName': district['districtName'],
                        'DISPATCH_RANGE': district['dispatchRange'],
                        # 'notDispatchRange': district['notDispatchRange'],
                        'NAME': district['fullName']
                        # 'cityId': district['cityId'],
                        # 'cityName': district['cityName'],
                        # 'code': district['code'],
                        # 'provinceId': district['provinceId'],
                        # 'provinceName': district['provinceName']
                    })


def get_all_city():
    results = []
    with open('..\\resource\\province.json') as pf:
        provinces = json.loads(pf.read())['RECORDS']
        province_dict = {}
        for p in provinces:
            province_dict[p['ADCODE']] = p['NAME']
        with open('..\\resource\\city.json') as cf:
            citys = json.loads(cf.read())['RECORDS']
            for city in citys:
                p_code = city['ADCODE'] / 10000 * 10000
                if province_dict.has_key(p_code):
                    result = {"provinceName": province_dict[p_code],
                              "provinceId": p_code,
                              "cityName": city['NAME'].lstrip(province_dict[p_code]),
                              "cityId": city['ADCODE'],
                              "districtName": "",
                              "districtId": ""}
                    results.append(result)
    return results

x_pi = 3.14159265358979324 * 3000.0 / 180.0
def bd09togcj02(bd_lon, bd_lat):
    x = bd_lon - 0.0065
    y = bd_lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    gg_lng = z * math.cos(theta)
    gg_lat = z * math.sin(theta)
    return [gg_lng, gg_lat]

print bd09togcj02(114.357914, 31.109574)
