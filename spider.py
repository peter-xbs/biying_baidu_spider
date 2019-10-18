# _*_ coding:utf-8 _*_

import requests
import urllib
import time
import re
import json
from bs4 import BeautifulSoup as BS
from selenium import webdriver
from config import get_header, get_sleep_time


month_days_dic = {1:31, 2:29, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31}
keywords_template = '{}市上市公司公告({}月{}日）东方财富网'

class BaiduSearchEngine(object):
    @classmethod
    def process(cls, output):
        with open(output, 'a') as fo:
            keywords_list = build_key_words()
            for keyword in keywords_list:
                res = cls.get_results(keyword)
                fo.write(''.join(res))


    @classmethod
    def deduplication(cls, input, output):
        S = set()
        with open(input) as f, open(output, 'w') as fo:
            for line in f:
                line_list = line.split('\t')
                check_ = '_'.join(line_list[:-1])
                if check_ in S:
                    continue
                fo.write(line)
                S.add(check_)

    @classmethod
    def get_results(cls, key_words):
        results = []
        time.sleep(get_sleep_time())
        query_str = 'wd=' + key_words
        html = requests.get('http://www.baidu.com/s?' + query_str, headers=get_header()).content
        soup = BS(html, "lxml")
        # print(soup1.prettify())
        content = soup.find(id="content_left")
        # 记录百度词条标题
        try:
            contents = content.contents
        except AttributeError as e:
            print(e)
        else:
            for item in content.contents:
                item_str = str(item).strip()
                if not item_str:
                    continue
                try:
                    item_soup = BS(str(item_str), 'lxml')
                    print('*'*20)
                    sub_item = item_soup.find('h3')
                    text = str(sub_item.text.replace('\n', '').replace(' ', ''))
                    href = re.findall('href="(http://.*?)"', str(sub_item))
                    href = href[0] if href else ''
                except Exception as e:
                    print(e)
                    continue
                if ')_东方财富网' in text and href:
                    res = spider(href)
                    res_soup = BS(res, 'lxml')
                    date = res_soup.find('div', attrs={"class":"time"})
                    try:
                        date = date.get_text()
                    except AttributeError:
                        continue
                    date_ = re.findall('(\d{4}年\d{1,2}月\d{1,2}日)', date)
                    date_ = date_[0] if date_ else ''
                    if not date:
                        print(date)
                        continue
                    line = '\t'.join([text, date_, href])+'\n'
                    results.append(line)
        return results

class BiyingSearchEngine(object):
    chrome = '/Users/peters/PycharmProjects/Tools/browser_driver/chromedriver'
    driver = webdriver.Chrome(executable_path=chrome)
    driver.maximize_window()
    base_url = 'https://cn.bing.com/search?q={}&qs=ds&form=QBRE'
    @classmethod
    def process(cls, output):
        with open(output, 'a') as fo:
            keywords_list = build_key_words()
            for keyword in keywords_list:
                print(keyword)
                res = cls.get_results(keyword)
                fo.write(''.join(res))
        cls.terminate_driver()

    @classmethod
    def terminate_driver(cls):
        cls.driver.quit()

    @classmethod
    def get_results(cls, keyword):
        results = []
        url = cls.base_url.format(keyword)
        try:
            cls.driver.get(url)
            time.sleep(1)
            res = cls.driver.find_elements_by_xpath('//*[@id="b_results"]/li/h2/a')
            for elem in res:
                title = str(elem.text).replace(' ', '')
                href = str(elem.get_attribute('href'))
                if ')_东方财富网' in title and 'eastmoney' in href and '/2019' not in href:
                    res = spider(href)
                    res_soup = BS(res, 'lxml')
                    date = res_soup.find('div', attrs={"class": "time"})
                    try:
                        date = date.get_text()
                    except AttributeError:
                        continue
                    date_ = re.findall('(\d{4}年\d{1,2}月\d{1,2}日)', date)
                    date_ = date_[0] if date_ else ''
                    if not date_:
                        print(date)
                        continue
                    line = '\t'.join([title, date_, href])+'\n'
                    results.append(line)
        except Exception as e:
            print(e)
        return results

    @classmethod
    def deduplicate(cls, input, output):
        S = set()
        with open(input) as f, open(output, 'w') as fo:
            for line in f.readlines():
                line_list = line.split('\t')
                if '2019' in line_list[1]:
                    continue
                check_ = '_'.join(line_list[:-1])
                if check_ in S:
                    continue
                fo.write(line)
                S.add(check_)
        try:
            cls.driver.quit()
        except Exception:
            pass



def spider(url):
    res = requests.get(url, headers=get_header()).content
    return res

def build_key_words():
    keywords_list = []
    for m in month_days_dic:
        for d in range(1, month_days_dic.get(m) + 1):
            for t in ["深", "沪"]:
                # if m in list(range(1, 9)):
                #     continue
                keyword = keywords_template.format(t, m, d)
                keywords_list.append(keyword)
    return keywords_list



def test():
    inp = '深市上市公司公告(10月17日)'
    url = 'https://cn.bing.com/search?q=深市上市公司公告(1月3日）东方财富网&qs=ds&form=QBRE'
    try:
        BiyingSearchEngine.driver.get(url)
        time.sleep(1)
        res = BiyingSearchEngine.driver.find_elements_by_xpath('//*[@id="b_results"]/li/h2/a')
        for elem in res:
            title = str(elem.text).replace(' ', '')
            href = str(elem.get_attribute('href'))
            if ')_东方财富网' in title and 'eastmoney' in href and '/2019' not in href:
                res = spider(href)
                res_soup = BS(res, 'lxml')
                date = res_soup.find('div', attrs={"class": "time"})
                try:
                    date = date.get_text()
                except AttributeError:
                    continue
                date_ = re.findall('(\d{4}年\d{1,2}月\d{1,2}日)', date)
                date_ = date_[0] if date_ else ''
                if not date_:
                    print(date)
                    continue
                print('\t'.join([title, date_, href]))

        time.sleep(10)
        # soup = BS(res, 'lxml')
        # print(soup.prettify())
    except Exception:
        pass
    BiyingSearchEngine.terminate_driver()
    # soup = BS(res.decode('utf-8'))
    # print(soup.prettify())

if __name__ == '__main__':
    output = 'baidu_result.txt'
    # BaiduSearchEngine.process(output)
    # BaiduSearchEngine.deduplication(output, 'baidu_result_unique.txt')
    # BiyingSearchEngine.process('baidu_result_unique2.txt')
    BiyingSearchEngine.deduplicate('baidu_result_unique3.txt', 'baidu_result_unique4.txt')