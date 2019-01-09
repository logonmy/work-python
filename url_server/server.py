#!/usr/bin/env python
# -*- coding: utf-8 -*-

import BaseHTTPServer
import urlparse
import re
import json
from util import UrlProcess


class UrlAction(BaseHTTPServer.BaseHTTPRequestHandler):
    url_process = UrlProcess()
    page_limit = 200
    path_pattern = re.compile('^/[\w_]+$')
    ctype = 'application/json'

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
        self.send_head()
        path = urlparse.urlsplit(self.path).path
        content_type = self.headers['Content-Type']
        if not re.match(self.path_pattern, path):
            self.wfile.write('{"msg": "you must give the right key"}')
        elif content_type != self.ctype:
            self.wfile.write('{"msg": "' + ("content type must be %s" % self.ctype) + '"}')
        else:
            key = path[1:]
            jstr = self.rfile.read(int(self.headers['content-length']))
            data = json.loads(jstr)
            if data:
                if 'new' in data and data['new']:
                    self.url_process.insert_urls(key, data['new'])
                elif 'success' in data and 'failed' in data:
                    self.url_process.process_result(key, data['success'], data['failed'])
                self.wfile.write('{"msg": "ok"}')

    def send_head(self):
        self.send_response(200)
        self.send_header("Content-type", 'application/json;charset=UTF-8')
        self.end_headers()


if __name__ == '__main__':
    server_address = ('127.0.0.1', 1234)
    httpd = BaseHTTPServer.HTTPServer(server_address, UrlAction)
    sa = httpd.socket.getsockname()
    print "Serving HTTP on", sa[0], "port", sa[1], "..."
    httpd.serve_forever()
