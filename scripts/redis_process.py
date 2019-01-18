#!/usr/bin/env python
# -*- coding: utf-8 -*-

import redis

r = redis.Redis(host='localhost', port=6379, db=0)

with open('detail.txt', 'w') as wf:
    for k, v in r.hgetall('detail:hash_data').items():
        wf.write(v+'\n')