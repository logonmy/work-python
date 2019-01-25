# /usr/bin/env python
# -*- coding: UTF-8 -*-

import requests
import re
import json

# 深圳 -- 254375
# resp = requests.get('https://sou.zhaopin.com/?jl=765')
# initial_stat_pattern = re.compile('<script>__INITIAL_STATE__=(.*?)</script>')
# initial_stat = re.findall(initial_stat_pattern, resp.content)
# data = json.loads(initial_stat[0])
# data['']

# url_prefix = 'https://fe-api.zhaopin.com/c/i/sou?pageSize=90&cityId=%s&workExperience=-1&education=-1&companyType=-1' \
#              '&employmentType=-1&jobWelfareTag=-1&kt=3&_v=0.44307880&x-zp-page-request-id=' \
#              '4d186747e5a94f6ca48f0dc6460839e7-1548054069638-396475'
# for area_id in ['2362', '2361', '2044', '2043', '2042', '2041', '2040', '2039', '2038', '2037']:
#     resp = requests.get(url_prefix % area_id)
#     data = json.loads(resp.content)
#     data = data['data']
#     print area_id, data['numFound'], data['numTotal']


url_prefix = 'https://fe-api.zhaopin.com/c/i/sou?pageSize=90&cityId=%s&salary=%s&workExperience=-1&education=%s&companyType=-1' \
             '&employmentType=-1&jobWelfareTag=-1&kt=3&_v=0.44307880&x-zp-page-request-id=' \
             '4d186747e5a94f6ca48f0dc6460839e7-1548054069638-396475'
for area_id in ['2362', '2361', '2044', '2043', '2042', '2041', '2040', '2039', '2038', '2037']:
    for salary in ['1,1000', '1001,2000', '2001,4000', '4001,6000', '6001,8000', '8001,10000', '10001,15000',
                   '15001,25000', '25001,35000', '35001,50000', '50001,70000', '70001,100000', '100001,999999']:
        for edu in ['1', '3', '4', '5', '7', '8']:
            resp = requests.get(url_prefix % (area_id, salary, edu))
            data = json.loads(resp.content)
            data = data['data']
            print area_id, data['numFound'], data['numTotal'], salary, edu
