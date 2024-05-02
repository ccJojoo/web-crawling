from bs4 import BeautifulSoup
from datetime import datetime
import re
import requests
from urllib import parse

import scrapy
from newspaper import Article


class RthkSpider(scrapy.Spider):
    name = "rthk"

    def start_requests(self):
        urls = []
        with open('words.txt', 'r') as f:
            words = f.read().splitlines()
        for word in words:
            r = requests.get('https://search.rthk.hk/search?q=%s&proxystylesheet=revamp16_v1p_frontend&start=0'%word)
            soup = BeautifulSoup(r.content, 'html.parser')
            try:
                result_num = int(re.search(r'\d+', soup.find('span',{'class': 'resNum'}).text).group())
            except AttributeError:
                continue
            urls += ['https://search.rthk.hk/search?q=%s&proxystylesheet=revamp16_v1p_frontend&start=%i'%(word,n+1) for n in range(0,result_num,10)]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_list)

    def parse_list(self, response):
        pages = response.xpath('//div[@class="resWrap"]//a[@ctype="c"]')
        for page in pages:
            title = page.xpath('h2/text()').get()
            url = page.xpath('@href').get()
            if 'news' not in url:
                continue
            date = datetime.strptime(url[-12:-4], '%Y%m%d')
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
            'domain': '香港电台'
        }