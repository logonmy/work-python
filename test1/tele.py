# /usr/bin/env python
# -*- coding: UTF-8 -*-
import csv
import urllib
import os
import re

# 广东单独处理
city_list = [
    'sh'
]
rootdir = u'E:\\work\\data\\tele\\'
prefix = 'http://www.telecredit.cn/mysearch?1532936873609&content='
suffix = '&capital_low=&capital_hight=&foundedtime_low=&foundedtime_hight=&province='
pattern = re.compile(r"^[\d\sa-zA-Z+-.]+")

word_all = set()
file_name = 'key_021dailyzq'
for city in city_list:
    reader = open(rootdir + file_name + ".csv", "r")
    write_file = rootdir + city + "_" + file_name + ".txt"
    out = open(write_file, 'w')
    all_lines = reader.readlines()
    for line in all_lines:
        word = line.split(',')[1]
        word = re.sub(pattern, '', word)
        # for word in words:
        if not word:
            continue
        word = word.strip("\n\"")
        if word not in word_all:
            word_all.add(word)
            codeKey = urllib.quote(word)
            url = prefix + codeKey + suffix + city + '&currentPage='
            for i in range(1, 11):
                newUrl = url + str(i)
                # print newUrl
                out.write(newUrl)
                out.write("\n")
        else:
            print word
    print len(word_all)
    out.close()
    reader.close()
