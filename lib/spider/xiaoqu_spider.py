#!/usr/bin/env python
# coding=utf-8
# author: zengyuetian
# 此代码仅供学习与交流，请勿用于商业用途。
# 爬取小区数据的爬虫派生类

import codecs
import re
import traceback
from os import replace

import lib.utility.version
import threadpool
from bs4 import BeautifulSoup
from lib.item.ershou import *
from lib.item.xiaoqu import *
from lib.spider.base_spider import *
from lib.utility.date import *
from lib.utility.log import *
from lib.utility.path import *
from lib.zone.area import *
from lib.zone.city import get_city
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class XiaoQuBaseSpider(BaseSpider):
    def collect_area_xiaoqu_data(self, city_name, area_name, fmt="csv"):
        """
        对于每个板块,获得这个板块下所有小区的信息
        并且将这些信息写入文件保存
        :param city_name: 城市
        :param area_name: 板块
        :param fmt: 保存文件格式
        :return: None
        """
        district_name = area_dict.get(area_name, "")
        csv_file = self.today_path + "/{0}_{1}.csv".format(district_name, area_name)
        with open(csv_file, "w") as f:
            # 开始获得需要的板块数据
            xqs = self.get_xiaoqu_info(city_name, area_name)
            # 锁定
            if self.mutex.acquire(1):
                self.total_num += len(xqs)
                # 释放
                self.mutex.release()
            if fmt == "csv":
                # 20220410,罗湖区,百仕达,旭飞华达园,2000,普通住宅,90,540,高楼层,三房,xxxx
                f.write("日期,区,片区,小区,指导价,房屋用途,面积,价格,楼层,户型,建造年份,链接\n")
                for xiaoqu in xqs:
                    for ershou in xiaoqu.ershous:
                        f.write(self.date_string + "," + xiaoqu.text()+"," + ershou.text() + "\n")
        print("Finish crawl area: " + area_name + ", save data to : " + csv_file)
        logger.info("Finish crawl area: " + area_name + ", save data to : " + csv_file)

    @staticmethod
    def get_xiaoqu_info(city, area):
        total_page = 1
        district = area_dict.get(area, "")
        chinese_district = get_chinese_district(district)
        chinese_area = chinese_area_dict.get(area, "")
        xiaoqu_list = list()
        page = 'http://{0}.{1}.com/xiaoqu/{2}/'.format(city, SPIDER_NAME, area)
        print(page)
        logger.info(page)

        headers = create_headers()
        response = requests.get(page, timeout=10, headers=headers)
        html = response.content
        xiaoquSoup = BeautifulSoup(html, "lxml")

        # 获得总的页数
        try:
            page_box = xiaoquSoup.find_all('div', class_='page-box')[0]
            matches = re.search('.*"totalPage":(\d+),.*', str(page_box))
            total_page = int(matches.group(1))
        except Exception as e:
            print("\tWarning: only find one page for {0}".format(area))
            print(e)

        # 从第一页开始,一直遍历到最后一页
        for i in range(1, total_page + 1):
            headers = create_headers()
            page = 'http://{0}.{1}.com/xiaoqu/{2}/pg{3}'.format(city, SPIDER_NAME, area, i)
            print("page url:"+page)  # 打印版块页面地址
            BaseSpider.random_delay()
            response = requests.get(page, timeout=10, headers=headers)
            html = response.content
            soup = BeautifulSoup(html, "lxml")

            # 获得有小区信息的panel
            house_elems = soup.find_all('li', class_="xiaoquListItem")
            for house_elem in house_elems:
                guiding_price = house_elem.find('div', class_="totalPrice")
                name = house_elem.find('div', class_='title')
                on_sale = house_elem.find('div', class_="xiaoquListItemSellCount")
                # 这里的年份只做初步判断，实际小区年份以各套房源内部为准。据分析，基本小区整体年份会比实际年份老2年左右
                year_built = house_elem.find('div', class_="positionInfo")
                # 继续清理数据
                xiaoqu_url = name.find('a',href=True)['href']
                print("xiaoqu url:"+xiaoqu_url)
                name = name.text.replace("\n", "")   
                on_sale = on_sale.text.replace("\n", "").strip()
                on_sale =  "".join(filter(str.isdigit, on_sale)) # 提取数字    
                guiding_price = guiding_price.text.replace("m2", "").strip()
                guiding_price =  "".join(filter(str.isdigit, guiding_price)) # 提取数字      
                year_built = year_built.text.replace("\n", "").strip()
                year_built =  "".join(filter(str.isdigit, year_built))
                used = ""
                ershous = list()
                if year_built>'2000' and on_sale>'0':
                    used,ershous = get_ershou_info(xiaoqu_url)
                # 作为对象保存
                xiaoqu = XiaoQu(chinese_district, chinese_area, name,guiding_price,used,ershous)
                xiaoqu_list.append(xiaoqu)
        return xiaoqu_list

    def start(self):
        city = get_city()
        self.today_path = create_date_path("{0}/xiaoqu".format(SPIDER_NAME), city, self.date_string)
        t1 = time.time()  # 开始计时

        # 获得城市有多少区列表, district: 区县
        districts = get_districts(city)
        print('City: {0}'.format(city))
        print('Districts: {0}'.format(districts))

        # 获得每个区的板块, area: 板块
        areas = list()
        for district in districts:
            if district != "nanshanqu" and district != "baoanqu":
               continue
            areas_of_district = get_areas(city, district)
            print('{0}: Area list:  {1}'.format(district, areas_of_district))
            # 用list的extend方法,L1.extend(L2)，该方法将参数L2的全部元素添加到L1的尾部
            areas.extend(areas_of_district)
            # 使用一个字典来存储区县和板块的对应关系, 例如{'beicai': 'pudongxinqu', }
            for area in areas_of_district:
                area_dict[area] = district
        print("Area:", areas)
        print("District and areas:", area_dict)

        # 准备线程池用到的参数
        nones = [None for i in range(len(areas))]
        city_list = [city for i in range(len(areas))]
        args = zip(zip(city_list, areas), nones)
        # areas = areas[0: 1]

        # 针对每个板块写一个文件,启动一个线程来操作
        pool_size = thread_pool_size
        pool = threadpool.ThreadPool(pool_size)
        my_requests = threadpool.makeRequests(self.collect_area_xiaoqu_data, args)
        [pool.putRequest(req) for req in my_requests]
        pool.wait()
        pool.dismissWorkers(pool_size, do_join=True)  # 完成后退出

        # 计时结束，统计结果
        t2 = time.time()
        print("Total crawl {0} areas.".format(len(areas)))
        print("Total cost {0} second to crawl {1} data items.".format(t2 - t1, self.total_num))


