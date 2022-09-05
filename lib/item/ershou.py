#!/usr/bin/env python
# coding=utf-8
# author: zengyuetian
# 此代码仅供学习与交流，请勿用于商业用途。
# 二手房信息的数据结构


class ErShou(object):
    def __init__(self, size, floor, price,rooms, url):
        self.size = size
        self.price = price
        self.floor = floor
        self.rooms = rooms
        self.url = url

    def text(self):
        return str(self.size) + "," + \
                str(self.price) + "," + \
                self.floor + "," + \
                str(self.rooms) + "," + \
                self.url
