# -*- coding: utf-8 -*-
# @Time: 2025/6/17 19:01
# @Author: 醋汁
# @Email: 2727913856@qq.com
# @File: 获取cookie.py
# @Software: PyCharm

# -*- coding: utf-8 -*-
# @Time: 2025/6/14 18:35
# @Author: 醋汁
# @Email: 2727913856@qq.com
# @File: spider.py.py
# @Software: PyCharm

from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pickle

# driver = webdriver.Chrome()
# driver.get("https://www.taobao.com/")
#
# # 手动输入账号密码登录
# input("请手动完成登录后按回车")
#
# # 保存登录后的 cookie 到文件
# cookies = driver.get_cookies()
# with open("pixiv_cookies.pkl", "wb") as f:
#     pickle.dump(cookies, f)
#
# driver.quit()


driver = webdriver.Chrome()

# 第一步：打开主页以设置 cookie
driver.get("https://www.taobao.com/")
time.sleep(2)

# 第二步：加载本地 cookie
with open("pixiv_cookies.pkl", "rb") as f:
    cookies = pickle.load(f)

for cookie in cookies:
    try:
        driver.add_cookie(cookie)
    except Exception as e:
        print("添加 cookie 出错：", e)

# 第三步：访问登录后页面
driver.get("https://s.taobao.com/search?q=%E5%9B%BA%E6%80%81%E9%93%A0%E4%BE%A0sd10&page=1")
time.sleep(3)

# 第四步：检查是否登录成功（是否含有用户元素）
print(driver.page_source)

driver.quit()

