#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
import struct
import shutil
import BaseHTTPServer
import urlparse

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class SocketClient:
    def __init__(self, host, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(10)
        self.s.connect((host, port))

    @staticmethod
    def format_query(query_str, in_encoding):
        query_str = query_str.replace("=", ":").replace("&", "\n")
        qsbyte = bytearray(query_str, in_encoding)
        qsbyte_len = len(qsbyte)
        qbyte = ''
        qbyte += struct.pack('<I', 0xFFFFEEEE)
        qbyte += struct.pack('<I', qsbyte_len)
        qbyte += struct.pack('<I', 0x00000000)
        qbyte += qsbyte
        return qbyte

    def execute(self, query_str, in_encoding, out_encoding):
        qbyte = self.format_query(query_str, in_encoding)
        self.s.sendall(qbyte)
        self.s.recv(4)  # head
        rsp_len = struct.unpack('I', self.s.recv(4))[0]  # length
        buffer_size = 1024
        i = rsp_len
        resp_body = ''
        while i > 0:
            resp_body += self.s.recv(buffer_size).decode(out_encoding, errors='ignore')
            i -= buffer_size
        return resp_body

    def close(self):
        self.s.close()


query_str_fmt = 'query_type=TQUERY&query_address=%s&query_tel=%s&data_type=poi&keywords=%s&city=440300&page_num=10&page=1&eid=&templateid=&userid=&sort_rule=7&show_score=true'


def get_result(query_address, query_tel, keywords):
    query_str = query_str_fmt % (query_address, query_tel, keywords)
    # print query_str
    client = SocketClient('10.82.244.24', 18430)
    try:
        resp = client.execute(urlparse.unquote(query_str).decode('utf-8'),
                              in_encoding,
                              out_encoding)
    except Exception, e:
        print e
        resp = ''
    finally:
        client.close()
    return resp


class SimpleHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):
        """Serve a GET request."""
        f = StringIO()
        if '?' not in self.path:
            f.write('request need parameter')
        else:
            path = self.path
            path = path[path.find('?') + 1:]
            params = dict([x.split('=') for x in path.split('&')])
            result = get_result(params.get('address'), params.get('tel'), params.get('name'))
            f.write(result.encode(out_encoding))
        length = f.tell()
        f.seek(0)

        self.send_response(200)
        self.send_header("Content-type", "application/xml")
        self.send_header("Content-Length", str(length))
        self.end_headers()

        if f:
            self.copyfile(f, self.wfile)
            f.close()

    def copyfile(self, source, outputfile):
        shutil.copyfileobj(source, outputfile)


if __name__ == '__main__':
    in_encoding = out_encoding = 'GBK'
    BaseHTTPServer.test(SimpleHTTPRequestHandler, BaseHTTPServer.HTTPServer)
