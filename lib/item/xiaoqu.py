#!/usr/bin/env python
# coding=utf-8
# author: zengyuetian
# 此代码仅供学习与交流，请勿用于商业用途。
# 小区信息的数据结构


class XiaoQu(object):
    def __init__(self, district, area, name,year_built, price, on_sale,url):
        self.district = district
        self.area = area
        self.year_built = year_built
        self.price = price
        self.name = name
        self.on_sale = on_sale
     #   self.elementary_schools = elementary_schools
      #  self.middle_schools = middle_schools
        self.url = url

    def text(self):
        return self.district + "," + \
                self.area + "," + \
                self.name + "," + \
                self.year_built + "," + \
                self.price + "," + \
                self.on_sale + "," + \
                self.url
