from threading import Thread
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as Wait
import os
from os import path
from bs4 import BeautifulSoup
from urllib.parse import quote
import time
import csv

Chromedriver_path = path.join(path.dirname(__file__), 'chromedriver.exe')
merchandise_folder = path.join(path.dirname(__file__), '淘宝商品信息')
folder = os.path.exists(merchandise_folder)

if not folder:
    os.makedirs(merchandise_folder)
    filedir_path = merchandise_folder
else:
    filedir_path = merchandise_folder


def parse_products(products):
    with open(products, "r", encoding='utf-8-sig') as f:
        raw_products = f.read().strip()
    raw_products = raw_products.replace("\t", ",").replace("\r", ",").replace("\n", ",")
    if raw_products == '':
        print("请在products.text文件中指定要爬取的产品名，并以 逗号/tab/表格鍵/回车符 分割，支持多行.\n"
              "保存文件并重试.\n\n"
              "例: product1,product2 product3\n\n")
        time.sleep(5)
        exit()
    produts_rdy = raw_products.split(",")
    return produts_rdy


products = path.join(path.dirname(__file__), "products.txt")
if os.path.exists(products):
    products_list = parse_products(products)
else:
    print("未找到需要爬取的products.txt文件，请创建.\n"
          "请在文件中指定要爬取的产品名，并以 逗号/空格/tab/表格鍵/回车符 分割，支持多行.\n"
          "保存文件并重试.\n\n"
          "例: product1,product2\n\n")
    time.sleep(5)
    exit()

browser = webdriver.Chrome(Chromedriver_path)
wait = Wait(browser, 10)


def crawl_products():
    html = browser.page_source
    soup = BeautifulSoup(html, 'lxml')
    items = soup.select('#mainsrp-itemlist  div  div div.items .item')
    products = []
    for item in items:
        image = item.select('.pic a img')[0]['data-src']
        price = item.select('.price')[0].text.strip()
        deal = item.select('.deal-cnt')[0].text.strip()
        title = item.select('.title')[0].text.strip()
        shop = item.select('.shop')[0].text.strip()
        location = item.select('.location')[0].text.strip()
        product = f'产品图片:{image},价格:{price},销量:{deal},产品名称:{title},店铺:{shop},产地:{location}'
        products.append(product)
    return products


def data_write(result, name):
    filename = path.join(merchandise_folder, products_list[name] + '.txt')
    for item in result:
        if os.path.exists(filename):
            with open(filename, 'a', encoding='UTF-8') as f:
                f.write(item + '\n')
        else:
            with open(filename, 'w', encoding='UTF-8') as f:
                f.write(item + '\n')


class Downloadworker(Thread):
    def __init__(self, i):
        Thread.__init__(self)
        self.i = i

    def run(self):
        browser.get("https://s.taobao.com/search?q=" + quote(products_list[self.i]))
        for i in range(50):
            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '#mainsrp-itemlist div.pic-box.J_MouseEneterLeave.J_PicBox')
                )
            )

            result = crawl_products()
            data_write(result, self.i)
            next_page = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '#mainsrp-pager div div div ul li.item.next a[data-url="pager"]')
                )
            )
            next_page.click()



# catalog = requests.get(f'https://www.88dus.com/top/fullflag/{page}/')
# catalog.encoding = ('GBK')
# html = catalog.text
# soup = BeautifulSoup(html, 'lxml')
for i in range(len(products_list)):
    if __name__ == '__main__':
        th = Downloadworker(i)
        th.start()
        th.join()
