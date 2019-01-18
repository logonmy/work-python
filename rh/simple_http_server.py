#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import posixpath
import BaseHTTPServer
import urllib
import shutil
import mimetypes
import re
import import_origin_data
import create_bm_task
import recycle_bm_task
import create_tc_task
import recycle_tc_task
import update_tc_result


try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class Request:
    def __init__(self, params):
        self.params = params

    def get_required(self, name):
        if name not in self.params or self.params[name] == '':
            raise Exception("参数错误，[%s]不能为空" % name)
        return self.params[name]


class SimpleHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):
        """Serve a GET request."""
        f = self.send_head()
        if f:
            self.copyfile(f, self.wfile)
            f.close()

    def do_HEAD(self):
        """Serve a HEAD request."""
        f = self.send_head()
        if f:
            f.close()

    def do_POST(self):
        """Serve a POST request."""
        r = True
        msg = '执行成功！！！'
        req = None
        try:
            req = Request(self.deal_post_data())
        except Exception, e:
            r = False
            msg = e.message
        if r:
            try:
                op = req.get_required('op')
                if op == '1':
                    import_origin_data.main(req.get_required('filename'))
                elif op == '2':
                    create_bm_task.main(req.get_required('begin_day').replace('-', ''), req.get_required('end_day').replace('-', ''))
                elif op == '3':
                    recycle_bm_task.main(req.get_required('filename'))
                elif op == '4':
                    create_tc_task.main(req.get_required('begin_day').replace('-', ''), req.get_required('end_day').replace('-', ''))
                elif op == '5':
                    recycle_tc_task.main(req.get_required('filename'))
                elif op == '6':
                    update_tc_result.main(req.get_required('task_day'))
                else:
                    msg = '暂未实现！'
            except Exception, e:
                r = False
                msg = e.message
        f = StringIO()
        f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write("<html>\n<title>执行结果</title>\n")
        f.write("<body>\n<h2>执行结果</h2>\n")
        f.write("<hr>\n")
        if r:
            f.write("<strong>Success:</strong>")
        else:
            f.write("<strong>Failed:</strong>")
        f.write(msg)
        f.write("<br><h2><a href=\"%s\">Back</a></h2>" % self.headers['referer'])
        f.write("</body>\n</html>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html;charset=utf-8")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        if f:
            self.copyfile(f, self.wfile)
            f.close()

    def deal_post_data(self):
        boundary = self.headers.plisttext.split("=")[1]
        remainbytes = int(self.headers['content-length'])
        line, remainbytes = self._read_line(remainbytes)
        if not boundary in line:
            raise Exception("Content NOT begin with boundary")
        param_dict = {}
        while remainbytes > 0:
            line, remainbytes = self._read_line(remainbytes)
            if 'name="file"' in line:
                param_name = 'filename'
                filename = re.findall(r'filename="(.*)"', line)[0]
                if filename == '':
                    raise Exception("请选择文件")
                param_value, remainbytes = self.receive_file(filename, remainbytes, boundary)
            else:
                param_name = re.findall(r'name="(.*)"', line)
                if param_name and param_name[0] != '':
                    param_name = param_name[0]
                _, remainbytes = self._read_line(remainbytes)
                line, remainbytes = self._read_line(remainbytes)
                param_value = line.strip()
                _, remainbytes = self._read_line(remainbytes)
            param_dict[param_name] = param_value
        return param_dict

    def receive_file(self, filename, remainbytes, boundary):
        path = self.translate_path(self.path)
        fn = os.path.join(path, "temp", filename)
        while os.path.exists(fn):
            fn += "_"
        fn = fn.replace("\\", '/').decode('utf-8')
        _, remainbytes = self._read_line(remainbytes)
        _, remainbytes = self._read_line(remainbytes)
        try:
            out = open(fn, 'wb')
        except IOError, e:
            raise Exception(message=e.message)
        preline, remainbytes = self._read_line(remainbytes)
        while remainbytes > 0:
            line, remainbytes = self._read_line(remainbytes)
            if boundary in line:
                preline = preline[0:-1]
                if preline.endswith('\r'):
                    preline = preline[0:-1]
                out.write(preline)
                out.close()
                break
            else:
                out.write(preline)
                preline = line
        return fn, remainbytes

    def _read_line(self, remainbytes):
        line = self.rfile.readline()
        remainbytes -= len(line)
        return line, remainbytes

    def send_head(self):
        """Common code for GET and HEAD commands.
        This sends the response code and MIME headers.
        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.
        """
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.response_html(path)
        ctype = self.guess_type(path)
        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", ctype)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f

    def response_html(self, path):
        f = StringIO()
        with open('web/index.html') as html_file:
            for line in html_file.readlines():
                f.write(line)
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html;charset=UTF-8")
        self.send_header("Content-Length", str(length))
        self.send_header("Encoding", "utf-8")
        self.end_headers()
        return f

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.
        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)
        """
        # abandon query parameters
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = os.getcwd()
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        return path

    def copyfile(self, source, outputfile):
        """Copy all data between two file objects.
        The SOURCE argument is a file object open for reading
        (or anything with a read() method) and the DESTINATION
        argument is a file object open for writing (or
        anything with a write() method).
        The only reason for overriding this would be to change
        the block size or perhaps to replace newlines by CRLF
        -- note however that this the default server uses this
        to copy binary data as well.
        """
        shutil.copyfileobj(source, outputfile)

    def guess_type(self, path):
        """Guess the type of a file.
        Argument is a PATH (a filename).
        Return value is a string of the form type/subtype,
        usable for a MIME Content-type header.
        The default implementation looks the file's extension
        up in the table self.extensions_map, using application/octet-stream
        as a default; however it would be permissible (if
        slow) to look inside the data to make a better guess.
        """

        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']

    if not mimetypes.inited:
        mimetypes.init()  # try to read system mime.types
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream',  # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
    })


def test(HandlerClass=SimpleHTTPRequestHandler,
         ServerClass=BaseHTTPServer.HTTPServer):
    BaseHTTPServer.test(HandlerClass, ServerClass)


if __name__ == '__main__':
    test()
