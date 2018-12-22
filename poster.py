# -*- coding:utf-8 -*-
import time
import json
import os
import re
import requests
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from hashlib import md5
from multiprocessing.pool import Pool

#设置随机请求头
agent=UserAgent()
headers={
        'Uaer-Agent':agent.random
    }

#解析每一部分的网页
def get_page(offset):
    data={
        'skip':offset
    }
    ltime=time.asctime(time.localtime(time.time()))
    ltime={'stamp':ltime}
    url='http://pic.haibao.com/ajax/image:getHotImageList.json?'+urlencode(ltime)
    try:
        response=requests.post(url,data=data,headers=headers)
        if response.status_code==200:
            return response.json()
    except requests.ConnectionError:
        return None
#       pass
#从上一页获取加载增量skip值及是否还有下一页的hasMore值
# def get_skip_hasMore(json):
#     pass

# 提取网页图片链接
def get_imgs(json):
    if json.get('result').get('html'):
        soup=BeautifulSoup(json.get('result').get('html'),'html5lib')
        for i in soup:
            img_links=i.find_all('div', class_="pagelibox")
            for link in img_links:
                yield {
                    'image':link.img['data-original']
                }

#保存图片并去重

def save_imgs(item):
    if not os.path.exists('Images'):
        os.mkdir('Images')
    try:
        response=requests.get(item.get('image'))
        if response.status_code==200:
            file_path='{0}/{1}.{2}'.format('Images',md5(response.content).hexdigest(),'jpg')
            if not os.path.exists(file_path):
                with open(file_path,'wb')as f:
                    f.write(response.content)
            else:
                print('Already Dwnload',file_path)
    except requests.ConnectionError:
        print('Faild to save Image')


def main(offset):
    json=get_page(offset)
    for item in get_imgs(json):
        print(item)
        save_imgs(item)
#根据该值控制爬取图片数量
SKIP_END=10

if __name__ == '__main__':
    groups=([x * 75 for x in range(0,SKIP_END)])
    pool=Pool()
    pool.map(main,groups)
    pool.close()
    pool.join()