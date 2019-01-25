#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from pymongo import MongoClient
import time, os, re, random
from datetime import datetime
from dateutil.relativedelta import relativedelta
import traceback
import zlib

font_url_pattern = re.compile('https://static.tianyancha.com/fonts-styles/css/(\w+/?\w+)/font.css')


def now_time():
    return int(round(time.time() * 1000))


def parse_other(soup, info):
    info['companyName'] = get_text(soup.select_one('h1.name'))
    divs = soup.select('div.detail > div')
    if soup.select_one('.address'):
        info['address'] = get_attr(soup.select_one('.address'), 'title')
    else:
        info['address'] = get_text(divs[1].select('div'), 1)
    if soup.select_one('.company-link'):
        info['companyLink'] = get_attr(soup.select_one('.company-link'), 'href')
    else:
        info['companyLink'] = get_text(divs[1].select('div span'), 1)
    if soup.select_one('#company_base_info_detail'):
        info['companyDetail'] = get_text(soup.select_one('#company_base_info_detail'))
    else:
        info['companyDetail'] = get_text(divs[2].select('span'), 1)


def parse_detail_1(soup, info):
    info['FAREN'] = get_text(soup.select_one('div.name > a'))
    tbodys = soup.select("#_container_baseInfo > table > tbody")
    trs = tbodys[0].select('tr')
    info['ZuZhiZiBen'] = get_attr(trs[0].select('td')[1].select_one('div[title]'), 'title')
    info['ZuZhiShiJian'] = get_text(trs[1].select_one('td').select('div[title] text'))
    info['GongSiZhuangTai'] = get_text(trs[2].select_one('td').select('div')[1])
    tbody = tbodys[1]
    trs = tbody.select('tr')
    tds = trs[0].select('td')
    info['GongShangZhuCeHao'] = get_text(tds[1])
    info['ZuZhiJiGouDaiMa'] = get_text(tds[3])
    info['PingFen'] = get_attr(tds[4].select_one('img'), 'alt')
    tds = trs[1].select('td')
    info['TongYiXinYongDaiMa'] = get_text(tds[1])
    info['GongSiLeiXing'] = get_text(tds[3])
    tds = trs[2].select('td')
    info['NaShuiRenShiBieHao'] = get_text(tds[1])
    info['HangYe'] = get_text(tds[3])
    tds = trs[3].select('td')
    info['YingYeQiXian'] = get_text(tds[1].select_one('span'))
    info['HeZhunRiQi'] = get_text(tds[3].select_one('text'))
    tds = trs[4].select('td')
    info['NaShuiRenZiZhi'] = get_text(tds[1])
    info['RenYuanGuiMo'] = get_text(tds[3])
    tds = trs[5].select('td')
    info['ShiJiaoZiBen'] = get_text(tds[1])
    info['DengJiJiGuan'] = get_text(tds[3])
    tds = trs[6].select('td')
    info['CanBaoRenShu'] = get_text(tds[1])
    info['YingWenMingChen'] = get_text(tds[3])
    tds = trs[7].select('td')
    info['ZhuCeDiZhi'] = get_text(tds[1])
    tds = trs[8].select('td')
    info['JingYingFanWei'] = get_text(tds[1].select_one('text'))
    parse_other(soup, info)


