import scrapy
import os
import pickle
import urllib.parse

class TbSpider(scrapy.Spider):
    name = "tb"
    allowed_domains = ["taobao.com"]

    def __init__(self, keyword=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if keyword is None:
            raise ValueError("请使用 -a keyword=xxx 指定搜索关键词")
        encoded = urllib.parse.quote(keyword)
        self.start_urls = [f"https://s.taobao.com/search?q={encoded}"]

    def parse(self, response):
        # 加载 cookies（只在首次请求时用）
        # 当前文件在/spiders 中，向上1层才能到项目根目录
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cookie_path = os.path.join(BASE_DIR, 'pixiv_cookies.pkl')

        with open(cookie_path, 'rb') as f:
            cookies_list = pickle.load(f)

        cookies_dict = {c['name']: c['value'] for c in cookies_list}

        # 构造一个新的请求（携带 cookie）
        yield scrapy.Request(
            url=response.url,
            callback=self.parseSearch,
            meta={"selenium": "True"},
            cookies=cookies_dict,
            dont_filter=True
        )

    def parseSearch(self, response):
        print("进入搜索页面：",response.url)
        product_list=response.xpath('//*[@id="content_items_wrapper"]/div')
        print("一共有"+len(product_list)+"个商品")
        for item in product_list.split("\n"):
            detail_url=response.urljoin(item.xpath('./a/@href').extract_first())
            print(detail_url)
            break
        # yield scrapy.Request(url=search_url, callback=self.parseSearch)
