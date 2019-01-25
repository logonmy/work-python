#/usr/bin/env python
# -*- coding: UTF-8 -*-
import csv
import urllib
import os
import re

#广东单独处理
city_list = [
'hub'
]
rootdir = u'E:\\work\\data\\'
prefix = 'http://www.telecredit.cn/mysearch?1532936873609&content='
suffix = '&capital_low=&capital_hight=&foundedtime_low=&foundedtime_hight=&province='

for city in city_list:
    reader = open(rootdir + "key_027daily-1.csv","r")
    write_file = rootdir+city+".txt"
    out = open(write_file,'w')
    all_lines = reader.readlines()
    for line in all_lines:
        line = line.strip()
        if len(line) > 3:
            print line
            codeKey = urllib.quote(line)
            url = prefix + codeKey + suffix +city +'&currentPage='
            for i in range(1,11):
                newUrl = url + str(i)
                out.write(newUrl)
                out.write("\n")
    out.close()
    reader.close()