#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, time, os, re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'
}


if __name__ == '__main__':
    r = requests.post('http://10.82.248.68:8002/downloadKeyCrawlerFile', {'crawlerTaskId':1710}, headers=headers, stream=True)
    f = open("file_path", "wb")
    for chunk in r.iter_content(chunk_size=512):
        if chunk:
            f.write(chunk)