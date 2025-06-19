# -*- coding: utf-8 -*-
# @Time: 2025/6/19 01:29
# @Author: 醋汁
# @Email: 2727913856@qq.com
# @File: 向redis数据库提交起始url.py
# @Software: PyCharm

import redis
import json
r = redis.Redis(host='localhost', port=6379)
# keyword=input("请输入搜索关键词")
keyword="自行车"
start_url = f"https://s.taobao.com/search?q={keyword}"
meta = {"keyword":keyword}
item = json.dumps({"url": start_url, "meta": meta})
r.lpush("tb:start_urls", item)