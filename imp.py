# coding=utf-8
# # python连接数据库，导入圆通当日数据
import pymysql
import logging
import os
from warnings import filterwarnings
import time


def load_file(table_name):
    # 连接数据库
    connection = pymysql.connect(host='localhost', port=3309, user='root', password='123456@701716', db='sf', charset='utf8')
    cursor = connection.cursor()
    if not connection.ping():
        print('连接数据库成功！')

    # 获取当前文件的存放路径
    path = os.getcwd()
    for each_file in os.listdir(path):
        # 获取该 路径下所有的csv文件的完整路径
        if '.csv' in each_file:
            full_path = os.path.join(path, each_file)
            new_path = full_path.replace('\\', '/')
            # 确保插入的列是正确的
            sql = r"load data infile '{file_path}' into table {table_name} character set utf8mb4 fields terminated by ',' lines terminated by '\r\n' ignore 1 lines(order_id,time,info,stationName,type) set stationName=if(@stationName='', -1, @stationName),type=if(@type='',-1,@type);".format(file_path=new_path, table_name=table_name)
            try:
                print('==== 正在导入： {0} === '.format(full_path))
                cursor.execute(sql)
                connection.commit()
            except:
                logging.error('=== 导入出错:{0} ==='.format(full_path), exc_info=True)
                connection.rollback()
                continue
    # 关闭数据库和游标
    connection.close()
    cursor.close()


if __name__ == '__main__':
    filterwarnings('ignore', category=pymysql.Warning)
    t1 = time.time()
    table = r'sf.yuantong_test'
    load_file(table)
    t2 = time.time()
    print('导入用时：{0}s'.format(str(t2-t1)))
