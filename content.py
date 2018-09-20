# coding:utf-8
import urllib.request
from bs4 import BeautifulSoup
import re
import os
import time
import pymongo

# 小说主地址
req_url_base = 'http://www.zuowen.com/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) '
                  'Chrome/17.0.963.56 Safari/535.11'}

from pymongo import MongoClient

# 数据库
client = MongoClient('192.168.50.159', 27017)
db = client.work
composition = db.composition


# 获取文章的内容
def get_content(request_url):
    try:
        req = urllib.request.Request(request_url, headers=headers)
        res = urllib.request.urlopen(req).read()
        # soup转化
        soups = BeautifulSoup(res, "html.parser")
        # 作文题目
        title = soups.select('.h_title')[0].text

        date = soups.select('p[style="text-align:center;padding:10px"]')[0].text

        # 路径
        path = soups.select('.path a')

        # 含有表格的
        table_list = soups.select('.con_content td')
        if len(table_list) != 0:
            print("有表格 == 不计入")
            # for item in table_list:
            #     item_list = item.select('a')
            #     if len(item_list) != 0:
            #         # 查看更多忽略
            #         if len(item_list[0].text) != '查看更多相关文章':
            #             get_content(item_list[0]['href'])
        else:
            # 作文内容
            content_text = soups.select('.con_content')[0]
            for ss in content_text.select("script"):  # 删除无用项
                ss.decompose()

            # 按照指定格式替换章节内容，运用正则表达式
            content_text = re.sub('\s+', '\r\n\t', content_text.text).strip('\r\n')

            # 替换掉 作文网专稿\r\n未经允许不得转载'
            content_text = content_text.replace('作文网专稿\r\n\t未经允许不得转载', '')
            # 替换掉 作文网专稿\r\n未经允许不得转载'
            content_text = content_text.replace('E度网专稿\r\n\t未经允许不得转载', '')

            item_data = {'catalog': path[0].text,
                         'education': path[1].text,
                         'grade': path[2].text,
                         'type': path[3].text,
                         'date': date,
                         'url': request_url,
                         'title': title,
                         'content': content_text}

            # 数据库存储
            composition.insert_one(item_data)

            # fo = open(title + '.txt', "ab+")
            # 以二进制写入作文题目
            #  fo.write((title + "\r\n").encode('UTF-8'))
            # 以二进制写入作文内容
            # fo.write(content_text.encode('UTF-8'))
            print(content_text)
    except Exception as e:
        print(e)


# 获取一个年级的一个类型
def get_one_type_content(request_url):
    try:
        req = urllib.request.Request(request_url, headers=headers)
        res = urllib.request.urlopen(req).read()
        # soup转化
        soups = BeautifulSoup(res, "html.parser")
        # 当前页的作文列表
        composition_list = soups.select('.artbox_l_t a')
        for item in composition_list:
            composition_url = item['href']
            get_content(composition_url)

        page_list = soups.select('.artpage a')
        if len(page_list) != 0:
            item_tag = page_list[len(page_list) - 1]
            try:
                item_url = item_tag['href']
                if len(item_url) != 0:
                    get_one_type_content(item_url)
            except Exception as e:
                print(e)

    except Exception as e:
        print(e)


# 获取一个小学的
def get_one_level_content(request_url):
    try:
        req = urllib.request.Request(request_url, headers=headers)
        res = urllib.request.urlopen(req).read()
        # soup转化
        soups = BeautifulSoup(res, "html.parser")
        # 当前页的作文列表
        type_list = soups.select('.taglist ul li a')
        for article in type_list:
            type_name = article.text
            if type_name != '全部':
                type_url = article['href']
                # 六年级
                if type_url.find('wunianji') >= 0:
                    get_one_type_content(type_url)

    except Exception as e:
        print(e)


get_one_level_content('http://www.zuowen.com/xiaoxue/')

client.close()
