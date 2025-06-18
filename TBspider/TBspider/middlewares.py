# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
from scrapy.http import HtmlResponse

class SeleniumSpiderMiddleware(object):
    def __init__(self):
        print("[*] 初始化共享 Selenium 浏览器...")
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")  # 可选：无头模式
        # options.add_argument("--disable-gpu")
        # options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(options=options)

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(middleware.spider_closed, signal=signals.spider_closed)
        return middleware

    def spider_closed(self, spider):
        print("[*] 关闭 Selenium 浏览器...")
        self.driver.quit()

    def process_request(self, request, spider):
        sel_flag = request.meta.get("selenium")  # 标记处理方式
        if not sel_flag:
            print("没有参数，不启用")
            return None  # 普通请求，不处理

        try:
            if sel_flag == "shouCang":
                return self.enter_shouCang(request)
            elif sel_flag == "pic":
                return self.handle_pic(request)
            elif sel_flag == "True":
                return self.default_handle(request)
            else:
                print("未启用")
                return None
        except Exception as e:
            print(f"[!] Selenium 处理请求出错: {e}")
            return None

    def default_handle(self, request):
        print("常规 selenium 模式，即获取网页源代码，不做任何selenium处理")
        driver = self.driver
        url = request.url
        print("中间件进入常规页面处理，此时的url是：", url)
        cookies_dict = request.cookies

        # 第一步：先访问主域名页面（用于设置 cookie）
        base_url = "https://www.taobao.com/"
        driver.get(base_url)
        time.sleep(1)

        # 第二步：注入 cookies
        for name, value in cookies_dict.items():
            cookie = {'name': name, 'value': value, 'domain': '.taobao.com'}
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                print(f"[!] 添加 cookie 失败: {cookie} | 原因: {e}")

        # 第三步：访问目标页面
        driver.get(url)
        time.sleep(5)  # 适当等待页面加载

        # 第四步：获取页面源代码
        print("最后返回的页面源代码的url:", driver.current_url)
        html = driver.page_source

        input("暂停查看网页源代码")

        # 第五步：构造 HtmlResponse 对象返回
        return HtmlResponse(
            url=driver.current_url,
            body=html,
            encoding='utf-8',
            request=request
        )

    def handle_pic(self, request):
        pass

    def enter_shouCang(self, request):
        pass
