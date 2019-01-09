#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
import logging
from pymongo import MongoClient
from selenium import webdriver
from bs4 import BeautifulSoup


class BaseSpider:
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'
    name = None

    def __init__(self):
        self.db = None
        self.logger = None
        self.headers = self.default_headers()
        self.init_db()
        self.init_logger()

    def init_logger(self):
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        fh = logging.FileHandler(self.name + '.log', mode='a')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        self.logger = logger

    def default_headers(self):
        return dict({'User-Agent': self.user_agent,
                     'Accept-Language': 'zh-CN,zh;q=0.8',
                     'Cache-Control': 'no-cache',
                     'Pragma': 'no-cache'})

    def get_cookie(self, urls, chang_ip=True):
        if chang_ip:
            self.change_ip()
        driver = self.init_driver()
        try:
            print 'driver get'
            driver.delete_all_cookies()
            for url in urls:
                driver.get(url)
                print driver.title
                time.sleep(5)
            self.headers['Cookie'] = ";".join(
                [cookie['name'] + "=" + cookie['value'] for cookie in driver.get_cookies()])
        except Exception, e:
            print 'get_cookie error: ' + str(e)
        finally:
            self.close_driver(driver)

    def init_db(self):
        while 1:
            try:
                conn = MongoClient('140.143.94.171', 27017)
                self.db = conn.crawler
                self.db.authenticate('mongodbcrawler', 'Shantianci56')
                break
            except:
                self.change_ip()

    def save(self, task_id, info):
        self.safe_save(task_id + '_' + time.strftime("%Y%m%d%H", time.localtime()), info)

    def save1(self, coll_name, info):
        self.safe_save(coll_name, info)

    def safe_save(self, coll_name, info):
        while True:
            try:
                info['timestamp'] = int(round(time.time() * 1000))
                self.db[coll_name].save(info)
                break
            except:
                self.init_db()

    @staticmethod
    def change_ip():
        os.system('D:\\node-changeip\\swip.bat')
        time.sleep(20)

    @staticmethod
    def init_driver():
        cap = webdriver.DesiredCapabilities.PHANTOMJS
        cap["phantomjs.page.settings.userAgent"] = BaseSpider.user_agent
        cap["phantomjs.page.customHeaders.User-Agent"] = BaseSpider.user_agent
        driver = webdriver.PhantomJS(
            executable_path=r"D:\exe\phantomjs.exe",
            desired_capabilities=cap)
        driver.implicitly_wait(30)
        driver.set_page_load_timeout(30)
        driver.set_script_timeout(30)
        return driver

    @staticmethod
    def close_driver(driver):
        if driver:
            driver.close()
            driver.quit()

    @staticmethod
    def soup(response):
        return BeautifulSoup(response.text, 'lxml')

    @staticmethod
    def get_text(tag, index=0):
        if not tag:
            return ''
        else:
            if type(tag) is not list:
                return tag.text
            else:
                if len(tag) > index:
                    return tag[index].text
                else:
                    return ''
