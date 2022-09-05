#!/usr/bin/env python
# coding=utf-8
# author: zengyuetian
# 此代码仅供学习与交流，请勿用于商业用途。
# 小区信息的数据结构


class XiaoQu(object):
    def __init__(self, district, area, name,year_built,guiding_price, used, ershous):
        self.district = district
        self.area = area
        self.name = name
        self.year_built = year_built
        self.guiding_price = guiding_price
        self.used = used
        self.ershous = ershous
    def text(self):
        return self.district + "," + \
                self.area + "," + \
                self.name + "," + \
                self.year_built + "," + \
                self.guiding_price + "," + \
                str(self.used)
