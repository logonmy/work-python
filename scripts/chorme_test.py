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
driver.get('https://www.tianyancha.com/search?key=%E6%AD%A6%E6%B1%89%E5%B8%82%E6%B1%9F%E6%B1%89%E5%8C%BA%E6%9C%89%E5%96%9C%E7%94%B5%E5%AD%90%E5%95%86%E5%8A%A1%E7%BB%8F%E8%90%A5%E9%83%A8')
print driver.title
#
# driver.delete_all_cookies()
# driver.get("https://www.dianping.com/wuhan/ch10")
# print driver.title
# driver.get("https://www.dianping.com/wuhan/ch10/r8190")
# print driver.title
# driver.find_element_by_xpath("//div[@class='navbar']/a[1]").click()
# # time.sleep(10)
# driver.get("http://www.dianping.com/shop/97779139")
# print driver.title
# driver
# waiter = WebDriverWait(driver, 10)
# waiter.until(lambda d: d.find_elements_by_tag_name("a"))

driver.quit()