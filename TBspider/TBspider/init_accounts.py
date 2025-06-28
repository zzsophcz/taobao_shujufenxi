# -*- coding: utf-8 -*-
# @Time: 2025/6/26 18:48
# @Author: 醋汁
# @Email: 2727913856@qq.com
# @File: init_accounts.py.py
# @Software: PyCharm

import pickle
import redis
from TBspider.settings import accounts  # 你的账号列表

r = redis.Redis(host='127.0.0.1', port=6379, db=0)

# 清空并重新初始化账号队列
r.delete('available_accounts')
for account in accounts:
    r.rpush('available_accounts', pickle.dumps(account))

print(f"Initialized {len(accounts)} accounts into Redis.")