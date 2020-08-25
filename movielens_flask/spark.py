# coding=utf-8
import os
from pyspark.ml.recommendation import ALS, ALSModel
from pyspark.sql import SQLContext
import logging
import json
import pandas as pd
import pickle

# 日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# 推荐引擎
class RecommendationEngine:
    # 模型训练
    def model_train(self):
        try:
            # 加载之前训练好的模型
            logger.info("Loading the ALS model...")
            self.model = ALSModel.load("als_model.data")
            self.recommendations = self.spark_session.read.json('recommendation.data')
            print('recommendation.data have read!!!')
        except:
            self.recommendations = self.spark_session.read.json('recommendation.data')
            # 第一次训练会比较慢
            logger.info("Training the ALS model...")
            als = ALS(rank=self.rank, maxIter = 10, regParam=0.1, userCol= 'userId', itemCol='movieId', ratingCol='rating')
            self.model = als.fit(self.ratings_df)
            # 给每个用户推荐Top10个商品
            self.recommendations = self.model.recommendForAllUsers(10)
            #print(type(self.recommendations))
            #print(self.recommendations)
            self.recommendations.write.json("recommendation.data")
            # 保存模型
            self.model.save("als_model.data")
        logger.info("ALS model built!")

    # 针对user_id 推荐TopK个电影
    def get_top_ratings(self, user_id, movies_count):
        ratings = self.recommendations.where(self.recommendations.userId == user_id).collect()
        return ratings

    # 初始化spark
    def __init__(self, sc, dataset_path, spark_session):
        logger.info("Starting the Recommendation Engine")

        self.sc = sc
        self.spark_session = spark_session
        logger.info("Loading Ratings data...")
        ratings_file_path = os.path.join(dataset_path, 'ratings.csv')
        logger.info("ratings_file_path: %s" % ratings_file_path)
        ratings_raw = pd.read_csv(ratings_file_path)
        sql_sc = SQLContext(sc)
        self.ratings_df = sql_sc.createDataFrame(ratings_raw)

        # Train the model
        self.rank = 8
        self.seed = 5
        self.iterations = 3
        self.regularization_parameter = 0.1
        self.model_train()
