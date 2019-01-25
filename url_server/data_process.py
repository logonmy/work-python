#!/usr/bin/env python
# -*- coding: utf-8 -*-

from util import RedisClient, UrlProcess
import sys


def del_urls(key, pattern=None):
    r = RedisClient().get_redis()
    urls = filter(lambda x: x[0] == 'E', r.smembers(key))
    if urls:
        r.srem(key, *urls)


def fail_retry(key):
    r = RedisClient().get_redis()
    url_process = UrlProcess()
    while True:
        urls = [x[x.rfind('/') + 1:] for x in r.spop(key + ':failed', 1000)]
        if urls:
            url_process.insert_urls(key, urls)
        else:
            break


def data_init(fp):
    task_id = 'task_1711_lv0'
    url_process = UrlProcess()
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


def print_usage():
    print 'Usage: %s [-i datafile] [-r key]' % (lambda x: x[x.rfind('/') + 1:])(sys.argv[0])


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print_usage()
        exit()
    if sys.argv[1] == '-i':
        data_init(sys.argv[2])
    elif sys.argv[1] == '-r':
        fail_retry(sys.argv[2])
    elif sys.argv[1] == '-d':
        fail_retry(sys.argv[2])
    else:
        print_usage()
