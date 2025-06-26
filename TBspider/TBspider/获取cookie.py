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
from selenium.webdriver.common.keys import Keys
import time
import random
import pickle

from TBspider.settings import accounts

# 随机选择一个账号
account = random.choice(accounts)
username = account["username"]
password = account["password"]

# 初始化浏览器
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")  # 防检测
driver = webdriver.Chrome(options=options)
# driver.maximize_window()

driver.get("https://login.taobao.com/havanaone/login/login.htm")
time.sleep(2)

# 输入账号密码
driver.find_element(By.XPATH, '//input[@name="fm-login-id"]').send_keys(username)
time.sleep(1)
driver.find_element(By.XPATH, '//input[@name="fm-login-password"]').send_keys(password)
time.sleep(1)

# 点击登录按钮
log_btn=driver.find_element(By.XPATH, '//button[@type="submit"]')
driver.execute_script("arguments[0].click();", log_btn)



# # 手动输入账号密码登录
# input("请手动完成登录后按回车")
input("暂停...")

# 保存登录后的 cookie 到文件
cookies = driver.get_cookies()
with open(f"pixiv_cookies_{username}.pkl", "wb") as f:
    pickle.dump(cookies, f)

driver.quit()


# driver = webdriver.Chrome()
#
# # 第一步：打开主页以设置 cookie
# driver.get("https://www.taobao.com/")
# time.sleep(2)
#
# # 第二步：加载本地 cookie
# with open("pixiv_cookies.pkl", "rb") as f:
#     cookies = pickle.load(f)
#
# for cookie in cookies:
#     try:
#         driver.add_cookie(cookie)
#     except Exception as e:
#         print("添加 cookie 出错：", e)
#
# # 第三步：访问登录后页面
# driver.get("https://s.taobao.com/search?page=1&q=%E9%93%A0%E4%BE%A0sd10&tab=all")
# try:
#     # 设置窗口大小，这样跳转框会出来
#     driver.set_window_size(966, 600)
#     time.sleep(1)
#     # 滑倒最下面
#     print("滑动到最下面")
#     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#     time.sleep(2)  # 等待加载更多内容
#
#     input_box = driver.find_element(By.XPATH, '//div[@class="next-pagination-pages"]//input')
#     submit_btn = driver.find_element(By.XPATH, '//div[@class="next-pagination-pages"]/button[last()]')
#     input_box.clear()
#     input_box.send_keys(3)
#     time.sleep(2)
#     # input_box.send_keys(Keys.ENTER)#这个可以
#     # driver.execute_script("arguments[0].click();", submit_btn)#为啥不行？
#
#     time.sleep(3)  # 等待加载
#
# except Exception as e:
#     print(f"跳转第 2 页失败：", e)
#     print("该网址没有跳转输入框，使用另外的逻辑")
# time.sleep(3)
#
# input("等待....")
# # 第四步：检查是否登录成功（是否含有用户元素）
# # print(driver.page_source)
#
# driver.quit()

