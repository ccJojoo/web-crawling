from selenium import webdriver
from selenium.webdriver.common.by import By
import zhconv
import time
import requests
import re

# 转换繁体字
def wordConv(text):
    return zhconv.convert(text, 'zh-hant')

keyword = "数字化风控"
driver = webdriver.Chrome(executable_path='Scripts\chromedriver.exe')
driver.get('https://www.google.com.hk')
driver.find_element(By.NAME, 'q').send_keys("\"{}\" after:2024-01-08\n".format(keyword))
time.sleep(1)

# 设置等待时间和滚动间隔
scroll_wait_time = 1
scroll_interval = 1

def Scrool():
    # 获取初始滚动位置
    last_scroll_position = driver.execute_script("return window.pageYOffset;")
    while True:
        # 执行下滑操作
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_wait_time)
        # 等待页面加载
        time.sleep(scroll_interval)
        # 获取当前滚动位置
        current_scroll_position = driver.execute_script("return window.pageYOffset;")
        # 判断滚动位置是否不再改变
        if current_scroll_position == last_scroll_position:
            break
        # 更新上一次滚动位置
        last_scroll_position = current_scroll_position
Scrool()
iframe = driver.find_element(By.LINK_TEXT, '重新搜索以显示省略的结果')
iframe.click()
Scrool()
a = driver.find_elements(By.CSS_SELECTOR, 'a[jsname="UWckNb"]')
all_frequency = 0
print('当前爬取的关键词为：', keyword)
for i in a:
    url = i.get_attribute('href')
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=header)
    if response.status_code == 200:
        print("当前访问网站", url)
        time.sleep(1)
        try:
            content = response.content.decode("utf-8")
        except:
            content = response.text
        frequency = len(re.findall(r'(?i){}'.format(keyword), content))
        frequency += len(re.findall(r'(?i){}'.format(wordConv(keyword)), content))
        print('该网站关键词出现频率为：', frequency)

        all_frequency += frequency
print('该时间段总出现次数为：', all_frequency)