def parse_detail_2(soup, info):
    tbodys = soup.select("#_container_baseInfo > table > tbody")
    tr = tbodys[0].select_one('tr')
    tds = tr.select('td')
    if len(tds) > 3:
        info['FAREN'] = get_text(tds[0].select_one('span'))
        info['ZuZhiZiBen'] = get_text(tds[1].select_one('div'))
        info['ZuZhiShiJian'] = get_text(tds[2].select_one('div'))
        info['GongSiZhuangTai'] = get_text(tds[3].select_one('div > div'))
    else:
        info['ZuZhiZiBen'] = get_text(tds[1].select_one('div'))
        info['ZuZhiShiJian'] = get_text(tds[2].select_one('div'))
        info['GongSiZhuangTai'] = get_text(tds[3].select_one('div > div'))
    tbody = tbodys[1]
    trs = tbody.select('tr')
    tds = trs[0].select('td')
    info['GongSiLeiXing'] = get_text(tds[1].select_one('span'))
    info['TongYiXinYongDaiMa'] = get_text(tds[3].select_one('span'))
    tds = trs[1].select('td')
    info['DengJiJiGuan'] = get_text(tds[1])
    info['YeWuZhuGuanDanWei'] = get_text(tds[3])
    tds = trs[2].select('td')
    info['GongShangZhuCeHao'] = get_text(tds[1])
    info['YeWuLeiXing'] = get_text(tds[3])
    parse_other(soup, info)


def parse_detail_sydw(soup, info):
    tbodys = soup.select("#_container_baseInfo > table > tbody")
    tr = tbodys[0].select_one('tr')
    tds = tr.select('td')
    info['FAREN'] = get_text(tds[0].select_one('span'))
    info['ZuZhiZiBen'] = get_text(tds[1].select_one('div'))
    info['YingYeQiXian'] = get_text(tds[2].select_one('div'))
    info['GongSiZhuangTai'] = get_text(tds[3].select_one('div > div'))
    tbody = tbodys[1]
    trs = tbody.select('tr')
    tds = trs[0].select('td')
    info['TongYiXinYongDaiMa'] = get_text(tds[3].select_one('span'))
    tds = trs[1].select('td')
    info['DengJiJiGuan'] = get_text(tds[1])
    tds = trs[3].select('td')
    info['JingYingFanWei'] = get_text(tds[1])
    parse_other(soup, info)


def parse_detail_tw(soup, info):
    trs = soup.select("#_container_baseInfo > table > tbody > tr")
    tds = trs[0].select('td')
    info['GongShangZhuCeHao'] = get_text(tds[1].select_one('span'))
    info['GongSiZhuangTai'] = get_text(tds[3].select_one('span'))
    tds = trs[1].select('td')
    info['companyName'] = get_text(tds[1].select_one('span'))
    info['ZuZhiZiBen'] = get_text(tds[3].select_one('span'))
    tds = trs[2].select('td')
    info['ShiJiaoZiBen'] = get_text(tds[1].select_one('span'))
    info['FAREN'] = get_text(tds[3].select_one('span'))
    tds = trs[3].select('td')
    info['ZhuCeDiZhi'] = get_text(tds[1].select_one('span'))
    info['DengJiJiGuan'] = get_text(tds[3].select_one('span'))
    tds = trs[4].select('td')
    info['ZuZhiShiJian'] = get_text(tds[1].select_one('span'))
    info['HeZhunRiQi'] = get_text(tds[3].select_one('span'))
    tds = trs[5].select('td')
    info['JingYingFanWei'] = get_text(tds[1].select_one('span'))
    parse_other(soup, info)


def parse_detail_hk(soup, info):
    trs = soup.select("#_container_baseInfo > table > tbody > tr")
    tds = trs[0].select('td')
    info['GongShangZhuCeHao'] = get_text(tds[1].select_one('span'))
    info['GongSiLeiXing'] = get_text(tds[3].select_one('span'))
    tds = trs[1].select('td')
    info['ZuZhiShiJian'] = get_text(tds[1].select_one('span'))
    info['GongSiZhuangTai'] = get_text(tds[3].select_one('span'))
    tds = trs[3].select('td')
    info['YingWenMingChen'] = get_text(tds[1].select_one('span'))
    tds = trs[5].select('td')
    info['JingYingFanWei'] = get_text(tds[1].select_one('span'))
    parse_other(soup, info)


