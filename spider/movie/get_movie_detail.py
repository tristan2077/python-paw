#!/usr/bin/env python
# encoding: utf-8

"""
@version: python2.7
@author: ‘sen-ele‘
@license: Apache Licence 
@file: get_movie_detail
@time: 18/4/17 AM10:59
"""

from bs4 import BeautifulSoup

import re
from pymongo import MongoClient

from spider import paw,redisConn,mongoConn


db = mongoConn.paw

import time

def get(url):

    mv=dict()

    response=paw.get(url)
    print "paw end!"

    if(response.status_code!=200):
        print(response.status_code)
        print("Exit from Exception")
        exit()
    try:
        soup_page=BeautifulSoup(response.text,'lxml')
        name=soup_page.find('span',property="v:itemreviewed").text
        year=soup_page.find('span',class_="year").text
        mv_info=soup_page.find('div',class_="indent clearfix")
        mv_img=mv_info.find('img',src=re.compile('^https://.*.doubanio.com/'))
        rating_num=soup_page.find('div',class_='rating_self clearfix').find('strong',class_='ll rating_num')
        mv_id=re.search(r'[0-9].*[0-9]',url).group(0)
        mv['name']=name
        mv['year']=year
        mv['img']=mv_img['src']
        print(rating_num.text)
        mv['rating']=float(rating_num.text)  #new modify to int for pick
        #mv['info']=mv_info
        mv['id']=mv_id
    except Exception,e:
        print(url)
        print e
        raise "Raise a Exception in 解析详情页"

    return mv
def insert():

    while True:
        if redisConn.scard("movie_urls"):
            url=redisConn.spop("movie_urls")
            content = dict()
            content['type'] = "豆瓣电影"
            content["tid"] = 1
            try:
                mv=get(url)
                content['id']=mv['id']
                content['content']=mv

                a = db.data.find_one({"id": content['id']})
                if (not a):
                    db.data.insert_one(content)
                    print("insert success")
                else:
                    print("Failed,id exist")
            except Exception,e:
                print(e)
                redisConn.sadd("failed_movie_url",url)
            time.sleep(1)
        else:
            print("All finished!")
            break
if __name__ == "__main__":
    insert()