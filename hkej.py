import requests
from bs4 import BeautifulSoup
import zhconv
import re
import csv
"""
    Note: 该网站只能用繁体搜
"""
# 转换繁体字
def wordConv(text):
    return zhconv.convert(text, 'zh-hant')
# 转换简体字
def Conv(text):
    return zhconv.convert(text, 'zh-cn')

def getKeywords(url):
    # 设置请求头
    header = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=header)
    # print(response.status_code)
    if response.status_code == 200:
        bs = BeautifulSoup(response.content, "html.parser")
        search_results = bs.find_all("div", attrs={"class": "result"})
        for item in search_results:
            h3_tag = item.find("h3")
            title = h3_tag.a['title']
            time = item.find("span", attrs={"class": "timeStamp"}).text
            href = 'https:' + h3_tag.a['href']
            content_response = requests.get(href, headers=header)
            if content_response.status_code == 200:
                soup = BeautifulSoup(content_response.content, "html.parser")
                if 'ejinsight' in href:
                    pic_tag = soup.find('div', attrs={"class":'pic pictop'})
                    if pic_tag == None:
                        combined_text = "Page Lost!"
                    else:
                        paragraphs = pic_tag.find_next_siblings('p')
                        combined_text = '\n'.join([p.get_text() for p in paragraphs])
                        frequency = len(re.findall(r'(?i){}'.format(keyword), combined_text))
                        frequency += len(re.findall(r'(?i){}'.format(Conv(keyword)), combined_text))
                else:
                    h1_tag = soup.find('h1', id='article-title')
                    paragraphs = h1_tag.find_next_siblings('p')
                    if len(paragraphs) == 0:
                        div_tag = soup.find('div', id='article-content')
                        paragraphs = div_tag.find_all('p')
                    combined_text = '\n'.join([p.get_text() for p in paragraphs])
                    frequency = len(re.findall(r'(?i){}'.format(keyword), combined_text))
            search_list.append([time, frequency, title, combined_text, href])
            print(time)

def writeFile(filename):
    with open(filename, "w", newline="", encoding="utf-8") as file:
        csvWriter = csv.writer(file)
        csvWriter.writerow(['Time', 'Frequency', 'Title', 'Content', 'Link'])
        csvWriter.writerows(search_list)

if __name__ == '__main__':
    search_list = []
    url = "https://search.hkej.com/template/fulltextsearch/php/search.php?q="
    keyword = "數字化風控"
    # keyword = "digitalized risk control"
    # keyword = "跨境結算"
    # keyword = "
    # "
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url + keyword, headers=header)
    bs = BeautifulSoup(response.content, "html.parser")
    pages = len(bs.find("div", attrs={"class": "paging-wrapper"}).find_all("span")) - 1
    if pages == -1:
        print("该关键词搜索无结果！")
    elif pages == 1:
        getKeywords(url=url+keyword)
    else:
        for i in range(pages):
            new_url = url + keyword + '&page=' + str(i+1)
            getKeywords(new_url)
    writeFile("{}.csv".format(keyword))
