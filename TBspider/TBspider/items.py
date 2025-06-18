# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TbspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field
    link = scrapy.Field()
    price = scrapy.Field()
    title = scrapy.Field()
    pic_link = scrapy.Field()
    shore_name = scrapy.Field()
    Sales = scrapy.Field()
    pro_info=scrapy.Field()
    keyword=scrapy.Field()
    pass
