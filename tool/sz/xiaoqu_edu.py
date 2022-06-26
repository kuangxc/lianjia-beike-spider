#json解析库,对应到lxml
import json
from datetime import date, timedelta

#json的解析语法，对应到xpath
import jsonpath
import pymysql
import records
import requests
from bs4 import BeautifulSoup
from numpy import append

pymysql.install_as_MySQLdb()


class XiaoquEdu():
    def __init__(self, name,edu):
        self.name = name
        self.edu = edu

    def text(self):
        return self.name + "," + \
                self.edu + "," 

# http://edu.chachaba.com/index.php/Home/Index/build/?b_name=%E5%8D%97%E5%9B%BD%E4%B8%BD%E5%9F%8E
edu_url="http://edu.chachaba.com/index.php/Home/Index/build/?b_name="
headers={"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0"}


conn = pymysql.connect(host='119.45.125.72', port=3305, user='root', passwd='xxx', 
db='db_estate', charset='utf8')
cur = conn.cursor()#获取一个游标
sql_query = "select distinct(xiaoqu) from t_xiaoqu where date > date_sub(now(),interval 2 day)"
cur.execute(sql_query)
data = cur.fetchall()
for d in data :
  xiaoqu=d[0]
print(edu_url+xiaoqu)
response = requests.get(edu_url+xiaoqu, timeout=10, headers=headers)
html = response.content
soup = BeautifulSoup(html, "lxml")
edu_elements = soup.find('p', class_="mlp-tb").find_all("a")
schools = ""
for edu_element in edu_elements:
  schools += edu_element.text+";"
print(schools)
