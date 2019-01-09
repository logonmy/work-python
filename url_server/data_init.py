#!/usr/bin/env python
# -*- coding: utf-8 -*-

from util import UrlProcess


def main():
    task_id = 'task_1711_lv0'
    url_process = UrlProcess('118.24.176.167')
    with open(r'E:\work\data\tyc\xiangchen\tyc_beijing_urls.txt') as f:
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
    main()