def get_ershou_info(xiaoqu_url):
    used = ""
    ershous = []
    for retry in range(3): 
        try: 
            response = requests.get(xiaoqu_url, timeout=10, headers=create_headers())
            html = response.content
            soup = BeautifulSoup(html, "lxml")
            ershou_element = soup.find('div', class_="goodSellHeader clear")
            # 如果取不到二手房详情URL，说明当前小区没有二手房出售
            if ershou_element is None:
                print(xiaoqu_url + " : 暂无房源")
                return used,ershous
            ershou_url = ershou_element.find('a',href=True)['href']
            start_price,end_price = 600,900
            step = 10
            allErsohus = get_ershou_with_price(ershou_url,start_price,end_price)
            if len(allErsohus) == 0:
                return used,ershous
            while start_price<end_price:
                stepErshous =  get_ershou_with_price(ershou_url,start_price,start_price+step)
                ershous = ershous + stepErshous
                start_price = start_price + step
            for ershou in ershous:
                print(ershou.text())
            used = get_house_used(ershous[0].url)
            break
        except Exception as e:
            traceback.print_exc()
            print(xiaoqu_url+' :'+str(e))
            time.sleep(retry)
    return used,ershous

def get_ershou_with_price(ershou_url,price_floor,price_ceiling):
    ershous = list()
    for retry in range(3): 
        try: 
            price_url = ("/ershoufang/l3l4bp%dep%dc") % ( price_floor , price_ceiling)
            #print(price_url)
            ershou_url = ershou_url.replace("/ershoufang/c",price_url)
            #print("ershou url:"+ershou_url)
            response = requests.get(ershou_url, timeout=10, headers=create_headers())
            time.sleep(1)
            html = response.content
            soup = BeautifulSoup(html, "lxml")
            noresult = soup.find_all("div",class_="m-noresult space-lite")
            if len(noresult) >0:
                return ershous
            sell_element = soup.find('ul',class_='sellListContent')
            if sell_element is None:
                print(ershou_url+" :"+" selling list is None")
                return ershous
            house_elements = sell_element.find_all('li',class_='clear')
            for house_element in house_elements:
                house_url = house_element.find('a',class_='img VIEWDATA CLICKDATA maidian-detail',href=True)['href']
                house_info = house_element.find('div',class_='houseInfo')
                house_info_text = str(house_info.text).replace(" ","").replace("\n","").replace("\r","")
                print("house url:"+house_url+" house info:",house_info_text)
                strs = house_info_text.split("|")
                floor = 0
                year_built = 0
                rooms = 0
                size = 0
                if len(strs) == 4:
                    # 高楼层(共56层) | 3室2厅 | 87.36平米 | 东北
                    floor = strs[0]
                    year_built =  "2015年建"
                    rooms = strs[1]
                    size = float(strs[2].replace("平米",""))
                elif len(strs) == 5:
                #  低楼层 (共34层)| 2000年建 | 3室2厅 | 101平米 | 南   
                    floor = strs[0]
                    year_built =  strs[1].replace("年建","")
                    #print("house url:"+house_url+" year built:",year_built)
                    rooms = strs[2]
                    size = float(strs[3].replace("平米",""))     
                else:
                    continue
                ershous.append(ErShou(size,floor,(price_floor+price_ceiling)/2,rooms,year_built,house_url))
            break
        except Exception as e:
            traceback.print_exc()
            print(ershou_url+' :'+str(e))
            time.sleep(retry)
    return ershous

def get_house_used(house_url):
    for i in range(3):
        try:
            response = requests.get(house_url, timeout=10, headers=create_headers())
            html = response.content
            soup = BeautifulSoup(html, "lxml")
            # 获得有小区信息的panel
            label_elements = soup.find('div', class_="transaction").find('div', class_="content").find_all('li')
            for label_element in label_elements:
                if label_element.text.find("房屋用途") >=0:
                    return label_element.text.replace("房屋用途", "").strip()
        except Exception as e:
            traceback.print_exc()
            print(house_url+' :'+str(e))
            time.sleep(i)
    return ""

if __name__ == "__main__":
    # urls = get_xiaoqu_area_urls()
    # print urls
    # get_xiaoqu_info("sh", "beicai")
    spider = XiaoQuBaseSpider("lianjia")
    spider.start()