def parse_detail_jj(soup, info):
    trs = soup.select("#_container_baseInfo > table > tbody > tr")
    tds = trs[1].select('td')
    info['YingWenMingChen'] = get_text(tds[1])
    tds = trs[2].select('td')
    info['ZuZhiShiJian'] = get_text(tds[1])
    info['ZuZhiZiBen'] = get_text(tds[3])
    tds = trs[3].select('td')
    info['TongYiXinYongDaiMa'] = get_text(tds[1])
    info['FaRen'] = get_text(tds[3])
    tds = trs[4].select('td')
    info['ZuZhiJiGouDaiMa'] = get_text(tds[1])
    tds = trs[11].select('td')
    info['DengJiJiGuan'] = get_text(tds[1])
    tds = trs[12].select('td')
    info['YeWuZhuGuanDanWei'] = get_text(tds[1])
    tds = trs[16].select('td')
    info['JingYingFanWei'] = get_text(tds[1])
    parse_other(soup, info)


def parse_detail_shzz(soup, info):
    tbodys = soup.select("#_container_baseInfo > table > tbody")
    tds = tbodys[0].select('tr > td')
    info['FAREN'] = get_text(tds[0].select_one('span'))
    info['ZuZhiZiBen'] = get_attr(tds[1].select_one('div[title]'), 'title')
    info['ZuZhiShiJian'] = get_attr(tds[2].select_one('div[title]'), 'title')
    info['GongSiZhuangTai'] = get_attr(tds[3].select_one('div[title]'), 'title')
    tbody = tbodys[1]
    trs = tbody.select('tr')
    tds = trs[0].select('td')
    info['GongSiLeiXing'] = get_text(tds[1].select_one('span'))
    info['TongYiXinYongDaiMa'] = get_text(tds[3].select_one('span'))
    tds = trs[1].select('td')
    info['DengJiJiGuan'] = get_text(tds[1])
    info['YeWuZhuGuanDanWei'] = get_text(tds[3])
    tds = trs[2].select('td')
    info['GongShangZhuCeHao'] = get_text(tds[1])
    info['YeWuLeiXing'] = get_text(tds[3])
    parse_other(soup, info)


def parse_detail_ls(soup, info):
    tbodys = soup.select("#_container_baseInfo > table > tbody")
    tds = tbodys[0].select('tr > td')
    info['FAREN'] = get_text(tds[0].select_one('span'))
    info['ZuZhiZiBen'] = get_attr(tds[1].select_one('div[title]'), 'title')
    info['ZuZhiShiJian'] = get_attr(tds[2].select_one('div[title]'), 'title')
    info['GongSiZhuangTai'] = get_attr(tds[3].select_one('div[title]'), 'title')
    tbody = tbodys[1]
    trs = tbody.select('tr')
    tds = trs[0].select('td')
    info['GongShangZhuCeHao'] = get_text(tds[1].select_one('span'))
    info['ZuZhiJiGouDaiMa'] = get_text(tds[3].select_one('span'))
    tds = trs[1].select('td')
    info['TongYiXinYongDaiMa'] = get_text(tds[1])
    tds = trs[2].select('td')
    info['NaShuiRenShiBieHao'] = get_text(tds[1])
    tds = trs[3].select('td')
    info['YingYeQiXian'] = get_text(tds[3])
    tds = trs[4].select('td')
    info['YeWuZhuGuanDanWei'] = get_text(tds[3])
    tds = trs[5].select('td')
    info['HeZhunRiQi'] = get_text(tds[1])
    parse_other(soup, info)


