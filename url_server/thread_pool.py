# -*- coding: utf-8 -*-

from threading import Thread
from Queue import Queue

tasks = Queue(1000)


def do_task():
    while tasks.get():
        print 'xxx'


def commit_task():
    tasks.put('x')

t1 = Thread(target=do_task, args=[])
t1.setDaemon(True)
t1.start()

print 'xx'
