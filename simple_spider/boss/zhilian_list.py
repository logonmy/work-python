#! /user/bin/env python
# -*- coding: utf-8 -*-
import requests
import json
import urllib

# https://fe-api.zhaopin.com/c/i/sou?pageSize=90&cityId=2362&workExperience=-1&education=-1&companyType=-1&employmentType=-1&jobWelfareTag=-1&kt=3&_v=0.44753989
url_pattern = 'https://fe-api.zhaopin.com/c/i/sou?pageSize=90&cityId=%s&workExperience=%s&industry=%s'
# 地区
citys = ['2362', '2361', '2044', '2043', '2042', '2041', '2040', '2039', '2038', '2037']
# 行业
hys = ['10100', '10200', '10800', '10900', '10300', '10400', '10000', '11300', '10500', '11500', '11600', '11100',
       '11400']
# 工作经验
exps = ['0000', '0001', '0103', '0305', '0510', '1099']
# 学历
edus = ['1', '3', '4', '5', '7', '8']

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'
}


def get_total(url):
    resp = requests.get(url, headers=headers, timeout=10)
    data = json.loads(resp.content)
    return data['data']['numFound']


def test_urls():
    url_prefix = 'https://fe-api.zhaopin.com/c/i/sou?pageSize=90'
    for p in citys:
        url1 = url_prefix + '&cityId=' + p
        total = get_total(url1)
        if total > 1000:
            for e in exps:
                url2 = url1 + '&workExperience=' + e
                total = get_total(url2)
                if total > 1000:
                    for b in hys:
                        url3 = url2 + '&industry=' + b
                        total = get_total(url3)
                        if total > 1000:
                            for ed in edus:
                                url4 = url3 + '&education=' + ed
                                total = get_total(url4)
                                print url4, total
                        else:
                            print url3, total
                else:
                    print url2, total
        else:
            print url1, total


def generate_urls():
    urls = []
    with open('zhilian_urls') as f:
        for l in f.readlines():
            url, total = l.strip().split(' ')
            if total > 90:
                urls.append(url)
                for i in range(0, int(total) / 90):
                    urls.append(url + '&start=' + str(90 * (i + 1)))
            else:
                urls.append(url)
    with open('zhilian_urls_all', 'w') as f:
        for url in urls:
            f.write(url + '\n')


if __name__ == '__main__':
    generate_urls()
