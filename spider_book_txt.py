# coding:utf-8
import urllib.request
from bs4 import BeautifulSoup
import re
import os
import time

# 小说主地址
req_url_base = 'https://www.booktxt.net/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 '
                  'Safari/537.36'}


def has_title(tag):
    return tag.get('property').equals('og:title')

# 小说下载函数


# txt_id：小说编号
# txt字典项介绍
# id：小说编号
# title：小说题目
# first_page：第一章页面
# txt_section：章节地址
# section_name：章节名称
# section_text：章节正文
# section_ct：章节页数
def get_txt(txt_id):
    txt = {'title': '', 'id': txt_id}
    try:
        # 根据小说编号获取小说URL
        req_url = req_url_base + txt['id'] + '/'
        print("小说编号：" + txt['id'])
        # 获取小说目录界面
        req = urllib.request.Request(req_url, headers=headers)
        res = urllib.request.urlopen(req).read()
        # soup转化
        soups = BeautifulSoup(res, "html.parser")

        # 获取小说题目
        title = soups.select('meta[property="og:title"]')
        txt['title'] = title[0]['content']

        # 获取小说作者
        author = soups.select('meta[property="og:novel:author"]')
        txt['author'] = author[0]['content']

        # 获取小说最近更新时间
        update = soups.select('meta[property="og:novel:update_time"]')
        txt['update'] = update[0]['content']

        # 获取最近更新章节名称
        lately = soups.select('meta[property="og:novel:lastest_chapter_name"]')
        txt['lately'] = lately[0]['content']

        # 获取小说简介
        intro = soups.select('meta[property="og:description"]')
        txt['intro'] = intro[0]['content']

        # 打开小说文件写入小说相关信息
        fo = open('{1}.txt'.format(txt['id'], txt['title']), "ab+")
        fo.write((txt['title'] + "\r\n").encode('UTF-8'))
        fo.write((txt['author'] + "\r\n").encode('UTF-8'))
        fo.write((txt['update'] + "\r\n").encode('UTF-8'))
        fo.write((txt['lately'] + "\r\n").encode('UTF-8'))
        fo.write("*******简介*******\r\n".encode('UTF-8'))
        fo.write(("\t" + txt['intro'] + "\r\n").encode('UTF-8'))
        fo.write("******************\r\n".encode('UTF-8'))

        print("编号：" + '{0:0>8}   '.format(txt['id']) + "小说名：《" + txt['title'] + "》  开始下载。")
        print("正在寻找第一章页面。。。")
        # 进入循环，写入每章内容
        chapter_list = soups.select('div #list dd a')
        for chapter in chapter_list:
            try:
                href = chapter['href']
                req_chapter = urllib.request.Request(req_url + str(href), headers=headers)
                res_chapter = urllib.request.urlopen(req_chapter).read()
                soup = BeautifulSoup(res_chapter, "html.parser")

                # 获取章节名称
                section_name = soup.select('div .bookname h1')[0]
                section_text = soup.select('div #content')[0]
                for ss in section_text.select("script"):  # 删除无用项
                    ss.decompose()
                # 获取章节文本
                section_text = re.sub('\s+', '\r\n\t', section_text.text)

                # 以二进制写入章节题目
                fo.write(('\r\n\n\n' + section_name.text + '\r\n\n').encode('UTF-8'))
                # 以二进制写入章节内容
                fo.write(section_text.encode('UTF-8'))
                print(txt['title'] + ' 章节：' + section_name.text + '     已下载')
            except Exception as e:
                print(e)
                print("编号：" + '{0:0>8}   '.format(txt['id']) + "小说名：《" + txt['title'] + "》 章节下载失败，正在重新下载。")

    except Exception as e:
        print(e)
        # 出现错误会将错误信息写入download.log文件，同时答应出来
        fo_err = open('download.log', "ab+")
        try:
            fo_err.write(('[' + time.strftime('%Y-%m-%d %X', time.localtime()) + "]：编号：" + '{0:0>8}   '.format(
                txt['id']) + "小说名：《" + txt['title'] + "》 下载失败。\r\n").encode('UTF-8'))
            print('[' + time.strftime('%Y-%m-%d %X', time.localtime()) + "]：编号：" + '{0:0>8}   '.format(
                txt['id']) + "小说名：《" + txt['title'] + "》 下载失败。")
            os.rename('{0:0>8}'.format(txt['id']) + '-' + txt['title'] + '.txt.download',
                      '{0:0>8}'.format(txt['id']) + '-' + txt['title'] + '.txt.error')
        except Exception as e:
            print(e)
            fo_err.write(('[' + time.strftime('%Y-%m-%d %X', time.localtime()) + "]：编号：" + '{0:0>8}   '.format(
                txt['id']) + "下载失败。\r\n").encode('UTF-8'))
            print('[' + time.strftime('%Y-%m-%d %X', time.localtime()) + "]：编号：" + '{0:0>8}   '.format(
                txt['id']) + "下载失败。")
        finally:  # 关闭文件
            fo_err.close()


# 此处为需要下载小说的编号，编号获取方法在上文中已经讲过。
get_txt("6_6454")
