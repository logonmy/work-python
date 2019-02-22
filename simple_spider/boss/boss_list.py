#! /user/bin/env python
# -*- coding: utf-8 -*-
import requests
import json
import urllib
from bs4 import BeautifulSoup


def get_leaf_positions(positions):
    ps = []
    for p in positions:
        if p['subLevelModelList']:
            [ps.append(x) for x in get_leaf_positions(p['subLevelModelList'])]
        else:
            ps.append(p['code'])
    return ps


position_url = 'https://www.zhipin.com/common/data/position.json'
resp = requests.get(position_url)
position_json = json.loads(resp.content)
positions = get_leaf_positions(position_json['data'])

# c101280600: 城市； p100101: 职位；e_106：工作经验；b_%E9%BE%99%E5%B2%97%E5%8C%BA: 地区
# https://www.zhipin.com/c101280600-p100101/e_106-b_%E9%BE%99%E5%B2%97%E5%8C%BA/
url_pattern = 'https://www.zhipin.com/c101280600-p%s/%s-b_%s/'
# 地区
bs = ['南山区', '福田区', '龙岗区', '宝安区', '龙华区', '罗湖区', '盐田区', '光明区']
# 工作经验
sel_exps = ['e_102', 'e_103', 'e_104', 'e_105', 'e_106', 'e_107']

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'
}
i = 0
for p in positions:
    for e in sel_exps:
        for b in bs:
            url = url_pattern % (p, e, urllib.quote(b))
            print url
            i += 1
            if i > 9999:
                i = 0
            # resp = requests.get(url, headers=headers, timeout=10)
            # soup = BeautifulSoup(resp.content, 'lxml')
