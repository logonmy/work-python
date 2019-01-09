#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import time, random


class Crack():
    def __init__(self, url):
        self.url = url
        self.browser = webdriver.Chrome(r'E:\work\exe\chromedriver.exe')
        # self.browser = webdriver.PhantomJS(r'E:\java\trunk\src\YayCrawler-work\exec\phantomjs\window\phantomjs.exe')
        self.wait = WebDriverWait(self.browser, 100)

    def open(self):
        """
        打开浏览器,并输入查询内容
        """
        self.browser.get(self.url)

    def close(self):
        """
        关闭浏览器
        :return:
        """
        if self.browser:
            self.browser.quit()

    """
    // 这段JS可以捕获鼠标移动的轨迹
    var track = [];
    var x, y;
    document.getElementById('yodaBox').addEventListener('mousedown', function(){
        console.log("start listen...")
        track = []
        odiv = document.getElementById('yodaBox')
        odiv.onmousemove = function(ev)
        {
            var oEvent=ev||event;
            let cx = oEvent.clientX;
            let cy = oEvent.clientY;
            if (x === undefined) {
                x = cx;
                y = cy;
            } else {
                track.push({'x': cx - x, 'y':cy - y});
                x = cx;
                y = cy;
            }
        }
        odiv.onmouseup = function(ev) {
            var s = "";
            track.forEach(function(x) {s += "(" + x['x'] + "," + x['y'] + "),"});
            console.log(s);
            window.localStorage['track'] = s;
        }
    })
    var s = ""
    track.forEach(function(x) {s += "(" + x['x'] + "," + x['y'] + "),"})
    """

    def get_track(self, distance):
        """
        根据偏移量获取移动轨迹
        :param distance: 偏移量
        :return: 移动轨迹
        """
        # 移动轨迹
        # track = []
        # # 当前位移
        # current = 0
        # # 减速阈值
        # mid = distance * 4 / 5
        # # 计算间隔
        # t = 0.2
        # # 初速度
        # v = 0
        #
        # while current < distance:
        #     if current < mid:
        #         # 加速度为正2
        #         a = 2
        #     # elif current < mid * 0.9:
        #     #     # 加速度为负3
        #     #     a = -5
        #     else:
        #         a = -5
        #     # 初速度v0
        #     v0 = v
        #     # 当前速度v = v0 + at
        #     v = v0 + a * t
        #     # 移动距离x = v0t + 1/2 * a * t^2
        #     move = v0 * t + 0.5 * a * t * t
        #     if move <= 0:
        #         move = 1
        #     # 当前位移
        #     current += move
        #     # 加入轨迹
        #     track.append(round(move))

        track = [(2, 0), (1, 0), (1, 0), (2, 0), (1, 0), (1, 0), (2, 0), (1, 0), (1, 0), (1, 0), (2, 0), (1, 0), (1, 0),
                 (2, 0), (1, 0), (1, 0), (2, 0), (1, 0), (1, 0), (2, 0), (1, 0), (1, 0), (1, 0), (2, 0), (1, 0), (1, 0),
                 (2, 0), (1, 0), (1, 0), (1, 0), (6, 0), (1, 0), (3, 0), (1, 0), (2, 0), (3, 0), (1, 0), (1, 0), (3, 0),
                 (2, 0), (3, 0), (1, 0), (1, 0), (2, 0), (2, 0), (2, 0), (1, 0), (1, 0), (2, 0), (1, 0), (1, 0), (2, 0),
                 (3, 0), (1, 0), (3, 0), (3, 0), (3, 0), (3, 0), (3, 0), (3, 0), (3, 0), (3, 0), (2, 0), (3, 0), (1, 0),
                 (1, 0), (3, 0), (2, 0), (1, 0), (1, 0), (2, 0), (1, 0), (1, 0), (2, 0), (1, 0), (1, 0), (2, 0), (1, 0),
                 (1, 0), (3, 0), (3, 0), (2, 0), (1, 0), (1, 0), (2, 0), (1, 0), (1, 0), (1, 0), (2, 0), (1, 0), (1, 0),
                 (2, 0), (1, 0), (2, 0), (1, 0), (1, 0), (1, 0), (2, 0), (1, 0), (1, 0), (1, 0), (2, 0), (1, 0), (1, 0),
                 (2, 0), (1, 0), (1, 0), (1, 0), (2, 0), (1, 0), (2, 2), (1, 0), (1, 0), (1, 0), (2, 1), (1, 0), (1, 0),
                 (2, 0), (0, 1), (2, 0), (1, 0), (1, 0), (1, 0), (1, 0), (1, 0)]
        track = [
            (3, 1), (1, 0), (1, 0), (2, 0), (1, 0), (1, 0), (2, 0), (1, 0), (1, 0), (1, 0), (4, 0), (3, 0), (3, 1),
            (1, 0), (1, 0), (6, 0), (1, 0), (3, 0), (1, 0), (2, 0), (1, 0), (1, 0), (3, 0), (7, 0), (9, 0), (6, 0),
            (5, 0), (6, 0), (3, 0), (2, 0), (2, 0), (2, 0), (1, 0), (1, 0), (2, 0), (1, 0), (1, 0), (1, 0), (2, 0),
            (1, 0), (1, 0), (3, 0), (2, 0), (1, 0), (1, 0), (2, 0), (1, 0), (1, 0), (3, 0), (2, 0), (1, 0), (1, 0),
            (2, 0), (1, 0), (1, 0), (2, 0), (1, 0), (1, 0), (2, 0), (1, 0), (1, 0), (4, 0), (3, 2), (1, 0), (1, 0),
            (1, 0), (2, 0), (1, 0), (1, 0), (2, 0), (1, 0), (1, 0), (2, 0), (1, 0), (1, 0), (2, 0), (1, 0), (1, 0),
            (1, 0), (2, 0), (1, 0), (1, 0), (2, 0), (1, 0), (1, 0), (2, 0), (1, 0), (1, 0), (2, 0), (1, 0), (1, 0),
            (2, 0), (2, 1), (2, 1), (1, 2), (2, 1), (1, 0), (1, 2), (2, 0), (2, 1), (2, 0), (1, 0), (1, 0), (2, 0),
            (1, 0), (1, 2), (2, 0), (1, 0), (1, 0), (2, 0), (1, 0), (0, 0)
        ]
        return track

    def get_slider(self):
        """
        获取滑块
        :return: 滑块对象
        """
        while True:
            try:
                slider = self.browser.find_element_by_xpath("//div[@id='yodaBox']")
                break
            except:
                time.sleep(0.5)
        return slider

    def move_to_gap(self, slider, track):
        """
        拖动滑块到缺口处
        :param slider: 滑块
        :param track: 轨迹
        :return:
        """
        ac = ActionChains(self.browser)
        ac.click_and_hold(slider)
        i = 0
        for (x, y) in track:
            i += 1
            ac.move_by_offset(xoffset=x, yoffset=y)
            if i > len(track) - 2:
                ac.pause(0.1)
            else:
                ac.pause(random.randint(1, 10) * 1.0 / 1000)
        ac.pause(1)
        ac.release().perform()

    def crack(self):
        # 打开浏览器
        self.open()

        track = self.get_track(200)
        print('滑动滑块')
        print(track)
        time.sleep(5)
        # 获取滑块
        slider = self.get_slider()
        # 拖动滑块到缺口处
        self.move_to_gap(slider, track)
        # 关闭浏览器
        self.close()


if __name__ == '__main__':
    print "开始验证"
    url = "https://verify.meituan.com/v2/web/general_page?action=spiderindefence&requestCode=2a47bf67e3ee41718cab80d94bc86514&platform=1000&adaptor=auto&succCallbackUrl=https%3A%2F%2Foptimus-mtsi.meituan.com%2Foptimus%2FverifyResult%3ForiginUrl%3Dhttp%253A%252F%252Fwww.dianping.com%252Fshop%252F27415905&theme=dianping"
    crack = Crack(url)
    crack.crack()
