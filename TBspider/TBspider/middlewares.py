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
from selenium.webdriver.common.keys import Keys
import random
from TBspider.settings import USER_AGENT_LIST


def smart_scroll(driver, pause_time=2, max_no_change=2):
    """
    智能滚动页面，直到主图数量不再增长。
    :param driver: selenium WebDriver
    :param pause_time: 每次滚动后的等待时间
    :param max_no_change: 连续几次无增长就认为加载完了
    """
    # 窗口最大化
    driver.maximize_window()
    # 寻找主图的选择器
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


def goto_page(driver, page_num):
    """
    设置跳转页码并跳转
    :param driver:
    :param page_num: 要在跳转框中输入的数字
    :return: 是否成功
    """
    try:
        # 设置窗口大小，这样跳转框会出来
        driver.set_window_size(1100, 600)
        time.sleep(2)
        # 滑倒最下面
        print("滑动到最下面")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # 等待加载更多内容

        input_box = driver.find_element(By.XPATH, '//div[@class="next-pagination-pages"]//input')
        submit_btn = driver.find_element(By.XPATH, '//div[@class="next-pagination-pages"]/button[last()]')
        input_box.clear()
        input_box.send_keys(str(page_num))
        print("输入的页码：",str(page_num))
        time.sleep(1)
        input_box.send_keys(Keys.ENTER)
        # driver.execute_script("arguments[0].click();", submit_btn)
        time.sleep(3)  # 等待加载

    except Exception as e:
        print(f"跳转第{page_num}页失败：", e)
        print("该网址没有跳转输入框，使用另外的逻辑")


def click_nextPage(driver, page_num):
    """
    根据传入的数字不断点击下一页
    :param driver:
    :param page_num:
    :return:
    """
    print(f"[INFO] 目标页码: 第 {page_num} 页")

    for i in range(1, page_num):
        try:
            # 等待“下一页”按钮可点击
            button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//div[contains(@class,"next-pagination-pages")]//button[last()]'))
            )
            # 点击
            driver.execute_script("arguments[0].click();", button)
            time.sleep(3)  # 等页面加载
            # 滑倒最下面
            total_height = driver.execute_script("return document.body.scrollHeight")
            time.sleep(1)
        except Exception as e:
            print(f"[ERROR] 第 {i + 1} 页跳转失败：{e}")
            return False
    return True


class SeleniumSpiderMiddleware(object):
    def __init__(self):
        print("[*] 初始化共享 Selenium 浏览器...")
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")  # 可选：无头模式
        # options.add_argument("--disable-gpu")
        # options.add_argument("--no-sandbox")
        #添加随机用户代理
        options.add_argument(f"user-agent={random.choice(USER_AGENT_LIST)}")

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
            elif sel_flag == "page_change":
                return self.enter_page_change(request)
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

        print("页面标题栏",driver.title)
        if driver.title=="验证码拦截":
            input("请手动滑块解除验证后回车确认！")
        time.sleep(2)
        html = driver.page_source

        # input("暂停查看网页源代码")
        print("最后返回的页面源代码的url:", driver.current_url)
        # 第五步：构造 HtmlResponse 对象返回
        return HtmlResponse(
            url=driver.current_url,
            body=html,
            encoding='utf-8',
            request=request  # 这里是为了保留原请求的meta参数
        )

    def enter_detail(self, request):
        pass

    def enter_search(self, request):
        driver = self.driver
        url = request.url
        print("进入搜索页面处理模式，此时的url是：", url)
        page = request.meta.get('page', 1)
        print("请求目标页码:", page)

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
        if page == 1:
            driver.get(url)
        else:
            driver.get(url)
            time.sleep(3)
            print("传入的page是:",page)
            goto_page(driver,page)

        time.sleep(3)  # 适当等待页面加载
        # 在这里添加下滑获取图片
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


