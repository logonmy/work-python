#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
import struct
import re
import csv
import sys
import os
import time
import xml.dom.minidom


class SocketClient:
    def __init__(self, host, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(10)
        self.s.connect((host, port))
        self.xml_parser = xml.dom.minidom

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

    def parse_xml(self, xml_str):
        # 暂时不支持中文。。。
        dom = self.xml_parser.parseString(xml_str)
        print dom.getroot()

    def close(self):
        self.s.close()


companymatch = re.compile('<companymatch>(.*?)</companymatch>')
Delivered = re.compile('<Delivered>(.*?)</Delivered>')
addrmatch = re.compile('<addrmatch>(.*?)</addrmatch>')
telmatch = re.compile('<telmatch>(.*?)</telmatch>')
searchtime = re.compile('<searchtime>(.*?)</searchtime>')


def parse(resp_text):
    return {
        'companymatch': get_first(re.findall(companymatch, resp_text)),
        'Delivered': get_first(re.findall(Delivered, resp_text)),
        'addrmatch': get_first(re.findall(addrmatch, resp_text)),
        'telmatch': get_first(re.findall(telmatch, resp_text)),
        'searchtime': get_first(re.findall(searchtime, resp_text))
    }


query_str_fmt = 'query_type=TQUERY&query_address=%s&query_tel=%s&data_type=poi&keywords=%s&city=440300&page_num=10&page=1&eid=&templateid=&userid=&sort_rule=7&show_score=true'


def get_result(query_address, query_tel, keywords):
    query_str = query_str_fmt % (query_address, query_tel, keywords)
    print query_str
    # client = SocketClient('10.82.244.24', 18430)
    try:
        resp = client.execute(query_str.decode('utf-8'),
                              in_encoding,
                              out_encoding)
    except Exception, e:
        print e
        resp = ''
    # client.close()
    return parse(resp)


def test():
    # client = SocketClient('10.82.244.24', 18430)
    query_str = 'query_type=TQUERY&query_address=深圳市南山区科技中一路华强高新发展大楼12楼1201-1206&query_tel=0755-66826666&data_type=poi&keywords=华强方特设计院（深圳）有限公司&city=440300&page_num=10&page=1&eid=&templateid=&userid=&sort_rule=7&show_score=true'
    resp = client.execute(query_str.decode('utf-8'), in_encoding, out_encoding)
    print resp
    print parse(resp)


def main():
    start = time.time()
    with open(input_file) as csvfile:
        with open(output_file, 'w') as csvwrite_file:
            csv_reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            fieldnames = csv_reader.fieldnames

            out_fieldnames = fieldnames + ['companymatch', 'Delivered', 'addrmatch', 'telmatch', 'searchtime']
            csv_writer = csv.DictWriter(csvwrite_file, out_fieldnames, quoting=csv.QUOTE_ALL, lineterminator='\n')
            csv_writer.writeheader()

            if 'NAME' in fieldnames:
                for i, fields in enumerate(csv_reader):
                    result = get_result(fields.get('ADDRESS'), get_first(fields.get('TEL')), fields.get('NAME'))
                    fields.update(result)
                    csv_writer.writerow(fields)
            else:
                raise Exception("csv中没有名称为NAME的列")
    print 'total elapse %s ms' % (time.time() - start)


def get_first(l, s=';'):
    if type(l) == list:
        return l[0] if len(l) > 0 else ''
    if l and s:
        return l.split(s)[0]
    else:
        return ''


if __name__ == '__main__':
    client = SocketClient('10.82.244.24', 18430)
    in_encoding = out_encoding = 'GBK'
    test()
    test()
    # if len(sys.argv) < 2:
    #     print 'Usage: python %s xxx.csv' % sys.argv[0]
    #     exit(1)
    # input_file = sys.argv[1]
    # if os.path.isfile(input_file):
    #     path, filename = os.path.split(input_file)
    #     filename, file_postfix = filename.split('.')
    #     output_file = os.path.join(path, filename + '_output.' + file_postfix)
    #     client = SocketClient('10.82.244.24', 18430)
    #     in_encoding = out_encoding = 'GBK'
    #     test()
    #     test()
    # else:
    #     print 'File not found: %s' % input_file
