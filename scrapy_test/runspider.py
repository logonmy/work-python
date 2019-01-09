#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import optparse
from importlib import import_module

from scrapy.crawler import CrawlerProcess
from scrapy.exceptions import UsageError
from scrapy.utils.spider import iter_spider_classes
from scrapy.utils.project import get_project_settings


def _import_file(filepath):
    abspath = os.path.abspath(filepath)
    dirname, file = os.path.split(abspath)
    fname, fext = os.path.splitext(file)
    if fext != '.py':
        raise ValueError("Not a Python source file: %s" % abspath)
    if dirname:
        sys.path = [dirname] + sys.path
    try:
        module = import_module(fname)
    finally:
        if dirname:
            sys.path.pop(0)
    return module


def run(crawler_process, args, opts):
    if len(args) != 1:
        raise UsageError()
    filename = args[0]
    if not os.path.exists(filename):
        raise UsageError("File not found: %s\n" % filename)
    try:
        module = _import_file(filename)
    except (ImportError, ValueError) as e:
        raise UsageError("Unable to load %r: %s\n" % (filename, e))
    spclasses = list(iter_spider_classes(module))
    if not spclasses:
        raise UsageError("No spider found in file: %s\n" % filename)
    spidercls = spclasses.pop()

    crawler_process.crawl(spidercls, None)
    crawler_process.start()


if __name__ == '__main__':
    argv = sys.argv

    parser = optparse.OptionParser(formatter=optparse.TitledHelpFormatter(), conflict_handler='resolve')
    opts, args = parser.parse_args(args=argv[1:])

    setting = get_project_settings()
    crawler_process = CrawlerProcess(setting)

    run(crawler_process, args, opts)
