from bs4 import BeautifulSoup
from datetime import datetime
import requests
from time import sleep
from urllib import parse

import dateparser
import scrapy
from newspaper import Article


class WenweipoSpider(scrapy.Spider):
    name = "wenweipo"

    def start_requests(self):
        urls = []
        with open('words.txt', 'r') as f:
            words = f.read().splitlines()
        for word in words:
            r = requests.get('https://search2.wenweipo.com/search?query=%s&f=all&start_date=2021-01-01'%word)
            sleep(1)
            soup = BeautifulSoup(r.content, 'html.parser')
            result_num = int(soup.find('div', attrs={'class': 'searchNumber'}).find('font').text)
            if result_num == 0:
                continue
            urls += ['https://search2.wenweipo.com/search?page=%i&query=%s&f=all&start_date=2021-01-01'%(n+1,word) for n in range(result_num//10+1)]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_list)

    def parse_list(self, response):
        pages = response.xpath('//div[@class="searchItem"]')
        for page in pages:
            title = ''.join(page.xpath('*//h3//text()').extract())
            url = page.xpath('div[@class="searchItemTitle"]/a/@href').get()
            date = dateparser.parse(page.xpath('*//div[@class="searchItemTime"]/text()').get())
            if date < datetime(2021, 1, 1):
                continue
            yield scrapy.Request(url=url, callback=self.parse, cb_kwargs={'title': title, 'date': date.strftime('%Y-%m-%d')})

    def parse(self, response, title, date):
        a = Article('')
        a.set_html(response.body)
        a.parse()
        yield {
            'title': title,
            'date': date,
            'content': a.text,
            'url': parse.unquote(response.url),
            'domain': '文汇网'
        }