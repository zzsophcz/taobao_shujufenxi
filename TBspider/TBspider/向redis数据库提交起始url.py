# -*- coding: utf-8 -*-
# @Time: 2025/6/19 01:29
# @Author: 醋汁
# @Email: 2727913856@qq.com
# @File: 向redis数据库提交起始url.py
# @Software: PyCharm

import redis
import json
r = redis.Redis(host='localhost', port=6379)

start_url = "https://s.taobao.com/search?q=固态铠侠sd10"
meta = {"keyword": "固态铠侠sd10"}
item = json.dumps({"url": start_url, "meta": meta})
r.lpush("tb:start_urls", item)