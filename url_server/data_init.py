#!/usr/bin/env python
# -*- coding: utf-8 -*-

from util import UrlProcess
import sys


def main(fp):
    task_id = 'task_1711_lv0'
    url_process = UrlProcess('118.24.176.167')
    with open(fp) as f:
        lines = f.readlines()
        line_arr = []
        for line in lines:
            line_arr.append(line)
            if len(line_arr) >= 200:
                url_process.insert_urls(task_id, line_arr)
                line_arr = []
        if line_arr:
            url_process.insert_urls(task_id, line_arr)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: data_init.py data_file'
        exit()
    main(sys.argv[1])
