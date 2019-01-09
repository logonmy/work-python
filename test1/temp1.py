#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import re

import StringIO.StringIO

class A:
    def __init__(self):
        db = 1

    @property
    def dbc(self):
        return self.db

if __name__ == '__main__':
    print A().dbc