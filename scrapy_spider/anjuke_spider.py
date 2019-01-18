#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy


class AnjukeSpider(scrapy.Spider):
    from pymongo import MongoClient
    conn = MongoClient('140.143.94.171', 27017)
    db = conn.crawler
    db.authenticate('mongodbcrawler', 'Shantianci56')
    table_anjuke = db['t_anjuke_1']

    name = "anjuke"
    user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36"
    start_urls = [
        'https://www.anjuke.com/sy-city.html',
    ]
    download_delay = 20

    url_list = ['https://putian.anjuke.com',
                'https://puyang.anjuke.com',
                'https://pingxiang.anjuke.com',
                'https://panjin.anjuke.com',
                'https://pingdingsha.anjuke.com',
                'https://panzhihua.anjuke.com',
                'https://nangong.anjuke.com',
                'https://nehe.anjuke.com',
                'https://nanxiong.anjuke.com',
                'https://nankang.anjuke.com',
                'https://ningguo.anjuke.com',
                'https://ninganshi.anjuke.com',
                'https://nujiang.anjuke.com',
                'https://naqu.anjuke.com',
                'https://nanping.anjuke.com',
                'https://neijiang.anjuke.com',
                'https://ningde.anjuke.com',
                'https://nanyang.anjuke.com',
                'https://nanchong.anjuke.com',
                'https://nantong.anjuke.com',
                'https://nanning.anjuke.com',
                'https://nc.anjuke.com',
                'https://nb.anjuke.com',
                'https://nanjing.anjuke.com',
                'https://miluo.anjuke.com',
                'https://mingguang.anjuke.com',
                'https://mianzhu.anjuke.com',
                'https://macheng.anjuke.com',
                'https://mengzhou.anjuke.com',
                'https://manzhouli.anjuke.com',
                'https://meihekou.anjuke.com',
                'https://mishan.anjuke.com',
                'https://minggang.anjuke.com',
                'https://meizhou.anjuke.com',
                'https://meishan.anjuke.com',
                'https://mudanjiang.anjuke.com',
                'https://maanshan.anjuke.com',
                'https://mianyang.anjuke.com',
                'https://laixi.anjuke.com',
                'https://laohekou.anjuke.com',
                'https://liuyang.anjuke.com',
                'https://maoming.anjuke.com',
                'https://laizhoushi.anjuke.com',
                'https://laoling.anjuke.com',
                'https://leping.anjuke.com',
                'https://longquan.anjuke.com',
                'https://linxiang.anjuke.com',
                'https://luoding.anjuke.com',
                'https://lianzhou.anjuke.com',
                'https://lufengshi.anjuke.com',
                'https://leizhou.anjuke.com',
                'https://lianjiangshi.anjuke.com',
                'https://lechang.anjuke.com',
                'https://lanxi.anjuke.com',
                'https://luxishi.anjuke.com',
                'https://langzhong.anjuke.com',
                'https://lianyuan.anjuke.com',
                'https://lengshuijiang.anjuke.com',
                'https://lichuan.anjuke.com',
                'https://lucheng.anjuke.com',
                'https://lingbao.anjuke.com',
                'https://linzhoushi.anjuke.com',
                'https://lingyuan.anjuke.com',
                'https://linjiang.anjuke.com',
                'https://longjing.anjuke.com',
                'https://liyang.anjuke.com',
                'https://leiyang.anjuke.com',
                'https://laiyang.anjuke.com',
                'https://longkou.anjuke.com',
                'https://lvliang.anjuke.com',
                'https://longnan.anjuke.com',
                'https://linzhi.anjuke.com',
                'https://linyishi.anjuke.com',
                'https://linxia.anjuke.com',
                'https://lingcang.anjuke.com',
                'https://laibin.anjuke.com',
                'https://liaoyuan.anjuke.com',
                'https://liupanshui.anjuke.com',
                'https://liangshan.anjuke.com',
                'https://luohe.anjuke.com',
                'https://longyan.anjuke.com',
                'https://linfen.anjuke.com',
                'https://lasa.anjuke.com',
                'https://liaoyang.anjuke.com',
                'https://leshan.anjuke.com',
                'https://loudi.anjuke.com',
                'https://lishui.anjuke.com',
                'https://lianyungang.anjuke.com',
                'https://liaocheng.anjuke.com',
                'https://linyi.anjuke.com',
                'https://lijiang.anjuke.com',
                'https://luzhou.anjuke.com',
                'https://luan.anjuke.com',
                'https://laiwu.anjuke.com',
                'https://liuzhou.anjuke.com',
                'https://luoyang.anjuke.com',
                'https://langfang.anjuke.com',
                'https://lanzhou.anjuke.com',
                'https://kaiyuan2.anjuke.com',
                'https://kaiyuan.anjuke.com',
                'https://lezilesu.anjuke.com',
                'https://kenli.anjuke.com',
                'https://kelamayi.anjuke.com',
                'https://kashi.anjuke.com',
                'https://kaifeng.anjuke.com',
                'https://ks.anjuke.com']

    def parse(self, response):
        headers = {'referer': self.start_urls[0]}
        for a in response.css('div.city_list>a'):
            item = {}
            item['name'] = a.xpath('text()').extract_first()
            item['link'] = a.xpath('@href').extract_first()
            if (item['link'] in self.url_list) and len(self.table_anjuke.find_one({'link': item['link']})['zu']) == 0:
                yield response.follow(item['link'], self.parseNav, meta={'item': item}, headers=headers)

    def parseNav(self, response):
        item = response.meta['item']
        nav = {}
        for a in response.css('.a_navnew'):
            nav[a.xpath('text()').extract_first()] = a.xpath('@href').extract_first()
        item['nav'] = nav

        # 二手房
        sale = []
        for a in response.xpath("//div[@id='content_Rd1']/div/div[1]/div[1]/a"):
            sale.append({'region': a.xpath('text()').extract_first(), 'link': a.xpath('@href').extract_first()})

        # 租房区域
        zu = []
        for a in response.css('#content_Rd3 .hot-areas a'):
            zu.append({'region': a.xpath('text()').extract_first(), 'link': a.xpath('@href').extract_first()})

        item['sales'] = sale
        item['zu'] = zu
        self.table_anjuke.save(item)
