#!/usr/bin/env python
# -*- coding: utf-8 -*-

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urlparse
import re
import json
from util import UrlProcess
# from threadpool import ThreadPool, makeRequests
from threading import Thread
from Queue import Queue


class UrlAction(BaseHTTPRequestHandler):
    url_process = UrlProcess()
    page_limit = 200
    path_pattern = re.compile('^/[\w_]+$')
    ctype = 'application/json'
    tasks = Queue(100)

    def __init__(self, request, client_address, server):
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)
        for i in range(4):
            t = Thread(target=self.run_loop, args=[])
            t.setDaemon(True)
            t.start()

    def run_loop(self):
        t = self.tasks.get()
        while t:
            self._do_post(t)
            t = self.tasks.get()

    def commit_task(self):
        self.tasks.put(self)

    def do_GET(self):
        self.send_head()
        path = urlparse.urlsplit(self.path).path
        if not re.match(self.path_pattern, path):
            self.wfile.write('you must give the key')
        else:
            key = path[1:]
            data = self.url_process.get_urls(key, self.page_limit)
            self.wfile.write(json.dumps(data))

    def do_POST(self):
        self.commit_task()

    @staticmethod
    def _do_post(x_self):
        x_self.send_head()
        path = urlparse.urlsplit(x_self.path).path
        content_type = x_self.headers['Content-Type']
        if not re.match(x_self.path_pattern, path):
            x_self.wfile.write('{"msg": "you must give the right key"}')
        elif content_type != x_self.ctype:
            x_self.wfile.write('{"msg": "' + ("content type must be %s" % x_self.ctype) + '"}')
        else:
            key = path[1:]
            jstr = x_self.rfile.read(int(x_self.headers['content-length']))
            data = json.loads(jstr)
            if data:
                if 'new' in data and data['new']:
                    x_self.url_process.insert_urls(key, data['new'])
                elif 'success' in data and 'failed' in data:
                    x_self.url_process.process_result(key, data['success'], data['failed'])
                x_self.wfile.write('{"msg": "ok"}')

    def send_head(self):
        self.send_response(200)
        self.send_header("Content-type", 'application/json;charset=UTF-8')
        self.end_headers()


if __name__ == '__main__':
    server_address = ('127.0.0.1', 1234)
    httpd = HTTPServer(server_address, UrlAction)
    sa = httpd.socket.getsockname()
    print "Serving HTTP on", sa[0], "port", sa[1], "..."
    httpd.serve_forever()
