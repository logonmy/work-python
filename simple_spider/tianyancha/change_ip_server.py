#!/usr/bin/env python
# -*- coding: utf-8 -*-

import BaseHTTPServer
import time
import threading
import os
import json


class UrlAction(BaseHTTPServer.BaseHTTPRequestHandler):
    last_time = None
    time_delta = 60  # seconds
    timeout = 60  # seconds

    def do_GET(self):
        self.send_head()
        last_time = self.last_time
        if last_time is None or last_time + self.time_delta < time.time():
            t = threading.Thread(target=self.change_ip)
            t.setDaemon(True)
            t.start()
            t.join(self.timeout)
            UrlAction.last_time = time.time()

        time.sleep(10)
        self.wfile.write(json.dumps({'success': 'ok'}))

    def send_head(self):
        self.send_response(200)
        self.send_header("Content-type", 'application/json;charset=UTF-8')
        self.end_headers()

    @staticmethod
    def change_ip():
        print 'change ip'
        os.system('D:\\node-changeip\\swip.bat')


if __name__ == '__main__':
    server_address = ('127.0.0.1', 4500)
    httpd = BaseHTTPServer.HTTPServer(server_address, UrlAction)
    sa = httpd.socket.getsockname()
    print "Serving HTTP on", sa[0], "port", sa[1], "..."
    httpd.serve_forever()
