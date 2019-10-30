# _*_ coding:utf-8 _*_

#######
#本爬虫主要用于收集近一年的公告摘要并对其进行类型分析
#######

import re
import time
from selenium import webdriver


class EastMoneySummary(object):
    chrome = '/Users/peters/PycharmProjects/Tools/browser_driver/chromedriver'
    driver = webdriver.Chrome(executable_path=chrome)
    driver.maximize_window()
    base_url = 'http://stock.eastmoney.com/news/czxgg{}.html'

    @classmethod
    def process(cls, output):
        fo = open(output, 'w', encoding='utf-8')
        url_list = cls.get_page_urls()
        for url in url_list:
            print(url)
            page_info = cls.get_page(url)
            if not page_info:
                continue
            for elem in page_info:
                href, text = elem
                summary_info = cls.get_summary(href)
                market = text[:2]
                sum_date = re.findall('/a/(201\d{5})\d+', href)
                sum_date = sum_date[0] if sum_date else ''
                for info in summary_info:
                    line = '\t'.join([info[0], info[1], info[2], market, sum_date, href])+'\n'
                    fo.write(line)
        try:
            cls.terminate_driver()
        except Exception:
            pass

    @classmethod
    def get_summary(cls, url):
        # 返回标题、摘要、类型
        try:
            res_dic = {}
            cls.driver.get(url)
            time.sleep(0.5)
            p_elems = cls.driver.find_elements_by_xpath('//*[@id="ContentBody"]/p')
            type_ = 'unknown'
            for item in p_elems:
                item_text = item.text

                if item_text.endswith(':') or item_text.endswith('：') or len(item_text) <=6:
                    type_ = item_text.strip('：').strip(':')
                    continue
                if '文章来源' in item_text or '责任编辑' in item_text:
                    continue

                item_html = item.get_attribute('innerHTML')
                item_key = re.findall('href="http://quote.eastmoney.com/(.*?).html"', item_html)
                item_key = item_key[0] if item_key else ''
                if not item_key:
                    continue
                item_key = item_key+type_
                if item_key not in res_dic:
                    res_dic[item_key] = [type_, item_text]
                else:
                    res_dic[item_key].append(item_text)

            results = []
            for key in res_dic:
                if len(res_dic[key]) == 2:
                    results.append(('NULL', res_dic[key][1], res_dic[key][0]))  # title, sum, type
                elif len(res_dic[key]) == 3:
                    results.append((res_dic[key][1], res_dic[key][2], res_dic[key][0]))
                else:
                    print('error parser: {}'.format(url))
            return results
        except Exception as e:
            print(e)
            cls.terminate_driver()
            return []

    @classmethod
    def get_page(cls, url):
        try:
            cls.driver.get(url)
            time.sleep(1)
            page_urls_elems = cls.driver.find_elements_by_xpath('//ul/li/div/p/a')
            page_info = [(elem.get_attribute('href'), elem.text) for elem in page_urls_elems]
            return page_info
        except Exception:
            cls.terminate_driver()
        return []

    @classmethod
    def get_page_urls(cls):
        url_list = []
        first_url = cls.base_url.format('')
        url_list.append(first_url)
        for i in range(2, 26):
            url = cls.base_url.format('_'+str(i))
            url_list.append(url)
        return url_list

    @classmethod
    def terminate_driver(cls):
        cls.driver.quit()

if __name__ == '__main__':
    EastMoneySummary.process('summary')