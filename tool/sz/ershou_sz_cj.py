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
    def __init__(self,date, district, area, num):
        self.date = date
        self.district = district
        self.num = num
        self.area = area

    def text(self):
        return self.date + "," + \
                self.district + "," + \
                self.num + "," + \
                self.area

yesterday = date.today() - timedelta(days=1)
yester_str = yesterday.strftime('%Y-%m-%d')

url="http://zjj.sz.gov.cn:8004/api/marketInfoShow/getEsfCjxxGsData"
headers={"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0"}

result = requests.post(url=url, headers=headers) 
#print(result.text)
#把json形式的字符串转换成python形式的Unicode字符串
data=json.loads(result.text)
#python形式的列表
list = []
size = len(jsonpath.jsonpath(data,'$.data.dataMj.*'))
mjs = jsonpath.jsonpath(data,'$.data.dataMj.*')
print(mjs)
print(type(mjs))
print(len(mjs))
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
    list.append(ErShouChengJiao(yester_str,district,area,num))
print(len(list))
db = records.Database('mysql://root:2e98962fa0d4d199@119.45.125.72:3305/db_estate?charset=utf8', encoding='utf-8')
for m in list:
    try: 
    # print("replace data into mysql")
      db.query('REPLACE INTO t_sz_fjzs (f_date,f_district, f_ershou_num, f_ershou_area) '
          'VALUES(:date, :district, :num, :area)',
          date=m.date, district=m.district, num=m.num,area=m.area)     
    except Exception as e:
        print(e)
        continue         
  


 
