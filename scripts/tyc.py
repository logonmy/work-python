# /usr/bin/env python
# -*- coding: UTF-8 -*-
import csv
import urllib
import os
import re

rootdir = u'E:\\work\\data\\tyc\\xiangchen\\'
url_pattern = '%s'
# pattern = re.compile(r"[(]\S+[)]")

reader = open(rootdir + "elm_2201_20180604.csv", "r")
write_file = rootdir + "tyc_changchun_keyword.txt"
out = open(write_file, 'w')
all_lines = reader.readlines()
word_set = set()
for line in all_lines:
    try:
        line = line.decode('gb2312').encode('utf8').strip("\"\r\n")
    except:
        continue
    words = line.split(',')
    if len(words) == 6 and words[2] not in word_set:
        word_set.add(words[2])
        out.write(url_pattern % urllib.quote(words[2]))
        out.write("\n")
out.close()
reader.close()


