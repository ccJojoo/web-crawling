import requests
from bs4 import BeautifulSoup
import re
import csv

def writeFile(filename):
    with open(filename, "w", newline="", encoding="utf-8") as file:
        csvWriter = csv.writer(file)
        csvWriter.writerow(['Time', 'Frequency', 'Title', 'Content', 'Link'])
        csvWriter.writerows(search_list)

url = 'http://www.hkcd.com.hk/hkcdweb/php/getSearchResult.php'
header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
# keyword = "數字化風控"
keyword = "監管科技"
data = {'keyword' : keyword}
response = requests.post(url, data)
href_list = []
search_list = []
if response.status_code == 200:
    print('Access Successful!')
    bs = BeautifulSoup(response.content, "html.parser")
    href_list = [a['href'] for a in bs.select('a')]
    print(href_list)
for href in href_list:
    print("当前访问的链接是", href)
    content_response = requests.get(href, headers=header)
    if content_response.status_code == 200:
        soup = BeautifulSoup(content_response.content, "html.parser")
        title_tag = soup.find('div', attrs={'class': 'poster'})
        if title_tag == None:
            title = soup.find('div', attrs={'class': 'breadcrumb'}).find_next_sibling('h2').get_text()
        else:
            title = title_tag.find_next_sibling('h2').get_text()
        time = soup.find_all('div', attrs={'class': 'msg'})[1].find_all('span')[1].get_text()
        p_tag = soup.find('div', attrs={'class': 'newsDetail'}).find_all('p')
        if len(p_tag) == 0:
            paragraphs = soup.find('div', attrs={'class': 'newsDetail'}).find_all('div')
            combined_text = '\n'.join([p.get_text() for p in paragraphs])
        else:
            paragraphs = soup.find('div', attrs={'class': 'newsDetail'}).find_all('p')
            combined_text = '\n'.join([p.get_text() for p in paragraphs])
        frequency = len(re.findall(r'(?i){}'.format(keyword), combined_text))
        search_list.append([time, frequency, title, combined_text, href])

writeFile("{}_hkcd.csv".format(keyword))