#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import re


with open('E:\\work\\temp\\temp') as f:
    cs = ['040100', '040200', '040300', '040400', '040500', '040600', '040700', '040800', '040900', '041000']
    for line in f.readlines():
        for c in cs:
            print line.replace('[keyword]', c).strip()
