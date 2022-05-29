#json解析库,对应到lxml
import json
from datetime import date, timedelta

#json的解析语法，对应到xpath
import jsonpath
import pymysql
import records
import requests
from numpy import append

pymysql.install_as_MySQLdb()


class ErShouChengJiao():
    def __init__(self,date, district, yishou_num, yishou_area, ershou_num, ershou_area):
        self.date = date
        self.district = district
        self.yishou_num = yishou_num
        self.yishou_area = yishou_area
        self.ershou_num = ershou_num
        self.ershou_area = ershou_area

    def text(self):
        return self.date + "," + \
                self.district + "," + \
                self.ershou_num + "," + \
                self.ershou_area

yesterday = date.today() - timedelta(days=1)
yester_str = yesterday.strftime('%Y-%m-%d')

yishou_url="http://zjj.sz.gov.cn:8004/api/marketInfoShow/getYsfCjxxGsData"
ershou_url="http://zjj.sz.gov.cn:8004/api/marketInfoShow/getEsfCjxxGsData"
headers={"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0"}

yishou_result = requests.post(url=yishou_url, headers=headers) 
ershou_result = requests.post(url=ershou_url, headers=headers) 
print(yishou_result.text)
#把json形式的字符串转换成python形式的Unicode字符串
data=json.loads(yishou_result.text)
#python形式的列表
list = []
# 解析一手
size = len(jsonpath.jsonpath(data,'$.data.dataMj.*'))
mjs = jsonpath.jsonpath(data,'$.data.dataMj.*')
tss = jsonpath.jsonpath(data,'$.data.dataTs.*')
for i in range(size):
    district = mjs[i]["name"]
    area = mjs[i]["value"]
    num = 0
    for ii in  range(size):
      if tss[ii]["name"] == district:
        num = tss[ii]["value"]
        break
    list.append(ErShouChengJiao(yester_str,district,num,area,0,0))
print("yishou get finish,size:",len(list))
data=json.loads(ershou_result.text)
# 解析一手
size = len(jsonpath.jsonpath(data,'$.data.dataMj.*'))
mjs = jsonpath.jsonpath(data,'$.data.dataMj.*')
tss = jsonpath.jsonpath(data,'$.data.dataTs.*')
for i in range(size):
   # print(i)
    district = mjs[i]["name"]
    area = mjs[i]["value"]
    num = 0
    for ii in  range(size):
      if tss[ii]["name"] == district:
        num = tss[ii]["value"]
        break
    for iii in range(len(list)):
        if list[iii].district == district:
            list[iii].ershou_num = num
            list[iii].ershou_area = area
print("ershou get finish size:",len(list))

db = records.Database('mysql://root:2e98962fa0d4d199@119.45.125.72:3305/db_estate?charset=utf8', encoding='utf-8')
for m in list:
    try: 
    # print("replace data into mysql")
      db.query('REPLACE INTO t_sz_fjzs (f_date,f_district,f_yishou_num,f_yishou_area, f_ershou_num, f_ershou_area) '
          'VALUES(:date, :district, :yishou_num, :yishou_area, :ershou_num, :ershou_area)',
          date=m.date, district=m.district, yishou_num=m.yishou_num,yishou_area=m.yishou_area,
          ershou_num=m.ershou_num,ershou_area=m.ershou_area)     
    except Exception as e:
        print(e)
        continue         
  