#!/usr/bin/env python
# coding=utf-8
# author: zengyuetian
# 此代码仅供学习与交流，请勿用于商业用途。
# 小区信息的数据结构


class XiaoQu(object):
    def __init__(self, district, area, name,year_built, price, 
    on_sale_erfang,onsale_sanfang,onsale_sifang,
    elementary_schools,url):
        self.district = district
        self.area = area
        self.name = name
        self.year_built = year_built
        self.price = price
        self.on_sale_erfang = on_sale_erfang
        self.onsale_sanfang = onsale_sanfang
        self.onsale_sifang = onsale_sifang
        self.elementary_schools = elementary_schools
        self.url = url

    def text(self):
        return self.district + "," + \
                self.area + "," + \
                self.name + "," + \
                self.year_built + "," + \
                str(self.price) + "," + \
                str(self.on_sale_erfang) + "," + \
                str(self.onsale_sanfang) + "," + \
                str(self.onsale_sifang) + "," + \
                self.elementary_schools + "," + \
                self.url
