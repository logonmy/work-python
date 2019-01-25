#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fontTools.ttLib import TTFont
# font = TTFont(r'E:/201809291213-tyc-num.woff')
font = TTFont(r'E:/201809291213-tyc-num.otf')
print font.tables
font['cmap'].tables[0].ttFont.getGlyphOrder()
font['name'].names