# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import mysql.connector


class PolyuPipeline:
    def process_item(self, item, spider):
        return item

class MySQLPipeline:
    def __init__(self):
        self.cnx = mysql.connector.connect(
            user = 'crawler',
            password = 'PolyU-SIAT-2024',
            host = '47.115.208.57',
            database = 'crawler'
        )
        self.cursor = self.cnx.cursor()

    def process_item(self, item, spider):
        self.cursor.execute('''insert into news (title, date, content, domain, url) values (%s, %s, %s, %s, %s)''', (
            item['title'], item['date'], item['content'], item['doamin'], item['url']
        ))
        self.conn.commit()
        return item

    def close_spider(self, spider):
        self.cursor.close()
        self.cnx.close()
