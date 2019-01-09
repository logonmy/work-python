#!/usr/bin/env python
# -*- coding: utf-8 -*-

import redis


class RedisClient:
    def __init__(self, host='localhost', port=6379, password=None, db=0):
        self._host = host
        self._port = port
        self._password = password
        self._db = db
        self._pool = self._init_pool()

    def _init_pool(self):
        return redis.ConnectionPool(max_connections=10, host=self._host, port=self._port, db=self._db)

    def get_redis(self):
        return redis.Redis(connection_pool=self._pool)


class UrlProcess:
    waiting_queue_postfix = ':waiting'
    running_queue_postfix = ':running'
    failed_queue_postfix = ':failed'
    success_cnt_postfix = ':success:cnt'

    def __init__(self, host='localhost'):
        self.rc = RedisClient(host=host).get_redis()

    def insert_urls(self, key, urls):
        r = self.rc
        r.sadd(key + self.waiting_queue_postfix, *urls)

    def get_urls(self, key, count):
        r = self.rc
        values = r.spop(key + self.waiting_queue_postfix, count)
        if values:
            r.sadd(key + self.running_queue_postfix, *values)
        return values

    def process_result(self, key, success_urls, failed_urls):
        r = self.rc
        if success_urls:
            r.srem(key + self.running_queue_postfix, *(success_urls + failed_urls))
            r.incr(key + self.success_cnt_postfix, len(success_urls))
        if failed_urls:
            r.sadd(key + self.failed_queue_postfix, *failed_urls)
