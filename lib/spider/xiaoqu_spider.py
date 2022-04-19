#!/usr/bin/env python
# coding=utf-8
# author: zengyuetian
# 此代码仅供学习与交流，请勿用于商业用途。
# 爬取小区数据的爬虫派生类

import codecs
import re
import traceback

import lib.utility.version
import threadpool
from bs4 import BeautifulSoup
from lib.item.xiaoqu import *
from lib.spider.base_spider import *
from lib.utility.date import *
from lib.utility.log import *
from lib.utility.path import *
from lib.zone.area import *
from lib.zone.city import get_city
from selenium import webdriver
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
                # 20220410,罗湖区,百仕达,旭飞华达园,2000,50400,普通住宅,1,2,3,南头小学,xxxx
                f.write("日期,区,片区,小区,建造年份,单价,房屋用途,二房,三房,四房,小学,链接\n")
                for xiaoqu in xqs:
                    f.write(self.date_string + "," + xiaoqu.text() + "\n")
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
                price = house_elem.find('div', class_="totalPrice")
                name = house_elem.find('div', class_='title')
                on_sale = house_elem.find('div', class_="xiaoquListItemSellCount")
                year_built = house_elem.find('div', class_="positionInfo")
                # 继续清理数据
                xiaoqu_url = name.find('a',href=True)['href']
                #print("xiaoqu url:"+xiaoqu_url)
                name = name.text.replace("\n", "")   
                price = price.text.replace("m2", "").strip()
                price =  "".join(filter(str.isdigit, price)) # 提取数字
                on_sale = on_sale.text.replace("\n", "").strip()
                on_sale =  "".join(filter(str.isdigit, on_sale)) # 提取数字          
                year_built = year_built.text.replace("\n", "").strip()
                year_built =  "".join(filter(str.isdigit, year_built))
                primary_schools = get_primary_schools(xiaoqu_url)
                used,erfang,sanfang,sifang = get_ershou_info(xiaoqu_url)
                # 作为对象保存
                xiaoqu = XiaoQu(chinese_district, chinese_area, name,year_built, price,used, erfang,sanfang,sifang,
                primary_schools,xiaoqu_url)
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
            if district !="nanshanqu" :
                print("ignore district ",district)
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


def get_primary_schools(xiaoqu_url):
    schools = ""
    web_retry =0
    while web_retry<5:
        try:
            headers = create_headers()
            options = webdriver.ChromeOptions()
            # 操作无页面显示，如果需要debug，需要注释下面这一行
            options.add_argument('--headless')
            for (k,v) in headers.items():
                options.add_argument(k+"="+v)
            driver = webdriver.Chrome(chrome_options=options)
            driver.get(xiaoqu_url)
            # content after click may is loading,retry if needed
            driver.find_element_by_xpath("//li[@data-bl='education']").click()
            time.sleep(1)
            retry = 0
            while retry <3:
                if len(driver.find_element_by_xpath("//div[@data-bl='primary-school']").text) !=0 :
                    #print("data-bl='primary-school "+ driver.find_element_by_xpath("//div[@data-bl='primary-school']").text)
                    break
                retry += 1
                time.sleep(retry)
            driver.find_element_by_xpath("//div[@data-bl='primary-school']").click()
            time.sleep(1)
            retry = 0
            while retry <3:
                if len(driver.find_element_by_xpath("//div[@class='aroundList']").text) !=0 :
                    break
                retry += 1
                time.sleep(retry)
            arround_element = driver.find_element_by_xpath("//div[@class='aroundList']")
            school_elements  = arround_element.find_elements(by=By.XPATH,value="//span[@class='itemText itemTitle']")  
            for s in school_elements:
                #print("school element:"+s.text)
                schools = schools +s.text+";"
            # 偶发性获取到的数据是幼儿园tab页，因网页数据加载有延迟
            # 暂时未找到好的办法，先通过这种丑陋的方式兼容，增加重试，解决>99%的数据错乱问题
            if schools.find("幼儿园") >=0:
                schools =""
                continue
        except Exception as e:
            traceback.print_exc()
            print(xiaoqu_url+" :"+str(e))
        schools = schools[0:len(schools)-1]
        driver.close()
        if len(schools)>0:
            break
        web_retry += 1
        time.sleep(web_retry)
    print("xiaoqu url:"+xiaoqu_url+",schools:"+schools)  # 打印版块页面地址
    return schools

def get_ershou_info(xiaoqu_url):
    used = ""
    erfang,sanfang,sifang = 0,0,0
    for retry in range(5): 
        try: 
            response = requests.get(xiaoqu_url, timeout=10, headers=create_headers())
            html = response.content
            soup = BeautifulSoup(html, "lxml")
            ershou_element = soup.find('div', class_="goodSellHeader clear")
            # 如果取不到二手房详情URL，说明当前小区没有二手房出售
            if ershou_element is None:
                print(xiaoqu_url + " : 暂无房源")
                return used,erfang,sanfang,sifang
            ershou_url = ershou_element.find('a',href=True)['href']
            response = requests.get(ershou_url, timeout=10, headers=create_headers())
            time.sleep(1)
            html = response.content
            soup = BeautifulSoup(html, "lxml")
            sell_element = soup.find('ul',class_='sellListContent')
            if sell_element is None:
                print(ershou_url+" :"+" selling list is None")
                continue
            house_elements = sell_element.find_all('div',class_='houseInfo')
            for house_element in house_elements:
                if house_element.text.find("2室") >=0:
                    erfang = erfang +1
                elif house_element.text.find("3室") >=0:
                    sanfang = sanfang +1
                elif house_element.text.find("4室") >=0:
                    sifang = sifang +1
            
            house_url = sell_element.find('a',class_='img VIEWDATA CLICKDATA maidian-detail',href=True)['href']
            #print(house_url)
            used = get_house_used(house_url)
            print(ershou_url," 用途:",used," 二房:",erfang,",三房:",sanfang,",四房:",sifang)
            break
        except Exception as e:
            traceback.print_exc()
            print(xiaoqu_url+' :'+str(e))
            time.sleep(retry)
    return used,erfang,sanfang,sifang

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
