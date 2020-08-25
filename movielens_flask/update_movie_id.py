import requests
from lxml import etree
from urllib.parse import urljoin
import pandas as pd

from sqlalchemy import Column, String, Integer, DateTime, UniqueConstraint, create_engine
from sqlalchemy.orm import sessionmaker

# 创建&返回session
def get_db_session():
    engine = create_engine('mysql+mysqlconnector://root:passw0rdcc4@localhost:3306/movielens')
    # 创建DBSession类型:
    DBSession = sessionmaker(bind=engine)
    # 创建session对象:
    session = DBSession()
    #sql_stmt = "SET SESSION sql_mode='STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION'"
    #session.execute(sql_stmt)

    return engine, session

# 添加电影链接及图片链接
def update_movie_id(title, movie_id):
    update_stmt = 'UPDATE movie SET movie_id = :movie_id WHERE title = :title'
    session.execute(update_stmt, {'movie_id': str(movie_id), 'title': title})
    session.commit()
    print('update movie_id ' + title + ' ' + str(movie_id))

# 添加电影链接及图片链接
def add_movie_id(title, movie_id):
    insert_stmt = 'insert ignore movie (movie_id, title) VALUES (:movie_id, :title)'
    session.execute(insert_stmt, {'movie_id': str(movie_id), 'title': title})
    session.commit()
    print('add movie_id ' + title + ' ' + str(movie_id))



#print(get_movie_pic_and_url("Schindler's List (1993)"))

# 获取mysql session
engine, session = get_db_session()
# 数据加载
df = pd.read_csv('movies.csv')
i = 0
for (title, movie_id) in zip(df['title'], df['movieId']):
    
    #update_movie_id(title, movie_id)
    add_movie_id(title, movie_id)

