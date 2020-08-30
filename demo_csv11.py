# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 20:29:38 2020

@author: Lenovo

智能演示 微信公众号首发
"""

import os
import pymysql
import pandas as pd
import time
from pdbc.trafodion import connector

config = {
        'host': '132.10.10.57',
        'port': 23400,
        'schema': 'ODS_TEST',
        'user': 'trafodion',
        'password': 'traf123',
        'charset': 'utf-8',
        'use_unicode': True,
        'get_warnings': True
    }
cnx = connector.connect(**config)
cursor = cnx.cursor()
print('esgyn数据库连接成功！')
print(' ')

# 1.连接 Mysql 数据库
try:
   # mysql2
   # conn = pymysql.connect(host='localhost', port=3306, user='root', password='123456@701716', db='ods_test', charset='utf8')
   # cur = conn.cursor()
   # print('数据库连接成功！')
   # print(' ')
    #esgyn
    config = {
        'host': '132.10.10.57',
        'port': 23400,
        'schema': 'ODS_TEST',
        'user': 'trafodion',
        'password': 'traf123',
        'charset': 'utf-8',
        'use_unicode': True,
        'get_warnings': True
    }
    cnx = connector.connect(**config)
    cursor = cnx.cursor()
    print('esgyn数据库连接成功！')
    print(' ')
except:
    print('数据库连接失败！')
t1 = time.time()
# 2.读取任意文件夹下的csv文件
# 获取程序所在路径及该路径下所有文件名称
path = os.getcwd()
print(path)
files = os.listdir(path)
# 遍历所有文件
i = 0
for file in files:
    # 判断文件是不是csv文件
    if file.split('.')[-1] in ['csv']:
        i += 1
        # 构建一个表名称，供后期SQL语句调用
        # 使用pandas库读取csv文件的所有内容,结果f是一个数据框，保留了表格的数据存储方式，是pandas的数据存储结构。
        f2 = pd.read_csv(file, encoding='utf-8')  # 注意：如果报错就改成 encoding='utf-8' 试试
        f = f2.astype(object).where(pd.notnull(f2), None)
        print(f)
        #print(f.dtypes)

        # 3.计算创建字段名称和字段类型的 SQL语句片段

        # 3.1 获取数据框的标题行（即字段名称）,将来作为sql语句中的字段名称。
        columns = f.columns.tolist()
        field = []
        print(columns)
        for item in columns:
            field.append(item)

        fields = ','.join(field)
        print(fields)

        # 5.1 将数据框的数据读入列表。每行数据是一个列表，所有数据组成一个大列表。也就是列表中的列表，将来可以批量插入数据库表中。
        values = f.values.tolist()  # 所有的数据
        #print(values)

        # 5.2 计算数据框中总共有多少个字段，每个字段用一个 %s 替代。
        s = ','.join(['%s' for _ in range(len(f.columns))])
        #print(s)
        for value in values:
        # 5.3 构建插入数据的SQL语句
            insert_sql = """upsert into YUANTONG_20191223 (order_id, "time", INFO, STATIONNAME, "TYPE") values({})""".format(str(value).replace('[','').replace(']','').replace('None',"''"))
            print('insert_sql is:' + insert_sql)

        # 5.4 开始插入数据
            cursor.execute(insert_sql)  # 使用 executemany批量插入数据
        #cnx.commit()
        print('表:' '数据插入完成！')
        print(' ')
#cur.close()  # 关闭游标
cnx.close()  # 关闭数据库连接
t2 = time.time()
print('导入用时：{0}h'.format(str((t2-t1)/3600)))
print('任务完成！共导入 {} 个CSV文件。'.format(i))





