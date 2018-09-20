# -*- coding:utf-8 -*-

import pymysql

from pymongo import MongoClient

# 数据库
client = MongoClient('192.168.91.1', 27017)
mogDB = client.work
composition = mogDB.composition

# 打开数据库连接
db = pymysql.connect("localhost", "root", "root", "work")

# 使用 cursor() 方法创建一个游标对象 cursor
cursor = db.cursor()

# 使用 execute()  方法执行 SQL 查询
cursor.execute("SELECT VERSION()")

# 使用 fetchone() 方法获取单条数据.
data = cursor.fetchone()

print("Database version : %s " % data)

# 使用 execute() 方法执行 SQL，如果表存在则删除
cursor.execute("DROP TABLE IF EXISTS composition")

sql = """CREATE TABLE composition (
         i_catalog  VARCHAR(255),
         i_education  VARCHAR(255),
         i_grade  VARCHAR(255), 
         i_type  VARCHAR(255),
         i_date  VARCHAR(255),
         i_url  VARCHAR(255),
         i_title  VARCHAR(255),
         i_content TEXT )"""

cursor.execute(sql)

for item in composition.find():
    sql = '''INSERT INTO composition ( i_catalog, i_education, i_grade, i_type, i_date, i_url, i_title, i_content)
                           VALUES
                           ( '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')''' % (
        pymysql.escape_string(item['catalog']), pymysql.escape_string(item['education']),
        pymysql.escape_string(item['grade']), pymysql.escape_string(item['type']),
        pymysql.escape_string(item['date']), pymysql.escape_string(item['url']),
        pymysql.escape_string(item['title']), pymysql.escape_string(item['content']))
    try:
        cursor.execute(sql)
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()

# 关闭数据库连接
db.close()
