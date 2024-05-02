from bs4 import BeautifulSoup
import requests
from urllib import parse

import dateparser
import scrapy


class HkcdSpider(scrapy.Spider):
    name = "hkcd"

    def start_requests(self):
        url = 'http://www.hkcd.com.hk/hkcdweb/php/getSearchResult.php'
        with open('words.txt', 'r') as f:
            words = f.read().splitlines()
        pages = []
        for word in words:
            r = requests.post(url, {'keyword': word})
            soup = BeautifulSoup(parse.unquote(r.content), 'html.parser')
            for a in soup.select('a'):
                pages.append([a['href'], a.h6.string, a.i.string])
        for u, t, d in pages:
            yield scrapy.Request(url=u, callback=self.parse, cb_kwargs={'title': t, 'date': d})

    def parse(self, response, title, date):
        content = '\n'.join(response.xpath('//div[@class="newsDetail"]//*/text()').getall())
        yield {
            'title': title,
            'date': dateparser.parse(date).strftime('%Y-%m-%d'),
            'content': content,
            'url': parse.unquote(response.url),
            'domain': '香港商报'
        }
