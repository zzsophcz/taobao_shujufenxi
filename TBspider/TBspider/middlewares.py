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

def smart_scroll(driver, pause_time=2, max_no_change=3):
    """
    智能滚动页面，直到主图数量不再增长。
    :param driver: selenium WebDriver
    :param pause_time: 每次滚动后的等待时间
    :param max_no_change: 连续几次无增长就认为加载完了
    """
    #窗口最大化
    driver.maximize_window()
    #寻找主图的选择器
    item_selector = '//*[@id="content_items_wrapper"]/div//img[@class="mainPic--Ds3X7I8z"]'

    last_count = 0
    no_change_times = 0

    scroll_step = 30  # 每次滚动的像素数
    scroll_pause = 1  # 每小步之间的停顿（模拟人滚动）

    while no_change_times < max_no_change:
        current_position = 0
        total_height = driver.execute_script("return document.body.scrollHeight")
        time.sleep(scroll_pause)

        # 模拟“逐步滚动”到页面底部
        while current_position < total_height:
            driver.execute_script(f"window.scrollTo(0, {current_position});")
            current_position += scroll_step

        time.sleep(pause_time)

        # 重新获取主图数量
        items = driver.find_elements(By.XPATH, item_selector)
        current_count = len(items)
        print(f"当前主图数量: {current_count}")

        if current_count == last_count:
            no_change_times += 1
        else:
            no_change_times = 0
            last_count = current_count

    print(f"滚动完成，最终主图数量: {last_count}")

class SeleniumSpiderMiddleware(object):
    def __init__(self):
        print("[*] 初始化共享 Selenium 浏览器...")
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")  # 可选：无头模式
        # options.add_argument("--disable-gpu")
        # options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(options=options)
        self.cookies_injected = False

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
            if sel_flag == "detail":
                return self.enter_detail(request)
            elif sel_flag == "search":
                return self.enter_search(request)
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

        # 第二步：注入 cookies
        if not self.cookies_injected:
            driver.get("https://www.taobao.com/")
            time.sleep(1)
            for name, value in cookies_dict.items():
                cookie = {'name': name, 'value': value, 'domain': '.taobao.com'}
                try:
                    driver.add_cookie(cookie)
                except Exception as e:
                    print("cookie 加载失败:", e)
            self.cookies_injected = True

        # 第三步：访问目标页面
        driver.get(url)
        time.sleep(3)  # 适当等待页面加载

        # 第四步：获取页面源代码
        print("最后返回的页面源代码的url:", driver.current_url)
        html = driver.page_source

        # input("暂停查看网页源代码")

        # 第五步：构造 HtmlResponse 对象返回
        return HtmlResponse(
            url=driver.current_url,
            body=html,
            encoding='utf-8',
            request=request #这里是为了保留原请求的meta参数
        )

    def enter_detail(self, request):
        pass

    def enter_search(self, request):
        driver = self.driver
        url = request.url
        print("进入搜索页面处理模式，此时的url是：", url)
        cookies_dict = request.cookies
        # 第二步：注入 cookies
        if not self.cookies_injected:
            driver.get("https://www.taobao.com/")
            time.sleep(1)
            for name, value in cookies_dict.items():
                cookie = {'name': name, 'value': value, 'domain': '.taobao.com'}
                try:
                    driver.add_cookie(cookie)
                except Exception as e:
                    print("cookie 加载失败:", e)
            self.cookies_injected = True
        # 第三步：访问目标页面
        driver.get(url)
        time.sleep(3)  # 适当等待页面加载
        #在这里添加下滑获取图片
        smart_scroll(driver)
        # 第四步：获取页面源代码
        print("最后返回的页面源代码的url:", driver.current_url)
        html = driver.page_source
        # input("暂停查看网页源代码")
        # 第五步：构造 HtmlResponse 对象返回
        return HtmlResponse(
            url=driver.current_url,
            body=html,
            encoding='utf-8',
            request=request
        )
