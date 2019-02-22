#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import time, random


ua = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 vvv/537.36'
cap = webdriver.DesiredCapabilities.PHANTOMJS
cap["phantomjs.page.settings.userAgent"] = ua
cap["phantomjs.page.customHeaders.User-Agent"] = ua
# cap["phantomjs.page.customHeaders.Accept"] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
# cap["phantomjs.page.customHeaders.Accept-Encoding"] =  'gzip, deflate, sdch'

# driver = webdriver.PhantomJS(executable_path=r"E:\work\exe\phantomjs.exe", desired_capabilities=cap)
driver = webdriver.Chrome(executable_path=r"E:\work\exe\chromedriver.exe")
driver.implicitly_wait(20)
driver.get('https://www.lagou.com/')
print ";".join([cookie['name'] + "=" + cookie['value'] for cookie in driver.get_cookies()])

driver.quit()