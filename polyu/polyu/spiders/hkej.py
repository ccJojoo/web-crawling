from bs4 import BeautifulSoup
from datetime import datetime
import requests
from urllib import parse

import dateparser
import scrapy
from newsplease import NewsPlease


class HkejSpider(scrapy.Spider):
    name = "hkej"

    # get urls of search results for every keyword
    def start_requests(self):
        urls = []
        with open('words.txt', 'r') as f:
            words = f.read().splitlines()
        for word in words:
            r = requests.get('https://search.hkej.com/template/fulltextsearch/php/search.php?q='+word, headers={'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0'})
            soup = BeautifulSoup(r.content, 'html.parser')
            try:
                page_num = int(soup.find('div',{'class': 'paging-wrapper'}).find_all('span')[-1].text)
            except IndexError:
                continue
            urls += ['https://search.hkej.com/template/fulltextsearch/php/search.php?q=%s&page=%i'%(word,n+1) for n in range(page_num)]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_list)

    # get urls of news from search results
    def parse_list(self, response):
        pages = response.xpath('//div[@class="result"]')
        for page in pages:
            title = page.xpath('h3/a/@title').get()
            url = 'https:' + page.xpath('h3/a/@href').get()
            date = dateparser.parse(page.xpath('*//span[@class="timeStamp"]/text()'))
            if date < datetime(2021, 1, 1):
                continue
            if 'ejinsight' in url:
                yield scrapy.Request(url=url, callback=self.parse_en, cb_kwargs={'title': title, 'date': date.strftime('%Y-%m-%d')})
            else:
                yield scrapy.Request(url=url, callback=self.parse_cn, cb_kwargs={'title': title, 'date': date.strftime('%Y-%m-%d')})

    # chinese news
    def parse_cn(self, response, title, date):
        content = '\n'.join(response.xpath('//div[@id="article-detail-wrapper"]//p//text()').extract()).replace('\t', '')
        if content == '':
            content = '\n'.join(response.xpath('//div[@id="articleDetailWrap"]//p//text()').extract()).replace('\t', '')
        yield {
            'title': title,
            'date': date,
            'content': content,
            'url': parse.unquote(response.url),
            'domain': '信报'
        }

    # english news
    def parse_en(self, response, word, title, date):
        yield {
            'title': title,
            'date': date,
            'content': NewsPlease.from_html(response.body).maintext,
            'link': parse.unquote(response.url),
            'domain': '信报'
        }
