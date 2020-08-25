import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from efficient_apriori import apriori

# 数据加载
df = pd.read_csv('./订单表.csv', encoding='gbk') 
print(df.shape)
print(df.head())
df['订单日期'] = pd.to_datetime(df['订单日期'])
# 以客户ID为 transactions的index
#dataset.index = dataset['客户ID'].group
df = df.sort_values(by=['客户ID', '订单日期'], ascending=True)
print(df.head())
print(df.shape)
df.to_csv('temp.csv')


# 将数据存放到transactions中
transactions = []
temp = []
temp_customer_id, temp_order_date = -1, -1
for i in range(0, df.shape[0]):
    customer_id = df.iloc[i]['客户ID']
    order_date = df.iloc[i]['订单日期']
    # 新的客户ID或订单日期
    if customer_id != temp_customer_id or order_date != temp_order_date:
        transactions.append(temp)
        temp = []
        temp_customer_id, temp_order_date = customer_id, order_date
    temp.append(df.iloc[i]['产品名称'])
if len(temp) > 0:
    transactions.append(temp)
#print(transactions)
print(len(transactions))

#print(transactions)
# 挖掘频繁项集和频繁规则
itemsets, rules = apriori(transactions, min_support=0.01,  min_confidence=0.3)
print("频繁项集：", itemsets)
print("关联规则：", rules)
