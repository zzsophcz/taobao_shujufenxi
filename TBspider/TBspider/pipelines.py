# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import pymysql
import re

class TbspiderPipeline:
    def open_spider(self, spider):
        print("管道启动!")
        # # 获取关键词并处理为表名
        # raw_keyword = spider.keyword
        # self.table_name = f"tb_{self.clean_table_name(raw_keyword)}"

        # 连接数据库
        self.conn = pymysql.connect(
            host='localhost',
            port=3307,
            user='root',
            password='123456',
            database='taobao',
            charset='utf8mb4'
        )
        self.cursor = self.conn.cursor()
        self.created_tables = set()  # 记录已创建过的表，避免重复创建

    def clean_table_name(self, keyword):
        # 将关键词转为合法表名：去除空格、特殊符号，仅保留字母数字下划线
        return re.sub(r'\W+', '_', keyword.strip())

    def create_table_if_not_exists(self, table_name):
        if table_name in self.created_tables:
            return
        create_sql = f"""
        CREATE TABLE IF NOT EXISTS `{table_name}` (
            id INT PRIMARY KEY AUTO_INCREMENT,
            title VARCHAR(255),
            price FLOAT,
            sales INT,
            shop VARCHAR(100),
            link TEXT,
            pic_url TEXT,
            description TEXT
        ) CHARSET=utf8mb4;
        """
        self.cursor.execute(create_sql)
        self.created_tables.add(table_name)

    def process_item(self, item, spider):
        raw_keyword = item.get('keyword')
        if not raw_keyword:
            raise ValueError("item中必须包含'keyword'字段，用于动态表名")
        table_name = f"tb_{self.clean_table_name(raw_keyword)}"
        self.create_table_if_not_exists(table_name)

        print(f"管道处理item: {item['title']}")
        print(f"准备写入数据库，表名：{table_name}")

        insert_sql = f"""
        INSERT INTO `{table_name}` (title, price, sales, shop, link, pic_url, description)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        data = (
            item['title'],
            float(item['price']),
            int(item['Sales']),
            item['shore_name'],
            item['link'],
            item['pic_link'],
            item['pro_info']
        )
        self.cursor.execute(insert_sql, data)
        # 执行插入
        print("写入完成")
        self.conn.commit()
        return item

    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()


