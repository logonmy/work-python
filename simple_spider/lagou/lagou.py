# /usr/bin/env python
# -*- coding: UTF-8 -*-

import requests
import json
import time
from selenium import webdriver
from pymongo import MongoClient

headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Cookie': 'JSESSIONID=ABAAABAABEEAAJA57ACC6152DA09BD5CF9FC7D26D3E7C2C;Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1550215945;Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1550215945;user_trace_token=20190215153225-d6ef68db-30f3-11e9-81f7-5254005c3644;_ga=GA1.2.927570450.1550215945;_gat=1;LGSID=20190215153225-d6ef6a12-30f3-11e9-81f7-5254005c3644;PRE_SITE=;PRE_HOST=;PRE_UTM=;PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F;LGRID=20190215153225-d6ef6b2d-30f3-11e9-81f7-5254005c3644;LGUID=20190215153225-d6ef6b8e-30f3-11e9-81f7-5254005c3644;_gid=GA1.2.347360680.1550215945;index_location_city=%E5%85%A8%E5%9B%BD',
    'Host': 'www.lagou.com',
    'Origin': 'https://www.lagou.com',
    'Pragma': 'no-cache',
    'Referer': 'https://www.lagou.com/jobs/list_Java',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
    'X-Anit-Forge-Code': '0',
    'X-Anit-Forge-Token': 'None',
    'X-Requested-With': 'XMLHttpRequest'
}


def init_driver():
    ua = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'
    cap = webdriver.DesiredCapabilities.PHANTOMJS
    cap["phantomjs.page.settings.userAgent"] = ua
    cap["phantomjs.page.customHeaders.User-Agent"] = ua
    driver = webdriver.PhantomJS(
        executable_path=r"D:\exe\phantomjs.exe",
        desired_capabilities=cap)
    driver.implicitly_wait(30)
    return driver


def refresh_cookies(url):
    driver = init_driver()
    try:
        driver.get(url)
        headers['Cookie'] = ";".join([cookie['name'] + "=" + cookie['value'] for cookie in driver.get_cookies()])
    finally:
        if driver:
            driver.close()
            driver.quit()


def request_result(url, data=None):
    if not data:
        data = {'first': 'true', 'pn': 1}
    print url, data
    while True:
        resp = requests.post(url, data, headers=headers, timeout=10)
        result = json.loads(resp.content)
        if 'content' not in result:
            refresh_cookies('https://www.lagou.com/jobs/list_?' + url.split('?')[1])
            time.sleep(1)
        else:
            break
    position_result = result['content']['positionResult']
    return position_result['result'], position_result['totalCount']


def now_time():
    return int(round(time.time() * 1000))


def init_db():
    while 1:
        try:
            conn = MongoClient('140.143.94.171', 27017)
            global db
            db = conn.crawler
            db.authenticate('mongodbcrawler', 'Shantianci56')
            break
        except:
            time.sleep(5)


def save_to_db(item):
    while 1:
        try:
            db['task_1875_level0_' + time.strftime("%Y%m%d%H", time.localtime())].save(item)
            break
        except Exception, e:
            init_db()


def parse_and_request_next(url, position_result, total):
    parse_position_result(position_result)
    if total > 15:
        for pn in range(1, total / 15 + 1):
            p, _ = request_result(url, {'first': 'true', 'pn': pn + 1})
            parse_position_result(p)


def parse_position_result(position_result):
    for r in position_result:
        item = {'timestamp': now_time()}
        result = {}
        result['longitude'] = r['longitude']
        result['latitude'] = r['latitude']
        result['HangYe'] = r['industryField']
        result['QiYeRenShu'] = r['companySize']
        result['ZhiWeiMingChen'] = r['positionName']
        result['QiYeMingChen'] = r['companyFullName']
        result['FaBuShiJian'] = r['createTime']
        result['RongZiLun'] = r['financeStage']
        result['CompanyId'] = r['companyId']
        result['JobId'] = r['positionId']
        result['district'] = r['district']
        result['city'] = r['city']
        item['result'] = result
        item['pageUrl'] = 'https://www.lagou.com/jobs/%s.html' % r['positionId']
        save_to_db(item)


city_district = {
    '深圳': [
        '南山区',
        '福田区',
        '宝安区',
        '龙岗区',
        '龙华新区',
        '罗湖区',
        '光明新区',
        '盐田区',
        '坪山新区',
        '大鹏新区',
    ]
}

jd = ['未融资', '天使轮', 'A轮', 'B轮', 'C轮', 'D轮及以上', '上市公司', '不需要融资']
hy = ['移动互联网', '电子商务', '金融', '企业服务', '教育', '文化娱乐', '游戏', 'O2O', '硬件']
gm = ['少于15人', '15-50人', '50-150人', '150-500人', '500-2000人', '2000人以上']
xl = ['大专', '本科', '硕士', '博士', '不要求']
gj = ['3年及以下', '3-5年', '5-10年', '10年以上']
# gx = ['全职', '实习']
# yx = ['2k以下', '2k-5k', '5k-10k', '10k-15k', '15k-25k', '25k-50k', '50k以上']

url_prefix = 'https://www.lagou.com/jobs/positionAjax.json?px=default&needAddtionalResult=false'
limit = 450

if __name__ == '__main__':
    init_db()
    for k, v in city_district.items():
        url_param_1 = '&city=' + k
        for d in v:
            url_param_2 = url_param_1 + '&district=' + d
            url = url_prefix + url_param_2
            position_result, total = request_result(url)
            if total > limit:
                for i in jd:
                    url_param_3 = url_param_2 + '&jd=' + i
                    url = url_prefix + url_param_3
                    position_result, total = request_result(url)
                    if total > limit:
                        for j in hy:
                            url_param_4 = url_param_3 + '&hy=' + j
                            url = url_prefix + url_param_4
                            position_result, total = request_result(url)
                            if total > limit:
                                for m in gm:
                                    url_param_5 = url_param_4 + '&gm=' + m
                                    url = url_prefix + url_param_5
                                    position_result, total = request_result(url)
                                    if total > limit:
                                        for n in xl:
                                            url_param_6 = url_param_5 + '&xl=' + n
                                            url = url_prefix + url_param_6
                                            position_result, total = request_result(url)
                                            if total > limit:
                                                for o in gj:
                                                    url_param_7 = url_param_6 + '&gj=' + o
                                                    url = url_prefix + url_param_7
                                                    position_result, total = request_result(url)
                                                    parse_and_request_next(url, position_result, total)
                                            else:
                                                parse_and_request_next(url, position_result, total)
                                    else:
                                        parse_and_request_next(url, position_result, total)
                            else:
                                parse_and_request_next(url, position_result, total)
                    else:
                        parse_and_request_next(url, position_result, total)
            else:
                parse_and_request_next(url, position_result, total)
