import scrapy
import os
import pickle
import urllib.parse
from TBspider.items import TbspiderItem
from scrapy_redis.spiders import RedisSpider
from urllib.parse import urlparse, parse_qs
from TBspider.settings import accounts
import random

class TbSpider(RedisSpider):
    name = "tb"
    # allowed_domains = ["taobao.com"]
    redis_key='tb:start_urls'

    def __init__(self, keyword=None, *args, **kwargs):

        domain = kwargs.pop('domain', '')
        self.allowed_domains = list(filter(None, domain.split(',')))
        super(TbSpider,self).__init__(*args, **kwargs)

    def parse(self, response):
        # 加载 cookies（只在首次请求时用）
        # 当前文件在/spiders 中，向上1层才能到项目根目录
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # 随机选择一个账号
        account = random.choice(accounts)
        username = account["username"]
        cookie_path = os.path.join(BASE_DIR, f'pixiv_cookies_{username}.pkl')

        with open(cookie_path, 'rb') as f:
            cookies_list = pickle.load(f)

        cookies_dict = {c['name']: c['value'] for c in cookies_list}

        #接受命令行中的关键词
        keyword = response.meta.get('keyword')
        # 构造一个新的请求（携带 cookie）
        yield scrapy.Request(
            url=response.url,
            callback=self.parseSearch,
            meta={"selenium": "search",'keyword': keyword},
            cookies=cookies_dict,
            dont_filter=True
        )

    def parseSearch(self, response):
        print("进入搜索页面：",response.url)
        # # #保存网页源代码
        # with open("搜索页面.html", "w", encoding="utf-8") as f:
        #     f.write(response.text)
        product_list=response.xpath('//*[@id="content_items_wrapper"]/div')
        print("一共有",len(product_list),"个商品")
        #保留关键词以便动态建表名
        keyword = response.meta.get('keyword')
        #传入page方便输入后翻页
        page = self.extract_page_from_url(response.url)+1
        for item in product_list:
            detail_url=response.urljoin(item.xpath('./a/@href').extract_first())
            pic_url=item.xpath('.//img[@class="mainPic--Ds3X7I8z"]/@src').extract_first()
            #对每个详情页面提交请求，准备爬取数据
            yield scrapy.Request(
                url=detail_url,
                callback=self.parseDetail,
                meta={"selenium": 'True',"pic_url": pic_url,'keyword': keyword},
                # dont_filter=True,  # ✅ 忽略去重机制，允许重复请求
                cookies=response.request.cookies
            )

        button_is_exist=response.xpath('//button[@disabled and contains(@class,"next-btn")]/span/text()').extract_first()
        if button_is_exist=="上一页" or button_is_exist==None:
            print("有下一页，提交翻页请求")
            #提交翻页请求
            yield scrapy.Request(
                url=response.url,
                callback=self.parseSearch,
                meta={"selenium": "search",'page': page,'keyword': keyword},
                dont_filter=True,
                cookies=response.request.cookies
                )

    @staticmethod
    def clean_sales(sales_str):
        """
        将销量1万+转化成10000
        :param sales_str:想要清洗的字符串
        :return:转化后的整型数字
        """
        sales_str = sales_str.replace('+', '')  # 去掉 '+'
        if '万' in sales_str:
            return int(float(sales_str.replace('万', '')) * 10000)
        else:
            return int(float(sales_str))
    @staticmethod
    def extract_page_from_url(url):
        """
        传入的url提取其中的page
        :param url:https://s.taobao.com/search?page=2&q=固态sd10
        :return:2
        """
        parsed = urlparse(url)#把 URL 拆成结构体，返回一个 ParseResult 对象
        query_params = parse_qs(parsed.query)#把 'page=2&q=固态sd10' 变成字典
        page_list = query_params.get('page', ['1'])  # 默认值为1
        return int(page_list[0])

    def parseDetail(self, response):
        print("进入详情页面:",response.url)
        item=TbspiderItem()
        item['keyword'] = response.meta.get('keyword')
        item['link']=response.url
        item['price']=response.xpath('//div[@class="_4nNipe17pV--highlightPrice--fea17cf4"]/span[last()]/text()').extract_first()
        item['price']=int(float(item['price']))#转化成整型好进行数据分析

        item['title']=response.xpath('//h1/text()').extract_first()
        item['pic_link']=response.meta['pic_url']
        item['shore_name']=response.xpath('//span[@class="_4nNipe17pV--shopName--ccf81bdd"]/text()').extract_first()

        item['Sales']=(response.xpath('//div[contains(@class,"salesDesc")]/text()').extract_first()).split()[-1]
        item['Sales']=self.clean_sales(item['Sales'])#转化成整型好进行数据分析
        #合并信息
        item['pro_info']=', '.join(response.xpath('//div[contains(@class,"isSelected") and contains(@class,"valueItem")]//text()').getall())
        # print("商品链接",item['link'])
        # print("价格", item['price'])
        # print("标题", item['title'])
        # print("图片链接", item['pic_link'])
        # print("店名", item['shore_name'])
        # print("销量", item['Sales'])
        # print("商品描述", item['pro_info'])
        yield item



