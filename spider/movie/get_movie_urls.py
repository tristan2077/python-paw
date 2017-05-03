#!/usr/bin/env python
# encoding: utf-8

"""
@version: python2.7
@author: ‘sen-ele‘
@license: Apache Licence 
@file: get_movie_urls
@time: 18/4/17 AM11:08
"""

from bs4 import BeautifulSoup
import re
import time



from spider import paw,redisConn


key="movie_tags"
save_key="movie_urls"

def get_onepage_urls(tag):
    response = paw.get(tag)
    if (response.status_code != 200):
        print(response.status_code)
        redisConn.lpush(key,tag)
        raise Exception("Exception throws")

    soup_page = BeautifulSoup(response.text, 'lxml')
    raw_urls = soup_page.find_all('a', href=re.compile('^https://movie.douban.com/subject/[0-9].*[0-9]/$'))

    for temp in raw_urls:
        redisConn.sadd(save_key, temp['href'])

    try:
        raw_total = soup_page.find('span', class_='thispage')
        nextpage = raw_total.find_next('a', href=re.compile('^https://movie.douban.com/tag/.*type=T$'))['href']
    except:
        nextpage = 'EOF'
    return nextpage
def get_allpage_urls(tag):
    nextpage=tag
    while True:
        nextpage=get_onepage_urls(nextpage)
        print nextpage
        time.sleep(10)
        if "EOF"==nextpage:
            break

while redisConn.scard(key):
    next_tag = redisConn.spop(key)
    print next_tag
    get_allpage_urls(next_tag)