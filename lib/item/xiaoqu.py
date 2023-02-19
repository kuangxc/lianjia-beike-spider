#!/usr/bin/env python
# coding=utf-8
# author: zengyuetian
# 此代码仅供学习与交流，请勿用于商业用途。
# 小区信息的数据结构


class XiaoQu(object):
    def __init__(self, district, area, name,guiding_price, used, ershous):
        self.district = district
        self.area = area
        self.name = name
        self.guiding_price = guiding_price
        self.used = used
        self.ershous = ershous
    def text(self):
        return self.district + "," + \
                self.area + "," + \
                self.name + "," + \
                self.guiding_price + "," + \
                str(self.used)