def parse_detail(url, soup, save_table):
    try:
        save_item = {'pageUrl': url, 'timestamp': now_time()}
        entityType = get_text(soup.select_one('span.tag-new-category'))
        info = dict({'entityType': entityType})
        if entityType == u'事业单位':
            parse_detail_sydw(soup, info)
        elif entityType == u'基金会':
            parse_detail_jj(soup, info)
        elif entityType == u'台湾企业':
            parse_detail_tw(soup, info)
        elif entityType == u'香港企业':
            parse_detail_hk(soup, info)
        elif entityType == u'社会组织':
            parse_detail_shzz(soup, info)
        elif entityType == u'律所':
            parse_detail_ls(soup, info)
        else:
            tbodys = soup.select('#_container_baseInfo > table > tbody')
            tbody_len = len(tbodys) if tbodys else 0
            if tbody_len == 0:
                log(url)
                return
            elif tbody_len == 2:
                if soup.select_one('td[tyc-event-ch="CompangyDetail.faren"]'):
                    parse_detail_1(soup, info)
                else:
                    parse_detail_2(soup, info)
            else:
                print '%s no parser' % url
                log(url)
                return
        save_item['result'] = info
        save_item['fontUrl'] = get_by_index(
            re.findall(font_url_pattern, ''.join([t.attrs['href'] for t in soup.select('link')])), 0)
        db[save_table + time.strftime("%Y%m%d%H", time.localtime())].save(save_item)
        if db[font_url_table].count({'fontUrl': save_item['fontUrl']}) == 0:
            db[font_url_table].save({'fontUrl': save_item['fontUrl']})
    except Exception, e:
        log(url)
        traceback.print_exc()


def get_by_index(l, i):
    if type(l) is list and len(l) > i:
        return l[i]
    else:
        return None


def get_text(tag, index=0):
    if not tag:
        return None
    else:
        if type(tag) is not list:
            t = tag
        else:
            if len(tag) > index:
                t = tag[index]
            else:
                return str(tag)
        if 'class' in t.attrs and 'tyc-num' in t.attrs['class']:
            return 'tyc-num>' + t.text
        else:
            return t.text


def get_attr(tag, attr):
    return tag.attrs[attr] if tag and attr in tag.attrs else None


def get_db():
    # db = MongoClient('140.143.94.171', 27017).crawler
    # db.authenticate('mongodbcrawler', 'Shantianci56')

    db = MongoClient('10.82.244.18', 27018).crawler
    db.authenticate('spider', 'spider')
    return db


log_file = open('tianyancha_parse.log', 'a')


def log(msg):
    timestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print timestr + ": " + str(msg)
    log_file.write(str(msg) + "\n")
    log_file.flush()


def main():
    cnt = db[table].count()
    print 'table【%s】 count %d ' % (table, cnt)
    batch = 50
    skip = 0
    while skip < cnt:
        print '%s parse 【%s】 from %d to %d . ' % (
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), table, skip, skip + batch)
        for row in db[table].find({}).sort('_id').skip(skip).limit(batch):
            parse_detail(row['pageUrl'], BeautifulSoup(zlib.decompress(row['source']), 'lxml'), save_table)
        skip += batch
    db[table].drop()


def error_process():
    with open(r'E:\work\data\tyc\detail\error.txt') as f:
        for row in f.readlines():
            row = row.strip()
            cursor = db[table].find({'pageUrl': row}).limit(1)
            try:
                result = next(cursor)
            except:
                continue
            if result:
                parse_detail(row, BeautifulSoup(result['source'], 'lxml'), save_table)


def test():
    with open('detail.html') as f:
        soup = BeautifulSoup(f.read(), 'lxml')
        print soup.select_one('text')


def find(table, query):
    print 'find from table %s ' % table
    return db[table].count(query) > 0


if __name__ == '__main__':
    db = get_db()
    font_url_table = 'tianyancha_font_url'
    begin = datetime(2018, 10, 30, 00)
    save_table = 'task_1632_level1_'
    while True:
        # table = 'tianyancha_wuhan_detail_%s' % begin.strftime('%Y%m%d-%H')
        table = 'task_1632_level1_%s' % begin.strftime('%Y%m%d%H')
        # main()
        if find(table, {'pageUrl': 'https://www.tianyancha.com/company/3098074899'}):
            print table
        begin += relativedelta(hours=1)
        if begin + relativedelta(hours=1) > datetime.now():
            time.sleep(3600)
